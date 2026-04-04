"""
03_outputs.py — CDMX Carbon Pricing Overlap Analysis
======================================================
Generates publication-quality figures and summary tables.

Outputs:
- outputs/figures/cdmx_venn_segments.png
- outputs/figures/cdmx_coverage_summary.png
- outputs/tables/cdmx_overlap_full_table.csv
- outputs/tables/cdmx_overlap_summary.csv

Usage: python 03_outputs.py
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROC_DIR   = os.path.join(SCRIPT_DIR, "data", "processed")
FIG_DIR    = os.path.join(SCRIPT_DIR, "outputs", "figures")
TAB_DIR    = os.path.join(SCRIPT_DIR, "outputs", "tables")
os.makedirs(FIG_DIR, exist_ok=True)
os.makedirs(TAB_DIR, exist_ok=True)

print("=" * 70)
print("CDMX 03_outputs.py — Generating publication figures and tables")
print("=" * 70)

# ── Load results ─────────────────────────────────────────────────────────────
results = pd.read_csv(os.path.join(PROC_DIR, "cdmx_overlap_results.csv"))
inv     = pd.read_csv(os.path.join(PROC_DIR, "cdmx_inventory_clean.csv"))

total_ghg = inv['co2eq_t'].sum()

# Extract segment data
segments = results[results['segment'].isin([
    'S_F_E', 'S_F', 'S_E', 'S_only', 'F_E', 'F_only', 'E_only', 'uncovered'
])].copy()

derived = results[results['segment'].isin([
    'gross_S', 'gross_F', 'gross_E', 'union'
])].copy()


# ═══════════════════════════════════════════════════════════════════════════════
# FIGURE 1: Venn Segment Stacked Bar Chart
# ═══════════════════════════════════════════════════════════════════════════════
print("\n── Figure 1: Venn segment breakdown ──")

fig, ax = plt.subplots(figsize=(10, 6))

# Colours for each segment
seg_colors = {
    'S_F_E':     '#2c3e50',  # dark blue-grey — triple overlap
    'S_E':       '#2980b9',  # blue — S∩E
    'S_F':       '#8e44ad',  # purple — S∩F
    'S_only':    '#27ae60',  # green — S only
    'F_E':       '#e67e22',  # orange — F∩E
    'F_only':    '#e74c3c',  # red — F only
    'E_only':    '#f39c12',  # yellow — E only
    'uncovered': '#bdc3c7',  # light grey
}

seg_labels_short = {
    'S_F_E':     'S∩F∩E',
    'S_E':       'S∩E only',
    'S_F':       'S∩F only',
    'S_only':    'S only',
    'F_E':       'F∩E only',
    'F_only':    'F only',
    'E_only':    'E only',
    'uncovered': 'Uncovered',
}

# Order: covered segments bottom-up, uncovered on top
seg_order = ['S_F_E', 'S_E', 'S_F', 'S_only', 'F_only', 'uncovered']
# Filter out segments with zero or near-zero values for cleaner display
seg_order_nonzero = [s for s in seg_order
                     if segments[segments['segment'] == s]['central_tco2eq'].values[0] > 100]

bottom = 0
bar_x = [0.5]
for seg in seg_order_nonzero:
    row = segments[segments['segment'] == seg].iloc[0]
    val = row['central_tco2eq'] / 1e6  # convert to MtCO2eq
    ax.bar(bar_x, val, bottom=bottom, width=0.5,
           color=seg_colors[seg], label=seg_labels_short[seg],
           edgecolor='white', linewidth=0.5)
    # Label segments > 0.5 Mt
    if val > 0.3:
        ax.text(bar_x[0], bottom + val / 2, f'{val:.2f}',
                ha='center', va='center', fontsize=9, fontweight='bold',
                color='white' if seg != 'uncovered' else 'black')
    bottom += val

ax.set_xlim(0, 1)
ax.set_ylabel('Emissions (MtCO₂eq)', fontsize=12)
ax.set_title('CDMX Carbon Pricing Coverage — Venn Segments (2020)',
             fontsize=13, fontweight='bold')
ax.set_xticks([0.5])
ax.set_xticklabels(['CDMX 2020'], fontsize=11)

# Add total annotation
ax.annotate(f'Total: {total_ghg/1e6:.1f} MtCO₂eq',
            xy=(0.5, total_ghg / 1e6), xytext=(0.85, total_ghg / 1e6 * 0.9),
            fontsize=10, ha='center',
            arrowprops=dict(arrowstyle='->', color='grey'))

ax.legend(loc='center left', bbox_to_anchor=(1.02, 0.5), fontsize=9)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

plt.tight_layout()
fig.savefig(os.path.join(FIG_DIR, "cdmx_venn_segments.png"),
            dpi=300, bbox_inches='tight')
plt.close()
print("  Saved: cdmx_venn_segments.png")


# ═══════════════════════════════════════════════════════════════════════════════
# FIGURE 2: Coverage Summary (Gross Instruments + Union vs Total)
# ═══════════════════════════════════════════════════════════════════════════════
print("\n── Figure 2: Coverage summary ──")

fig, ax = plt.subplots(figsize=(9, 5))

labels = ['S (CDMX\ntax)', 'F (IEPS)', 'E (Pilot\nETS)',
          'Union\n(S∪F∪E)', 'Total\nCDMX']
central_vals = [
    derived[derived['segment'] == 'gross_S']['central_tco2eq'].values[0] / 1e6,
    derived[derived['segment'] == 'gross_F']['central_tco2eq'].values[0] / 1e6,
    derived[derived['segment'] == 'gross_E']['central_tco2eq'].values[0] / 1e6,
    derived[derived['segment'] == 'union']['central_tco2eq'].values[0] / 1e6,
    total_ghg / 1e6,
]
low_vals = [
    derived[derived['segment'] == 'gross_S']['low_tco2eq'].values[0] / 1e6,
    derived[derived['segment'] == 'gross_F']['low_tco2eq'].values[0] / 1e6,
    derived[derived['segment'] == 'gross_E']['low_tco2eq'].values[0] / 1e6,
    derived[derived['segment'] == 'union']['low_tco2eq'].values[0] / 1e6,
    total_ghg / 1e6,
]
high_vals = [
    derived[derived['segment'] == 'gross_S']['high_tco2eq'].values[0] / 1e6,
    derived[derived['segment'] == 'gross_F']['high_tco2eq'].values[0] / 1e6,
    derived[derived['segment'] == 'gross_E']['high_tco2eq'].values[0] / 1e6,
    derived[derived['segment'] == 'union']['high_tco2eq'].values[0] / 1e6,
    total_ghg / 1e6,
]

colors = ['#27ae60', '#e74c3c', '#2980b9', '#2c3e50', '#95a5a6']
err_low  = [max(0, c - l) for c, l in zip(central_vals, low_vals)]
err_high = [max(0, h - c) for c, h in zip(central_vals, high_vals)]

bars = ax.bar(labels, central_vals, color=colors, edgecolor='white', linewidth=0.5)
ax.errorbar(labels, central_vals, yerr=[err_low, err_high],
            fmt='none', ecolor='black', capsize=4, linewidth=1.2)

# Add value labels
for bar, val in zip(bars, central_vals):
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.3,
            f'{val:.1f}', ha='center', va='bottom', fontsize=10, fontweight='bold')

ax.set_ylabel('Emissions (MtCO₂eq)', fontsize=12)
ax.set_title('CDMX Carbon Pricing Coverage Summary (2020)',
             fontsize=13, fontweight='bold')
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.set_ylim(0, max(central_vals) * 1.15)

# Add coverage % annotation
union_pct = central_vals[3] / central_vals[4] * 100
ax.text(3, central_vals[3] * 0.5,
        f'{union_pct:.0f}%\nof total',
        ha='center', va='center', fontsize=11, fontweight='bold', color='white')

plt.tight_layout()
fig.savefig(os.path.join(FIG_DIR, "cdmx_coverage_summary.png"),
            dpi=300, bbox_inches='tight')
plt.close()
print("  Saved: cdmx_coverage_summary.png")


# ═══════════════════════════════════════════════════════════════════════════════
# TABLE 1: Full overlap results
# ═══════════════════════════════════════════════════════════════════════════════
print("\n── Table 1: Full overlap table ──")

# Reformat for publication
out = results.copy()
out['central_ggco2eq'] = out['central_tco2eq'] / 1000  # convert to GgCO2eq
out['low_ggco2eq']     = out['low_tco2eq'] / 1000
out['high_ggco2eq']    = out['high_tco2eq'] / 1000
out = out[['segment', 'label', 'central_ggco2eq', 'low_ggco2eq', 'high_ggco2eq',
           'central_pct', 'low_pct', 'high_pct']]
out.to_csv(os.path.join(TAB_DIR, "cdmx_overlap_full_table.csv"), index=False,
           float_format='%.1f')
print(f"  Saved: cdmx_overlap_full_table.csv")


# ═══════════════════════════════════════════════════════════════════════════════
# TABLE 2: Summary table (key metrics only)
# ═══════════════════════════════════════════════════════════════════════════════
print("\n── Table 2: Summary table ──")

summary = {
    'Metric': [
        'Total CDMX GHG (2020)',
        'Gross S (CDMX tax)',
        'Gross F (IEPS)',
        'Gross E (Pilot ETS)',
        'S ∩ F ∩ E overlap',
        'S ∩ F overlap (excl. E)',
        'S ∩ E overlap (excl. F)',
        'Deduplicated union (S∪F∪E)',
        'Uncovered emissions',
    ],
    'Central (GgCO2eq)': [
        total_ghg / 1000,
        derived[derived['segment'] == 'gross_S']['central_tco2eq'].values[0] / 1000,
        derived[derived['segment'] == 'gross_F']['central_tco2eq'].values[0] / 1000,
        derived[derived['segment'] == 'gross_E']['central_tco2eq'].values[0] / 1000,
        segments[segments['segment'] == 'S_F_E']['central_tco2eq'].values[0] / 1000,
        segments[segments['segment'] == 'S_F']['central_tco2eq'].values[0] / 1000,
        segments[segments['segment'] == 'S_E']['central_tco2eq'].values[0] / 1000,
        derived[derived['segment'] == 'union']['central_tco2eq'].values[0] / 1000,
        segments[segments['segment'] == 'uncovered']['central_tco2eq'].values[0] / 1000,
    ],
    'Central (% of total)': [
        100.0,
        derived[derived['segment'] == 'gross_S']['central_pct'].values[0],
        derived[derived['segment'] == 'gross_F']['central_pct'].values[0],
        derived[derived['segment'] == 'gross_E']['central_pct'].values[0],
        segments[segments['segment'] == 'S_F_E']['central_pct'].values[0],
        segments[segments['segment'] == 'S_F']['central_pct'].values[0],
        segments[segments['segment'] == 'S_E']['central_pct'].values[0],
        derived[derived['segment'] == 'union']['central_pct'].values[0],
        segments[segments['segment'] == 'uncovered']['central_pct'].values[0],
    ],
}
summary_df = pd.DataFrame(summary)
summary_df.to_csv(os.path.join(TAB_DIR, "cdmx_overlap_summary.csv"),
                   index=False, float_format='%.1f')
print(f"  Saved: cdmx_overlap_summary.csv")

# Print to console
print("\n  Summary Results:")
print(f"  {'Metric':40s}  {'Central':>12s}  {'% of total':>10s}")
print(f"  {'-'*40}  {'-'*12}  {'-'*10}")
for _, row in summary_df.iterrows():
    print(f"  {row['Metric']:40s}  {row['Central (GgCO2eq)']:>10,.1f}  "
          f"{row['Central (% of total)']:>9.1f}%")

print("\n" + "=" * 70)
print("03_outputs.py complete")
print("=" * 70)
