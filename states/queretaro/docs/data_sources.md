# Data Sources — Queretaro Carbon Pricing Overlap Analysis

## Primary Source

**Inventario de Emisiones de Gases y Compuestos de Efecto Invernadero del Estado de Queretaro, Ano Base 2021**
- Publisher: Secretaria de Desarrollo Sustentable (SEDESU), Gobierno del Estado de Queretaro
- Date: Diciembre 2023
- Base year: 2021
- Methodology: IPCC 2006 Guidelines
- GWPs: AR5 (CO2=1, CH4=28, N2O=265, HCFC-141b=725, HCFC-22=1810, SF6=23,500)
- Tier levels: Predominantly Tier 2; Tier 1 for livestock enteric fermentation, metal industry, and HFC refrigeration

### Key Tables Used

| Table | Content | Used in |
|-------|---------|---------|
| Table 3 | GWP values (AR5) | Validation |
| Table 4 | Estimation tiers by category | Methodology notes |
| Table 5 | Municipal emissions by category | Cross-validation of totals |
| Table 7 | Calorific values of fuels (MJ/bl) | Fuel fraction derivation |
| Table 8 | Energy balance by sector (PJ) | Sector energy allocation |
| Table 9 | Fuel consumption percentages | State fuel mix |
| Table 10 | Electricity generation fuel (PJ) by municipality | [1A1] NG fraction + plant ETS |
| Table 11 | Industrial fuel consumption (PJ) by type | [1A2] NG fraction calculation |
| Table 12 | Road transport fuel by municipality (PJ) | [1A3] NG fraction |
| Table 13 | Energy emissions by subcategory (GgCO2e) | Inventory leaf values |
| Table 14 | IPPU emissions by subcategory | IPPU leaf values |
| Table 16 | AFOLU emissions by subcategory | AFOLU leaf values |
| Table 19 | Waste emissions by subcategory | Waste leaf values |
| Table 21 | Uncertainties by category | Low/high scenario calibration |

## Emission Factors

- CO2 emission factors: INECC 2014 (Mexico-specific factors for different fuel types)
- CH4 and N2O emission factors: DOF 2015 / IPCC 2006 default values
- GWPs: IPCC AR5 (Table 3 of inventory)
- For fuel fraction calculations: NG=57,755; Diesel=72,851; LP=63,100; Combustoleo=77,400; Coque=97,500; Gasolinas=69,300 (all kgCO2/TJ)

## Energy Data

- Comision Reguladora de Energia (CRE): Electricity generation permits and fuel consumption
- Secretaria de Energia (SENER): Balance Nacional de Energia 2021, SIE data
- SEMARNAT: Cedulas de Operacion Anual (COA) — federal and state jurisdiction
- SEDESU: State-level COA data

## Supplementary Sources

- INEGI: Population (2020 census), economic data, vehicle fleet registry
- CONAFOR: Forest fire data for biomass burning estimates
- SAGARPA/SEDEA: Agricultural production, livestock population
- CEA: Wastewater treatment data
- SIAP: Agricultural activity data for fertilizer application
