"""
03_outputs.py — Tamaulipas Carbon Pricing Overlap Analysis
============================================================
Produces publication-quality figures and summary tables.

Outputs:
    outputs/figures/tamaulipas_venn_segments_2025.png
    outputs/figures/tamaulipas_coverage_summary_2025.png
    outputs/tables/tamaulipas_overlap_summary.csv
    outputs/tables/tamaulipas_overlap_full_table.csv
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import os, warnings
warnings.filterwarnings("ignore")

# ── Paths ────────────────────────────────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR   = os.path.dirname(SCRIPT_DIR)
PROC_DIR   = os.path.join(BASE_DIR, "data", "processed")
FIG_DIR    = os.path.join(BASE_DIR, "outputs", "figures")
TBL_DIR    = os.path.join(BASE_DIR, "outputs", "tables")
os.makedirs(FIG_DIR, exist_ok=True)
os.makedirs(TBL_DIR, exist_ok=True)

# ── Style ────────────────────────────────────────────────────────────────────
plt.rcParams.update({
    "font.family":    "sans-serif",
    "font.size":      9,
    "axes.titlesize": 11,
    "axes.titleweight": "bold",
    "axes.spines.top": False,
    "axes.spines.right": False,
    "figure.dpi":     150,
})

WB_BLUE  = "#00538C"
WB_RED   = "#BE0000"
WB_TEAL  = "#00A9A5"
WB_GOLD  = "#E7A720"
WB_GREY  = "#6D6E71"
WB_LGREY = "#E8E8E8"

SEG_COLS = {
    "S∩F∩E":    "#6B3FA0",
    "S∩E only": "#00538C",
    "S∩F only": "#00A9A5",
    "S only":   "#7EB8D4",
    "F only":   "#E7A720",
    "Uncovered":"#D9D9D9",
}

# ── Load data ────────────────────────────────────────────────────────────────
overlap = pd.read_csv(os.path.join(PROC_DIR, "tamaulipas_overlap_estimates.csv"))

def get_scen(scen):
    return overlap[overlap["scenario"] == scen].iloc[0]

c = get_scen("central")
l = get_scen("low")
h = get_scen("high")

print("=" * 72)
print("Tamaulipas 03_outputs.py — generating figures and tables")
print("=" * 72)

# ── Figure 1: Venn segment bar chart ─────────────────────────────────────────
fig, ax = plt.subplots(figsize=(10, 6))
fig.suptitle(
    "Tamaulipas: Carbon Pricing Coverage Decomposition (2025)\n"
    "State Carbon Tax (≥25k tCO₂e) × Federal IEPS × Mexico Pilot ETS",
    fontsize=11, fontweight="bold", y=1.01
)

SEG_LABELS = ["S∩F∩E", "S∩E only", "S∩F only", "S only", "F only", "Uncovered"]
SEG_KEYS   = ["S_F_E_GgCO2e", "S_E_only_GgCO2e", "S_F_only_GgCO2e",
              "S_only_GgCO2e", "F_only_GgCO2e", "uncovered_GgCO2e"]

vals   = [c[k] for k in SEG_KEYS]
vals_l = [l[k] for k in SEG_KEYS]
vals_h = [h[k] for k in SEG_KEYS]
colours = [SEG_COLS[s] for s in SEG_LABELS]

bars = ax.bar(SEG_LABELS, vals, color=colours, width=0.55,
              edgecolor="white", linewidth=0.5)

# Uncertainty whiskers
for i, (v, vl, vh) in enumerate(zip(vals, vals_l, vals_h)):
    lo = max(0, v - vl)
    hi = max(0, vh - v)
    ax.errorbar(i, v, yerr=[[lo], [hi]], fmt="none",
                capsize=4, color="#444", linewidth=1.0, capthick=1.0)

# Value labels
for bar, v in zip(bars, vals):
    if v > 100:
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 200,
                f"{v:,.0f}", ha="center", va="bottom", fontsize=8, fontweight="bold")

# State total line
total = c["state_total_GgCO2e"]
ax.axhline(total, color=WB_GREY, linestyle="--", linewidth=0.8, alpha=0.7)
ax.text(5.5, total + 300, f"State total\n{total:,.0f}", fontsize=7, color=WB_GREY, ha="right")

ax.set_ylabel("GgCO₂e (AR5 GWPs)")
ax.set_ylim(0, total * 1.15)
ax.tick_params(axis="x", rotation=20, labelsize=8)

# Key metrics box
metrics = (
    f"S={c['S_pct']:.1f}% | F={c['F_pct']:.1f}% | E={c['E_pct']:.1f}%\n"
    f"Union={c['union_pct']:.1f}% | Tier 3 estimate\n"
    f"S threshold: ≥25,000 tCO₂e/yr (~36 companies)"
)
ax.text(0.01, 0.97, metrics, transform=ax.transAxes,
        fontsize=7.5, va="top", ha="left",
        bbox=dict(boxstyle="round,pad=0.3", facecolor="#FFF8E1",
                  edgecolor=WB_GOLD, alpha=0.9))

fig.text(0.5, -0.04,
    "Tier 3: dual 25k tCO₂e/yr threshold for S and E. "
    "SAR→AR5 GWP conversion applied (CH₄=28, N₂O=265). "
    "BaU 2025 projection from PECC Tamaulipas Table III.\n"
    "Ranges from low/high threshold fractions and ±8% growth uncertainty.",
    ha="center", fontsize=7, style="italic", color=WB_GREY)

fig.tight_layout()
out1 = os.path.join(FIG_DIR, "tamaulipas_venn_segments_2025.png")
fig.savefig(out1, dpi=150, bbox_inches="tight")
plt.close()
print(f"Saved: {out1}")

# ── Figure 2: Instrument coverage comparison ─────────────────────────────────
fig2, ax2 = plt.subplots(figsize=(10, 5.5))
fig2.suptitle(
    "Tamaulipas: Carbon Pricing Instrument Coverage (2025)\n"
    "State Tax vs Federal IEPS vs Pilot ETS",
    fontsize=11, fontweight="bold"
)

INSTRUMENTS = ["S (State tax\n≥25k)", "F (Federal\nIEPS)", "E (Pilot\nETS)", "Union\nS∪F∪E"]
INST_KEYS   = ["S_gross_GgCO2e", "F_gross_GgCO2e", "E_gross_GgCO2e", "union_GgCO2e"]
INST_COLS   = [WB_BLUE, WB_GOLD, WB_RED, WB_TEAL]

vals_c = [c[k] for k in INST_KEYS]
vals_l = [l[k] for k in INST_KEYS]
vals_h = [h[k] for k in INST_KEYS]

bars2 = ax2.bar(INSTRUMENTS, vals_c, color=INST_COLS, width=0.45,
                edgecolor="white", linewidth=0.5, alpha=0.88)

# Whiskers
for i, (vc, vl, vh) in enumerate(zip(vals_c, vals_l, vals_h)):
    lo = max(0, vc - vl)
    hi = max(0, vh - vc)
    ax2.errorbar(i, vc, yerr=[[lo], [hi]], fmt="none",
                 capsize=4, color="#333", linewidth=0.8)

# Labels with percentage
PCT_KEYS = ["S_pct", "F_pct", "E_pct", "union_pct"]
for bar, v, pct_key in zip(bars2, vals_c, PCT_KEYS):
    pct = c[pct_key]
    ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 200,
             f"{v:,.0f}\n({pct:.1f}%)", ha="center", va="bottom",
             fontsize=8, fontweight="bold")

# State total line
ax2.axhline(total, color=WB_GREY, linestyle="--", linewidth=0.8)
ax2.text(3.5, total + 300, f"State total: {total:,.0f}", fontsize=7, color=WB_GREY, ha="right")

ax2.set_ylabel("GgCO₂e")
ax2.set_ylim(0, total * 1.15)

# Analytical note
note = (
    "Key: Tamaulipas S has ≥25k tCO₂e/yr threshold (unique among states).\n"
    "S ≈ E because both use same threshold; difference is sector scope.\n"
    "S∩E dominant: NG at large plants (not taxed by F).\n"
    "F covers transport + below-threshold non-NG combustion.\n"
    "~36 companies covered by state tax."
)
ax2.text(0.01, 0.98, note, transform=ax2.transAxes,
         fontsize=7, va="top", ha="left",
         bbox=dict(boxstyle="round,pad=0.4", facecolor="#E8F4FD",
                   edgecolor=WB_BLUE, alpha=0.9))

fig2.text(0.5, -0.03,
    "Source: PECC Tamaulipas 2015-2030 (2013 inventory, BaU 2025). "
    "GWPs: AR5 (CH₄=28, N₂O=265). Estimation tier: Tier 3.",
    ha="center", fontsize=7, style="italic", color=WB_GREY)

fig2.tight_layout()
out2 = os.path.join(FIG_DIR, "tamaulipas_coverage_summary_2025.png")
fig2.savefig(out2, dpi=150, bbox_inches="tight")
plt.close()
print(f"Saved: {out2}")

# ── Table 1: Summary overlap table ──────────────────────────────────────────
cols_summary = [
    "year", "scenario",
    "S_gross_GgCO2e", "S_pct",
    "F_gross_GgCO2e", "F_pct",
    "E_gross_GgCO2e", "E_pct",
    "S_F_E_GgCO2e", "S_F_E_pct",
    "S_E_only_GgCO2e", "S_E_only_pct",
    "S_F_only_GgCO2e", "S_F_only_pct",
    "S_only_GgCO2e", "S_only_pct",
    "F_only_GgCO2e", "F_only_pct",
    "union_GgCO2e", "union_pct",
    "uncovered_GgCO2e", "uncovered_pct",
    "estimation_tier",
]
summary_tbl = overlap[cols_summary].copy()
summary_tbl.to_csv(os.path.join(TBL_DIR, "tamaulipas_overlap_summary.csv"), index=False)
print(f"Saved: outputs/tables/tamaulipas_overlap_summary.csv")

# ── Table 2: Full publication table ──────────────────────────────────────────
SEGS_PUB = [
    ("S∩F∩E — all three instruments", "S_F_E_GgCO2e", "S_F_E_pct",
     "Non-NG combustion at above-threshold plants: electricity (diesel/FO fraction), "
     "refinery (non-NG fraction), manufacturing (diesel/GLP at large plants)"),
    ("S∩E only — state tax + ETS", "S_E_only_GgCO2e", "S_E_only_pct",
     "NG combustion at above-threshold plants (NG exempt from F); "
     "fugitive O&G (CH4 from PEMEX installations); IPPU process CO2 (caliza, negro de humo)"),
    ("S∩F only — state tax + federal", "S_F_only_GgCO2e", "S_F_only_pct",
     "Near zero: S and E have same threshold, so S∩F-only requires S but not E sector scope — "
     "only applies to HFC (NE data gap)"),
    ("S only — state tax unique", "S_only_GgCO2e", "S_only_pct",
     "Near zero: same reasoning as S∩F only — HFC NG fraction (NE)"),
    ("F only — federal tax unique", "F_only_GgCO2e", "F_only_pct",
     "Transport (road, rail, aviation, maritime); below-threshold non-NG combustion; "
     "agricultural combustion diesel/GLP"),
    ("Uncovered", "uncovered_GgCO2e", "uncovered_pct",
     "AFOLU (livestock CH4, land use CO2, cropland N2O); waste; residential/commercial NG; "
     "below-threshold NG combustion; HFC data gap"),
]

rows_pub = []
for scen in ["central", "low", "high"]:
    row_data = get_scen(scen)
    for seg_name, key, pct_key, content in SEGS_PUB:
        rows_pub.append(dict(
            year=2025, scenario=scen,
            segment=seg_name,
            GgCO2e=round(row_data[key], 1),
            pct_of_state=round(row_data[pct_key], 2),
            content_description=content,
            estimation_tier="Tier 3",
        ))
    for inst, key, pct_key in [
        ("S gross (state tax ≥25k)", "S_gross_GgCO2e", "S_pct"),
        ("F gross (federal IEPS)",   "F_gross_GgCO2e", "F_pct"),
        ("E gross (pilot ETS ≥25k)", "E_gross_GgCO2e", "E_pct"),
        ("S∪F∪E union",              "union_GgCO2e",   "union_pct"),
    ]:
        rows_pub.append(dict(
            year=2025, scenario=scen,
            segment=inst,
            GgCO2e=round(row_data[key], 1),
            pct_of_state=round(row_data[pct_key], 2),
            content_description="",
            estimation_tier="Tier 3",
        ))

full_tbl = pd.DataFrame(rows_pub)
full_tbl.to_csv(os.path.join(TBL_DIR, "tamaulipas_overlap_full_table.csv"), index=False)
print(f"Saved: outputs/tables/tamaulipas_overlap_full_table.csv")

# ── Console summary ──────────────────────────────────────────────────────────
print(f"\n{'='*72}")
print(f"TAMAULIPAS — FINAL PUBLICATION SUMMARY (2025 CENTRAL)")
print(f"{'='*72}")
print(f"  State total:       {c['state_total_GgCO2e']:>10,.0f} GgCO2e")
print(f"  S (state tax≥25k): {c['S_gross_GgCO2e']:>10,.0f}  ({c['S_pct']:.1f}%)  "
      f"[{l['S_gross_GgCO2e']:,.0f}–{h['S_gross_GgCO2e']:,.0f}]")
print(f"  F (federal IEPS):  {c['F_gross_GgCO2e']:>10,.0f}  ({c['F_pct']:.1f}%)  "
      f"[{l['F_gross_GgCO2e']:,.0f}–{h['F_gross_GgCO2e']:,.0f}]")
print(f"  E (pilot ETS):     {c['E_gross_GgCO2e']:>10,.0f}  ({c['E_pct']:.1f}%)  "
      f"[{l['E_gross_GgCO2e']:,.0f}–{h['E_gross_GgCO2e']:,.0f}]")
print(f"  S∩F∩E:             {c['S_F_E_GgCO2e']:>10,.0f}  ({c['S_F_E_pct']:.1f}%)")
print(f"  S∩E only:          {c['S_E_only_GgCO2e']:>10,.0f}  ({c['S_E_only_pct']:.1f}%)  <- NG at large plants")
print(f"  S∩F only:          {c['S_F_only_GgCO2e']:>10,.0f}  ({c['S_F_only_pct']:.1f}%)")
print(f"  S only:            {c['S_only_GgCO2e']:>10,.0f}  ({c['S_only_pct']:.1f}%)")
print(f"  F only:            {c['F_only_GgCO2e']:>10,.0f}  ({c['F_only_pct']:.1f}%)  <- transport + below-threshold")
print(f"  Union S∪F∪E:       {c['union_GgCO2e']:>10,.0f}  ({c['union_pct']:.1f}%)")
print(f"  Uncovered:         {c['uncovered_GgCO2e']:>10,.0f}  ({c['uncovered_pct']:.1f}%)")
print(f"\n  Key structural findings:")
print(f"  1. S coverage narrowest of all states analysed (~{c['S_pct']:.0f}%)")
print(f"     due to 25k tCO2e/yr legal threshold (same as ETS)")
print(f"  2. S ≈ E in scope — same threshold drives near-identical coverage")
print(f"     Dominant segment: S∩E (NG at large plants, {c['S_E_only_pct']:.1f}% of state)")
print(f"  3. Minimal S∩F∩E overlap — NG dominance means little non-NG at large plants")
print(f"  4. F captures unique emissions: transport + below-threshold non-NG")
print(f"  5. Large uncovered block: AFOLU + waste + below-threshold NG + HFC data gap")
print(f"\n✓ 03_outputs.py complete\n")
