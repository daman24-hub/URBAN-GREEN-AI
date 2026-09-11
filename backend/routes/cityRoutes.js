const express = require('express');
const City = require('../models/City');
const { authenticateToken, authorizeRoles } = require('../middleware/auth');

const router = express.Router();

// GET /api/cities
router.get('/', async (req, res) => {
  try {
    const cities = await City.find();
    res.json({
      success: true,
      count: cities.length,
      cities
    });
  } catch (err) {
    res.status(500).json({ success: false, message: err.message });
  }
});

// GET /api/cities/:id
router.get('/:id', async (req, res) => {
  try {
    const city = await City.findById(req.params.id);
    if (!city) {
      return res.status(404).json({ success: false, message: 'City not found' });
    }
    res.json({ success: true, city });
  } catch (err) {
    res.status(500).json({ success: false, message: err.message });
  }
});

// POST /api/cities (Admin/Govt or Developer only)
router.post('/', authenticateToken, authorizeRoles('govt', 'developer'), async (req, res) => {
  try {
    const city = await City.create(req.body);
    res.status(201).json({ success: true, city });
  } catch (err) {
    res.status(400).json({ success: false, message: err.message });
  }
});

module.exports = router;
