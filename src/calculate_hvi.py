#!/usr/bin/env python3
"""
Week 3: Heat Vulnerability Index (HVI) Calculator & Hotspot Ranker
City: Bhopal, Madhya Pradesh, India
Focus: Multi-criteria weighted normalization of Land Surface Temperature,
vegetation deficit, building footprint density, and lack of permeable open space.
"""

import csv
import json
import os

def calculate_hvi():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    csv_in = os.path.join(base_dir, "data", "bhopal_grid_100m_merged.csv")
    geojson_in = os.path.join(base_dir, "data", "bhopal_grid_100m_merged.geojson")
    hotspots_out = os.path.join(base_dir, "outputs", "bhopal_hotspots_ranked.csv")

    print("=" * 70)
    print("Calculating Heat Vulnerability Index (HVI) for Bhopal Grid Cells")
    print("=" * 70)

    # Read CSV
    with open(csv_in, mode="r", encoding="utf-8") as f:
        reader = list(csv.DictReader(f))

    # Convert numeric fields
    for row in reader:
        row["lst_celsius"] = float(row["lst_celsius"])
        row["ndvi"] = float(row["ndvi"])
        row["building_density_pct"] = float(row["building_density_pct"])
        row["open_space_pct"] = float(row["open_space_pct"])
        row["road_density_km_per_sqkm"] = float(row["road_density_km_per_sqkm"])
        row["annual_rainfall_mm"] = float(row["annual_rainfall_mm"])
        row["latitude"] = float(row["latitude"])
        row["longitude"] = float(row["longitude"])

    # Extract min/max for min-max scaling
    min_lst = min(r["lst_celsius"] for r in reader)
    max_lst = max(r["lst_celsius"] for r in reader)
    min_ndvi = min(r["ndvi"] for r in reader)
    max_ndvi = max(r["ndvi"] for r in reader)
    min_bld = min(r["building_density_pct"] for r in reader)
    max_bld = max(r["building_density_pct"] for r in reader)
    min_open = min(r["open_space_pct"] for r in reader)
    max_open = max(r["open_space_pct"] for r in reader)

    # Weights defined in Week 3 syllabus
    # W_lst = 0.35, W_ndvi = 0.25, W_built = 0.25, W_open = 0.15
    W_LST = 0.35
    W_NDVI = 0.25
    W_BUILT = 0.25
    W_OPEN = 0.15

    for row in reader:
        # Normalized indicators [0.0 to 1.0]
        # Higher means greater heat vulnerability
        norm_lst = (row["lst_celsius"] - min_lst) / (max_lst - min_lst)
        norm_ndvi_deficit = 1.0 - ((row["ndvi"] - min_ndvi) / (max_ndvi - min_ndvi))
        norm_built = (row["building_density_pct"] - min_bld) / (max_bld - min_bld)
        norm_open_deficit = 1.0 - ((row["open_space_pct"] - min_open) / (max_open - min_open))

        hvi = (
            W_LST * norm_lst +
            W_NDVI * norm_ndvi_deficit +
            W_BUILT * norm_built +
            W_OPEN * norm_open_deficit
        )
        row["hvi_score"] = round(hvi, 4)

        if hvi >= 0.75:
            row["hvi_category"] = "Extreme Hotspot"
        elif hvi >= 0.55:
            row["hvi_category"] = "High Vulnerability"
        elif hvi >= 0.35:
            row["hvi_category"] = "Moderate Vulnerability"
        else:
            row["hvi_category"] = "Low Vulnerability"

    # Sort by HVI descending
    reader_sorted = sorted(reader, key=lambda x: x["hvi_score"], reverse=True)

    # Assign rank
    for rank, row in enumerate(reader_sorted, start=1):
        row["hvi_rank"] = rank

    # Write back updated merged CSV with HVI fields
    csv_fieldnames = list(reader_sorted[0].keys())
    with open(csv_in, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=csv_fieldnames)
        writer.writeheader()
        writer.writerows(reader)
    print(f"-> Updated {csv_in} with HVI scores and categories.")

    # Update GeoJSON with HVI properties
    with open(geojson_in, mode="r", encoding="utf-8") as f:
        geojson_data = json.load(f)

    # Map cell_id to properties
    props_by_id = {r["cell_id"]: r for r in reader}
    for feature in geojson_data["features"]:
        cid = feature["id"]
        if cid in props_by_id:
            p = props_by_id[cid]
            feature["properties"]["hvi_score"] = p["hvi_score"]
            feature["properties"]["hvi_category"] = p["hvi_category"]
            feature["properties"]["hvi_rank"] = p["hvi_rank"]

    with open(geojson_in, mode="w", encoding="utf-8") as f:
        json.dump(geojson_data, f, indent=2)
    print(f"-> Updated {geojson_in} with HVI properties.")

    # Extract Top 30 Hotspots
    top_30_hotspots = reader_sorted[:30]
    os.makedirs(os.path.dirname(hotspots_out), exist_ok=True)
    with open(hotspots_out, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=csv_fieldnames)
        writer.writeheader()
        writer.writerows(top_30_hotspots)

    print(f"-> Exported Top 30 Hotspots to: {hotspots_out}")
    print("\n--- Top 10 Bhopal Heat Hotspots ---")
    print(f"{'Rank':<5} {'Cell ID':<14} {'Zone':<32} {'LST (°C)':<10} {'NDVI':<8} {'Built %':<8} {'HVI':<8} {'Category'}")
    print("-" * 105)
    for h in top_30_hotspots[:10]:
        print(f"{h['hvi_rank']:<5} {h['cell_id']:<14} {h['zone_name']:<32} {h['lst_celsius']:<10.1f} {h['ndvi']:<8.3f} {h['building_density_pct']:<8.1f} {h['hvi_score']:<8.4f} {h['hvi_category']}")
    print("=" * 105)

if __name__ == "__main__":
    calculate_hvi()
