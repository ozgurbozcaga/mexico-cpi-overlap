# Estado de Mexico — Assumptions for 02_estimate.py

## Estimation Tier: Tier 3

Published state GHG inventory (IEEGyCEI-2022) with IPCC 2006 sector structure, AR5 GWPs, and ±5.47% uncertainty. Estado de Mexico has the most detailed inventory in this analysis set, with 11 manufacturing sub-categories and 6 IPPU sub-categories.

## S (State Carbon Tax) Scope

### Gas scope: CO2, CH4, N2O ONLY

Unlike Zacatecas (full Kyoto basket), Queretaro, or Yucatan, the Estado de Mexico carbon tax covers **only CO2, CH4, and N2O**. HFCs, PFCs, and SF6 are NOT covered. This is a narrower gas scope that excludes fluorinated gas emissions from IPPU.

### Source scope: All fixed sources (fuentes fijas)

- **Post-Dec 2022 reform**: scope expanded to include federal-jurisdiction fixed sources (previously state-jurisdiction only)
- No facility-size threshold
- Downstream regulation: tax applies to the emitting entity
- Direct + indirect emissions covered

### S coverage by sector:

| Sector | S Share | Rationale |
|--------|---------|-----------|
| 1.A.1.a Electricity | 1.0 | Fixed-source combustion |
| 1.A.2 Manufacturing | 1.0 | Fixed-source combustion |
| 1.A.3 Transport | **0.0** | **Mobile sources — excluded** |
| 1.A.4.a Commercial | 1.0 | Fixed-source combustion |
| 1.A.4.b Residential | **0.0** | **Not fixed sources — excluded** |
| 1.A.4.c Agricultural | 1.0 | Fixed-source combustion |
| 1.B Fugitive | 0.0 | Zero in state (no fuel production) |
| 2.A.1 Cement | 1.0 | Process CO2 at fixed source |
| 2.A.2 Lime | 1.0 | Process CO2 at fixed source |
| 2.A.3 Glass | 1.0 | Process CO2 at fixed source |
| 2.A.4 Other carbonates | 1.0 | Process CO2 at fixed source |
| 2.C Metals | 1.0 | Process emissions at fixed source |
| 2.D Lubricants/wax | 1.0 | Non-energy product use at fixed source |
| 3.x AFOLU | **0.0** | **Livestock, soils — not fixed sources** |
| 4.x Waste | **0.0** | **Excluded from tax scope** |

**Key difference from Zacatecas/Yucatan**: No HFC/PFC/SF6 coverage means the F-gas component of IPPU is uncovered. However, the IEEGyCEI-2022 inventory does not separately report F-gas emissions by IPPU sub-sector, so this exclusion primarily affects any HFC leakage from commercial/industrial refrigeration (which in other states appears in product use categories).

## F (Federal IEPS Carbon Tax) Scope

### Natural gas exemption

F covers combustion CO2 from all fossil fuels **except natural gas**. The F share for each combustion sector = 1 - NG share.

### Natural gas share assumptions

Estado de Mexico has **significantly higher NG penetration** than states like Zacatecas, reflecting its proximity to the national gas pipeline network and major industrial/power generation infrastructure.

| Sector | NG Share | F Share (=1-NG) | Basis |
|--------|----------|-----------------|-------|
| Electricity (1.A.1.a) | **80%** | 20% | Major gas-fired power plants including PIEs (productores independientes de energia); national grid CFE dispatch favors NG |
| Manufacturing (1.A.2) | **50%** | 50% | Diversified fuel mix — inventory confirms NG + gas LP + diesel + combustoleo/coke/coal across 11 sub-sectors |
| Commercial (1.A.4.a) | **40%** | 60% | Urban area with NG distribution; significant NG use in commercial buildings |
| Residential (1.A.4.b) | **15%** | 85% | Mostly gas LP (tanque estacionario); some piped NG in newer developments |
| Agricultural (1.A.4.c) | **5%** | 95% | Minimal NG use in agricultural combustion |
| Transport (1.A.3) | **0%** | 100% | All transport fuels are petroleum-based (gasoline, diesel, jet fuel) |

**Impact of high NG shares**: The 80% NG share in electricity means F covers only 20% of electricity combustion CO2 — creating a large S∩E-only segment from NG-fired power plants that are covered by the state tax and ETS but NOT by the federal fuel tax. Similarly, the 50% NG share in manufacturing means F covers only half of manufacturing combustion, creating a substantial S-only segment for NG-fired industrial combustion below the ETS threshold.

### F does NOT cover

- Process emissions (IPPU 2.A, 2.C, 2.D) — not combustion-based
- AFOLU (3.x) — not fossil fuel combustion
- Waste (4.x) — not fossil fuel combustion
- Fugitive (1.B) — not applicable (zero in state)

## E (Mexico Pilot ETS) Scope

### Threshold: >= 25,000 tCO2e/yr direct CO2

### ETS coverage range

Central estimate: **50%** of eligible fixed-source emissions from facilities above threshold.
Range: **30% (low) / 50% (central) / 70% (high)**.

### Sector-specific ETS multipliers

The multiplier adjusts the base 50% coverage upward or downward depending on the sector's facility size distribution:

| Sector | Multiplier | Effective E share | Rationale |
|--------|-----------|-------------------|-----------|
| Electricity (1.A.1.a) | **1.2** | 60% | Large power plants (PIEs, CFE), most above 25,000 tCO2e threshold |
| Manufacturing (1.A.2) | **1.0** | 50% | Mix of large (transport equipment, chemicals) and small facilities |
| Cement (2.A.1) | **1.3** | 65% | Large point sources, high per-facility emissions |
| Lime (2.A.2) | **1.3** | 65% | Large point sources |
| Glass (2.A.3) | **1.3** | 65% | Large point sources |
| Other carbonates (2.A.4) | **1.3** | 65% | Large limestone/soda ash operations (2,417 KtCO2e total) |
| Metals (2.C) | **0.8** | 40% | Smaller-scale lead/zinc operations |
| Lubricants/wax (2.D) | **0.0** | 0% | Non-energy products, dispersed, below threshold |
| Commercial (1.A.4.a) | **0.0** | 0% | No commercial buildings above 25,000 tCO2e |
| Agricultural (1.A.4.c) | **0.0** | 0% | No agricultural operations above threshold |

**Key insight for carbonates/limestone**: The 2,417.1 KtCO2e from "other carbonates" is one of the largest single IPPU categories in any Mexican state. These are process CO2 emissions not covered by F (not combustion), so they fall in the **S∩E-only** segment — a distinctive feature of Estado de Mexico's overlap pattern. The high NG exemption from F amplifies this effect.

## Venn Segment Computation

Standard inclusion-exclusion per sector (same as other states):
```
S∩F∩E = min(s, f, e) × sector_total
S∩E_only = [min(s,e) - min(s,f,e)] × sector_total
S∩F_only = [min(s,f) - min(s,f,e)] × sector_total
S_only = [s - min(s,f) - min(s,e) + min(s,f,e)] × sector_total
F∩E_only = [min(f,e) - min(s,f,e)] × sector_total
F_only = [f - min(s,f) - max(0, min(f,e) - min(s,f,e))] × sector_total
E_only = [e - min(s,e) - max(0, min(f,e) - min(s,f,e))] × sector_total
Uncovered = [1 - min(1, s+f+e - min(s,f) - min(s,e) - min(f,e) + min(s,f,e))] × sector_total
```

## Revenue Cross-Check

| Parameter | Value |
|-----------|-------|
| Tax rate (2022) | 43 MXN/tCO2e |
| Tax rate (2023+) | 58 MXN/tCO2e |
| Ecological tax revenue | MXN 252 million (not all from carbon tax) |
| Revenue-implied floor | ~4,300–5,900 KtCO2e (if ALL ecological revenue were carbon tax) |
| Expected gross S | Should be in this ballpark or higher |

The ecological tax revenue includes multiple instruments beyond the carbon tax, so the actual carbon tax revenue is lower than MXN 252M. Gross S should exceed the revenue-implied floor since the tax base (covered emissions) is larger than what is actually collected (compliance, exemptions, phase-in).

## Known Limitations

1. **1.A.4 split**: The inventory reports 1.A.4 as a single total (3,425.1 KtCO2e) with sub-sector detail. The split into commercial (515.5), residential (2,428.6), and agricultural (481.0) is taken directly from the inventory.
2. **NG share uncertainty**: The 80% NG share for electricity is an estimate based on Estado de Mexico's power generation profile (major PIE gas plants). Actual NG share may vary ±10%.
3. **No HFC quantification**: The inventory does not separately quantify HFC/PFC/SF6 emissions. Since S excludes these gases, this does not affect the overlap model, but means we cannot quantify the "gas scope gap" between Estado de Mexico and broader-scope states.
4. **ETS threshold uncertainty**: Without facility-level data, the ETS coverage multipliers are informed estimates.
5. **Dec 2022 reform**: The scope expansion to federal-jurisdiction sources may have a transitional period of incomplete compliance.
