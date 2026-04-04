# CDMX — Carbon Pricing Overlap Analysis

## Summary

Three-instrument Venn decomposition estimating deduplicated GHG emissions coverage from the CDMX state carbon tax, Federal IEPS carbon tax, and Mexico Pilot ETS.

| Metric | Central | Range |
|--------|---------|-------|
| **Total CDMX GHG (2020)** | 19,888 GgCO₂eq | — |
| **Gross S (CDMX tax)** | 3,525 GgCO₂eq (17.7%) | — |
| **Gross F (IEPS)** | 13,624 GgCO₂eq (68.5%) | 13,605 – 13,653 |
| **Gross E (Pilot ETS)** | 355 GgCO₂eq (1.8%) | 228 – 482 |
| **Deduplicated union** | 17,120 GgCO₂eq (86.1%) | 17,117 – 17,124 |
| **Uncovered** | 2,768 GgCO₂eq (13.9%) | 2,765 – 2,772 |

### Key Overlaps
| Overlap | Central | Note |
|---------|---------|------|
| S∩F∩E | 4.5 GgCO₂eq (0.0%) | Negligible — NG exemption + small ETS |
| S∩F only | 23.9 GgCO₂eq (0.1%) | Very small — almost all stationary fuel is NG |
| S∩E only | 350.0 GgCO₂eq (1.8%) | Large NG-burning facilities in ETS scope |

## Key Findings

1. **Transport dominates CDMX emissions (67%)** — overwhelmingly F-only coverage. The CDMX state tax does not cover mobile sources.

2. **NG exemption from F is extreme** — Natural gas provides 99.4% of industrial and 99.8% of commercial fossil energy in CDMX. This creates near-complete separation between S and F in stationary sectors, with the S∩F overlap below 30 GgCO₂eq.

3. **S∩E is the only meaningful overlap** (~350 GgCO₂eq) — large NG-burning facilities covered by both the state tax (on all GHGs) and the ETS (on CO₂), but not by the federal tax (NG-exempt).

4. **S-only is the dominant S segment (89%)** — driven by industria no regulada (2,399 GgCO₂eq), which are thousands of small NG-burning establishments below the ETS threshold and using NG (exempt from F).

5. **Uncovered emissions (13.9%)** are primarily: residential NG combustion (1,671 GgCO₂eq), waste CH₄ (529 GgCO₂eq), emisiones domésticas (275 GgCO₂eq), and livestock/agriculture (30 GgCO₂eq).

## Estimation Tier

**Tier 3** — Fuel-fraction estimation for F, Pareto/threshold estimation for E. No facility-level registry data available.

## Base Year

**2020** (COVID-affected — GDP fell 5–43% by sector). No extrapolation applied.

## Directory Structure

```
states/cdmx/
├── 01_clean.py               # Data extraction, validation, fuel fractions
├── 02_estimate.py             # Three-instrument Venn decomposition
├── 03_outputs.py              # Publication figures and tables
├── data/
│   ├── raw/
│   │   ├── cdmx_ghg_inventory_2020.csv
│   │   ├── cdmx_fuel_consumption_2020.csv
│   │   └── cdmx_facility_counts_2020.csv
│   └── processed/
│       ├── cdmx_inventory_clean.csv
│       ├── cdmx_fuel_fractions.csv
│       ├── cdmx_overlap_results.csv
│       └── cdmx_validation_report.txt
├── outputs/
│   ├── figures/
│   │   ├── cdmx_venn_segments.png
│   │   └── cdmx_coverage_summary.png
│   └── tables/
│       ├── cdmx_overlap_full_table.csv
│       └── cdmx_overlap_summary.csv
└── docs/
    ├── data_sources.md
    ├── assumptions_02.md
    ├── methodology.md
    └── README.md
```

## Usage

```bash
python 01_clean.py      # Extract and validate inventory data
python 02_estimate.py   # Compute overlap estimates
python 03_outputs.py    # Generate figures and tables
```

## Data Source

Inventario de Emisiones de la Zona Metropolitana del Valle de México 2020, Sedema (2023). CDMX entity-level data from Annex Tables 9 and 67–69.
