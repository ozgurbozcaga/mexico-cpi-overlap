#!/usr/bin/env python3
"""
03_outputs.py — Estado de Mexico Publication Outputs
"""

import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPT_DIR)
PROC_DIR = os.path.join(BASE_DIR, "data", "processed")
FIG_DIR = os.path.join(BASE_DIR, "outputs", "figures")
TAB_DIR = os.path.join(BASE_DIR, "outputs", "tables")
os.makedirs(FIG_DIR, exist_ok=True)
os.makedirs(TAB_DIR, exist_ok=True)

overlap = pd.read_csv(os.path.join(PROC_DIR, "estado_de_mexico_overlap_summary.csv"))
ranges = pd.read_csv(os.path.join(PROC_DIR, "estado_de_mexico_overlap_ranges.csv"))
sectors = pd.read_csv(os.path.join(PROC_DIR, "estado_de_mexico_overlap_sectors.csv"))
inventory = pd.read_csv(os.path.join(PROC_DIR, "estado_de_mexico_inventory.csv"))

# =====================================================================
# FIGURE 1: Venn Segments Bar Chart
# =====================================================================
seg_cols = ["S∩F∩E", "S∩E_only", "S∩F_only", "S_only", "F∩E_only", "F_only", "E_only", "Uncovered"]
seg_labels = ["S∩F∩E", "S∩E\nonly", "S∩F\nonly", "S\nonly", "F∩E\nonly", "F\nonly", "E\nonly", "Un-\ncovered"]
seg_data = overlap[overlap["segment"].isin(seg_cols)].set_index("segment").loc[seg_cols]
colors = ["#2C3E50", "#3498DB", "#E67E22", "#27AE60", "#9B59B6", "#E74C3C", "#1ABC9C", "#BDC3C7"]

fig, ax = plt.subplots(figsize=(10, 5))
bars = ax.bar(range(len(seg_cols)), seg_data["central_KtCO2e"].values, color=colors, edgecolor="white")
ax.set_xticks(range(len(seg_cols)))
ax.set_xticklabels(seg_labels, fontsize=9)
ax.set_ylabel("KtCO₂e", fontsize=11)
ax.set_title("Estado de México — Three-Instrument Overlap Segments\n(IEEGyCEI-2022, Central Estimate)", fontsize=12, fontweight="bold")
for bar, val in zip(bars, seg_data["central_KtCO2e"].values):
    if val > 50:
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(seg_data["central_KtCO2e"].values)*0.02,
                f"{val:,.0f}", ha="center", va="bottom", fontsize=8)
ax.set_ylim(0, ax.get_ylim()[1] * 1.15)
ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
plt.tight_layout()
fig.savefig(os.path.join(FIG_DIR, "estado_de_mexico_venn_segments.png"), dpi=200, bbox_inches="tight")
plt.close()

# =====================================================================
# FIGURE 2: Instrument Coverage with Ranges
# =====================================================================
fig, ax = plt.subplots(figsize=(8, 5))
inst_names = ["Gross S\n(State Tax)", "Gross F\n(Fed. Tax)", "Gross E\n(ETS)", "Dedup\nUnion"]
c_vals = [ranges.loc[1, "gross_S"], ranges.loc[1, "gross_F"], ranges.loc[1, "gross_E"], ranges.loc[1, "dedup_union"]]
l_vals = [ranges.loc[0, "gross_S"], ranges.loc[0, "gross_F"], ranges.loc[0, "gross_E"], ranges.loc[0, "dedup_union"]]
h_vals = [ranges.loc[2, "gross_S"], ranges.loc[2, "gross_F"], ranges.loc[2, "gross_E"], ranges.loc[2, "dedup_union"]]
errs = [[c - l for c, l in zip(c_vals, l_vals)], [h - c for c, h in zip(c_vals, h_vals)]]
inst_colors = ["#27AE60", "#E74C3C", "#3498DB", "#2C3E50"]
bars = ax.bar(inst_names, c_vals, color=inst_colors, edgecolor="white")
ax.errorbar(inst_names, c_vals, yerr=errs, fmt="none", ecolor="black", capsize=5, linewidth=1.5)
for bar, val, err_h in zip(bars, c_vals, errs[1]):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + err_h + max(c_vals)*0.01,
            f"{val:,.0f}", ha="center", va="bottom", fontsize=9, fontweight="bold")
ax.set_ylabel("KtCO₂e", fontsize=11)
ax.set_title("Estado de México — Instrument Coverage\n(IEEGyCEI-2022, Central ± Range)", fontsize=12, fontweight="bold")
ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
plt.tight_layout()
fig.savefig(os.path.join(FIG_DIR, "estado_de_mexico_instrument_coverage.png"), dpi=200, bbox_inches="tight")
plt.close()

# =====================================================================
# FIGURE 3: Inventory Breakdown Pie Chart
# =====================================================================
cat_totals = inventory.groupby("broad_category")["central_KtCO2e"].sum().sort_values(ascending=False)
cat_totals = cat_totals[cat_totals > 10]
cat_colors = {
    "TRANSPORT": "#E74C3C", "MANUFACTURING": "#E67E22", "WASTE": "#8E44AD",
    "ELECTRICITY": "#F39C12", "IPPU": "#3498DB", "AFOLU": "#27AE60",
    "OTHER_SECTORS": "#1ABC9C", "FUGITIVE": "#7F8C8D",
}
colors_pie = [cat_colors.get(c, "#BDC3C7") for c in cat_totals.index]
grand_total = inventory["central_KtCO2e"].sum()

fig, ax = plt.subplots(figsize=(8, 7))
wedges, texts, autotexts = ax.pie(
    cat_totals.values,
    labels=[c.replace("_", "\n") for c in cat_totals.index],
    autopct="%1.1f%%", colors=colors_pie, textprops={"fontsize": 9},
    pctdistance=0.82, startangle=90
)
for t in autotexts:
    t.set_fontsize(8)
ax.set_title(f"Estado de México — GHG Emissions by Sector\n(IEEGyCEI-2022, {grand_total:,.0f} KtCO₂e)",
             fontsize=12, fontweight="bold")
plt.tight_layout()
fig.savefig(os.path.join(FIG_DIR, "estado_de_mexico_inventory_breakdown.png"), dpi=200, bbox_inches="tight")
plt.close()

# =====================================================================
# TABLES
# =====================================================================
overlap.to_csv(os.path.join(TAB_DIR, "estado_de_mexico_overlap_table.csv"), index=False)
ranges.to_csv(os.path.join(TAB_DIR, "estado_de_mexico_range_table.csv"), index=False)
sectors[["ipcc_2006", "description", "central_KtCO2e", "s_share", "f_share", "e_share"] + seg_cols].round(1).to_csv(
    os.path.join(TAB_DIR, "estado_de_mexico_sector_detail.csv"), index=False)

for d in [FIG_DIR, TAB_DIR]:
    for f in os.listdir(d):
        print(f"Saved: {os.path.join(d, f)}")
print("\n03_outputs.py complete.")
