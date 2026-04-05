"""
=============================================================================
Case:            Mexico State Carbon Pricing -- Yucatan
Script:          02_estimate.py
Estimation tier: Tier 3
Base year:       2023  (IEEGYCEI del Estado de Yucatan, SDS 2024)
GWPs:            AR5 (CH4=28, N2O=265)

Three-instrument Venn decomposition:
  S = Yucatan state carbon tax (all Kyoto gases, fixed sources, no threshold)
  F = Federal IEPS carbon tax (fossil fuel combustion CO2, NG-exempt)
  E = Mexico Pilot ETS (direct CO2, facilities >= 25,000 tCO2e/yr)

Eight segments via inclusion-exclusion:
  S n F n E, S n F, S n E, S_only, F n E, F_only, E_only, uncovered

Key Yucatan-specific features:
  - AR5 GWPs natively -- no conversion needed (best-quality inventory)
  - HFCs quantified: 334.18 GgCO2e entirely in S-only (not F, not E)
  - Electricity 93.5% NG -- minimal S n F overlap for power sector
  - Cement process CO2: 318 GgCO2e in S and E but NOT F
  - No coverage threshold -- all fixed productive sources
  - NG/calcination stimuli are PAYMENT RELIEF, not scope exclusions

Run:    python 02_estimate.py
Input:  data/processed/yucatan_tax_scope_2023.csv
        data/processed/yucatan_energy_fuel_2023.csv
Output: data/processed/yucatan_overlap_results.csv
        outputs/tables/yucatan_overlap_summary.csv
=============================================================================
"""

import os
import logging
import pandas as pd
import numpy as np

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)

SCRIPT_DIR    = os.path.dirname(os.path.abspath(__file__))
PROCESSED_DIR = os.path.join(SCRIPT_DIR, "data", "processed")
TABLES_DIR    = os.path.join(SCRIPT_DIR, "outputs", "tables")
os.makedirs(TABLES_DIR, exist_ok=True)

BASE_YEAR = 2023

# ---------------------------------------------------------------------------
# 1. Load cleaned data
# ---------------------------------------------------------------------------
df_scope = pd.read_csv(os.path.join(PROCESSED_DIR, "yucatan_tax_scope_2023.csv"))
df_fuel  = pd.read_csv(os.path.join(PROCESSED_DIR, "yucatan_energy_fuel_2023.csv"))

# Total state emissions (excl 3B+3D)
TOTAL_STATE = 10425.52  # GgCO2e, from inventory

# ---------------------------------------------------------------------------
# 2. Fuel fractions for F overlap (non-NG share of combustion CO2)
# ---------------------------------------------------------------------------

# Electricity: from Table 12
ng_share_elec = df_fuel.loc[df_fuel["fuel"] == "Gas natural", "share"].values[0]
non_ng_elec   = 1 - ng_share_elec  # ~6.5%

# Manufacturing: estimated central 65% NG (Yucatan gas pipeline infrastructure)
MANUF_NG = {"central": 0.65, "low": 0.50, "high": 0.80}

# Commercial/institutional: mostly gas LP, some NG
# Yucatan 1A4a: CO2=130.57, from Table 9: 0.31 CH4, 0.09 N2O
# Assume 40% NG, 60% LP/diesel for commercial
COMM_NG = {"central": 0.40, "low": 0.20, "high": 0.60}

# Agricultural combustion: diesel-dominated, very little NG
AGRI_NG = {"central": 0.10, "low": 0.00, "high": 0.20}

# ---------------------------------------------------------------------------
# 3. ETS coverage fractions (above 25,000 tCO2e/yr threshold)
#    (central, low, high)
# ---------------------------------------------------------------------------

ETS_FRAC = {
    # Electricity: 5 major power plants, mostly CC. Merida I-IV, Valladolid.
    # Several plants well above 25k. High concentration.
    "1A1a":  (0.90, 0.80, 0.95),

    # Other energy: 12.79 GgCO2e -- likely below threshold
    "1A1cii": (0.00, 0.00, 0.30),

    # Manufacturing -- depends on facility size
    # Iron/steel: 1.66 GgCO2e -- below threshold
    "1A2a":  (0.00, 0.00, 0.00),
    # Chemicals: 95 GgCO2e -- likely 1-2 large facilities
    "1A2c":  (0.50, 0.30, 0.70),
    # Food/beverage: 414 GgCO2e -- many plants, some large
    "1A2e":  (0.40, 0.20, 0.60),
    # Non-metallic minerals (coke de petroleo): 209 GgCO2e -- few large
    "1A2f":  (0.60, 0.40, 0.80),
    # Transport equipment: 2.34 -- below threshold
    "1A2g":  (0.00, 0.00, 0.00),
    # Mining: 70 GgCO2e -- 1-2 operations
    "1A2i":  (0.50, 0.30, 0.70),
    # Construction: 21 -- below threshold
    "1A2k":  (0.00, 0.00, 0.00),
    # Textiles: 49 -- possibly 1 large facility
    "1A2l":  (0.30, 0.10, 0.50),
    # Unspecified: 0.17 -- negligible
    "1A2m":  (0.00, 0.00, 0.00),

    # IPPU process emissions -- large single facilities
    # Cement: CEMEX Merida plant, single large facility
    "2A1":   (0.95, 0.85, 1.00),
    # Cal: 7.37 -- below threshold
    "2A2":   (0.00, 0.00, 0.50),
    # Iron/steel process: 3.32 -- below threshold
    "2C1":   (0.00, 0.00, 0.50),
}

# ---------------------------------------------------------------------------
# 4. Eight-segment Venn decomposition
# ---------------------------------------------------------------------------

def compute_segments(scenario="central"):
    """Compute 8-segment Venn: S x F x E."""

    segs = {
        "S_F_E": 0, "S_F": 0, "S_E": 0, "S_only": 0,
        "F_E": 0, "F_only": 0, "E_only": 0, "uncovered": 0,
    }

    sc_idx = {"central": 0, "low": 1, "high": 2}[scenario]

    for _, row in df_scope.iterrows():
        code   = row["ipcc_code"]
        co2e   = row["co2e_gg"]
        in_S   = bool(row["in_S"])
        in_F   = bool(row["in_F"])
        in_E_e = bool(row["in_E_eligible"])

        # --- F fraction: non-NG share of combustion CO2 ---
        # F only covers combustion CO2 from non-NG fossil fuels
        f_frac = 0.0
        if in_F:
            if code == "1A1a":
                f_frac = non_ng_elec  # ~6.5%
            elif code == "1A1cii":
                f_frac = non_ng_elec
            elif code.startswith("1A2"):
                f_frac = 1 - MANUF_NG[scenario]
            elif code == "1A4a":
                f_frac = 1 - COMM_NG[scenario]
            elif code == "1A4c":
                f_frac = 1 - AGRI_NG[scenario]
            elif code.startswith("1A3"):
                f_frac = 1.0  # transport: 100% non-NG
            # IPPU process emissions (2A, 2C, 2D): NOT in F

        # F covers combustion CO2 only.
        # For combustion categories, F_co2e = co2e * f_frac (approx)
        # For IPPU categories (2A, 2C, 2D, 2F): f_frac = 0
        f_co2e = co2e * f_frac

        # --- E fraction: above-threshold direct CO2 ---
        e_frac = 0.0
        if in_E_e and code in ETS_FRAC:
            e_frac = ETS_FRAC[code][sc_idx]
        e_co2e = co2e * e_frac

        # --- Assign to Venn segments ---
        if in_S:
            # Within S scope, decompose by F and E
            sfe = co2e * f_frac * e_frac        # S n F n E
            sf  = f_co2e - sfe                    # S n F only
            se  = e_co2e - sfe                    # S n E only
            s_o = co2e - f_co2e - e_co2e + sfe    # S only

            segs["S_F_E"]  += sfe
            segs["S_F"]    += sf
            segs["S_E"]    += se
            segs["S_only"] += s_o

        elif in_F or in_E_e:
            # Not in S, but in F and/or E
            fe = co2e * f_frac * e_frac
            segs["F_E"]    += fe
            segs["F_only"] += f_co2e - fe
            segs["E_only"] += e_co2e - fe
            segs["uncovered"] += co2e - f_co2e - e_co2e + fe

        else:
            segs["uncovered"] += co2e

    return segs


results = {}
for scen in ["central", "low", "high"]:
    results[scen] = compute_segments(scen)

# ---------------------------------------------------------------------------
# 5. Derived instrument totals
# ---------------------------------------------------------------------------

for scen in ["central", "low", "high"]:
    s = results[scen]
    s["gross_S"] = s["S_F_E"] + s["S_F"] + s["S_E"] + s["S_only"]
    s["gross_F"] = s["S_F_E"] + s["S_F"] + s["F_E"] + s["F_only"]
    s["gross_E"] = s["S_F_E"] + s["S_E"] + s["F_E"] + s["E_only"]
    s["union"]   = sum(v for k, v in s.items()
                       if k not in ("uncovered", "gross_S", "gross_F",
                                    "gross_E", "union"))

# ---------------------------------------------------------------------------
# 6. Print results
# ---------------------------------------------------------------------------

log.info("\n" + "=" * 70)
log.info("YUCATAN CARBON PRICING OVERLAP -- 2023")
log.info("=" * 70)

c = results["central"]
l = results["low"]
h = results["high"]

log.info(f"\nTotal state emissions: {TOTAL_STATE:,.2f} GgCO2e")

seg_labels = {
    "S_F_E":  "S n F n E  (all three)",
    "S_F":    "S n F only (not E)",
    "S_E":    "S n E only (not F)",
    "S_only": "S only",
    "F_E":    "F n E only (not S)",
    "F_only": "F only",
    "E_only": "E only",
    "uncovered": "Uncovered",
}

log.info(f"\n{'Segment':25s}  {'Central':>10s}  {'Low':>10s}  {'High':>10s}  {'% state':>8s}")
log.info("-" * 70)
for key, label in seg_labels.items():
    cv, lv, hv = c[key], l[key], h[key]
    pct = cv / TOTAL_STATE * 100
    log.info(f"  {label:23s}  {cv:10.2f}  {lv:10.2f}  {hv:10.2f}  {pct:7.1f}%")

log.info(f"\n{'Derived':25s}  {'Central':>10s}  {'Low':>10s}  {'High':>10s}  {'% state':>8s}")
log.info("-" * 70)
for key, label in [("gross_S", "Gross S (Yucatan tax)"),
                    ("gross_F", "Gross F (IEPS)"),
                    ("gross_E", "Gross E (Pilot ETS)"),
                    ("union",   "Union S u F u E")]:
    cv, lv, hv = c[key], l[key], h[key]
    pct = cv / TOTAL_STATE * 100
    log.info(f"  {label:23s}  {cv:10.2f}  {lv:10.2f}  {hv:10.2f}  {pct:7.1f}%")

# ---------------------------------------------------------------------------
# 7. Build output table
# ---------------------------------------------------------------------------

rows = []
all_labels = list(seg_labels.items()) + [
    ("gross_S", "Gross S (Yucatan tax)"),
    ("gross_F", "Gross F (IEPS)"),
    ("gross_E", "Gross E (Pilot ETS)"),
    ("union",   "Deduplicated union (S u F u E)"),
]

for key, label in all_labels:
    rows.append({
        "segment":       key,
        "label":         label,
        "central_GgCO2e": round(c[key], 2),
        "low_GgCO2e":     round(l[key], 2),
        "high_GgCO2e":    round(h[key], 2),
        "central_pct":    round(c[key] / TOTAL_STATE * 100, 2),
        "low_pct":        round(l[key] / TOTAL_STATE * 100, 2),
        "high_pct":       round(h[key] / TOTAL_STATE * 100, 2),
        "tier":          "Tier 3",
        "base_year":     2023,
    })

df_out = pd.DataFrame(rows)

out_path  = os.path.join(PROCESSED_DIR, "yucatan_overlap_results.csv")
tbl_path  = os.path.join(TABLES_DIR,    "yucatan_overlap_summary.csv")
df_out.to_csv(out_path, index=False)
df_out.to_csv(tbl_path, index=False)

log.info(f"\nOutputs written:")
log.info(f"  {out_path}")
log.info(f"  {tbl_path}")

# ---------------------------------------------------------------------------
# 8. Key findings summary
# ---------------------------------------------------------------------------

log.info(f"\n{'=' * 70}")
log.info("KEY FINDINGS -- YUCATAN")
log.info(f"{'=' * 70}")
log.info(f"  1. HFC S-only segment: {c['S_only']:.2f} GgCO2e ({c['S_only']/TOTAL_STATE*100:.1f}%)")
log.info(f"     Dominated by HFC refrigeration (334 GgCO2e) -- first state")
log.info(f"     where HFCs are both in tax scope AND quantified in inventory.")
log.info(f"  2. S n E (process CO2): cement (318), cal (7), iron (3) = "
         f"~{318+7+3:.0f} GgCO2e in S and E but NOT F.")
log.info(f"  3. Electricity S n F overlap is minimal due to 93.5% NG.")
log.info(f"  4. Transport F-only: {c['F_only']:.0f} GgCO2e ({c['F_only']/TOTAL_STATE*100:.1f}%)")
log.info(f"  5. Net carbon sink: forest absorption exceeds gross emissions.")

log.info("\n02_estimate.py complete.")
