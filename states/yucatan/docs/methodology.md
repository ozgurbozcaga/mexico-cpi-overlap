## Yucatan -- Methodology Note

### Overview
Three-instrument Venn decomposition for Yucatan, Mexico.
Eight segments via inclusion-exclusion across:
- **S**: Yucatan state carbon tax
- **F**: Mexico federal IEPS carbon tax
- **E**: Mexico Pilot ETS

### Estimation tier
**Tier 3** -- Direct inventory data (2023, AR5 GWPs) with instrument scope
applied at IPCC subcategory level. No extrapolation needed (current year data).
No GWP conversion needed (inventory already uses AR5).

### Data flow
1. `01_clean.py`: Extract 2023 emissions from PDF inventory (Table 9).
   Validate sector totals against Table 8. Extract electricity fuel
   consumption (Table 12). Map IPCC categories to S/F/E scope.
2. `02_estimate.py`: Apply eight-segment Venn decomposition.
   NG exemption fractions determine S n F overlap.
   ETS threshold fractions determine E-related segments.
   Central/low/high scenarios for uncertainty.
3. `03_outputs.py`: Publication figures (stacked bar, horizontal bar,
   HFC breakdown) and CSV tables.

### Key methodological choices
1. **Scope 1 only**: Conservative assumption despite "directa e indirecta"
   language in the law.
2. **NG/calcination stimuli as payment relief**: Emissions remain in S scope
   for coverage calculations.
3. **No threshold**: All fixed productive sources covered.
4. **HFCs included**: First state where HFCs are both in scope and quantified.
5. **Process CO2 in S n E but not F**: Cement/cal/iron process emissions
   create a meaningful S n E only segment.

### Yucatan-specific features
- **Best inventory quality**: AR5 GWPs, 2023 data, no conversion needed
- **HFC S-only segment**: 334 GgCO2e (3.2% of state) -- largest S-only
  component, driven by tourism/hospitality commercial AC
- **93.5% NG electricity**: Minimal S n F overlap in power sector
- **Net carbon sink**: Forest absorption exceeds gross emissions
- **Tourism economy**: High HFC from commercial AC, significant aviation
