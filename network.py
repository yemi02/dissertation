import pandapower as pp
import pandas as pd
from substation import NGET_BUSES, SHE_BUSES, SPT_BUSES, OFTO_BUSES
from buses import create_buses

# Creating an empty network
net = pp.create_empty_network()

# Creating Buses
SHE_BUS, SPT_BUS, OFTO_BUS, NGET_bus_lookup = create_buses(net)

print(net)

