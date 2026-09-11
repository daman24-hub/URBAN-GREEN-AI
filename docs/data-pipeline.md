# Data Pipeline & Collection Methodology: Bhopal Urban Heat Study

**Pilot City**: Bhopal, Madhya Pradesh, India  
**Study Area Bounding Box**: 
- Latitude: $23.2300^\circ\text{ N}$ to $23.2700^\circ\text{ N}$
- Longitude: $77.3900^\circ\text{ E}$ to $77.4300^\circ\text{ E}$
- Spatial Extent: $4.0\text{ km} \times 4.0\text{ km}$ ($16.0\text{ km}^2$)
- Grid Resolution: $100\text{ m} \times 100\text{ m}$ ($40 \times 40 = 1,600$ grid cells)

---

## 1. Overview & Architecture

The Week 2 objective is to assemble a single unified, grid-based spatial dataset for the pilot city of Bhopal. By harmonizing satellite earth observation data with open urban infrastructure and meteorological APIs into consistent 100m × 100m cells, we establish the analytical foundation for microclimate heat vulnerability modeling.

```
+---------------------------+     +-------------------------------+
|  Landsat 8/9 TIRS Band 10 |     | Sentinel-2 MSI Bands 4 & 8    |
|  (Thermal Radiance)       |     | (Red & Near-Infrared)         |
+-------------+-------------+     +---------------+---------------+
              |                                   |
              v                                   v
+---------------------------+     +-------------------------------+
| Land Surface Temp (LST)   |     | NDVI (Vegetation Index)       |
+-------------+-------------+     +---------------+---------------+
              \                                   /
               \                                 /
                v                               v
        +-----------------------------------------------+
        |  100m x 100m Spatial Grid (Bhopal Urban Core) |
        +-----------------------+-----------------------+
                                ^
         /----------------------+-----------------------\
        |                                               |
+-------+--------------------+                 +--------+--------------------+
| OSMnx / OpenStreetMap      |                 | SoilGrids & Open-Meteo      |
| - Building Footprints (%)  |                 | - Soil Classification       |
| - Road Density (km/km2)    |                 | - Annual Precipitation (mm) |
| - Open Space Ratio (%)     |                 | - Summer Temp Baseline      |
+----------------------------+                 +-----------------------------+
```

---

## 2. Satellite Data Collection

### 2.1 Land Surface Temperature (LST) from Landsat 8/9 TIRS
- **Sensor**: Thermal Infrared Sensor (TIRS) Band 10 ($10.60\text{ }\mu\text{m} - 11.19\text{ }\mu\text{m}$).
- **Acquisition Window**: Peak pre-monsoon dry summer (April–May) during maximum solar insolation at 10:45 AM local solar time.
- **Processing Chain**:
  1. **Top of Atmosphere (TOA) Spectral Radiance ($L_\lambda$)**:
     $$L_\lambda = M_L \times Q_{cal} + A_L$$
     where $M_L$ is the radiance multiplicative scaling factor ($0.0003342$), $A_L$ is the additive rescaling factor ($0.1$), and $Q_{cal}$ is the quantized calibrated pixel value (DN).
  2. **Brightness Temperature ($T_B$)**:
     $$T_B = \frac{K_2}{\ln\left(\frac{K_1}{L_\lambda} + 1\right)}$$
     where $K_1 = 774.8853\text{ W}/(\text{m}^2\cdot\text{sr}\cdot\mu\text{m})$ and $K_2 = 1321.0789\text{ K}$.
  3. **Land Surface Emissivity ($\varepsilon$)**:
     Computed using the NDVI Thresholds Method (Sobrino et al.):
     $$P_v = \left(\frac{\text{NDVI} - \text{NDVI}_{min}}{\text{NDVI}_{max} - \text{NDVI}_{min}}\right)^2$$
     $$\varepsilon = \varepsilon_v P_v + \varepsilon_s (1 - P_v) + C$$
     where $\varepsilon_v \approx 0.985$ (vegetation), $\varepsilon_s \approx 0.965$ (bare soil), and $C$ represents cavity effect/surface roughness.
  4. **Final Land Surface Temperature ($LST$) in Celsius**:
     $$LST = \frac{T_B}{1 + \left(\frac{\lambda \times T_B}{\rho}\right) \ln(\varepsilon)} - 273.15$$
     where $\lambda = 10.895\text{ }\mu\text{m}$ and $\rho = \frac{h \cdot c}{\sigma} = 1.438 \times 10^{-2}\text{ m}\cdot\text{K}$.

### 2.2 Normalized Difference Vegetation Index (NDVI) from Sentinel-2 MSI
- **Bands**: Band 4 (Red, $\lambda = 665\text{ nm}$) and Band 8 (Near-Infrared, $\lambda = 842\text{ nm}$) at $10\text{ m}$ native resolution.
- **Formula**:
  $$\text{NDVI} = \frac{\text{NIR} - \text{Red}}{\text{NIR} + \text{Red}}$$
- **Values for Bhopal**:
  - Dense tree cover (Bhojtal lakefront buffers, Arera Colony parks): $+0.40$ to $+0.65$.
  - Mixed urban/residential (TT Nagar): $+0.18$ to $+0.35$.
  - Dense commercial/built asphalt (Old Bhopal, MP Nagar): $-0.02$ to $+0.12$.

---

## 3. Supporting Geospatial & Urban Infrastructure

### 3.1 OpenStreetMap via OSMnx
- **Building Footprints**: Polygons queried with `tags={'building': True}`.
  - **Building Density ($\%$)**: Sum of building polygon intersection area divided by cell area ($10,000\text{ m}^2$).
  - Dense zones like Old Bhopal (Chowk/Shahjahanabad) and MP Nagar Zone 1 & 2 exhibit $75\% - 89\%$ building coverage.
- **Road Network**: Queried with `network_type='all'`.
  - **Road Density ($\text{km}/\text{km}^2$)**: Total length of intersecting road centerlines scaled per square kilometer.
- **Open Space Percentage ($\%$)**:
  - Unsealed surface area calculated as residual open ground available for urban forestry interventions:
    $$\text{Open Space } \% = \max(5.0\%, 100\% - (\text{Building Density } \% + \text{Paved Impervious } \%))$$

### 3.2 Soil Classification (ISRIC SoilGrids)
- **Primary Bhopal Soil Type**: **Deep Black Clay (Vertisols / Black Cotton Soil)**.
  - Characterized by high montmorillonite clay content ($>45\%$), deep profile, high moisture holding capacity during monsoons, and shrink-swell shrinkage cracks during summer heatwaves.
- **Lakeside & Drainage Zones**: **Alluvial soils** along Bhojtal and Lower Lake shores.
- **Residential & Undulating Uplands**: **Clay Loam** in TT Nagar and Arera Colony.

### 3.3 Climate & Weather Normals (Open-Meteo API)
- **Annual Rainfall**: $1,095\text{ mm}$ (concentrated June–September during the South-West monsoon).
- **Summer Peak Baseline**: $42.5^\circ\text{C}$ daytime air temperature in May/June.

---

## 4. Dataset Schema & Field Dictionary

Both `data/bhopal_grid_100m_merged.geojson` and `data/bhopal_grid_100m_merged.csv` adhere to this schema:

| Column Name | Data Type | Units | Description |
|---|---|---|---|
| `cell_id` | String | - | Unique cell identifier (`BPL_CELL_0001` to `1600`) |
| `grid_row` | Integer | - | Row index (0 to 39, South to North) |
| `grid_col` | Integer | - | Column index (0 to 39, West to East) |
| `latitude` | Float | Deg N | WGS84 Centroid Latitude |
| `longitude` | Float | Deg E | WGS84 Centroid Longitude |
| `zone_name` | String | - | Representative Bhopal locality name |
| `lst_celsius` | Float | °C | Estimated Land Surface Temperature |
| `ndvi` | Float | [-1, 1] | Normalized Difference Vegetation Index |
| `building_density_pct` | Float | % | Built footprint ground coverage |
| `open_space_pct` | Float | % | Available unsealed ground space |
| `road_density_km_per_sqkm` | Float | km/km² | Road network density |
| `soil_type` | String | - | Soil classification (Vertisol, Clay Loam, Alluvial) |
| `annual_rainfall_mm` | Float | mm | Historical annual precipitation |
| `summer_max_temp_celsius` | Float | °C | Regional baseline peak air temperature |

---

## 5. Execution & Reproducibility

To regenerate the dataset from scratch:
```bash
python3 src/generate_week2_dataset.py
```
This produces:
- `data/bhopal_grid_100m_merged.csv` (1,600 rows)
- `data/bhopal_grid_100m_merged.geojson` (1,600 polygon features)
