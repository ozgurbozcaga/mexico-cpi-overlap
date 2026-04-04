# Queretaro — Carbon Pricing Overlap Analysis

**State & Trends of Carbon Pricing — World Bank Climate Change Group**

## Overview

Three-instrument overlap analysis for the State of Queretaro, Mexico:
- **S** — Queretaro state carbon tax (all Kyoto gases, economy-wide fixed sources)
- **F** — Federal IEPS carbon tax (fossil fuels except natural gas)
- **E** — Mexico Pilot ETS (facilities >= 25,000 tCO2e/yr)

**Base year:** 2021 | **Target years:** 2025, 2026 | **Estimation tier:** Tier 3

## Key Results (2025 central)

| Instrument | Coverage | % of state |
|-----------|----------|-----------|
| S (state tax) | ~4,700 GgCO2e | ~42% |
| F (federal) | ~2,900 GgCO2e | ~26% |
| E (pilot ETS) | ~3,700 GgCO2e | ~33% |
| Union S\|F\|E | ~7,100 GgCO2e | ~63% |
| Uncovered | ~4,100 GgCO2e | ~37% |

## Distinctive Features

- **NG dominance:** Electricity ~100% NG, manufacturing ~95.5% NG → federal tax nearly irrelevant for stationary sources
- **All Kyoto gases:** State tax captures HFC refrigeration (70.5 GgCO2e) not covered by F or E
- **Small electricity plant:** Queretaro's small plant (20.2 GgCO2e) falls below ETS threshold → 98.9% not 100%
- **Auto/aero cluster:** Strong concentration (BMW, Safran, Bombardier) raises ETS coverage of manufacturing

## Directory Structure

```
queretaro/
  data/
    raw/
      queretaro_ghg_inventory_2021.csv      # Extracted inventory (leaf codes)
      Inventario-emisiones-...2021.pdf.pdf  # Source PDF (SEDESU 2023)
    processed/
      queretaro_inventory_2021.csv          # Validated inventory with sector labels
      queretaro_fuel_fractions_2021.csv     # NG/ETS fractions per category
      queretaro_power_plant_detail_2021.csv # Plant-level electricity data
      queretaro_tax_scope_2021.csv          # Full scope mapping + Venn segments
      queretaro_extrapolated_2025_2026.csv  # Extrapolated emissions
      queretaro_overlap_estimates.csv       # Final overlap estimates
  scripts/
    01_clean.py    # Inventory extraction, validation, fuel fractions
    02_estimate.py # Scope mapping, Venn decomposition, extrapolation
    03_outputs.py  # Publication figures and tables
  outputs/
    figures/
      queretaro_venn_segments_2025_2026.png
      queretaro_coverage_summary_2025_2026.png
    tables/
      queretaro_overlap_summary.csv
      queretaro_overlap_full_table.csv
  docs/
    data_sources.md     # Primary data sources and tables used
    assumptions_02.md   # Assumptions log for scope mapping
    methodology.md      # Full methodology note
    README.md           # This file
```

## Usage

Run scripts sequentially:

```bash
cd states/queretaro
python scripts/01_clean.py
python scripts/02_estimate.py
python scripts/03_outputs.py
```

## Data Source

Inventario de Emisiones de Gases y Compuestos de Efecto Invernadero del Estado de Queretaro, Ano Base 2021. SEDESU, December 2023. IPCC 2006 methodology, AR5 GWPs, predominantly Tier 2.
