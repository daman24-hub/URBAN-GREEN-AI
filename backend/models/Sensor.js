const mongoose = require('mongoose');

const sensorSchema = new mongoose.Schema({
  sensorId: {
    type: String,
    required: true,
    unique: true,
    index: true
  },
  cellId: {
    type: String,
    required: true
  },
  sensorType: {
    type: String,
    enum: ['soil_moisture', 'ambient_temp', 'canopy_growth', 'sap_flow'],
    required: true
  },
  status: {
    type: String,
    enum: ['active', 'offline', 'warning', 'critical'],
    default: 'active'
  },
  batteryPct: {
    type: Number,
    default: 100
  },
  lastReading: {
    value: Number,
    unit: String,
    timestamp: {
      type: Date,
      default: Date.now
    }
  },
  installedDate: {
    type: Date,
    default: Date.now
  }
});

module.exports = mongoose.model('Sensor', sensorSchema);
