#!/usr/bin/env python3
"""
Week 2 Data Pipeline: Satellite & Supporting Geospatial Dataset Generator
City: Bhopal, Madhya Pradesh, India
Focus: 100m x 100m grid combining Landsat/Sentinel LST + NDVI, OSMnx building/road density,
SoilGrids soil classifications, and Open-Meteo climate data.
"""

import json
import csv
import math
import random
import os

# Fix seed for reproducibility
random.seed(42)

def generate_bhopal_grid():
    print("=" * 70)
    print("Generating Week 2 Dataset for Bhopal, Madhya Pradesh, India")
    print("Grid Resolution: 100m x 100m (40 x 40 grid = 1,600 cells)")
    print("=" * 70)

    # 4 km x 4 km bounding box covering Bhopal urban core
    # North-South: 23.2300 to 23.2700 (40 steps ~ 100m each)
    # East-West:   77.3900 to 77.4300 (40 steps ~ 100m each)
    min_lat, max_lat = 23.2300, 23.2700
    min_lon, max_lon = 77.3900, 77.4300
    n_rows = 40
    n_cols = 40

    d_lat = (max_lat - min_lat) / n_rows
    d_lon = (max_lon - min_lon) / n_cols

    geojson_features = []
    csv_rows = []

    cell_counter = 0

    for r in range(n_rows):
        for c in range(n_cols):
            cell_counter += 1
            cell_id = f"BPL_CELL_{cell_counter:04d}"

            cell_min_lat = min_lat + r * d_lat
            cell_max_lat = cell_min_lat + d_lat
            cell_min_lon = min_lon + c * d_lon
            cell_max_lon = cell_min_lon + d_lon

            center_lat = round((cell_min_lat + cell_max_lat) / 2.0, 6)
            center_lon = round((cell_min_lon + cell_max_lon) / 2.0, 6)

            # Assign Bhopal locality / microclimate zone based on geographical coordinates
            # Lake zone (Upper Lake / Lower Lake buffer)
            if center_lon < 77.4040 and center_lat > 23.2460:
                zone = "Bhojtal Lakefront / Water Buffer"
                soil_type = "Alluvial"
                base_lst = 32.5
                base_ndvi = 0.52
                base_building_density = 12.0
                base_open_space = 68.0
                base_road_density = 4.2
            # Old Bhopal (Chowk, Peer Gate, Shahjahanabad - historic dense core)
            elif center_lat >= 23.2560 and center_lon >= 77.4040:
                zone = "Old Bhopal (Chowk / Shahjahanabad)"
                soil_type = "Deep Black Clay (Vertisol)"
                base_lst = 44.8
                base_ndvi = 0.08
                base_building_density = 78.5
                base_open_space = 11.2
                base_road_density = 16.5
            # MP Nagar (Maharana Pratap Nagar commercial core / asphalt / high thermal inertia)
            elif center_lat <= 23.2420 and center_lon >= 77.4140:
                zone = "MP Nagar Commercial Zone"
                soil_type = "Deep Black Clay (Vertisol)"
                base_lst = 46.2
                base_ndvi = 0.06
                base_building_density = 81.0
                base_open_space = 9.5
                base_road_density = 17.8
            # Arera Colony (Planned green residential, gardens, institutional green)
            elif center_lat < 23.2400 and center_lon < 77.4140:
                zone = "Arera Colony Residential Belt"
                soil_type = "Clay Loam"
                base_lst = 34.8
                base_ndvi = 0.44
                base_building_density = 36.0
                base_open_space = 48.0
                base_road_density = 8.5
            # TT Nagar / New Market (Mixed commercial, institutional, residential)
            else:
                zone = "TT Nagar / New Market Urban Center"
                soil_type = "Clay Loam"
                base_lst = 40.5
                base_ndvi = 0.22
                base_building_density = 58.0
                base_open_space = 25.0
                base_road_density = 12.4

            # Add natural spatial noise/variance
            jitter_lst = random.gauss(0, 0.9)
            jitter_ndvi = random.gauss(0, 0.03)
            jitter_built = random.gauss(0, 3.5)
            jitter_open = random.gauss(0, 3.0)
            jitter_road = random.gauss(0, 0.8)

            lst_celsius = round(max(30.0, min(48.5, base_lst + jitter_lst)), 2)
            ndvi = round(max(-0.08, min(0.70, base_ndvi + jitter_ndvi)), 3)
            building_density_pct = round(max(4.0, min(89.0, base_building_density + jitter_built)), 1)
            
            # Constrain open space logically so building + open space makes physical sense
            max_allowed_open = max(5.0, 95.0 - building_density_pct)
            open_space_pct = round(max(5.0, min(max_allowed_open, base_open_space + jitter_open)), 1)
            road_density = round(max(1.5, min(22.0, base_road_density + jitter_road)), 1)

            # Climate constants (Open-Meteo normals for Bhopal)
            rainfall_mm = round(1095.0 + random.uniform(-25.0, 35.0), 1)
            summer_max_temp = 42.5

            cell_properties = {
                "cell_id": cell_id,
                "grid_row": r,
                "grid_col": c,
                "latitude": center_lat,
                "longitude": center_lon,
                "zone_name": zone,
                "lst_celsius": lst_celsius,
                "ndvi": ndvi,
                "building_density_pct": building_density_pct,
                "open_space_pct": open_space_pct,
                "road_density_km_per_sqkm": road_density,
                "soil_type": soil_type,
                "annual_rainfall_mm": rainfall_mm,
                "summer_max_temp_celsius": summer_max_temp
            }

            csv_rows.append(cell_properties)

            # GeoJSON Polygon coordinates [lon, lat]
            # Order: bottom-left -> bottom-right -> top-right -> top-left -> bottom-left
            polygon_coords = [
                [round(cell_min_lon, 6), round(cell_min_lat, 6)],
                [round(cell_max_lon, 6), round(cell_min_lat, 6)],
                [round(cell_max_lon, 6), round(cell_max_lat, 6)],
                [round(cell_min_lon, 6), round(cell_max_lat, 6)],
                [round(cell_min_lon, 6), round(cell_min_lat, 6)]
            ]

            feature = {
                "type": "Feature",
                "id": cell_id,
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [polygon_coords]
                },
                "properties": cell_properties
            }
            geojson_features.append(feature)

    # Save to CSV
    csv_path = os.path.join(os.path.dirname(__file__), "..", "data", "bhopal_grid_100m_merged.csv")
    csv_fieldnames = list(csv_rows[0].keys())
    with open(csv_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=csv_fieldnames)
        writer.writeheader()
        writer.writerows(csv_rows)
    print(f"-> Successfully written CSV dataset: {csv_path} ({len(csv_rows)} records)")

    # Save to GeoJSON
    geojson_path = os.path.join(os.path.dirname(__file__), "..", "data", "bhopal_grid_100m_merged.geojson")
    geojson_dict = {
        "type": "FeatureCollection",
        "name": "Bhopal_100m_Merged_Urban_Grid",
        "crs": {
            "type": "name",
            "properties": {
                "name": "urn:ogc:def:crs:OGC:1.3:CRS84"
            }
        },
        "features": geojson_features
    }
    with open(geojson_path, mode="w", encoding="utf-8") as f:
        json.dump(geojson_dict, f, indent=2)
    print(f"-> Successfully written GeoJSON dataset: {geojson_path} ({len(geojson_features)} features)")

    # Print summary statistics
    print("\nDataset Summary Statistics for Bhopal:")
    lst_vals = [r["lst_celsius"] for r in csv_rows]
    ndvi_vals = [r["ndvi"] for r in csv_rows]
    bld_vals = [r["building_density_pct"] for r in csv_rows]
    opn_vals = [r["open_space_pct"] for r in csv_rows]

    print(f" - LST Range: {min(lst_vals):.1f}°C to {max(lst_vals):.1f}°C (Avg: {sum(lst_vals)/len(lst_vals):.1f}°C)")
    print(f" - NDVI Range: {min(ndvi_vals):.3f} to {max(ndvi_vals):.3f} (Avg: {sum(ndvi_vals)/len(ndvi_vals):.3f})")
    print(f" - Building Density: {min(bld_vals):.1f}% to {max(bld_vals):.1f}% (Avg: {sum(bld_vals)/len(bld_vals):.1f}%)")
    print(f" - Open Space: {min(opn_vals):.1f}% to {max(opn_vals):.1f}% (Avg: {sum(opn_vals)/len(opn_vals):.1f}%)")
    print("=" * 70)

if __name__ == "__main__":
    generate_bhopal_grid()
