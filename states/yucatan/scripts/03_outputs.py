"""
=============================================================================
Case:     Mexico State Carbon Pricing -- Yucatan
Script:   03_outputs.py
Purpose:  Publication-quality figures and CSV tables from overlap estimates.
          Three-instrument Venn: S (Yucatan tax) x F (IEPS) x E (Pilot ETS).
Target:   State & Trends of Carbon Pricing methodology note
=============================================================================
"""

import os
import logging
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)

SCRIPT_DIR    = os.path.dirname(os.path.abspath(__file__))
PROCESSED_DIR = os.path.join(SCRIPT_DIR, "data", "processed")
TABLES_DIR    = os.path.join(SCRIPT_DIR, "outputs", "tables")
FIGS_DIR      = os.path.join(SCRIPT_DIR, "outputs", "figures")
for d in [TABLES_DIR, FIGS_DIR]:
    os.makedirs(d, exist_ok=True)

TOTAL_STATE = 10425.52  # GgCO2e, 2023

# ---------------------------------------------------------------------------
# 1. Load overlap results
# ---------------------------------------------------------------------------
df = pd.read_csv(os.path.join(PROCESSED_DIR, "yucatan_overlap_results.csv"))

# Extract segment values
def get_val(segment, col="central_GgCO2e"):
    row = df[df["segment"] == segment]
    if row.empty:
        return 0.0
    return row[col].values[0]

seg_keys = ["S_F_E", "S_F", "S_E", "S_only", "F_E", "F_only", "E_only", "uncovered"]
central = {k: get_val(k) for k in seg_keys}
low     = {k: get_val(k, "low_GgCO2e") for k in seg_keys}
high    = {k: get_val(k, "high_GgCO2e") for k in seg_keys}

# Derived
for d in [central, low, high]:
    d["gross_S"] = d["S_F_E"] + d["S_F"] + d["S_E"] + d["S_only"]
    d["gross_F"] = d["S_F_E"] + d["S_F"] + d["F_E"] + d["F_only"]
    d["gross_E"] = d["S_F_E"] + d["S_E"] + d["F_E"] + d["E_only"]
    d["union"]   = sum(d[k] for k in seg_keys if k != "uncovered")

# World Bank / State & Trends colour palette
PALETTE = {
    "S_F_E":     "#1A3C5E",   # dark navy
    "S_F":       "#2F6DAE",   # WB blue
    "S_E":       "#4A90D9",   # medium blue
    "S_only":    "#6BAED6",   # light blue
    "F_only":    "#F7A600",   # WB amber
    "F_E":       "#E8850C",   # dark amber
    "E_only":    "#C0392B",   # deep red
    "Uncovered": "#D9D9D9",   # grey
}

LABELS = {
    "S_F_E":     "S n F n E  (all three)",
    "S_F":       "S n F only (state + federal, not ETS)",
    "S_E":       "S n E only (state + ETS, not federal)",
    "S_only":    "S only (state tax unique -- HFCs + fugitive)",
    "F_only":    "F only (federal -- transport)",
    "F_E":       "F n E only (not applicable)",
    "E_only":    "E only (ETS -- above-threshold, NG portion)",
    "Uncovered": "Not covered by any instrument",
}

# ─────────────────────────────────────────────────────────────────────────
# FIGURE 1: Stacked bar -- Venn segment decomposition
# ─────────────────────────────────────────────────────────────────────────

fig, ax = plt.subplots(figsize=(8, 9))
fig.patch.set_facecolor("white")

# Order: bottom to top
seg_order = ["S_F_E", "S_F", "S_E", "S_only", "F_only", "E_only", "Uncovered"]
seg_vals  = [
    ("S_F_E",     central["S_F_E"]),
    ("S_F",       central["S_F"]),
    ("S_E",       central["S_E"]),
    ("S_only",    central["S_only"]),
    ("F_only",    central["F_only"]),
    ("E_only",    central["E_only"]),
    ("Uncovered", TOTAL_STATE - central["union"]),
]

bottom = 0
for key, val in seg_vals:
    ax.bar(0.5, val, bottom=bottom, width=0.5,
           color=PALETTE[key], edgecolor="white", linewidth=0.8)
    # Label if large enough
    if val > 100:
        mid = bottom + val / 2
        pct = val / TOTAL_STATE * 100
        txt_color = "white" if key not in ("Uncovered",) else "#333"
        ax.text(0.5, mid, f"{val:,.0f}\n({pct:.1f}%)",
                ha="center", va="center", fontsize=8,
                color=txt_color, fontweight="bold")
    bottom += val

# Error bar for union
union_c = central["union"]
union_lo = min(low["union"], high["union"])
union_hi = max(low["union"], high["union"])
yerr_lo = max(0, union_c - union_lo)
yerr_hi = max(0, union_hi - union_c)
ax.errorbar(0.5, union_c,
            yerr=[[yerr_lo], [yerr_hi]],
            fmt="none", color="#333", capsize=8, linewidth=2,
            label="Union uncertainty range")

ax.set_xlim(0, 1)
ax.set_ylim(0, TOTAL_STATE * 1.08)
ax.set_xticks([])
ax.set_ylabel("GgCO2e", fontsize=11)
ax.set_title("Yucatan 2023: Carbon Pricing Venn Decomposition\n"
             "S (State Tax) x F (Federal IEPS) x E (Pilot ETS)",
             fontsize=12, fontweight="bold", pad=12)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.spines["bottom"].set_visible(False)

# Legend
legend_patches = [mpatches.Patch(color=PALETTE[k], label=LABELS[k])
                  for k in ["S_F_E", "S_F", "S_E", "S_only", "F_only",
                            "E_only", "Uncovered"]]
ax.legend(handles=legend_patches, loc="upper right", fontsize=7.5,
          frameon=True, edgecolor="#ccc")

note = (
    "Notes: S = Yucatan state carbon tax (all Kyoto gases, fixed sources, no threshold). "
    "F = Mexico federal carbon tax (IEPS, NG-exempt). "
    "E = Mexico Pilot ETS (>=25,000 tCO2e/yr, non-binding pilot).\n"
    "HFCs (334 GgCO2e) fall entirely in S-only -- first state with HFCs quantified + in scope. "
    "NG/calcination stimuli are payment relief, not scope exclusions. "
    "Base year 2023. Tier 3. Source: World Bank Climate Change Group."
)
fig.text(0.5, -0.02, note, ha="center", fontsize=6.5, color="#555",
         wrap=True, style="italic")

plt.tight_layout()
fig1_path = os.path.join(FIGS_DIR, "yucatan_venn_segments_2023.png")
plt.savefig(fig1_path, dpi=200, bbox_inches="tight", facecolor="white")
plt.close()
log.info(f"Figure 1 saved: {fig1_path}")


# ─────────────────────────────────────────────────────────────────────────
# FIGURE 2: Horizontal bar -- instrument totals + union vs state total
# ─────────────────────────────────────────────────────────────────────────

fig2, ax2 = plt.subplots(figsize=(11, 5))
fig2.patch.set_facecolor("white")

categories = [
    ("Yucatan State Tax (S)",    "gross_S", "#2F6DAE"),
    ("Federal IEPS (F)",         "gross_F", "#F7A600"),
    ("Pilot ETS (E, legal)",     "gross_E", "#C0392B"),
    ("Union S u F u E",          "union",   "#1A3C5E"),
    ("Total State Emissions",    None,      "#AAAAAA"),
]

y_pos = np.arange(len(categories))
for i, (label, key, color) in enumerate(categories):
    if key:
        cv = central[key]
        lv = min(low[key], high[key])
        hv = max(low[key], high[key])
        ax2.barh(i, cv, color=color, edgecolor="white", height=0.6)
        ax2.errorbar(cv, i, xerr=[[max(0, cv - lv)], [max(0, hv - cv)]],
                     fmt="none", color="#333", capsize=4, linewidth=1.2)
        ax2.text(cv + 50, i, f"{cv:,.0f} ({cv/TOTAL_STATE*100:.1f}%)",
                 va="center", fontsize=9, color="#333")
    else:
        ax2.barh(i, TOTAL_STATE, color=color, edgecolor="white", height=0.6)
        ax2.text(TOTAL_STATE + 50, i, f"{TOTAL_STATE:,.0f}",
                 va="center", fontsize=9, color="#333")

ax2.set_yticks(y_pos)
ax2.set_yticklabels([c[0] for c in categories], fontsize=10)
ax2.set_xlabel("GgCO2e", fontsize=10)
ax2.set_title("Yucatan 2023: Carbon Pricing Coverage -- Instrument Totals",
              fontsize=12, fontweight="bold")
ax2.spines["top"].set_visible(False)
ax2.spines["right"].set_visible(False)
ax2.invert_yaxis()

note2 = (
    "Notes: Instrument totals are gross (un-deduplicated). "
    "Union = S u F u E via inclusion-exclusion. "
    "ETS is non-binding pilot; legal scope shown. "
    "Error bars show low-high uncertainty. Base year 2023. Tier 3."
)
ax2.text(0.5, -0.12, note2, transform=ax2.transAxes,
         ha="center", fontsize=7, color="#555", style="italic")

plt.tight_layout()
fig2_path = os.path.join(FIGS_DIR, "yucatan_coverage_summary_2023.png")
plt.savefig(fig2_path, dpi=200, bbox_inches="tight", facecolor="white")
plt.close()
log.info(f"Figure 2 saved: {fig2_path}")


# ─────────────────────────────────────────────────────────────────────────
# FIGURE 3: HFC breakdown -- unique to Yucatan
# ─────────────────────────────────────────────────────────────────────────

df_hfc = pd.read_csv(os.path.join(PROCESSED_DIR, "yucatan_hfc_detail_2023.csv"))

fig3, ax3 = plt.subplots(figsize=(8, 5))
fig3.patch.set_facecolor("white")

colors_hfc = ["#2F6DAE", "#6BAED6", "#4A90D9", "#1A3C5E", "#7BC8F6", "#133A5E"]
ax3.barh(df_hfc["application"], df_hfc["co2e_gg"],
         color=colors_hfc[:len(df_hfc)], edgecolor="white", height=0.6)

for i, (_, r) in enumerate(df_hfc.iterrows()):
    ax3.text(r["co2e_gg"] + 2, i, f"{r['co2e_gg']:.1f} GgCO2e",
             va="center", fontsize=9)

ax3.set_xlabel("GgCO2e", fontsize=10)
ax3.set_title("Yucatan HFC/HCFC Emissions by Application (2023)\n"
              "All in S-only segment -- first state with HFCs quantified + in tax scope",
              fontsize=10, fontweight="bold")
ax3.spines["top"].set_visible(False)
ax3.spines["right"].set_visible(False)
ax3.invert_yaxis()

plt.tight_layout()
fig3_path = os.path.join(FIGS_DIR, "yucatan_hfc_breakdown_2023.png")
plt.savefig(fig3_path, dpi=200, bbox_inches="tight", facecolor="white")
plt.close()
log.info(f"Figure 3 saved: {fig3_path}")


# ─────────────────────────────────────────────────────────────────────────
# Publication table (formatted for methodology note)
# ─────────────────────────────────────────────────────────────────────────

pub_rows = []

def add_row(label, cv, lv, hv, note=""):
    pub_rows.append({
        "Category": label,
        "Central (GgCO2e)": round(cv, 1),
        "Low (GgCO2e)": round(lv, 1),
        "High (GgCO2e)": round(hv, 1),
        "Share of state (%)": round(cv / TOTAL_STATE * 100, 1) if cv > 0 else 0.0,
        "Note": note,
    })

add_row("-- INSTRUMENT TOTALS (gross) --", 0, 0, 0)
add_row("Yucatan state carbon tax (S)",
        central["gross_S"], low["gross_S"], high["gross_S"],
        "All Kyoto gases; fixed productive sources; no threshold")
add_row("Federal IEPS carbon tax (F)",
        central["gross_F"], low["gross_F"], high["gross_F"],
        "Combustion CO2; NG-exempt; all sectors incl. transport")
add_row("Mexico Pilot ETS (E)",
        central["gross_E"], low["gross_E"], high["gross_E"],
        "Direct CO2; >=25k tCO2e/yr; non-binding pilot")

add_row("-- VENN SEGMENTS (8) --", 0, 0, 0)
for key, label in LABELS.items():
    if key == "Uncovered":
        cv = TOTAL_STATE - central["union"]
        lv = TOTAL_STATE - high["union"]
        hv = TOTAL_STATE - low["union"]
    elif key == "F_E":
        cv, lv, hv = central.get(key, 0), low.get(key, 0), high.get(key, 0)
    else:
        cv = central[key]
        lv = low[key]
        hv = high[key]
    add_row(label, cv, lv, hv)

add_row("-- KEY METRICS --", 0, 0, 0)
add_row("Net S-only (state tax unique coverage)",
        central["S_only"], low["S_only"], high["S_only"],
        "HFCs (334 GgCO2e) + fugitive NG (90) + lubricants (20)")
add_row("Deduplicated union S u F u E",
        central["union"], low["union"], high["union"],
        "All emissions covered by at least one instrument")
add_row("Total Yucatan state emissions",
        TOTAL_STATE, TOTAL_STATE, TOTAL_STATE,
        "Excl. 3B (land) and 3D (products de madera). AR5 GWPs.")

df_pub = pd.DataFrame(pub_rows)
pub_path = os.path.join(TABLES_DIR, "yucatan_overlap_full_table.csv")
df_pub.to_csv(pub_path, index=False)
log.info(f"Publication table: {pub_path}")


# ─────────────────────────────────────────────────────────────────────────
# Console summary
# ─────────────────────────────────────────────────────────────────────────

log.info("\n" + "=" * 70)
log.info("KEY RESULTS -- YUCATAN 2023 CARBON PRICING OVERLAP")
log.info("=" * 70)
log.info(f"  Total state emissions: {TOTAL_STATE:,.2f} GgCO2e")
log.info(f"")
log.info(f"  GROSS INSTRUMENT COVERAGE:")
log.info(f"    S (Yucatan tax):  {central['gross_S']:,.1f} GgCO2e "
         f"({central['gross_S']/TOTAL_STATE*100:.1f}%)")
log.info(f"    F (IEPS):         {central['gross_F']:,.1f} GgCO2e "
         f"({central['gross_F']/TOTAL_STATE*100:.1f}%)")
log.info(f"    E (Pilot ETS):    {central['gross_E']:,.1f} GgCO2e "
         f"({central['gross_E']/TOTAL_STATE*100:.1f}%)")
log.info(f"    Union S u F u E:  {central['union']:,.1f} GgCO2e "
         f"({central['union']/TOTAL_STATE*100:.1f}%)")
log.info(f"")
log.info(f"  VENN SEGMENTS:")
for key in ["S_F_E", "S_F", "S_E", "S_only", "F_only", "E_only"]:
    v = central[key]
    log.info(f"    {LABELS[key]:45s}: {v:8,.1f} ({v/TOTAL_STATE*100:.1f}%)")
unc = TOTAL_STATE - central["union"]
log.info(f"    {'Uncovered':45s}: {unc:8,.1f} ({unc/TOTAL_STATE*100:.1f}%)")

log.info("\n03_outputs.py complete.")
