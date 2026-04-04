"""
03_outputs.py — Tables and publication-quality figures
=======================================================
Case:            Mexico Federal Carbon Tax × Mexico Pilot ETS (SCE Fase Piloto)
Estimation tier: Tier 2 / Tier 3

Reads from:  outputs/tables/results_*.csv
Writes to:   outputs/tables/*.csv   (formatted publication tables)
             outputs/figures/*.png  (publication figures, 300 dpi)

Outputs
-------
Tables
  T1_ctax_coverage_2014_2024.csv       Carbon tax coverage, Mt + share, 2014-2024
  T2_ets_coverage_2020_2024.csv        ETS coverage, Mt + share, 2020-2024
  T3_overlap_summary_2020_2023.csv     Full overlap-period summary with all shares
  T4_sector_breakdown_2023.csv         ETS sector detail, 2023

Figures
  F1_ctax_coverage_share.png           Carbon tax coverage share 2014-2024 (line + band)
  F2_stacked_coverage_shares.png       Stacked area: ctax-only / overlap / ets-only (% national)
  F3_uncertainty_waterfall_2023.png    Uncertainty waterfall, 2023 base year

Run: python scripts/03_outputs.py
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.ticker as mticker
from pathlib import Path

ROOT    = Path(__file__).resolve().parent.parent
TABLES  = ROOT / "outputs" / "tables"
FIGURES = ROOT / "outputs" / "figures"
FIGURES.mkdir(parents=True, exist_ok=True)

# ── Publication style ──────────────────────────────────────────────────────────
WB_BLUE   = "#003087"   # World Bank blue
WB_CYAN   = "#009CA7"   # World Bank teal
WB_ORANGE = "#F05023"   # World Bank orange
WB_YELLOW = "#FDB714"   # World Bank yellow
WB_GREY   = "#6D6E71"   # neutral grey
WB_LGREY  = "#D9D9D6"   # light grey (uncertainty bands)

plt.rcParams.update({
    "font.family":       "sans-serif",
    "font.size":         9,
    "axes.titlesize":    10,
    "axes.titleweight":  "bold",
    "axes.labelsize":    9,
    "axes.spines.top":   False,
    "axes.spines.right": False,
    "xtick.labelsize":   8,
    "ytick.labelsize":   8,
    "legend.fontsize":   8,
    "legend.frameon":    False,
    "figure.dpi":        150,
    "savefig.dpi":       300,
    "savefig.bbox":      "tight",
})

SOURCE_NOTE = (
    "Sources: INECC INEGYCEI 2014–2024; SEMARNAT SCE allocation table (DOF Nov 2019); "
    "IEA Mexico energy statistics; SENER BNE 2024.\n"
    "Note: Coverage is CO₂-only (combustion + process). National denominator is all-gas "
    "CO₂e Sin UTCUTS (INECC). Shares are conservative — covered CH₄ and N₂O not included "
    "in numerator.\nEstimation tier: Tier 2 (ETS) / Tier 3 (NG-share uncertainty). "
    "Uncertainty bounds reflect NG share parameter ranges; ETS allocation uncertainty not shown."
)

ALL_YEARS     = [str(y) for y in range(2014, 2025)]
CTAX_YEARS    = ALL_YEARS
ETS_YEARS     = [str(y) for y in range(2020, 2025)]
OVERLAP_YEARS = [str(y) for y in range(2020, 2024)]


# ══════════════════════════════════════════════════════════════════════════════
# LOAD DATA
# ══════════════════════════════════════════════════════════════════════════════

def load_results():
    ctax_full = pd.read_csv(TABLES / "results_ctax_shares_full.csv",    index_col="year")
    ets        = pd.read_csv(TABLES / "results_ets_coverage.csv",        index_col="year")
    overlap    = pd.read_csv(TABLES / "results_overlap.csv",             index_col="year")
    summary    = pd.read_csv(TABLES / "results_summary.csv",             index_col="year")
    sector_det = pd.read_csv(TABLES / "results_ets_sector_detail.csv")
    ctax_full.index = ctax_full.index.astype(str)
    ets.index        = ets.index.astype(str)
    overlap.index    = overlap.index.astype(str)
    summary.index    = summary.index.astype(str)
    return ctax_full, ets, overlap, summary, sector_det


# ══════════════════════════════════════════════════════════════════════════════
# TABLES
# ══════════════════════════════════════════════════════════════════════════════

def build_tables(ctax_full, ets, overlap, summary, sector_det):

    # ── T1: Carbon tax coverage 2014-2024 ─────────────────────────────────
    t1 = pd.DataFrame({
        "Year":                      ctax_full.index,
        "National GHG (MtCO₂e)":     ctax_full["national_ghg_mt"].round(1),
        "Carbon tax coverage (MtCO₂)": ctax_full["ctax_coverage_point_mt"].round(1),
        "Low (MtCO₂)":               ctax_full["ctax_coverage_low_mt"].round(1),
        "High (MtCO₂)":              ctax_full["ctax_coverage_high_mt"].round(1),
        "Share of national GHG (%)": (ctax_full["ctax_abs_share_point"] * 100).round(1),
        "Share low (%)":             (ctax_full["ctax_abs_share_low"]   * 100).round(1),
        "Share high (%)":            (ctax_full["ctax_abs_share_high"]  * 100).round(1),
    })
    t1.to_csv(TABLES / "T1_ctax_coverage_2014_2024.csv", index=False)
    print("Saved: T1_ctax_coverage_2014_2024.csv")

    # ── T2: ETS coverage 2020-2024 ────────────────────────────────────────
    # Merge with national total from summary for overlap years; use ctax_full for 2024
    nat = pd.concat([
        ctax_full["national_ghg_mt"].rename("nat"),
    ])
    ets_t2 = ets.copy()
    nat_series = ctax_full["national_ghg_mt"]
    ets_t2["national_ghg_mt"] = [nat_series.get(y, np.nan) for y in ets_t2.index]
    ets_t2["share_pct"] = ets_t2["ets_total_mt"] / ets_t2["national_ghg_mt"] * 100

    t2 = pd.DataFrame({
        "Year":                       ets_t2.index,
        "National GHG (MtCO₂e)":      ets_t2["national_ghg_mt"].round(1),
        "ETS total coverage (MtCO₂)": ets_t2["ets_total_mt"].round(1),
        "  of which: combustion":     ets_t2["ets_comb_mt"].round(1),
        "  of which: process CO₂":   ets_t2["ets_proc_mt"].round(1),
        "  of which: NG combustion":  ets_t2["ng_in_ets_point_mt"].round(1),
        "Share of national GHG (%)":  ets_t2["share_pct"].round(1),
        "Extrapolated (2022+)":       ["No","No","Yes","Yes","Yes"],
    })
    t2.to_csv(TABLES / "T2_ets_coverage_2020_2024.csv", index=False)
    print("Saved: T2_ets_coverage_2020_2024.csv")

    # ── T3: Full overlap-period summary 2020-2023 ─────────────────────────
    t3 = pd.DataFrame({
        "Year":                             summary.index,
        "National GHG (MtCO₂e)":           summary["national_ghg_mt"].round(1),
        # Absolute volumes
        "Carbon tax coverage (MtCO₂)":     summary["ctax_point_mt"].round(1),
        "ETS coverage (MtCO₂)":            summary["ets_point_mt"].round(1),
        "Overlap (MtCO₂) — point":         summary["overlap_point_mt"].round(1),
        "Overlap (MtCO₂) — low":           summary["overlap_low_mt"].round(1),
        "Overlap (MtCO₂) — high":          summary["overlap_high_mt"].round(1),
        "Net combined coverage (MtCO₂)":   summary["dedup_point_mt"].round(1),
        # Absolute shares (no deduplication)
        "Carbon tax abs. share (%)":        (summary["ctax_abs_share"]    * 100).round(1),
        "ETS abs. share (%)":               (summary["ets_abs_share"]     * 100).round(1),
        "Overlap abs. share (%)":           (summary["overlap_abs_share"] * 100).round(1),
        # Net shares (post-deduplication)
        "Net combined share (%) — point":   (summary["combined_net_share_point"] * 100).round(1),
        "Net combined share (%) — low":     (summary["combined_net_share_low"]   * 100).round(1),
        "Net combined share (%) — high":    (summary["combined_net_share_high"]  * 100).round(1),
        "  of which: ctax-only (%)":        (summary["ctax_net_share"]    * 100).round(1),
        "  of which: overlap (%)":          (summary["overlap_net_share"] * 100).round(1),
        "  of which: ets-only (%)":         (summary["ets_net_share"]     * 100).round(1),
    })
    t3.to_csv(TABLES / "T3_overlap_summary_2020_2023.csv", index=False)
    print("Saved: T3_overlap_summary_2020_2023.csv")

    # ── T4: ETS sector breakdown 2023 ─────────────────────────────────────
    # English names alongside official Spanish designations from SEMARNAT DOF
    SECTOR_NAMES = {
        "electricidad":      ("Electricity generation",          "Generación de electricidad"),
        "petroleo_gas":      ("Oil and gas (upstream)",          "Petróleo y Gas"),
        "refinacion":        ("Petroleum refining",              "Refinación"),
        "cemento":           ("Cement",                          "Cemento"),
        "hierro_acero":      ("Iron and steel",                  "Hierro y Acero"),
        "industria_quimica": ("Chemical industry",               "Industria Química"),
        "petroquimica":      ("Petrochemicals",                  "Petroquímica"),
        "cal":               ("Lime",                            "Cal"),
        "vidrio":            ("Glass",                           "Vidrio"),
        "mineria":           ("Mining",                          "Minería"),
        "papel":             ("Pulp and paper",                  "Papel"),
        "alimentos_bebidas": ("Food and beverages",              "Alimentos y Bebidas"),
        "otros":             ("Other industries",                "Otros"),
    }

    det_2023 = sector_det[sector_det["year"] == "2023"].copy()
    if len(det_2023) == 0:
        det_2023 = sector_det[sector_det["year"] == 2023].copy()

    det_2023 = det_2023.sort_values("alloc_total_mt", ascending=False)
    det_2023["non_ng_overlap_mt"] = det_2023["alloc_comb_mt"] * (1 - det_2023["ng_share_point"])
    det_2023["sector_en"] = det_2023["sector"].map(lambda s: SECTOR_NAMES.get(s, (s, s))[0])
    det_2023["sector_es"] = det_2023["sector"].map(lambda s: SECTOR_NAMES.get(s, (s, s))[1])

    t4 = pd.DataFrame({
        "ETS sector (English)":            det_2023["sector_en"],
        "ETS sector (Spanish — DOF)":      det_2023["sector_es"],
        "Total allocation (MtCO₂)":        det_2023["alloc_total_mt"].round(2),
        "  Combustion component (MtCO₂)":  det_2023["alloc_comb_mt"].round(2),
        "  Process CO₂ (MtCO₂)":           det_2023["alloc_proc_mt"].round(2),
        "NG share — central (%)":          (det_2023["ng_share_point"] * 100).round(1),
        "NG CO₂ in ETS (MtCO₂)":          det_2023["ng_co2_in_ets_point_mt"].round(2),
        "Overlap contribution (MtCO₂)":    det_2023["non_ng_overlap_mt"].round(2),
        "Extrapolated (2022–2024)":        det_2023["extrapolated"].map({True: "Yes", False: "No"}),
    })
    t4.to_csv(TABLES / "T4_sector_breakdown_2023.csv", index=False)
    print("Saved: T4_sector_breakdown_2023.csv")

    return t1, t2, t3, t4


# ══════════════════════════════════════════════════════════════════════════════
# FIGURE 1 — Carbon tax coverage share 2014-2024
# ══════════════════════════════════════════════════════════════════════════════

def fig1_ctax_coverage_share(ctax_full):
    """
    Line chart: carbon tax coverage as % of national GHG, 2014-2024.
    Uncertainty band from NG share low/high.
    Vertical dashed line at 2020 to mark ETS pilot start.
    """
    years = ctax_full.index.astype(int).tolist()
    pt    = ctax_full["ctax_abs_share_point"] * 100
    lo    = ctax_full["ctax_abs_share_low"]   * 100
    hi    = ctax_full["ctax_abs_share_high"]  * 100

    fig, ax = plt.subplots(figsize=(8, 4))

    ax.fill_between(years, lo, hi, color=WB_CYAN, alpha=0.20, label="Uncertainty range (NG share)")
    ax.plot(years, pt, color=WB_CYAN, linewidth=2.0, marker="o", markersize=4,
            label="Carbon tax coverage (point estimate)")

    # Annotate each point
    for yr, v in zip(years, pt):
        ax.annotate(f"{v:.1f}%", (yr, v), textcoords="offset points",
                    xytext=(0, 7), ha="center", fontsize=7, color=WB_GREY)

    ax.axvline(2020, color=WB_GREY, linewidth=0.8, linestyle="--")
    ax.text(2020.1, ax.get_ylim()[0] + 1, "ETS pilot\nstarts", fontsize=7,
            color=WB_GREY, va="bottom")

    ax.set_xlim(2013.5, 2024.5)
    ax.set_ylim(25, 45)
    ax.set_xticks(years)
    ax.set_xlabel("Year")
    ax.set_ylabel("% of national GHG (Sin UTCUTS)")
    ax.set_title("Mexico Federal Carbon Tax: Share of National GHG Emissions, 2014–2024")
    ax.yaxis.set_major_formatter(mticker.FormatStrFormatter("%.0f%%"))
    ax.legend(loc="upper right")

    fig.text(0.0, -0.08, SOURCE_NOTE, fontsize=6, color=WB_GREY,
             transform=ax.transAxes, wrap=True, va="top")

    fig.tight_layout()
    fig.savefig(FIGURES / "F1_ctax_coverage_share.png")
    plt.close(fig)
    print("Saved: F1_ctax_coverage_share.png")


# ══════════════════════════════════════════════════════════════════════════════
# FIGURE 2 — Stacked coverage share composition 2020-2023
# ══════════════════════════════════════════════════════════════════════════════

def fig2_stacked_coverage_shares(summary):
    """
    Grouped stacked bars showing the three components of net combined coverage
    as % of national GHG, plus the national total covered on secondary axis.

    Stacking order (bottom to top):
      1. Carbon-tax-only (not in ETS)
      2. Overlap (in both — counted once)
      3. ETS-only (not in carbon tax)

    Error bars on the total combined bar show uncertainty range.
    """
    years = summary.index.tolist()
    x     = np.arange(len(years))
    w     = 0.55

    ctax_only = summary["ctax_net_share"]  * 100
    ov        = summary["overlap_net_share"] * 100
    ets_only  = summary["ets_net_share"]   * 100
    net_pt    = summary["combined_net_share_point"] * 100
    net_lo    = summary["combined_net_share_low"]   * 100
    net_hi    = summary["combined_net_share_high"]  * 100

    fig, ax = plt.subplots(figsize=(8, 5))

    b1 = ax.bar(x, ctax_only, w, color=WB_CYAN,   label="Carbon tax only")
    b2 = ax.bar(x, ov,        w, bottom=ctax_only,
                color=WB_YELLOW, label="Overlap (counted once)")
    b3 = ax.bar(x, ets_only,  w, bottom=ctax_only + ov,
                color=WB_BLUE,   label="ETS only")

    # Error bars for combined net total
    err_lo = net_pt - net_lo
    err_hi = net_hi - net_pt
    ax.errorbar(x, net_pt,
                yerr=[err_lo, err_hi],
                fmt="none", color=WB_ORANGE, capsize=5, linewidth=1.5,
                label="Combined net: uncertainty range")

    # Label each bar total
    for xi, (pt, lo, hi) in enumerate(zip(net_pt, net_lo, net_hi)):
        ax.text(xi, pt + err_hi.iloc[xi] + 0.8,
                f"{pt:.1f}%\n[{lo:.1f}–{hi:.1f}%]",
                ha="center", fontsize=7, color=WB_GREY)

    # Absolute share reference lines for each instrument
    for xi, yr in enumerate(years):
        ctax_abs = summary.loc[yr, "ctax_abs_share"] * 100
        ets_abs  = summary.loc[yr, "ets_abs_share"]  * 100
        ax.hlines(ctax_abs, xi - w/2, xi + w/2,
                  colors=WB_CYAN, linewidth=1, linestyles=":", alpha=0.6)
        ax.hlines(ets_abs, xi - w/2, xi + w/2,
                  colors=WB_BLUE, linewidth=1, linestyles=":", alpha=0.6)

    # Dotted reference legend entry
    ctax_line = plt.Line2D([0], [0], color=WB_CYAN, linewidth=1,
                           linestyle=":", label="Carbon tax abs. share (incl. overlap)")
    ets_line  = plt.Line2D([0], [0], color=WB_BLUE, linewidth=1,
                           linestyle=":", label="ETS abs. share (incl. overlap)")

    ax.set_xticks(x)
    ax.set_xticklabels(years)
    ax.set_ylim(0, 85)
    ax.set_ylabel("% of national GHG (Sin UTCUTS)")
    ax.set_xlabel("Year")
    ax.set_title("Mexico Carbon Pricing: Coverage Shares of National GHG Emissions, 2020–2023\n"
                 "Net combined (deduplicated) vs. absolute shares per instrument")
    ax.yaxis.set_major_formatter(mticker.FormatStrFormatter("%.0f%%"))

    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles + [ctax_line, ets_line],
              labels  + ["Carbon tax abs. share (incl. overlap)",
                         "ETS abs. share (incl. overlap)"],
              loc="upper left", ncol=2)

    fig.text(0.0, -0.08, SOURCE_NOTE, fontsize=6, color=WB_GREY,
             transform=ax.transAxes, va="top")

    fig.tight_layout()
    fig.savefig(FIGURES / "F2_stacked_coverage_shares.png")
    plt.close(fig)
    print("Saved: F2_stacked_coverage_shares.png")


# ══════════════════════════════════════════════════════════════════════════════
# FIGURE 3 — Uncertainty waterfall, 2023
# ══════════════════════════════════════════════════════════════════════════════

def fig3_uncertainty_waterfall(summary, ets, overlap, ctax_full):
    """
    Horizontal waterfall for 2023 showing how covered MtCO₂ is composed
    and how the overlap deduction works.

    Bars (left to right):
      Carbon tax coverage (point ± band)
      + ETS coverage
      − Overlap (deducted, shown positive for readability)
      = Net combined coverage (point ± band)
    Right panel shows each as % of national GHG.
    """
    yr = "2023"
    s  = summary.loc[yr]
    nat = s["national_ghg_mt"]

    labels  = ["Carbon tax\ncoverage", "ETS\ncoverage",
               "Overlap\n(deducted)", "Net combined\ncoverage"]
    values  = [s["ctax_point_mt"], s["ets_point_mt"],
               s["overlap_point_mt"], s["dedup_point_mt"]]

    # Error bar arrays: [left/downward error, right/upward error]
    lo_err = [s["ctax_point_mt"]    - s["ctax_low_mt"],
              0,
              s["overlap_high_mt"]  - s["overlap_point_mt"],  # more overlap = worse
              s["dedup_point_mt"]   - s["dedup_low_mt"]]
    hi_err = [s["ctax_high_mt"]     - s["ctax_point_mt"],
              0,
              s["overlap_point_mt"] - s["overlap_low_mt"],    # less overlap = better
              s["dedup_high_mt"]    - s["dedup_point_mt"]]

    colours  = [WB_CYAN, WB_BLUE, WB_ORANGE, WB_GREY]
    share_pt = [v / nat * 100 for v in values]

    fig, (ax_mt, ax_pct) = plt.subplots(1, 2, figsize=(11, 4.5),
                                         gridspec_kw={"width_ratios": [1.8, 1]})

    # Left panel: MtCO₂
    bars = ax_mt.barh(labels, values, color=colours,
                      xerr=[lo_err, hi_err],
                      error_kw={"capsize": 4, "elinewidth": 1.2, "ecolor": WB_GREY})

    # Annotations — offset from bar right edge + error bar
    for i, (bar, val, lo, hi) in enumerate(zip(bars, values, lo_err, hi_err)):
        right_edge = val + hi
        sign = "−" if i == 2 else ""   # overlap shown with minus sign
        lo_str = val - lo
        hi_str = val + hi
        ax_mt.text(right_edge + 6, bar.get_y() + bar.get_height() / 2,
                   f"{sign}{val:.1f}  [{lo_str:.1f}–{hi_str:.1f}] MtCO₂",
                   va="center", fontsize=7.5, color="#333333")

    # x-axis: must fit largest bar (net combined 461 Mt) + hi_err (24 Mt) + label text (~120 pts)
    ax_mt.set_xlim(0, 620)
    ax_mt.set_xlabel("MtCO₂")
    ax_mt.set_title(f"Coverage volumes — 2023\n(national total: {nat:.1f} MtCO₂e Sin UTCUTS)")
    ax_mt.invert_yaxis()

    # Right panel: % of national GHG
    ax_pct.barh(labels, share_pt, color=colours)
    for i, (val, lo, hi) in enumerate(zip(share_pt, lo_err, hi_err)):
        lo_pct = (values[i] - lo) / nat * 100
        hi_pct = (values[i] + hi) / nat * 100
        sign = "−" if i == 2 else ""
        ax_pct.text(val + 0.4, i,
                    f"{sign}{val:.1f}%  [{lo_pct:.1f}–{hi_pct:.1f}%]",
                    va="center", fontsize=7.5, color="#333333")
    ax_pct.set_xlim(0, 80)
    ax_pct.set_xlabel("% of national GHG (Sin UTCUTS)")
    ax_pct.set_title("Coverage shares — 2023")
    ax_pct.set_yticklabels([])
    ax_pct.invert_yaxis()

    fig.text(0.02, -0.04,
             "Note: 'Overlap (deducted)' bar shown as positive for readability; "
             "it is subtracted to derive the net combined figure.\n" + SOURCE_NOTE,
             fontsize=6, color=WB_GREY, transform=fig.transFigure, va="top")

    fig.suptitle("Mexico Carbon Pricing: Coverage Waterfall, 2023", fontweight="bold")
    fig.tight_layout()
    fig.savefig(FIGURES / "F3_uncertainty_waterfall_2023.png")
    plt.close(fig)
    print("Saved: F3_uncertainty_waterfall_2023.png")


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════

def main():
    print("=" * 60)
    print("03_outputs.py — Mexico carbon overlap tables and figures")
    print("=" * 60)

    ctax_full, ets, overlap, summary, sector_det = load_results()

    print("\n--- Tables ---")
    t1, t2, t3, t4 = build_tables(ctax_full, ets, overlap, summary, sector_det)

    print("\n--- Figures ---")
    fig1_ctax_coverage_share(ctax_full)
    fig2_stacked_coverage_shares(summary)
    fig3_uncertainty_waterfall(summary, ets, overlap, ctax_full)

    print("\n" + "=" * 60)
    print("03_outputs.py complete.")
    print(f"  Tables:  {TABLES}")
    print(f"  Figures: {FIGURES}")
    print("=" * 60)

    # Terminal preview of T3
    print("\n=== T3 preview (overlap-period summary) ===")
    t3_preview = t3[["Year","Carbon tax abs. share (%)","ETS abs. share (%)",
                      "Overlap abs. share (%)","Net combined share (%) — point",
                      "Net combined share (%) — low","Net combined share (%) — high"]].copy()
    print(t3_preview.to_string(index=False))

if __name__ == "__main__":
    main()
