import pandapower as pp
import pandas as pd
from rapidfuzz import process, fuzz
import re

# Constants and helpers
NETWORK_SHEETS = ["B-1-1a", "B-1-1b", "B-1-1c", "B-1-1d"]

def clean_name(name):
    if not isinstance(name, str):
        return ""
    blacklist = [
        "substation", "offshore", "onshore", "station", "grid",
        "400kv", "275kv", "132kv", "132/33kv",
        "north", "south", "east",
        "wind", "farm", "hydro", "solar"
    ]
    name = name.lower()
    for word in blacklist:
        name = name.replace(word, "")
    name = re.sub(r"[^a-z0-9\s]", "", name)
    name = re.sub(r"\s+", " ", name).strip()
    return name.upper()

def map_to_lcoe_category(plant_type_str):
    if not isinstance(plant_type_str, str):
        return "Unknown"
    pt = plant_type_str.lower()
    if "energy storage" in pt or "storage" in pt:
        return "Battery Storage"
    gas_keywords = ["ccgt", "ocgt", "gas reciprocating", "chp", "advanced gas turbine", "agt", "oil & agt"]
    if any(keyword in pt for keyword in gas_keywords):
        return "Gas"
    if "nuclear" in pt:
        return "Nuclear"
    if "wind" in pt:
        return "Wind"
    if "pv array" in pt or "solar" in pt:
        return "Solar PV"
    if "hydro" in pt or "pump storage" in pt or "pumped storage" in pt:
        return "Hydro & Pumped"
    if "biomass" in pt or "thermal" in pt:
        return "Biomass & Thermal"
    if "reactive compensation" in pt or "demand" in pt or "waste" in pt:
        return "Other/Non-Gen"
    return "Other"

def get_best_match(name, site_names_clean):
    match = process.extractOne(name, site_names_clean, scorer=fuzz.WRatio)
    if match:
        return match[0], match[1]
    return None, 0

def load_substations():
    substations = []
    for sheet in NETWORK_SHEETS:
        sub_df = pd.read_excel("ETYS_documents/ETYS_B.xlsx", sheet_name=sheet, skiprows=1)
        sub_df = sub_df.dropna(subset=["Site Name", "Site Code"]).copy()
        sub_df["Cleaned Site"] = sub_df["Site Name"].apply(clean_name)
        substations.append(sub_df[["Site Name", "Site Code", "Cleaned Site"]])
    sub_df = pd.concat(substations, ignore_index=True)
    sub_df = sub_df.drop_duplicates(subset=["Cleaned Site"])
    return sub_df

def create_gens(net, NGET_bus_lookup, substation_group):
    total_generation_connected = 0
    gen_df = pd.read_excel("ETYS_documents/ETYS_F.xlsx", sheet_name="TEC Register", skiprows=1)
    gen_df = gen_df.dropna(subset=["Project Status", "HOST TO"])
    gen_df["Project Status"] = gen_df["Project Status"].str.strip().str.lower()
    gen_df["HOST TO"] = gen_df["HOST TO"].str.strip().str.upper()

    gen_df = gen_df[
        (gen_df["Project Status"] == "built") &
        (gen_df["HOST TO"] == "NGET")
    ].copy()

    gen_df["Cleaned Site"] = gen_df["Connection Site"].apply(clean_name)
    gen_df["LCOE Category"] = gen_df["Plant Type"].apply(map_to_lcoe_category)

    sub_df = load_substations()
    site_names_clean = sub_df["Cleaned Site"].tolist()

    gen_df["Matched Site"], gen_df["Match Score"] = zip(*gen_df["Cleaned Site"].map(lambda x: get_best_match(x, site_names_clean)))

    merged_df = pd.merge(
        gen_df,
        sub_df,
        left_on="Matched Site",
        right_on="Cleaned Site",
        how="left",
        suffixes=("", "_sub")
    )

    matched_df = merged_df[["Connection Site", "Site Code", "Site Name", "MW Connected", "Match Score", "LCOE Category"]].copy()

    final_matched = matched_df.groupby("Site Code").agg({
        "MW Connected": "sum",
        "Site Name": "first",
        "LCOE Category": lambda x: x.mode().iloc[0] if not x.mode().empty else "Unknown",
        "Match Score": "max"
    }).reset_index()

    # LCOE cost mappings (€/MWh)
    fixed_costs = {
        "Battery Storage": 100,
        "Gas": 50,
        "Nuclear": 20,
        "Wind": 10,
        "Solar PV": 10,
        "Hydro & Pumped": 30,
        "Biomass & Thermal": 60,
        "Other": 70,
        "Other/Non-Gen": 80
    }

    final_matched["Fixed Cost"] = final_matched["LCOE Category"].map(fixed_costs).fillna(1000)

    # Clear poly_cost to avoid duplicates
    net.poly_cost.drop(net.poly_cost.index, inplace=True)

    for _, row in final_matched.iterrows():
        site_code = row["Site Code"]
        total_mw = row["MW Connected"]
        fixed_cost = row["Fixed Cost"]

        total_generation_connected += total_mw

        if site_code not in substation_group:
            continue

        buses = substation_group[site_code]
        if not buses:
            continue

        mw_per_bus = total_mw / len(buses)

        for bus_name in buses:
            if bus_name in NGET_bus_lookup:
                bus_idx = NGET_bus_lookup[bus_name]

                # Create generator with max_p_mw = allocated, initial p_mw = 0
                pp.create_gen(net, bus=bus_idx, p_mw=0.0, min_p_mw=0.0, max_p_mw=mw_per_bus)

                gen_idx = net.gen.index[-1]

                # Assign cost using official API to avoid duplicates
                pp.create_poly_cost(net, element=gen_idx, et='gen',
                                    cp0_eur=0.0,
                                    cp1_eur_per_mw=fixed_cost,
                                    cp2_eur_per_mw2=0.0)
            else:
                continue

    print("Generator creation complete.")
    print("Total generation connected in network:", total_generation_connected, "MW")
