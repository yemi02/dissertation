import pandas as pd

# Initialize empty sets for each operator's substations (sets prevent duplicates)
NGET_SUBSTATIONS = set()
SHE_SUBSTATIONS = set()
SPT_SUBSTATIONS = set()
OFTO_SUBSTATIONS = set()

# Define each operator with their respective sheet name and substation set reference
operators = [
    {
        "name": "NGET",
        "sheet_name": "B-1-1c",
        "substations": NGET_SUBSTATIONS
    },
    {
        "name": "SHE",
        "sheet_name": "B-1-1a",
        "substations": SHE_SUBSTATIONS
    },
    {
        "name": "SPT",
        "sheet_name": "B-1-1b",
        "substations": SPT_SUBSTATIONS
    },
    {
        "name": "OFTO",
        "sheet_name": "B-1-1d",
        "substations": OFTO_SUBSTATIONS
    },
]

# Read substation data from each operator's sheet and populate the corresponding set
for operator in operators:
    df = pd.read_excel("ETYS_B.xlsx", sheet_name=operator["sheet_name"], skiprows=1)
    for idx in df.index:
        site_code = df.at[idx, "Site Code"]
        operator["substations"].add(site_code)


