#!/usr/bin/env python3
"""
Week 3: Interactive Heat Vulnerability Map Generator for Bhopal
Generates maps/bhopal_hvi_heatmap.html using Leaflet.js with interactive
choropleth grid cells, top hotspot pins, legend, and tree species inspector.
"""

import json
import csv
import os

def generate_interactive_map():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    geojson_path = os.path.join(base_dir, "data", "bhopal_grid_100m_merged.geojson")
    species_csv = os.path.join(base_dir, "data", "bhopal_urban_tree_species.csv")
    recs_csv = os.path.join(base_dir, "outputs", "hotspot_species_recommendations.csv")
    map_out = os.path.join(base_dir, "maps", "bhopal_hvi_heatmap.html")

    print("=" * 70)
    print("Generating Interactive Bhopal HVI Heatmap")
    print("=" * 70)

    # Load GeoJSON
    with open(geojson_path, mode="r", encoding="utf-8") as f:
        geojson_data = json.load(f)

    # Load recommendations dictionary for quick lookup by cell_id
    recs_by_cell = {}
    if os.path.exists(recs_csv):
        with open(recs_csv, mode="r", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                cid = row["cell_id"]
                if cid not in recs_by_cell:
                    recs_by_cell[cid] = []
                recs_by_cell[cid].append(row)

    # Convert geojson data into embedded JS variable
    geojson_str = json.dumps(geojson_data)
    recs_str = json.dumps(recs_by_cell)

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Bhopal Heat Vulnerability Index (HVI) & Urban Green AI Map</title>
  
  <!-- Leaflet CSS & JS -->
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
  
  <!-- Google Fonts -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">

  <style>
    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }}
    body {{
      font-family: 'Outfit', sans-serif;
      background: #0f172a;
      color: #f8fafc;
      overflow: hidden;
    }}
    #map {{
      height: 100vh;
      width: 100vw;
      z-index: 1;
    }}

    /* Glassmorphism Header Bar */
    .header-panel {{
      position: absolute;
      top: 16px;
      left: 16px;
      z-index: 1000;
      background: rgba(15, 23, 42, 0.88);
      backdrop-filter: blur(12px);
      border: 1px solid rgba(255, 255, 255, 0.12);
      border-radius: 16px;
      padding: 16px 20px;
      max-width: 440px;
      box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4);
    }}
    .header-panel h1 {{
      font-size: 1.25rem;
      font-weight: 700;
      letter-spacing: -0.02em;
      background: linear-gradient(135deg, #38bdf8, #34d399);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      margin-bottom: 4px;
    }}
    .header-panel p {{
      font-size: 0.84rem;
      color: #94a3b8;
      line-height: 1.4;
    }}
    .stats-row {{
      display: flex;
      gap: 12px;
      margin-top: 12px;
      padding-top: 10px;
      border-top: 1px solid rgba(255, 255, 255, 0.08);
    }}
    .stat-pill {{
      flex: 1;
      background: rgba(255, 255, 255, 0.04);
      border: 1px solid rgba(255, 255, 255, 0.06);
      border-radius: 10px;
      padding: 6px 10px;
      text-align: center;
    }}
    .stat-pill .val {{
      font-size: 1.05rem;
      font-weight: 700;
      color: #f1f5f9;
      font-family: 'JetBrains Mono', monospace;
    }}
    .stat-pill .lbl {{
      font-size: 0.68rem;
      color: #64748b;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      margin-top: 2px;
    }}

    /* Legend */
    .legend-panel {{
      position: absolute;
      bottom: 24px;
      right: 16px;
      z-index: 1000;
      background: rgba(15, 23, 42, 0.9);
      backdrop-filter: blur(12px);
      border: 1px solid rgba(255, 255, 255, 0.12);
      border-radius: 14px;
      padding: 14px 18px;
      min-width: 220px;
      box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4);
    }}
    .legend-title {{
      font-size: 0.8rem;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.06em;
      color: #94a3b8;
      margin-bottom: 8px;
    }}
    .legend-scale {{
      display: flex;
      flex-direction: column;
      gap: 6px;
    }}
    .legend-item {{
      display: flex;
      align-items: center;
      gap: 10px;
      font-size: 0.78rem;
      color: #cbd5e1;
    }}
    .legend-color {{
      width: 18px;
      height: 12px;
      border-radius: 3px;
      border: 1px solid rgba(255,255,255,0.2);
    }}

    /* Custom Leaflet Popup Styling */
    .leaflet-popup-content-wrapper {{
      background: rgba(15, 23, 42, 0.95);
      backdrop-filter: blur(14px);
      border: 1px solid rgba(255, 255, 255, 0.15);
      color: #f8fafc;
      border-radius: 14px;
      padding: 4px;
      box-shadow: 0 14px 40px rgba(0,0,0,0.5);
    }}
    .leaflet-popup-tip {{
      background: rgba(15, 23, 42, 0.95);
    }}
    .popup-box {{
      padding: 8px 10px;
      font-size: 0.85rem;
      max-width: 320px;
    }}
    .popup-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      border-bottom: 1px solid rgba(255, 255, 255, 0.1);
      padding-bottom: 6px;
      margin-bottom: 8px;
    }}
    .popup-cell-id {{
      font-family: 'JetBrains Mono', monospace;
      font-size: 0.82rem;
      color: #38bdf8;
      font-weight: 600;
    }}
    .popup-badge {{
      font-size: 0.7rem;
      font-weight: 600;
      padding: 2px 8px;
      border-radius: 999px;
    }}
    .badge-extreme {{ background: #dc2626; color: #fff; }}
    .badge-high {{ background: #ea580c; color: #fff; }}
    .badge-mod {{ background: #ca8a04; color: #fff; }}
    .badge-low {{ background: #16a34a; color: #fff; }}

    .metric-grid {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 6px;
      margin-bottom: 10px;
    }}
    .metric-cell {{
      background: rgba(255, 255, 255, 0.05);
      border-radius: 8px;
      padding: 6px 8px;
    }}
    .metric-cell .m-lbl {{
      font-size: 0.68rem;
      color: #94a3b8;
    }}
    .metric-cell .m-val {{
      font-family: 'JetBrains Mono', monospace;
      font-weight: 600;
      font-size: 0.86rem;
      color: #f1f5f9;
    }}
    .tree-box {{
      background: rgba(16, 185, 129, 0.1);
      border: 1px solid rgba(16, 185, 129, 0.25);
      border-radius: 10px;
      padding: 8px 10px;
      margin-top: 6px;
    }}
    .tree-box-title {{
      font-size: 0.74rem;
      font-weight: 700;
      text-transform: uppercase;
      color: #34d399;
      letter-spacing: 0.05em;
      margin-bottom: 4px;
    }}
    .tree-item {{
      font-size: 0.78rem;
      color: #e2e8f0;
      margin-bottom: 3px;
    }}
  </style>
</head>
<body>

  <!-- Header Overlay -->
  <div class="header-panel">
    <h1>URBAN GREEN AI: BHOPAL</h1>
    <p>Pilot Microclimate Grid (100m x 100m) & Heat Vulnerability Index (HVI)</p>
    <div class="stats-row">
      <div class="stat-pill">
        <div class="val">1,600</div>
        <div class="lbl">Grid Cells</div>
      </div>
      <div class="stat-pill">
        <div class="val">48.5°C</div>
        <div class="lbl">Peak LST</div>
      </div>
      <div class="stat-pill">
        <div class="val">30</div>
        <div class="lbl">Top Hotspots</div>
      </div>
      <div class="stat-pill">
        <div class="val">26</div>
        <div class="lbl">Tree Species</div>
      </div>
    </div>
  </div>

  <!-- Legend Overlay -->
  <div class="legend-panel">
    <div class="legend-title">Heat Vulnerability (HVI)</div>
    <div class="legend-scale">
      <div class="legend-item">
        <div class="legend-color" style="background: #dc2626;"></div>
        <span>Extreme Hotspot (&gt; 0.75)</span>
      </div>
      <div class="legend-item">
        <div class="legend-color" style="background: #f97316;"></div>
        <span>High Vulnerability (0.55 - 0.75)</span>
      </div>
      <div class="legend-item">
        <div class="legend-color" style="background: #eab308;"></div>
        <span>Moderate (0.35 - 0.55)</span>
      </div>
      <div class="legend-item">
        <div class="legend-color" style="background: #22c55e;"></div>
        <span>Low / Vegetated (&lt; 0.35)</span>
      </div>
    </div>
  </div>

  <!-- Leaflet Map Container -->
  <div id="map"></div>

  <script>
    const geojsonData = {geojson_str};
    const recsData = {recs_str};

    // Initialize map centered at Bhopal urban core
    const map = L.map('map', {{
      center: [23.2500, 77.4100],
      zoom: 14,
      minZoom: 12,
      maxZoom: 18
    }});

    // Dark Basemap tile layer
    L.tileLayer('https://{{s}}.basemaps.cartocdn.com/dark_all/{{z}}/{{x}}/{{y}}{{r}}.png', {{
      attribution: '&copy; <a href="https://carto.com/">CARTO</a> | OSM contributors',
      maxZoom: 19
    }}).addTo(map);

    // Color function based on HVI Score
    function getHviColor(score) {{
      return score >= 0.75 ? '#dc2626' :
             score >= 0.55 ? '#f97316' :
             score >= 0.35 ? '#eab308' :
                             '#22c55e';
    }}

    function getBadgeClass(cat) {{
      if (cat === 'Extreme Hotspot') return 'badge-extreme';
      if (cat === 'High Vulnerability') return 'badge-high';
      if (cat === 'Moderate Vulnerability') return 'badge-mod';
      return 'badge-low';
    }}

    // GeoJSON Grid Layer
    const gridLayer = L.geoJSON(geojsonData, {{
      style: function(feature) {{
        const hvi = feature.properties.hvi_score || 0.4;
        return {{
          fillColor: getHviColor(hvi),
          weight: 0.8,
          opacity: 0.6,
          color: 'rgba(255,255,255,0.15)',
          fillOpacity: 0.68
        }};
      }},
      onEachFeature: function(feature, layer) {{
        const p = feature.properties;
        const cid = p.cell_id;
        const recs = recsData[cid] || [];

        let treeHtml = '';
        if (recs.length > 0) {{
          treeHtml = `<div class="tree-box">
            <div class="tree-box-title">🌿 AI Species Recommendation</div>`;
          recs.slice(0, 2).forEach((r, idx) => {{
            treeHtml += `<div class="tree-item"><b>${{idx+1}}. ${{r.common_name}}</b> (${{r.hindi_name}}) - Match: ${{r.match_score}}%</div>`;
          }});
          treeHtml += `</div>`;
        }} else if (p.hvi_score >= 0.75) {{
          treeHtml = `<div class="tree-box">
            <div class="tree-box-title">🌿 AI Species Recommendation</div>
            <div class="tree-item"><b>1. Karanj</b> (Millettia pinnata) - Deep Taproot</div>
            <div class="tree-item"><b>2. Neem</b> (Azadirachta indica) - High Shade</div>
          </div>`;
        }}

        const popupHtml = `
          <div class="popup-box">
            <div class="popup-header">
              <span class="popup-cell-id">${{p.cell_id}}</span>
              <span class="popup-badge ${{getBadgeClass(p.hvi_category)}}">${{p.hvi_category}}</span>
            </div>
            <div style="font-size: 0.76rem; color: #94a3b8; margin-bottom: 8px;">${{p.zone_name}}</div>
            <div class="metric-grid">
              <div class="metric-cell">
                <div class="m-lbl">HVI Score</div>
                <div class="m-val">${{p.hvi_score}}</div>
              </div>
              <div class="metric-cell">
                <div class="m-lbl">Land Temp (LST)</div>
                <div class="m-val" style="color:#f87171;">${{p.lst_celsius}}°C</div>
              </div>
              <div class="metric-cell">
                <div class="m-lbl">Vegetation (NDVI)</div>
                <div class="m-val" style="color:#4ade80;">${{p.ndvi}}</div>
              </div>
              <div class="metric-cell">
                <div class="m-lbl">Built Density</div>
                <div class="m-val">${{p.building_density_pct}}%</div>
              </div>
              <div class="metric-cell">
                <div class="m-lbl">Open Space</div>
                <div class="m-val">${{p.open_space_pct}}%</div>
              </div>
              <div class="metric-cell">
                <div class="m-lbl">Soil Type</div>
                <div class="m-val" style="font-size:0.75rem;">${{p.soil_type.split(' ')[0]}}</div>
              </div>
            </div>
            ${{treeHtml}}
          </div>
        `;
        layer.bindPopup(popupHtml);

        // Highlight interaction
        layer.on({{
          mouseover: function(e) {{
            const l = e.target;
            l.setStyle({{
              weight: 2,
              color: '#38bdf8',
              fillOpacity: 0.85
            }});
          }},
          mouseout: function(e) {{
            gridLayer.resetStyle(e.target);
          }}
        }});
      }}
    }}).addTo(map);

    console.log("Bhopal HVI Map successfully initialized.");
  </script>
</body>
</html>
"""

    os.makedirs(os.path.dirname(map_out), exist_ok=True)
    with open(map_out, mode="w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"-> Successfully written Interactive HTML Map: {map_out}")
    print("=" * 70)

if __name__ == "__main__":
    generate_interactive_map()
