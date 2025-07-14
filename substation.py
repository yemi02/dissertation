import pandas as pd

# Sheet Names
sheetNames = ["B-2-1a", "B-2-1b", "B-2-1c", "B-2-1d", "B-3-1a", "B-3-1b", "B-3-1c", "B-3-1d"]

NGET = {
    "substation": "B-1-1c",
    "circuit": "B-2-1c",
    "trafo": "B-3-1c",
    "BUSES": []
}

SHE = {
    "substation": "B-1-1a",
    "circuit": "B-2-1a",
    "trafo": "B-3-1a",
    "BUSES": []
}

SPT = {
    "substation": "B-1-1b",
    "circuit": "B-2-1b",
    "trafo": "B-3-1b",
    "BUSES": []
}

OFTO = {
    "substation": "B-1-1d",
    "circuit": "B-2-1d",
    "trafo": "B-3-1d",
    "BUSES": []
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
df = pd.read_excel("ETYS_B.xlsx", sheet_name=(NGET["substation"]), skiprows=1)
for idx in df.index:
    NGET["BUSES"].append(df.at[idx, "Site Code"])

# SHE SUBSTATION CODES
df = pd.read_excel("ETYS_B.xlsx", sheet_name=(SHE["substation"]), skiprows=1)
for idx in df.index:
    SHE["BUSES"].append(df.at[idx, "Site Code"])

# SPT SUBSTATION CODES
df = pd.read_excel("ETYS_B.xlsx", sheet_name=(SPT["substation"]), skiprows=1)
for idx in df.index:
    SPT["BUSES"].append(df.at[idx, "Site Code"])

# OFTO SUBSTATION CODES
df = pd.read_excel("ETYS_B.xlsx", sheet_name=(OFTO["substation"]), skiprows=1)
for idx in df.index:
    OFTO["BUSES"].append(df.at[idx, "Site Code"])

NGET_BUSES = NGET["BUSES"]
SHE_BUSES = SHE["BUSES"]
SPT_BUSES = SPT["BUSES"]
OFTO_BUSES = OFTO["BUSES"]


