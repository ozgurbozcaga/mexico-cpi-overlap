# Assumptions Log -- 02_estimate.py (San Luis Potosi)

## Critical Data Challenges

### Challenge 1: Cumulative Data (NOT single-year)
The inventory reports cumulative 8-year totals for 2007-2014 with no per-year sectoral breakdowns. Annual values derived by dividing cumulative totals by 8. The stated annual average of 23.13 Mt CO2e/yr (SAR GWPs) is used as validation.

### Challenge 2: GWP Conversion (SAR -> AR5)
The inventory uses SAR GWPs (CH4=21, N2O=310). All other state pipelines use AR5 (CH4=28, N2O=265). Conversion applied at the subsector level using mass emissions:
- AR5 CO2eq = CO2 + CH4_mass x 28 + N2O_mass x 265
- CO2 component unchanged
- Net effect: CH4-heavy sectors increase (+33%); N2O-heavy sectors decrease (-14.5%)
- State total: SAR 23,135 -> AR5 ~23,743 GgCO2e/yr (+2.6%)

### Challenge 3: Old Base Year
2014 is the most recent year. Extrapolation to 2025/2026 deferred as a future step. Results reported for base-year annual average only.

### Challenge 4: No HFC/PFC Data
The inventory reports only CO2, CH4, N2O. The SLP carbon tax covers HFCs, PFCs, black carbon, CFCs, and HCFCs. This means S coverage is **understated** due to missing data for these gases.

### Challenge 5: IPPU Combustion/Process Mix
The RETC data used for IPPU does not distinguish combustion emissions from process emissions (confirmed p.23-24 of inventory). Assumptions:
- Cement/cal: Predominantly process CO2 (calcination of limestone). NOT covered by F.
- Metalurgia: Mix of process and combustion. Conservatively treated as ALL process (F=0). Some combustion CO2 may exist, which would increase F coverage.
- Glass: Predominantly process (melting). Treated as process (F=0).
- Chemical, automotive, celulosa: Treated as process (F=0). May understate F slightly.

## Instrument Scope Assumptions

### S -- SLP State Carbon Tax

| Decision | Assumption | Basis | Confidence |
|----------|-----------|-------|-----------|
| Scope 1 only | YES | Art. 36 SEXTIES: "emisiones directas...desde fuentes fijas" | High -- confirmed from primary legislation |
| No coverage threshold | All sizes covered | Art. 36 QUATER: no de minimis. Fiscal stimulus grants 100% payment exemption below 300 tCO2e/yr but compliance obligation remains | High |
| Gas scope | CO2, CH4, N2O, HFCs, PFCs, black carbon, CFCs, HCFCs | Ley de Hacienda; NO SF6 (removed June 2024 reform) | High |
| [1A1] electricity in scope | YES | Fixed source, productive process | High |
| [1A2] manufacturing in scope | YES | Fixed source, productive process | High |
| [1A4a] commercial/institutional | YES | Fixed source, productive process | High |
| [1A4b] residential | NO | Not a productive process | High |
| IPPU all subsectors in scope | YES | Process emissions from productive activities | High |
| [1A3] transport exempt | YES | Mobile sources | High |
| AFOLU exempt | YES | Non-combustion ag/forestry excluded | High |
| Waste exempt | YES | Waste management excluded | High |
| Agricultural combustion | IN scope | Fixed-source productive process (sugarcane processing, etc.) | Medium |

### F -- Federal IEPS Carbon Tax

| Parameter | Value (central) | Range | Basis |
|-----------|----------------|-------|-------|
| [1A1] NG fraction | 43.1% | 35-55% | 422.6 PJ NG x 57,755 EF / 56.58 Mt total CO2; Tamazunchale (NG CC) + Villa de Reyes (combustoleo) |
| [1A1] taxable (non-NG) | 56.9% | 45-65% | Complement of NG fraction; Villa de Reyes combustoleo drives this |
| [1A2] NG fraction | 35.3% | 28-42% | GN=6.53 / (GN+GLP+diesel=18.52); non-NG=64.7% |
| [1A2] taxable (non-NG) | 64.7% | 58-72% | **Highest non-NG industrial share of all states analysed** |
| [1A4] NG fraction | 25% | 15-35% | GLP dominant; some NG pipeline in SLP metro |
| [1A3] taxable | 100% | 100% | All gasoline/diesel covered |
| IPPU | 0% | 0% | Process emissions; not covered by fuel sales tax |

**[1A1] NG fraction derivation (critical -- differs from other states):**
- Energy balance: Total statewide NG = 542.7 PJ (2007-2014 cumulative)
- NG allocated to electricity generation: 422.6 PJ
- NG CO2 = 422.6 x 1000 x 57,755 / 1e9 = 24.41 Mt
- Total electricity CO2 = 56.58 Mt (Table 1)
- NG fraction = 24.41 / 56.58 = 43.1%
- Non-NG CO2 = 32.17 Mt (from combustoleo at Villa de Reyes + other fossil fuels)
- **Impact:** F covers ~57% of electricity CO2 -- the highest of any state analysed
- **Key difference:** Unlike Durango (99.6% NG) and Queretaro (99.99% NG), SLP has a major conventional thermal plant (Villa de Reyes) burning combustoleo

**[1A2] NG fraction derivation (critical -- highest non-NG of all states):**
- Table 1 industrial fuel CO2: GN=6.53, GLP=9.81, diesel=2.18 Mt (cumulative)
- Total industrial CO2 = 18.52 Mt; NG share = 35.3%
- Non-NG share = 64.7% (GLP=53.0%, diesel=11.8%)
- **Impact:** S*F manufacturing overlap is the largest of any state

### E -- Mexico Pilot ETS

| Category | ETS Fraction (central) | Range | Basis |
|----------|----------------------|-------|-------|
| [1A1] Electricity | 100% | 95-100% | Tamazunchale (2,515 kt/yr) + Villa de Reyes (1,383 kt/yr); both >> 25,000 tCO2e |
| [1A2] Manufacturing | 50% | 35-65% | Diverse industry; metalurgia single facility 2,071 kt >> threshold; many SMEs below |
| Cement/cal | 95% | 85-100% | Cerritos (1,076 kt/yr) + SLP city cement; all >> threshold |
| Metalurgia | 95% | 85-100% | Single SLP facility 2,071 kt/yr >> threshold |
| Vidrio | 90% | 75-100% | SLP glass facility 151 kt/yr >> threshold |
| Celulosa/papel | 85% | 70-95% | SLP pulp/paper 81.6 kt/yr >> threshold |
| Automotriz | 60% | 40-80% | Multiple plants; some large (20.9 kt, 4.2 kt) near/below threshold |
| Quimica | 50% | 30-70% | Scattered facilities; mixed sizes |
| Otras industrias | 40% | 20-60% | Diverse small industries |

### Partial S Coverage for 1A4 (Residential/Commercial Mix)

The inventory lumps residential + commercial + public combustion into a single "Residencial, Comercial y Publico" category (21.56 Mt CO2 cumulative). The SLP carbon tax covers commercial/institutional (productive processes at fixed sources) but NOT residential.

Split assumption:
- Commercial/public (in S): 40% of category (central), range 30-50%
- Residential (not in S): 60% of category
- Basis: National energy balance commercial/residential splits for Mexican states

## Venn Decomposition Independence Assumption

The NG-exempt fraction (F scope) and ETS threshold fraction (E scope) are treated as independent within each category. This is well-justified for SLP because:
- [1A1]: The two power plants use different fuels (Tamazunchale=NG, Villa de Reyes=combustoleo), but both are above ETS threshold. Independence is satisfied.
- [1A2]: Fuel mix varies by plant, but ETS threshold is facility-size-based. No strong a priori correlation between fuel choice and plant size.
- IPPU: Independence is vacuous (F=0 for all IPPU categories).

## Data Gaps and Caveats

1. **HFC/PFC data gap:** SLP carbon tax covers these gases but inventory has no data. S coverage is understated.
2. **IPPU combustion/process mix:** Conservative assumption that all IPPU is process (F=0).
3. **Old base year (2014):** No extrapolation to present. Results should be updated when newer inventory is available.
4. **RETC data is base year 2006:** Facility sizes may have changed by 2007-2014 period.
5. **Cumulative totals may mask trends:** 8-year average smooths interannual variation.
6. **Progressive rate reductions:** SLP tax has declining rates for large emitters (3 UMA down to 0.10 UMA for 1M+ tonnes). Does not affect coverage scope, only effective tax rate.
7. **Scope 1 confirmed:** No scope 2 uncertainty -- primary legislation explicitly states "direct emissions from fixed sources."
