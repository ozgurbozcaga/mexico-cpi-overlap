# Methodology Note — Morelos Carbon Pricing Overlap Analysis

**Case:** Mexico — Morelos State Carbon Tax x Federal IEPS Carbon Tax x Mexico Pilot ETS
**Estimation tier:** Tier 3
**Base year:** 2014 (Morelos atmospheric emissions inventory, SDS/SEMARNAT/INECC)
**Target years:** 2025, 2026
**Version:** 1.0 — World Bank State & Trends of Carbon Pricing, working analysis

---

## 1. Critical Caveats — Read First

**Wrong inventory type.** The Morelos document is a 2014 air quality inventory, not an IPCC GHG inventory. GHG content is a supplementary annex. This creates three material limitations: (a) units are Mg/year, not GgCO2e — conversion required; (b) HFCs, PFCs, and SF6 are absent, meaning state tax S coverage is understated; (c) GWPs are not explicitly stated — AR5 applied for consistency.

**Old base year.** The 11-year extrapolation from 2014 to 2025/2026 carries substantially larger uncertainty than Colima (2015 base) or Durango (2022 base). Ranges should be read as order-of-magnitude estimates, not precise projections.

**Biogenic CO2.** The inventory includes CO2 from domestic wood combustion (~626,000 Mg, ~11% of state CO2) in its totals. This is biogenic and not subject to carbon pricing. It sits in the state total denominator but not in any instrument's coverage numerator.

---

## 2. Inventory Structure

Source: Inventario de Emisiones Contaminantes a la Atmosfera, Estado de Morelos, 2014.
SDS Morelos / SEMARNAT / INECC / LT Consulting. Published January 2017.
GWPs applied: AR5 (CH4=28, N2O=265).

### 2014 Emission totals (GgCO2e, AR5)

| Source type | CO2 | CH4 | N2O | Total GgCO2e |
|-------------|-----|-----|-----|-------------|
| Fixed industrial | 1,504.3 | 0.2 | 1.8 | 1,506.3 |
| Area sources | 1,198.8 | 234.3 | 16.3 | 1,449.4 |
| Mobile (road) | 2,619.4 | 8.3 | 35.7 | 2,663.4 |
| Mobile (non-road) | 1.6 | 0.0 | 0.1 | 1.7 |
| Waste (wastewater) | 0.0 | 98.4 | 4.5 | 102.9 |
| **State total** | **5,324.1** | **341.3** | **58.4** | **5,723.8** |

Note: Area sources include biogenic domestic wood CO2 (~626 GgCO2e).

### Key fixed-source sectors (CO2 dominant)

| Sector | CO2 Mg | % of fixed CO2 | Notes |
|--------|---------|----------------|-------|
| Cemento y cal | 901,618 | 59.9% | DOMINANT; ~60% process CO2 |
| Alimentos y bebidas | 292,319 | 19.4% | Sugar mills; fossil CO2 only |
| Quimica | 82,990 | 5.5% | CIVAC chemical zone |
| Vidrio | 106,470 | 7.1% | Glass industry |
| Celulosa y papel | 47,957 | 3.2% | Pulp/paper mills |
| Others + residual | 73,005 | 4.9% | All other sectors |

### Industrial fuel mix (Cuadro 3, energy shares)

| Fuel | Energy share | Taxable under IEPS |
|------|-------------|-------------------|
| Petroleum coke | 41.8% | YES |
| Bagasse | 20.3% | NO (biogenic) |
| Fuel oil | 14.5% | YES |
| LPG | 11.1% | YES |
| Diesel | 6.5% | YES |
| Natural gas | 4.0% | NO (statutory exemption) |
| Other | 1.8% | Mostly YES |

Taxable combustion CO2 fraction: ~96.7% (NG at only 3.3% — minimal IEPS gap)

---

## 3. Instrument Scope Mapping

### S — Morelos state carbon tax

Covers CO2, CH4, N2O, HFCs, PFCs, SF6 from stationary sources.
Exempt: mobile sources; maritime; small-scale agricultural activities.

In scope: all fixed industrial (FIXED); commercial combustion; domestic fossil combustion; fugitive O&G (if present).
Exempt: transport; livestock; agricultural burning; forest fires; wastewater.

DATA GAP: HFCs/PFCs/SF6 absent from 2014 inventory. Estimated impact: +3-4% on S coverage.

S gross coverage (2014 central): 2,304 GgCO2e (40.2% of state).

### F — Federal IEPS carbon tax

Covers all fossil fuel combustion except natural gas (upstream fuel levy).
Does NOT cover process emissions (cement calcination, glass) or fugitive CH4.

Because NG is only 3.3% of industrial combustion CO2 in Morelos (vs 99.6% in Durango), the NG exemption has negligible effect on F coverage of fixed sources. The dominant gap for F is cement PROCESS CO2 (calcination = ~541,000 Mg, in S and E but NOT in F).

F gross coverage (2014 central): 1,092 GgCO2e (19.1% of state).

### E — Mexico Pilot ETS

Legal scope >= 25,000 tCO2e/yr. Non-binding pilot (2020-).

Key Morelos facilities (inferred from inventory):
- 3 cement plants (all well above threshold)
- 2 glass plants (1+ likely above)
- 2 pulp/paper mills (1+ likely above)
- Several large chemical/food processing facilities

E gross coverage (2014 central): 1,291 GgCO2e (22.6% of state).

---

## 4. Cement Sector: The Defining Feature of Morelos

Cement (901,618 Mg CO2) accounts for 60% of all fixed-source CO2. The sector has a critical three-way split for carbon pricing:

    Process CO2 (calcination, ~60%):    in S, in E, NOT in F
    Combustion CO2 (petcoke/FO, ~40%): in S, in E, in F
    NG combustion (~1% of combustion):  in S, in E, NOT in F

This creates the dominant S∩E-only Venn segment in Morelos: 775 GgCO2e (13.5% of state) in the 2014 base year, which is cement calcination process CO2 at large plants. This segment is unique among the Mexican states analyzed — it doesn't appear in Colima, Durango, or Jalisco/Zacatecas.

The cement process split (60/40) is estimated from the national average for Mexican cement industry (INECC/IPCC 2006 clinker-based approach). If the Morelos clinker fraction is different, results change materially. A 55/45 split would shift ~90 GgCO2e from S∩E into S∩F∩E.

---

## 5. Venn Decomposition

For stationary sources (in S):

    S_F_E  = em x f_frac x e_frac      (taxable fuel at large plants)
    S_E    = em x (1-f_frac) x e_frac  (process CO2 + NG at large plants)
    S_F    = em x f_frac x (1-e_frac)  (taxable fuel at small facilities)
    S_only = em x (1-f_frac) x (1-e_frac)

For non-S sources (mobile, agri, waste):

    F_only = em x f_frac x (1-e_frac)  (transport fuels)

Independence assumption: F and E fractions treated as statistically independent within each category. For cement this is conservative since large plants (high E fraction) predominantly use petcoke (high F fraction) — actual S_F_E may be higher than estimated.

---

## 6. Results Summary

### 2025 central estimate

| Segment | GgCO2e | % of state | Content |
|---------|---------|------------|---------|
| S∩F∩E | 563 | 8.9% | Cement combustion (petcoke); glass/chemical taxable fuels at large plants |
| **S∩E only** | **820** | **13.0%** | **Cement calcination process CO2 — unique to Morelos** |
| S∩F only | 493 | 7.8% | Taxable fuels at small manufacturing facilities |
| S only | 498 | 7.9% | NG combustion; commercial NG; HFC data gap |
| **F only** | **3,139** | **49.8%** | **All mobile transport (road, non-road, aviation)** |
| Uncovered | 792 | 12.6% | Biogenic wood CO2; livestock CH4; ag burning; wastewater |

| Instrument | 2014 base | 2025 central | 2025 range |
|-----------|----------|--------------|-----------|
| S | 2,304 (40.2%) | 2,374 (37.7%) | 1,815-2,990 |
| F | 3,654 (63.8%) | 4,195 (66.5%) | 3,181-5,282 |
| E | 1,291 (22.6%) | 1,383 (21.9%) | 901-1,938 |
| Union | 4,969 (86.8%) | 5,513 (87.4%) | 4,319-7,450 |

**Key finding on F:** The federal tax has high coverage (64-67%) because it applies to ALL transport fuels. Mobile transport (~2,665 GgCO2e, ~47% of state) sits entirely in F_only — exempt from the state tax, below ETS threshold. This is the single largest Venn segment and makes Morelos structurally similar to Colima in terms of F dominance, but for a different reason: Colima has a large thermoelectric plant (Manzanillo diesel fraction), while Morelos has a large distributed vehicle fleet.

---

## 7. Comparison with Other States

| Feature | Colima (2025) | Durango (2025) | Morelos (2025) |
|---------|--------------|----------------|----------------|
| Base year | 2015 | 2022 | 2014 |
| NG in state tax | No | Yes | Yes |
| Dominant sector | Electricity (NG) | Electricity (NG) | Cement (petcoke) |
| S coverage | 19.5% | 34.2% | 37.7% |
| Defining Venn segment | S∩F (stationary comb.) | S∩E (NG at large plants) | S∩E (cement calcination) |
| Union coverage | 87.3% | 56.6% | 87.4% |
| Largest uncovered | ASOUT (~10%) | ASOUT+livestock (~43%) | Biogenic wood + livestock (12.6%) |

---

## 8. Open Issues

1. **HFC/PFC/SF6 data gap:** S coverage understated by estimated 3-4%. Should be flagged in any publication table with a note estimating the missing coverage.

2. **Cement process split:** 60/40 national average. Morelos-specific clinker production data (from CANACEM or INECC) would sharpen this — it is the highest-impact single assumption in this analysis.

3. **2014 base year:** Consider presenting results as "2014 base with illustrative extrapolation" rather than point estimates. A post-2015 state inventory would be transformative.

4. **Biogenic wood CO2 denominator effect:** The ~626 GgCO2e of biogenic domestic wood CO2 is included in the state total denominator but not in any instrument numerator. This slightly understates all instrument coverage percentages. Could be presented both ways (with and without biogenic CO2 in denominator).

---

*Methodology note for State & Trends of Carbon Pricing. Tier designation and assumptions require review before publication.*
