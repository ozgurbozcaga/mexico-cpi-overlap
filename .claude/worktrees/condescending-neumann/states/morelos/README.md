# Morelos Carbon Pricing Overlap Analysis

Case: Mexico Morelos State Carbon Tax x Federal IEPS Carbon Tax x Mexico Pilot ETS
Estimation tier: Tier 3 (process split + fuel fraction + Pareto threshold)
Base year: 2014 | Target years: 2025, 2026
Status: Complete — pipeline runs end-to-end

WARNING: 2014 base year (11-year extrapolation); HFCs/PFCs/SF6 absent from inventory.
Results are MORE UNCERTAIN than Colima (2015) or Durango (2022).

## Key Results (2025, Central Estimate)

| Instrument | GgCO2e | % of state | Range |
|-----------|---------|------------|-------|
| S Morelos state tax | 2,374 | 37.7% | 1,815-2,990 |
| F Federal IEPS tax | 4,195 | 66.5% | 3,181-5,282 |
| E Pilot ETS | 1,383 | 21.9% | 901-1,938 |
| Union S+F+E | 5,513 | 87.4% | 4,319-7,450 |

State total (extrapolated 2025): ~6,306 GgCO2e

### Venn segments (2025 central)

| Segment | GgCO2e | % | Content |
|---------|---------|---|---------|
| S_F_E | 563 | 8.9% | Cement combustion (petcoke/FO) at large plants |
| S_E only | 820 | 13.0% | CEMENT CALCINATION process CO2 — in S and ETS, not taxed by F |
| S_F only | 493 | 7.8% | Taxable fuels at small manufacturing facilities |
| S only | 498 | 7.9% | NG combustion; commercial; HFC data gap |
| F only | 3,139 | 49.8% | Mobile transport (road gasoline/diesel; aviation; rail) |
| Uncovered | 792 | 12.6% | Biogenic wood CO2; livestock CH4; ag burning; wastewater |

## Key Structural Findings

1. Cement calcination creates a unique S∩E-only segment (~820 GgCO2e). Process CO2 from limestone decomposition (CaCO3 → CaO + CO2) is in scope for the state tax and ETS, but the federal IEPS fuel tax does NOT apply to process emissions. This segment is absent in Colima and Durango.

2. Natural gas exemption barely matters here. NG is only 3.3% of industrial combustion CO2 (vs 99.6% in Durango). The federal tax gap in Morelos is driven by process emissions, not NG.

3. Biogenic wood combustion (~626 GgCO2e, 11% of state) inflates the state total denominator but is unpriced by any instrument.

4. HFCs/PFCs/SF6 absent from inventory — S coverage understated by estimated 3-4%.

5. 2014 base year: ranges should be treated as illustrative, not precise projections.

## Repository Structure

    states/morelos/
    data/raw/
        morelos_ghg_inventory_2014.csv   (from Annex II/IV of 2014 air quality inventory)
        morelos_fuel_consumption_2014.csv (from Cuadro 3 of inventory)
    data/processed/
        morelos_inventory_2014.csv
        morelos_fuel_fractions_2014.csv
        morelos_cement_process_split_2014.csv
        morelos_tax_scope_2014.csv
        morelos_extrapolated_2025_2026.csv
        morelos_overlap_estimates.csv
    scripts/
        01_clean.py
        02_estimate.py
        03_outputs.py
    outputs/figures/
        morelos_venn_segments_2025_2026.png
        morelos_coverage_summary_2025_2026.png
    outputs/tables/
        morelos_overlap_summary.csv
        morelos_overlap_full_table.csv
    docs/
        data_sources.md
        assumptions_02.md
        methodology.md
    README.md

## Running the Pipeline

    cd states/morelos
    pip install pandas matplotlib numpy
    python scripts/01_clean.py
    python scripts/02_estimate.py
    python scripts/03_outputs.py

## Data Source

Inventario de Emisiones Contaminantes a la Atmosfera, Morelos, 2014.
SDS Morelos / SEMARNAT / INECC / LT Consulting / Molina Center. Published January 2017.
GWPs: AR5 (CH4=28, N2O=265). Original units: Mg/year. Converted to GgCO2e.

## Key Assumptions to Flag for Review

1. Cement process/combustion split: 60/40 national average assumed (INECC/IPCC 2006); Morelos-specific clinker data would sharpen this — highest-impact assumption
2. HFCs absent: S coverage understated; estimated gap ~3-4% of state
3. 2014 base: 11-year extrapolation; ranges are very wide
4. ETS coverage per subsector: Tier 3 Pareto estimation; COA registry data would move this to Tier 2
5. Biogenic wood CO2 included in state total denominator; not in any instrument numerator

See docs/assumptions_02.md for full derivations.
