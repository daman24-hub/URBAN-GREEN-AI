const express = require('express');
const Species = require('../models/Species');
const { authenticateToken, authorizeRoles } = require('../middleware/auth');

const router = express.Router();

// GET /api/species (with optional query filters e.g. ?coolingValue=Very+High&rootType=Deep+Taproot)
router.get('/', async (req, res) => {
  try {
    const { coolingValue, canopyCategory, rootType, search } = req.query;
    const filter = {};

    if (coolingValue) filter.coolingValue = coolingValue;
    if (canopyCategory) filter.canopyCategory = canopyCategory;
    if (rootType) filter.rootType = new RegExp(rootType, 'i');
    if (search) {
      filter.$or = [
        { commonName: new RegExp(search, 'i') },
        { scientificName: new RegExp(search, 'i') },
        { hindiName: new RegExp(search, 'i') }
      ];
    }

    const species = await Species.find(filter).sort({ commonName: 1 });
    res.json({
      success: true,
      count: species.length,
      species
    });
  } catch (err) {
    res.status(500).json({ success: false, message: err.message });
  }
});

// GET /api/species/:id (by Mongo _id or speciesId e.g. SPECIES_01)
router.get('/:id', async (req, res) => {
  try {
    const { id } = req.params;
    let sp = await Species.findOne({
      $or: [
        { speciesId: id.toUpperCase() },
        ...(id.match(/^[0-9a-fA-F]{24}$/) ? [{ _id: id }] : [])
      ]
    });

    if (!sp) {
      return res.status(404).json({ success: false, message: 'Species not found.' });
    }
    res.json({ success: true, species: sp });
  } catch (err) {
    res.status(500).json({ success: false, message: err.message });
  }
});

// POST /api/species (Restricted to govt / developer)
router.post('/', authenticateToken, authorizeRoles('govt', 'developer'), async (req, res) => {
  try {
    const species = await Species.create(req.body);
    res.status(201).json({ success: true, species });
  } catch (err) {
    res.status(400).json({ success: false, message: err.message });
  }
});

module.exports = router;
