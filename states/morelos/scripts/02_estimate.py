"""
02_estimate.py — Morelos Carbon Pricing Overlap Analysis
=========================================================
Case: Mexico — Morelos state carbon tax (S) × Federal IEPS carbon tax (F) ×
      Mexico Pilot ETS (E)
Estimation tier: Tier 3
Base year: 2014  |  Target years: 2025, 2026
Author: World Bank Climate Change Group — State & Trends of Carbon Pricing

Instruments:
──────────────────────────────────────────────────────────────────────────────
S  Morelos state carbon tax
   Scope:    CO2, CH4, N2O, HFCs, PFCs, SF6 from STATIONARY sources
   Exempt:   All mobile sources; maritime; small-scale agricultural activities
   NG exempt: NO (unlike federal tax)
   CRITICAL GAP: HFCs/PFCs/SF6 absent from 2014 inventory → data gap flagged

F  Mexico federal IEPS carbon tax (Art. 2o-C)
   Scope:    Upstream fuel levy; all fossil fuels EXCEPT natural gas
             Covers stationary AND mobile combustion
   Exempt:   Natural gas; process emissions; fugitive emissions

E  Mexico Pilot ETS
   Scope:    Direct emissions ≥ 25,000 tCO2e/yr; legal scope (non-binding pilot)

Key analytical structure of Morelos:
   1. CEMENT dominates fixed sources at 60% of total (901,618 Mg CO2)
      - ~60% of cement CO2 is calcination PROCESS → in S, NOT in F
      - ~40% combustion (petcoke/FO) → in both S and F
   2. NG is only 4% of industrial energy → F exemption has minimal impact
   3. Mobile (49.2% of state CO2) is F-only; exempt from S
   4. Livestock CH4 (89% of area CH4) is exempt from all instruments
   5. Domestic wood CO2 (~12% of state CO2) is BIOGENIC → exempt from both S and F
   6. HFCs/PFCs/SF6 not in inventory → reported S coverage is UNDERSTATED

Units note:
   Base inventory in Mg/year (tonnes/year) — converted to GgCO2e in 01_clean.py
   1 Mg = 0.001 Gg; state total ≈ 5,682 GgCO2e (AR5 GWPs)
"""

import pandas as pd
import numpy as np
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR   = os.path.dirname(SCRIPT_DIR)
PROC_DIR   = os.path.join(BASE_DIR, "data", "processed")
os.makedirs(PROC_DIR, exist_ok=True)

print("=" * 65)
print("Morelos 02_estimate.py — scope mapping and overlap estimation")
print("=" * 65)

# ── 1. Load data ────────────────────────────────────────────────────────────
inv   = pd.read_csv(os.path.join(PROC_DIR, "morelos_inventory_2014.csv"))
fracs = pd.read_csv(os.path.join(PROC_DIR, "morelos_fuel_fractions_2014.csv"))
cement= pd.read_csv(os.path.join(PROC_DIR, "morelos_cement_process_split_2014.csv"))

# ── 2. Scope mapping function ────────────────────────────────────────────────
# Returns in_S, f_frac (central/low/high), e_frac (central/low/high)

def get_scope(row, fracs_df, cement_df):
    cat = row["category"]
    src = row["source_type"]
    sg  = row["ipcc_sector"]

    in_S = False
    f_c = f_l = f_h = 0.0
    e_c = e_l = e_h = 0.0
    note = ""

    # ── FIXED SOURCES ────────────────────────────────────────────────────────
    if src == "FIXED":
        in_S = True  # all fixed sources covered by state tax

        if cat == "Cemento_y_cal":
            # Cement: special treatment
            # F covers only combustion CO2 (petcoke/FO fraction of cement total)
            # process CO2 (calcination) is NOT covered by F
            c_c = cement_df[cement_df["scenario"]=="central"].iloc[0]
            c_l = cement_df[cement_df["scenario"]=="low"].iloc[0]
            c_h = cement_df[cement_df["scenario"]=="high"].iloc[0]
            fr  = fracs_df[fracs_df["category"]=="Cemento_y_cal"].iloc[0]
            f_c = (1 - c_c["process_frac"]) * fr["f_frac_central"]
            f_l = (1 - c_h["process_frac"]) * fr["f_frac_low"]
            f_h = (1 - c_l["process_frac"]) * fr["f_frac_high"]
            e_c = fr["ets_frac_central"]
            e_l = fr["ets_frac_low"]
            e_h = fr["ets_frac_high"]
            note = f"Cement: F={f_c:.2f}(central)=combustion frac × non-NG frac; E={e_c}"

        elif cat in fracs_df["category"].values:
            fr  = fracs_df[fracs_df["category"]==cat].iloc[0]
            f_c = fr["f_frac_central"]
            f_l = fr["f_frac_low"]
            f_h = fr["f_frac_high"]
            e_c = fr["ets_frac_central"]
            e_l = fr["ets_frac_low"]
            e_h = fr["ets_frac_high"]
            note = f"Fixed {cat}: F={f_c:.2f}; E={e_c}"

        else:
            # Other manufacturing — use OTHER_MANUFACTURING fracs
            fr  = fracs_df[fracs_df["category"]=="OTHER_MANUFACTURING"].iloc[0]
            f_c = fr["f_frac_central"]
            f_l = fr["f_frac_low"]
            f_h = fr["f_frac_high"]
            e_c = fr["ets_frac_central"]
            e_l = fr["ets_frac_low"]
            e_h = fr["ets_frac_high"]
            note = f"Fixed other manufacturing: F={f_c:.2f}; E={e_c}"

    # ── AREA SOURCES ─────────────────────────────────────────────────────────
    elif src == "AREA":
        if cat == "Combustion_industrial":
            in_S = True
            fr   = fracs_df[fracs_df["category"]=="Combustion_industrial"].iloc[0]
            f_c  = fr["f_frac_central"]
            f_l  = fr["f_frac_low"]
            f_h  = fr["f_frac_high"]
            e_c  = e_l = e_h = 0.0
            note = "Area industrial combustion: small facilities in S; below ETS threshold"

        elif cat == "Combustion_comercial":
            # Commercial combustion: small-scale; in S (stationary); below ETS
            in_S = True
            fr   = fracs_df[fracs_df["category"]=="Combustion_comercial"].iloc[0]
            f_c  = fr["f_frac_central"]
            f_l  = fr["f_frac_low"]
            f_h  = fr["f_frac_high"]
            e_c  = e_l = e_h = 0.0
            note = "Commercial combustion: S(stationary); F(LPG dominant); E=0"

        elif cat == "Combustion_doméstica":
            # Domestic combustion: primarily leña (biogenic CO2)
            # For CARBON PRICING COVERAGE:
            # - CO2 from wood is biogenic → NOT covered by S or F
            # - CH4/N2O from domestic combustion ARE fossil-equivalent for GWP
            # - LPG portion of domestic combustion: in S and F
            # Assumption: 70% of domestic combustion CO2 is biogenic (wood);
            # 30% is from LPG/fossil (taxable)
            in_S = True
            FOSSIL_CO2_FRAC = 0.30  # est. from LPG share in residential
            f_c = FOSSIL_CO2_FRAC * 0.90  # LPG (taxable); small NG exempt
            f_l = 0.20 * 0.85
            f_h = 0.45 * 0.95
            e_c = e_l = e_h = 0.0
            note = "Domestic: S(stationary); ~70% biogenic wood CO2 not priced; LPG fraction in F; E=0"

        elif cat in ("Quemas_agricolas","Combustion_agricola","Incendios_forestales"):
            # Agricultural burning / forest fires: mobile/agricultural activities
            # Exempt from state tax ("small-scale agricultural activities")
            in_S = False
            f_c  = f_l = f_h = 0.0  # biomass burning not covered by IEPS fuel tax
            e_c  = e_l = e_h = 0.0
            note = "Ag burning / forest fires: exempt from state tax; not in F or E"

        elif cat == "Emisiones_ganaderas":
            # Livestock: agricultural activity — exempt from state tax
            in_S = False
            f_c  = f_l = f_h = 0.0
            e_c  = e_l = e_h = 0.0
            note = "Livestock CH4: exempt from state tax (agricultural); not in F or E"

        elif cat == "Aguas_residuales":
            # Wastewater: area-source (municipal); S scope unclear for small-scale
            # Conservatively: small municipal facilities exempt per "small-scale" clause
            in_S = False
            f_c  = f_l = f_h = 0.0
            e_c  = e_l = e_h = 0.0
            note = "Wastewater (area source): not in state tax scope (small-scale); not in F or E"

        else:  # Otras_area: construction dust, asphalt, etc.
            in_S = False
            f_c  = f_l = f_h = 0.0
            e_c  = e_l = e_h = 0.0
            note = "Other area sources: not in stationary emissions scope"

    elif src == "WASTE":
        # Wastewater: not in state tax scope; not in F or E
        in_S = False
        f_c = f_l = f_h = 0.0
        e_c = e_l = e_h = 0.0
        note = "Wastewater (WASTE source): not in Morelos state tax scope; not in F or E"

    elif src in ("MOBILE", "MOBILE_NONROAD"):
        # All mobile: exempt from Morelos state tax
        in_S = False
        if cat == "Aviacion":
            f_c = f_l = f_h = 1.0  # jet fuel taxable
        elif cat in ("Locomotoras", "Terminal_autobuses"):
            f_c = f_l = f_h = 0.90  # mostly diesel
        elif cat == "Lanchas_recreativas":
            f_c = f_l = f_h = 1.0
        else:
            # On-road: gasoline+diesel; all taxable
            f_c = f_l = f_h = 1.0
        e_c = e_l = e_h = 0.0  # transport not in Mexico Pilot ETS
        note = f"Mobile {cat}: exempt from state tax; F=taxable fuels; E=0"

    return pd.Series({
        "in_S": in_S,
        "f_frac_central": f_c, "f_frac_low": f_l, "f_frac_high": f_h,
        "e_frac_central": e_c, "e_frac_low":  e_l, "e_frac_high":  e_h,
        "scope_note": note,
    })


scope = inv.apply(lambda r: get_scope(r, fracs, cement), axis=1)
scope_df = pd.concat([inv, scope], axis=1)

# ── 3. Venn segments ──────────────────────────────────────────────────────────
SEGS = ["S_F_E","S_E_only","S_F_only","S_only","F_only","F_E_only","E_only","uncovered"]

def compute_venn(row, scen="central"):
    em   = row["total_GgCO2e"]
    in_S = row["in_S"]
    f    = row[f"f_frac_{scen}"]
    e    = row[f"e_frac_{scen}"]

    if in_S:
        return pd.Series({
            "S_F_E":    em * f * e,
            "S_E_only": em * (1-f) * e,
            "S_F_only": em * f * (1-e),
            "S_only":   em * (1-f) * (1-e),
            "F_only":   0.0,
            "F_E_only": 0.0,
            "E_only":   0.0,
            "uncovered":0.0,
        })
    else:
        return pd.Series({
            "S_F_E":    0.0,
            "S_E_only": 0.0,
            "S_F_only": 0.0,
            "S_only":   0.0,
            "F_only":   em * f * (1-e),
            "F_E_only": em * f * e,
            "E_only":   em * (1-f) * e,
            "uncovered":em * (1-f) * (1-e),
        })

for scen in ["central","low","high"]:
    v = scope_df.apply(lambda r: compute_venn(r, scen), axis=1)
    for col in v.columns:
        scope_df[f"{col}_{scen}"] = v[col]

scope_df.to_csv(os.path.join(PROC_DIR, "morelos_tax_scope_2014.csv"), index=False)
print(f"\nSaved: data/processed/morelos_tax_scope_2014.csv")

# ── 4. 2014 summary ────────────────────────────────────────────────────────────
STATE_TOTAL_2014 = scope_df["total_GgCO2e"].sum()

def instrument_totals(segs):
    S = segs["S_F_E"] + segs["S_E_only"] + segs["S_F_only"] + segs["S_only"]
    F = segs["S_F_E"] + segs["S_F_only"] + segs["F_only"]   + segs["F_E_only"]
    E = segs["S_F_E"] + segs["S_E_only"] + segs["F_E_only"] + segs["E_only"]
    union = sum(segs[s] for s in SEGS if s != "uncovered")
    return S, F, E, union

summary_2014 = {scen: {s: scope_df[f"{s}_{scen}"].sum() for s in SEGS}
                for scen in ["central","low","high"]}

S_c, F_c, E_c, union_c = instrument_totals(summary_2014["central"])
print(f"\n2014 base year results (central):")
print(f"  State total:     {STATE_TOTAL_2014:8.1f} GgCO2e")
print(f"  S (state tax):   {S_c:8.1f}  ({S_c/STATE_TOTAL_2014*100:.1f}%)")
print(f"  F (federal):     {F_c:8.1f}  ({F_c/STATE_TOTAL_2014*100:.1f}%)")
print(f"  E (ETS):         {E_c:8.1f}  ({E_c/STATE_TOTAL_2014*100:.1f}%)")
for seg in SEGS:
    v = summary_2014["central"][seg]
    print(f"  {seg:<12}: {v:7.1f}  ({v/STATE_TOTAL_2014*100:.1f}%)")

# ── 5. Growth rates — 11-year extrapolation ────────────────────────────────────
# 2014 → 2025 = 11 years; 2014 → 2026 = 12 years
# Rates drawn from national-level trends (INECC INEGYCEI); no state time series
# Morelos-specific: small industrial state; cement dominant; limited heavy industry growth
# Uncertainty MUCH wider than Durango (±60% of central for 11-year horizon)
#
# Key forward adjustments:
# - Cement: new capacity unlikely; some efficiency improvements; modest growth
# - Mobile (transport): national trend +1.5-2%/yr; fleet continues growing
# - Livestock/area CH4: stable or slight decline (national trend)
# - Area combustion domestic: declining wood use (urbanisation, LPG substitution)

GROWTH = {
    # (central, low, high) annual rates — wider ranges for 11-year horizon
    "industrial_process_cement":    (0.005, -0.020,  0.025),
    "industrial_process_glass":     (0.008, -0.015,  0.030),
    "manufacturing_chemical":       (0.010, -0.020,  0.035),
    "manufacturing_pulp_paper":     (0.005, -0.025,  0.030),
    "manufacturing_food_bev":       (0.010, -0.015,  0.035),
    "manufacturing_petro_products": (0.005, -0.025,  0.030),
    "manufacturing_metals":         (0.005, -0.030,  0.030),
    "manufacturing_nonmet_minerals":(0.005, -0.020,  0.025),
    "manufacturing_plastics":       (0.010, -0.020,  0.035),
    "manufacturing_petrochem":      (0.005, -0.020,  0.025),
    "manufacturing_automotive":     (0.010, -0.020,  0.040),
    "manufacturing_electrical":     (0.010, -0.020,  0.040),
    "manufacturing_textiles":       (0.000, -0.025,  0.020),
    "area_residential":             (-0.010, -0.030,  0.010), # leña use declining
    "area_commercial":              (0.015, -0.010,  0.035),
    "area_industrial_small":        (0.010, -0.020,  0.035),
    "area_agri_combustion":         (0.000, -0.020,  0.020),
    "afolu_livestock":              (0.005, -0.015,  0.025),
    "afolu_burning":                (0.000, -0.030,  0.030),
    "afolu_fire":                   (0.000, -0.050,  0.050),
    "waste_wastewater":             (0.020, -0.005,  0.040),
    "area_other":                   (0.010, -0.020,  0.030),
    "mobile_road":                  (0.015, -0.005,  0.030), # national fleet growth
    "mobile_nonroad":               (0.010, -0.015,  0.025),
}

rows_extrap = []
for _, row in scope_df.iterrows():
    sg   = row["ipcc_sector"]
    g_c, g_l, g_h = GROWTH.get(sg, (0.010, -0.020, 0.030))
    em_base = row["total_GgCO2e"]
    for yr in [2025, 2026]:
        n = yr - 2014
        for scen, rate in [("central", g_c), ("low", g_l), ("high", g_h)]:
            r = row.to_dict()
            r["year"]            = yr
            r["scenario"]        = scen
            r["total_GgCO2e"]    = em_base * (1 + rate) ** n  # overwrite base value
            rows_extrap.append(r)

extrap = pd.DataFrame(rows_extrap)

# Recompute Venn for extrapolated emissions
for scen in ["central","low","high"]:
    mask = extrap["scenario"] == scen
    venn = extrap[mask].apply(lambda r: compute_venn(r, scen), axis=1)
    for col in venn.columns:
        extrap.loc[mask, f"{col}_computed"] = venn[col].values

extrap.to_csv(os.path.join(PROC_DIR, "morelos_extrapolated_2025_2026.csv"), index=False)
print(f"\nSaved: data/processed/morelos_extrapolated_2025_2026.csv")

# ── 6. Build overlap estimates table ──────────────────────────────────────────
records = []

def make_record(year, scenario, segs, total):
    S, F, E, union = instrument_totals(segs)
    return dict(
        year=year, scenario=scenario,
        state_total_GgCO2e=total,
        S_gross_GgCO2e=S, S_pct=S/total*100,
        F_gross_GgCO2e=F, F_pct=F/total*100,
        E_gross_GgCO2e=E, E_pct=E/total*100,
        S_F_E_GgCO2e=segs["S_F_E"],   S_F_E_pct=segs["S_F_E"]/total*100,
        S_E_only_GgCO2e=segs["S_E_only"], S_E_only_pct=segs["S_E_only"]/total*100,
        S_F_only_GgCO2e=segs["S_F_only"], S_F_only_pct=segs["S_F_only"]/total*100,
        S_only_GgCO2e=segs["S_only"],  S_only_pct=segs["S_only"]/total*100,
        F_only_GgCO2e=segs["F_only"],  F_only_pct=segs["F_only"]/total*100,
        uncovered_GgCO2e=segs["uncovered"], uncovered_pct=segs["uncovered"]/total*100,
        union_GgCO2e=union, union_pct=union/total*100,
        S_F_overlap=segs["S_F_E"]+segs["S_F_only"],
        S_E_overlap=segs["S_F_E"]+segs["S_E_only"],
        estimation_tier="Tier 3",
        data_gap_note="HFCs/PFCs/SF6 absent from 2014 inventory; S coverage understated",
        base_year_note="2014 base; 11-year extrapolation to 2025/2026; wider uncertainty"
    )

# 2014 base
for scen in ["central","low","high"]:
    segs = summary_2014[scen]
    records.append(make_record(2014, scen, segs, STATE_TOTAL_2014))

# 2025, 2026
for yr in [2025, 2026]:
    for scen in ["central","low","high"]:
        mask = (extrap["scenario"]==scen) & (extrap["year"]==yr)
        sub  = extrap[mask]
        total_yr = sub["total_GgCO2e"].sum()
        seg_totals = {s: sub[f"{s}_computed"].sum() for s in SEGS}
        records.append(make_record(yr, scen, seg_totals, total_yr))

overlap_df = pd.DataFrame(records).sort_values(["year","scenario"])
overlap_df.to_csv(os.path.join(PROC_DIR, "morelos_overlap_estimates.csv"), index=False)
print(f"Saved: data/processed/morelos_overlap_estimates.csv")

# ── 7. Print summary ──────────────────────────────────────────────────────────
print("\n" + "="*65)
print("MORELOS COVERAGE ESTIMATES — CENTRAL SCENARIO")
print("="*65)
for yr in [2014, 2025, 2026]:
    r_c = overlap_df[(overlap_df["year"]==yr) & (overlap_df["scenario"]=="central")].iloc[0]
    r_l = overlap_df[(overlap_df["year"]==yr) & (overlap_df["scenario"]=="low")].iloc[0]
    r_h = overlap_df[(overlap_df["year"]==yr) & (overlap_df["scenario"]=="high")].iloc[0]
    print(f"\n  Year {yr}:")
    print(f"    State total:    {r_c['state_total_GgCO2e']:7.0f} GgCO2e")
    print(f"    S (state tax):  {r_c['S_gross_GgCO2e']:7.0f}  ({r_c['S_pct']:.1f}%)")
    print(f"    F (federal):    {r_c['F_gross_GgCO2e']:7.0f}  ({r_c['F_pct']:.1f}%)")
    print(f"    E (ETS):        {r_c['E_gross_GgCO2e']:7.0f}  ({r_c['E_pct']:.1f}%)")
    print(f"    S_F_E:          {r_c['S_F_E_GgCO2e']:7.0f}  ({r_c['S_F_E_pct']:.1f}%)")
    print(f"    S_E only:       {r_c['S_E_only_GgCO2e']:7.0f}  ({r_c['S_E_only_pct']:.1f}%)")
    print(f"    S_F only:       {r_c['S_F_only_GgCO2e']:7.0f}  ({r_c['S_F_only_pct']:.1f}%)")
    print(f"    S only:         {r_c['S_only_GgCO2e']:7.0f}  ({r_c['S_only_pct']:.1f}%)")
    print(f"    F only:         {r_c['F_only_GgCO2e']:7.0f}  ({r_c['F_only_pct']:.1f}%)")
    print(f"    Union S+F+E:    {r_c['union_GgCO2e']:7.0f}  ({r_c['union_pct']:.1f}%)")
    rS = f"[{r_l['S_gross_GgCO2e']:.0f}-{r_h['S_gross_GgCO2e']:.0f}]"
    rF = f"[{r_l['F_gross_GgCO2e']:.0f}-{r_h['F_gross_GgCO2e']:.0f}]"
    rE = f"[{r_l['E_gross_GgCO2e']:.0f}-{r_h['E_gross_GgCO2e']:.0f}]"
    print(f"    Ranges: S{rS} F{rF} E{rE}")

print("\n⚠  IMPORTANT CAVEATS:")
print("  1. HFCs/PFCs/SF6 ABSENT from inventory — S coverage understated")
print("  2. 11-year extrapolation — ranges should be treated as illustrative")
print("  3. Biogenic domestic wood CO2 (~11% of state) effectively in S but unpriced")
print("  4. ETS = legal scope; non-binding pilot")
print("\n✓ 02_estimate.py complete\n")
