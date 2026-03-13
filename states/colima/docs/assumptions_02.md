## Colima Overlap Estimation — Key Assumptions (02_estimate.py)

### Base data
- 2015 inventory (IMADES/Under2 Coalition, published 2019-01-31)
- AR5 GWPs throughout; no GWP conversion required
- Estimation tier: Tier 3 for stationary combustion sectors
  (INECC national sector growth rates applied to 2015 subsector totals)

### Extrapolation (2015 → 2025/2026)
- Electricity sector (Manzanillo plant): split into NG fraction (exempt,
  CAGR ~+0.2%/yr) and diesel+FO fraction (taxable, CAGR -2.0%/yr central).
  The diesel phase-out at CFE thermoelectrics is well-documented in SENER
  prospectiva; -2%/yr is conservative. Range: [-8%/yr, +1%/yr].
- Manufacturing sectors: INECC 1A2 national CAGR 2015-2022 applied by
  subsector class (+0.8% to +1.5%/yr). Range: ±2–3.5pp.
- Residential/commercial/agriculture: LP gas demand tied to Colima
  population growth (~+0.8%/yr). Range: [-1%, +2%/yr].

### Natural gas exemption
- Natural gas is EXEMPT from the Mexico federal carbon tax (Ley del IEPS,
  Artículo 2o-C) and, by design mirroring the federal structure, from
  state carbon taxes.
- The Manzanillo thermoelectric plant burns ~82% NG by CO2 mass.
  Only the diesel+FO fraction (~18%) is subject to either tax.
- This is the largest single driver of the gap between gross emissions
  and taxable coverage in Colima (reduces electricity sector in-scope
  emissions from ~7,128 GgCO2e to ~1,275 GgCO2e at 2015 base).

### Overlap structure
1. State tax × Federal carbon tax: 100% overlap on in-scope fuels.
   Federal tax is upstream (importer/distributor); state tax is downstream
   (end-use stationary source). Same fuels taxed twice. Overlap = state
   coverage exactly.
2. State tax × Pilot ETS: Large stationary emitters only (>25,000 tCO2e/yr
   threshold). Applies to Manzanillo plant (diesel fraction), metallurgical
   facilities. ETS is non-binding pilot — operational coverage likely lower
   than legal scope. Flag results accordingly.

### Uncertainty
- Point estimates are CAGR central values applied to 2015 base.
- Low/high bounds use CAGR low/high (see GROWTH_MAP in script).
- Additional structural uncertainty: Colima state tax design details not
  yet fully published (as of 2025 implementation start). Threshold for
  stationary sources and exact fuel list may differ from Jalisco model.
  This is the dominant source of uncertainty for 2025/2026 estimates.
- Results should be presented as ranges in the methodology note.