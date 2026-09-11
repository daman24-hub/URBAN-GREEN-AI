"""
Spatial Service: Grid cell retrieval, spatial indexing, and nearest-neighbor search.
"""

import csv
import math
import os
from typing import List, Dict, Any, Optional, Tuple

class SpatialService:
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.csv_path = os.path.join(self.base_dir, "data", "bhopal_grid_100m_merged.csv")
        self.species_csv_path = os.path.join(self.base_dir, "data", "bhopal_urban_tree_species.csv")
        
        self.grid_cells: List[Dict[str, Any]] = []
        self.cells_by_id: Dict[str, Dict[str, Any]] = []
        self.species_list: List[Dict[str, Any]] = []
        self.species_by_id: Dict[str, Dict[str, Any]] = {}
        
        self._load_data()

    def _load_data(self):
        # Load grid cells
        if os.path.exists(self.csv_path):
            with open(self.csv_path, mode="r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    cell = {
                        "cell_id": row["cell_id"],
                        "latitude": float(row["latitude"]),
                        "longitude": float(row["longitude"]),
                        "zone_name": row["zone_name"],
                        "lst_celsius": float(row["lst_celsius"]),
                        "ndvi": float(row["ndvi"]),
                        "building_density_pct": float(row["building_density_pct"]),
                        "open_space_pct": float(row["open_space_pct"]),
                        "road_density_km_per_sqkm": float(row["road_density_km_per_sqkm"]),
                        "soil_type": row["soil_type"],
                        "annual_rainfall_mm": float(row["annual_rainfall_mm"]),
                        "hvi_score": float(row.get("hvi_score", 0.5)),
                        "hvi_category": row.get("hvi_category", "Moderate Vulnerability"),
                        "hvi_rank": int(row.get("hvi_rank", 999))
                    }
                    self.grid_cells.append(cell)
            self.cells_by_id = {c["cell_id"]: c for c in self.grid_cells}
        else:
            print(f"Warning: {self.csv_path} not found.")

        # Load tree species
        if os.path.exists(self.species_csv_path):
            with open(self.species_csv_path, mode="r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    sp = {
                        "species_id": row["species_id"],
                        "scientific_name": row["scientific_name"],
                        "common_name": row["common_name"],
                        "hindi_name": row["hindi_name"],
                        "canopy_spread_m": float(row["canopy_spread_m"]),
                        "canopy_category": row["canopy_category"],
                        "mature_height_m": float(row["mature_height_m"]),
                        "cooling_value": row["cooling_value"],
                        "water_requirement": row["water_requirement"],
                        "soil_preference": row["soil_preference"],
                        "root_type": row["root_type"],
                        "drought_tolerance": row["drought_tolerance"],
                        "air_pollution_tolerance": row["air_pollution_tolerance"],
                        "growth_rate": row["growth_rate"],
                        "crown_density": row["crown_density"],
                        "ideal_urban_context": row["ideal_urban_context"]
                    }
                    self.species_list.append(sp)
            self.species_by_id = {s["species_id"]: s for s in self.species_list}
        else:
            print(f"Warning: {self.species_csv_path} not found.")

    def get_hotspots(
        self,
        city: str = "bhopal",
        limit: int = 20,
        min_hvi: Optional[float] = None,
        category: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        # Sort by HVI descending
        filtered = list(self.grid_cells)
        if min_hvi is not None:
            filtered = [c for c in filtered if c["hvi_score"] >= min_hvi]
        if category:
            filtered = [c for c in filtered if category.lower() in c["hvi_category"].lower()]
        
        filtered_sorted = sorted(filtered, key=lambda x: x["hvi_score"], reverse=True)
        return filtered_sorted[:limit]

    def get_cell_by_id(self, cell_id: str) -> Optional[Dict[str, Any]]:
        return self.cells_by_id.get(cell_id)

    def get_nearest_cell(self, lat: float, lng: float) -> Tuple[Optional[Dict[str, Any]], float]:
        """
        Computes nearest grid cell centroid using Haversine formula.
        Returns (cell_dict, distance_in_meters).
        """
        if not self.grid_cells:
            return None, 0.0

        min_dist = float("inf")
        nearest = None

        R = 6371000.0  # Earth radius in meters
        phi1 = math.radians(lat)

        for cell in self.grid_cells:
            phi2 = math.radians(cell["latitude"])
            dphi = math.radians(cell["latitude"] - lat)
            dlambda = math.radians(cell["longitude"] - lng)

            a = math.sin(dphi / 2.0)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2.0)**2
            c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
            dist = R * c

            if dist < min_dist:
                min_dist = dist
                nearest = cell

        return nearest, round(min_dist, 1)

spatial_service = SpatialService()
