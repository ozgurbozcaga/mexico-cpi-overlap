#!/usr/bin/env python3
"""
extract_edgar_zacatecas.py — Extract EDGAR gridded emissions for Zacatecas
==========================================================================
Run this in Claude Code on your local WSL/Ubuntu environment.

Prerequisites:
    pip install netCDF4 xarray numpy geopandas shapely rasterio

Data needed:
    1. EDGAR sector NetCDF files (download from https://edgar.jrc.ec.europa.eu/dataset_ghg2025)
       - Individual sector files: *_ENE_*.nc, *_IND_*.nc, *_TRO_*.nc, etc.
       - OR the TOTALS file: *_TOTALS_*.nc (for aggregate only)
       
    2. GADM Mexico Level 1 shapefile (download from https://gadm.org/download_country.html)
       - Select: Mexico → Shapefile → Level 1
       - Extract to: data/raw/gadm41_MEX_1.shp (and associated .dbf, .shx, .prj files)
       
    Alternatively for geoBoundaries:
       wget https://github.com/wmgeolab/geoBoundaries/raw/main/releaseData/gbOpen/MEX/ADM1/geoBoundaries-MEX-ADM1-all.zip

Usage:
    python3 extract_edgar_zacatecas.py --edgar-dir /path/to/edgar/ncfiles --gadm /path/to/gadm41_MEX_1.shp

Or simply edit the paths below and run:
    python3 extract_edgar_zacatecas.py
"""

import os
import sys
import glob
import numpy as np
import netCDF4 as nc
import geopandas as gpd
from shapely.geometry import Point

# =====================================================================
# CONFIGURATION — Edit these paths for your local setup
# =====================================================================

# Path to GADM Level 1 shapefile for Mexico
# Download from: https://gadm.org/download_country.html → Mexico → Shapefile → Level 1
GADM_PATH = "data/raw/gadm41_MEX_1.shp"

# Path to EDGAR NetCDF files directory
# Download sector files from: https://edgar.jrc.ec.europa.eu/dataset_ghg2025
# File naming pattern: EDGAR_2025_GHG_GWP_100_AR5_GHG_2024_{SECTOR}_flx.nc
EDGAR_DIR = "data/raw/edgar/"

# State name in GADM (NAME_1 field)
STATE_NAME = "Zacatecas"

# Output directory
OUTPUT_DIR = "data/processed/"

# =====================================================================
# SECTOR MAPPING: EDGAR sector codes → our analysis categories
# =====================================================================

SECTOR_MAP = {
    # EDGAR code: (IPCC 2006 mapping, description, category for S/F/E analysis)
    "ENE":     ("1.A.1.a", "Power industry", "ELECTRICITY"),
    "REF_TRF": ("1.A.1.bc", "Oil refineries & transformation", "REFINING"),
    "IND":     ("1.A.2", "Combustion for manufacturing", "MANUFACTURING"),
    "TRO":     ("1.A.3.b", "Road transportation", "TRANSPORT"),
    "TNR_Aviation_LTO": ("1.A.3.a_LTO", "Aviation landing/takeoff", "TRANSPORT"),
    "TNR_Aviation_CDS": ("1.A.3.a_CDS", "Aviation climb/descent", "TRANSPORT"),
    "TNR_Aviation_CRS": ("1.A.3.a_CRS", "Aviation cruise", "TRANSPORT"),
    "TNR_Other": ("1.A.3.ce", "Railways/pipelines/off-road", "TRANSPORT"),
    "TNR_Ship": ("1.A.3.d", "Shipping", "TRANSPORT"),
    "RCO":     ("1.A.4", "Energy for buildings", "RESIDENTIAL_COMMERCIAL"),
    "PRO_COAL": ("1.B.1", "Fugitive coal", "FUGITIVE"),
    "PRO_OIL": ("1.B.2_oil", "Fugitive oil", "FUGITIVE"),
    "PRO_GAS": ("1.B.2_gas", "Fugitive gas", "FUGITIVE"),
    "PRO_FFF": ("1.B+5.B", "Fuel exploitation + fossil fuel fires", "FUGITIVE"),
    "CHE":     ("2.B", "Chemical processes", "IPPU"),
    "IRO":     ("2.C", "Iron and steel production", "IPPU"),
    "PRU_SOL": ("2.D+2E+2F+2G", "Solvents/products use (incl. HFCs)", "IPPU"),
    "ENF":     ("3.A.1", "Enteric fermentation", "AFOLU"),
    "MNM":     ("3.A.2", "Manure management", "AFOLU"),
    "AGS":     ("3.C", "Agricultural soils", "AFOLU"),
    "AWB":     ("3.C.1b", "Agricultural waste burning", "AFOLU"),
    "N2O":     ("3.C.5+6", "Indirect N2O from agriculture", "AFOLU"),
    "SWD_LDF": ("4.A+4B+4E", "Solid waste landfills", "WASTE"),
    "SWD_INC": ("4.C", "Solid waste incineration", "WASTE"),
    "WWT":     ("4.D", "Wastewater handling", "WASTE"),
    "IDE":     ("5.A", "Indirect emissions NOx/NH3", "OTHER"),
}


def create_state_mask(gadm_path, state_name, lat_arr, lon_arr):
    """
    Create a boolean mask for grid cells whose centers fall within the state boundary.
    
    Args:
        gadm_path: Path to GADM Level 1 shapefile
        state_name: Name of the state (NAME_1 field in GADM)
        lat_arr: Array of latitude centers (from NetCDF)
        lon_arr: Array of longitude centers (from NetCDF)
    
    Returns:
        2D boolean mask (lat × lon), state geometry
    """
    print(f"Loading GADM shapefile: {gadm_path}")
    gdf = gpd.read_file(gadm_path)
    
    # Find the state
    state = gdf[gdf["NAME_1"] == state_name]
    if len(state) == 0:
        # Try case-insensitive
        state = gdf[gdf["NAME_1"].str.lower() == state_name.lower()]
    if len(state) == 0:
        print(f"ERROR: State '{state_name}' not found. Available states:")
        for s in sorted(gdf["NAME_1"].unique()):
            print(f"  {s}")
        sys.exit(1)
    
    state_geom = state.geometry.values[0]
    bounds = state_geom.bounds  # (minx, miny, maxx, maxy) = (lon_min, lat_min, lon_max, lat_max)
    print(f"State bounds: lat [{bounds[1]:.2f}, {bounds[3]:.2f}], lon [{bounds[0]:.2f}, {bounds[2]:.2f}]")
    
    # Subset to bounding box first (for speed)
    lat_mask_bb = (lat_arr >= bounds[1] - 0.1) & (lat_arr <= bounds[3] + 0.1)
    lon_mask_bb = (lon_arr >= bounds[0] - 0.1) & (lon_arr <= bounds[2] + 0.1)
    
    lat_idx = np.where(lat_mask_bb)[0]
    lon_idx = np.where(lon_mask_bb)[0]
    
    # Create full mask (initialized to False)
    mask = np.zeros((len(lat_arr), len(lon_arr)), dtype=bool)
    
    # Check each cell center in the bounding box
    n_in = 0
    for i in lat_idx:
        for j in lon_idx:
            pt = Point(lon_arr[j], lat_arr[i])
            if state_geom.contains(pt):
                mask[i, j] = True
                n_in += 1
    
    print(f"Grid cells inside {state_name}: {n_in}")
    
    # Estimate area
    R = 6371.0  # km
    total_area_km2 = 0
    dlon_rad = np.radians(0.1)
    for i in lat_idx:
        for j in lon_idx:
            if mask[i, j]:
                lat_s = np.radians(lat_arr[i] - 0.05)
                lat_n = np.radians(lat_arr[i] + 0.05)
                cell_area = R**2 * abs(np.sin(lat_n) - np.sin(lat_s)) * dlon_rad
                total_area_km2 += cell_area
    print(f"Masked area: {total_area_km2:,.0f} km² (official Zacatecas: 72,275 km²)")
    
    return mask, state_geom


def extract_sector_emissions(nc_path, mask, lat_arr, lon_arr, sector_code):
    """
    Extract annual emissions for a single sector within the masked area.
    
    Args:
        nc_path: Path to sector NetCDF file
        mask: 2D boolean mask
        lat_arr, lon_arr: Coordinate arrays
        sector_code: EDGAR sector code (for logging)
    
    Returns:
        Total annual emissions in KtCO2e
    """
    ds = nc.Dataset(nc_path)
    
    # Find the flux variable (could be 'fluxes' or 'emi_*' or sector name)
    flux_var = None
    for var in ds.variables:
        if var not in ('lat', 'lon', 'time'):
            flux_var = var
            break
    
    if flux_var is None:
        print(f"  WARNING: No flux variable found in {nc_path}")
        ds.close()
        return 0.0
    
    flux = ds.variables[flux_var][:]
    units = ds.variables[flux_var].units if hasattr(ds.variables[flux_var], 'units') else 'unknown'
    
    # Handle potential extra dimensions (time)
    if flux.ndim == 3:
        flux = flux[0, :, :]  # Take first (only) time step
    
    R = 6371000.0  # meters
    dlon_rad = np.radians(0.1)
    seconds_per_year = 365.25 * 24 * 3600
    
    total_kg_s = 0.0
    for i in range(len(lat_arr)):
        for j in range(len(lon_arr)):
            if mask[i, j] and flux[i, j] > 0 and not np.isnan(flux[i, j]):
                lat_s = np.radians(lat_arr[i] - 0.05)
                lat_n = np.radians(lat_arr[i] + 0.05)
                cell_area = R**2 * abs(np.sin(lat_n) - np.sin(lat_s)) * dlon_rad
                total_kg_s += flux[i, j] * cell_area
    
    ds.close()
    
    # Convert kg/s → kt/year
    total_kt = total_kg_s * seconds_per_year / 1e6
    return total_kt


def main():
    """Main extraction routine."""
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Step 1: Create state mask
    # --------------------------
    # First, get lat/lon from any EDGAR file
    edgar_files = glob.glob(os.path.join(EDGAR_DIR, "*.nc"))
    if not edgar_files:
        # Try current directory
        edgar_files = glob.glob("*.nc")
    if not edgar_files:
        print("ERROR: No EDGAR NetCDF files found.")
        print(f"  Looked in: {EDGAR_DIR} and current directory")
        print("  Download from: https://edgar.jrc.ec.europa.eu/dataset_ghg2025")
        sys.exit(1)
    
    ref_file = edgar_files[0]
    print(f"Reference file: {ref_file}")
    
    ds = nc.Dataset(ref_file)
    lat_arr = ds.variables['lat'][:]
    lon_arr = ds.variables['lon'][:]
    ds.close()
    
    # Create mask
    if not os.path.exists(GADM_PATH):
        print(f"ERROR: GADM shapefile not found at {GADM_PATH}")
        print("  Download from: https://gadm.org/download_country.html → Mexico → Level 1")
        sys.exit(1)
    
    mask, state_geom = create_state_mask(GADM_PATH, STATE_NAME, lat_arr, lon_arr)
    
    # Step 2: Extract emissions by sector
    # ------------------------------------
    results = []
    
    for sector_code, (ipcc_code, description, category) in SECTOR_MAP.items():
        # Find matching NetCDF file
        pattern = f"*_{sector_code}_*.nc"
        matches = glob.glob(os.path.join(EDGAR_DIR, pattern))
        
        if not matches:
            # Try with different patterns
            matches = glob.glob(os.path.join(EDGAR_DIR, f"*{sector_code}*flx.nc"))
        
        if not matches:
            print(f"  SKIP: {sector_code} ({description}) — no file found")
            results.append({
                "edgar_sector": sector_code,
                "ipcc_2006": ipcc_code,
                "description": description,
                "category": category,
                "KtCO2e": 0.0,
                "status": "file_not_found",
            })
            continue
        
        nc_path = matches[0]
        print(f"  Processing: {sector_code} ({description})")
        kt = extract_sector_emissions(nc_path, mask, lat_arr, lon_arr, sector_code)
        print(f"    → {kt:,.1f} KtCO2e")
        
        results.append({
            "edgar_sector": sector_code,
            "ipcc_2006": ipcc_code,
            "description": description,
            "category": category,
            "KtCO2e": round(kt, 2),
            "status": "extracted",
        })
    
    # Also process TOTALS if available
    totals_files = glob.glob(os.path.join(EDGAR_DIR, "*TOTALS*flx.nc"))
    if totals_files:
        print(f"  Processing: TOTALS (all sectors)")
        kt_total = extract_sector_emissions(totals_files[0], mask, lat_arr, lon_arr, "TOTALS")
        print(f"    → {kt_total:,.1f} KtCO2e")
        results.append({
            "edgar_sector": "TOTALS",
            "ipcc_2006": "ALL",
            "description": "All sectors combined",
            "category": "TOTAL",
            "KtCO2e": round(kt_total, 2),
            "status": "extracted",
        })
    
    # Step 3: Save results
    # --------------------
    import pandas as pd
    df = pd.DataFrame(results)
    
    output_path = os.path.join(OUTPUT_DIR, "zacatecas_edgar_gridded_emissions.csv")
    df.to_csv(output_path, index=False)
    print(f"\nSaved: {output_path}")
    
    # Summary
    extracted = df[df["status"] == "extracted"]
    if len(extracted) > 0:
        print(f"\n{'='*60}")
        print(f"ZACATECAS EDGAR GRIDDED EMISSIONS (2024)")
        print(f"{'='*60}")
        
        sector_sum = extracted[extracted["edgar_sector"] != "TOTALS"]["KtCO2e"].sum()
        
        for _, row in extracted.iterrows():
            if row["edgar_sector"] != "TOTALS":
                print(f"  {row['edgar_sector']:20s} {row['description']:40s} {row['KtCO2e']:8.1f} KtCO2e")
        
        print(f"  {'─'*70}")
        print(f"  {'SUM':20s} {'(sector files)':40s} {sector_sum:8.1f} KtCO2e")
        
        totals_row = extracted[extracted["edgar_sector"] == "TOTALS"]
        if len(totals_row) > 0:
            print(f"  {'TOTALS':20s} {'(totals file)':40s} {totals_row.iloc[0]['KtCO2e']:8.1f} KtCO2e")
        
        print(f"\n  Total: {sector_sum/1000:,.2f} MtCO2e (from sector files)")
    
    print("\nDone.")


if __name__ == "__main__":
    main()
