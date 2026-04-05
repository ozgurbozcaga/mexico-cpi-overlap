# Estado de Mexico — Methodology

## Overview

This analysis estimates the deduplicated GHG emissions coverage of three overlapping carbon pricing instruments in Estado de Mexico. It is part of the broader Mexico state-level CPI overlap analysis for the State & Trends of Carbon Pricing (S&T) publication.

Estado de Mexico is the **largest state by emissions** in the analysis set (~36.4 MtCO2e), approximately 5x larger than the next-largest state. It is highly industrialized, with manufacturing combustion (6,111 KtCO2e) as the single largest fixed-source category and significant IPPU from carbonates/limestone (2,417 KtCO2e).

## Estimation Tier

**Tier 3** — Published state GHG inventory (IEEGyCEI-2022) with IPCC 2006 sector detail, AR5 GWPs, and ±5.47% uncertainty estimate.

## Three-Stage Pipeline

### Stage 1: Inventory Extraction (01_clean.py)

1. Extract sector totals directly from the published IEEGyCEI-2022 inventory
2. Cross-validate that sector sums match published totals (Energy 22,452.9 + IPPU 4,639.5 + AFOLU 3,511.7 + Waste 5,780.8 = 36,384.9 KtCO2e)
3. Verify sub-sector detail for manufacturing (11 sub-categories summing to 6,111.1), transport (3 modes summing to 7,309.8), and other sectors (3 sub-sectors summing to 3,425.1)
4. Apply ±5.47% uncertainty (from the inventory's own estimate) for low/high bounds
5. Output: sector-level inventory with central/low/high estimates in KtCO2e

### Stage 2: Overlap Estimation (02_estimate.py)

For each inventory sector, determine the coverage share of each instrument:

- **S share**: Whether the sector contains fixed-source CO2/CH4/N2O emissions covered by the state carbon tax. Key exclusions: mobile sources (transport), residential combustion, AFOLU, waste. Key inclusion: all IPPU process emissions that produce CO2/CH4/N2O.
- **F share**: The fraction of sector emissions from non-natural-gas fossil fuel combustion. Key parameter: natural gas share per sector. Estado de Mexico has **high NG penetration** (80% electricity, 50% manufacturing), creating large F-exempt segments.
- **E share**: The fraction of sector emissions from facilities above the 25,000 tCO2e/yr ETS threshold. Sector-specific multipliers adjust for facility size distribution.

The 1.A.4 sector (3,425.1 KtCO2e) is split into three sub-sectors with different instrument coverage:
- Commercial/institutional (515.5 KtCO2e): S-covered fixed sources
- Residential (2,428.6 KtCO2e): S-excluded (not fixed sources)
- Agricultural combustion (481.0 KtCO2e): S-covered fixed sources

Compute eight Venn segments using inclusion-exclusion per sector, then aggregate.

Range estimates combine inventory uncertainty (±5.47%) with ETS threshold uncertainty (30/50/70%) to produce low/central/high coverage estimates.

### Stage 3: Outputs (03_outputs.py)

Generate three publication-quality figures:
1. **Venn segments bar chart**: Eight overlap segments showing the composition of covered vs. uncovered emissions
2. **Instrument coverage with error bars**: Gross S, F, E, and deduplicated union with low/high ranges
3. **Inventory breakdown pie chart**: Emissions by broad category

Generate three summary tables:
1. **Overlap table**: Segment-level KtCO2e and percentages
2. **Range table**: Low/central/high for total, gross S/F/E, and deduplicated union
3. **Sector detail**: Per-sector instrument shares and Venn segment allocations

## Key Methodological Choices

### Why the gas scope matters

Estado de Mexico covers only CO2, CH4, N2O — excluding HFCs, PFCs, and SF6. This is narrower than Zacatecas (full Kyoto basket + SF6), Queretaro, and Yucatan. In practice, this exclusion primarily affects:
- HFC leakage from commercial/industrial refrigeration (not separately quantified in inventory)
- SF6 from electrical equipment insulation

Since the inventory does not disaggregate F-gas emissions by sub-sector, the practical impact on the overlap model is minimal — the excluded gases would appear in a "product use" category if present.

### High NG penetration creates distinctive overlap patterns

Estado de Mexico's high natural gas shares (80% electricity, 50% manufacturing) mean that large portions of combustion emissions are exempt from the federal IEPS fuel tax (which excludes NG). This creates:

1. **Large S∩E-only segments**: NG-fired power plants and industrial facilities are covered by the state tax (combustion at fixed sources) and potentially by the ETS (large facilities), but NOT by the federal fuel tax. This is the most distinctive feature of Estado de Mexico's overlap pattern.

2. **Large S-only segments**: NG-fired industrial combustion below the ETS threshold falls in S-only (state tax covers, but neither F nor E applies).

3. **Smaller S∩F∩E triple overlap**: Because NG is exempt from F, the triple-overlap segment is proportionally smaller than in low-NG states like Zacatecas.

### IPPU carbonates as S∩E-only

The 2,417.1 KtCO2e from "other carbonates" (limestone + soda ash) is one of the largest single IPPU sub-categories in any Mexican state. These are process CO2 emissions:
- Covered by S (process emissions at fixed sources producing CO2)
- NOT covered by F (not combustion, not fuel-based)
- Partially covered by E (large point sources above ETS threshold; multiplier 1.3)

This means carbonates contribute substantially to the S∩E-only segment — a block of emissions jointly covered by the state tax and ETS but not by the federal fuel tax.

### Lubricants/wax as S-only

The 1,259.1 KtCO2e from non-energy products (lubricants + wax) is a large S-only block:
- Covered by S (process emissions at fixed sources)
- NOT covered by F (not combustion-based)
- NOT covered by E (dispersed, below 25,000 tCO2e/yr threshold)

### Dec 2022 scope expansion

The state carbon tax was reformed in December 2022 to expand from state-jurisdiction fixed sources only to include federal-jurisdiction fixed sources. This means that large industrial facilities previously regulated only at the federal level are now also subject to the state carbon tax. The overlap model assumes full post-reform scope (S covers all fixed sources regardless of jurisdictional level).

## Comparison with Other States

| Feature | Estado de Mexico | Zacatecas | CDMX | Yucatan |
|---------|-----------------|-----------|------|---------|
| Total emissions (KtCO2e) | **36,385** | 7,145 | ~30,000 | ~10,000 |
| State inventory | **2022 (Tier 3)** | None (EDGAR) | 2020 | 2023 |
| Gas scope | **CO2/CH4/N2O only** | Full Kyoto+SF6 | CO2/CH4/N2O | Full Kyoto |
| NG share (electricity) | **80%** | 60% | ~95% | ~93% |
| NG share (manufacturing) | **50%** | 15% | ~70% | ~93% |
| Key industry | **Manufacturing + IPPU** | Mining | Services | Cement |
| IPPU share | **12.7%** | <3% | ~5% | ~15% |
| Facility threshold | **None** | None | None | None |
| Tax rate | **43–58 MXN/tCO2e** | 250 MXN | Variable | 50 MXN |

## Limitations and Caveats

1. **NG share uncertainty**: The 80% NG share for electricity is an estimate. Actual NG share in the CFE/PIE generation mix serving Estado de Mexico may vary ±10%.
2. **ETS threshold uncertainty**: Without facility-level data, the ETS multipliers are informed estimates based on sector characteristics.
3. **No F-gas disaggregation**: The inventory does not separately quantify HFC/PFC/SF6, so we cannot precisely quantify the gas-scope exclusion's impact.
4. **Revenue attribution**: The MXN 252M ecological tax figure includes non-carbon instruments, making the carbon tax revenue cross-check approximate.
5. **Dec 2022 reform transition**: Full post-reform scope is assumed, but compliance may be phased in.
6. **Single-year snapshot**: 2022 base year; actual emissions may vary year to year.
