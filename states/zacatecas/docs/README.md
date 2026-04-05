# Zacatecas — CPI Overlap Analysis

## Summary

| Parameter | Value |
|-----------|-------|
| **State** | Zacatecas |
| **Estimation Tier** | **Tier 3** — EDGAR v8.0 gridded spatial disaggregation |
| **Base data** | EDGAR 2025 GHG v8.0, 0.1° gridded emissions (ton/cell/year), masked to GADM Level 1 Zacatecas boundary. 665 grid cells, ~66,500 km² |
| **GWPs** | AR5 (CH₄=28, N₂O=265) |
| **Instruments** | S (state carbon tax) × F (federal IEPS) × E (Mexico pilot ETS) |
| **Gas scope (S)** | CO₂, CH₄, N₂O, HFC, PFC, SF₆ (full Kyoto basket) |
| **Facility threshold (S)** | None — all fixed sources |
| **Tax rate** | MXN 250/tCO₂e |
| **In force** | 2017 (operational from 2020 post-SCJN ruling) |

## Key Results (Central Estimate)

| Metric | KtCO₂e | % of Total |
|--------|--------|------------|
| Total state emissions | 7,145 | 100% |
| Gross S (state tax) | 1,060 | 14.8% |
| Gross F (federal tax) | 3,520 | 49.3% |
| Gross E (ETS) | 244 | 3.4% |
| **Deduplicated union** | **3,931** | **55.0%** |
| Uncovered | 3,215 | 45.0% |

### Low / Central / High Range

| Estimate | Total | Gross S | Gross F | Gross E | Dedup Union | Dedup % |
|----------|-------|---------|---------|---------|-------------|---------|
| Low      | 5,235 |   740   | 2,753   |   105   |  3,025      | 57.8%   |
| Central  | 7,145 | 1,060   | 3,520   |   244   |  3,931      | 55.0%   |
| High     | 9,055 | 1,381   | 4,286   |   440   |  4,836      | 53.4%   |

## Methodology

### EDGAR Gridded Extraction (Tier 3)

Emissions are extracted directly from EDGAR 2025 GHG v8.0 gridded NetCDF files at 0.1° spatial resolution. Each file contains annual emissions in tonnes per grid cell for a single EDGAR sector (e.g., `EDGAR_2025_GHG_GWP_100_AR5_GHG_2024_ENE_emi.nc`). The extraction process:

1. Load the GADM v4.1 Mexico Level 1 shapefile and isolate the Zacatecas state polygon
2. Construct a 0.1° grid matching the EDGAR lat/lon coordinates (cell centers at -89.95 to 89.95, -179.95 to 179.95)
3. Clip the grid to the Zacatecas bounding box and create a boolean mask of cells whose centers fall within the state boundary (665 cells, ~66,500 km² vs. official 72,275 km² — a 7.8% edge-cell shortfall)
4. For each of the 26 EDGAR sector NetCDF files, extract the sub-grid, apply the mask, and sum all cell values to obtain the sector total in tonnes CO₂e
5. Convert to KtCO₂e (÷1,000)

This replaces the earlier Tier 4 proxy-based approach (national EDGAR totals allocated to Zacatecas using GDP/population proxies), providing spatially explicit emissions grounded in EDGAR's bottom-up gridding methodology.

### Three-Instrument Overlap Framework

Three carbon pricing instruments potentially apply to emissions within Zacatecas:

- **S (State carbon tax)**: Covers all fixed-source emissions across the full Kyoto basket (CO₂, CH₄, N₂O, HFC, PFC, SF₆). No facility-size threshold. Excludes mobile sources, AFOLU, and waste.
- **F (Federal IEPS carbon tax)**: Upstream fuel levy on fossil fuel combustion CO₂, covering all fuels **except natural gas**. Applies to both mobile and fixed sources. Does not cover process emissions, AFOLU, or waste.
- **E (Mexico pilot ETS)**: Covers direct CO₂ from facilities emitting ≥25,000 tCO₂e/yr. Limited to CO₂ only (not CH₄/N₂O/HFCs). Coverage estimated as 30% (low) / 50% (central) / 70% (high) of eligible fixed-source emissions.

For each EDGAR sector, coverage shares (s, f, e ∈ [0,1]) are assigned based on the instrument's legal scope. Eight Venn segments are computed via inclusion-exclusion to obtain the deduplicated union coverage.

### Natural Gas Share Assumptions

Source: ProAire Zacatecas 2018-2028 (criteria pollutant inventory, base year 2016).

| Sector | NG Share | Basis |
|--------|----------|-------|
| Electricity (ENE) | 60% | National CFE generation mix |
| Refining (REF_TRF) | 40% | Transformation/distribution |
| Manufacturing (IND) | 15% | ProAire confirms LPG/diesel dominant, no NG listed |
| Commercial (RCO) | 30% | Some NG in commercial buildings |
| Residential (RCO) | 10% | Predominantly LPG + leña |
| Agricultural (RCO) | 5% | Minimal NG use |

### ETS Threshold Coverage

Without facility-level data, ETS coverage is estimated as a range:
- **Low (30%)**: Conservative — few facilities above 25,000 tCO₂e/yr in a mining-dominated, dispersed economy
- **Central (50%)**: Moderate — some large power, refining, and mining combustion facilities
- **High (70%)**: Upper bound — assumes consolidation of mining energy use at large operations

## Unique Characteristics of Zacatecas

- **Only state among the 11 without a published GHG inventory** — EDGAR gridded data is the primary emissions source. No IGEI exists for cross-validation at the sector level.

- **AFOLU (40%) + transport (37%) dominate** — both largely outside state tax scope. Agriculture (enteric fermentation 1,200 KtCO₂e, agricultural soils 1,336 KtCO₂e) and road transport (2,492 KtCO₂e) together account for 77% of state emissions, but AFOLU is uncovered by all instruments and transport is excluded from the state tax.

- **F-only segment (2,870 KtCO₂e, 40%) is the dominant overlap category** — road transport is covered by the federal fuel tax but excluded from the state carbon tax and ETS. This makes Zacatecas heavily reliant on the federal instrument for carbon price coverage.

- **Near-zero IPPU process emissions despite being Mexico's #1 silver and #1 zinc producer** — mining emissions appear as energy use (IND/ENE sectors), not as process emissions (IRO = 0, NFE = 1.2 KtCO₂e). EDGAR classifies combustion at mining/smelting operations under manufacturing energy, so the mining sector's carbon footprint is embedded in IND and ENE rather than IPPU.

- **Low NG penetration in industry** — ProAire 2018 confirms LPG/diesel-dominant industrial combustion. This means F covers ~85% of manufacturing combustion CO₂ (vs. <50% in NG-heavy states like CDMX or Guanajuato).

- **Revenue cross-check gap**: Gross S from the model (1,060 KtCO₂e) vs. revenue-implied coverage (~2,216 KtCO₂e from MXN 554M at MXN 250/tCO₂e). Possible explanations:
  - EDGAR spatial underallocation: the 7.8% edge-cell shortfall reduces gridded totals relative to true state emissions
  - Broader practical tax scope than our conservative scope-1-only interpretation (e.g., some mobile-source or waste emissions may be taxed in practice)
  - Cumulative back-tax collection from the 2017-2019 legal challenge period (the tax was enacted in 2017 but faced SCJN challenges; 2021 revenue may include arrears)

## Cross-Validation

| Source | KtCO₂e | Notes |
|--------|--------|-------|
| **EDGAR gridded (this analysis)** | **7,145** | 26 sectors, 665 cells, Tier 3 |
| RENE 2018 (facility-level) | 1,917 – 3,138 | Federal reporting threshold; covers only large emitters |
| Revenue-implied 2021 | ~2,216 | MXN 554M ÷ MXN 250/tCO₂e; only S-covered emissions |
| Previous proxy estimate (Tier 4) | 8,790 | Now superseded by EDGAR gridded approach |

The EDGAR gridded total (7,145 KtCO₂e) is 18.7% lower than the earlier proxy estimate (8,790 KtCO₂e), primarily because EDGAR's spatial allocation places fewer transport and energy emissions within the Zacatecas polygon than the GDP/population proxies assumed. The RENE and revenue-implied figures are subsets (facility-level and S-covered only) and are consistent with the gridded total.

## File Structure

```
states/zacatecas/
├── scripts/
│   ├── 01_clean.py                  # EDGAR gridded inventory → sector-level emissions table
│   ├── 02_estimate.py               # Three-instrument overlap estimation (S × F × E)
│   ├── 03_outputs.py                # Publication figures and summary tables
│   └── extract_edgar_zacatecas.py   # Standalone EDGAR NetCDF extraction utility
├── data/
│   ├── raw/                         # (no raw state data — EDGAR gridded serves as primary source)
│   └── processed/
│       ├── zacatecas_edgar_gridded_emissions.csv   # Raw EDGAR sector sums (26 sectors, KtCO₂e)
│       ├── zacatecas_edgar_inventory.csv           # Inventory with uncertainty bounds
│       ├── zacatecas_inventory_summary.csv          # Category-level summary
│       ├── zacatecas_reference_data.csv             # Cross-validation reference values
│       ├── zacatecas_overlap_sectors.csv             # Per-sector instrument shares + Venn segments
│       ├── zacatecas_overlap_summary.csv             # Aggregate Venn segment totals
│       ├── zacatecas_overlap_ranges.csv              # Low/central/high range estimates
│       └── zacatecas_synthetic_inventory.csv         # Legacy proxy-based inventory (superseded)
├── outputs/
│   ├── figures/
│   │   ├── zacatecas_venn_segments.png              # Eight overlap segments bar chart
│   │   ├── zacatecas_instrument_coverage.png        # Instrument coverage with error bars
│   │   └── zacatecas_inventory_breakdown.png        # Emissions pie chart by broad category
│   └── tables/
│       ├── zacatecas_overlap_table.csv              # Publication-ready overlap summary
│       ├── zacatecas_range_table.csv                # Low/central/high range table
│       └── zacatecas_sector_detail.csv              # Sector-level detail with shares
└── docs/
    ├── README.md                    # This file
    ├── data_sources.md              # Data provenance and citations
    ├── assumptions_02.md            # Detailed assumptions for overlap estimation
    └── methodology.md              # Technical methodology documentation
```

## Potential Improvements

1. **RETC facility data**: Download from datos.gob.mx to identify actual large emitters in Zacatecas and validate ETS threshold assumptions
2. **EDGAR subnational time series (2020-2023)**: Extract annual gridded totals to assess emission trends and temporal stability of the 2024 snapshot
3. **SIE state energy data**: Cross-validate electricity consumption and fuel sales by state from the SENER portal
4. **SENER state-level fuel consumption**: Verify the 15% NG share assumption for manufacturing against official fuel balance data
5. **RETC + RENE reconciliation**: Match facility-level reported emissions against EDGAR gridded cells to quantify point-source vs. area-source contributions
