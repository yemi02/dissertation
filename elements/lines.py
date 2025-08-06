import pandapower as pp
import pandas as pd
import math
from elements.substations import NGET_SUBSTATIONS, SHE_SUBSTATIONS, SPT_SUBSTATIONS, OFTO_SUBSTATIONS


# === Utility Functions ===

def convert_x_from_pu_to_ohm_per_km(x_pu, length_km):
    s_base = 100_000_000  # 100 MVA
    v_base = 400_000      # 400 kV
    z_base = (v_base**2) / s_base
    x_ohm = (x_pu/100) * z_base
    return x_ohm / length_km

def convert_mva_to_ka(mva_rating):
    return ((mva_rating * 1_000_000) / ( math.sqrt(3) * 400_000)) / 1000

# === Line Creation Function ===

def create_lines(net, NGET_bus_lookup, SHE_BUS, SPT_BUS, OFTO_BUS):
    df = pd.read_excel("ETYS_documents/ETYS_B.xlsx", sheet_name="B-2-1c", skiprows=1)

    for idx in df.index:
        from_bus_name = df.at[idx, "Node 1"]
        to_bus_name = df.at[idx, "Node 2"]
        x_pu = df.at[idx, "X (" + '%' + " on 100 MVA)"]
        ka_rating = 1e10  # default very high value

        circuit_type = df.at[idx, "Circuit Type"]

        if circuit_type in ["OHL", "parallel OHL"]:
            length_km = df.at[idx, "OHL Length (km)"]
        elif circuit_type == "Cable":
            length_km = df.at[idx, "Cable Length (km)"]
            if (length_km == 0):
                length_km = 0.001
            if (x_pu == 0):
                x_pu = 0.001
        elif circuit_type in ["Zero Length", "Series Reactor", "Series Capacitor", "SSSC"]:
            length_km = 0.001
            if circuit_type == "Zero Length":
                x_pu = 0.001
        elif circuit_type in ["Composite", "parallel Composite"]:
            length_km = df.at[idx, "OHL Length (km)"] + df.at[idx, "Cable Length (km)"]
        else:
            print("Unhandled circuit type:", circuit_type)
            continue
        
        # Assign Line rating for NGET CIRCUITS
        if from_bus_name[:4] in NGET_SUBSTATIONS and to_bus_name[:4] in NGET_SUBSTATIONS:
            ka_rating = convert_mva_to_ka(df.at[idx, "Winter Rating (MVA)"])

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

        # Create line
        pp.create_line_from_parameters(
            net,
            from_bus=from_bus,
            to_bus=to_bus,
            length_km=length_km,
            r_ohm_per_km=0.0,
            x_ohm_per_km=convert_x_from_pu_to_ohm_per_km(x_pu, length_km),
            c_nf_per_km=0.0,
            max_i_ka=ka_rating,
            max_loading_percent=100
        )
    print("Line creation complete")