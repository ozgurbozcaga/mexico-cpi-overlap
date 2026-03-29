"""
02_estimate.py — Guanajuato Carbon Pricing Overlap Estimation
Case: Guanajuato state carbon tax (S) × Federal IEPS (F) × Mexico Pilot ETS (E)
Estimation tier: Tier 3

Instruments:
  S = Guanajuato state carbon tax
      Scope: CO2, CH4, N2O from stationary sources in energy and industrial sectors
      Exempt: transport (mobile), residential, commercial, agricultural, AFOLU, Waste
      Exempt: HFC emissions (state tax only covers CO2/CH4/N2O)

  F = Mexico Federal IEPS carbon tax (Art. 2o-C)
      Scope: upstream levy on ALL fossil fuels EXCEPT natural gas
      Covers at point of fuel sale → applied to combustión emisiones por tipo de combustible
      Key exemption: natural gas (NG) — creates large S∩E-only segment for NG combustion
      Does NOT cover: process emissions, fugitive emissions, biomass combustion

  E = Mexico Pilot ETS (legal scope)
      Scope: facilities >= 25,000 tCO2e/yr across energy and industrial sectors
      Status: non-binding pilot; treated as upper bound (legal coverage)
      ETS threshold in GgCO2e: 0.025 GgCO2e per facility per year

Venn segments computed:
  S∩F∩E  — covered by all three instruments
  S∩E    — covered by S and E but NOT F (NG combustion + process N2O in large facilities)
  S∩F    — covered by S and F but NOT E (non-NG fuels in small facilities below ETS threshold)
  S_only — covered by S only (NG combustion below threshold, small IPPU, ladrilleras biomass)
  F∩E    — large facilities using non-NG fuels outside S scope (expected ~0)
  F_only — non-NG fuel use outside S scope (transport dominant)
  E_only — large facilities outside S and F scope (expected ~0)
  uncov  — not covered by any instrument

Run: python scripts/02_estimate.py
Input: data/processed/sector_emissions_clean.csv
       data/processed/fuel_fractions_by_sector.csv
Output: data/processed/overlap_estimates.csv
        data/processed/overlap_estimates_scenarios.csv
"""

import os
import sys
import logging
import pandas as pd
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROC_DIR = os.path.join(BASE_DIR, 'data', 'processed')

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
log = logging.getLogger(__name__)

# ── Instrument scope definitions ──────────────────────────────────────────────

# S scope: stationary industrial/energy sources, CO2/CH4/N2O only
S_SCOPE = {
    'Industrias_energia',
    'Industrias_manufactura',
    'Ladrilleras',
    'Caprolactama',
    'Acido_nitrico',
    'Emisiones_fugitivas',
}
# HFC_RAC is NOT in S scope (S only covers CO2/CH4/N2O per state tax law)

# ── ETS coverage fractions (Tier 3 Pareto estimation) ─────────────────────────
# Three scenarios: (central, low, high)
# Documented in docs/assumptions_02.md
ETS_COVERAGE = {
    # Industrias_energia: Salamanca refinery (PEMEX) + associated power generation.
    # Single large facility processing 194.5 kbd crude (Tabla 4). Combustion
    # emissions ~4,431 GgCO2e/yr are orders of magnitude above ETS threshold.
    # Any co-located smaller operations raise uncertainty slightly.
    'Industrias_energia':   (0.95, 0.85, 0.99),

    # Industrias_manufactura: Bajío automotive cluster (GM Silao, Mazda Salamanca,
    # Honda El Salto region, VW suppliers), large food/beverage processors,
    # chemical plants. Large manufacturers will exceed threshold; smaller suppliers
    # below. Standard Pareto estimate for Mexican industrial states.
    'Industrias_manufactura': (0.65, 0.50, 0.80),

    # Ladrilleras: Brick kilns are family/small-scale in Guanajuato.
    # No individual kiln expected to exceed 25,000 tCO2e/yr.
    'Ladrilleras':          (0.00, 0.00, 0.00),

    # Caprolactama: Lanxess Guanajuato produces 85,000 t/yr caprolactama.
    # Process N2O alone = 202.7 GgCO2e >> 0.025 GgCO2e threshold. Definitively E-covered.
    'Caprolactama':         (1.00, 0.90, 1.00),

    # Acido_nitrico: 2,399 t/yr production. Process N2O = 5.7 GgCO2e.
    # As standalone N2O only, this is >> ETS threshold if at same facility.
    # Slight uncertainty on whether this is co-located with caprolactama.
    'Acido_nitrico':        (0.90, 0.70, 1.00),

    # Emisiones_fugitivas: Fugitive CH4 from Salamanca refinery.
    # The refinery itself is far above ETS threshold; its fugitives are
    # attributed to the same E-covered facility.
    'Emisiones_fugitivas':  (0.95, 0.85, 0.99),
}

# ── Non-NG fossil fuel fractions (F coverage) ─────────────────────────────────
# Source: fuel-level CO2 breakdown from IGCEI 2013 uncertainty table (pp.68-70)
# For sectors where F applies (stationary combustion):
# non_ng_fraction = fraction of total sector emissions from non-NG fossil fuels
# These fractions are treated as deterministic (data-derived from inventory table).
# Ladrilleras fossil fraction has explicit uncertainty range (see LOW/HIGH below).

# Central non-NG (F-covered) fractions:
F_FRACTION_CENTRAL = {
    'Industrias_energia':     0.2667,   # (combustoleo + diesel) / all fuels by CO2 mass
    'Industrias_manufactura': 0.4767,   # (combustoleo + diesel + LP + aceites) / all
    'Ladrilleras':            0.50,     # central assumption: 50% fossil
    'Caprolactama':           0.00,     # process emissions, not fuel combustion
    'Acido_nitrico':          0.00,     # process emissions, not fuel combustion
    'Emisiones_fugitivas':    0.00,     # fugitive CH4, not a fuel purchase
}

# Low/high for uncertain sectors only (Ladrilleras)
F_FRACTION_LOW = {**F_FRACTION_CENTRAL, 'Ladrilleras': 0.30}
F_FRACTION_HIGH = {**F_FRACTION_CENTRAL, 'Ladrilleras': 0.70}

# ── Transport and other F-only sectors (outside S scope) ──────────────────────
# These sectors are covered by F (non-NG fuels) but NOT by S or E
# Included for completeness in total F coverage reporting
F_ONLY_OUTSIDE_S = {
    'Autotransporte':         7068.4,    # all transport fuel non-NG
    'Aviacion':               88.6,      # jet fuel non-NG
    'Combustion_agricola':    257.8,     # agricultural mobile (LP + diesel)
    'Maquinaria_construccion': 52.8,     # construction machinery mobile
    # Residential LP and commercial LP also F-only:
    # Residential LP CO2 from table: 711.73 + CH4 1.55 + N2O 0.29 ≈ 713.6 GgCO2e
    # Commercial LP: ~169 GgCO2e (estimated as ~95% of 176.8 total commercial)
    'Residencial_LP':         713.6,
    'Comercial_LP':           168.8,
}


def compute_venn_segments(
    subsector: str,
    total_ggco2e: float,
    f_frac: float,
    ets_coverage: tuple,
) -> dict:
    """
    Compute the four S-scope Venn segments for a single subsector.

    Assumes independence between F-coverage (fuel-type based) and E-coverage
    (facility-size based) within a subsector. This is a conservative approximation
    appropriate for Tier 3 where facility-level data are unavailable.

    Independence assumption: the fuel mix of E-covered facilities equals the
    sector-average fuel mix. For Guanajuato this is plausible because:
    - The refinery uses both NG and non-NG fuels in roughly sector-average proportions
    - Large manufacturers have similar LP/NG/diesel mix to sector average

    Args:
        subsector: name for logging
        total_ggco2e: total emissions in S scope for this subsector (GgCO2e)
        f_frac: fraction covered by F (non-NG fossil fuels), central/low/high
        ets_coverage: tuple of (central, low, high) ETS coverage fractions

    Returns dict with segments for each scenario.
    """
    results = {}
    e_central, e_low, e_high = ets_coverage

    for scenario, e, f in [
        ('central', e_central, f_frac),
        ('low',     e_low,     F_FRACTION_LOW.get(subsector, f_frac)),
        ('high',    e_high,    F_FRACTION_HIGH.get(subsector, f_frac)),
    ]:
        ng_frac = 1.0 - f  # NG + biomass/fugitive fraction (not F-covered)

        s_f_e  = f * e * total_ggco2e        # S∩F∩E
        s_e    = ng_frac * e * total_ggco2e  # S∩E only (not F) — NG in large facilities
        s_f    = f * (1-e) * total_ggco2e    # S∩F only (not E)
        s_only = ng_frac * (1-e) * total_ggco2e  # S only

        total_check = s_f_e + s_e + s_f + s_only
        assert abs(total_check - total_ggco2e) < 0.01, (
            f"Venn total mismatch for {subsector}/{scenario}: "
            f"{total_check:.3f} != {total_ggco2e:.3f}"
        )

        results[scenario] = {
            'S_F_E':   round(s_f_e, 2),
            'S_E_only': round(s_e, 2),
            'S_F_only': round(s_f, 2),
            'S_only':  round(s_only, 2),
        }

    return results


def build_overlap_table(sector_df: pd.DataFrame, fractions_df: pd.DataFrame) -> pd.DataFrame:
    """
    Build the full Venn overlap table for all S-scope subsectors.
    """
    fractions = fractions_df.set_index('subsector')
    rows = []

    for _, srow in sector_df[sector_df['subsector'].isin(S_SCOPE)].iterrows():
        sub = srow['subsector']
        total = srow['total_ggco2e']

        if sub not in fractions.index:
            log.warning(f"  No fuel fraction data for {sub} — skipping")
            continue

        f_central = fractions.loc[sub, 'non_ng_fraction']
        ets_cov   = ETS_COVERAGE.get(sub, (0.0, 0.0, 0.0))

        segs = compute_venn_segments(sub, total, f_central, ets_cov)

        for scenario in ['central', 'low', 'high']:
            rows.append({
                'subsector':         sub,
                'sector':            srow['sector'],
                'scenario':          scenario,
                'total_S_scope_ggco2e': total,
                'f_fraction':        fractions.loc[sub, 'non_ng_fraction'] if scenario == 'central'
                                     else (F_FRACTION_LOW.get(sub, f_central) if scenario == 'low'
                                           else F_FRACTION_HIGH.get(sub, f_central)),
                'ets_fraction':      ets_cov[0] if scenario == 'central'
                                     else (ets_cov[1] if scenario == 'low' else ets_cov[2]),
                **segs[scenario],
            })

    return pd.DataFrame(rows)


def add_f_only_outside_s(overlap_df: pd.DataFrame) -> pd.DataFrame:
    """Append F-only (outside S scope) rows for completeness."""
    f_only_rows = []
    for subsector, total in F_ONLY_OUTSIDE_S.items():
        for scenario in ['central', 'low', 'high']:
            f_only_rows.append({
                'subsector':         subsector,
                'sector':            'ENERGIA_non_S',
                'scenario':          scenario,
                'total_S_scope_ggco2e': 0.0,
                'f_fraction':        1.0,
                'ets_fraction':      0.0,
                'S_F_E':    0.0,
                'S_E_only': 0.0,
                'S_F_only': 0.0,
                'S_only':   0.0,
                'F_only_outside_S': total,
            })
    f_only_df = pd.DataFrame(f_only_rows)
    return pd.concat([overlap_df, f_only_df], ignore_index=True, sort=False).fillna(0.0)


def summarise(overlap_df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate Venn segments by scenario, with and without F-only-outside-S."""
    s_scope = overlap_df[overlap_df['total_S_scope_ggco2e'] > 0]
    summary_rows = []

    for scenario in ['central', 'low', 'high']:
        df_s = s_scope[s_scope['scenario'] == scenario]
        df_all = overlap_df[overlap_df['scenario'] == scenario]

        total_S = df_s['total_S_scope_ggco2e'].sum()
        SFE      = df_s['S_F_E'].sum()
        SE       = df_s['S_E_only'].sum()
        SF       = df_s['S_F_only'].sum()
        S_only   = df_s['S_only'].sum()
        F_only   = df_all.get('F_only_outside_S', pd.Series([0]*len(df_all))).sum()

        # Derived coverage totals
        S_total  = SFE + SE + SF + S_only
        F_in_S   = SFE + SF          # F coverage within S scope
        E_in_S   = SFE + SE          # E coverage within S scope
        F_total  = SFE + SF + F_only # F total (S-scope + outside-S)

        # Deduplicated coverage (union)
        covered_by_any = S_total + F_only  # F_only is already outside S

        summary_rows.append({
            'scenario':               scenario,
            'S_total_ggco2e':         round(S_total, 1),
            'F_within_S_ggco2e':      round(F_in_S, 1),
            'E_within_S_ggco2e':      round(E_in_S, 1),
            'S∩F∩E_ggco2e':           round(SFE, 1),
            'S∩E_only_ggco2e':        round(SE, 1),
            'S∩F_only_ggco2e':        round(SF, 1),
            'S_only_ggco2e':          round(S_only, 1),
            'F_only_outside_S_ggco2e':round(F_only, 1),
            'F_total_ggco2e':         round(F_total, 1),
            'state_total_ggco2e':     19264.8,
            'S_share_pct':            round(S_total / 19264.8 * 100, 1),
            'F_share_pct':            round(F_total / 19264.8 * 100, 1),
        })

    return pd.DataFrame(summary_rows)


def main():
    log.info("=== 02_estimate.py — Guanajuato Overlap Estimation (Tier 3) ===")

    # Load processed data
    sector_df    = pd.read_csv(os.path.join(PROC_DIR, 'sector_emissions_clean.csv'))
    fractions_df = pd.read_csv(os.path.join(PROC_DIR, 'fuel_fractions_by_sector.csv'))

    log.info("S-scope subsectors and totals:")
    s_scope_total = 0
    for sub in S_SCOPE:
        row = sector_df[sector_df['subsector'] == sub]
        if len(row) > 0:
            total = row['total_ggco2e'].values[0]
            s_scope_total += total
            log.info(f"  {sub}: {total:.1f} GgCO2e")
    log.info(f"  TOTAL S scope: {s_scope_total:.1f} GgCO2e")
    log.info(f"  HFC_RAC excluded from S scope: 306.8 GgCO2e (HFC not covered by state tax)")

    # Build overlap table (subsector × scenario)
    overlap_df = build_overlap_table(sector_df, fractions_df)
    overlap_df = add_f_only_outside_s(overlap_df)

    # Summary table
    summary_df = summarise(overlap_df)

    # ── Print central results ──────────────────────────────────────────────────
    central = summary_df[summary_df['scenario'] == 'central'].iloc[0]
    log.info("\n=== CENTRAL SCENARIO RESULTS ===")
    log.info(f"  S total coverage:       {central['S_total_ggco2e']:>8.1f} GgCO2e "
             f"({central['S_share_pct']:.1f}% of state total)")
    log.info(f"  F total coverage:       {central['F_total_ggco2e']:>8.1f} GgCO2e "
             f"({central['F_share_pct']:.1f}% of state total)")
    log.info(f"  --- Venn segments (within S scope) ---")
    log.info(f"  S∩F∩E:                  {central['S∩F∩E_ggco2e']:>8.1f} GgCO2e")
    log.info(f"  S∩E only (not F):       {central['S∩E_only_ggco2e']:>8.1f} GgCO2e  "
             f"← NG in large facilities + process N2O")
    log.info(f"  S∩F only (not E):       {central['S∩F_only_ggco2e']:>8.1f} GgCO2e  "
             f"← non-NG fuels in small facilities")
    log.info(f"  S only:                 {central['S_only_ggco2e']:>8.1f} GgCO2e  "
             f"← NG small facilities + process N2O small IPPU")
    log.info(f"  F only (outside S):     {central['F_only_outside_S_ggco2e']:>8.1f} GgCO2e  "
             f"← transport dominant")

    # Print subsector-level breakdown
    log.info("\n=== SUBSECTOR BREAKDOWN (central scenario) ===")
    central_sub = overlap_df[
        (overlap_df['scenario'] == 'central') &
        (overlap_df['total_S_scope_ggco2e'] > 0)
    ].copy()
    for _, row in central_sub.iterrows():
        log.info(
            f"  {row['subsector']:<30} total={row['total_S_scope_ggco2e']:>7.1f}  "
            f"S∩F∩E={row['S_F_E']:>7.1f}  "
            f"S∩E={row['S_E_only']:>7.1f}  "
            f"S∩F={row['S_F_only']:>6.1f}  "
            f"S_only={row['S_only']:>6.1f}"
        )

    # ── Write outputs ──────────────────────────────────────────────────────────
    out_detail = os.path.join(PROC_DIR, 'overlap_estimates.csv')
    overlap_df.to_csv(out_detail, index=False)
    log.info(f"\nWrote: {out_detail}")

    out_summary = os.path.join(PROC_DIR, 'overlap_summary.csv')
    summary_df.to_csv(out_summary, index=False)
    log.info(f"Wrote: {out_summary}")

    # ── Key structural note ────────────────────────────────────────────────────
    log.info("\n=== KEY STRUCTURAL FINDINGS ===")
    log.info("  1. NG exemption from F creates dominant S∩E-only segment:")
    log.info("     Salamanca refinery + large manufacturers use NG heavily →")
    log.info("     ~3,960 GgCO2e covered by S and E but NOT F (central)")
    log.info("  2. Process N2O (caprolactama + ácido nítrico = 208.4 GgCO2e):")
    log.info("     In S scope and E scope but NOT F scope → S∩E-only segment")
    log.info("  3. Transport (7,068 GgCO2e) is F-only — NOT in S or E scope")
    log.info("  4. HFC (306.8 GgCO2e) outside all three instruments (not CO2/CH4/N2O)")
    log.info("  5. No process CO2 (no cement, no glass) — different from Morelos")

    log.info("=== 02_estimate.py complete ===")


if __name__ == '__main__':
    main()
