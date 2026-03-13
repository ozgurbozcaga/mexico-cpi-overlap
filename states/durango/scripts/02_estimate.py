"""
02_estimate.py — Durango Carbon Pricing Overlap Analysis
=========================================================
Case: Mexico — Durango state carbon tax (S) × Federal IEPS carbon tax (F) ×
      Mexico Pilot ETS (E)
Estimation tier: Tier 3 (threshold/Pareto for ETS; fuel-fraction for F)
Base year: 2022  |  Target years: 2025, 2026
Author: World Bank Climate Change Group — State & Trends of Carbon Pricing

Instruments:
──────────────────────────────────────────────────────────────────────────────
S  Durango state carbon tax
   Scope:    All gases (CO2, CH4, N2O, HFCs, SF6, PFCs, black carbon)
             from STATIONARY SOURCES in all sectors
   Exempt:   Aviation, maritime, transport, waste, forestry, agriculture
   NG exempt: NO — unlike federal tax and Colima, NG is in scope

F  Mexico federal IEPS carbon tax (Art. 2o-C)
   Scope:    Upstream fuel tax; covers all fossil fuels EXCEPT natural gas
             Applies to stationary AND mobile (transport) combustion
   Exempt:   Natural gas (explicit statutory exemption)
             Process emissions (PIUP) not covered (tax on fuel sales)
             Fugitive emissions not covered

E  Mexico Pilot ETS (Sistema de Comercio de Emisiones, piloto 2020–)
   Scope:    Direct emissions from facilities ≥ 25,000 tCO2e/yr
             Sectors: electricity, manufacturing, O&G, other large industry
             Note: non-binding pilot phase; legal ≠ operational coverage
   Coverage: Legal scope used (upper bound per project methodology)

Key analytical insight:
   Because the federal tax is upstream on fuels (not NG), and Durango's
   electricity system is 99.6% NG, the federal tax covers virtually none
   of [1A1]. The state tax covers 100% of [1A1] (no NG exemption).
   This means [1A1] is almost entirely in S∩E only — NOT in F.

Methodology:
   1. Map each IPCC leaf category to scope flags (S, F fraction, E fraction)
   2. For each category compute Venn segments:
      S∩F∩E, S∩E_only, S∩F_only, S_only, F_only, F∩E_only, E_only, uncovered
   3. Extrapolate 2022 → 2025, 2026 using sector growth rates
   4. Propagate uncertainty via low/central/high scenarios

Growth rates (used for 2022→2025/2026 extrapolation):
   Based on 2010–2022 historical TCAMs from inventory, adjusted for
   expected trajectory (COVID recovery normalization, new CC plant in Lerdo)

Outputs:
   data/processed/durango_tax_scope_2022.csv
   data/processed/durango_extrapolated_2025_2026.csv
   data/processed/durango_overlap_estimates.csv
"""

import pandas as pd
import numpy as np
import os

# ── Paths ────────────────────────────────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR   = os.path.dirname(SCRIPT_DIR)
PROC_DIR   = os.path.join(BASE_DIR, "data", "processed")
os.makedirs(PROC_DIR, exist_ok=True)

print("=" * 65)
print("Durango 02_estimate.py — scope mapping and overlap estimation")
print("=" * 65)

# ── 1. Load processed data ───────────────────────────────────────────────────
inv      = pd.read_csv(os.path.join(PROC_DIR, "durango_inventory_2022.csv"))
fracs    = pd.read_csv(os.path.join(PROC_DIR, "durango_fuel_fractions_2022.csv"))

STATE_TOTAL_2022 = 13201.59  # gross excluding absorptions

# ── 2. Define scope mapping rules ────────────────────────────────────────────
# Returns (in_S, f_frac_central, f_frac_low, f_frac_high,
#          e_frac_central, e_frac_low, e_frac_high, venn_note)
# f_frac = fraction of category covered by federal tax (non-NG combustion fuel share)
# e_frac = fraction of category covered by ETS (above threshold)

def get_scope(row, fracs_df):
    code = row["ipcc_code"]
    sg   = row["sector_group"]
    em   = row["emissions_GgCO2e"]

    # Default: nothing
    in_S = False
    f_c  = f_l = f_h = 0.0
    e_c  = e_l = e_h = 0.0
    note = ""

    # ── ENERGY ──────────────────────────────────────────────────────────────
    if code == "1A1a":
        # Electricity generation: IN S (all fuels, no NG exemption)
        in_S = True
        # F: only non-NG fuels (diesel + combustóleo = 0.38% of 1A1 CO2)
        fr = fracs_df[fracs_df["ipcc_code"]=="1A1a"].iloc[0]
        ng_c = fr["ng_exempt_frac_central"]
        ng_l = fr["ng_exempt_frac_low"]
        ng_h = fr["ng_exempt_frac_high"]
        f_c, f_l, f_h = 1-ng_c, 1-ng_h, 1-ng_l  # note inversion for low/high
        # E: all power plants above threshold
        e_c = fr["ets_frac_central"]
        e_l = fr["ets_frac_low"]
        e_h = fr["ets_frac_high"]
        note = "1A1: S(all fuels); F(diesel+FO only, ~0.38%); E(100%, 5 plants all >>threshold)"

    elif sg == "manufacturing":  # 1A2a-m
        in_S = True
        # F: non-NG fossil fraction (NG exempt from IEPS)
        fr = fracs_df[fracs_df["ipcc_code"]=="1A2"].iloc[0]
        ng_c = fr["ng_exempt_frac_central"]
        ng_l = fr["ng_exempt_frac_low"]
        ng_h = fr["ng_exempt_frac_high"]
        f_c, f_l, f_h = 1-ng_c, 1-ng_h, 1-ng_l
        # E: subsector-specific threshold fractions
        e_c, e_l, e_h = _mfg_ets_frac(code)
        note = f"1A2 manuf: S(all); F(non-NG ~{(1-ng_c)*100:.0f}% central); E(subsector-specific)"

    elif sg == "transport":  # 1A3a-c
        in_S = False  # transport EXEMPT from Durango state tax
        f_c = f_l = f_h = 1.0   # all transport fuels in federal tax scope
        e_c = e_l = e_h = 0.0   # transport not in Mexico Pilot ETS
        note = "1A3: EXEMPT from Durango state tax; F=100% (gasoline/diesel/jet); E=0"

    elif code in ("1A4a","1A4b"):  # commercial, residential
        in_S = True
        fr = fracs_df[fracs_df["ipcc_code"]=="1A4ab"].iloc[0]
        ng_c = fr["ng_exempt_frac_central"]
        ng_l = fr["ng_exempt_frac_low"]
        ng_h = fr["ng_exempt_frac_high"]
        f_c, f_l, f_h = 1-ng_c, 1-ng_h, 1-ng_l
        e_c = e_l = e_h = 0.0
        note = "1A4a/b: S(all); F(LPG+diesel, ~85% central, NG~15% exempt); E=0"

    elif code == "1A4c":  # agriculture combustion
        in_S = False  # agricultural emissions exempt from Durango state tax
        fr = fracs_df[fracs_df["ipcc_code"]=="1A4c"].iloc[0]
        ng_c = fr["ng_exempt_frac_central"]
        ng_l = fr["ng_exempt_frac_low"]
        ng_h = fr["ng_exempt_frac_high"]
        f_c, f_l, f_h = 1-ng_c, 1-ng_h, 1-ng_l
        e_c = e_l = e_h = 0.0
        note = "1A4c: Durango ag exempt; F=90% central (mostly diesel); E=0"

    elif code == "1A5":  # non-specified
        in_S = True
        fr = fracs_df[fracs_df["ipcc_code"]=="1A5"].iloc[0]
        ng_c = fr["ng_exempt_frac_central"]
        ng_l = fr["ng_exempt_frac_low"]
        ng_h = fr["ng_exempt_frac_high"]
        f_c, f_l, f_h = 1-ng_c, 1-ng_h, 1-ng_l
        e_c = e_l = e_h = 0.0
        note = "1A5: S(all); F(50% central non-NG, high uncertainty); E=0"

    elif sg == "fugitive":  # 1B2a, 1B2b
        in_S = True
        # F: fugitive CH4 from NG infrastructure → NOT covered by upstream fuel tax
        f_c = f_l = f_h = 0.0
        fr = fracs_df[fracs_df["ipcc_code"]=="1B2"].iloc[0]
        e_c = fr["ets_frac_central"]
        e_l = fr["ets_frac_low"]
        e_h = fr["ets_frac_high"]
        note = "1B2: S(all, CH4 from NG infra); F=0 (upstream tax N/A for fugitives); E(50% central)"

    elif sg == "piup_metals":  # 2C2, 2C5
        in_S = True
        # F: process emissions, not fuel combustion → NOT covered
        f_c = f_l = f_h = 0.0
        fr = fracs_df[fracs_df["ipcc_code"]=="2C"].iloc[0]
        e_c = fr["ets_frac_central"]
        e_l = fr["ets_frac_low"]
        e_h = fr["ets_frac_high"]
        note = "2C: S(process, in stationary scope); F=0 (process not fuel tax); E(90% central)"

    elif sg == "piup_lubricants":  # 2D1
        in_S = True
        f_c = f_l = f_h = 1.0   # lubricant C is from fossil fuel → covered upstream
        e_c = e_l = e_h = 0.0
        note = "2D: S(lubricants, stationary); F=1.0 (fossil non-NG carbon); E=0"

    elif sg == "piup_hfcs":  # 2F1a_res/com/ind
        in_S = True
        # F: HFCs are not fossil fuels → not covered by IEPS
        f_c = f_l = f_h = 0.0
        e_c = e_l = e_h = 0.0
        note = "2F: S(HFCs from AC/refrigeration, stationary); F=0; E=0"

    elif sg == "afolu":  # 3A, 3C
        in_S = False  # forestry AND agricultural emissions exempt
        f_c = f_l = f_h = 0.0
        e_c = e_l = e_h = 0.0
        note = "ASOUT: exempt from all three instruments"

    elif sg == "waste":  # 4x
        in_S = False  # waste exempt from Durango state tax
        f_c = f_l = f_h = 0.0
        e_c = e_l = e_h = 0.0
        note = "Waste: Durango state tax exempts waste; not in F or E"

    return pd.Series({
        "in_S":          in_S,
        "f_frac_central": f_c, "f_frac_low": f_l, "f_frac_high": f_h,
        "e_frac_central": e_c, "e_frac_low":  e_l, "e_frac_high":  e_h,
        "scope_note":    note,
    })


def _mfg_ets_frac(code):
    """Subsector-specific ETS threshold fractions for [1A2] categories.
    Tier 3 estimation: based on plant size distribution inferred from
    sector structure (key categories from inventory Table 5).
    Returns (central, low, high)."""
    fracs_ets = {
        # Pulp & paper: large mills; key category; ~90% above threshold
        "1A2d": (0.90, 0.75, 0.97),
        # Food/beverage: large processors; Durango has significant food industry
        "1A2e": (0.70, 0.50, 0.85),
        # Wood products: lumber (sawmills); Durango = #1 lumber state; distributed small mills
        "1A2j": (0.40, 0.20, 0.60),
        # Mining: large mines (gold, silver, copper, iron); Peñoles, others >> threshold
        "1A2i": (0.80, 0.60, 0.95),
        # Non-metallic minerals: some cement/lime plants
        "1A2f": (0.70, 0.50, 0.90),
        # Iron & steel: 22.54 GgCO2e; likely 1–2 facilities
        "1A2a": (0.80, 0.60, 0.95),
        # Non-ferrous metals: 18.72; some above threshold
        "1A2b": (0.70, 0.50, 0.90),
        # Chemicals: 14.78; medium certainty
        "1A2c": (0.60, 0.40, 0.80),
        # Smaller subsectors: transport equip, machinery, construction, textiles, unspecified
        "1A2g": (0.30, 0.10, 0.50),
        "1A2h": (0.00, 0.00, 0.10),
        "1A2k": (0.20, 0.05, 0.40),
        "1A2l": (0.30, 0.10, 0.50),
        "1A2m": (0.40, 0.20, 0.60),
    }
    if code in fracs_ets:
        return fracs_ets[code]
    return (0.50, 0.30, 0.70)  # fallback


# ── 3. Apply scope mapping ────────────────────────────────────────────────────
scope = inv.apply(lambda r: get_scope(r, fracs), axis=1)
scope_df = pd.concat([inv, scope], axis=1)

# ── 4. Compute Venn segments for 2022 ─────────────────────────────────────────
# For each category, split emissions into 8 Venn segments:
# S∩F∩E | S∩E_only | S∩F_only | S_only | F_only | F∩E_only | E_only | uncovered

def compute_venn_row(row, scen="central"):
    em   = row["emissions_GgCO2e"]
    in_S = row["in_S"]
    f    = row[f"f_frac_{scen}"]
    e    = row[f"e_frac_{scen}"]

    if in_S:
        # S is total. F and E are fractions of S.
        # For overlap categories, assume F and E are INDEPENDENT within S
        # (i.e., the NG-exempt fraction and ETS threshold fraction apply
        #  to the same pool of emissions independently)
        # For [1A1]: F fraction is 0.38%, E fraction is 100%
        #   → all non-NG is in E (power plants); NG part is also in E
        #   → S∩F∩E  = em × f × 1 (non-NG fuel at large plants — all in E since all in ETS)
        #   → S∩E_only = em × (1-f) × e (NG fraction × ETS = large plant NG)
        #   → S∩F_only = em × f × (1-e) (non-NG at non-ETS sources — essentially 0 for 1A1)
        #   → S_only   = em × (1-f) × (1-e)
        # For 1A2: f = taxable fraction, e = ETS fraction
        #   These are treated as independent (random assignment assumption)
        SE_F  = em * f * e          # S∩F∩E
        SE    = em * (1-f) * e      # S∩E only (NG in ETS; no federal tax)
        SF    = em * f * (1-e)      # S∩F only (taxable, below ETS threshold)
        S_only= em * (1-f) * (1-e) # S only (NG, below ETS threshold)
        F_only    = 0.0             # can't be in F but not S for stationary (S includes all stationary)
        FE_only   = 0.0
        E_only    = 0.0
        uncovered = 0.0
    else:
        # Not in S.  Can still be in F and/or E.
        # For transport (1A3): in F, not in E
        # For AFOLU, waste: in none
        # For 1A4c: not S, but in F (federal tax covers ag fuels)
        SE_F  = 0.0
        SE    = em * (1-f) * e      # E but not S — in practice 0 (E ⊂ S for all relevant)
        SF    = 0.0
        S_only= 0.0
        F_only    = em * f * (1-e)  # F but not S, not E
        FE_only   = em * f * e      # F and E but not S — in practice 0
        E_only    = em * (1-f) * e  # E but not F, not S — in practice 0
        uncovered = em * (1-f) * (1-e)

    return pd.Series({
        "S_F_E":    SE_F,
        "S_E_only": SE,
        "S_F_only": SF,
        "S_only":   S_only,
        "F_only":   F_only,
        "F_E_only": FE_only,
        "E_only":   E_only,
        "uncovered":uncovered,
    })


for scen in ["central", "low", "high"]:
    venn = scope_df.apply(lambda r: compute_venn_row(r, scen), axis=1)
    for col in venn.columns:
        scope_df[f"{col}_{scen}"] = venn[col]

# Save tax scope table
scope_df.to_csv(os.path.join(PROC_DIR, "durango_tax_scope_2022.csv"), index=False)
print(f"\nSaved: data/processed/durango_tax_scope_2022.csv")

# ── 5. Summarise Venn segments for 2022 ──────────────────────────────────────
SEGS = ["S_F_E","S_E_only","S_F_only","S_only","F_only","F_E_only","E_only","uncovered"]
summary_2022 = {}
for scen in ["central","low","high"]:
    seg_totals = {s: scope_df[f"{s}_{scen}"].sum() for s in SEGS}
    summary_2022[scen] = seg_totals

# Derived instrument totals
def instrument_totals(segs):
    S = segs["S_F_E"] + segs["S_E_only"] + segs["S_F_only"] + segs["S_only"]
    F = segs["S_F_E"] + segs["S_F_only"] + segs["F_only"]   + segs["F_E_only"]
    E = segs["S_F_E"] + segs["S_E_only"] + segs["F_E_only"] + segs["E_only"]
    union = sum(segs[s] for s in SEGS if s != "uncovered")
    return S, F, E, union

print("\n2022 Venn decomposition (central estimate):")
for s in SEGS:
    v = summary_2022["central"][s]
    pct = v / STATE_TOTAL_2022 * 100
    print(f"  {s:<12}: {v:8.1f} GgCO2e  ({pct:5.1f}% of state)")

S_c, F_c, E_c, union_c = instrument_totals(summary_2022["central"])
print(f"\n  STATE TAX (S) gross  : {S_c:.1f}  ({S_c/STATE_TOTAL_2022*100:.1f}%)")
print(f"  FEDERAL TAX (F)      : {F_c:.1f}  ({F_c/STATE_TOTAL_2022*100:.1f}%)")
print(f"  PILOT ETS (E)        : {E_c:.1f}  ({E_c/STATE_TOTAL_2022*100:.1f}%)")
print(f"  UNION S∪F∪E          : {union_c:.1f}  ({union_c/STATE_TOTAL_2022*100:.1f}%)")
print(f"  Uncovered            : {summary_2022['central']['uncovered']:.1f}  "
      f"({summary_2022['central']['uncovered']/STATE_TOTAL_2022*100:.1f}%)")

# ── 6. Sector growth rates and extrapolation 2022→2025/2026 ──────────────────
# Central rates derived from 2010–2022 historical TCAMs, adjusted for:
# - [1A1]: new 350 MW Lerdo CC plant enters 2024 → uptick then efficiency gains
# - [1A2]: COVID recovery normalizing; [1A2d] paper/pulp stable
# - [1A3]: population growth + vehicle fleet expansion
# - Low/High: ±40% of central rate (wider than Colima given 2022 base uncertainty)

GROWTH = {
    # (central, low, high) annual rate
    "electricity_generation": (-0.010,  -0.030,  0.005),   # new plant + NG efficiency
    "manufacturing":          ( 0.025,  -0.010,  0.050),   # recovery from COVID dip
    "transport":              ( 0.010,  -0.010,  0.025),   # fleet growth
    "other_energy":           ( 0.005,  -0.010,  0.015),   # residential/commercial slow growth
    "non_specified":          ( 0.000,  -0.020,  0.020),
    "fugitive":               ( 0.005,  -0.010,  0.020),   # NG infrastructure growth
    "piup_metals":            ( 0.008,  -0.020,  0.030),
    "piup_lubricants":        ( 0.005,  -0.010,  0.020),
    "piup_hfcs":              ( 0.015,   0.005,  0.030),   # HFC use growing
    "afolu":                  ( 0.002,  -0.010,  0.015),
    "waste":                  ( 0.020,   0.005,  0.035),
}

rows_extrap = []
for _, row in scope_df.iterrows():
    sg = row["sector_group"]
    g_c, g_l, g_h = GROWTH.get(sg, (0.0, 0.0, 0.0))
    em_base = row["emissions_GgCO2e"]

    for yr in [2025, 2026]:
        n = yr - 2022
        for scen, rate in [("central", g_c), ("low", g_l), ("high", g_h)]:
            em_yr = em_base * (1 + rate) ** n
            r = row.to_dict()
            r["year"]     = yr
            r["scenario"] = scen
            r["emissions_GgCO2e"] = em_yr
            rows_extrap.append(r)

extrap = pd.DataFrame(rows_extrap)

# Recompute Venn segments for extrapolated data
# (scope fractions stay constant; only emissions change)
for scen in ["central","low","high"]:
    mask = extrap["scenario"] == scen
    venn = extrap[mask].apply(lambda r: compute_venn_row(r, scen), axis=1)
    for col in venn.columns:
        extrap.loc[mask, f"{col}_computed"] = venn[col].values

extrap.to_csv(os.path.join(PROC_DIR, "durango_extrapolated_2025_2026.csv"), index=False)
print(f"\nSaved: data/processed/durango_extrapolated_2025_2026.csv")

# ── 7. Build final overlap estimates table ────────────────────────────────────
records = []

def make_record(year, scenario, segs, total):
    S, F, E, union = instrument_totals(segs)
    r = dict(
        year=year, scenario=scenario,
        state_total_GgCO2e=total,
        # Instrument gross coverage
        S_gross_GgCO2e=S, S_pct=S/total*100,
        F_gross_GgCO2e=F, F_pct=F/total*100,
        E_gross_GgCO2e=E, E_pct=E/total*100,
        # Venn segments
        S_F_E_GgCO2e=segs["S_F_E"],   S_F_E_pct=segs["S_F_E"]/total*100,
        S_E_only_GgCO2e=segs["S_E_only"], S_E_only_pct=segs["S_E_only"]/total*100,
        S_F_only_GgCO2e=segs["S_F_only"], S_F_only_pct=segs["S_F_only"]/total*100,
        S_only_GgCO2e=segs["S_only"],  S_only_pct=segs["S_only"]/total*100,
        F_only_GgCO2e=segs["F_only"],  F_only_pct=segs["F_only"]/total*100,
        uncovered_GgCO2e=segs["uncovered"], uncovered_pct=segs["uncovered"]/total*100,
        # Net unique coverage
        S_net_GgCO2e=S,  # all of S is unique relative to just F (S adds NG stationary)
        union_GgCO2e=union, union_pct=union/total*100,
        # Overlap scalars
        S_F_overlap=segs["S_F_E"]+segs["S_F_only"],
        S_E_overlap=segs["S_F_E"]+segs["S_E_only"],
        F_E_overlap=segs["S_F_E"]+segs["F_E_only"],
        estimation_tier="Tier 3",
        notes="NG exempt from F but not S; ETS threshold via Pareto per subsector"
    )
    return r

# 2022 base year
extrap_state_totals = {}
for yr in [2025, 2026]:
    for scen in ["central","low","high"]:
        mask = (extrap["scenario"]==scen) & (extrap["year"]==yr)
        sub  = extrap[mask]
        total_yr = sub["emissions_GgCO2e"].sum()
        # Recompute from saved Venn columns
        seg_totals = {s: sub[f"{s}_computed"].sum() for s in SEGS}
        extrap_state_totals[(yr,scen)] = (total_yr, seg_totals)
        records.append(make_record(yr, scen, seg_totals, total_yr))

# Add 2022
for scen in ["central","low","high"]:
    seg_totals = {s: scope_df[f"{s}_{scen}"].sum() for s in SEGS}
    records.append(make_record(2022, scen, seg_totals, STATE_TOTAL_2022))

overlap_df = pd.DataFrame(records).sort_values(["year","scenario"])
overlap_df.to_csv(os.path.join(PROC_DIR, "durango_overlap_estimates.csv"), index=False)
print(f"Saved: data/processed/durango_overlap_estimates.csv")

# ── 8. Print summary ─────────────────────────────────────────────────────────
print("\n" + "="*65)
print("DURANGO COVERAGE ESTIMATES — CENTRAL SCENARIO")
print("="*65)
for yr in [2022, 2025, 2026]:
    row_c = overlap_df[(overlap_df["year"]==yr) & (overlap_df["scenario"]=="central")].iloc[0]
    row_l = overlap_df[(overlap_df["year"]==yr) & (overlap_df["scenario"]=="low")].iloc[0]
    row_h = overlap_df[(overlap_df["year"]==yr) & (overlap_df["scenario"]=="high")].iloc[0]

    print(f"\n  Year {yr}:")
    print(f"    State total:   {row_c['state_total_GgCO2e']:7.0f} GgCO2e")
    print(f"    S (state tax): {row_c['S_gross_GgCO2e']:7.0f}  ({row_c['S_pct']:.1f}%)")
    print(f"    F (federal):   {row_c['F_gross_GgCO2e']:7.0f}  ({row_c['F_pct']:.1f}%)")
    print(f"    E (ETS):       {row_c['E_gross_GgCO2e']:7.0f}  ({row_c['E_pct']:.1f}%)")
    print(f"    S∩F∩E:         {row_c['S_F_E_GgCO2e']:7.0f}  ({row_c['S_F_E_pct']:.1f}%)")
    print(f"    S∩E only:      {row_c['S_E_only_GgCO2e']:7.0f}  ({row_c['S_E_only_pct']:.1f}%)")
    print(f"    S∩F only:      {row_c['S_F_only_GgCO2e']:7.0f}  ({row_c['S_F_only_pct']:.1f}%)")
    print(f"    S only:        {row_c['S_only_GgCO2e']:7.0f}  ({row_c['S_only_pct']:.1f}%)")
    print(f"    F only:        {row_c['F_only_GgCO2e']:7.0f}  ({row_c['F_only_pct']:.1f}%)")
    print(f"    Union S∪F∪E:   {row_c['union_GgCO2e']:7.0f}  ({row_c['union_pct']:.1f}%)")
    rng_S = f"[{row_l['S_gross_GgCO2e']:.0f}–{row_h['S_gross_GgCO2e']:.0f}]"
    rng_F = f"[{row_l['F_gross_GgCO2e']:.0f}–{row_h['F_gross_GgCO2e']:.0f}]"
    rng_E = f"[{row_l['E_gross_GgCO2e']:.0f}–{row_h['E_gross_GgCO2e']:.0f}]"
    print(f"    Ranges:  S {rng_S}  F {rng_F}  E {rng_E}")

print("\n✓ 02_estimate.py complete\n")
