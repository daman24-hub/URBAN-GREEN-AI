# Urban Green AI — API Guide & Postman Collection Reference

**Base URL**: `http://127.0.0.1:8000`  
**Interactive Swagger UI**: `http://127.0.0.1:8000/docs`  
**ReDoc Documentation**: `http://127.0.0.1:8000/redoc`

---

## 1. Quick Start

### Start the Microservice:
```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

---

## 2. API Endpoints Reference

### 2.1 Health Check
**Endpoint**: `GET /`

```bash
curl -X GET "http://127.0.0.1:8000/"
```

**Response**:
```json
{
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
```

---

### 2.2 Ranked Hotspots
**Endpoint**: `GET /api/hotspots`  
**Description**: Returns ranked Heat Vulnerability Index (HVI) grid cells for the target city.

#### Query Parameters:
| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `city` | string | No | `"bhopal"` | Target pilot city |
| `limit` | int | No | `20` | Max cells to return (1-100) |
| `min_hvi` | float | No | `null` | Threshold filter (e.g. `0.75` for Extreme Hotspots) |
| `category` | string | No | `null` | String filter (e.g. `"Extreme Hotspot"`) |

#### cURL Example:
```bash
curl -X GET "http://127.0.0.1:8000/api/hotspots?city=bhopal&limit=5&min_hvi=0.90"
```

#### Sample Response:
```json
{
  "city": "Bhopal",
  "total_returned": 5,
  "hotspots": [
    {
      "cell_id": "BPL_CELL_0308",
      "latitude": 23.2375,
      "longitude": 77.4175,
      "zone_name": "MP Nagar Commercial Zone",
      "lst_celsius": 48.5,
      "ndvi": -0.011,
      "building_density_pct": 81.3,
      "open_space_pct": 5.0,
      "road_density_km_per_sqkm": 17.8,
      "soil_type": "Deep Black Clay (Vertisol)",
      "annual_rainfall_mm": 1098.2,
      "hvi_score": 0.9617,
      "hvi_category": "Extreme Hotspot",
      "hvi_rank": 1
    }
  ]
}
```

---

### 2.3 Point Species Recommendation
**Endpoint**: `GET /api/recommend`  
**Description**: Takes geographical coordinates `(lat, lng)`, executes nearest-neighbor cell lookup, and runs the rule-based AI species matching engine.

#### Query Parameters:
| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `lat` | float | **Yes** | - | WGS84 Latitude (e.g. `23.2355`) |
| `lng` | float | **Yes** | - | WGS84 Longitude (e.g. `77.4215`) |
| `top_n` | int | No | `3` | Number of top tree species to return |

#### cURL Example:
```bash
curl -X GET "http://127.0.0.1:8000/api/recommend?lat=23.2355&lng=77.4215&top_n=3"
```

#### Sample Response:
```json
{
  "queried_coordinates": {
    "lat": 23.2355,
    "lng": 77.4215
  },
  "matched_cell": {
    "cell_id": "BPL_CELL_0225",
    "zone_name": "MP Nagar Commercial Zone",
    "hvi_score": 0.9415,
    "hvi_category": "Extreme Hotspot",
    "lst_celsius": 46.64,
    "open_space_pct": 5.0,
    "soil_type": "Deep Black Clay (Vertisol)"
  },
  "distance_meters": 32.5,
  "recommended_species": [
    {
      "species_id": "SPECIES_05",
      "common_name": "Karanj",
      "scientific_name": "Millettia pinnata",
      "hindi_name": "करंज",
      "canopy_spread_m": 9.0,
      "cooling_value": "High",
      "root_type": "Deep Taproot",
      "match_score": 100.0,
      "justification": "High cooling capacity | Deep taproot is safe near paved sidewalks and building foundations | Highly tolerant of shrink-swell characteristics of Bhopal Vertisols"
    },
    {
      "species_id": "SPECIES_12",
      "common_name": "North Indian Rosewood / Sheesham",
      "scientific_name": "Dalbergia sissoo",
      "hindi_name": "शीशम",
      "canopy_spread_m": 10.0,
      "cooling_value": "High",
      "root_type": "Deep Taproot",
      "match_score": 95.0,
      "justification": "Deep taproot | High vehicular particulate absorption capacity"
    },
    {
      "species_id": "SPECIES_01",
      "common_name": "Neem",
      "scientific_name": "Azadirachta indica",
      "hindi_name": "नीम",
      "canopy_spread_m": 12.0,
      "cooling_value": "Very High",
      "root_type": "Deep Taproot",
      "match_score": 90.0,
      "justification": "Very high cooling capacity critical for severe microclimate heat island | Excellent drought resilience"
    }
  ]
}
```

---

### 2.4 Environmental Impact Estimator
**Endpoint**: `POST /api/impact-estimate`  
**Description**: Combines species and planting counts to predict temperature reduction ($\Delta T$), annual $\text{CO}_2$ sequestration, and stormwater runoff absorbed based on i-Tree Eco empirical benchmarks.

#### Request Body (`application/json`):
```json
{
  "cell_id": "BPL_CELL_0308",
  "plantings": [
    {
      "species_id": "SPECIES_05",
      "count": 15
    },
    {
      "species_id": "SPECIES_01",
      "count": 10
    }
  ]
}
```

#### cURL Example:
```bash
curl -X POST "http://127.0.0.1:8000/api/impact-estimate" \
     -H "Content-Type: application/json" \
     -d '{
       "cell_id": "BPL_CELL_0308",
       "plantings": [
         {"species_id": "SPECIES_05", "count": 15},
         {"species_id": "SPECIES_01", "count": 10}
       ]
     }'
```

#### Sample Response:
```json
{
  "cell_id": "BPL_CELL_0308",
  "total_trees": 25,
  "total_canopy_area_sqm": 2085.17,
  "canopy_cover_percentage_gain": 20.85,
  "predicted_temperature_drop_celsius": 2.89,
  "annual_co2_sequestration_kg": 650.0,
  "annual_co2_sequestration_metric_tons": 0.65,
  "annual_stormwater_intercepted_liters": 456652.2,
  "breakdown": [
    {
      "species_id": "SPECIES_05",
      "common_name": "Karanj",
      "scientific_name": "Millettia pinnata",
      "count": 15,
      "canopy_area_added_sqm": 954.26,
      "co2_sequestration_kg_per_year": 330.0,
      "stormwater_intercepted_liters_per_year": 208982.9
    },
    {
      "species_id": "SPECIES_01",
      "common_name": "Neem",
      "scientific_name": "Azadirachta indica",
      "count": 10,
      "canopy_area_added_sqm": 1130.97,
      "co2_sequestration_kg_per_year": 320.0,
      "stormwater_intercepted_liters_per_year": 247669.3
    }
  ]
}
```

---

### 2.5 Master Planting Plan (Week Deliverable)
**Endpoint**: `GET /api/plan`  
**Description**: Master pipeline chaining hotspots $\rightarrow$ species matching $\rightarrow$ environmental impact calculation into an actionable, ranked city planting schedule.

#### Query Parameters:
| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `city` | string | No | `"bhopal"` | Target city |
| `top_hotspots` | int | No | `10` | Top priority cells to mitigate (1-30) |
| `target_temp_drop` | float | No | `2.0` | Target cooling reduction (°C) |

#### cURL Example:
```bash
curl -X GET "http://127.0.0.1:8000/api/plan?city=bhopal&top_hotspots=10&target_temp_drop=2.0"
```

#### Sample Response:
```json
{
  "summary": {
    "city": "Bhopal",
    "total_hotspot_cells_addressed": 10,
    "total_trees_to_plant": 72,
    "total_canopy_area_added_sqm": 5372.15,
    "average_temperature_reduction_celsius": 0.62,
    "total_annual_co2_sequestration_metric_tons": 1.584,
    "total_annual_stormwater_absorbed_megaliters": 1.176
  },
  "plan_details": [
    {
      "hvi_rank": 1,
      "cell_id": "BPL_CELL_0308",
      "zone_name": "MP Nagar Commercial Zone",
      "latitude": 23.2375,
      "longitude": 77.4175,
      "current_lst_celsius": 48.5,
      "current_hvi_score": 0.9617,
      "open_space_pct": 5.0,
      "recommended_trees_count": 12,
      "predicted_temperature_drop_celsius": 1.04,
      "new_projected_lst_celsius": 47.46,
      "annual_co2_kg": 264.0,
      "annual_stormwater_liters": 180258.9,
      "top_species_selected": [
        {
          "species_id": "SPECIES_05",
          "common_name": "Karanj",
          "hindi_name": "करंज",
          "match_score": 100.0
        },
        {
          "species_id": "SPECIES_12",
          "common_name": "North Indian Rosewood / Sheesham",
          "hindi_name": "शीशम",
          "match_score": 95.0
        }
      ]
    }
  ]
}
```

*Triggering this endpoint automatically updates `outputs/bhopal_planting_plan.geojson` and `outputs/bhopal_planting_plan.csv`.*

---

## 3. Month 1 Retrospective (Weeks 1 – 4)

| Week | Phase | Delivered Assets | Key Outcomes |
|---|---|---|---|
| **Week 1** | Scope & Alignment | Workspace scaffolding (`data/`, `src/`, `maps/`, `outputs/`, `docs/`) | Bhopal chosen as pilot city |
| **Week 2** | Satellite & Spatial Data | `bhopal_grid_100m_merged.csv` & `.geojson`, `data-pipeline.md` | 1,600 100m cells combining LST, NDVI, OSMnx building/roads, SoilGrids, Open-Meteo |
| **Week 3** | HVI & Species Matcher | `calculate_hvi.py`, `species_database.json`, `bhopal_hvi_heatmap.html` | Top 30 heat hotspots ranked; 26 native species with multi-criteria rule matching |
| **Week 4** | API Microservice | FastAPI app (`app/main.py`), 4 callable endpoints, i-Tree impact estimator, master `/api/plan` endpoint, `tests/test_api.py` | Complete analytics exposed as an unblocked production microservice ready for web frontend |
