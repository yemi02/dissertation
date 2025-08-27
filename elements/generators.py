import pandapower as pp
import pandas as pd
from rapidfuzz import process, fuzz
import re


# -----------------
# Helper Functions
# -----------------
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
        return "Other"
    pt = plant_type_str.lower()

    if "coal" in pt:
        return "Coal"
    elif "wind" in pt:
        return "Wind"
    elif "pv array" in pt or "solar" in pt:
        return "Solar PV"
    elif "nuclear" in pt:
        return "Nuclear"
    elif "hydro" in pt:
        return "Hydro"
    elif "pump storage" in pt or "pumped storage" in pt:
        return "Pumped Storage"
    elif "ccgt" in pt:
        return "CCGT"
    elif "ocgt" in pt:
        return "OCGT"
    elif "chp" in pt:
        return "CHP"
    elif "oil" in pt:
        return "Oil"
    elif "biomass" in pt or "thermal" in pt:
        return "Biomass"
    elif "energy storage" in pt or "battery storage" in pt or "storage" in pt:
        return "Battery Storage"
    else:
        return "Other"

def get_best_match(name, site_names_clean):
    match = process.extractOne(name, site_names_clean, scorer=fuzz.WRatio)
    if match:
        return match[0], match[1]
    return None, 0


# -----------------
# Main Generator Creation
# -----------------
def create_gens(net, NGET_bus_lookup, substation_group, gen_file, gen_sheet, network_file, substation_sheet):

    def load_substations():
        substations = []
        for sheet in substation_sheet:
            sub_df = pd.read_excel(network_file, sheet_name=sheet, skiprows=1)
            sub_df = sub_df.dropna(subset=["Site Name", "Site Code"]).copy()
            sub_df["Cleaned Site"] = sub_df["Site Name"].apply(clean_name)
            substations.append(sub_df[["Site Name", "Site Code", "Cleaned Site"]])
        sub_df = pd.concat(substations, ignore_index=True)
        sub_df = sub_df.drop_duplicates(subset=["Cleaned Site"])
        return sub_df

    # Load TEC Register
    gen_df = pd.read_excel(gen_file, sheet_name=gen_sheet, skiprows=1)
    gen_df = gen_df.dropna(subset=["Project Status", "HOST TO"])
    gen_df["Project Status"] = gen_df["Project Status"].str.strip().str.lower()
    gen_df["HOST TO"] = gen_df["HOST TO"].str.strip().str.upper()

    # Filter only built NGET generators
    gen_df = gen_df[
        (gen_df["Project Status"] == "built") &
        (gen_df["HOST TO"] == "NGET")
    ].copy()

    # Clean names and map categories
    gen_df["Cleaned Site"] = gen_df["Connection Site"].apply(clean_name)
    gen_df["LCOE Category"] = gen_df["Plant Type"].apply(map_to_lcoe_category)

    # Load substations and match
    sub_df = load_substations()
    site_names_clean = sub_df["Cleaned Site"].tolist()
    gen_df["Matched Site"], gen_df["Match Score"] = zip(*gen_df["Cleaned Site"].map(
        lambda x: get_best_match(x, site_names_clean)
    ))

    # Merge generators with substations
    matched_df = pd.merge(
        gen_df,
        sub_df,
        left_on="Matched Site",
        right_on="Cleaned Site",
        how="left",
        suffixes=("", "_sub")
    )

    # Keep only needed columns — each row is ONE generator
    final_matched = matched_df[[
        "Connection Site", "Site Code", "Site Name",
        "MW Connected", "Match Score", "LCOE Category"
    ]].copy()

    # Fixed costs €/MWh
    fixed_costs = {
        "Wind": 10,
        "Solar PV": 15,
        "Nuclear": 20,
        "Hydro": 40,
        "Pumped Storage": 65,
        "CCGT": 50,
        "OCGT": 60,
        "CHP": 90,
        "Oil": 55,
        "Biomass": 35,
        "Other": 70,
        "Coal": 80,
        "Battery Storage": 65
    }

    final_matched["Fixed Cost"] = final_matched["LCOE Category"].map(fixed_costs).fillna(1000)

    # Clear old poly_cost
    if not net.poly_cost.empty:
        net.poly_cost.drop(net.poly_cost.index, inplace=True)

    # Loop through each generator row
    for _, row in final_matched.iterrows():
        site_code = row["Site Code"]
        total_mw = row["MW Connected"]
        fixed_cost = row["Fixed Cost"]
        gen_type = row["LCOE Category"]

        if site_code not in substation_group:
            continue

        buses = substation_group[site_code]
        if not buses:
            continue

        mw_per_bus = total_mw / len(buses)

        for bus_name in buses:
            if bus_name in NGET_bus_lookup:
                bus_idx = NGET_bus_lookup[bus_name]

                # Create generator
                pp.create_gen(
                    net, bus=bus_idx, p_mw=0.0, min_p_mw=0.0,
                    max_p_mw=mw_per_bus, name=gen_type, controllable=True
                )

                # Add cost
                gen_idx = net.gen.index[-1]
                pp.create_poly_cost(
                    net, element=gen_idx, et='gen',
                    cp0_eur=0.0,
                    cp1_eur_per_mw=fixed_cost,
                    cp2_eur_per_mw2=0.0
                )

    print("Generator creation complete.")
