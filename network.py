import pandapower as pp
import pandas as pd
from substations import NGET_SUBSTATIONS, SHE_SUBSTATIONS, SPT_SUBSTATIONS, OFTO_SUBSTATIONS
from buses import create_buses
from lines import create_lines
from transformers import create_transformers
from loads import create_loads


# Creating Empty Network
net = pp.create_empty_network()

# Creating Buses
SHE_BUS, SPT_BUS, OFTO_BUS, NGET_bus_lookup = create_buses(net)

# Creating Lines
create_lines(net, NGET_bus_lookup, SHE_BUS, SPT_BUS, OFTO_BUS)

# creating Transformers
create_transformers(net, NGET_bus_lookup, SHE_BUS, SPT_BUS, OFTO_BUS)

# Creating Demands // not completed yet
create_loads(net, NGET_bus_lookup)

# create generators // not completed yet
for bus_idx in net.bus.index:
        pp.create_gen(net, bus=bus_idx, p_mw=15, vm_pu=1.0, slack=False)

# slack bus
pp.create_ext_grid(net, bus=SPT_BUS, vm_pu = 1, name="SPT BUS")

# print(net.line[net.line.x_ohm_per_km == 0])
# print(net.impedance[net.impedance.xft_pu == 0])


pp.rundcpp(net)


with pd.ExcelWriter("dc_power_flow_results.xlsx") as writer:
    net.res_bus.to_excel(writer, sheet_name="Bus Results")
    net.res_line.to_excel(writer, sheet_name="Line Results")
    net.res_gen.to_excel(writer, sheet_name="Generator Results")
    net.res_load.to_excel(writer, sheet_name="Load Results")


print(net) 
