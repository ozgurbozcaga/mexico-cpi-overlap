# Mexico Carbon Pricing Overlap — Methodology and Data Sources

**Case:** Mexico Federal Carbon Tax (IEPS componente carbono) × Mexico Pilot ETS (SCE Fase Piloto)  
**Estimation tier:** Tier 2 (ETS coverage) / Tier 3 (NG-share uncertainty propagation)  
**Coverage definition:** Operational — emissions from sources actively participating  
**Analysis years:** Carbon tax: 2014–2024 | ETS: 2020–2024 | Overlap: 2020–2023  
**Last updated:** March 2026

---

## 1. Instruments in Scope

**Mexico Federal Carbon Tax (IEPS componente carbono)**  
In force since January 2014. An upstream tax applied at the point of fossil fuel production, import, or first sale. Covers all fossil fuels except natural gas, which is zero-rated under Ley del IEPS Art. 2(I)(H). No facility-level threshold. Scope boundary applied: narrow/conservative — combustion CO₂ from 1A categories only; fugitives (1B) and process CO₂ (2A/2B/2C) excluded.

**Mexico Pilot ETS (SCE Fase Piloto)**  
Operational since January 2020. Legal basis: LGCC Art. 94; SCE Reglamento (DOF 1 Oct 2019). Facility threshold: ≥100,000 tCO₂e/year. No binding financial obligation in the pilot phase — legal and operational coverage therefore diverge. SEMARNAT sector allocations are used as the best available proxy for operational coverage. Treated as implemented (not voluntary) for this analysis.

---

## 2. Data Sources

| Dataset | File | Coverage | Use |
|---|---|---|---|
| INECC INEGYCEI 2014–2019 | `INEGyCEI_2014-2019.xlsx` | CO₂ by IPCC category, 6 years in tabs | INECC panel, national totals |
| INECC INEGYCEI 2020–2024 | `mexico_{year}_ghgemissions.xlsx` × 5 | CO₂ by IPCC category, annual | INECC panel, national totals |
| IEA Mexico energy statistics | `IEA_mexico.xlsx` | Industry energy by fuel (ISIC), 2000–2023 | NG share for cement/lime/glass (ISIC 23) |
| SENER BNE 2024 | `Anexo_gr_fico_y_estad_stico_-_BNE_2024.xlsx` | Sector fuel mix, 2010–2024 | Power sector NG share (F4.5/F4.6); sector fuel series (F5.x) |
| SEMARNAT SCE allocation table | DOF notice, 27 Nov 2019 | Sector allocations 2020–2021 | ETS covered emissions proxy |

All raw files are committed to `data/raw/` and should not be modified.

---

## 3. Methodology

### 3.1 Carbon Tax Coverage

**Method:** INECC 1A total combustion CO₂ minus estimated natural gas combustion CO₂ across all sectors.

> Carbon tax coverage = INECC 1A\_total − Σ (sector CO₂ × NG share)

The national total (Sin UTCUTS, all-gas CO₂e) is drawn from the INECC files' pre-computed summary column. Coverage shares use this as the denominator. Numerators are CO₂-only — shares are therefore conservative, as covered CH₄ and N₂O are not counted.

**NG share sources by sector:**

| Sector | Source | Central estimate |
|---|---|---|
| Power (1A1a) | BNE F4.5 fuel mix (2024), applied 2014–2023 via F4.6 stability check | 84.7% ±2pp |
| Refining (1A1b) | Expert range | 50% [40–60%] |
| O&G upstream (1A1cii) | Expert range (own associated gas) | 80% [70–90%] |
| Cement/lime/glass | IEA ISIC 23 fuel breakdown × IPCC 2006 EFs | 16–19% (petcoke central; generic oil sensitivity) |
| Mining (1A2i) | Expert range (diesel-dominated) | 12% [5–20%] |
| Other industry | BNE F5.7 aggregate ±5pp | Year-varying (~38–51%) |
| Residual (transport + other) | Conservative fixed | 5% [2–10%] |

### 3.2 ETS Coverage

SEMARNAT pilot allocations (2020–2021) are used as the operational coverage proxy. For 2022–2024, allocations are extrapolated by applying INECC subcategory growth rates to the 2021 baseline.

Each sector's allocation is split into combustion and process components using the INECC combustion/process ratio for that sector's mapped categories. The NG share is then applied to the combustion component only.

### 3.3 Overlap Estimation

> Overlap = ETS combustion coverage × (1 − NG share)  
> = ETS combustion coverage − NG CO₂ within ETS

Process CO₂ (2A/2B/2C) covered by the ETS is outside the carbon tax scope — it is not overlap. NG combustion within the ETS is zero-rated by the carbon tax — it is not overlap. Only non-NG combustion CO₂ covered by the ETS constitutes the overlap.

### 3.4 Coverage Shares

Two share types are reported for each instrument:

- **Absolute share:** instrument coverage / national GHG total, with no deduplication. Summing the two absolute shares double-counts the overlap.
- **Net share:** deduplicated joint coverage / national GHG total, where the overlap is subtracted once. This is the correct figure for assessing the combined reach of both instruments.

> Net combined coverage = Carbon tax coverage + ETS coverage − Overlap

---

## 4. Key Assumptions and Limitations

**SEMARNAT allocations as coverage proxy.** No facility-level MRV or registry data is publicly available for the SCE Fase Piloto. Allocations are used as the best available proxy. The pilot phase has no binding obligation, meaning some allocated facilities may not be actively reporting.

**1A2miii (Otras ramas) excluded.** This INECC category (21–29 Mt/year) cannot be attributed to any named ETS sector and is excluded from the ETS scope with an explicit conservatism note. Its inclusion would raise ETS coverage estimates modestly.

**2A4 (Other carbonate uses, ~5–7 Mt) excluded from central estimate.** Included in sensitivity runs only, as attribution to ETS-covered facilities is uncertain.

**NG share parameters carry uncertainty.** For most sectors outside power, NG shares are derived from expert ranges rather than facility-level data. The resulting uncertainty bands (±10pp on overlap, ±8pp on combined net share) are propagated throughout and reported explicitly.

**INECC frozen values.** Categories 1A1b, 1A1cii, and 1B2 show identical 2023 and 2024 values — likely carried forward in the inventory. These are flagged; 2023 is used as the preferred base year for these categories.

**Inventory reclassification at 2019–2020.** Categories 1A2e (food & beverages), 1A2i (mining), and 1A2miii show large step changes at this boundary, reflecting a reclassification between inventory editions rather than real emissions changes. The 1A\_total series is unaffected and is used for carbon tax coverage.

**Coverage shares are CO₂-only / all-gas CO₂e.** The denominator is INECC Emisiones Sin UTCUTS (all gases, CO₂e). Numerators are CO₂ only. Shares are conservative.

---

## 5. Output Files

| File | Description |
|---|---|
| `data/processed/clean_inecc_panel.csv` | INECC CO₂ by category, 2014–2024 (MtCO₂) |
| `data/processed/clean_ng_shares.csv` | NG share by sector and year, with low/high bounds |
| `data/processed/clean_iea_nonmetallic.csv` | IEA ISIC 23 fuel breakdown and derived CO₂ |
| `data/processed/clean_bne_power.csv` | Power sector NG share by year |
| `data/processed/clean_bne_sectors.csv` | BNE sector fuel time series (PJ) |
| `outputs/tables/T1_ctax_coverage_2014_2024.csv` | Carbon tax coverage, Mt + share, 2014–2024 |
| `outputs/tables/T2_ets_coverage_2020_2024.csv` | ETS coverage by component, 2020–2024 |
| `outputs/tables/T3_overlap_summary_2020_2023.csv` | Full overlap summary with absolute and net shares |
| `outputs/tables/T4_sector_breakdown_2023.csv` | ETS sector detail, 2023 |
| `outputs/figures/F1_ctax_coverage_share.png` | Carbon tax coverage share 2014–2024 |
| `outputs/figures/F2_stacked_coverage_shares.png` | Stacked coverage shares 2020–2023 |
| `outputs/figures/F3_uncertainty_waterfall_2023.png` | Uncertainty waterfall, 2023 |

---

## 6. Reproduce

```bash
pip install -r requirements.txt
python scripts/01_clean.py
python scripts/02_estimate.py
python scripts/03_outputs.py
```

All scripts are independently runnable and log their actions. Raw data files must be present in `data/raw/`.
