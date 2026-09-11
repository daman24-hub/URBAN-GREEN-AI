const mongoose = require('mongoose');

const plantingRecordSchema = new mongoose.Schema({
  cellId: {
    type: String,
    required: true,
    index: true
  },
  cityName: {
    type: String,
    default: 'Bhopal'
  },
  speciesId: {
    type: String,
    required: true
  },
  commonName: String,
  scientificName: String,
  treeCount: {
    type: Number,
    required: true,
    min: 1
  },
  predictedTempDropCelsius: Number,
  projectedCo2KgPerYear: Number,
  projectedStormwaterLitersPerYear: Number,
  status: {
    type: String,
    enum: ['planned', 'approved', 'planted', 'monitored'],
    default: 'planned'
  },
  plantedDate: Date,
  loggedBy: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User'
  },
  notes: String,
  createdAt: {
    type: Date,
    default: Date.now
  }
});

module.exports = mongoose.model('PlantingRecord', plantingRecordSchema);
