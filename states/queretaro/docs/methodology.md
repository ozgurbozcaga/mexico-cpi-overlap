# Methodology Note — Queretaro Carbon Pricing Overlap Analysis

**Case:** Mexico — Queretaro State Carbon Tax x Federal IEPS Carbon Tax x Mexico Pilot ETS
**Estimation tier:** Tier 3
**Base year:** 2021 (IEGYCEI Queretaro, SEDESU)
**Target years:** 2025, 2026
**Version:** 1.0 — World Bank State & Trends of Carbon Pricing, working analysis

---

## 1. Overview and Policy Context

The State of Queretaro operates under three overlapping carbon pricing instruments:

**S — Queretaro state carbon tax:** A direct emissions tax on productive processes / fixed sources covering ALL Kyoto greenhouse gases (CO2, CH4, N2O, HFCs, PFCs, SF6). Economy-wide scope for stationary sources. Unlike the federal tax, natural gas is NOT exempted. Transport, residential, AFOLU, and waste are excluded.

**F — Federal IEPS carbon tax (Art. 2o-C):** An upstream fuel levy on fossil fuel sales except natural gas. Covers all downstream combustion — stationary and mobile — but structurally misses NG (by statute) and non-combustion process emissions.

**E — Mexico Pilot ETS (Sistema de Comercio de Emisiones):** A facility-level scheme covering direct emissions >= 25,000 tCO2e/yr. Non-binding pilot phase (2020–); legal scope used as upper bound per project methodology.

The key policy design interaction: the state tax covers ALL Kyoto gases from fixed sources, while the federal tax exempts NG. Because Queretaro's electricity is virtually 100% NG-fired and manufacturing is ~95.5% NG by CO2, the federal tax covers almost nothing in the two largest stationary sectors. The state tax therefore provides the primary carbon pricing coverage for stationary sources.

---

## 2. Estimation Tier: Tier 3

Tier 3 applies because no facility-level registry match between ETS participants and the state tax base is available.

**Tier 3 methods:**
- **F scope:** Fuel-fraction method — compute NG share of CO2 per category using Table 10/11 fuel consumption data and INECC emission factors. Non-NG fraction is subject to federal tax.
- **E scope:** Pareto threshold method — estimate the share of emissions from facilities >= 25,000 tCO2e/yr based on known plant-level data (electricity) and sector concentration evidence (manufacturing, IPPU).
- **Independence assumption:** NG-exempt fraction and ETS threshold fraction treated as independent within each category (see Section 5).

---

## 3. Emission Inventory

**Source:** Inventario de Emisiones de Gases y Compuestos de Efecto Invernadero del Estado de Queretaro, Ano Base 2021. Published by SEDESU, December 2023.
**GWPs:** AR5 (CO2=1, CH4=28, N2O=265, HFCs per species). Consistent with INECC national INEGYCEI.
**Methodology:** IPCC 2006 Guidelines; predominantly Tier 2; Tier 1 for livestock enteric fermentation, metal industry, and HFC refrigeration.

### Key 2021 emission values (GgCO2e)

| IPCC code | Category | 2021 | % of state |
|-----------|----------|------|-----------|
| [1A1] | Electricity generation | 1,895.94 | 17.9% |
| [1A2] | Manufacturing | 2,182.47 | 20.6% |
| [1A3] | Transport | 2,503.49 | 23.6% |
| [1A4a] | Commercial | 84.93 | 0.8% |
| [1Ab] | Residential | 381.05 | 3.6% |
| [1A4c] | Agriculture combustion | 119.08 | 1.1% |
| [2A] | Minerals (cal + vidrio) | 163.73 | 1.5% |
| [2C1] | Iron/steel | 0.28 | 0.0% |
| [2F] | HFCs | 70.48 | 0.7% |
| [3A+3C] | AFOLU (gross) | 2,449.76 | 23.1% |
| [4] | Waste | 738.48 | 7.0% |
| **Total (excl. absorptions)** | | **10,589.69** | **100%** |

### Queretaro's distinctive features

**NG-dominated electricity:** Three power plants (El Sauz, Queretaro, San Juan del Rio). In 2021: NG=32.80 PJ, diesel=3.80E-05 PJ. Using INECC EFs: NG=99.9998% of [1A1] CO2. Consequences: federal tax covers ~0% of electricity; state tax covers 100%; ETS covers 98.9% (one small plant below threshold).

**NG-dominated manufacturing:** Table 11 shows NG=36.11 PJ of 37.46 PJ total fossil fuel. After emission factor correction: NG=95.51% of fossil CO2. Strong automotive/aerospace cluster (BMW, Safran, Bombardier). Federal tax covers only ~4.5% of manufacturing CO2.

**All Kyoto gases in state tax:** Uniquely broad scope captures HFC refrigeration (70.48 GgCO2e), dominated by mobile AC (65.57 GgCO2e). These are in S but not in F or E.

---

## 4. Instrument Scope Mapping

### S — Queretaro state carbon tax

In scope (all Kyoto gases, fixed sources): [1A1] electricity; [1A2] manufacturing; [1A4a] commercial; [1A4c] agricultural combustion; ALL IPPU (2A2 cal, 2A3 vidrio, 2C1 iron/steel, 2F HFCs).

Exempt: [1A3] transport; [1Ab] residential; [3] AFOLU; [4] waste.

S gross coverage (2021 central): ~4,617 GgCO2e (43.6% of state).

### F — Federal IEPS carbon tax

Covered (non-NG fossil combustion): [1A1] ~0%; [1A2] ~4.5%; [1A3] ~98.6%; [1A4a] ~80%; [1Ab] ~95%; [1A4c] ~98%.

Not covered: NG combustion (statutory exemption); process emissions (IPPU); HFCs; AFOLU; waste.

### E — Mexico Pilot ETS

Threshold: >= 25,000 tCO2e/yr per facility.

| Category | Central | Range | Rationale |
|----------|---------|-------|-----------|
| [1A1] Electricity | 98.9% | 98.5-99.5% | 2 of 3 plants above threshold; one small plant (20.2 GgCO2e) excluded |
| [1A2] Manufacturing | 75% | 60-88% | Strong auto/aero cluster; large concentrated plants |
| [2A2] Lime | 60% | 40-80% | 2 plants ~24 GgCO2e each, near threshold |
| [2A3] Glass | 95% | 85-100% | 2 companies ~57 GgCO2e each >> threshold |
| [2C1] Iron/steel | 0% | 0% | 280 tCO2e << threshold |
| [2F] HFCs | 0% | 0% | Refrigerant leaks not in ETS |

---

## 5. Venn Decomposition

For categories in scope of S, emissions are partitioned into four segments:

    S_F_E  = em x f_frac x e_frac
    S_E    = em x (1 - f_frac) x e_frac        [NG at large plants]
    S_F    = em x f_frac x (1 - e_frac)        [taxable fuels at small facilities]
    S_only = em x (1 - f_frac) x (1 - e_frac)  [NG at small facilities; HFCs; process]

For categories not in S scope:

    F_only = em x f_frac x (1 - e_frac)        [transport; residential non-NG]
    F_E    = em x f_frac x e_frac               [virtually zero — no ETS in non-S sectors]
    E_only = em x (1 - f_frac) x e_frac        [virtually zero]
    uncov  = em x (1 - f_frac) x (1 - e_frac)  [AFOLU; waste; transport NG; residential NG]

**Independence assumption:** NG-exempt fraction and ETS threshold fraction treated as uncorrelated. In Queretaro's case, this is well-supported because the NG share is extremely high across all plant sizes (~96% in manufacturing). Update with facility-level data if available.

---

## 6. Extrapolation 2021 to 2025/2026

| Sector | Forward (central) | Low | High | Key adjustment |
|--------|------------------|-----|------|----------------|
| [1A1] | -0.5%/yr | -2.5% | +1.0% | Grid relatively stable; slight efficiency gains |
| [1A2] | +3.0%/yr | -0.5% | +5.5% | Strong auto/aero cluster; above-average growth |
| [1A3] | +1.5%/yr | -0.5% | +3.0% | Population/fleet growth in ZMQ metro |
| [1A4] | +1.0%/yr | -1.0% | +2.0% | Services sector growth |
| IPPU | +1.0%/yr | -1.0% | +2.5% | Construction-driven demand |
| HFCs | +2.0%/yr | +0.5% | +3.5% | National cooling demand increase |

Fuel-fraction parameters held constant across years. Low/high scenarios apply asymmetric growth rate ranges.

---

## 7. Structural Findings

**1. State tax is the primary carbon pricing instrument for stationary sources.** Because NG dominates both electricity (~100%) and manufacturing (~95.5%), the federal tax is nearly irrelevant for the two largest stationary sectors. The state tax fills this gap by covering NG.

**2. The dominant Venn segment is S^E only (NG at large plants).** Electricity NG at El Sauz and San Juan del Rio, plus manufacturing NG at large plants, form the largest overlap — state tax plus ETS, with no federal tax.

**3. Transport is the largest F-only block.** [1A3] at ~23.6% of state is covered only by the federal tax.

**4. HFC refrigeration is uniquely covered by the state tax.** At 70.48 GgCO2e (0.7% of state), HFCs are in S scope (all Kyoto gases) but not in F (not a fossil fuel) or E (refrigerant leaks not in ETS).

**5. AFOLU and waste remain fully uncovered.** AFOLU at ~23.1% and waste at ~7.0% together account for ~30% of state emissions, covered by no instrument.

**6. Small Queretaro electricity plant creates a non-trivial ETS gap.** Unlike most states where all power plants exceed the 25,000 tCO2e threshold, Queretaro's small plant (20,200 tCO2e) falls below, reducing ETS coverage of [1A1] to 98.9%.

---

## 8. Open Questions

1. Full Queretaro state carbon tax legal text — exact scope clauses and rate structure.
2. SEMARNAT ETS participant list for Queretaro — confirm registered facilities.
3. [1A2] subsector breakdown — inventory reports aggregate [1A2]; facility-level data would improve ETS estimates.
4. [2A2] lime plant sizes — the two plants are near the 25kt threshold; COA data could resolve.
5. Post-2021 state inventory — if SEDESU publishes 2022/2023 data, replace extrapolation.

---

*This methodology note feeds directly into the State & Trends of Carbon Pricing methodology note. Tier designation, assumptions, and uncertainty ranges should be reviewed before publication.*
