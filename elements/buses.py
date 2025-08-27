import pandapower as pp
import pandas as pd
from elements.substations import NGET_SUBSTATIONS



# === Bus Creation Function ===

def create_buses(net, network_file, bus_sheet):
    def NGET_buses():

        bus_names = []
        sheet_names = bus_sheet

        for sheet_name in sheet_names:
            df = pd.read_excel(network_file, sheet_name=sheet_name, skiprows=1)
            
            for idx in df.index:
                bus_names.append(df.at[idx, "Node 1"])
                bus_names.append(df.at[idx, "Node 2"])

        buses = list(dict.fromkeys(bus_names))
        return buses

    # Creating (slack) Buses for other sub networks
    SHE_BUS = pp.create_bus(net, vn_kv=400, name="SHE_BUS")
    SPT_BUS = pp.create_bus(net, vn_kv=400, name="SPT_BUS")
    OFTO_BUS = pp.create_bus(net, vn_kv=400, name="OFTO_BUS")
    
    buses = NGET_buses()
    NGET_bus_lookup = {}

    # create bus
    for bus in buses:
        if bus[:4] in NGET_SUBSTATIONS:
            bus_idx = pp.create_bus(net, vn_kv=400, name=bus)
            NGET_bus_lookup[bus] = bus_idx # Store in lookup table

    print("Bus creation complete.")
    return SHE_BUS, SPT_BUS, OFTO_BUS, NGET_bus_lookup

