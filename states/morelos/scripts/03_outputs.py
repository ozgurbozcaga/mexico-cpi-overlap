"""
03_outputs.py — Morelos Carbon Pricing Overlap Analysis
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

plt.rcParams.update({"font.family":"sans-serif","font.size":9,
                     "axes.titlesize":11,"axes.titleweight":"bold",
                     "axes.spines.top":False,"axes.spines.right":False,
                     "figure.dpi":150})

WB_BLUE="#00538C"; WB_RED="#BE0000"; WB_TEAL="#00A9A5"
WB_GOLD="#E7A720"; WB_GREY="#6D6E71"; WB_WARN="#FF6B35"

SEG_COLS = {
    "S∩F∩E":    "#6B3FA0",
    "S∩E only": "#00538C",
    "S∩F only": "#00A9A5",
    "S only":   "#7EB8D4",
    "F only":   "#E7A720",
    "Uncovered":"#D9D9D9",
}

overlap = pd.read_csv(os.path.join(PROC_DIR, "morelos_overlap_estimates.csv"))

def get_row(yr, scen):
    return overlap[(overlap["year"]==yr) & (overlap["scenario"]==scen)].iloc[0]

# ── Figure 1: Venn segment bar chart 2025 + 2026 ────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(12, 6.5), sharey=True)
fig.suptitle(
    "Morelos State Carbon Tax × Federal Carbon Tax × Mexico Pilot ETS\n"
    "Emission Coverage Decomposition (GgCO₂e, Tier 3 estimate)",
    fontsize=11, fontweight="bold", y=1.01
)

SEG_LABELS = ["S∩F∩E","S∩E only","S∩F only","S only","F only","Uncovered"]
SEG_KEYS   = ["S_F_E_GgCO2e","S_E_only_GgCO2e","S_F_only_GgCO2e",
               "S_only_GgCO2e","F_only_GgCO2e","uncovered_GgCO2e"]

for ax, yr in zip(axes, [2025, 2026]):
    c = get_row(yr, "central")
    l = get_row(yr, "low")
    h = get_row(yr, "high")
    vals   = [c[k] for k in SEG_KEYS]
    vals_l = [l[k] for k in SEG_KEYS]
    vals_h = [h[k] for k in SEG_KEYS]
    colours = [SEG_COLS[s] for s in SEG_LABELS]

    bars = ax.bar(SEG_LABELS, vals, color=colours, width=0.55,
                  edgecolor="white", linewidth=0.5)
    for i,(v,vl,vh) in enumerate(zip(vals,vals_l,vals_h)):
        lo = max(0, v-vl); hi = max(0, vh-v)
        ax.errorbar(i, v, yerr=[[lo],[hi]], fmt="none",
                    capsize=4, color="#444", linewidth=1.0)
    for bar, v in zip(bars, vals):
        if v > 30:
            ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+15,
                    f"{v:.0f}", ha="center", va="bottom", fontsize=7.5, fontweight="bold")

    total = c["state_total_GgCO2e"]
    ax.axhline(total, color=WB_GREY, linestyle="--", linewidth=0.8, alpha=0.6)
    ax.text(5.5, total+20, f"State total\n{total:.0f}", fontsize=7, color=WB_GREY, ha="right")
    ax.set_title(f"{yr}", fontsize=12)
    ax.set_ylabel("GgCO₂e" if yr==2025 else "")
    ax.set_ylim(0, 8000)
    ax.tick_params(axis="x", rotation=30, labelsize=7.5)

    metrics = (f"S={c['S_pct']:.1f}% | F={c['F_pct']:.1f}% | E={c['E_pct']:.1f}%\n"
               f"Union={c['union_pct']:.1f}% | Tier 3 | ⚠ 2014 base year")
    ax.text(0.01, 0.97, metrics, transform=ax.transAxes, fontsize=7, va="top",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="#FFF3CD", edgecolor=WB_WARN, alpha=0.95))

# Warning banner
fig.text(0.5, -0.05,
    "⚠  DATA CAVEATS: (1) 2014 base year; 11-year extrapolation — wider uncertainty than other states.  "
    "(2) HFCs/PFCs/SF₆ absent from 2014 inventory — state tax S coverage understated.\n"
    "(3) Biogenic CO₂ from wood combustion (~11% of state) included in state total but unpriced.  "
    "(4) ETS = legal scope only (non-binding pilot).  "
    "GWPs: AR5 (CH₄=28, N₂O=265).",
    ha="center", fontsize=7, style="italic", color=WB_WARN, wrap=True)

fig.tight_layout()
out1 = os.path.join(FIG_DIR, "morelos_venn_segments_2025_2026.png")
fig.savefig(out1, dpi=150, bbox_inches="tight")
plt.close()
print(f"Saved: {out1}")

# ── Figure 2: Coverage summary ───────────────────────────────────────────────
fig2, ax2 = plt.subplots(figsize=(10, 5.5))
fig2.suptitle(
    "Morelos Carbon Pricing Coverage Summary\nThree Instruments, 2014–2026 (GgCO₂e)",
    fontsize=11, fontweight="bold"
)

YEARS = [2014, 2025, 2026]
INSTS = ["S (State tax)", "F (Federal IEPS)", "E (Pilot ETS)", "Union S∪F∪E"]
IKEYS = ["S_gross_GgCO2e","F_gross_GgCO2e","E_gross_GgCO2e","union_GgCO2e"]
ICOLS = [WB_BLUE, WB_GOLD, WB_RED, WB_TEAL]

bar_width = 0.18
x = np.arange(len(YEARS))

for i,(inst,key,col) in enumerate(zip(INSTS,IKEYS,ICOLS)):
    centrals = [get_row(yr,"central")[key] for yr in YEARS]
    lows     = [get_row(yr,"low")[key]     for yr in YEARS]
    highs    = [get_row(yr,"high")[key]    for yr in YEARS]
    bars = ax2.bar(x+i*bar_width-1.5*bar_width, centrals, bar_width,
                   label=inst, color=col, alpha=0.88, edgecolor="white")
    ax2.errorbar(x+i*bar_width-1.5*bar_width, centrals,
                 yerr=[[max(0,c-l) for c,l in zip(centrals,lows)],
                       [max(0,h-c) for c,h in zip(centrals,highs)]],
                 fmt="none", capsize=3, color="#333", linewidth=0.8)
    for bar, v in zip(bars, centrals):
        ax2.text(bar.get_x()+bar.get_width()/2, bar.get_height()+20,
                 f"{v/1000:.1f}k", ha="center", va="bottom", fontsize=7, color=col, fontweight="bold")

totals = [get_row(yr,"central")["state_total_GgCO2e"] for yr in YEARS]
ax2.plot(x, totals, "D--", color=WB_GREY, markersize=5, linewidth=1.0,
         label="State total", zorder=5)
for xi, t in zip(x, totals):
    ax2.text(xi+0.03, t+50, f"{t:.0f}", fontsize=7, color=WB_GREY)

ax2.set_xticks(x)
ax2.set_xticklabels([str(y) for y in YEARS])
ax2.set_ylabel("GgCO₂e")
ax2.set_ylim(0, 9000)
ax2.legend(loc="upper right", fontsize=7.5, framealpha=0.9)

note = (
    "Key findings: Cement industry (25-28% of state) drives S coverage;\n"
    "calcination process CO₂ is in S but NOT in F → S∩E only is dominant overlap.\n"
    "Mobile transport (49% of 2014 CO₂) is F-only; exempt from state tax.\n"
    "Livestock CH₄ (~6% of state GgCO₂e) fully uncovered.\n"
    "⚠  HFCs/PFCs/SF₆ absent — S coverage understated."
)
ax2.text(0.01, 0.97, note, transform=ax2.transAxes, fontsize=7, va="top",
         bbox=dict(boxstyle="round,pad=0.4", facecolor="#FFF3CD", edgecolor=WB_WARN, alpha=0.9))

fig2.text(0.5, -0.03,
    "Source: Inventario de Emisiones Morelos 2014 (SDS/SEMARNAT/INECC/LT Consulting). "
    "Tier 3 estimate. 2014 base; 11-year extrapolation. GWPs: AR5.",
    ha="center", fontsize=7, style="italic", color=WB_GREY)

fig2.tight_layout()
out2 = os.path.join(FIG_DIR, "morelos_coverage_summary_2025_2026.png")
fig2.savefig(out2, dpi=150, bbox_inches="tight")
plt.close()
print(f"Saved: {out2}")

# ── Tables ────────────────────────────────────────────────────────────────────
COLS_SUMMARY = [
    "year","scenario","state_total_GgCO2e",
    "S_gross_GgCO2e","S_pct","F_gross_GgCO2e","F_pct","E_gross_GgCO2e","E_pct",
    "S_F_E_GgCO2e","S_F_E_pct","S_E_only_GgCO2e","S_E_only_pct",
    "S_F_only_GgCO2e","S_F_only_pct","S_only_GgCO2e","S_only_pct",
    "F_only_GgCO2e","F_only_pct","union_GgCO2e","union_pct",
    "uncovered_GgCO2e","uncovered_pct","estimation_tier","data_gap_note",
]
overlap[COLS_SUMMARY].to_csv(os.path.join(TBL_DIR, "morelos_overlap_summary.csv"), index=False)
print(f"Saved: outputs/tables/morelos_overlap_summary.csv")

# Full table
SEGS_PUB = [
    ("S∩F∩E — all three",     "S_F_E_GgCO2e",     "S_F_E_pct",
     "Cement combustion (petcoke/FO fraction) + manuf. taxable fuels at large plants"),
    ("S∩E only — state + ETS","S_E_only_GgCO2e",  "S_E_only_pct",
     "Cement calcination process CO₂ at large plants — in ETS, in S, but NOT in F"),
    ("S∩F only — state + fed","S_F_only_GgCO2e",  "S_F_only_pct",
     "Manufacturing/commercial taxable fuels at small facilities below ETS threshold"),
    ("S only — state unique",  "S_only_GgCO2e",    "S_only_pct",
     "Process CO₂ at small facilities; NG combustion; commercial NG; HFC gap"),
    ("F only — federal unique","F_only_GgCO2e",    "F_only_pct",
     "All mobile (road, aviation, non-road); agricultural combustion"),
    ("Uncovered",              "uncovered_GgCO2e", "uncovered_pct",
     "Livestock CH₄; biogenic wood combustion CO₂; agricultural burning; wastewater"),
]
rows_pub = []
for yr in [2014, 2025, 2026]:
    for scen in ["central","low","high"]:
        r = get_row(yr, scen)
        for seg_name, key, pct_key, content in SEGS_PUB:
            rows_pub.append(dict(year=yr, scenario=scen, segment=seg_name,
                                 GgCO2e=round(r[key],1), pct_of_state=round(r[pct_key],2),
                                 content_description=content, estimation_tier="Tier 3"))
        for inst, key, pct_key in [
            ("S gross","S_gross_GgCO2e","S_pct"),("F gross","F_gross_GgCO2e","F_pct"),
            ("E gross","E_gross_GgCO2e","E_pct"),("Union S∪F∪E","union_GgCO2e","union_pct")]:
            rows_pub.append(dict(year=yr, scenario=scen, segment=inst,
                                 GgCO2e=round(r[key],1), pct_of_state=round(r[pct_key],2),
                                 content_description="", estimation_tier="Tier 3"))

pd.DataFrame(rows_pub).to_csv(os.path.join(TBL_DIR, "morelos_overlap_full_table.csv"), index=False)
print(f"Saved: outputs/tables/morelos_overlap_full_table.csv")

# ── Console summary ───────────────────────────────────────────────────────────
print("\n" + "="*65)
print("MORELOS — FINAL PUBLICATION SUMMARY (2025 CENTRAL)")
print("="*65)
c25 = get_row(2025, "central")
l25 = get_row(2025, "low")
h25 = get_row(2025, "high")

print(f"  State total:       {c25['state_total_GgCO2e']:,.0f} GgCO2e")
print(f"  S (state tax):     {c25['S_gross_GgCO2e']:,.0f}  ({c25['S_pct']:.1f}%)  [{l25['S_gross_GgCO2e']:.0f}-{h25['S_gross_GgCO2e']:.0f}]")
print(f"  F (federal IEPS):  {c25['F_gross_GgCO2e']:,.0f}  ({c25['F_pct']:.1f}%)  [{l25['F_gross_GgCO2e']:.0f}-{h25['F_gross_GgCO2e']:.0f}]")
print(f"  E (pilot ETS):     {c25['E_gross_GgCO2e']:,.0f}  ({c25['E_pct']:.1f}%)  [{l25['E_gross_GgCO2e']:.0f}-{h25['E_gross_GgCO2e']:.0f}]")
print(f"  S∩F∩E:             {c25['S_F_E_GgCO2e']:,.0f}  ({c25['S_F_E_pct']:.1f}%)  ← cement combustion + manuf taxable at large plants")
print(f"  S∩E only:          {c25['S_E_only_GgCO2e']:,.0f}  ({c25['S_E_only_pct']:.1f}%)  ← cement CALCINATION process CO₂")
print(f"  S∩F only:          {c25['S_F_only_GgCO2e']:,.0f}  ({c25['S_F_only_pct']:.1f}%)")
print(f"  S only:            {c25['S_only_GgCO2e']:,.0f}  ({c25['S_only_pct']:.1f}%)")
print(f"  F only:            {c25['F_only_GgCO2e']:,.0f}  ({c25['F_only_pct']:.1f}%)  ← mobile transport")
print(f"  Union S∪F∪E:       {c25['union_GgCO2e']:,.0f}  ({c25['union_pct']:.1f}%)")
print(f"  Uncovered:         {c25['uncovered_GgCO2e']:,.0f}  ({c25['uncovered_pct']:.1f}%)")
print("\n  ⚠  S is understated: HFCs/PFCs/SF₆ not in 2014 inventory")
print("  ⚠  Cement process CO₂ drives the S∩E segment — unique to Morelos")
print("\n✓ 03_outputs.py complete\n")
