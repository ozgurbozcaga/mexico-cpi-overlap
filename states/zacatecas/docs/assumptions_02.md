# Zacatecas — Assumptions for 02_estimate.py

## Estimation Tier: Tier 3

Upgraded from Tier 4 (proxy allocation of national data) to Tier 3 (EDGAR v8.0 gridded spatial disaggregation with GADM state boundary mask). Zacatecas remains the most data-constrained state in the analysis — it has **no published state GHG inventory** — but the EDGAR gridded approach eliminates the need for proxy-based sector allocation and provides spatially explicit emissions at 0.1° resolution.

## EDGAR Gridded Inventory (01_clean.py)

### Extraction Approach

Sector-level emissions are summed directly from EDGAR 2025 GHG v8.0 gridded NetCDF files. For each of the 26 sector files:
1. A boolean mask of 665 grid cells (0.1°) whose centers fall within the GADM Zacatecas polygon is applied
2. All masked cell values (tonnes CO₂e/cell/year) are summed to obtain the sector total
3. Uncertainty bounds are applied per broad category (see below)

This replaces the previous proxy allocation approach, which derived Zacatecas sector emissions by applying GDP/population/sector-specific shares to national EDGAR totals.

### Uncertainty Ranges

| Broad Category | Low Multiplier | High Multiplier | Rationale |
|----------------|---------------|-----------------|-----------|
| ELECTRICITY | 0.75× | 1.25× | Gridding of power plants is relatively precise |
| REFINING | 0.60× | 1.40× | EDGAR may allocate transformation energy imprecisely |
| MANUFACTURING | 0.70× | 1.30× | Point-source gridding is moderately reliable |
| TRANSPORT | 0.80× | 1.20× | Road network-based gridding is relatively stable |
| RESIDENTIAL_COMMERCIAL | 0.75× | 1.25× | Population-density-based gridding |
| FUGITIVE | 0.50× | 1.50× | Highly uncertain for states without oil/gas production |
| IPPU | 0.50× | 1.50× | Wide range — process emissions depend on facility inventory |
| AFOLU | 0.70× | 1.30× | Land-use-based gridding is moderately reliable |
| WASTE | 0.50× | 1.50× | Population-based but uncertain waste management practices |
| OTHER | 0.60× | 1.40× | Indirect emissions have high uncertainty |

## Three-Instrument Overlap (02_estimate.py)

### S (State Carbon Tax) Scope

**Covered by S:**
- All fixed-source CO₂, CH₄, N₂O, HFC, PFC, SF₆ emissions from installations
- Power generation combustion (ENE, 1.A.1.a): s = 1.0
- Refining/transformation (REF_TRF, 1.A.1.bc): s = 1.0
- Manufacturing combustion (IND, 1.A.2): s = 1.0
- Commercial/institutional + agricultural combustion (portion of RCO, 1.A.4): s = 0.50
- All IPPU process emissions (NMM, CHE, IRO, NFE, NEU): s = 1.0
- HFCs from fixed-source commercial/industrial use (PRU_SOL, 2.D-2G): s = 0.40
- Fugitive emissions from fixed installations (PRO_FFF, 1.B.1-2): s = 0.50

**Excluded from S:**
- Transport (mobile sources) — TRO, TNR_Aviation_*, TNR_Other, TNR_Ship: s = 0.0
- Residential combustion — portion of RCO (50% of RCO is residential): included in s = 0.50 overall
- AFOLU non-combustion — ENF, MNM, AGS, AWB, N2O: s = 0.0
- Waste — SWD_LDF, SWD_INC, WWT: s = 0.0
- Indirect emissions — IDE: s = 0.0

**HFC treatment:** HFCs are in the gas scope but only commercial/industrial fixed-source HFC leakage is counted. Residential HFC leakage and mobile AC are excluded. Applied 40% S coverage to PRU_SOL.

**SF₆ treatment:** Zacatecas is one of few states explicitly including SF₆ in the gas basket. SF₆ from electrical equipment insulation at fixed installations is covered by S but not by F or E.

### F (Federal IEPS Carbon Tax) Scope

**Natural gas exemption:** F covers combustion CO₂ from all fossil fuels except natural gas.

**Natural gas share assumptions (critical for F scope):**

| Sector | NG Share | F Share (= 1 - NG) | Basis |
|--------|----------|---------------------|-------|
| ENE (Electricity) | 60% | 40% | National grid mix (CFE generation) |
| REF_TRF (Refining) | 40% | 60% | Transformation/distribution |
| IND (Manufacturing) | 15% | 85% | **Very low** — ProAire shows LPG + diesel dominant |
| RCO (Commercial) | 30% | 70% | Some NG in commercial buildings |
| RCO (Residential) | 10% | 90% | Predominantly LPG + lena |
| RCO (Agricultural) | 5% | 95% | Minimal NG in agriculture |
| Transport (all) | 0% | 100% | All transport fuels are non-NG |

Weighted RCO F share: 0.30×0.70 + 0.50×0.90 + 0.20×0.95 = 0.86

**Key insight:** Zacatecas's low NG penetration in manufacturing means F covers ~85% of industrial combustion CO₂ (vs. <50% in NG-dominant states like CDMX or Guanajuato).

**F does NOT cover:** Process emissions, non-combustion emissions, AFOLU, waste, fugitive emissions.

### E (Mexico Pilot ETS) Scope

**Threshold:** ≥25,000 tCO₂e/yr direct CO₂ only

**ETS coverage range:** 30% (low) / 50% (central) / 70% (high) of fixed-source emissions

**Sector-specific adjustments:**
- ENE: e = 50% × 0.8 = 40% (fewer large power plants in Zacatecas than nationally)
- REF_TRF: e = 50% × 0.5 = 25% (uncertain if above threshold)
- IND: e = 50% (central assumption for manufacturing)
- All other fixed-source sectors: e = 0% (emissions too small or not direct CO₂)
- Transport, AFOLU, waste: e = 0%

### Venn Segment Computation

Uses standard inclusion-exclusion per sector:
```
S∩F∩E = min(s, f, e) × sector_total
S∩E_only = [min(s,e) - min(s,f,e)] × sector_total
S∩F_only = [min(s,f) - min(s,f,e)] × sector_total
S_only = [s - min(s,f) - min(s,e) + min(s,f,e)] × sector_total
F∩E_only = [min(f,e) - min(s,f,e)] × sector_total
F_only = [f - min(s,f) - max(0, min(f,e) - min(s,f,e))] × sector_total
E_only = [e - min(s,e) - max(0, min(f,e) - min(s,f,e))] × sector_total
Uncovered = [1 - min(1, s+f+e - min(s,f) - min(s,e) - min(f,e) + min(s,f,e))] × sector_total
```

Segments are summed across all 26 EDGAR sectors to obtain state-level totals.

## Cross-Validation

| Check | Value | Comparison |
|-------|-------|------------|
| EDGAR gridded total | 7,145 KtCO₂e | Primary estimate (Tier 3) |
| RENE 2018 (facility-level) | 1,917 – 3,138 KtCO₂e | Subset: only large facilities |
| Revenue-implied (2021) | ~2,216 KtCO₂e | Subset: only S-covered emissions |
| Previous proxy estimate (Tier 4) | 8,790 KtCO₂e | Now superseded |
| Gross S (this model) | 1,060 KtCO₂e | Below revenue-implied; see README for discussion |

## Known Limitations

1. **No state GHG inventory**: EDGAR gridded data is the best available substitute but relies on EDGAR's spatial allocation methodology, which uses proxy datasets (point-source databases, population density, road networks, land use) that may not perfectly reflect Zacatecas's actual emission distribution
2. **Edge-cell shortfall**: The 665-cell mask covers ~66,500 km² vs. the official 72,275 km² (−7.8%), potentially underestimating emissions at state boundaries
3. **NG penetration uncertainty**: ProAire only lists industrial fuels qualitatively; actual NG consumption may differ from the 15% assumption
4. **ETS threshold allocation**: Without facility-level data, the 30-50-70% range is a broad estimate
5. **Temporal mismatch**: EDGAR 2024 data applied as representative of the current period; actual emissions may vary year to year
6. **Revenue cross-check gap**: Model gross S (1,060 KtCO₂e) is below revenue-implied (2,216 KtCO₂e); possible causes discussed in README
