import pandas as pd
from user_input import network_file, substation_sheet

# Initialize empty sets for each operator's substations (sets prevent duplicates)
NGET_SUBSTATIONS = set()
SHE_SUBSTATIONS = set()
SPT_SUBSTATIONS = set()
OFTO_SUBSTATIONS = set()

# Define each operator with their respective sheet name and substation set reference
operators = [
    {
        "name": "NGET",
        "sheet_name": substation_sheet[2],
        "substations": NGET_SUBSTATIONS
    },
    {
        "name": "SHE",
        "sheet_name": substation_sheet[0],
        "substations": SHE_SUBSTATIONS
    },
    {
        "name": "SPT",
        "sheet_name": substation_sheet[1],
        "substations": SPT_SUBSTATIONS
    },
    {
        "name": "OFTO",
        "sheet_name": substation_sheet[3],
        "substations": OFTO_SUBSTATIONS
    },
]

# Read substation data from each operator's sheet and populate the corresponding set
for operator in operators:
    df = pd.read_excel(network_file, sheet_name=operator["sheet_name"], skiprows=1)
    for idx in df.index:
        site_code = df.at[idx, "Site Code"]
        operator["substations"].add(site_code)


