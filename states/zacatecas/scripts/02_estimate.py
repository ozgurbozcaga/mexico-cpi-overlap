#!/usr/bin/env python3
"""
02_estimate.py — Zacatecas Three-Instrument CPI Overlap (EDGAR Gridded)
========================================================================
Uses EDGAR 2025 gridded sector emissions instead of proxy-based estimates.
Total state emissions: ~7,145 KtCO2e (Tier 3).

Instruments: S (state carbon tax) x F (federal IEPS) x E (pilot ETS)
S gas scope: CO2, CH4, N2O, HFC, PFC, SF6 (full Kyoto basket)
S source scope: all fixed sources (no threshold)
F: upstream fuel levy, all fossil fuels EXCEPT natural gas
E: facilities >= 25,000 tCO2e/yr direct CO2
"""

import pandas as pd
import numpy as np
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPT_DIR)
PROC_DIR = os.path.join(BASE_DIR, "data", "processed")

inv = pd.read_csv(os.path.join(PROC_DIR, "zacatecas_edgar_inventory.csv"))

print("=" * 70)
print("ZACATECAS CPI OVERLAP ESTIMATION — EDGAR Gridded (Tier 3)")
print("=" * 70)

# =====================================================================
# NATURAL GAS SHARE ASSUMPTIONS
# Source: ProAire 2018 — industrial combustion uses LPG + diesel, no NG listed
# =====================================================================
NG_SHARES = {
    "ENE": 0.60,        # National grid mix — CFE generation ~60% NG
    "REF_TRF": 0.40,    # Transformation/distribution — some NG
    "IND": 0.15,        # Very low NG in Zacatecas industry (ProAire confirms)
    "RCO_commercial": 0.30,
    "RCO_residential": 0.10,
    "RCO_agri": 0.05,
}

# ETS threshold coverage (share of fixed-source emissions from facilities >= 25,000 tCO2e/yr)
ETS_LOW, ETS_CENTRAL, ETS_HIGH = 0.30, 0.50, 0.70

# RCO split: residential vs commercial/institutional vs agricultural combustion
RCO_COMMERCIAL = 0.30
RCO_RESIDENTIAL = 0.50
RCO_AGRI = 0.20

# =====================================================================
# SECTOR-BY-SECTOR INSTRUMENT COVERAGE ASSIGNMENT
# =====================================================================

results = []
for _, row in inv.iterrows():
    code = row["edgar_sector"]
    central = row["central_KtCO2e"]
    low = row["low_KtCO2e"]
    high = row["high_KtCO2e"]

    s, f, e = 0.0, 0.0, 0.0

    if code == "ENE":
        # Power plants = fixed sources → S covers all
        # F covers non-NG combustion CO2
        # E covers above-threshold plants
        s = 1.0
        f = 1.0 - NG_SHARES["ENE"]  # 0.40
        e = ETS_CENTRAL * 0.8  # fewer large plants in Zacatecas

    elif code == "REF_TRF":
        # EDGAR allocates some transformation energy here even without a refinery
        # Treat as fixed-source energy industry → S covers
        s = 1.0
        f = 1.0 - NG_SHARES["REF_TRF"]  # 0.60
        e = ETS_CENTRAL * 0.5  # uncertain if above threshold

    elif code == "IND":
        # Manufacturing combustion at fixed installations → S covers all
        # F covers non-NG combustion → 85% (very low NG in Zacatecas)
        s = 1.0
        f = 1.0 - NG_SHARES["IND"]  # 0.85
        e = ETS_CENTRAL  # 0.50

    elif code in ("TRO", "TNR_Other"):
        # Mobile sources → S EXCLUDED
        s = 0.0
        f = 1.0  # All transport fuels are non-NG
        e = 0.0

    elif code.startswith("TNR_Aviation"):
        # Aviation — mobile → S excluded
        s = 0.0
        f = 1.0  # Jet fuel is not NG
        e = 0.0

    elif code == "TNR_Ship":
        # Zero for landlocked state
        pass

    elif code == "RCO":
        # Buildings: split into commercial (S-covered) + residential (S-excluded)
        s = RCO_COMMERCIAL + RCO_AGRI  # 0.50 — commercial + agri fixed sources
        f_weighted = (RCO_COMMERCIAL * (1 - NG_SHARES["RCO_commercial"]) +
                      RCO_RESIDENTIAL * (1 - NG_SHARES["RCO_residential"]) +
                      RCO_AGRI * (1 - NG_SHARES["RCO_agri"]))
        f = f_weighted  # ~0.86
        e = 0.0  # No buildings above 25,000 tCO2e

    elif code == "PRO_FFF":
        # Fugitive emissions — if from fixed installations, S covers
        # Zacatecas has minimal oil/gas → small and uncertain
        s = 0.5  # Partially fixed sources
        f = 0.0  # Not combustion-based
        e = 0.0

    elif code == "NMM":
        # Non-metallic minerals (cement/lime) — process emissions at fixed sources
        s = 1.0
        f = 0.0  # Process, not fuel-based
        e = 0.0  # Only 0.06 KtCO2e — well below threshold

    elif code == "CHE":
        # Chemical industry process emissions
        s = 1.0
        f = 0.0
        e = 0.0  # Small, below threshold

    elif code == "IRO":
        # Zero in Zacatecas
        pass

    elif code == "NFE":
        # Non-ferrous metals (silver/zinc smelting process emissions)
        s = 1.0
        f = 0.0  # Process emissions
        e = 0.0  # Only 1.2 KtCO2e — below threshold for process

    elif code == "NEU":
        # Non-energy use of fuels
        s = 1.0
        f = 0.0
        e = 0.0

    elif code == "PRU_SOL":
        # HFCs, solvents, other product use (2.D-2G)
        # S covers HFCs/PFCs/SF6 from fixed installations
        # But much of HFC leakage is from residential AC/refrigeration (not fixed)
        s = 0.40  # Only commercial/industrial fixed-source HFC leakage
        f = 0.0   # Not fuel-based
        e = 0.0

    elif code in ("ENF", "MNM", "AGS", "AWB", "N2O"):
        # AFOLU — S excluded (livestock, cropland, not fixed sources)
        s = 0.0
        f = 0.0
        e = 0.0

    elif code in ("SWD_LDF", "SWD_INC", "WWT"):
        # Waste — S excluded
        s = 0.0
        f = 0.0
        e = 0.0

    elif code == "IDE":
        # Indirect emissions — not directly covered by any instrument
        s = 0.0
        f = 0.0
        e = 0.0

    results.append({
        "edgar_sector": code,
        "description": row["description"],
        "broad_category": row["broad_category"],
        "central_KtCO2e": central,
        "low_KtCO2e": low,
        "high_KtCO2e": high,
        "s_share": round(s, 4),
        "f_share": round(f, 4),
        "e_share": round(min(e, 1.0), 4),
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
    print(f"  {seg:15s}: {totals[seg]:8.1f} KtCO2e  ({totals[seg]/grand*100:5.1f}%)")
print(f"  {'TOTAL':15s}: {grand:8.1f} KtCO2e")

print(f"\nINSTRUMENT COVERAGE:")
print(f"  Gross S (state tax):  {gross_S:8.1f} KtCO2e ({gross_S/grand*100:5.1f}%)")
print(f"  Gross F (fed. tax):   {gross_F:8.1f} KtCO2e ({gross_F/grand*100:5.1f}%)")
print(f"  Gross E (ETS):        {gross_E:8.1f} KtCO2e ({gross_E/grand*100:5.1f}%)")
print(f"  Deduplicated union:   {dedup:8.1f} KtCO2e ({dedup/grand*100:5.1f}%)")
print(f"  Uncovered:            {totals['Uncovered']:8.1f} KtCO2e ({totals['Uncovered']/grand*100:5.1f}%)")

overlap_SF = totals["S∩F∩E"] + totals["S∩F_only"]
overlap_SE = totals["S∩F∩E"] + totals["S∩E_only"]
print(f"\nOVERLAP:")
print(f"  S ∩ F:     {overlap_SF:8.1f} KtCO2e")
print(f"  S ∩ E:     {overlap_SE:8.1f} KtCO2e")
print(f"  S ∩ F ∩ E: {totals['S∩F∩E']:8.1f} KtCO2e")

# =====================================================================
# SAVE
# =====================================================================

df.to_csv(os.path.join(PROC_DIR, "zacatecas_overlap_sectors.csv"), index=False)

summary_rows = []
for seg in seg_cols:
    summary_rows.append({"segment": seg, "central_KtCO2e": round(totals[seg], 1),
                          "pct_of_total": round(totals[seg]/grand*100, 2)})
for name, val in [("Gross_S", gross_S), ("Gross_F", gross_F), ("Gross_E", gross_E), ("Dedup_Union", dedup)]:
    summary_rows.append({"segment": name, "central_KtCO2e": round(val, 1),
                          "pct_of_total": round(val/grand*100, 2)})
pd.DataFrame(summary_rows).to_csv(os.path.join(PROC_DIR, "zacatecas_overlap_summary.csv"), index=False)

# Range estimation (low/high inventory × low/high ETS)
def range_calc(inv_col, ets_val):
    tot_s = tot_f = tot_e = tot_dedup = tot_all = 0
    for _, r in df.iterrows():
        t = r[inv_col]
        s, f = r["s_share"], r["f_share"]
        e_orig = r["e_share"]
        e = min(e_orig * ets_val / ETS_CENTRAL, 1.0) if e_orig > 0 else 0
        sfe = min(s,f,e); se = min(s,e); sf = min(s,f); fe = min(f,e)
        union = min(1, s+f+e-sf-se-fe+sfe)
        tot_s += s*t; tot_f += f*t; tot_e += e*t; tot_dedup += union*t; tot_all += t
    return {"total": round(tot_all,1), "gross_S": round(tot_s,1), "gross_F": round(tot_f,1),
            "gross_E": round(tot_e,1), "dedup_union": round(tot_dedup,1),
            "dedup_pct": round(tot_dedup/tot_all*100,1) if tot_all>0 else 0}

ranges = pd.DataFrame([
    {"estimate": "low", **range_calc("low_KtCO2e", ETS_LOW)},
    {"estimate": "central", **range_calc("central_KtCO2e", ETS_CENTRAL)},
    {"estimate": "high", **range_calc("high_KtCO2e", ETS_HIGH)},
])
ranges.to_csv(os.path.join(PROC_DIR, "zacatecas_overlap_ranges.csv"), index=False)
print(f"\nRANGE ESTIMATES:")
for _, r in ranges.iterrows():
    print(f"  {r['estimate']:8s}: total={r['total']:,.1f}  S={r['gross_S']:,.1f}  F={r['gross_F']:,.1f}  E={r['gross_E']:,.1f}  dedup={r['dedup_union']:,.1f} ({r['dedup_pct']}%)")

for f in ["zacatecas_overlap_sectors.csv","zacatecas_overlap_summary.csv","zacatecas_overlap_ranges.csv"]:
    print(f"Saved: {os.path.join(PROC_DIR, f)}")
print("\n02_estimate.py complete.")
