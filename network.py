import pandapower as pp
import pandas as pd
import warnings
import os

from elements.buses import create_buses
from elements.lines import create_lines
from elements.transformers import create_transformers
from elements.loads import create_loads, group_bus_by_substation
from elements.generators import create_gens
from utilities.island_cleanup import keep_largest_island 

warnings.filterwarnings('ignore')

# --- Create Empty Network ---
net = pp.create_empty_network()

# --- Create Elements ---
SHE_BUS, SPT_BUS, OFTO_BUS, NGET_bus_lookup = create_buses(net)
create_lines(net, NGET_bus_lookup, SHE_BUS, SPT_BUS, OFTO_BUS)
create_transformers(net, NGET_bus_lookup, SHE_BUS, SPT_BUS, OFTO_BUS)
substation_group = group_bus_by_substation(NGET_bus_lookup)
create_loads(net, NGET_bus_lookup, substation_group)
create_gens(net, NGET_bus_lookup, substation_group)

# Slack Bus
pp.create_ext_grid(net, SPT_BUS, vm_pu=1, name="SPT BUS")

# Save Network for reference
pp.to_excel(net, os.path.join("results", "network_v0.xlsx"))

# --- Remove all but largest island ---
net = keep_largest_island(net)


# Apply load scaling
net.load.loc[:, 'p_mw'] *= 0.8

# Ensure we still have a slack or generators
if net.ext_grid.empty and net.gen.empty:
    raise ValueError("No slack/ext_grid or generator in the largest island; cannot run power flow.")

# --- Run DC Power Flow ---
pp.rundcpp(net)
print('DCPF converged:', net.converged)

# --- Run DC Optimal Power Flow ---
try:
    pp.rundcopp(net)
    print('DCOPF converged:', net.OPF_converged)
except Exception as e:
    print('DCOPF failed to converge')
    print('Error:', e)

# Ensure the results folder exists
os.makedirs("results", exist_ok=True)

# --- Save Results ---
with pd.ExcelWriter(os.path.join("results", "dc_opf_results.xlsx")) as writer:
    net.res_bus.to_excel(writer, sheet_name="Bus Results")
    net.res_line.to_excel(writer, sheet_name="Line Results")
    net.res_gen.to_excel(writer, sheet_name="Generator Results")
    net.res_load.to_excel(writer, sheet_name="Load Results")
    net.res_ext_grid.to_excel(writer, sheet_name="External Grid Results")