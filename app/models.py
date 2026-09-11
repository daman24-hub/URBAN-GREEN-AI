"""
Pydantic Schemas for Urban Green AI API
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class GridCellResponse(BaseModel):
    cell_id: str
    latitude: float
    longitude: float
    zone_name: str
    lst_celsius: float
    ndvi: float
    building_density_pct: float
    open_space_pct: float
    road_density_km_per_sqkm: float
    soil_type: str
    annual_rainfall_mm: float
    hvi_score: float
    hvi_category: str
    hvi_rank: int

class HotspotsResponse(BaseModel):
    city: str
    total_returned: int
    hotspots: List[GridCellResponse]

class SpeciesRecommendationItem(BaseModel):
    species_id: str
    common_name: str
    scientific_name: str
    hindi_name: str
    canopy_spread_m: float
    cooling_value: str
    root_type: str
    match_score: float
    justification: str

class RecommendResponse(BaseModel):
    queried_coordinates: Dict[str, float]
    matched_cell: GridCellResponse
    distance_meters: float
    recommended_species: List[SpeciesRecommendationItem]

class PlantingItem(BaseModel):
    species_id: str = Field(..., description="ID of species from catalog e.g. SPECIES_05")
    count: int = Field(..., ge=1, description="Number of trees to plant")

class ImpactEstimateRequest(BaseModel):
    cell_id: Optional[str] = Field(None, description="Target 100m grid cell ID e.g. BPL_CELL_0308")
    plantings: List[PlantingItem] = Field(..., min_length=1, description="List of species and tree counts")

class SpeciesImpactBreakdown(BaseModel):
    species_id: str
    common_name: str
    scientific_name: str
    count: int
    canopy_area_added_sqm: float
    co2_sequestration_kg_per_year: float
    stormwater_intercepted_liters_per_year: float

class ImpactEstimateResponse(BaseModel):
    cell_id: Optional[str]
    total_trees: int
    total_canopy_area_sqm: float
    canopy_cover_percentage_gain: float
    predicted_temperature_drop_celsius: float
    annual_co2_sequestration_kg: float
    annual_co2_sequestration_metric_tons: float
    annual_stormwater_intercepted_liters: float
    breakdown: List[SpeciesImpactBreakdown]

class HotspotPlanItem(BaseModel):
    hvi_rank: int
    cell_id: str
    zone_name: str
    latitude: float
    longitude: float
    current_lst_celsius: float
    current_hvi_score: float
    open_space_pct: float
    recommended_trees_count: int
    predicted_temperature_drop_celsius: float
    new_projected_lst_celsius: float
    annual_co2_kg: float
    annual_stormwater_liters: float
    top_species_selected: List[SpeciesRecommendationItem]

class MasterPlanSummary(BaseModel):
    city: str
    total_hotspot_cells_addressed: int
    total_trees_to_plant: int
    total_canopy_area_added_sqm: float
    average_temperature_reduction_celsius: float
    total_annual_co2_sequestration_metric_tons: float
    total_annual_stormwater_absorbed_megaliters: float

class MasterPlanResponse(BaseModel):
    summary: MasterPlanSummary
    plan_details: List[HotspotPlanItem]
