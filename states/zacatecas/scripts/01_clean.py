#!/usr/bin/env python3
"""
01_clean.py — Zacatecas GHG Inventory from EDGAR Gridded Data
==============================================================
Case:           Mexico State-Level CPI Overlap — Zacatecas
Estimation Tier: Tier 3 (EDGAR v8.0 gridded spatial disaggregation)
Base year:       2024 (EDGAR 2025 release)
GWPs:           AR5 (CH4=28, N2O=265)
Data source:    EDGAR 2025 GHG v8.0 — 0.1deg gridded emission NetCDF files,
                masked to Zacatecas state boundary using GADM Level 1 shapefile.
                665 grid cells, ~66,500 km2 (official 72,275 km2, -7.8% edge effect)
"""

import pandas as pd
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPT_DIR)
PROC_DIR = os.path.join(BASE_DIR, "data", "processed")
os.makedirs(PROC_DIR, exist_ok=True)

edgar_sectors = [
    ("ENE",              "1.A.1.a",   "Power industry",                    "ELECTRICITY",           378.766),
    ("REF_TRF",          "1.A.1.bc",  "Refining & transformation",         "REFINING",              168.183),
    ("IND",              "1.A.2",     "Manufacturing & construction",      "MANUFACTURING",         101.773),
    ("TNR_Aviation_LTO", "1.A.3.a",   "Aviation (landing/takeoff)",        "TRANSPORT",               1.911),
    ("TNR_Aviation_CDS", "1.A.3.a",   "Aviation (climb/descent)",          "TRANSPORT",              21.159),
    ("TNR_Aviation_CRS", "1.A.3.a",   "Aviation (cruise)",                 "TRANSPORT",              76.044),
    ("TRO",              "1.A.3.b",   "Road transportation",               "TRANSPORT",            2491.848),
    ("TNR_Other",        "1.A.3.ce",  "Rail & other transport",            "TRANSPORT",              61.873),
    ("TNR_Ship",         "1.A.3.d",   "Shipping",                          "TRANSPORT",               0.000),
    ("RCO",              "1.A.4",     "Buildings (residential/commercial)", "RESIDENTIAL_COMMERCIAL", 620.869),
    ("PRO_FFF",          "1.B.1-2",   "Fugitive emissions (coal/oil/gas)", "FUGITIVE",               12.818),
    ("NMM",              "2.A",       "Non-metallic minerals (cement/lime)","IPPU",                    0.060),
    ("CHE",              "2.B",       "Chemical industry",                 "IPPU",                   22.392),
    ("IRO",              "2.C",       "Iron & steel production",           "IPPU",                    0.000),
    ("NFE",              "2.C",       "Non-ferrous metals",                "IPPU",                    1.183),
    ("NEU",              "2.D",       "Non-energy use of fuels",           "IPPU",                    0.904),
    ("PRU_SOL",          "2.D-2G",    "Solvents & HFCs/product use",       "IPPU",                  175.709),
    ("ENF",              "3.A.1",     "Enteric fermentation",              "AFOLU",                1200.208),
    ("MNM",              "3.A.2",     "Manure management",                 "AFOLU",                 101.492),
    ("AGS",              "3.C",       "Agricultural soils",                "AFOLU",                1335.694),
    ("AWB",              "3.C.1b",    "Agricultural waste burning",        "AFOLU",                  27.990),
    ("N2O",              "3.C.5-6",   "Indirect N2O from agriculture",     "AFOLU",                 189.913),
    ("SWD_LDF",          "4.A",       "Solid waste disposal (landfills)",  "WASTE",                   3.745),
    ("SWD_INC",          "4.C",       "Waste incineration",                "WASTE",                   4.071),
    ("WWT",              "4.D",       "Wastewater treatment",              "WASTE",                  58.052),
    ("IDE",              "5.A",       "Indirect NOx/NH3 emissions",        "OTHER",                  88.438),
]

df = pd.DataFrame(edgar_sectors,
                   columns=["edgar_sector", "ipcc_2006", "description",
                            "broad_category", "central_KtCO2e"])

# Uncertainty bounds by category
unc = {
    "ELECTRICITY": (0.75, 1.25), "REFINING": (0.60, 1.40),
    "MANUFACTURING": (0.70, 1.30), "TRANSPORT": (0.80, 1.20),
    "RESIDENTIAL_COMMERCIAL": (0.75, 1.25), "FUGITIVE": (0.50, 1.50),
    "IPPU": (0.50, 1.50), "AFOLU": (0.70, 1.30),
    "WASTE": (0.50, 1.50), "OTHER": (0.60, 1.40),
}
df["low_KtCO2e"] = df.apply(lambda r: round(r["central_KtCO2e"] * unc.get(r["broad_category"], (0.5,1.5))[0], 2), axis=1)
df["high_KtCO2e"] = df.apply(lambda r: round(r["central_KtCO2e"] * unc.get(r["broad_category"], (0.5,1.5))[1], 2), axis=1)

total_c = df["central_KtCO2e"].sum()
total_l = df["low_KtCO2e"].sum()
total_h = df["high_KtCO2e"].sum()

print("=" * 65)
print("ZACATECAS GHG INVENTORY — EDGAR 2025 Gridded (Tier 3)")
print("=" * 65)
print(f"  Total: {total_c:,.1f} KtCO2e = {total_c/1000:,.2f} MtCO2e")
print(f"  Range: {total_l:,.1f} – {total_h:,.1f} KtCO2e")

print(f"\nBROAD CATEGORY BREAKDOWN:")
for cat in df.groupby("broad_category")["central_KtCO2e"].sum().sort_values(ascending=False).items():
    print(f"  {cat[0]:25s}: {cat[1]:8.1f} KtCO2e ({cat[1]/total_c*100:5.1f}%)")

out = df[["edgar_sector","ipcc_2006","description","broad_category","central_KtCO2e","low_KtCO2e","high_KtCO2e"]]
out.to_csv(os.path.join(PROC_DIR, "zacatecas_edgar_inventory.csv"), index=False)

summary = df.groupby("broad_category").agg(
    central_KtCO2e=("central_KtCO2e","sum"), low_KtCO2e=("low_KtCO2e","sum"), high_KtCO2e=("high_KtCO2e","sum")
).round(1)
summary.to_csv(os.path.join(PROC_DIR, "zacatecas_inventory_summary.csv"))

ref = pd.DataFrame([
    {"parameter": "edgar_gridded_total_KtCO2e", "value": round(total_c, 1)},
    {"parameter": "estimation_tier", "value": 3},
    {"parameter": "mask_cells", "value": 665},
    {"parameter": "mask_area_km2", "value": 66500},
    {"parameter": "official_area_km2", "value": 72275},
    {"parameter": "rene_2018_low_KtCO2e", "value": 1916.5},
    {"parameter": "rene_2018_high_KtCO2e", "value": 3137.8},
    {"parameter": "revenue_implied_2021_KtCO2e", "value": 2216.0},
])
ref.to_csv(os.path.join(PROC_DIR, "zacatecas_reference_data.csv"), index=False)

for f in ["zacatecas_edgar_inventory.csv","zacatecas_inventory_summary.csv","zacatecas_reference_data.csv"]:
    print(f"Saved: {os.path.join(PROC_DIR, f)}")
print("\n01_clean.py complete.")
