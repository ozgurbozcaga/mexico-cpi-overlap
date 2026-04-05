# Methodology Note -- San Luis Potosi Carbon Pricing Overlap Analysis

**Case:** Mexico -- SLP State Carbon Tax x Federal IEPS Carbon Tax x Mexico Pilot ETS
**Estimation tier:** Tier 3
**Base year:** Annual average 2007-2014 (cumulative inventory / 8)
**GWPs:** AR5 (CH4=28, N2O=265) -- converted from SAR
**Version:** 1.0 -- World Bank State & Trends of Carbon Pricing, working analysis

---

## 1. Overview and Policy Context

San Luis Potosi operates under three overlapping carbon pricing instruments:

**S -- SLP state carbon tax (Ley de Hacienda, effective 1 Jan 2025):** A direct emissions tax on all GHGs (CO2, CH4, N2O, HFCs, PFCs, black carbon, CFCs, HCFCs -- NO SF6) from fixed sources in productive processes. Scope 1 only, confirmed from primary legislation. No coverage threshold (fiscal stimulus grants payment exemption below 300 tCO2e/yr but compliance obligation remains). Transport (mobile), residential, AFOLU non-combustion, and waste are excluded.

**F -- Federal IEPS carbon tax (Art. 2o-C):** An upstream fuel levy on fossil fuel sales except natural gas. Covers all downstream combustion -- stationary and mobile -- but structurally misses NG and non-combustion process emissions.

**E -- Mexico Pilot ETS (Sistema de Comercio de Emisiones):** A facility-level scheme covering direct emissions >= 25,000 tCO2e/yr. Non-binding pilot phase; legal scope used as upper bound per project methodology.

---

## 2. Data Processing: SAR to AR5 GWP Conversion

The SLP inventory uses SAR GWPs (CH4=21, N2O=310), while all other state analyses in this project use AR5 (CH4=28, N2O=265). Conversion is performed at the subsector level using mass emissions from Table 1:

    AR5_CO2eq = CO2_mass + CH4_mass x 28 + N2O_mass x 265

The CO2 component (which dominates at ~99% of mass) is unchanged. The net effect:
- CH4 equivalent increases by 33% (28/21)
- N2O equivalent decreases by 14.5% (265/310)
- State total: SAR ~23,135 GgCO2e/yr -> AR5 ~23,743 GgCO2e/yr (+2.6%)

Key sector-level effects:
- AFOLU (CH4-heavy from livestock): increases under AR5
- Waste (CH4-dominated): increases under AR5
- Metalurgia (significant N2O): decreases under AR5
- Energy, IPPU (CO2-dominated): minimal change

---

## 3. Cumulative-to-Annual Conversion

The inventory reports cumulative 8-year totals (2007-2014). No per-year sectoral breakdowns are available. Annual values are derived by dividing by 8. The stated annual average of 23.13 Mt CO2e/yr (SAR GWPs) validates this approach.

---

## 4. Estimation Tier: Tier 3

Tier 3 applies because no facility-level registry match between ETS participants and the state tax base is available.

**Tier 3 methods:**
- **F scope:** Fuel-fraction method -- compute NG share of CO2 per category using energy balance data and INECC emission factors. Non-NG fraction is subject to federal tax.
- **E scope:** Pareto threshold method -- estimate the share of emissions from facilities >= 25,000 tCO2e/yr using RETC facility-level data (base year 2006, Tables 19-23).
- **Independence assumption:** NG-exempt fraction and ETS threshold fraction treated as independent within each category.

---

## 5. SLP-Specific Features

### 5.1 Electricity: Highest Non-NG Share of Any State

SLP has two major power plants with different fuels:
- **Tamazunchale:** Combined-cycle, NG-fired (~2,515 kt CO2/yr)
- **Villa de Reyes:** Conventional thermoelectric, combustoleo-fired (~1,383 kt CO2/yr), being converted to combined cycle

NG fraction of electricity CO2 = 43.1% (central). Non-NG = 56.9%.
This means F covers ~57% of electricity CO2 -- **the highest of any state analysed** (vs. Durango 0.4%, Queretaro ~0%).

### 5.2 Industry: Highest Non-NG Fuel Share (65%)

Industrial fuel mix: GLP=53%, NG=35%, diesel=12%.
Non-NG share = 64.7% -- **the highest of all states analysed**.
This drives the largest S*F manufacturing overlap in the analysis.

### 5.3 Large Cement/Cal Sector

Cement/cal = ~2,555 GgCO2e/yr (process CO2). In S and E but NOT F (process emissions, not combustion). Cerritos facility alone = 1,076 kt CO2/yr.

### 5.4 Metalurgia with N2O

SLP metalurgia has significant N2O emissions (0.005496 Mt cumulative = 5,496 tonnes). The SAR->AR5 conversion reduces the N2O CO2eq (310->265), but the absolute amount remains material.

---

## 6. Instrument Scope Mapping

### S -- SLP state carbon tax

In scope: [1A1] electricity; [1A2] manufacturing; [1A4a] commercial/institutional; ALL IPPU process emissions.
Exempt: [1A3] transport; [1A4b] residential; AFOLU; waste; biogenic (lena, bagazo).

S gross coverage (central): see results below.

### F -- Federal IEPS carbon tax

Non-NG combustion: [1A1] ~57%; [1A2] ~65%; [1A3] 100%; [1A4] ~75%.
Not covered: NG combustion; process emissions; HFCs; AFOLU; waste.

### E -- Mexico Pilot ETS

Electricity 100% (both plants >> threshold); cement 95%; metalurgia 95%; vidrio 90%; celulosa 85%; manufacturing aggregate 50%.

---

## 7. Venn Decomposition

For categories in S scope:

    S_F_E  = em x f_frac x e_frac
    S_E    = em x (1 - f_frac) x e_frac
    S_F    = em x f_frac x (1 - e_frac)
    S_only = em x (1 - f_frac) x (1 - e_frac)

For 1A4 (residential/commercial mix): partial S coverage applied (40% commercial in S, 60% residential not in S).

For categories not in S scope:

    F_only = em x f_frac x (1 - e_frac)
    uncov  = em x (1 - f_frac) x (1 - e_frac)

---

## 8. Structural Findings

1. **SLP has the highest federal tax overlap with electricity** of any state analysed, due to Villa de Reyes combustoleo. F covers ~57% of electricity CO2.

2. **Largest S*F industrial overlap** driven by 65% non-NG industrial fuel share (GLP=53%, diesel=12%).

3. **Large cement/cal sector** (~2,555 GgCO2e/yr) is in S and E but NOT F (process CO2).

4. **No HFC/PFC data:** S coverage is understated because the inventory lacks data for gases covered by the SLP tax.

5. **No extrapolation:** Base year 2007-2014 is outdated. Results should be updated with newer data.

---

## 9. Open Questions

1. Updated SLP GHG inventory (post-2014) -- would eliminate need for cumulative-to-annual conversion.
2. SEMARNAT ETS participant list for SLP -- confirm registered facilities.
3. Villa de Reyes conversion status -- if completed, electricity NG fraction would increase dramatically, reducing F overlap.
4. Facility-level data for IPPU combustion/process split -- would improve F coverage estimate.
5. HFC inventory data -- would fill the data gap for S coverage.

---

*This methodology note feeds directly into the State & Trends of Carbon Pricing methodology note. Tier designation, assumptions, and uncertainty ranges should be reviewed before publication.*
