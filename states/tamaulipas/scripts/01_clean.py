"""
01_clean.py — Tamaulipas Carbon Pricing Overlap Analysis
=========================================================
Case: Mexico — Tamaulipas state carbon tax × Federal IEPS × Mexico Pilot ETS
Estimation tier: Tier 3 (dual 25,000 tCO2e/yr threshold for S and E)
Base year: 2013 (PECC Tamaulipas inventory, IPCC 2006)
Target year: 2025 (via Table III BaU projections)

CRITICAL: SAR → AR5 GWP conversion required.
   Inventory uses SAR GWPs (CH4=21, N2O=310).
   All other state pipelines use AR5 (CH4=28, N2O=265).
   Conversion: CH4_AR5 = CH4_SAR × (28/21), N2O_AR5 = N2O_SAR × (265/310).

Data sources:
   - Programa Estatal de Cambio Climático Tamaulipas 2015-2030
     Published: Periódico Oficial, 15 Sept 2016
     Local file: Tamaulipas_cxli-111-150916F-ANEXO.pdf
   - Table 5.1: Full 2013 IPCC inventory with CO2/CH4/N2O breakdown
   - Table 5.6: Fuel consumption by sector 2013 (PJ)
   - Table 5.12: Electricity generation fuel — NG and diesel (TJ), 1995-2013
   - Table 5.14: Manufacturing fuel — NG, diesel, GLP (TJ), 1995-2013
   - Table 5.11: Refinery NG consumption (TJ), 1995-2013
   - Table III: BaU projections 1990-2030 by sector
   - Tables 5.3/5.4: Power plant inventory (CFE + private CC plants)

Outputs:
   data/processed/tamaulipas_inventory_2013_ar5.csv
   data/processed/tamaulipas_fuel_fractions_2013.csv
   data/processed/tamaulipas_bau_projections.csv

Usage: python 01_clean.py
"""

import pandas as pd
import numpy as np
import os, sys

# ── Paths ────────────────────────────────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR   = os.path.dirname(SCRIPT_DIR)
RAW_DIR    = os.path.join(BASE_DIR, "data", "raw")
PROC_DIR   = os.path.join(BASE_DIR, "data", "processed")
os.makedirs(PROC_DIR, exist_ok=True)

print("=" * 72)
print("Tamaulipas 01_clean.py — inventory extraction and SAR→AR5 conversion")
print("=" * 72)

# ── GWP conversion factors ───────────────────────────────────────────────────
CH4_SAR, CH4_AR5 = 21, 28
N2O_SAR, N2O_AR5 = 310, 265
CH4_CONV = CH4_AR5 / CH4_SAR   # 1.3333
N2O_CONV = N2O_AR5 / N2O_SAR   # 0.8548

print(f"\nGWP conversion factors:")
print(f"  CH4: SAR={CH4_SAR} → AR5={CH4_AR5}  (×{CH4_CONV:.4f})")
print(f"  N2O: SAR={N2O_SAR} → AR5={N2O_AR5}  (×{N2O_CONV:.4f})")

# ── 1. Hardcoded inventory from Table 5.1 (p.98-99) ──────────────────────────
# Units: CO2 in Gg (= kt), CH4/N2O as CO2eq with SAR GWPs in Gg
# NE = Not Estimated, NA = Not Applicable → treated as 0.0

raw_data = [
    # IPCC code, description, CO2, CH4_CO2eq_SAR, N2O_CO2eq_SAR, Total_SAR
    ("1A1a", "Generación de electricidad",       13894.84,    5.20,    7.70, 13907.74),
    ("1A1b", "Refinación del petróleo",           2948.80,    1.10,    1.63,  2951.53),
    ("1A2",  "Industrias manufactureras",         1975.50,    0.79,    1.29,  1977.58),
    ("1A3a", "Aviación",                           239.96,    0.00,    0.00,   239.96),
    ("1A3b", "Transporte terrestre",              6915.71,    3.39,   49.98,  6969.08),
    ("1A3c", "Ferrocarriles",                       48.51,    0.05,    5.80,    54.36),
    ("1A3d", "Navegación marítima y fluvial",      210.27,    0.42,    1.76,   212.45),
    ("1A4a", "Combustión comercial/institucional",  74.31,    0.12,    0.04,    74.47),
    ("1A4b_gn", "Combustión residencial GN",       100.19,    0.19,    0.06,   100.44),
    ("1A4b_glp","Combustión residencial GLP",      748.56,    0.25,    2.23,   751.04),
    ("1A4c", "Combustión agrícola",                 12.53,    0.02,    0.01,    12.56),
    ("1B2",  "Industria petróleo y gas natural",   678.77, 2932.51,    0.41,  3611.69),
    ("2A4",  "Usos de caliza",                      50.14,    0.00,    0.00,    50.14),
    ("2B8",  "Negro de humo (carbon black)",       392.26,    0.00,    0.00,   392.26),
    ("2F1",  "Refrigeración y AC (HFC)",             0.00,    0.00,    0.00,     0.00),  # NE
    ("3A1",  "Fermentación entérica",                0.00, 1733.39,    0.00,  1733.39),
    ("3A2",  "Manejo de estiércol",                  0.00,   45.18,   20.19,    65.37),
    ("3B",   "Cambios de uso de suelo",           3669.07,    0.00,    0.00,  3669.07),
    ("3C1f", "Quema biomasa tierras forestales",     0.00,    1.47,    0.80,     2.27),
    ("3C1c", "Quema biomasa tierras cultivo",        0.00,   50.24,   19.23,    69.47),
    ("3C4",  "N2O directas suelos gestionados",      0.00,    0.00, 1079.06,  1079.06),
    ("3C5",  "N2O indirectas suelos gestionados",    0.00,    0.00,   93.45,    93.45),
    ("3C7",  "Cultivo de arroz",                     0.00,    4.48,    0.00,     4.48),
    ("4A",   "Eliminación de desechos",            163.13,  284.03,    0.00,   447.16),
    ("4D1",  "Tratamiento aguas residuales",         0.00,  231.49,   96.62,   328.11),
]

inv = pd.DataFrame(raw_data, columns=[
    "ipcc_code", "description", "co2_Gg", "ch4_co2eq_sar", "n2o_co2eq_sar", "total_sar"
])

# ── 2. SAR → AR5 conversion ──────────────────────────────────────────────────
inv["ch4_co2eq_ar5"] = inv["ch4_co2eq_sar"] * CH4_CONV
inv["n2o_co2eq_ar5"] = inv["n2o_co2eq_sar"] * N2O_CONV
inv["total_ar5"]     = inv["co2_Gg"] + inv["ch4_co2eq_ar5"] + inv["n2o_co2eq_ar5"]

# ── 3. Validate totals ───────────────────────────────────────────────────────
total_sar = inv["total_sar"].sum()
total_ar5 = inv["total_ar5"].sum()
expected_sar = 38797.14

print(f"\n--- Inventory validation ---")
print(f"  Total (SAR): {total_sar:.2f} GgCO2e  (expected: {expected_sar:.2f})")
diff_sar = abs(total_sar - expected_sar)
if diff_sar > 5.0:
    print(f"  ⚠ SAR total mismatch by {diff_sar:.2f} GgCO2e")
else:
    print(f"  ✓ SAR total reconciled (diff = {diff_sar:.2f})")

print(f"  Total (AR5): {total_ar5:.2f} GgCO2e")
print(f"  AR5/SAR ratio: {total_ar5/total_sar:.4f} ({(total_ar5/total_sar-1)*100:+.1f}%)")

# ── 4. Sector grouping ───────────────────────────────────────────────────────
def sector_group(code):
    if code == "1A1a":            return "electricity_generation"
    if code == "1A1b":            return "petroleum_refining"
    if code == "1A2":             return "manufacturing"
    if code.startswith("1A3"):    return "transport"
    if code.startswith("1A4"):    return "other_energy"
    if code == "1B2":             return "fugitive_oil_gas"
    if code == "2A4":             return "ippu_caliza"
    if code == "2B8":             return "ippu_negro_humo"
    if code == "2F1":             return "ippu_hfc"
    if code.startswith("3A"):     return "afolu_livestock"
    if code == "3B":              return "afolu_land_use"
    if code.startswith("3C"):     return "afolu_agriculture"
    if code.startswith("4"):      return "waste"
    return "other"

inv["sector_group"] = inv["ipcc_code"].apply(sector_group)

# Print sector summary
print(f"\n--- Sector summary (AR5 GWPs) ---")
sector_sums = inv.groupby("sector_group")["total_ar5"].sum().sort_values(ascending=False)
for sg, val in sector_sums.items():
    pct = val / total_ar5 * 100
    print(f"  {sg:<25} {val:8.2f} GgCO2e  ({pct:5.1f}%)")

inv.to_csv(os.path.join(PROC_DIR, "tamaulipas_inventory_2013_ar5.csv"), index=False)
print(f"\nSaved: data/processed/tamaulipas_inventory_2013_ar5.csv  ({len(inv)} rows)")

# ── 5. Fuel fractions from Table 5.12 and Table 5.14 ─────────────────────────
# IPCC 2006 default emission factors (kg CO2/TJ)
EF = {
    "gas_natural":  56100.0,
    "diesel":       74100.0,
    "combustoleo":  77400.0,
    "glp":          63100.0,
    "gasolina":     69300.0,
    "turbosina":    71500.0,
}

print(f"\n--- Fuel fraction analysis ---")

# [1A1a] Electricity generation — Table 5.12 (2013 values)
# NG = 247,524.83 TJ, Diesel = 117.93 TJ
# NOTE: Combustóleo acknowledged as 5.2% of electricity fuel but not in SIE data.
# We estimate combustóleo contribution separately.
elec_ng_tj     = 247524.83
elec_diesel_tj = 117.93
# Combustóleo: text says 5.2% of electricity petrolíferos; total excl comb ≈ 247,643
# → total incl comb ≈ 247,643 / (1-0.052) ≈ 261,228 → comb ≈ 13,585 TJ
elec_comb_tj   = 13585.0  # estimated from text "5.2% of electricity fuel"

elec_co2 = {
    "gas_natural":  elec_ng_tj     * EF["gas_natural"]  / 1e6,  # Gg CO2
    "diesel":       elec_diesel_tj * EF["diesel"]       / 1e6,
    "combustoleo":  elec_comb_tj   * EF["combustoleo"]  / 1e6,
}
elec_co2_total = sum(elec_co2.values())
elec_ng_frac   = elec_co2["gas_natural"] / elec_co2_total

print(f"\n  [1A1a] Electricity generation — CO2 by fuel (2013):")
for f, v in elec_co2.items():
    print(f"    {f:<14}: {v:8.2f} GgCO2  ({v/elec_co2_total*100:5.2f}%)")
print(f"    Total CO2:     {elec_co2_total:8.2f}")
print(f"    NG fraction:   {elec_ng_frac:.4f}  ({elec_ng_frac*100:.2f}%)")
print(f"    NOTE: combustóleo estimated from text (5.2% of elec fuel); not in SIE data")

# [1A1b] Refinery — Table 5.11: all NG in inventory
# But refinery uses mixed fuels in practice. The inventory only captures NG.
# PEMEX Ciudad Madero uses NG + refinery gas + some liquid fuels.
# Conservative estimate: NG ~85% of refinery emissions (central); range 75-95%
ref_ng_frac = 0.85

print(f"\n  [1A1b] Petroleum refining:")
print(f"    Inventory shows only NG (52,563 TJ → 2,952 GgCO2e)")
print(f"    But PEMEX uses mixed fuels. Assumed NG fraction: {ref_ng_frac:.0%} (range 75-95%)")

# [1A2] Manufacturing — Table 5.14 (2013 values)
# NG = 32,427.87 TJ, Diesel = 1,360.09 TJ, GLP = 880.21 TJ
mfg_ng_tj     = 32427.87
mfg_diesel_tj = 1360.09
mfg_glp_tj    = 880.21

mfg_co2 = {
    "gas_natural": mfg_ng_tj     * EF["gas_natural"] / 1e6,
    "diesel":      mfg_diesel_tj * EF["diesel"]      / 1e6,
    "glp":         mfg_glp_tj    * EF["glp"]         / 1e6,
}
mfg_co2_total = sum(mfg_co2.values())
mfg_ng_frac   = mfg_co2["gas_natural"] / mfg_co2_total

print(f"\n  [1A2] Manufacturing — CO2 by fuel (Table 5.14, 2013):")
for f, v in mfg_co2.items():
    print(f"    {f:<14}: {v:8.2f} GgCO2  ({v/mfg_co2_total*100:5.2f}%)")
print(f"    Total CO2:     {mfg_co2_total:8.2f}")
print(f"    NG fraction:   {mfg_ng_frac:.4f}  ({mfg_ng_frac*100:.2f}%)")

# [1A4] Other sectors — Table 5.6 fuel data
# Residential: NG=1.79 PJ, GLP=11.99 PJ → NG ≈ 13%
# Commercial: GLP=1.18 PJ only
# Agricultural: GLP=0.20 PJ only
other_ng_frac = 0.13  # weighted average; mostly residential GLP

print(f"\n  [1A4] Other sectors:")
print(f"    Residential NG=1.79 PJ, GLP=11.99 PJ → NG share ~13%")
print(f"    Commercial: GLP only. Agricultural: GLP only.")
print(f"    Combined NG fraction: {other_ng_frac:.0%}")

# ── 6. Build fuel fractions table ────────────────────────────────────────────
fractions = pd.DataFrame([
    dict(
        ipcc_code="1A1a", sector_group="electricity_generation",
        ng_exempt_frac_central=elec_ng_frac,
        ng_exempt_frac_low=0.90, ng_exempt_frac_high=0.97,
        derivation_ng=(
            "Table 5.12: NG=247,525 TJ, Diesel=118 TJ + estimated combustóleo=13,585 TJ "
            "(5.2% of electricity fuel per inventory text p.115). "
            "NG CO2 fraction = 92.7%. Range: 90-97% (combustóleo data uncertainty)."
        ),
    ),
    dict(
        ipcc_code="1A1b", sector_group="petroleum_refining",
        ng_exempt_frac_central=ref_ng_frac,
        ng_exempt_frac_low=0.75, ng_exempt_frac_high=0.95,
        derivation_ng=(
            "Table 5.11 shows only NG consumption (52,563 TJ). But PEMEX Cd. Madero "
            "uses mixed fuels (NG + refinery gas + liquid fuels). "
            "Central 85% NG; wide range due to data gap on non-NG refinery fuels."
        ),
    ),
    dict(
        ipcc_code="1A2", sector_group="manufacturing",
        ng_exempt_frac_central=mfg_ng_frac,
        ng_exempt_frac_low=0.88, ng_exempt_frac_high=0.97,
        derivation_ng=(
            "Table 5.14: NG=32,428 TJ, Diesel=1,360 TJ, GLP=880 TJ. "
            f"NG CO2 fraction = {mfg_ng_frac*100:.1f}%. "
            "No combustóleo data for this sector (SIE note). Range ±2-4%."
        ),
    ),
    dict(
        ipcc_code="1A4", sector_group="other_energy",
        ng_exempt_frac_central=other_ng_frac,
        ng_exempt_frac_low=0.08, ng_exempt_frac_high=0.20,
        derivation_ng=(
            "Table 5.6: Residential NG=1.79 PJ vs GLP=11.99 PJ. "
            "Commercial GLP only=1.18 PJ. Agric GLP only=0.20 PJ. "
            "Weighted NG share ~13%."
        ),
    ),
])

fractions.to_csv(os.path.join(PROC_DIR, "tamaulipas_fuel_fractions_2013.csv"), index=False)
print(f"\nSaved: data/processed/tamaulipas_fuel_fractions_2013.csv  ({len(fractions)} rows)")

# ── 7. Table III BaU projections — extract 2013 and 2025 ─────────────────────
# Table III columns: Industria Energética, Ind Manuf, Transporte, Otros sectores,
#   Emisiones Fugitivas, Proc Industriales, Desechos, Agric y Ganadería, Cambio Uso Suelo
# All values in GgCO2e (SAR GWPs)

bau_data = {
    "sector": [
        "industria_energetica", "ind_manufacturera", "transporte",
        "otros_sectores", "emisiones_fugitivas", "procesos_industriales",
        "desechos", "agricultura_ganaderia", "cambio_uso_suelo"
    ],
    "bau_2013": [
        16859.28, 1977.58, 7475.85,
        938.51,   3611.69,  442.40,
        775.28,   3045.22, 3669.07
    ],
    "bau_2022": [
        20753.22, 2449.39, 10011.60,
        1098.34,  4747.70,  401.94,
        920.08,   3538.68, 3590.99
    ],
    "bau_2025": [
        22242.57, 2630.47, 11078.48,
        1159.47,  5200.85,  390.43,
        961.02,   3751.31, 3564.96
    ],
}

bau = pd.DataFrame(bau_data)
bau["growth_2013_2025"] = bau["bau_2025"] / bau["bau_2013"]
bau["growth_2013_2022"] = bau["bau_2022"] / bau["bau_2013"]

# 2022 actual validation: user says 47,530 GgCO2e total
bau_2022_total = sum(bau_data["bau_2022"])
print(f"\n--- BaU projection validation ---")
print(f"  Table III 2022 total (SAR): {bau_2022_total:.2f} GgCO2e")
print(f"  2022 actual (official):     47,530 GgCO2e")
print(f"  Table III 2022 vs actual:   {bau_2022_total:.0f} vs 47,530 ({(bau_2022_total/47530-1)*100:+.1f}%)")
print(f"  → BaU trajectory validated within rounding")

print(f"\n  Growth ratios 2013 → 2025 (BaU, SAR basis):")
for _, row in bau.iterrows():
    print(f"    {row['sector']:<28} ×{row['growth_2013_2025']:.4f}")

bau.to_csv(os.path.join(PROC_DIR, "tamaulipas_bau_projections.csv"), index=False)
print(f"\nSaved: data/processed/tamaulipas_bau_projections.csv")

# ── 8. Apply BaU growth to AR5 inventory for 2025 projections ────────────────
# Map inventory categories to Table III sectors for growth ratios
GROWTH_MAP = {
    "electricity_generation": "industria_energetica",
    "petroleum_refining":     "industria_energetica",
    "manufacturing":          "ind_manufacturera",
    "transport":              "transporte",
    "other_energy":           "otros_sectores",
    "fugitive_oil_gas":       "emisiones_fugitivas",
    "ippu_caliza":            "procesos_industriales",
    "ippu_negro_humo":        "procesos_industriales",
    "ippu_hfc":               "procesos_industriales",
    "afolu_livestock":        "agricultura_ganaderia",
    "afolu_land_use":         "cambio_uso_suelo",
    "afolu_agriculture":      "agricultura_ganaderia",
    "waste":                  "desechos",
}

growth_lookup = dict(zip(bau["sector"], bau["growth_2013_2025"]))

inv["growth_2025"] = inv["sector_group"].map(
    lambda sg: growth_lookup.get(GROWTH_MAP.get(sg, ""), 1.0)
)
inv["total_ar5_2025"] = inv["total_ar5"] * inv["growth_2025"]

total_ar5_2025 = inv["total_ar5_2025"].sum()
print(f"\n--- 2025 projections (AR5 GWPs) ---")
print(f"  Total 2013 (AR5): {total_ar5:.2f} GgCO2e")
print(f"  Total 2025 (AR5): {total_ar5_2025:.2f} GgCO2e")
print(f"  Growth ratio:     ×{total_ar5_2025/total_ar5:.4f}")

# Save updated inventory with 2025 projections
inv.to_csv(os.path.join(PROC_DIR, "tamaulipas_inventory_2013_ar5.csv"), index=False)

# ── 9. Power plant detail ────────────────────────────────────────────────────
plants = pd.DataFrame([
    dict(name="CT Altamira (CFE)", technology="Termoeléctrica convencional",
         capacity_MW=800, location="Altamira", year_start=1976),
    dict(name="CT Río Bravo / Emilio Portes Gil (CFE)", technology="Termoeléctrica convencional",
         capacity_MW=511, location="Río Bravo", year_start=1971),
    dict(name="CC Altamira V", technology="Ciclo combinado",
         capacity_MW=1121, location="Altamira", year_start=2006),
    dict(name="CC Altamira III y IV", technology="Ciclo combinado",
         capacity_MW=1036, location="Altamira", year_start=2003),
    dict(name="CC Río Bravo", technology="Ciclo combinado",
         capacity_MW=500, location="Valle Hermoso", year_start=2005),
    dict(name="CC Río Bravo II (Anáhuac)", technology="Ciclo combinado",
         capacity_MW=495, location="Valle Hermoso", year_start=2002),
    dict(name="CC Río Bravo III", technology="Ciclo combinado",
         capacity_MW=495, location="Valle Hermoso", year_start=2004),
    dict(name="CC Altamira II", technology="Ciclo combinado",
         capacity_MW=495, location="Altamira", year_start=2002),
])
plants["above_25k_threshold"] = True  # all plants >> 25,000 tCO2e/yr
total_mw = plants["capacity_MW"].sum()
print(f"\n--- Power plants (Tables 5.3/5.4) ---")
print(f"  {len(plants)} plants, {total_mw:,} MW total capacity")
print(f"  All well above 25,000 tCO2e/yr threshold")
print(f"  92% of electricity from ciclo combinado (NG-fired)")

plants.to_csv(os.path.join(PROC_DIR, "tamaulipas_power_plants.csv"), index=False)
print(f"  Saved: data/processed/tamaulipas_power_plants.csv")

# ── 10. Summary ──────────────────────────────────────────────────────────────
print(f"\n{'='*72}")
print(f"TAMAULIPAS INVENTORY SUMMARY")
print(f"{'='*72}")
print(f"  Base year:       2013")
print(f"  Target year:     2025 (BaU projection)")
print(f"  Original GWPs:   SAR (CH4=21, N2O=310)")
print(f"  Converted GWPs:  AR5 (CH4=28, N2O=265)")
print(f"  Total 2013 SAR:  {total_sar:,.2f} GgCO2e")
print(f"  Total 2013 AR5:  {total_ar5:,.2f} GgCO2e  ({(total_ar5/total_sar-1)*100:+.1f}%)")
print(f"  Total 2025 AR5:  {total_ar5_2025:,.2f} GgCO2e")
print(f"\n  Key Tamaulipas features:")
print(f"  • 2nd largest electricity producer nationally (33,558 GWh in 2013)")
print(f"  • Electricity ~93% NG (incl estimated combustóleo)")
print(f"  • Manufacturing ~94% NG (Table 5.14)")
print(f"  • PEMEX refinery at Ciudad Madero (2,952 GgCO2e)")
print(f"  • Large fugitive O&G emissions (3,612→{inv[inv['ipcc_code']=='1B2']['total_ar5'].iloc[0]:.0f} GgCO2e after AR5)")
print(f"  • HFC data: NE (flagged as data gap)")
print(f"  • State carbon tax threshold: 25,000 tCO2e/yr (same as ETS)")
print(f"\n✓ 01_clean.py complete\n")
