import pandapower as pp
import pandas as pd
from substation import NGET_SUBSTATIONS

def create_buses(net):
    """
    Creates buses in a pandapower network and returns a lookup dictionary.

    Returns:
    - bus_lookup: dict mapping bus name → pandapower bus index
    """

    # Creating (slack) Buses for other sub networks
    SHE_BUS = pp.create_bus(net, vn_kv=400, name="SHE_BUS")
    SPT_BUS = pp.create_bus(net, vn_kv=400, name="SPT_BUS")
    OFTO_BUS = pp.create_bus(net, vn_kv=400, name="OFTO_BUS")

    # Creating the buses for the NGET network
    busArr = []

    sheetNames = ["B-2-1c", "B-3-1c"]

    for sheetName in sheetNames:
        df = pd.read_excel("ETYS_B.xlsx", sheet_name=sheetName, skiprows=1)
        
        for idx in df.index:
            busArr.append(df.at[idx, "Node 1"])
            busArr.append(df.at[idx, "Node 2"])

    buses = list(dict.fromkeys(busArr))

    # Bus lookup table for lines and transformer creation
    NGET_bus_lookup = {}

    for bus in buses:
        substation = bus[:4] # gets the substation code
        
        if substation in NGET_SUBSTATIONS:
            
            # create bus
            bus_idx = pp.create_bus(net, vn_kv=400, name=bus)
            
            # Store in lookup table
            NGET_bus_lookup[bus] = bus_idx

    return SHE_BUS, SPT_BUS, OFTO_BUS, NGET_bus_lookup