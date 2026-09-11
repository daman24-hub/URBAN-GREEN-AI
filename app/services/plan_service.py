"""
Plan Service: Chains hotspots, species matching, and impact estimation into an actionable master planting plan.
"""

import json
import csv
import os
from typing import Dict, Any, List
from app.services.spatial_service import spatial_service
from app.services.impact_service import impact_service
from src.species_matcher import species_filter

class PlanService:
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    def generate_master_plan(
        self,
        city: str = "bhopal",
        top_hotspots: int = 10,
        target_temp_drop: float = 2.0
    ) -> Dict[str, Any]:
        """
        Chains:
        1. Top HVI hotspots retrieval.
        2. Dynamic species matching per hotspot.
        3. Automated tree capacity calculation from open space.
        4. Environmental impact estimation.
        5. Citywide summary aggregation.
        """
        hotspots = spatial_service.get_hotspots(city=city, limit=top_hotspots)
        species_list = spatial_service.species_list

        plan_details = []

        total_trees_all = 0
        total_canopy_all = 0.0
        total_co2_kg_all = 0.0
        total_water_liters_all = 0.0
        temp_drops_all = []

        for cell in hotspots:
            cid = cell["cell_id"]
            zone = cell["zone_name"]
            lat = cell["latitude"]
            lng = cell["longitude"]
            current_lst = cell["lst_celsius"]
            current_hvi = cell["hvi_score"]
            open_pct = cell["open_space_pct"]

            # Available ground space for planting
            # 100m x 100m = 10,000 m2
            open_area_sqm = 10000.0 * (open_pct / 100.0)
            
            # Scale target canopy based on user-requested target_temp_drop (e.g. 1.0 to 3.0°C)
            # 10% canopy gain (~1,000 m2) gives ~1.1 - 1.3°C drop
            desired_canopy_sqm = (target_temp_drop / 1.15) * 1000.0
            # Bound within physical reality: at least 350 m2 (few trees) up to available open space (or max 2,500 m2)
            target_canopy_sqm = max(350.0, min(desired_canopy_sqm, open_area_sqm * 0.75, 2500.0))

            # Get top 3 compatible species from AI matching engine
            recommended_species = species_filter(cell, species_list, top_n=3)

            # Distribute planting counts across top recommended species
            plantings = []
            if recommended_species:
                primary = recommended_species[0]
                secondary = recommended_species[1] if len(recommended_species) > 1 else primary

                prim_sp = spatial_service.species_by_id.get(primary["species_id"], {})
                sec_sp = spatial_service.species_by_id.get(secondary["species_id"], {})

                spread_p = prim_sp.get("canopy_spread_m", 10.0)
                spread_s = sec_sp.get("canopy_spread_m", 8.0)

                area_p = 3.14159 * ((spread_p / 2.0) ** 2)
                area_s = 3.14159 * ((spread_s / 2.0) ** 2)

                # Split target canopy 60/40
                count_p = max(2, int((target_canopy_sqm * 0.6) / area_p))
                count_s = max(2, int((target_canopy_sqm * 0.4) / area_s))

                plantings = [
                    {"species_id": primary["species_id"], "count": count_p},
                    {"species_id": secondary["species_id"], "count": count_s}
                ]
            else:
                plantings = [{"species_id": "SPECIES_05", "count": 10}]

            # Calculate impact
            impact = impact_service.estimate_impact(plantings=plantings, cell_id=cid)

            cell_trees = impact["total_trees"]
            cell_canopy = impact["total_canopy_area_sqm"]
            cell_temp_drop = impact["predicted_temperature_drop_celsius"]
            cell_co2 = impact["annual_co2_sequestration_kg"]
            cell_water = impact["annual_stormwater_intercepted_liters"]

            new_lst = round(max(28.0, current_lst - cell_temp_drop), 2)

            plan_item = {
                "hvi_rank": cell["hvi_rank"],
                "cell_id": cid,
                "zone_name": zone,
                "latitude": lat,
                "longitude": lng,
                "current_lst_celsius": current_lst,
                "current_hvi_score": current_hvi,
                "open_space_pct": open_pct,
                "recommended_trees_count": cell_trees,
                "predicted_temperature_drop_celsius": cell_temp_drop,
                "new_projected_lst_celsius": new_lst,
                "annual_co2_kg": cell_co2,
                "annual_stormwater_liters": cell_water,
                "top_species_selected": recommended_species
            }

            plan_details.append(plan_item)

            total_trees_all += cell_trees
            total_canopy_all += cell_canopy
            total_co2_kg_all += cell_co2
            total_water_liters_all += cell_water
            temp_drops_all.append(cell_temp_drop)

        avg_temp_drop = round(sum(temp_drops_all) / len(temp_drops_all), 2) if temp_drops_all else 0.0

        summary = {
            "city": city.title(),
            "total_hotspot_cells_addressed": len(plan_details),
            "total_trees_to_plant": total_trees_all,
            "total_canopy_area_added_sqm": round(total_canopy_all, 2),
            "average_temperature_reduction_celsius": avg_temp_drop,
            "total_annual_co2_sequestration_metric_tons": round(total_co2_kg_all / 1000.0, 3),
            "total_annual_stormwater_absorbed_megaliters": round(total_water_liters_all / 1000000.0, 3)
        }

        return {
            "summary": summary,
            "plan_details": plan_details
        }

    def export_plan_files(self, plan_data: Dict[str, Any]):
        """
        Exports the master planting plan as GeoJSON and CSV to outputs/
        """
        geojson_out = os.path.join(self.base_dir, "outputs", "bhopal_planting_plan.geojson")
        csv_out = os.path.join(self.base_dir, "outputs", "bhopal_planting_plan.csv")

        os.makedirs(os.path.dirname(geojson_out), exist_ok=True)

        features = []
        csv_rows = []

        for p in plan_data["plan_details"]:
            lat = p["latitude"]
            lng = p["longitude"]
            half_side = 0.00045  # ~50m half-width

            coords = [
                [round(lng - half_side, 6), round(lat - half_side, 6)],
                [round(lng + half_side, 6), round(lat - half_side, 6)],
                [round(lng + half_side, 6), round(lat + half_side, 6)],
                [round(lng - half_side, 6), round(lat + half_side, 6)],
                [round(lng - half_side, 6), round(lat - half_side, 6)]
            ]

            species_names = ", ".join([f"{s['common_name']} ({s['hindi_name']})" for s in p["top_species_selected"][:2]])

            feature = {
                "type": "Feature",
                "id": p["cell_id"],
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [coords]
                },
                "properties": {
                    "cell_id": p["cell_id"],
                    "hvi_rank": p["hvi_rank"],
                    "zone_name": p["zone_name"],
                    "current_lst": p["current_lst_celsius"],
                    "projected_lst": p["new_projected_lst_celsius"],
                    "temp_drop": p["predicted_temperature_drop_celsius"],
                    "recommended_trees": p["recommended_trees_count"],
                    "top_species": species_names,
                    "annual_co2_kg": p["annual_co2_kg"],
                    "annual_stormwater_liters": p["annual_stormwater_liters"]
                }
            }
            features.append(feature)

            csv_rows.append({
                "hvi_rank": p["hvi_rank"],
                "cell_id": p["cell_id"],
                "zone_name": p["zone_name"],
                "latitude": lat,
                "longitude": lng,
                "current_lst_celsius": p["current_lst_celsius"],
                "new_projected_lst_celsius": p["new_projected_lst_celsius"],
                "predicted_temp_drop_celsius": p["predicted_temperature_drop_celsius"],
                "trees_to_plant": p["recommended_trees_count"],
                "top_species": species_names,
                "annual_co2_kg": p["annual_co2_kg"],
                "annual_stormwater_liters": p["annual_stormwater_liters"]
            })

        geojson_doc = {
            "type": "FeatureCollection",
            "name": "Bhopal_Master_Planting_Plan",
            "features": features
        }

        with open(geojson_out, mode="w", encoding="utf-8") as f:
            json.dump(geojson_doc, f, indent=2)

        if csv_rows:
            with open(csv_out, mode="w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=list(csv_rows[0].keys()))
                writer.writeheader()
                writer.writerows(csv_rows)

        print(f"-> Exported GeoJSON Master Plan: {geojson_out}")
        print(f"-> Exported CSV Master Plan: {csv_out}")

plan_service = PlanService()
