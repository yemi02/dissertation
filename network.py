import pandapower as pp
import pandas as pd
import pandapower.topology as top
import networkx as nx
from buses import create_buses
from lines import create_lines
from transformers import create_transformers
from loads import create_loads, group_bus_by_substation
from generators import create_gens


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
net.load["controllable"] = False


# create generators
create_gens(net, NGET_bus_lookup, substation_group)

# slack bus
slack = pp.create_gen(net, bus=SPT_BUS, p_mw=0, vm_pu=1.0, controllable=True, min_p_mw=0, max_p_mw=100, slack=True)
pp.create_poly_cost(net, element=slack, et='gen', cp1_eur_per_mw=100)    



pp.drop_buses(net, [0, 2, 450, 451, 452, 453], drop_elements=True)

# unsupplied = top.unsupplied_buses(net)
# print(f"Unsupplied buses: {unsupplied}")


# G = top.create_nxgraph(net)  # This creates the network graph
# num_components = nx.number_connected_components(G)

# print("Connected components:", num_components)

# components = list(nx.connected_components(G))
# for i, comp in enumerate(components):
# #     print(f"Component {i+1} has {len(comp)} buses: {sorted(comp)}")
#         continue



# if not net.ext_grid.empty:
#     ext_grid_bus = net.ext_grid.bus.iloc[0]
    
#     if ext_grid_bus in net.bus.index:
#         try:
#             connected_buses = top.connected_component(net, ext_grid_bus)
#             for load_bus in net.load.bus.unique():
#                 if load_bus not in connected_buses:
#                     print(f"Bus {load_bus} with load is not connected to ext_grid")
#         except KeyError as e:
#             print(f"Error: Bus {e} not found in the internal network graph.")
#     else:
#         print(f"ext_grid bus {ext_grid_bus} not found in net.bus.")
# else:
#     print("No ext_grid defined in the network.")





# # Combine all source buses
# source_buses = net.ext_grid.bus.tolist() + net.gen.bus.tolist()

# connected_buses = set()
# for bus in source_buses:
#     if bus in net.bus.index:
#         try:
#             component = top.connected_component(net, bus)
#             connected_buses.update(component)
#         except KeyError:
#             print(f"Bus {bus} not found in graph.")
#     else:
#         print(f"Bus {bus} not in net.bus.")

# disconnected = set(net.bus.index) - connected_buses
# print(f"Disconnected buses: {disconnected}")



# Run OPF
try:
    pp.rundcpp(net)
except pp.LoadflowNotConverged:
    print("Power flow did not converge.")


print(net)



with pd.ExcelWriter("dc_opf_results.xlsx") as writer:
    net.res_bus.to_excel(writer, sheet_name="Bus Results")
    net.res_line.to_excel(writer, sheet_name="Line Results")
    net.res_gen.to_excel(writer, sheet_name="Generator Results")
    net.res_load.to_excel(writer, sheet_name="Load Results")
    net.res_ext_grid.to_excel(writer, sheet_name="External Grid Results")