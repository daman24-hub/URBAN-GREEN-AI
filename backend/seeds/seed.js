const mongoose = require('mongoose');
const bcrypt = require('bcryptjs');
const fs = require('fs');
const path = require('path');
const connectDB = require('../config/db');

const User = require('../models/User');
const City = require('../models/City');
const Species = require('../models/Species');
const Sensor = require('../models/Sensor');
const Alert = require('../models/Alert');

const seedData = async () => {
  try {
    await connectDB();
    console.log('Seeding Database for Urban Green AI...');

    // 1. Seed Users
    await User.deleteMany();
    console.log(' - Cleared existing users.');

    const salt = await bcrypt.genSalt(10);
    const hashedPassword = await bcrypt.hash('Password123!', salt);

    const users = await User.create([
      {
        name: 'Dr. R. Sharma (Director)',
        email: 'govt@urbangreen.ai',
        password: hashedPassword,
        role: 'govt',
        department: 'Bhopal Municipal Corporation & Urban Forestry'
      },
      {
        name: 'A. Verma (GIS Engineer)',
        email: 'developer@urbangreen.ai',
        password: hashedPassword,
        role: 'developer',
        department: 'Smart City Spatial Analytics Unit'
      },
      {
        name: 'M. Patel (Grid Operations)',
        email: 'utility@urbangreen.ai',
        password: hashedPassword,
        role: 'utility',
        department: 'MP Urban Infrastructure & Power Works'
      }
    ]);
    console.log(` -> Seeded ${users.length} default users with roles: govt, developer, utility.`);

    // 2. Seed City (Bhopal)
    await City.deleteMany();
    const city = await City.create({
      name: 'Bhopal',
      state: 'Madhya Pradesh',
      country: 'India',
      centerCoordinates: {
        latitude: 23.2500,
        longitude: 77.4100
      },
      bounds: {
        minLat: 23.2300,
        maxLat: 23.2700,
        minLon: 77.3900,
        maxLon: 77.4300
      },
      baselineClimate: {
        summerPeakTempCelsius: 42.5,
        annualRainfallMm: 1095.0,
        predominantSoil: 'Deep Black Clay (Vertisols)'
      }
    });
    console.log(` -> Seeded pilot city: ${city.name}, ${city.state}.`);

    // 3. Seed Species from data/species_database.json
    const speciesJsonPath = path.join(__dirname, '../../data/species_database.json');
    if (fs.existsSync(speciesJsonPath)) {
      await Species.deleteMany();
      const rawSpecies = JSON.parse(fs.readFileSync(speciesJsonPath, 'utf-8'));

      const speciesDocs = rawSpecies.map(s => ({
        speciesId: s.species_id,
        commonName: s.common_name,
        scientificName: s.scientific_name,
        hindiName: s.hindi_name,
        canopySpreadM: s.canopy_spread_m,
        canopyCategory: s.canopy_category,
        matureHeightM: s.mature_height_m,
        coolingValue: s.cooling_value,
        waterRequirement: s.water_requirement,
        soilPreference: Array.isArray(s.soil_preference) ? s.soil_preference.join(', ') : s.soil_preference,
        rootType: s.root_type,
        droughtTolerance: s.drought_tolerance,
        airPollutionTolerance: s.air_pollution_tolerance,
        growthRate: s.growth_rate,
        crownDensity: s.crown_density,
        idealUrbanContext: s.ideal_urban_context
      }));

      await Species.insertMany(speciesDocs);
      console.log(` -> Seeded ${speciesDocs.length} tree species into MongoDB.`);
    }

    // 4. Seed Simulated IoT Sensors in Hotspots
    await Sensor.deleteMany();
    const sensors = await Sensor.create([
      {
        sensorId: 'IOT_BPL_MPN_01',
        cellId: 'BPL_CELL_0308',
        sensorType: 'soil_moisture',
        status: 'active',
        batteryPct: 94,
        lastReading: { value: 18.5, unit: '%' }
      },
      {
        sensorId: 'IOT_BPL_MPN_02',
        cellId: 'BPL_CELL_0308',
        sensorType: 'ambient_temp',
        status: 'active',
        batteryPct: 88,
        lastReading: { value: 46.8, unit: '°C' }
      }
    ]);
    console.log(` -> Seeded ${sensors.length} simulated IoT sensors.`);

    // 5. Seed Alert
    await Alert.deleteMany();
    await Alert.create({
      alertId: 'ALT_2026_001',
      cellId: 'BPL_CELL_0308',
      sensorId: 'IOT_BPL_MPN_02',
      alertType: 'high_heat_spike',
      severity: 'critical',
      message: 'Ambient heat spike detected in MP Nagar (>46.5°C). Critical watering needed for newly planted saplings.',
      resolved: false
    });
    console.log(' -> Seeded sample heat anomaly alert.');

    console.log('Database Seeding Completed Successfully!');
    process.exit(0);
  } catch (err) {
    console.error('Seeding Error:', err);
    process.exit(1);
  }
};

seedData();
