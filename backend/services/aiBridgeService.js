const axios = require('axios');

const AI_SERVICE_URL = process.env.AI_SERVICE_URL || 'http://127.0.0.1:8000';

class AIBridgeService {
  /**
   * Calls FastAPI microservice GET /api/plan
   */
  async fetchPlan(city = 'bhopal', topHotspots = 10, targetTempDrop = 2.0) {
    try {
      const response = await axios.get(`${AI_SERVICE_URL}/api/plan`, {
        params: {
          city,
          top_hotspots: topHotspots,
          target_temp_drop: targetTempDrop
        },
        timeout: 10000
      });
      return response.data;
    } catch (error) {
      throw new Error(`AI Microservice Connection Failed: ${error.message}`);
    }
  }

  /**
   * Calls FastAPI microservice GET /api/hotspots
   */
  async fetchHotspots(city = 'bhopal', limit = 20, minHvi = null) {
    try {
      const params = { city, limit };
      if (minHvi) params.min_hvi = minHvi;

      const response = await axios.get(`${AI_SERVICE_URL}/api/hotspots`, { params, timeout: 8000 });
      return response.data;
    } catch (error) {
      throw new Error(`AI Microservice Error: ${error.message}`);
    }
  }

  /**
   * Calls FastAPI microservice GET /api/recommend
   */
  async fetchSpeciesRecommendation(lat, lng, topN = 3) {
    try {
      const response = await axios.get(`${AI_SERVICE_URL}/api/recommend`, {
        params: { lat, lng, top_n: topN },
        timeout: 8000
      });
      return response.data;
    } catch (error) {
      throw new Error(`AI Microservice Error: ${error.message}`);
    }
  }
}

module.exports = new AIBridgeService();
