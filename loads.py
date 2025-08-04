import pandapower as pp
import pandas as pd
from collections import defaultdict
from substations import NGET_SUBSTATIONS, SHE_SUBSTATIONS, SPT_SUBSTATIONS, OFTO_SUBSTATIONS

# === Utility Functions ===

def group_bus_by_substation(NGET_bus_lookup):
    substation_group = defaultdict(list)

    for bus_name, bus_idx in NGET_bus_lookup.items():
        substation_name = bus_name[:4]
        if substation_name in NGET_SUBSTATIONS:
            substation_group[substation_name].append(bus_name)
    substation_group = dict(substation_group)
    return substation_group

# === Load Creation Function ===

def create_loads(net, NGET_bus_lookup, substation_group):

    # === Initialize accumulators and containers ===

    load_per_substation = {substation: 0 for substation in NGET_SUBSTATIONS}

    NGET_LOAD_BUS_NOT_EXISTING = set()
    SHE_LOAD_BUS = {}
    SPT_LOAD_BUS = {}
    OFTO_LOAD_BUS = {}
    NONEXISTENT_LOAD_BUS = {}
    total_NGET_connected = 0
    total_NGET_load_not_connected = 0
    total_SHE_load = 0
    total_SPT_load = 0
    total_OFTO_load = 0
    total_load_missing = 0

    df = pd.read_excel("ETYS_G.xlsx", sheet_name="demand data 2023", skiprows=9)
    for idx in df.index:
        bus = df.at[idx, "Node"]
        substation = bus[:4]
        p_mw = df.at[idx, "24/25 MW"]

        if substation in NGET_SUBSTATIONS:
            if bus in NGET_bus_lookup:
                pp.create_load(net, NGET_bus_lookup[bus], p_mw, controllable=False)
                total_NGET_connected += p_mw
            elif substation in load_per_substation:

                load_per_substation[substation] += p_mw
                total_NGET_connected += p_mw
                
            else:
                NGET_LOAD_BUS_NOT_EXISTING.add(bus)
                total_NGET_load_not_connected += p_mw

        elif bus[:4] in SHE_SUBSTATIONS:
            SHE_LOAD_BUS[bus] = p_mw
            total_SHE_load += p_mw

        elif bus[:4] in SPT_SUBSTATIONS:
            SPT_LOAD_BUS[bus] = p_mw
            total_SPT_load += p_mw

        elif bus[:4] in OFTO_SUBSTATIONS:
            OFTO_LOAD_BUS[bus] = p_mw
            total_OFTO_load += p_mw
        else:
            NONEXISTENT_LOAD_BUS[bus] = p_mw
            total_load_missing += p_mw

    # Distirbuting load evenly among buses

    for substation, total_load in load_per_substation.items():
        buses = substation_group.get(substation, [])

        if not buses:
            # print("Buses not found for substation", substation)
            continue

        load_per_bus = total_load/len(buses)

        for bus_name in buses:
            bus_idx = NGET_bus_lookup[bus_name]
            if bus_idx is not None:
                pp.create_load(net, bus_idx, p_mw=load_per_bus, controllable=False)
            else:
                # print(f"Bus {bus_name} not found in NGET_bus_lookup")
                continue                  

    print("Load creation complete.")
    