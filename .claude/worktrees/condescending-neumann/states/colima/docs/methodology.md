# Methodology Note: Colima Carbon Pricing Coverage Overlap Analysis

**Case:** Mexico State Carbon Pricing — Colima  
**Publication:** World Bank *State & Trends of Carbon Pricing*  
**Series:** Mexico Carbon Pricing Overlap Series (State-Level)  
**Estimation tier:** Tier 3 (stationary combustion) / Tier 4 (transport, state total)  
**Base year:** 2015 | **Target years:** 2025, 2026  
**GWPs:** AR5 (CH₄ = 28, N₂O = 265)  
**Prepared by:** World Bank Climate Change Group  
**Last updated:** March 2026

---

## 1. Scope and Objective

This note documents the methodology and key assumptions used to estimate the **deduplicated emissions coverage** of three carbon pricing instruments that simultaneously apply to greenhouse gas emissions in Colima, Mexico:

| Symbol | Instrument | Administering authority |
|--------|-----------|------------------------|
| **S** | Colima state carbon tax | Colima state government |
| **F** | Mexico federal carbon tax (IEPS) | SAT / federal government (upstream levy) |
| **E** | Mexico Pilot ETS | SEMARNAT (non-binding pilot phase) |

The central analytical problem is **double- and triple-counting**: naively summing the reported coverage of each instrument overstates the total emissions priced, because the same tonne of CO₂e may fall under multiple instruments simultaneously. The objective is to decompose total coverage into mutually exclusive segments and compute the **deduplicated union** S ∪ F ∪ E.

Coverage definition used throughout: **operational coverage** — emissions from sources actively regulated (reporting, receiving allocations, or paying the levy). Where legal and operational coverage diverge materially (as in the Pilot ETS), this is flagged explicitly.

---

## 2. Instruments: Legal Scope and Design

### 2.1 Colima State Carbon Tax (S)

- **Implementation:** 2025 (newly enacted; first year of operation)
- **Design basis:** Modelled on the Jalisco and Zacatecas state carbon tax structures — a levy on fossil fuel combustion at **stationary sources** within Colima state
- **Exempt fuels:** Natural gas (explicitly excluded, mirroring the federal IEPS carve-out)
- **Excluded sources:** Mobile sources (road, rail, air, water transport) — these are covered by the federal IEPS transport fuel duties, not the state carbon tax
- **In-scope sources:** Electricity generation (diesel and fuel oil fraction only), manufacturing industries (cement, food/beverage, metallurgical, non-metallic minerals, chemical, other), residential LP gas combustion, commercial sector, agriculture and forestry

> **Caveat:** Full regulatory text for the Colima state carbon tax was not publicly available at the time of this analysis. Design details (threshold for stationary sources, exact qualifying fuel list) are assumed to follow the Jalisco/Zacatecas model. If the final enacted regulation differs, estimates should be revised.

### 2.2 Mexico Federal Carbon Tax (F)

- **Legal basis:** Ley del Impuesto Especial sobre Producción y Servicios (IEPS), Artículo 2o-C; in force since January 2020
- **Design:** Upstream levy applied at the point of first sale or import of fossil fuels by importers and distributors. No facility-level threshold.
- **Exempt fuels:** Natural gas (explicit statutory carve-out)
- **Coverage in Colima:** All fuels subject to the state carbon tax, **plus** road transport fuels (gasoline, diesel), water navigation, rail, and civil aviation fuels
- **Overlap with S:** By construction, **100% overlap on all in-scope fuels**. The upstream design means every fossil fuel combusted at a Colima stationary source — and therefore within the state tax's reach — has already been taxed by the federal government at the point of supply. The state tax adds a second price signal on the same emissions base; it does not extend coverage to sources the federal instrument misses.

### 2.3 Mexico Pilot ETS (E)

- **Legal basis:** ACUERDO por el que se establecen las bases para el Sistema de Comercio de Emisiones (SCE), SEMARNAT; mandatory reporting began 2020, pilot trading 2022–2024
- **Threshold:** Facilities emitting ≥ 25,000 tCO₂e/yr in the energy and industrial sectors
- **Binding status:** **Non-binding pilot** — no financial penalty for non-compliance during the pilot phase. Legal and operational coverage diverge materially.
- **Colima participants (identified):**
  - Manzanillo thermoelectric plant (CFE) — full facility (≫ threshold); NG fraction not taxed by either carbon tax
  - Peña Colorada iron pellet plant (Manzanillo) — large stationary emitter
  - Las Encinas iron pellet plant (Cuauhtémoc) — large stationary emitter
  - Cementos Apasco, Tecomán — combustion emissions (process emissions also in ETS but not in carbon taxes)
- **Important:** All ETS results in this analysis represent **legal scope**. Operational coverage (actual participation, verified emissions, allowance surrenders) is likely lower and cannot be quantified from available public data.

---

## 3. Data Foundation

### 3.1 Primary Emissions Inventory

All base-year emissions figures are drawn from a single authoritative source:

| Attribute | Value |
|-----------|-------|
| Document | *Greenhouse Gas Inventory of the State of Colima, Base Year 2015* |
| Producer | IMADES — Instituto para el Medio Ambiente y Desarrollo Sustentable del Estado de Colima |
| Funding | Under2 Coalition Future Fund (Québec, Scotland, Wales); grant UC/FF/2018/002 |
| Published | 2019-01-31 |
| GWPs | AR5: CH₄ = 28, N₂O = 265, SF₆ = 23,500, black carbon = 900 |
| Methodology | IPCC 2006 Guidelines; Tier 2 stationary combustion; Tier 3 road transport (MOVES-Mexico model) |
| Uncertainty | ±8.9% overall (inventory's own estimate) |
| Local file | `data/raw/Colima_future_fund_report_2018_pdf.pdf` |

**Rationale for 2015 base year:** The 2015 IMADES inventory is the most recent publicly available state-level GHG inventory for Colima. A superseded 2005 inventory used SAR GWPs and would have required a 20-year extrapolation gap. The 2015 base reduces the extrapolation gap to 10–11 years (to 2025/2026), which is manageable within the Tier 3 approach.

**GWP harmonisation:** No conversion required. The 2015 inventory uses AR5 GWPs, consistent with INECC's INEGYCEI 2022 national inventory. AR5 values are used throughout.

### 3.2 2015 Inventory — Key Figures

**Sector totals (net):**

| Sector | GgCO₂e | Share |
|--------|---------|-------|
| Energy | 15,070 | 83.1% |
| AFOLU | 1,879 | 10.4% |
| IPPU | 724 | 4.0% |
| Waste | 464 | 2.6% |
| **Total** | **18,137** | **100%** |

**Energy sector breakdown:**

| Subsector | GgCO₂e | Share of energy |
|-----------|---------|----------------|
| Electricity generation | 7,128 | 47.3% |
| Road transportation | 5,578 | 37.0% |
| Manufacturing & construction | 1,950 | 12.9% |
| Residential | 189 | 1.3% |
| Water navigation | 95 | 0.6% |
| Other (rail, aviation, commercial, agri, biogas) | 130 | 0.9% |

**Manzanillo thermoelectric plant (CFE — "Termoeléctrica Gral. Manuel Álvarez Moreno"):**

| Item | Value |
|------|-------|
| Location | Manzanillo municipality |
| Generation (2015) | 13,984 GWh |
| Natural gas input | 98,435 TJ (82% of plant CO₂ by mass) |
| Diesel input | 16,951 TJ (18% of plant CO₂ by mass) |
| Fuel oil input | 28 TJ (trace) |
| Total plant CO₂e | ~7,128 GgCO₂e |
| Taxable fraction (diesel+FO) | ~1,276 GgCO₂e (~18%) |
| Exempt fraction (NG) | ~5,852 GgCO₂e (~82%) |

The NG exemption at this single facility is the **dominant driver** of the gap between Colima's gross emissions and its taxable coverage.

### 3.3 Supporting Data Sources

| Source | Used for |
|--------|---------|
| INECC INEGYCEI 2022 national inventory (Table 1A1, 1A2) | Sector growth rate calibration |
| SENER Prospectiva de Petróleo, Gas y Petroquímica 2022 | Electricity sector diesel/NG trend |
| CANACEM annual cement production statistics 2015–2022 | Cement sector growth rate |
| SE / Dirección General de Minas, production statistics | Iron ore / pellet sector growth rate |
| SENER Balance Nacional de Energía 2022 | LP gas residential demand trend |
| CONAPO Proyecciones de Población 2018–2030 | Colima population growth (residential proxy) |
| INECC INEGYCEI 2022, 1A2e, 1A2f | Food/beverage and non-metallic minerals growth |

---

## 4. Estimation Tier Rationale

The tiered framework used across the Mexico overlap cases is:

| Tier | Condition | Method |
|------|-----------|--------|
| 1 | Facility registry data for both instruments | Direct matching (EUTL / national registries) |
| 2 | One instrument has registry data | Apply coverage ratio to bound overlap |
| 3 | Neither instrument has facility data | Sector-level estimation using growth rates + threshold rules |
| 4 | Minimal data | Legal scope intersection + energy balance bounds; reported as range |

**Colima uses Tier 3/4** because:
- No publicly disaggregated SEMARNAT MRV data at state level for individual facilities
- No Mexican equivalent of the EUTL for cross-instrument facility matching
- The Pilot ETS participant list is not fully public for state-level subsetting
- Colima state tax regulatory text was not fully published at analysis date

Tier 1 or 2 estimation is not feasible under current data availability. Results are reported as ranges with explicit uncertainty bounds.

---

## 5. Methodology

### Step 1 — Map Legal Scope (`01_clean.py`)

The 2015 IMADES inventory is transcribed from the PDF source into structured form and augmented with three scope flags per subsector:

- `in_state_tax_scope` — within the Colima state carbon tax's legal reach
- `overlap_federal_tax` — also reached by the federal IEPS carbon tax
- `overlap_ets_pilot` — within the Pilot ETS ≥25,000 tCO₂e/yr threshold

The electricity sector is treated specially. The Manzanillo plant's fuel mix is split at source into:
- **NG fraction** (~82% of plant CO₂e): exempt from both federal and state carbon taxes; in ETS legal scope
- **Diesel + fuel oil fraction** (~18% of plant CO₂e): subject to both carbon taxes and ETS

This split uses the fuel consumption data reported in the IMADES inventory (Table 4.2) and standard IPCC 2006 emission factors. The 82/18 split is computed from mass of CO₂ per fuel type, not from energy content.

**Scope decisions:**

| Subsector | In S scope | In F scope | In E scope | Rationale |
|-----------|-----------|-----------|-----------|-----------|
| Electricity (diesel+FO) | ✓ | ✓ | ✓ | Taxed fuels; above ETS threshold |
| Electricity (NG) | ✗ | ✗ | ✓ | NG exempt from both taxes; ETS covers full facility |
| Manufacturing — cement, metallurgical | ✓ | ✓ | ✓ | Large facilities above ETS threshold |
| Manufacturing — other | ✓ | ✓ | ✗ | Smaller facilities; below ETS threshold |
| Residential / commercial / agri | ✓ | ✓ | ✗ | Dispersed sources; below ETS threshold |
| Road / water / rail / aviation | ✗ | ✓ | ✗ | Mobile sources; outside state tax scope |
| IPPU process emissions | ✗ | ✗ | ✓ | Process CO₂ (cement calcination); not a combustion tax |
| AFOLU / waste | ✗ | ✗ | ✗ | Outside all three instruments |

### Step 2 — Extrapolate to 2025/2026 (`02_estimate.py`)

Compound annual growth rates (CAGRs) are derived from INECC INEGYCEI national sector trends (2015–2022) and applied to each subsector's 2015 base value:

$$E_{subsector,year} = E_{subsector,2015} \times (1 + g)^{year - 2015}$$

**Sector growth rates applied:**

| Sector class | CAGR central | CAGR low | CAGR high | Primary source |
|---|---|---|---|---|
| Electricity — diesel fraction | −2.0%/yr | −8.0% | +1.0% | SENER prospectiva; CFE dispatch data showing progressive diesel phase-out |
| Electricity — NG fraction | +0.2%/yr | −3.0% | +3.0% | SENER BEN 2022 |
| Manufacturing — cement | +1.2%/yr | −2.0% | +3.0% | CANACEM production 2015–2022 |
| Manufacturing — food/beverage | +1.5%/yr | −1.0% | +3.5% | INECC 1A2e national trend |
| Manufacturing — metallurgical | +0.8%/yr | −5.0% | +3.0% | SE/Minería iron ore export data |
| Manufacturing — non-metallic minerals | +1.3%/yr | −2.0% | +3.5% | INECC 1A2f national trend |
| Manufacturing — other/chemical | +1.0%/yr | −2.0% | +3.0% | General industrial proxy |
| Residential / commercial / agriculture | +0.8%/yr | −1.0% | +2.0% | SENER LP gas; CONAPO population growth |
| Transport (F-only) | +1.0%/yr | −2.0% | +3.0% | General transport fuel proxy |

Each subsector produces a **(low, central, high)** triple. Low and high bounds represent the range of plausible CAGR assumptions; they do not constitute formal confidence intervals.

**Dominant source of uncertainty:** The structural uncertainty from unknown Colima state tax design details (threshold, exact fuel list) exceeds the CAGR uncertainty for all sectors combined. This is the main reason results are presented as ranges rather than point estimates.

### Step 3 — Venn Decomposition (`02_estimate.py`, `03_outputs.py`)

The full seven-segment Venn decomposition is computed using the coverage flags and extrapolated values:

| Segment | Definition | Colima content |
|---------|-----------|----------------|
| **S∩F∩E** | All three instruments | Electricity (diesel+FO), cement combustion, metallurgical |
| **S∩F only** | State + federal, not ETS | Remaining manufacturing, residential, commercial, agri |
| **S only** | State tax only | Biogas/energy generation plants (non-fossil fuel) |
| **F only** | Federal only, not state or ETS | Road, water, rail, civil aviation transport |
| **E only** | ETS only, not either carbon tax | NG fraction of Manzanillo plant |
| **S∩E only** | State + ETS, not federal | Empty — all ETS sources in state scope are also in federal scope |
| **F∩E only** | Federal + ETS, not state | Empty — federal IEPS does not cover NG; NG is therefore E-only |

Deduplicated union by inclusion–exclusion:

$$S \cup F \cup E = (S \cap F \cap E) + (S \cap F_{only}) + S_{only} + F_{only} + E_{only}$$

The S∩E and F∩E terms are both zero by the logic described above, simplifying the calculation.

### Step 4 — Publication Outputs (`03_outputs.py`)

Two figures and one full table are produced:

- **Figure 1** (`colima_venn_segments_2025_2026.png`): Stacked bar chart showing the seven Venn segments as shares of total state emissions for 2025 and 2026, with uncertainty error bars on the total covered stack.
- **Figure 2** (`colima_coverage_summary_2025_2026.png`): Grouped bar chart comparing gross instrument totals and the deduplicated union against total state emissions for both years.
- **Table** (`colima_overlap_full_table.csv`): Full breakdown with central, low, and high estimates and coverage shares for all segments and derived metrics.

---

## 6. Results

Central estimates (2025; 2026 is within ±0.5% on all metrics):

| Metric | GgCO₂e | % of state | Range |
|--------|---------|------------|-------|
| **Colima state tax — gross coverage (S)** | 3,533 | 19.5% | 2,354–4,434 |
| **Federal carbon tax — Colima coverage (F)** | 9,854 | 54.3% | 7,029–12,125 |
| **Pilot ETS — legal coverage (E)** | 7,635 | 42.1% | 5,267–10,031 |
| S∩F∩E — covered by all three | 1,665 | 9.2% | 951–2,166 |
| S∩F only — state + federal, not ETS | 1,859 | 10.2% | 1,395–2,255 |
| **S only — state tax unique coverage** | **~10** | **0.05%** | 7–12 |
| F only — transport fuels | 6,331 | 34.9% | 4,683–7,703 |
| E only — NG electricity (not taxed) | 5,970 | 32.9% | 4,315–7,865 |
| **Deduplicated union S∪F∪E** | **15,834** | **87.3%** | 11,352–20,001 |
| Total state emissions | 18,137 | 100% | 16,403–21,049 |

---

## 7. Key Analytical Conclusions

### 7.1 The Colima state carbon tax adds virtually no unique emissions coverage

The net S-only segment — emissions under the Colima state tax not covered by either the federal carbon tax or the Pilot ETS — is approximately **10 GgCO₂e (~0.05% of state emissions)**. This consists entirely of biogas combustion at small energy generation plants, which burn non-fossil fuel and are therefore already exempt from the federal IEPS levy.

This result is structural. The federal carbon tax is an upstream levy, meaning every fossil fuel that reaches a Colima stationary source has already been taxed federally at the point of first supply. The state carbon tax's function is to apply an **additional price signal** on the same emissions base — stacking on top of the federal instrument — rather than extending coverage to previously unpriced sources.

For the purposes of the State & Trends methodology note, this means Colima state tax coverage should be reported alongside — not added to — federal carbon tax coverage, to avoid double-counting.

### 7.2 The natural gas exemption is the dominant structural factor

Of Colima's 18,137 GgCO₂e total, the Manzanillo thermoelectric plant accounts for 7,128 GgCO₂e (39% of the state total). Approximately 82% of the plant's CO₂e comes from natural gas combustion, which is explicitly exempt from both the federal and state carbon taxes under Mexico's IEPS framework. This single fuel-mix characteristic reduces the electricity sector's in-scope emissions from 7,128 GgCO₂e to approximately 1,276 GgCO₂e — an 82% reduction from the gross figure.

Without the NG exemption, the Colima state tax would cover an estimated 9,500+ GgCO₂e (~52% of state emissions). The exemption reduces this to 19.5%. This carve-out is the most important assumption in the entire analysis and should be verified directly against any revised state tax legislation.

### 7.3 The deduplicated union covers approximately 87% of state emissions

The three instruments together, with full deduplication, cover approximately 15,834 GgCO₂e (87.3% of state emissions). The remaining ~13% is outside all three instruments: AFOLU emissions, waste sector, IPPU process emissions (cement calcination, HFCs), and residential biomass combustion.

### 7.4 The Pilot ETS adds substantive but non-binding coverage

The ETS legal scope covers approximately 42% of state emissions, primarily through the large Manzanillo plant (NG fraction) and major industrial facilities. Because the pilot phase carries no financial penalty, operational coverage is likely materially lower. ETS figures in this analysis are **upper bounds** on actual operational coverage.

### 7.5 2025 and 2026 estimates are near-identical

The two target years differ by less than 0.5% on all key metrics. The declining diesel trend at Manzanillo (−2%/yr central) is approximately offset by manufacturing sector growth (+1–1.5%/yr). For publication purposes, a single 2025–2026 estimate with the full uncertainty range is appropriate.

---

## 8. Caveats and Open Questions

1. **State tax design details unconfirmed.** Full regulatory text not available at analysis date. The Jalisco/Zacatecas model is assumed. Any deviation in the final enacted regulation — particularly on threshold for stationary sources or qualifying fuel list — should trigger a revision.

2. **Manzanillo plant ETS participation unconfirmed.** Whether the plant appears on the SEMARNAT Pilot ETS participant list should be verified against the official registry. Analysis assumes inclusion based on the ≥25,000 tCO₂e/yr threshold.

3. **No post-2015 Colima inventory.** If IMADES or INECC publishes a more recent state inventory, the extrapolation approach should be replaced with a direct updated base year.

4. **Cement combustion/process split assumed.** The 67%/33% combustion/process split for Cementos Apasco is estimated from the clinker fraction and IPCC 2006 emission factors. Process CO₂ (calcination) is in the ETS legal scope but not in either carbon tax scope. Verify against SEMARNAT MRV data if available.

5. **Pilot ETS non-binding caveat.** All ETS overlap figures represent legal scope. Operational coverage during the pilot phase is unquantified and likely lower. Results should be presented with explicit flags in any publication table.

---

## 9. Relationship to Other Mexico Cases

This Colima analysis is part of the broader Mexico carbon pricing overlap series within the `mexico-cpi-overlap` repository. The federal pipeline (federal carbon tax × Mexico Pilot ETS) has been completed separately at the national level. The state-level analyses (Colima, and ten additional states) estimate how state carbon taxes interact with the two federal instruments within each state's emissions boundary.

Key cross-case note: **the federal carbon tax overlap methodology is consistent across all state cases** — the upstream design guarantees 100% overlap with any state-level stationary combustion tax that respects the NG exemption. What varies across states is the size of the in-scope stationary combustion base, the industrial composition, and whether large ETS-threshold facilities are present.

---

*End of methodology note. For data sources and access dates, see `docs/data_sources.md`. For script-level assumptions, see `docs/assumptions_02.md`.*
