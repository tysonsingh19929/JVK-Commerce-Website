/**
 * JVK COMMERCE - BACKEND APPLICATION SERVER
 * Production-ready Express API with dual PostgreSQL/Disk persistence,
 * Client Management, Invoicing/Billings, Lead Capture & Admin Dashboard.
 */

require('dotenv').config();
const express = require('express');
const cors = require('cors');
const path = require('path');
const jwt = require('jsonwebtoken');
const db = require('./db');

const app = express();
const PORT = process.env.PORT || 8080;
const JWT_SECRET = process.env.JWT_SECRET || 'jvk_commerce_jwt_secret_key_2026_enterprise_growth';
const ADMIN_PASSWORD = process.env.ADMIN_PASSWORD || 'JVKAdmin2026!';
const ADMIN_USERNAME = process.env.ADMIN_USERNAME || 'admin';

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Explicit SEO routes
app.get('/robots.txt', (req, res) => {
  res.type('text/plain; charset=utf-8');
  res.send('User-agent: *\nAllow: /\nDisallow: /admin\nDisallow: /api/\n\nSitemap: https://jvkcommerce.com/sitemap.xml\n');
});

app.get('/sitemap.xml', (req, res) => {
  res.type('application/xml; charset=utf-8');
  res.sendFile(path.join(__dirname, 'sitemap.xml'));
});

// Serve main static frontend files
app.use(express.static(path.join(__dirname)));

// Serve Admin UI at /admin
app.use('/admin', express.static(path.join(__dirname, 'admin')));

// ----------------------------------------------------------------------------
// AUTHENTICATION MIDDLEWARE
// ----------------------------------------------------------------------------
function authenticateToken(req, res, next) {
  const authHeader = req.headers['authorization'];
  const token = authHeader && authHeader.split(' ')[1];

  if (!token) {
    return res.status(401).json({ success: false, error: 'Access token required' });
  }

  jwt.verify(token, JWT_SECRET, (err, user) => {
    if (err) {
      return res.status(403).json({ success: false, error: 'Invalid or expired token' });
    }
    req.user = user;
    next();
  });
}

// ----------------------------------------------------------------------------
// HEALTH CHECK
// ----------------------------------------------------------------------------
app.get('/api/health', async (req, res) => {
  try {
    const health = await db.getHealth();
    res.json({
      status: 'ok',
      service: 'JVK Commerce Backend',
      timestamp: new Date().toISOString(),
      database: health
    });
  } catch (err) {
    res.status(500).json({ status: 'error', error: err.message });
  }
});

// ----------------------------------------------------------------------------
// AUTH ROUTES
// ----------------------------------------------------------------------------
app.post('/api/auth/login', (req, res) => {
  const { username, password } = req.body;

  if (username === ADMIN_USERNAME && password === ADMIN_PASSWORD) {
    const token = jwt.sign(
      { username: ADMIN_USERNAME, role: 'admin' },
      JWT_SECRET,
      { expiresIn: '7d' }
    );
    return res.json({
      success: true,
      token,
      expiresIn: '7 days',
      user: { username: ADMIN_USERNAME, role: 'admin' }
    });
  }

  return res.status(401).json({ success: false, error: 'Invalid username or password' });
});

app.get('/api/auth/me', authenticateToken, (req, res) => {
  res.json({ success: true, user: req.user });
});

// ----------------------------------------------------------------------------
// ENQUIRIES ROUTES (PUBLIC SUBMIT + PROTECTED ADMIN LIST)
// ----------------------------------------------------------------------------
app.post('/api/enquiries', async (req, res) => {
  try {
    const { name, company, email, market, message } = req.body;

    if (!name || !email || !message) {
      return res.status(400).json({
        success: false,
        error: 'Name, email, and message are required fields.'
      });
    }

    // Basic email format check
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      return res.status(400).json({
        success: false,
        error: 'Please provide a valid email address.'
      });
    }

    const ip = req.headers['x-forwarded-for'] || req.socket.remoteAddress || '';
    const userAgent = req.headers['user-agent'] || '';

    const newEnquiry = await db.insertEnquiry({
      name: name.trim(),
      company: company ? company.trim() : 'Not provided',
      email: email.trim().toLowerCase(),
      market: market ? market.trim() : 'Not specified',
      message: message.trim(),
      ip_address: ip,
      user_agent: userAgent
    });

    res.status(201).json({
      success: true,
      id: newEnquiry.id,
      message: 'Enquiry received and securely stored.',
      data: newEnquiry
    });
  } catch (err) {
    console.error('Enquiry creation error:', err);
    res.status(500).json({ success: false, error: 'Internal server error' });
  }
});

app.get('/api/enquiries', authenticateToken, async (req, res) => {
  try {
    const status = req.query.status || 'all';
    const list = await db.getEnquiries(status);
    res.json({ success: true, count: list.length, data: list });
  } catch (err) {
    res.status(500).json({ success: false, error: err.message });
  }
});

app.patch('/api/enquiries/:id', authenticateToken, async (req, res) => {
  try {
    const { id } = req.params;
    const { status, notes } = req.body;
    const updates = {};
    if (status) updates.status = status;
    if (notes !== undefined) updates.notes = notes;

    const updated = await db.updateEnquiry(id, updates);
    if (!updated) {
      return res.status(404).json({ success: false, error: 'Enquiry not found' });
    }
    res.json({ success: true, data: updated });
  } catch (err) {
    res.status(500).json({ success: false, error: err.message });
  }
});

// ----------------------------------------------------------------------------
// LEARNING OPT-INS (PUBLIC SUBMIT + PROTECTED ADMIN LIST)
// ----------------------------------------------------------------------------
app.post('/api/learning', async (req, res) => {
  try {
    const { email, whatsapp, consent } = req.body;

    if (!email) {
      return res.status(400).json({ success: false, error: 'Email address is required.' });
    }

    if (consent !== true && consent !== 'true') {
      return res.status(400).json({ success: false, error: 'Consent agreement is required.' });
    }

    const ip = req.headers['x-forwarded-for'] || req.socket.remoteAddress || '';
    const record = await db.insertLearning({
      email: email.trim().toLowerCase(),
      whatsapp: whatsapp ? whatsapp.trim() : '',
      consent: true,
      ip_address: ip
    });

    res.status(201).json({
      success: true,
      id: record.id,
      message: 'Learning registration saved successfully.'
    });
  } catch (err) {
    console.error('Learning opt-in error:', err);
    res.status(500).json({ success: false, error: 'Internal server error' });
  }
});

app.get('/api/learning', authenticateToken, async (req, res) => {
  try {
    const list = await db.getLearningOptins();
    res.json({ success: true, count: list.length, data: list });
  } catch (err) {
    res.status(500).json({ success: false, error: err.message });
  }
});

// ----------------------------------------------------------------------------
// CLIENTS MANAGEMENT (ADMIN PROTECTED)
// ----------------------------------------------------------------------------
app.get('/api/clients', authenticateToken, async (req, res) => {
  try {
    const list = await db.getClients();
    res.json({ success: true, count: list.length, data: list });
  } catch (err) {
    res.status(500).json({ success: false, error: err.message });
  }
});

app.post('/api/clients', authenticateToken, async (req, res) => {
  try {
    const { name, company, email, phone, billing_address, country, vat_tax_number, marketplaces, service_tier, notes } = req.body;

    if (!name || !company || !email) {
      return res.status(400).json({ success: false, error: 'Contact name, company name, and email are required.' });
    }

    const newClient = await db.insertClient({
      name: name.trim(),
      company: company.trim(),
      email: email.trim().toLowerCase(),
      phone: phone ? phone.trim() : '',
      billing_address: billing_address ? billing_address.trim() : '',
      country: country ? country.trim() : '',
      vat_tax_number: vat_tax_number ? vat_tax_number.trim() : '',
      marketplaces: marketplaces ? marketplaces.trim() : '',
      service_tier: service_tier ? service_tier.trim() : 'Full Account Management',
      notes: notes ? notes.trim() : ''
    });

    res.status(201).json({ success: true, data: newClient });
  } catch (err) {
    res.status(500).json({ success: false, error: err.message });
  }
});

app.get('/api/clients/:id', authenticateToken, async (req, res) => {
  try {
    const client = await db.getClientById(req.params.id);
    if (!client) {
      return res.status(404).json({ success: false, error: 'Client not found' });
    }
    res.json({ success: true, data: client });
  } catch (err) {
    res.status(500).json({ success: false, error: err.message });
  }
});

app.put('/api/clients/:id', authenticateToken, async (req, res) => {
  try {
    const updated = await db.updateClient(req.params.id, req.body);
    if (!updated) {
      return res.status(404).json({ success: false, error: 'Client not found' });
    }
    res.json({ success: true, data: updated });
  } catch (err) {
    res.status(500).json({ success: false, error: err.message });
  }
});

// ----------------------------------------------------------------------------
// BILLINGS & INVOICES (ADMIN PROTECTED)
// ----------------------------------------------------------------------------
app.get('/api/billings', authenticateToken, async (req, res) => {
  try {
    const status = req.query.status || 'all';
    const list = await db.getBillings(status);
    res.json({ success: true, count: list.length, data: list });
  } catch (err) {
    res.status(500).json({ success: false, error: err.message });
  }
});

app.post('/api/billings', authenticateToken, async (req, res) => {
  try {
    const { client_id, client_name, client_company, invoice_number, service_description, amount, tax_amount, total_amount, currency, issue_date, due_date, status, payment_method, notes } = req.body;

    if (!service_description || amount === undefined) {
      return res.status(400).json({
        success: false,
        error: 'Service description and invoice amount are required.'
      });
    }

    const newBilling = await db.insertBilling({
      client_id,
      client_name,
      client_company,
      invoice_number,
      service_description,
      amount,
      tax_amount,
      total_amount,
      currency,
      issue_date,
      due_date,
      status,
      payment_method,
      notes
    });

    res.status(201).json({ success: true, data: newBilling });
  } catch (err) {
    res.status(500).json({ success: false, error: err.message });
  }
});

app.get('/api/billings/:id', authenticateToken, async (req, res) => {
  try {
    const billing = await db.getBillingById(req.params.id);
    if (!billing) {
      return res.status(404).json({ success: false, error: 'Invoice not found' });
    }
    res.json({ success: true, data: billing });
  } catch (err) {
    res.status(500).json({ success: false, error: err.message });
  }
});

app.patch('/api/billings/:id', authenticateToken, async (req, res) => {
  try {
    const updated = await db.updateBilling(req.params.id, req.body);
    if (!updated) {
      return res.status(404).json({ success: false, error: 'Invoice not found' });
    }
    res.json({ success: true, data: updated });
  } catch (err) {
    res.status(500).json({ success: false, error: err.message });
  }
});

// ----------------------------------------------------------------------------
// DASHBOARD STATS
// ----------------------------------------------------------------------------
app.get('/api/dashboard/stats', authenticateToken, async (req, res) => {
  try {
    const stats = await db.getDashboardStats();
    res.json({ success: true, data: stats });
  } catch (err) {
    res.status(500).json({ success: false, error: err.message });
  }
});

// Fallback to index.html for frontend routing (Universal Express 4/5 middleware)
app.use((req, res) => {
  if (req.path.startsWith('/admin')) {
    return res.sendFile(path.join(__dirname, 'admin', 'index.html'));
  }
  res.sendFile(path.join(__dirname, 'index.html'));
});

// Start server
app.listen(PORT, () => {
  console.log(`=======================================================`);
  console.log(`  JVK Commerce Backend running on port ${PORT}`);
  console.log(`  Live URL: http://localhost:${PORT}`);
  console.log(`  Admin Dashboard: http://localhost:${PORT}/admin`);
  console.log(`  Database Engine: ${db.isPostgres ? 'Render PostgreSQL' : 'Standalone Disk Store (data/jvk_store.json)'}`);
  console.log(`=======================================================`);
});
