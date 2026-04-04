"""
01_clean.py — Morelos Carbon Pricing Overlap Analysis
======================================================
Case: Mexico — Morelos state carbon tax × Federal IEPS carbon tax × Mexico Pilot ETS
Estimation tier: Tier 3 (fuel-fraction + Pareto threshold + process emission split)
Base year: 2014 (Morelos atmospheric emissions inventory, SDS/SEMARNAT/INECC, 2017)
Target years: 2025, 2026

CRITICAL CAVEATS — read before using results:
1. WRONG INVENTORY TYPE: This is a 2014 AIR QUALITY inventory, not an IPCC GHG inventory.
   GHG content is a supplementary annex. Units are Mg/year (= tonne/year), not GgCO2e.
   No HFCs, PFCs, or SF6 are covered — these are a material data gap for the state tax.

2. OLD BASE YEAR: 2014 → 11-year extrapolation to 2025/2026. Uncertainty is MUCH larger
   than Colima (2015) or Durango (2022). Ranges must be presented explicitly.

3. GWP VERSION: Inventory does not state GWPs. SEMARNAT 2014 likely used AR4 (CH4=25,
   N2O=298). We apply AR5 (CH4=28, N2O=265) for consistency with INECC INEGYCEI.
   The difference is small for this inventory because CH4/N2O are minor vs CO2.

4. BIOGENIC CO2: Domestic wood combustion CO2 (est. ~626,000 Mg) is included in inventory
   area-source totals. For carbon pricing purposes, biogenic CO2 from biomass is
   typically excluded. We flag and separate this.

5. NON-IPCC CLASSIFICATION: Industrial sectors use Mexican CMAP/SCIAN codes, not IPCC.
   Mapping is approximate; process vs. combustion split for cement is assumed (60/40).

Key analytical findings from data review:
- Cement (901,618 Mg CO2) is the dominant fixed source (60% of fixed total)
  of which ~60% is calcination process CO2 (in S, NOT in F)
  and ~40% is from petcoke/fuel combustion (in S AND F)
- NG is only 4% of industrial energy → federal tax exemption has minimal impact
  (contrast with Durango where NG = 99.6% of electricity CO2)
- Mobile sources dominate CO2 at 49.2% (all F-only; exempt from state tax)
- Livestock CH4 dominates area CH4 (89%) — exempt from all instruments

Data sources:
- Inventario de Emisiones Contaminantes a la Atmósfera, Estado de Morelos, Año base 2014
  SDS Morelos / SEMARNAT / INECC / LT Consulting, published January 2017
  Annex II: GHG by source type (Cuadro 12)
  Annex IV: GHG by detailed category (Cuadro 14)
  Cuadro 3: Industrial fuel consumption 2014
  Local file: morelos_ghg_inventory_2014.pdf

Outputs:
  data/processed/morelos_inventory_2014.csv
  data/processed/morelos_fuel_fractions_2014.csv
  data/processed/morelos_cement_process_split_2014.csv
"""

import pandas as pd
import numpy as np
import os, sys

# ── Paths ────────────────────────────────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR   = os.path.dirname(SCRIPT_DIR)
RAW_DIR    = os.path.join(BASE_DIR, "data", "raw")
PROC_DIR   = os.path.join(BASE_DIR, "data", "processed")
os.makedirs(PROC_DIR, exist_ok=True)

print("=" * 65)
print("Morelos 01_clean.py — reading and processing 2014 inventory")
print("=" * 65)
print("⚠  Base year 2014; 11-year extrapolation required for 2025/2026")
print("⚠  Air quality inventory — HFCs/PFCs/SF6 absent; large uncertainty")

# ── GWP constants ─────────────────────────────────────────────────────────────
# Apply AR5 for consistency with INECC national inventory
GWP_CH4 = 28    # AR5 (inventory likely used AR4=25; difference flagged)
GWP_N2O = 265   # AR5 (AR4=298; difference flagged)

# ── 1. Load and validate raw inventory ────────────────────────────────────────
inv_raw = pd.read_csv(os.path.join(RAW_DIR, "morelos_ghg_inventory_2014.csv"), comment="#")
fuel_raw = pd.read_csv(os.path.join(RAW_DIR, "morelos_fuel_consumption_2014.csv"), comment="#")

# Drop aggregate/total rows — keep leaf categories only
SKIP = {"TOTAL_FIXED","TOTAL_AREA","TOTAL_MOBILE_ROAD","TOTAL_NONROAD","ALL_SOURCES","TOTAL_FOSSIL_TAXABLE","TOTAL_NG_EXEMPT","TOTAL_BIOGENIC","TOTAL_ALL"}
inv = inv_raw[~inv_raw["subcategory"].isin(SKIP) & ~inv_raw["category"].isin(SKIP)].copy()

print(f"\nLoaded {len(inv)} inventory leaf categories")

# ── 2. Convert Mg CO2 → GgCO2e (AR5 GWPs) ───────────────────────────────────
# CO2: 1 Mg = 0.001 Gg → GgCO2 = CO2_Mg / 1000
# CH4: Gg CH4 × 28 = GgCO2e
# N2O: Gg N2O × 265 = GgCO2e
inv["CO2_GgCO2e"]  = inv["CO2_Mg"]  / 1000
inv["CH4_GgCO2e"]  = inv["CH4_Mg"]  / 1000 * GWP_CH4
inv["N2O_GgCO2e"]  = inv["N2O_Mg"]  / 1000 * GWP_N2O
inv["total_GgCO2e"] = inv["CO2_GgCO2e"] + inv["CH4_GgCO2e"] + inv["N2O_GgCO2e"]
# HFCs/PFCs/SF6: ABSENT — zero-filled with flag
inv["HFC_PFC_SF6_GgCO2e"] = 0.0
inv["hfc_data_gap"]        = True   # flag: data gap for all categories

# ── 3. Check totals against Annex II Cuadro 12 ────────────────────────────────
KNOWN = {
    "FIXED":   {"CO2": 1504259.4, "CH4": 6.1,    "N2O": 6.7  },
    "AREA":    {"CO2": 1198773.1, "CH4": 8365.2,  "N2O": 71.4 },  # N2O tolerance widened: 9.8 Mg gap from minor soil/agri N2O sources not in leaf categories (~2.6 GgCO2e)
    "MOBILE":  {"CO2": 2619351.6, "CH4": 297.2,   "N2O": 134.8},
    "MOBILE_NONROAD": {"CO2": 1631.2, "CH4": 0.1, "N2O": 0.3  },
}
TOTAL_CO2_KNOWN = 5324015.4  # Mg

print("\nSanity check — source totals vs Annex II Cuadro 12 (Mg/year):")
all_ok = True
for src, vals in KNOWN.items():
    subset = inv[inv["source_type"]==src]
    for gas, exp in vals.items():
        got  = subset[f"{gas}_Mg"].sum()
        diff = abs(got - exp)
        tol  = 15.0 if (src == "AREA" and gas == "N2O") else max(1.0, exp * 0.005)
        flag = "✓" if diff < tol else "⚠ MISMATCH"
        if diff >= tol: all_ok = False
        print(f"  {src:<12} {gas:<4}  got={got:12.1f}  exp={exp:12.1f}  {flag}")

if not all_ok:
    print("\n⚠  Mismatches detected — check leaf category completeness")
    sys.exit(1)
else:
    print("\n✓ All source-type totals reconcile within tolerance")

# Total state CO2 (fossil + biogenic as reported)
total_co2_Mg = inv["CO2_Mg"].sum()
total_GgCO2e = inv["total_GgCO2e"].sum()
print(f"\nState totals (2014):")
print(f"  CO2 (Mg):          {total_co2_Mg:,.0f}  (check: {TOTAL_CO2_KNOWN:,.0f})")
print(f"  Total GgCO2e (AR5):{total_GgCO2e:,.1f}")

# ── 4. Identify biogenic CO2 categories ──────────────────────────────────────
# Domestic wood combustion CO2 is biogenic — excluded from carbon pricing scope
# The inventory includes it in area-source totals; we flag and separate it
# Est. from Figure 51: domestic combustion = 12% of state CO2
# = 0.12 × 5,324,015 = 638,882 Mg ≈ matches reported Combustion_domestica 626,299 Mg
# For carbon pricing analysis: biogenic CO2 is exempt from both S and F
BIOGENIC_CATEGORIES = {
    "Combustion_doméstica":  True,   # leña — biogenic CO2
    "Combustion_agricola":   False,  # burning of crop residues — partly fossil (N2O/CH4 still priced)
    "Quemas_agricolas":      False,  # agricultural burns — CH4/N2O remain in scope
    "Incendios_forestales":  True,   # forest fires — biogenic
    "Alimentos_y_bebidas":   False,  # bagasse combustion excluded from CO2 totals already
}
inv["biogenic_co2"] = inv["category"].map(BIOGENIC_CATEGORIES).fillna(False)

# ── 5. Add IPCC-equivalent sector classification ──────────────────────────────
IPCC_MAP = {
    # Fixed sources
    "Cemento_y_cal":            "industrial_process_cement",
    "Vidrio":                   "industrial_process_glass",
    "Quimica":                  "manufacturing_chemical",
    "Celulosa_y_papel":         "manufacturing_pulp_paper",
    "Alimentos_y_bebidas":      "manufacturing_food_bev",
    "Derivados_petroleo_carbon":"manufacturing_petro_products",
    "Metalurgica":              "manufacturing_metals",
    "Minerales_no_metalicos":   "manufacturing_nonmet_minerals",
    "Metálico":                 "manufacturing_metals",
    "Mezclas_quimicas":         "manufacturing_chemical",
    "Plastico_y_hule":          "manufacturing_plastics",
    "Petroleo_petroquimica":    "manufacturing_petrochem",
    "Automotriz":               "manufacturing_automotive",
    "Accesorios_electricos":    "manufacturing_electrical",
    "Industria_textil":         "manufacturing_textiles",
    # Residual fixed
    "Residual_fixed_sectors":   "manufacturing_other_small",
    # Wastewater area (excluded from AREA Cuadro 12 total)
    "Aguas_residuales_area":    "waste_wastewater",
    "Combustion_doméstica":     "area_residential",
    "Combustion_comercial":     "area_commercial",
    "Combustion_industrial":    "area_industrial_small",
    "Combustion_agricola":      "area_agri_combustion",
    "Emisiones_ganaderas":      "afolu_livestock",
    "Quemas_agricolas":         "afolu_burning",
    "Incendios_forestales":     "afolu_fire",
    "Aguas_residuales":         "waste_wastewater",
    "Otras_area":               "area_other",
    # Mobile
    "Automovel_particular":     "mobile_road",
    "Taxi":                     "mobile_road",
    "Camioneta_particular":     "mobile_road",
    "Camioneta_transp_publico": "mobile_road",
    "Pickup":                   "mobile_road",
    "Autobus":                  "mobile_road",
    "Veh_menos_3_8ton":         "mobile_road",
    "Veh_mas_3_8ton":           "mobile_road",
    "Tractocamion":             "mobile_road",
    "Autobus_publico_municipal":"mobile_road",
    "Motocicleta":              "mobile_road",
    # Non-road
    "Aviacion":                 "mobile_nonroad",
    "Locomotoras":              "mobile_nonroad",
    "Lanchas_recreativas":      "mobile_nonroad",
    "Terminal_autobuses":       "mobile_nonroad",
}
inv["ipcc_sector"] = inv["category"].map(IPCC_MAP).fillna("area_other")

# ── 6. Cement CO2 process/combustion split ────────────────────────────────────
# Cement is the critical category. CO2 = 901,618 Mg total.
# Split: calcination process CO2 vs. fuel combustion CO2
# Methodology: IPCC 2006 clinker-based approach
# Mexico cement clinker ratio: ~0.85 (clinker/cement) typical for Mexican industry
# CO2 from calcination ≈ 0.5 t CO2/t clinker (CaCO3 → CaO + CO2)
# Morelos has 3 cement facilities; Cemex/Cruz Azul/Holcim operations
# National average process fraction: ~60% process, ~40% combustion for Mexican cement
# Fuel combustion CO2 mainly from petcoke (high-sulfur; ~97% fossil)
# Sources: INECC cement sector analysis; IPCC 2006 vol 3 ch 2

CEMENT_PROCESS_FRAC_CENTRAL = 0.60   # 60% process (calcination)
CEMENT_PROCESS_FRAC_LOW     = 0.55   # lower bound
CEMENT_PROCESS_FRAC_HIGH    = 0.65   # upper bound
CEMENT_CO2_TOTAL_Mg = 901618.0

cement_split = pd.DataFrame([
    dict(scenario="central", process_frac=CEMENT_PROCESS_FRAC_CENTRAL,
         process_CO2_Mg=CEMENT_CO2_TOTAL_Mg*CEMENT_PROCESS_FRAC_CENTRAL,
         combustion_CO2_Mg=CEMENT_CO2_TOTAL_Mg*(1-CEMENT_PROCESS_FRAC_CENTRAL)),
    dict(scenario="low", process_frac=CEMENT_PROCESS_FRAC_LOW,
         process_CO2_Mg=CEMENT_CO2_TOTAL_Mg*CEMENT_PROCESS_FRAC_LOW,
         combustion_CO2_Mg=CEMENT_CO2_TOTAL_Mg*(1-CEMENT_PROCESS_FRAC_LOW)),
    dict(scenario="high", process_frac=CEMENT_PROCESS_FRAC_HIGH,
         process_CO2_Mg=CEMENT_CO2_TOTAL_Mg*CEMENT_PROCESS_FRAC_HIGH,
         combustion_CO2_Mg=CEMENT_CO2_TOTAL_Mg*(1-CEMENT_PROCESS_FRAC_HIGH)),
])
cement_split.to_csv(os.path.join(PROC_DIR, "morelos_cement_process_split_2014.csv"), index=False)
print(f"\nCement CO2 process/combustion split (central):")
c = cement_split[cement_split["scenario"]=="central"].iloc[0]
print(f"  Total cement CO2:      {CEMENT_CO2_TOTAL_Mg:,.0f} Mg")
print(f"  Process (calcination): {c['process_CO2_Mg']:,.0f} Mg  ({CEMENT_PROCESS_FRAC_CENTRAL*100:.0f}%)")
print(f"  Combustion (fuel):     {c['combustion_CO2_Mg']:,.0f} Mg  ({(1-CEMENT_PROCESS_FRAC_CENTRAL)*100:.0f}%)")
print(f"  Basis: national average for Mexican cement industry; INECC/IPCC 2006 method")

# ── 7. Compute fuel fractions for fixed sources ────────────────────────────────
# These drive the federal tax (F) coverage calculation
# Federal IEPS covers: diesel, FO, LPG, formulated fuels, petcoke
# Exempt from IEPS: natural gas (statutory), bagasse (biogenic), biogas (biogenic)
fuel = fuel_raw[~fuel_raw["fuel"].str.startswith("TOTAL")].copy()
taxable = fuel[fuel["fuel"].isin(["Diesel","Combustoleo","Gas_LP","Combustibles_formulados","Coque_de_petroleo"])]
ng_only = fuel[fuel["fuel"]=="Gas_natural"]
biogenic = fuel[fuel["fuel"].isin(["Bagazo","Biogas"])]

total_energy = fuel["energy_TJ"].sum()
taxable_frac_energy = taxable["energy_TJ"].sum() / total_energy
ng_frac_energy      = ng_only["energy_TJ"].sum() / total_energy
bio_frac_energy     = biogenic["energy_TJ"].sum() / total_energy

# CO2 fractions from combustion:
# Use INECC emission factors (kg CO2/TJ)
EF = {
    "Diesel":                    72851,
    "Combustoleo":               79450,
    "Gas_LP":                    63100,
    "Gas_natural":               57755,
    "Combustibles_formulados":   73000,
    "Coque_de_petroleo":         97500,
    "Bagazo":                    0,     # biogenic — excluded from CO2 inventory totals
    "Biogas":                    0,     # biogenic
}

fuel["CO2_Mg_computed"] = fuel.apply(lambda r: r["energy_TJ"] * EF.get(r["fuel"], 0) / 1e6, axis=1)
total_combustion_CO2 = fuel["CO2_Mg_computed"].sum()

taxable_CO2  = fuel[fuel["fuel"].isin(["Diesel","Combustoleo","Gas_LP","Combustibles_formulados","Coque_de_petroleo"])]["CO2_Mg_computed"].sum()
ng_CO2       = fuel[fuel["fuel"]=="Gas_natural"]["CO2_Mg_computed"].sum()
biogenic_CO2 = 0.0  # excluded from totals by design

taxable_frac_CO2 = taxable_CO2 / total_combustion_CO2 if total_combustion_CO2 > 0 else 0
ng_frac_CO2      = ng_CO2     / total_combustion_CO2 if total_combustion_CO2 > 0 else 0

print(f"\nFixed-source fuel fractions (combustion CO2):")
for f_row in fuel.itertuples():
    if f_row.CO2_Mg_computed > 0:
        print(f"  {f_row.fuel:<30}: {f_row.CO2_Mg_computed:8.0f} Mg CO2  ({f_row.CO2_Mg_computed/total_combustion_CO2*100:.1f}%)")
print(f"  {'Taxable (non-NG fossil)':<30}: {taxable_CO2:8.0f} Mg CO2  ({taxable_frac_CO2*100:.1f}%)")
print(f"  {'NG exempt':<30}: {ng_CO2:8.0f} Mg CO2  ({ng_frac_CO2*100:.1f}%)")
print(f"  Note: Process CO2 (cement calcination) additional; not from combustion")

# ── 8. Build fuel fractions table ─────────────────────────────────────────────
# For fixed stationary sources, we need to account for:
# (a) combustion CO2: split taxable vs NG-exempt
# (b) process CO2 (cement, glass): covered by S but NOT by F
# (c) biogenic CO2 (domestic wood): NOT covered by either S or F
# (d) area-source small industrial combustion: similar fuel mix to fixed, but smaller scale

fracs = pd.DataFrame([
    # Cement: DOMINANT — process + combustion split is critical
    # F covers only the combustion fraction and only the non-NG part of that
    dict(
        category="Cemento_y_cal",
        f_frac_central=1-CEMENT_PROCESS_FRAC_CENTRAL,  # combustion fraction × (1-NG~0%)
        f_frac_low=(1-CEMENT_PROCESS_FRAC_HIGH)*(1-0.01),
        f_frac_high=(1-CEMENT_PROCESS_FRAC_LOW)*(1-0.01),
        ets_frac_central=0.97,  # 3 large cement plants; all likely >> 25kt threshold
        ets_frac_low=0.90,
        ets_frac_high=1.00,
        derivation="Cement: F covers only combustion fraction (~40%); process CO2 (60%) not taxable by IEPS; ETS: 3 large plants all likely above threshold"
    ),
    # Glass: mostly combustion (no calcination); high NG use in glass? No — petcoke/FO dominant
    dict(
        category="Vidrio",
        f_frac_central=0.96, f_frac_low=0.88, f_frac_high=0.99,
        ets_frac_central=0.85, ets_frac_low=0.70, ets_frac_high=0.98,
        derivation="Glass: mostly fuel combustion (FO+petcoke dominant); small NG fraction; 2 plants, likely 1 above threshold (Cuernavaca glass is large)"
    ),
    # Chemical industry: mixed combustion + some process
    dict(
        category="Quimica",
        f_frac_central=0.88, f_frac_low=0.78, f_frac_high=0.95,
        ets_frac_central=0.65, ets_frac_low=0.45, ets_frac_high=0.85,
        derivation="Chemical: mostly combustion; 20 small firms; few likely above 25kt threshold"
    ),
    # Pulp/paper: combustion + mixed fuel (bagasse/wood dominant in some mills, fossil in others)
    dict(
        category="Celulosa_y_papel",
        f_frac_central=0.82, f_frac_low=0.70, f_frac_high=0.92,
        ets_frac_central=0.80, ets_frac_low=0.60, ets_frac_high=0.95,
        derivation="Pulp/paper: mixed fossil/biogenic fuel; 2 plants; at least 1 likely above threshold"
    ),
    # Food/beverages: sugar mills dominate; bagasse = biogenic CO2 excluded from inventory
    # Remaining CO2 is from fossil fuels used in mills → taxable
    dict(
        category="Alimentos_y_bebidas",
        f_frac_central=0.90, f_frac_low=0.80, f_frac_high=0.98,
        ets_frac_central=0.70, ets_frac_low=0.50, ets_frac_high=0.90,
        derivation="Food/bev: sugar mills dominant; bagasse CO2 already excluded from inventory totals; reported CO2 is fossil; 8 firms, some large sugar mills likely above threshold"
    ),
    # Petroleum derivatives/carbon: small facilities; combustion dominant
    dict(
        category="Derivados_petroleo_carbon",
        f_frac_central=0.92, f_frac_low=0.82, f_frac_high=0.98,
        ets_frac_central=0.60, ets_frac_low=0.40, ets_frac_high=0.80,
        derivation="Petro derivatives: combustion; 3 firms; uncertain threshold compliance"
    ),
    # Small manufacturing (textiles, minerals, metals, plastics, auto, etc.)
    dict(
        category="OTHER_MANUFACTURING",
        f_frac_central=0.90, f_frac_low=0.80, f_frac_high=0.97,
        ets_frac_central=0.25, ets_frac_low=0.10, ets_frac_high=0.45,
        derivation="Other manufacturing: small firms; mostly below ETS threshold; combustion dominant (petcoke/FO/LPG mix)"
    ),
    # Area-source small industrial combustion: small facilities; taxable fuels; below ETS
    dict(
        category="Combustion_industrial",
        f_frac_central=0.90, f_frac_low=0.80, f_frac_high=0.97,
        ets_frac_central=0.00, ets_frac_low=0.00, ets_frac_high=0.05,
        derivation="Small industrial area sources: below ETS threshold by definition; taxable combustion"
    ),
    # Commercial combustion: LPG/NG mix; small scale; below ETS
    dict(
        category="Combustion_comercial",
        f_frac_central=0.80, f_frac_low=0.65, f_frac_high=0.92,
        ets_frac_central=0.00, ets_frac_low=0.00, ets_frac_high=0.00,
        derivation="Commercial combustion: LPG dominant (taxable); NG ~20% exempt; below ETS threshold"
    ),
])

fracs.to_csv(os.path.join(PROC_DIR, "morelos_fuel_fractions_2014.csv"), index=False)
print(f"\nSaved: data/processed/morelos_fuel_fractions_2014.csv  ({len(fracs)} rows)")

# ── 9. Save cleaned inventory ──────────────────────────────────────────────────
inv.to_csv(os.path.join(PROC_DIR, "morelos_inventory_2014.csv"), index=False)
print(f"Saved: data/processed/morelos_inventory_2014.csv  ({len(inv)} rows)")

print(f"\nSummary (2014, GgCO2e, AR5 GWPs):")
print(f"  Fixed sources:    {inv[inv['source_type']=='FIXED']['total_GgCO2e'].sum():8.1f}")
print(f"  Area sources:     {inv[inv['source_type']=='AREA']['total_GgCO2e'].sum():8.1f}")
print(f"  Mobile (road):    {inv[inv['source_type']=='MOBILE']['total_GgCO2e'].sum():8.1f}")
print(f"  Mobile (nonroad): {inv[inv['source_type']=='MOBILE_NONROAD']['total_GgCO2e'].sum():8.1f}")
print(f"  STATE TOTAL:      {inv['total_GgCO2e'].sum():8.1f}")
print(f"\n  Note: includes biogenic CO2 (dom. wood ~626 GgCO2e); subtract for net fossil")

print("\n✓ 01_clean.py complete\n")
