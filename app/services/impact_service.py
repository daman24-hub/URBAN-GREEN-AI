"""
Impact Service: Computes predicted microclimate temperature reduction,
annual CO2 sequestration, and stormwater runoff interception based on i-Tree Eco benchmarks.
"""

import math
from typing import List, Dict, Any, Optional
from app.services.spatial_service import spatial_service

class ImpactService:
    def __init__(self):
        # i-Tree Eco carbon sequestration benchmarks for subtropical species
        self.co2_rates = {
            "Large": 32.0,    # kg CO2/tree/year
            "Medium": 22.0,   # kg CO2/tree/year
            "Small": 11.0     # kg CO2/tree/year
        }
        
        # Cooling multiplier based on species evapotranspiration & shade density
        self.cooling_multipliers = {
            "Very High": 1.30,
            "High": 1.10,
            "Moderate": 0.85
        }
        
        # Bhopal annual precipitation constant (meters)
        self.bhopal_annual_rain_m = 1.095
        # Canopy rainfall interception coefficient (i-Tree standard: ~20% of gross precipitation)
        self.canopy_interception_coeff = 0.20

    def estimate_impact(
        self,
        plantings: List[Dict[str, Any]],
        cell_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Calculates microclimate impact for a collection of planted trees.
        """
        cell_area_sqm = 10000.0  # 100m x 100m cell

        total_trees = 0
        total_canopy_sqm = 0.0
        total_co2_kg = 0.0
        total_stormwater_liters = 0.0
        weighted_cooling_sum = 0.0

        breakdown = []

        for item in plantings:
            sid = item["species_id"]
            count = int(item["count"])
            sp = spatial_service.species_by_id.get(sid)

            if not sp:
                # Fallback defaults if species ID is unknown
                canopy_spread = 8.0
                canopy_cat = "Medium"
                cooling_val = "High"
                common_name = "Urban Tree"
                sci_name = "Tree spp."
            else:
                canopy_spread = sp["canopy_spread_m"]
                canopy_cat = sp["canopy_category"]
                cooling_val = sp["cooling_value"]
                common_name = sp["common_name"]
                sci_name = sp["scientific_name"]

            # Canopy Area = pi * r^2
            radius = canopy_spread / 2.0
            single_canopy_sqm = math.pi * (radius ** 2)
            species_total_canopy = round(single_canopy_sqm * count, 2)

            # CO2 Sequestration
            rate_co2 = self.co2_rates.get(canopy_cat, 20.0)
            species_total_co2 = round(rate_co2 * count, 2)

            # Stormwater Interception (Liters = Area_m2 * Rain_m * Interception_fraction * 1000)
            species_total_water = round(species_total_canopy * self.bhopal_annual_rain_m * self.canopy_interception_coeff * 1000.0, 1)

            # Cooling weight
            mult = self.cooling_multipliers.get(cooling_val, 1.0)
            weighted_cooling_sum += (species_total_canopy * mult)

            total_trees += count
            total_canopy_sqm += species_total_canopy
            total_co2_kg += species_total_co2
            total_stormwater_liters += species_total_water

            breakdown.append({
                "species_id": sid,
                "common_name": common_name,
                "scientific_name": sci_name,
                "count": count,
                "canopy_area_added_sqm": species_total_canopy,
                "co2_sequestration_kg_per_year": species_total_co2,
                "stormwater_intercepted_liters_per_year": species_total_water
            })

        # Canopy cover percentage gain in cell
        canopy_gain_pct = round((total_canopy_sqm / cell_area_sqm) * 100.0, 2)

        # Temperature Drop Formula:
        # Based on Akbari et al. & i-Tree microclimate models:
        # ~0.8 to 1.3 °C drop per 10% canopy gain in 100m cell, capped at 4.5 °C.
        effective_canopy_ratio = weighted_cooling_sum / cell_area_sqm if cell_area_sqm > 0 else 0
        raw_temp_drop = effective_canopy_ratio * 11.5
        temp_drop = round(min(4.5, raw_temp_drop), 2)

        return {
            "cell_id": cell_id,
            "total_trees": total_trees,
            "total_canopy_area_sqm": round(total_canopy_sqm, 2),
            "canopy_cover_percentage_gain": canopy_gain_pct,
            "predicted_temperature_drop_celsius": temp_drop,
            "annual_co2_sequestration_kg": round(total_co2_kg, 2),
            "annual_co2_sequestration_metric_tons": round(total_co2_kg / 1000.0, 3),
            "annual_stormwater_intercepted_liters": round(total_stormwater_liters, 1),
            "breakdown": breakdown
        }

impact_service = ImpactService()
