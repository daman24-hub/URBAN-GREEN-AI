const mongoose = require('mongoose');

const gridCellSchema = new mongoose.Schema({
  cellId: {
    type: String,
    required: true,
    unique: true,
    index: true
  },
  cityName: {
    type: String,
    required: true,
    default: 'Bhopal'
  },
  latitude: {
    type: Number,
    required: true
  },
  longitude: {
    type: Number,
    required: true
  },
  zoneName: String,
  lstCelsius: Number,
  ndvi: Number,
  buildingDensityPct: Number,
  openSpacePct: Number,
  roadDensityKmPerSqKm: Number,
  soilType: String,
  annualRainfallMm: Number,
  hviScore: {
    type: Number,
    index: true
  },
  hviCategory: String,
  hviRank: Number,
  lastUpdated: {
    type: Date,
    default: Date.now
  }
});

module.exports = mongoose.model('GridCell', gridCellSchema);
