# Estado de Mexico — Data Sources

## Primary Sources

### 1. IEEGyCEI-2022 — Inventario Estatal de Emisiones de Gases y Compuestos de Efecto Invernadero

- **Content**: Full state GHG inventory for Estado de Mexico, IPCC 2006 sector structure
- **Base year**: 2022
- **GWPs**: AR5 (CH4=28, N2O=265)
- **Total**: 36,384.9 GgCO2e (= KtCO2e)
- **Uncertainty**: ±5.47% (inventory's own estimate)
- **Estimation tier**: Tier 3 (uses state-specific activity data and emission factors)
- **Sectors**: Energy (22,452.9), IPPU (4,639.5), AFOLU (3,511.7), Waste (5,780.8)
- **Key detail**: Sub-sector disaggregation for manufacturing (11 sub-categories), transport (3 modes), and other sectors (commercial/residential/agricultural)
- **File**: `data/raw/INVENTARIO DE EMISIONES DE GEI_2022.pdf`
- **Citation**: Gobierno del Estado de Mexico (2023). Inventario Estatal de Emisiones de Gases y Compuestos de Efecto Invernadero del Estado de Mexico, ano base 2022 (IEEGyCEI-2022).

### 2. Impuesto al Carbono en Estado de Mexico — Policy Brief (2024)

- **Content**: Carbon tax design parameters, legal framework, rate schedule, scope
- **Key data extracted**:
  - Gas scope: CO2, CH4, N2O only (no HFCs, PFCs, SF6)
  - Source scope: all fixed sources (fuentes fijas), state + federal jurisdiction (post-Dec 2022 reform)
  - No facility threshold
  - Rate: 43 MXN/tCO2e (2022), 58 MXN/tCO2e (from Dec 2023)
  - Downstream regulation, direct + indirect emissions
  - Revenue: ecological taxes of MXN 252M (not all from carbon tax)
- **File**: `data/raw/Impuesto al Carbono en Estado de México_2024_docx.pdf`
- **Citation**: MEXICO2 (2024). Reportes de politica publica sobre impuestos al carbono subnacionales en Mexico. Impuesto al carbono del Estado de Mexico.

### 3. Federal IEPS Carbon Tax (Ley del IEPS, Art. 2, Fraccion I, Inciso H)

- **Content**: Federal upstream fuel levy on fossil fuel combustion CO2
- **Key parameters**:
  - Upstream: applied at production/import of fossil fuels
  - Covers all fossil fuels EXCEPT natural gas
  - Rate varies by fuel type (based on CO2 content differential vs. natural gas)
- **Citation**: Congreso de la Union (2013). Ley del Impuesto Especial sobre Produccion y Servicios, reformas 2013.

### 4. Mexico Pilot ETS (Sistema de Comercio de Emisiones)

- **Content**: National pilot emissions trading system
- **Key parameters**:
  - Threshold: facilities emitting >= 25,000 tCO2e/yr direct CO2
  - Covers direct CO2 only (not CH4, N2O, HFCs)
  - Pilot phase 2020-2023, transitional phase from 2023
- **Citation**: SEMARNAT (2019). Acuerdo por el que se establecen las bases preliminares del Programa de Prueba del Sistema de Comercio de Emisiones. DOF 01/10/2019.

## Secondary / Cross-Validation Sources

### 5. RENE (Registro Nacional de Emisiones)

- Covers facilities above federal COA reporting threshold
- Provides independent check on large-emitter coverage relevant to ETS threshold assumptions
- **Citation**: SEMARNAT. Registro Nacional de Emisiones, datos publicos.

### 6. Revenue-Implied Coverage Cross-Check

- Ecological tax revenue: MXN 252 million (not all from carbon tax)
- At 43–58 MXN/tCO2e → floor of ~4,300–5,900 KtCO2e if all revenue were from carbon tax
- Actual carbon tax share is a fraction of total ecological taxes
- Provides order-of-magnitude plausibility check for gross S

### 7. SENER / SIE — Energy Data

- State-level fuel consumption data for cross-validating natural gas share assumptions
- Confirms significant NG penetration in Estado de Mexico electricity and manufacturing
- **Citation**: SENER. Sistema de Informacion Energetica (SIE).

## Data Quality Assessment

Estado de Mexico is one of the best-documented states in this analysis:

| Feature | Estado de Mexico | Typical State |
|---------|-----------------|---------------|
| Published inventory | **Yes (2022)** | ~50% have one |
| Estimation tier | **Tier 3** | Tier 3–4 |
| Sub-sector detail | **11 manufacturing sub-categories** | Broad categories only |
| Uncertainty estimate | **±5.47% (published)** | Not provided |
| IPPU detail | **6 sub-categories** | 1–2 categories |

## Access Dates

All sources accessed March-April 2026.
