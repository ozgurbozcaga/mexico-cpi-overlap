# Data Sources — Morelos Carbon Pricing Overlap Analysis

## Primary Inventory Source

**Inventario de Emisiones Contaminantes a la Atmósfera del Estado de Morelos, Año base 2014**

- Producers: Secretaría de Desarrollo Sustentable (SDS) Morelos / SEMARNAT / INECC / LT Consulting
- Review: Molina Center for Energy and the Environment
- Published: January 30, 2017
- Local file: `data/raw/Morelos_inventory_pdf.pdf`
- Accessed: March 2026

**CRITICAL LIMITATION — read before using results:**
This is an **air quality inventory**, not an IPCC GHG inventory. GHG content is a supplementary annex (Annex II and IV). Consequences:
- Units: Mg/year (= tonne CO₂e/year). Converted to GgCO₂e in 01_clean.py.
- GHGs covered: CO₂, CH₄, N₂O, black carbon only. **HFCs, PFCs, SF₆ are absent.**
- GWP version not stated; likely AR4 (CH₄=25, N₂O=298) per SEMARNAT practice in 2014-2017. We apply AR5 (CH₄=28, N₂O=265) for consistency with INECC INEGYCEI.
- Base year 2014 → 11-year extrapolation to 2025/2026. Wider uncertainty than other states.

### Key tables used:

| Table | Content | Used for |
|-------|---------|----------|
| Cuadro 3 | Industrial fuel consumption 2014 (Mg/TJ by fuel type) | F scope fractions |
| Cuadro 12 (Annex II) | GHG totals by source type (Mg/year) | Sanity check |
| Cuadro 14 (Annex IV) | GHG by detailed category (Mg/year) | All emission values |
| Figure 9 (Cuadro 3) | Energy shares by fuel type (pie chart) | NG fraction confirmation |

### Data reconciliation notes:

Three artefacts required correction before analysis (documented in 01_clean.py):

1. **FIXED total gap (37,265 Mg CO₂):** Sectors Automotriz, Accesorios, Petroquimica, Mezclas all show 0.0 in Annex IV GHG columns (rounded) but contribute to the Cuadro 12 aggregate. Resolved by adding a `Residual_fixed_sectors` row. Impact on results: negligible (allocated to OTHER_MANUFACTURING scope fractions).

2. **AREA over-count (200,000 Mg CO₂):** Two artefacts in Annex IV over-state the AREA leaf sum: (a) `Otras_area` (170,102 Mg) is an aggregation of categories already counted individually; (b) `Aguas_residuales` (29,900 Mg CO₂ residual) is excluded from the Cuadro 12 AREA total per IPCC convention (wastewater is a separate reporting sector). Resolved by reclassifying to WASTE source type.

3. **AREA N₂O gap (9.8 Mg):** Minor N₂O emitting area categories (soil emissions, fertiliser application) present in Cuadro 13 but not in the GHG Annex IV leaf breakdown. At 9.8 Mg × 265 GWP = 2.6 GgCO₂e this is negligible. Tolerance widened and documented.

## Instrument Design Sources

### S — Morelos State Carbon Tax
- **Ley de Hacienda del Estado de Morelos** — carbon tax provisions
- Scope: CO₂, CH₄, N₂O, HFCs, PFCs, SF₆ from stationary sources
- Exemptions: mobile sources; maritime; small-scale agricultural activities
- **Data gap:** HFCs/PFCs/SF₆ absent from 2014 inventory → S coverage understated; see assumptions_02.md

### F — Federal IEPS Carbon Tax
- IEPS Art. 2o-C; NG exemption statutory
- For Morelos: NG is only 3.3% of industrial combustion CO₂ → minimal impact of NG exemption

### E — Mexico Pilot ETS
- SEMARNAT SCE; threshold ≥25,000 tCO₂e/yr; non-binding pilot
- Morelos has 3 cement plants, 2 glass plants, 2 pulp/paper plants as main ETS candidates

## Supporting References

- INECC INEGYCEI 2022 — national sector trends for growth rate calibration
- INECC-IMP (2014): Factores de emisión de CO₂ para combustibles mexicanos — emission factors
- IPCC 2006 Guidelines Volume 3 (IPPU) — cement calcination process split methodology
- SEMARNAT COA (Cédulas de Operación Anual) — cross-reference for facility-level data

## Open Questions / Pending Verification

1. **Full Morelos carbon tax legal text** — confirm exact scope clauses; particularly whether "small-scale agricultural activities" has a specific threshold or covers all agricultural sources
2. **Post-2014 GHG inventory** — if SDS Morelos or INECC publishes a 2018+ inventory, replace this analysis entirely (would be Tier 2 with national IPCC categories)
3. **Cement sector process fraction** — 60/40 split assumed from national average; Morelos-specific clinker ratio would improve precision
4. **ETS participant registry for Morelos** — confirm which specific facilities are registered in SEMARNAT SCE
5. **HFCs/PFCs/SF₆ for Morelos** — INECC sector estimates available at national level; could be pro-rated by industrial activity
