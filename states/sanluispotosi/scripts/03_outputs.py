"""
03_outputs.py -- San Luis Potosi Carbon Pricing Overlap Analysis
=================================================================
Produces publication-quality figures and summary tables.

Outputs:
    outputs/figures/slp_venn_segments.png
    outputs/figures/slp_coverage_summary.png
    outputs/tables/slp_overlap_summary.csv
    outputs/tables/slp_overlap_full_table.csv
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import os, warnings
warnings.filterwarnings("ignore")

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR   = os.path.dirname(SCRIPT_DIR)
PROC_DIR   = os.path.join(BASE_DIR, "data", "processed")
FIG_DIR    = os.path.join(BASE_DIR, "outputs", "figures")
TBL_DIR    = os.path.join(BASE_DIR, "outputs", "tables")
os.makedirs(FIG_DIR, exist_ok=True)
os.makedirs(TBL_DIR, exist_ok=True)

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

SEG_COLS = {
    "S*F*E":    "#6B3FA0",
    "S*E only": "#00538C",
    "S*F only": "#00A9A5",
    "S only":   "#7EB8D4",
    "F only":   "#E7A720",
    "F*E only": "#C45B28",
    "E only":   "#D4A5A5",
    "Uncovered":"#D9D9D9",
}

# ── Load data ────────────────────────────────────────────────────────────
overlap  = pd.read_csv(os.path.join(PROC_DIR, "slp_overlap_estimates.csv"))
scope_df = pd.read_csv(os.path.join(PROC_DIR, "slp_tax_scope.csv"))

def get_scen(scen):
    return overlap[overlap["scenario"]==scen].iloc[0]

c = get_scen("central")
l = get_scen("low")
h = get_scen("high")

STATE_TOTAL = c["state_total_GgCO2e"]

# ── Figure 1: Venn segment bar chart ─────────────────────────────────────
SEG_LABELS = ["S*F*E", "S*E only", "S*F only", "S only", "F only", "Uncovered"]
SEG_KEYS   = ["S_F_E_GgCO2e", "S_E_only_GgCO2e", "S_F_only_GgCO2e",
              "S_only_GgCO2e", "F_only_GgCO2e", "uncovered_GgCO2e"]

fig, ax = plt.subplots(figsize=(10, 6))
fig.suptitle(
    "San Luis Potosi: Carbon Pricing Coverage Decomposition\n"
    "Three-Instrument Venn (S x F x E), Annual Avg 2007-2014, AR5 GWPs",
    fontsize=11, fontweight="bold", y=0.98
)

vals   = [c[k] for k in SEG_KEYS]
vals_l = [l[k] for k in SEG_KEYS]
vals_h = [h[k] for k in SEG_KEYS]
colours = [SEG_COLS[s] for s in SEG_LABELS]

bars = ax.bar(SEG_LABELS, vals, color=colours, width=0.55,
              edgecolor="white", linewidth=0.5)

for i, (v, vl, vh) in enumerate(zip(vals, vals_l, vals_h)):
    lo = max(0, v - vl)
    hi = max(0, vh - v)
    ax.errorbar(i, v, yerr=[[lo],[hi]], fmt="none",
                capsize=4, color="#444", linewidth=1.0, capthick=1.0)

for bar, v in zip(bars, vals):
    if v > 50:
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 60,
                f"{v:.0f}", ha="center", va="bottom", fontsize=8, fontweight="bold")

ax.axhline(STATE_TOTAL, color=WB_GREY, linestyle="--", linewidth=0.8, alpha=0.7)
ax.text(5.5, STATE_TOTAL + 100, f"State total\n{STATE_TOTAL:.0f} GgCO2e/yr",
        fontsize=7, color=WB_GREY, ha="right")

ax.set_ylabel("GgCO2e/yr")
ax.set_ylim(0, STATE_TOTAL * 1.15)
ax.tick_params(axis="x", rotation=25, labelsize=8)

S_pct = c["S_pct"]
F_pct = c["F_pct"]
E_pct = c["E_pct"]
U_pct = c["union_pct"]
metrics = (f"S={S_pct:.1f}% | F={F_pct:.1f}% | E={E_pct:.1f}%\n"
           f"Union={U_pct:.1f}% | Tier 3 | AR5 GWPs")
ax.text(0.01, 0.97, metrics, transform=ax.transAxes,
        fontsize=7.5, va="top", ha="left",
        bbox=dict(boxstyle="round,pad=0.3", facecolor="#FFF8E1", edgecolor=WB_GOLD, alpha=0.9))

fig.text(0.5, -0.02,
    "Source: IEGEI-SLP 2007-2014 (UASLP/SEGAM/VariClim). "
    "SAR GWPs converted to AR5 (CH4=28, N2O=265). Tier 3 estimation.\n"
    "Note: No HFC/PFC data in inventory -- S coverage understated. "
    "No extrapolation (base year 2007-2014).",
    ha="center", fontsize=7, style="italic", color=WB_GREY)

fig.tight_layout()
out1 = os.path.join(FIG_DIR, "slp_venn_segments.png")
fig.savefig(out1, dpi=150, bbox_inches="tight")
plt.close()
print(f"Saved: {out1}")

# ── Figure 2: Coverage summary — horizontal grouped bars ─────────────────
fig2, ax2 = plt.subplots(figsize=(10, 5.5))
fig2.suptitle(
    "San Luis Potosi: Carbon Pricing Coverage Summary\n"
    "Three Instruments, Base Year Annual Avg 2007-2014 (GgCO2e, AR5)",
    fontsize=11, fontweight="bold"
)

INSTRUMENTS = ["S (State tax)", "F (Federal IEPS)", "E (Pilot ETS)", "Union S|F|E"]
INST_KEYS   = ["S_gross_GgCO2e", "F_gross_GgCO2e", "E_gross_GgCO2e", "union_GgCO2e"]
INST_COLS   = [WB_BLUE, WB_GOLD, WB_RED, WB_TEAL]

x = np.arange(len(INSTRUMENTS))
bar_width = 0.25

# Central, Low, High bars side by side
for i, (scen, label, alpha) in enumerate([
    ("low", "Low", 0.5), ("central", "Central", 0.9), ("high", "High", 0.5)
]):
    row = get_scen(scen)
    vals = [row[k] for k in INST_KEYS]
    offset = (i - 1) * bar_width
    bars = ax2.bar(x + offset, vals, bar_width, alpha=alpha,
                   color=[INST_COLS[j] for j in range(len(INSTRUMENTS))],
                   edgecolor="white", linewidth=0.4, label=label)
    if scen == "central":
        for bar, v, col in zip(bars, vals, INST_COLS):
            ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 50,
                     f"{v:.0f}", ha="center", va="bottom", fontsize=7,
                     color=col, fontweight="bold")

ax2.axhline(STATE_TOTAL, color=WB_GREY, linestyle="--", linewidth=0.8, alpha=0.6)
ax2.text(3.5, STATE_TOTAL + 100, f"State total: {STATE_TOTAL:.0f}", fontsize=7,
         color=WB_GREY, ha="right")

ax2.set_xticks(x)
ax2.set_xticklabels(INSTRUMENTS)
ax2.set_ylabel("GgCO2e/yr")
ax2.set_ylim(0, STATE_TOTAL * 1.2)
ax2.legend(title="Scenario", fontsize=7, title_fontsize=8)

note = (
    "Key findings:\n"
    f"  - SLP state tax covers {S_pct:.0f}% of state emissions (fixed sources, productive processes)\n"
    f"  - Federal tax covers {F_pct:.0f}% (non-NG fuels; highest elec. overlap of any state)\n"
    f"  - ETS covers {E_pct:.0f}% (large facilities: cement, metalurgy, power, glass, paper)\n"
    f"  - Industrial non-NG fuel share = 65% (highest of all states; GLP=53%, diesel=12%)\n"
    "  - No HFC/PFC data: S coverage understated"
)
ax2.text(0.01, 0.98, note, transform=ax2.transAxes,
         fontsize=6.5, va="top", ha="left",
         bbox=dict(boxstyle="round,pad=0.4", facecolor="#E8F4FD", edgecolor=WB_BLUE, alpha=0.9))

fig2.text(0.5, -0.02,
    "Source: IEGEI-SLP 2007-2014 (UASLP/SEGAM/VariClim). "
    "GWPs: AR5 (CH4=28, N2O=265). Tier 3 estimate.",
    ha="center", fontsize=7, style="italic", color=WB_GREY)

fig2.tight_layout()
out2 = os.path.join(FIG_DIR, "slp_coverage_summary.png")
fig2.savefig(out2, dpi=150, bbox_inches="tight")
plt.close()
print(f"Saved: {out2}")

# ── Table 1: Summary overlap table ──────────────────────────────────────
cols_summary = [
    "year", "scenario", "gwp_basis",
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
summary_tbl.to_csv(os.path.join(TBL_DIR, "slp_overlap_summary.csv"), index=False)
print(f"Saved: outputs/tables/slp_overlap_summary.csv")

# ── Table 2: Full table for publication ──────────────────────────────────
SEGS_PUB = [
    ("S*F*E -- all three instruments", "S_F_E_GgCO2e", "S_F_E_pct",
     "Electricity non-NG at large plants + manufacturing non-NG at large plants"),
    ("S*E only -- state tax + ETS", "S_E_only_GgCO2e", "S_E_only_pct",
     "Electricity NG (Tamazunchale) + manufacturing NG at large plants + cement/cal process at large facilities"),
    ("S*F only -- state tax + federal", "S_F_only_GgCO2e", "S_F_only_pct",
     "Manufacturing GLP+diesel below ETS threshold; commercial/public non-NG"),
    ("S only -- state tax unique", "S_only_GgCO2e", "S_only_pct",
     "NG at small facilities; IPPU process at small facilities; commercial NG"),
    ("F only -- federal tax unique", "F_only_GgCO2e", "F_only_pct",
     "Transport (gasoline+diesel); residential non-NG (GLP)"),
    ("Uncovered", "uncovered_GgCO2e", "uncovered_pct",
     "AFOLU (livestock, crop burning); waste; residential NG"),
]

rows_pub = []
for scen in ["central", "low", "high"]:
    row_data = get_scen(scen)
    for seg_name, key, pct_key, content in SEGS_PUB:
        rows_pub.append(dict(
            year="2007-2014 avg", scenario=scen, gwp_basis="AR5",
            segment=seg_name,
            GgCO2e=round(row_data[key], 1),
            pct_of_state=round(row_data[pct_key], 2),
            content_description=content,
            estimation_tier="Tier 3",
        ))
    for inst, key, pct_key in [
        ("S gross (state tax)", "S_gross_GgCO2e", "S_pct"),
        ("F gross (federal tax)", "F_gross_GgCO2e", "F_pct"),
        ("E gross (pilot ETS)", "E_gross_GgCO2e", "E_pct"),
        ("S|F|E deduplicated union", "union_GgCO2e", "union_pct"),
    ]:
        rows_pub.append(dict(
            year="2007-2014 avg", scenario=scen, gwp_basis="AR5",
            segment=inst,
            GgCO2e=round(row_data[key], 1),
            pct_of_state=round(row_data[pct_key], 2),
            content_description="",
            estimation_tier="Tier 3",
        ))

full_tbl = pd.DataFrame(rows_pub)
full_tbl.to_csv(os.path.join(TBL_DIR, "slp_overlap_full_table.csv"), index=False)
print(f"Saved: outputs/tables/slp_overlap_full_table.csv")

# ── Console summary ──────────────────────────────────────────────────────
print(f"\n{'='*70}")
print("SAN LUIS POTOSI -- FINAL PUBLICATION SUMMARY (CENTRAL)")
print(f"{'='*70}")
print(f"  Base year:         Annual avg 2007-2014 (cumulative / 8)")
print(f"  GWP basis:         AR5 (CH4=28, N2O=265) -- converted from SAR")
print(f"  State total:       {STATE_TOTAL:,.0f} GgCO2e/yr ({STATE_TOTAL/1000:.2f} MtCO2e/yr)")
print(f"  S (state tax):     {c['S_gross_GgCO2e']:,.0f}  ({c['S_pct']:.1f}%)  "
      f"[{l['S_gross_GgCO2e']:.0f}-{h['S_gross_GgCO2e']:.0f}]")
print(f"  F (federal IEPS):  {c['F_gross_GgCO2e']:,.0f}  ({c['F_pct']:.1f}%)  "
      f"[{l['F_gross_GgCO2e']:.0f}-{h['F_gross_GgCO2e']:.0f}]")
print(f"  E (pilot ETS):     {c['E_gross_GgCO2e']:,.0f}  ({c['E_pct']:.1f}%)  "
      f"[{l['E_gross_GgCO2e']:.0f}-{h['E_gross_GgCO2e']:.0f}]")
print(f"  S*F*E:             {c['S_F_E_GgCO2e']:,.0f}  ({c['S_F_E_pct']:.1f}%)")
print(f"  S*E only:          {c['S_E_only_GgCO2e']:,.0f}  ({c['S_E_only_pct']:.1f}%)")
print(f"  S*F only:          {c['S_F_only_GgCO2e']:,.0f}  ({c['S_F_only_pct']:.1f}%)")
print(f"  S only:            {c['S_only_GgCO2e']:,.0f}  ({c['S_only_pct']:.1f}%)")
print(f"  F only:            {c['F_only_GgCO2e']:,.0f}  ({c['F_only_pct']:.1f}%)")
print(f"  Union S|F|E:       {c['union_GgCO2e']:,.0f}  ({c['union_pct']:.1f}%)")
print(f"  Uncovered:         {c['uncovered_GgCO2e']:,.0f}  ({c['uncovered_pct']:.1f}%)")
print(f"\n  KEY: Non-NG industrial fuel = 65% (highest of all states)")
print(f"       Electricity non-NG = {(1-0.431)*100:.0f}% (Villa de Reyes combustoleo)")
print(f"       Cement/cal = {scope_df[scope_df['sector_group']=='ippu_cemento']['emissions_GgCO2e'].sum():.0f} GgCO2e/yr process CO2 (in S,E not F)")
print(f"       Data gap: No HFC/PFC data in inventory")
print(f"\n  03_outputs.py complete\n")
