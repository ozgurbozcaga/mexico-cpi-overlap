"""
01_clean.py — Queretaro Carbon Pricing Overlap Analysis
========================================================
Case: Mexico — Queretaro state carbon tax x Federal carbon tax x Mexico Pilot ETS
Estimation tier: Tier 3 (Pareto/threshold for ETS) + Tier 3 (fuel-fraction for F)
Base year: 2021 (Inventario de Gases y Compuestos de Efecto Invernadero, SEDESU)
Target years: 2025, 2026

Key assumptions:
- AR5 GWPs used (CH4=28, N2O=265) — matches inventory methodology (Table 3)
- [1A1] fuel split computed from Table 10: NG ~100% of CO2 (diesel negligible)
- [1A2] NG fraction computed from Table 11 fuel consumption x INECC emission factors
  -> NG share of fossil CO2 ~95.5% (central); range 93-97%
- Three electricity plants: El Sauz (Pedro Escobedo), Queretaro, San Juan del Rio
- IPPU: cal (2 plants), vidrio (2 companies), hierro/acero (1), HFCs (all Kyoto gases)
- Biogenic CO2 from lena combustion excluded from inventory totals (IPCC convention)

Data sources:
- Inventario de Emisiones de Gases y Compuestos de Efecto Invernadero
  del Estado de Queretaro, Ano Base 2021
  Secretaria de Desarrollo Sustentable (SEDESU), Diciembre 2023
  Local file: Inventario-emisiones-Gases-Compuestos-de-Efecto-Invernadero-2021.pdf.pdf
- Table 10: Fuel consumption [1A1] electricity generation
- Table 11: Fuel consumption [1A2] industrial sector
- Table 12: Fuel consumption [1A3] road transport by municipality
- Table 13: Energy emissions by subcategory (GgCO2e)
- Table 14: IPPU emissions by subcategory
- Table 16: AFOLU emissions by subcategory
- Table 19: Waste emissions by subcategory
- Table 21: Uncertainties by category and subcategory

Outputs:
- data/processed/queretaro_inventory_2021.csv
- data/processed/queretaro_fuel_fractions_2021.csv
- data/processed/queretaro_power_plant_detail_2021.csv

Usage: python 01_clean.py
"""

import pandas as pd
import numpy as np
import os, sys

# -- Paths -------------------------------------------------------------------
SCRIPT_DIR  = os.path.dirname(os.path.abspath(__file__))
BASE_DIR    = os.path.dirname(SCRIPT_DIR)
RAW_DIR     = os.path.join(BASE_DIR, "data", "raw")
PROC_DIR    = os.path.join(BASE_DIR, "data", "processed")
os.makedirs(PROC_DIR, exist_ok=True)

print("=" * 65)
print("Queretaro 01_clean.py — reading and processing 2021 inventory")
print("=" * 65)

# -- 1. Load raw inventory ---------------------------------------------------
inv_path = os.path.join(RAW_DIR, "queretaro_ghg_inventory_2021.csv")
raw = pd.read_csv(inv_path, comment="#")
raw = raw[~raw["ipcc_code"].isin(["TOTAL_EX_ABS", "TOTAL_NET"])].copy()
print(f"Loaded {len(raw)} raw inventory rows")

# -- 2. Build clean inventory ------------------------------------------------
LEAF_CODES = [
    # Energy — electricity generation
    "1A1",
    # Manufacturing (aggregate — no subsector breakdown in inventory)
    "1A2",
    # Transport
    "1A3a", "1A3b", "1A3c",
    # Other sectors
    "1A4a", "1Ab", "1A4c",
    # IPPU — minerals
    "2A2", "2A3",
    # IPPU — metals
    "2C1",
    # IPPU — HFCs
    "2F1_res", "2F1_ac_res", "2F1_ac_ind", "2F1_ac_mov",
    # AFOLU — livestock
    "3A1", "3A2",
    # AFOLU — aggregated sources
    "3C1", "3C3", "3C4", "3C5", "3C6",
    # Waste
    "4A", "4C", "4D",
]

inv = raw[raw["ipcc_code"].isin(LEAF_CODES)].copy()
inv = inv.reset_index(drop=True)
print(f"Retained {len(inv)} leaf-level rows for analysis")

# Verify totals against known sector aggregates from inventory
sector_check = {
    "1A1 electricity":   inv[inv["ipcc_code"] == "1A1"]["emissions_GgCO2e"].sum(),
    "1A2 manufacturing": inv[inv["ipcc_code"] == "1A2"]["emissions_GgCO2e"].sum(),
    "1A3 transport":     inv[inv["ipcc_code"].str.startswith("1A3")]["emissions_GgCO2e"].sum(),
    "1A4a commercial":   inv[inv["ipcc_code"] == "1A4a"]["emissions_GgCO2e"].sum(),
    "1Ab residential":   inv[inv["ipcc_code"] == "1Ab"]["emissions_GgCO2e"].sum(),
    "1A4c agriculture":  inv[inv["ipcc_code"] == "1A4c"]["emissions_GgCO2e"].sum(),
    "2A minerals":       inv[inv["ipcc_code"].isin(["2A2", "2A3"])]["emissions_GgCO2e"].sum(),
    "2C metals":         inv[inv["ipcc_code"] == "2C1"]["emissions_GgCO2e"].sum(),
    "2F HFCs":           inv[inv["ipcc_code"].str.startswith("2F")]["emissions_GgCO2e"].sum(),
    "3A livestock":      inv[inv["ipcc_code"].str.startswith("3A")]["emissions_GgCO2e"].sum(),
    "3C land sources":   inv[inv["ipcc_code"].str.startswith("3C")]["emissions_GgCO2e"].sum(),
    "4 waste":           inv[inv["ipcc_code"].str.startswith("4")]["emissions_GgCO2e"].sum(),
}

expected = {
    "1A1 electricity":   1895.94,
    "1A2 manufacturing": 2182.47,
    "1A3 transport":     2503.49,
    "1A4a commercial":   84.93,
    "1Ab residential":   381.05,
    "1A4c agriculture":  119.08,
    "2A minerals":       163.73,
    "2C metals":         0.28,
    "2F HFCs":           70.48,
    "3A livestock":      1260.55,
    "3C land sources":   1189.21,
    "4 waste":           738.48,
}

print("\nSanity check — sector aggregates vs inventory totals:")
all_ok = True
for k in expected:
    got  = sector_check[k]
    exp  = expected[k]
    diff = abs(got - exp)
    tol  = 0.5
    flag = "OK" if diff < tol else "MISMATCH"
    if diff >= tol:
        all_ok = False
    print(f"  {k:<25}  got={got:8.2f}  exp={exp:8.2f}  {flag}")

if not all_ok:
    print("\n  Sector total mismatches detected — check leaf code selection.")
    sys.exit(1)
else:
    print("\n  All sector totals reconciled within 0.5 GgCO2e")

gross_total = sum(sector_check.values())
print(f"\n  Leaf sum: {gross_total:.2f} GgCO2e")
print(f"  State gross total (inventory): 10,589.69 GgCO2e")
print(f"  Difference: {abs(gross_total - 10589.69):.2f} GgCO2e (3B land sinks excluded)")

# -- 3. Add sector labels ---------------------------------------------------
def sector_group(code):
    if code == "1A1":           return "electricity_generation"
    if code == "1A2":           return "manufacturing"
    if code.startswith("1A3"): return "transport"
    if code == "1A4a":          return "commercial"
    if code == "1Ab":           return "residential"
    if code == "1A4c":          return "ag_combustion"
    if code.startswith("2A"):  return "ippu_minerals"
    if code.startswith("2C"):  return "ippu_metals"
    if code.startswith("2F"):  return "ippu_hfcs"
    if code.startswith("3"):   return "afolu"
    if code.startswith("4"):   return "waste"
    return "other"

inv["sector_group"] = inv["ipcc_code"].apply(sector_group)
inv.to_csv(os.path.join(PROC_DIR, "queretaro_inventory_2021.csv"), index=False)
print(f"\nSaved: data/processed/queretaro_inventory_2021.csv  ({len(inv)} rows)")

# -- 4. Compute [1A1] fuel fractions from Table 10 ---------------------------
# 2021 fuel consumption for electricity generation (PJ) and INECC emission factors
EF = {
    "gas_natural": 57755.0,   # kg CO2/TJ (INECC Mexico)
    "diesel":      72851.0,
}
FUEL_1A1 = {
    "gas_natural": 32.80,     # PJ (Table 10 total)
    "diesel":      3.80e-05,  # PJ (Table 10 — San Juan del Rio only, negligible)
}

co2_by_fuel_1A1 = {f: FUEL_1A1[f] * 1000 * EF[f] / 1e9 for f in FUEL_1A1}
total_co2_1A1   = sum(co2_by_fuel_1A1.values())
ng_frac_1A1     = co2_by_fuel_1A1["gas_natural"] / total_co2_1A1
tax_frac_1A1    = co2_by_fuel_1A1["diesel"] / total_co2_1A1

print(f"\n[1A1] Electricity — 2021 CO2 by fuel:")
for f, v in co2_by_fuel_1A1.items():
    print(f"  {f:<14}: {v:7.2f} GgCO2  ({v/total_co2_1A1*100:.4f}%)")
print(f"  Total computed CO2: {total_co2_1A1:.2f}  |  Inventory CO2: 1894.13")
print(f"  NG fraction = {ng_frac_1A1:.6f}  ({ng_frac_1A1*100:.4f}%)")
print(f"  Taxable (diesel) fraction = {tax_frac_1A1:.6f}  ({tax_frac_1A1*100:.4f}%)")

# -- 5. Compute [1A2] fuel fractions from Table 11 ---------------------------
EF_1A2 = {
    "gas_lp":       63100.0,
    "diesel":       72851.0,
    "gas_natural":  57755.0,
    "combustoleo":  77400.0,
    "coque":        97500.0,
    "gasolinas":    69300.0,
}
FUEL_1A2 = {
    "gas_lp":       0.67,
    "diesel":       0.32,
    "gas_natural": 36.11,
    "combustoleo":  0.10,
    "coque":        0.24,
    "gasolinas":    0.02,
}

co2_by_fuel_1A2 = {f: FUEL_1A2[f] * 1000 * EF_1A2[f] / 1e9 for f in FUEL_1A2}
total_co2_1A2   = sum(co2_by_fuel_1A2.values())
ng_co2_1A2      = co2_by_fuel_1A2["gas_natural"]
ng_frac_1A2     = ng_co2_1A2 / total_co2_1A2
tax_frac_1A2    = 1.0 - ng_frac_1A2

print(f"\n[1A2] Manufacturing — 2021 CO2 by fuel:")
for f, v in co2_by_fuel_1A2.items():
    print(f"  {f:<14}: {v:7.2f} GgCO2  ({v/total_co2_1A2*100:.2f}%)")
print(f"  Total computed CO2: {total_co2_1A2:.2f}  |  Inventory CO2: 2180.28")
print(f"  NG fraction = {ng_frac_1A2:.4f}  ({ng_frac_1A2*100:.2f}%)")
print(f"  Taxable (non-NG) fraction = {tax_frac_1A2:.4f}  ({tax_frac_1A2*100:.2f}%)")

# -- 6. Build fuel-fraction parameters table ---------------------------------
fractions = pd.DataFrame([
    # [1A1] Electricity: NG ~100%, diesel negligible
    # ETS: 3 plants; El Sauz (1,638 GgCO2e) and SJR (236 GgCO2e) >> threshold;
    #       Queretaro plant (20 GgCO2e) < 25,000 tCO2e → ETS ~98.9%
    dict(
        ipcc_code="1A1", sector_group="electricity_generation",
        ng_exempt_frac_low=0.999, ng_exempt_frac_central=ng_frac_1A1, ng_exempt_frac_high=1.000,
        ets_frac_low=0.985, ets_frac_central=0.989, ets_frac_high=0.995,
        derivation_ng="Table 10 fuel consumption x INECC EFs; NG=99.9998% of CO2",
        derivation_ets="3 plants: El Sauz 1638 GgCO2e + SJR 236 GgCO2e >> threshold; Qro 20 GgCO2e < threshold (1.1%)"
    ),
    # [1A2] Manufacturing: NG=36.11/37.46 PJ fossil = 96.4% energy, 95.5% CO2
    # ETS: strong auto/aerospace cluster; large concentrated plants
    dict(
        ipcc_code="1A2", sector_group="manufacturing",
        ng_exempt_frac_low=0.93, ng_exempt_frac_central=ng_frac_1A2, ng_exempt_frac_high=0.97,
        ets_frac_low=0.60, ets_frac_central=0.75, ets_frac_high=0.88,
        derivation_ng="Table 11: NG=36.11 PJ of 37.46 PJ fossil; corrected by EFs -> ~95.5% of fossil CO2",
        derivation_ets="Strong automotive/aerospace cluster; glass, automotive parts, large concentrated plants"
    ),
    # [1A4a] Commercial: NG ~20% estimated (pipeline distribution in ZMQ)
    dict(
        ipcc_code="1A4a", sector_group="commercial",
        ng_exempt_frac_low=0.10, ng_exempt_frac_central=0.20, ng_exempt_frac_high=0.30,
        ets_frac_low=0.00, ets_frac_central=0.00, ets_frac_high=0.00,
        derivation_ng="Commercial: LPG dominant; NG pipeline in ZMQ → ~20% NG estimated",
        derivation_ets="Small distributed commercial establishments; none above threshold"
    ),
    # [1Ab] Residential: NOT in S; NG ~5% of fossil CO2
    dict(
        ipcc_code="1Ab", sector_group="residential",
        ng_exempt_frac_low=0.02, ng_exempt_frac_central=0.05, ng_exempt_frac_high=0.10,
        ets_frac_low=0.00, ets_frac_central=0.00, ets_frac_high=0.00,
        derivation_ng="Residential: LPG dominant; some NG pipeline in urban areas; ~5% NG",
        derivation_ets="Small distributed households"
    ),
    # [1A4c] Agriculture combustion: minimal NG
    dict(
        ipcc_code="1A4c", sector_group="ag_combustion",
        ng_exempt_frac_low=0.00, ng_exempt_frac_central=0.02, ng_exempt_frac_high=0.05,
        ets_frac_low=0.00, ets_frac_central=0.00, ets_frac_high=0.00,
        derivation_ng="Agricultural: mainly diesel + LPG for mechanized ag; negligible NG",
        derivation_ets="Small distributed agricultural sources"
    ),
    # [1A3] Transport: NG = 0.596 PJ of 31.11 PJ total (~1.4% CO2)
    dict(
        ipcc_code="1A3", sector_group="transport",
        ng_exempt_frac_low=0.01, ng_exempt_frac_central=0.014, ng_exempt_frac_high=0.02,
        ets_frac_low=0.00, ets_frac_central=0.00, ets_frac_high=0.00,
        derivation_ng="Table 12: NG=0.596 PJ of 31.11 PJ total transport; ~1.4% of CO2",
        derivation_ets="Transport not in Mexico Pilot ETS"
    ),
    # [2A2] Cal: process CO2; 2 establishments; each ~24 GgCO2e near threshold
    dict(
        ipcc_code="2A2", sector_group="ippu_minerals",
        ng_exempt_frac_low=0.00, ng_exempt_frac_central=0.00, ng_exempt_frac_high=0.00,
        ets_frac_low=0.40, ets_frac_central=0.60, ets_frac_high=0.80,
        derivation_ng="Process emissions (calcination); not fossil fuel combustion",
        derivation_ets="2 lime producers; each ~24 GgCO2e close to 25kt threshold; high uncertainty"
    ),
    # [2A3] Vidrio: process CO2; 2 companies well above threshold
    dict(
        ipcc_code="2A3", sector_group="ippu_minerals",
        ng_exempt_frac_low=0.00, ng_exempt_frac_central=0.00, ng_exempt_frac_high=0.00,
        ets_frac_low=0.85, ets_frac_central=0.95, ets_frac_high=1.00,
        derivation_ng="Process emissions (glass production); not fossil fuel combustion",
        derivation_ets="2 glass companies; each ~57 GgCO2e >> 25kt threshold"
    ),
    # [2C1] Hierro/acero: 0.28 GgCO2e — way below threshold
    dict(
        ipcc_code="2C1", sector_group="ippu_metals",
        ng_exempt_frac_low=0.00, ng_exempt_frac_central=0.00, ng_exempt_frac_high=0.00,
        ets_frac_low=0.00, ets_frac_central=0.00, ets_frac_high=0.00,
        derivation_ng="Process emissions; not combustion",
        derivation_ets="0.28 GgCO2e = 280 tCO2e << 25,000 threshold"
    ),
    # [2F] HFCs: not fossil fuel, not in ETS
    dict(
        ipcc_code="2F", sector_group="ippu_hfcs",
        ng_exempt_frac_low=0.00, ng_exempt_frac_central=0.00, ng_exempt_frac_high=0.00,
        ets_frac_low=0.00, ets_frac_central=0.00, ets_frac_high=0.00,
        derivation_ng="HFC refrigerant leaks; not a fossil fuel",
        derivation_ets="Refrigerant leaks not in Mexico Pilot ETS scope"
    ),
])

fractions.to_csv(os.path.join(PROC_DIR, "queretaro_fuel_fractions_2021.csv"), index=False)
print(f"\nSaved: data/processed/queretaro_fuel_fractions_2021.csv  ({len(fractions)} rows)")

# -- 7. Power plant detail table ---------------------------------------------
plants = pd.DataFrame([
    dict(name="El Sauz (Pedro Escobedo)",
         municipality="Pedro Escobedo", generation_MWh=3_500_140,
         fuel_ng_PJ=28.36, fuel_diesel_PJ=0.00,
         estimated_CO2e_GgCO2e=1638.8,
         above_25ktCO2e_threshold=True),
    dict(name="Planta Queretaro",
         municipality="Queretaro", generation_MWh=24_486,
         fuel_ng_PJ=0.35, fuel_diesel_PJ=0.00,
         estimated_CO2e_GgCO2e=20.2,
         above_25ktCO2e_threshold=False),  # 20,200 tCO2e < 25,000
    dict(name="Planta San Juan del Rio",
         municipality="San Juan del Rio", generation_MWh=400_573,
         fuel_ng_PJ=4.09, fuel_diesel_PJ=3.80e-05,
         estimated_CO2e_GgCO2e=236.3,
         above_25ktCO2e_threshold=True),
])
plants.to_csv(os.path.join(PROC_DIR, "queretaro_power_plant_detail_2021.csv"), index=False)
print(f"Saved: data/processed/queretaro_power_plant_detail_2021.csv  ({len(plants)} plants, "
      f"{plants['generation_MWh'].sum():,.0f} MWh total)")

print("\n  01_clean.py complete\n")
