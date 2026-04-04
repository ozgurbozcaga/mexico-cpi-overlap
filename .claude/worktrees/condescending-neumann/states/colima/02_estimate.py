"""
=============================================================================
Case:            Mexico State Carbon Pricing — Colima
Script:          02_estimate.py
Estimation tier: Tier 3 (stationary combustion via INECC sector growth rates
                 applied to 2015 base inventory; natural gas exemption
                 applied explicitly at fuel level)
                 Tier 4 for uncertainty bounds (energy balance cross-check)
Base year:       2015 (IMADES/Under2 Coalition inventory)
Target years:    2025, 2026 (Colima state carbon tax implementation)
GWPs:            AR5 (CH4=28, N2O=265) — consistent across base and INECC
Author:          mexico-cpi-overlap project
=============================================================================

Approach
--------
For each in-scope subsector, apply a compound annual growth rate (CAGR)
derived from INECC INEGYCEI national sector trends (2015-2022 published
data, extrapolated to 2025/2026 using linear trend).

Sector CAGR sources:
  Electricity (stationary): INECC INEGYCEI 2022 Table 1A1, Mexico national
    electricity sector. Colima's plant is a single large facility; SENER
    generation data shows CFE thermoelectric output declining nationally
    as combined-cycle + renewables displace oil/diesel generation.
    --> Conservative central estimate: flat to slight decline on diesel
        fraction; NG share roughly stable. Use -1.5%/yr ± 10% uncertainty.

  Manufacturing/industry: INECC 1A2 national trend. Post-COVID recovery
    2021-2023; moderate growth. Mexico industrial energy use +1.2%/yr
    over 2015-2022. Colima-specific: cement (Apasco) and steel (Peña
    Colorada) are key drivers.
    --> Central: +1.2%/yr ± 15% uncertainty.

  Residential/commercial/agriculture: National LP gas and diesel trends
    from SENER prospects. Slow growth tied to population.
    --> Central: +0.8%/yr ± 20% uncertainty.

Natural gas exemption
---------------------
Applied at source: NG combustion is excluded from both federal and state
tax scope. For the electricity sector, only the diesel+fuel oil fraction
is carried through to the taxable coverage estimate. The NG fraction is
tracked separately and reported as "exempt overlap."

Overlap structure (Colima state tax × federal carbon tax)
----------------------------------------------------------
The federal carbon tax is upstream (applied to fossil fuel importers/
distributors). It covers all fuels taxed by the Colima state tax.
Therefore: federal ∩ state = state tax scope (100% overlap on in-scope
fuels). The overlap is the state tax coverage itself.

Overlap structure (Colima state tax × Mexico Pilot ETS)
--------------------------------------------------------
ETS covers facilities >25,000 tCO2e/yr in energy and industry sectors.
Colima facilities likely in ETS: Manzanillo thermoelectric, Peña Colorada/
Las Encinas iron pellet plants, possibly Cementos Apasco.
However: Mexico Pilot ETS has no binding financial obligation (pilot phase).
Legal and operational coverage diverge. Results flagged accordingly.

Outputs (to data/processed/ and outputs/tables/)
-------------------------------------------------
  colima_extrapolated_{year}.csv   — subsector emissions by target year
  colima_overlap_estimates.csv     — overlap table: point + low + high
  colima_overlap_summary.csv       — summary by instrument pair and year
=============================================================================
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

PROCESSED_DIR  = os.path.join(os.path.dirname(__file__), "data", "processed")
TABLES_DIR     = os.path.join(os.path.dirname(__file__), "outputs", "tables")
os.makedirs(TABLES_DIR, exist_ok=True)

BASE_YEAR    = 2015
TARGET_YEARS = [2025, 2026]

# ---------------------------------------------------------------------------
# 1. Load cleaned data
# ---------------------------------------------------------------------------
df_scope = pd.read_csv(os.path.join(PROCESSED_DIR, "colima_tax_scope_2015.csv"))
df_inv   = pd.read_csv(os.path.join(PROCESSED_DIR, "colima_inventory_2015.csv"))

# ---------------------------------------------------------------------------
# 2. Sector growth rates (CAGR) and uncertainty bands
#    Source: INECC INEGYCEI 2022 national sector trends; SENER BEN 2022;
#            IMF/INEGI Mexico GDP growth for industrial proxy (2022-2026 outlook)
#    Uncertainty: ±1 sigma range expressed as multiplier applied to CAGR
#    Each row: (subsector_pattern, cagr_central, cagr_low, cagr_high, note)
# ---------------------------------------------------------------------------

# Group subsectors into growth-rate classes
GROWTH_MAP = {
    # --- Electricity generation ---
    # Manzanillo thermoelectric: diesel fraction declining as CFE national
    # dispatch favours NG combined-cycle. SENER 2022 shows Manzanillo plant
    # generation declining modestly. Diesel consumption at plant has been
    # cut significantly post-2018 (fuel-switching to NG). Central estimate:
    # flat total plant output but diesel fraction shrinking.
    # For the TAXABLE fraction (diesel+FO only): higher negative rate.
    "electricity_taxable": dict(
        cagr_central=-0.020,   # -2.0%/yr on taxable fraction
        cagr_low    =-0.080,   # pessimistic: faster diesel phase-out
        cagr_high   = 0.010,   # optimistic: diesel persists
        note="Manzanillo plant diesel fraction; NG exempt. "
             "SENER shows progressive diesel reduction at CFE thermoelectrics."
    ),
    "electricity_ng_exempt": dict(
        cagr_central= 0.002,   # near-flat, slight NG growth
        cagr_low    =-0.030,
        cagr_high   = 0.030,
        note="NG fraction — EXEMPT from both taxes. Tracked for total plant accounting."
    ),

    # --- Manufacturing: cement ---
    # Cementos Apasco Tecomán: national cement production +1.0%/yr 2015-2022
    # (CANACEM data). Post-COVID infrastructure spending pushes demand.
    "manuf_cement": dict(
        cagr_central= 0.012,
        cagr_low    =-0.020,
        cagr_high   = 0.030,
        note="CANACEM national cement production trend 2015-2022."
    ),

    # --- Manufacturing: food/beverage ---
    # INECC 1A2e national +1.5%/yr 2015-2022; Colima agro-industry tied
    # to sugar, coconut, lime processing.
    "manuf_food": dict(
        cagr_central= 0.015,
        cagr_low    =-0.010,
        cagr_high   = 0.035,
        note="INECC 1A2e national trend; Colima agro-industry."
    ),

    # --- Manufacturing: metallurgical (iron pellets) ---
    # Peña Colorada + Las Encinas production linked to global steel demand.
    # Mexico iron ore exports +0.8%/yr 2015-2022 (SE/Minería data).
    "manuf_metal": dict(
        cagr_central= 0.008,
        cagr_low    =-0.050,   # high downside: mine exhaustion, market
        cagr_high   = 0.030,
        note="INECC 1A2a; Colima pelletizing plants production trend."
    ),

    # --- Manufacturing: non-metallic minerals (largest manuf subsector) ---
    # Construction materials tied to national construction GDP.
    # INECC 1A2f +1.3%/yr 2015-2022.
    "manuf_nonmetal": dict(
        cagr_central= 0.013,
        cagr_low    =-0.020,
        cagr_high   = 0.035,
        note="INECC 1A2f national non-metallic minerals trend."
    ),

    # --- Manufacturing: other/chemical/petrochem ---
    # General industrial proxy +1.0%/yr.
    "manuf_other": dict(
        cagr_central= 0.010,
        cagr_low    =-0.020,
        cagr_high   = 0.030,
        note="General industrial proxy (INECC 1A2m)."
    ),

    # --- Residential/commercial/agriculture ---
    # LP gas demand tied to population growth (~1.1%/yr in Colima 2015-2025
    # CONAPO). Partial offset from efficiency improvements.
    "residential_commercial": dict(
        cagr_central= 0.008,
        cagr_low    =-0.010,
        cagr_high   = 0.020,
        note="SENER LP gas prospects; Colima population growth."
    ),
}

# Map scope subsectors to growth class
SUBSECTOR_TO_GROWTH = {
    "Electricity generation":          "electricity_taxable",  # taxable fraction applied separately
    "Energy generation plants":        "manuf_other",           # biogas — near-zero anyway
    "Manuf — Cement and lime":         "manuf_cement",
    "Manuf — Food and beverage":       "manuf_food",
    "Manuf — Metallurgical":           "manuf_metal",
    "Manuf — Non-metallic minerals":   "manuf_nonmetal",
    "Manuf — Other industries":        "manuf_other",
    "Manuf — Petroleum/petrochem":     "manuf_other",
    "Manuf — Chemical":                "manuf_other",
    "Manuf — Hazardous waste treat":   "manuf_other",
    "Residential":                     "residential_commercial",
    "Commercial":                      "residential_commercial",
    "Agriculture/forestry/fishing":    "residential_commercial",
}

# ---------------------------------------------------------------------------
# 3. Electricity sector: split taxable vs exempt fractions
#    Base year diesel+FO fraction of plant CO2e
# ---------------------------------------------------------------------------
# From 01_clean.py calculations:
#   NG share: 82.1% of plant CO2 -> exempt
#   Diesel+FO share: 17.9% -> taxable
# Apply to full electricity co2e_gg_2015 = 7128 GgCO2e

ELEC_TAXABLE_SHARE = 0.179   # diesel + fuel oil share of plant CO2e
ELEC_NG_SHARE      = 1 - ELEC_TAXABLE_SHARE

elec_base_total   = df_scope.loc[
    df_scope["subsector"] == "Electricity generation", "co2e_gg_2015"
].values[0]

elec_base_taxable = elec_base_total * ELEC_TAXABLE_SHARE   # ~1275 GgCO2e
elec_base_ng      = elec_base_total * ELEC_NG_SHARE         # ~5853 GgCO2e

log.info(f"Electricity base: total={elec_base_total:.0f}, "
         f"taxable={elec_base_taxable:.0f}, NG-exempt={elec_base_ng:.0f} GgCO2e")

# ---------------------------------------------------------------------------
# 4. Extrapolation function
# ---------------------------------------------------------------------------

def extrapolate(base_value, cagr, n_years):
    return base_value * (1 + cagr) ** n_years


def extrapolate_with_bounds(base_value, growth_class, n_years):
    g = GROWTH_MAP[growth_class]
    central = extrapolate(base_value, g["cagr_central"], n_years)
    low     = extrapolate(base_value, g["cagr_low"],     n_years)
    high    = extrapolate(base_value, g["cagr_high"],    n_years)
    # Convention: low <= central <= high in terms of CO2e
    # For negative CAGR sectors, low > central (more decay = less CO2e)
    return (
        min(low, central, high),
        central,
        max(low, central, high),
    )

# ---------------------------------------------------------------------------
# 5. Build extrapolated estimates for each target year
# ---------------------------------------------------------------------------

results = []

for year in TARGET_YEARS:
    n = year - BASE_YEAR

    for _, row in df_scope.iterrows():
        subsector = row["subsector"]

        if not row["in_state_tax_scope"]:
            continue  # only extrapolate in-scope subsectors

        if subsector == "Electricity generation":
            # Handle split: taxable (diesel+FO) and exempt (NG) separately
            t_low, t_cen, t_high = extrapolate_with_bounds(
                elec_base_taxable, "electricity_taxable", n)
            ng_low, ng_cen, ng_high = extrapolate_with_bounds(
                elec_base_ng, "electricity_ng_exempt", n)
            # Taxable portion
            results.append({
                "year": year, "subsector": f"{subsector} (diesel+FO — taxable)",
                "base_co2e_gg": elec_base_taxable,
                "co2e_low": round(t_low, 2),
                "co2e_central": round(t_cen, 2),
                "co2e_high": round(t_high, 2),
                "growth_class": "electricity_taxable",
                "in_state_scope": True,
                "overlap_federal": True,
                "overlap_ets": True,
                "note": "Diesel+FO fraction only; NG exempt both taxes",
            })
            # NG exempt portion — tracked but not in overlap
            results.append({
                "year": year, "subsector": f"{subsector} (NG — EXEMPT)",
                "base_co2e_gg": elec_base_ng,
                "co2e_low": round(ng_low, 2),
                "co2e_central": round(ng_cen, 2),
                "co2e_high": round(ng_high, 2),
                "growth_class": "electricity_ng_exempt",
                "in_state_scope": False,  # NG exempt
                "overlap_federal": False,
                "overlap_ets": True,
                "note": "NG fraction — EXEMPT from state and federal carbon taxes",
            })

        else:
            gc = SUBSECTOR_TO_GROWTH.get(subsector)
            if gc is None:
                log.warning(f"No growth class for: {subsector} — skipping")
                continue
            base = row["co2e_gg_2015"]
            low, cen, high = extrapolate_with_bounds(base, gc, n)
            results.append({
                "year": year, "subsector": subsector,
                "base_co2e_gg": base,
                "co2e_low": round(low, 2),
                "co2e_central": round(cen, 2),
                "co2e_high": round(high, 2),
                "growth_class": gc,
                "in_state_scope": bool(row["in_state_tax_scope"]),
                "overlap_federal": bool(row["overlap_federal_tax"]),
                "overlap_ets": bool(row["overlap_ets_pilot"]),
                "note": row.get("taxable_co2e_gg_note", ""),
            })

df_extrap = pd.DataFrame(results)

# ---------------------------------------------------------------------------
# 6. Overlap estimates by instrument pair and year
# ---------------------------------------------------------------------------

overlap_rows = []

for year in TARGET_YEARS:
    yr_df = df_extrap[df_extrap["year"] == year]

    # --- A. Colima state tax coverage ---
    state_df = yr_df[yr_df["in_state_scope"]]
    state_low = state_df["co2e_low"].sum()
    state_cen = state_df["co2e_central"].sum()
    state_hig = state_df["co2e_high"].sum()

    # --- B. State tax ∩ Federal carbon tax ---
    # All fuels in state scope are also taxed federally (upstream).
    # Overlap = state coverage (full overlap on in-scope fuels).
    fed_state_df = yr_df[yr_df["in_state_scope"] & yr_df["overlap_federal"]]
    fed_state_low = fed_state_df["co2e_low"].sum()
    fed_state_cen = fed_state_df["co2e_central"].sum()
    fed_state_hig = fed_state_df["co2e_high"].sum()

    # --- C. State tax ∩ Pilot ETS ---
    # ETS covers large emitters (>25,000 tCO2e/yr threshold).
    # In-scope subsectors also in ETS: electricity (diesel fraction),
    # metallurgical, cement (combustion portion).
    ets_state_df = yr_df[yr_df["in_state_scope"] & yr_df["overlap_ets"]]
    ets_state_low = ets_state_df["co2e_low"].sum()
    ets_state_cen = ets_state_df["co2e_central"].sum()
    ets_state_hig = ets_state_df["co2e_high"].sum()

    # --- D. Federal tax coverage of Colima (for context) ---
    # Federal tax covers all taxed fuels in Colima including road transport.
    # Road transport is in federal scope but not state scope.
    # We estimate road transport for reference using manuf_other growth class.
    road_base = df_scope.loc[
        df_scope["subsector"] == "Transport — Road", "co2e_gg_2015"
    ].values[0]
    road_low, road_cen, road_hig = extrapolate_with_bounds(
        road_base, "manuf_other", year - BASE_YEAR)

    # Note: natural gas in federal scope is also exempt
    # Federal coverage in Colima = state scope + road transport (approx)
    fed_colima_cen = state_cen + road_cen
    fed_colima_low = state_low + road_low
    fed_colima_hig = state_hig + road_hig

    # --- E. Total state emissions (for coverage share calc) ---
    # Approximate by growing total 2015 emissions at blended rate
    # (dominated by electricity sector)
    total_2015 = 18137  # GgCO2e net
    # Blended growth ~ electricity (83% of total) + small sectors
    total_cen = extrapolate(total_2015, 0.000, year - BASE_YEAR)   # flat central
    total_low = extrapolate(total_2015, -0.010, year - BASE_YEAR)
    total_hig = extrapolate(total_2015,  0.015, year - BASE_YEAR)

    for label, low, cen, hig, coverage_note in [
        ("Colima state tax — total coverage",
         state_low, state_cen, state_hig,
         "Stationary combustion (taxed fuels only; NG exempt)"),

        ("Colima state tax ∩ Mexico federal carbon tax",
         fed_state_low, fed_state_cen, fed_state_hig,
         "100% overlap: all fuels in state scope also taxed upstream by federal tax"),

        ("Colima state tax ∩ Mexico Pilot ETS (legal)",
         ets_state_low, ets_state_cen, ets_state_hig,
         "Large stationary emitters (electricity diesel, metallurgical); "
         "ETS is non-binding pilot — legal/operational coverage diverges"),

        ("Mexico federal carbon tax — Colima coverage (context)",
         fed_colima_low, fed_colima_cen, fed_colima_hig,
         "Approx: state scope + road transport; excludes NG"),

        ("Colima total state emissions (context)",
         total_low, total_cen, total_hig,
         "Approximate: 2015 base extrapolated at blended sector rates"),
    ]:
        share_low = low / total_hig * 100   # conservative share
        share_cen = cen / total_cen * 100
        share_hig = hig / total_low * 100   # high share

        overlap_rows.append({
            "year": year,
            "instrument_pair": label,
            "co2e_low_gg":     round(low, 1),
            "co2e_central_gg": round(cen, 1),
            "co2e_high_gg":    round(hig, 1),
            "share_state_low_pct":  round(share_low, 1),
            "share_state_cen_pct":  round(share_cen, 1),
            "share_state_high_pct": round(share_hig, 1),
            "tier": "Tier 3 (stationary combustion) / Tier 4 (transport, total state)",
            "note": coverage_note,
        })

df_overlap = pd.DataFrame(overlap_rows)

# ---------------------------------------------------------------------------
# 7. Print summary
# ---------------------------------------------------------------------------

log.info("\n=== COLIMA CARBON PRICING OVERLAP ESTIMATES ===")
for year in TARGET_YEARS:
    log.info(f"\n--- {year} ---")
    yr = df_overlap[df_overlap["year"] == year]
    for _, r in yr.iterrows():
        log.info(
            f"  {r['instrument_pair']}\n"
            f"    Central: {r['co2e_central_gg']:.0f} GgCO2e "
            f"({r['share_state_cen_pct']:.1f}% of state)  "
            f"Range: [{r['co2e_low_gg']:.0f} – {r['co2e_high_gg']:.0f}]"
        )

# ---------------------------------------------------------------------------
# 8. Save outputs
# ---------------------------------------------------------------------------

extrap_path  = os.path.join(PROCESSED_DIR, "colima_extrapolated_2025_2026.csv")
overlap_path = os.path.join(PROCESSED_DIR, "colima_overlap_estimates.csv")
table_path   = os.path.join(TABLES_DIR,    "colima_overlap_summary.csv")

df_extrap.to_csv(extrap_path, index=False)
df_overlap.to_csv(overlap_path, index=False)
df_overlap.to_csv(table_path, index=False)

log.info(f"\nOutputs written:")
for p in [extrap_path, overlap_path, table_path]:
    log.info(f"  {p}")

# ---------------------------------------------------------------------------
# 9. Assumptions log (for methodology note)
# ---------------------------------------------------------------------------

ASSUMPTIONS = """
## Colima Overlap Estimation — Key Assumptions (02_estimate.py)

### Base data
- 2015 inventory (IMADES/Under2 Coalition, published 2019-01-31)
- AR5 GWPs throughout; no GWP conversion required
- Estimation tier: Tier 3 for stationary combustion sectors
  (INECC national sector growth rates applied to 2015 subsector totals)

### Extrapolation (2015 → 2025/2026)
- Electricity sector (Manzanillo plant): split into NG fraction (exempt,
  CAGR ~+0.2%/yr) and diesel+FO fraction (taxable, CAGR -2.0%/yr central).
  The diesel phase-out at CFE thermoelectrics is well-documented in SENER
  prospectiva; -2%/yr is conservative. Range: [-8%/yr, +1%/yr].
- Manufacturing sectors: INECC 1A2 national CAGR 2015-2022 applied by
  subsector class (+0.8% to +1.5%/yr). Range: ±2–3.5pp.
- Residential/commercial/agriculture: LP gas demand tied to Colima
  population growth (~+0.8%/yr). Range: [-1%, +2%/yr].

### Natural gas exemption
- Natural gas is EXEMPT from the Mexico federal carbon tax (Ley del IEPS,
  Artículo 2o-C) and, by design mirroring the federal structure, from
  state carbon taxes.
- The Manzanillo thermoelectric plant burns ~82% NG by CO2 mass.
  Only the diesel+FO fraction (~18%) is subject to either tax.
- This is the largest single driver of the gap between gross emissions
  and taxable coverage in Colima (reduces electricity sector in-scope
  emissions from ~7,128 GgCO2e to ~1,275 GgCO2e at 2015 base).

### Overlap structure
1. State tax × Federal carbon tax: 100% overlap on in-scope fuels.
   Federal tax is upstream (importer/distributor); state tax is downstream
   (end-use stationary source). Same fuels taxed twice. Overlap = state
   coverage exactly.
2. State tax × Pilot ETS: Large stationary emitters only (>25,000 tCO2e/yr
   threshold). Applies to Manzanillo plant (diesel fraction), metallurgical
   facilities. ETS is non-binding pilot — operational coverage likely lower
   than legal scope. Flag results accordingly.

### Uncertainty
- Point estimates are CAGR central values applied to 2015 base.
- Low/high bounds use CAGR low/high (see GROWTH_MAP in script).
- Additional structural uncertainty: Colima state tax design details not
  yet fully published (as of 2025 implementation start). Threshold for
  stationary sources and exact fuel list may differ from Jalisco model.
  This is the dominant source of uncertainty for 2025/2026 estimates.
- Results should be presented as ranges in the methodology note.
"""

assump_path = os.path.join(os.path.dirname(__file__), "docs", "assumptions_02.md")
with open(assump_path, "w", encoding="utf-8") as f:
    f.write(ASSUMPTIONS.strip())
log.info(f"Assumptions log written: {assump_path}")

log.info("02_estimate.py complete.")
