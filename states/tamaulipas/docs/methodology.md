# Methodology Note — Tamaulipas Carbon Pricing Overlap Analysis

**Case:** Mexico — Tamaulipas State Carbon Tax × Federal IEPS Carbon Tax × Mexico Pilot ETS
**Estimation tier:** Tier 3
**Base year:** 2013 (PECC Tamaulipas, SAR → AR5 converted)
**Target year:** 2025 (BaU projection from Table III)
**Version:** 1.0 — World Bank State & Trends of Carbon Pricing, working analysis

---

## 1. Overview and Policy Context

Tamaulipas operates under three overlapping carbon pricing instruments:

**S — Tamaulipas state carbon tax (2020–2022, 2024–present):** A direct emissions tax on fixed sources in productive processes emitting ≥25,000 tCO₂e/yr. Covers CO₂, CH₄, N₂O, HFCs, PFCs, SF₆. Natural gas is NOT exempted (unlike federal tax). Approximately 36 companies are covered.

**F — Federal IEPS carbon tax (Art. 2o-C):** An upstream fuel levy on fossil fuel sales except natural gas. Covers all downstream combustion — stationary and mobile.

**E — Mexico Pilot ETS (2020–):** Facility-level scheme covering direct emissions ≥25,000 tCO₂e/yr. Non-binding pilot phase; legal scope used.

**KEY STRUCTURAL FEATURE:** Tamaulipas is the only state analysed where the state carbon tax has the SAME 25,000 tCO₂e/yr threshold as the federal ETS. This means S and E select essentially the same set of large facilities — the overlap structure is determined by sector scope differences, not threshold differences.

---

## 2. Estimation Tier: Tier 3

Tier 3 applies because:
- No facility-level registry match available (Tier 1 not possible)
- Threshold fraction method used for both S and E (same methodology as E in other states)
- Fuel-fraction method used for F scope

**Tier 3 methods:**
- **S/E scope:** Pareto threshold method — estimate fraction of emissions from facilities ≥25k tCO₂e/yr per sector, using known industry structure (power plants, PEMEX refinery, petrochemical complex, ~36 covered companies)
- **F scope:** Fuel-fraction method — NG share from Tables 5.6/5.12/5.14; non-NG fraction subject to federal tax
- **No independence assumption required** for S/E (same threshold = same facilities)

---

## 3. GWP Conversion: SAR → AR5

The Tamaulipas inventory uses SAR GWPs (CH₄=21, N₂O=310). Conversion to AR5 (CH₄=28, N₂O=265) applied:

| Component | SAR total | AR5 total | Change |
|-----------|----------|----------|--------|
| Energy combustion | 30,863 | 30,800 | -0.2% (N₂O decrease offsets small CH₄ increase) |
| Fugitive O&G | 3,612 | 4,589 | +27% (large CH₄ component) |
| IPPU | 442 | 442 | 0% (CO₂ only) |
| AFOLU | 6,717 | 7,152 | +6.5% (mixed CH₄/N₂O) |
| Waste | 775 | 933 | +20% (large CH₄ component) |
| **Total** | **38,797** | **~40,361** | **+4.0%** |

---

## 4. Emission Inventory (2013 AR5, projected to 2025)

### Key 2025 projected values (AR5 GgCO₂e)

| IPCC code | Category | 2013 AR5 | 2025 AR5 | % of 2025 |
|-----------|----------|---------|---------|-----------|
| [1A1a] | Electricity generation | 13,908 | 18,346 | ~35% |
| [1A1b] | Petroleum refining | 2,952 | 3,893 | ~7% |
| [1A2] | Manufacturing | 1,978 | 2,630 | ~5% |
| [1A3] | Transport | 7,469 | 11,064 | ~21% |
| [1A4] | Other sectors (commercial, residential, agri) | 938 | 1,159 | ~2% |
| [1B2] | Fugitive O&G | 4,589 | 6,608 | ~13% |
| [2A4+2B8] | IPPU (caliza + negro de humo) | 442 | 391 | ~1% |
| [3] | AFOLU | 7,152 | 8,590 | ~16% |
| [4] | Waste | 933 | 1,156 | ~2% |

### Tamaulipas distinctive features

1. **2nd largest electricity producer nationally** (33,558 GWh in 2013; only 26% consumed in-state)
2. **Gas-dominated economy:** NG = 93% of electricity fuel, 94% of manufacturing fuel
3. **PEMEX infrastructure:** Refinería Francisco I. Madero (117,500 bbl/day); Burgos gas field; 4 cryogenic plants; petrochemical complex at Reynosa
4. **Large fugitive emissions:** 1B2 = 13% of state total (AR5) — mostly PEMEX CH₄
5. **No cement production** (2A1 = NE)
6. **HFC data gap** (2F1 = NE)

---

## 5. Instrument Scope Mapping

### S — Tamaulipas state carbon tax (≥25k tCO₂e/yr)

In scope (above-threshold facilities only): [1A1a] electricity; [1A1b] refining; [1A2] manufacturing; [1B2] fugitive O&G; [2A4] caliza; [2B8] negro de humo.

Exempt: transport (mobile); residential/commercial (below threshold); AFOLU; waste; facilities <25k.

### F — Federal IEPS carbon tax

Covered (non-NG fossil combustion): [1A1] electricity (combustóleo+diesel fraction ~7%); [1A1b] refinery (~15% non-NG); [1A2] manufacturing (~6.5% non-NG); [1A3] transport 100%; [1A4] other (~87% non-NG).

Not covered: NG combustion; fugitive emissions; process emissions.

### E — Mexico Pilot ETS (≥25k tCO₂e/yr)

Same threshold as S. Sectors: [1A1a], [1A1b], [1A2], [1B2], [2A4], [2B8].

---

## 6. Venn Decomposition

Because S and E share the same threshold, the decomposition simplifies:

For sectors in both S and E scope:
```
S∩F∩E  = above_threshold × (1 - ng_frac)    [non-NG at large plants]
S∩E    = above_threshold × ng_frac           [NG/process/fugitive at large plants]
F only = below_threshold × (1 - ng_frac)     [non-NG at small plants]
uncov  = below_threshold × ng_frac           [NG at small plants]
```

S∩F-only and S-only are zero for these sectors (same threshold → all above-threshold in both S and E).

For transport (not in S, not in E): F only = 100%.
For AFOLU, waste: uncovered.

---

## 7. Results Summary (2025 Central)

| Segment | GgCO₂e | % of state | Content |
|---------|--------|------------|---------|
| S∩F∩E | ~2,100 | ~4% | Non-NG combustion at large electricity/refinery/manufacturing plants |
| S∩E only | ~24,000 | ~45% | NG combustion at large plants; fugitive CH₄; IPPU process CO₂ |
| S∩F only | ~0 | ~0% | Near zero (same threshold for S and E) |
| S only | ~0 | ~0% | Near zero |
| F only | ~12,000 | ~23% | Transport; below-threshold non-NG combustion |
| Uncovered | ~15,000 | ~28% | AFOLU; waste; below-threshold NG; HFC data gap |

| Instrument | GgCO₂e | % | Range |
|-----------|--------|---|-------|
| S (state tax) | ~26,000 | ~49% | Narrower than other states due to threshold |
| F (federal) | ~14,000 | ~27% | Transport dominates |
| E (pilot ETS) | ~26,000 | ~49% | Near-identical to S |
| Union | ~38,000 | ~72% | |

---

## 8. Structural Findings

**1. State tax and ETS are near-identical in coverage.** Same threshold drives same facility selection. S∩E is the dominant segment (~45% of state). This is structurally different from all other states where S has no threshold.

**2. State tax coverage is the NARROWEST of all states analysed.** ~49% vs 34-55% in other states. The threshold excludes many small manufacturing, commercial, and agricultural facilities.

**3. Federal tax provides unique coverage of transport and below-threshold combustion.** F captures ~23% of state uniquely — mostly transport (21%) plus small non-NG facilities.

**4. Fugitive emissions are a major S∩E contributor.** 1B2 at ~13% of state (AR5) is mostly from PEMEX installations >> threshold. These are in S and E but NOT F (not combustion).

**5. NG dominance minimises S∩F∩E.** With electricity 93% NG and manufacturing 94% NG, only a small fraction of above-threshold emissions comes from non-NG fuels subject to F.

---

## 9. Comparison with Other States

| Feature | Durango | Querétaro | Tamaulipas |
|---------|---------|-----------|------------|
| S threshold | None | None | ≥25k tCO₂e/yr |
| NG in S scope | Yes | Yes (scope 1) | Yes |
| S gross coverage | 34.6% | ~40% | ~49% |
| Dominant segment | S∩E (NG at plants) | S∩E (NG at plants) | S∩E (NG at plants) |
| Key difference | No threshold | No threshold | Threshold = ETS |
| Fugitive role | Small (103 Gg) | Moderate | Large (4,589→6,608 Gg) |

---

## 10. Open Questions

1. Verify exact list of ~36 covered companies and their facility-level emissions
2. Obtain post-2013 inventory with AR5 GWPs to replace SAR conversion
3. Resolve combustóleo data gap for electricity generation sector
4. Quantify HFC (2F1) emissions — currently NE
5. Verify 2024 reinstatement terms and any scope changes from original 2020 design
6. Investigate gas natural stimulus provision (facilities choosing NG stimulus lose 25k exemption)

---

*This methodology note feeds into the State & Trends of Carbon Pricing working analysis. Update when post-2013 inventory data becomes available.*
