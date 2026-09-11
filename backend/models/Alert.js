const mongoose = require('mongoose');

const alertSchema = new mongoose.Schema({
  alertId: {
    type: String,
    required: true,
    unique: true
  },
  cellId: {
    type: String,
    required: true
  },
  sensorId: String,
  alertType: {
    type: String,
    enum: ['high_heat_spike', 'drought_stress', 'mortality_risk', 'sensor_offline'],
    required: true
  },
  severity: {
    type: String,
    enum: ['low', 'medium', 'high', 'critical'],
    default: 'medium'
  },
  message: {
    type: String,
    required: true
  },
  resolved: {
    type: Boolean,
    default: false
  },
  resolvedAt: Date,
  createdAt: {
    type: Date,
    default: Date.now
  }
});

module.exports = mongoose.model('Alert', alertSchema);
