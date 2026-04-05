# Data Sources -- San Luis Potosi Carbon Pricing Overlap Analysis

## Primary Source

**Inventario Estatal de Gases de Efecto Invernadero de San Luis Potosi (IEGEI-SLP), 2007-2014**
- Publisher: Secretaria de Ecologia y Gestion Ambiental (SEGAM), Universidad Autonoma de San Luis Potosi (UASLP), VariClim
- Version: 5.0 (2019)
- Period: Cumulative 2007-2014 (8 years); no per-year sectoral breakdowns
- Annual average: 23.13 Mt CO2e/yr (SAR GWPs)
- Base year data: 2006 (RETC facility-level data); activity data updated through 2014
- Methodology: IPCC 2006 Guidelines
- GWPs: **SAR (CH4=21, N2O=310)** -- converted to AR5 in our analysis
- Gases: CO2, CH4, N2O only (no HFC/PFC/SF6 data)

### Key Tables Used

| Table | Content | Used in |
|-------|---------|---------|
| Table 1 (pp.15-17) | Cumulative emissions by sector/subsector (Mt, SAR) | Primary inventory data |
| Table 2 (p.20) | Energy sector emissions detail | Energy subsector breakdown |
| Table 4 (p.22) | IPPU emissions by subsector | IPPU data |
| Table 5 (p.23) | IPPU CO2eq pie chart | IPPU subsector shares |
| Table 6 (p.25) | AFOLU emissions by subsector | AFOLU data |
| Table 16 (p.34) | Waste emissions | Waste data |
| Table 19 (pp.38-39) | RETC establishments, SLP municipality (2006) | Facility ETS threshold |
| Table 20 (p.39) | RETC establishments, Cerritos (2006) | Cement facility ETS |
| Table 21 (p.39) | RETC establishments, Soledad de Graciano (2006) | ETS threshold |
| Table 22 (p.40) | RETC establishments, Tamazunchale (2006) | Power plant ETS |
| Table 23 (p.40) | CO2 industrial by municipality summary | Municipal allocation |

## Emission Factors

- CO2: Inventory-reported values (INECC/IPCC 2006 defaults)
- CH4, N2O: Inventory-reported mass values; GWP conversion done in our analysis
- GWP conversion: SAR (CH4=21, N2O=310) -> AR5 (CH4=28, N2O=265)
- Fuel EFs for NG fraction: NG=57,755; Combustoleo=79,450; Diesel=72,851; GLP=63,100 (kgCO2/TJ, INECC)

## Energy Data

- Energy balance from SIE (Sistema de Informacion Energetica, Secretaria de Energia)
- NG consumption: 542.7 PJ statewide (2007-2014 cumulative)
- NG for electricity generation: 422.6 PJ (from energy balance allocation)
- Industrial fuel consumption: GN=6.53 Mt CO2, GLP=9.81 Mt, diesel=2.18 Mt

## Facility-Level Data (RETC, base year 2006)

| Facility/Municipality | Sector | CO2 (kt/yr) | Above 25kt ETS? |
|----------------------|--------|-------------|-----------------|
| Tamazunchale | Electricity (NG CC) | 2,515 | YES |
| Villa de Reyes | Electricity (thermal) | 1,383 | YES |
| Cerritos | Cement/Cal | 1,076 | YES |
| SLP municipality (#20) | Metalurgia | 2,071 | YES |
| SLP municipality (#3) | Celulosa/papel | 81,568 | YES |
| SLP municipality (#16) | Cement/Cal | 61,453 | YES |
| SLP municipality (#21) | Vidrio | 151,320 | YES |

## SLP Carbon Tax Legal Source

- Ley de Hacienda para el Estado de San Luis Potosi
- Art. 36 QUATER through 36 OCTIES (carbon tax provisions)
- Effective: 1 January 2025
- Gas scope: CO2, CH4, N2O, black carbon, CFCs, HCFCs, HFCs, PFCs (NO SF6 -- removed June 2024)
- Source scope: Direct emissions from fixed sources in productive processes (Scope 1 only)
- Threshold: None (all sizes covered; fiscal stimulus exempts payment below 300 tCO2e/yr)

## Supplementary Sources

- SEMARNAT: RETC database (facility-level emissions reporting)
- SAGARPA/SIAP: Agricultural production data (crop burning calculations)
- INEGI: Population data (waste projections)
- SCT/IMT: Transport corridor emissions (Section 2.5 of inventory)
