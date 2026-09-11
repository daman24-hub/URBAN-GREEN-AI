require('dotenv').config();
const express = require('express');
const cors = require('cors');
const connectDB = require('./config/db');

// Route imports
const authRoutes = require('./routes/authRoutes');
const cityRoutes = require('./routes/cityRoutes');
const speciesRoutes = require('./routes/speciesRoutes');
const plantingRoutes = require('./routes/plantingRoutes');
const aiBridgeRoutes = require('./routes/aiBridgeRoutes');

const app = express();
const PORT = process.env.PORT || 5001;

// Connect to Database
connectDB();

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Health Check
app.get('/api/health', (req, res) => {
  res.json({
    status: 'online',
    service: 'Urban Green AI — Express + MongoDB Backend',
    version: '1.0.0',
    port: PORT,
    database: 'MongoDB (127.0.0.1:27017)',
    connectedServices: {
      aiMicroservice: process.env.AI_SERVICE_URL || 'http://127.0.0.1:8000'
    }
  });
});

// API Routes
app.use('/api/auth', authRoutes);
app.use('/api/cities', cityRoutes);
app.use('/api/species', speciesRoutes);
app.use('/api/plantings', plantingRoutes);
app.use('/api/ai', aiBridgeRoutes);

// 404 Handler
app.use('*', (req, res) => {
  res.status(404).json({ success: false, message: `Route ${req.originalUrl} not found.` });
});

// Start Server
if (process.env.NODE_ENV !== 'test') {
  app.listen(PORT, () => {
    console.log(`======================================================================`);
    console.log(`Urban Green AI Express Backend listening on http://127.0.0.1:${PORT}`);
    console.log(`AI Microservice connected on ${process.env.AI_SERVICE_URL || 'http://127.0.0.1:8000'}`);
    console.log(`======================================================================`);
  });
}

module.exports = app;
