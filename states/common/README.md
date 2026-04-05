# Cross-State Analysis Infrastructure

This directory contains the cross-state analytical infrastructure for the Mexico CPI overlap analysis: EDGAR gridded emissions time-series, EDGAR vs state inventory comparisons, and time-series coverage computations for all 12 state-level CPIs.

## EDGAR vs State Inventory Comparison Methodology

### Data Sources

- **EDGAR**: EDGAR 2025 GHG v8.0 gridded emission NetCDF files (0.1deg resolution, ton/cell/year) masked to GADM Level 1 state boundaries via spatial point-in-polygon assignment.
- **State inventories**: Each state's published GHG inventory (varying base years, 2005-2023).

### Sector Mapping

Both EDGAR sectors and state inventory IPCC 2006 codes are mapped to **13 standardized comparison categories**:

| Category | IPCC Code | EDGAR Sectors |
|---|---|---|
| Electricity | 1.A.1.a | ENE |
| Refining/transformation | 1.A.1.bc | REF_TRF |
| Manufacturing | 1.A.2 | IND |
| Transport | 1.A.3 | TRO, TNR_Aviation_*, TNR_Other, TNR_Ship |
| Buildings/other | 1.A.4 | RCO |
| Fugitive | 1.B | PRO_FFF |
| IPPU minerals | 2.A | NMM |
| IPPU chemicals | 2.B | CHE |
| IPPU metals | 2.C | IRO, NFE |
| IPPU products | 2.D-2.G | NEU, PRU_SOL |
| Livestock | 3.A | ENF, MNM |
| Cropland/soils | 3.C | AGS, AWB, N2O |
| Waste | 4 | SWD_LDF, SWD_INC, WWT |

All totals **exclude LULUCF** (3.B) and EDGAR's **IDE** (indirect NOx/NH3 emissions).

### Key Findings

**Sectors where EDGAR aligns well with inventories** (0.5-2.0x ratio in most states):
- **Transport** -- road network proxy is robust
- **Electricity** -- point-source locations known
- **Buildings** -- population-based proxy reliable
- **Cropland/soils** -- cropland area data good

**Sectors where EDGAR is systematically unreliable at state level**:
- **Waste/landfills** -- global waste model doesn't capture subnational infrastructure (ranges from 0.16x to 27x across states)
- **Manufacturing** -- industrial proxies miss state specialization (0.21x to 2.71x)
- **Livestock** -- EDGAR uses FAO-based grids that don't match Mexican census data (0.44x to 5.78x)

**States with fundamental EDGAR limitations**:
- **CDMX** -- 11 grid cells cannot represent a dense 9M-person city (transport at 0.16x)
- **Colima** -- 19-year gap between 2005 inventory and 2024 EDGAR makes comparison meaningless

### Comparable-Scope Totals and Ratios

From `edgar_vs_inventory_totals.csv` (comparable scope excludes categories absent in either source):

| State | Inventory Year | Inventory (KtCO2e) | EDGAR (KtCO2e) | Ratio |
|---|---|---|---|---|
| Queretaro | 2021 | 10,590 | 8,561 | **1.02x** |
| Tamaulipas | 2013 | 36,692 | 38,145 | **1.04x** |
| Guanajuato | 2013 | 20,919 | 21,853 | **1.05x** |
| San Luis Potosi | 2014 | 23,331 | 25,064 | **1.07x** |
| Morelos | 2014 | 5,703 | 4,995 | **0.88x** |
| Yucatan | 2023 | 10,426 | 12,429 | **1.19x** |
| Estado de Mexico | 2019 | 36,385 | 26,930 | **0.74x** |
| Zacatecas | 2024 | 7,057 | 5,303 | **0.75x** |
| CDMX | 2020 | 19,855 | 8,197 | **0.41x** |
| Colima | 2015 | 16,815 | 4,624 | **0.28x** |
| Durango | 2022 | 13,153 | 52,019 | **3.95x** |

Best alignment: Queretaro (1.02x), Tamaulipas (1.04x), Guanajuato (1.05x). Spatial resolution failure: CDMX (0.41x). Inventory age gap: Colima (0.28x). Durango outlier (3.95x) driven by livestock sector divergence.

## Time-Series Coverage Methodology

### Anchored Extrapolation

For states with usable inventories, emissions are estimated as:

```
emissions(sector, year) = inventory(sector, inv_year) x [EDGAR(sector, year) / EDGAR(sector, inv_year)]
```

The **inventory provides the absolute level**; **EDGAR provides year-to-year growth rates** at the 13-category level.

### Special Cases

| State | Method | Reason |
|---|---|---|
| Zacatecas | EDGAR direct | No state inventory available |
| Baja California | EDGAR direct | No state inventory available |
| Colima | EDGAR direct | Inventory too old (2005, 19-year gap) |
| CDMX | Inventory static | EDGAR spatial resolution inadequate (11 grid cells) |

### Three-Instrument Overlap

Coverage is computed as the three-instrument overlap **S x F x E** applied per sector per year:

- **F** (Federal carbon tax): active from **2014** (all years in analysis window)
- **E** (Mexico Pilot ETS): active from **2020** (Zacatecas 2017-2019 = two-instrument overlap only)
- **S** (State CPI): active from each state's CPI start date

**Baja California**: 100% S subset of F overlap, net additional coverage = 0. CPI abolished 2021.

### Instrument Activation Dates

| CPI | State | S Active From |
|---|---|---|
| Tax_MX_ZA | Zacatecas | 2017 |
| Tax_MX_BC | Baja California | 2020 |
| Tax_MX_Queretaro | Queretaro | 2022 |
| Tax_MX_SoMexico | Estado de Mexico | 2022 |
| Tax_MX_TA | Tamaulipas | 2022 |
| Tax_MX_Yucatan | Yucatan | 2022 |
| Tax_MX_Guanajuato | Guanajuato | 2023 |
| Tax_MX_Durango | Durango | 2024 |
| Tax_MX_Colima | Colima | 2025 |
| Tax_MX_MC | CDMX | 2025 |
| Tax_MX_MO | Morelos | 2025 |
| Tax_MX_SLP | San Luis Potosi | 2025 |

## Key Assumptions

1. **S/F/E share parameters** (NG shares, ETS threshold coverage) held static across all years
2. **EDGAR growth rates** applied at the 13-category level, not individual EDGAR sector level
3. **E instrument inactive before 2020** -- Zacatecas 2017-2019 is two-instrument overlap only
4. **All totals exclude LULUCF** (3.B) and IDE (5.A)
5. **Baja California**: 100% S subset of F overlap, net additional = 0
6. **CDMX**: no EDGAR growth rate applied (spatial resolution inadequate)
7. **Colima**: EDGAR direct (19-year inventory gap)
8. **San Luis Potosi**: inventory is 2007-2014 annual average; EDGAR 2014 used as anchor year
9. **Future improvements**: dynamic NG shares from SENER time-series; facility-level RETC data for ETS threshold refinement

## Latest Coverage Results Summary

From `coverage_summary_by_cpi.csv` -- all 12 CPIs ranked by gross S coverage at latest available year:

| CPI ID | State | Latest Year | Total (KtCO2e) | Gross S (KtCO2e) | Gross S % | Dedup Union (KtCO2e) | Dedup % | Data Source |
|---|---|---|---|---|---|---|---|---|
| Tax_MX_SLP | San Luis Potosi | 2024 | 27,935 | 17,793 | 63.7% | 22,082 | 79.1% | inventory_anchored |
| Tax_MX_TA | Tamaulipas | 2024 | 31,633 | 18,786 | 59.4% | 25,963 | 82.1% | inventory_anchored |
| Tax_MX_MO | Morelos | 2024 | 6,322 | 3,278 | 51.9% | 5,547 | 87.7% | inventory_anchored |
| Tax_MX_SoMexico | Estado de Mexico | 2024 | 37,135 | 18,211 | 49.0% | 27,490 | 74.0% | inventory_anchored |
| Tax_MX_Yucatan | Yucatan | 2024 | 11,118 | 5,423 | 48.8% | 8,569 | 77.1% | inventory_anchored |
| Tax_MX_Queretaro | Queretaro | 2024 | 11,647 | 4,867 | 41.8% | 8,246 | 70.8% | inventory_anchored |
| Tax_MX_Durango | Durango | 2024 | 14,630 | 6,046 | 41.3% | 8,915 | 60.9% | inventory_anchored |
| Tax_MX_Guanajuato | Guanajuato | 2024 | 22,033 | 7,812 | 35.5% | 14,914 | 67.7% | inventory_anchored |
| Tax_MX_BC | Baja California | 2021 | 19,834 | 4,917 | 24.8% | 10,790 | 54.4% | edgar_direct |
| Tax_MX_Colima | Colima | 2024 | 4,878 | 946 | 19.4% | 1,864 | 38.2% | edgar_direct |
| Tax_MX_MC | CDMX | 2024 | 19,888 | 3,525 | 17.7% | 17,120 | 86.1% | inventory_static |
| Tax_MX_ZA | Zacatecas | 2024 | 7,057 | 1,060 | 15.0% | 3,931 | 55.7% | edgar_direct |

## File Inventory

| File | Description |
|---|---|
| `extract_edgar_inventory_years.py` | Extracts EDGAR sector-level emissions from NetCDF grids for each state's inventory base year using GADM masks |
| `edgar_vs_inventory_comparison.py` | Compares EDGAR vs state inventory at 13-category level; produces sector and totals CSVs |
| `04_timeseries_coverage.py` | Computes annual three-instrument (S x F x E) coverage for all 12 CPIs using anchored extrapolation |
| `edgar_state_timeseries.csv` | EDGAR sector-level emissions by state, 2017-2024 (KtCO2e) |
| `edgar_inventory_comparison_years.csv` | EDGAR sector-level emissions at each state's inventory base year |
| `edgar_vs_inventory_sector_comparison.csv` | Side-by-side sector comparison: inventory vs EDGAR at 13 categories |
| `edgar_vs_inventory_totals.csv` | State-level totals with ex-LULUCF and comparable-scope ratios |
| `sector_coverage_matrix.csv` | Binary matrix: which of 13 categories are present per state inventory |
| `coverage_timeseries.csv` | Full annual time-series of S/F/E overlap segments for all 12 CPIs |
| `coverage_summary_by_cpi.csv` | Summary table: latest-year coverage for each CPI |
| `README.md` | This file |

## Data Sources

- **EDGAR 2025 GHG v8.0** (JRC, September 2025). Crippa, M., et al. "EDGAR v8.0 Greenhouse Gas Emissions." European Commission, Joint Research Centre (JRC). Available at: https://edgar.jrc.ec.europa.eu/dataset_ghg80
- **GADM v4.1** Mexico Level 1 administrative boundaries shapefile
- **State GHG inventories**:
  - Queretaro: PEACC inventory, base year 2021
  - CDMX: Inventario de Emisiones de la CDMX, base year 2020
  - Durango: State GHG inventory, base year 2022
  - Morelos: State GHG inventory, base year 2014
  - Guanajuato: PEACC inventory, base year 2013
  - Tamaulipas: PEACC inventory, base year 2013
  - San Luis Potosi: State GHG inventory, 2007-2014 annual average
  - Estado de Mexico: IEEGyCEI-2022, base year 2019
  - Yucatan: State GHG inventory, base year 2023
  - Colima: State GHG inventory, base year 2005 (not used -- too old)
- **FY26 projection workbook** for national EDGAR data and federal instrument parameters
