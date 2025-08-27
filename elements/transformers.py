import pandapower as pp
import pandas as pd
from elements.substations import NGET_SUBSTATIONS, SHE_SUBSTATIONS, SPT_SUBSTATIONS, OFTO_SUBSTATIONS

# === Transformer Creation Function ===

def create_transformers(net, NGET_bus_lookup, SHE_BUS, SPT_BUS, OFTO_BUS, network_file, transformer_sheet):
    df = pd.read_excel(network_file, sheet_name=transformer_sheet, skiprows=1)
    for idx in df.index:
        from_bus_name = df.at[idx, "Node 1"]
        to_bus_name = df.at[idx, "Node 2"]
        x_pu = df.at[idx, "X (" + '%' + " on 100MVA)"]/100
        mva_rating = df.at[idx, "Rating (MVA)"]

        # Assign bus indices
        if from_bus_name[:4] in NGET_SUBSTATIONS:
            from_bus = NGET_bus_lookup[from_bus_name]
        elif from_bus_name[:4] in SHE_SUBSTATIONS:
            from_bus = SHE_BUS
        elif from_bus_name[:4] in SPT_SUBSTATIONS:
            from_bus = SPT_BUS
        elif from_bus_name[:4] in OFTO_SUBSTATIONS:
            from_bus = OFTO_BUS
        else:
            print("Unhandled from_bus:", from_bus_name)
            continue

        if to_bus_name[:4] in NGET_SUBSTATIONS:
            to_bus = NGET_bus_lookup[to_bus_name]
        elif to_bus_name[:4] in SHE_SUBSTATIONS:
            to_bus = SHE_BUS
        elif to_bus_name[:4] in SPT_SUBSTATIONS:
            to_bus = SPT_BUS
        elif to_bus_name[:4] in OFTO_SUBSTATIONS:
            to_bus = OFTO_BUS
        else:
            print("Unhandled to_bus:", to_bus_name)
            continue

        # Create transformer in the form of an impedance element
        pp.create_impedance(net,
            from_bus=from_bus,
            to_bus=to_bus,
            rft_pu=0,
            xft_pu=x_pu,
            sn_mva=mva_rating
        )
    print("Transformer creation complete.")            


