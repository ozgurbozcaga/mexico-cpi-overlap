"""
02_estimate.py — Queretaro Carbon Pricing Overlap Analysis
===========================================================
Case: Mexico — Queretaro state carbon tax (S) x Federal IEPS carbon tax (F) x
      Mexico Pilot ETS (E)
Estimation tier: Tier 3 (threshold/Pareto for ETS; fuel-fraction for F)
Base year: 2021  |  Target years: 2025, 2026
Author: World Bank Climate Change Group — State & Trends of Carbon Pricing

Instruments:
----------------------------------------------------------------------
S  Queretaro state carbon tax
   Scope:    ALL Kyoto gases (CO2, CH4, N2O, HFCs, PFCs, SF6)
             from productive processes / fixed sources (economy-wide)
   Covered:  [1A1] electricity, [1A2] manufacturing, [1A4a] commercial,
             [1A4c] agricultural combustion, ALL IPPU (2A-2F incl HFCs)
   Exempt:   [1A3] transport, [1Ab] residential, AFOLU (3A,3B,3C), waste (4)
   NG:       NO exemption — unlike federal tax, NG IS taxed

F  Mexico federal IEPS carbon tax (Art. 2o-C)
   Scope:    Upstream fuel tax; covers all fossil fuels EXCEPT natural gas
             Applies to stationary AND mobile (transport) combustion
   Exempt:   Natural gas (explicit statutory exemption)
             Process emissions (IPPU) not covered
             Fugitive emissions not covered

E  Mexico Pilot ETS (Sistema de Comercio de Emisiones, piloto 2020-)
   Scope:    Direct CO2 from facilities >= 25,000 tCO2e/yr
             Sectors: electricity, manufacturing, O&G, other large industry
   Coverage: Legal scope used (upper bound per project methodology)

Key analytical insights:
   1. Queretaro's electricity is ~100% NG → F covers ~0% of [1A1]
   2. Manufacturing fossil fuel is ~95.5% NG → F covers only ~4.5% of [1A2]
   3. Queretaro covers all Kyoto gases → HFC refrigeration (70.48 GgCO2e) in S
   4. Strong automotive/aerospace cluster → higher ETS fraction than average
   5. Residential excluded from S (unlike some other states)

Outputs:
   data/processed/queretaro_tax_scope_2021.csv
   data/processed/queretaro_extrapolated_2025_2026.csv
   data/processed/queretaro_overlap_estimates.csv
"""

import pandas as pd
import numpy as np
import os

# -- Paths -------------------------------------------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR   = os.path.dirname(SCRIPT_DIR)
PROC_DIR   = os.path.join(BASE_DIR, "data", "processed")
os.makedirs(PROC_DIR, exist_ok=True)

print("=" * 65)
print("Queretaro 02_estimate.py — scope mapping and overlap estimation")
print("=" * 65)

# -- 1. Load processed data --------------------------------------------------
inv   = pd.read_csv(os.path.join(PROC_DIR, "queretaro_inventory_2021.csv"))
fracs = pd.read_csv(os.path.join(PROC_DIR, "queretaro_fuel_fractions_2021.csv"))

STATE_TOTAL_2021 = 10589.69  # gross excluding absorptions


# -- 2. Define scope mapping rules -------------------------------------------
def get_scope(row, fracs_df):
    code = row["ipcc_code"]
    sg   = row["sector_group"]

    in_S = False
    f_c = f_l = f_h = 0.0
    e_c = e_l = e_h = 0.0
    note = ""

    # -- ENERGY ---------------------------------------------------------------
    if code == "1A1":
        # Electricity: IN S (all gases, no NG exemption)
        in_S = True
        fr = fracs_df[fracs_df["ipcc_code"] == "1A1"].iloc[0]
        ng_c = fr["ng_exempt_frac_central"]
        ng_l = fr["ng_exempt_frac_low"]
        ng_h = fr["ng_exempt_frac_high"]
        f_c, f_l, f_h = 1 - ng_c, 1 - ng_h, 1 - ng_l
        e_c = fr["ets_frac_central"]
        e_l = fr["ets_frac_low"]
        e_h = fr["ets_frac_high"]
        note = "1A1: S(all); F(diesel ~0%); E(98.9%, 2 of 3 plants >> threshold)"

    elif sg == "manufacturing":
        in_S = True
        fr = fracs_df[fracs_df["ipcc_code"] == "1A2"].iloc[0]
        ng_c = fr["ng_exempt_frac_central"]
        ng_l = fr["ng_exempt_frac_low"]
        ng_h = fr["ng_exempt_frac_high"]
        f_c, f_l, f_h = 1 - ng_c, 1 - ng_h, 1 - ng_l
        e_c = fr["ets_frac_central"]
        e_l = fr["ets_frac_low"]
        e_h = fr["ets_frac_high"]
        note = "1A2: S(all); F(non-NG ~4.5%); E(75% central, auto/aero cluster)"

    elif sg == "transport":
        in_S = False
        fr = fracs_df[fracs_df["ipcc_code"] == "1A3"].iloc[0]
        ng_c = fr["ng_exempt_frac_central"]
        ng_l = fr["ng_exempt_frac_low"]
        ng_h = fr["ng_exempt_frac_high"]
        f_c, f_l, f_h = 1 - ng_c, 1 - ng_h, 1 - ng_l
        e_c = e_l = e_h = 0.0
        note = "1A3: EXEMPT from S; F=~98.6% (all fuels except NG); E=0"

    elif sg == "commercial":
        in_S = True
        fr = fracs_df[fracs_df["ipcc_code"] == "1A4a"].iloc[0]
        ng_c = fr["ng_exempt_frac_central"]
        ng_l = fr["ng_exempt_frac_low"]
        ng_h = fr["ng_exempt_frac_high"]
        f_c, f_l, f_h = 1 - ng_c, 1 - ng_h, 1 - ng_l
        e_c = e_l = e_h = 0.0
        note = "1A4a: S(all); F(LPG+other ~80%); E=0"

    elif sg == "residential":
        in_S = False
        fr = fracs_df[fracs_df["ipcc_code"] == "1Ab"].iloc[0]
        ng_c = fr["ng_exempt_frac_central"]
        ng_l = fr["ng_exempt_frac_low"]
        ng_h = fr["ng_exempt_frac_high"]
        f_c, f_l, f_h = 1 - ng_c, 1 - ng_h, 1 - ng_l
        e_c = e_l = e_h = 0.0
        note = "1Ab: EXEMPT from S; F=~95% (LPG dominant); E=0"

    elif sg == "ag_combustion":
        in_S = True
        fr = fracs_df[fracs_df["ipcc_code"] == "1A4c"].iloc[0]
        ng_c = fr["ng_exempt_frac_central"]
        ng_l = fr["ng_exempt_frac_low"]
        ng_h = fr["ng_exempt_frac_high"]
        f_c, f_l, f_h = 1 - ng_c, 1 - ng_h, 1 - ng_l
        e_c = e_l = e_h = 0.0
        note = "1A4c: IN S (productive processes); F=~98% (diesel+LPG); E=0"

    # -- IPPU ----------------------------------------------------------------
    elif sg == "ippu_minerals":
        in_S = True
        f_c = f_l = f_h = 0.0  # process emissions, not fuel
        fr = fracs_df[fracs_df["ipcc_code"] == code].iloc[0]
        e_c = fr["ets_frac_central"]
        e_l = fr["ets_frac_low"]
        e_h = fr["ets_frac_high"]
        note = f"{code}: S(process CO2, all Kyoto gases); F=0; E=subsector-specific"

    elif sg == "ippu_metals":
        in_S = True
        f_c = f_l = f_h = 0.0
        e_c = e_l = e_h = 0.0  # 0.28 GgCO2e << threshold
        note = "2C1: S(process); F=0; E=0 (280 tCO2e << 25kt threshold)"

    elif sg == "ippu_hfcs":
        in_S = True
        f_c = f_l = f_h = 0.0
        e_c = e_l = e_h = 0.0
        note = "2F: S(HFCs, all Kyoto gases covered); F=0; E=0"

    # -- AFOLU ---------------------------------------------------------------
    elif sg == "afolu":
        in_S = False
        f_c = f_l = f_h = 0.0
        e_c = e_l = e_h = 0.0
        note = "AFOLU: exempt from all three instruments"

    # -- WASTE ---------------------------------------------------------------
    elif sg == "waste":
        in_S = False
        f_c = f_l = f_h = 0.0
        e_c = e_l = e_h = 0.0
        note = "Waste: exempt from all three instruments"

    return pd.Series({
        "in_S":           in_S,
        "f_frac_central": f_c, "f_frac_low": f_l, "f_frac_high": f_h,
        "e_frac_central": e_c, "e_frac_low": e_l, "e_frac_high": e_h,
        "scope_note":     note,
    })


# -- 3. Apply scope mapping --------------------------------------------------
scope = inv.apply(lambda r: get_scope(r, fracs), axis=1)
scope_df = pd.concat([inv, scope], axis=1)


# -- 4. Compute Venn segments for 2021 ----------------------------------------
def compute_venn_row(row, scen="central"):
    em   = row["emissions_GgCO2e"]
    in_S = row["in_S"]
    f    = row[f"f_frac_{scen}"]
    e    = row[f"e_frac_{scen}"]

    if in_S:
        SE_F     = em * f * e
        SE       = em * (1 - f) * e
        SF       = em * f * (1 - e)
        S_only   = em * (1 - f) * (1 - e)
        F_only   = 0.0
        FE_only  = 0.0
        E_only   = 0.0
        uncov    = 0.0
    else:
        SE_F     = 0.0
        SE       = 0.0
        SF       = 0.0
        S_only   = 0.0
        F_only   = em * f * (1 - e)
        FE_only  = em * f * e
        E_only   = em * (1 - f) * e
        uncov    = em * (1 - f) * (1 - e)

    return pd.Series({
        "S_F_E":     SE_F,
        "S_E_only":  SE,
        "S_F_only":  SF,
        "S_only":    S_only,
        "F_only":    F_only,
        "F_E_only":  FE_only,
        "E_only":    E_only,
        "uncovered": uncov,
    })


for scen in ["central", "low", "high"]:
    venn = scope_df.apply(lambda r: compute_venn_row(r, scen), axis=1)
    for col in venn.columns:
        scope_df[f"{col}_{scen}"] = venn[col]

scope_df.to_csv(os.path.join(PROC_DIR, "queretaro_tax_scope_2021.csv"), index=False)
print(f"\nSaved: data/processed/queretaro_tax_scope_2021.csv")


# -- 5. Summarise Venn segments for 2021 -------------------------------------
SEGS = ["S_F_E", "S_E_only", "S_F_only", "S_only",
        "F_only", "F_E_only", "E_only", "uncovered"]

summary_2021 = {}
for scen in ["central", "low", "high"]:
    summary_2021[scen] = {s: scope_df[f"{s}_{scen}"].sum() for s in SEGS}


def instrument_totals(segs):
    S     = segs["S_F_E"] + segs["S_E_only"] + segs["S_F_only"] + segs["S_only"]
    F     = segs["S_F_E"] + segs["S_F_only"] + segs["F_only"]   + segs["F_E_only"]
    E     = segs["S_F_E"] + segs["S_E_only"] + segs["F_E_only"] + segs["E_only"]
    union = sum(segs[s] for s in SEGS if s != "uncovered")
    return S, F, E, union


print("\n2021 Venn decomposition (central estimate):")
for s in SEGS:
    v   = summary_2021["central"][s]
    pct = v / STATE_TOTAL_2021 * 100
    print(f"  {s:<12}: {v:8.1f} GgCO2e  ({pct:5.1f}% of state)")

S_c, F_c, E_c, union_c = instrument_totals(summary_2021["central"])
print(f"\n  STATE TAX (S) gross  : {S_c:.1f}  ({S_c/STATE_TOTAL_2021*100:.1f}%)")
print(f"  FEDERAL TAX (F)      : {F_c:.1f}  ({F_c/STATE_TOTAL_2021*100:.1f}%)")
print(f"  PILOT ETS (E)        : {E_c:.1f}  ({E_c/STATE_TOTAL_2021*100:.1f}%)")
print(f"  UNION S|F|E          : {union_c:.1f}  ({union_c/STATE_TOTAL_2021*100:.1f}%)")
print(f"  Uncovered            : {summary_2021['central']['uncovered']:.1f}  "
      f"({summary_2021['central']['uncovered']/STATE_TOTAL_2021*100:.1f}%)")


# -- 6. Growth rates and extrapolation 2021->2025/2026 -----------------------
GROWTH = {
    "electricity_generation": (-0.005, -0.025, 0.010),
    "manufacturing":          ( 0.030, -0.005, 0.055),
    "transport":              ( 0.015, -0.005, 0.030),
    "commercial":             ( 0.010, -0.010, 0.020),
    "residential":            ( 0.010, -0.005, 0.020),
    "ag_combustion":          ( 0.005, -0.010, 0.015),
    "ippu_minerals":          ( 0.010, -0.010, 0.025),
    "ippu_metals":            ( 0.005, -0.010, 0.020),
    "ippu_hfcs":              ( 0.020,  0.005, 0.035),
    "afolu":                  ( 0.005, -0.010, 0.015),
    "waste":                  ( 0.020,  0.005, 0.035),
}

rows_extrap = []
for _, row in scope_df.iterrows():
    sg = row["sector_group"]
    g_c, g_l, g_h = GROWTH.get(sg, (0.0, 0.0, 0.0))
    em_base = row["emissions_GgCO2e"]

    for yr in [2025, 2026]:
        n = yr - 2021
        for scen, rate in [("central", g_c), ("low", g_l), ("high", g_h)]:
            em_yr = em_base * (1 + rate) ** n
            r = row.to_dict()
            r["year"]             = yr
            r["scenario"]         = scen
            r["emissions_GgCO2e"] = em_yr
            rows_extrap.append(r)

extrap = pd.DataFrame(rows_extrap)

for scen in ["central", "low", "high"]:
    mask = extrap["scenario"] == scen
    venn = extrap[mask].apply(lambda r: compute_venn_row(r, scen), axis=1)
    for col in venn.columns:
        extrap.loc[mask, f"{col}_computed"] = venn[col].values

extrap.to_csv(os.path.join(PROC_DIR, "queretaro_extrapolated_2025_2026.csv"), index=False)
print(f"\nSaved: data/processed/queretaro_extrapolated_2025_2026.csv")


# -- 7. Build final overlap estimates table ----------------------------------
records = []

def make_record(year, scenario, segs, total):
    S, F, E, union = instrument_totals(segs)
    return dict(
        year=year, scenario=scenario,
        state_total_GgCO2e=total,
        S_gross_GgCO2e=S, S_pct=S / total * 100,
        F_gross_GgCO2e=F, F_pct=F / total * 100,
        E_gross_GgCO2e=E, E_pct=E / total * 100,
        S_F_E_GgCO2e=segs["S_F_E"],     S_F_E_pct=segs["S_F_E"] / total * 100,
        S_E_only_GgCO2e=segs["S_E_only"], S_E_only_pct=segs["S_E_only"] / total * 100,
        S_F_only_GgCO2e=segs["S_F_only"], S_F_only_pct=segs["S_F_only"] / total * 100,
        S_only_GgCO2e=segs["S_only"],    S_only_pct=segs["S_only"] / total * 100,
        F_only_GgCO2e=segs["F_only"],    F_only_pct=segs["F_only"] / total * 100,
        F_E_only_GgCO2e=segs["F_E_only"], F_E_only_pct=segs["F_E_only"] / total * 100,
        E_only_GgCO2e=segs["E_only"],    E_only_pct=segs["E_only"] / total * 100,
        uncovered_GgCO2e=segs["uncovered"], uncovered_pct=segs["uncovered"] / total * 100,
        union_GgCO2e=union, union_pct=union / total * 100,
        S_F_overlap=segs["S_F_E"] + segs["S_F_only"],
        S_E_overlap=segs["S_F_E"] + segs["S_E_only"],
        F_E_overlap=segs["S_F_E"] + segs["F_E_only"],
        estimation_tier="Tier 3",
        notes="Queretaro: all Kyoto gases in S; NG not exempt from S; ETS threshold via Pareto"
    )

# 2021 base year
for scen in ["central", "low", "high"]:
    records.append(make_record(2021, scen, summary_2021[scen], STATE_TOTAL_2021))

# 2025, 2026
for yr in [2025, 2026]:
    for scen in ["central", "low", "high"]:
        mask = (extrap["scenario"] == scen) & (extrap["year"] == yr)
        sub  = extrap[mask]
        total_yr   = sub["emissions_GgCO2e"].sum()
        seg_totals = {s: sub[f"{s}_computed"].sum() for s in SEGS}
        records.append(make_record(yr, scen, seg_totals, total_yr))

overlap_df = pd.DataFrame(records).sort_values(["year", "scenario"])
overlap_df.to_csv(os.path.join(PROC_DIR, "queretaro_overlap_estimates.csv"), index=False)
print(f"Saved: data/processed/queretaro_overlap_estimates.csv")


# -- 8. Print summary --------------------------------------------------------
print("\n" + "=" * 65)
print("QUERETARO COVERAGE ESTIMATES — CENTRAL SCENARIO")
print("=" * 65)
for yr in [2021, 2025, 2026]:
    row_c = overlap_df[(overlap_df["year"] == yr) & (overlap_df["scenario"] == "central")].iloc[0]
    row_l = overlap_df[(overlap_df["year"] == yr) & (overlap_df["scenario"] == "low")].iloc[0]
    row_h = overlap_df[(overlap_df["year"] == yr) & (overlap_df["scenario"] == "high")].iloc[0]

    print(f"\n  Year {yr}:")
    print(f"    State total:   {row_c['state_total_GgCO2e']:7.0f} GgCO2e")
    print(f"    S (state tax): {row_c['S_gross_GgCO2e']:7.0f}  ({row_c['S_pct']:.1f}%)")
    print(f"    F (federal):   {row_c['F_gross_GgCO2e']:7.0f}  ({row_c['F_pct']:.1f}%)")
    print(f"    E (ETS):       {row_c['E_gross_GgCO2e']:7.0f}  ({row_c['E_pct']:.1f}%)")
    print(f"    S^F^E:         {row_c['S_F_E_GgCO2e']:7.0f}  ({row_c['S_F_E_pct']:.1f}%)")
    print(f"    S^E only:      {row_c['S_E_only_GgCO2e']:7.0f}  ({row_c['S_E_only_pct']:.1f}%)")
    print(f"    S^F only:      {row_c['S_F_only_GgCO2e']:7.0f}  ({row_c['S_F_only_pct']:.1f}%)")
    print(f"    S only:        {row_c['S_only_GgCO2e']:7.0f}  ({row_c['S_only_pct']:.1f}%)")
    print(f"    F only:        {row_c['F_only_GgCO2e']:7.0f}  ({row_c['F_only_pct']:.1f}%)")
    print(f"    Union S|F|E:   {row_c['union_GgCO2e']:7.0f}  ({row_c['union_pct']:.1f}%)")
    rng_S = f"[{row_l['S_gross_GgCO2e']:.0f}-{row_h['S_gross_GgCO2e']:.0f}]"
    rng_F = f"[{row_l['F_gross_GgCO2e']:.0f}-{row_h['F_gross_GgCO2e']:.0f}]"
    rng_E = f"[{row_l['E_gross_GgCO2e']:.0f}-{row_h['E_gross_GgCO2e']:.0f}]"
    print(f"    Ranges:  S {rng_S}  F {rng_F}  E {rng_E}")

print("\n  02_estimate.py complete\n")
