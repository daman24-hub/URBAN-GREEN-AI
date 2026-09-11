# Urban Green AI — Backend API Reference & Architecture Contract

**Express Backend URL**: `http://127.0.0.1:5001`  
**FastAPI AI Microservice URL**: `http://127.0.0.1:8000`  
**Database**: MongoDB (`mongodb://127.0.0.1:27017/urbangreen_ai`)

---

## 1. System Overview & Architecture

The Week 5 backend provides a persistent, production-style Express + MongoDB REST API wrapping the analytical AI microservice.

```
       [Client / Postman / Frontend]
                     |
         +-----------+-----------+
         | (Port 5001)           | (Port 8000)
         v                       v
[Express REST Gateway]     [FastAPI AI Engine]
  ├── Auth & Users (JWT)     ├── Heat Vulnerability Index
  ├── Cities & Species       ├── Species Matcher
  ├── Planting Records       └── Impact Estimates
  └── AI Bridge Sync ------------> (/api/plan)
         |
         v
[MongoDB Database]
  (7 Collections)
```

---

## 2. Authentication & Role-Based Access Control (RBAC)

All protected endpoints require an HTTP `Authorization` header:
```http
Authorization: Bearer <YOUR_JWT_TOKEN>
```

### Roles:
- **`govt`**: Municipal directors, city planning officials (Full access, approval rights, planting deletion).
- **`developer`**: Urban forestry specialists, GIS engineers (Can add species, submit planting records, trigger AI sync).
- **`utility`**: Water, power, and road infrastructure operators (Read-only access to hotspots and planting schedules to prevent root/cable conflicts).

### Default Test Accounts:
| Role | Email | Password | Department |
|---|---|---|---|
| `govt` | `govt@urbangreen.ai` | `Password123!` | Bhopal Municipal Corporation & Urban Forestry |
| `developer` | `developer@urbangreen.ai` | `Password123!` | Smart City Spatial Analytics Unit |
| `utility` | `utility@urbangreen.ai` | `Password123!` | MP Urban Infrastructure & Power Works |

---

## 3. Endpoints Specification

### 3.1 Authentication Routes (`/api/auth`)

#### 1. Register User
`POST /api/auth/register`
```json
{
  "name": "Jane Doe",
  "email": "jane@example.com",
  "password": "Password123!",
  "role": "developer",
  "department": "Urban Ecology"
}
```

#### 2. Login User
`POST /api/auth/login`
```json
{
  "email": "developer@urbangreen.ai",
  "password": "Password123!"
}
```
**Response**:
```json
{
  "success": true,
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "6aa2...",
    "name": "A. Verma (GIS Engineer)",
    "email": "developer@urbangreen.ai",
    "role": "developer"
  }
}
```

#### 3. Current User Profile
`GET /api/auth/me` *(Protected)*

---

### 3.2 City Routes (`/api/cities`)

- **`GET /api/cities`**: Returns all managed pilot cities.
- **`GET /api/cities/:id`**: Returns specific city details and bounding coordinates.
- **`POST /api/cities`** *(Protected: `govt`, `developer`)*: Add a new city.

---

### 3.3 Species Catalog Routes (`/api/species`)

- **`GET /api/species`**: Returns cataloged urban tree species with optional filters:
  - `?coolingValue=Very+High`
  - `?canopyCategory=Large`
  - `?rootType=Deep+Taproot`
  - `?search=Neem`
- **`GET /api/species/:id`**: Lookup by MongoDB ID or Species ID (e.g. `/api/species/SPECIES_01`).
- **`POST /api/species`** *(Protected: `govt`, `developer`)*: Add a new tree species.

---

### 3.4 Planting Record Routes (`/api/plantings`)

- **`GET /api/plantings`**: List all planting records (filter by `?status=planned` or `?cellId=BPL_CELL_0308`).
- **`POST /api/plantings`** *(Protected)*: Create a new planting intervention record:
```json
{
  "cellId": "BPL_CELL_0308",
  "speciesId": "SPECIES_05",
  "commonName": "Karanj",
  "scientificName": "Millettia pinnata",
  "treeCount": 15,
  "predictedTempDropCelsius": 1.2,
  "projectedCo2KgPerYear": 330.0,
  "status": "planned"
}
```
- **`PATCH /api/plantings/:id/status`** *(Protected)*: Update state (`planned` $\rightarrow$ `approved` $\rightarrow$ `planted` $\rightarrow$ `monitored`).
- **`DELETE /api/plantings/:id`** *(Protected: `govt` only)*: Delete planting record.

---

### 3.5 AI Microservice Bridge Routes (`/api/ai`)

#### 1. Live Synchronize Master Plan into MongoDB
`POST /api/ai/sync-plan?city=bhopal&topHotspots=10` *(Protected)*

**How it works**:
1. Express queries the FastAPI microservice (`GET http://127.0.0.1:8000/api/plan`).
2. Receives ranked hotspots, botanical recommendations, and environmental impact numbers.
3. Automatically upserts records into MongoDB `GridCell` and `PlantingRecord` collections.

**Sample Response**:
```json
{
  "success": true,
  "message": "Successfully synchronized 10 hotspots from AI Microservice into MongoDB.",
  "city": "Bhopal",
  "summary": {
    "total_hotspot_cells_addressed": 10,
    "total_trees_to_plant": 72,
    "average_temperature_reduction_celsius": 0.62,
    "total_annual_co2_sequestration_metric_tons": 1.584,
    "total_annual_stormwater_absorbed_megaliters": 1.176
  },
  "syncedCellsCount": 10,
  "syncedPlantingRecordsCount": 10,
  "sampleCellIds": ["BPL_CELL_0308", "BPL_CELL_0307", "BPL_CELL_0150"]
}
```

#### 2. Live Hotspots Proxy
`GET /api/ai/live-hotspots?city=bhopal&limit=5`

---

## 4. Database Schema Structure (7 Collections)

| Collection | Model File | Purpose | Key Attributes |
|---|---|---|---|
| `users` | `models/User.js` | User identity & RBAC | `email`, `password`, `role` (`govt`/`developer`/`utility`), `department` |
| `cities` | `models/City.js` | City spatial metadata | `name`, `centerCoordinates`, `bounds`, `baselineClimate` |
| `gridcells` | `models/GridCell.js` | 100m grid spatial cache | `cellId`, `latitude`, `longitude`, `lstCelsius`, `hviScore`, `hviRank` |
| `species` | `models/Species.js` | Botanical tree catalog | `speciesId`, `commonName`, `coolingValue`, `rootType`, `soilPreference` |
| `plantingrecords` | `models/PlantingRecord.js` | Actionable planting ledger | `cellId`, `speciesId`, `treeCount`, `status`, `predictedTempDropCelsius` |
| `sensors` | `models/Sensor.js` | Simulated post-planting IoT | `sensorId`, `cellId`, `sensorType`, `batteryPct`, `lastReading` |
| `alerts` | `models/Alert.js` | Automated heat/drought alerts | `alertId`, `cellId`, `alertType`, `severity`, `message`, `resolved` |
