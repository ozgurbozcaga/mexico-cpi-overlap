# Assumptions — 02_estimate.py (CDMX)

## Instrument Scope Definitions

### S — CDMX State Carbon Tax
- **Gas scope:** CO₂, CH₄, N₂O only. HFCs are excluded.
- **Source scope:** Direct emissions from stationary sources in commercial, service, and industrial sectors.
- **Included categories:**
  - All fuentes puntuales (regulated industry): manufacturing, electricity generation, regulated commercial/services, fuel storage
  - Area-source combustion: comercial-institucional, industria no regulada
- **Excluded categories:**
  - Residential combustion (1,676 GgCO₂eq — largest exclusion)
  - Road transport (13,362 GgCO₂eq)
  - Aviation, rail, construction equipment, bus terminals (non-road mobile)
  - Waste (529 GgCO₂eq — landfill CH₄, wastewater)
  - Agriculture (N₂O from fertilisers: 6.4 GgCO₂eq)
  - Livestock (enteric fermentation, manure: 23.5 GgCO₂eq)
  - Emisiones domésticas (275 GgCO₂eq — domestic non-combustion CO₂)
  - HFC from residential AC maintenance (0.7 GgCO₂eq)
  - Asados al carbón (charcoal grills: 24 GgCO₂eq — excluded conservatively as informal/mixed residential-commercial)
  - Agricultural equipment combustion (25 GgCO₂eq — mobile, not stationary)
- **HFC deduction:** Inventory-reported HFC in point sources is ~43 tCO₂eq (negligible). S coverage is computed from CO₂ + CH₄×28 + N₂O×265 for each S-covered category.

### F — Federal IEPS Carbon Tax
- **Mechanism:** Upstream excise on fossil fuels at point of sale. Covers combustion CO₂ only (not CH₄, N₂O, HFC, process, fugitive).
- **Key exemption:** Natural gas is fully exempt.
- **Coverage:** Applies to all sectors consuming non-NG fossil fuels (gasoline, diesel, gas LP, fuel oil, turbosina, coke).
- **Non-NG fraction by sector** (central / low / high):

| Sector | Central | Low | High | Basis |
|--------|---------|-----|------|-------|
| Industrial (regulated + unregulated) | 0.8% | 0.4% | 1.5% | Annex Tables 67-69: NG = 1,433.5M m³ vs LP = 65.6k m³ + diesel = 8.7k m³. NG provides 99.4% of fossil energy. |
| Commercial (regulated + unregulated) | 0.3% | 0.1% | 0.5% | NG = 41.8M m³ vs LP = 131.6k m³. NG provides 99.8% of fossil energy. |
| Electricity generation | 1.5% | 0.5% | 3.0% | CDMX power plants are primarily NG-fired (no coal). Small diesel backup generation. |
| Residential | 0.3% | 0.1% | 0.5% | Same fuel mix as commercial; NG dominates. |
| Transport | 100% | 100% | 100% | Gasoline and diesel; no NG vehicles in fleet. |
| Aviation | 100% | 100% | 100% | Turbosina (jet fuel). |
| Rail/construction/bus terminals | 100% | 100% | 100% | Diesel-dominated. |
| Agriculture equipment | 100% | 100% | 100% | Diesel and LP. |

**Critical note:** The extremely high NG share (99.4–99.8%) in CDMX industrial and commercial sectors means that F covers less than 1% of combustion emissions in S-covered sectors. This creates a dominant S-only block and a negligible S∩F overlap — the strongest NG exemption effect observed across all Mexico state pipelines.

### E — Mexico Pilot ETS
- **Threshold:** ≥ 25,000 tCO₂e/yr per facility
- **Scope:** Direct CO₂ from energy and industrial sectors
- **Status:** Pilot phase (non-binding); treated as legal coverage for overlap purposes
- **Coverage fractions** (central / low / high):

| Category | Central | Low | High | Rationale |
|----------|---------|-----|------|-----------|
| Electricity generation | 70% | 50% | 85% | ~20 federal power plants in ZMVM. Largest (Jorge Luque, Valle de México) well above 25k tCO₂e threshold. Many small distributed generators below. CDMX-specific share uncertain. |
| Manufacturing (regulated) | 30% | 15% | 50% | ~502 industrial facilities, avg ~690 tCO₂e. CDMX has no heavy industry (no refinery, no large cement, no steel). A few large chemical plants (industria química: 111 GgCO₂eq from ~41 local + federal plants) may cross threshold. Lower than Guanajuato/Durango. |
| Commercial (regulated) | 2% | 0% | 5% | ~1,838 facilities, avg ~105 tCO₂e. Only very largest (hospitals, shopping centres with large gas boilers) could conceivably reach 25k. |
| Area-source combustion | 0% | 0% | 0% | By definition, non-regulated small sources are below ETS threshold. |

## Venn Decomposition Logic

Eight segments computed via inclusion-exclusion:
- **S∩F∩E:** Non-NG combustion CO₂ in above-threshold S-covered facilities. Tiny (~4.5 GgCO₂eq central) because both F-fraction and E-fraction are small in the same categories.
- **S∩F (not E):** Non-NG combustion CO₂ in below-threshold S-covered sources. Small (~24 GgCO₂eq).
- **S∩E (not F):** NG combustion CO₂ + CH₄/N₂O from above-threshold S-covered facilities. This is the dominant overlap segment (~350 GgCO₂eq). Driven by large electricity generators and chemical plants burning NG.
- **S only:** NG combustion CO₂ + CH₄/N₂O in below-threshold S-covered sources. Dominant segment (~3,146 GgCO₂eq). Driven by industria no regulada (2,399 GgCO₂eq) burning mostly NG and being below ETS threshold.
- **F∩E (not S):** Expected zero — all E-eligible categories are also in S scope.
- **F only:** Non-NG combustion CO₂ outside S scope. Overwhelmingly road transport (~13,595 GgCO₂eq).
- **E only:** Expected zero — same reasoning as F∩E.
- **Uncovered:** Emissions outside all three instruments (~2,768 GgCO₂eq): residential NG combustion, waste CH₄, residential other, livestock, agriculture, HFC.

## Key Structural Features of CDMX

1. **Service-dominated economy:** Transport = 67% of GHG, area combustion = 28%, point sources = 4.5%. No heavy industry. This contrasts sharply with Guanajuato (refinery) or Morelos (cement).
2. **NG dominance in stationary combustion:** 99.4% industrial, 99.8% commercial. Creates near-complete separation between S and F in stationary sectors.
3. **COVID-2020 baseline:** All emissions depressed. Industrial/commercial sectors hit hardest (GDP decline up to 43% in some subsectors). Transport decline was 60–80% in congestion metrics but partial recovery by late 2020.
4. **Largest single emitter category:** Industria no regulada (2,399 GgCO₂eq) — small manufacturing and workshops burning mostly NG. These are in S scope but below ETS threshold and mostly exempt from F due to NG use.
5. **Paper industry anomaly:** At ZMVM level, paper industry = 5,935 GgCO₂eq (8.8% of total). But CDMX's share is only 27.5 GgCO₂eq — the large mills (Kimberly-Clark, etc.) are in Estado de México.
