"""
02_estimate.py — CDMX Carbon Pricing Overlap Analysis
======================================================
Case: Mexico — CDMX state carbon tax × Federal IEPS × Mexico Pilot ETS
Estimation tier: Tier 3
Base year: 2020

Three-instrument Venn decomposition:
  S = CDMX state carbon tax (CO2/CH4/N2O from stationary commercial/service/industrial)
  F = Federal IEPS carbon tax (fossil fuel combustion CO2, NG-exempt, all sectors)
  E = Mexico Pilot ETS (direct CO2, facilities >= 25,000 tCO2e/yr)

Eight segments via inclusion-exclusion:
  S∩F∩E, S∩F, S∩E, S_only, F∩E, F_only, E_only, uncovered

Key CDMX-specific features:
  - Natural gas provides ~99.4% of industrial and ~99.8% of commercial fossil energy
    → F coverage in S-covered sectors is extremely small (~0.6% of industrial combustion)
  - CDMX is service-dominated: transport = 67%, area combustion = 28%, point sources = 4.5%
  - No heavy industry (no refineries, no large cement, no petrochemicals)
  - ETS threshold covers only a fraction of the many small manufacturing plants
  - COVID-2020 depressed all emissions (GDP fell 5-43% by sector)

Run: python 02_estimate.py
Input: data/processed/cdmx_inventory_clean.csv
       data/processed/cdmx_fuel_fractions.csv
Output: data/processed/cdmx_overlap_results.csv
"""

import pandas as pd
import numpy as np
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROC_DIR   = os.path.join(SCRIPT_DIR, "data", "processed")

print("=" * 70)
print("CDMX 02_estimate.py — Three-instrument overlap estimation")
print("=" * 70)

# ── Load processed data ──────────────────────────────────────────────────────
inv  = pd.read_csv(os.path.join(PROC_DIR, "cdmx_inventory_clean.csv"))
fuel = pd.read_csv(os.path.join(PROC_DIR, "cdmx_fuel_fractions.csv"), index_col=0)

# ── Instrument scope definitions ─────────────────────────────────────────────

# S scope: CO2/CH4/N2O from stationary sources in commercial/service/industrial
S_CATS = {
    'INDUSTRY_REG',          # regulated manufacturing point sources
    'ELECTRICITY',           # electricity generation (stationary industrial)
    'COMMERCIAL_REG',        # regulated commercial/service point sources
    'FUEL_STORAGE',          # fuel storage (tiny, stationary industrial)
    'INDUSTRY_UNREG',        # non-regulated industrial combustion (area)
    'COMMERCIAL_UNREG',      # non-regulated commercial combustion (area)
}
# EXCLUDED from S: RESIDENTIAL, ROAD_TRANSPORT, AVIATION, RAIL, WASTE,
#   AGRICULTURE, LIVESTOCK, RESIDENTIAL_OTHER, HFC_RESIDENTIAL,
#   CONSTRUCTION_EQUIP, BUS_TERMINALS, AGRICULTURE_EQUIP,
#   COMMERCIAL_INFORMAL (asados — ambiguous but small, excluded conservatively),
#   FUGITIVE_LP, CONSTRUCTION, MISC_AREA, NON_ROAD_OTHER, LADRILLERAS

# F scope: fossil fuel combustion CO2, all sectors, NG-exempt
# Covers categories with fossil fuel combustion, but only the non-NG fraction
F_COMBUSTION_CATS = {
    'INDUSTRY_REG',
    'ELECTRICITY',
    'COMMERCIAL_REG',
    'FUEL_STORAGE',
    'INDUSTRY_UNREG',
    'COMMERCIAL_UNREG',
    'RESIDENTIAL',
    'ROAD_TRANSPORT',
    'AGRICULTURE_EQUIP',
    'AVIATION',             # turbosina/jet fuel → covered by F
    'RAIL',                 # diesel → covered by F
    'CONSTRUCTION_EQUIP',   # diesel/gas LP → covered by F
    'BUS_TERMINALS',        # diesel → covered by F
    'COMMERCIAL_INFORMAL',  # charcoal (biogenic) → NOT covered; exclude
}
# F does NOT cover: WASTE (non-combustion CH4/N2O), AGRICULTURE (N2O),
#   LIVESTOCK (CH4/N2O), HFC_RESIDENTIAL (HFC), FUGITIVE_LP (fugitive CH4),
#   RESIDENTIAL_OTHER (domestic non-fuel emissions), COMMERCIAL_INFORMAL (charcoal = biogenic)

# E scope: direct CO2, facilities >= 25,000 tCO2e/yr, energy + industrial sectors
# Only applies to point sources (regulated) — area sources are by definition
# below-threshold small emitters
E_ELIGIBLE_CATS = {
    'INDUSTRY_REG',
    'ELECTRICITY',
    'COMMERCIAL_REG',  # small probability — very few commercial facilities this large
}

# ── ETS coverage fractions (Tier 3 estimates) ────────────────────────────────
# (central, low, high)
# Documented in docs/assumptions_02.md
ETS_FRAC = {
    'ELECTRICITY':     (0.70, 0.50, 0.85),
    # 20 power plants in ZMVM (all federal), CDMX subset. Largest gas-fired
    # plants (Jorge Luque, Valle de México) well above 25k threshold; many
    # smaller distributed generation below. 70% central.

    'INDUSTRY_REG':    (0.30, 0.15, 0.50),
    # ~502 industrial facilities, avg ~690 tCO2e each. CDMX has no heavy
    # industry (no refineries, cement, steel). A few large chemical and paper
    # plants may cross 25k. Lower than Guanajuato/Durango manufacturing share.

    'COMMERCIAL_REG':  (0.02, 0.00, 0.05),
    # ~1,838 commercial facilities, avg ~105 tCO2e each. Only the very largest
    # (hospitals, shopping centres with large gas boilers) could reach 25k.
}

# ── NG exemption fractions (non-NG share of fossil combustion CO2) ───────────
# From fuel_fractions computed in 01_clean.py
# These represent the fraction of combustion CO2 covered by F (non-NG fuels)
NG_FRAC = {
    # Industrial sector: NG provides 99.4% of fossil energy
    # CO2-weighted non-NG share slightly different due to emission factors
    # Central: 0.8%, Low: 0.4% (more NG-dominant), High: 1.5% (some diesel/coke)
    'industrial':   {'central': 0.008, 'low': 0.004, 'high': 0.015},

    # Commercial sector: NG provides 99.8% of fossil energy
    # Central: 0.3%, Low: 0.1%, High: 0.5%
    'commercial':   {'central': 0.003, 'low': 0.001, 'high': 0.005},

    # Residential: NG ~99.8% of fossil energy; LP is the non-NG fuel
    'residential':  {'central': 0.003, 'low': 0.001, 'high': 0.005},

    # Electricity generation: mostly NG-fired in CDMX (no coal, minimal diesel)
    # Central: 1.5% (diesel backup generators), Low: 0.5%, High: 3.0%
    'electricity':  {'central': 0.015, 'low': 0.005, 'high': 0.030},

    # Transport: 100% non-NG (gasoline, diesel, LP)
    'transport':    {'central': 1.000, 'low': 1.000, 'high': 1.000},

    # Aviation: 100% turbosina (jet fuel)
    'aviation':     {'central': 1.000, 'low': 1.000, 'high': 1.000},

    # Rail/construction equipment: diesel-dominated
    'diesel_mobile': {'central': 1.000, 'low': 1.000, 'high': 1.000},

    # Agriculture equipment: mostly diesel/LP
    'agri_equip':   {'central': 1.000, 'low': 1.000, 'high': 1.000},
}


# ═══════════════════════════════════════════════════════════════════════════════
# STEP 1: Aggregate emissions by analytical category
# ═══════════════════════════════════════════════════════════════════════════════
print("\n── Step 1: Aggregating emissions by category ──")

agg = (inv.groupby('analysis_cat')
       .agg(co2eq=('co2eq_t', 'sum'),
            co2=('co2_t', 'sum'),
            ch4=('ch4_t', 'sum'),
            n2o=('n2o_t', 'sum'),
            hfc=('hfc_t', 'sum'))
       .reset_index())

total_ghg = agg['co2eq'].sum()
print(f"  Total CDMX GHG: {total_ghg:,.0f} tCO2eq")


# ═══════════════════════════════════════════════════════════════════════════════
# STEP 2: Compute S coverage
# ═══════════════════════════════════════════════════════════════════════════════
print("\n── Step 2: Computing S (CDMX carbon tax) coverage ──")

# S covers CO2, CH4, N2O — NOT HFC
# For categories in S_CATS, subtract HFC contribution
GWP_CH4 = 28
GWP_N2O = 265

results = []

for _, row in agg.iterrows():
    cat = row['analysis_cat']
    co2eq = row['co2eq']

    in_S = cat in S_CATS
    # S covers CO2+CH4+N2O only → subtract HFC
    s_co2eq = co2eq - row['hfc'] * GWP_CH4 if in_S else 0  # approximate HFC deduction
    # More precise: use inventory co2eq minus (hfc × average GWP)
    # Since HFC in point sources is tiny (~43 tCO2eq), approximate is fine
    if in_S:
        # Recompute from individual gases
        s_co2eq = row['co2'] + row['ch4'] * GWP_CH4 + row['n2o'] * GWP_N2O

    results.append({
        'category': cat,
        'total_co2eq': co2eq,
        'co2': row['co2'],
        'ch4': row['ch4'],
        'n2o': row['n2o'],
        'hfc': row['hfc'],
        'in_S': in_S,
        'S_co2eq': s_co2eq,
    })

df = pd.DataFrame(results)
total_S = df['S_co2eq'].sum()
print(f"  S coverage: {total_S:,.0f} tCO2eq ({total_S/total_ghg:.1%} of CDMX total)")


# ═══════════════════════════════════════════════════════════════════════════════
# STEP 3: Compute Venn segments for S-covered sources
# ═══════════════════════════════════════════════════════════════════════════════
print("\n── Step 3: Computing Venn segments (S × F × E) ──")

def compute_segments(scenario='central'):
    """Compute eight-segment Venn decomposition for given scenario."""
    segments = {
        'S_F_E': 0, 'S_F': 0, 'S_E': 0, 'S_only': 0,
        'F_E': 0, 'F_only': 0, 'E_only': 0, 'uncovered': 0,
    }

    for _, row in df.iterrows():
        cat = row['category']
        co2eq = row['total_co2eq']
        s_co2eq = row['S_co2eq']
        in_S = row['in_S']

        # ── Determine F coverage for this category ──
        # F = non-NG fraction × combustion CO2
        # F only covers fossil fuel combustion CO2, not CH4/N2O/HFC/process
        f_frac = 0
        if cat in ('INDUSTRY_REG', 'INDUSTRY_UNREG'):
            f_frac = NG_FRAC['industrial'][scenario]
        elif cat in ('COMMERCIAL_REG', 'COMMERCIAL_UNREG'):
            f_frac = NG_FRAC['commercial'][scenario]
        elif cat == 'ELECTRICITY':
            f_frac = NG_FRAC['electricity'][scenario]
        elif cat == 'RESIDENTIAL':
            f_frac = NG_FRAC['residential'][scenario]
        elif cat == 'ROAD_TRANSPORT':
            f_frac = NG_FRAC['transport'][scenario]
        elif cat == 'AVIATION':
            f_frac = NG_FRAC['aviation'][scenario]
        elif cat in ('RAIL', 'CONSTRUCTION_EQUIP', 'BUS_TERMINALS', 'NON_ROAD_OTHER'):
            f_frac = NG_FRAC['diesel_mobile'][scenario]
        elif cat == 'AGRICULTURE_EQUIP':
            f_frac = NG_FRAC['agri_equip'][scenario]
        # All other categories: F = 0 (waste CH4, agriculture N2O, HFC, fugitive, etc.)

        # F covers combustion CO2 only — approximate as co2 × f_frac
        # (CH4/N2O from combustion are not covered by IEPS)
        f_co2 = row['co2'] * f_frac

        # ── Determine E coverage ──
        e_frac = 0
        if cat in E_ELIGIBLE_CATS:
            ets_vals = ETS_FRAC.get(cat, (0, 0, 0))
            idx = {'central': 0, 'low': 1, 'high': 2}[scenario]
            e_frac = ets_vals[idx]
        # E covers direct CO2 from above-threshold facilities
        e_co2 = row['co2'] * e_frac

        # ── Assign to Venn segments ──
        if in_S:
            # Within S-covered emissions, decompose into S∩F∩E, S∩F, S∩E, S_only
            # Total S emissions for this category
            total_s = s_co2eq

            # S∩F = non-NG combustion CO2 within S scope
            sf_co2 = row['co2'] * f_frac  # F portion within S

            # S∩E = above-threshold CO2 within S scope
            se_co2 = row['co2'] * e_frac  # E portion within S

            # S∩F∩E = overlap of F and E within S
            # This is the non-NG fraction of above-threshold facility CO2
            sfe_co2 = row['co2'] * f_frac * e_frac

            # Assign using inclusion-exclusion
            segments['S_F_E']  += sfe_co2
            segments['S_F']    += sf_co2 - sfe_co2       # S∩F only (not E)
            segments['S_E']    += se_co2 - sfe_co2       # S∩E only (not F)
            # S_only = total S minus portions in F and E
            segments['S_only'] += total_s - sf_co2 - se_co2 + sfe_co2

        else:
            # Not in S scope — could be F_only, F∩E, E_only, or uncovered
            # E is only for point sources → if not in S and not in E_ELIGIBLE, no E
            if cat in E_ELIGIBLE_CATS:
                # Shouldn't happen: all E-eligible are also in S
                # But just in case
                fe_co2 = row['co2'] * f_frac * e_frac
                segments['F_E']    += fe_co2
                segments['F_only'] += f_co2 - fe_co2
                segments['E_only'] += e_co2 - fe_co2
                segments['uncovered'] += co2eq - f_co2 - e_co2 + fe_co2
            elif f_co2 > 0:
                segments['F_only'] += f_co2
                segments['uncovered'] += co2eq - f_co2
            else:
                segments['uncovered'] += co2eq

    return segments


# Compute for all three scenarios
results_all = {}
for scen in ['central', 'low', 'high']:
    segs = compute_segments(scen)
    results_all[scen] = segs

# Print central results
print(f"\n  {'Segment':12s}  {'Central':>14s}  {'Low':>14s}  {'High':>14s}")
print(f"  {'-'*12}  {'-'*14}  {'-'*14}  {'-'*14}")
for seg in ['S_F_E', 'S_F', 'S_E', 'S_only', 'F_E', 'F_only', 'E_only', 'uncovered']:
    c = results_all['central'][seg]
    l = results_all['low'][seg]
    h = results_all['high'][seg]
    print(f"  {seg:12s}  {c:>14,.0f}  {l:>14,.0f}  {h:>14,.0f}")

# Derived metrics
print("\n  Derived metrics (central):")
c = results_all['central']
total_S_calc = c['S_F_E'] + c['S_F'] + c['S_E'] + c['S_only']
total_F_calc = c['S_F_E'] + c['S_F'] + c['F_E'] + c['F_only']
total_E_calc = c['S_F_E'] + c['S_E'] + c['F_E'] + c['E_only']
union = sum(v for k, v in c.items() if k != 'uncovered')
print(f"  Gross S:  {total_S_calc:>14,.0f} ({total_S_calc/total_ghg:.1%})")
print(f"  Gross F:  {total_F_calc:>14,.0f} ({total_F_calc/total_ghg:.1%})")
print(f"  Gross E:  {total_E_calc:>14,.0f} ({total_E_calc/total_ghg:.1%})")
print(f"  Union:    {union:>14,.0f} ({union/total_ghg:.1%})")
print(f"  Uncov:    {c['uncovered']:>14,.0f} ({c['uncovered']/total_ghg:.1%})")
print(f"  Total:    {total_ghg:>14,.0f}")


# ═══════════════════════════════════════════════════════════════════════════════
# STEP 4: Build output table
# ═══════════════════════════════════════════════════════════════════════════════
print("\n── Step 4: Building output table ──")

rows = []
seg_labels = {
    'S_F_E':     'S ∩ F ∩ E (all three)',
    'S_F':       'S ∩ F only (not E)',
    'S_E':       'S ∩ E only (not F)',
    'S_only':    'S only',
    'F_E':       'F ∩ E only (not S)',
    'F_only':    'F only',
    'E_only':    'E only',
    'uncovered': 'Uncovered',
}

for seg_key, seg_label in seg_labels.items():
    rows.append({
        'segment': seg_key,
        'label': seg_label,
        'central_tco2eq': results_all['central'][seg_key],
        'low_tco2eq':     results_all['low'][seg_key],
        'high_tco2eq':    results_all['high'][seg_key],
        'central_pct':    results_all['central'][seg_key] / total_ghg * 100,
        'low_pct':        results_all['low'][seg_key] / total_ghg * 100,
        'high_pct':       results_all['high'][seg_key] / total_ghg * 100,
    })

# Add derived rows
for scen in ['central', 'low', 'high']:
    c = results_all[scen]
    results_all[scen]['gross_S'] = c['S_F_E'] + c['S_F'] + c['S_E'] + c['S_only']
    results_all[scen]['gross_F'] = c['S_F_E'] + c['S_F'] + c['F_E'] + c['F_only']
    results_all[scen]['gross_E'] = c['S_F_E'] + c['S_E'] + c['F_E'] + c['E_only']
    results_all[scen]['union']   = sum(v for k, v in c.items()
                                       if k not in ('uncovered', 'gross_S', 'gross_F',
                                                     'gross_E', 'union'))

derived = [
    ('gross_S',  'Gross S (CDMX tax)'),
    ('gross_F',  'Gross F (IEPS)'),
    ('gross_E',  'Gross E (Pilot ETS)'),
    ('union',    'Deduplicated union (S ∪ F ∪ E)'),
]
for key, label in derived:
    rows.append({
        'segment': key,
        'label': label,
        'central_tco2eq': results_all['central'][key],
        'low_tco2eq':     results_all['low'][key],
        'high_tco2eq':    results_all['high'][key],
        'central_pct':    results_all['central'][key] / total_ghg * 100,
        'low_pct':        results_all['low'][key] / total_ghg * 100,
        'high_pct':       results_all['high'][key] / total_ghg * 100,
    })

out = pd.DataFrame(rows)
out.to_csv(os.path.join(PROC_DIR, "cdmx_overlap_results.csv"), index=False)
print(f"  Saved: cdmx_overlap_results.csv ({len(out)} rows)")

print("\n" + "=" * 70)
print("02_estimate.py complete")
print("=" * 70)
