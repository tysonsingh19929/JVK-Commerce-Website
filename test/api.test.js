/**
 * JVK COMMERCE - BACKEND API AUTOMATED TEST SUITE
 * Tests health, enquiry capture, learning opt-in, JWT auth,
 * client record management, and invoicing / billing operations.
 */

const http = require('http');

const PORT = 8089;
process.env.PORT = PORT;
process.env.ADMIN_PASSWORD = 'TestPassword123!';
process.env.JWT_SECRET = 'test_jwt_secret_key';

// Start server in test mode
const app = require('../server');

function request(options, data = null) {
  return new Promise((resolve, reject) => {
    const req = http.request(options, (res) => {
      let body = '';
      res.on('data', chunk => body += chunk);
      res.on('end', () => {
        try {
          const parsed = JSON.parse(body);
          resolve({ status: res.statusCode, headers: res.headers, body: parsed });
        } catch (e) {
          resolve({ status: res.statusCode, headers: res.headers, body });
        }
      });
    });
    req.on('error', reject);
    if (data) {
      req.write(typeof data === 'string' ? data : JSON.stringify(data));
    }
    req.end();
  });
}

async function runTests() {
  console.log('=== STARTING JVK COMMERCE API TEST SUITE ===\n');
  let token = '';
  let clientId = '';
  let billingId = '';
  let passed = 0;
  let failed = 0;

  function assert(condition, message) {
    if (condition) {
      console.log(`  [PASS] ${message}`);
      passed++;
    } else {
      console.error(`  [FAIL] ${message}`);
      failed++;
    }
  }

  try {
    // Wait for server to listen
    await new Promise(r => setTimeout(r, 500));

    // Test 1: Health check
    const health = await request({
      hostname: 'localhost',
      port: PORT,
      path: '/api/health',
      method: 'GET'
    });
    assert(health.status === 200 && health.body.status === 'ok', 'Health check returns 200 OK');

    // Test 2: Submit Public Enquiry
    const enqRes = await request({
      hostname: 'localhost',
      port: PORT,
      path: '/api/enquiries',
      method: 'POST',
      headers: { 'Content-Type': 'application/json' }
    }, {
      name: 'Test Client',
      company: 'Test Brands LLC',
      email: 'test@brand.com',
      market: 'USA & UK',
      message: 'Need account management and PPC support for 20 SKUs.'
    });
    assert(enqRes.status === 201 && enqRes.body.success === true, 'Submit enquiry returns 201 Created with record ID');
    const enquiryId = enqRes.body.id;

    // Test 3: Submit Learning Opt-In
    const lrnRes = await request({
      hostname: 'localhost',
      port: PORT,
      path: '/api/learning',
      method: 'POST',
      headers: { 'Content-Type': 'application/json' }
    }, {
      email: 'learning@brand.com',
      whatsapp: '+971554741125',
      consent: true
    });
    assert(lrnRes.status === 201 && lrnRes.body.success === true, 'Submit learning opt-in returns 201 Created');

    // Test 4: Admin Login
    const loginRes = await request({
      hostname: 'localhost',
      port: PORT,
      path: '/api/auth/login',
      method: 'POST',
      headers: { 'Content-Type': 'application/json' }
    }, {
      username: 'admin',
      password: 'TestPassword123!'
    });
    assert(loginRes.status === 200 && Boolean(loginRes.body.token), 'Admin login returns 200 OK with valid JWT token');
    token = loginRes.body.token;

    // Test 5: Protected Dashboard Stats
    const statsRes = await request({
      hostname: 'localhost',
      port: PORT,
      path: '/api/dashboard/stats',
      method: 'GET',
      headers: { 'Authorization': `Bearer ${token}` }
    });
    assert(statsRes.status === 200 && statsRes.body.data.overview.total_enquiries > 0, 'Dashboard stats returns 200 OK with aggregated metrics');

    // Test 6: Create Client
    const clientRes = await request({
      hostname: 'localhost',
      port: PORT,
      path: '/api/clients',
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    }, {
      name: 'Faisal Al-Nuaimi',
      company: 'Nuaimi Retail Group',
      email: 'faisal@nuaimigroup.ae',
      phone: '+971509876543',
      country: 'United Arab Emirates',
      vat_tax_number: 'TRN 100987654300003',
      marketplaces: 'Amazon.ae, Noon, Amazon.sa',
      service_tier: 'Full Account Management & PPC'
    });
    assert(clientRes.status === 201 && clientRes.body.data.id, 'Create client returns 201 Created');
    clientId = clientRes.body.data.id;

    // Test 7: Create Invoice / Billing
    const billingRes = await request({
      hostname: 'localhost',
      port: PORT,
      path: '/api/billings',
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    }, {
      client_id: clientId,
      invoice_number: 'JVK-2026-TEST',
      service_description: 'Q4 Marketplace Strategy & Amazon Advertising Campaign',
      amount: 4500.00,
      tax_amount: 225.00,
      total_amount: 4725.00,
      currency: 'USD',
      issue_date: '2026-11-05',
      due_date: '2026-11-20',
      status: 'pending',
      payment_method: 'Bank Wire'
    });
    assert(billingRes.status === 201 && billingRes.body.data.total_amount === 4725.00, 'Create billing invoice returns 201 Created with exact total amount');
    billingId = billingRes.body.data.id;

    // Test 8: Update Billing Status (Mark Paid)
    const updateBillRes = await request({
      hostname: 'localhost',
      port: PORT,
      path: `/api/billings/${billingId}`,
      method: 'PATCH',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    }, {
      status: 'paid',
      payment_method: 'Stripe Online Payment'
    });
    assert(updateBillRes.status === 200 && updateBillRes.body.data.status === 'paid', 'Mark billing as Paid updates record and timestamp');

    // Test 9: Update Enquiry Status
    const updateEnqRes = await request({
      hostname: 'localhost',
      port: PORT,
      path: `/api/enquiries/${enquiryId}`,
      method: 'PATCH',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    }, {
      status: 'contacted',
      notes: 'Initial strategy call scheduled via WhatsApp.'
    });
    assert(updateEnqRes.status === 200 && updateEnqRes.body.data.status === 'contacted', 'Update enquiry status and notes returns 200 OK');

    console.log(`\n=== RESULTS: ${passed} PASSED, ${failed} FAILED ===\n`);
    process.exit(failed > 0 ? 1 : 0);
  } catch (err) {
    console.error('Test execution error:', err);
    process.exit(1);
  }
}

runTests();
