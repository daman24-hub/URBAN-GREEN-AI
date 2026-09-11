#!/usr/bin/env python3
"""
Week 3: Rule-Based Species Matching Engine
City: Bhopal, Madhya Pradesh, India
Focus: Match urban tree species to 100m x 100m grid cells based on HVI thermal stress,
soil compatibility, open space constraints, root architecture safety, and water demand.
"""

import csv
import json
import os

def load_species_database(species_csv_path):
    species_list = []
    with open(species_csv_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["canopy_spread_m"] = float(row["canopy_spread_m"])
            row["mature_height_m"] = float(row["mature_height_m"])
            species_list.append(row)
    return species_list

def species_filter(grid_cell, species_list, top_n=3):
    """
    Rule-based & multi-criteria matching function for urban forestry.
    
    Args:
        grid_cell (dict): Dictionary with cell attributes:
            - hvi_score (float)
            - lst_celsius (float)
            - building_density_pct (float)
            - open_space_pct (float)
            - soil_type (str)
            - zone_name (str)
        species_list (list): Catalog of tree species.
        top_n (int): Number of top species to return.
        
    Returns:
        list of dict: Top recommended species with match score and specific rationale.
    """
    hvi = float(grid_cell.get("hvi_score", 0.5))
    lst = float(grid_cell.get("lst_celsius", 38.0))
    bld_pct = float(grid_cell.get("building_density_pct", 50.0))
    open_pct = float(grid_cell.get("open_space_pct", 25.0))
    soil = grid_cell.get("soil_type", "Clay Loam")
    zone = grid_cell.get("zone_name", "")

    candidates = []

    for sp in species_list:
        score = 0.0
        reasons = []

        # -------------------------------------------------------------
        # Rule 1: Thermal Stress & Cooling Value
        # -------------------------------------------------------------
        cooling = sp["cooling_value"]
        if hvi >= 0.75:  # Extreme Hotspot
            if cooling == "Very High":
                score += 35.0
                reasons.append("Very high cooling capacity critical for severe microclimate heat island")
            elif cooling == "High":
                score += 25.0
                reasons.append("High cooling capacity helps buffer high surface temperature")
            else:
                score += 10.0
        elif hvi >= 0.55:  # High Vulnerability
            if cooling in ["Very High", "High"]:
                score += 30.0
                reasons.append("Strong shade canopy provides effective temperature reduction")
            else:
                score += 18.0
        else:  # Moderate or Low
            score += 20.0
            reasons.append("Balanced microclimate shade")

        # -------------------------------------------------------------
        # Rule 2: Physical Spatial Constraint & Root Architecture
        # -------------------------------------------------------------
        canopy_cat = sp["canopy_category"]
        root = sp["root_type"]

        if bld_pct >= 70.0 or open_pct <= 15.0:
            # High-density built-up environment (e.g. MP Nagar, Old Bhopal)
            if root in ["Spreading Surface", "Spreading Aerial", "Spreading Buttress"]:
                # Severe risk of pavement destruction or structural foundation damage
                score -= 40.0
                reasons.append("Penalized: Aggressive surface roots pose infrastructure hazard in dense zone")
            elif root == "Deep Taproot":
                score += 25.0
                reasons.append("Deep taproot is safe near paved sidewalks and building foundations")
            else:
                score += 10.0

            # Canopy sizing check
            if canopy_cat == "Small":
                score += 20.0
                reasons.append("Compact crown fits narrow street rights-of-way and setback gaps")
            elif canopy_cat == "Medium":
                score += 15.0
                reasons.append("Moderate crown size manageable with urban pruning")
            else:
                # Large tree in cramped cell
                score -= 15.0
                reasons.append("Large crown may conflict with adjacent overhead utilities/structures")
        else:
            # Moderate to low density zone (parks, wide avenues, lakefront)
            if canopy_cat == "Large":
                score += 25.0
                reasons.append("Expansive canopy maximizes contiguous shade over open ground")
            elif canopy_cat == "Medium":
                score += 18.0
            else:
                score += 12.0

        # -------------------------------------------------------------
        # Rule 3: Soil Compatibility
        # -------------------------------------------------------------
        pref_soil = sp["soil_preference"]
        # Vertisols / Black Cotton Soil in Bhopal
        if "Black Cotton/Clay" in soil or "Vertisol" in soil:
            if "Black Cotton/Clay" in pref_soil or "Adaptable" in pref_soil:
                score += 20.0
                reasons.append("Highly tolerant of shrink-swell characteristics of Bhopal Vertisols")
            else:
                score += 5.0
        # Alluvial near lakes
        elif "Alluvial" in soil:
            if "Alluvial" in pref_soil or "Adaptable" in pref_soil:
                score += 20.0
                reasons.append("Adapted to alluvial moisture and lakeside drainage")
            else:
                score += 8.0
        else:  # Clay Loam
            if "Clay Loam" in pref_soil or "Adaptable" in pref_soil or "Loam" in pref_soil:
                score += 20.0
                reasons.append("Well-suited to loamy urban soil profile")
            else:
                score += 10.0

        # -------------------------------------------------------------
        # Rule 4: Water Demand & Summer Drought Resilience
        # -------------------------------------------------------------
        drought = sp["drought_tolerance"]
        water_req = sp["water_requirement"]

        if drought in ["Very High", "High"]:
            score += 15.0
            reasons.append("Excellent drought resilience during Bhopal's pre-monsoon heatwaves")
        elif drought == "Moderate":
            score += 8.0

        # Penalize high water trees in dense dry commercial sectors without irrigation
        if water_req == "High" and ("Lake" not in zone and open_pct < 40.0):
            score -= 15.0
            reasons.append("Penalized: High water demand requires frequent irrigation in non-riparian zone")

        # -------------------------------------------------------------
        # Rule 5: Pollution & Dust Tolerance
        # -------------------------------------------------------------
        pollution = sp["air_pollution_tolerance"]
        if bld_pct > 60.0 and pollution == "High":
            score += 10.0
            reasons.append("High dust and vehicular particulate absorption capacity")

        final_score = round(max(0.0, min(100.0, score)), 1)
        candidates.append({
            "species_id": sp["species_id"],
            "common_name": sp["common_name"],
            "scientific_name": sp["scientific_name"],
            "hindi_name": sp["hindi_name"],
            "canopy_spread_m": sp["canopy_spread_m"],
            "cooling_value": sp["cooling_value"],
            "root_type": sp["root_type"],
            "match_score": final_score,
            "justification": " | ".join(reasons)
        })

    # Sort descending by match_score
    candidates_sorted = sorted(candidates, key=lambda x: x["match_score"], reverse=True)
    return candidates_sorted[:top_n]


def test_hotspot_matching():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    species_csv = os.path.join(base_dir, "data", "bhopal_urban_tree_species.csv")
    hotspots_csv = os.path.join(base_dir, "outputs", "bhopal_hotspots_ranked.csv")
    out_csv = os.path.join(base_dir, "outputs", "hotspot_species_recommendations.csv")

    species_list = load_species_database(species_csv)

    with open(hotspots_csv, mode="r", encoding="utf-8") as f:
        hotspots = list(csv.DictReader(f))

    # Test against top 10 hotspot cells (as requested in Week 3 Sat curriculum)
    test_sample = hotspots[:10]

    output_rows = []

    print("=" * 80)
    print("Testing Species Matcher against Top 10 Bhopal Heat Hotspots")
    print("=" * 80)

    for cell in test_sample:
        recs = species_filter(cell, species_list, top_n=3)
        cell_id = cell["cell_id"]
        zone = cell["zone_name"]
        lst = float(cell["lst_celsius"])
        hvi = float(cell["hvi_score"])
        built = float(cell["building_density_pct"])
        open_sp = float(cell["open_space_pct"])

        print(f"\nHotspot Cell: {cell_id} | Rank: {cell['hvi_rank']} | Zone: {zone}")
        print(f" -> LST: {lst:.1f}°C | HVI: {hvi:.4f} | Built: {built:.1f}% | Open Space: {open_sp:.1f}%")
        print(" Recommended Urban Trees:")

        for i, rec in enumerate(recs, 1):
            print(f"   {i}. {rec['common_name']} ({rec['scientific_name']} / {rec['hindi_name']})")
            print(f"      Match Score: {rec['match_score']}/100 | Cooling: {rec['cooling_value']} | Root: {rec['root_type']}")
            print(f"      Why: {rec['justification']}")

            output_rows.append({
                "hvi_rank": cell["hvi_rank"],
                "cell_id": cell_id,
                "zone_name": zone,
                "lst_celsius": lst,
                "hvi_score": hvi,
                "building_density_pct": built,
                "open_space_pct": open_sp,
                "recommendation_rank": i,
                "species_id": rec["species_id"],
                "common_name": rec["common_name"],
                "scientific_name": rec["scientific_name"],
                "hindi_name": rec["hindi_name"],
                "match_score": rec["match_score"],
                "cooling_value": rec["cooling_value"],
                "canopy_spread_m": rec["canopy_spread_m"],
                "root_type": rec["root_type"],
                "justification": rec["justification"]
            })

    # Save recommendations to CSV
    fieldnames = list(output_rows[0].keys())
    with open(out_csv, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(output_rows)

    print("\n" + "=" * 80)
    print(f"-> Successfully saved test recommendations to: {out_csv}")
    print("=" * 80)

if __name__ == "__main__":
    test_hotspot_matching()
