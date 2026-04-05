# Zacatecas — Data Sources

## Primary Sources

### 1. EDGAR 2025 GHG v8.0 — Gridded Emissions (0.1° NetCDF)

- **Content**: Global gridded GHG emissions at 0.1° × 0.1° resolution (~11 km at equator), by EDGAR sector
- **Format**: NetCDF files, one per sector, variable `emissions` in tonnes CO₂e per cell per year
- **Year**: 2024 data (EDGAR 2025 release)
- **GWPs**: AR5 GWP-100 (CH₄=28, N₂O=265)
- **Sectors extracted**: 26 files covering IPCC 2006 categories 1.A through 5.A
- **Grid**: 1800 × 3600 cells, cell centers at -89.95 to 89.95 lat, -179.95 to 179.95 lon
- **Spatial masking**: GADM v4.1 Mexico Level 1 shapefile used to create a boolean mask of 665 cells within the Zacatecas state boundary (~66,500 km²)
- **Extraction method**: Cell-center-in-polygon test using Shapely `contains_xy`; sum of masked cell values gives sector total in tonnes
- **Citation**: Crippa, M. et al. (2024). EDGAR v8.0 Greenhouse Gas Emissions. European Commission, Joint Research Centre (JRC). https://edgar.jrc.ec.europa.eu/
- **Access**: Downloaded as sector-level zip archives from EDGAR portal, 2024 NetCDF files extracted

### 2. GADM v4.1 — Global Administrative Areas (Mexico Level 1)

- **Content**: Shapefile of Mexico's 32 state boundaries
- **File**: `gadm41_MEX_1.shp` (with .shx, .dbf, .prj, .cpg)
- **Used for**: Defining the Zacatecas state polygon for EDGAR gridded extraction
- **Feature used**: `NAME_1 == "Zacatecas"`
- **Citation**: GADM (2024). Database of Global Administrative Areas, version 4.1. https://gadm.org/
- **Note**: GADM polygon area (~66,500 km² at 0.1° resolution) is 7.8% smaller than the official state area (72,275 km²) due to coastal/border edge-cell effects and polygon simplification

### 3. UK PACT / MEXICO₂ Policy Brief — Zacatecas (November 2023)

- **Content**: Carbon tax design parameters, legal framework, revenue data
- **Key data extracted**:
  - Gas scope: CO₂, CH₄, N₂O, HFC, PFC, SF₆
  - Rate: MXN 250/tCO₂e (flat rate)
  - No facility threshold
  - Revenue: MXN 554 million (2021) → implies ~2,216,000 tCO₂e taxed
  - RENE 2018: 1,916,509 tCO₂e; rising to 3,137,822 tCO₂e
- **Citation**: MEXICO₂ (2023). Reportes de politica publica sobre impuestos al carbono subnacionales en Mexico. Impuesto al carbono del estado de Zacatecas.

### 4. INECC Subnational Climate Policy Report — Zacatecas (2020)

- **Content**: Inventory of 17 climate policy instruments, institutional framework
- **Key finding**: Zacatecas has NO state GHG inventory (IGEI)
- **Citation**: INECC/SEMARNAT (2020). Informacion sobre la implementacion de la politica climatica subnacional: Zacatecas.

### 5. ProAire Zacatecas 2018-2028

- **Content**: Criteria pollutant emissions inventory (base year 2016)
- **Key data extracted**:
  - Industrial profile: cement/lime, metallurgical, non-metallic minerals, automotive
  - Fuel mix: LPG + diesel dominant in industry (low natural gas penetration)
  - No PEMEX refinery, no petrochemicals
  - 11 industrial parks across 5 municipalities
  - Mining is 21.1% of state GDP (#1 silver producer nationally at 45.2%)
- **NOTE**: Contains NO GHG data — criteria pollutants only (PM10, PM2.5, SOx, CO, NOx, COV, NH3)
- **Used for**: Natural gas share assumptions in the overlap model
- **Citation**: SEMARNAT/Gobierno de Zacatecas (2018). Programa de Gestion para Mejorar la Calidad del Aire del Estado de Zacatecas 2018-2028.

## Secondary / Cross-Validation Sources

### 6. INEGI Census and Economic Data

- Population 2020: 1,622,138 (vs national 126,014,024 → 1.29% share)
- State GDP: ~1.3% of national (INEGI PIB por Entidad Federativa, 2021)
- Mining GDP: 21.1% of state GDP; 14.3% per INEGI 2022

### 7. RENE (Registro Nacional de Emisiones)

- 2018 reported: 1,916,509 tCO₂e
- Later year: 3,137,822 tCO₂e
- Covers only facilities above federal COA reporting threshold
- Source: SEMARNAT (2020). Informe de Resultados del RENE 2015-2018.

### 8. Revenue-Implied Coverage Cross-Check

- 2021 revenue: MXN 554 million (Secretaria de Finanzas del Estado de Zacatecas, 2022)
- At MXN 250/tCO₂e → ~2,216,000 tCO₂e implied taxed emissions
- Provides independent floor estimate for S-covered emissions

## Data NOT Available

- **State GHG inventory**: Does not exist for Zacatecas
- **State energy balance**: SENER publishes national only; SIE has some state-level electricity data
- **RETC facility data for Zacatecas**: Available on datos.gob.mx but not downloaded for this analysis

## Upgrade from Tier 4 to Tier 3

The previous version of this analysis used **Tier 4** (proxy-based allocation of national EDGAR totals using GDP, population, and sector-specific proxies). The current version uses **Tier 3** (EDGAR v8.0 gridded spatial disaggregation with GADM state boundary mask), which:

- Eliminates the need for proxy share assumptions
- Uses EDGAR's own spatial allocation methodology (based on point-source databases, population density, road networks, land use, etc.)
- Provides sector-level emissions grounded in the global gridding rather than a single national-to-state scaling factor
- Reduces the total estimate from 8,790 KtCO₂e (Tier 4) to 7,145 KtCO₂e (Tier 3)

## Access Dates

All sources accessed March-April 2026.
