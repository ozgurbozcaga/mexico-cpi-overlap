# Data Sources — Tamaulipas Carbon Pricing Overlap Analysis

## Primary Inventory Source

**Programa Estatal de Cambio Climático Tamaulipas 2015–2030 (PECC)**

- Producer: Gobierno del Estado de Tamaulipas / SEDUMA
- Technical supervision: Ithaca Environmental, Local & Global Ideas, LARCI Mexico
- Coordination: COCEF (Comisión de Cooperación Ecológica Fronteriza), INECC, BID
- Published: Periódico Oficial del Estado, 15 de septiembre de 2016, Tomo CXLI, Anexo 111
- Local file: `data/raw/Tamaulipas_cxli-111-150916F-ANEXO.pdf`
- Accessed: April 2026

**Coverage:** 1990–2013 time series + BaU projections 2014–2030
**GWPs:** SAR (CH₄=21, N₂O=310) — **REQUIRES CONVERSION TO AR5**
**Methodology:** IPCC 2006 Guidelines; Tier 2 for energy CO₂ (national EFs from SIE/SENER)

### Key tables and figures used:

| Source | Page | Content | Used for |
|--------|------|---------|----------|
| Table I | p.4 | Total emissions by category 2010–2013 | Cross-validation |
| Table III | pp.6–7 | Full BaU projections 1990–2030, 9 subsectors | Growth ratios for 2025 extrapolation |
| Table 5.1 | pp.98–99 | Full 2013 IPCC inventory with CO₂/CH₄/N₂O breakdown | All emission values in 01_clean.py |
| Table 5.3 | p.102 | CFE conventional power plants | ETS threshold confirmation |
| Table 5.4 | p.102 | Ciclo combinado power plants (PIEs) | ETS threshold confirmation |
| Table 5.5 | p.105 | Energy consumption by category 1995–2013 (PJ) | Sector energy trends |
| Table 5.6 | p.106 | Fuel consumption by sector 2013 (PJ) | NG share per sector |
| Table 5.7 | p.110 | GHG emissions by energy subcategory 1995–2013 | Historical growth rates |
| Table 5.8 | p.111 | Detailed energy emissions by subcategory 1995–2013 | Cross-validation |
| Table 5.10 | p.113 | Energy consumption 1A1 (refining + electricity) 1995–2013 | Fuel trends |
| Table 5.11 | p.114 | Refinery NG consumption and emissions 1995–2013 | NG fraction at refinery |
| Table 5.12 | p.115 | Electricity generation fuel (NG + diesel) and emissions 1995–2013 | NG/diesel CO₂ split |
| Table 5.13 | p.116 | Electric sector description 2002–2013 | Capacity and generation |
| Table 5.14 | pp.119–120 | Manufacturing fuel consumption (NG/diesel/GLP) 1995–2013 | Manufacturing NG fraction |

## 2022 Benchmark Validation

- **2022 state emissions inventory (unpublished):** 47,530 GgCO₂e total, energy sector 83%
- Source: official state government communication (not publicly available)
- Used to validate Table III BaU trajectory (Table III projects 47,512 for 2022 — within 0.04%)

## Instrument Design Sources

### S — Tamaulipas State Carbon Tax

- **Ley de Hacienda del Estado de Tamaulipas**, Art. 36 Bis and related articles
- Implementation: 2020–2022, suspended 2023, reinstated 2024
- Threshold: ≥25,000 tCO₂e/yr (legal exemption for smaller facilities)
- Scope: direct emissions from fixed sources in productive processes
- Gases: CO₂, CH₄, N₂O, HFCs, PFCs, SF₆
- ~36 companies covered (per official state source)
- **FLAG:** Law text uses "expulsiones directas o indirectas" — conservative scope 1 interpretation applied

### F — Mexico Federal IEPS Carbon Tax

- Ley del IEPS, Artículo 2o-C
- Natural gas exemption: confirmed statutory
- Covers all downstream fossil fuel combustion except NG

### E — Mexico Pilot ETS (Sistema de Comercio de Emisiones)

- SEMARNAT: Acuerdo piloto SCE
- Threshold: ≥25,000 tCO₂e/yr
- Non-binding pilot phase; legal scope used as upper bound

## Supporting Energy Statistics

- **SIE (Sistema de Información Energética):** SENER fuel consumption data for Tamaulipas
  - Basis for Tables 5.6, 5.12, 5.14 in the inventory
  - Note: combustóleo consumption not disaggregated by sector (SIE limitation)
- **PEMEX:** Refinería Francisco I. Madero (Ciudad Madero) — 117,500 bbl/day capacity
- **CFE/SENER:** Power plant capacity and generation data (Tables 5.3/5.4/5.13)

## Open Questions / Pending Verification

1. **Combustóleo in electricity generation:** Inventory notes 5.2% of electricity fuel is combustóleo but SIE data lacks sector disaggregation. Estimated at 13,585 TJ; update if sectoral data becomes available.
2. **PEMEX refinery non-NG fuel use:** Inventory only captures NG; refinery uses mixed fuels in practice. Central 85% NG assumed with wide range.
3. **HFC (2F1) data gap:** Reported as "NE" (not estimated). Flagged as data gap — no emissions quantified for refrigeration/AC HFCs.
4. **Post-2013 inventory:** If state publishes updated inventory with AR5 GWPs, replace SAR→AR5 conversion.
5. **State tax implementation details:** Verify exact facility list and compliance data for 2024-present period.
6. **4D2 industrial wastewater:** Reported as "NA" — potential data gap.
