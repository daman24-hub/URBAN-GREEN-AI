"""
FastAPI Microservice for Urban Green AI
City: Bhopal, Madhya Pradesh, India
"""

from typing import Optional
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.models import (
    HotspotsResponse,
    RecommendResponse,
    ImpactEstimateRequest,
    ImpactEstimateResponse,
    MasterPlanResponse,
    GridCellResponse,
    SpeciesRecommendationItem
)
from app.services.spatial_service import spatial_service
from app.services.impact_service import impact_service
from app.services.plan_service import plan_service
from src.species_matcher import species_filter

app = FastAPI(
    title="Urban Green AI — API",
    description="Spatial heat vulnerability analytics, AI species matching, and environmental impact estimators for urban heat mitigation.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS for frontend applications & Postman
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", tags=["Health"])
def health_check():
    return {
        "status": "online",
        "service": "Urban Green AI Microservice",
        "pilot_city": "Bhopal, Madhya Pradesh, India",
        "version": "1.0.0",
        "endpoints": {
            "hotspots": "/api/hotspots",
            "recommend": "/api/recommend",
            "impact_estimate": "/api/impact-estimate",
            "master_plan": "/api/plan",
            "swagger_docs": "/docs"
        }
    }

# ----------------------------------------------------------------------
# 1. Mon Task: GET /api/hotspots?city=X
# ----------------------------------------------------------------------
@app.get(
    "/api/hotspots",
    response_model=HotspotsResponse,
    tags=["Hotspots"],
    summary="Get ranked Heat Vulnerability Index (HVI) grid cells"
)
def get_hotspots(
    city: str = Query("bhopal", description="City name (e.g., bhopal)"),
    limit: int = Query(20, ge=1, le=100, description="Max cells to return"),
    min_hvi: Optional[float] = Query(None, ge=0.0, le=1.0, description="Minimum HVI threshold (e.g., 0.75 for Extreme Hotspots)"),
    category: Optional[str] = Query(None, description="Filter by category (e.g., 'Extreme Hotspot')")
):
    cells = spatial_service.get_hotspots(
        city=city,
        limit=limit,
        min_hvi=min_hvi,
        category=category
    )
    return {
        "city": city.title(),
        "total_returned": len(cells),
        "hotspots": cells
    }

# ----------------------------------------------------------------------
# 2. Tue Task: GET /api/recommend?lat=&lng=
# ----------------------------------------------------------------------
@app.get(
    "/api/recommend",
    response_model=RecommendResponse,
    tags=["Species Recommendation"],
    summary="Get top recommended tree species for specific coordinates"
)
def recommend_species(
    lat: float = Query(..., description="WGS84 Latitude (e.g., 23.2355 for MP Nagar)"),
    lng: float = Query(..., description="WGS84 Longitude (e.g., 77.4215)"),
    top_n: int = Query(3, ge=1, le=10, description="Number of species recommendations")
):
    cell, dist_m = spatial_service.get_nearest_cell(lat, lng)
    if not cell:
        raise HTTPException(status_code=404, detail="No matching grid cell found in study area.")

    recs = species_filter(cell, spatial_service.species_list, top_n=top_n)

    return {
        "queried_coordinates": {"lat": lat, "lng": lng},
        "matched_cell": cell,
        "distance_meters": dist_m,
        "recommended_species": recs
    }

# ----------------------------------------------------------------------
# 3. Wed & Thu Task: POST /api/impact-estimate
# ----------------------------------------------------------------------
@app.post(
    "/api/impact-estimate",
    response_model=ImpactEstimateResponse,
    tags=["Impact Estimation"],
    summary="Calculate predicted temperature drop, CO2 sequestration, and flood mitigation"
)
def estimate_impact(payload: ImpactEstimateRequest):
    plantings_dict = [{"species_id": p.species_id, "count": p.count} for p in payload.plantings]
    result = impact_service.estimate_impact(plantings=plantings_dict, cell_id=payload.cell_id)
    return result

# ----------------------------------------------------------------------
# 4. Fri Task: Master Endpoint GET /api/plan?city=X
# ----------------------------------------------------------------------
@app.get(
    "/api/plan",
    response_model=MasterPlanResponse,
    tags=["Master Plan"],
    summary="Master endpoint: Chaining hotspots -> species -> impact into a ranked planting plan"
)
def get_master_plan(
    city: str = Query("bhopal", description="Target city"),
    top_hotspots: int = Query(10, ge=1, le=30, description="Number of priority hotspots to address"),
    target_temp_drop: float = Query(2.0, ge=0.5, le=4.5, description="Target localized cooling in Celsius")
):
    plan_data = plan_service.generate_master_plan(
        city=city,
        top_hotspots=top_hotspots,
        target_temp_drop=target_temp_drop
    )
    # Also export to outputs/ for offline use and GIS integration
    plan_service.export_plan_files(plan_data)
    return plan_data

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
