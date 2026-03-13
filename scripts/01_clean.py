"""
01_clean.py — Data cleaning and harmonisation
==============================================
Case:            Mexico Federal Carbon Tax × Mexico Pilot ETS (SCE Fase Piloto)
Estimation tier: Tier 2 / Tier 3
Coverage type:   Operational coverage (CO2 from sources actively participating)

Outputs (data/processed/):
  clean_inecc_panel.csv        INECC CO2 by category, 2014-2024 (MtCO2)
  clean_iea_nonmetallic.csv    IEA Non-metallic minerals fuel breakdown, 2020-2023 (PJ + derived CO2)
  clean_bne_power.csv          BNE power sector NG share by year, 2014-2024
  clean_bne_sectors.csv        BNE sector fuel consumption time series 2014-2024 (PJ)
  clean_ng_shares.csv          Derived NG share of CO2 by sector and year (point + low + high)

Key assumptions documented inline and in docs/data_sources.md.

Run: python scripts/01_clean.py
"""

import pandas as pd
import numpy as np
import logging
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent.parent
RAW  = ROOT / "data" / "raw"
PROC = ROOT / "data" / "processed"
PROC.mkdir(parents=True, exist_ok=True)

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
log = logging.getLogger(__name__)

# ── Constants ──────────────────────────────────────────────────────────────────

# IPCC 2006 default emission factors (tCO2/TJ)
EF = {
    "gas_seco":           56.1,
    "carbon_mineral":     96.1,
    "coque_petroleo":    107.0,
    "coque_carbon":      107.0,
    "diesel":             74.1,
    "combustoleo":        77.4,
    "glp":                63.1,
    "gasolinas":          69.3,
    "querosenos":         71.5,
    "petroleo_crudo":     73.3,
    "lena":                0.0,
    "bagazo":              0.0,
    "energia_solar":       0.0,
    "energia_electrica":   0.0,
}

EF_PETCOKE_CEMENT = 107.0   # central: Mexican cement kilns are predominantly petcoke-fired
EF_OIL_GENERIC    =  77.4   # sensitivity: generic oil products lower bound

ALL_YEARS     = [str(y) for y in range(2014, 2025)]
CTAX_YEARS    = ALL_YEARS
ETS_YEARS     = [str(y) for y in range(2020, 2025)]
OVERLAP_YEARS = [str(y) for y in range(2020, 2024)]

INECC_CATS = {
    "1A1a":    r"1A1a\]",
    "1A1b":    r"1A1b\]",
    "1A1cii":  r"1A1cii",
    "1A2a":    r"1A2a\]",
    "1A2b":    r"1A2b\]",
    "1A2c":    r"1A2c\]",
    "1A2d":    r"1A2d\]",
    "1A2e":    r"1A2e\]",
    "1A2g":    r"1A2g\]",
    "1A2i":    r"1A2i\]",
    "1A2miii": r"1A2miii",
    "1A_total":r"\[1A\]",
    "2A1":     r"2A1\]",
    "2A2":     r"2A2\]",
    "2A3":     r"2A3\]",
    "2A4":     r"2A4\]",
    "2B1":     r"2B1\]",
    "2B8":     r"2B8\]",
    "2C1":     r"2C1\]",
    "2C2":     r"2C2\]",
    "2H1":     r"2H1\]",
    "1B2":     r"1B2\]",
}

# ══════════════════════════════════════════════════════════════════════════════
# 1. INECC PANEL
# ══════════════════════════════════════════════════════════════════════════════

def extract_inecc_value(df, pattern, co2_col):
    mask = df.iloc[:, 0].astype(str).str.contains(pattern, na=False)
    hits = df[mask]
    if len(hits) == 0:
        return np.nan
    val = pd.to_numeric(hits.iloc[0][co2_col], errors="coerce")
    return val / 1e6 if pd.notna(val) else np.nan


def load_inecc_panel():
    log.info("Loading INECC panel 2014-2024...")
    results = {}

    # 2014-2019: multi-sheet file
    xl = pd.ExcelFile(RAW / "INEGyCEI_2014-2019.xlsx")
    for yr in xl.sheet_names:
        df = pd.read_excel(RAW / "INEGyCEI_2014-2019.xlsx", sheet_name=yr, header=None)
        results[yr] = {cat: extract_inecc_value(df, pat, 1) for cat, pat in INECC_CATS.items()}

    # 2020-2024: individual files
    for yr in range(2020, 2025):
        df = pd.read_excel(RAW / f"mexico_{yr}_ghgemissions.xlsx")
        co2_col = df.columns[1]
        results[str(yr)] = {
            cat: extract_inecc_value(df, pat, co2_col) for cat, pat in INECC_CATS.items()
        }

    panel = pd.DataFrame(results).T
    panel.index.name = "year"
    panel = panel[list(INECC_CATS.keys())]

    # Flag: 1A1cii NaN in 2014 — impute from 2015
    if pd.isna(panel.loc["2014", "1A1cii"]):
        panel.loc["2014", "1A1cii"] = panel.loc["2015", "1A1cii"]
        log.warning("1A1cii 2014: NaN — imputed from 2015 (%.2f Mt). Flag in data_sources.md.", panel.loc["2014", "1A1cii"])

    # Flag: frozen values in 2023-2024
    for cat in ["1A1b", "1A1cii", "1B2"]:
        if abs(panel.loc["2023", cat] - panel.loc["2024", cat]) < 0.001:
            log.warning("%s: 2024 = 2023 (%.3f Mt) — frozen estimate. Base year for this category: 2023.", cat, panel.loc["2023", cat])

    # Flag: reclassification break at 2019-2020
    for cat in ["1A2e", "1A2i", "1A2miii"]:
        v19, v20 = panel.loc["2019", cat], panel.loc["2020", cat]
        if pd.notna(v19) and pd.notna(v20) and v19 > 0 and abs((v20-v19)/v19) > 0.4:
            log.warning("%s: Step change 2019→2020 (%.1f→%.1f Mt, %+.0f%%) — inventory reclassification. 1A_total unaffected.", cat, v19, v20, (v20-v19)/v19*100)

    # Sanity check: subcat sum vs 1A_total
    subcats = ["1A1a","1A1b","1A1cii","1A2a","1A2b","1A2c","1A2d","1A2e","1A2g","1A2i","1A2miii"]
    for yr in ALL_YEARS:
        gap = panel.loc[yr, "1A_total"] - panel.loc[yr, subcats].sum()
        log.info("  %s 1A gap (transport+other+residual): %.1f Mt", yr, gap)
        if gap < 0:
            log.warning("  %s: NEGATIVE 1A gap %.1f Mt — check extraction.", yr, gap)

    log.info("INECC panel loaded: %d years × %d categories", len(panel), len(panel.columns))
    return panel


# ══════════════════════════════════════════════════════════════════════════════
# 2. IEA NON-METALLIC MINERALS
# ══════════════════════════════════════════════════════════════════════════════

def load_iea_nonmetallic():
    """
    IEA ISIC 23 fuel breakdown → direct combustion CO2 for cement/lime/glass combined.
    Assumption: 'Oil and oil products' in this sector is predominantly petcoke
    (central estimate) vs generic oil EF (sensitivity).
    Electricity excluded (indirect, not in carbon tax scope).
    """
    log.info("Loading IEA Non-metallic minerals fuel breakdown...")
    df = pd.read_excel(RAW / "IEA_mexico.xlsx", sheet_name="Industry - Energy", header=0)
    df.columns = ["Country","End_use","Product"] + list(df.columns[3:])
    df = df[(df["Country"]=="Mexico") &
            df["End_use"].str.contains("Non-metallic minerals", na=False) &
            ~df["End_use"].str.contains("Cement, as part", na=False)].copy()
    df = df.replace("..", np.nan)

    years_needed = list(range(2020, 2024))
    year_cols = [c for c in df.columns if c in years_needed]
    records = []
    for yr in year_cols:
        oil  = pd.to_numeric(df[df["Product"].str.contains("Oil and oil", na=False)][yr].values[0], errors="coerce")
        gas  = pd.to_numeric(df[df["Product"].str.match(r"^Gas \(PJ\)$", na=False)][yr].values[0], errors="coerce")
        coal = pd.to_numeric(df[df["Product"].str.contains("Coal and coal", na=False)][yr].values[0], errors="coerce")

        co2_central    = ((oil or 0)*EF_PETCOKE_CEMENT + (gas or 0)*EF["gas_seco"] + (coal or 0)*EF["carbon_mineral"]) / 1000
        co2_sensitivity= ((oil or 0)*EF_OIL_GENERIC    + (gas or 0)*EF["gas_seco"] + (coal or 0)*EF["carbon_mineral"]) / 1000
        ng_co2 = (gas or 0) * EF["gas_seco"] / 1000

        records.append({
            "year": str(yr),
            "oil_pj": oil, "gas_pj": gas, "coal_pj": coal,
            "co2_direct_central_mt":     co2_central,
            "co2_direct_sensitivity_mt": co2_sensitivity,
            "ng_share_central":    ng_co2 / co2_central     if co2_central > 0     else np.nan,
            "ng_share_sensitivity":ng_co2 / co2_sensitivity if co2_sensitivity > 0 else np.nan,
        })
        log.info("  IEA NM %s: oil=%.1f, gas=%.1f, coal=%.1f PJ → CO2_central=%.2f Mt, NG_share=%.1f%%",
                 yr, oil, gas, coal, co2_central, ng_co2/co2_central*100 if co2_central else 0)

    return pd.DataFrame(records).set_index("year")


# ══════════════════════════════════════════════════════════════════════════════
# 3. BNE POWER SECTOR
# ══════════════════════════════════════════════════════════════════════════════

def load_bne_power():
    """
    Derive NG share of power sector combustion CO2 from BNE F4.5 (2024 fuel mix).
    Apply uniformly across 2014-2024; ±2pp uncertainty from F4.6 generation mix stability.
    """
    log.info("Loading BNE power sector fuel mix...")
    path = RAW / "Anexo_gr_fico_y_estad_stico_-_BNE_2024.xlsx"
    f45 = pd.read_excel(path, sheet_name="F 4.5", header=None)

    fuel_rows = {
        "carbon_mineral":  "Carbón mineral",
        "coque_petroleo":  "Coque de petróleo",
        "diesel":          "Diésel",
        "combustoleo":     "Combustóleo",
        "gas_seco":        "Gas seco",
    }
    fuel_pj = {}
    for i in range(len(f45)):
        label = str(f45.iloc[i, 1]).strip()
        for key, pattern in fuel_rows.items():
            if pattern in label:
                fuel_pj[key] = pd.to_numeric(f45.iloc[i, 2], errors="coerce")

    co2_by_fuel = {k: fuel_pj.get(k, 0) * EF.get(k, 0) / 1000 for k in fuel_pj}
    total_co2   = sum(co2_by_fuel.values())
    ng_share    = co2_by_fuel.get("gas_seco", 0) / total_co2 if total_co2 > 0 else np.nan

    log.info("BNE power 2024: total combustion CO2=%.2f Mt, NG share=%.1f%%", total_co2, ng_share*100)

    records = [{
        "year": yr,
        "ng_share_point": ng_share,
        "ng_share_low":   max(0, ng_share - 0.02),
        "ng_share_high":  min(1, ng_share + 0.02),
        "note": "F4.5 direct" if yr == "2024" else "F4.5 applied (F4.6 confirms mix stability 2014-2023)",
    } for yr in ALL_YEARS]

    return pd.DataFrame(records).set_index("year")


# ══════════════════════════════════════════════════════════════════════════════
# 4. BNE SECTOR FUEL TIME SERIES
# ══════════════════════════════════════════════════════════════════════════════

def load_bne_sectors():
    """Extract BNE sector × fuel PJ time series 2014-2024 from F-series sheets."""
    log.info("Loading BNE sector fuel time series...")
    path = RAW / "Anexo_gr_fico_y_estad_stico_-_BNE_2024.xlsx"
    target_years = {str(y) for y in range(2014, 2025)}

    sector_sheets = {
        "industry":        ("F 5.7",  3),
        "agriculture":     ("F 5.4",  3),
        "commercial":      ("F 5.10", 3),
        "residential":     ("F 5.13", 3),
        "transport":       ("F 5.17", 2),
        "non_energy":      ("F 5.20", 3),
        "own_consumption": ("F 4.7",  3),
    }
    fuel_patterns = {
        "gas_seco":         ["Gas seco"],
        "gas_natural":      ["Gas natural"],
        "carbon_mineral":   ["Carbón mineral", "Carbon mineral"],
        "coque_petroleo":   ["Coque de petróleo", "Coque de petroleo"],
        "coque_carbon":     ["Coque de carbón", "Coque de carbon"],
        "diesel":           ["Diésel", "Diesel"],
        "combustoleo":      ["Combustóleo", "Combustoleo"],
        "glp":              ["GLP"],
        "gasolinas":        ["Gasolinas y naftas"],
        "querosenos":       ["Querosenos"],
        "lena":             ["Leña", "Lena"],
        "bagazo":           ["Bagazo de caña", "Bagazo de cana"],
        "energia_electrica":["Energía eléctrica", "Energia electrica"],
    }

    all_records = []
    for sector, (sheet_name, yr_row_idx) in sector_sheets.items():
        df = pd.read_excel(path, sheet_name=sheet_name, header=None)
        yr_row = df.iloc[yr_row_idx]
        year_col_map = {}
        for j, v in enumerate(yr_row):
            try:
                y = int(float(v))
                if str(y) in target_years:
                    year_col_map[str(y)] = j
            except (ValueError, TypeError):
                pass

        for fuel_key, patterns in fuel_patterns.items():
            for pat in patterns:
                mask = df.iloc[:, 1].astype(str).str.contains(pat, na=False, regex=False)
                hits = df[mask]
                if len(hits) == 0:
                    continue
                row_data = hits.iloc[0]
                for yr, col_j in year_col_map.items():
                    val = pd.to_numeric(row_data.iloc[col_j], errors="coerce")
                    all_records.append({"sector": sector, "fuel": fuel_key, "year": yr,
                                        "pj": val if pd.notna(val) else np.nan})
                break

    out = (pd.DataFrame(all_records)
           .pivot_table(index=["sector","year"], columns="fuel", values="pj", aggfunc="first")
           .reset_index())
    out.columns.name = None
    log.info("BNE sectors: %d rows across %d sectors", len(out), out["sector"].nunique())
    return out


# ══════════════════════════════════════════════════════════════════════════════
# 5. DERIVE NG SHARES
# ══════════════════════════════════════════════════════════════════════════════

def derive_ng_shares(bne_sectors, bne_power, iea_nm):
    """
    NG share of combustion CO2 by INECC sector category and year.
    Expert-range assignments documented per sector.
    """
    log.info("Deriving NG shares by sector and year...")
    industry = bne_sectors[bne_sectors["sector"]=="industry"].copy().set_index("year")
    taxable  = ["carbon_mineral","coque_petroleo","coque_carbon","diesel","combustoleo","glp","gasolinas"]
    taxable  = [f for f in taxable if f in industry.columns]

    records = []
    for yr in ALL_YEARS:
        rec = {"year": yr}
        row = industry.loc[yr] if yr in industry.index else pd.Series(dtype=float)

        # BNE industry aggregate NG share (informational cross-check)
        gs = row.get("gas_seco", np.nan)
        co2_tax = sum((row.get(f, 0) or 0) * EF.get(f, 0) / 1000 for f in taxable)
        co2_ng  = (gs * EF["gas_seco"] / 1000) if pd.notna(gs) else 0
        total   = co2_tax + co2_ng
        rec["industry_ng_share"] = co2_ng / total if total > 0 else np.nan

        # 1A1a — power (BNE F4.5)
        rec["1A1a_ng_point"] = bne_power.loc[yr, "ng_share_point"] if yr in bne_power.index else np.nan
        rec["1A1a_ng_low"]   = bne_power.loc[yr, "ng_share_low"]   if yr in bne_power.index else np.nan
        rec["1A1a_ng_high"]  = bne_power.loc[yr, "ng_share_high"]  if yr in bne_power.index else np.nan

        # 1A1b — refining (expert range; BNE cannot isolate)
        rec["1A1b_ng_point"], rec["1A1b_ng_low"], rec["1A1b_ng_high"] = 0.50, 0.40, 0.60

        # 1A1cii — O&G upstream (expert range; predominantly own associated gas)
        rec["1A1cii_ng_point"], rec["1A1cii_ng_low"], rec["1A1cii_ng_high"] = 0.80, 0.70, 0.90

        # Non-metallic minerals (cement/lime/glass) — IEA ISIC 23
        if yr in iea_nm.index:
            rec["nm_ng_point"] = iea_nm.loc[yr, "ng_share_central"]
            rec["nm_ng_low"]   = iea_nm.loc[yr, "ng_share_central"] * 0.75
            rec["nm_ng_high"]  = iea_nm.loc[yr, "ng_share_sensitivity"]
        else:
            base = "2020" if "2020" in iea_nm.index else iea_nm.index[0]
            rec["nm_ng_point"] = iea_nm.loc[base, "ng_share_central"]
            rec["nm_ng_low"]   = rec["nm_ng_point"] * 0.75
            rec["nm_ng_high"]  = iea_nm.loc[base, "ng_share_sensitivity"]

        # 1A2i — mining (diesel-dominated; expert range)
        rec["1A2i_ng_point"], rec["1A2i_ng_low"], rec["1A2i_ng_high"] = 0.12, 0.05, 0.20

        # 1A2miii — otras ramas (conservative; cannot disaggregate)
        rec["1A2miii_ng_point"], rec["1A2miii_ng_low"], rec["1A2miii_ng_high"] = 0.20, 0.10, 0.35

        # Other ETS sectors (chemicals, steel, paper, food, automotive) — BNE industry aggregate ±5pp
        ind = rec["industry_ng_share"]
        if pd.notna(ind):
            rec["other_ng_point"] = ind
            rec["other_ng_low"]   = max(0, ind - 0.05)
            rec["other_ng_high"]  = min(1, ind + 0.05)
        else:
            rec["other_ng_point"], rec["other_ng_low"], rec["other_ng_high"] = 0.30, 0.20, 0.40

        records.append(rec)

    return pd.DataFrame(records).set_index("year")


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════

def main():
    log.info("="*60)
    log.info("01_clean.py — Mexico carbon overlap data cleaning")
    log.info("="*60)

    inecc = load_inecc_panel()
    inecc.to_csv(PROC / "clean_inecc_panel.csv")
    log.info("Saved: clean_inecc_panel.csv")

    iea_nm = load_iea_nonmetallic()
    iea_nm.to_csv(PROC / "clean_iea_nonmetallic.csv")
    log.info("Saved: clean_iea_nonmetallic.csv")

    bne_power = load_bne_power()
    bne_power.to_csv(PROC / "clean_bne_power.csv")
    log.info("Saved: clean_bne_power.csv")

    bne_sectors = load_bne_sectors()
    bne_sectors.to_csv(PROC / "clean_bne_sectors.csv", index=False)
    log.info("Saved: clean_bne_sectors.csv")

    ng_shares = derive_ng_shares(bne_sectors, bne_power, iea_nm)
    ng_shares.to_csv(PROC / "clean_ng_shares.csv")
    log.info("Saved: clean_ng_shares.csv")

    log.info("="*60)
    log.info("01_clean.py complete.")
    log.info("="*60)

if __name__ == "__main__":
    main()
