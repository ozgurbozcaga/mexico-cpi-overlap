"""
=============================================================================
Case:            Mexico State Carbon Pricing — Colima
Script:          01_clean.py
Estimation tier: Tier 4 (legal scope + energy balance bounds, reported as
                 ranges), upgraded from Tier 4 to Tier 3+ for stationary
                 combustion given quality of 2015 base inventory.
Base year:       2015 (IMADES / Under2 Coalition GHG Inventory of Colima,
                 published 2019-01-31)
Target year:     2022 (latest INECC INEGYCEI reference year)
GWPs:            AR5 (CH4=28, N2O=265) — matches base inventory and INECC
Data source:     Colima_future_fund_report_2018.pdf (base year 2015 inventory)
Key assumption:  2015 inventory data hard-coded from PDF extract; values in
                 Gg CO2e unless otherwise noted.
Author:          mexico-cpi-overlap project
=============================================================================

Outputs (to data/processed/):
  colima_inventory_2015.csv      — full inventory by sector/subsector/gas
  colima_energy_detail_2015.csv  — energy subsector detail with fuel split
  colima_ippu_detail_2015.csv    — IPPU subsector detail
  colima_tax_scope_2015.csv      — subsectors in Colima state carbon tax scope
  colima_fuel_consumption_2015.csv — fuel consumption by subsector (TJ)
  colima_manzanillo_plant_2015.csv — thermoelectric plant-level fuel data

Validation targets (from national INECC data):
  Colima 2015 gross energy = 18,357 GgCO2e  (state inventory)
  Colima 2015 net total    = 18,137 GgCO2e  (state inventory)
"""

import os
import logging
import pandas as pd
import numpy as np

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)

PROCESSED_DIR = os.path.join(os.path.dirname(__file__), "data", "processed")
os.makedirs(PROCESSED_DIR, exist_ok=True)

# ---------------------------------------------------------------------------
# 1. GWPs used in 2015 Colima inventory (AR5, 100-year)
# ---------------------------------------------------------------------------
GWP = {
    "CO2": 1,
    "CH4": 28,
    "N2O": 265,
    "HCFC141b": 725,
    "HCFC22": 1810,
    "SF6": 23500,
    "black_carbon": 900,
}

# ---------------------------------------------------------------------------
# 2. Full inventory — sector/subsector totals
#    Source: Chart 4, Chart 16, Chart 19, Chart 21, Chart 26, Chart 39
#    Units: GgCO2e/year (2015)
#    Note: AFOLU land and removals kept separate to allow gross/net distinction
# ---------------------------------------------------------------------------

INVENTORY_ROWS = [
    # sector, subsector, ipcc_code, co2_gg, ch4_gg, n2o_gg, bc_gg, hfc_gg, co2e_gg
    # --- ENERGY ---
    ("Energy", "Electricity generation",        "1A1ai",  7034.06,  0.15,  0.02,  0.09,  0.00,  7128.00),
    ("Energy", "Energy generation plants",      "1A1aiii",   0.33,  0.30,  0.00,  0.00,  0.00,     9.00),
    # Manufacturing subsectors (Chart 19 — by fuel combustion)
    ("Energy", "Manuf — Cement and lime",       "1A2f",   231.76,  0.008, 0.002, 0.013,  0.00,   244.35),
    ("Energy", "Manuf — Food and beverage",     "1A2e",   267.08,  0.026, 0.001, 0.012,  0.00,   279.11),
    ("Energy", "Manuf — Metallurgical",         "1A2a",   270.01,  0.009, 0.018, 0.000,  0.00,   275.27),
    ("Energy", "Manuf — Non-metallic minerals", "1A2f",   659.99,  1.434, 0.020, 0.000,  0.00,   705.64),
    ("Energy", "Manuf — Other industries",      "1A2m",   423.80,  0.231, 0.003, 0.000,  0.00,   431.27),
    ("Energy", "Manuf — Petroleum/petrochem",   "1A2",      7.35,  0.191, 0.004, 0.000,  0.00,    13.73),
    ("Energy", "Manuf — Chemical",              "1A2c",     0.12,  0.000, 0.000, 0.000,  0.00,     0.12),
    ("Energy", "Manuf — Hazardous waste treat", "1A2",      0.14,  0.000, 0.000, 0.000,  0.00,     0.14),
    # Transport (Chart 21)
    ("Energy", "Transport — Civil aviation",    "1A3a",    16.60,  0.000, 0.000, 0.000,  0.00,    17.38),
    ("Energy", "Transport — Railways",          "1A3c",    33.49,  0.000, 0.010, 0.000,  0.00,    41.51),
    ("Energy", "Transport — Water navigation",  "1A3d",    66.97,  0.010, 0.000, 0.030,  0.00,    94.74),
    ("Energy", "Transport — Road",              "1A3b",  3610.17,  0.460, 0.140, 2.130,  0.00,  5577.93),
    # Other combustion (Chart 23)
    ("Energy", "Residential",                   "1A4b",   133.99,  0.230, 0.000, 0.050,  0.00,   189.05),
    ("Energy", "Commercial",                    "1A4a",    13.69,  0.000, 0.000, 0.000,  0.00,    13.78),
    ("Energy", "Agriculture/forestry/fishing",  "1A4c",    33.10,  0.000, 0.000, 0.020,  0.00,    49.88),

    # --- IPPU (Chart 26) ---
    ("IPPU", "Cement production",               "2A1",    408.80,  0.000, 0.000, 0.000,  0.000,  408.80),
    ("IPPU", "Lime production",                 "2A2",     21.07,  0.000, 0.000, 0.000,  0.000,   21.07),
    ("IPPU", "Iron production (pellets)",       "2C1",    136.57,  0.000, 0.000, 0.000,  0.000,  136.57),
    ("IPPU", "Use of products (HFCs)",          "2F/2G",    0.00,  0.000, 0.000, 0.000,  0.217,  157.20),

    # --- AFOLU (Chart 34 + Chart 35 + Chart 36) ---
    ("AFOLU", "Livestock — enteric ferment.",   "3A1",      0.00,  8.478, 0.000, 0.000,  0.000,  237.38),
    ("AFOLU", "Livestock — manure mgmt",        "3A2",      0.00,  0.209, 0.113, 0.000,  0.000,   35.78),
    # Agriculture aggregate (Chart 35 state totals)
    ("AFOLU", "Ag — Whitewashed",               "3C2",     22.32,  0.000, 0.000, 0.000,  0.000,   22.32),
    ("AFOLU", "Ag — Urea application",          "3C3",     15.91,  0.000, 0.000, 0.000,  0.000,   15.91),
    ("AFOLU", "Ag — Rice cultivation",          "3C7",      0.00,  0.436, 0.000, 0.000,  0.000,   12.22),
    ("AFOLU", "Ag — Synthetic fertilizers",     "3C4/5",    0.00,  0.000, 0.580, 0.000,  0.000,   10.06),  # approx
    ("AFOLU", "Ag — Biomass burning",           "3C1",     58.97,  0.123, 0.003, 0.021,  0.000,   82.11),
    # Land use change (Chart 36 — emissions only)
    ("AFOLU", "Land — converted to grasslands", "3B",     363.06,  0.000, 0.000, 0.000,  0.000,  363.06),
    ("AFOLU", "Land — converted to settlements","3B",      22.14,  0.000, 0.000, 0.000,  0.000,   22.14),
    ("AFOLU", "Land — converted to other",      "3B",       4.12,  0.000, 0.000, 0.000,  0.000,    4.12),
    ("AFOLU", "Land — converted to agri",       "3B",     950.80,  0.000, 0.000, 0.000,  0.000,  950.80),
    ("AFOLU", "Land — degraded forest",         "3B",     160.48,  0.000, 0.000, 0.000,  0.000,  160.48),
    # Removals (negative)
    ("AFOLU", "Removals — forest lands",        "3B",    -140.65,  0.000, 0.000, 0.000,  0.000, -140.65),
    ("AFOLU", "Removals — pastures",            "3B",     -78.13,  0.000, 0.000, 0.000,  0.000,  -78.13),

    # --- WASTE (Chart 39 state totals) ---
    ("Waste", "Solid waste disposal (MSW)",      "4A",      0.00,  2.596, 0.000, 0.000,  0.000,   72.70),
    ("Waste", "Waste burning opencast",          "4C",      1.25,  0.000, 0.000, 0.011,  0.000,   11.45),
    ("Waste", "Wastewater — municipal treated",  "4D",      0.00,  4.600, 0.030, 0.000,  0.000,  191.01),
    ("Waste", "Wastewater — municipal untreated","4D",      0.00,  6.172, 0.000, 0.000,  0.000,  118.23),
    ("Waste", "Wastewater — industrial treated", "4D",      0.00,  2.520, 0.000, 0.000,  0.000,   70.61),
]

COLS = ["sector", "subsector", "ipcc_code",
        "co2_gg", "ch4_gg", "n2o_gg", "bc_gg", "hfc_gg", "co2e_gg"]

df_inv = pd.DataFrame(INVENTORY_ROWS, columns=COLS)
df_inv["base_year"] = 2015

# ---------------------------------------------------------------------------
# 3. Sector-level validation
# ---------------------------------------------------------------------------
log.info("=== Inventory sector check ===")
sector_totals = df_inv.groupby("sector")["co2e_gg"].sum().round(1)
for s, v in sector_totals.items():
    log.info(f"  {s}: {v:.1f} GgCO2e")

energy_total = sector_totals.get("Energy", 0)
ippu_total   = sector_totals.get("IPPU", 0)
afolu_total  = sector_totals.get("AFOLU", 0)
waste_total  = sector_totals.get("Waste", 0)

# Gross = before removals; net subtracts removals
gross_total  = df_inv.loc[df_inv["co2e_gg"] > 0, "co2e_gg"].sum()
net_total    = df_inv["co2e_gg"].sum()

INVENTORY_GROSS_TARGET = 18357  # Gg, from report
INVENTORY_NET_TARGET   = 18137  # Gg, from report

log.info(f"Gross total (computed): {gross_total:.0f} GgCO2e  |  target: {INVENTORY_GROSS_TARGET}")
log.info(f"Net total  (computed): {net_total:.0f} GgCO2e  |  target: {INVENTORY_NET_TARGET}")

for label, computed, target in [
    ("Energy",  energy_total, 15070),
    ("IPPU",    ippu_total,     724),
    ("AFOLU",   afolu_total,   1879),
    ("Waste",   waste_total,    464),
]:
    diff_pct = abs(computed - target) / target * 100
    flag = "✓" if diff_pct < 2 else "⚠"
    log.info(f"  {flag} {label}: computed={computed:.0f}, target={target}, diff={diff_pct:.1f}%")

# ---------------------------------------------------------------------------
# 4. Energy subsector detail — fuel consumption (TJ, 2015)
#    Source: Charts 6, 7, 9 in 2015 inventory
# ---------------------------------------------------------------------------

ENERGY_FUEL_ROWS = [
    # subsector, fuel, tj
    # -- Electricity generation (Manzanillo thermoelectric plant) --
    ("Electricity generation",        "Natural gas",    98435.0),
    ("Electricity generation",        "Fuel oil",          28.0),
    ("Electricity generation",        "Diesel",         16951.0),
    # -- Energy generation plants (biogas) --
    ("Energy generation plants",      "Biogas",            14.49),
    # -- Manufacturing industries (Chart 9) --
    ("Manuf — Cement and lime",       "Mixed (NG/diesel/petcoke/coalcoke)", 2636.35),
    ("Manuf — Food and beverage",     "Mixed (NG/diesel/fuel oil)",         5897.71),
    ("Manuf — Metallurgical",         "Mixed (NG/coalcoke/fuel oil)",       1882.64),
    ("Manuf — Non-metallic minerals", "Mixed (NG/diesel/fuel oil)",          286.39),
    ("Manuf — Other industries",      "Mixed",                              3462.44),
    ("Manuf — Petroleum/petrochem",   "Mixed",                                 0.08),
    ("Manuf — Chemical",              "Mixed",                                 0.51),
    ("Manuf — Metal-mechanic",        "Mixed",                                 0.02),
    # -- Transport (Chart 7) --
    ("Transport — Road",              "Gasoline/diesel",                   63913.0),
    ("Transport — Water navigation",  "Diesel",                              919.0),
    ("Transport — Railways",          "Diesel",                              459.46),
    ("Transport — Civil aviation",    "Turbosine/kerosene",                  225.0),
    # -- Other combustion (Charts 11, 12, 13) --
    ("Residential",                   "LP gas",                              830.22),
    ("Residential",                   "Firewood",                            763.14),
    ("Residential",                   "Kerosene",                             16.36),
    ("Commercial",                    "LP gas",                              210.38),
    ("Agriculture/forestry/fishing",  "LP gas",                              332.5),
    ("Agriculture/forestry/fishing",  "Diesel",                              136.3),
]

df_fuel = pd.DataFrame(ENERGY_FUEL_ROWS, columns=["subsector", "fuel", "tj"])
df_fuel["base_year"] = 2015

fuel_total = df_fuel["tj"].sum()
FUEL_TOTAL_TARGET = 197400  # TJ, from Chart 6
log.info(f"Fuel total check: {fuel_total:.0f} TJ  |  target: ~{FUEL_TOTAL_TARGET} TJ")

# ---------------------------------------------------------------------------
# 5. Manzanillo thermoelectric plant — facility-level data
#    Critical for determining whether it falls under Mexico Pilot ETS
# ---------------------------------------------------------------------------

MANZANILLO_PLANT = {
    "plant_name":        "Termoeléctrica Gral. Manuel Álvarez Moreno",
    "operator":          "CFE",
    "municipality":      "Manzanillo",
    "state":             "Colima",
    "generation_gwh":    13984,        # GWh in 2015 (SENER 2016)
    "ng_consumption_tj": 98435,        # TJ natural gas
    "fo_consumption_tj":    28,        # TJ fuel oil
    "diesel_consumption_tj": 16951,    # TJ diesel
    "co2e_gg":           7128,         # GgCO2e (electricity generation total)
    "note": (
        "Dominates Colima energy sector (47% of state CO2e). "
        "Natural gas (>85% of plant fuel) is EXEMPT from Mexico federal carbon tax. "
        "Diesel component (~16,951 TJ) IS subject to federal tax. "
        "Plant likely reportable to SEMARNAT COA; check Mexico ETS participant list."
    ),
}

df_plant = pd.DataFrame([MANZANILLO_PLANT])

# ---------------------------------------------------------------------------
# 6. IPPU detail
# ---------------------------------------------------------------------------

IPPU_ROWS = [
    # subcategory, municipality, production_tons, co2e_gg, note
    ("Cement production", "Tecomán",   911668, 408.8,  "Cementos Apasco; clinker fraction 0.86"),
    ("Lime production",   "Ixtlahuacán", 27363,  21.1, "Calidra del Occidente; 2005 AD used (2015 not reported)"),
    ("Iron production",   "Manzanillo", 2981665, 89.5, "Consorcio Minero Benito Juárez, Peña Colorada"),
    ("Iron production",   "Cuauhtémoc", 1570674, 47.1, "Las Encinas pelleting plant"),
    ("Use of products",   "State",         None, 157.2, "HCFC-22 refrigeration/AC; HFCs from COA"),
]

df_ippu = pd.DataFrame(IPPU_ROWS,
    columns=["subcategory", "municipality", "production_tons", "co2e_gg", "note"])
df_ippu["base_year"] = 2015

# ---------------------------------------------------------------------------
# 7. Tax scope mapping — Colima state carbon tax
#    Colima's state carbon tax (Ley de Hacienda amendment) follows the
#    Jalisco/Zacatecas model: targets fossil fuel combustion at stationary
#    sources above a specified threshold. Mobile sources (road transport)
#    are typically EXCLUDED from state-level carbon taxes in Mexico because
#    the federal IEPS already covers transport fuels.
#    Natural gas exemption: same as federal — NG is NOT taxed.
#
#    Coverage determination:
#      IN SCOPE  → stationary combustion using taxed fuels (diesel, fuel oil,
#                  petroleum coke, coal coke, LP gas, etc.)
#      OUT OF SCOPE → natural gas combustion; transport; AFOLU; waste;
#                     IPPU process emissions (non-combustion)
#
#    Overlap with federal tax:
#      Federal tax covers same fuels (excl. NG) at point of sale upstream.
#      All fuels taxed by state are ALSO taxed by the federal tax.
#      → Full overlap on in-scope fuels; de-duplication needed.
#
#    Overlap with Mexico Pilot ETS:
#      ETS covers large emitters in energy + industry (>25,000 tCO2e/yr).
#      Manzanillo plant and major industrial facilities likely in ETS scope.
#      However ETS is pilot (non-binding) — operational/legal coverage diverges.
# ---------------------------------------------------------------------------

TAX_SCOPE_ROWS = [
    # subsector, in_state_tax_scope, overlap_federal_tax, overlap_ets_pilot,
    # co2e_gg_2015, taxable_co2e_gg_note
    ("Electricity generation",        True,  True,  True,
     7128.0, "Diesel fraction only (~16,951 TJ); NG (98,435 TJ) exempt both taxes"),
    ("Energy generation plants",      True,  False, False,
       9.0,  "Biogas — zero-carbon accounting; effectively untaxed"),
    ("Manuf — Cement and lime",       True,  True,  True,
     244.4,  "Process emissions (IPPU) excluded; combustion fuels in scope"),
    ("Manuf — Food and beverage",     True,  True,  False,
     279.1,  "Below ETS threshold likely; all combustion fuels in scope"),
    ("Manuf — Metallurgical",         True,  True,  True,
     275.3,  "Large facilities (Peña Colorada, Las Encinas) likely ETS-eligible"),
    ("Manuf — Non-metallic minerals", True,  True,  False,
     705.6,  "Various small facilities; combustion fuels in scope"),
    ("Manuf — Other industries",      True,  True,  False,
     431.3,  "Mixed; combustion fuels in scope"),
    ("Manuf — Petroleum/petrochem",   True,  True,  False,
      13.7,  "Small; in scope"),
    ("Manuf — Chemical",              True,  True,  False,
       0.1,  "Negligible; in scope"),
    ("Manuf — Hazardous waste treat", True,  True,  False,
       0.1,  "Negligible"),
    # Transport — excluded from state tax
    ("Transport — Road",              False, True,  False,
    5577.9,  "Federal IEPS covers road fuels; state tax typically excludes mobile sources"),
    ("Transport — Water navigation",  False, True,  False,
      94.7,  "Marine diesel — federal only"),
    ("Transport — Railways",          False, True,  False,
      41.5,  "Diesel — federal only"),
    ("Transport — Civil aviation",    False, True,  False,
      17.4,  "Turbosine — federal only"),
    # Other combustion
    ("Residential",                   True,  True,  False,
     189.1,  "LP gas and firewood; firewood technically exempt; LP gas taxed"),
    ("Commercial",                    True,  True,  False,
      13.8,  "LP gas in scope"),
    ("Agriculture/forestry/fishing",  True,  True,  False,
      49.9,  "Diesel and LP gas; agricultural diesel may have state exemptions"),
    # IPPU process emissions — out of scope for combustion-based taxes
    ("Cement production (IPPU)",      False, False, True,
     408.8,  "Process CO2 from calcination — not a combustion tax; ETS only"),
    ("Lime production (IPPU)",        False, False, False,
      21.1,  "Process CO2; small facility"),
    ("Iron production (IPPU)",        False, False, True,
     136.6,  "Process emissions from pelletization; ETS-eligible facilities"),
    ("Use of products (HFCs)",        False, False, False,
     157.2,  "HFCs — not covered by any carbon pricing instrument"),
    # AFOLU — out of scope
    ("AFOLU (all subsectors)",        False, False, False,
    1879.0,  "Agriculture/land/livestock — outside carbon tax and ETS scope"),
    # Waste — out of scope
    ("Waste (all subsectors)",        False, False, False,
     464.0,  "Waste sector — outside scope"),
]

SCOPE_COLS = [
    "subsector", "in_state_tax_scope", "overlap_federal_tax",
    "overlap_ets_pilot", "co2e_gg_2015", "note"
]
df_scope = pd.DataFrame(TAX_SCOPE_ROWS, columns=SCOPE_COLS)

# Summary
in_scope = df_scope.loc[df_scope["in_state_tax_scope"], "co2e_gg_2015"].sum()
federal_overlap = df_scope.loc[df_scope["overlap_federal_tax"], "co2e_gg_2015"].sum()
ets_overlap = df_scope.loc[df_scope["overlap_ets_pilot"], "co2e_gg_2015"].sum()
total_state = df_scope["co2e_gg_2015"].sum()

log.info("=== Tax scope summary (2015 base) ===")
log.info(f"  Total state emissions: {total_state:.0f} GgCO2e")
log.info(f"  In Colima state tax scope: {in_scope:.0f} GgCO2e ({in_scope/total_state*100:.1f}%)")
log.info(f"  Overlap with federal carbon tax: {federal_overlap:.0f} GgCO2e ({federal_overlap/total_state*100:.1f}%)")
log.info(f"  Overlap with Mexico Pilot ETS: {ets_overlap:.0f} GgCO2e ({ets_overlap/total_state*100:.1f}%)")

# ---------------------------------------------------------------------------
# 8. Diesel-only taxable fraction for electricity generation
#    The Manzanillo plant burns mostly natural gas (exempt) and some diesel.
#    We need to isolate the diesel-attributable CO2e for the overlap calc.
# ---------------------------------------------------------------------------

# Simple fuel-share approach: diesel / (NG + FO + diesel) by energy content
ng_tj  = 98435
fo_tj  =    28
d_tj   = 16951
total_plant_tj = ng_tj + fo_tj + d_tj

# CO2e attributable to diesel combustion at plant
# Using emission factors from Chart 14: diesel CO2 EF = 72,881 kg/TJ
diesel_co2_gg = d_tj * 72881 / 1e6  # Gg
# Using fuel oil EF = 79,450 kg/TJ
fo_co2_gg = fo_tj * 79450 / 1e6
# Natural gas EF = 57,756 kg/TJ
ng_co2_gg = ng_tj * 57756 / 1e6

plant_co2_total = diesel_co2_gg + fo_co2_gg + ng_co2_gg  # cross-check vs 7034 Gg
log.info(f"Manzanillo plant CO2 cross-check: {plant_co2_total:.0f} GgCO2 (inventory: 7034 GgCO2)")
log.info(f"  NG share: {ng_co2_gg:.0f} Gg ({ng_co2_gg/plant_co2_total*100:.1f}%) — EXEMPT from federal+state tax")
log.info(f"  Diesel share: {diesel_co2_gg:.0f} Gg ({diesel_co2_gg/plant_co2_total*100:.1f}%) — IN SCOPE")
log.info(f"  Fuel oil share: {fo_co2_gg:.0f} Gg ({fo_co2_gg/plant_co2_total*100:.1f}%) — IN SCOPE")

taxable_elec_co2e = diesel_co2_gg + fo_co2_gg  # approximate (ignoring CH4/N2O for now)
df_scope.loc[df_scope["subsector"] == "Electricity generation",
             "taxable_co2e_gg_note"] = (
    f"Taxable (diesel+FO) fraction: ~{taxable_elec_co2e:.0f} GgCO2 of {7034:.0f} GgCO2 total"
)

# ---------------------------------------------------------------------------
# 9. Save outputs
# ---------------------------------------------------------------------------

out_inventory = os.path.join(PROCESSED_DIR, "colima_inventory_2015.csv")
out_fuel      = os.path.join(PROCESSED_DIR, "colima_fuel_consumption_2015.csv")
out_plant     = os.path.join(PROCESSED_DIR, "colima_manzanillo_plant_2015.csv")
out_ippu      = os.path.join(PROCESSED_DIR, "colima_ippu_detail_2015.csv")
out_scope     = os.path.join(PROCESSED_DIR, "colima_tax_scope_2015.csv")

df_inv.to_csv(out_inventory, index=False)
df_fuel.to_csv(out_fuel, index=False)
df_plant.to_csv(out_plant, index=False)
df_ippu.to_csv(out_ippu, index=False)
df_scope.to_csv(out_scope, index=False)

log.info("Outputs written:")
for p in [out_inventory, out_fuel, out_plant, out_ippu, out_scope]:
    log.info(f"  {p}")

# ---------------------------------------------------------------------------
# 10. Metadata — for docs/data_sources.md update
# ---------------------------------------------------------------------------

METADATA = """
## Colima 2015 GHG Inventory

- **Source document**: Greenhouse Gas Inventory of the State of Colima, Base Year 2015
- **Producer**: IMADES (Instituto para el Medio Ambiente y Desarrollo Sustentable del Estado de Colima)
- **Funded by**: Under2 Coalition Future Fund (Québec, Scotland, Wales; grant UC/FF/2018/002)
- **Date published**: 2019-01-31
- **Local filename**: Colima_future_fund_report_2018_pdf.pdf
- **GWPs**: AR5 (CH4=28, N2O=265, SF6=23500, black carbon=900) — matches INECC INEGYCEI 2022
- **Methodology**: IPCC 2006 Guidelines; Tier 2 for stationary combustion, Tier 3 for road transport (MOVES-Mexico)
- **Coverage**: All 10 municipalities; full IPCC 2006 sector breakdown
- **Key uncertainty**: 8.9% overall combined (inventory's own estimate)

### Validation notes
- Net total 18,137 GgCO2e matches inventory (Chart 1 / Chart 4)
- Energy sector 15,070 GgCO2e: electricity (47%) + road transport (37%)
- Manzanillo municipality = 57% of state total (CFE thermoelectric plant)
- Cement plant (Cementos Apasco, Tecomán): 911,668 tons cement, ~409 GgCO2e
- Lime plant (Calidra del Occidente, Ixtlahuacán): 27,363 tons — 2005 activity data used in inventory
- Iron pellet plants: Peña Colorada (Manzanillo) + Las Encinas (Cuauhtémoc) = 4.55 Mt pellets

### Previous inventory
- Base year 2005 inventory existed but used SAR GWPs and had 20-year extrapolation gap
- 2015 inventory supersedes 2005 as the base for all Colima overlap calculations
"""

meta_path = os.path.join(os.path.dirname(__file__), "docs", "data_sources.md")
os.makedirs(os.path.dirname(meta_path), exist_ok=True)
with open(meta_path, "w", encoding="utf-8") as f:
    f.write(METADATA.strip())
log.info(f"Metadata written: {meta_path}")

log.info("01_clean.py complete.")
