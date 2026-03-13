# Assumptions Log — 02_estimate.py (Durango)

## Instrument Scope Assumptions

### S — Durango State Carbon Tax

| Decision | Assumption | Basis | Confidence |
|----------|-----------|-------|-----------|
| NG in scope | YES (unlike federal tax and Colima) | State tax design; no NG exemption clause | High — confirmed in policy references |
| [1B2] fugitive in scope | YES (stationary source of GHGs) | Policy scope is stationary GHG sources | Medium — fugitive = stationary infrastructure |
| [2F] HFCs in scope | YES | Tax explicitly covers HFCs, SF₆, PFCs | High |
| [2C] metal processes in scope | YES | Process emissions from stationary plants | High |
| [1A4c] agriculture exempt | YES | Tax exempts "agricultural emissions" | High |
| Transport exempt | YES | Explicit exemption in tax design | High |
| Waste exempt | YES | Explicit exemption in tax design | High |

### F — Federal IEPS Carbon Tax

| Parameter | Value (central) | Range | Basis |
|-----------|----------------|-------|-------|
| [1A1] taxable fraction (diesel+FO) | 0.38% | 0.3–0.5% | Table 12 fuel PJ × Table 13 EFs; NG=99.62% of CO₂ |
| [1A2] NG fraction of fossil CO₂ | 71% | 65–77% | Fig 13: NG=61% energy; corrected for biogenic exclusion and relative EFs |
| [1A4a/b] taxable fraction | 85% | 75–90% | Inventory text: LPG ~67% of GHG; diesel ~18%; NG ~15% exempt |
| [1B2] federal tax fraction | 0% | 0% | Fugitive CH₄ from NG infra; upstream fuel tax does not apply |
| [2C] federal tax fraction | 0% | 0% | Process emissions; not covered by fuel sales tax |
| [2F] federal tax fraction | 0% | 0% | HFCs not fossil fuel |

**[1A2] NG fraction derivation (key assumption):**
- Energy mix from Figure 13: NG=61%, wood=13%, other fossil=26%
- Biogenic CO₂ (wood) excluded from inventory → fossil-only denominator
- Correcting for emission factors: NG EF=57,755 kg/TJ; non-NG fossil EF≈74,000 kg/TJ
- NG CO₂ share = (0.61×57,755) / (0.61×57,755 + 0.26×74,000) = 62.3%
- Adjusted upward to 71% central (long-run substitution trend; gas growing at 11.4% TMCA in [1A2])
- This assumption has the largest sensitivity in the F coverage calculation for stationary sources
- **Sensitivity:** ±6% change in NG fraction → ±53 GgCO₂e change in F coverage from [1A2]

### E — Mexico Pilot ETS

| Subsector | ETS Fraction (central) | Range | Basis |
|-----------|----------------------|-------|-------|
| [1A1] electricity | 100% | 100% | All 5 named plants >> 25,000 tCO₂e/yr; smallest (84 MW turbogás) ≈ 85,000 tCO₂e/yr |
| [1A2d] pulp/paper | 90% | 75–97% | Key category; large mills identified in COA; 1–3 facilities |
| [1A2e] food/beverage | 70% | 50–85% | Large food processors; Durango has significant dairy/meat industry |
| [1A2j] wood products | 40% | 20–60% | Lumber industry; distributed small sawmills; some large industrial mills |
| [1A2i] mining | 80% | 60–95% | Large mines (gold, silver); Peñoles, Grupo México operations |
| [1A2f] non-metallic minerals | 70% | 50–90% | Some cement/lime plants |
| [1A2a] iron/steel | 80% | 60–95% | Concentrated in few facilities |
| [1A2b] non-ferrous metals | 70% | 50–90% | Some smelters |
| [1A2c] chemicals | 60% | 40–80% | Mixed size distribution |
| [1A2g,h,k,l,m] smaller | 20–40% | 5–60% | Distributed small manufacturers |
| [1B2] fugitive O&G | 50% | 30–70% | Large gas distribution / compression may qualify |
| [2C] metal processes | 90% | 70–100% | [2C2] ferroalloys likely 1 large facility >> threshold |
| All other | 0% | 0% | Small distributed sources below threshold |

## Growth Rate Assumptions (2022→2025/2026)

| Sector | Central rate | Low | High | Rationale |
|--------|-------------|-----|------|-----------|
| Electricity [1A1] | -1.0%/yr | -3.0% | +0.5% | Historical TMCA -2.38%; new Lerdo CC plant 2024 may increase slightly then efficiency normalises |
| Manufacturing [1A2] | +2.5%/yr | -1.0% | +5.0% | Historical TMCA +4.4%; COVID recovery normalised; Durango manufacturing recovering |
| Transport [1A3] | +1.0%/yr | -1.0% | +2.5% | Historical TMCA +0.84%; fleet growth continues |
| Other sectors [1A4] | +0.5%/yr | -1.0% | +1.5% | Near-flat historically; slight population growth |
| Fugitive [1B2] | +0.5%/yr | -1.0% | +2.0% | Historical TMCA +0.56%; NG infrastructure modestly growing |
| PIUP metals [2C] | +0.8%/yr | -2.0% | +3.0% | Historical TMCA +0.74% |
| HFCs [2F] | +1.5%/yr | +0.5% | +3.0% | HFC use growing nationally; cooling demand increasing |

**Uncertainty ranges:** ±40% of central rate for most sectors, reflecting 3-year forecast horizon
and structural uncertainty around manufacturing recovery trajectory.

## Venn Decomposition Independence Assumption

The NG-exempt fraction (F scope) and ETS threshold fraction (E scope) are treated as **independent** 
within each category. This means:

- S∩F∩E = emissions × f_frac × e_frac
- S∩E only = emissions × (1-f_frac) × e_frac  (NG-derived emissions at large plants)
- S∩F only = emissions × f_frac × (1-e_frac)   (taxable fuels at small facilities)
- S only = emissions × (1-f_frac) × (1-e_frac)  (NG at small facilities)

**Justification:** There is no strong a priori reason to expect large plants to use more or less
NG than small plants in the same subsector. The 2022 fuel mix figures from Figure 13 are 
sector-wide averages. This is a simplifying assumption — ideally, facility-level data 
(COA/SEMARNAT registry) would allow direct matching.

**For [1A1]:** The independence assumption is trivially satisfied since E=100%:
all power plants are above threshold, so S∩F∩E = S∩F = 0.38% of [1A1].
