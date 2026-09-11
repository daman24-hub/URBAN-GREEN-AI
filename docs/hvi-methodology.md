# Heat Vulnerability Index (HVI) Methodology & Species-Matching Engine

**Pilot City**: Bhopal, Madhya Pradesh, India  
**Project**: Urban Green AI — Spatial Heat Mitigation & Species Recommendation

---

## 1. Executive Summary

Rapid urbanization in Bhopal has exacerbated the Urban Heat Island (UHI) phenomenon. During pre-monsoon summer months (April–June), localized Land Surface Temperatures ($LST$) in dense asphalt and concrete centers such as Maharana Pratap (MP) Nagar and Old Bhopal frequently surpass $46^\circ\text{C}$—over $12^\circ\text{C}$ hotter than the vegetated Bhojtal (Upper Lake) riparian corridor.

This document formalizes:
1. **Heat Vulnerability Index (HVI)**: A multi-criteria spatial index computed over a $100\text{m} \times 100\text{m}$ grid to isolate and rank microclimate heat hotspots.
2. **AI Species Matching Engine**: A deterministic, rule-based decision algorithm that pairs each hotspot cell with optimal urban tree species based on thermal mitigation needs, edaphic compatibility with Bhopal's Vertisols (Black Cotton Soil), root safety, and drought resilience.

---

## 2. Heat Vulnerability Index (HVI) Formulation

The Heat Vulnerability Index integrates four satellite and spatial indicators into a standardized composite score ranging from $0.0$ (minimal risk) to $1.0$ (extreme vulnerability).

### 2.1 Component Indicators & Normalization

All raw indicators are transformed into normalized vulnerability components $[0, 1]$ via min-max scaling:

1. **Thermal Exposure ($LST_{norm}$)**:
   $$LST_{norm} = \frac{LST - LST_{min}}{LST_{max} - LST_{min}}$$
   - *Physical Rationale*: Direct thermal radiative forcing experienced by citizens and ground surfaces.

2. **Vegetation Deficit ($NDVI_{deficit}$)**:
   $$NDVI_{deficit} = 1.0 - \left(\frac{\text{NDVI} - \text{NDVI}_{min}}{\text{NDVI}_{max} - \text{NDVI}_{min}}\right)$$
   - *Physical Rationale*: Lack of photosynthetic biomass and canopy transpiration reduces natural evaporative cooling.

3. **Built-Up Density ($Built_{norm}$)**:
   $$Built_{norm} = \frac{\text{Building Density } \% - Built_{min}}{Built_{max} - Built_{min}}$$
   - *Physical Rationale*: Concrete, masonry, and rooftop materials possess high thermal mass, storing daytime solar heat and radiating it as nighttime sensible heat.

4. **Permeable Ground Deficit ($OpenSpace_{deficit}$)**:
   $$OpenSpace_{deficit} = 1.0 - \left(\frac{\text{Open Space } \% - Open_{min}}{Open_{max} - Open_{min}}\right)$$
   - *Physical Rationale*: Lack of unsealed soil limits stormwater infiltration and leaves minimal planting footprint for urban forestry interventions.

---

### 2.2 Composite Weighting Equation

Based on multi-criteria spatial analysis and urban microclimate literature, weights are assigned as:

$$\text{HVI} = 0.35 \times LST_{norm} + 0.25 \times NDVI_{deficit} + 0.25 \times Built_{norm} + 0.15 \times OpenSpace_{deficit}$$

$$\sum_{i} w_i = 0.35 + 0.25 + 0.25 + 0.15 = 1.0$$

### 2.3 Vulnerability Categorization

| HVI Score Range | Classification | Microclimate Description | Typical Bhopal Locality |
|---|---|---|---|
| **$\ge 0.75$** | **Extreme Hotspot** | Acute thermal stress, $LST > 45^\circ\text{C}$, $<10\%$ open space, sparse vegetation | MP Nagar Zones 1 & 2, Old Bhopal Chowk |
| **$0.55 - 0.749$** | **High Vulnerability** | High heat retention, $LST \approx 40-44^\circ\text{C}$, medium-high building density | TT Nagar, New Market core |
| **$0.35 - 0.549$** | **Moderate Vulnerability** | Balanced residential microclimate with tree cover | Arera Colony, Shahpura |
| **$< 0.35$** | **Low Vulnerability / Heat Sink** | Riparian buffer, high moisture, $LST < 35^\circ\text{C}$, dense vegetation cover | Bhojtal / Lower Lake Shoreline |

---

## 3. Top Hotspot Findings in Bhopal

Applying this formula across the $1,600$ grid cells in Bhopal produces the following ranked hotspots (top sample extracted in `outputs/bhopal_hotspots_ranked.csv`):

| Rank | Cell ID | Locality | LST (°C) | NDVI | Building Density | Open Space | HVI Score |
|---|---|---|---|---|---|---|---|
| **1** | `BPL_CELL_0308` | MP Nagar Commercial Zone | 48.5°C | -0.011 | 81.3% | 5.0% | **0.9617** |
| **2** | `BPL_CELL_0307` | MP Nagar Commercial Zone | 47.4°C | +0.062 | 88.8% | 5.0% | **0.9436** |
| **3** | `BPL_CELL_0150` | MP Nagar Commercial Zone | 47.9°C | +0.034 | 83.7% | 5.0% | **0.9435** |
| **4** | `BPL_CELL_0470` | MP Nagar Commercial Zone | 47.0°C | +0.054 | 89.0% | 5.0% | **0.9418** |
| **5** | `BPL_CELL_0225` | MP Nagar Commercial Zone | 46.6°C | +0.035 | 89.0% | 5.0% | **0.9415** |

**Key Diagnostic**: MP Nagar acts as an acute urban heat island due to unbroken asphalt parking lots, multistory commercial concrete blocks, high traffic volume, and virtually non-existent green medians.

---

## 4. AI Rule-Based Species Matching Engine

Rather than applying a generic planting list, the recommendation engine (`src/species_matcher.py`) evaluates each candidate species from our 26-species botanical database against the specific microclimate constraints of each grid cell.

### 4.1 Decision Rules & Multi-Criteria Matrix

```
                      +-----------------------------+
                      | Grid Cell Attributes:       |
                      | HVI, LST, Built %, Open %,  |
                      | Soil Type, Zone             |
                      +--------------+--------------+
                                     |
                                     v
                 +---------------------------------------+
                 | For each species in Species Database: |
                 +---------------------------------------+
                                     |
         +---------------------------+---------------------------+
         |                           |                           |
         v                           v                           v
+------------------+       +-------------------+       +--------------------+
| Rule 1: Cooling  |       | Rule 2: Physical  |       | Rule 3: Soil &     |
| Demand           |       | Constraints &     |       | Drought Match      |
| Match            |       | Root Safety       |       |                    |
| - High HVI needs |       | - Dense built =   |       | - Vertisols match  |
|   Very High/High |       |   penalize surface|       |   Black Clay trees |
|   cooling trees  |       |   roots; favor    |       | - Drought hardiness|
|                  |       |   Deep Taproots   |       |   for summer peak  |
+--------+---------+       +---------+---------+       +---------+----------+
         \                           |                           /
          \                          |                          /
           \                         v                         /
            +-------------------------------------------------+
            | Cumulative Compatibility Score (0 - 100)        |
            | + Explanatory Botanical Justification           |
            +------------------------+------------------------+
                                     |
                                     v
            +-------------------------------------------------+
            | Top 3 Ranked Recommended Species for Hotspot    |
            +-------------------------------------------------+
```

### 4.2 Detailed Rule Mechanics:

1. **Thermal Mitigation Rule**:
   - For cells with $\text{HVI} \ge 0.75$, species with `Very High` cooling capacity earn $+35$ points; `High` earns $+25$ points.

2. **Infrastructure Protection & Root Architecture Rule**:
   - In dense cells ($\text{Building Density} \ge 70\%$ or $\text{Open Space} \le 15\%$):
     - Trees with `Spreading Surface`, `Aerial`, or `Buttress` roots (e.g., *Delonix regia / Gulmohar*, *Bombax ceiba / Semal*, *Ficus benghalensis / Banyan*) are **penalized by $-40$ points** to prevent pavement cracking, road upheaval, and foundation compromise.
     - Species with `Deep Taproot` (e.g., *Millettia pinnata / Karanj*, *Azadirachta indica / Neem*, *Dalbergia sissoo / Sheesham*) receive **$+25$ bonus points**.
     - Compact/Medium canopies receive $+15$ to $+20$ points to avoid powerline and building facade conflicts.

3. **Edaphic / Soil Adaptation Rule**:
   - For cells located on **Deep Black Clay (Vertisols)**:
     - Species adapted to shrink-swell clay (e.g., *Karanj*, *Neem*, *Palash*, *Tamarind*, *Kachnar*) receive $+20$ points.
   - For cells on **Alluvial** soils near Bhojtal Lake:
     - Moisture-tolerant species (e.g., *Terminalia arjuna / Arjun*, *Syzygium cumini / Jamun*, *Neolamarckia cadamba / Kadam*) receive $+20$ points.

4. **Seasonal Drought Resilience Rule**:
   - Species with `Very High` or `High` drought tolerance receive $+15$ points to survive Bhopal's scorching May heatwaves without continuous municipal irrigation.

---

## 5. Sample Hotspot Recommendations

Tested against the top 10 Bhopal hotspots (full log in `outputs/hotspot_species_recommendations.csv`):

```
Cell ID: BPL_CELL_0308 | Zone: MP Nagar Commercial Zone
LST: 48.5°C | HVI: 0.9617 | Built: 81.3% | Open Space: 5.0%

Recommended Urban Trees:
  1. Karanj (Millettia pinnata / करंज) [Match Score: 100.0/100]
     - High cooling capacity helps buffer high surface temperature
     - Deep taproot is safe near paved sidewalks and building foundations
     - Moderate crown size manageable with urban pruning
     - Highly tolerant of shrink-swell characteristics of Bhopal Vertisols
     - High dust and vehicular particulate absorption capacity

  2. Sheesham (Dalbergia sissoo / शीशम) [Match Score: 95.0/100]
     - High cooling capacity with deep taproot
     - Strong tolerance to roadside particulate matter and vehicular emissions

  3. Neem (Azadirachta indica / नीम) [Match Score: 90.0/100]
     - Very high cooling capacity critical for severe microclimate heat island
     - Deep non-invasive taproot; highly resilient to black cotton soil shrink-swell
```

---

## 6. How to Run & Verify

1. **Calculate HVI and generate hotspot rankings**:
   ```bash
   python3 src/calculate_hvi.py
   ```
2. **Execute Species Matching Engine**:
   ```bash
   python3 src/species_matcher.py
   ```
3. **Generate Interactive Visual Map**:
   ```bash
   python3 src/generate_map.py
   ```
   Open `maps/bhopal_hvi_heatmap.html` in any browser to inspect the complete 1,600-cell choropleth grid with popups.
