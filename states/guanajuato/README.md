# carbon-overlap — Guanajuato State Carbon Tax × Federal IEPS × Mexico Pilot ETS

## Summary

**State:** Guanajuato, Mexico | **Base year:** 2013 | **Estimation tier:** Tier 3

| Instrument | Scope | Coverage |
|-----------|-------|----------|
| S — Guanajuato state carbon tax | CO₂/CH₄/N₂O, stationary industrial/energy sources | 6,622 GgCO₂e (34.4%) |
| F — Mexico Federal IEPS (Art. 2o-C) | All fossil fuels **except natural gas**, upstream | ~10,477 GgCO₂e (54.4%) |
| E — Mexico Pilot ETS | Facilities ≥ 25,000 tCO₂e/yr, legal scope | ~5,700 GgCO₂e within S scope |

## Central results (2013, GgCO₂e)

| Venn segment | Value | Share of S |
|-------------|-------|-----------|
| S∩F∩E (triple overlap) | 1,734 | 26.2% |
| S∩E only (NG combustion + process N₂O in large facilities) | 3,966 | 59.9% |
| S∩F only (non-NG fuels in small/medium facilities) | 393 | 5.9% |
| S only | 529 | 8.0% |
| **S total** | **6,622** | 100% |

Range (low–high for ETS coverage uncertainty): S∩F∩E: 1,365–2,136 GgCO₂e

## Key structural findings

1. **NG exemption from F is the dominant driver.** The Salamanca refinery (PEMEX) runs
   primarily on natural gas (53.15 PJ), which is exempt from the federal IEPS.
   ~3,085 GgCO₂e of refinery NG combustion falls in S∩E-only (state tax + ETS, not federal).

2. **Process N₂O creates a second S∩E-only segment.** Caprolactama production (85,000 t/yr)
   generates 202.7 GgCO₂e of process N₂O covered by S and E but not F (F is a fuel levy).

3. **No process CO₂ from mineral production.** No cement, no blast furnaces — different from
   Morelos. IPPU is narrowly chemical industry (N₂O) and HFC refrigerants.

4. **HFC (306.8 GgCO₂e) is outside all three instruments** (state tax covers CO₂/CH₄/N₂O only).

5. **Transport (7,068 GgCO₂e) is F-only.** Largest single category outside S/E scope.

## Repository structure

```
states/guanajuato/
├── data/
│   ├── raw/
│   │   ├── guanajuato_sector_emissions_2013.csv      ← from IGCEI 2013 results table (p.51)
│   │   ├── guanajuato_fuel_consumption_pj_2013.csv   ← from Tabla 2 (p.26)
│   │   ├── guanajuato_fuel_co2_by_sector_2013.csv    ← from uncertainty table (pp.68-70)
│   │   └── guanajuato_ippu_activity_2013.csv         ← from Tabla 5 (p.30)
│   └── processed/
│       ├── sector_emissions_clean.csv
│       ├── fuel_fractions_by_sector.csv
│       ├── overlap_estimates.csv                     ← subsector × scenario detail
│       ├── overlap_summary.csv                       ← aggregate by scenario
│       └── validation_report.txt
├── scripts/
│   ├── 01_clean.py     ← ingest raw, validate vs inventory totals, compute fuel fractions
│   ├── 02_estimate.py  ← three-instrument Venn overlap estimation (Tier 3)
│   └── 03_outputs.py   ← publication tables + figures
├── outputs/
│   ├── tables/
│   │   ├── guanajuato_overlap_summary.csv
│   │   └── guanajuato_subsector_detail.csv
│   └── figures/
│       ├── guanajuato_venn_overlap.png
│       ├── guanajuato_coverage_by_sector.png
│       └── guanajuato_state_coverage_pie.png
└── docs/
    ├── data_sources.md
    ├── assumptions_02.md      ← full documentation of all assumptions
    └── methodology.md
```

## Running the pipeline

```bash
cd states/guanajuato
pip install pandas matplotlib numpy  # or use repo requirements.txt
python scripts/01_clean.py
python scripts/02_estimate.py
python scripts/03_outputs.py
```

## Assumptions and uncertainties

See `docs/assumptions_02.md` for full documentation of all parameters.

Key uncertain parameters:
- ETS coverage of manufacturing (central 65%, range 50–80%)
- Ladrilleras fossil fuel fraction (central 50%, range 30–70%)

All results presented as central estimate + low–high scenario range.

## Source

Primary inventory: IGCEI Guanajuato 2013, Instituto de Ecología del Estado.
Instrument design: Ley de Cambio Climático para el Estado de Guanajuato y sus Municipios (2013);
Mexico IEPS Art. 2o-C; SEMARNAT Pilot ETS documentation.

---
*World Bank Climate Change Group | State & Trends of Carbon Pricing (internal working paper)*
