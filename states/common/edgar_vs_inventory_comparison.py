#!/usr/bin/env python3
"""
EDGAR vs State Inventory sector-level comparison.
Maps both sources to 13 standardized comparison categories,
excluding LULUCF (3.B/5) and IDE (indirect NOx/NH3).
"""

import pandas as pd
import numpy as np

BASE = "/mnt/c/Users/ozgur/OneDrive/ClimateProjects/mexico-cpi-overlap/states"
COMMON = f"{BASE}/common"

# ── 13 comparison categories ──────────────────────────────────────────
CATEGORIES = [
    ("Electricity",          "1.A.1.a"),
    ("Refining/transformation", "1.A.1.bc"),
    ("Manufacturing",        "1.A.2"),
    ("Transport",            "1.A.3"),
    ("Buildings/other",      "1.A.4"),
    ("Fugitive",             "1.B"),
    ("IPPU minerals",        "2.A"),
    ("IPPU chemicals",       "2.B"),
    ("IPPU metals",          "2.C"),
    ("IPPU products",        "2.D-2.G"),
    ("Livestock",            "3.A"),
    ("Cropland/soils",       "3.C"),
    ("Waste",                "4"),
]
CAT_NAMES = [c[0] for c in CATEGORIES]

# ── EDGAR sector → category mapping ──────────────────────────────────
EDGAR_CAT_MAP = {
    "ENE":               "Electricity",
    "REF_TRF":           "Refining/transformation",
    "IND":               "Manufacturing",
    "TRO":               "Transport",
    "TNR_Aviation_CDS":  "Transport",
    "TNR_Aviation_CRS":  "Transport",
    "TNR_Aviation_LTO":  "Transport",
    "TNR_Other":         "Transport",
    "TNR_Ship":          "Transport",
    "RCO":               "Buildings/other",
    "PRO_FFF":           "Fugitive",
    "NMM":               "IPPU minerals",
    "CHE":               "IPPU chemicals",
    "IRO":               "IPPU metals",
    "NFE":               "IPPU metals",
    "NEU":               "IPPU products",
    "PRU_SOL":           "IPPU products",
    "ENF":               "Livestock",
    "MNM":               "Livestock",
    "AGS":               "Cropland/soils",
    "AWB":               "Cropland/soils",
    "N2O":               "Cropland/soils",
    "SWD_LDF":           "Waste",
    "SWD_INC":           "Waste",
    "WWT":               "Waste",
    # Excluded:
    "IDE":               None,  # indirect NOx/NH3
}


def map_ipcc_to_category(code):
    """Map an IPCC code string to one of 13 categories. Returns None for LULUCF/excluded."""
    if not isinstance(code, str):
        return None
    c = code.strip().replace(".", "").replace(" ", "").upper()

    # LULUCF exclusions
    if c.startswith("3B") or c.startswith("5"):
        return None
    # Biogenic energy rows
    if "BIO" in c.upper():
        return None

    # 1A1 subcategories
    if c in ("1A1", "1A1A", "1A1AI", "1A1AII", "1A1AIII"):
        return "Electricity"
    if c.startswith("1A1A"):
        return "Electricity"
    if c.startswith("1A1B") or c.startswith("1A1C"):
        return "Refining/transformation"
    if c == "1A1":
        return "Electricity"  # default if no sub

    # Manufacturing
    if c.startswith("1A2"):
        return "Manufacturing"
    # Transport
    if c.startswith("1A3"):
        return "Transport"
    # Buildings/other
    if c.startswith("1A4") or c.startswith("1A5"):
        return "Buildings/other"
    # Fugitive
    if c.startswith("1B"):
        return "Fugitive"

    # IPPU
    if c.startswith("2A"):
        return "IPPU minerals"
    if c.startswith("2B"):
        return "IPPU chemicals"
    if c.startswith("2C"):
        return "IPPU metals"
    if c.startswith("2D") or c.startswith("2E") or c.startswith("2F") or c.startswith("2G"):
        return "IPPU products"

    # AFOLU
    if c.startswith("3A"):
        return "Livestock"
    if c.startswith("3C"):
        return "Cropland/soils"

    # Waste
    if c.startswith("4"):
        return "Waste"

    return None


def load_inventory(state_key):
    """
    Load each state's inventory and return dict of {category: KtCO2e}.
    Also returns (year, filename).
    """
    result = {c: 0.0 for c in CAT_NAMES}

    if state_key == "cdmx":
        df = pd.read_csv(f"{BASE}/cdmx/data/processed/cdmx_inventory_clean.csv")
        year = 2020
        # Emissions in tonnes CO2e → KtCO2e (÷1000)
        cat_map = {
            "ELECTRICITY": "Electricity",
            "INDUSTRY_REG": "Manufacturing",
            "INDUSTRY_UNREG": "Manufacturing",
            "COMMERCIAL_REG": "Buildings/other",
            "COMMERCIAL_UNREG": "Buildings/other",
            "RESIDENTIAL": "Buildings/other",
            "RESIDENTIAL_OTHER": "Buildings/other",
            "HFC_RESIDENTIAL": "IPPU products",
            "ROAD_TRANSPORT": "Transport",
            "AVIATION": "Transport",
            "RAIL": "Transport",
            "BUS_TERMINALS": "Transport",
            "CONSTRUCTION_EQUIP": "Transport",
            "WASTE": "Waste",
            "AGRICULTURE": "Cropland/soils",
            "AGRICULTURE_EQUIP": "Buildings/other",
            "LIVESTOCK": "Livestock",
            "FUGITIVE_LP": "Fugitive",
            "FUEL_STORAGE": "Fugitive",
            "MISC_AREA": None,  # fires, charcoal, structural fires - exclude
            "CONSTRUCTION": None,
        }
        for _, row in df.iterrows():
            cat = cat_map.get(row["analysis_cat"])
            if cat:
                result[cat] += row["co2eq_t"] / 1000.0
        return result, year, "cdmx_inventory_clean.csv"

    elif state_key == "colima":
        df = pd.read_csv(f"{BASE}/colima/data/processed/colima_inventory_2015_clean.csv")
        year = 2015
        for _, row in df.iterrows():
            ipcc = str(row.get("ipcc_code", ""))
            cat = map_ipcc_to_category(ipcc)
            if cat:
                result[cat] += row["co2e_gg"]  # GgCO2e = KtCO2e
        return result, year, "colima_inventory_2015_clean.csv"

    elif state_key == "durango":
        df = pd.read_csv(f"{BASE}/durango/data/processed/durango_inventory_2022.csv")
        year = 2022
        for _, row in df.iterrows():
            cat = map_ipcc_to_category(row["ipcc_code"])
            if cat:
                result[cat] += row["emissions_GgCO2e"]  # GgCO2e = KtCO2e
        return result, year, "durango_inventory_2022.csv"

    elif state_key == "estado_de_mexico":
        df = pd.read_csv(f"{BASE}/estado_de_mexico/data/processed/estado_de_mexico_inventory.csv")
        year = 2019  # EdoMex uses ~2019 base year
        cat_map = {
            "1.A.1.a": "Electricity",
            "1.A.2": "Manufacturing",
            "1.A.3": "Transport",
            "1.A.4": "Buildings/other",
            "1.B": "Fugitive",
            "2.A.1": "IPPU minerals",
            "2.A.2": "IPPU minerals",
            "2.A.3": "IPPU minerals",
            "2.A.4": "IPPU minerals",
            "2.C": "IPPU metals",
            "2.D": "IPPU products",
            "3.x": None,  # AFOLU aggregated, can't split livestock vs cropland
            "4.x": "Waste",
        }
        for _, row in df.iterrows():
            cat = cat_map.get(row["ipcc_2006"])
            if cat:
                result[cat] += row["central_KtCO2e"]  # already KtCO2e
        # AFOLU: assign total to livestock + cropland proportionally (we can't split)
        afolu_row = df[df["ipcc_2006"] == "3.x"]
        if len(afolu_row) > 0:
            # Just put in livestock as a combined AFOLU value, mark as approximate
            result["Livestock"] = afolu_row.iloc[0]["central_KtCO2e"] * 0.5
            result["Cropland/soils"] = afolu_row.iloc[0]["central_KtCO2e"] * 0.5
        return result, year, "estado_de_mexico_inventory.csv"

    elif state_key == "guanajuato":
        df = pd.read_csv(f"{BASE}/guanajuato/data/processed/sector_emissions_clean.csv")
        year = 2013
        for _, row in df.iterrows():
            ipcc = str(row.get("category_ipcc", ""))
            # Handle special cases
            if ipcc == "1A2_local":
                cat = "Manufacturing"
            elif ipcc == "1A3e":
                cat = "Transport"
            else:
                cat = map_ipcc_to_category(ipcc)
            if cat:
                result[cat] += row["total_ggco2e"]  # GgCO2e = KtCO2e
        return result, year, "sector_emissions_clean.csv"

    elif state_key == "morelos":
        df = pd.read_csv(f"{BASE}/morelos/data/processed/morelos_inventory_2014.csv")
        year = 2014
        sector_map = {
            "manufacturing_automotive": "Manufacturing",
            "manufacturing_food_bev": "Manufacturing",
            "manufacturing_electrical": "Manufacturing",
            "manufacturing_pulp_paper": "Manufacturing",
            "industrial_process_cement": "IPPU minerals",
            "manufacturing_petro_products": "Manufacturing",
            "manufacturing_textiles": "Manufacturing",
            "manufacturing_metals": "Manufacturing",
            "manufacturing_nonmet_minerals": "Manufacturing",
            "manufacturing_chemical": "Manufacturing",
            "manufacturing_plastics": "Manufacturing",
            "manufacturing_petrochem": "Manufacturing",
            "manufacturing_other_small": "Manufacturing",
            "industrial_process_glass": "IPPU minerals",
            "area_agri_combustion": "Buildings/other",
            "area_commercial": "Buildings/other",
            "area_residential": "Buildings/other",
            "area_industrial_small": "Manufacturing",
            "afolu_livestock": "Livestock",
            "afolu_burning": "Cropland/soils",
            "afolu_fire": None,  # forest fires = LULUCF-adjacent
            "waste_wastewater": "Waste",
            "mobile_road": "Transport",
            "mobile_nonroad": "Transport",
        }
        for _, row in df.iterrows():
            cat = sector_map.get(row["ipcc_sector"])
            if cat:
                result[cat] += row["total_GgCO2e"]  # GgCO2e = KtCO2e
                # Add HFC if present
                if pd.notna(row.get("HFC_PFC_SF6_GgCO2e")):
                    result[cat] += row["HFC_PFC_SF6_GgCO2e"]
        return result, year, "morelos_inventory_2014.csv"

    elif state_key == "queretaro":
        df = pd.read_csv(f"{BASE}/queretaro/data/processed/queretaro_inventory_2021.csv")
        year = 2021
        for _, row in df.iterrows():
            ipcc = str(row.get("ipcc_code", ""))
            # Handle Querétaro-specific codes
            if ipcc == "1Ab":  # typo for 1A4b
                cat = "Buildings/other"
            elif ipcc.startswith("2F1"):
                cat = "IPPU products"
            else:
                cat = map_ipcc_to_category(ipcc)
            if cat:
                result[cat] += row["emissions_GgCO2e"]
        return result, year, "queretaro_inventory_2021.csv"

    elif state_key == "sanluispotosi":
        df = pd.read_csv(f"{BASE}/sanluispotosi/data/processed/slp_inventory_annual_ar5.csv")
        year = 2014  # closest single year
        ipcc_map = {
            "1A1": "Electricity",
            "1A3_gas": "Transport",
            "1A3_die": "Transport",
            "1A2_gn": "Manufacturing",
            "1A2_glp": "Manufacturing",
            "1A2_die": "Manufacturing",
            "1A4": "Buildings/other",
            "1A_bio_lena": None,  # biogenic
            "1A_bio_bag": None,  # biogenic
            "2_metalurgia": "IPPU metals",
            "2_quimica": "IPPU chemicals",
            "2_cemento_cal": "IPPU minerals",
            "2_automotriz": "IPPU products",
            "2_celulosa": "IPPU products",
            "2_vidrio": "IPPU minerals",
            "2_otras": "IPPU products",
            "3_ferm_ent": "Livestock",
            "3_excretas": "Livestock",
            "3_quema_ag": "Cropland/soils",
            "4_domesticos": "Waste",
            "4_industriales": "Waste",
        }
        for _, row in df.iterrows():
            cat = ipcc_map.get(row["ipcc_code"])
            if cat:
                result[cat] += row["emissions_GgCO2e"]
        return result, year, "slp_inventory_annual_ar5.csv"

    elif state_key == "tamaulipas":
        df = pd.read_csv(f"{BASE}/tamaulipas/data/processed/tamaulipas_inventory_2013_ar5.csv")
        year = 2013
        for _, row in df.iterrows():
            ipcc = str(row.get("ipcc_code", ""))
            # Handle special codes
            if ipcc == "1A1a":
                cat = "Electricity"
            elif ipcc == "1A1b":
                cat = "Refining/transformation"
            elif ipcc == "1B2":
                cat = "Fugitive"
            elif ipcc == "2A4":
                cat = "IPPU minerals"
            elif ipcc == "2B8":
                cat = "IPPU chemicals"
            elif ipcc == "2F1":
                cat = "IPPU products"
            elif ipcc.startswith("1A4b"):
                cat = "Buildings/other"
            elif ipcc.startswith("3C1"):
                cat = "Cropland/soils"
            elif ipcc == "3C7":
                cat = "Cropland/soils"
            else:
                cat = map_ipcc_to_category(ipcc)
            if cat:
                result[cat] += row["total_ar5"]
        return result, year, "tamaulipas_inventory_2013_ar5.csv"

    elif state_key == "yucatan":
        df = pd.read_csv(f"{BASE}/yucatan/data/processed/yucatan_inventory_2023.csv")
        year = 2023
        for _, row in df.iterrows():
            ipcc = str(row.get("ipcc_code", ""))
            if ipcc.startswith("2F1") or ipcc.startswith("2F1a"):
                cat = "IPPU products"
            elif ipcc == "1A1cii":
                cat = "Refining/transformation"
            else:
                cat = map_ipcc_to_category(ipcc)
            if cat:
                result[cat] += row["co2e_gg"]
        return result, year, "yucatan_inventory_2023.csv"

    elif state_key == "zacatecas":
        df = pd.read_csv(f"{BASE}/zacatecas/data/processed/zacatecas_inventory_summary.csv")
        year = 2024  # synthetic/EDGAR-based
        cat_map = {
            "ELECTRICITY": "Electricity",
            "REFINING": "Refining/transformation",
            "MANUFACTURING": "Manufacturing",
            "TRANSPORT": "Transport",
            "RESIDENTIAL_COMMERCIAL": "Buildings/other",
            "FUGITIVE": "Fugitive",
            "IPPU": "IPPU minerals",  # approximate
            "AFOLU": "Livestock",  # can't split
            "WASTE": "Waste",
            "OTHER": None,
        }
        for _, row in df.iterrows():
            cat = cat_map.get(row["broad_category"])
            if cat:
                result[cat] += row["central_KtCO2e"]
        return result, year, "zacatecas_inventory_summary.csv"

    else:
        raise ValueError(f"Unknown state: {state_key}")


def load_edgar_for_state(state_name, year):
    """Load EDGAR data for state/year from timeseries or inventory comparison files."""
    ts = pd.read_csv(f"{COMMON}/edgar_state_timeseries.csv")
    ic = pd.read_csv(f"{COMMON}/edgar_inventory_comparison_years.csv")
    combined = pd.concat([ts, ic], ignore_index=True)

    sub = combined[(combined["state"] == state_name) & (combined["year"] == year)]
    if len(sub) == 0:
        # Try closest year available
        avail = combined[combined["state"] == state_name]["year"].unique()
        if len(avail) > 0:
            closest = min(avail, key=lambda y: abs(y - year))
            print(f"  NOTE: {state_name} year {year} not in EDGAR, using {closest}")
            sub = combined[(combined["state"] == state_name) & (combined["year"] == closest)]
            year = closest
        else:
            print(f"  WARNING: {state_name} not found in EDGAR data")
            return {c: 0.0 for c in CAT_NAMES}, year

    result = {c: 0.0 for c in CAT_NAMES}
    for _, row in sub.iterrows():
        cat = EDGAR_CAT_MAP.get(row["edgar_sector"])
        if cat:
            result[cat] += row["KtCO2e"]
    return result, year


# ── State registry ────────────────────────────────────────────────────
# (state_key, display_name, edgar_name, inventory_year)
STATES = [
    ("cdmx",            "CDMX",            "CDMX",            2020),
    ("colima",          "Colima",          "Colima",          2015),
    ("durango",         "Durango",         "Durango",         2022),
    ("estado_de_mexico","Estado de México","Estado de México", 2019),
    ("guanajuato",      "Guanajuato",      "Guanajuato",      2013),
    ("morelos",         "Morelos",         "Morelos",         2014),
    ("queretaro",       "Querétaro",       "Querétaro",       2021),
    ("sanluispotosi",   "San Luis Potosí", "San Luis Potosí", 2014),
    ("tamaulipas",      "Tamaulipas",      "Tamaulipas",      2013),
    ("yucatan",         "Yucatán",         "Yucatán",         2023),
    ("zacatecas",       "Zacatecas",       "Zacatecas",       2024),
]


def main():
    # ── Step 1: Audit and load all inventories ────────────────────────
    print("=" * 70)
    print("STEP 1: Inventory Sector Audit")
    print("=" * 70)

    all_inv = {}  # state_key → {cat: KtCO2e}
    inv_meta = {}  # state_key → (year, filename)

    for key, display, edgar, inv_year in STATES:
        inv_data, year, fname = load_inventory(key)
        all_inv[key] = inv_data
        inv_meta[key] = (year, fname)
        total = sum(v for v in inv_data.values())
        print(f"\n{display} ({fname}, year={year})")
        print(f"  Total ex-LULUCF: {total:,.1f} KtCO2e")
        for cat in CAT_NAMES:
            if inv_data[cat] > 0:
                print(f"    {cat:30s} {inv_data[cat]:>10,.1f}")

    # ── Sector coverage matrix ────────────────────────────────────────
    print("\n" + "=" * 70)
    print("SECTOR COVERAGE MATRIX")
    print("=" * 70)
    header = f"{'State':<18}" + "".join(f"{c[:8]:>9}" for c in CAT_NAMES)
    print(header)
    print("-" * len(header))

    coverage_rows = []
    for key, display, _, _ in STATES:
        row_data = {"state": display}
        line = f"{display:<18}"
        for cat in CAT_NAMES:
            has = "Y" if all_inv[key][cat] > 0 else "-"
            line += f"{has:>9}"
            row_data[cat] = has
        print(line)
        coverage_rows.append(row_data)

    # Save coverage matrix
    pd.DataFrame(coverage_rows).to_csv(
        f"{COMMON}/sector_coverage_matrix.csv", index=False)

    # ── Step 2-3: Sector-level comparison ─────────────────────────────
    print("\n" + "=" * 70)
    print("STEP 2-3: EDGAR vs Inventory Sector Comparison")
    print("=" * 70)

    comparison_rows = []
    totals_rows = []

    for key, display, edgar_name, inv_year in STATES:
        edgar_data, edgar_year = load_edgar_for_state(edgar_name, inv_year)
        inv_data = all_inv[key]

        print(f"\n--- {display} (inv={inv_year}, edgar={edgar_year}) ---")

        inv_total = 0.0
        edgar_total = 0.0
        inv_comparable = 0.0
        edgar_comparable = 0.0

        for cat, ipcc in CATEGORIES:
            inv_val = inv_data[cat]
            edgar_val = edgar_data[cat]
            inv_total += inv_val
            edgar_total += edgar_val

            # Determine flag
            if inv_val == 0 and edgar_val == 0:
                flag = "both_zero"
                ratio = np.nan
            elif inv_val > 0 and edgar_val == 0:
                flag = "inventory_only"
                ratio = 0.0
            elif inv_val == 0 and edgar_val > 0:
                flag = "edgar_only"
                ratio = np.inf
            else:
                ratio = edgar_val / inv_val
                if ratio > 2.0:
                    flag = "edgar_high"
                elif ratio < 0.5:
                    flag = "edgar_low"
                else:
                    flag = "aligned"
                inv_comparable += inv_val
                edgar_comparable += edgar_val

            diff = edgar_val - inv_val

            comparison_rows.append({
                "state": display,
                "inventory_year": inv_year,
                "comparison_category": cat,
                "ipcc_code": ipcc,
                "inventory_KtCO2e": round(inv_val, 2),
                "edgar_KtCO2e": round(edgar_val, 2),
                "ratio_edgar_over_inv": round(ratio, 4) if np.isfinite(ratio) else ("inf" if ratio == np.inf else ""),
                "difference_KtCO2e": round(diff, 2),
                "flag": flag,
            })

            if flag not in ("both_zero", "edgar_only") and inv_val > 0:
                marker = ""
                if flag == "edgar_high":
                    marker = " ⚠ HIGH"
                elif flag == "edgar_low":
                    marker = " ⚠ LOW"
                elif flag == "inventory_only":
                    marker = " ⚠ EDGAR=0"
                print(f"  {cat:30s} inv={inv_val:>8,.1f}  edgar={edgar_val:>8,.1f}  "
                      f"ratio={ratio:>5.2f}x{marker}")

        totals_rows.append({
            "state": display,
            "inventory_year": inv_year,
            "inventory_total_exLULUCF": round(inv_total, 2),
            "edgar_total_exLULUCF": round(edgar_total, 2),
            "ratio": round(edgar_total / inv_total, 4) if inv_total > 0 else "",
            "inventory_total_comparable": round(inv_comparable, 2),
            "edgar_total_comparable": round(edgar_comparable, 2),
            "ratio_comparable": round(edgar_comparable / inv_comparable, 4) if inv_comparable > 0 else "",
        })

    # ── Save outputs ──────────────────────────────────────────────────
    comp_df = pd.DataFrame(comparison_rows)
    comp_df.to_csv(f"{COMMON}/edgar_vs_inventory_sector_comparison.csv", index=False)
    print(f"\nSaved: edgar_vs_inventory_sector_comparison.csv ({len(comp_df)} rows)")

    totals_df = pd.DataFrame(totals_rows)
    totals_df.to_csv(f"{COMMON}/edgar_vs_inventory_totals.csv", index=False)
    print(f"Saved: edgar_vs_inventory_totals.csv ({len(totals_df)} rows)")

    print(f"Saved: sector_coverage_matrix.csv")

    # ── Summary table ─────────────────────────────────────────────────
    print("\n" + "=" * 100)
    print("COMPARABLE-SCOPE TOTALS (only categories where both sources have data)")
    print("=" * 100)
    print(f"{'State':<20} {'Year':>5} {'Inv Total':>12} {'EDGAR Total':>12} {'Ratio':>7}  "
          f"{'Inv Comp':>12} {'EDGAR Comp':>12} {'Ratio':>7}")
    print("-" * 100)
    for _, row in totals_df.iterrows():
        print(f"{row['state']:<20} {row['inventory_year']:>5} "
              f"{row['inventory_total_exLULUCF']:>12,.1f} {row['edgar_total_exLULUCF']:>12,.1f} "
              f"{row['ratio']:>7.2f}x  "
              f"{row['inventory_total_comparable']:>12,.1f} {row['edgar_total_comparable']:>12,.1f} "
              f"{str(row['ratio_comparable']):>7}")
    print("=" * 100)


if __name__ == "__main__":
    main()
