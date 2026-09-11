process.env.NODE_ENV = 'test';
const assert = require('assert');
const http = require('http');
const mongoose = require('mongoose');
const app = require('../server');

let server;
let baseUrl;
let authToken;
let govtToken;
let testPlantingId;

function request(method, path, body = null, token = null) {
  return new Promise((resolve, reject) => {
    const url = new URL(path, baseUrl);
    const options = {
      method,
      hostname: url.hostname,
      port: url.port,
      path: url.pathname + url.search,
      headers: {
        'Content-Type': 'application/json'
      }
    };

    if (token) {
      options.headers['Authorization'] = `Bearer ${token}`;
    }

    const req = http.request(options, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          const parsed = JSON.parse(data);
          resolve({ status: res.statusCode, body: parsed });
        } catch (e) {
          resolve({ status: res.statusCode, body: data });
        }
      });
    });

    req.on('error', reject);
    if (body) {
      req.write(JSON.stringify(body));
    }
    req.end();
  });
}

async function runTests() {
  console.log('======================================================================');
  console.log('Running Automated Test Suite: Express + MongoDB Backend (Week 5)');
  console.log('======================================================================');

  const PORT = 5055;
  server = app.listen(PORT);
  baseUrl = `http://127.0.0.1:${PORT}`;

  try {
    // Test 1: Health Check
    console.log('\n[1] Testing GET /api/health ...');
    const health = await request('GET', '/api/health');
    assert.strictEqual(health.status, 200);
    assert.strictEqual(health.body.status, 'online');
    console.log('    -> PASSED: Health check returned online status.');

    // Test 2: Login as Developer
    console.log('\n[2] Testing POST /api/auth/login (Developer) ...');
    const loginDev = await request('POST', '/api/auth/login', {
      email: 'developer@urbangreen.ai',
      password: 'Password123!'
    });
    assert.strictEqual(loginDev.status, 200);
    assert.strictEqual(loginDev.body.success, true);
    assert.ok(loginDev.body.token);
    authToken = loginDev.body.token;
    console.log('    -> PASSED: Successfully logged in and received JWT token.');

    // Test 3: Login as Govt Director
    console.log('\n[3] Testing POST /api/auth/login (Govt Admin) ...');
    const loginGovt = await request('POST', '/api/auth/login', {
      email: 'govt@urbangreen.ai',
      password: 'Password123!'
    });
    assert.strictEqual(loginGovt.status, 200);
    govtToken = loginGovt.body.token;
    console.log('    -> PASSED: Successfully logged in as Govt role.');

    // Test 4: Auth /me protected route
    console.log('\n[4] Testing GET /api/auth/me (Protected Route) ...');
    const me = await request('GET', '/api/auth/me', null, authToken);
    assert.strictEqual(me.status, 200);
    assert.strictEqual(me.body.user.role, 'developer');
    console.log(`    -> PASSED: Returned authenticated user ${me.body.user.name} (${me.body.user.role}).`);

    // Test 5: Get Cities
    console.log('\n[5] Testing GET /api/cities ...');
    const cities = await request('GET', '/api/cities');
    assert.strictEqual(cities.status, 200);
    assert.ok(cities.body.count >= 1);
    assert.strictEqual(cities.body.cities[0].name, 'Bhopal');
    console.log(`    -> PASSED: Retrieved ${cities.body.count} city: ${cities.body.cities[0].name}.`);

    // Test 6: Get Species & Query Filter
    console.log('\n[6] Testing GET /api/species & Specific Lookup ...');
    const allSpecies = await request('GET', '/api/species?coolingValue=Very+High');
    assert.strictEqual(allSpecies.status, 200);
    assert.ok(allSpecies.body.count >= 5);
    console.log(`    -> PASSED: Retrieved ${allSpecies.body.count} species with 'Very High' cooling.`);

    const singleSpecies = await request('GET', '/api/species/SPECIES_01');
    assert.strictEqual(singleSpecies.status, 200);
    assert.strictEqual(singleSpecies.body.species.commonName, 'Neem');
    console.log(`    -> PASSED: Lookup SPECIES_01 returned: ${singleSpecies.body.species.commonName} (${singleSpecies.body.species.hindiName}).`);

    // Test 7: Create Planting Record
    console.log('\n[7] Testing POST /api/plantings ...');
    const createPlanting = await request('POST', '/api/plantings', {
      cellId: 'BPL_CELL_0308',
      speciesId: 'SPECIES_05',
      commonName: 'Karanj',
      scientificName: 'Millettia pinnata',
      treeCount: 15,
      predictedTempDropCelsius: 1.2,
      projectedCo2KgPerYear: 330.0,
      status: 'planned'
    }, authToken);
    assert.strictEqual(createPlanting.status, 201);
    testPlantingId = createPlanting.body.planting._id;
    console.log(`    -> PASSED: Created planting record (ID: ${testPlantingId}).`);

    // Test 8: Patch Planting Status
    console.log('\n[8] Testing PATCH /api/plantings/:id/status ...');
    const patchStatus = await request('PATCH', `/api/plantings/${testPlantingId}/status`, {
      status: 'approved',
      notes: 'Approved by Bhopal municipal urban greening committee'
    }, authToken);
    assert.strictEqual(patchStatus.status, 200);
    assert.strictEqual(patchStatus.body.planting.status, 'approved');
    console.log('    -> PASSED: Updated planting status to "approved".');

    // Test 9: AI Microservice Bridge Live Sync
    console.log('\n[9] Testing POST /api/ai/sync-plan (FastAPI Bridge) ...');
    const syncPlan = await request('POST', '/api/ai/sync-plan?city=bhopal&topHotspots=5', null, authToken);
    assert.strictEqual(syncPlan.status, 200);
    assert.strictEqual(syncPlan.body.success, true);
    assert.ok(syncPlan.body.syncedCellsCount >= 5);
    console.log(`    -> PASSED: Successfully bridged with FastAPI /api/plan! Synchronized ${syncPlan.body.syncedCellsCount} hotspots into MongoDB.`);

    console.log('\n======================================================================');
    console.log('ALL 9 TESTS PASSED SUCCESSFULLY! Express + MongoDB + AI Bridge verified.');
    console.log('======================================================================\n');
  } catch (err) {
    console.error('TEST FAILED:', err);
    process.exitCode = 1;
  } finally {
    server.close();
    await mongoose.connection.close();
    process.exit(process.exitCode || 0);
  }
}

runTests();
