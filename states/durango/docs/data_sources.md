# Data Sources — Durango Carbon Pricing Overlap Analysis

## Primary Inventory Source

**Inventario Estatal de Emisiones de Gases y Compuestos de Efecto Invernadero (IEEGYCEI)**
**Estado de Durango, Base Year 2022**

- Producer: Centro Mario Molina para Estudios Estratégicos sobre Energía y Medio Ambiente A.C.
- Commissioned by: Secretaría de Recursos Naturales y Medio Ambiente de Durango (SRNMA)
- Additional contributor: Secretaría de Energía (SENER)
- Published: 2024 (exact date TBC)
- Local file: `data/raw/Durango_inventory.pdf`
- Accessed: March 2026

**Coverage:** 2010–2022 time series; GHGs: CO₂, CH₄, N₂O, HFCs, PFCs, SF₆, NF₃, black carbon
**GWPs:** AR5 (CH₄=28, N₂O=265) — consistent with INECC national INEGYCEI
**Methodology:** IPCC 2006 Guidelines + 2019 Refinement; Tier 2 for stationary combustion CO₂ (national EFs)

### Key tables and figures used:

| Source | Content | Used for |
|--------|---------|----------|
| Table 8 | 2010–2022 sector trends (GgCO₂e) | Historical CAGRs for extrapolation |
| Table 9 | Full 2022 IPCC-coded inventory | All emission values in 01_clean.py |
| Table 11 | Power plant inventory (5 plants, capacity) | ETS threshold confirmation |
| Table 12 | Fuel consumption [1A1] 2010–2022 (PJ) | NG/diesel/FO split for F scope |
| Table 13 | CO₂ emission factors [1A1] (kg/TJ) | Fuel-CO₂ attribution |
| Table 14 | CO₂ emission factors [1A2] (kg/TJ) | Manufacturing fuel fractions |
| Figure 13 | Fuel mix [1A2] 2022 (% energy by fuel) | NG share estimate for manufacturing |

## Instrument Design Sources

### S — Durango State Carbon Tax
- **Ley de Cambio Climático del Estado de Durango** (published Periódico Oficial del Estado)
  - Referenced in inventory section 1.2
  - Full regulatory text: not yet confirmed as publicly available; Jalisco/Zacatecas model used as design template
  - **⚠ FLAG:** Tax design confirmed via inventory references; full legal text not independently verified
- Scope confirmed: CO₂, CH₄, N₂O, HFCs, SF₆, PFCs, black carbon from STATIONARY sources
- Exemptions: aviation, maritime, transport, waste, forestry, agriculture
- **KEY DIFFERENCE FROM COLIMA:** No natural gas exemption

### F — Mexico Federal IEPS Carbon Tax
- Ley del Impuesto Especial sobre Producción y Servicios (IEPS), Artículo 2o-C
- SAT (Servicio de Administración Tributaria) — annual revenue data
- Natural gas exemption: confirmed statutory; applies to all downstream users
- Source: IEPS legislation, INECC documentation
- Accessed via: INECC website and SAT fiscal reports

### E — Mexico Pilot ETS (Sistema de Comercio de Emisiones)
- SEMARNAT: Acuerdo piloto SCE; official participants list
- Threshold: ≥25,000 tCO₂e/yr direct emissions from covered sectors
- **Note:** Non-binding pilot phase; legal scope used as upper bound (per project methodology)
- MRV data: COA (Cédulas de Operación Anual) via SEMARNAT
- Accessed: SEMARNAT SISCAP platform

## Supporting Energy Statistics

- **SIE (Sistema de Información Energética):** SENER fuel consumption and generation data
  - Used to cross-validate [1A1] fuel consumption figures
- **CRE (Comisión Reguladora de Energía):** Plant-level capacity and fuel data
- **INEGI:** Economic activity and GDP by sector (context for manufacturing trends)

## National Reference

- INECC: INEGYCEI 2022 (Inventario Nacional de Emisiones de GEI)
  - Used to cross-check national sector growth rates for extrapolation validation
  - AR5 GWP consistency confirmed

## Open Questions / Pending Verification

1. **Full Durango carbon tax legal text** — exact scope clauses not independently confirmed; Jalisco/Zacatecas template assumed. Update if text published.
2. **SEMARNAT ETS participant list for Durango** — confirm which of the 5 power plants + major industrial facilities are formally registered in SCE. This affects E scope directly.
3. **Post-2022 inventory** — if SRNMA publishes a 2023 or 2024 inventory, replace extrapolation with actual data.
4. **[1A2] fuel mix from COA data** — Figure 13 gives % shares; exact TJ values by fuel for 2022 would improve F scope precision for manufacturing.
5. **New Lerdo 350 MW combined cycle plant** — reported to enter service 2024; will increase [1A1] but as CC (high-efficiency NG), emissions impact depends on displaced fuel type. Update when operational data available.
