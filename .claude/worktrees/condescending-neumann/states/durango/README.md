# Durango Carbon Pricing Overlap Analysis

Case: Mexico Durango State Carbon Tax x Federal IEPS Carbon Tax x Mexico Pilot ETS
Estimation tier: Tier 3 (fuel-fraction + Pareto threshold)
Base year: 2022 | Target years: 2025, 2026
Status: Complete

## Key Results (2025, Central Estimate)

| Instrument | GgCO2e | % of state | Range |
|-----------|---------|------------|-------|
| S Durango state tax | 4,550 | 34.2% | 4,247-4,785 |
| F Federal IEPS tax | 3,402 | 25.6% | 3,119-3,645 |
| E Pilot ETS | 3,996 | 30.0% | 3,545-4,367 |
| Union S+F+E | 7,531 | 56.6% | 6,714-8,197 |

State total (extrapolated 2025): ~13,297 GgCO2e

### Venn segments (2025 central)

| Segment | GgCO2e | % | Content |
|---------|---------|---|---------|
| S_F_E | 210 | 1.6% | Electricity diesel/FO; manuf. taxable at large plants |
| S_E only | 3,786 | 28.5% | Electricity NG (99.6% of [1A1]) at power plants — DOMINANT |
| S_F only | 211 | 1.6% | Manufacturing non-NG fuels at small facilities |
| S only | 343 | 2.6% | HFCs, fugitives, small-facility NG |
| F only | 2,981 | 22.4% | Transport [1A3] road, rail, aviation |
| Uncovered | 5,766 | 43.4% | Livestock, land non-CO2, waste, NG residential |

## Key Structural Findings

1. No NG exemption makes a large difference. Unlike the federal tax and the Colima state tax, the Durango state tax covers natural gas. Because NG = 99.6% of electricity CO2, the state tax reaches ~3,300 GgCO2e the federal tax misses entirely. The dominant Venn segment is S_E (NG at large power plants), not S_F.

2. Transport is F-only. Road, rail, and aviation (~2,900 GgCO2e, 21.9% of state) are under the federal tax only; the state tax explicitly exempts transport.

3. Livestock and land dominate the uncovered share. ASOUT = ~37% of state; all exempt from all three instruments.

4. ETS figures are legal-scope upper bounds. Non-binding pilot phase.

## Repository Structure

    states/durango/
    data/raw/
        durango_ghg_inventory_2022.csv
        durango_fuel_consumption_2022.csv
    data/processed/
        durango_inventory_2022.csv
        durango_fuel_fractions_2022.csv
        durango_power_plant_detail_2022.csv
        durango_tax_scope_2022.csv
        durango_extrapolated_2025_2026.csv
        durango_overlap_estimates.csv
    scripts/
        01_clean.py
        02_estimate.py
        03_outputs.py
    outputs/figures/
        durango_venn_segments_2025_2026.png
        durango_coverage_summary_2025_2026.png
    outputs/tables/
        durango_overlap_summary.csv
        durango_overlap_full_table.csv
    docs/
        data_sources.md
        assumptions_02.md
        methodology.md
    README.md

## Running the Pipeline

    cd states/durango
    pip install pandas matplotlib numpy
    python scripts/01_clean.py
    python scripts/02_estimate.py
    python scripts/03_outputs.py

## Data Source

Inventario Estatal de Emisiones de GEI, Durango, Base Year 2022
Centro Mario Molina para Estudios Estrategicos sobre Energia y Medio Ambiente A.C.
Commissioned by SRNMA Durango, 2024.
GWPs: AR5 (CH4=28, N2O=265). IPCC 2006 + 2019 Refinement methodology.

## Key Assumptions to Flag for Review

1. Durango state tax NG in scope: confirmed from inventory policy references; full legal text not independently verified
2. [1A2] NG fraction = 71% of fossil CO2: derived from Figure 13 energy shares; key sensitivity for F coverage
3. [1A2j] lumber ETS fraction = 40%: distributed sawmills; widest uncertainty range
4. ETS = legal scope, not operational coverage (non-binding pilot)
5. New Lerdo CC plant 350 MW (2024): not yet reflected; update when operational data available

See docs/assumptions_02.md for full derivation of all parameters.
