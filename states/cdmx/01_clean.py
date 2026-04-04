"""
01_clean.py — CDMX Carbon Pricing Overlap Analysis
====================================================
Case: Mexico — CDMX state carbon tax × Federal IEPS × Mexico Pilot ETS
Estimation tier: Tier 3 (fuel-fraction for F, Pareto/threshold for ETS)
Base year: 2020 (Inventario de Emisiones ZMVM 2020, Sedema, published 2023)

Key assumptions:
- AR5 GWPs (CH4=28, N2O=265) — matches inventory methodology
- Fuel fractions for NG share computed from Annex Tables 67-69
  (CDMX-specific fuel consumption by sector)
- Industrial NG share ~99.5% of industrial stationary combustion (by energy)
- Commercial NG share ~96.8% of commercial stationary combustion (by energy)
- 2020 is a COVID-affected year; noted in methodology but used as-is
- Biogenic CO2 excluded per IPCC convention (inventory already excludes it)

Data sources:
- Inventario de Emisiones de la ZMVM 2020, Sedema (2023)
  CDMX-specific tables: Annex Table 9 (GHG by category), Table 2 (ZMVM entity)
  Fuel consumption: Annex Tables 67 (gas LP), 68 (gas natural), 69 (diesel/other)
  Facility counts: Annex Table 40, p.20 characteristics

Outputs:
- data/processed/cdmx_inventory_clean.csv
- data/processed/cdmx_fuel_fractions.csv
- data/processed/cdmx_validation_report.txt

Usage: python 01_clean.py
"""

import pandas as pd
import numpy as np
import os

# ── Paths ────────────────────────────────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_DIR    = os.path.join(SCRIPT_DIR, "data", "raw")
PROC_DIR   = os.path.join(SCRIPT_DIR, "data", "processed")
os.makedirs(PROC_DIR, exist_ok=True)

print("=" * 70)
print("CDMX 01_clean.py — Reading and processing 2020 inventory")
print("=" * 70)

# ── GWP constants (AR5) ─────────────────────────────────────────────────────
GWP_CH4 = 28
GWP_N2O = 265

# ── Known totals from Annex Table 9 (for validation) ────────────────────────
KNOWN = {
    'cdmx_total_co2eq':    19_888_435,
    'cdmx_co2_t':          19_097_213,
    'cdmx_ch4_t':              21_335,
    'cdmx_n2o_t':                 450,
    'cdmx_hfc_t':                  57,
    'puntuales_co2eq':        896_493,   # rounded from 896,492.52
    'area_co2eq':           5_629_620,   # rounded from 5,629,620.30
    'moviles_co2eq':       13_362_322,   # rounded from 13,362,321.85
}

# ── Energy conversion factors ────────────────────────────────────────────────
# Net calorific values from Balance Nacional de Energía (SENER, 2022)
# Used to convert volumetric fuel consumption to energy (PJ)
NCV = {
    'gas_natural_mj_per_m3':   37.83,   # 1 m3 NG ≈ 37.83 MJ (variable 35-39)
    'gas_lp_mj_per_m3':       26.10,    # 1 m3 gas LP ≈ 26.10 MJ
    'diesel_mj_per_m3':    36_276.0,    # 1 m3 diesel ≈ 36,276 MJ
    'carbon_veg_mj_per_t': 29_000.0,    # 1 t charcoal ≈ 29,000 MJ
    'lena_mj_per_t':       14_400.0,    # 1 t firewood ≈ 14,400 MJ
}

# ── CO2 emission factors (kg CO2 / TJ) from IPCC 2006 defaults ──────────────
EF_CO2 = {
    'gas_natural':  56_100,
    'gas_lp':       63_100,
    'diesel':       74_100,
    'carbon_veg':   30_000,    # biomass — biogenic, NOT counted
}


# ═══════════════════════════════════════════════════════════════════════════════
# STEP 1: Load and validate inventory
# ═══════════════════════════════════════════════════════════════════════════════
print("\n── Step 1: Loading inventory data ──")

inv = pd.read_csv(os.path.join(RAW_DIR, "cdmx_ghg_inventory_2020.csv"),
                  comment='#')
inv['hfc_t'] = inv['hfc_t'].fillna(0)
inv['co2_t'] = inv['co2_t'].fillna(0)
inv['ch4_t'] = inv['ch4_t'].fillna(0)
inv['n2o_t'] = inv['n2o_t'].fillna(0)

# Recompute CO2eq from individual gases for cross-check
inv['co2eq_check'] = (inv['co2_t']
                      + inv['ch4_t'] * GWP_CH4
                      + inv['n2o_t'] * GWP_N2O
                      + inv['hfc_t'] * GWP_CH4)  # placeholder — HFC GWPs vary

print(f"  Loaded {len(inv)} rows")

# Validate source-type subtotals
val_lines = []
for stype in ['PUNTUALES', 'AREA', 'MOVILES']:
    sub = inv[inv['source_type'] == stype]
    calc_co2eq = sub['co2eq_t'].sum()
    known_key = {'PUNTUALES': 'puntuales_co2eq',
                 'AREA': 'area_co2eq',
                 'MOVILES': 'moviles_co2eq'}[stype]
    known_val = KNOWN[known_key]
    pct_diff = abs(calc_co2eq - known_val) / known_val * 100
    status = "PASS" if pct_diff < 1.0 else "FAIL"
    line = (f"  {stype:12s}: extracted={calc_co2eq:>15,.1f}  "
            f"known={known_val:>15,d}  diff={pct_diff:.2f}%  [{status}]")
    print(line)
    val_lines.append(line)

# Grand total
total_co2eq = inv['co2eq_t'].sum()
total_co2   = inv['co2_t'].sum()
total_ch4   = inv['ch4_t'].sum()
total_n2o   = inv['n2o_t'].sum()
pct_total = abs(total_co2eq - KNOWN['cdmx_total_co2eq']) / KNOWN['cdmx_total_co2eq'] * 100
print(f"  TOTAL CO2eq: extracted={total_co2eq:>15,.1f}  "
      f"known={KNOWN['cdmx_total_co2eq']:>15,d}  diff={pct_total:.2f}%")
val_lines.append(f"  TOTAL: diff={pct_total:.2f}%")


# ═══════════════════════════════════════════════════════════════════════════════
# STEP 2: Assign analytical categories for overlap analysis
# ═══════════════════════════════════════════════════════════════════════════════
print("\n── Step 2: Assigning analytical categories ──")

def assign_analysis_category(row):
    """Map each inventory row to an analytical category for overlap."""
    st = row['source_type']
    cat = str(row['category'])
    sub = str(row.get('subcategory', ''))

    # Point sources — regulated industry and commercial
    if st == 'PUNTUALES':
        if 'Generación' in cat:
            return 'ELECTRICITY'
        elif 'Comercios' in cat:
            return 'COMMERCIAL_REG'
        elif 'Almacenamiento' in cat:
            return 'FUEL_STORAGE'
        else:
            return 'INDUSTRY_REG'

    # Area sources
    if st == 'AREA':
        if 'Combustión' in cat:
            if 'comercial' in sub.lower():
                return 'COMMERCIAL_UNREG'
            elif 'industria no regulada' in sub.lower():
                return 'INDUSTRY_UNREG'
            elif 'habitacional' in sub.lower():
                return 'RESIDENTIAL'
            elif 'agrícola' in sub.lower() or 'equipos agrícolas' in sub.lower():
                return 'AGRICULTURE_EQUIP'
            elif 'HCNQ' in sub:
                return 'FUGITIVE_LP'
            else:
                return 'COMBUSTION_OTHER'
        if 'Desechos' in cat:
            return 'WASTE'
        if 'Móviles no carreteros' in cat:
            if 'aeronaves' in sub.lower():
                return 'AVIATION'
            elif 'locomotoras' in sub.lower():
                return 'RAIL'
            elif 'maquinaria' in sub.lower():
                return 'CONSTRUCTION_EQUIP'
            elif 'terminales' in sub.lower():
                return 'BUS_TERMINALS'
            else:
                return 'NON_ROAD_OTHER'
        if 'Distribución' in cat or 'fugas' in cat.lower():
            return 'FUGITIVE_LP'
        if 'Agricultura' in cat:
            return 'AGRICULTURE'
        if 'Ganadería' in cat:
            return 'LIVESTOCK'
        if 'Construcción' in cat:
            return 'CONSTRUCTION'
        if 'Otras fuentes' in cat:
            if 'domésticas' in sub.lower():
                return 'RESIDENTIAL_OTHER'
            elif 'aires acondicionados' in sub.lower():
                return 'HFC_RESIDENTIAL'
            elif 'Asados' in sub.lower():
                return 'COMMERCIAL_INFORMAL'
            elif 'Ladrilleras' in sub.lower():
                return 'LADRILLERAS'
            else:
                return 'MISC_AREA'
        return 'OTHER_AREA'

    # Mobile sources — road transport
    if st == 'MOVILES':
        return 'ROAD_TRANSPORT'

    return 'UNCLASSIFIED'


inv['analysis_cat'] = inv.apply(assign_analysis_category, axis=1)

# Print category assignment summary
cat_summary = (inv.groupby('analysis_cat')['co2eq_t']
               .sum().sort_values(ascending=False))
print("  Category assignments (tCO2eq):")
for cat, val in cat_summary.items():
    print(f"    {cat:25s}  {val:>14,.1f}")


# ═══════════════════════════════════════════════════════════════════════════════
# STEP 3: Compute fuel fractions (NG share) by sector
# ═══════════════════════════════════════════════════════════════════════════════
print("\n── Step 3: Computing fuel fractions from energy data ──")

fuel = pd.read_csv(os.path.join(RAW_DIR, "cdmx_fuel_consumption_2020.csv"),
                   comment='#')

# Convert all fuels to energy (PJ)
def to_pj(row):
    f = row['fuel']
    v = row['volume']
    if f == 'gas_natural':
        return v * NCV['gas_natural_mj_per_m3'] / 1e9
    elif f == 'gas_lp':
        return v * NCV['gas_lp_mj_per_m3'] / 1e9
    elif f == 'diesel':
        return v * NCV['diesel_mj_per_m3'] / 1e9
    elif f == 'lena':
        return v * NCV['lena_mj_per_t'] / 1e9
    elif f == 'carbon_vegetal':
        return v * NCV['carbon_veg_mj_per_t'] / 1e9
    return 0

fuel['energy_pj'] = fuel.apply(to_pj, axis=1)

# Compute NG share by sector (fossil fuels only — exclude biogenic)
fracs = {}
for sector in ['industrial', 'comercios_servicios', 'residencial', 'transporte']:
    sub = fuel[fuel['sector'] == sector].copy()
    # Exclude biogenic fuels (leña, carbón vegetal) from fossil fraction calc
    fossil = sub[~sub['fuel'].isin(['lena', 'carbon_vegetal'])]
    total_fossil = fossil['energy_pj'].sum()
    ng = fossil[fossil['fuel'] == 'gas_natural']['energy_pj'].sum()
    ng_frac = ng / total_fossil if total_fossil > 0 else 0
    fracs[sector] = {
        'total_fossil_pj': total_fossil,
        'ng_pj': ng,
        'ng_fraction': ng_frac,
        'non_ng_fraction': 1 - ng_frac,
    }
    print(f"  {sector:25s}: NG={ng:.4f} PJ / total fossil={total_fossil:.4f} PJ → "
          f"NG share = {ng_frac:.3%}")

fuel_fracs = pd.DataFrame(fracs).T
fuel_fracs.index.name = 'sector'

# Key results:
# Industrial: NG ~99.5% (NG 54.24 PJ vs LP 0.0017 PJ + diesel 0.315 PJ)
# Commercial: NG ~96.8% (NG 1.583 PJ vs LP 0.0034 PJ + charcoal ~biogenic)
# Residential: NG ~92.3% (NG 9.107 PJ vs LP 0.020 PJ)
# Transport: 100% non-NG (gas LP only in this sector)


# ═══════════════════════════════════════════════════════════════════════════════
# STEP 4: Save processed files
# ═══════════════════════════════════════════════════════════════════════════════
print("\n── Step 4: Saving processed files ──")

inv.to_csv(os.path.join(PROC_DIR, "cdmx_inventory_clean.csv"), index=False)
print(f"  Saved: cdmx_inventory_clean.csv ({len(inv)} rows)")

fuel_fracs.to_csv(os.path.join(PROC_DIR, "cdmx_fuel_fractions.csv"))
print(f"  Saved: cdmx_fuel_fractions.csv ({len(fuel_fracs)} rows)")

# Validation report
with open(os.path.join(PROC_DIR, "cdmx_validation_report.txt"), 'w') as f:
    f.write("CDMX GHG Inventory 2020 — Validation Report\n")
    f.write("=" * 50 + "\n\n")
    f.write("Source: Inventario de Emisiones ZMVM 2020, Annex Table 9\n")
    f.write("Entity: Ciudad de México (16 alcaldías)\n")
    f.write(f"Total CO2eq: {total_co2eq:,.1f} tCO2eq\n")
    f.write(f"Known total: {KNOWN['cdmx_total_co2eq']:,d} tCO2eq\n")
    f.write(f"Difference: {pct_total:.2f}%\n\n")
    f.write("Subtotal validation:\n")
    for line in val_lines:
        f.write(line + "\n")
    f.write("\n\nFuel fractions (NG share of fossil combustion):\n")
    for sector, data in fracs.items():
        f.write(f"  {sector}: NG = {data['ng_fraction']:.3%}\n")
    f.write("\nNotes:\n")
    f.write("- 2020 is a COVID-affected year (GDP fell 5-43% by sector)\n")
    f.write("- GWPs: AR5 (CH4=28, N2O=265)\n")
    f.write("- HFC GWPs vary by specific gas; inventory-reported CO2eq used directly\n")
print(f"  Saved: cdmx_validation_report.txt")

print("\n" + "=" * 70)
print("01_clean.py complete")
print("=" * 70)
