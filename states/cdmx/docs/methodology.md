# Methodology — CDMX Carbon Pricing Overlap Analysis

## Overview

This analysis estimates the deduplicated GHG emissions coverage from three overlapping carbon pricing instruments in Ciudad de México (CDMX):

| Instrument | Abbreviation | Type | Scope |
|-----------|-------------|------|-------|
| CDMX state carbon tax | S | Emissions-based tax | CO₂/CH₄/N₂O from stationary commercial/service/industrial sources |
| Federal IEPS carbon tax | F | Upstream fuel excise | Combustion CO₂ from all fossil fuels except natural gas |
| Mexico Pilot ETS | E | Cap-and-trade (pilot) | Direct CO₂ from facilities ≥ 25,000 tCO₂e/yr |

## Estimation Tier

**Tier 3** — Neither instrument has facility-level registry data for direct matching. Overlap is estimated using fuel-mix fractions (for F) and Pareto/threshold analysis (for E), applied to inventory sector totals.

## Base Year and Inventory

- **Base year:** 2020
- **Source:** Inventario de Emisiones de la ZMVM 2020 (Sedema, 2023)
- **Entity scope:** Ciudad de México only (16 alcaldías), extracted from Annex Table 9
- **Total CDMX GHG:** 19,888 GgCO₂eq
- **GWPs:** AR5 (CH₄=28, N₂O=265)
- **COVID caveat:** 2020 is an atypical pandemic year. GDP fell 5–43% depending on sector.

## Three-Instrument Venn Decomposition

### Step 1 — Map Instrument Scope to Inventory Categories

Each inventory category is assigned binary flags for S, F, and E eligibility:

**S scope** (CDMX carbon tax):
- Fuentes puntuales: all manufacturing, electricity generation, regulated commercial/services → YES
- Area combustion: comercial-institucional, industria no regulada → YES
- All other area sources (residential, waste, agriculture, livestock, domestic) → NO
- Mobile sources (road transport, aviation, rail) → NO
- HFCs → NO (tax covers CO₂/CH₄/N₂O only)

**F scope** (IEPS):
- Any source burning fossil fuels (except NG) → YES, for the non-NG fraction only
- Non-combustion emissions (waste CH₄, process, HFC, agriculture N₂O) → NO
- NG combustion → NO (exempt)

**E scope** (Pilot ETS):
- Only fuentes puntuales (regulated facilities that could exceed 25,000 tCO₂e/yr)
- Area sources and mobile sources → NO (below threshold by definition)

### Step 2 — Quantify F Coverage (NG Exemption)

For each S-covered sector, the non-NG fraction of fossil combustion CO₂ is estimated from CDMX-specific fuel consumption data (Annex Tables 67–69):

- Convert all fuels to energy (PJ) using net calorific values from Balance Nacional de Energía
- Compute NG share of total fossil energy by sector
- Apply CO₂ emission factors to estimate NG share of combustion CO₂
- F covers only the non-NG fraction of combustion CO₂

**Result:** Industrial NG share = 99.4%, Commercial = 99.8%. F covers < 1% of stationary combustion in S-covered sectors.

### Step 3 — Quantify E Coverage (ETS Threshold)

For each E-eligible category, estimate the fraction of emissions from facilities above 25,000 tCO₂e/yr:

- Electricity generation: 70% central (50–85% range) — few large plants dominate
- Manufacturing: 30% central (15–50% range) — no heavy industry in CDMX
- Commercial: 2% central (0–5% range) — nearly all below threshold

### Step 4 — Compute Eight Venn Segments

For each category, decompose total emissions into eight mutually exclusive segments:

```
S∩F∩E = CO₂ × f_frac × e_frac           (within S-covered categories)
S∩F   = CO₂ × f_frac × (1 - e_frac)     (within S-covered categories)
S∩E   = CO₂ × e_frac × (1 - f_frac) + non-CO₂ GHG × e_frac
S_only = S_total - S∩F - S∩E - S∩F∩E
F∩E   = 0 (all E-eligible categories are in S)
F_only = CO₂ × f_frac                    (outside S scope)
E_only = 0 (same as F∩E)
Uncov  = total - all covered segments
```

Where:
- `f_frac` = non-NG fraction of combustion CO₂ (varies by sector and scenario)
- `e_frac` = above-threshold facility fraction (varies by category and scenario)
- `S_total` = CO₂ + CH₄×28 + N₂O×265 for S-covered categories

### Step 5 — Derive Union and Gross Coverage

```
Gross S = S∩F∩E + S∩F + S∩E + S_only
Gross F = S∩F∩E + S∩F + F∩E + F_only
Gross E = S∩F∩E + S∩E + F∩E + E_only
Union   = Total - Uncovered
```

## Uncertainty

Three scenarios (central, low, high) are computed by varying:
- Non-NG fuel fractions (±50% around central for industrial/commercial; wider for electricity)
- ETS coverage fractions (range reflects facility-size distribution uncertainty)

The primary source of uncertainty is the ETS threshold allocation for electricity generation and manufacturing. The NG exemption fraction is well-constrained by fuel consumption data.

## Validation

- Inventory extraction validated against known entity totals (Annex Table 2): all source-type subtotals within 0.01% of reported values
- Fuel fractions cross-checked against ZMVM energy balance (Table 2)
- Category assignments manually verified against source descriptions

## Limitations

1. **COVID-2020 baseline:** Emissions are depressed relative to normal years. Coverage shares may not represent typical operations.
2. **Metropolitan inventory scope:** The ZMVM inventory covers the full metropolitan area. CDMX-specific data is extracted from entity-level breakdowns, but some allocation between entities involves modelling assumptions (e.g., fuel consumption allocation from state-level sales data).
3. **No facility-level data:** ETS threshold estimation relies on aggregate sector data and average facility size, not actual facility registries.
4. **Industria no regulada ambiguity:** This is the largest S-covered category (2,399 GgCO₂eq) but represents thousands of small establishments whose individual characteristics are unknown.
5. **Single-year estimate:** No time series or extrapolation is applied (unlike Durango/Colima) since the base year is 2020.
