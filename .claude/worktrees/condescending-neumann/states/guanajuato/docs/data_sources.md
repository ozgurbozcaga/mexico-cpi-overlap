# Data Sources — Guanajuato Carbon Pricing Overlap Analysis

## Primary inventory source

**IGCEI Guanajuato 2013**
- Full name: Inventario de Gases y Compuestos de Efecto Invernadero del Estado de Guanajuato
- Author: Instituto de Ecología del Estado (IEE), Gobierno de Guanajuato
- Year: 2013 (base year inventory, published ~2016)
- URL: ecologia.guanajuato.gob.mx
- Methodology: IPCC 2006 guidelines, Levels 1 and 2
- GWPs: AR5 (CH₄=28, N₂O=265, 100-year horizon)
- Accessed: March 2026

**Key tables used:**
| Table | Content | Page |
|-------|---------|------|
| Results table | Emissions by subsector (all gases) | 51 |
| Tabla 2 | Fuel consumption by sector, PJ, 2013 | 26 |
| Tabla 5 | IPPU chemical production activity | 30 |
| Tabla 16 (uncertainty table) | Emissions by fuel type and sector | 68–70 |
| Tabla 4 | Crude oil processed at Salamanca refinery | 27 |
| Tabla 3 | Vehicle fleet by MOVES category | 27 |

## Instrument legal design sources

**Guanajuato state carbon tax:**
- Ley de Cambio Climático para el Estado de Guanajuato y sus Municipios (2013)
- Scope: direct CO₂, CH₄, N₂O emissions from stationary sources in industrial and energy sectors
- Source confirmed by Ozgur (project instructions)

**Federal IEPS carbon tax (F):**
- Ley del Impuesto Especial sobre Producción y Servicios, Art. 2o-C
- Upstream fossil fuel levy on all fuels EXCEPT natural gas
- Administrador: SAT (Servicio de Administración Tributaria)

**Mexico Pilot ETS (E):**
- SEMARNAT Program (pilot phase, non-binding)
- Legal scope: facilities ≥ 25,000 tCO₂e/yr in energy and industrial sectors
- Source: SEMARNAT MRV system documentation; project methodology note

## Derived data sources (not directly available)

**ETS facility coverage fractions (Tier 3 Pareto estimation):**
- Energy industries: Salamanca refinery reference from Tabla 4 (194.5 kbd crude)
- Manufacturing: Bajío automotive cluster knowledge (GM Silao, Mazda Salamanca area)
  and standard Pareto estimate for Mexican industrial states
- Documented in assumptions_02.md

**Ladrilleras fossil fuel fraction:**
- Informed assumption (50% central, range 30–70%)
- Basis: literature on brick kiln fuel use in Mexico (mixed firewood/diesel/LP)
- No facility-level data available for Guanajuato

## Notes on data gaps

1. **Energy industries CO₂ gap**: Uncertainty table lists 4,153 Gg CO₂ from three fuels
   (combustóleo, GN, diesel), but results table shows 4,424 Gg. Gap of ~271 Gg (~6%)
   likely from additional fuel fractions at refinery not individually listed.
   Treatment: fuel fractions applied proportionally from uncertainty table to results-table total.

2. **Commercial sector fuel split**: Only LP and small NG listed in fuel table.
   Commercial sector (176.8 GgCO₂e) is outside S scope so this does not affect overlap estimates.

3. **Multi-year data**: The IGCEI is a single-year base inventory for 2013.
   No time-series trend available from this source alone.

---
*Last updated: March 2026 | Ozgur Bozcaga, World Bank Climate Change Group*
