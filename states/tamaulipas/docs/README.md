# Tamaulipas — Carbon Pricing Overlap Analysis

## Overview

Three-instrument Venn overlap estimation for Tamaulipas state:
- **S**: Tamaulipas state carbon tax (≥25,000 tCO₂e/yr threshold)
- **F**: Federal IEPS carbon tax (NG-exempt)
- **E**: Mexico Pilot ETS (≥25,000 tCO₂e/yr threshold)

Estimation tier: **Tier 3** (threshold/Pareto + fuel-fraction methods)

## Key Feature: Dual Threshold

Unlike all other states in this analysis, Tamaulipas state carbon tax has a **legal coverage threshold of 25,000 tCO₂e/yr** — the same as the federal ETS. Only ~36 companies are covered. This makes S and E near-identical in coverage (same facilities), with the overlap structure determined by sector scope differences rather than threshold differences.

## Data

- **Base year:** 2013 (PECC Tamaulipas inventory)
- **Target year:** 2025 (BaU projection from Table III)
- **GWP conversion:** SAR (CH₄=21, N₂O=310) → AR5 (CH₄=28, N₂O=265)
- **Source:** Programa Estatal de Cambio Climático Tamaulipas 2015-2030

## Pipeline

```
scripts/01_clean.py     → Extract inventory, SAR→AR5, fuel fractions, BaU projections
scripts/02_estimate.py  → Scope mapping, dual-threshold Venn decomposition
scripts/03_outputs.py   → Publication figures and CSV tables
```

Run in order:
```bash
cd states/tamaulipas/scripts
python 01_clean.py
python 02_estimate.py
python 03_outputs.py
```

## Outputs

- `data/processed/tamaulipas_inventory_2013_ar5.csv` — Full inventory with AR5 GWPs
- `data/processed/tamaulipas_fuel_fractions_2013.csv` — NG/non-NG fractions by sector
- `data/processed/tamaulipas_bau_projections.csv` — Table III growth ratios
- `data/processed/tamaulipas_scope_2025.csv` — Detailed scope mapping
- `data/processed/tamaulipas_overlap_estimates.csv` — Final Venn estimates
- `outputs/figures/tamaulipas_venn_segments_2025.png` — Segment bar chart
- `outputs/figures/tamaulipas_coverage_summary_2025.png` — Instrument comparison
- `outputs/tables/tamaulipas_overlap_summary.csv` — Summary table
- `outputs/tables/tamaulipas_overlap_full_table.csv` — Full publication table

## Documentation

- `docs/data_sources.md` — All data sources with table references
- `docs/assumptions_02.md` — Detailed assumption log (SAR→AR5, thresholds, fuel fractions)
- `docs/methodology.md` — Full methodology note
