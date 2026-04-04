# Assumptions Log — 02_estimate.py (Queretaro)

## Instrument Scope Assumptions

### S — Queretaro State Carbon Tax

| Decision | Assumption | Basis | Confidence |
|----------|-----------|-------|-----------|
| NG in scope | YES (unlike federal tax) | State tax design; no NG exemption clause | High — confirmed in policy references |
| ALL Kyoto gases | YES (CO2, CH4, N2O, HFCs, PFCs, SF6) | Explicit in tax scope | High |
| Economy-wide fixed sources | YES — "productive processes" | Tax applies to all stationary economic activity | High |
| [1A1] electricity in scope | YES | Stationary source, productive process | High |
| [1A2] manufacturing in scope | YES | Stationary source, productive process | High |
| [1A4a] commercial in scope | YES | Fixed-source commercial combustion | High |
| [1A4c] ag combustion in scope | YES | Productive process (mechanized ag, greenhouses) | Medium-High |
| ALL IPPU in scope (2A-2F) | YES | Process emissions from productive activities; HFCs from equipment leaks | High |
| [1A3] transport exempt | YES | Mobile sources explicitly excluded | High |
| [1Ab] residential exempt | YES | Not a productive process | High |
| AFOLU exempt | YES | Agricultural/land-use emissions excluded | High |
| Waste exempt | YES | Waste management excluded | High |

### F — Federal IEPS Carbon Tax

| Parameter | Value (central) | Range | Basis |
|-----------|----------------|-------|-------|
| [1A1] taxable fraction (diesel) | 0.0002% | 0-0.001% | Table 10: diesel=3.80E-05 PJ vs NG=32.80 PJ; virtually zero |
| [1A2] NG fraction of fossil CO2 | 95.51% | 93-97% | Table 11 fuel PJ x INECC EFs; taxable ~4.5% |
| [1A4a] NG fraction | 20% | 10-30% | Commercial: LPG dominant; NG pipeline in ZMQ metro area |
| [1Ab] NG fraction | 5% | 2-10% | Residential: LPG dominant; some urban NG pipeline |
| [1A4c] NG fraction | 2% | 0-5% | Agricultural: diesel+LPG for mechanized ag; negligible NG |
| [1A3] NG fraction | 1.4% | 1-2% | Table 12: NG=0.596 PJ of 31.11 PJ total transport |
| [2] IPPU | 0% | 0% | Process emissions; not covered by fuel sales tax |

**[1A2] NG fraction derivation (critical assumption):**
- Table 11 fuel consumption (PJ): NG=36.11, LPG=0.67, diesel=0.32, combustoleo=0.10, coque=0.24, gasolinas=0.02
- Total fossil fuel = 37.46 PJ (excluding purchased electricity 13.88 PJ)
- NG = 96.4% of fossil energy
- After correcting for INECC emission factors (NG EF=57,755 vs weighted non-NG EF~74,000 kgCO2/TJ):
  NG CO2 = 2,085.1 GgCO2; non-NG CO2 = 97.6 GgCO2 → NG share = 95.51%
- **Impact:** F covers only ~4.5% of [1A2] CO2, making federal tax nearly irrelevant for Queretaro manufacturing
- **Sensitivity:** ±2% change in NG fraction → ±44 GgCO2e change in F coverage from [1A2]

**[1A1] NG fraction derivation:**
- Table 10: NG=32.80 PJ across all 3 plants; diesel=3.80E-05 PJ (San Juan del Rio only)
- NG CO2 = 32.80 x 1000 x 57,755 / 1E9 = 1,894.4 GgCO2
- Diesel CO2 = 3.80E-05 x 1000 x 72,851 / 1E9 = 0.003 GgCO2
- NG fraction = 99.9998% → federal tax covers effectively 0% of electricity CO2
- This is the extreme case: Queretaro electricity is virtually 100% NG

### E — Mexico Pilot ETS

| Subsector | ETS Fraction (central) | Range | Basis |
|-----------|----------------------|-------|-------|
| [1A1] electricity | 98.9% | 98.5-99.5% | 3 plants: El Sauz (1,638 GgCO2e) + SJR (236 GgCO2e) >> threshold; Queretaro (20.2 GgCO2e) < 25kt |
| [1A2] manufacturing | 75% | 60-88% | Strong automotive/aerospace cluster; large concentrated plants (glass, automotive parts) |
| [2A2] lime production | 60% | 40-80% | 2 establishments ~24 GgCO2e each; near 25kt threshold — high uncertainty |
| [2A3] glass production | 95% | 85-100% | 2 companies ~57 GgCO2e each >> threshold |
| [2C1] iron/steel | 0% | 0% | 0.28 GgCO2e = 280 tCO2e << 25,000 threshold |
| [2F] HFCs | 0% | 0% | Refrigerant leaks; not in Mexico Pilot ETS scope |
| [1A4a] commercial | 0% | 0% | Small distributed establishments |
| [1A4c] agriculture | 0% | 0% | Small distributed sources |
| Transport, AFOLU, waste | 0% | 0% | Not in ETS sectoral scope |

**[1A1] ETS derivation (plant-level analysis):**
- El Sauz (Pedro Escobedo): 3,500,140 MWh, NG=28.36 PJ → 1,638.8 GgCO2e (**above threshold**)
- Planta Queretaro: 24,486 MWh, NG=0.35 PJ → 20.2 GgCO2e = 20,200 tCO2e (**below** 25,000 threshold)
- San Juan del Rio: 400,573 MWh, NG=4.09 PJ → 236.3 GgCO2e (**above threshold**)
- ETS-covered = (1,638.8 + 236.3) / 1,895.3 = 98.9%
- The small Queretaro plant exclusion is unique to Queretaro among states analysed — most states have all plants above threshold

**[2A2] lime production — near-threshold uncertainty:**
- 2 establishments: Cadereyta de Montes and Toliman
- Total = 48.74 GgCO2e → average ~24.4 GgCO2e each
- At 24.4 GgCO2e, both plants are very close to the 25,000 tCO2e threshold
- Central estimate 60% reflects uncertainty: one may be above, one below
- Range 40-80% captures scenarios from both-below to both-above

## Growth Rate Assumptions (2021→2025/2026)

| Sector | Central rate | Low | High | Rationale |
|--------|-------------|-----|------|-----------|
| Electricity [1A1] | -0.5%/yr | -2.5% | +1.0% | Queretaro grid relatively stable; slight efficiency gains |
| Manufacturing [1A2] | +3.0%/yr | -0.5% | +5.5% | Strong auto/aerospace cluster (BMW, Safran); GDP growth above national average |
| Transport [1A3] | +1.5%/yr | -0.5% | +3.0% | Population growth ~2%/yr; vehicle fleet expansion; ZMQ metro growth |
| Commercial [1A4a] | +1.0%/yr | -1.0% | +2.0% | Services sector growth in Queretaro metro |
| Residential [1Ab] | +1.0%/yr | -0.5% | +2.0% | Population growth |
| Ag combustion [1A4c] | +0.5%/yr | -1.0% | +1.5% | Slow growth; mechanization relatively mature |
| IPPU minerals [2A] | +1.0%/yr | -1.0% | +2.5% | Glass and lime demand tied to construction |
| IPPU metals [2C] | +0.5%/yr | -1.0% | +2.0% | Small sector; near-zero base |
| HFCs [2F] | +2.0%/yr | +0.5% | +3.5% | HFC use growing nationally; cooling demand increasing |
| AFOLU [3] | +0.5%/yr | -1.0% | +1.5% | Livestock herd slow growth; land use relatively stable |
| Waste [4] | +2.0%/yr | +0.5% | +3.5% | Population growth + urbanization; per-capita waste generation rising |

**Manufacturing growth justification:**
Queretaro hosts a strong automotive/aerospace cluster (BMW, Safran, Bombardier, Kellogg's) driving
above-average industrial growth. Historical TMCA for manufacturing has been strong. Central
estimate of +3%/yr is conservative relative to recent investment announcements but accounts
for potential cyclical slowdown.

**Uncertainty ranges:** Asymmetric ranges reflect structural differences — manufacturing has
upside from new investment; electricity has downside from efficiency improvements.

## Venn Decomposition Independence Assumption

The NG-exempt fraction (F scope) and ETS threshold fraction (E scope) are treated as **independent**
within each category. This means:

- S_F_E  = emissions x f_frac x e_frac
- S_E    = emissions x (1-f_frac) x e_frac        [NG-derived emissions at large plants]
- S_F    = emissions x f_frac x (1-e_frac)         [taxable fuels at small facilities]
- S_only = emissions x (1-f_frac) x (1-e_frac)    [NG at small facilities; HFCs; process CO2]

**Justification:** There is no strong a priori reason to expect large plants to use more or less
NG than small plants in the same subsector. Queretaro's manufacturing sector is heavily NG-dominated
across all plant sizes (96.4% of fossil energy). This makes the independence assumption more
defensible than in states with heterogeneous fuel mixes.

**For [1A1]:** Near-trivially satisfied since NG=99.9998%: the S_F_E segment is negligible
regardless of E fraction. The economically meaningful segment is S_E_only (NG at large plants).

**For [2A2/2A3]:** Independence is vacuous since f_frac=0 (process emissions). The only
dimension is ETS threshold, which is determined by plant size alone.
