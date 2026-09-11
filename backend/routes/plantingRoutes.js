const express = require('express');
const PlantingRecord = require('../models/PlantingRecord');
const { authenticateToken, authorizeRoles } = require('../middleware/auth');

const router = express.Router();

// GET /api/plantings (with filters for status, cellId)
router.get('/', async (req, res) => {
  try {
    const { status, cellId } = req.query;
    const filter = {};
    if (status) filter.status = status;
    if (cellId) filter.cellId = cellId;

    const plantings = await PlantingRecord.find(filter)
      .populate('loggedBy', 'name email role department')
      .sort({ createdAt: -1 });

    res.json({
      success: true,
      count: plantings.length,
      plantings
    });
  } catch (err) {
    res.status(500).json({ success: false, message: err.message });
  }
});

// POST /api/plantings (Authenticated)
router.post('/', authenticateToken, async (req, res) => {
  try {
    const plantingData = {
      ...req.body,
      loggedBy: req.user.id
    };
    const planting = await PlantingRecord.create(plantingData);
    res.status(201).json({ success: true, planting });
  } catch (err) {
    res.status(400).json({ success: false, message: err.message });
  }
});

// PATCH /api/plantings/:id/status (e.g., 'planned' -> 'approved' -> 'planted')
router.patch('/:id/status', authenticateToken, async (req, res) => {
  try {
    const { status, plantedDate, notes } = req.body;
    const validStatuses = ['planned', 'approved', 'planted', 'monitored'];

    if (!validStatuses.includes(status)) {
      return res.status(400).json({ success: false, message: `Status must be one of: ${validStatuses.join(', ')}` });
    }

    const update = { status };
    if (plantedDate) update.plantedDate = plantedDate;
    if (notes) update.notes = notes;

    const planting = await PlantingRecord.findByIdAndUpdate(req.params.id, update, { new: true });
    if (!planting) {
      return res.status(404).json({ success: false, message: 'Planting record not found.' });
    }

    res.json({ success: true, planting });
  } catch (err) {
    res.status(500).json({ success: false, message: err.message });
  }
});

// DELETE /api/plantings/:id (Admin / Govt only)
router.delete('/:id', authenticateToken, authorizeRoles('govt'), async (req, res) => {
  try {
    const planting = await PlantingRecord.findByIdAndDelete(req.params.id);
    if (!planting) {
      return res.status(404).json({ success: false, message: 'Planting record not found.' });
    }
    res.json({ success: true, message: 'Planting record deleted successfully.' });
  } catch (err) {
    res.status(500).json({ success: false, message: err.message });
  }
});

module.exports = router;
