# Methodology Note — Guanajuato Coverage Overlap Estimation

## Case summary

**State:** Guanajuato, Mexico  
**Instruments:** Guanajuato state carbon tax (S) × Mexico Federal IEPS (F) × Mexico Pilot ETS (E)  
**Base year:** 2013  
**Estimation tier:** Tier 3  
**State total emissions:** 19,264.8 GgCO₂e (IGCEI 2013)

---

## Venn framework

Coverage overlap follows the project-wide three-instrument framework:

```
Overlap(A,B) = Covered(A) ∩ Covered(B)
Deduplicated coverage = Covered(A) + Covered(B) − Overlap(A,B)
```

Eight mutually exclusive segments are computed:
- S∩F∩E — all three instruments
- S∩E only — state tax + ETS (not federal)
- S∩F only — state tax + federal (not ETS)
- S only — state tax only
- F∩E — federal + ETS (not state) → ~0 in this case
- F only — federal only (transport, residential, commercial)
- E only — ETS only → ~0 in this case
- Uncovered — no instrument

---

## Step-by-step estimation

### Step 1: Map S scope

S covers CO₂, CH₄, N₂O from stationary industrial/energy sources:
- Energy industries (Salamanca refinery + power) and manufacturing combustion
- Ladrilleras (brick kilns) — local stationary category
- IPPU process N₂O (caprolactama, ácido nítrico)
- Excludes: transport, residential, commercial, agricultural, AFOLU, Waste, HFC

**S total = 6,622.1 GgCO₂e** (34.4% of state total)

Note: HFC (306.8 GgCO₂e) explicitly excluded — state law covers CO₂/CH₄/N₂O only.

### Step 2: Apply F fractions (fuel-type based, deterministic)

Within each S-scope sector, F-covered emissions are those from non-NG fossil fuels.
Fractions derived from IGCEI 2013 uncertainty table (Table 16):

- Energy industries: 26.7% non-NG (combustóleo + diesel), 73.3% NG
- Manufacturing: 47.7% non-NG (combustóleo + diesel + LP + aceites), 52.3% NG
- Process N₂O (IPPU): 0% F-covered (F applies to fuel sales only)
- Fugitives: 0% F-covered (F applies to fuel sales only)
- Ladrilleras: 50% fossil (assumption, range 30–70%)

### Step 3: Apply ETS coverage fractions (Tier 3 Pareto)

Within each S-scope sector, ETS-covered emissions are those from facilities ≥ 25,000 tCO₂e/yr.
No facility-level registry data available → Pareto/size-based estimation.

Key size indicators from inventory:
- Salamanca refinery: 194,500 barrels/day crude (definitively E-covered)
- Caprolactama: 85,000 t/yr, process N₂O alone = 202.7 GgCO₂e >> threshold

### Step 4: Compute Venn segments

Under the independence assumption (fuel mix of E-covered facilities = sector average):

```
S∩F∩E = F_fraction × E_fraction × sector_total
S∩E   = (1-F_fraction) × E_fraction × sector_total
S∩F   = F_fraction × (1-E_fraction) × sector_total
S_only = (1-F_fraction) × (1-E_fraction) × sector_total
```

---

## Central results

| Segment | GgCO₂e | % of state total |
|---------|--------|-----------------|
| S∩F∩E (triple overlap) | 1,733.9 | 9.0% |
| S∩E only (NG+process in large facilities) | 3,965.7 | 20.6% |
| S∩F only (non-NG in small facilities) | 393.2 | 2.0% |
| S only | 529.3 | 2.7% |
| **S total** | **6,622.1** | **34.4%** |
| F only (outside S, primarily transport) | 8,350.0 | 43.3% |
| HFC (outside all instruments) | 306.8 | 1.6% |
| Uncovered (AFOLU, Waste, NG non-S, other) | ~3,986 | ~20.7% |

### Range (low–high)

| Segment | Low | Central | High |
|---------|-----|---------|------|
| S∩F∩E | ~1,365 | 1,734 | ~2,136 |
| S∩E only | ~4,243 | 3,966 | ~3,591 |
| S total | ~6,622 | 6,622 | ~6,622 |

Note: S total is invariant across scenarios (state scope is deterministic).
Scenarios affect the S∩F∩E vs S∩E split (ETS coverage fraction).

---

## Key structural features of Guanajuato

### 1. NG exemption creates dominant S∩E-only block

The Salamanca refinery (energy industries) runs primarily on NG (53.15 PJ vs 13.78 PJ fuel oil).
NG combustion in the refinery is covered by S (stationary industrial source) and E (large facility),
but NOT by F (NG exempt from IEPS). This creates ~3,085 GgCO₂e in the S∩E-only segment
from energy industries alone.

Large manufacturing (automotive, chemicals) similarly has significant NG use (13.31 PJ),
adding ~669 GgCO₂e to S∩E-only from manufacturing.

### 2. Process N₂O adds to S∩E-only

Caprolactama production (85,000 t/yr) generates 202.7 GgCO₂e of process N₂O — the second-
largest single-category contributor to the S∩E-only segment after the refinery NG combustion.
Process N₂O is in S scope (stationary industrial CO₂-equivalent), in E scope (large facility),
but NOT in F scope (F is a fuel levy; process reactions are not fuel combustion).

### 3. No process CO₂ from mineral production

Unlike Morelos (cement calcination) or other states with minerals industry,
Guanajuato has NO cement production and NO blast furnaces (confirmed by IGCEI 2013, p.28).
The IPPU sector is narrowly focused on chemical industry N₂O and HFC refrigerants.

### 4. Transport is F-only (largest single category outside S)

Autotransporte (7,068.4 GgCO₂e) uses only non-NG fuels (gasoline, diesel, kerosene).
This is entirely F-covered but outside S and E scope. F's large total share of state
emissions (54.4%) is driven primarily by transport coverage.

---

## Legal/operational divergence flag

**Mexico Pilot ETS (E):** The pilot phase was non-binding — no financial obligations
for covered installations. Legal coverage overestimates operational coverage.
All E values are presented as **upper bounds**. Flag: legal > operational.

**Guanajuato state tax:** Design is for direct GHG taxes (not upstream fuel levy like F).
For energy industries and manufacturing, legal and operational coverage likely align.
The ladrilleras category (informal/semi-formal sector) may have lower operational
compliance, but at 12.1 GgCO₂e this is immaterial to overall results.

---

## Cross-state comparison context

Guanajuato has the largest S-scope total of the four analysed states at 6,622 GgCO₂e,
driven by the Salamanca refinery. The S∩E-only segment dominates (59.9% of S total)
due to heavy NG use at the refinery and process N₂O from the chemical sector.
This contrasts with Durango (where electricity NG dominates) and Colima (small state,
NG-dominated utilities). Morelos is the only state with significant process CO₂ from minerals.

---
*Ozgur Bozcaga | World Bank Climate Change Group | State & Trends of Carbon Pricing (internal)*
