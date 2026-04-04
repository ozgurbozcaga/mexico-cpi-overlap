"""
03_outputs.py — Queretaro Carbon Pricing Overlap Analysis
==========================================================
Produces publication-quality figures and summary tables.

Outputs:
    outputs/figures/queretaro_venn_segments_2025_2026.png
    outputs/figures/queretaro_coverage_summary_2025_2026.png
    outputs/tables/queretaro_overlap_summary.csv
    outputs/tables/queretaro_overlap_full_table.csv
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import os, warnings
warnings.filterwarnings("ignore")

# -- Paths -------------------------------------------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR   = os.path.dirname(SCRIPT_DIR)
PROC_DIR   = os.path.join(BASE_DIR, "data", "processed")
FIG_DIR    = os.path.join(BASE_DIR, "outputs", "figures")
TBL_DIR    = os.path.join(BASE_DIR, "outputs", "tables")
os.makedirs(FIG_DIR, exist_ok=True)
os.makedirs(TBL_DIR, exist_ok=True)

# -- Style -------------------------------------------------------------------
plt.rcParams.update({
    "font.family":      "sans-serif",
    "font.size":        9,
    "axes.titlesize":   11,
    "axes.titleweight": "bold",
    "axes.spines.top":  False,
    "axes.spines.right":False,
    "figure.dpi":       150,
})

WB_BLUE  = "#00538C"
WB_RED   = "#BE0000"
WB_TEAL  = "#00A9A5"
WB_GOLD  = "#E7A720"
WB_GREY  = "#6D6E71"

SEG_COLS = {
    "S^F^E":    "#6B3FA0",
    "S^E only": "#00538C",
    "S^F only": "#00A9A5",
    "S only":   "#7EB8D4",
    "F only":   "#E7A720",
    "Uncovered":"#D9D9D9",
}

# -- Load data ---------------------------------------------------------------
overlap  = pd.read_csv(os.path.join(PROC_DIR, "queretaro_overlap_estimates.csv"))
scope_df = pd.read_csv(os.path.join(PROC_DIR, "queretaro_tax_scope_2021.csv"))

def get_yr_scen(yr, scen):
    return overlap[(overlap["year"] == yr) & (overlap["scenario"] == scen)].iloc[0]


# -- Figure 1: Venn segment bar chart ----------------------------------------
fig, axes = plt.subplots(1, 2, figsize=(12, 6), sharey=True)
fig.suptitle(
    "Queretaro State Carbon Tax x Federal Carbon Tax x Mexico Pilot ETS\n"
    "Emission Coverage Decomposition (GgCO2e, Tier 3 estimate)",
    fontsize=11, fontweight="bold", y=1.01
)

SEG_LABELS = ["S^F^E", "S^E only", "S^F only", "S only", "F only", "Uncovered"]
SEG_KEYS   = ["S_F_E_GgCO2e", "S_E_only_GgCO2e", "S_F_only_GgCO2e",
               "S_only_GgCO2e", "F_only_GgCO2e", "uncovered_GgCO2e"]

for ax, yr in zip(axes, [2025, 2026]):
    c = get_yr_scen(yr, "central")
    l = get_yr_scen(yr, "low")
    h = get_yr_scen(yr, "high")

    vals    = [c[k] for k in SEG_KEYS]
    vals_l  = [l[k] for k in SEG_KEYS]
    vals_h  = [h[k] for k in SEG_KEYS]
    colours = [SEG_COLS[s] for s in SEG_LABELS]

    bars = ax.bar(SEG_LABELS, vals, color=colours, width=0.55,
                  edgecolor="white", linewidth=0.5)

    for i, (v, vl, vh) in enumerate(zip(vals, vals_l, vals_h)):
        lo = max(0, v - vl)
        hi = max(0, vh - v)
        ax.errorbar(i, v, yerr=[[lo], [hi]], fmt="none",
                    capsize=4, color="#444", linewidth=1.0, capthick=1.0)

    for bar, v in zip(bars, vals):
        if v > 30:
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 30,
                    f"{v:.0f}", ha="center", va="bottom", fontsize=7.5, fontweight="bold")

    total = c["state_total_GgCO2e"]
    ax.axhline(total, color=WB_GREY, linestyle="--", linewidth=0.8, alpha=0.7)
    ax.text(5.5, total + 50, f"State total\n{total:.0f}", fontsize=7, color=WB_GREY, ha="right")

    ax.set_title(f"{yr}", fontsize=12)
    ax.set_ylabel("GgCO2e" if yr == 2025 else "")
    ax.set_ylim(0, 12500)
    ax.tick_params(axis="x", rotation=30, labelsize=7.5)

    union_pct = c["union_pct"]
    S_pct     = c["S_pct"]
    F_pct     = c["F_pct"]
    E_pct     = c["E_pct"]
    metrics = (f"S={S_pct:.1f}% | F={F_pct:.1f}% | E={E_pct:.1f}%\n"
               f"Union={union_pct:.1f}% | Tier 3 estimate")
    ax.text(0.01, 0.97, metrics, transform=ax.transAxes,
            fontsize=7, va="top", ha="left",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="#FFF8E1",
                      edgecolor=WB_GOLD, alpha=0.9))

fig.text(0.5, -0.04,
    "Tier 3 estimation: ETS threshold via Pareto; Federal tax excludes NG (~100% of electricity CO2).\n"
    "Base year 2021 (IEGYCEI Queretaro, SEDESU). All Kyoto gases in state tax scope.\n"
    "Ranges from low/high growth scenarios and fuel fraction uncertainty.",
    ha="center", fontsize=7, style="italic", color=WB_GREY)

fig.tight_layout()
out1 = os.path.join(FIG_DIR, "queretaro_venn_segments_2025_2026.png")
fig.savefig(out1, dpi=150, bbox_inches="tight")
plt.close()
print(f"Saved: {out1}")


# -- Figure 2: Coverage summary ---------------------------------------------
fig2, ax2 = plt.subplots(figsize=(10, 5.5))
fig2.suptitle(
    "Queretaro Carbon Pricing Coverage Summary\n"
    "Three Instruments, 2021-2026 (GgCO2e)",
    fontsize=11, fontweight="bold"
)

YEARS       = [2021, 2025, 2026]
INSTRUMENTS = ["S (State tax)", "F (Federal IEPS)", "E (Pilot ETS)", "Union S|F|E"]
INST_KEYS   = ["S_gross_GgCO2e", "F_gross_GgCO2e", "E_gross_GgCO2e", "union_GgCO2e"]
INST_COLS   = [WB_BLUE, WB_GOLD, WB_RED, WB_TEAL]

bar_width = 0.18
x = np.arange(len(YEARS))

for i, (inst, key, col) in enumerate(zip(INSTRUMENTS, INST_KEYS, INST_COLS)):
    centrals = [get_yr_scen(yr, "central")[key] for yr in YEARS]
    lows     = [get_yr_scen(yr, "low")[key]     for yr in YEARS]
    highs    = [get_yr_scen(yr, "high")[key]    for yr in YEARS]
    errs_lo  = [c - lo for c, lo in zip(centrals, lows)]
    errs_hi  = [hi - c for c, hi in zip(centrals, highs)]

    bars = ax2.bar(x + i * bar_width - 1.5 * bar_width, centrals,
                   bar_width, label=inst, color=col, alpha=0.88,
                   edgecolor="white", linewidth=0.4)
    ax2.errorbar(x + i * bar_width - 1.5 * bar_width, centrals,
                 yerr=[errs_lo, errs_hi], fmt="none",
                 capsize=3, color="#333", linewidth=0.8)
    for bar, v in zip(bars, centrals):
        ax2.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 35,
                 f"{v/1000:.1f}k", ha="center", va="bottom", fontsize=7,
                 color=col, fontweight="bold")

totals = [get_yr_scen(yr, "central")["state_total_GgCO2e"] for yr in YEARS]
ax2.plot(x, totals, "D--", color=WB_GREY, markersize=5, linewidth=1.0,
         label="State total gross emissions", zorder=5)
for xi, t in zip(x, totals):
    ax2.text(xi + 0.03, t + 100, f"{t:.0f}", fontsize=7, color=WB_GREY, ha="left")

ax2.set_xticks(x)
ax2.set_xticklabels([str(y) for y in YEARS])
ax2.set_ylabel("GgCO2e")
ax2.set_ylim(0, 14000)
ax2.legend(loc="upper right", fontsize=7.5, framealpha=0.9)
ax2.set_xlabel("Year")

note = (
    "Key finding: Queretaro state tax covers ~41% of state emissions.\n"
    "Tax scope is broad: all Kyoto gases, economy-wide fixed sources.\n"
    "Federal tax limited: NG=~100% of elec CO2 and ~95.5% of manuf CO2.\n"
    "Transport (~23.6%) is F only. Residential (~3.6%) exempt from S."
)
ax2.text(0.01, 0.98, note, transform=ax2.transAxes,
         fontsize=7, va="top", ha="left",
         bbox=dict(boxstyle="round,pad=0.4", facecolor="#E8F4FD",
                   edgecolor=WB_BLUE, alpha=0.9))

fig2.text(0.5, -0.03,
    "Source: IEGYCEI Queretaro 2021 (SEDESU). Tier 3 (ETS threshold + fuel fractions). "
    "GWPs: AR5 (CH4=28, N2O=265).",
    ha="center", fontsize=7, style="italic", color=WB_GREY)

fig2.tight_layout()
out2 = os.path.join(FIG_DIR, "queretaro_coverage_summary_2025_2026.png")
fig2.savefig(out2, dpi=150, bbox_inches="tight")
plt.close()
print(f"Saved: {out2}")


# -- Table 1: Summary overlap table -----------------------------------------
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
summary_tbl.to_csv(os.path.join(TBL_DIR, "queretaro_overlap_summary.csv"), index=False)
print(f"Saved: outputs/tables/queretaro_overlap_summary.csv")


# -- Table 2: Full table for publication -------------------------------------
rows_pub = []
SEGS_PUB = [
    ("S^F^E -- all three instruments", "S_F_E_GgCO2e", "S_F_E_pct",
     "Manuf non-NG fuels at large plants; negligible electricity diesel at large plants"),
    ("S^E only -- state tax + ETS", "S_E_only_GgCO2e", "S_E_only_pct",
     "Electricity NG (99.99%) at large plants (El Sauz, SJR); manufacturing NG at large plants"),
    ("S^F only -- state tax + federal", "S_F_only_GgCO2e", "S_F_only_pct",
     "Manuf non-NG at small plants; commercial non-NG fuels; ag combustion non-NG"),
    ("S only -- state tax unique", "S_only_GgCO2e", "S_only_pct",
     "NG at small manuf; commercial NG; HFC refrigeration (70.5 GgCO2e); IPPU process CO2 non-ETS"),
    ("F only -- federal tax unique", "F_only_GgCO2e", "F_only_pct",
     "Transport non-NG fuels (~98.6%); residential non-NG fuels (~95%)"),
    ("Uncovered", "uncovered_GgCO2e", "uncovered_pct",
     "AFOLU (livestock, land sources); waste; transport NG; residential NG"),
]

for yr in [2021, 2025, 2026]:
    for scen in ["central", "low", "high"]:
        row_data = get_yr_scen(yr, scen)
        for seg_name, key, pct_key, content in SEGS_PUB:
            rows_pub.append(dict(
                year=yr, scenario=scen,
                segment=seg_name,
                GgCO2e=round(row_data[key], 1),
                pct_of_state=round(row_data[pct_key], 2),
                content_description=content,
                estimation_tier="Tier 3",
            ))
        for inst, key, pct_key in [
            ("S gross (state tax)",        "S_gross_GgCO2e", "S_pct"),
            ("F gross (federal tax)",      "F_gross_GgCO2e", "F_pct"),
            ("E gross (pilot ETS)",        "E_gross_GgCO2e", "E_pct"),
            ("S|F|E deduplicated union",   "union_GgCO2e",   "union_pct"),
        ]:
            rows_pub.append(dict(
                year=yr, scenario=scen,
                segment=inst,
                GgCO2e=round(row_data[key], 1),
                pct_of_state=round(row_data[pct_key], 2),
                content_description="",
                estimation_tier="Tier 3",
            ))

full_tbl = pd.DataFrame(rows_pub)
full_tbl.to_csv(os.path.join(TBL_DIR, "queretaro_overlap_full_table.csv"), index=False)
print(f"Saved: outputs/tables/queretaro_overlap_full_table.csv")


# -- Console summary --------------------------------------------------------
print("\n" + "=" * 65)
print("QUERETARO -- FINAL PUBLICATION SUMMARY (2025 CENTRAL)")
print("=" * 65)
yr25c = get_yr_scen(2025, "central")
yr25l = get_yr_scen(2025, "low")
yr25h = get_yr_scen(2025, "high")

print(f"  State total:       {yr25c['state_total_GgCO2e']:,.0f} GgCO2e")
print(f"  S (state tax):     {yr25c['S_gross_GgCO2e']:,.0f}  ({yr25c['S_pct']:.1f}%)  "
      f"[{yr25l['S_gross_GgCO2e']:.0f}-{yr25h['S_gross_GgCO2e']:.0f}]")
print(f"  F (federal IEPS):  {yr25c['F_gross_GgCO2e']:,.0f}  ({yr25c['F_pct']:.1f}%)  "
      f"[{yr25l['F_gross_GgCO2e']:.0f}-{yr25h['F_gross_GgCO2e']:.0f}]")
print(f"  E (pilot ETS):     {yr25c['E_gross_GgCO2e']:,.0f}  ({yr25c['E_pct']:.1f}%)  "
      f"[{yr25l['E_gross_GgCO2e']:.0f}-{yr25h['E_gross_GgCO2e']:.0f}]")
print(f"  S^F^E:             {yr25c['S_F_E_GgCO2e']:,.0f}  ({yr25c['S_F_E_pct']:.1f}%)")
print(f"  S^E only:          {yr25c['S_E_only_GgCO2e']:,.0f}  ({yr25c['S_E_only_pct']:.1f}%)  <- NG at large plants")
print(f"  S^F only:          {yr25c['S_F_only_GgCO2e']:,.0f}  ({yr25c['S_F_only_pct']:.1f}%)")
print(f"  S only:            {yr25c['S_only_GgCO2e']:,.0f}  ({yr25c['S_only_pct']:.1f}%)  <- HFCs, small NG sources")
print(f"  F only:            {yr25c['F_only_GgCO2e']:,.0f}  ({yr25c['F_only_pct']:.1f}%)  <- Transport + residential")
print(f"  Union S|F|E:       {yr25c['union_GgCO2e']:,.0f}  ({yr25c['union_pct']:.1f}%)")
print(f"  Uncovered:         {yr25c['uncovered_GgCO2e']:,.0f}  ({yr25c['uncovered_pct']:.1f}%)")
print("\n  Structural findings:")
print("  - State tax covers ~41% — broad scope (all Kyoto gases, economy-wide fixed sources)")
print("  - Federal tax adds unique coverage through transport (~23.6%) and residential (~3.4%)")
print("  - Dominant overlap is S^E: NG-fired electricity at El Sauz + SJR (> 98% of 1A1)")
print("  - NG dominance limits F: ~100% of electricity and ~95.5% of manufacturing CO2 is NG-exempt")
print("  - HFC refrigeration (70.5 GgCO2e) uniquely covered by S — not in F or E")
print("\n  03_outputs.py complete\n")
