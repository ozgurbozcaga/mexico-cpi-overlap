"""
03_outputs.py — Guanajuato Carbon Pricing Overlap: Tables and Figures
Case: Guanajuato state carbon tax × Federal IEPS × Mexico Pilot ETS, base year 2013

Run: python scripts/03_outputs.py
Input: data/processed/overlap_estimates.csv
       data/processed/overlap_summary.csv
       data/processed/sector_emissions_clean.csv
Output: outputs/tables/guanajuato_overlap_summary.csv
        outputs/tables/guanajuato_subsector_detail.csv
        outputs/figures/guanajuato_venn_overlap.png
        outputs/figures/guanajuato_coverage_by_sector.png
"""

import os
import sys
import logging
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Circle, FancyArrowPatch
import matplotlib.ticker as mticker

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROC_DIR  = os.path.join(BASE_DIR, 'data', 'processed')
FIG_DIR   = os.path.join(BASE_DIR, 'outputs', 'figures')
TBL_DIR   = os.path.join(BASE_DIR, 'outputs', 'tables')
os.makedirs(FIG_DIR, exist_ok=True)
os.makedirs(TBL_DIR, exist_ok=True)

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
log = logging.getLogger(__name__)

# ── colour palette (consistent with other state pipelines) ─────────────────────
COL = {
    'S':     '#2166AC',  # State tax — blue
    'F':     '#D6604D',  # Federal tax — red
    'E':     '#4DAC26',  # ETS — green
    'SFE':   '#762A83',  # Triple overlap — purple
    'SE':    '#1A9641',  # S∩E only — teal-green
    'SF':    '#E66101',  # S∩F only — orange
    'S_only':'#5AAECD',  # S only — light blue
    'F_only':'#F4A582',  # F only — light red
    'uncov': '#D9D9D9',  # Uncovered — grey
    'HFC':   '#FEE08B',  # HFC special — yellow
}

STATE_TOTAL = 19264.8  # GgCO2e, Guanajuato 2013


def load_data():
    detail  = pd.read_csv(os.path.join(PROC_DIR, 'overlap_estimates.csv'))
    summary = pd.read_csv(os.path.join(PROC_DIR, 'overlap_summary.csv'))
    sectors = pd.read_csv(os.path.join(PROC_DIR, 'sector_emissions_clean.csv'))
    return detail, summary, sectors


def make_summary_table(summary_df: pd.DataFrame, detail_df: pd.DataFrame):
    """Write clean summary table for publication."""
    rows = []
    for _, row in summary_df.iterrows():
        sc = row['scenario']
        rows.append({
            'Scenario':                          sc.capitalize(),
            'S total coverage (GgCO2e)':         row['S_total_ggco2e'],
            'F total coverage (GgCO2e)':         row['F_total_ggco2e'],
            'E within S scope (GgCO2e)':         row['E_within_S_ggco2e'],
            'S∩F∩E — triple overlap (GgCO2e)':   row['S∩F∩E_ggco2e'],
            'S∩E only — NG+process in large (GgCO2e)': row['S∩E_only_ggco2e'],
            'S∩F only — non-NG in small (GgCO2e)': row['S∩F_only_ggco2e'],
            'S only (GgCO2e)':                   row['S_only_ggco2e'],
            'F only outside S scope (GgCO2e)':   row['F_only_outside_S_ggco2e'],
            'S share of state total (%)':         row['S_share_pct'],
            'F share of state total (%)':         row['F_share_pct'],
        })
    df_out = pd.DataFrame(rows)
    out_path = os.path.join(TBL_DIR, 'guanajuato_overlap_summary.csv')
    df_out.to_csv(out_path, index=False, float_format='%.1f')
    log.info(f"Wrote: {out_path}")
    return df_out


def make_subsector_table(detail_df: pd.DataFrame):
    """Write subsector-level detail table for central scenario."""
    central = detail_df[
        (detail_df['scenario'] == 'central') &
        (detail_df['total_S_scope_ggco2e'] > 0)
    ].copy()

    # Add low/high range columns
    low_df  = detail_df[(detail_df['scenario'] == 'low')  & (detail_df['total_S_scope_ggco2e'] > 0)]
    high_df = detail_df[(detail_df['scenario'] == 'high') & (detail_df['total_S_scope_ggco2e'] > 0)]

    out_cols = ['subsector', 'sector', 'total_S_scope_ggco2e',
                'f_fraction', 'ets_fraction',
                'S_F_E', 'S_E_only', 'S_F_only', 'S_only']
    out = central[out_cols].copy()
    out.columns = [
        'Subsector', 'Sector', 'Total_S_scope_GgCO2e',
        'F_coverage_fraction', 'ETS_coverage_fraction',
        'S∩F∩E_GgCO2e', 'S∩E_only_GgCO2e', 'S∩F_only_GgCO2e', 'S_only_GgCO2e'
    ]

    out_path = os.path.join(TBL_DIR, 'guanajuato_subsector_detail.csv')
    out.to_csv(out_path, index=False, float_format='%.2f')
    log.info(f"Wrote: {out_path}")
    return out


def plot_venn(summary_df: pd.DataFrame):
    """
    Draw a three-circle Venn diagram showing S/F/E coverage with labelled
    intersection areas. Uses proportional circle areas.
    """
    central = summary_df[summary_df['scenario'] == 'central'].iloc[0]

    SFE   = central['S∩F∩E_ggco2e']
    SE    = central['S∩E_only_ggco2e']
    SF    = central['S∩F_only_ggco2e']
    Sonly = central['S_only_ggco2e']
    S_total = central['S_total_ggco2e']
    F_total = central['F_total_ggco2e']
    E_total = central['E_within_S_ggco2e']
    Fonly_outside = central['F_only_outside_S_ggco2e']

    fig, ax = plt.subplots(figsize=(9, 7))
    ax.set_xlim(-4, 4)
    ax.set_ylim(-3.5, 3.5)
    ax.set_aspect('equal')
    ax.axis('off')

    # Circle radii proportional to sqrt of coverage
    r_S = 1.8
    r_F = 2.8  # F much larger due to transport
    r_E = 1.5

    # Positions: S (left), F (right), E (top)
    cx_S, cy_S = -0.8, -0.3
    cx_F, cy_F =  1.0, -0.3
    cx_E, cy_E =  0.1,  1.2

    alpha = 0.35
    c_S = Circle((cx_S, cy_S), r_S, color=COL['S'], alpha=alpha, zorder=1)
    c_F = Circle((cx_F, cy_F), r_F, color=COL['F'], alpha=alpha, zorder=1)
    c_E = Circle((cx_E, cy_E), r_E, color=COL['E'], alpha=alpha, zorder=1)
    for c in [c_S, c_F, c_E]:
        ax.add_patch(c)

    # Labels for circles
    ax.text(cx_S - 1.5, cy_S - 0.2, 'S\n(State tax)',
            ha='center', va='center', fontsize=10, fontweight='bold', color=COL['S'])
    ax.text(cx_F + 2.1, cy_F - 0.3, 'F\n(Federal IEPS)',
            ha='center', va='center', fontsize=10, fontweight='bold', color='#8B0000')
    ax.text(cx_E + 0.1, cy_E + 1.7, 'E\n(Pilot ETS)',
            ha='center', va='center', fontsize=10, fontweight='bold', color='#1A5C00')

    # Intersection labels
    label_kwargs = dict(ha='center', va='center', fontsize=8.5, fontweight='bold')

    # S only (bottom-left of S circle)
    ax.text(cx_S - 0.9, cy_S - 0.7, f'S only\n{Sonly:.0f}',
            color=COL['S_only'], bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.8),
            **label_kwargs)

    # S∩F only (between S and F, below E)
    ax.text(0.1, -1.3, f'S∩F\n{SF:.0f}',
            color=COL['SF'], bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.8),
            **label_kwargs)

    # S∩E only (between S and E)
    ax.text(-0.55, 0.7, f'S∩E\n{SE:.0f}',
            color=COL['SE'], bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.8),
            **label_kwargs)

    # S∩F∩E (centre)
    ax.text(0.25, 0.15, f'S∩F∩E\n{SFE:.0f}',
            color=COL['SFE'], bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.9),
            ha='center', va='center', fontsize=9, fontweight='bold')

    # F only outside S (far right)
    ax.text(2.8, -1.6, f'F only\n(outside S)\n{Fonly_outside:.0f}',
            color=COL['F_only'], bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.8),
            ha='center', va='center', fontsize=7.5, fontweight='bold')

    # Note on HFC and uncovered
    hfc = 306.8
    uncov = STATE_TOTAL - S_total - Fonly_outside
    ax.text(-3.6, -3.0,
            f'HFC (not in S/F/E scope): {hfc:.0f} GgCO₂e\n'
            f'Approx. uncovered (AFOLU, Waste, NG non-S): ~{uncov-hfc:.0f} GgCO₂e',
            fontsize=7, color='#555555', va='bottom', ha='left',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='#F5F5F5', alpha=0.8))

    # Low/high range annotation
    low_row  = summary_df[summary_df['scenario'] == 'low'].iloc[0]
    high_row = summary_df[summary_df['scenario'] == 'high'].iloc[0]
    ax.text(0, -3.0,
            f"S total: {S_total:.0f} [{low_row['S_total_ggco2e']:.0f}–{high_row['S_total_ggco2e']:.0f}] GgCO₂e  "
            f"({central['S_share_pct']:.1f}% of state total)",
            fontsize=8, ha='center', va='bottom', color='#333333',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.9))

    ax.set_title(
        'Guanajuato 2013 — Carbon Pricing Coverage Overlap\n'
        'S = State tax  |  F = Federal IEPS  |  E = Pilot ETS\n'
        'Values in GgCO₂e  |  Central scenario  |  Estimation tier: 3',
        fontsize=10, pad=12
    )

    fig.text(0.01, 0.01,
             'Source: IGCEI Guanajuato 2013 (Instituto de Ecología del Estado). '
             'Estimation: World Bank Climate Change Group internal working paper.',
             fontsize=6, color='#777777')

    plt.tight_layout()
    out_path = os.path.join(FIG_DIR, 'guanajuato_venn_overlap.png')
    plt.savefig(out_path, dpi=150, bbox_inches='tight')
    plt.close()
    log.info(f"Wrote: {out_path}")


def plot_coverage_by_sector(detail_df: pd.DataFrame, sector_df: pd.DataFrame):
    """
    Stacked horizontal bar chart showing emission coverage by subsector.
    Each bar shows S∩F∩E / S∩E / S∩F / S_only / F_only / uncovered segments.
    """
    central = detail_df[
        (detail_df['scenario'] == 'central') &
        (detail_df['total_S_scope_ggco2e'] > 0)
    ].copy()

    # Add the main non-S categories
    non_s_items = [
        ('Autotransporte',      7068.4, 'F_only'),
        ('Residencial',          736.6, 'mixed'),  # LP F-only + NG/leña uncovered
        ('AFOLU (net)',         2521.1, 'uncov'),
        ('Desechos',            1433.8, 'uncov'),
        ('HFC_RAC',              306.8, 'hfc'),
        ('Comercial+Maq.+Av.', 318.2,  'F_only'),
    ]

    fig, ax = plt.subplots(figsize=(10, 7))

    segment_cols = ['S_F_E', 'S_E_only', 'S_F_only', 'S_only']
    seg_labels   = ['S∩F∩E', 'S∩E only', 'S∩F only', 'S only']
    seg_colors   = [COL['SFE'], COL['SE'], COL['SF'], COL['S_only']]

    # Build bar data
    subsectors = list(central['subsector'])
    totals_s   = list(central['total_S_scope_ggco2e'])

    y_pos = list(range(len(subsectors)))
    bar_height = 0.5

    for idx, (sub, total) in enumerate(zip(subsectors, totals_s)):
        row = central[central['subsector'] == sub].iloc[0]
        left = 0
        for col, color, label in zip(segment_cols, seg_colors, seg_labels):
            val = row[col]
            if val > 0:
                ax.barh(idx, val, bar_height, left=left, color=color, edgecolor='white', linewidth=0.4)
                if val > 50:
                    ax.text(left + val/2, idx, f'{val:.0f}', ha='center', va='center',
                            fontsize=6.5, color='white', fontweight='bold')
            left += val

    # Format
    ax.set_yticks(y_pos)
    ax.set_yticklabels([s.replace('_', ' ') for s in subsectors], fontsize=8.5)
    ax.set_xlabel('GgCO₂e', fontsize=9)
    ax.set_title(
        'Guanajuato 2013 — Carbon Pricing Coverage by Subsector (S scope)\n'
        'Central scenario, Tier 3 estimation',
        fontsize=10
    )
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x:,.0f}'))
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # Legend
    legend_patches = [
        mpatches.Patch(color=COL['SFE'],    label='S∩F∩E (all three)'),
        mpatches.Patch(color=COL['SE'],     label='S∩E only (NG+process in large facilities)'),
        mpatches.Patch(color=COL['SF'],     label='S∩F only (non-NG in small facilities)'),
        mpatches.Patch(color=COL['S_only'], label='S only'),
    ]
    ax.legend(handles=legend_patches, loc='lower right', fontsize=7.5, framealpha=0.8)

    # Annotate total
    total_S = central['total_S_scope_ggco2e'].sum()
    ax.text(0.98, 0.02, f'Total S scope: {total_S:,.0f} GgCO₂e\n({total_S/STATE_TOTAL*100:.1f}% of state total)',
            transform=ax.transAxes, ha='right', va='bottom', fontsize=7.5,
            bbox=dict(boxstyle='round,pad=0.3', facecolor='#F0F0F0', alpha=0.8))

    plt.tight_layout()
    out_path = os.path.join(FIG_DIR, 'guanajuato_coverage_by_sector.png')
    plt.savefig(out_path, dpi=150, bbox_inches='tight')
    plt.close()
    log.info(f"Wrote: {out_path}")


def plot_state_totalpie(summary_df: pd.DataFrame):
    """
    Pie chart of total state emissions by coverage category.
    """
    central = summary_df[summary_df['scenario'] == 'central'].iloc[0]

    SFE    = central['S∩F∩E_ggco2e']
    SE     = central['S∩E_only_ggco2e']
    SF     = central['S∩F_only_ggco2e']
    Sonly  = central['S_only_ggco2e']
    Fonly  = central['F_only_outside_S_ggco2e']
    hfc    = 306.8

    # Uncovered = total - S segments - F_only_outside_S - HFC
    s_total = SFE + SE + SF + Sonly
    covered_sum = s_total + Fonly + hfc
    uncov = STATE_TOTAL - covered_sum

    labels = ['S∩F∩E', 'S∩E only', 'S∩F only', 'S only', 'F only (outside S)',
              'HFC (unpriced)', 'Uncovered (AFOLU/Waste/NG outside S)']
    sizes  = [SFE, SE, SF, Sonly, Fonly, hfc, uncov]
    colors = [COL['SFE'], COL['SE'], COL['SF'], COL['S_only'],
              COL['F_only'], COL['HFC'], COL['uncov']]
    explode = [0.03]*len(labels)

    fig, ax = plt.subplots(figsize=(9, 6))
    wedges, texts, autotexts = ax.pie(
        sizes, labels=None, colors=colors, explode=explode,
        autopct=lambda p: f'{p:.1f}%' if p > 2 else '',
        startangle=140, pctdistance=0.75, textprops={'fontsize': 8}
    )
    for at in autotexts:
        at.set_fontsize(7.5)
        at.set_fontweight('bold')

    legend_labels = [f'{l} ({s:.0f} GgCO₂e)' for l, s in zip(labels, sizes)]
    ax.legend(wedges, legend_labels, loc='lower left', fontsize=7.5,
              bbox_to_anchor=(-0.05, -0.05), framealpha=0.8)
    ax.set_title(
        f'Guanajuato 2013 — State Emissions by Carbon Pricing Coverage\n'
        f'Total: {STATE_TOTAL:,.0f} GgCO₂e  |  Central scenario',
        fontsize=10
    )

    plt.tight_layout()
    out_path = os.path.join(FIG_DIR, 'guanajuato_state_coverage_pie.png')
    plt.savefig(out_path, dpi=150, bbox_inches='tight')
    plt.close()
    log.info(f"Wrote: {out_path}")


def main():
    log.info("=== 03_outputs.py — Guanajuato Output Generation ===")

    detail_df, summary_df, sector_df = load_data()

    # Tables
    make_summary_table(summary_df, detail_df)
    make_subsector_table(detail_df)

    # Figures
    plot_venn(summary_df)
    plot_coverage_by_sector(detail_df, sector_df)
    plot_state_totalpie(summary_df)

    log.info("=== 03_outputs.py complete ===")


if __name__ == '__main__':
    main()
