#!/usr/bin/env python3
"""
Extract EDGAR sector-level emissions for inventory comparison years.
Uses emi (ton/cell/year) NetCDF files and GADM masks.
Outputs: edgar_inventory_comparison_years.csv
"""

import os
import sys
import zipfile
import numpy as np
import netCDF4 as nc
import geopandas as gpd
from shapely.geometry import Point
import pandas as pd

# Paths
EDGAR_DIR = "/mnt/c/Users/ozgur/OneDrive/ClimateProjects/EDGAR_sector"
NC_DIR = os.path.join(EDGAR_DIR, "nc_timeseries")
ZIP_DIR = EDGAR_DIR
GADM_PATH = "/mnt/c/Users/ozgur/OneDrive/ClimateProjects/mexico-cpi-overlap/gadm/gadm41_MEX_1.shp"
OUTPUT_DIR = "/mnt/c/Users/ozgur/OneDrive/ClimateProjects/mexico-cpi-overlap/states/common"

# State × year extraction targets
TARGETS = [
    ("Querétaro",       "Querétaro",        2021),
    ("CDMX",            "Distrito Federal", 2020),
    ("Durango",         "Durango",          2022),
    ("Morelos",         "Morelos",          2014),
    ("Guanajuato",      "Guanajuato",       2013),
    ("Tamaulipas",      "Tamaulipas",       2013),
    ("San Luis Potosí", "San Luis Potosí",  2014),
]

# Sectors (same as existing timeseries)
SECTORS = [
    ("AGS",               "3.C"),
    ("AWB",               "3.C.1b"),
    ("CHE",               "2.B"),
    ("ENE",               "1.A.1.a"),
    ("ENF",               "3.A.1"),
    ("IDE",               "5.A"),
    ("IND",               "1.A.2"),
    ("IRO",               "2.C"),
    ("MNM",               "3.A.2"),
    ("N2O",               "3.C.5-6"),
    ("NEU",               "2.D"),
    ("NFE",               "2.C"),
    ("NMM",               "2.A"),
    ("PRO_FFF",           "1.B"),
    ("PRU_SOL",           "2.D-2G"),
    ("RCO",               "1.A.4"),
    ("REF_TRF",           "1.A.1.bc"),
    ("SWD_INC",           "4.C"),
    ("SWD_LDF",           "4.A"),
    ("TNR_Aviation_CDS",  "1.A.3.a"),
    ("TNR_Aviation_CRS",  "1.A.3.a"),
    ("TNR_Aviation_LTO",  "1.A.3.a"),
    ("TNR_Other",         "1.A.3.ce"),
    ("TNR_Ship",          "1.A.3.d"),
    ("TRO",               "1.A.3.b"),
    ("WWT",               "4.D"),
]


def ensure_nc_file(sector, year):
    """Ensure the NC file for a given sector/year exists, extracting from zip if needed."""
    fname = f"EDGAR_2025_GHG_GWP_100_AR5_GHG_{year}_{sector}_emi.nc"
    fpath = os.path.join(NC_DIR, fname)
    if os.path.exists(fpath):
        return fpath

    # Extract from zip
    zip_name = f"{sector}_emi_nc.zip"
    zip_path = os.path.join(ZIP_DIR, zip_name)
    if not os.path.exists(zip_path):
        print(f"  WARNING: No zip found for {sector}: {zip_path}")
        return None

    print(f"  Extracting {fname} from {zip_name}...")
    with zipfile.ZipFile(zip_path, 'r') as zf:
        if fname in zf.namelist():
            zf.extract(fname, NC_DIR)
            return fpath
        else:
            print(f"  WARNING: {fname} not found in {zip_name}")
            return None


def create_state_mask(gadm_name, lat_arr, lon_arr, gdf):
    """Create boolean mask for grid cells within state boundary."""
    state = gdf[gdf["NAME_1"] == gadm_name]
    if len(state) == 0:
        raise ValueError(f"State '{gadm_name}' not found in GADM")

    state_geom = state.geometry.values[0]
    bounds = state_geom.bounds  # minx, miny, maxx, maxy

    lat_mask = (lat_arr >= bounds[1] - 0.1) & (lat_arr <= bounds[3] + 0.1)
    lon_mask = (lon_arr >= bounds[0] - 0.1) & (lon_arr <= bounds[2] + 0.1)
    lat_idx = np.where(lat_mask)[0]
    lon_idx = np.where(lon_mask)[0]

    mask = np.zeros((len(lat_arr), len(lon_arr)), dtype=bool)
    n_in = 0
    for i in lat_idx:
        for j in lon_idx:
            if state_geom.contains(Point(lon_arr[j], lat_arr[i])):
                mask[i, j] = True
                n_in += 1

    print(f"  {gadm_name}: {n_in} grid cells in mask")
    return mask


def extract_emissions(nc_path, mask):
    """Sum masked cells from emi file (ton/cell/year), return KtCO2e."""
    ds = nc.Dataset(nc_path)
    # Find the emissions variable
    for var in ds.variables:
        if var not in ('lat', 'lon', 'time'):
            data = ds.variables[var][:]
            break
    ds.close()

    if data.ndim == 3:
        data = data[0, :, :]

    # Mask and sum: tonnes → KtCO2e (÷1000)
    masked = np.where(mask & ~np.isnan(data) & (data > 0), data, 0.0)
    total_tonnes = float(masked.sum())
    return round(total_tonnes / 1000.0, 4)


def main():
    # Get lat/lon arrays from a reference file
    ref = os.path.join(NC_DIR, "EDGAR_2025_GHG_GWP_100_AR5_GHG_2020_ENE_emi.nc")
    ds = nc.Dataset(ref)
    lat_arr = ds.variables['lat'][:]
    lon_arr = ds.variables['lon'][:]
    ds.close()

    # Load GADM once
    print("Loading GADM shapefile...")
    gdf = gpd.read_file(GADM_PATH)

    # Determine unique years needed
    years_needed = set(y for _, _, y in TARGETS)
    # Determine unique GADM names
    gadm_names = set(g for _, g, _ in TARGETS)

    # Check which years need extraction from zips
    for year in years_needed:
        test_file = os.path.join(NC_DIR, f"EDGAR_2025_GHG_GWP_100_AR5_GHG_{year}_ENE_emi.nc")
        if not os.path.exists(test_file):
            print(f"Year {year} not in nc_timeseries, will extract from zips")

    # Build masks (reuse across sectors for same state)
    print("\nBuilding state masks...")
    masks = {}
    for gadm_name in gadm_names:
        masks[gadm_name] = create_state_mask(gadm_name, lat_arr, lon_arr, gdf)

    # Extract emissions
    print("\nExtracting emissions...")
    rows = []
    for state_name, gadm_name, year in TARGETS:
        print(f"\n--- {state_name} ({gadm_name}), year {year} ---")
        mask = masks[gadm_name]

        for sector, ipcc in SECTORS:
            nc_path = ensure_nc_file(sector, year)
            if nc_path is None:
                rows.append({
                    "state": state_name,
                    "gadm_name": gadm_name,
                    "edgar_sector": sector,
                    "ipcc_2006": ipcc,
                    "year": year,
                    "KtCO2e": 0.0,
                })
                continue

            kt = extract_emissions(nc_path, mask)
            rows.append({
                "state": state_name,
                "gadm_name": gadm_name,
                "edgar_sector": sector,
                "ipcc_2006": ipcc,
                "year": year,
                "KtCO2e": kt,
            })

    # Save
    df = pd.DataFrame(rows)
    out_path = os.path.join(OUTPUT_DIR, "edgar_inventory_comparison_years.csv")
    df.to_csv(out_path, index=False)
    print(f"\nSaved: {out_path}")

    # Summary table
    print(f"\n{'='*60}")
    print(f"SUMMARY: EDGAR Total Emissions by State")
    print(f"{'='*60}")
    print(f"{'State':<20} {'Year':>6} {'EDGAR Total (KtCO₂e)':>22}")
    print(f"{'-'*20} {'-'*6} {'-'*22}")
    for state_name, gadm_name, year in TARGETS:
        sub = df[(df["state"] == state_name) & (df["year"] == year)]
        total = sub["KtCO2e"].sum()
        print(f"{state_name:<20} {year:>6} {total:>20,.1f}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
