"""
01_clean.py -- San Luis Potosi Carbon Pricing Overlap Analysis
================================================================
Case: Mexico -- SLP state carbon tax x Federal IEPS x Mexico Pilot ETS
Estimation tier: Tier 3
Base year: Annual average 2007-2014 (cumulative 8-year inventory / 8)
Source: IEGEI-SLP 2017, UASLP / SEGAM / VariClim, v5 2019

CRITICAL NOTES:
- Inventory reports CUMULATIVE 8-year totals (2007-2014), NOT single-year.
  Annual values derived by dividing by 8.
- Inventory uses SAR GWPs (CH4=21, N2O=310). ALL other state pipelines use
  AR5 (CH4=28, N2O=265). This script converts mass emissions to AR5 CO2eq.
- CO2 component stays unchanged; only CH4 and N2O equivalents change.
- Biogenic fuels (lena, bagazo) excluded from totals per IPCC convention.
- No HFC/PFC data in inventory (data gap for S coverage).
- IPPU data from RETC does not distinguish combustion vs process emissions.

GWP conversion:
  SAR:  CH4=21,  N2O=310
  AR5:  CH4=28,  N2O=265
  For each category: AR5_CO2eq = CO2 + CH4_mass*28 + N2O_mass*265

Data sources:
  Table 1 (pp.15-17): Cumulative sector emissions 2007-2014
  Table 2 (p.20): Energy sector detail
  Table 4 (p.22): IPPU detail
  Table 6 (p.25): AFOLU detail
  Table 16 (p.34): Waste detail
  Tables 19-23 (pp.38-40): RETC facility-level CO2 by municipality

Outputs:
  data/processed/slp_inventory_annual_ar5.csv
  data/processed/slp_fuel_fractions.csv
  data/processed/slp_facility_detail.csv

Usage: python 01_clean.py
"""

import pandas as pd
import numpy as np
import os, sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR   = os.path.dirname(SCRIPT_DIR)
PROC_DIR   = os.path.join(BASE_DIR, "data", "processed")
os.makedirs(PROC_DIR, exist_ok=True)

print("=" * 70)
print("San Luis Potosi 01_clean.py -- inventory extraction & AR5 conversion")
print("=" * 70)

# ── GWP constants ───────────────────────────────────────────────────────
GWP_SAR  = {"CH4": 21,  "N2O": 310}
GWP_AR5  = {"CH4": 28,  "N2O": 265}
YEARS    = 8  # cumulative period 2007-2014

# ── 1. Raw inventory data from Table 1 (pp.15-17) ──────────────────────
# All values in MILLIONS OF TONNES (Mt), cumulative 2007-2014
# Columns: subsector, CO2_Mt, CH4_Mt, N2O_Mt (mass, not CO2eq)
raw_data = [
    # ── ENERGY ──────────────────────────────────────────────────────────
    # 1A1 Electricity generation
    dict(ipcc_code="1A1", subsector="Generacion",
         sector="energy", sector_group="electricity_generation",
         CO2_Mt=56.58, CH4_Mt=0.00158, N2O_Mt=0.00007),
    # 1A3 Transport (gasoline)
    dict(ipcc_code="1A3_gas", subsector="Transporte (gasolina)",
         sector="energy", sector_group="transport",
         CO2_Mt=16.79, CH4_Mt=0.00799, N2O_Mt=0.0007),
    # 1A3 Transport (diesel)
    dict(ipcc_code="1A3_die", subsector="Transporte (diesel)",
         sector="energy", sector_group="transport",
         CO2_Mt=9.79, CH4_Mt=0.00051, N2O_Mt=0.01082),
    # 1A2 Industrial combustion — natural gas
    dict(ipcc_code="1A2_gn", subsector="Consumo industrial GN",
         sector="energy", sector_group="manufacturing",
         CO2_Mt=6.53, CH4_Mt=0.00058, N2O_Mt=1.1656e-05),
    # 1A2 Industrial combustion — GLP
    dict(ipcc_code="1A2_glp", subsector="Consumo industrial GLP",
         sector="energy", sector_group="manufacturing",
         CO2_Mt=9.81, CH4_Mt=0.00015, N2O_Mt=1.5553e-05),
    # 1A2 Industrial combustion — diesel
    dict(ipcc_code="1A2_die", subsector="Consumo industrial diesel",
         sector="energy", sector_group="manufacturing",
         CO2_Mt=2.18, CH4_Mt=8.8579e-05, N2O_Mt=1.7716e-05),
    # 1A4 Residential, commercial, public (GLP + GN)
    dict(ipcc_code="1A4", subsector="Residencial, Comercial y Publico",
         sector="energy", sector_group="other_energy",
         CO2_Mt=21.56, CH4_Mt=0.001709, N2O_Mt=3.4195e-05),
    # Biogenic — lena (EXCLUDED from totals)
    dict(ipcc_code="1A_bio_lena", subsector="Consumo de lena (biogenico)",
         sector="energy", sector_group="biogenic",
         CO2_Mt=0.87, CH4_Mt=0.002343, N2O_Mt=0.0000312),
    # Biogenic — bagazo (EXCLUDED from totals)
    dict(ipcc_code="1A_bio_bag", subsector="Consumo de bagazo (biogenico)",
         sector="energy", sector_group="biogenic",
         CO2_Mt=2.013, CH4_Mt=0.006039, N2O_Mt=0.00008052),

    # ── IPPU ────────────────────────────────────────────────────────────
    dict(ipcc_code="2_metalurgia", subsector="Metalurgia",
         sector="ippu", sector_group="ippu_metalurgia",
         CO2_Mt=1.98, CH4_Mt=0.0, N2O_Mt=0.005496),
    dict(ipcc_code="2_quimica", subsector="Quimica",
         sector="ippu", sector_group="ippu_quimica",
         CO2_Mt=0.18, CH4_Mt=0.0, N2O_Mt=0.0),
    dict(ipcc_code="2_cemento_cal", subsector="Cemento y cal",
         sector="ippu", sector_group="ippu_cemento",
         CO2_Mt=20.44, CH4_Mt=1.44e-06, N2O_Mt=0.0),
    dict(ipcc_code="2_automotriz", subsector="Automotriz",
         sector="ippu", sector_group="ippu_automotriz",
         CO2_Mt=0.31, CH4_Mt=0.0, N2O_Mt=2.43e-06),
    dict(ipcc_code="2_celulosa", subsector="Celulosa y papel",
         sector="ippu", sector_group="ippu_celulosa",
         CO2_Mt=1.08, CH4_Mt=9.4e-06, N2O_Mt=0.0),
    dict(ipcc_code="2_vidrio", subsector="Vidrio",
         sector="ippu", sector_group="ippu_vidrio",
         CO2_Mt=1.67, CH4_Mt=0.0, N2O_Mt=0.0),
    dict(ipcc_code="2_otras", subsector="Otras industrias",
         sector="ippu", sector_group="ippu_otras",
         CO2_Mt=0.91, CH4_Mt=0.0, N2O_Mt=0.0),

    # ── AFOLU ───────────────────────────────────────────────────────────
    dict(ipcc_code="3_ferm_ent", subsector="Fermentacion enterica",
         sector="afolu", sector_group="afolu",
         CO2_Mt=0.0, CH4_Mt=0.212, N2O_Mt=0.0),
    dict(ipcc_code="3_excretas", subsector="Manejo de excretas",
         sector="afolu", sector_group="afolu",
         CO2_Mt=0.0, CH4_Mt=0.00294, N2O_Mt=0.007735),
    dict(ipcc_code="3_quema_ag", subsector="Quema agricola",
         sector="afolu", sector_group="afolu",
         CO2_Mt=6.778, CH4_Mt=0.202, N2O_Mt=0.0),

    # ── WASTE ───────────────────────────────────────────────────────────
    dict(ipcc_code="4_domesticos", subsector="Residuos domesticos",
         sector="waste", sector_group="waste",
         CO2_Mt=0.0, CH4_Mt=0.368, N2O_Mt=0.0),
    dict(ipcc_code="4_industriales", subsector="Residuos industriales",
         sector="waste", sector_group="waste",
         CO2_Mt=0.00695, CH4_Mt=0.04, N2O_Mt=0.0),
]

df = pd.DataFrame(raw_data)

# ── 2. Validate SAR CO2eq against inventory totals ──────────────────────
df["CO2eq_SAR_Mt"] = df["CO2_Mt"] + df["CH4_Mt"]*GWP_SAR["CH4"] + df["N2O_Mt"]*GWP_SAR["N2O"]

# Sector totals from inventory (cumulative, SAR, Mt CO2eq)
expected_SAR = {
    "energy":  130.24,
    "ippu":     28.28,
    "afolu":    17.94,   # inventory says 17.9415
    "waste":     8.62,
}

print("\nSAR GWP validation (cumulative 8yr, Mt CO2eq):")
all_ok = True
for sec, exp in expected_SAR.items():
    got = df[df["sector"]==sec]["CO2eq_SAR_Mt"].sum()
    diff = abs(got - exp)
    tol = 0.15  # tolerance for rounding in PDF tables
    flag = "ok" if diff < tol else "MISMATCH"
    if diff >= tol:
        all_ok = False
    print(f"  {sec:<10}: computed={got:8.2f}  expected={exp:8.2f}  diff={diff:.3f}  {flag}")

grand_total_SAR = df["CO2eq_SAR_Mt"].sum()
print(f"\n  Grand total (SAR): {grand_total_SAR:.2f} Mt (expected 185.08)")
diff_total = abs(grand_total_SAR - 185.08)
if diff_total > 0.5:
    print(f"  WARNING: Grand total off by {diff_total:.2f} Mt")
    all_ok = False

if not all_ok:
    print("\n  WARNING: Some sector totals do not reconcile exactly.")
    print("  Proceeding with hardcoded values from inventory tables.")
else:
    print("\n  All sector totals reconciled within tolerance")

# ── 3. Convert to AR5 GWPs ──────────────────────────────────────────────
df["CO2eq_AR5_Mt"] = df["CO2_Mt"] + df["CH4_Mt"]*GWP_AR5["CH4"] + df["N2O_Mt"]*GWP_AR5["N2O"]

print("\n--- SAR vs AR5 comparison (cumulative 8yr, Mt CO2eq) ---")
for sec in ["energy", "ippu", "afolu", "waste", "biogenic"]:
    mask = df["sector_group"]=="biogenic" if sec=="biogenic" else df["sector"]==sec
    sar = df[mask]["CO2eq_SAR_Mt"].sum()
    ar5 = df[mask]["CO2eq_AR5_Mt"].sum()
    ch = ar5 - sar
    print(f"  {sec:<10}: SAR={sar:8.2f}  AR5={ar5:8.2f}  change={ch:+.2f}")

# Exclude biogenic for totals
df_fossil_mt = df[df["sector_group"]!="biogenic"].copy()
grand_AR5 = df_fossil_mt["CO2eq_AR5_Mt"].sum()
grand_SAR_fossil = df_fossil_mt["CO2eq_SAR_Mt"].sum()
print(f"\n  Grand total (excl biogenic):")
print(f"    SAR: {grand_SAR_fossil:.2f} Mt cumulative = {grand_SAR_fossil/YEARS:.2f} Mt/yr")
print(f"    AR5: {grand_AR5:.2f} Mt cumulative = {grand_AR5/YEARS:.2f} Mt/yr")
print(f"    AR5/SAR ratio: {grand_AR5/grand_SAR_fossil:.4f}")

# ── 4. Compute annual averages (divide by 8) ────────────────────────────
df["CO2_annual_kt"]     = df["CO2_Mt"]     / YEARS * 1000  # Mt -> kt
df["CH4_annual_kt"]     = df["CH4_Mt"]     / YEARS * 1000
df["N2O_annual_kt"]     = df["N2O_Mt"]     / YEARS * 1000
df["CO2eq_AR5_annual_kt"] = df["CO2eq_AR5_Mt"] / YEARS * 1000
df["CO2eq_SAR_annual_kt"] = df["CO2eq_SAR_Mt"] / YEARS * 1000

# Convert to GgCO2e for consistency with other state pipelines (1 Gg = 1 kt)
df["emissions_GgCO2e"] = df["CO2eq_AR5_annual_kt"]  # 1 kt = 1 Gg

print("\n--- Annual average inventory (AR5 GWPs, GgCO2e/yr) ---")
for sec in ["energy", "ippu", "afolu", "waste"]:
    sub = df[df["sector"]==sec]
    total = sub["emissions_GgCO2e"].sum()
    print(f"\n  {sec.upper()} ({total:.1f} GgCO2e/yr):")
    for _, r in sub.iterrows():
        print(f"    {r['subsector']:<40} {r['emissions_GgCO2e']:8.1f}")

bio = df[df["sector_group"]=="biogenic"]["emissions_GgCO2e"].sum()
print(f"\n  BIOGENIC (excluded): {bio:.1f} GgCO2e/yr")

df_fossil = df[df["sector_group"]!="biogenic"].copy()
state_total = df_fossil["emissions_GgCO2e"].sum()
print(f"\n  STATE TOTAL (excl biogenic, AR5): {state_total:.1f} GgCO2e/yr")

# ── 5. Build fuel-fraction parameters ───────────────────────────────────
# These drive scope calculations in 02_estimate.py
#
# Key SLP-specific features:
# a) Electricity: NG fraction ~43% by CO2. Tamazunchale (NG CC) + Villa de Reyes
#    (conventional thermal, combustoleo). Non-NG = ~57%.
#    Derivation: 422.6 PJ NG x 57,755 kgCO2/TJ = 24.41 Mt out of 56.58 Mt total.
# b) Industry: GN=6.53, GLP=9.81, diesel=2.18 Mt CO2 → non-NG = 65%
# c) Residential/commercial: GLP+GN mix, NG ~25% estimated
# d) IPPU: process emissions, F=0
# e) Metalurgia: significant N2O (0.005496 Mt cumulative)

EF_NG = 57755.0   # kgCO2/TJ INECC
EF_FO = 79450.0   # kgCO2/TJ combustoleo
EF_DIE = 72851.0  # kgCO2/TJ diesel
EF_GLP = 63100.0  # kgCO2/TJ GLP

# [1A1] Electricity: NG fraction by CO2
# NG energy for generation: 422.6 PJ (from energy balance)
# NG CO2 = 422.6e3 * 57,755 / 1e9 = 24.41 Mt
ng_co2_1A1 = 422.6e3 * EF_NG / 1e9  # 24.41 Mt
total_co2_1A1 = 56.58  # Mt cumulative
ng_frac_1A1 = ng_co2_1A1 / total_co2_1A1  # ~0.431

# [1A2] Industry: by fuel type
ind_gn  = 6.53   # Mt CO2
ind_glp = 9.81
ind_die = 2.18
ind_total = ind_gn + ind_glp + ind_die
ng_frac_1A2 = ind_gn / ind_total  # 0.353

# [1A4] Residential/commercial/public: GLP dominant, some GN
# Inventory text says "GLP, GN" mix. Estimate NG ~25% (pipeline exists in SLP city)
ng_frac_1A4 = 0.25  # central estimate

print(f"\n--- Fuel fractions ---")
print(f"  [1A1] Electricity NG fraction: {ng_frac_1A1:.3f} ({ng_frac_1A1*100:.1f}%)")
print(f"    NG CO2 = {ng_co2_1A1:.2f} Mt / {total_co2_1A1:.2f} Mt total")
print(f"  [1A2] Industry NG fraction: {ng_frac_1A2:.3f} ({ng_frac_1A2*100:.1f}%)")
print(f"    GN={ind_gn}, GLP={ind_glp}, diesel={ind_die}")
print(f"    Non-NG share = {(1-ng_frac_1A2)*100:.1f}% -- highest of all states")
print(f"  [1A4] Residential/commercial NG fraction: {ng_frac_1A4:.2f} (estimated)")

fractions = pd.DataFrame([
    dict(
        category="1A1", sector_group="electricity_generation",
        ng_exempt_frac_central=ng_frac_1A1,
        ng_exempt_frac_low=0.35, ng_exempt_frac_high=0.55,
        ets_frac_central=1.00, ets_frac_low=0.95, ets_frac_high=1.00,
        derivation_ng="422.6 PJ NG x 57,755 EF / 56.58 Mt total CO2; Tamazunchale (NG CC) + Villa de Reyes (combustoleo)",
        derivation_ets="Tamazunchale ~2,515 kt/yr + Villa de Reyes ~1,383 kt/yr; both >> 25,000 tCO2e threshold"
    ),
    dict(
        category="1A2", sector_group="manufacturing",
        ng_exempt_frac_central=ng_frac_1A2,
        ng_exempt_frac_low=0.28, ng_exempt_frac_high=0.42,
        ets_frac_central=0.50, ets_frac_low=0.35, ets_frac_high=0.65,
        derivation_ng="GN=6.53 / (GN+GLP+diesel=18.52) = 35.3%; non-NG=64.7% highest of all states",
        derivation_ets="Diverse industry; some large plants but many SMEs. Metalurgia single facility 2,071 kt/yr >> threshold but others smaller"
    ),
    dict(
        category="1A4", sector_group="other_energy",
        ng_exempt_frac_central=ng_frac_1A4,
        ng_exempt_frac_low=0.15, ng_exempt_frac_high=0.35,
        ets_frac_central=0.00, ets_frac_low=0.00, ets_frac_high=0.00,
        derivation_ng="GLP dominant; NG pipeline in SLP metro area; estimated 25% NG",
        derivation_ets="Distributed small commercial/residential sources; none above 25,000 tCO2e"
    ),
])

fractions.to_csv(os.path.join(PROC_DIR, "slp_fuel_fractions.csv"), index=False)
print(f"\nSaved: data/processed/slp_fuel_fractions.csv")

# ── 6. Facility detail table (from RETC data, Tables 19-23, base 2006) ──
facilities = pd.DataFrame([
    dict(municipality="San Luis Potosi", sector="Mixed industry",
         co2_kgyr=448_644_917, n_establishments=29,
         notes="Metalurgia #20: 2,071 Mt; Celulosa #3: 81.6 Mt; Cemento #14+#16: 67.8 Mt"),
    dict(municipality="Cerritos", sector="Cemento y Cal",
         co2_kgyr=1_075_731_636, n_establishments=1,
         notes="Single large cement/cal facility"),
    dict(municipality="Soledad de Graciano", sector="Automotriz + Cemento",
         co2_kgyr=796_210, n_establishments=2,
         notes="Automotriz 151 kt + Cemento 645 kt"),
    dict(municipality="Tamazunchale", sector="Generacion electrica",
         co2_kgyr=2_514_692_617, n_establishments=1,
         notes="Tamazunchale CC (NG-fired); largest single source in state"),
    dict(municipality="Villa de Reyes", sector="Generacion electrica",
         co2_kgyr=1_383_056_174, n_establishments=1,
         notes="Termoelectrica convencional (combustoleo); being converted to CC"),
])
facilities["co2_ktyr"] = facilities["co2_kgyr"] / 1e6
facilities["above_25kt_threshold"] = facilities["co2_ktyr"] > 25.0
facilities.to_csv(os.path.join(PROC_DIR, "slp_facility_detail.csv"), index=False)
print(f"Saved: data/processed/slp_facility_detail.csv")

# ── 7. Save processed inventory ─────────────────────────────────────────
out_cols = ["ipcc_code", "subsector", "sector", "sector_group",
            "CO2_Mt", "CH4_Mt", "N2O_Mt",
            "CO2eq_SAR_Mt", "CO2eq_AR5_Mt",
            "CO2_annual_kt", "CH4_annual_kt", "N2O_annual_kt",
            "CO2eq_AR5_annual_kt", "CO2eq_SAR_annual_kt",
            "emissions_GgCO2e"]
df[out_cols].to_csv(os.path.join(PROC_DIR, "slp_inventory_annual_ar5.csv"), index=False)
print(f"Saved: data/processed/slp_inventory_annual_ar5.csv ({len(df)} rows)")

print(f"\n{'='*70}")
print(f"STATE TOTAL (annual avg, AR5, excl biogenic): {state_total:.1f} GgCO2e/yr")
print(f"  = {state_total/1000:.2f} MtCO2e/yr")
print(f"  (SAR equivalent: {grand_SAR_fossil/YEARS*1000:.1f} GgCO2e/yr = "
      f"{grand_SAR_fossil/YEARS:.2f} MtCO2e/yr)")
print(f"{'='*70}")
print("\n  01_clean.py complete\n")
