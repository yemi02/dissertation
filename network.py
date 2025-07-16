import pandapower as pp
import pandas as pd
from substation import NGET_SUBSTATIONS, SHE_SUBSTATIONS, SPT_SUBSTATIONS, OFTO_SUBSTATIONS
from buses import create_buses

# Creating an empty network
net = pp.create_empty_network()

# Creating Buses
SHE_BUS, SPT_BUS, OFTO_BUS, NGET_bus_lookup = create_buses(net)

# Creating lines
df = pd.read_excel("ETYS_B.xlsx", sheet_name="B-2-1c", skiprows=1)

# for idx in df.index:
#     if df.at[idx, "OHL Length (km)"] == 0 and df.at[idx, "Cable Length (km)"] == 0:
#         node1 = df.at[idx, "Node 1"]
#         node2 = df.at[idx, "Node 2"]

#         if (node1[:4] in NGET_SUBSTATIONS) and (node2[:4] in NGET_SUBSTATIONS):
            
#             if df.at[idx, "OHL Length (km)"] != 0:

#                 length = df.at[idx, "OHL Length (km)"]

#                 pp.create_line_from_parameters(
#                     net,
#                     from_bus=NGET_bus_lookup[node1],
#                     to_bus=NGET_bus_lookup[node2],
#                     length_km=length,
#                     r_ohm_per_km=0.0,       # ignored in DCPF
#                     x_ohm_per_km=x_ohm_per_km,
#                     c_nf_per_km=0.0,        # ignored in DCPF
#                     max_i_ka=I_max_kA
#                     )

print(net)

