"""
02_estimate.py -- San Luis Potosi Carbon Pricing Overlap Analysis
==================================================================
Case: Mexico -- SLP state carbon tax (S) x Federal IEPS carbon tax (F) x
      Mexico Pilot ETS (E)
Estimation tier: Tier 3 (fuel-fraction for F; Pareto/threshold for E)
Base year: Annual average 2007-2014 (from cumulative inventory / 8)
GWPs: AR5 (CH4=28, N2O=265) -- converted from SAR in 01_clean.py

Instruments:
  S  SLP state carbon tax (Ley de Hacienda, effective 1 Jan 2025)
     Scope:   CO2, CH4, N2O, black carbon, CFCs, HCFCs, HFCs, PFCs (NO SF6)
              Direct emissions from fixed sources in productive processes
              Scope 1 only (confirmed from primary legislation Art. 36 SEXTIES)
     Covered: [1A1] electricity, [1A2] manufacturing, [1A4a] commercial,
              ALL IPPU process emissions, agricultural combustion
     Exempt:  Transport (mobile), residential, AFOLU non-combustion, waste,
              biogenic (lena, bagazo)
     Threshold: NONE. All fixed-source productive emissions covered.
              (Fiscal stimulus grants 100% payment exemption below 300 tCO2e/yr
               but facilities remain legally covered)

  F  Federal IEPS carbon tax
     Scope:   Upstream fuel tax on all fossil fuels EXCEPT natural gas
     Covers:  Stationary AND mobile combustion of non-NG fuels
     Exempt:  Natural gas (statutory), process emissions, fugitive, HFCs

  E  Mexico Pilot ETS
     Scope:   Direct emissions from facilities >= 25,000 tCO2e/yr
     Sectors: Electricity, manufacturing, O&G, large industry, IPPU
     Note:    Non-binding pilot; legal scope used as upper bound

Key SLP-specific features:
  1. Industrial fuel mix 65% non-NG (GLP 53% + diesel 12%) -- highest of all states
     -> S intersect F overlap will be substantial for manufacturing
  2. Electricity ~43% NG / ~57% combustoleo+diesel -- Villa de Reyes effect
     -> Federal tax covers ~57% of electricity (unlike Durango/Queretaro ~0%)
  3. Large cement/cal sector (20.44 Mt cumul CO2) -- process CO2 in S and E but NOT F
  4. Major metalurgia with significant N2O (SAR->AR5 changes this value)
  5. No HFC data in inventory -- understates S coverage

Outputs:
  data/processed/slp_tax_scope.csv
  data/processed/slp_overlap_estimates.csv
"""

import pandas as pd
import numpy as np
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR   = os.path.dirname(SCRIPT_DIR)
PROC_DIR   = os.path.join(BASE_DIR, "data", "processed")

print("=" * 70)
print("San Luis Potosi 02_estimate.py -- scope mapping & overlap estimation")
print("=" * 70)

# ── 1. Load processed data ──────────────────────────────────────────────
inv   = pd.read_csv(os.path.join(PROC_DIR, "slp_inventory_annual_ar5.csv"))
fracs = pd.read_csv(os.path.join(PROC_DIR, "slp_fuel_fractions.csv"))

# Exclude biogenic
inv = inv[inv["sector_group"] != "biogenic"].copy().reset_index(drop=True)

STATE_TOTAL = inv["emissions_GgCO2e"].sum()
print(f"\nState total (annual avg, AR5, excl biogenic): {STATE_TOTAL:.1f} GgCO2e/yr")

# ── 2. Scope mapping ────────────────────────────────────────────────────
# For each category: (in_S, f_frac, e_frac) for central/low/high scenarios

def get_fracs(cat):
    """Get fuel fractions from the fractions table."""
    row = fracs[fracs["category"] == cat]
    if len(row) == 0:
        return None
    return row.iloc[0]

def map_scope(row):
    sg = row["sector_group"]
    code = row["ipcc_code"]

    in_S = False
    f_c = f_l = f_h = 0.0
    e_c = e_l = e_h = 0.0
    note = ""

    # ── ELECTRICITY GENERATION ──────────────────────────────────────
    if sg == "electricity_generation":
        in_S = True
        fr = get_fracs("1A1")
        ng_c = fr["ng_exempt_frac_central"]
        ng_l = fr["ng_exempt_frac_low"]
        ng_h = fr["ng_exempt_frac_high"]
        f_c, f_l, f_h = 1-ng_c, 1-ng_h, 1-ng_l
        e_c = fr["ets_frac_central"]
        e_l = fr["ets_frac_low"]
        e_h = fr["ets_frac_high"]
        note = f"1A1: S(all); F(non-NG ~{(1-ng_c)*100:.0f}%); E({e_c*100:.0f}%); Villa de Reyes combustoleo drives high F"

    # ── MANUFACTURING ───────────────────────────────────────────────
    elif sg == "manufacturing":
        in_S = True
        fr = get_fracs("1A2")
        # NG fraction varies by fuel type row
        if code == "1A2_gn":
            # This IS the NG row -> 100% NG exempt from F, NOT in F
            f_c = f_l = f_h = 0.0
        elif code == "1A2_glp":
            # GLP -> 100% covered by F (not NG)
            f_c = f_l = f_h = 1.0
        elif code == "1A2_die":
            # Diesel -> 100% covered by F
            f_c = f_l = f_h = 1.0
        else:
            # Aggregate: use fractions
            ng_c = fr["ng_exempt_frac_central"]
            f_c, f_l, f_h = 1-ng_c, 1-fr["ng_exempt_frac_high"], 1-fr["ng_exempt_frac_low"]

        e_c = fr["ets_frac_central"]
        e_l = fr["ets_frac_low"]
        e_h = fr["ets_frac_high"]
        note = f"1A2 {code}: S(all); F(fuel-specific); E({e_c*100:.0f}%)"

    # ── TRANSPORT ───────────────────────────────────────────────────
    elif sg == "transport":
        in_S = False  # mobile sources excluded
        f_c = f_l = f_h = 1.0  # all gasoline/diesel covered by federal tax
        e_c = e_l = e_h = 0.0  # not in ETS
        note = "1A3: transport EXEMPT from SLP state tax; F=100%; E=0"

    # ── OTHER ENERGY (residential/commercial/public) ────────────────
    elif sg == "other_energy":
        # SLP tax: commercial/public = in scope (productive processes at fixed sources)
        # Residential = NOT in scope (not productive process)
        # Inventory lumps them together. Estimate commercial = ~40% of category
        # We treat entire 1A4 as partially in S: commercial portion in S, residential not
        # Central estimate: 40% in S (commercial+public), 60% residential excluded
        in_S = True  # simplified: treat as in S for the commercial/institutional portion
        fr = get_fracs("1A4")
        ng_c = fr["ng_exempt_frac_central"]
        ng_l = fr["ng_exempt_frac_low"]
        ng_h = fr["ng_exempt_frac_high"]
        f_c, f_l, f_h = 1-ng_c, 1-ng_h, 1-ng_l
        e_c = e_l = e_h = 0.0
        # NOTE: residential portion is NOT in S. We handle this by applying a
        # partial_S factor in the Venn computation below.
        note = "1A4: mixed; commercial/public IN S (productive); residential NOT in S; F(non-NG)"

    # ── IPPU — all process emissions ────────────────────────────────
    elif sg.startswith("ippu"):
        in_S = True
        # Process emissions NOT covered by federal fuel tax
        f_c = f_l = f_h = 0.0

        # ETS thresholds per IPPU subsector
        if sg == "ippu_cemento":
            # Cerritos cement: 1,076 kt/yr >> threshold; SLP city + Soledad cement also large
            e_c, e_l, e_h = 0.95, 0.85, 1.00
            note = "2_cemento: process CO2; S=yes; F=0 (not combustion); E=95% (Cerritos 1,076 kt/yr)"
        elif sg == "ippu_metalurgia":
            # Single facility 2,071 kt/yr >> threshold
            e_c, e_l, e_h = 0.95, 0.85, 1.00
            note = "2_metalurgia: S=yes; F=0; E=95% (SLP metalurgia 2,071 kt/yr facility)"
        elif sg == "ippu_vidrio":
            # Glass industry in SLP municipality: 151 Mt/yr (RETC)
            e_c, e_l, e_h = 0.90, 0.75, 1.00
            note = "2_vidrio: S=yes; F=0; E=90% (large glass facility 151 kt/yr)"
        elif sg == "ippu_celulosa":
            # Celulosa y papel: 81.6 Mt/yr in SLP municipality + 1.7 Mt in SLP city
            e_c, e_l, e_h = 0.85, 0.70, 0.95
            note = "2_celulosa: S=yes; F=0; E=85% (large pulp/paper 81.6 kt/yr)"
        elif sg == "ippu_automotriz":
            # Multiple automotive plants; some large, some small
            e_c, e_l, e_h = 0.60, 0.40, 0.80
            note = "2_automotriz: S=yes; F=0; E=60% (mixed plant sizes)"
        elif sg == "ippu_quimica":
            # Chemical industry scattered
            e_c, e_l, e_h = 0.50, 0.30, 0.70
            note = "2_quimica: S=yes; F=0; E=50% (scattered facilities)"
        elif sg == "ippu_otras":
            e_c, e_l, e_h = 0.40, 0.20, 0.60
            note = "2_otras: S=yes; F=0; E=40% (diverse small industries)"
        else:
            e_c, e_l, e_h = 0.50, 0.30, 0.70
            note = f"IPPU {sg}: S=yes; F=0; E=50% default"

    # ── AFOLU ───────────────────────────────────────────────────────
    elif sg == "afolu":
        in_S = False
        f_c = f_l = f_h = 0.0
        e_c = e_l = e_h = 0.0
        note = "AFOLU: exempt from all three instruments"

    # ── WASTE ───────────────────────────────────────────────────────
    elif sg == "waste":
        in_S = False
        f_c = f_l = f_h = 0.0
        e_c = e_l = e_h = 0.0
        note = "Waste: exempt from all three instruments"

    return pd.Series({
        "in_S": in_S,
        "f_frac_central": f_c, "f_frac_low": f_l, "f_frac_high": f_h,
        "e_frac_central": e_c, "e_frac_low": e_l, "e_frac_high": e_h,
        "scope_note": note,
    })


scope = inv.apply(map_scope, axis=1)
scope_df = pd.concat([inv, scope], axis=1)

# ── Handle partial S coverage for 1A4 (residential excluded) ────────────
# The inventory lumps residential + commercial + public together.
# SLP tax covers fixed sources in productive processes -> commercial/institutional YES
# Residential combustion -> NO (not productive process)
# Estimate: commercial+public = 40% of 1A4 emissions (central)
# We apply this by splitting the 1A4 row into S-eligible and non-S portions
COMM_FRAC_CENTRAL = 0.40
COMM_FRAC_LOW     = 0.30
COMM_FRAC_HIGH    = 0.50

# ── 3. Compute Venn segments ────────────────────────────────────────────
SEGS = ["S_F_E", "S_E_only", "S_F_only", "S_only",
        "F_only", "F_E_only", "E_only", "uncovered"]

def compute_venn(row, scen="central"):
    em   = row["emissions_GgCO2e"]
    in_S = row["in_S"]
    f    = row[f"f_frac_{scen}"]
    e    = row[f"e_frac_{scen}"]
    sg   = row["sector_group"]

    # Special handling for 1A4: partial S coverage
    if sg == "other_energy":
        comm_f = {"central": COMM_FRAC_CENTRAL, "low": COMM_FRAC_LOW, "high": COMM_FRAC_HIGH}[scen]
        em_S = em * comm_f        # commercial/public portion in S
        em_notS = em * (1 - comm_f)  # residential portion not in S

        # S-eligible portion
        SFE   = em_S * f * e
        SE    = em_S * (1-f) * e
        SF    = em_S * f * (1-e)
        S_only= em_S * (1-f) * (1-e)

        # Non-S portion (residential): can still be in F
        F_only    = em_notS * f * (1-e)
        FE_only   = em_notS * f * e
        E_only    = em_notS * (1-f) * e
        uncovered = em_notS * (1-f) * (1-e)

        return pd.Series(dict(
            S_F_E=SFE, S_E_only=SE, S_F_only=SF, S_only=S_only,
            F_only=F_only, F_E_only=FE_only, E_only=E_only, uncovered=uncovered))

    if in_S:
        SFE   = em * f * e
        SE    = em * (1-f) * e
        SF    = em * f * (1-e)
        S_only= em * (1-f) * (1-e)
        return pd.Series(dict(
            S_F_E=SFE, S_E_only=SE, S_F_only=SF, S_only=S_only,
            F_only=0.0, F_E_only=0.0, E_only=0.0, uncovered=0.0))
    else:
        F_only    = em * f * (1-e)
        FE_only   = em * f * e
        E_only    = em * (1-f) * e
        uncovered = em * (1-f) * (1-e)
        return pd.Series(dict(
            S_F_E=0.0, S_E_only=0.0, S_F_only=0.0, S_only=0.0,
            F_only=F_only, F_E_only=FE_only, E_only=E_only, uncovered=uncovered))


for scen in ["central", "low", "high"]:
    venn = scope_df.apply(lambda r: compute_venn(r, scen), axis=1)
    for col in venn.columns:
        scope_df[f"{col}_{scen}"] = venn[col]

scope_df.to_csv(os.path.join(PROC_DIR, "slp_tax_scope.csv"), index=False)
print(f"\nSaved: data/processed/slp_tax_scope.csv")

# ── 4. Summarise Venn segments ──────────────────────────────────────────
def instrument_totals(segs):
    S = segs["S_F_E"] + segs["S_E_only"] + segs["S_F_only"] + segs["S_only"]
    F = segs["S_F_E"] + segs["S_F_only"] + segs["F_only"]   + segs["F_E_only"]
    E = segs["S_F_E"] + segs["S_E_only"] + segs["F_E_only"] + segs["E_only"]
    union = sum(segs[s] for s in SEGS if s != "uncovered")
    return S, F, E, union


summary = {}
for scen in ["central", "low", "high"]:
    seg_totals = {s: scope_df[f"{s}_{scen}"].sum() for s in SEGS}
    summary[scen] = seg_totals

print(f"\n{'='*70}")
print("SAN LUIS POTOSI — VENN DECOMPOSITION (base year annual avg, AR5)")
print(f"{'='*70}")

for scen in ["central", "low", "high"]:
    segs = summary[scen]
    S, F, E, union = instrument_totals(segs)
    print(f"\n  {scen.upper()} scenario:")
    for s in SEGS:
        v = segs[s]
        pct = v / STATE_TOTAL * 100
        print(f"    {s:<12}: {v:8.1f} GgCO2e  ({pct:5.1f}%)")
    print(f"    {'---':>12}")
    print(f"    S (state tax)  : {S:8.1f}  ({S/STATE_TOTAL*100:.1f}%)")
    print(f"    F (federal)    : {F:8.1f}  ({F/STATE_TOTAL*100:.1f}%)")
    print(f"    E (pilot ETS)  : {E:8.1f}  ({E/STATE_TOTAL*100:.1f}%)")
    print(f"    Union S|F|E    : {union:8.1f}  ({union/STATE_TOTAL*100:.1f}%)")
    print(f"    Uncovered      : {segs['uncovered']:8.1f}  ({segs['uncovered']/STATE_TOTAL*100:.1f}%)")

# ── 5. Build overlap estimates table (base year only) ───────────────────
# NOTE: No extrapolation to 2025/2026 because base year is 2007-2014 annual avg.
# Extrapolation to present day flagged as future step in documentation.

records = []
for scen in ["central", "low", "high"]:
    segs = summary[scen]
    S, F, E, union = instrument_totals(segs)
    r = dict(
        year="2007-2014 avg", scenario=scen,
        state_total_GgCO2e=STATE_TOTAL,
        gwp_basis="AR5",
        S_gross_GgCO2e=S, S_pct=S/STATE_TOTAL*100,
        F_gross_GgCO2e=F, F_pct=F/STATE_TOTAL*100,
        E_gross_GgCO2e=E, E_pct=E/STATE_TOTAL*100,
        S_F_E_GgCO2e=segs["S_F_E"],     S_F_E_pct=segs["S_F_E"]/STATE_TOTAL*100,
        S_E_only_GgCO2e=segs["S_E_only"], S_E_only_pct=segs["S_E_only"]/STATE_TOTAL*100,
        S_F_only_GgCO2e=segs["S_F_only"], S_F_only_pct=segs["S_F_only"]/STATE_TOTAL*100,
        S_only_GgCO2e=segs["S_only"],    S_only_pct=segs["S_only"]/STATE_TOTAL*100,
        F_only_GgCO2e=segs["F_only"],    F_only_pct=segs["F_only"]/STATE_TOTAL*100,
        F_E_only_GgCO2e=segs["F_E_only"], F_E_only_pct=segs["F_E_only"]/STATE_TOTAL*100,
        E_only_GgCO2e=segs["E_only"],    E_only_pct=segs["E_only"]/STATE_TOTAL*100,
        uncovered_GgCO2e=segs["uncovered"], uncovered_pct=segs["uncovered"]/STATE_TOTAL*100,
        union_GgCO2e=union, union_pct=union/STATE_TOTAL*100,
        S_F_overlap=segs["S_F_E"]+segs["S_F_only"],
        S_E_overlap=segs["S_F_E"]+segs["S_E_only"],
        estimation_tier="Tier 3",
        notes="Base year 2007-2014 annual avg; SAR->AR5 converted; no extrapolation; no HFC data"
    )
    records.append(r)

overlap_df = pd.DataFrame(records)
overlap_df.to_csv(os.path.join(PROC_DIR, "slp_overlap_estimates.csv"), index=False)
print(f"\nSaved: data/processed/slp_overlap_estimates.csv")

# ── 6. Print structural findings ────────────────────────────────────────
c = summary["central"]
S_c, F_c, E_c, union_c = instrument_totals(c)

print(f"\n{'='*70}")
print("STRUCTURAL FINDINGS — SAN LUIS POTOSI")
print(f"{'='*70}")
print(f"""
  1. HIGHEST federal tax overlap with electricity of any state analysed.
     Villa de Reyes (combustoleo) drives non-NG share to ~57% for [1A1].
     F covers {c['S_F_E']+c['S_F_only']+c['F_only']:.0f} GgCO2e ({(c['S_F_E']+c['S_F_only']+c['F_only'])/STATE_TOTAL*100:.1f}%)

  2. HIGHEST non-NG industrial fuel share (65%) of all states.
     GLP (53%) + diesel (12%) dominate; NG only 35%.
     S*F manufacturing overlap is substantial.

  3. LARGE cement/cal sector: {scope_df[scope_df['sector_group']=='ippu_cemento']['emissions_GgCO2e'].sum():.0f} GgCO2e/yr (process CO2).
     In S and E but NOT F (process, not combustion).

  4. SAR->AR5 conversion effect: state total changes from
     {inv['CO2eq_SAR_annual_kt'].sum():.0f} (SAR) to {STATE_TOTAL:.0f} (AR5) GgCO2e/yr
     ({(STATE_TOTAL/(inv['CO2eq_SAR_annual_kt'].sum())-1)*100:+.1f}%)
     CH4-heavy sectors (AFOLU, waste) increase; N2O-heavy (metalurgia) decrease.

  5. DATA GAP: No HFC/PFC data in inventory. SLP carbon tax covers these gases
     but coverage is understated. Inventory only reports CO2, CH4, N2O.

  6. IPPU combustion/process mix: RETC data does not distinguish combustion
     from process emissions. Cement/cal assumed predominantly process CO2.
     Metalurgia and glass may be a mix. Conservative: all IPPU treated as process.

  7. No extrapolation: base year 2007-2014 is old (most recent = 2014).
     Extrapolation to 2025/2026 deferred as future step.
""")

print("  02_estimate.py complete\n")
