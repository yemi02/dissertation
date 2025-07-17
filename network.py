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

# Creating Demands
create_loads(net, NGET_bus_lookup)

print(net) 
