"""
=============================================================================
Case:            Mexico State Carbon Pricing -- Yucatan
Script:          01_clean.py
Estimation tier: Tier 3
Base year:       2023  (IEEGYCEI del Estado de Yucatan 2010-2023, SDS 2024)
GWPs:            AR5 (CH4=28, N2O=265) -- inventory already uses AR5;
                 NO CONVERSION NEEDED
Data source:     IEEGYCEI_del_Estado_de_Yucatan_2010_2023.pdf
Author:          mexico-cpi-overlap project
=============================================================================

Outputs (to data/processed/):
  yucatan_inventory_2023.csv       -- full inventory by IPCC code / gas
  yucatan_energy_fuel_2023.csv     -- electricity fuel consumption (PJ)
  yucatan_tax_scope_2023.csv       -- subsectors with S/F/E scope flags
  yucatan_hfc_detail_2023.csv      -- HFC refrigeration breakdown

Validation targets (from inventory Table 9):
  Total 2023 (excl. 3B+3D): 10,425.52 GgCO2e
  Emissions netas:          -2,685.91 GgCO2e
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
# 1. Full inventory -- Table 9 (pp.30-35), 2023 values, GgCO2e
#    Already AR5 GWPs -- no conversion needed
# ---------------------------------------------------------------------------

INVENTORY_ROWS = [
    # (ipcc_code, level, co2_gg, ch4_gg, n2o_gg, hfc_gg, hcfc_gg, co2e_gg)
    # --- ENERGY (Sector 1) ---
    ("1A1a",  "Generacion electrica",                2967.64,  1.60,  1.77,  0.00, 0.00, 2971.00),
    ("1A1cii","Otras industrias de la energia",        12.78,  0.01,  0.01,  0.00, 0.00,   12.79),
    ("1A2a",  "Hierro y acero",                         1.66,  0.00,  0.00,  0.00, 0.00,    1.66),
    ("1A2c",  "Productos quimicos",                    95.06,  0.05,  0.07,  0.00, 0.00,   95.18),
    ("1A2e",  "Alimentos, bebidas y tabaco",          413.21,  0.25,  0.31,  0.00, 0.00,  413.77),
    ("1A2f",  "Minerales no metalicos",               208.44,  0.31,  0.62,  0.00, 0.00,  209.37),
    ("1A2g",  "Equipo de transporte",                   2.34,  0.00,  0.00,  0.00, 0.00,    2.34),
    ("1A2i",  "Mineria",                               69.57,  0.07,  0.13,  0.00, 0.00,   69.78),
    ("1A2k",  "Construccion",                          20.67,  0.02,  0.04,  0.00, 0.00,   20.73),
    ("1A2l",  "Textiles y cueros",                     48.95,  0.02,  0.03,  0.00, 0.00,   49.00),
    ("1A2m",  "Industria no especificada",              0.17,  0.00,  0.00,  0.00, 0.00,    0.17),
    ("1A3a",  "Aviacion civil",                       173.36,  0.03,  1.27,  0.00, 0.00,  174.66),
    ("1A3b",  "Transporte terrestre",                2636.56, 12.23,114.66,  0.00, 0.00, 2763.45),
    ("1A3c",  "Ferrocarriles",                         65.42,  0.10,  6.68,  0.00, 0.00,   72.20),
    ("1A3d",  "Navegacion maritima y fluvial",        107.91,  0.29,  0.78,  0.00, 0.00,  108.97),
    ("1A4a",  "Comercial/Institucional",              130.57,  0.31,  0.09,  0.00, 0.00,  130.97),
    ("1A4b",  "Residencial",                          115.17, 92.94, 11.74,  0.00, 0.00,  219.85),
    ("1A4c",  "Agropecuario",                          10.67,  0.02,  0.00,  0.00, 0.00,   10.70),
    ("1A5",   "Sector no especificado",                 0.27,  0.00,  0.00,  0.00, 0.00,    0.27),
    ("1B2a",  "Transporte y almac. Gas LP",             0.00,  0.00,  0.00,  0.00, 0.00, 5.83e-4),
    ("1B2b",  "Distribucion y uso gas natural",         0.08, 89.86,  0.00,  0.00, 0.00,   89.95),
    # --- IPPU (Sector 2) ---
    ("2A1",   "Produccion de cemento",                318.04,  0.00,  0.00,  0.00, 0.00,  318.04),
    ("2A2",   "Produccion de cal",                      7.37,  0.00,  0.00,  0.00, 0.00,    7.37),
    ("2C1",   "Produccion de hierro y acero",           3.32,  0.00,  0.00,  0.00, 0.00,    3.32),
    ("2D1",   "Uso de lubricantes",                    19.66,  0.00,  0.00,  0.00, 0.00,   19.66),
    ("2F1ai", "Refrig/AC residencial",                  0.00,  0.00,  0.00, 25.10, 0.00,   25.10),
    ("2F1aii","Refrig/AC comercios",                    0.00,  0.00,  0.00,291.61, 0.00,  291.61),
    ("2F1aiii","Refrig/AC hoteles",                     0.00,  0.00,  0.00, 12.12, 0.00,   12.12),
    ("2F1aiv","Refrig/AC hospitales",                   0.00,  0.00,  0.00,  0.94, 0.00,    0.94),
    ("2F1av", "Refrig/AC oficinas",                     0.00,  0.00,  0.00,  0.41, 0.00,    0.41),
    ("2F1avi","Refrig/AC industria",                    0.00,  0.00,  0.00,  1.63, 2.37,    4.00),
    # --- AFOLU (Sector 3) ---
    ("3A1",   "Fermentacion enterica",                  0.00,941.07,  0.00,  0.00, 0.00,  941.07),
    ("3A2",   "Gestion de estiercol",                   0.00, 26.36, 60.59,  0.00, 0.00,   86.95),
    ("3C1",   "Quema de biomasa",                       0.00,  3.25,  0.91,  0.00, 0.00,    4.16),
    ("3C3",   "Aplicacion de urea",                    74.32,  0.00,  0.00,  0.00, 0.00,   74.32),
    ("3C4",   "N2O suelos gestionados directas",        0.00,  0.00,265.11,  0.00, 0.00,  265.11),
    ("3C5",   "N2O suelos gestionados indirectas",      0.00,  0.00, 97.32,  0.00, 0.00,   97.32),
    ("3C6",   "N2O por SME indirectas",                 0.00,  0.00, 74.49,  0.00, 0.00,   74.49),
    # --- WASTE (Sector 4) ---
    ("4A1",   "Sitios eliminacion desechos gestionados",0.00,224.35,  0.00,  0.00, 0.00,  224.35),
    ("4A2",   "Sitios eliminacion no gestionados",      0.00,  6.28,  0.00,  0.00, 0.00,    6.28),
    ("4A3",   "Sitios eliminacion no categorizados",    0.00, 43.39,  0.00,  0.00, 0.00,   43.39),
    ("4C2",   "Incineracion abierta de residuos",       5.42, 11.13,  2.43,  0.00, 0.00,   18.98),
    ("4D1",   "Aguas residuales domesticas",            0.00,132.50, 39.22,  0.00, 0.00,  317.98),
    ("4D2",   "Aguas residuales industriales",          0.00,289.22, 28.76,  0.00, 0.00,  171.72),
]

COLS = ["ipcc_code", "level", "co2_gg", "ch4_gg", "n2o_gg", "hfc_gg", "hcfc_gg", "co2e_gg"]

df_inv = pd.DataFrame(INVENTORY_ROWS, columns=COLS)
df_inv["base_year"] = 2023
df_inv["gwp_basis"] = "AR5"

# ---------------------------------------------------------------------------
# 2. Sector-level validation against Table 8 / Table 9
# ---------------------------------------------------------------------------
log.info("=== Inventory sector validation ===")

# Map IPCC codes to sectors
def sector_map(code):
    if code.startswith("1"):
        return "Energy"
    if code.startswith("2"):
        return "IPPU"
    if code.startswith("3"):
        return "AFOLU"
    if code.startswith("4"):
        return "Waste"
    return "Other"

df_inv["sector"] = df_inv["ipcc_code"].apply(sector_map)

sector_totals = df_inv.groupby("sector")["co2e_gg"].sum()
for s, v in sector_totals.items():
    log.info(f"  {s}: {v:.2f} GgCO2e")

gross_total = df_inv["co2e_gg"].sum()
INVENTORY_TARGET = 10425.52
log.info(f"Gross total (computed): {gross_total:.2f} GgCO2e | target: {INVENTORY_TARGET}")

# Sector validation targets from Table 8
SECTOR_TARGETS = {
    "Energy":  7416.84,
    "IPPU":     682.56,
    "AFOLU":   1543.41,  # sin 3B+3D
    "Waste":    782.71,
}
for label, target in SECTOR_TARGETS.items():
    computed = sector_totals.get(label, 0)
    diff_pct = abs(computed - target) / target * 100
    flag = "OK" if diff_pct < 3 else "WARN"
    log.info(f"  {flag} {label}: computed={computed:.2f}, target={target}, diff={diff_pct:.1f}%")

# ---------------------------------------------------------------------------
# 3. Electricity generation fuel consumption -- Table 12, p.43
#    Units: PJ, 2023
# ---------------------------------------------------------------------------

ELEC_FUEL_ROWS = [
    ("Gas natural",   47.30),
    ("Diesel",         2.10),
    ("Combustoleo",    1.20),
]

df_fuel = pd.DataFrame(ELEC_FUEL_ROWS, columns=["fuel", "pj_2023"])
df_fuel["share"] = df_fuel["pj_2023"] / df_fuel["pj_2023"].sum()
df_fuel["base_year"] = 2023

log.info("\n=== Electricity generation fuel mix (2023) ===")
for _, r in df_fuel.iterrows():
    log.info(f"  {r['fuel']}: {r['pj_2023']:.2f} PJ ({r['share']*100:.1f}%)")

ng_share_elec = df_fuel.loc[df_fuel["fuel"] == "Gas natural", "share"].values[0]
non_ng_share_elec = 1 - ng_share_elec
log.info(f"  NG share: {ng_share_elec*100:.1f}% | Non-NG (taxable by F): {non_ng_share_elec*100:.1f}%")

# ---------------------------------------------------------------------------
# 4. HFC detail -- from Table 9 category 2F1
# ---------------------------------------------------------------------------

HFC_ROWS = [
    ("2F1ai",   "Residencial",   25.10),
    ("2F1aii",  "Comercios",    291.61),
    ("2F1aiii", "Hoteles",       12.12),
    ("2F1aiv",  "Hospitales",     0.94),
    ("2F1av",   "Oficinas",       0.41),
    ("2F1avi",  "Industria",      4.00),  # 1.63 HFC + 2.37 HCFC
]

df_hfc = pd.DataFrame(HFC_ROWS, columns=["ipcc_code", "application", "co2e_gg"])
df_hfc["note"] = "First state with HFC quantified + in tax scope"
total_hfc = df_hfc["co2e_gg"].sum()
log.info(f"\n=== HFC/HCFC total: {total_hfc:.2f} GgCO2e (3.21% of state) ===")

# ---------------------------------------------------------------------------
# 5. Manufacturing fuel fractions -- estimate non-NG share
#    From Table 9 gas decomposition: 1A2 total CO2 = 860.07 Gg
#    The inventory does not provide fuel-level detail for 1A2 subsectors.
#    Use national INECC manufacturing fuel mix: ~60% NG, ~40% other
#    For food/beverage specifically, Yucatan likely uses NG predominantly
#    given the gas pipeline infrastructure.
#    Conservative estimate: 65% NG for manufacturing overall.
# ---------------------------------------------------------------------------

MANUF_NG_SHARE = 0.65  # central estimate
MANUF_NG_LOW   = 0.50  # more diverse fuels
MANUF_NG_HIGH  = 0.80  # more NG-dominant

log.info(f"\n=== Manufacturing NG share assumption ===")
log.info(f"  Central: {MANUF_NG_SHARE*100:.0f}% | Low: {MANUF_NG_LOW*100:.0f}% | High: {MANUF_NG_HIGH*100:.0f}%")

# ---------------------------------------------------------------------------
# 6. Tax scope mapping -- Yucatan state carbon tax
#    Scope: fixed sources in productive activities, all Kyoto gases
#    No threshold. NG/calcination stimuli are PAYMENT RELIEF, not scope excl.
# ---------------------------------------------------------------------------

TAX_SCOPE_ROWS = [
    # (ipcc_code, level, in_S, in_F, in_E_eligible, co2e_gg, note)
    # --- S-covered: stationary combustion + IPPU ---
    ("1A1a",  "Generacion electrica",          True,  True,  True,  2971.00,
     "NG 93.5%; non-NG fraction taxable by F"),
    ("1A1cii","Otras industrias energia",      True,  True,  True,    12.79,
     "Other energy industries"),
    ("1A2a",  "Hierro y acero",                True,  True,  True,     1.66,
     "Small facility"),
    ("1A2c",  "Productos quimicos",            True,  True,  True,    95.18,
     "Chemical manufacturing"),
    ("1A2e",  "Alimentos, bebidas, tabaco",    True,  True,  True,   413.77,
     "Largest manufacturing subsector; food processing"),
    ("1A2f",  "Minerales no metalicos",        True,  True,  True,   209.37,
     "Coke de petroleo used; non-metallic minerals"),
    ("1A2g",  "Equipo de transporte",          True,  True,  False,    2.34,
     "Small; below ETS threshold"),
    ("1A2i",  "Mineria",                       True,  True,  True,    69.78,
     "Mining combustion"),
    ("1A2k",  "Construccion",                  True,  True,  False,   20.73,
     "Construction combustion"),
    ("1A2l",  "Textiles y cueros",             True,  True,  False,   49.00,
     "Textiles; below ETS threshold"),
    ("1A2m",  "Industria no especificada",     True,  True,  False,    0.17,
     "Negligible"),
    ("1A4a",  "Comercial/Institucional",       True,  True,  False,  130.97,
     "Commercial stationary combustion"),
    ("1A4c",  "Agropecuario combustion",       True,  True,  False,   10.70,
     "Agricultural fixed combustion"),
    ("1B2b",  "Fugitivas gas natural distrib", True,  False, False,   89.95,
     "Fugitive CH4 from NG distribution; in S but not F (not combustion)"),
    # IPPU -- all in S scope
    ("2A1",   "Cemento proceso CO2",           True,  False, True,   318.04,
     "Process CO2 from calcination; NOT in F (not combustion)"),
    ("2A2",   "Cal proceso CO2",               True,  False, True,     7.37,
     "Process CO2"),
    ("2C1",   "Hierro/acero proceso",          True,  False, True,     3.32,
     "Process CO2"),
    ("2D1",   "Uso lubricantes",               True,  False, False,   19.66,
     "Non-energy CO2 from lubricant use"),
    ("2F1",   "Refrig/AC HFC+HCFC",           True,  False, False,  334.18,
     "ALL HFC in S-only: not combustion (not F), not CO2 (not E)"),
    # --- F-only: transport ---
    ("1A3a",  "Aviacion civil",                False, True,  False,  174.66,
     "Mobile; federal IEPS only"),
    ("1A3b",  "Transporte terrestre",          False, True,  False, 2763.45,
     "Road transport; federal IEPS only"),
    ("1A3c",  "Ferrocarriles",                 False, True,  False,   72.20,
     "Rail diesel; federal only"),
    ("1A3d",  "Navegacion maritima/fluvial",   False, True,  False,  108.97,
     "Marine diesel; federal only"),
    # --- Excluded from S and F ---
    ("1A4b",  "Residencial",                   False, False, False,  219.85,
     "Residential excluded from S; mostly firewood (biogenic)"),
    ("1A5",   "No especificado",               False, False, False,    0.27,
     "Negligible"),
    ("1B2a",  "Gas LP almacenamiento",         False, False, False, 5.83e-4,
     "Negligible"),
    # AFOLU -- excluded
    ("3A",    "Ganado",                        False, False, False, 1028.02,
     "Livestock; excluded from all instruments"),
    ("3C",    "Fuentes agregadas AFOLU",       False, False, False,  515.39,
     "Agriculture non-combustion; excluded"),
    # Waste -- excluded
    ("4A",    "Eliminacion residuos solidos",   False, False, False,  274.03,
     "Solid waste; excluded"),
    ("4C2",   "Incineracion abierta residuos", False, False, False,   18.98,
     "Open burning; excluded"),
    ("4D",    "Aguas residuales",              False, False, False,  489.70,
     "Wastewater; excluded"),
]

SCOPE_COLS = ["ipcc_code", "level", "in_S", "in_F", "in_E_eligible",
              "co2e_gg", "note"]
df_scope = pd.DataFrame(TAX_SCOPE_ROWS, columns=SCOPE_COLS)
df_scope["base_year"] = 2023

# Summary
in_S = df_scope.loc[df_scope["in_S"], "co2e_gg"].sum()
in_F = df_scope.loc[df_scope["in_F"], "co2e_gg"].sum()
total = df_scope["co2e_gg"].sum()

log.info("\n=== Tax scope summary (2023 base) ===")
log.info(f"  Total state emissions: {total:.2f} GgCO2e")
log.info(f"  In Yucatan state tax (S): {in_S:.2f} GgCO2e ({in_S/total*100:.1f}%)")
log.info(f"  In federal IEPS (F, gross): {in_F:.2f} GgCO2e ({in_F/total*100:.1f}%)")
log.info(f"  HFC in S-only: {total_hfc:.2f} GgCO2e ({total_hfc/total*100:.1f}%)")

# ---------------------------------------------------------------------------
# 7. Key derived quantities for 02_estimate.py
# ---------------------------------------------------------------------------

# Electricity non-NG CO2e (taxable by F within electricity)
elec_total = 2971.00
elec_non_ng_co2e = elec_total * non_ng_share_elec
log.info(f"\n=== Electricity taxable fraction ===")
log.info(f"  Total 1A1a: {elec_total:.2f} GgCO2e")
log.info(f"  Non-NG share: {non_ng_share_elec*100:.1f}%")
log.info(f"  Non-NG CO2e: {elec_non_ng_co2e:.2f} GgCO2e")

# ---------------------------------------------------------------------------
# 8. Save outputs
# ---------------------------------------------------------------------------

df_inv.to_csv(os.path.join(PROCESSED_DIR, "yucatan_inventory_2023.csv"), index=False)
df_fuel.to_csv(os.path.join(PROCESSED_DIR, "yucatan_energy_fuel_2023.csv"), index=False)
df_scope.to_csv(os.path.join(PROCESSED_DIR, "yucatan_tax_scope_2023.csv"), index=False)
df_hfc.to_csv(os.path.join(PROCESSED_DIR, "yucatan_hfc_detail_2023.csv"), index=False)

log.info("\nOutputs written to data/processed/")
log.info("01_clean.py complete.")
