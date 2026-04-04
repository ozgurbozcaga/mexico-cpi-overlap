# Colima State Carbon Tax — Coverage Overlap Analysis

**Case:** Mexico State Carbon Pricing — Colima  
**Part of:** `mexico-cpi-overlap` repository  
**Publication:** World Bank *State & Trends of Carbon Pricing*  
**Status:** Complete (Tier 3/4 estimation)  
**Last updated:** March 2026

---

## 1. What This Analysis Does

This case estimates the **deduplicated emissions coverage** across three carbon pricing instruments that simultaneously apply to Colima, Mexico:

| Symbol | Instrument | Operator |
|--------|-----------|---------|
| **S** | Colima state carbon tax | Colima state government |
| **F** | Mexico federal carbon tax | SAT / federal (upstream) |
| **E** | Mexico Pilot ETS | SEMARNAT (non-binding pilot) |

The core question: how many tonnes of CO₂e does each instrument cover, and — accounting for the fact that the same emission source may be taxed by more than one instrument — what is the **total deduplicated coverage** across all three?

The analysis produces a full **seven-segment Venn decomposition** (S only, F only, E only, S∩F, S∩E, F∩E, S∩F∩E) plus the union S∪F∪E, with uncertainty bounds.

---

## 2. Instruments in Scope

### S — Colima State Carbon Tax
- **Implementation year:** 2025 (newly enacted)
- **Design:** Follows the Jalisco/Zacatecas model — levied on fossil fuel combustion at **stationary sources** within Colima state
- **Natural gas:** EXEMPT (mirrors federal IEPS structure)
- **Mobile sources:** Excluded (transport fuels covered by federal IEPS, not state tax)
- **Key in-scope sources:** Electricity generation (diesel/FO fraction only), manufacturing (cement, food, metallurgical, non-metallic minerals, other), residential LP gas, commercial, agriculture/forestry

### F — Mexico Federal Carbon Tax
- **Legal basis:** Ley del IEPS, Artículo 2o-C; in force since 2020
- **Design:** Upstream levy applied to fossil fuel importers and distributors
- **Natural gas:** EXEMPT (explicit carve-out in IEPS)
- **Coverage in Colima:** All taxed fuels in state scope + road, water, rail, and civil aviation transport fuels
- **Overlap with S:** 100% on in-scope fuels — every source the state tax reaches is also taxed upstream by the federal tax. The state tax adds a second price signal on the same base, not new coverage.

### E — Mexico Pilot ETS
- **Legal basis:** ACUERDO SEMARNAT, Sistema de Comercio de Emisiones piloto; mandatory reporting began 2022
- **Threshold:** ≥ 25,000 tCO₂e/yr per facility (energy and industry sectors)
- **Binding status:** **Non-binding pilot** — no financial penalty for non-compliance during pilot phase. Legal and operational coverage diverge materially.
- **Coverage in Colima:** Manzanillo thermoelectric plant (full plant — but NG fraction exempt from both taxes), Peña Colorada / Las Encinas iron pellet plants, Cementos Apasco Tecomán
- **Results flagged accordingly:** ETS figures represent legal scope; operational coverage is likely lower

---

## 3. Data Foundation

### Primary inventory source
- **Document:** *Greenhouse Gas Inventory of the State of Colima, Base Year 2015*
- **Producer:** IMADES (Instituto para el Medio Ambiente y Desarrollo Sustentable del Estado de Colima)
- **Funded by:** Under2 Coalition Future Fund (Québec, Scotland, Wales; grant UC/FF/2018/002)
- **Published:** 2019-01-31
- **GWPs:** AR5 (CH₄=28, N₂O=265) — matches INECC INEGYCEI 2022; no GWP conversion required
- **Methodology:** IPCC 2006 Guidelines; Tier 2 stationary combustion, Tier 3 road transport (MOVES-Mexico)
- **Overall uncertainty:** ±8.9% (inventory's own estimate)

**Why 2015 and not more recent?** The 2015 IMADES inventory is the most recent public state-level GHG inventory for Colima. A 2005 inventory existed but used SAR GWPs and would have required a 20-year extrapolation; the 2015 base reduces the extrapolation gap to 10–11 years.

### Key 2015 inventory figures

| Sector | GgCO₂e | Share |
|--------|---------|-------|
| Energy | 15,070 | 83% |
| AFOLU | 1,879 | 10% |
| IPPU | 724 | 4% |
| Waste | 464 | 3% |
| **Total** | **18,137** | 100% |

**Energy subsector detail (GgCO₂e):**
- Electricity generation (Manzanillo thermoelectric): 7,128 (47% of energy; 39% of state)
- Road transportation: 5,578 (37% of energy)
- Manufacturing & construction: 1,950 (13%)
- Residential, commercial, agriculture, navigation, rail, aviation: ~420

**Manzanillo thermoelectric plant (CFE — "Termoeléctrica Gral. Manuel Álvarez Moreno"):**
- Fuels: Natural gas 98,435 TJ + Diesel 16,951 TJ + Fuel oil 28 TJ
- NG share of plant CO₂: **~82%** → exempt from both federal and state carbon taxes
- Taxable (diesel+FO) fraction: ~18% → ~1,275 GgCO₂e of 7,128 GgCO₂e total

This single fuel-mix characteristic is the dominant driver of Colima's results: the state's largest emitter is mostly exempt.

---

## 4. Estimation Tier

| Component | Tier | Rationale |
|-----------|------|-----------|
| Stationary combustion (S, F overlap) | **Tier 3** | INECC INEGYCEI national sector growth rates applied to 2015 subsector totals; no facility registry available |
| Transport (F-only) | **Tier 3** | Same growth rate approach |
| ETS overlap | **Tier 3** | Facility-class identification; no Colima-specific ETS registry data |
| Total state emissions | **Tier 4** | Blended CAGR on 2015 base; energy balance cross-check |

No facility-level registry data is available for Colima (no EUTL equivalent; Mexico SEMARNAT MRV data not publicly disaggregated to state level for all sectors). Tier 1 or 2 estimation is not feasible.

---

## 5. Methodology — Step by Step

### Step 1: Map legal scope (01_clean.py)
Construct the 2015 inventory by subsector from the IMADES PDF. Apply scope flags:
- `in_state_tax_scope` — is this subsector within the Colima state tax's legal reach?
- `overlap_federal_tax` — is it also reached by the federal IEPS carbon tax?
- `overlap_ets_pilot` — is it within the Pilot ETS threshold (≥25,000 tCO₂e/yr facilities)?

The natural gas exemption is applied at the fuel level for the electricity sector: the Manzanillo plant's fuel mix is split into NG fraction (exempt, tracked separately) and diesel+FO fraction (taxable, carried into overlap calculations).

**Outputs:** `colima_inventory_2015.csv`, `colima_fuel_consumption_2015.csv`, `colima_manzanillo_plant_2015.csv`, `colima_ippu_detail_2015.csv`, `colima_tax_scope_2015.csv`

### Step 2: Extrapolate to target years 2025/2026 (02_estimate.py)
Apply compound annual growth rates (CAGRs) derived from INECC INEGYCEI national sector trends (2015–2022) to each in-scope subsector, projected forward to 2025 and 2026. Sector-specific growth classes:

| Growth class | CAGR central | CAGR range | Source |
|---|---|---|---|
| Electricity (diesel fraction) | −2.0%/yr | −8% to +1% | SENER prospectiva; CFE dispatch data |
| Electricity (NG fraction) | +0.2%/yr | −3% to +3% | SENER |
| Manuf — cement | +1.2%/yr | −2% to +3% | CANACEM national cement production |
| Manuf — food/beverage | +1.5%/yr | −1% to +3.5% | INECC 1A2e national |
| Manuf — metallurgical | +0.8%/yr | −5% to +3% | SE/Minería iron ore exports |
| Manuf — non-metallic minerals | +1.3%/yr | −2% to +3.5% | INECC 1A2f |
| Manuf — other/chemical | +1.0%/yr | −2% to +3% | General industrial proxy |
| Residential/commercial/agri | +0.8%/yr | −1% to +2% | SENER LP gas; CONAPO population |
| Transport | +1.0%/yr | −2% to +3% | General proxy |

Each subsector produces a (low, central, high) triple. Uncertainty bounds reflect CAGR uncertainty only; structural uncertainty from the state tax design (threshold, exact fuel list) is the dominant unquantified source.

**Output:** `colima_extrapolated_2025_2026.csv`

### Step 3: Compute overlap and Venn decomposition (02_estimate.py + 03_outputs.py)
Using the coverage flags and extrapolated values, compute all seven Venn segments:

```
S∩F∩E  =  electricity (diesel), cement combustion, metallurgical
S∩F    =  remaining manufacturing, residential, commercial, agriculture
S only =  biogas/energy generation plants (non-fossil; exempt from IEPS)
F only =  road, water, rail, aviation transport
E only =  NG fraction of Manzanillo plant (in ETS legal scope; not taxed)
S∩E    =  empty (all ETS sources in state scope also in federal scope)
F∩E    =  empty (federal tax does not cover NG; NG is E-only)
```

Deduplicated union by inclusion–exclusion:
```
S∪F∪E = S∩F∩E + S∩F + S_only + F_only + E_only
```

**Output:** `colima_overlap_estimates.csv`, `colima_overlap_full_table.csv`

### Step 4: Produce publication outputs (03_outputs.py)
- **Figure 1:** Stacked bar chart — full Venn segment decomposition by year (2025 and 2026)
- **Figure 2:** Grouped bar chart — instrument totals vs deduplicated union vs total state emissions
- **Table:** Full breakdown with central estimates, low/high bounds, and coverage shares

---

## 6. Results Summary

Central estimates (2025 and 2026 are near-identical; 2025 shown):

| Metric | GgCO₂e | % of state |
|--------|---------|------------|
| **Colima state tax — gross coverage** | 3,533 | 19.5% |
| **Federal carbon tax — Colima coverage** | 9,854 | 54.3% |
| **Pilot ETS — legal coverage** | 7,635 | 42.1% |
| S∩F∩E — covered by all three | 1,665 | 9.2% |
| S∩F only — state + federal, not ETS | 1,859 | 10.2% |
| **S only — state tax unique (not F or E)** | **~10** | **0.05%** |
| F only — transport fuels | 6,331 | 34.9% |
| E only — NG electricity (not taxed) | 5,970 | 32.9% |
| **Deduplicated union S∪F∪E** | **15,834** | **87.3%** |

Uncertainty ranges: see `outputs/tables/colima_overlap_full_table.csv`

---

## 7. Key Analytical Conclusions

### The Colima state tax adds virtually no unique emissions coverage
The net S-only segment — emissions the state tax reaches that are covered by neither the federal carbon tax nor the Pilot ETS — is approximately **10 GgCO₂e (0.05% of state emissions)**. This consists entirely of biogas combustion at small energy generation plants, which are non-fossil and already exempt from the federal IEPS levy.

This result is structural, not coincidental. The federal carbon tax is upstream (applied to fuel importers/distributors), so every fossil fuel the state tax reaches has already been taxed at the point of sale by the federal government. The state tax's function is to apply an **additional price signal** on the same emissions — not to extend coverage to sources the federal instrument misses.

### The natural gas exemption is the single largest driver of the coverage gap
Of Colima's 18,137 GgCO₂e total emissions, the Manzanillo thermoelectric plant accounts for 7,128 GgCO₂e (~39%). Approximately 82% of the plant's fuel input is natural gas, which is explicitly exempt from both the federal and state carbon taxes under Mexico's IEPS framework. This single carve-out reduces the electricity sector's in-scope emissions from 7,128 GgCO₂e to ~1,275 GgCO₂e — a reduction of ~83%.

### The deduplicated union covers ~87% of state emissions
Three instruments together — with full deduplication — cover approximately 15,834 GgCO₂e (87.3% of state). The remaining ~13% is outside all three instruments: AFOLU, waste, IPPU process emissions (cement calcination, HFCs), and residential biomass combustion.

### The Pilot ETS adds substantive coverage but is non-binding
The ETS (legal scope) covers ~42% of state emissions, mostly through the Manzanillo NG fraction, which is large but exempt from both carbon taxes. Because the ETS is a non-binding pilot, operational coverage is likely materially lower than the legal figures reported here. Results for instrument E should be treated as upper bounds.

### 2025 and 2026 estimates are near-identical
The two target years differ by less than 0.5% on all metrics. Declining diesel use at Manzanillo (−2%/yr) is roughly offset by manufacturing growth (+1–1.5%/yr). For publication purposes, a single 2025–2026 estimate with the full uncertainty range is appropriate.

---

## 8. Caveats and Open Questions

1. **Colima state tax design details not fully published as of early 2025.** The analysis assumes the Jalisco/Zacatecas model (stationary combustion, NG exempt, no facility threshold stated). If the final regulation differs — e.g., introduces a threshold excluding small sources, or extends to additional fuel types — estimates should be revised.

2. **Is Manzanillo thermoelectric on the Pilot ETS participant list?** This determines whether the ETS overlap for the electricity sector is binding or nominal. Analysis assumes legal inclusion based on the ≥25,000 tCO₂e/yr threshold; this should be verified against the SEMARNAT participant registry.

3. **No public Colima inventory more recent than 2015.** If IMADES or INECC publishes a 2020 or later state inventory, the extrapolation approach should be replaced with direct base-year data.

4. **Cement plant combustion share.** The 67% combustion/33% process split for Cementos Apasco was estimated from the clinker fraction and standard IPCC emission factors. The process portion (calcination) is in the ETS legal scope but not in either carbon tax scope. This split should be verified against SEMARNAT MRV data if available.

---

## 9. Files in This Case

```
states/colima/
├── 01_clean.py                         # Ingest 2015 inventory; scope flags; fuel splits
├── 02_estimate.py                      # Extrapolation to 2025/2026; Venn computation
├── 03_outputs.py                       # Publication tables and figures
├── data/
│   ├── raw/
│   │   └── Colima_future_fund_report_2018_pdf.pdf   # Source inventory
│   └── processed/
│       ├── colima_inventory_2015.csv
│       ├── colima_fuel_consumption_2015.csv
│       ├── colima_manzanillo_plant_2015.csv
│       ├── colima_ippu_detail_2015.csv
│       ├── colima_tax_scope_2015.csv
│       ├── colima_extrapolated_2025_2026.csv
│       └── colima_overlap_estimates.csv
├── outputs/
│   ├── figures/
│   │   ├── colima_venn_segments_2025_2026.png
│   │   └── colima_coverage_summary_2025_2026.png
│   └── tables/
│       ├── colima_overlap_summary.csv
│       └── colima_overlap_full_table.csv
├── docs/
│   ├── data_sources.md                 # Source metadata and access notes
│   └── assumptions_02.md              # Estimation assumptions (auto-generated)
└── README.md                           # This file
```

---

## 10. Suggested Commit Sequence

```bash
git add states/colima/data/raw/
git commit -m "colima: add raw 2015 IMADES inventory PDF"

git add states/colima/01_clean.py states/colima/data/processed/
git commit -m "colima: 01_clean — ingest 2015 inventory; apply scope flags; split Manzanillo NG/diesel"

git add states/colima/02_estimate.py
git commit -m "colima: 02_estimate — extrapolate to 2025/2026 via INECC sector CAGRs; Venn decomposition"

git add states/colima/03_outputs.py states/colima/outputs/
git commit -m "colima: 03_outputs — publication figures and full overlap table"

git add states/colima/docs/ states/colima/README.md
git commit -m "colima: docs — data sources, assumptions log, README with methodology and results"
```

---

*Analysis by World Bank Climate Change Group. Estimation tier: Tier 3/4. Base year: 2015. Target years: 2025–2026. Part of the Mexico carbon pricing coverage overlap series for the State & Trends of Carbon Pricing publication.*
