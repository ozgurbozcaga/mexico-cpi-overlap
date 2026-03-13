# Methodology Note — Durango Carbon Pricing Overlap Analysis

**Case:** Mexico — Durango State Carbon Tax × Federal IEPS Carbon Tax × Mexico Pilot ETS
**Estimation tier:** Tier 3
**Base year:** 2022 (IEEGYCEI Durango, Centro Mario Molina / SRNMA)
**Target years:** 2025, 2026
**Version:** 1.0 — World Bank State & Trends of Carbon Pricing, working analysis

---

## 1. Overview and Policy Context

The State of Durango operates under three overlapping carbon pricing instruments:

**S — Durango state carbon tax:** A direct emissions tax on stationary sources covering all major greenhouse gases (CO2, CH4, N2O, HFCs, SF6, PFCs, black carbon). Unlike the federal tax, natural gas is NOT exempted. Transport, waste, forestry, and agriculture are excluded from scope.

**F — Federal IEPS carbon tax (Art. 2o-C):** An upstream fuel levy on fossil fuel sales except natural gas. Covers all downstream combustion — stationary and mobile — but structurally misses NG (by statute) and non-combustion process emissions.

**E — Mexico Pilot ETS (Sistema de Comercio de Emisiones):** A facility-level scheme covering direct emissions >= 25,000 tCO2e/yr. Non-binding pilot phase (2020–); legal scope used as upper bound per project methodology.

The key policy design interaction: the state tax expands on the federal tax in one critical dimension — natural gas is in scope. Because Durango's electricity system is 99.6% gas-fired, the state tax reaches a large block of emissions the federal tax misses entirely.

---

## 2. Estimation Tier: Tier 3

Tier 3 applies because no facility-level registry match between ETS participants and the state tax base is available (which would be Tier 1). Fuel-fraction and Pareto/threshold methods are used instead.

**Tier 3 methods:**
- **F scope:** Fuel-fraction method — compute NG share of CO2 per category using Table 12 fuel consumption data and Table 13 national emission factors. Non-NG fraction is subject to federal tax.
- **E scope:** Pareto threshold method — estimate the share of emissions from facilities >= 25,000 tCO2e/yr per [1A2] subsector, based on Durango's known industry structure (key categories from Table 5) and sector concentration evidence.
- **Independence assumption:** NG-exempt fraction and ETS threshold fraction treated as independent within each category (see Section 5).

---

## 3. Emission Inventory

**Source:** IEEGYCEI Durango 2022, Centro Mario Molina for SRNMA, published 2024.
**GWPs:** AR5 (CH4=28, N2O=265). Consistent with INECC national INEGYCEI.
**Methodology:** IPCC 2006 Guidelines + 2019 Refinement; Tier 2 CO2 (national EFs), Tier 1 CH4/N2O.

### Key 2022 emission values (GgCO2e)

| IPCC code | Category | 2022 | % of state |
|-----------|----------|------|-----------|
| [1A1a] | Electricity generation | 3,316.2 | 25.1% |
| [1A2] | Manufacturing | 882.7 | 6.7% |
| [1A3] | Transport | 2,893.0 | 21.9% |
| [1A4+1B2] | Other energy + fugitive | 256.5 | 1.9% |
| [2] | PIUP | 116.9 | 0.9% |
| [3A+3C] | Livestock + land non-CO2 | 4,927.4 | 37.3% |
| [4] | Waste | 808.3 | 6.1% |
| **Total (excl. absorptions)** | | **13,201.6** | **100%** |

### Durango's distinctive features

**Gas-dominated electricity:** Five power plants (1,737 MW total) are predominantly CCGT. In 2022: NG=57.15 PJ, diesel=0.01 PJ, fuel oil=0.15 PJ. Using INECC EFs: NG = 99.62% of [1A1] CO2. Consequences: federal tax covers only 0.38% of electricity; state tax covers 100%; ETS covers 100%.

**Timber industry:** Durango is Mexico's leading lumber producer. [1A2j] wood products = 127.8 GgCO2e (14% of [1A2]), mostly distributed sawmills. ETS threshold fraction is lower than other manufacturing subsectors (40% central, range 20-60%).

---

## 4. Instrument Scope Mapping

### S — Durango state carbon tax

In scope (all gases, stationary sources): [1A1] electricity; [1A2] manufacturing; [1A4a/b] commercial/residential; [1B2] fugitive O&G; [2C] metal processes; [2D] lubricants; [2F] HFCs.

Exempt: [1A3] transport; [1A4c] agriculture; [3] ASOUT; [4] waste.

S gross coverage (2022 central): 4,572 GgCO2e (34.6% of state).

### F — Federal IEPS carbon tax

Covered (non-NG fossil combustion): [1A1] electricity 0.38%; [1A2] manufacturing ~29% (non-NG fraction); [1A3] transport 100%; [1A4a/b] ~85% (LPG+diesel; NG ~15% exempt); [1A4c] agriculture ~90%; [2D] lubricants 100%.

Not covered: any NG combustion (statutory exemption); [1B2] fugitives; [2C] process emissions; [2F] HFCs; ASOUT; waste.

F gross coverage (2022 central): 3,293 GgCO2e (24.9% of state).

### E — Mexico Pilot ETS

Threshold: >= 25,000 tCO2e/yr per facility.

| Category | Central | Range | Rationale |
|----------|---------|-------|-----------|
| [1A1] Electricity | 100% | 100% | All 5 plants well above threshold |
| [1A2d] Pulp/paper | 90% | 75-97% | Key category; large mills |
| [1A2e] Food/beverage | 70% | 50-85% | Large processors present |
| [1A2i] Mining | 80% | 60-95% | Large precious-metal mines |
| [1A2j] Wood/lumber | 40% | 20-60% | Distributed sawmills; lower concentration |
| [2C2] Ferroalloys | 90% | 70-100% | One large facility (48.9 GgCO2e) |
| [1B2] Fugitive | 50% | 30-70% | Some large NG infrastructure facilities |

E gross coverage (2022 central): 4,044 GgCO2e (30.6% of state).

---

## 5. Venn Decomposition

For categories in scope of S, emissions are partitioned into four segments:

    S_F_E  = em x f_frac x e_frac
    S_E    = em x (1 - f_frac) x e_frac        [NG at large plants]
    S_F    = em x f_frac x (1 - e_frac)        [taxable fuels at small facilities]
    S_only = em x (1 - f_frac) x (1 - e_frac)  [NG at small facilities; HFCs; process]

For categories not in S scope:

    F_only = em x f_frac x (1 - e_frac)        [transport; agri combustion]

**Independence assumption:** NG-exempt fraction and ETS threshold fraction treated as uncorrelated. If large plants use more NG than small plants (plausible for CCGT vs. older industrial boilers), this overstates S_F_E and understates S_E — a conservative bias toward F coverage. Update with facility-level data if available.

---

## 6. Extrapolation 2022 to 2025/2026

| Sector | Historical TMCA | Forward (central) | Key adjustment |
|--------|----------------|------------------|----------------|
| [1A1] | -2.38% | -1.0% | New 350 MW Lerdo CC plant (2024) moderates decline |
| [1A2] | +4.40% | +2.5% | COVID recovery normalising |
| [1A3] | +0.84% | +1.0% | Fleet growth continues |
| [1A4] | -0.09% | +0.5% | Population growth |
| [1B2] | +0.56% | +0.5% | NG infrastructure |

Fuel-fraction parameters held constant across years. Low/high scenarios apply +-40% of central growth rate.

---

## 7. Results Summary

### 2022 base year (central)

| Segment | GgCO2e | % of state | Content |
|---------|---------|------------|---------|
| S_F_E | 196 | 1.5% | Electricity diesel/FO; manuf. taxable at large plants |
| S_E only | 3,848 | 29.1% | Electricity NG (99.6% of [1A1]); manuf. NG at large plants |
| S_F only | 203 | 1.5% | Manuf. taxable fuels at small facilities |
| S only | 325 | 2.5% | HFCs; fugitives below ETS; small NG facilities |
| F only | 2,894 | 21.9% | Transport; agricultural combustion |
| Uncovered | 5,687 | 43.1% | Livestock; land non-CO2; waste; NG residential |

| Instrument | 2022 | 2025 (central) | 2025 range |
|-----------|------|----------------|-----------|
| S | 4,572 (34.6%) | 4,550 (34.2%) | 4,247-4,785 |
| F | 3,293 (24.9%) | 3,402 (25.6%) | 3,119-3,645 |
| E | 4,044 (30.6%) | 3,996 (30.0%) | 3,545-4,367 |
| Union | 7,466 (56.6%) | 7,531 (56.6%) | 6,714-8,197 |

---

## 8. Structural Findings

**1. State tax and federal tax are not near-redundant in Durango.** Because the federal tax exempts NG and NG dominates electricity generation (99.6% of [1A1] CO2), the two taxes address almost non-overlapping emission pools in the power sector. S_E_only (NG at large plants = 29.1% of state) is the dominant Venn segment.

**2. Transport is the largest F-only block.** [1A3] at 21.9% of state is covered only by the federal tax; the state tax explicitly exempts transport.

**3. Livestock and land remain fully uncovered.** ASOUT at 37.3% of state (predominantly livestock CH4) is covered by no instrument and accounts for most of the 43.1% uncovered share.

**4. ETS figures are upper bounds.** Legal scope only; non-binding pilot. Update to operational coverage when GX-ETS or binding successor enters force.

---

## 9. Comparison with Colima

| Feature | Colima (2025) | Durango (2025) |
|---------|--------------|----------------|
| NG in state tax | No | Yes |
| Electricity NG share of CO2 | 82% (exempt) | 99.6% (in scope) |
| S gross coverage | 19.5% | 34.2% |
| Dominant overlap type | S_F (stationary combustion) | S_E (NG at large plants) |
| Union coverage | 87.3% | 56.6% |
| Largest uncovered block | ASOUT+waste (~13%) | ASOUT+livestock (~43%) |

---

## 10. Open Questions

1. Full Durango state carbon tax legal text — exact scope clauses not independently confirmed; update when published.
2. SEMARNAT ETS participant list for Durango — confirm registered facilities to move toward Tier 2.
3. New Lerdo 350 MW combined cycle plant (2024) — update [1A1] when operational data available.
4. [1A2] fuel mix from COA data — Figure 13 gives percent shares; exact TJ values would improve F scope for manufacturing.
5. Post-2022 state inventory — if SRNMA publishes 2023/2024 data, replace extrapolation.

---

*This methodology note feeds directly into the State & Trends of Carbon Pricing methodology note. Tier designation, assumptions, and uncertainty ranges should be reviewed before publication.*
