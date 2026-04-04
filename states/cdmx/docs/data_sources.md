# Data Sources — CDMX Carbon Pricing Overlap Analysis

## Primary Source

**Inventario de Emisiones de la Zona Metropolitana del Valle de México 2020**
- Publisher: Secretaría del Medio Ambiente del Gobierno de la Ciudad de México (Sedema)
- Published: 2023
- Base year: 2020
- Coverage: 16 alcaldías (CDMX), 59 municipios (Estado de México), Tizayuca (Hidalgo)
- GWPs: AR5 (CO₂=1, CH₄=28, N₂O=265)
- Gases: CO₂, CH₄, N₂O, HFC; also reports CN (black carbon)
- Local file: `inventario-emisiones-cdmx-2020_pdf.pdf`
- Access date: 2026-04-04

### Tables extracted:
| Table | Content | Pages |
|-------|---------|-------|
| Annex Table 2 | Emissions by entity (CDMX/Edomex/Tizayuca) — criteria + GHG totals | 81 |
| Annex Table 9 | CDMX GHG by source and category (CO₂, CH₄, N₂O, HFC, CO₂eq, CN) | 95–96 |
| Annex Table 10 | CDMX GHG percentage contribution by source/category | 97–98 |
| Annex Table 40 | ZMVM fixed-source facility counts by sector (local/federal) | 132 |
| Annex Table 67 | CDMX gas LP consumption by sector (m³/yr) | 148 |
| Annex Table 68 | CDMX natural gas consumption by sector (m³/yr) | 148 |
| Annex Table 69 | CDMX other fuel consumption (diesel, firewood, charcoal) | 148 |
| Table 2 | ZMVM energy balance by sector (PJ) — contextual | 22 |

## Supplementary Sources

**CDMX Carbon Tax (Impuesto a las Emisiones de Carbono)**
- Jurisdiction: Ciudad de México
- Scope: Direct emissions of CO₂, CH₄, N₂O from stationary sources in commercial, service, and industrial sectors
- Exempt: Transport, aviation, residential
- Source: CDMX official environmental taxation page

**Federal IEPS Carbon Tax**
- Scope: Upstream excise on fossil fuels (combustion CO₂)
- Key exemption: Natural gas
- Source: Ley del Impuesto Especial sobre Producción y Servicios, Art. 2, Fracción I, inciso H

**Mexico Pilot ETS (Sistema de Comercio de Emisiones)**
- Scope: Facilities ≥ 25,000 tCO₂e/yr, energy and industrial sectors
- Status: Pilot phase (non-binding financial obligation)
- Source: SEMARNAT, Acuerdo DOF 2019-10-01

## Energy Conversion Factors

- Net calorific values: Balance Nacional de Energía 2020 (SENER, 2022)
- CO₂ emission factors: IPCC 2006 Guidelines defaults (kg CO₂/TJ)
  - Natural gas: 56,100
  - Gas LP: 63,100
  - Diesel: 74,100

## Notes

- The 2020 inventory reflects COVID-19 pandemic effects (GDP decline of 5–43% by sector). The inventory authors explicitly note this year should not be used for trend analysis or projections.
- Biogenic CO₂ (680,451 t from biomass) is excluded per IPCC convention.
- Indirect emissions (electricity imported from outside ZMVM: ~7.8 Mt) are not included in the territorial inventory.
