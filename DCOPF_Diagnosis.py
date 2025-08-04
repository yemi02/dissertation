#!/usr/bin/env python
# coding: utf-8

# ## DC OPF Diagnosis and Troubleshooting Notebook
# This notebook is designed for the diagnosis, testing, and troubleshooting of DC Optimal Power Flow (DCOPF) calculations on power system networks using the `pandapower` library.

# #### 1. Network Construction from Custom Modules

# In[4]:


# Import required libraries for network analysis and data handling
import pandapower as pp
import pandas as pd
from buses import create_buses
from lines import create_lines
from transformers import create_transformers
from loads import create_loads, group_bus_by_substation
from generators import create_gens

import sys
print("Python executable:", sys.executable)
print("Python version:", sys.version)


# Create Empty Network
net = pp.create_empty_network()

# Create Buses
SHE_BUS, SPT_BUS, OFTO_BUS, NGET_bus_lookup = create_buses(net)


# Create Lines
create_lines(net, NGET_bus_lookup, SHE_BUS, SPT_BUS, OFTO_BUS)

# create Transformers
create_transformers(net, NGET_bus_lookup, SHE_BUS, SPT_BUS, OFTO_BUS)

# Create Loads
substation_group = group_bus_by_substation(NGET_bus_lookup)
create_loads(net, NGET_bus_lookup, substation_group)

# create generators
create_gens(net, NGET_bus_lookup, substation_group)

# slack bus
pp.create_ext_grid(net, SPT_BUS, vm_pu = 1, name="SPT BUS")

# Save the network to an Excel file for persistent storage and easy loading
pp.to_excel(net, 'network_v0.xlsx')


# #### 2. Network Topology Analysis: Island Detection
# This section loads the previously saved network and performs a topological analysis to identify disconnected components, also known as 'islands'. Power flow calculations can only be successfully performed on a connected network. Detecting islands is a crucial step for troubleshooting convergence issues, as disconnected sections of the grid cannot solve. The sizes and a few bus indices of each detected island are printed.

# In[5]:


import pandapower as pp
import pandapower.topology as ppt
import networkx as nx

# Load the network
net = pp.from_excel('network_v0.xlsx')
print(net)

# Create the networkx graph
graph = ppt.create_nxgraph(net)

# Find islands (connected components)
islands = list(ppt.connected_components(graph))
print(f"Found {len(islands)} island(s).")

# Print summary for each island (showing only size, not all indices)
for i, isl in enumerate(islands):
    print(f"Island {i+1}: {len(isl)} buses (bus indices: {list(isl)[:5]}...)" if len(isl) > 5 else f"Island {i+1}: {isl}")


# #### 3. Power Flow Analysis on the Main Connected Component (Island 2)
# The following operations are performed:
# 1. **Network Isolation**: A deep copy of the original network is made, and all buses *not* belonging to Island 2 are removed.
# 2. **Generator & Load Configuration**: Generators are set to be controllable for OPF, loads are fixed, and minimum generation for generators is set to zero. Load levels are also scaled down (e.g., to 60% of original values) to create a specific scenario.
# 3. **DCPF Execution**: A DC Power Flow (DCPF) is run to determine voltage angles and power flows under the specified conditions. Its convergence status is reported.
# 4. **DCOPF Execution**: A DC Optimal Power Flow (DCOPF) is then attempted. This aims to minimize generation costs while respecting operational constraints. Its convergence status is reported, and any errors are caught and displayed for troubleshooting.

# In[ ]:


import pandapower as pp
import pandapower.topology as ppt
import matplotlib.pyplot as plt
import warnings
import copy

warnings.filterwarnings('ignore')

# Get the buses for the largest island (Island 2, assuming it's the second in the list)
island2_buses = list(islands[1])

# Create a deep copy of the network to modify it without affecting the original
island2_net = copy.deepcopy(net)

# Configure controllable elements for DCOPF
island2_net.gen['controllable'] = True
island2_net.load['controllable'] = False
island2_net.gen['min_p_mw'] = 0

# Apply specific load scaling for the scenario being tested
island2_net.load.loc[:,'p_mw'] = island2_net.load.loc[:,'p_mw'] * 0.5

# Remove buses not part of Island 2 from the copied network
buses_to_drop = list(set(island2_net.bus.index) - set(island2_buses))
pp.drop_buses(island2_net, buses_to_drop)

# Check for slack/external grid or generators in the isolated island
if island2_net.ext_grid.empty and island2_net.gen.empty:
    raise ValueError("No slack/ext_grid or generator in island 2; DC power flow cannot be run.")

# --- Run DC Power Flow (DCPF) ---
pp.rundcpp(island2_net)
print('DCPF converged:', island2_net.converged)

# --- Run DC Optimal Power Flow (DCOPF) ---
try:
    pp.rundcopp(island2_net)
    print('DCOPF converged:', island2_net.OPF_converged)
except Exception as e:
    print('DCOPF failed to converge')
    print('Error:', e)

with pd.ExcelWriter("dc_opf_results.xlsx") as writer:
    island2_net.res_bus.to_excel(writer, sheet_name="Bus Results")
    island2_net.res_line.to_excel(writer, sheet_name="Line Results")
    island2_net.res_gen.to_excel(writer, sheet_name="Generator Results")
    island2_net.res_load.to_excel(writer, sheet_name="Load Results")
    island2_net.res_ext_grid.to_excel(writer, sheet_name="External Grid Results")