"""
02_estimate.py — Tamaulipas Carbon Pricing Overlap Analysis
=============================================================
Case: Mexico — Tamaulipas state carbon tax (S) × Federal IEPS (F) × Mexico Pilot ETS (E)
Estimation tier: Tier 3 (dual 25,000 tCO2e/yr threshold for S and E)
Base year: 2013 (AR5-adjusted)  |  Target year: 2025 (BaU projection)

UNIQUE FEATURE: Tamaulipas state carbon tax has a 25,000 tCO2e/yr facility
threshold — same as the federal ETS. This is unlike all other states analysed
(Colima, Durango, Morelos, Guanajuato, CDMX, Querétaro, San Luis Potosí)
where the state tax covers all facilities regardless of size.

Instruments:
─────────────────────────────────────────────────────────────────────────────
S  Tamaulipas state carbon tax (2020-2022, 2024-present; suspended 2023)
   Scope:    Direct emissions from FIXED sources in productive processes
             ≥ 25,000 tCO2e/yr
   Gases:    CO2, CH4, N2O, HFCs, PFCs, SF6 (Kyoto basket)
   Covered:  1A1a electricity, 1A1b refining, 1A2 manufacturing,
             IPPU process (caliza, negro de humo), 1B2 fugitive O&G
             — all ONLY above-threshold facilities
   Exempt:   Transport (mobile), residential, agriculture, AFOLU, waste,
             facilities < 25,000 tCO2e/yr
   NG:       IN SCOPE (no NG exemption, unlike federal tax)

F  Mexico federal IEPS carbon tax (Art. 2o-C)
   Scope:    Upstream fuel tax; all fossil fuels EXCEPT natural gas
   Exempt:   Natural gas; process emissions; fugitive emissions

E  Mexico Pilot ETS (2020–)
   Scope:    Direct emissions from facilities ≥ 25,000 tCO2e/yr
   Sectors:  Electricity, manufacturing, O&G, other large industry

KEY INSIGHT: S and E have the SAME 25,000 tCO2e/yr threshold.
   → For sectors covered by both, above-threshold coverage is identical
   → Overlap structure depends on SECTOR scope differences, not threshold
   → S∩E overlap is determined by which sectors are in both S and E scope
   → Below-threshold emissions are EXEMPT from both S and E

Outputs:
   data/processed/tamaulipas_scope_2025.csv
   data/processed/tamaulipas_overlap_estimates.csv
"""

import pandas as pd
import numpy as np
import os

# ── Paths ────────────────────────────────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR   = os.path.dirname(SCRIPT_DIR)
PROC_DIR   = os.path.join(BASE_DIR, "data", "processed")

print("=" * 72)
print("Tamaulipas 02_estimate.py — scope mapping and overlap estimation")
print("=" * 72)

# ── 1. Load processed data ───────────────────────────────────────────────────
inv   = pd.read_csv(os.path.join(PROC_DIR, "tamaulipas_inventory_2013_ar5.csv"))
fracs = pd.read_csv(os.path.join(PROC_DIR, "tamaulipas_fuel_fractions_2013.csv"))

STATE_TOTAL_2013_AR5 = inv["total_ar5"].sum()
STATE_TOTAL_2025_AR5 = inv["total_ar5_2025"].sum()

print(f"\n  State total 2013 (AR5): {STATE_TOTAL_2013_AR5:,.2f} GgCO2e")
print(f"  State total 2025 (AR5): {STATE_TOTAL_2025_AR5:,.2f} GgCO2e")

# ── 2. ETS/S threshold coverage fractions ────────────────────────────────────
# Both S and E use the same 25,000 tCO2e/yr threshold.
# We estimate what fraction of each sector's emissions comes from
# above-threshold facilities.

# For Tamaulipas, the threshold coverage fraction applies to BOTH S and E
# within their respective sector scopes.

THRESHOLD_FRAC = {
    # sector_group: (central, low, high)
    # Electricity: 8 plants, all >> 25k threshold (smallest ~495 MW CC)
    "electricity_generation": (1.00, 1.00, 1.00),
    # Refinery: PEMEX Cd. Madero is single large facility >> threshold
    "petroleum_refining":     (1.00, 1.00, 1.00),
    # Manufacturing: ~36 companies covered per official sources
    # Mixed: some large petrochemical/autogeneration, many SMEs below threshold
    # Tamaulipas has significant petrochemical (Reynosa complex), food, auto parts
    "manufacturing":          (0.65, 0.50, 0.80),
    # Other energy: distributed small commercial/residential → 0%
    "other_energy":           (0.00, 0.00, 0.00),
    # Fugitive O&G: PEMEX installations (processing plants, compression stations)
    # Major infrastructure: 4 cryogenic plants, pipeline system, Burgos gas field
    # Most fugitive emissions from large PEMEX facilities >> threshold
    "fugitive_oil_gas":       (0.80, 0.60, 0.95),
    # IPPU caliza: small operation, likely below threshold
    "ippu_caliza":            (0.50, 0.20, 0.80),
    # IPPU negro de humo: carbon black plant, likely 1-2 facilities >> threshold
    "ippu_negro_humo":        (0.90, 0.70, 1.00),
    # HFC: NE — no data
    "ippu_hfc":               (0.00, 0.00, 0.00),
    # Transport, AFOLU, waste: not applicable
    "transport":              (0.00, 0.00, 0.00),
    "afolu_livestock":        (0.00, 0.00, 0.00),
    "afolu_land_use":         (0.00, 0.00, 0.00),
    "afolu_agriculture":      (0.00, 0.00, 0.00),
    "waste":                  (0.00, 0.00, 0.00),
}

# ── 3. Define scope mapping ──────────────────────────────────────────────────
# S scope: sectors with above-threshold fixed sources
# F scope: non-NG fossil combustion fraction
# E scope: same threshold as S, but limited to ETS-eligible sectors

# S-eligible sectors (subject to threshold):
S_SECTORS = {
    "electricity_generation", "petroleum_refining", "manufacturing",
    "fugitive_oil_gas", "ippu_caliza", "ippu_negro_humo", "ippu_hfc",
    # other_energy: commercial (1A4a) could be in scope IF above threshold
    # but in practice no commercial/residential facility exceeds 25k → excluded
}

# E-eligible sectors (ETS scope):
E_SECTORS = {
    "electricity_generation", "petroleum_refining", "manufacturing",
    "fugitive_oil_gas", "ippu_caliza", "ippu_negro_humo",
    # HFC not in ETS scope
}

# NG exempt fractions for F scope
def get_ng_frac(sector_group, scenario="central"):
    row = fracs[fracs["sector_group"] == sector_group]
    if len(row) == 0:
        # Categories not in fracs table → use defaults
        if sector_group in ("ippu_caliza", "ippu_negro_humo", "ippu_hfc"):
            return 0.0  # process emissions, not combustion
        if sector_group == "fugitive_oil_gas":
            return 1.0  # fugitive CH4, not covered by fuel tax
        if sector_group.startswith("afolu") or sector_group == "waste":
            return 0.0  # not applicable
        if sector_group == "transport":
            return 0.0  # transport fuels: gasoline, diesel (no NG)
        return 0.0
    r = row.iloc[0]
    suf = {"central": "central", "low": "low", "high": "high"}[scenario]
    return r[f"ng_exempt_frac_{suf}"]


def compute_scope(row, scenario="central"):
    """Compute Venn segments for a single inventory row."""
    sg   = row["sector_group"]
    em   = row["total_ar5_2025"]

    # Threshold fraction (same for S and E where applicable)
    tf_c, tf_l, tf_h = THRESHOLD_FRAC.get(sg, (0, 0, 0))
    tf = {"central": tf_c, "low": tf_l, "high": tf_h}[scenario]

    # Determine instrument scope
    in_S_scope = sg in S_SECTORS
    in_E_scope = sg in E_SECTORS

    # S coverage = threshold fraction × emissions (only for S sectors)
    s_frac = tf if in_S_scope else 0.0
    # E coverage = threshold fraction × emissions (only for E sectors)
    e_frac = tf if in_E_scope else 0.0

    # F coverage = non-NG combustion fraction
    ng_frac = get_ng_frac(sg, scenario)

    # For process emissions (IPPU) and fugitives: F = 0 (not combustion-based)
    if sg in ("ippu_caliza", "ippu_negro_humo", "ippu_hfc", "fugitive_oil_gas"):
        f_frac = 0.0
    elif sg == "transport":
        f_frac = 1.0  # all transport fuels taxable (no NG in transport)
    elif sg.startswith("afolu") or sg == "waste":
        f_frac = 0.0  # not covered by F
    else:
        f_frac = 1.0 - ng_frac  # non-NG fraction is taxable

    # ── Venn decomposition ──────────────────────────────────────────────
    # Key: because S has a threshold, below-threshold emissions are NOT in S.
    # S applies to: above-threshold emissions in S-eligible sectors
    # E applies to: above-threshold emissions in E-eligible sectors
    # F applies to: non-NG combustion emissions (all facility sizes)

    # Above-threshold emissions (covered by S and/or E)
    above_threshold = em * tf if (in_S_scope or in_E_scope) else 0.0
    below_threshold = em - above_threshold

    if in_S_scope and in_E_scope:
        # Both S and E apply to above-threshold emissions
        # F applies to non-NG fraction of above-threshold
        S_F_E   = above_threshold * f_frac          # all three
        S_E     = above_threshold * (1 - f_frac)    # S+E but not F (NG/process/fugitive)
        S_F     = 0.0  # S and E have same threshold → if in both, no S∩F-only above threshold
        S_only  = 0.0  # same reasoning
        # Below-threshold: only F applies (if combustion)
        F_only  = below_threshold * f_frac
        FE_only = 0.0   # E has same threshold as S → nothing in E but not S
        E_only  = 0.0
        uncov   = below_threshold * (1 - f_frac)
    elif in_S_scope and not in_E_scope:
        # S applies above threshold, E does not apply
        # This occurs for HFC (but HFC is NE → 0 emissions)
        S_F_E   = 0.0
        S_E     = 0.0
        S_F     = above_threshold * f_frac
        S_only  = above_threshold * (1 - f_frac)
        F_only  = below_threshold * f_frac
        FE_only = 0.0
        E_only  = 0.0
        uncov   = below_threshold * (1 - f_frac)
    elif not in_S_scope and in_E_scope:
        # E applies above threshold, S does not
        # Shouldn't happen with current sector definitions
        S_F_E   = 0.0
        S_E     = 0.0
        S_F     = 0.0
        S_only  = 0.0
        F_only  = (em - above_threshold) * f_frac + above_threshold * f_frac
        FE_only = above_threshold * (1 - f_frac)  # E only above threshold
        E_only  = 0.0
        uncov   = (em - above_threshold) * (1 - f_frac)
    else:
        # Neither S nor E applies
        # Only F may apply (transport) or nothing (AFOLU, waste)
        S_F_E   = 0.0
        S_E     = 0.0
        S_F     = 0.0
        S_only  = 0.0
        F_only  = em * f_frac
        FE_only = 0.0
        E_only  = 0.0
        uncov   = em * (1 - f_frac)

    return pd.Series({
        "in_S":   in_S_scope,
        "in_E":   in_E_scope,
        "s_frac": s_frac,
        "e_frac": e_frac,
        "f_frac": f_frac,
        "threshold_frac": tf,
        "S_F_E":     S_F_E,
        "S_E_only":  S_E,
        "S_F_only":  S_F,
        "S_only":    S_only,
        "F_only":    F_only,
        "F_E_only":  FE_only,
        "E_only":    E_only,
        "uncovered": uncov,
    })


# ── 4. Apply scope mapping for all scenarios ─────────────────────────────────
SEGS = ["S_F_E", "S_E_only", "S_F_only", "S_only",
        "F_only", "F_E_only", "E_only", "uncovered"]

all_results = []
for scen in ["central", "low", "high"]:
    scope = inv.apply(lambda r: compute_scope(r, scen), axis=1)
    scope_df = pd.concat([inv, scope], axis=1)
    scope_df["scenario"] = scen

    # For low/high: also vary the growth projection (±15% of BaU growth)
    if scen == "low":
        # Lower growth → scale 2025 emissions down
        scale = 0.92  # ~8% below BaU
        for seg in SEGS:
            scope_df[seg] = scope_df[seg] * scale
        scope_df["total_ar5_2025"] = scope_df["total_ar5_2025"] * scale
    elif scen == "high":
        scale = 1.08  # ~8% above BaU
        for seg in SEGS:
            scope_df[seg] = scope_df[seg] * scale
        scope_df["total_ar5_2025"] = scope_df["total_ar5_2025"] * scale

    all_results.append(scope_df)

results = pd.concat(all_results, ignore_index=True)
results.to_csv(os.path.join(PROC_DIR, "tamaulipas_scope_2025.csv"), index=False)
print(f"\nSaved: data/processed/tamaulipas_scope_2025.csv")

# ── 5. Aggregate Venn segments ───────────────────────────────────────────────
def instrument_totals(segs):
    S = segs["S_F_E"] + segs["S_E_only"] + segs["S_F_only"] + segs["S_only"]
    F = segs["S_F_E"] + segs["S_F_only"] + segs["F_only"]   + segs["F_E_only"]
    E = segs["S_F_E"] + segs["S_E_only"] + segs["F_E_only"] + segs["E_only"]
    union = sum(segs[s] for s in SEGS if s != "uncovered")
    return S, F, E, union

records = []
for scen in ["central", "low", "high"]:
    mask = results["scenario"] == scen
    sub  = results[mask]
    total = sub["total_ar5_2025"].sum()

    seg_totals = {s: sub[s].sum() for s in SEGS}
    S, F, E, union = instrument_totals(seg_totals)

    r = dict(
        year=2025, scenario=scen,
        state_total_GgCO2e=total,
        S_gross_GgCO2e=S, S_pct=S/total*100,
        F_gross_GgCO2e=F, F_pct=F/total*100,
        E_gross_GgCO2e=E, E_pct=E/total*100,
        S_F_E_GgCO2e=seg_totals["S_F_E"],     S_F_E_pct=seg_totals["S_F_E"]/total*100,
        S_E_only_GgCO2e=seg_totals["S_E_only"], S_E_only_pct=seg_totals["S_E_only"]/total*100,
        S_F_only_GgCO2e=seg_totals["S_F_only"], S_F_only_pct=seg_totals["S_F_only"]/total*100,
        S_only_GgCO2e=seg_totals["S_only"],    S_only_pct=seg_totals["S_only"]/total*100,
        F_only_GgCO2e=seg_totals["F_only"],    F_only_pct=seg_totals["F_only"]/total*100,
        F_E_only_GgCO2e=seg_totals["F_E_only"], F_E_only_pct=seg_totals["F_E_only"]/total*100,
        E_only_GgCO2e=seg_totals["E_only"],    E_only_pct=seg_totals["E_only"]/total*100,
        uncovered_GgCO2e=seg_totals["uncovered"], uncovered_pct=seg_totals["uncovered"]/total*100,
        union_GgCO2e=union, union_pct=union/total*100,
        S_F_overlap=seg_totals["S_F_E"] + seg_totals["S_F_only"],
        S_E_overlap=seg_totals["S_F_E"] + seg_totals["S_E_only"],
        estimation_tier="Tier 3",
        notes="Dual 25k threshold for S and E; SAR→AR5 converted; BaU 2025 projection",
    )
    records.append(r)

overlap_df = pd.DataFrame(records)
overlap_df.to_csv(os.path.join(PROC_DIR, "tamaulipas_overlap_estimates.csv"), index=False)
print(f"Saved: data/processed/tamaulipas_overlap_estimates.csv")

# ── 6. Print summary ─────────────────────────────────────────────────────────
print(f"\n{'='*72}")
print(f"TAMAULIPAS COVERAGE ESTIMATES — 2025 (AR5 GWPs)")
print(f"{'='*72}")

for scen in ["central", "low", "high"]:
    row = overlap_df[overlap_df["scenario"] == scen].iloc[0]
    print(f"\n  {scen.upper()} scenario:")
    print(f"    State total:   {row['state_total_GgCO2e']:9,.0f} GgCO2e")
    print(f"    S (state tax): {row['S_gross_GgCO2e']:9,.0f}  ({row['S_pct']:5.1f}%)  ← ≥25k threshold")
    print(f"    F (federal):   {row['F_gross_GgCO2e']:9,.0f}  ({row['F_pct']:5.1f}%)")
    print(f"    E (pilot ETS): {row['E_gross_GgCO2e']:9,.0f}  ({row['E_pct']:5.1f}%)  ← ≥25k threshold")
    print(f"    S∩F∩E:         {row['S_F_E_GgCO2e']:9,.0f}  ({row['S_F_E_pct']:5.1f}%)")
    print(f"    S∩E only:      {row['S_E_only_GgCO2e']:9,.0f}  ({row['S_E_only_pct']:5.1f}%)  ← NG at large plants")
    print(f"    S∩F only:      {row['S_F_only_GgCO2e']:9,.0f}  ({row['S_F_only_pct']:5.1f}%)")
    print(f"    S only:        {row['S_only_GgCO2e']:9,.0f}  ({row['S_only_pct']:5.1f}%)")
    print(f"    F only:        {row['F_only_GgCO2e']:9,.0f}  ({row['F_only_pct']:5.1f}%)  ← transport + below-threshold")
    print(f"    Union S∪F∪E:   {row['union_GgCO2e']:9,.0f}  ({row['union_pct']:5.1f}%)")
    print(f"    Uncovered:     {row['uncovered_GgCO2e']:9,.0f}  ({row['uncovered_pct']:5.1f}%)")

c = overlap_df[overlap_df["scenario"] == "central"].iloc[0]
print(f"\n  STRUCTURAL FINDINGS:")
print(f"  • S coverage MUCH NARROWER than other states ({c['S_pct']:.1f}% vs 34-55% typical)")
print(f"    because of 25,000 tCO2e/yr threshold — only ~36 companies covered")
print(f"  • S∩E overlap is dominant: same threshold means near-identical coverage")
print(f"    S∩E = {c['S_E_only_GgCO2e']:.0f} GgCO2e ({c['S_E_only_pct']:.1f}%) — NG at large plants")
print(f"  • F only = {c['F_only_GgCO2e']:.0f} GgCO2e ({c['F_only_pct']:.1f}%) — transport + below-threshold non-NG")
print(f"  • Fugitive emissions ({inv[inv['ipcc_code']=='1B2']['total_ar5_2025'].iloc[0]:.0f} GgCO2e)")
print(f"    mostly in S∩E (PEMEX facilities >> threshold, CH4 not in F)")
print(f"  • NG dominance (93-94% of electricity + manufacturing) → minimal S∩F∩E overlap")

print(f"\n✓ 02_estimate.py complete\n")
