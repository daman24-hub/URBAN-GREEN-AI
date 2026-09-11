const express = require('express');
const aiBridgeService = require('../services/aiBridgeService');
const GridCell = require('../models/GridCell');
const PlantingRecord = require('../models/PlantingRecord');
const { authenticateToken } = require('../middleware/auth');

const router = express.Router();

/**
 * POST /api/ai/sync-plan
 * Calls FastAPI microservice /api/plan, caches/upserts results into MongoDB
 */
router.post('/sync-plan', authenticateToken, async (req, res) => {
  try {
    const city = req.query.city || 'bhopal';
    const topHotspots = parseInt(req.query.topHotspots || '10', 10);
    const targetTempDrop = parseFloat(req.query.targetTempDrop || '2.0');

    // 1. Fetch live generated plan from FastAPI microservice
    const aiPlan = await aiBridgeService.fetchPlan(city, topHotspots, targetTempDrop);

    const syncedHotspots = [];
    const createdPlantings = [];

    // 2. Iterate through plan details and upsert into MongoDB
    for (const item of aiPlan.plan_details) {
      // Upsert GridCell cache
      const updatedCell = await GridCell.findOneAndUpdate(
        { cellId: item.cell_id },
        {
          cellId: item.cell_id,
          cityName: city.charAt(0).toUpperCase() + city.slice(1),
          latitude: item.latitude,
          longitude: item.longitude,
          zoneName: item.zone_name,
          lstCelsius: item.current_lst_celsius,
          openSpacePct: item.open_space_pct,
          hviScore: item.current_hvi_score,
          hviRank: item.hvi_rank,
          lastUpdated: new Date()
        },
        { upsert: true, new: true }
      );
      syncedHotspots.push(updatedCell.cellId);

      // Create or update planned planting record for primary recommended species
      if (item.top_species_selected && item.top_species_selected.length > 0) {
        const topSpecies = item.top_species_selected[0];

        const plantingDoc = await PlantingRecord.findOneAndUpdate(
          { cellId: item.cell_id, status: 'planned' },
          {
            cellId: item.cell_id,
            cityName: city.charAt(0).toUpperCase() + city.slice(1),
            speciesId: topSpecies.species_id,
            commonName: topSpecies.common_name,
            scientificName: topSpecies.scientific_name,
            treeCount: item.recommended_trees_count,
            predictedTempDropCelsius: item.predicted_temperature_drop_celsius,
            projectedCo2KgPerYear: item.annual_co2_kg,
            projectedStormwaterLitersPerYear: item.annual_stormwater_liters,
            status: 'planned',
            notes: `AI Generated recommendation from HVI rank #${item.hvi_rank}. Botanical match score: ${topSpecies.match_score}%.`,
            loggedBy: req.user.id
          },
          { upsert: true, new: true }
        );
        createdPlantings.push(plantingDoc._id);
      }
    }

    res.json({
      success: true,
      message: `Successfully synchronized ${syncedHotspots.length} hotspots from AI Microservice into MongoDB.`,
      city: city.charAt(0).toUpperCase() + city.slice(1),
      summary: aiPlan.summary,
      syncedCellsCount: syncedHotspots.length,
      syncedPlantingRecordsCount: createdPlantings.length,
      sampleCellIds: syncedHotspots.slice(0, 5)
    });
  } catch (err) {
    res.status(502).json({
      success: false,
      message: 'Failed to synchronize with AI Microservice.',
      error: err.message
    });
  }
});

/**
 * GET /api/ai/live-hotspots
 * Proxy pass-through querying FastAPI /api/hotspots
 */
router.get('/live-hotspots', async (req, res) => {
  try {
    const { city, limit, minHvi } = req.query;
    const data = await aiBridgeService.fetchHotspots(city || 'bhopal', limit || 20, minHvi);
    res.json({ success: true, data });
  } catch (err) {
    res.status(502).json({ success: false, error: err.message });
  }
});

module.exports = router;
