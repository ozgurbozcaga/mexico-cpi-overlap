## Yucatan Overlap Estimation -- Key Assumptions (02_estimate.py)

### Base data
- 2023 inventory (SDS Yucatan / Centro Mario Molina, published 2024)
- AR5 GWPs throughout; NO GWP conversion required
- Estimation tier: Tier 3
- Base year: 2023 (no extrapolation needed -- data is current)

### Scope 1/2 ambiguity
The Yucatan carbon tax law uses the phrase "emisiones directas e indirectas"
-- the same ambiguity as Queretaro. Conservative scope 1 assumption applied.
No change to methodology. If scope 2 (electricity consumption) were included,
the S coverage would increase substantially, but this interpretation is not
confirmed by implementing regulations.

### Coverage threshold
NONE. The Yucatan carbon tax applies to all fixed sources engaged in
productive activities ("fuentes fijas... que realicen actividades productivas").
This is broader than states with explicit thresholds.

### NG stimulus (93% deduction)
The Yucatan carbon tax allows a 93% deduction on natural gas emissions.
This is a PAYMENT RELIEF mechanism, not a scope exclusion. NG emissions
are still counted in S scope for our coverage analysis. The distinction
matters: the tax still covers these emissions legally, even if the effective
rate is reduced.

### Calcination stimulus (up to 100% deduction)
CO2 from calcination/sintering processes can receive up to 100% deduction.
Again, this is PAYMENT RELIEF -- the emissions remain in S scope for
coverage calculation purposes.

### Tax rate
2.7 UMA per tCO2e (~MXN 305 in 2025).

### Gas scope
All six Kyoto basket gases: CO2, CH4, N2O, HFCs, PFCs, SF6.
This is the standard scope for Mexican state carbon taxes.

### HFC quantification (unique to Yucatan)
HFCs are quantified in the inventory: 331.81 GgCO2e (HFC) + 2.37 GgCO2e
(HCFC) = 334.18 GgCO2e total. These fall entirely in the S-only segment:
- NOT in F: HFCs are not from fossil fuel combustion
- NOT in E: HFCs are not direct CO2 emissions
- IN S: HFCs are Kyoto basket gases from fixed sources (refrigeration/AC)
This is the first state where HFCs are both in tax scope AND quantified
in the inventory data. Dominated by commercial refrigeration (291.61 GgCO2e)
reflecting Yucatan's tourism/hospitality economy.

### F overlap (federal IEPS)
- F covers fossil fuel combustion CO2, NG-exempt
- Electricity: 93.5% NG -> only 6.5% of electricity emissions in F scope
- Manufacturing: estimated 65% NG (central), range 50-80%
- Commercial: estimated 40% NG (central), range 20-60%
- Agricultural combustion: estimated 10% NG (central), range 0-20%
- Transport: 100% non-NG (all in F, not in S)
- IPPU process emissions: NOT in F (not combustion)

### E overlap (Pilot ETS)
- E covers direct CO2 from facilities >= 25,000 tCO2e/yr
- Electricity: 90% central (5 major plants, mostly combined cycle)
- Cement (2A1): 95% central (single CEMEX plant, ~318 GgCO2e)
- Food/beverage manufacturing: 40% central (some large plants)
- Non-metallic minerals: 60% central (few large operations)
- HFCs: NOT in E (not CO2 emissions)
- Fugitive emissions: NOT in E (not direct combustion CO2)

### Process CO2 handling
Cement (318 GgCO2e), cal (7.37), and iron/steel (3.32) process emissions
are in S and E but NOT F. This creates the S n E only segment:
process CO2 from large facilities is covered by both the state tax and
the ETS, but not by the federal fuel tax (since it's not combustion).

### Fugitive emissions (1B2)
Gas natural distribution fugitive emissions (89.95 GgCO2e, mostly CH4)
are in S scope (fixed source, productive activity) but NOT in F
(not combustion) and NOT in E (not direct CO2 above threshold).
These fall in S-only.

### Uncertainty
- Low/high bounds on NG fractions drive S n F uncertainty
- Low/high bounds on ETS fractions drive E-related segments
- No extrapolation uncertainty (data is 2023)
- Structural uncertainty: implementing regulations not yet final
