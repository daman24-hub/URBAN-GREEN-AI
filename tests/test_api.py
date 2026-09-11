"""
Automated Test Suite for Urban Green AI FastAPI Endpoints
"""

import os
import unittest
from fastapi.testclient import TestClient
from app.main import app

class TestUrbanGreenAIAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_01_health_check(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "online")
        self.assertIn("Bhopal", data["pilot_city"])
        self.assertIn("/api/plan", data["endpoints"]["master_plan"])

    def test_02_get_hotspots(self):
        response = self.client.get("/api/hotspots?city=bhopal&limit=5")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["city"], "Bhopal")
        self.assertEqual(data["total_returned"], 5)
        self.assertEqual(len(data["hotspots"]), 5)

        # Verify sorted descending by HVI
        hvis = [h["hvi_score"] for h in data["hotspots"]]
        self.assertEqual(hvis, sorted(hvis, reverse=True))
        # Ensure HVI is high for top hotspots
        self.assertGreaterEqual(hvis[0], 0.90)

    def test_03_get_hotspots_filter(self):
        response = self.client.get("/api/hotspots?min_hvi=0.90")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        for cell in data["hotspots"]:
            self.assertGreaterEqual(cell["hvi_score"], 0.90)
            self.assertEqual(cell["hvi_category"], "Extreme Hotspot")

    def test_04_recommend_coordinates(self):
        # Query coordinates within MP Nagar
        lat, lng = 23.2355, 77.4215
        response = self.client.get(f"/api/recommend?lat={lat}&lng={lng}&top_n=3")
        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.assertIn("matched_cell", data)
        self.assertIn("recommended_species", data)
        self.assertEqual(len(data["recommended_species"]), 3)

        # Distance should be small (within grid resolution)
        self.assertLess(data["distance_meters"], 500.0)

        # Check top recommendation properties
        top_sp = data["recommended_species"][0]
        self.assertIn("common_name", top_sp)
        self.assertIn("match_score", top_sp)
        self.assertGreater(top_sp["match_score"], 80.0)

    def test_05_impact_estimate(self):
        payload = {
            "cell_id": "BPL_CELL_0308",
            "plantings": [
                {"species_id": "SPECIES_05", "count": 15},  # Karanj (Medium, High Cooling)
                {"species_id": "SPECIES_01", "count": 10}   # Neem (Large, Very High Cooling)
            ]
        }
        response = self.client.post("/api/impact-estimate", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.assertEqual(data["total_trees"], 25)
        self.assertGreater(data["total_canopy_area_sqm"], 500.0)
        self.assertGreater(data["predicted_temperature_drop_celsius"], 0.5)
        self.assertGreater(data["annual_co2_sequestration_kg"], 400.0)
        self.assertGreater(data["annual_stormwater_intercepted_liters"], 50000.0)
        self.assertEqual(len(data["breakdown"]), 2)

    def test_06_master_plan(self):
        response = self.client.get("/api/plan?city=bhopal&top_hotspots=5&target_temp_drop=2.0")
        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.assertIn("summary", data)
        self.assertIn("plan_details", data)
        self.assertEqual(len(data["plan_details"]), 5)

        summary = data["summary"]
        self.assertEqual(summary["total_hotspot_cells_addressed"], 5)
        self.assertGreater(summary["total_trees_to_plant"], 15)
        self.assertGreater(summary["average_temperature_reduction_celsius"], 0.5)
        self.assertGreater(summary["total_annual_co2_sequestration_metric_tons"], 0.1)

        # Verify export files exist
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        geojson_file = os.path.join(base_dir, "outputs", "bhopal_planting_plan.geojson")
        csv_file = os.path.join(base_dir, "outputs", "bhopal_planting_plan.csv")

        self.assertTrue(os.path.exists(geojson_file))
        self.assertTrue(os.path.exists(csv_file))

if __name__ == "__main__":
    unittest.main()
