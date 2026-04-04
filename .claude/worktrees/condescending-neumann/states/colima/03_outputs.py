"""
=============================================================================
Case:     Mexico State Carbon Pricing — Colima
Script:   03_outputs.py
Purpose:  Publication-quality tables and figures from overlap estimates.
          Adds full Venn decomposition (7 segments) across the three
          instruments: Colima state carbon tax (S), Mexico federal carbon
          tax (F), Mexico Pilot ETS (E).
          Highlights:
            - Net S-only coverage (in state tax but not F or E)
            - Cumulative deduplicated union S ∪ F ∪ E
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
from matplotlib.patches import FancyBboxPatch
import matplotlib.gridspec as gridspec

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)

PROCESSED_DIR = os.path.join(os.path.dirname(__file__), "data", "processed")
TABLES_DIR    = os.path.join(os.path.dirname(__file__), "outputs", "tables")
FIGS_DIR      = os.path.join(os.path.dirname(__file__), "outputs", "figures")
for d in [TABLES_DIR, FIGS_DIR]:
    os.makedirs(d, exist_ok=True)

BASE_YEAR    = 2015
TARGET_YEARS = [2025, 2026]
TOTAL_2015   = 18137   # GgCO2e — IMADES inventory net total

# Growth rates (from 02_estimate.py; replicated for transport sectors)
CAGR = {
    "electricity_taxable": {"c": -0.020, "l": -0.080, "h":  0.010},
    "electricity_ng":      {"c":  0.002, "l": -0.030, "h":  0.030},
    "manuf_cement":        {"c":  0.012, "l": -0.020, "h":  0.030},
    "manuf_food":          {"c":  0.015, "l": -0.010, "h":  0.035},
    "manuf_metal":         {"c":  0.008, "l": -0.050, "h":  0.030},
    "manuf_nonmetal":      {"c":  0.013, "l": -0.020, "h":  0.035},
    "manuf_other":         {"c":  0.010, "l": -0.020, "h":  0.030},
    "res_comm":            {"c":  0.008, "l": -0.010, "h":  0.020},
    "transport":           {"c":  0.010, "l": -0.020, "h":  0.030},
    "total_state":         {"c":  0.000, "l": -0.010, "h":  0.015},
}

def proj(base, rate_key, n, bound="c"):
    r = CAGR[rate_key][bound]
    return base * (1 + r) ** n


# ─── 2015 base values for F-only transport segments ──────────────────────
TRANSPORT_BASE = {
    "Road":          5577.9,
    "Water nav":       94.7,
    "Railways":        41.5,
    "Civil aviation":  17.4,
}

ELEC_TAXABLE_SHARE = 0.179
ELEC_BASE_TOTAL    = 7128.0
ELEC_BASE_TAXABLE  = ELEC_BASE_TOTAL * ELEC_TAXABLE_SHARE   # 1275.9
ELEC_BASE_NG       = ELEC_BASE_TOTAL * (1 - ELEC_TAXABLE_SHARE)  # 5852.1

# 2015 base for in-scope manufacturing subsectors (from 01_clean outputs)
MANUF_BASE = {
    "Cement & lime":          408.8 * 0.671,   # combustion share only (~67%); process in ETS
    "Food & beverage":        271.0,
    "Metallurgical":          289.0,
    "Non-metallic minerals":  702.0,
    "Other industries":       424.0,
    "Petrochem":               13.3,
    "Chemical":                 0.1,
    "Hazardous waste":          0.1,
}
RES_COMM_BASE = {
    "Residential":   181.4,
    "Commercial":    13.1,
    "Agri/forestry": 47.5,
}
BIOGAS_BASE = 8.7   # energy generation plants (S-only)

# ─── Build Venn segments per year ────────────────────────────────────────

def build_segments(year):
    n = year - BASE_YEAR

    # S ∩ F ∩ E  — electricity diesel, cement combustion, metallurgical
    sfE_c = (proj(ELEC_BASE_TAXABLE, "electricity_taxable", n, "c")
             + proj(MANUF_BASE["Cement & lime"],  "manuf_cement", n, "c")
             + proj(MANUF_BASE["Metallurgical"],  "manuf_metal",  n, "c"))
    sfE_l = (proj(ELEC_BASE_TAXABLE, "electricity_taxable", n, "l")
             + proj(MANUF_BASE["Cement & lime"],  "manuf_cement", n, "l")
             + proj(MANUF_BASE["Metallurgical"],  "manuf_metal",  n, "l"))
    sfE_h = (proj(ELEC_BASE_TAXABLE, "electricity_taxable", n, "h")
             + proj(MANUF_BASE["Cement & lime"],  "manuf_cement", n, "h")
             + proj(MANUF_BASE["Metallurgical"],  "manuf_metal",  n, "h"))

    # S ∩ F only — remaining in-scope manufacturing + res/comm/agri
    sf_c = sum(proj(v, "manuf_food",    n, "c") if k == "Food & beverage"   else
               proj(v, "manuf_nonmetal",n, "c") if k == "Non-metallic minerals" else
               proj(v, "manuf_other",   n, "c")
               for k, v in MANUF_BASE.items()
               if k not in ("Cement & lime", "Metallurgical"))
    sf_c += sum(proj(v, "res_comm", n, "c") for v in RES_COMM_BASE.values())

    sf_l = sum(proj(v, "manuf_food",    n, "l") if k == "Food & beverage"   else
               proj(v, "manuf_nonmetal",n, "l") if k == "Non-metallic minerals" else
               proj(v, "manuf_other",   n, "l")
               for k, v in MANUF_BASE.items()
               if k not in ("Cement & lime", "Metallurgical"))
    sf_l += sum(proj(v, "res_comm", n, "l") for v in RES_COMM_BASE.values())

    sf_h = sum(proj(v, "manuf_food",    n, "h") if k == "Food & beverage"   else
               proj(v, "manuf_nonmetal",n, "h") if k == "Non-metallic minerals" else
               proj(v, "manuf_other",   n, "h")
               for k, v in MANUF_BASE.items()
               if k not in ("Cement & lime", "Metallurgical"))
    sf_h += sum(proj(v, "res_comm", n, "h") for v in RES_COMM_BASE.values())

    # S only — biogas / energy generation plants
    s_only_c = proj(BIOGAS_BASE, "manuf_other", n, "c")
    s_only_l = proj(BIOGAS_BASE, "manuf_other", n, "l")
    s_only_h = proj(BIOGAS_BASE, "manuf_other", n, "h")

    # F only — road + other transport (not in S scope, not in ETS)
    f_only_c = sum(proj(v, "transport", n, "c") for v in TRANSPORT_BASE.values())
    f_only_l = sum(proj(v, "transport", n, "l") for v in TRANSPORT_BASE.values())
    f_only_h = sum(proj(v, "transport", n, "h") for v in TRANSPORT_BASE.values())

    # E only — NG electricity (not subject to either tax)
    e_only_c = proj(ELEC_BASE_NG, "electricity_ng", n, "c")
    e_only_l = proj(ELEC_BASE_NG, "electricity_ng", n, "l")
    e_only_h = proj(ELEC_BASE_NG, "electricity_ng", n, "h")

    # S ∩ E only — none (no ETS-covered source in state scope that isn't also in federal scope)
    se_c = se_l = se_h = 0.0

    # F ∩ E only — none (federal tax does not cover NG; ETS NG fraction not taxed federally)
    fe_c = fe_l = fe_h = 0.0

    # ── Derived totals ──────────────────────────────────────────────────
    S_c = sfE_c + sf_c + s_only_c
    S_l = min(sfE_l + sf_l + s_only_l, sfE_h + sf_h + s_only_h)
    S_h = max(sfE_l + sf_l + s_only_l, sfE_h + sf_h + s_only_h)

    F_c = sfE_c + sf_c + f_only_c
    F_l = min(sfE_l + sf_l + f_only_l, sfE_h + sf_h + f_only_h)
    F_h = max(sfE_l + sf_l + f_only_l, sfE_h + sf_h + f_only_h)

    E_c = sfE_c + e_only_c
    E_l = min(sfE_l + e_only_l, sfE_h + e_only_h)
    E_h = max(sfE_l + e_only_l, sfE_h + e_only_h)

    # Union = all distinct segments
    union_c = sfE_c + sf_c + s_only_c + f_only_c + e_only_c
    union_l = min(
        sfE_l + sf_l + s_only_l + f_only_l + e_only_l,
        sfE_h + sf_h + s_only_h + f_only_h + e_only_h,
    )
    union_h = max(
        sfE_l + sf_l + s_only_l + f_only_l + e_only_l,
        sfE_h + sf_h + s_only_h + f_only_h + e_only_h,
    )

    total_c = proj(TOTAL_2015, "total_state", n, "c")
    total_l = proj(TOTAL_2015, "total_state", n, "l")
    total_h = proj(TOTAL_2015, "total_state", n, "h")

    def pct(val, tot):
        return round(val / tot * 100, 1)

    return {
        "year": year,
        # ── 7 Venn segments ──────────────────────────────────────────
        "S∩F∩E_c": sfE_c, "S∩F∩E_l": sfE_l, "S∩F∩E_h": sfE_h,
        "S∩F_only_c": sf_c, "S∩F_only_l": sf_l, "S∩F_only_h": sf_h,
        "S_only_c": s_only_c, "S_only_l": s_only_l, "S_only_h": s_only_h,
        "F_only_c": f_only_c, "F_only_l": f_only_l, "F_only_h": f_only_h,
        "E_only_c": e_only_c, "E_only_l": e_only_l, "E_only_h": e_only_h,
        "S∩E_only_c": 0.0, "F∩E_only_c": 0.0,
        # ── Instrument totals ────────────────────────────────────────
        "S_total_c": S_c, "S_total_l": S_l, "S_total_h": S_h,
        "F_total_c": F_c, "F_total_l": F_l, "F_total_h": F_h,
        "E_total_c": E_c, "E_total_l": E_l, "E_total_h": E_h,
        # ── Union ────────────────────────────────────────────────────
        "union_c": union_c, "union_l": union_l, "union_h": union_h,
        "total_state_c": total_c,
        # ── Coverage shares ──────────────────────────────────────────
        "S_pct_c":     pct(S_c,     total_c),
        "F_pct_c":     pct(F_c,     total_c),
        "E_pct_c":     pct(E_c,     total_c),
        "union_pct_c": pct(union_c, total_c),
        "s_only_pct_c": pct(s_only_c, total_c),
    }


segs = [build_segments(y) for y in TARGET_YEARS]
df_segs = pd.DataFrame(segs)

# ─────────────────────────────────────────────────────────────────────────
# Publication table
# ─────────────────────────────────────────────────────────────────────────

rows = []
for s in segs:
    yr = s["year"]

    def r(label, c, l, h, note=""):
        rows.append({
            "Year": yr, "Category": label,
            "Central (GgCO₂e)": round(c, 0),
            "Low (GgCO₂e)":     round(l, 0),
            "High (GgCO₂e)":    round(h, 0),
            "Share of state (%)": round(c / s["total_state_c"] * 100, 1),
            "Note": note,
        })

    r("— INSTRUMENT TOTALS (gross, before dedup) —", np.nan, np.nan, np.nan)
    r("Colima state carbon tax (S)",
      s["S_total_c"], s["S_total_l"], s["S_total_h"],
      "Stationary combustion; taxed fuels only (NG exempt)")
    r("Mexico federal carbon tax (F)",
      s["F_total_c"], s["F_total_l"], s["F_total_h"],
      "All fuels incl. transport; upstream levy; NG exempt")
    r("Mexico Pilot ETS (E)",
      s["E_total_c"], s["E_total_l"], s["E_total_h"],
      "Large emitters ≥25,000 tCO₂e/yr; non-binding pilot; legal scope only")

    r("— VENN DECOMPOSITION (7 segments) —", np.nan, np.nan, np.nan)
    r("S ∩ F ∩ E  [all three]",
      s["S∩F∩E_c"], s["S∩F∩E_l"], s["S∩F∩E_h"],
      "Electricity diesel+FO, cement combustion, metallurgical")
    r("S ∩ F only  [state + federal, not ETS]",
      s["S∩F_only_c"], s["S∩F_only_l"], s["S∩F_only_h"],
      "Manuf (food, non-metallic, other), residential, commercial, agri")
    r("S only  [state tax only — not federal, not ETS]",
      s["S_only_c"], s["S_only_l"], s["S_only_h"],
      "Biogas/energy generation plants; non-fossil fuel — exempt from IEPS federal tax")
    r("F only  [federal only — not state, not ETS]",
      s["F_only_c"], s["F_only_l"], s["F_only_h"],
      "Road, water, rail, aviation transport fuels")
    r("E only  [ETS only — not taxed by either carbon tax]",
      s["E_only_c"], s["E_only_l"], s["E_only_h"],
      "NG fraction at Manzanillo thermoelectric; exempt from both taxes")
    r("S ∩ E only  [state + ETS, not federal]",
      0.0, 0.0, 0.0, "Empty — all ETS sources in state scope are also in federal scope")
    r("F ∩ E only  [federal + ETS, not state]",
      0.0, 0.0, 0.0, "Empty — federal tax does not cover NG; NG is E-only")

    r("— KEY DERIVED METRICS —", np.nan, np.nan, np.nan)
    r("Net S-only: Colima state tax NOT covered by F or E",
      s["S_only_c"], s["S_only_l"], s["S_only_h"],
      "Biogas only; <0.1% of state. State tax adds near-zero unique coverage vs federal tax")
    r("Cumulative deduplicated union  S ∪ F ∪ E",
      s["union_c"], s["union_l"], s["union_h"],
      "All emissions covered by at least one of the three instruments")
    r("Total Colima state emissions (context)",
      s["total_state_c"], np.nan, np.nan,
      "IMADES 2015 base extrapolated at blended sector CAGR")

df_table = pd.DataFrame(rows)
table_path = os.path.join(TABLES_DIR, "colima_overlap_full_table.csv")
df_table.to_csv(table_path, index=False)
log.info(f"Table written: {table_path}")


# ─────────────────────────────────────────────────────────────────────────
# FIGURE 1: Stacked bar — Venn segment breakdown (2025 & 2026)
# ─────────────────────────────────────────────────────────────────────────

# World Bank / State & Trends colour palette
PALETTE = {
    "S∩F∩E":     "#1A3C5E",   # dark navy
    "S∩F only":  "#2F6DAE",   # WB blue
    "S only":    "#6BAED6",   # light blue
    "F only":    "#F7A600",   # WB amber
    "E only":    "#C0392B",   # deep red
    "Uncovered": "#D9D9D9",   # grey
}

fig, axes = plt.subplots(1, 2, figsize=(13, 7), sharey=True)
fig.patch.set_facecolor("white")

for ax, s in zip(axes, segs):
    yr   = s["year"]
    tot  = s["total_state_c"]

    # Stacked segments (bottom to top: S∩F∩E, S∩F, S_only, F_only, E_only, uncovered)
    seg_vals = [
        ("S∩F∩E",     s["S∩F∩E_c"]),
        ("S∩F only",  s["S∩F_only_c"]),
        ("S only",    s["S_only_c"]),
        ("F only",    s["F_only_c"]),
        ("E only",    s["E_only_c"]),
        ("Uncovered", tot - s["union_c"]),
    ]

    bottom = 0
    bars = {}
    for label, val in seg_vals:
        bar = ax.bar(0.5, val, bottom=bottom, width=0.45,
                     color=PALETTE[label], edgecolor="white", linewidth=0.8)
        bars[label] = (bottom, val)
        bottom += val

    # Error bars for union (total covered)
    ax.errorbar(0.5, s["union_c"],
                yerr=[[s["union_c"] - s["union_l"]],
                      [s["union_h"] - s["union_c"]]],
                fmt="none", color="#333333", capsize=6, linewidth=1.5,
                label="Union uncertainty range")

    # Annotation inside each segment (if large enough)
    cumulative = 0
    for label, val in seg_vals:
        mid = cumulative + val / 2
        pct = val / tot * 100
        if val > 200:
            ax.text(0.5, mid, f"{val:,.0f}\n({pct:.1f}%)",
                    ha="center", va="center", fontsize=7.5,
                    color="white" if PALETTE[label] in ("#1A3C5E","#2F6DAE","#C0392B","#F7A600") else "#333",
                    fontweight="bold")
        cumulative += val

    ax.set_xlim(0, 1)
    ax.set_title(str(yr), fontsize=14, fontweight="bold", pad=10)
    ax.set_xticks([])
    ax.tick_params(axis="y", labelsize=9)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["bottom"].set_visible(False)

axes[0].set_ylabel("GgCO₂e", fontsize=10)
axes[0].set_ylim(0, max(s["total_state_c"] for s in segs) * 1.08)

# Shared legend
legend_patches = [
    mpatches.Patch(color=PALETTE["S∩F∩E"],    label="S ∩ F ∩ E   (all three instruments)"),
    mpatches.Patch(color=PALETTE["S∩F only"], label="S ∩ F only  (state + federal tax; not ETS)"),
    mpatches.Patch(color=PALETTE["S only"],   label="S only       (state tax only — biogas; <0.1%)"),
    mpatches.Patch(color=PALETTE["F only"],   label="F only        (federal tax only — transport)"),
    mpatches.Patch(color=PALETTE["E only"],   label="E only        (Pilot ETS only — NG electricity)"),
    mpatches.Patch(color=PALETTE["Uncovered"],label="Not covered by any instrument"),
]
fig.legend(handles=legend_patches, loc="lower center", ncol=2,
           fontsize=8.5, frameon=True, edgecolor="#cccccc",
           bbox_to_anchor=(0.5, -0.08))

fig.suptitle(
    "Colima Carbon Pricing: Venn Segment Decomposition\n"
    "Colima State Tax (S)  ×  Mexico Federal Carbon Tax (F)  ×  Mexico Pilot ETS (E)",
    fontsize=12, fontweight="bold", y=1.01
)

note = (
    "Notes: S = Colima state carbon tax (stationary combustion; NG exempt). "
    "F = Mexico federal carbon tax (upstream fuel levy; NG exempt). "
    "E = Mexico Pilot ETS (≥25,000 tCO₂e/yr; non-binding pilot — legal scope shown).\n"
    "Error bars on stacked total show low–high uncertainty range. "
    "Base year 2015 (IMADES/Under2 Coalition inventory); extrapolated via INECC national sector CAGRs. "
    "Tier 3/4 estimation. Source: World Bank Climate Change Group."
)
fig.text(0.5, -0.13, note, ha="center", fontsize=7.5, color="#555555",
         wrap=True, style="italic")

plt.tight_layout()
fig1_path = os.path.join(FIGS_DIR, "colima_venn_segments_2025_2026.png")
plt.savefig(fig1_path, dpi=180, bbox_inches="tight", facecolor="white")
plt.close()
log.info(f"Figure 1 saved: {fig1_path}")


# ─────────────────────────────────────────────────────────────────────────
# FIGURE 2: Summary coverage chart — instrument totals + union
# ─────────────────────────────────────────────────────────────────────────

fig2, ax2 = plt.subplots(figsize=(11, 6))
fig2.patch.set_facecolor("white")

INST_COLORS = {
    "Colima\nState Tax (S)":    "#2F6DAE",
    "Federal\nCarbon Tax (F)":  "#F7A600",
    "Pilot ETS (E)\n(legal)":   "#C0392B",
    "Deduplicated\nUnion S∪F∪E":"#1A3C5E",
    "Total State\nEmissions":   "#AAAAAA",
}

x_labels = list(INST_COLORS.keys())
n_groups  = len(TARGET_YEARS)
x         = np.arange(len(x_labels))
width     = 0.3
offsets   = [-width/2, width/2]

for i, s in enumerate(segs):
    vals = [
        (s["S_total_c"], s["S_total_l"], s["S_total_h"]),
        (s["F_total_c"], s["F_total_l"], s["F_total_h"]),
        (s["E_total_c"], s["E_total_l"], s["E_total_h"]),
        (s["union_c"],   s["union_l"],   s["union_h"]),
        (s["total_state_c"], s["total_state_c"], s["total_state_c"]),
    ]
    for j, (lbl, col) in enumerate(INST_COLORS.items()):
        c, lo, hi = vals[j]
        bar = ax2.bar(x[j] + offsets[i], c, width,
                      color=col, alpha=0.85 if i == 0 else 1.0,
                      edgecolor="white", linewidth=0.6,
                      label=f"{s['year']}" if j == 0 else "")
        if not np.isnan(lo):
            ax2.errorbar(x[j] + offsets[i], c,
                         yerr=[[c - lo], [hi - c]],
                         fmt="none", color="#333", capsize=4, linewidth=1.2)
        # Value label on bar
        ax2.text(x[j] + offsets[i], c + 200, f"{c:,.0f}",
                 ha="center", va="bottom", fontsize=7.5, rotation=0,
                 color="#333333")

ax2.set_xticks(x)
ax2.set_xticklabels(x_labels, fontsize=9)
ax2.set_ylabel("GgCO₂e", fontsize=10)
ax2.set_title(
    "Colima Carbon Pricing Coverage: Instrument Totals and Deduplicated Union\n"
    "2025 vs 2026", fontsize=11, fontweight="bold"
)
ax2.spines["top"].set_visible(False)
ax2.spines["right"].set_visible(False)
ax2.tick_params(axis="y", labelsize=9)
ax2.set_ylim(0, max(s["total_state_c"] for s in segs) * 1.18)

# Year legend
handles = [
    mpatches.Patch(facecolor="#888888", alpha=0.85, label="2025"),
    mpatches.Patch(facecolor="#888888", alpha=1.0,  label="2026"),
]
ax2.legend(handles=handles, fontsize=9, loc="upper right", frameon=True)

note2 = (
    "Notes: Instrument totals are gross (un-deduplicated). Union = S ∪ F ∪ E (deduplicated, "
    "inclusion–exclusion). Pilot ETS is non-binding; legal scope shown. "
    "Error bars show low–high uncertainty range. Base year 2015; INECC sector CAGRs applied. "
    "Tier 3/4. Source: World Bank Climate Change Group."
)
ax2.text(0.5, -0.14, note2, transform=ax2.transAxes,
         ha="center", fontsize=7.5, color="#555555", style="italic")

plt.tight_layout()
fig2_path = os.path.join(FIGS_DIR, "colima_coverage_summary_2025_2026.png")
plt.savefig(fig2_path, dpi=180, bbox_inches="tight", facecolor="white")
plt.close()
log.info(f"Figure 2 saved: {fig2_path}")


# ─────────────────────────────────────────────────────────────────────────
# Print key results to console
# ─────────────────────────────────────────────────────────────────────────

log.info("\n" + "="*65)
log.info("KEY RESULTS — COLIMA CARBON PRICING OVERLAP")
log.info("="*65)
for s in segs:
    tot = s["total_state_c"]
    log.info(f"\n{'─'*50}  {s['year']}  {'─'*5}")
    log.info(f"  Total state emissions (central): {tot:,.0f} GgCO₂e")
    log.info(f"")
    log.info(f"  GROSS INSTRUMENT COVERAGE (before dedup):")
    log.info(f"    Colima state tax (S):   {s['S_total_c']:6,.0f}  [{s['S_total_l']:,.0f}–{s['S_total_h']:,.0f}]  "
             f"({s['S_total_c']/tot*100:.1f}% of state)")
    log.info(f"    Federal carbon tax (F): {s['F_total_c']:6,.0f}  [{s['F_total_l']:,.0f}–{s['F_total_h']:,.0f}]  "
             f"({s['F_total_c']/tot*100:.1f}% of state)")
    log.info(f"    Pilot ETS (E, legal):   {s['E_total_c']:6,.0f}  [{s['E_total_l']:,.0f}–{s['E_total_h']:,.0f}]  "
             f"({s['E_total_c']/tot*100:.1f}% of state)")
    log.info(f"")
    log.info(f"  VENN SEGMENTS:")
    log.info(f"    S∩F∩E  (all three):    {s['S∩F∩E_c']:6,.0f}  [{s['S∩F∩E_l']:,.0f}–{s['S∩F∩E_h']:,.0f}]  "
             f"({s['S∩F∩E_c']/tot*100:.1f}%)")
    log.info(f"    S∩F only:              {s['S∩F_only_c']:6,.0f}  [{s['S∩F_only_l']:,.0f}–{s['S∩F_only_h']:,.0f}]  "
             f"({s['S∩F_only_c']/tot*100:.1f}%)")
    log.info(f"    S only (state tax, unique): {s['S_only_c']:4,.0f}  [{s['S_only_l']:,.0f}–{s['S_only_h']:,.0f}]  "
             f"({s['S_only_c']/tot*100:.2f}%)")
    log.info(f"    F only (transport):    {s['F_only_c']:6,.0f}  [{s['F_only_l']:,.0f}–{s['F_only_h']:,.0f}]  "
             f"({s['F_only_c']/tot*100:.1f}%)")
    log.info(f"    E only (NG electricity):{s['E_only_c']:5,.0f}  [{s['E_only_l']:,.0f}–{s['E_only_h']:,.0f}]  "
             f"({s['E_only_c']/tot*100:.1f}%)")
    log.info(f"")
    log.info(f"  KEY METRICS:")
    log.info(f"    Net S-ONLY (state tax unique, not F or E):")
    log.info(f"      {s['S_only_c']:,.0f} GgCO₂e  ({s['S_only_c']/tot*100:.2f}% of state)")
    log.info(f"      → Biogas plants only; effectively zero unique coverage")
    log.info(f"")
    log.info(f"    Deduplicated UNION S∪F∪E:")
    log.info(f"      {s['union_c']:,.0f} GgCO₂e  [{s['union_l']:,.0f}–{s['union_h']:,.0f}]")
    log.info(f"      ({s['union_c']/tot*100:.1f}% of state emissions)")

log.info("\n" + "="*65)
log.info("03_outputs.py complete.")
