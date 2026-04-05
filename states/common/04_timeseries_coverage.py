#!/usr/bin/env python3
"""
04_timeseries_coverage.py — Compute annual coverage for all Mexico state-level CPIs.

Methodology: Anchored Extrapolation
  emissions(sector, year) = inventory(sector, inv_year) × [EDGAR(sector, year) / EDGAR(sector, inv_year)]
  EDGAR provides the growth rate; the inventory provides the level.

Key assumptions documented here:
  1. S/F/E share parameters (NG shares, ETS threshold coverage) held static across all years
  2. EDGAR growth rates applied at the 13-category level, not individual EDGAR sector level
  3. E instrument (Mexico Pilot ETS) inactive before 2020 — Zacatecas 2017-2019 = two-instrument overlap
  4. All totals exclude LULUCF (3.B) and IDE (5.A)
  5. Baja California: 100% S⊂F overlap, net additional = 0
  6. CDMX: no EDGAR growth rate applied due to spatial resolution inadequacy (11 grid cells)
  7. Colima: EDGAR direct due to 19-year inventory gap (2005 inventory)
  8. San Luis Potosí: inventory is 2007-2014 annual average; EDGAR 2014 used as anchor
"""

import os
import sys
import pandas as pd
import numpy as np

# ============================================================
# Paths
# ============================================================
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
STATES_DIR = os.path.dirname(SCRIPT_DIR)

EDGAR_TS_PATH = os.path.join(SCRIPT_DIR, "edgar_state_timeseries.csv")
EDGAR_INV_PATH = os.path.join(SCRIPT_DIR, "edgar_inventory_comparison_years.csv")

# ============================================================
# EDGAR sector → 13 comparison categories
# ============================================================
EDGAR_TO_CAT = {
    'ENE': 'Electricity', 'REF_TRF': 'Refining', 'IND': 'Manufacturing',
    'TRO': 'Transport', 'TNR_Aviation_CDS': 'Transport', 'TNR_Aviation_CRS': 'Transport',
    'TNR_Aviation_LTO': 'Transport', 'TNR_Other': 'Transport', 'TNR_Ship': 'Transport',
    'RCO': 'Buildings', 'PRO_FFF': 'Fugitive',
    'NMM': 'IPPU_minerals', 'CHE': 'IPPU_chemicals',
    'IRO': 'IPPU_metals', 'NFE': 'IPPU_metals',
    'NEU': 'IPPU_products', 'PRU_SOL': 'IPPU_products',
    'ENF': 'Livestock', 'MNM': 'Livestock',
    'AGS': 'Cropland', 'AWB': 'Cropland', 'N2O': 'Cropland',
    'SWD_LDF': 'Waste', 'SWD_INC': 'Waste', 'WWT': 'Waste',
}

ALL_CATEGORIES = [
    'Electricity', 'Refining', 'Manufacturing', 'Transport', 'Buildings',
    'Fugitive', 'IPPU_minerals', 'IPPU_chemicals', 'IPPU_metals',
    'IPPU_products', 'Livestock', 'Cropland', 'Waste',
]

SEGMENTS = ['sfe', 'se', 'sf', 's_only', 'fe', 'f_only', 'e_only', 'uncovered']


def ipcc_to_category(code):
    """Map IPCC 2006 code string to one of 13 comparison categories."""
    c = str(code).strip().upper().replace('.', '')
    # Specific prefix matching (order matters)
    if c.startswith('1A1A') or c == '1A1':
        return 'Electricity'
    if c.startswith('1A1B'):
        return 'Refining'
    if c.startswith('1A1C'):
        return 'Electricity'
    if c.startswith('1A1') and not c.startswith('1A1A') and not c.startswith('1A1B') and not c.startswith('1A1C'):
        return 'Electricity'
    if c.startswith('1A2'):
        return 'Manufacturing'
    if c.startswith('1A3'):
        return 'Transport'
    if c.startswith('1A4') or c.startswith('1A5') or c.startswith('1AB'):
        return 'Buildings'
    if c.startswith('1B'):
        return 'Fugitive'
    if c.startswith('2A'):
        return 'IPPU_minerals'
    if c.startswith('2B'):
        return 'IPPU_chemicals'
    if c.startswith('2C'):
        return 'IPPU_metals'
    if c.startswith('2D') or c.startswith('2F') or c.startswith('2G'):
        return 'IPPU_products'
    if c.startswith('3A'):
        return 'Livestock'
    if c.startswith('3B'):
        return 'LULUCF'
    if c.startswith('3C') or c.startswith('3X'):
        return 'Cropland'
    if c.startswith('4') or c.startswith('4X'):
        return 'Waste'
    if c.startswith('5'):
        return 'IDE'
    return None


def sector_group_to_category(sg):
    """Map sector_group labels used in some inventories to categories."""
    sg = str(sg).lower().strip()
    mapping = {
        'electricity_generation': 'Electricity',
        'petroleum_refining': 'Refining',
        'manufacturing': 'Manufacturing',
        'transport': 'Transport',
        'commercial': 'Buildings', 'residential': 'Buildings',
        'other_energy': 'Buildings', 'non_specified': 'Buildings',
        'ag_combustion': 'Buildings',
        'fugitive': 'Fugitive', 'fugitive_oil_gas': 'Fugitive',
        'ippu_minerals': 'IPPU_minerals', 'ippu_caliza': 'IPPU_minerals',
        'ippu_hfcs': 'IPPU_products', 'ippu_hfc': 'IPPU_products',
        'ippu_negro_humo': 'IPPU_chemicals',
        'ippu_metalurgia': 'IPPU_metals', 'ippu_metals': 'IPPU_metals',
        'ippu_quimica': 'IPPU_chemicals',
        'ippu_cemento': 'IPPU_minerals',
        'ippu_automotriz': 'IPPU_products',
        'ippu_celulosa': 'IPPU_products',
        'ippu_vidrio': 'IPPU_minerals',
        'ippu_otras': 'IPPU_products',
        'afolu': 'Livestock', 'afolu_livestock': 'Livestock',
        'afolu_agriculture': 'Cropland', 'afolu_burning': 'Cropland',
        'afolu_fire': 'Cropland', 'afolu_land_use': 'LULUCF',
        'waste': 'Waste', 'waste_wastewater': 'Waste',
        'biogenic': None,
    }
    return mapping.get(sg)


# ============================================================
# CPI definitions
# ============================================================
CPI_DEFS = [
    {'unique_id': 'Tax_MX_ZA', 'cpi_name': 'Zacatecas carbon tax',
     'state': 'Zacatecas', 'state_dir': 'zacatecas', 'inv_year': None,
     's_active': 2017, 'method': 'edgar_direct'},
    {'unique_id': 'Tax_MX_BC', 'cpi_name': 'Baja California carbon tax',
     'state': 'Baja California', 'state_dir': None, 'inv_year': None,
     's_active': 2020, 'method': 'edgar_direct_bc'},
    {'unique_id': 'Tax_MX_Queretaro', 'cpi_name': 'Querétaro carbon tax',
     'state': 'Querétaro', 'state_dir': 'queretaro', 'inv_year': 2021,
     's_active': 2022, 'method': 'inventory_anchored'},
    {'unique_id': 'Tax_MX_SoMexico', 'cpi_name': 'Estado de México carbon tax',
     'state': 'Estado de México', 'state_dir': 'estado_de_mexico', 'inv_year': 2022,
     's_active': 2022, 'method': 'inventory_anchored'},
    {'unique_id': 'Tax_MX_TA', 'cpi_name': 'Tamaulipas carbon tax',
     'state': 'Tamaulipas', 'state_dir': 'tamaulipas', 'inv_year': 2013,
     's_active': 2022, 'method': 'inventory_anchored'},
    {'unique_id': 'Tax_MX_Yucatan', 'cpi_name': 'Yucatán carbon tax',
     'state': 'Yucatán', 'state_dir': 'yucatan', 'inv_year': 2023,
     's_active': 2022, 'method': 'inventory_anchored'},
    {'unique_id': 'Tax_MX_Guanajuato', 'cpi_name': 'Guanajuato carbon tax',
     'state': 'Guanajuato', 'state_dir': 'guanajuato', 'inv_year': 2013,
     's_active': 2023, 'method': 'inventory_anchored'},
    {'unique_id': 'Tax_MX_Durango', 'cpi_name': 'Durango carbon tax',
     'state': 'Durango', 'state_dir': 'durango', 'inv_year': 2022,
     's_active': 2024, 'method': 'inventory_anchored'},
    {'unique_id': 'Tax_MX_Colima', 'cpi_name': 'Colima carbon tax',
     'state': 'Colima', 'state_dir': 'colima', 'inv_year': None,
     's_active': 2025, 'method': 'edgar_direct_colima'},
    {'unique_id': 'Tax_MX_MC', 'cpi_name': 'CDMX carbon tax',
     'state': 'CDMX', 'state_dir': 'cdmx', 'inv_year': 2020,
     's_active': 2025, 'method': 'inventory_static'},
    {'unique_id': 'Tax_MX_MO', 'cpi_name': 'Morelos carbon tax',
     'state': 'Morelos', 'state_dir': 'morelos', 'inv_year': 2014,
     's_active': 2025, 'method': 'inventory_anchored'},
    {'unique_id': 'Tax_MX_SLP', 'cpi_name': 'San Luis Potosí carbon tax',
     'state': 'San Luis Potosí', 'state_dir': 'sanluispotosi', 'inv_year': 2014,
     's_active': 2025, 'method': 'inventory_anchored'},
]

# ============================================================
# EDGAR data loading
# ============================================================

def load_edgar():
    """Load and combine EDGAR timeseries + inventory comparison data."""
    ts = pd.read_csv(EDGAR_TS_PATH)
    inv = pd.read_csv(EDGAR_INV_PATH)
    edgar = pd.concat([ts, inv], ignore_index=True)
    # Drop excluded sectors
    edgar = edgar[~edgar['edgar_sector'].isin(['IDE'])]
    # Map to categories
    edgar['category'] = edgar['edgar_sector'].map(EDGAR_TO_CAT)
    edgar = edgar.dropna(subset=['category'])
    return edgar


def edgar_category_by_year(edgar, state_name):
    """Sum EDGAR emissions by category and year for a given state."""
    st = edgar[edgar['state'] == state_name].copy()
    return st.groupby(['category', 'year'])['KtCO2e'].sum().reset_index()


def compute_growth(edgar, state_name, inv_year, target_years):
    """Compute growth rate per category: EDGAR(year)/EDGAR(inv_year).
    Returns dict: {(category, year): growth_rate}
    """
    cat_yr = edgar_category_by_year(edgar, state_name)
    anchor = cat_yr[cat_yr['year'] == inv_year].set_index('category')['KtCO2e']
    result = {}
    for year in target_years:
        yr_data = cat_yr[cat_yr['year'] == year].set_index('category')['KtCO2e']
        for cat in ALL_CATEGORIES:
            a = anchor.get(cat, 0.0)
            t = yr_data.get(cat, 0.0)
            if a > 0:
                result[(cat, year)] = t / a
            else:
                result[(cat, year)] = 1.0
    return result


# ============================================================
# State data loaders — produce per-category segment DataFrames
# ============================================================

def _make_seg_row(cat, total, sfe, se, sf, s_only, fe, f_only, e_only, uncov):
    return {'category': cat, 'total': total, 'sfe': sfe, 'se': se, 'sf': sf,
            's_only': s_only, 'fe': fe, 'f_only': f_only, 'e_only': e_only,
            'uncovered': uncov}


def _agg_to_categories(rows):
    """Aggregate list of segment dicts by category."""
    df = pd.DataFrame(rows)
    if df.empty:
        return df
    return df.groupby('category')[['total'] + SEGMENTS].sum().reset_index()


def load_estado_de_mexico():
    """EdoMex: overlap_sectors.csv with s_share/f_share/e_share in KtCO2e."""
    path = os.path.join(STATES_DIR, 'estado_de_mexico', 'data', 'processed',
                        'estado_de_mexico_overlap_sectors.csv')
    df = pd.read_csv(path)
    rows = []
    for _, r in df.iterrows():
        cat = ipcc_to_category(r['ipcc_2006'])
        if cat in ('LULUCF', 'IDE') or cat is None:
            continue
        total = r['central_KtCO2e']
        rows.append(_make_seg_row(
            cat, total, r['S∩F∩E'], r['S∩E_only'], r['S∩F_only'],
            r['S_only'], r['F∩E_only'], r['F_only'], r['E_only'], r['Uncovered']))
    return _agg_to_categories(rows)


def load_zacatecas():
    """Zacatecas: overlap_sectors.csv with edgar_sector keys, KtCO2e."""
    path = os.path.join(STATES_DIR, 'zacatecas', 'data', 'processed',
                        'zacatecas_overlap_sectors.csv')
    df = pd.read_csv(path)
    rows = []
    for _, r in df.iterrows():
        cat = EDGAR_TO_CAT.get(r['edgar_sector'])
        if cat is None:
            continue
        total = r['central_KtCO2e']
        rows.append(_make_seg_row(
            cat, total, r['S∩F∩E'], r['S∩E_only'], r['S∩F_only'],
            r['S_only'], r['F∩E_only'], r['F_only'], r['E_only'], r['Uncovered']))
    return _agg_to_categories(rows)


def _load_tax_scope_standard(state_dir, filename):
    """Load states with tax_scope format: in_S, f_frac_central, e_frac_central, segment columns.
    Units are GgCO2e = KtCO2e."""
    path = os.path.join(STATES_DIR, state_dir, 'data', 'processed', filename)
    df = pd.read_csv(path)
    rows = []
    # Determine the emissions column
    if 'emissions_GgCO2e' in df.columns:
        em_col = 'emissions_GgCO2e'
    elif 'total_GgCO2e' in df.columns:
        em_col = 'total_GgCO2e'
    else:
        em_col = 'emissions_GgCO2e'
    # Determine the IPCC code column
    ipcc_col = 'ipcc_code'
    if ipcc_col not in df.columns:
        ipcc_col = 'ipcc_sector'
    for _, r in df.iterrows():
        cat = ipcc_to_category(r[ipcc_col])
        if cat is None or cat in ('LULUCF', 'IDE'):
            continue
        # Also try sector_group if ipcc doesn't map
        if cat is None:
            sg = r.get('sector_group', '')
            cat = sector_group_to_category(sg)
            if cat is None or cat in ('LULUCF', 'IDE'):
                continue
        total = r[em_col]
        if pd.isna(total) or total == 0:
            continue
        rows.append(_make_seg_row(
            cat, total,
            r.get('S_F_E_central', 0.0), r.get('S_E_only_central', 0.0),
            r.get('S_F_only_central', 0.0), r.get('S_only_central', 0.0),
            r.get('F_E_only_central', 0.0), r.get('F_only_central', 0.0),
            r.get('E_only_central', 0.0), r.get('uncovered_central', 0.0)))
    return _agg_to_categories(rows)


def load_queretaro():
    return _load_tax_scope_standard('queretaro', 'queretaro_tax_scope_2021.csv')


def load_durango():
    return _load_tax_scope_standard('durango', 'durango_tax_scope_2022.csv')


def load_morelos():
    """Morelos: tax_scope with ipcc_sector column, total_GgCO2e, segment columns."""
    path = os.path.join(STATES_DIR, 'morelos', 'data', 'processed',
                        'morelos_tax_scope_2014.csv')
    df = pd.read_csv(path)
    # Morelos ipcc_sector uses descriptive labels; map them to 13 categories
    morelos_cat_map = {
        'manufacturing_automotive': 'Manufacturing',
        'manufacturing_food_bev': 'Manufacturing',
        'manufacturing_electrical': 'Manufacturing',
        'manufacturing_pulp_paper': 'Manufacturing',
        'manufacturing_petro_products': 'Manufacturing',
        'manufacturing_textiles': 'Manufacturing',
        'manufacturing_metals': 'IPPU_metals',
        'manufacturing_nonmet_minerals': 'Manufacturing',
        'manufacturing_chemical': 'IPPU_chemicals',
        'manufacturing_plastics': 'Manufacturing',
        'manufacturing_petrochem': 'Manufacturing',
        'manufacturing_other_small': 'Manufacturing',
        'industrial_process_cement': 'IPPU_minerals',
        'industrial_process_glass': 'IPPU_minerals',
        'area_agri_combustion': 'Buildings',
        'area_commercial': 'Buildings',
        'area_residential': 'Buildings',
        'area_industrial_small': 'Manufacturing',
        'afolu_livestock': 'Livestock',
        'afolu_burning': 'Cropland',
        'afolu_fire': 'Cropland',
        'waste_wastewater': 'Waste',
        'mobile_road': 'Transport',
        'mobile_nonroad': 'Transport',
    }
    rows = []
    for _, r in df.iterrows():
        ipcc_s = str(r.get('ipcc_sector', ''))
        cat = morelos_cat_map.get(ipcc_s)
        if cat is None:
            continue
        total = r.get('total_GgCO2e', 0.0)
        if pd.isna(total) or total == 0:
            continue
        rows.append(_make_seg_row(
            cat, total,
            r.get('S_F_E_central', 0.0), r.get('S_E_only_central', 0.0),
            r.get('S_F_only_central', 0.0), r.get('S_only_central', 0.0),
            r.get('F_E_only_central', 0.0) if 'F_E_only_central' in df.columns else 0.0,
            r.get('F_only_central', 0.0),
            r.get('E_only_central', 0.0) if 'E_only_central' in df.columns else 0.0,
            r.get('uncovered_central', 0.0)))
    return _agg_to_categories(rows)


def load_slp():
    """SLP: slp_tax_scope.csv with full segment columns. Units: GgCO2e = KtCO2e."""
    path = os.path.join(STATES_DIR, 'sanluispotosi', 'data', 'processed',
                        'slp_tax_scope.csv')
    df = pd.read_csv(path)
    rows = []
    for _, r in df.iterrows():
        sg = r.get('sector_group', '')
        cat = sector_group_to_category(sg)
        if cat is None or cat in ('LULUCF', 'IDE', None):
            continue
        total = r.get('emissions_GgCO2e', 0.0)
        if pd.isna(total) or total == 0:
            continue
        rows.append(_make_seg_row(
            cat, total,
            r.get('S_F_E_central', 0.0), r.get('S_E_only_central', 0.0),
            r.get('S_F_only_central', 0.0), r.get('S_only_central', 0.0),
            r.get('F_E_only_central', 0.0) if not pd.isna(r.get('F_E_only_central', np.nan)) else 0.0,
            r.get('F_only_central', 0.0), r.get('E_only_central', 0.0) if not pd.isna(r.get('E_only_central', np.nan)) else 0.0,
            r.get('uncovered_central', 0.0)))
    return _agg_to_categories(rows)


def load_tamaulipas():
    """Tamaulipas: scope_2025.csv. Scale segments from 2025 projection back to 2013 inventory."""
    path = os.path.join(STATES_DIR, 'tamaulipas', 'data', 'processed',
                        'tamaulipas_scope_2025.csv')
    df = pd.read_csv(path)
    # Only central scenario
    df = df[df['scenario'] == 'central'] if 'scenario' in df.columns else df
    rows = []
    for _, r in df.iterrows():
        sg = r.get('sector_group', '')
        cat = sector_group_to_category(sg)
        if cat is None:
            code = str(r.get('ipcc_code', ''))
            cat = ipcc_to_category(code)
        if cat is None or cat in ('LULUCF', 'IDE'):
            continue
        # Use 2013 inventory values (total_ar5), not projected
        inv_total = r.get('total_ar5', 0.0)
        if pd.isna(inv_total) or inv_total == 0:
            continue
        # Scale factor: base segments were computed on total_ar5_2025
        proj_total = r.get('total_ar5_2025', inv_total)
        if proj_total > 0:
            scale = inv_total / proj_total
        else:
            scale = 1.0
        rows.append(_make_seg_row(
            cat, inv_total,
            r.get('S_F_E', 0.0) * scale, r.get('S_E_only', 0.0) * scale,
            r.get('S_F_only', 0.0) * scale, r.get('S_only', 0.0) * scale,
            r.get('F_E_only', 0.0) * scale if not pd.isna(r.get('F_E_only', np.nan)) else 0.0,
            r.get('F_only', 0.0) * scale, r.get('E_only', 0.0) * scale if not pd.isna(r.get('E_only', np.nan)) else 0.0,
            r.get('uncovered', 0.0) * scale))
    return _agg_to_categories(rows)


def load_guanajuato():
    """Guanajuato: overlap_estimates.csv (S-scope) + sector_emissions_clean.csv (all)."""
    ol_path = os.path.join(STATES_DIR, 'guanajuato', 'data', 'processed',
                           'overlap_estimates.csv')
    se_path = os.path.join(STATES_DIR, 'guanajuato', 'data', 'processed',
                           'sector_emissions_clean.csv')
    ol = pd.read_csv(ol_path)
    se = pd.read_csv(se_path)
    # Central scenario only for overlap
    ol = ol[ol['scenario'] == 'central']

    rows = []
    # S-scope sectors from overlap
    subsector_cat_map = {
        'Industrias_energia': 'Electricity',
        'Industrias_manufactura': 'Manufacturing',
        'Ladrilleras': 'Manufacturing',
        'Emisiones_fugitivas': 'Fugitive',
        'Caprolactama': 'IPPU_chemicals',
        'Acido_nitrico': 'IPPU_chemicals',
        'HFC_RAC': 'IPPU_products',
    }
    s_subsectors = set()
    for _, r in ol.iterrows():
        sub = r['subsector']
        cat = subsector_cat_map.get(sub)
        if cat is None:
            continue
        s_subsectors.add(sub)
        total = r['total_S_scope_ggco2e']
        rows.append(_make_seg_row(
            cat, total,
            r.get('S_F_E', 0.0), r.get('S_E_only', 0.0),
            r.get('S_F_only', 0.0), r.get('S_only', 0.0),
            0.0, r.get('F_only_outside_S', 0.0), 0.0, 0.0))

    # Non-S sectors from sector_emissions
    se_cat_map = {
        'Autotransporte': 'Transport', 'Aviacion': 'Transport',
        'Maquinaria_construccion': 'Transport',
        'Combustion_agricola': 'Buildings',
        'Combustion_comercial': 'Buildings',
        'Combustion_residencial': 'Buildings',
    }
    # F share for non-S combustion sectors (buildings)
    BLDG_F_FRAC = 0.85
    for _, r in se.iterrows():
        sub = r['subsector']
        if sub in s_subsectors:
            continue
        cat_ipcc = ipcc_to_category(str(r.get('category_ipcc', '')))
        cat = se_cat_map.get(sub, cat_ipcc)
        if cat is None or cat in ('LULUCF', 'IDE'):
            continue
        total = r['total_ggco2e']
        if pd.isna(total) or total <= 0:
            continue
        if cat == 'Transport':
            rows.append(_make_seg_row(cat, total, 0, 0, 0, 0, 0, total, 0, 0))
        elif cat == 'Buildings':
            f_amt = total * BLDG_F_FRAC
            rows.append(_make_seg_row(cat, total, 0, 0, 0, 0, 0, f_amt, 0, total - f_amt))
        elif cat in ('Livestock', 'Cropland', 'Waste'):
            rows.append(_make_seg_row(cat, total, 0, 0, 0, 0, 0, 0, 0, total))
        else:
            rows.append(_make_seg_row(cat, total, 0, 0, 0, 0, 0, 0, 0, total))
    return _agg_to_categories(rows)


def load_yucatan(edgar):
    """Yucatan: Use inventory + tax_scope booleans + overlap_results aggregate.
    Derive effective f/e shares from aggregate data, distribute to categories."""
    inv_path = os.path.join(STATES_DIR, 'yucatan', 'data', 'processed',
                            'yucatan_inventory_2023.csv')
    ts_path = os.path.join(STATES_DIR, 'yucatan', 'data', 'processed',
                           'yucatan_tax_scope_2023.csv')
    ol_path = os.path.join(STATES_DIR, 'yucatan', 'data', 'processed',
                           'yucatan_overlap_results.csv')

    inv = pd.read_csv(inv_path)
    ts = pd.read_csv(ts_path)
    ol = pd.read_csv(ol_path)

    # Get aggregate segments from overlap_results (central)
    ol_dict = ol.set_index('segment')
    agg_sfe = ol_dict.loc['S_F_E', 'central_GgCO2e']
    agg_sf = ol_dict.loc['S_F', 'central_GgCO2e']
    agg_se = ol_dict.loc['S_E', 'central_GgCO2e']
    agg_s_only = ol_dict.loc['S_only', 'central_GgCO2e']
    agg_f_only = ol_dict.loc['F_only', 'central_GgCO2e']
    agg_uncov = ol_dict.loc['uncovered', 'central_GgCO2e']
    agg_fe = ol_dict.loc['F_E', 'central_GgCO2e'] if 'F_E' in ol_dict.index else 0.0
    agg_e_only = ol_dict.loc['E_only', 'central_GgCO2e'] if 'E_only' in ol_dict.index else 0.0

    # Get per-sector flags from tax_scope
    ts_flags = {}
    for _, r in ts.iterrows():
        code = r['ipcc_code']
        ts_flags[code] = {
            'in_S': bool(r['in_S']),
            'in_F': bool(r.get('in_F', False)),
            'in_E': bool(r.get('in_E_eligible', False)),
            'co2e': r['co2e_gg'],
        }

    # Group tax_scope sectors by (S, F, E) flags
    groups = {}  # (S,F,E) -> list of (ipcc_code, co2e, category)
    for code, info in ts_flags.items():
        cat = ipcc_to_category(code)
        if cat is None or cat in ('LULUCF', 'IDE'):
            continue
        key = (info['in_S'], info['in_F'], info['in_E'])
        groups.setdefault(key, []).append((code, info['co2e'], cat))

    # Compute group totals
    def group_total(key):
        return sum(x[1] for x in groups.get(key, []))

    ttt = group_total((True, True, True))
    ttf = group_total((True, True, False))
    tft = group_total((True, False, True))
    tff = group_total((True, False, False))

    # Derive effective f and e shares for F-eligible and E-eligible S-sectors
    f_eligible = ttt + ttf
    e_eligible = ttt + tft
    total_sf = agg_sfe + agg_sf  # total S∩F
    total_se = agg_sfe + agg_se  # total S∩E
    eff_f = total_sf / f_eligible if f_eligible > 0 else 0.0
    eff_e = total_se / e_eligible if e_eligible > 0 else 0.0

    # For each sector, compute segments using uniform effective shares within groups
    rows = []
    for key, sectors in groups.items():
        in_s, in_f, in_e = key
        for code, co2e, cat in sectors:
            if co2e <= 0:
                continue
            s = 1.0 if in_s else 0.0
            f = eff_f if in_f else 0.0
            e = eff_e if in_e else 0.0
            if not in_s:
                if in_f:
                    # Transport or other non-S F-only sectors
                    rows.append(_make_seg_row(cat, co2e, 0, 0, 0, 0, 0, co2e, 0, 0))
                else:
                    rows.append(_make_seg_row(cat, co2e, 0, 0, 0, 0, 0, 0, 0, co2e))
            else:
                sfe = co2e * f * e
                se = co2e * (1 - f) * e if in_e else 0.0
                sf = co2e * f * (1 - e) if in_f else 0.0
                s_only = co2e - sfe - se - sf
                rows.append(_make_seg_row(cat, co2e, sfe, se, sf, s_only, 0, 0, 0, 0))

    return _agg_to_categories(rows)


def load_cdmx():
    """CDMX: overlap_results.csv in tonnes, convert to KtCO2e. Aggregate only."""
    ol_path = os.path.join(STATES_DIR, 'cdmx', 'data', 'processed',
                           'cdmx_overlap_results.csv')
    ol = pd.read_csv(ol_path)
    ol_dict = ol.set_index('segment')
    # Convert from tonnes to Kt
    def val(seg):
        return ol_dict.loc[seg, 'central_tco2eq'] / 1000.0

    sfe = val('S_F_E')
    sf = val('S_F')
    se = val('S_E')
    s_only = val('S_only')
    fe = val('F_E') if 'F_E' in ol_dict.index else 0.0
    f_only = val('F_only')
    e_only = val('E_only') if 'E_only' in ol_dict.index else 0.0
    uncov = val('uncovered')
    total = sfe + sf + se + s_only + fe + f_only + e_only + uncov

    # CDMX has no per-category breakdown needed (inventory_static)
    # We map gross to a single "ALL" pseudo-category for simplicity
    # But for the output, we just output the totals directly
    rows = [_make_seg_row('ALL', total, sfe, se, sf, s_only, fe, f_only, e_only, uncov)]
    return pd.DataFrame(rows)


# ============================================================
# EDGAR-direct loaders
# ============================================================

def compute_edgar_direct_segments(edgar, state_name, year, overlap_sectors_df=None,
                                  coverage_pcts=None, bc_mode=False):
    """Compute segments from EDGAR data for a given state and year.

    For Zacatecas: uses overlap_sectors s/f/e shares.
    For Colima: uses aggregate coverage percentages.
    For Baja California: uses special S⊂F rule.
    """
    cat_yr = edgar_category_by_year(edgar, state_name)
    yr_data = cat_yr[cat_yr['year'] == year].set_index('category')['KtCO2e']

    if overlap_sectors_df is not None:
        # Zacatecas: apply s/f/e shares per sector
        st = edgar[(edgar['state'] == state_name) & (edgar['year'] == year)].copy()
        st['category'] = st['edgar_sector'].map(EDGAR_TO_CAT)
        st = st.dropna(subset=['category'])

        # Merge with overlap shares
        ol = overlap_sectors_df.set_index('edgar_sector')
        rows = []
        for _, r in st.iterrows():
            sec = r['edgar_sector']
            cat = r['category']
            em = r['KtCO2e']
            if sec in ol.index:
                s = ol.loc[sec, 's_share']
                f = ol.loc[sec, 'f_share']
                e = ol.loc[sec, 'e_share']
                sfe_v = ol.loc[sec, 'S∩F∩E'] / ol.loc[sec, 'central_KtCO2e'] * em if ol.loc[sec, 'central_KtCO2e'] > 0 else 0
                se_v = ol.loc[sec, 'S∩E_only'] / ol.loc[sec, 'central_KtCO2e'] * em if ol.loc[sec, 'central_KtCO2e'] > 0 else 0
                sf_v = ol.loc[sec, 'S∩F_only'] / ol.loc[sec, 'central_KtCO2e'] * em if ol.loc[sec, 'central_KtCO2e'] > 0 else 0
                s_only_v = ol.loc[sec, 'S_only'] / ol.loc[sec, 'central_KtCO2e'] * em if ol.loc[sec, 'central_KtCO2e'] > 0 else 0
                fe_v = ol.loc[sec, 'F∩E_only'] / ol.loc[sec, 'central_KtCO2e'] * em if ol.loc[sec, 'central_KtCO2e'] > 0 else 0
                f_only_v = ol.loc[sec, 'F_only'] / ol.loc[sec, 'central_KtCO2e'] * em if ol.loc[sec, 'central_KtCO2e'] > 0 else 0
                e_only_v = ol.loc[sec, 'E_only'] / ol.loc[sec, 'central_KtCO2e'] * em if ol.loc[sec, 'central_KtCO2e'] > 0 else 0
                uncov_v = ol.loc[sec, 'Uncovered'] / ol.loc[sec, 'central_KtCO2e'] * em if ol.loc[sec, 'central_KtCO2e'] > 0 else em
                rows.append(_make_seg_row(cat, em, sfe_v, se_v, sf_v, s_only_v,
                                          fe_v, f_only_v, e_only_v, uncov_v))
            else:
                rows.append(_make_seg_row(cat, em, 0, 0, 0, 0, 0, 0, 0, em))
        return _agg_to_categories(rows)

    elif bc_mode:
        # Baja California: S = transport + buildings, 100% S⊂F
        total_all = sum(yr_data.get(c, 0) for c in ALL_CATEGORIES)
        s_cats = ['Transport', 'Buildings']
        gross_S = sum(yr_data.get(c, 0) for c in s_cats)

        # F covers non-NG combustion across all sectors
        # Approximate F shares by sector type
        f_shares = {
            'Electricity': 0.20, 'Refining': 0.50, 'Manufacturing': 0.30,
            'Transport': 1.0, 'Buildings': 0.85, 'Fugitive': 0.0,
            'IPPU_minerals': 0.0, 'IPPU_chemicals': 0.0, 'IPPU_metals': 0.0,
            'IPPU_products': 0.0, 'Livestock': 0.0, 'Cropland': 0.0, 'Waste': 0.0,
        }
        # E shares (ETS for large emitters)
        e_shares = {
            'Electricity': 0.60, 'Refining': 0.50, 'Manufacturing': 0.40,
            'Transport': 0.0, 'Buildings': 0.0, 'Fugitive': 0.0,
            'IPPU_minerals': 0.50, 'IPPU_chemicals': 0.30, 'IPPU_metals': 0.40,
            'IPPU_products': 0.0, 'Livestock': 0.0, 'Cropland': 0.0, 'Waste': 0.0,
        }
        rows = []
        for cat in ALL_CATEGORIES:
            em = yr_data.get(cat, 0)
            if em <= 0:
                continue
            f_sh = f_shares.get(cat, 0)
            e_sh = e_shares.get(cat, 0)
            if cat in s_cats:
                # S covers these categories, 100% overlap with F
                s_sh = 1.0
                # All S emissions are in F (S⊂F), s_share = 1, f_share = 1 for S
                # S∩F = gross_S for this category
                sfe_v = em * f_sh * e_sh  # portion also in E
                sf_v = em * f_sh * (1 - e_sh)  # S∩F not E
                se_v = 0  # no S∩E without F (since S⊂F)
                s_only_v = em * (1 - f_sh)  # small portion not in F (NG)
                # Actually for BC, S covers transport+buildings.
                # Transport is 100% F. Buildings ~85% F.
                # S∩F∩E: transport has 0 E, buildings has 0 E → both 0
                sfe_v = 0.0
                sf_v = em * f_sh  # all F-covered S is S∩F only (no E)
                se_v = 0.0
                s_only_v = em * (1 - f_sh)
                rows.append(_make_seg_row(cat, em, sfe_v, se_v, sf_v, s_only_v, 0, 0, 0, 0))
            else:
                # Not in S
                fe_v = em * f_sh * e_sh
                f_only_v = em * f_sh * (1 - e_sh)
                e_only_v = em * (1 - f_sh) * e_sh
                uncov_v = em * (1 - f_sh) * (1 - e_sh)
                rows.append(_make_seg_row(cat, em, 0, 0, 0, 0, fe_v, f_only_v, e_only_v, uncov_v))
        return _agg_to_categories(rows)

    elif coverage_pcts is not None:
        # Colima: apply aggregate coverage percentages
        total_all = sum(yr_data.get(c, 0) for c in ALL_CATEGORIES)
        # S ⊂ F for Colima, S∩E from large stationary emitters
        sfe_pct = coverage_pcts['sfe_pct']
        sf_pct = coverage_pcts['sf_pct']
        f_only_pct = coverage_pcts['f_only_pct']
        uncov_pct = coverage_pcts['uncov_pct']

        sfe_v = total_all * sfe_pct
        sf_v = total_all * sf_pct
        f_only_v = total_all * f_only_pct
        uncov_v = total_all * uncov_pct

        # Distribute across categories proportionally
        rows = []
        # S sectors: Electricity + Manufacturing
        s_em = yr_data.get('Electricity', 0) + yr_data.get('Manufacturing', 0) + yr_data.get('Refining', 0)
        f_only_em = yr_data.get('Transport', 0) + yr_data.get('Buildings', 0) * 0.85
        uncov_em = total_all - s_em - f_only_em

        for cat in ALL_CATEGORIES:
            em = yr_data.get(cat, 0)
            if em <= 0:
                continue
            if cat in ('Electricity', 'Manufacturing', 'Refining'):
                frac = em / s_em if s_em > 0 else 0
                rows.append(_make_seg_row(cat, em, sfe_v * frac, 0, sf_v * frac, 0, 0, 0, 0, 0))
            elif cat in ('Transport',):
                rows.append(_make_seg_row(cat, em, 0, 0, 0, 0, 0, em, 0, 0))
            elif cat == 'Buildings':
                f_part = em * 0.85
                uncov_part = em * 0.15
                rows.append(_make_seg_row(cat, em, 0, 0, 0, 0, 0, f_part, 0, uncov_part))
            else:
                rows.append(_make_seg_row(cat, em, 0, 0, 0, 0, 0, 0, 0, em))
        return _agg_to_categories(rows)

    return pd.DataFrame()


# ============================================================
# Colima coverage percentages from overlap_estimates
# ============================================================
# From colima_overlap_estimates.csv 2025 central:
# gross_S = 3518.3, S∩F = 3508.3, S∩E = 1616.0, state_total ≈ 18137.0
# S ⊂ F: S∩F∩E = S∩E = 1616.0, S∩F_only = 3518.3 - 1616.0 = 1902.3
# gross_F = 9679.7, F_only = 9679.7 - 3518.3 = 6161.4
# uncovered = 18137.0 - 9679.7 = 8457.3
COLIMA_PCTS = {
    'sfe_pct': 1616.0 / 18137.0,
    'sf_pct': 1902.3 / 18137.0,
    'f_only_pct': 6161.4 / 18137.0,
    'uncov_pct': 8457.3 / 18137.0,
}


# ============================================================
# Core time-series computation
# ============================================================

def apply_growth_to_segments(base_segments, growth_rates, year):
    """Scale per-category segments by EDGAR growth rates.
    base_segments: DataFrame with category + segment columns (inventory year values).
    growth_rates: dict {(category, year): rate}.
    Returns scaled DataFrame.
    """
    result = base_segments.copy()
    for i, row in result.iterrows():
        cat = row['category']
        g = growth_rates.get((cat, year), 1.0)
        for col in ['total'] + SEGMENTS:
            result.at[i, col] = row[col] * g
    return result


def apply_e_activation(segments_df, year):
    """If year < 2020, collapse all E-related segments:
    sfe → sf, se → s_only, fe → f_only, e_only → uncovered.
    """
    if year >= 2020:
        return segments_df
    result = segments_df.copy()
    result['sf'] = result['sf'] + result['sfe']
    result['s_only'] = result['s_only'] + result['se']
    result['f_only'] = result['f_only'] + result['fe']
    result['uncovered'] = result['uncovered'] + result['e_only']
    result['sfe'] = 0.0
    result['se'] = 0.0
    result['fe'] = 0.0
    result['e_only'] = 0.0
    return result


def segments_to_output_row(segments_df, cpi_def, year, data_source):
    """Aggregate per-category segments into a single output row."""
    totals = segments_df[['total'] + SEGMENTS].sum()
    total_em = totals['total']
    gross_S = totals['sfe'] + totals['se'] + totals['sf'] + totals['s_only']
    gross_F = totals['sfe'] + totals['sf'] + totals['fe'] + totals['f_only']
    gross_E = totals['sfe'] + totals['se'] + totals['fe'] + totals['e_only']
    dedup = total_em - totals['uncovered']
    uncov = totals['uncovered']
    overlap_SFE = totals['sfe']
    overlap_SF = totals['sfe'] + totals['sf']
    overlap_SE = totals['sfe'] + totals['se']

    pct = lambda v: (v / total_em * 100) if total_em > 0 else 0.0

    return {
        'unique_id': cpi_def['unique_id'],
        'cpi_name': cpi_def['cpi_name'],
        'state': cpi_def['state'],
        'year': year,
        'total_emissions_KtCO2e': round(total_em, 2),
        'gross_S_KtCO2e': round(gross_S, 2),
        'gross_F_KtCO2e': round(gross_F, 2),
        'gross_E_KtCO2e': round(gross_E, 2),
        'dedup_union_KtCO2e': round(dedup, 2),
        'uncovered_KtCO2e': round(uncov, 2),
        'gross_S_pct': round(pct(gross_S), 2),
        'gross_F_pct': round(pct(gross_F), 2),
        'gross_E_pct': round(pct(gross_E), 2),
        'dedup_pct': round(pct(dedup), 2),
        'overlap_SF_KtCO2e': round(overlap_SF, 2),
        'overlap_SE_KtCO2e': round(overlap_SE, 2),
        'overlap_SFE_KtCO2e': round(overlap_SFE, 2),
        'data_source': data_source,
    }


# ============================================================
# Main
# ============================================================

def main():
    print("Loading EDGAR data...")
    edgar = load_edgar()

    # Available EDGAR years from timeseries
    edgar_ts_years = sorted(edgar[edgar['year'] >= 2017]['year'].unique())

    all_rows = []

    for cpi in CPI_DEFS:
        state = cpi['state']
        method = cpi['method']
        inv_year = cpi['inv_year']
        s_active = cpi['s_active']
        uid = cpi['unique_id']
        print(f"\n{'='*60}")
        print(f"Processing: {state} ({uid}), method={method}")

        # Determine target years
        if s_active <= 2024:
            start_yr = max(s_active, 2017)
            target_years = [y for y in edgar_ts_years if start_yr <= y <= 2024]
        else:
            # States starting 2025: baseline 2024 only
            target_years = [2024]

        # --------------------------------------------------------
        # EDGAR-direct methods
        # --------------------------------------------------------
        if method == 'edgar_direct':
            # Zacatecas
            ol_path = os.path.join(STATES_DIR, 'zacatecas', 'data', 'processed',
                                   'zacatecas_overlap_sectors.csv')
            ol_df = pd.read_csv(ol_path)
            for yr in target_years:
                seg = compute_edgar_direct_segments(edgar, state, yr, overlap_sectors_df=ol_df)
                if seg.empty:
                    continue
                seg = apply_e_activation(seg, yr)
                row = segments_to_output_row(seg, cpi, yr, 'edgar_direct')
                all_rows.append(row)
                print(f"  {yr}: total={row['total_emissions_KtCO2e']:.0f} Kt, "
                      f"S={row['gross_S_pct']:.1f}%, dedup={row['dedup_pct']:.1f}%")

        elif method == 'edgar_direct_bc':
            # Baja California: 2020-2021 only
            bc_years = [y for y in target_years if y <= 2021]
            for yr in bc_years:
                seg = compute_edgar_direct_segments(edgar, state, yr, bc_mode=True)
                if seg.empty:
                    continue
                seg = apply_e_activation(seg, yr)
                row = segments_to_output_row(seg, cpi, yr, 'edgar_direct')
                all_rows.append(row)
                print(f"  {yr}: total={row['total_emissions_KtCO2e']:.0f} Kt, "
                      f"S={row['gross_S_pct']:.1f}%, dedup={row['dedup_pct']:.1f}%")

        elif method == 'edgar_direct_colima':
            # Colima: EDGAR direct with aggregate coverage percentages
            for yr in target_years:
                seg = compute_edgar_direct_segments(
                    edgar, state, yr, coverage_pcts=COLIMA_PCTS)
                if seg.empty:
                    continue
                seg = apply_e_activation(seg, yr)
                row = segments_to_output_row(seg, cpi, yr, 'edgar_direct')
                all_rows.append(row)
                print(f"  {yr}: total={row['total_emissions_KtCO2e']:.0f} Kt, "
                      f"S={row['gross_S_pct']:.1f}%, dedup={row['dedup_pct']:.1f}%")

        # --------------------------------------------------------
        # Inventory-static: CDMX
        # --------------------------------------------------------
        elif method == 'inventory_static':
            seg = load_cdmx()
            # Output for 2024 baseline (= 2020 inventory, no growth)
            for yr in target_years:
                seg_yr = apply_e_activation(seg.copy(), yr)
                row = segments_to_output_row(seg_yr, cpi, yr, 'inventory_static')
                all_rows.append(row)
                print(f"  {yr}: total={row['total_emissions_KtCO2e']:.0f} Kt, "
                      f"S={row['gross_S_pct']:.1f}%, dedup={row['dedup_pct']:.1f}%")

        # --------------------------------------------------------
        # Inventory-anchored methods
        # --------------------------------------------------------
        elif method == 'inventory_anchored':
            # Load base-year per-category segments
            loaders = {
                'Querétaro': load_queretaro,
                'Estado de México': load_estado_de_mexico,
                'Tamaulipas': load_tamaulipas,
                'Yucatán': lambda: load_yucatan(edgar),
                'Guanajuato': load_guanajuato,
                'Durango': load_durango,
                'Morelos': load_morelos,
                'San Luis Potosí': load_slp,
            }
            loader = loaders.get(state)
            if loader is None:
                print(f"  WARNING: No loader for {state}")
                continue

            print(f"  Loading inventory data (inv_year={inv_year})...")
            base_seg = loader()
            if base_seg.empty:
                print(f"  WARNING: Empty segment data for {state}")
                continue

            base_total = base_seg['total'].sum()
            print(f"  Base year total: {base_total:.0f} KtCO2e, categories: {len(base_seg)}")

            # Compute growth rates from EDGAR
            growth = compute_growth(edgar, state, inv_year, target_years)

            for yr in target_years:
                seg_yr = apply_growth_to_segments(base_seg, growth, yr)
                seg_yr = apply_e_activation(seg_yr, yr)
                row = segments_to_output_row(seg_yr, cpi, yr, 'inventory_anchored')
                all_rows.append(row)
                print(f"  {yr}: total={row['total_emissions_KtCO2e']:.0f} Kt, "
                      f"S={row['gross_S_pct']:.1f}%, dedup={row['dedup_pct']:.1f}%")

    # ============================================================
    # Output 1: Master coverage CSV
    # ============================================================
    print(f"\n{'='*60}")
    print("Writing output files...")

    out_df = pd.DataFrame(all_rows)
    out_path = os.path.join(SCRIPT_DIR, 'coverage_timeseries.csv')
    out_df.to_csv(out_path, index=False)
    print(f"  -> {out_path} ({len(out_df)} rows)")

    # ============================================================
    # Output 2: Summary CSV — one row per CPI, latest year
    # ============================================================
    summary_rows = []
    for cpi in CPI_DEFS:
        uid = cpi['unique_id']
        cpi_rows = out_df[out_df['unique_id'] == uid]
        if cpi_rows.empty:
            continue
        latest = cpi_rows.loc[cpi_rows['year'].idxmax()]
        start_year = cpi['s_active']
        summary_rows.append({
            'unique_id': uid,
            'cpi_name': cpi['cpi_name'],
            'state': cpi['state'],
            'start_year': start_year,
            'latest_year': int(latest['year']),
            'latest_total_KtCO2e': latest['total_emissions_KtCO2e'],
            'latest_gross_S_KtCO2e': latest['gross_S_KtCO2e'],
            'latest_gross_S_pct': latest['gross_S_pct'],
            'latest_dedup_KtCO2e': latest['dedup_union_KtCO2e'],
            'latest_dedup_pct': latest['dedup_pct'],
            'data_source': latest['data_source'],
        })

    sum_df = pd.DataFrame(summary_rows)
    sum_path = os.path.join(SCRIPT_DIR, 'coverage_summary_by_cpi.csv')
    sum_df.to_csv(sum_path, index=False)
    print(f"  -> {sum_path} ({len(sum_df)} rows)")

    # ============================================================
    # Output 3: Console summary table
    # ============================================================
    print(f"\n{'='*70}")
    print(f"{'CPI':<26} {'Start':>5} {'Year':>4} {'Total Kt':>10} {'S%':>6} "
          f"{'F%':>6} {'E%':>6} {'Dedup%':>7} {'Source':<20}")
    print('-' * 70)
    for _, r in sum_df.iterrows():
        uid = r['unique_id']
        yr = r['latest_year']
        row_data = out_df[(out_df['unique_id'] == uid) & (out_df['year'] == yr)]
        if row_data.empty:
            continue
        rd = row_data.iloc[0]
        label = r['state'][:24]
        print(f"{label:<26} {r['start_year']:>5} {yr:>4} {rd['total_emissions_KtCO2e']:>10.0f} "
              f"{rd['gross_S_pct']:>5.1f}% {rd['gross_F_pct']:>5.1f}% "
              f"{rd['gross_E_pct']:>5.1f}% {rd['dedup_pct']:>6.1f}% "
              f"{rd['data_source']:<20}")
    print('=' * 70)


if __name__ == '__main__':
    main()
