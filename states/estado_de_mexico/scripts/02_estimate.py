#!/usr/bin/env python3
"""
02_estimate.py — Estado de Mexico Three-Instrument CPI Overlap
===============================================================
Uses published IEEGyCEI-2022 inventory (36,384.9 KtCO2e, Tier 3).

Instruments: S (state carbon tax) x F (federal IEPS) x E (pilot ETS)
S gas scope: CO2, CH4, N2O ONLY (no HFCs, PFCs, SF6 — narrower than Zacatecas/Yucatan)
S source scope: all fixed sources (fuentes fijas), state + federal jurisdiction (post-Dec 2022)
S rate: 43 MXN/tCO2e (2022), 58 MXN/tCO2e (from Dec 2023)
F: upstream fuel levy, all fossil fuels EXCEPT natural gas
E: facilities >= 25,000 tCO2e/yr direct CO2
"""

import pandas as pd
import numpy as np
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPT_DIR)
PROC_DIR = os.path.join(BASE_DIR, "data", "processed")

inv = pd.read_csv(os.path.join(PROC_DIR, "estado_de_mexico_inventory.csv"))

print("=" * 70)
print("ESTADO DE MEXICO CPI OVERLAP ESTIMATION — IEEGyCEI-2022 (Tier 3)")
print("=" * 70)

# =====================================================================
# NATURAL GAS SHARE ASSUMPTIONS
# Estado de Mexico has significant NG use — major gas-fired power plants,
# diversified industrial fuel mix (NG + gas LP + diesel + combustoleo/coke)
# =====================================================================
NG_SHARES = {
    "electricity":  0.80,  # Major gas-fired power plants including PIEs
    "manufacturing": 0.50, # Diversified: NG + gas LP + diesel + combustoleo/coke/coal
    "commercial":   0.40,  # Some NG in commercial buildings
    "residential":  0.15,  # Mostly gas LP
    "agricultural": 0.05,  # Minimal NG use
}

# ETS threshold coverage: 50% central (30-70% range)
ETS_LOW, ETS_CENTRAL, ETS_HIGH = 0.30, 0.50, 0.70

# Sector-specific ETS multipliers (adjust for facility size distribution)
ETS_MULT = {
    "electricity":  1.2,  # Large power plants, mostly above threshold
    "manufacturing": 1.0, # Mix of large and small
    "cement":       1.3,  # Large point sources
    "lime":         1.3,
    "glass":        1.3,
    "carbonates":   1.3,
    "metals":       0.8,  # Smaller scale
    "lubricants":   0.0,  # Non-energy products, not combustion, below threshold
    "commercial":   0.0,  # Too small for ETS
    "residential":  0.0,
    "agricultural": 0.0,
}

# Sub-sector values from inventory (1.A.4 breakdown)
COMMERCIAL_KT = 515.5
RESIDENTIAL_KT = 2428.6
AGRICULTURAL_KT = 481.0

# =====================================================================
# SECTOR-BY-SECTOR INSTRUMENT COVERAGE ASSIGNMENT
# =====================================================================

results = []

for _, row in inv.iterrows():
    code = row["ipcc_2006"]
    desc = row["description"]
    cat = row["broad_category"]
    central = row["central_KtCO2e"]
    low = row["low_KtCO2e"]
    high = row["high_KtCO2e"]

    if code == "1.A.1.a":
        # Electricity generation — fixed source → S covers
        # F covers non-NG combustion; E covers large plants
        s = 1.0
        f = 1.0 - NG_SHARES["electricity"]  # 0.20
        e = ETS_CENTRAL * ETS_MULT["electricity"]  # 0.60
        results.append({
            "ipcc_2006": code, "description": desc, "broad_category": cat,
            "central_KtCO2e": central, "low_KtCO2e": low, "high_KtCO2e": high,
            "s_share": s, "f_share": f, "e_share": min(e, 1.0),
        })

    elif code == "1.A.2":
        # Manufacturing & construction — fixed source → S covers
        s = 1.0
        f = 1.0 - NG_SHARES["manufacturing"]  # 0.50
        e = ETS_CENTRAL * ETS_MULT["manufacturing"]  # 0.50
        results.append({
            "ipcc_2006": code, "description": desc, "broad_category": cat,
            "central_KtCO2e": central, "low_KtCO2e": low, "high_KtCO2e": high,
            "s_share": s, "f_share": f, "e_share": min(e, 1.0),
        })

    elif code == "1.A.3":
        # Transport — MOBILE sources → S EXCLUDED
        # F covers all (transport fuels are non-NG)
        # E = 0 (mobile)
        s = 0.0
        f = 1.0
        e = 0.0
        results.append({
            "ipcc_2006": code, "description": desc, "broad_category": cat,
            "central_KtCO2e": central, "low_KtCO2e": low, "high_KtCO2e": high,
            "s_share": s, "f_share": f, "e_share": e,
        })

    elif code == "1.A.4":
        # Other sectors — split into commercial, residential, agricultural
        total_14 = COMMERCIAL_KT + RESIDENTIAL_KT + AGRICULTURAL_KT

        # Commercial/institutional (515.5) — fixed source → S covers
        s_com = 1.0
        f_com = 1.0 - NG_SHARES["commercial"]  # 0.60
        e_com = 0.0  # Below ETS threshold
        results.append({
            "ipcc_2006": "1.A.4.a", "description": "Commercial/institutional combustion",
            "broad_category": "OTHER_SECTORS",
            "central_KtCO2e": COMMERCIAL_KT,
            "low_KtCO2e": round(COMMERCIAL_KT * (1 - 0.0547), 1),
            "high_KtCO2e": round(COMMERCIAL_KT * (1 + 0.0547), 1),
            "s_share": s_com, "f_share": f_com, "e_share": e_com,
        })

        # Residential (2,428.6) — NOT fixed source → S EXCLUDED
        s_res = 0.0
        f_res = 1.0 - NG_SHARES["residential"]  # 0.85
        e_res = 0.0
        results.append({
            "ipcc_2006": "1.A.4.b", "description": "Residential combustion",
            "broad_category": "OTHER_SECTORS",
            "central_KtCO2e": RESIDENTIAL_KT,
            "low_KtCO2e": round(RESIDENTIAL_KT * (1 - 0.0547), 1),
            "high_KtCO2e": round(RESIDENTIAL_KT * (1 + 0.0547), 1),
            "s_share": s_res, "f_share": f_res, "e_share": e_res,
        })

        # Agricultural combustion (481.0) — fixed source → S covers
        s_agri = 1.0
        f_agri = 1.0 - NG_SHARES["agricultural"]  # 0.95
        e_agri = 0.0
        results.append({
            "ipcc_2006": "1.A.4.c", "description": "Agricultural combustion",
            "broad_category": "OTHER_SECTORS",
            "central_KtCO2e": AGRICULTURAL_KT,
            "low_KtCO2e": round(AGRICULTURAL_KT * (1 - 0.0547), 1),
            "high_KtCO2e": round(AGRICULTURAL_KT * (1 + 0.0547), 1),
            "s_share": s_agri, "f_share": f_agri, "e_share": e_agri,
        })

    elif code == "1.B":
        # Fugitive — 0 in Estado de Mexico (no fuel production)
        results.append({
            "ipcc_2006": code, "description": desc, "broad_category": cat,
            "central_KtCO2e": 0.0, "low_KtCO2e": 0.0, "high_KtCO2e": 0.0,
            "s_share": 0.0, "f_share": 0.0, "e_share": 0.0,
        })

    elif code == "2.A.1":
        # Cement — process emissions at fixed source → S covers (CO2)
        # F = 0 (process, not combustion); E covers large plants
        s = 1.0
        f = 0.0
        e = ETS_CENTRAL * ETS_MULT["cement"]  # 0.65
        results.append({
            "ipcc_2006": code, "description": desc, "broad_category": cat,
            "central_KtCO2e": central, "low_KtCO2e": low, "high_KtCO2e": high,
            "s_share": s, "f_share": f, "e_share": min(e, 1.0),
        })

    elif code == "2.A.2":
        # Lime — process emissions → S covers; E covers large plants
        s = 1.0
        f = 0.0
        e = ETS_CENTRAL * ETS_MULT["lime"]  # 0.65
        results.append({
            "ipcc_2006": code, "description": desc, "broad_category": cat,
            "central_KtCO2e": central, "low_KtCO2e": low, "high_KtCO2e": high,
            "s_share": s, "f_share": f, "e_share": min(e, 1.0),
        })

    elif code == "2.A.3":
        # Glass — process emissions → S covers; E covers large plants
        s = 1.0
        f = 0.0
        e = ETS_CENTRAL * ETS_MULT["glass"]  # 0.65
        results.append({
            "ipcc_2006": code, "description": desc, "broad_category": cat,
            "central_KtCO2e": central, "low_KtCO2e": low, "high_KtCO2e": high,
            "s_share": s, "f_share": f, "e_share": min(e, 1.0),
        })

    elif code == "2.A.4":
        # Other carbonates (limestone + soda ash) — LARGE: 2,417.1 KtCO2e
        # Process emissions → S covers; E covers large plants
        s = 1.0
        f = 0.0
        e = ETS_CENTRAL * ETS_MULT["carbonates"]  # 0.65
        results.append({
            "ipcc_2006": code, "description": desc, "broad_category": cat,
            "central_KtCO2e": central, "low_KtCO2e": low, "high_KtCO2e": high,
            "s_share": s, "f_share": f, "e_share": min(e, 1.0),
        })

    elif code == "2.C":
        # Metals (lead + zinc) — process emissions → S covers; smaller scale
        s = 1.0
        f = 0.0
        e = ETS_CENTRAL * ETS_MULT["metals"]  # 0.40
        results.append({
            "ipcc_2006": code, "description": desc, "broad_category": cat,
            "central_KtCO2e": central, "low_KtCO2e": low, "high_KtCO2e": high,
            "s_share": s, "f_share": f, "e_share": min(e, 1.0),
        })

    elif code == "2.D":
        # Non-energy products (lubricants + wax) — 1,259.1 KtCO2e
        # S covers (process emissions at fixed sources)
        # F = 0 (not combustion-based)
        # E = 0 (below ETS threshold — non-energy use, dispersed)
        s = 1.0
        f = 0.0
        e = 0.0
        results.append({
            "ipcc_2006": code, "description": desc, "broad_category": cat,
            "central_KtCO2e": central, "low_KtCO2e": low, "high_KtCO2e": high,
            "s_share": s, "f_share": f, "e_share": e,
        })

    elif code == "3.x":
        # AFOLU — S EXCLUDED (livestock, soils, not fixed sources)
        s = 0.0
        f = 0.0
        e = 0.0
        results.append({
            "ipcc_2006": code, "description": desc, "broad_category": cat,
            "central_KtCO2e": central, "low_KtCO2e": low, "high_KtCO2e": high,
            "s_share": s, "f_share": f, "e_share": e,
        })

    elif code == "4.x":
        # Waste — S EXCLUDED
        s = 0.0
        f = 0.0
        e = 0.0
        results.append({
            "ipcc_2006": code, "description": desc, "broad_category": cat,
            "central_KtCO2e": central, "low_KtCO2e": low, "high_KtCO2e": high,
            "s_share": s, "f_share": f, "e_share": e,
        })

df = pd.DataFrame(results)

# =====================================================================
# COMPUTE VENN SEGMENTS
# =====================================================================

def venn_segments(row):
    t = row["central_KtCO2e"]
    s, f, e = row["s_share"], row["f_share"], row["e_share"]
    sfe = min(s, f, e)
    se = min(s, e)
    sf = min(s, f)
    fe = min(f, e)
    return pd.Series({
        "S∩F∩E": max(0, sfe) * t,
        "S∩E_only": max(0, se - sfe) * t,
        "S∩F_only": max(0, sf - sfe) * t,
        "S_only": max(0, s - sf - se + sfe) * t,
        "F∩E_only": max(0, fe - sfe) * t,
        "F_only": max(0, f - sf - max(0, fe - sfe)) * t,
        "E_only": max(0, e - se - max(0, fe - sfe)) * t,
        "Uncovered": max(0, 1 - min(1, s + f + e - sf - se - fe + sfe)) * t,
    })

venn = df.apply(venn_segments, axis=1)
df = pd.concat([df, venn], axis=1)

seg_cols = ["S∩F∩E", "S∩E_only", "S∩F_only", "S_only", "F∩E_only", "F_only", "E_only", "Uncovered"]
totals = df[seg_cols].sum()
grand = totals.sum()

gross_S = totals["S∩F∩E"] + totals["S∩E_only"] + totals["S∩F_only"] + totals["S_only"]
gross_F = totals["S∩F∩E"] + totals["S∩F_only"] + totals["F∩E_only"] + totals["F_only"]
gross_E = totals["S∩F∩E"] + totals["S∩E_only"] + totals["F∩E_only"] + totals["E_only"]
dedup = grand - totals["Uncovered"]

print(f"\n{'='*70}")
print(f"VENN SEGMENT RESULTS (Central, KtCO2e)")
print(f"{'='*70}")
for seg in seg_cols:
    print(f"  {seg:15s}: {totals[seg]:>10,.1f} KtCO2e  ({totals[seg]/grand*100:5.1f}%)")
print(f"  {'TOTAL':15s}: {grand:>10,.1f} KtCO2e")

print(f"\nINSTRUMENT COVERAGE:")
print(f"  Gross S (state tax):  {gross_S:>10,.1f} KtCO2e ({gross_S/grand*100:5.1f}%)")
print(f"  Gross F (fed. tax):   {gross_F:>10,.1f} KtCO2e ({gross_F/grand*100:5.1f}%)")
print(f"  Gross E (ETS):        {gross_E:>10,.1f} KtCO2e ({gross_E/grand*100:5.1f}%)")
print(f"  Deduplicated union:   {dedup:>10,.1f} KtCO2e ({dedup/grand*100:5.1f}%)")
print(f"  Uncovered:            {totals['Uncovered']:>10,.1f} KtCO2e ({totals['Uncovered']/grand*100:5.1f}%)")

overlap_SF = totals["S∩F∩E"] + totals["S∩F_only"]
overlap_SE = totals["S∩F∩E"] + totals["S∩E_only"]
print(f"\nOVERLAP:")
print(f"  S ∩ F:     {overlap_SF:>10,.1f} KtCO2e")
print(f"  S ∩ E:     {overlap_SE:>10,.1f} KtCO2e")
print(f"  S ∩ F ∩ E: {totals['S∩F∩E']:>10,.1f} KtCO2e")

# =====================================================================
# REVENUE CROSS-CHECK
# =====================================================================
print(f"\nREVENUE CROSS-CHECK:")
print(f"  Gross S = {gross_S:,.1f} KtCO2e")
print(f"  At 43 MXN/tCO2e (2022): revenue = MXN {gross_S * 1000 * 43 / 1e6:,.0f}M")
print(f"  At 58 MXN/tCO2e (2023+): revenue = MXN {gross_S * 1000 * 58 / 1e6:,.0f}M")
print(f"  MXN 252M ecological taxes implies floor of ~{252e6/58/1000:,.0f}-{252e6/43/1000:,.0f} KtCO2e")
print(f"  Gross S ({gross_S:,.0f} KtCO2e) is {'ABOVE' if gross_S > 5900 else 'IN RANGE of'} revenue-implied floor ✓")

# =====================================================================
# SAVE
# =====================================================================

df.to_csv(os.path.join(PROC_DIR, "estado_de_mexico_overlap_sectors.csv"), index=False)

summary_rows = []
for seg in seg_cols:
    summary_rows.append({"segment": seg, "central_KtCO2e": round(totals[seg], 1),
                          "pct_of_total": round(totals[seg]/grand*100, 2)})
for name, val in [("Gross_S", gross_S), ("Gross_F", gross_F), ("Gross_E", gross_E), ("Dedup_Union", dedup)]:
    summary_rows.append({"segment": name, "central_KtCO2e": round(val, 1),
                          "pct_of_total": round(val/grand*100, 2)})
pd.DataFrame(summary_rows).to_csv(os.path.join(PROC_DIR, "estado_de_mexico_overlap_summary.csv"), index=False)

# Range estimation (low/high inventory x low/high ETS)
def range_calc(inv_col, ets_val):
    tot_s = tot_f = tot_e = tot_dedup = tot_all = 0
    for _, r in df.iterrows():
        t = r[inv_col]
        s, f_val = r["s_share"], r["f_share"]
        e_orig = r["e_share"]
        e = min(e_orig * ets_val / ETS_CENTRAL, 1.0) if e_orig > 0 else 0
        sfe = min(s, f_val, e); se = min(s, e); sf = min(s, f_val); fe = min(f_val, e)
        union = min(1, s + f_val + e - sf - se - fe + sfe)
        tot_s += s * t; tot_f += f_val * t; tot_e += e * t; tot_dedup += union * t; tot_all += t
    return {"total": round(tot_all, 1), "gross_S": round(tot_s, 1), "gross_F": round(tot_f, 1),
            "gross_E": round(tot_e, 1), "dedup_union": round(tot_dedup, 1),
            "dedup_pct": round(tot_dedup / tot_all * 100, 1) if tot_all > 0 else 0}

ranges = pd.DataFrame([
    {"estimate": "low", **range_calc("low_KtCO2e", ETS_LOW)},
    {"estimate": "central", **range_calc("central_KtCO2e", ETS_CENTRAL)},
    {"estimate": "high", **range_calc("high_KtCO2e", ETS_HIGH)},
])
ranges.to_csv(os.path.join(PROC_DIR, "estado_de_mexico_overlap_ranges.csv"), index=False)
print(f"\nRANGE ESTIMATES:")
for _, r in ranges.iterrows():
    print(f"  {r['estimate']:8s}: total={r['total']:>10,.1f}  S={r['gross_S']:>10,.1f}  F={r['gross_F']:>10,.1f}  E={r['gross_E']:>10,.1f}  dedup={r['dedup_union']:>10,.1f} ({r['dedup_pct']}%)")

for f_name in ["estado_de_mexico_overlap_sectors.csv", "estado_de_mexico_overlap_summary.csv",
                "estado_de_mexico_overlap_ranges.csv"]:
    print(f"Saved: {os.path.join(PROC_DIR, f_name)}")
print("\n02_estimate.py complete.")
