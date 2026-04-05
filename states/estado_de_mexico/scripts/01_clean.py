#!/usr/bin/env python3
"""
01_clean.py — Estado de Mexico GHG Inventory (IEEGyCEI-2022)
=============================================================
Case:           Mexico State-Level CPI Overlap — Estado de Mexico
Estimation Tier: Tier 3 (published state inventory)
Base year:       2022
GWPs:           AR5 (CH4=28, N2O=265)
Data source:    Inventario Estatal de Emisiones de Gases y Compuestos de Efecto
                Invernadero del Estado de Mexico (IEEGyCEI-2022).
                Published inventory with IPCC 2006 sector detail.
Grand total:    36,384.9 GgCO2e (= KtCO2e)
Uncertainty:    +/- 5.47% (inventory's own estimate)
"""

import pandas as pd
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPT_DIR)
PROC_DIR = os.path.join(BASE_DIR, "data", "processed")
os.makedirs(PROC_DIR, exist_ok=True)

# =====================================================================
# SECTOR TOTALS FROM IEEGyCEI-2022 (GgCO2e = KtCO2e)
# =====================================================================

inventory_sectors = [
    # Energy sector (22,452.9 total)
    ("1.A.1.a", "Electricity generation",           "ELECTRICITY",    5606.9),
    ("1.A.2",   "Manufacturing & construction",      "MANUFACTURING",  6111.1),
    ("1.A.3",   "Transport",                         "TRANSPORT",      7309.8),
    ("1.A.4",   "Other sectors (comm/res/agri)",     "OTHER_SECTORS",  3425.1),
    ("1.B",     "Fugitive emissions",                "FUGITIVE",          0.0),

    # IPPU sector (4,639.5 total)
    ("2.A.1",   "Cement production",                 "IPPU",            582.5),
    ("2.A.2",   "Lime production",                   "IPPU",            186.7),
    ("2.A.3",   "Glass production",                  "IPPU",            123.5),
    ("2.A.4",   "Other carbonates (limestone+soda ash)", "IPPU",       2417.1),
    ("2.C",     "Metals (lead + zinc)",              "IPPU",             70.7),
    ("2.D",     "Non-energy products (lubricants+wax)", "IPPU",        1259.1),

    # AFOLU sector
    ("3.x",     "AFOLU (agriculture/forestry/land use)", "AFOLU",      3511.7),

    # Waste sector
    ("4.x",     "Waste (solid waste + wastewater)",  "WASTE",          5780.8),
]

df = pd.DataFrame(inventory_sectors,
                   columns=["ipcc_2006", "description", "broad_category",
                            "central_KtCO2e"])

# =====================================================================
# CROSS-VALIDATE SECTOR SUMS
# =====================================================================

energy_total = df[df["ipcc_2006"].str.startswith("1.")]["central_KtCO2e"].sum()
ippu_total = df[df["ipcc_2006"].str.startswith("2.")]["central_KtCO2e"].sum()
afolu_total = df[df["ipcc_2006"].str.startswith("3.")]["central_KtCO2e"].sum()
waste_total = df[df["ipcc_2006"].str.startswith("4.")]["central_KtCO2e"].sum()
grand_total = df["central_KtCO2e"].sum()

print("=" * 65)
print("ESTADO DE MEXICO GHG INVENTORY — IEEGyCEI-2022 (Tier 3)")
print("=" * 65)

# Validate against published totals
assert abs(energy_total - 22452.9) < 0.2, f"Energy mismatch: {energy_total}"
assert abs(ippu_total - 4639.5) < 0.2, f"IPPU mismatch: {ippu_total}"
assert abs(afolu_total - 3511.7) < 0.2, f"AFOLU mismatch: {afolu_total}"
assert abs(waste_total - 5780.8) < 0.2, f"Waste mismatch: {waste_total}"
assert abs(grand_total - 36384.9) < 0.2, f"Grand total mismatch: {grand_total}"

print(f"  Energy sector:  {energy_total:>10,.1f} KtCO2e  (published: 22,452.9)")
print(f"  IPPU sector:    {ippu_total:>10,.1f} KtCO2e  (published:  4,639.5)")
print(f"  AFOLU sector:   {afolu_total:>10,.1f} KtCO2e  (published:  3,511.7)")
print(f"  Waste sector:   {waste_total:>10,.1f} KtCO2e  (published:  5,780.8)")
print(f"  ---")
print(f"  GRAND TOTAL:    {grand_total:>10,.1f} KtCO2e  (published: 36,384.9)")
print(f"  = {grand_total/1000:,.2f} MtCO2e")
print(f"\n  Cross-validation: ALL SECTOR SUMS MATCH ✓")

# =====================================================================
# UNCERTAINTY: ±5.47% (inventory's own estimate)
# =====================================================================

UNC_PCT = 0.0547
df["low_KtCO2e"] = (df["central_KtCO2e"] * (1 - UNC_PCT)).round(1)
df["high_KtCO2e"] = (df["central_KtCO2e"] * (1 + UNC_PCT)).round(1)

total_low = df["low_KtCO2e"].sum()
total_high = df["high_KtCO2e"].sum()

print(f"\n  Uncertainty: ±{UNC_PCT*100:.2f}%")
print(f"  Range: {total_low:,.1f} – {total_high:,.1f} KtCO2e")

# =====================================================================
# SUB-SECTOR DETAIL (for documentation and overlap model)
# =====================================================================

manufacturing_sub = [
    ("1.A.2.a", "Transport equipment manufacturing",   1641.6),
    ("1.A.2.b", "Non-metallic minerals manufacturing", 1061.1),
    ("1.A.2.c", "Chemicals manufacturing",              735.8),
    ("1.A.2.d", "Food & beverages manufacturing",       672.7),
    ("1.A.2.e", "Pulp & paper manufacturing",           549.6),
    ("1.A.2.f", "Unspecified industry",                  745.8),
    ("1.A.2.g", "Iron & steel manufacturing",            233.4),
    ("1.A.2.h", "Non-ferrous metals manufacturing",      197.7),
    ("1.A.2.i", "Textiles manufacturing",                219.8),
    ("1.A.2.j", "Machinery manufacturing",                38.0),
    ("1.A.2.k", "Wood manufacturing",                     15.6),
]
mfg_sum = sum(s[2] for s in manufacturing_sub)
assert abs(mfg_sum - 6111.1) < 0.2, f"Manufacturing sub-sector mismatch: {mfg_sum}"

transport_sub = [
    ("1.A.3.b", "Terrestrial transport",  6993.1),
    ("1.A.3.a", "Aviation",                249.4),
    ("1.A.3.c", "Rail transport",           67.4),
]
trn_sum = sum(s[2] for s in transport_sub)
assert abs(trn_sum - 7309.9) < 0.2, f"Transport sub-sector mismatch: {trn_sum}"

other_sectors_sub = [
    ("1.A.4.a", "Commercial/institutional", 515.5),
    ("1.A.4.b", "Residential",            2428.6),
    ("1.A.4.c", "Agricultural combustion",  481.0),
]
oth_sum = sum(s[2] for s in other_sectors_sub)
assert abs(oth_sum - 3425.1) < 0.2, f"Other sectors sub-sector mismatch: {oth_sum}"

print(f"\n  Manufacturing sub-sector sum: {mfg_sum:,.1f} (matches 6,111.1) ✓")
print(f"  Transport sub-sector sum:    {trn_sum:,.1f} (matches 7,309.8) ✓")
print(f"  Other sectors sub-sector sum:{oth_sum:,.1f} (matches 3,425.1) ✓")

print(f"\nBROAD CATEGORY BREAKDOWN:")
for cat, grp in df.groupby("broad_category")["central_KtCO2e"].sum().sort_values(ascending=False).items():
    print(f"  {cat:20s}: {grp:>10,.1f} KtCO2e ({grp/grand_total*100:5.1f}%)")

# =====================================================================
# SAVE
# =====================================================================

out = df[["ipcc_2006", "description", "broad_category",
          "central_KtCO2e", "low_KtCO2e", "high_KtCO2e"]]
out.to_csv(os.path.join(PROC_DIR, "estado_de_mexico_inventory.csv"), index=False)

summary = df.groupby("broad_category").agg(
    central_KtCO2e=("central_KtCO2e", "sum"),
    low_KtCO2e=("low_KtCO2e", "sum"),
    high_KtCO2e=("high_KtCO2e", "sum")
).round(1)
summary.to_csv(os.path.join(PROC_DIR, "estado_de_mexico_inventory_summary.csv"))

# Sub-sector detail CSV
sub_detail = pd.DataFrame(
    manufacturing_sub + transport_sub + other_sectors_sub,
    columns=["ipcc_2006", "description", "central_KtCO2e"]
)
sub_detail.to_csv(os.path.join(PROC_DIR, "estado_de_mexico_subsector_detail.csv"), index=False)

ref = pd.DataFrame([
    {"parameter": "inventory_total_KtCO2e", "value": round(grand_total, 1)},
    {"parameter": "estimation_tier", "value": 3},
    {"parameter": "base_year", "value": 2022},
    {"parameter": "gwp_basis", "value": "AR5"},
    {"parameter": "uncertainty_pct", "value": 5.47},
    {"parameter": "source", "value": "IEEGyCEI-2022"},
    {"parameter": "energy_total_KtCO2e", "value": round(energy_total, 1)},
    {"parameter": "ippu_total_KtCO2e", "value": round(ippu_total, 1)},
    {"parameter": "afolu_total_KtCO2e", "value": round(afolu_total, 1)},
    {"parameter": "waste_total_KtCO2e", "value": round(waste_total, 1)},
])
ref.to_csv(os.path.join(PROC_DIR, "estado_de_mexico_reference_data.csv"), index=False)

for f in ["estado_de_mexico_inventory.csv", "estado_de_mexico_inventory_summary.csv",
           "estado_de_mexico_subsector_detail.csv", "estado_de_mexico_reference_data.csv"]:
    print(f"Saved: {os.path.join(PROC_DIR, f)}")
print("\n01_clean.py complete.")
