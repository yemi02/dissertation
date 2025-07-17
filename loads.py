import pandapower as pp
import pandas as pd
from substations import NGET_SUBSTATIONS, SHE_SUBSTATIONS, SPT_SUBSTATIONS, OFTO_SUBSTATIONS


# === Load Creation Function ===

def create_loads(net, NGET_bus_lookup):

    # === Initialize accumulators and containers ===

    NGET_LOAD_BUS_NOT_EXISTING = set()
    SHE_LOAD_BUS = {}
    SPT_LOAD_BUS = {}
    OFTO_LOAD_BUS = {}
    NONEXISTENT_LOAD_BUS = {}
    total_SHE_load = 0
    total_SPT_load = 0
    total_OFTO_load = 0
    total_load_missing = 0

    df = pd.read_excel("ETYS_G.xlsx", sheet_name="demand data 2023", skiprows=9)
    for idx in df.index:
        bus = df.at[idx, "Node"]
        p_mw = df.at[idx, "24/25 MW"]

        if bus[:4] in NGET_SUBSTATIONS:
            if bus in NGET_bus_lookup:
                pp.create_load(net, NGET_bus_lookup[bus], p_mw)
            else:
                NGET_LOAD_BUS_NOT_EXISTING.add(bus)

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

    print(total_SHE_load, total_SPT_load, total_OFTO_load, total_load_missing)
    print(len(NGET_LOAD_BUS_NOT_EXISTING), len(SHE_LOAD_BUS), len(SPT_LOAD_BUS), len(OFTO_LOAD_BUS), len(NONEXISTENT_LOAD_BUS))