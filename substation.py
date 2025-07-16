import pandas as pd

# Sheet Names
sheetNames = ["B-2-1a", "B-2-1b", "B-2-1c", "B-2-1d", "B-3-1a", "B-3-1b", "B-3-1c", "B-3-1d"]

NGET = {
    "sheetName": "B-1-1c",
    "circuit": "B-2-1c",
    "trafo": "B-3-1c",
    "SUBSTATIONS": []
}

SHE = {
    "sheetName": "B-1-1a",
    "circuit": "B-2-1a",
    "trafo": "B-3-1a",
    "SUBSTATIONS": []
}

SPT = {
    "sheetName": "B-1-1b",
    "circuit": "B-2-1b",
    "trafo": "B-3-1b",
    "SUBSTATIONS": []
}

OFTO = {
    "sheetName": "B-1-1d",
    "circuit": "B-2-1d",
    "trafo": "B-3-1d",
    "SUBSTATIONS": []
}

for sheetName in sheetNames:
    df = pd.read_excel("ETYS_B.xlsx", sheet_name=sheetName, skiprows=1)
    busArr = []
    for idx in df.index:
        busArr.append(df.at[idx, "Node 1"])
        busArr.append(df.at[idx, "Node 2"])

allBuses = list(dict.fromkeys(busArr))

# Getting substation code for each Network
# NGET SUBSTATION CODES
df = pd.read_excel("ETYS_B.xlsx", sheet_name=(NGET["sheetName"]), skiprows=1)
for idx in df.index:
    NGET["SUBSTATIONS"].append(df.at[idx, "Site Code"])

# SHE SUBSTATION CODES
df = pd.read_excel("ETYS_B.xlsx", sheet_name=(SHE["sheetName"]), skiprows=1)
for idx in df.index:
    SHE["SUBSTATIONS"].append(df.at[idx, "Site Code"])

# SPT SUBSTATION CODES
df = pd.read_excel("ETYS_B.xlsx", sheet_name=(SPT["sheetName"]), skiprows=1)
for idx in df.index:
    SPT["SUBSTATIONS"].append(df.at[idx, "Site Code"])

# OFTO SUBSTATION CODES
df = pd.read_excel("ETYS_B.xlsx", sheet_name=(OFTO["sheetName"]), skiprows=1)
for idx in df.index:
    OFTO["SUBSTATIONS"].append(df.at[idx, "Site Code"])

NGET_SUBSTATIONS = NGET["SUBSTATIONS"]
SHE_SUBSTATIONS = SHE["SUBSTATIONS"]
SPT_SUBSTATIONS = SPT["SUBSTATIONS"]
OFTO_SUBSTATIONS = OFTO["SUBSTATIONS"]


