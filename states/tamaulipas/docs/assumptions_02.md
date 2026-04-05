# Assumptions Log — 02_estimate.py (Tamaulipas)

## CRITICAL: SAR → AR5 GWP Conversion

The inventory uses SAR GWPs (CH₄=21, N₂O=310). All other state pipelines use AR5 (CH₄=28, N₂O=265).

| Gas | SAR GWP | AR5 GWP | Conversion factor | Effect |
|-----|---------|---------|-------------------|--------|
| CH₄ | 21 | 28 | ×1.3333 | Increases CH₄ contributions by 33% |
| N₂O | 310 | 265 | ×0.8548 | Decreases N₂O contributions by 15% |
| CO₂ | 1 | 1 | ×1.0000 | No change |

Net effect: total increases ~4% (CH₄ increase dominates, especially fugitive emissions).

**Largest impact:** 1B2 fugitive O&G: SAR=3,612 → AR5=4,589 GgCO₂e (+27%) due to large CH₄ component.

## CRITICAL: Dual 25,000 tCO₂e/yr Threshold

**Unique to Tamaulipas:** The state carbon tax has a LEGAL COVERAGE THRESHOLD of 25,000 tCO₂e/yr. Facilities below this are EXEMPT. This is the same threshold as the federal ETS.

| Feature | Other states | Tamaulipas |
|---------|-------------|------------|
| S threshold | None (all facilities) | ≥25,000 tCO₂e/yr |
| E threshold | ≥25,000 tCO₂e/yr | ≥25,000 tCO₂e/yr |
| Consequence | S and E differ by sector scope AND threshold | S and E differ only by sector scope |
| S coverage | 30-55% of state | ~25-35% of state |

**Implication:** Because S and E have the same threshold, for sectors in BOTH S and E scope, the above-threshold coverage is identical. There is no S∩F-only or S-only segment for these sectors (any emission above threshold is in both S and E).

## Instrument Scope Assumptions

### S — Tamaulipas State Carbon Tax

| Decision | Assumption | Basis | Confidence |
|----------|-----------|-------|-----------|
| Scope 1 only | YES (conservative) | Law text: "expulsiones directas o indirectas" is ambiguous; same approach as Querétaro | Medium — flag in methodology |
| NG in scope | YES | No NG exemption in state tax | High |
| Threshold | 25,000 tCO₂e/yr | Legal provision; ~36 companies covered | High |
| Transport exempt | YES (mobile sources) | "Fixed sources" — transport is mobile | High |
| Residential exempt | YES (below threshold) | No residential facility exceeds 25,000 tCO₂e/yr | High |
| AFOLU exempt | YES | Not productive process fixed sources | High |
| Waste exempt | YES | Not covered | High |
| 1A4a commercial | Effectively exempt | No commercial facility exceeds 25k threshold | High |
| Suspended 2023 | Ignored for 2025 analysis | Tax reinstated 2024; analysis covers active period | Medium |

### F — Federal IEPS Carbon Tax

| Parameter | Value (central) | Range | Basis |
|-----------|----------------|-------|-------|
| [1A1a] NG fraction of CO₂ | 92.7% | 90–97% | Table 5.12 NG+diesel + estimated combustóleo (5.2% per text) |
| [1A1b] NG fraction | 85% | 75–95% | Table 5.11 shows only NG; PEMEX uses mixed fuels; wide uncertainty |
| [1A2] NG fraction of CO₂ | 93.5% | 88–97% | Table 5.14: NG=32,428 TJ, diesel=1,360 TJ, GLP=880 TJ |
| [1A4] NG fraction | 13% | 8–20% | Table 5.6: residential NG=1.79 PJ vs GLP=11.99 PJ |
| [1B2] F coverage | 0% | 0% | Fugitive CH₄ from O&G infrastructure; not covered by fuel tax |
| [2A4] F coverage | 0% | 0% | Process CO₂ from caliza; not fuel combustion |
| [2B8] F coverage | 0% | 0% | Process CO₂ from carbon black; not fuel combustion |
| Transport F coverage | 100% | 100% | All transport fuels taxable (gasoline, diesel, turbosina) |

**[1A1a] combustóleo data gap:**
- Table 5.12 excludes combustóleo (SIE data not available at sector level)
- Inventory text (p.115): "combustóleo represents 5.2% of electricity fuel"
- Estimated: 13,585 TJ combustóleo → ~1,051 GgCO₂
- This makes the "real" NG fraction ~92.7% (vs 99.9% if using only Table 5.12 NG+diesel)
- **Sensitivity:** ±4% on NG fraction → ±600 GgCO₂e change in S∩F∩E vs S∩E allocation

### E — Mexico Pilot ETS / Threshold Fractions

| Sector | Central | Range | Basis |
|--------|---------|-------|-------|
| [1A1a] electricity | 100% | 100% | 8 plants (5,453 MW total), all >> 25k threshold |
| [1A1b] refinery | 100% | 100% | PEMEX Cd. Madero single facility >> threshold |
| [1A2] manufacturing | 65% | 50–80% | ~36 total companies covered; petrochemical, food, auto parts; many SMEs below |
| [1A4] other sectors | 0% | 0% | All commercial/residential below threshold |
| [1B2] fugitive O&G | 80% | 60–95% | PEMEX: 4 cryogenic plants, gas processing, pipeline compression >> threshold |
| [2A4] caliza | 50% | 20–80% | Single operation, uncertain if above threshold |
| [2B8] negro de humo | 90% | 70–100% | Carbon black plant, likely 1–2 large facilities |
| [2F1] HFC | 0% | 0% | NE data; not in ETS scope |

## BaU Projection Assumptions (2013 → 2025)

Growth ratios derived from Table III (PECC Tamaulipas) BaU projections:

| Sector | 2013 (SAR) | 2025 (SAR) | Growth ratio | Notes |
|--------|-----------|-----------|-------------|-------|
| Industria Energética | 16,859 | 22,243 | ×1.319 | Electricity + refining |
| Ind. Manufacturera | 1,978 | 2,630 | ×1.330 | |
| Transporte | 7,476 | 11,078 | ×1.482 | Fleet growth + population |
| Otros sectores | 939 | 1,159 | ×1.235 | |
| Emisiones Fugitivas | 3,612 | 5,201 | ×1.440 | O&G infrastructure growth |
| Procesos Industriales | 442 | 390 | ×0.883 | Declining (caliza) |
| Desechos | 775 | 961 | ×1.240 | Population-driven |
| Agricultura y Ganadería | 3,045 | 3,751 | ×1.232 | |
| Cambio Uso Suelo | 3,669 | 3,565 | ×0.972 | Slight decline |

**Validation:** Table III 2022 projection = 47,512 GgCO₂e; 2022 actual = 47,530 GgCO₂e (0.04% difference).

**Low/high scenarios:** ±8% of BaU 2025 total, combined with low/high threshold fractions.

## Venn Decomposition Logic

Because S and E share the same threshold, the decomposition simplifies:

For sectors in BOTH S and E scope (1A1a, 1A1b, 1A2, 1B2, 2A4, 2B8):
- S∩F∩E = above_threshold × f_frac (non-NG combustion at large plants)
- S∩E   = above_threshold × (1 - f_frac) (NG/process/fugitive at large plants)
- S∩F   = 0 (same threshold → if above threshold for S, also above for E)
- S only = 0 (same reasoning)
- F only = below_threshold × f_frac (non-NG combustion at small plants)
- Uncovered = below_threshold × (1 - f_frac)

For sectors ONLY in S scope (2F1 HFC):
- S∩F = above_threshold × f_frac (but HFC is NE → all zero)
- S only = above_threshold × (1 - f_frac)

For sectors NOT in S scope (transport, AFOLU, waste, residential):
- F only = emissions × f_frac (transport)
- Uncovered = emissions × (1 - f_frac)

**No independence assumption needed** for the S/E interaction (unlike Durango) because S and E have the same threshold — they select the same facilities.

## Data Gaps Flagged

1. **HFC (2F1):** Not estimated in inventory. Tamaulipas covers HFCs in state tax gas scope but has no quantification. This is a known data gap — potential underestimate of S coverage.
2. **Combustóleo in electricity:** Estimated from text, not from data tables. Introduces ±4% uncertainty in electricity NG fraction.
3. **Refinery non-NG fuels:** Only NG captured in Table 5.11. Real refinery fuel mix includes refinery gas, coke, etc.
4. **Industrial wastewater (4D2):** Reported as "NA" — not quantified.
5. **2A1 Cement:** Reported as "NE" — no cement production in state (confirmed).
