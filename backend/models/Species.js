const mongoose = require('mongoose');

const speciesSchema = new mongoose.Schema({
  speciesId: {
    type: String,
    required: true,
    unique: true,
    index: true
  },
  commonName: {
    type: String,
    required: true
  },
  scientificName: {
    type: String,
    required: true
  },
  hindiName: String,
  canopySpreadM: Number,
  canopyCategory: {
    type: String,
    enum: ['Small', 'Medium', 'Large']
  },
  matureHeightM: Number,
  coolingValue: {
    type: String,
    enum: ['Very High', 'High', 'Moderate']
  },
  waterRequirement: {
    type: String,
    enum: ['Low', 'Medium', 'High']
  },
  soilPreference: String,
  rootType: String,
  droughtTolerance: String,
  airPollutionTolerance: String,
  growthRate: String,
  crownDensity: String,
  idealUrbanContext: String,
  createdAt: {
    type: Date,
    default: Date.now
  }
});

module.exports = mongoose.model('Species', speciesSchema);
