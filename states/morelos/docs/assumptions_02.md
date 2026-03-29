# Assumptions Log — 02_estimate.py (Morelos)

## Instrument Scope Assumptions

### S — Morelos State Carbon Tax

| Decision | Assumption | Basis | Confidence |
|----------|-----------|-------|-----------|
| All fixed sources in scope | YES | "stationary sources" language covers all registered industrial facilities | High |
| Commercial combustion (area source) in scope | YES | Small commercial boilers/heaters are stationary | Medium — depends on size threshold |
| Domestic combustion in scope | Partially: LPG/fossil fraction only | Wood combustion CO₂ is biogenic; not priced | High |
| Agricultural burning exempt | YES | "small-scale agricultural activities" exemption | High |
| Livestock exempt | YES | Not a stationary source | High |
| Mobile sources exempt | YES | Explicit exemption | High |
| Wastewater exempt | YES | Area-source category; not stationary industrial | Medium |
| HFCs/PFCs/SF₆ in scope | YES — but ABSENT from 2014 inventory | Scope explicitly includes HFCs/PFCs/SF₆; data gap flagged | Gap only |

**HFC/PFC/SF₆ data gap quantification:**
- INECC national HFC emissions (2022): ~25 MtCO₂e nationally
- Morelos GDP share: ~1.5%; industrial sector share ~0.8%
- Estimated Morelos HFCs (rough): 0.008 × 25,000 GgCO₂e = ~200 GgCO₂e
- This would add ~3-4% to S coverage — material but not dominant
- Flag for publication: "S coverage is understated by an estimated 3-4% due to absent HFC data"

### F — Federal IEPS Carbon Tax

**Fuel fractions (fixed stationary sources):**

| Fuel | Taxable under IEPS | CO₂ Mg (est.) | CO₂ share |
|------|-------------------|---------------|-----------|
| Petcoke | YES | 432 | 60.4% |
| Fuel oil | YES | 122 | 17.1% |
| LPG | YES | 74 | 10.4% |
| Diesel | YES | 50 | 7.1% |
| Formulated fuels | YES | 12 | 1.7% |
| Natural gas | NO (statutory) | 24 | 3.3% |
| **Taxable total** | | **690** | **96.7%** |
| **NG exempt** | | **24** | **3.3%** |

Key insight: NG is only 3.3% of fixed-source combustion CO₂ in Morelos. The NG exemption has negligible impact on F coverage — in direct contrast to Durango (NG=99.6%) and Colima (NG=82%).

**Cement F fraction derivation:**
- Total cement CO₂: 901,618 Mg
- Process fraction (calcination): 60% = 540,971 Mg → NOT taxable by IEPS
- Combustion fraction: 40% = 360,647 Mg → taxable (petcoke/FO dominant)
- NG share of combustion: ~1% (cement kilns use petcoke/coal, not NG)
- F fraction of total cement CO₂ = 40% × 99% = 39.6% ≈ 0.396
- Range: process_frac varies 55-65% → F frac range 34.6-44.6%

### E — Mexico Pilot ETS

| Category | ETS Central | Range | Rationale |
|----------|------------|-------|-----------|
| Cemento y cal (3 plants) | 97% | 90-100% | 3 large cement plants; Cemex/Cruz Azul operations; all >> 25kt threshold |
| Vidrio (2 plants) | 85% | 70-98% | Large glass production; 1 large facility likely above threshold |
| Celulosa y papel (2 plants) | 80% | 60-95% | Pulp/paper mills; at least 1 likely above threshold |
| Quimica (20 firms) | 65% | 45-85% | Mixed size; CIVAC concentration helps; 20 firms = varied sizes |
| Alimentos y bebidas (8 firms) | 70% | 50-90% | Sugar mills dominate; large mills likely above threshold |
| Derivados petroleo carbon (3 firms) | 60% | 40-80% | Medium uncertainty |
| Other manufacturing (smaller sectors) | 25% | 10-45% | Small firms; mostly below threshold |

### Biogenic CO₂ Treatment

Morelos has two biogenic CO₂ streams that require careful handling:

**Domestic wood combustion CO₂ (~626,000 Mg, 10.9% of state):**
- The 2014 inventory includes this in area-source CO₂ totals
- For carbon pricing: biogenic CO₂ is not subject to state or federal carbon tax
- In our scope mapping: `Combustion_doméstica` is in S scope (stationary), but f_frac only covers the LPG/fossil fraction (~30%)
- Practical effect: large block of "state total" that is technically in S legal scope but economically unpriced by any instrument

**Bagasse combustion in sugar mills (Alimentos y bebidas):**
- Bagasse CO₂ is biogenic; the inventory methodology already excludes it from CO₂ totals
- The reported 292,319 Mg CO₂ for Alimentos y bebidas is therefore FOSSIL-derived only
- No adjustment needed — correctly handled in inventory

## Growth Rate Assumptions (2014→2025/2026)

11-year extrapolation: rates are calibrated to national INECC trends with Morelos adjustments.
Uncertainty ranges are ±60% of central for an 11-year horizon.

| Sector | Central | Range | Rationale |
|--------|---------|-------|-----------|
| Cement | +0.5%/yr | -2% to +2.5% | National production flat-to-growing; efficiency improvements |
| Glass | +0.8%/yr | -1.5% to +3.0% | Slow growth; construction linkage |
| Chemical | +1.0%/yr | -2% to +3.5% | CIVAC industrial zone; moderate growth |
| Food/bev | +1.0%/yr | -1.5% to +3.5% | Sugar mills linked to harvest variability |
| Mobile (road) | +1.5%/yr | -0.5% to +3.0% | National fleet growth; Morelos urbanisation |
| Domestic combustion | -1.0%/yr | -3% to +1.0% | LPG substitution for wood; urbanisation |
| Livestock | +0.5%/yr | -1.5% to +2.5% | Stable agriculture base |

**Note on wide ranges:** With an 11-year horizon, actual 2025 emissions could vary 35-50% from central in either direction for individual sectors. These estimates should be treated as indicative of the order of magnitude, not precise projections.
