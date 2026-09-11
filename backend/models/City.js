const mongoose = require('mongoose');

const citySchema = new mongoose.Schema({
  name: {
    type: String,
    required: true,
    unique: true,
    trim: true
  },
  state: {
    type: String,
    required: true
  },
  country: {
    type: String,
    default: 'India'
  },
  centerCoordinates: {
    latitude: { type: Number, required: true },
    longitude: { type: Number, required: true }
  },
  bounds: {
    minLat: Number,
    maxLat: Number,
    minLon: Number,
    maxLon: Number
  },
  baselineClimate: {
    summerPeakTempCelsius: Number,
    annualRainfallMm: Number,
    predominantSoil: String
  },
  createdAt: {
    type: Date,
    default: Date.now
  }
});

module.exports = mongoose.model('City', citySchema);
