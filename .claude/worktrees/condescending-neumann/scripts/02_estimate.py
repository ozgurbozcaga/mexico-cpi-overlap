"""
02_estimate.py — Overlap estimation
=====================================
Case:            Mexico Federal Carbon Tax × Mexico Pilot ETS (SCE Fase Piloto)
Estimation tier: Tier 2 (ETS coverage) / Tier 3 (NG-share uncertainty propagation)

Produces three output series, each with point estimate + low/high bounds:

  A) Carbon tax coverage  — 2014-2024 (MtCO2)
     = INECC 1A_total combustion CO2 minus NG combustion CO2 (narrow/conservative scope)
     Excludes: natural gas combustion, process CO2 (2A/2B/2C), fugitives (1B)

  B) ETS coverage — 2020-2024 (MtCO2)
     = SEMARNAT pilot allocations as proxy for covered emissions
     2020-2021: direct from allocation table
     2022-2024: extrapolated via INECC subcategory growth rates
     Separately reports: combustion CO2 covered, process CO2 covered, NG CO2 within ETS

  C) Overlap (A ∩ B) — 2020-2023 (MtCO2)
     = ETS-covered combustion CO2 from non-NG fuels only
     = ETS combustion coverage × (1 - NG share)
     Process CO2 and NG combustion in ETS are NOT in scope of carbon tax → not overlap

     Uncertainty bounds propagated from NG share low/high per sector.

Key assumptions:
  - SEMARNAT allocation = operational coverage proxy (no MRV/registry data available)
  - Carbon tax scope: narrow/conservative — 1A combustion only, NG zero-rated, 1B excluded
  - NG shares: BNE-derived for power (84.7% ±2pp); expert ranges for other sectors
  - 2A4 (other carbonates, ~5.4 Mt): excluded from central estimate; included in sensitivity
  - 1A2miii (otras ramas, ~22 Mt): excluded from ETS scope; noted as conservatism source

Run: python scripts/02_estimate.py
"""

import pandas as pd
import numpy as np
import logging
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW  = ROOT / "data" / "raw"
PROC = ROOT / "data" / "processed"
OUT  = ROOT / "outputs" / "tables"
OUT.mkdir(parents=True, exist_ok=True)

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
log = logging.getLogger(__name__)

CTAX_YEARS    = [str(y) for y in range(2014, 2025)]
ETS_YEARS     = [str(y) for y in range(2020, 2025)]
OVERLAP_YEARS = [str(y) for y in range(2020, 2024)]

# ══════════════════════════════════════════════════════════════════════════════
# NATIONAL GHG TOTALS
# ══════════════════════════════════════════════════════════════════════════════

def load_national_totals():
    """
    Extract INECC 'EMISIONES Sin UTCUTS' total GHG in MtCO2e for all years 2014-2024.

    Source: INECC INEGYCEI annual inventories.
    Denominator: all-gas CO2e, excluding LULUCF (Sin UTCUTS), as per State & Trends convention.

    Note: numerators (carbon tax, ETS, overlap) are CO2-only. The coverage shares are
    therefore conservative — CH4 and N2O from covered facilities are not counted in the
    numerator. This is standard practice for carbon pricing coverage ratios and is noted
    in the methodology documentation.

    Column reference:
      2014-2019 file (multi-sheet): col index 28 = 'EMISIONES t de CO2e' summary column
      2020-2024 files: 'Unnamed: 28' = same summary column
    """
    log.info("Loading national GHG totals (Sin UTCUTS) 2014-2024...")
    totals = {}

    # 2014-2019
    path_old = RAW / "INEGyCEI_2014-2019.xlsx"
    xl = pd.ExcelFile(path_old)
    for yr in xl.sheet_names:
        df = pd.read_excel(path_old, sheet_name=yr, header=None)
        mask = df[0].astype(str).str.contains('Sin UTCUTS', na=False)
        val = pd.to_numeric(df[mask].iloc[0, 28], errors='coerce')
        totals[yr] = val / 1e6 if pd.notna(val) else np.nan
        log.info("  %s: national total = %.1f MtCO2e", yr, totals[yr])

    # 2020-2024
    for yr in range(2020, 2025):
        path = RAW / f"mexico_{yr}_ghgemissions.xlsx"
        df = pd.read_excel(path)
        mask = df.iloc[:, 0].astype(str).str.contains('Sin UTCUTS', na=False)
        val = pd.to_numeric(df[mask].iloc[0]['Unnamed: 28'], errors='coerce')
        totals[str(yr)] = val / 1e6 if pd.notna(val) else np.nan
        log.info("  %s: national total = %.1f MtCO2e", yr, totals[str(yr)])

    return pd.Series(totals, name='national_ghg_mt')


# ── SEMARNAT ETS pilot allocations 2020-2021 (MtCO2)
# Source: SEMARNAT Aviso DOF 27 Nov 2019 — allocation table, pilot phase
# Allocation used as proxy for operational coverage (best available data)
# NOTE: allocations ≈ covered emissions in pilot phase (no binding surrender obligation
# but allocation = facility-level cap = coverage proxy)
SEMARNAT_ALLOC = {
    # sector label        : {year: MtCO2}
    "electricidad":         {"2020": 138.1, "2021": 138.1},
    "petroleo_gas":         {"2020":  35.3, "2021":  35.3},
    "refinacion":           {"2020":  17.8, "2021":  17.8},
    "cemento":              {"2020":  30.2, "2021":  30.2},
    "hierro_acero":         {"2020":  14.7, "2021":  14.7},
    "industria_quimica":    {"2020":   7.0, "2021":   7.0},
    "petroquimica":         {"2020":   5.7, "2021":   5.7},
    "cal":                  {"2020":   0.6, "2021":   0.6},
    "vidrio":               {"2020":   2.7, "2021":   2.7},
    "mineria":              {"2020":   2.1, "2021":   2.1},
    "papel":                {"2020":   2.3, "2021":   2.3},
    "alimentos_bebidas":    {"2020":   7.7, "2021":   7.7},
    "otros":                {"2020":   7.0, "2021":   8.8},
}

# INECC category → ETS sector mapping
# Used for growth-rate extrapolation and process/combustion split
SECTOR_INECC_MAP = {
    "electricidad":      {"combustion": ["1A1a"],           "process": []},
    "petroleo_gas":      {"combustion": ["1A1cii"],         "process": []},
    "refinacion":        {"combustion": ["1A1b"],           "process": []},
    "cemento":           {"combustion": ["1A2b"],           "process": ["2A1"]},
    "cal":               {"combustion": ["1A2b"],           "process": ["2A2"]},
    "vidrio":            {"combustion": ["1A2b"],           "process": ["2A3"]},
    "hierro_acero":      {"combustion": ["1A2a"],           "process": ["2C1"]},
    "industria_quimica": {"combustion": ["1A2c"],           "process": ["2B1","2B8"]},
    "petroquimica":      {"combustion": ["1A2c"],           "process": ["2B8"]},
    "mineria":           {"combustion": ["1A2i"],           "process": []},
    "papel":             {"combustion": ["1A2d"],           "process": ["2H1"]},
    "alimentos_bebidas": {"combustion": ["1A2e"],           "process": []},
    "otros":             {"combustion": ["1A2g"],           "process": []},
}

# For cement/lime/glass: share of combined IEA non-metallic allocation
# Based on 2020-2021 SEMARNAT allocations as fractions of combined 33.5 Mt
NONMETALLIC_SHARE = {
    "cemento": 30.2 / (30.2 + 0.6 + 2.7),
    "cal":      0.6 / (30.2 + 0.6 + 2.7),
    "vidrio":   2.7 / (30.2 + 0.6 + 2.7),
}

# NG share selector per ETS sector
# Maps sector → key in ng_shares dataframe
NG_SHARE_KEY = {
    "electricidad":      ("1A1a_ng_point",    "1A1a_ng_low",    "1A1a_ng_high"),
    "petroleo_gas":      ("1A1cii_ng_point",  "1A1cii_ng_low",  "1A1cii_ng_high"),
    "refinacion":        ("1A1b_ng_point",    "1A1b_ng_low",    "1A1b_ng_high"),
    "cemento":           ("nm_ng_point",      "nm_ng_low",      "nm_ng_high"),
    "cal":               ("nm_ng_point",      "nm_ng_low",      "nm_ng_high"),
    "vidrio":            ("nm_ng_point",      "nm_ng_low",      "nm_ng_high"),
    "hierro_acero":      ("other_ng_point",   "other_ng_low",   "other_ng_high"),
    "industria_quimica": ("other_ng_point",   "other_ng_low",   "other_ng_high"),
    "petroquimica":      ("other_ng_point",   "other_ng_low",   "other_ng_high"),
    "mineria":           ("1A2i_ng_point",    "1A2i_ng_low",    "1A2i_ng_high"),
    "papel":             ("other_ng_point",   "other_ng_low",   "other_ng_high"),
    "alimentos_bebidas": ("other_ng_point",   "other_ng_low",   "other_ng_high"),
    "otros":             ("other_ng_point",   "other_ng_low",   "other_ng_high"),
}


# ══════════════════════════════════════════════════════════════════════════════
# A. CARBON TAX COVERAGE
# ══════════════════════════════════════════════════════════════════════════════

def estimate_carbon_tax_coverage(inecc, ng_shares):
    """
    Carbon tax coverage = INECC 1A_total − NG combustion CO2 across all sectors.

    NG combustion CO2 = sum over 1A subcategories of (category CO2 × NG share).

    Sectors covered by BNE-derived NG shares:
      1A1a (power), 1A1b (refining), 1A1cii (O&G upstream)
    Residual sectors (1A3 transport + 1A4 other + 1A2 industry):
      NG share derived from 1A_total gap × weighted average of sector NG shares.

    Note: 1B fugitives excluded (narrow/conservative scope per methodology decision).
    """
    log.info("Estimating carbon tax coverage 2014-2024...")
    records = []

    for yr in CTAX_YEARS:
        iyr = int(yr)
        row_i = inecc.loc[iyr] if iyr in inecc.index else inecc.loc[yr]
        row_ng = ng_shares.loc[iyr] if iyr in ng_shares.index else ng_shares.loc[yr]

        total_1A = row_i["1A_total"]

        # Known sector CO2 values
        co2_1A1a   = row_i["1A1a"]
        co2_1A1b   = row_i["1A1b"]
        co2_1A1cii = row_i["1A1cii"]

        # 1A2 industry aggregate (sum of available subcats)
        industry_subcats = ["1A2a","1A2b","1A2c","1A2d","1A2e","1A2g","1A2i","1A2miii"]
        co2_1A2 = sum(row_i[c] for c in industry_subcats if pd.notna(row_i.get(c)))

        # Residual = 1A_total - energy industries - 1A2
        # Captures: 1A3 (transport) + 1A4 (residential/commercial/agriculture)
        co2_residual = total_1A - co2_1A1a - co2_1A1b - co2_1A1cii - co2_1A2

        def ng_co2(co2_val, point_key, low_key, high_key):
            return (
                co2_val * row_ng[point_key],
                co2_val * row_ng[low_key],
                co2_val * row_ng[high_key],
            )

        # NG CO2 by sector
        ng_1A1a_p,  ng_1A1a_l,  ng_1A1a_h  = ng_co2(co2_1A1a,   "1A1a_ng_point",   "1A1a_ng_low",   "1A1a_ng_high")
        ng_1A1b_p,  ng_1A1b_l,  ng_1A1b_h  = ng_co2(co2_1A1b,   "1A1b_ng_point",   "1A1b_ng_low",   "1A1b_ng_high")
        ng_1Acii_p, ng_1Acii_l, ng_1Acii_h = ng_co2(co2_1A1cii, "1A1cii_ng_point", "1A1cii_ng_low", "1A1cii_ng_high")

        # Industry: use BNE industry aggregate NG share
        ind_ng_p = row_ng["industry_ng_share"]
        ind_ng_l = max(0, ind_ng_p - 0.05) if pd.notna(ind_ng_p) else 0.25
        ind_ng_h = min(1, ind_ng_p + 0.05) if pd.notna(ind_ng_p) else 0.45
        ng_1A2_p, ng_1A2_l, ng_1A2_h = co2_1A2*ind_ng_p, co2_1A2*ind_ng_l, co2_1A2*ind_ng_h

        # Residual (transport + other sectors): transport is >95% non-NG; residential ~5-10%
        # Conservative estimate: 5% NG share on residual
        ng_res_p, ng_res_l, ng_res_h = co2_residual*0.05, co2_residual*0.02, co2_residual*0.10

        total_ng_p = ng_1A1a_p + ng_1A1b_p + ng_1Acii_p + ng_1A2_p + ng_res_p
        total_ng_l = ng_1A1a_l + ng_1A1b_l + ng_1Acii_l + ng_1A2_l + ng_res_l
        total_ng_h = ng_1A1a_h + ng_1A1b_h + ng_1Acii_h + ng_1A2_h + ng_res_h

        ctax_point = total_1A - total_ng_p
        ctax_low   = total_1A - total_ng_h  # less NG subtracted → higher coverage → low bound on coverage uncertainty?
        ctax_high  = total_1A - total_ng_l  # Note: low NG bound → more taxed → high coverage

        records.append({
            "year":              yr,
            "inecc_1A_total_mt": total_1A,
            "ng_co2_point_mt":   total_ng_p,
            "ng_co2_low_mt":     total_ng_l,
            "ng_co2_high_mt":    total_ng_h,
            "ctax_coverage_point_mt": ctax_point,
            "ctax_coverage_low_mt":   ctax_low,
            "ctax_coverage_high_mt":  ctax_high,
            # Breakdown for audit trail
            "ng_power_mt":      ng_1A1a_p,
            "ng_refining_mt":   ng_1A1b_p,
            "ng_og_mt":         ng_1Acii_p,
            "ng_industry_mt":   ng_1A2_p,
            "ng_residual_mt":   ng_res_p,
        })
        log.info("  %s: 1A_total=%.1f, NG=%.1f (l=%.1f h=%.1f), ctax=%.1f Mt",
                 yr, total_1A, total_ng_p, total_ng_l, total_ng_h, ctax_point)

    return pd.DataFrame(records).set_index("year")


# ══════════════════════════════════════════════════════════════════════════════
# B. ETS COVERAGE
# ══════════════════════════════════════════════════════════════════════════════

def estimate_ets_coverage(inecc, ng_shares):
    """
    ETS coverage = SEMARNAT allocations as proxy for operational coverage.

    2020-2021: direct from SEMARNAT Aviso (DOF 27 Nov 2019).
    2022-2024: extrapolated using INECC category growth rates applied to 2021 baseline.

    For each sector, total allocation is split into:
      - Combustion component: using INECC combustion/process ratio
      - Process component:    remainder

    NG share applied to combustion component only.
    """
    log.info("Estimating ETS coverage 2020-2024...")

    # Pre-compute INECC combustion/total ratios per sector for 2020 onwards
    def get_comb_fraction(sector, yr, inecc_row):
        """Fraction of sector allocation attributable to combustion (not process CO2)."""
        comb_cats = SECTOR_INECC_MAP[sector]["combustion"]
        proc_cats = SECTOR_INECC_MAP[sector]["process"]
        comb_co2 = sum(inecc_row.get(c, 0) or 0 for c in comb_cats)
        proc_co2 = sum(inecc_row.get(c, 0) or 0 for c in proc_cats)
        total = comb_co2 + proc_co2
        if total <= 0:
            return 1.0  # default: all combustion if no process data
        return comb_co2 / total

    # Build sector allocations for all ETS years
    sector_records = []
    for sector in SEMARNAT_ALLOC:
        for yr in ETS_YEARS:
            iyr = int(yr)
            inecc_row = inecc.loc[iyr] if iyr in inecc.index else inecc.loc[yr]
            ng_row    = ng_shares.loc[iyr] if iyr in ng_shares.index else ng_shares.loc[yr]

            # Allocation: 2020-2021 direct; 2022-2024 extrapolated
            if yr in ("2020", "2021"):
                alloc = SEMARNAT_ALLOC[sector][yr]
            else:
                # Growth rate: use primary INECC combustion category growth
                comb_cats = SECTOR_INECC_MAP[sector]["combustion"]
                # Use first available combustion category for growth rate
                base_val_2021, curr_val = None, None
                for cat in comb_cats:
                    b = inecc.loc[2021, cat] if 2021 in inecc.index else None
                    c = inecc_row.get(cat)
                    if b and b > 0 and pd.notna(c):
                        base_val_2021, curr_val = b, c
                        break
                if base_val_2021 and curr_val and base_val_2021 > 0:
                    growth = curr_val / base_val_2021
                    alloc = SEMARNAT_ALLOC[sector]["2021"] * growth
                else:
                    alloc = SEMARNAT_ALLOC[sector]["2021"]  # flat if no growth data

            # Combustion/process split
            comb_frac = get_comb_fraction(sector, yr, inecc_row)
            alloc_comb  = alloc * comb_frac
            alloc_proc  = alloc * (1 - comb_frac)

            # NG share of combustion component
            ng_keys = NG_SHARE_KEY.get(sector, ("other_ng_point","other_ng_low","other_ng_high"))
            ng_p = ng_row.get(ng_keys[0], 0.30)
            ng_l = ng_row.get(ng_keys[1], 0.20)
            ng_h = ng_row.get(ng_keys[2], 0.40)

            sector_records.append({
                "year": yr,
                "sector": sector,
                "alloc_total_mt":   alloc,
                "alloc_comb_mt":    alloc_comb,
                "alloc_proc_mt":    alloc_proc,
                "comb_frac":        comb_frac,
                "ng_share_point":   ng_p,
                "ng_share_low":     ng_l,
                "ng_share_high":    ng_h,
                "ng_co2_in_ets_point_mt": alloc_comb * ng_p,
                "ng_co2_in_ets_low_mt":   alloc_comb * ng_l,
                "ng_co2_in_ets_high_mt":  alloc_comb * ng_h,
                "extrapolated": yr not in ("2020", "2021"),
            })

    sector_df = pd.DataFrame(sector_records)

    # Aggregate to year-level
    agg = sector_df.groupby("year").agg(
        ets_total_mt=("alloc_total_mt", "sum"),
        ets_comb_mt =("alloc_comb_mt",  "sum"),
        ets_proc_mt =("alloc_proc_mt",  "sum"),
        ng_in_ets_point_mt=("ng_co2_in_ets_point_mt", "sum"),
        ng_in_ets_low_mt  =("ng_co2_in_ets_low_mt",   "sum"),
        ng_in_ets_high_mt =("ng_co2_in_ets_high_mt",  "sum"),
    ).reset_index().set_index("year")

    for yr in ETS_YEARS:
        r = agg.loc[yr]
        log.info("  ETS %s: total=%.1f, comb=%.1f, proc=%.1f, NG_in_ETS=%.1f Mt",
                 yr, r["ets_total_mt"], r["ets_comb_mt"], r["ets_proc_mt"], r["ng_in_ets_point_mt"])

    return agg, sector_df


# ══════════════════════════════════════════════════════════════════════════════
# C. OVERLAP
# ══════════════════════════════════════════════════════════════════════════════

def estimate_overlap(ets_agg, ets_sector_df):
    """
    Overlap = ETS combustion coverage × (1 - NG share)
            = ETS combustion coverage − NG CO2 within ETS

    Process CO2 (2A/2B/2C) in ETS is outside carbon tax scope → not overlap.
    NG combustion in ETS is outside carbon tax scope → not overlap.
    Only non-NG combustion CO2 covered by ETS = overlap.

    Uncertainty: propagated from NG share low/high bounds.
    """
    log.info("Estimating overlap 2020-2023...")
    records = []
    for yr in OVERLAP_YEARS:
        r = ets_agg.loc[yr]
        comb_mt      = r["ets_comb_mt"]
        ng_p, ng_l, ng_h = r["ng_in_ets_point_mt"], r["ng_in_ets_low_mt"], r["ng_in_ets_high_mt"]

        # Overlap = combustion − NG combustion
        overlap_point = comb_mt - ng_p
        overlap_high  = comb_mt - ng_l   # less NG subtracted → more overlap
        overlap_low   = comb_mt - ng_h   # more NG subtracted → less overlap

        records.append({
            "year":                yr,
            "ets_total_mt":        r["ets_total_mt"],
            "ets_comb_mt":         comb_mt,
            "ets_proc_mt":         r["ets_proc_mt"],
            "ng_in_ets_point_mt":  ng_p,
            "overlap_point_mt":    overlap_point,
            "overlap_low_mt":      max(0, overlap_low),
            "overlap_high_mt":     overlap_high,
            "overlap_pct_of_ets":  overlap_point / r["ets_total_mt"] if r["ets_total_mt"] > 0 else np.nan,
        })
        log.info("  Overlap %s: ETS=%.1f, comb=%.1f, NG_in_ETS=%.1f → overlap=%.1f [%.1f–%.1f] Mt",
                 yr, r["ets_total_mt"], comb_mt, ng_p, overlap_point, max(0,overlap_low), overlap_high)

    return pd.DataFrame(records).set_index("year")


# ══════════════════════════════════════════════════════════════════════════════
# D. DEDUPLICATED SUMMARY
# ══════════════════════════════════════════════════════════════════════════════

def build_summary(ctax_df, ets_df, overlap_df, national_totals):
    """
    Combine carbon tax, ETS, and overlap into a single summary table.

    Two share series computed per instrument:
      Absolute share: instrument coverage / national GHG total (including double-counted overlap)
      Net share:      deduplicated joint coverage / national GHG total (overlap subtracted once)

    Denominator: INECC 'EMISIONES Sin UTCUTS' all-gas CO2e.
    Numerators: CO2-only (combustion + process). Shares are conservative by construction.
    """
    log.info("Building summary table...")
    records = []

    for yr in OVERLAP_YEARS:
        national = national_totals.get(yr, np.nan)
        ct  = ctax_df.loc[yr]
        ets = ets_df.loc[yr]
        ov  = overlap_df.loc[yr]

        ctax_p = ct["ctax_coverage_point_mt"]
        ctax_l = ct["ctax_coverage_low_mt"]
        ctax_h = ct["ctax_coverage_high_mt"]
        ets_p  = ets["ets_total_mt"]
        ov_p   = ov["overlap_point_mt"]
        ov_l   = ov["overlap_low_mt"]
        ov_h   = ov["overlap_high_mt"]

        # Deduplicated (net) combined coverage
        dedup_p = ctax_p + ets_p - ov_p
        dedup_l = ctax_l + ets_p - ov_h   # low coverage: low ctax + high overlap subtracted
        dedup_h = ctax_h + ets_p - ov_l   # high coverage: high ctax + low overlap subtracted

        def share(val):
            return val / national if pd.notna(national) and national > 0 else np.nan

        records.append({
            "year":                        yr,
            "national_ghg_mt":             national,
            # Absolute volumes
            "ctax_point_mt":               ctax_p,
            "ctax_low_mt":                 ctax_l,
            "ctax_high_mt":                ctax_h,
            "ets_point_mt":                ets_p,
            "overlap_point_mt":            ov_p,
            "overlap_low_mt":              ov_l,
            "overlap_high_mt":             ov_h,
            "dedup_point_mt":              dedup_p,
            "dedup_low_mt":                dedup_l,
            "dedup_high_mt":               dedup_h,
            # Absolute shares (pre-deduplication — each instrument counted independently)
            "ctax_abs_share":              share(ctax_p),
            "ets_abs_share":               share(ets_p),
            "overlap_abs_share":           share(ov_p),
            # Net shares (post-deduplication)
            "ctax_net_share":              share(ctax_p - ov_p),  # ctax-only portion
            "ets_net_share":               share(ets_p  - ov_p),  # ets-only portion
            "overlap_net_share":           share(ov_p),           # shared portion (counted once)
            "combined_net_share_point":    share(dedup_p),
            "combined_net_share_low":      share(dedup_l),
            "combined_net_share_high":     share(dedup_h),
            # Auxiliary
            "overlap_pct_of_ets":          ov["overlap_pct_of_ets"],
        })

    return pd.DataFrame(records).set_index("year")


def build_ctax_only_shares(ctax_df, national_totals):
    """
    Coverage shares for carbon tax across full 2014-2024 period.
    For 2014-2019 (pre-ETS): net share = absolute share (no overlap possible).
    For 2020-2024: absolute share only (net/overlap computed in build_summary).
    """
    log.info("Building carbon tax coverage shares 2014-2024...")
    records = []
    for yr in CTAX_YEARS:
        national = national_totals.get(yr, np.nan)
        ct = ctax_df.loc[yr]
        ctax_p = ct["ctax_coverage_point_mt"]
        ctax_l = ct["ctax_coverage_low_mt"]
        ctax_h = ct["ctax_coverage_high_mt"]
        def share(val):
            return val / national if pd.notna(national) and national > 0 else np.nan
        records.append({
            "year":                    yr,
            "national_ghg_mt":         national,
            "ctax_coverage_point_mt":  ctax_p,
            "ctax_coverage_low_mt":    ctax_l,
            "ctax_coverage_high_mt":   ctax_h,
            "ctax_abs_share_point":    share(ctax_p),
            "ctax_abs_share_low":      share(ctax_l),
            "ctax_abs_share_high":     share(ctax_h),
        })
    return pd.DataFrame(records).set_index("year")


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════

def main():
    log.info("="*60)
    log.info("02_estimate.py — Mexico carbon overlap estimation")
    log.info("="*60)

    # Load cleaned data
    inecc      = pd.read_csv(PROC / "clean_inecc_panel.csv",  index_col="year")
    ng_shares  = pd.read_csv(PROC / "clean_ng_shares.csv",    index_col="year")

    # Load national GHG totals (Sin UTCUTS, all-gas CO2e)
    national_totals = load_national_totals()

    # A. Carbon tax coverage (2014-2024)
    ctax_df = estimate_carbon_tax_coverage(inecc, ng_shares)
    ctax_df.to_csv(OUT / "results_carbon_tax_coverage.csv")
    log.info("Saved: results_carbon_tax_coverage.csv")

    # B. ETS coverage (2020-2024)
    ets_agg, ets_sector_df = estimate_ets_coverage(inecc, ng_shares)
    ets_agg.to_csv(OUT / "results_ets_coverage.csv")
    ets_sector_df.to_csv(OUT / "results_ets_sector_detail.csv", index=False)
    log.info("Saved: results_ets_coverage.csv + results_ets_sector_detail.csv")

    # C. Overlap (2020-2023)
    overlap_df = estimate_overlap(ets_agg, ets_sector_df)
    overlap_df.to_csv(OUT / "results_overlap.csv")
    log.info("Saved: results_overlap.csv")

    # D. Summary with absolute and net coverage shares (2020-2023)
    summary_df = build_summary(ctax_df, ets_agg, overlap_df, national_totals)
    summary_df.to_csv(OUT / "results_summary.csv")
    log.info("Saved: results_summary.csv")

    # E. Carbon tax shares across full 2014-2024 period
    ctax_shares_df = build_ctax_only_shares(ctax_df, national_totals)
    ctax_shares_df.to_csv(OUT / "results_ctax_shares_full.csv")
    log.info("Saved: results_ctax_shares_full.csv")

    log.info("="*60)
    log.info("02_estimate.py complete.")
    log.info("="*60)

    # Print key results
    log.info("\n=== CARBON TAX COVERAGE SHARES 2014-2024 ===")
    print(ctax_shares_df[["national_ghg_mt","ctax_coverage_point_mt",
                           "ctax_abs_share_point"]].round(3).to_string())

    log.info("\n=== OVERLAP PERIOD SUMMARY 2020-2023 ===")
    cols = ["national_ghg_mt","ctax_point_mt","ets_point_mt","overlap_point_mt",
            "ctax_abs_share","ets_abs_share","overlap_abs_share","combined_net_share_point",
            "combined_net_share_low","combined_net_share_high"]
    print(summary_df[cols].round(3).to_string())

if __name__ == "__main__":
    main()
