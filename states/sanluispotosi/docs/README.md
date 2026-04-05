# San Luis Potosi -- Carbon Pricing Overlap Analysis

**State & Trends of Carbon Pricing -- World Bank Climate Change Group**

## Overview

Three-instrument overlap analysis for the State of San Luis Potosi, Mexico:
- **S** -- SLP state carbon tax (CO2, CH4, N2O, HFCs, PFCs, black carbon, CFCs, HCFCs; fixed sources, productive processes)
- **F** -- Federal IEPS carbon tax (fossil fuels except natural gas)
- **E** -- Mexico Pilot ETS (facilities >= 25,000 tCO2e/yr)

**Base year:** Annual average 2007-2014 (cumulative inventory / 8) | **Estimation tier:** Tier 3
**GWPs:** AR5 (CH4=28, N2O=265) -- converted from SAR (CH4=21, N2O=310)

## Distinctive Features

- **Cumulative inventory:** 8-year totals divided by 8 for annual averages (no per-year breakdowns)
- **SAR->AR5 conversion:** Only state requiring GWP conversion; all others use AR5 natively
- **Highest non-NG electricity:** Villa de Reyes combustoleo plant gives NG fraction ~43% (vs. 99%+ in other states)
- **Highest non-NG industry:** GLP=53%, NG=35%, diesel=12%; non-NG=65% (highest of all states)
- **Large cement/cal sector:** ~2,555 GgCO2e/yr process CO2 (in S,E not F)
- **No HFC data:** Inventory reports only CO2, CH4, N2O; S coverage understated
- **Old base year:** 2014 most recent; no extrapolation to present (flagged as future step)
- **No coverage threshold:** All fixed-source productive emissions covered (payment exemption below 300 tCO2e/yr does not remove coverage obligation)
- **Scope 1 confirmed:** Primary legislation explicitly states "direct emissions from fixed sources"

## Directory Structure

```
sanluispotosi/
  data/
    raw/
      INVENTARIO_GEI_SLP_2017_V.5._2019.pdf.pdf  # Source PDF
    processed/
      slp_inventory_annual_ar5.csv      # Validated inventory (AR5, annual avg)
      slp_fuel_fractions.csv            # NG/ETS fractions per category
      slp_facility_detail.csv           # RETC facility-level data
      slp_tax_scope.csv                 # Scope mapping + Venn segments
      slp_overlap_estimates.csv         # Final overlap estimates
  scripts/
    01_clean.py    # Inventory extraction, SAR->AR5 conversion, annual avg
    02_estimate.py # Scope mapping, Venn decomposition
    03_outputs.py  # Publication figures and tables
  outputs/
    figures/
      slp_venn_segments.png
      slp_coverage_summary.png
    tables/
      slp_overlap_summary.csv
      slp_overlap_full_table.csv
  docs/
    data_sources.md     # Primary data sources and tables used
    assumptions_02.md   # Assumptions log (SAR->AR5, cumulative, no HFC, scope 1)
    methodology.md      # Full methodology note
    README.md           # This file
```

## Usage

Run scripts sequentially:

```bash
cd states/sanluispotosi
python scripts/01_clean.py
python scripts/02_estimate.py
python scripts/03_outputs.py
```

## Data Source

Inventario Estatal de Gases de Efecto Invernadero de San Luis Potosi (IEGEI-SLP), 2007-2014, v5. UASLP / SEGAM / VariClim, 2019. IPCC 2006 methodology, SAR GWPs (converted to AR5).
