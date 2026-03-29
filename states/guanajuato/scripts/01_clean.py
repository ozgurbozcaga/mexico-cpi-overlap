"""
01_clean.py — Guanajuato Carbon Pricing Overlap Analysis
Case: Guanajuato state carbon tax × Mexico Federal IEPS × Mexico Pilot ETS
Estimation tier: Tier 3 (Pareto/size-based ETS; fuel-level F fractions from inventory table)
Base year: 2013

Instruments:
  S = Guanajuato state carbon tax — CO2, CH4, N2O from stationary industrial/energy sources
  F = Mexico Federal IEPS carbon tax (Art. 2o-C) — upstream levy on all fossil fuels except NG
  E = Mexico Pilot ETS — legal scope, facilities >= 25,000 tCO2e/yr, non-binding

Key structural features of Guanajuato (from IGCEI 2013, Instituto de Ecología del Estado):
  - Salamanca refinery (PEMEX) dominates energy industries (NG 53.15 PJ + fuel oil 13.78 PJ)
  - NG exemption from F creates large S∩E-only segment (NG in large stationary facilities)
  - Process N2O (caprolactama 202.7 GgCO2e, ácido nítrico 5.7 GgCO2e) in S and E scope but NOT F
  - No cement production, no blast furnaces (unlike Morelos)
  - HFC (306.8 GgCO2e) excluded from S scope (state tax covers CO2/CH4/N2O only)
  - Ladrilleras (brick kilns, 12.1 GgCO2e): local stationary category, mixed fuel, below ETS threshold

Data sources relied on:
  - IGCEI Guanajuato 2013: results table (p.51), fuel consumption Table 2 (p.26),
    uncertainty table (pp.68-70), Table 5 IPPU activity (p.30)
  - GWP AR5: CH4=28, N2O=265

Run: python scripts/01_clean.py
Outputs: data/processed/sector_emissions_clean.csv
         data/processed/fuel_fractions_by_sector.csv
         data/processed/validation_report.txt
"""

import os
import sys
import logging
import pandas as pd
import numpy as np

# ── paths ──────────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR  = os.path.join(BASE_DIR, 'data', 'raw')
PROC_DIR = os.path.join(BASE_DIR, 'data', 'processed')
os.makedirs(PROC_DIR, exist_ok=True)

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
log = logging.getLogger(__name__)

# ── GWP constants (AR5, consistent across all state pipelines) ─────────────────
GWP_CH4 = 28
GWP_N2O = 265

# ── known totals from IGCEI 2013 (for validation) ─────────────────────────────
KNOWN_TOTALS = {
    'state_total_ggco2e': 19264.8,
    'energia_total_ggco2e': 14794.7,
    'ippu_total_ggco2e': 515.2,
    'co2_total_gg': 12945.1,    # net across all sectors
    'ch4_total_ggco2e': 3679.6,
    'n2o_total_ggco2e': 2333.3,
    'hfc_total_ggco2e': 306.8,
}


def load_sector_emissions() -> pd.DataFrame:
    """Load and return sector emissions from raw CSV."""
    fpath = os.path.join(RAW_DIR, 'guanajuato_sector_emissions_2013.csv')
    df = pd.read_csv(fpath)
    log.info(f"Loaded {len(df)} subsector rows from raw sector emissions")
    return df


def load_fuel_co2() -> pd.DataFrame:
    """Load fuel-level CO2/GHG breakdown from uncertainty table extract."""
    fpath = os.path.join(RAW_DIR, 'guanajuato_fuel_co2_by_sector_2013.csv')
    df = pd.read_csv(fpath)
    log.info(f"Loaded {len(df)} fuel×sector rows from CO2 breakdown table")
    return df


def load_fuel_consumption() -> pd.DataFrame:
    """Load fuel consumption in PJ from Table 2."""
    fpath = os.path.join(RAW_DIR, 'guanajuato_fuel_consumption_pj_2013.csv')
    df = pd.read_csv(fpath)
    log.info(f"Loaded {len(df)} sector×fuel rows from fuel consumption table")
    return df


def compute_fuel_fractions(fuel_co2: pd.DataFrame) -> pd.DataFrame:
    """
    Compute NG fraction and non-NG (F-covered) fraction of combustion emissions
    for S-scope stationary sectors, based on fuel-level CO2 breakdown.

    For energy industries and manufacturing, the split is deterministic from the
    inventory uncertainty table which provides CO2 by fuel type.

    Returns DataFrame with one row per stationary sector showing:
      - total_co2_gg_from_table: CO2 summed over fuels in uncertainty table
      - ng_fraction: fraction attributable to natural gas (not covered by F)
      - non_ng_fraction: fraction attributable to non-NG fossil fuels (covered by F)
      - notes on residual/biomass
    """
    records = []

    # ── Energy industries ──────────────────────────────────────────────────────
    ei = fuel_co2[fuel_co2['sector'] == 'Industrias_energia']
    ei_total = ei['co2_gg'].sum()
    ei_ng    = ei.loc[ei['fuel'] == 'Gas_natural', 'co2_gg'].sum()
    ei_non_ng = ei.loc[ei['fuel'] != 'Gas_natural', 'co2_gg'].sum()
    records.append({
        'subsector': 'Industrias_energia',
        'total_co2_from_table_gg': round(ei_total, 2),
        'ng_co2_gg': round(ei_ng, 2),
        'non_ng_co2_gg': round(ei_non_ng, 2),
        'ng_fraction': round(ei_ng / ei_total, 4) if ei_total > 0 else 0,
        'non_ng_fraction': round(ei_non_ng / ei_total, 4) if ei_total > 0 else 0,
        'biomass_fraction': 0.0,
        'note': 'Fuels: combustoleo, GN, diesel. GN=78.9% by PJ but 73.3% by CO2 (lower EF)'
    })

    # ── Manufacturing industries ───────────────────────────────────────────────
    mf = fuel_co2[fuel_co2['sector'] == 'Industrias_manufactura']
    mf_total = mf['co2_gg'].sum()
    mf_ng    = mf.loc[mf['fuel'] == 'Gas_natural', 'co2_gg'].sum()
    mf_non_ng = mf.loc[
        (mf['fuel'] != 'Gas_natural') & (mf['fuel'] != 'Aceites_gastados'), 'co2_gg'
    ].sum()
    mf_other  = mf.loc[mf['fuel'] == 'Aceites_gastados', 'co2_gg'].sum()
    records.append({
        'subsector': 'Industrias_manufactura',
        'total_co2_from_table_gg': round(mf_total, 2),
        'ng_co2_gg': round(mf_ng, 2),
        'non_ng_co2_gg': round(mf_non_ng + mf_other, 2),
        'ng_fraction': round(mf_ng / mf_total, 4) if mf_total > 0 else 0,
        'non_ng_fraction': round((mf_non_ng + mf_other) / mf_total, 4) if mf_total > 0 else 0,
        'biomass_fraction': 0.0,
        'note': 'Fuels: combustoleo, diesel, LP, GN, aceites. Leña/biogas residual ~17% not in table'
    })

    # ── Ladrilleras (brick kilns) ──────────────────────────────────────────────
    # Not in uncertainty table; use informed assumption: ~50% fossil (diesel/LP),
    # ~50% biomass (firewood). No NG assumed in brick kilns.
    records.append({
        'subsector': 'Ladrilleras',
        'total_co2_from_table_gg': 0.0,  # not disaggregated in table
        'ng_co2_gg': 0.0,
        'non_ng_co2_gg': 0.0,
        'ng_fraction': 0.0,
        'non_ng_fraction': 0.50,  # central assumption: 50% fossil fuels
        'biomass_fraction': 0.50,
        'note': 'Brick kilns: assumed 50% fossil (diesel/LP), 50% biomass; range 30-70% fossil'
    })

    # ── IPPU process emissions ─────────────────────────────────────────────────
    # Process N2O is not from fuel combustion; F does not apply
    for sub in ['Caprolactama', 'Acido_nitrico']:
        records.append({
            'subsector': sub,
            'total_co2_from_table_gg': 0.0,
            'ng_co2_gg': 0.0,
            'non_ng_co2_gg': 0.0,
            'ng_fraction': 0.0,
            'non_ng_fraction': 0.0,
            'biomass_fraction': 0.0,
            'note': 'Process N2O emissions — not from fuel combustion; F (fuel levy) does not apply'
        })

    # ── Fugitive emissions ─────────────────────────────────────────────────────
    records.append({
        'subsector': 'Emisiones_fugitivas',
        'total_co2_from_table_gg': 0.0,
        'ng_co2_gg': 0.0,
        'non_ng_co2_gg': 0.0,
        'ng_fraction': 0.0,
        'non_ng_fraction': 0.0,
        'biomass_fraction': 0.0,
        'note': 'Fugitive CH4 from petroleum refining; not a fuel sale; F does not apply'
    })

    return pd.DataFrame(records)


def validate_sector_totals(df: pd.DataFrame) -> list:
    """
    Validate computed totals against known inventory aggregates.
    Returns list of validation messages.
    """
    msgs = []

    # State total
    state_total = df['total_ggco2e'].sum()
    expected = KNOWN_TOTALS['state_total_ggco2e']
    diff_pct = abs(state_total - expected) / expected * 100
    msgs.append(
        f"State total: computed={state_total:.1f}, expected={expected:.1f}, "
        f"diff={diff_pct:.2f}% {'OK' if diff_pct < 0.1 else 'WARNING'}"
    )

    # Energy sector
    energia = df[df['sector'] == 'ENERGIA']['total_ggco2e'].sum()
    expected_e = KNOWN_TOTALS['energia_total_ggco2e']
    diff_pct_e = abs(energia - expected_e) / expected_e * 100
    msgs.append(
        f"Energy sector: computed={energia:.1f}, expected={expected_e:.1f}, "
        f"diff={diff_pct_e:.2f}% {'OK' if diff_pct_e < 0.1 else 'WARNING'}"
    )

    # IPPU total
    ippu = df[df['sector'] == 'IPPU']['total_ggco2e'].sum()
    expected_i = KNOWN_TOTALS['ippu_total_ggco2e']
    diff_pct_i = abs(ippu - expected_i) / expected_i * 100
    msgs.append(
        f"IPPU sector: computed={ippu:.1f}, expected={expected_i:.1f}, "
        f"diff={diff_pct_i:.2f}% {'OK' if diff_pct_i < 0.1 else 'WARNING'}"
    )

    # CO2 total (net)
    co2_total = df['co2_gg'].sum()
    expected_co2 = KNOWN_TOTALS['co2_total_gg']
    diff_pct_co2 = abs(co2_total - expected_co2) / abs(expected_co2) * 100
    msgs.append(
        f"Net CO2 total: computed={co2_total:.1f}, expected={expected_co2:.1f}, "
        f"diff={diff_pct_co2:.2f}% {'OK' if diff_pct_co2 < 0.1 else 'WARNING'}"
    )

    return msgs


def main():
    log.info("=== 01_clean.py — Guanajuato 2013 GHG Inventory Cleaning ===")

    # Load raw data
    sector_df   = load_sector_emissions()
    fuel_co2_df = load_fuel_co2()
    fuel_pj_df  = load_fuel_consumption()

    # ── Validate/clean sector emissions ───────────────────────────────────────
    # Recompute total from components as a sanity check
    sector_df['total_check'] = (
        sector_df['co2_gg'].fillna(0) +
        sector_df['ch4_ggco2e'].fillna(0) +
        sector_df['n2o_ggco2e'].fillna(0) +
        sector_df['hfc_ggco2e'].fillna(0)
    )
    sector_df['total_diff'] = (sector_df['total_ggco2e'] - sector_df['total_check']).abs()
    max_diff = sector_df['total_diff'].max()
    if max_diff > 0.05:
        log.warning(f"Max internal total discrepancy: {max_diff:.3f} GgCO2e — check raw data")
    else:
        log.info(f"Internal total check passed (max discrepancy: {max_diff:.4f} GgCO2e)")

    # ── Fuel fractions ─────────────────────────────────────────────────────────
    fuel_fractions = compute_fuel_fractions(fuel_co2_df)
    log.info("Fuel fractions computed:")
    for _, row in fuel_fractions.iterrows():
        log.info(
            f"  {row['subsector']}: NG={row['ng_fraction']:.2%}, "
            f"nonNG={row['non_ng_fraction']:.2%}, biomass={row['biomass_fraction']:.2%}"
        )

    # ── Validation ─────────────────────────────────────────────────────────────
    validation_msgs = validate_sector_totals(sector_df)

    # ── Note on gap between uncertainty table and results table ────────────────
    # Energy industries CO2 from uncertainty table: 1079.56+3043.80+30.05=4153.41 Gg
    # Results table shows 4424.2 Gg CO2. Gap = ~271 Gg (~6.1%).
    # This gap likely reflects fuels not individually listed in the uncertainty table
    # (e.g. additional heavy fuel fractions, coke, waste fuels at refinery).
    # We apply fuel fractions derived from the uncertainty table to the results-table
    # totals, treating the gap as distributed proportionally across fuels.
    gap_ei = 4424.2 - (1079.56 + 3043.80 + 30.05)
    log.info(
        f"Energy industries CO2 gap (results table vs uncertainty table): "
        f"{gap_ei:.1f} Gg ({gap_ei/4424.2*100:.1f}%); "
        f"distributed proportionally to NG/non-NG fractions in estimation"
    )

    # ── Write outputs ──────────────────────────────────────────────────────────
    # Drop helper columns before saving
    clean_cols = [
        'sector', 'subsector', 'category_ipcc',
        'co2_gg', 'ch4_ggco2e', 'n2o_ggco2e', 'hfc_ggco2e', 'total_ggco2e', 'notes'
    ]
    sector_clean = sector_df[clean_cols].copy()
    out_sectors = os.path.join(PROC_DIR, 'sector_emissions_clean.csv')
    sector_clean.to_csv(out_sectors, index=False)
    log.info(f"Wrote: {out_sectors}")

    out_fractions = os.path.join(PROC_DIR, 'fuel_fractions_by_sector.csv')
    fuel_fractions.to_csv(out_fractions, index=False)
    log.info(f"Wrote: {out_fractions}")

    # Write validation report
    out_val = os.path.join(PROC_DIR, 'validation_report.txt')
    with open(out_val, 'w') as f:
        f.write("=== VALIDATION REPORT: Guanajuato 2013 GHG Inventory ===\n\n")
        for msg in validation_msgs:
            f.write(msg + '\n')
        f.write("\n=== KEY DATA NOTES ===\n")
        f.write(f"State total: 19,264.8 GgCO2e (IPCC 2006 methodology, AR5 GWPs)\n")
        f.write(f"Energy sector: 14,794.7 GgCO2e (76.8% of total)\n")
        f.write(f"Energy industries CO2 gap: {gap_ei:.1f} Gg distributed proportionally\n")
        f.write(f"IPPU: 515.2 GgCO2e — includes 306.8 HFC (excluded from state tax scope)\n")
        f.write(f"Process N2O in S scope: 208.4 GgCO2e (caprolactama + acid nitric)\n")
        f.write(f"No cement or blast furnace process CO2 (unlike Morelos)\n")
        f.write(f"NG fraction energy industries: 73.3% (by CO2 mass)\n")
        f.write(f"NG fraction manufacturing: 52.3% (by CO2 mass)\n")
        f.write(f"Ladrilleras fossil fraction: 50% (central assumption, range 30-70%)\n")
    log.info(f"Wrote: {out_val}")

    log.info("=== 01_clean.py complete ===")
    for msg in validation_msgs:
        log.info(f"  VALIDATION: {msg}")


if __name__ == '__main__':
    main()
