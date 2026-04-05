# Zacatecas — Methodology

## Overview

This analysis estimates the deduplicated GHG emissions coverage of three overlapping carbon pricing instruments in Zacatecas, Mexico. It is part of the broader Mexico state-level CPI overlap analysis for the State & Trends of Carbon Pricing (S&T) publication.

## Estimation Tier

**Tier 3** — EDGAR v8.0 gridded spatial disaggregation with GADM Level 1 state boundary mask.

Upgraded from Tier 4 (proxy allocation of national data). Zacatecas is unique among the 11 Mexican states with carbon taxes: it has **no published state GHG inventory**. The EDGAR gridded approach provides spatially explicit sector-level emissions without requiring proxy-based allocation assumptions.

## Three-Stage Pipeline

### Stage 1: EDGAR Gridded Inventory Construction (01_clean.py)

1. Load the 26 EDGAR 2025 GHG v8.0 gridded NetCDF files (0.1° resolution, tonnes CO₂e per cell per year, AR5 GWP-100)
2. Load the GADM v4.1 Mexico Level 1 shapefile and isolate the Zacatecas state polygon
3. Construct a boolean mask: for each 0.1° grid cell in the Zacatecas bounding box, test whether the cell center falls within the state polygon using Shapely `contains_xy`
4. Result: 665 cells (~66,500 km²) inside Zacatecas (vs. official 72,275 km²; 7.8% edge-cell shortfall)
5. For each sector NetCDF, extract the bounding-box sub-grid, apply the mask, and sum all masked cell values
6. Assign broad emission categories (ELECTRICITY, TRANSPORT, AFOLU, etc.) and uncertainty bounds (low/high multipliers per category)
7. Output: sector-level inventory with central/low/high estimates in KtCO₂e

**Key difference from Tier 4:** Emissions are extracted directly from EDGAR's spatial gridding rather than allocated from national totals using GDP/population proxies. EDGAR's gridding methodology uses point-source databases, road networks, population density, land-use maps, and other spatial proxies at the global level, providing a more rigorous spatial disaggregation than single-factor state-level proxies.

### Stage 2: Overlap Estimation (02_estimate.py)

For each EDGAR sector, determine the coverage share of each instrument:

- **S share**: Whether the sector contains fixed-source emissions covered by the state carbon tax. Determined by the tax's legal scope (fixed sources, full Kyoto basket gases, no facility threshold). Mobile sources, AFOLU, and waste are excluded.
- **F share**: The fraction of sector emissions from non-natural-gas fossil fuel combustion. Determined by the sector's fuel mix and the federal IEPS natural gas exemption. Key parameter: natural gas share per sector (from ProAire 2018).
- **E share**: The fraction of sector emissions from facilities above the 25,000 tCO₂e/yr ETS threshold. Estimated as a range (30/50/70%) with sector-specific adjustments for facility size distribution.

Compute eight Venn segments using inclusion-exclusion:
```
S∩F∩E = min(s, f, e) × sector_total
S∩E_only = [min(s,e) - min(s,f,e)] × sector_total
S∩F_only = [min(s,f) - min(s,f,e)] × sector_total
S_only = [s - min(s,f) - min(s,e) + min(s,f,e)] × sector_total
F∩E_only = [min(f,e) - min(s,f,e)] × sector_total
F_only = [f - min(s,f) - max(0, min(f,e) - min(s,f,e))] × sector_total
E_only = [e - min(s,e) - max(0, min(f,e) - min(s,f,e))] × sector_total
Uncovered = [1 - min(1, s+f+e - min(s,f) - min(s,e) - min(f,e) + min(s,f,e))] × sector_total
```

Aggregate across all 26 EDGAR sectors to obtain state-level instrument coverage and overlap.

Range estimates combine inventory uncertainty (low/high bounds per sector) with ETS threshold uncertainty (30/50/70%) to produce low/central/high coverage estimates.

### Stage 3: Outputs (03_outputs.py)

Generate three publication-quality figures:
1. **Venn segments bar chart**: Eight overlap segments showing the composition of covered vs. uncovered emissions
2. **Instrument coverage with error bars**: Gross S, F, E, and deduplicated union with low/high ranges
3. **Inventory breakdown pie chart**: Emissions by broad category (AFOLU, TRANSPORT, etc.)

Generate three summary tables:
1. **Overlap table**: Segment-level KtCO₂e and percentages
2. **Range table**: Low/central/high for total, gross S/F/E, and deduplicated union
3. **Sector detail**: Per-sector instrument shares and Venn segment allocations

## Key Methodological Choices

### Why EDGAR gridded (Tier 3) instead of proxy allocation (Tier 4)?

The previous approach allocated national EDGAR sector totals to Zacatecas using single-factor proxies (GDP share, population share, sector-specific indicators). This had several weaknesses:
- Proxy shares were assumed constants with wide uncertainty
- No spatial grounding — the same proxy could over- or under-allocate depending on sector
- Total estimate (8,790 KtCO₂e) could not be independently validated

The EDGAR gridded approach:
- Uses EDGAR's own spatial allocation methodology, which combines multiple proxy layers (point sources, road density, population, land use, nightlights) for each sector
- Provides 0.1° spatial resolution within the state boundary
- Produces a total (7,145 KtCO₂e) that can be cross-validated against RENE facility data and revenue-implied coverage
- Eliminates the need for state-level proxy share assumptions

### Natural gas share determination

The ProAire 2018 emissions inventory lists fuel types for each combustion category. Industrial combustion in Zacatecas uses LPG and diesel with **no natural gas listed**, suggesting very low NG penetration. This is consistent with Zacatecas's semi-arid interior location and limited pipeline infrastructure. A conservative 15% NG share is assumed for manufacturing.

### HFC and SF₆ treatment

Zacatecas's carbon tax covers the full Kyoto basket including SF₆ — broader than most Mexican states. HFCs from commercial/industrial refrigeration at fixed installations are included in S coverage (40% of total HFC/product-use emissions). SF₆ from electrical equipment falls in S-only (not covered by F or E).

### RCO (buildings) split

The RCO sector (1.A.4, buildings) is split into three sub-sectors for instrument coverage:
- Commercial/institutional (30%): fixed sources, covered by S
- Residential (50%): not fixed sources, excluded from S
- Agricultural combustion (20%): fixed sources, covered by S
- Overall S share for RCO: 0.50

## Comparison with Other States

| Feature | Zacatecas | Guanajuato | CDMX | Yucatan |
|---------|-----------|------------|------|---------|
| State inventory | **None** | 2013 | 2020 | 2023 |
| Tier | **3 (gridded)** | 3 | 3 | 3 |
| NG share (industry) | **15%** | ~70% | ~99% | ~93% |
| Key industry | **Mining** | Automotive | Services | Cement |
| Gas scope | **Full Kyoto+SF₆** | CO₂/CH₄/N₂O | CO₂/CH₄/N₂O | Full Kyoto |
| Facility threshold | **None** | None | None | None |

## Limitations and Caveats

1. **EDGAR gridding uncertainty**: EDGAR's spatial allocation relies on global proxy datasets that may not perfectly reflect Zacatecas's sub-state emission distribution. The 0.1° resolution (~11 km) smooths point-source emissions.
2. **Edge-cell shortfall**: 7.8% area mismatch between the GADM polygon mask (66,500 km²) and official state area (72,275 km²) may systematically undercount emissions at state borders.
3. **No facility-level validation**: Without a state GHG inventory or comprehensive RETC data, sector-level emissions cannot be validated against bottom-up facility reports.
4. **Single-year snapshot**: EDGAR 2024 data is used as representative of the current period; year-to-year variability is not captured.
5. **Revenue cross-check gap**: The model's gross S (1,060 KtCO₂e) is below the revenue-implied coverage (2,216 KtCO₂e), suggesting either spatial underallocation, broader practical tax scope, or back-tax effects.
