# Estado de México — CPI Overlap Analysis

## Summary

| Parameter | Value |
|-----------|-------|
| **State** | Estado de México |
| **Estimation Tier** | **Tier 3** — Published state inventory (IEEGyCEI-2022) |
| **Base data** | Inventario Estatal de Emisiones de Gases y Compuestos de Efecto Invernadero del Estado de México (IEEGyCEI-2022). Published GHG inventory with IPCC 2006 sector structure, 13 energy sub-categories, 6 IPPU sub-categories. |
| **Base year** | 2022 |
| **GWPs** | AR5 (CH₄=28, N₂O=265) |
| **Instruments** | S (state carbon tax) × F (federal IEPS) × E (Mexico pilot ETS) |
| **Gas scope (S)** | CO₂, CH₄, N₂O only — **no HFCs, PFCs, SF₆** |
| **Facility threshold (S)** | None — all fixed sources (fuentes fijas) |
| **Source scope (S)** | State + federal jurisdiction (expanded December 2022); direct + indirect emissions |
| **Tax rate** | 43 MXN/tCO₂e (January 2022), raised to 58 MXN/tCO₂e (December 2023) |
| **In force** | January 2022; scope expanded December 2022 to include federal-jurisdiction sources and indirect emissions |

## Key Results (Central Estimate)

| Metric | KtCO₂e | % of Total |
|--------|--------|------------|
| Total state emissions | 36,385.0 | 100% |
| Gross S (state tax) | 17,354.1 | 47.7% |
| Gross F (federal tax) | 14,317.3 | 39.3% |
| Gross E (ETS) | 8,599.3 | 23.6% |
| **Deduplicated union** | **26,728.2** | **73.5%** |
| Uncovered | 9,656.8 | 26.5% |

### Venn Segment Breakdown

| Segment | KtCO₂e | % of Total |
|---------|--------|------------|
| S∩F∩E | 4,176.9 | 11.5% |
| S∩E only | 4,422.4 | 12.2% |
| S∩F only | 766.2 | 2.1% |
| S only | 7,988.5 | 22.0% |
| F∩E only | 0.0 | 0.0% |
| F only | 9,374.1 | 25.8% |
| E only | 0.0 | 0.0% |
| Uncovered | 9,656.8 | 26.5% |

### Pairwise Overlaps

| Overlap | KtCO₂e |
|---------|--------|
| S ∩ F | 4,943.1 |
| S ∩ E | 8,599.3 |
| S ∩ F ∩ E | 4,176.9 |

### Low / Central / High Range

| Estimate | Total | Gross S | Gross F | Gross E | Dedup Union | Dedup % |
|----------|-------|---------|---------|---------|-------------|---------|
| Low      | 34,394.7 | 16,404.7 | 13,534.2 | 4,877.3 | 25,266.1 | 73.5% |
| Central  | 36,385.0 | 17,354.1 | 14,317.3 | 8,599.3 | 26,728.2 | 73.5% |
| High     | 38,375.3 | 18,303.5 | 15,100.4 | 12,697.7 | 28,190.3 | 73.5% |

## Methodology

### Published State Inventory (Tier 3)

Emissions are taken directly from the published IEEGyCEI-2022 inventory — a Tier 3 source with IPCC 2006 sector structure and AR5 GWPs. No proxy allocation, EDGAR gridded extraction, or scaling is required. The inventory provides:

- **Energy sector** (22,452.9 KtCO₂e): disaggregated into electricity generation (5,606.9), manufacturing with 11 sub-categories (6,111.1), transport with 3 modes (7,309.8), and other sectors split into commercial/residential/agricultural (3,425.1)
- **IPPU sector** (4,639.5 KtCO₂e): cement (582.5), lime (186.7), glass (123.5), other carbonates (2,417.1), metals (70.7), lubricants/wax (1,259.1)
- **AFOLU sector** (3,511.7 KtCO₂e): agriculture, forestry, and land use combined
- **Waste sector** (5,780.8 KtCO₂e): solid waste disposal and wastewater treatment combined

Cross-validation: all sector sums are verified against published totals (Energy + IPPU + AFOLU + Waste = 36,384.9 KtCO₂e). Sub-sector sums are validated for manufacturing (11 sub-categories → 6,111.1), transport (3 modes → 7,309.8), and other sectors (3 sub-sectors → 3,425.1).

Uncertainty of ±5.47% is the inventory's own estimate, applied uniformly to produce low/high bounds.

### Three-Instrument Overlap Framework

Three carbon pricing instruments potentially apply to emissions within Estado de México:

- **S (State carbon tax)**: Covers all fixed-source emissions of CO₂, CH₄, and N₂O — but **not** HFCs, PFCs, or SF₆. No facility-size threshold. Scope expanded in December 2022 to include federal-jurisdiction fixed sources and indirect emissions. Excludes mobile sources, residential combustion, AFOLU, and waste.
- **F (Federal IEPS carbon tax)**: Upstream fuel levy on fossil fuel combustion CO₂, covering all fuels **except natural gas**. Applies to both mobile and fixed sources. Does not cover process emissions, AFOLU, or waste.
- **E (Mexico pilot ETS)**: Covers direct CO₂ from facilities emitting ≥25,000 tCO₂e/yr. Limited to CO₂ only (not CH₄/N₂O/HFCs). Coverage estimated as 30% (low) / 50% (central) / 70% (high) of eligible fixed-source emissions, with sector-specific multipliers for facility size distribution.

For each inventory sector, coverage shares (s, f, e ∈ [0,1]) are assigned based on the instrument's legal scope. Eight Venn segments are computed via inclusion-exclusion to obtain the deduplicated union coverage.

### Natural Gas Share Assumptions

Estado de México has **significantly higher natural gas penetration** than most states in the analysis set, reflecting its proximity to the national gas pipeline network, major PIE (productor independiente de energía) gas-fired power plants, and diversified industrial base.

| Sector | NG Share | F Share (=1−NG) | Basis |
|--------|----------|-----------------|-------|
| Electricity (1.A.1.a) | 80% | 20% | Major gas-fired power plants including PIEs; CFE dispatch favors NG |
| Manufacturing (1.A.2) | 50% | 50% | Inventory confirms NG + gas LP + diesel + combustóleo/coke/coal across 11 sub-sectors |
| Commercial (1.A.4.a) | 40% | 60% | Urban area with NG distribution network |
| Residential (1.A.4.b) | 15% | 85% | Mostly gas LP (tanque estacionario); some piped NG in newer developments |
| Agricultural (1.A.4.c) | 5% | 95% | Minimal NG in agricultural combustion |
| Transport (1.A.3) | 0% | 100% | All transport fuels are petroleum-based |

**Key insight:** The 80% NG share in electricity means F covers only 20% of electricity combustion CO₂ — creating a large S∩E-only segment from NG-fired power plants covered by S and E but not F. The 50% NG share in manufacturing similarly creates a substantial S-only segment for NG-fired industrial combustion below the ETS threshold.

### ETS Threshold Coverage

Without facility-level data, ETS coverage is estimated as a range with sector-specific multipliers:

| Sector | Multiplier | Effective E share | Rationale |
|--------|-----------|-------------------|-----------|
| Electricity (1.A.1.a) | ×1.2 | 60% | Large power plants (PIEs, CFE), most above 25,000 tCO₂e threshold |
| Manufacturing (1.A.2) | ×1.0 | 50% | Mix of large (transport equipment, chemicals) and small facilities |
| Cement (2.A.1) | ×1.3 | 65% | Large point sources, high per-facility emissions |
| Lime (2.A.2) | ×1.3 | 65% | Large point sources |
| Glass (2.A.3) | ×1.3 | 65% | Large point sources |
| Other carbonates (2.A.4) | ×1.3 | 65% | Large limestone/soda ash operations |
| Metals (2.C) | ×0.8 | 40% | Smaller-scale lead/zinc operations |
| Lubricants/wax (2.D) | ×0.0 | 0% | Non-energy products, dispersed, below threshold |
| All 1.A.4, AFOLU, Waste | ×0.0 | 0% | Below threshold or excluded from ETS |

- **Low (30%)**: Conservative — assumes fewer facilities above threshold
- **Central (50%)**: Moderate — base assumption
- **High (70%)**: Upper bound — assumes more concentration at large facilities

## Unique Characteristics of Estado de México

### Largest state in the analysis set (36,385 KtCO₂e)

At 36.4 MtCO₂e, Estado de México is roughly **5× larger than the next-largest state** (Zacatecas at ~7,145 KtCO₂e) in the 11-state CPI overlap analysis. This scale is driven by Mexico's most populous state (17+ million people) with heavy industry surrounding Mexico City — the Toluca-Lerma industrial corridor, major power generation facilities, extensive urban transport networks, and the metropolitan waste infrastructure serving the greater Mexico City area.

### Highest deduplicated coverage (73.5%)

The deduplicated union of 26,728 KtCO₂e (73.5%) is the highest coverage rate in the analysis set. This reflects the massive industrial base where energy combustion and IPPU process emissions at fixed sources are covered by at least one instrument. Only AFOLU (3,512 KtCO₂e), waste (5,781 KtCO₂e), and the residential share of combustion (364 KtCO₂e uncovered portion) fall outside all three instruments.

### CO₂/CH₄/N₂O gas scope only — no HFC/PFC/SF₆ coverage

Unlike Zacatecas (full Kyoto basket + SF₆), Querétaro, Yucatán, Tamaulipas, and San Luis Potosí which include HFCs, the Estado de México carbon tax covers **only CO₂, CH₄, and N₂O**. No HFC, PFC, or SF₆ emissions are covered by S. This narrower gas scope is a distinguishing feature — states that include fluorinated gases capture an additional slice of IPPU product-use emissions. However, since the IEEGyCEI-2022 does not separately quantify F-gas emissions by sub-sector, the practical impact on the overlap model is minimal.

### S∩E-only block of 4,422 KtCO₂e (12.2%) — largest in the set

The S∩E-only segment is exceptionally large, driven by two mechanisms:

1. **NG-fired electricity at large plants**: With 80% NG in the power sector, the majority of electricity combustion is exempt from F (NG exemption) but covered by both S (fixed-source combustion) and E (large facilities above 25,000 tCO₂e). The NG-exempt share of above-threshold electricity (80% × 60% × 5,606.9 = 2,242.8 KtCO₂e) is a major contributor.

2. **Massive carbonates/limestone IPPU (2,417 KtCO₂e)**: Process CO₂ emissions from limestone and soda ash processing are covered by S (process emissions at fixed sources) and partially by E (large point sources, ×1.3 multiplier → 65% ETS coverage), but **not by F** (not combustion-based, no fuel involved). The ETS-covered share (65% × 2,417.1 = 1,571.1 KtCO₂e) flows entirely into S∩E-only. Cement (378.6 KtCO₂e), lime (121.4 KtCO₂e), and glass (80.3 KtCO₂e) similarly contribute to this segment.

This pattern is distinctive: in low-NG states like Zacatecas (15% manufacturing NG), most combustion emissions fall in S∩F∩E or S∩F-only. In Estado de México, the NG exemption from F redirects a large block into S∩E-only.

### S-only of 7,989 KtCO₂e (22.0%) — also the largest in the set

The S-only segment includes several distinct components:

- **Lubricants/wax (1,259.1 KtCO₂e)**: An unusually large non-combustion product-use category. Covered by S (process emissions at fixed sources) but not by F (not combustion-based) or E (dispersed, below 25,000 tCO₂e threshold). This is the largest single S-only IPPU block in the analysis.
- **NG-fired manufacturing below ETS threshold**: With 50% NG in manufacturing, the NG-exempt portion of below-threshold manufacturing combustion (50% × 50% × 6,111.1 = 3,055.6 KtCO₂e) falls in S-only.
- **NG-fired electricity below ETS threshold**: 80% × 40% × 5,606.9 = 2,242.8 KtCO₂e from the NG-exempt, below-threshold portion of power generation.
- **Smaller IPPU**: Carbonates below ETS threshold (845.9), metals below threshold (42.4), cement below threshold (203.9), commercial combustion NG-exempt share (206.2), and agricultural combustion NG-exempt share (24.1).

### Significant manufacturing detail: 11 sub-categories under 1.A.2

The inventory breaks manufacturing combustion (6,111.1 KtCO₂e) into 11 sub-categories, providing unusual granularity:

| Sub-sector | KtCO₂e | Share |
|-----------|--------|-------|
| Transport equipment manufacturing | 1,641.6 | 26.9% |
| Non-metallic minerals manufacturing | 1,061.1 | 17.4% |
| Unspecified industry | 745.8 | 12.2% |
| Chemicals manufacturing | 735.8 | 12.0% |
| Food & beverages manufacturing | 672.7 | 11.0% |
| Pulp & paper manufacturing | 549.6 | 9.0% |
| Iron & steel manufacturing | 233.4 | 3.8% |
| Textiles manufacturing | 219.8 | 3.6% |
| Non-ferrous metals manufacturing | 197.7 | 3.2% |
| Machinery manufacturing | 38.0 | 0.6% |
| Wood manufacturing | 15.6 | 0.3% |

Transport equipment manufacturing (1,641.6 KtCO₂e) is the single largest sub-sector, reflecting the automotive industry corridor in Toluca and Lerma, where major assembly and parts plants operate.

### Waste sector is exceptionally large (5,781 KtCO₂e, 15.9%) — all uncovered

The waste sector is the largest in the analysis set, reflecting the population density and landfill infrastructure of the Mexico City metropolitan area. At 5,780.8 KtCO₂e, it exceeds the **entire state emissions** of several other states in the set. All waste emissions are uncovered by the three carbon pricing instruments.

### Scope expansion in December 2022

The Estado de México carbon tax was initially enacted in January 2022 covering only **state-jurisdiction fixed sources**. In December 2022, the scope was expanded to include:
- **Federal-jurisdiction fixed sources** (large industrial facilities regulated by SEMARNAT rather than the state environmental agency)
- **Indirect emissions** (Scope 2 and downstream effects)

This means 2022 coverage may understate subsequent years' legal scope. Our analysis applies the **post-reform expanded scope**, representing the current legal framework. The expansion is a major reason why gross S (17,354 KtCO₂e, 47.7%) is high — it captures all fixed-source combustion and process emissions regardless of whether the facility falls under state or federal environmental jurisdiction.

### Transport is F-only (7,310 KtCO₂e)

Transport (7,309.8 KtCO₂e) is covered by the federal fuel tax (all transport fuels are petroleum-based, NG share = 0%) but excluded from the state tax (mobile sources) and ETS. This is the single largest F-only block, comprising terrestrial transport (6,993.1), aviation (249.4), and rail (67.4).

## Revenue Cross-Check

| Parameter | Value |
|-----------|-------|
| Gross S (model) | 17,354.1 KtCO₂e |
| Tax rate (2022) | 43 MXN/tCO₂e |
| Tax rate (2023+) | 58 MXN/tCO₂e |
| Implied potential revenue (43 MXN) | MXN 746 million |
| Implied potential revenue (58 MXN) | MXN 1,007 million |
| Ecological tax revenue (actual, 2024) | MXN 252 million (includes non-carbon taxes) |
| Revenue-implied floor | ~4,300–5,900 KtCO₂e (if all ecological revenue were carbon tax) |

Gross S (17,354 KtCO₂e) is well above the revenue-implied floor of ~4,300–5,900 KtCO₂e. This is consistent with expectations — the gap between potential and actual revenue reflects:
- Ecological tax revenue includes multiple instruments beyond the carbon tax (environmental taxes on waste, water use, etc.)
- Partial compliance and phased-in enforcement, especially for newly covered federal-jurisdiction sources post-December 2022
- Administrative gaps and exemptions
- The December 2022 scope expansion means pre-reform revenue reflects the narrower state-jurisdiction-only scope

## Cross-Validation

| Source | KtCO₂e | Notes |
|--------|--------|-------|
| **IEEGyCEI-2022 (this analysis)** | **36,385** | Published state inventory, Tier 3 |
| IEEGyCEI-2020 (previous inventory) | 41,184 | Base year 2020; 13.2% higher than 2022 |
| Inventory uncertainty range | 34,395 – 38,375 | ±5.47% from inventory's own estimate |

The 2022 inventory total (36,385 KtCO₂e) is 13.2% lower than the 2020 inventory (41,184 KtCO₂e). This decrease is attributed to COVID-19 effects on industrial production and the waste sector — consistent with the timing (2022 base year captures partial recovery, not full pre-pandemic levels) and the state's heavy dependence on manufacturing and metropolitan waste generation.

## File Structure

```
states/estado_de_mexico/
├── scripts/
│   ├── 01_clean.py                  # Inventory extraction → sector-level emissions table
│   ├── 02_estimate.py               # Three-instrument overlap estimation (S × F × E)
│   └── 03_outputs.py                # Publication figures and summary tables
├── data/
│   ├── raw/
│   │   ├── INVENTARIO DE EMISIONES DE GEI_2022.pdf      # IEEGyCEI-2022
│   │   └── Impuesto al Carbono en Estado de México_2024_docx.pdf  # Carbon tax policy brief
│   └── processed/
│       ├── estado_de_mexico_inventory.csv            # Sector inventory with uncertainty bounds
│       ├── estado_de_mexico_inventory_summary.csv     # Category-level summary
│       ├── estado_de_mexico_subsector_detail.csv      # Manufacturing/transport/other sub-sectors
│       ├── estado_de_mexico_reference_data.csv        # Cross-validation reference values
│       ├── estado_de_mexico_overlap_sectors.csv       # Per-sector instrument shares + Venn segments
│       ├── estado_de_mexico_overlap_summary.csv       # Aggregate Venn segment totals
│       └── estado_de_mexico_overlap_ranges.csv        # Low/central/high range estimates
├── outputs/
│   ├── figures/
│   │   ├── estado_de_mexico_venn_segments.png         # Eight overlap segments bar chart
│   │   ├── estado_de_mexico_instrument_coverage.png   # Instrument coverage with error bars
│   │   └── estado_de_mexico_inventory_breakdown.png   # Emissions pie chart by broad category
│   └── tables/
│       ├── estado_de_mexico_overlap_table.csv         # Publication-ready overlap summary
│       ├── estado_de_mexico_range_table.csv           # Low/central/high range table
│       └── estado_de_mexico_sector_detail.csv         # Sector-level detail with shares
└── docs/
    ├── README.md                    # This file
    ├── data_sources.md              # Data provenance and citations
    ├── assumptions_02.md            # Detailed assumptions for overlap estimation
    └── methodology.md              # Technical methodology documentation
```

## Potential Improvements

1. **Facility-level RETC data**: Download from datos.gob.mx to validate ETS threshold assumptions and refine sector-specific multipliers. Particularly valuable for the large carbonates/limestone sector (2,417 KtCO₂e) where facility concentration directly affects ETS coverage.
2. **Time-series using 2020 and 2022 inventories**: Both inventories exist, enabling trend analysis and validation of the 13.2% decrease attributed to COVID-19 effects on industrial production.
3. **Sub-sector NG share verification from COA/COI reports**: The 80% NG share in electricity and 50% in manufacturing are estimates; SEMARNAT's Cédula de Operación Anual (COA) and Cédula de Operación Industrial (COI) reports could provide facility-level fuel consumption data.
4. **HFC disaggregation**: If available from INECC or an updated inventory, quantify F-gas emissions separately to assess the practical impact of the CO₂/CH₄/N₂O-only gas scope vs. broader-scope states.
5. **Post-reform compliance tracking**: Monitor actual carbon tax revenue separated from other ecological taxes to refine the revenue cross-check as enforcement of the December 2022 scope expansion matures.
6. **SENER state energy balance**: Cross-validate electricity generation fuel mix and industrial fuel consumption against SIE (Sistema de Información Energética) state-level data.
