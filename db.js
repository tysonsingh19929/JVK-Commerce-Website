/**
 * JVK COMMERCE - MULTI-ENGINE DATABASE ADAPTER
 * Supports:
 *   1. MongoDB Atlas (when MONGODB_URI or MONGO_URI is set)
 *   2. Render Managed PostgreSQL (when DATABASE_URL is set)
 *   3. Atomic disk persistence (data/jvk_store.json) for standalone execution
 */

const fs = require('fs');
const path = require('path');
const { Pool } = require('pg');
const { MongoClient } = require('mongodb');

const DATA_DIR = path.join(__dirname, 'data');
const STORE_FILE = path.join(DATA_DIR, 'jvk_store.json');

// Ensure data folder exists
if (!fs.existsSync(DATA_DIR)) {
  fs.mkdirSync(DATA_DIR, { recursive: true });
}

// -----------------------------------------------------------------------------
// Initial Sample Data (for seeding empty databases & local dev)
// -----------------------------------------------------------------------------
const initialData = {
  enquiries: [],
  learning_optins: [],
  clients: [
    {
      id: "cli_sample_1",
      name: "Alexander Vance",
      company: "Vance Consumer Products Ltd",
      email: "alex@vanceproducts.com",
      phone: "+44 7700 900123",
      billing_address: "14 Berkeley Square, Mayfair, London, W1J 6BQ, UK",
      country: "United Kingdom",
      vat_tax_number: "GB987654321",
      marketplaces: "Amazon US, Amazon UK, Noon UAE",
      service_tier: "Full Account Management & PPC",
      status: "active",
      notes: "Annual marketplace management contract covering 24 baby hygiene SKUs.",
      created_at: new Date(Date.now() - 15 * 86400000).toISOString(),
      updated_at: new Date().toISOString()
    },
    {
      id: "cli_sample_2",
      name: "Tariq Al-Mansoor",
      company: "Al-Mansoor Trading & Distribution",
      email: "tariq@almansoor.ae",
      phone: "+971 50 123 4567",
      billing_address: "Business Bay, Iris Bay Tower, Suite 1204, Dubai, UAE",
      country: "United Arab Emirates",
      vat_tax_number: "TRN 100234567800003",
      marketplaces: "Amazon.ae, Amazon.sa, Noon",
      service_tier: "Regional GCC Marketplace Launch & WBN",
      status: "active",
      notes: "GCC regional launch across beauty and personal care lines.",
      created_at: new Date(Date.now() - 30 * 86400000).toISOString(),
      updated_at: new Date().toISOString()
    }
  ],
  billings: [
    {
      id: "inv_sample_1",
      client_id: "cli_sample_1",
      client_name: "Alexander Vance",
      client_company: "Vance Consumer Products Ltd",
      invoice_number: "JVK-2026-001",
      service_description: "Monthly Global Marketplace Management & PPC Optimization - November 2026",
      amount: 3500.00,
      tax_amount: 0.00,
      total_amount: 3500.00,
      currency: "USD",
      issue_date: "2026-11-01",
      due_date: "2026-11-15",
      status: "paid",
      paid_at: "2026-11-03T10:15:00.000Z",
      payment_method: "Bank Wire Transfer",
      notes: "Wire received in full via Emirates NBD account.",
      created_at: new Date(Date.now() - 5 * 86400000).toISOString(),
      updated_at: new Date().toISOString()
    },
    {
      id: "inv_sample_2",
      client_id: "cli_sample_2",
      client_name: "Tariq Al-Mansoor",
      client_company: "Al-Mansoor Trading & Distribution",
      invoice_number: "JVK-2026-002",
      service_description: "GCC Regional Marketplace Onboarding & Arabic Catalog Localization",
      amount: 4200.00,
      tax_amount: 210.00,
      total_amount: 4410.00,
      currency: "USD",
      issue_date: "2026-11-02",
      due_date: "2026-11-20",
      status: "pending",
      paid_at: null,
      payment_method: "Direct Transfer",
      notes: "Invoice sent. Follow up before due date.",
      created_at: new Date(Date.now() - 3 * 86400000).toISOString(),
      updated_at: new Date().toISOString()
    }
  ]
};

// -----------------------------------------------------------------------------
// Engine 1: MongoDB Atlas Driver
// -----------------------------------------------------------------------------
const mongoUri = process.env.MONGODB_URI || process.env.MONGO_URI;
let mongoClient = null;
let mongoDb = null;
let mongoInitPromise = null;

async function initMongo() {
  if (!mongoUri) return null;
  if (mongoDb) return mongoDb;
  if (mongoInitPromise) return mongoInitPromise;

  mongoInitPromise = (async () => {
    try {
      console.log('[Database] Connecting to MongoDB Atlas...');
      mongoClient = new MongoClient(mongoUri, {
        serverSelectionTimeoutMS: 8000,
        connectTimeoutMS: 10000
      });
      await mongoClient.connect();
      const dbName = process.env.MONGODB_DB_NAME || 'jvk_commerce';
      mongoDb = mongoClient.db(dbName);
      console.log(`[Database] MongoDB connected successfully: database="${dbName}"`);

      // Ensure indexes
      await Promise.allSettled([
        mongoDb.collection('enquiries').createIndex({ id: 1 }, { unique: true }),
        mongoDb.collection('enquiries').createIndex({ created_at: -1 }),
        mongoDb.collection('enquiries').createIndex({ status: 1 }),
        mongoDb.collection('learning_optins').createIndex({ id: 1 }, { unique: true }),
        mongoDb.collection('learning_optins').createIndex({ created_at: -1 }),
        mongoDb.collection('clients').createIndex({ id: 1 }, { unique: true }),
        mongoDb.collection('clients').createIndex({ created_at: -1 }),
        mongoDb.collection('billings').createIndex({ id: 1 }, { unique: true }),
        mongoDb.collection('billings').createIndex({ client_id: 1 }),
        mongoDb.collection('billings').createIndex({ created_at: -1 })
      ]);

      // Seed initial sample data if empty
      const clientCount = await mongoDb.collection('clients').countDocuments();
      if (clientCount === 0) {
        await mongoDb.collection('clients').insertMany(initialData.clients);
        await mongoDb.collection('billings').insertMany(initialData.billings);
        console.log('[Database] MongoDB seeded with initial clients & billings');
      }

      return mongoDb;
    } catch (err) {
      console.error('[Database] MongoDB connection error:', err.message);
      mongoDb = null;
      return null;
    }
  })();

  return mongoInitPromise;
}

if (mongoUri) {
  initMongo();
}

// -----------------------------------------------------------------------------
// Engine 2: PostgreSQL Driver (Render Managed PostgreSQL)
// -----------------------------------------------------------------------------
const isPostgres = Boolean(!mongoUri && process.env.DATABASE_URL);
let pgPool = null;

if (isPostgres) {
  pgPool = new Pool({
    connectionString: process.env.DATABASE_URL,
    ssl: process.env.DATABASE_URL.includes('localhost') ? false : { rejectUnauthorized: false }
  });
}

async function initPostgres() {
  if (!pgPool) return;

  const createTablesSQL = `
    CREATE TABLE IF NOT EXISTS enquiries (
      id VARCHAR(64) PRIMARY KEY,
      name VARCHAR(255) NOT NULL,
      company VARCHAR(255),
      email VARCHAR(255) NOT NULL,
      market VARCHAR(255),
      message TEXT NOT NULL,
      ip_address VARCHAR(64),
      user_agent TEXT,
      status VARCHAR(32) DEFAULT 'new',
      notes TEXT,
      created_at TIMESTAMPTZ DEFAULT NOW(),
      updated_at TIMESTAMPTZ DEFAULT NOW()
    );

    CREATE TABLE IF NOT EXISTS learning_optins (
      id VARCHAR(64) PRIMARY KEY,
      email VARCHAR(255) NOT NULL,
      whatsapp VARCHAR(64),
      consent BOOLEAN NOT NULL DEFAULT TRUE,
      ip_address VARCHAR(64),
      status VARCHAR(32) DEFAULT 'subscribed',
      created_at TIMESTAMPTZ DEFAULT NOW()
    );

    CREATE TABLE IF NOT EXISTS clients (
      id VARCHAR(64) PRIMARY KEY,
      name VARCHAR(255) NOT NULL,
      company VARCHAR(255) NOT NULL,
      email VARCHAR(255) NOT NULL,
      phone VARCHAR(64),
      billing_address TEXT,
      country VARCHAR(128),
      vat_tax_number VARCHAR(128),
      marketplaces TEXT,
      service_tier VARCHAR(128),
      status VARCHAR(32) DEFAULT 'active',
      notes TEXT,
      created_at TIMESTAMPTZ DEFAULT NOW(),
      updated_at TIMESTAMPTZ DEFAULT NOW()
    );

    CREATE TABLE IF NOT EXISTS billings (
      id VARCHAR(64) PRIMARY KEY,
      client_id VARCHAR(64) REFERENCES clients(id) ON DELETE SET NULL,
      client_name VARCHAR(255),
      client_company VARCHAR(255),
      invoice_number VARCHAR(64) NOT NULL,
      service_description TEXT NOT NULL,
      amount NUMERIC(12,2) NOT NULL,
      tax_amount NUMERIC(12,2) DEFAULT 0.00,
      total_amount NUMERIC(12,2) NOT NULL,
      currency VARCHAR(16) DEFAULT 'USD',
      issue_date DATE,
      due_date DATE,
      status VARCHAR(32) DEFAULT 'pending',
      paid_at TIMESTAMPTZ,
      payment_method VARCHAR(64),
      notes TEXT,
      created_at TIMESTAMPTZ DEFAULT NOW(),
      updated_at TIMESTAMPTZ DEFAULT NOW()
    );
  `;

  try {
    await pgPool.query(createTablesSQL);
    console.log('[Database] PostgreSQL schema initialized successfully');
  } catch (err) {
    console.error('[Database] Failed to initialize PostgreSQL tables:', err);
  }
}

if (isPostgres) {
  initPostgres();
}

// -----------------------------------------------------------------------------
// Engine 3: Local Disk JSON Store Fallback
// -----------------------------------------------------------------------------
function loadLocalStore() {
  try {
    if (!fs.existsSync(STORE_FILE)) {
      fs.writeFileSync(STORE_FILE, JSON.stringify(initialData, null, 2), 'utf-8');
      return initialData;
    }
    const raw = fs.readFileSync(STORE_FILE, 'utf-8');
    return JSON.parse(raw);
  } catch (err) {
    console.error('Error reading store file, initializing defaults:', err);
    return initialData;
  }
}

function saveLocalStore(data) {
  try {
    fs.writeFileSync(STORE_FILE, JSON.stringify(data, null, 2), 'utf-8');
  } catch (err) {
    console.error('Error saving store file:', err);
  }
}

if (!mongoUri && !isPostgres) {
  loadLocalStore();
  console.log('[Database] Standalone disk store active at data/jvk_store.json');
}

// Helper to determine active database engine
async function getActiveEngine() {
  if (mongoUri) {
    const db = await initMongo();
    if (db) return 'mongodb';
  }
  if (isPostgres && pgPool) return 'postgresql';
  return 'standalone_disk';
}

// -----------------------------------------------------------------------------
// UNIFIED REPOSITORY INTERFACE
// -----------------------------------------------------------------------------
module.exports = {
  isPostgres,
  isMongo: Boolean(mongoUri),

  async getHealth() {
    const engine = await getActiveEngine();
    if (engine === 'mongodb') {
      try {
        const ping = await mongoDb.command({ ping: 1 });
        return { status: 'ok', engine: 'mongodb', ping: ping.ok === 1 ? 'ok' : 'degraded', database: mongoDb.databaseName };
      } catch (err) {
        return { status: 'error', engine: 'mongodb', error: err.message };
      }
    }
    if (engine === 'postgresql') {
      const res = await pgPool.query('SELECT NOW() as now');
      return { status: 'ok', engine: 'postgresql', time: res.rows[0].now };
    }
    return { status: 'ok', engine: 'standalone_disk', file: 'data/jvk_store.json' };
  },

  // ---------------------------------------------------------------------------
  // ENQUIRIES (LEADS)
  // ---------------------------------------------------------------------------
  async insertEnquiry(enquiry) {
    const record = {
      id: `enq_${Date.now()}_${Math.random().toString(36).substr(2, 6)}`,
      status: 'new',
      notes: '',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      ...enquiry
    };

    const engine = await getActiveEngine();
    if (engine === 'mongodb') {
      const doc = { ...record };
      await mongoDb.collection('enquiries').insertOne(doc);
      return record;
    }
    if (engine === 'postgresql') {
      const sql = `
        INSERT INTO enquiries (id, name, company, email, market, message, ip_address, user_agent, status, notes, created_at, updated_at)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
        RETURNING *;
      `;
      const values = [
        record.id, record.name, record.company, record.email, record.market, record.message,
        record.ip_address || '', record.user_agent || '', record.status, record.notes,
        record.created_at, record.updated_at
      ];
      const res = await pgPool.query(sql, values);
      return res.rows[0];
    } else {
      const store = loadLocalStore();
      store.enquiries.unshift(record);
      saveLocalStore(store);
      return record;
    }
  },

  async getEnquiries(filterStatus) {
    const engine = await getActiveEngine();
    if (engine === 'mongodb') {
      const query = filterStatus && filterStatus !== 'all' ? { status: filterStatus } : {};
      const items = await mongoDb.collection('enquiries').find(query, { projection: { _id: 0 } }).sort({ created_at: -1 }).toArray();
      return items;
    }
    if (engine === 'postgresql') {
      let sql = 'SELECT * FROM enquiries ORDER BY created_at DESC';
      let params = [];
      if (filterStatus && filterStatus !== 'all') {
        sql = 'SELECT * FROM enquiries WHERE status = $1 ORDER BY created_at DESC';
        params = [filterStatus];
      }
      const res = await pgPool.query(sql, params);
      return res.rows;
    } else {
      const store = loadLocalStore();
      if (filterStatus && filterStatus !== 'all') {
        return store.enquiries.filter(e => e.status === filterStatus);
      }
      return store.enquiries;
    }
  },

  async updateEnquiry(id, updates) {
    const engine = await getActiveEngine();
    if (engine === 'mongodb') {
      const result = await mongoDb.collection('enquiries').findOneAndUpdate(
        { id },
        { $set: { ...updates, updated_at: new Date().toISOString() } },
        { returnDocument: 'after', projection: { _id: 0 } }
      );
      return result;
    }
    if (engine === 'postgresql') {
      const fields = [];
      const values = [];
      let idx = 1;
      for (const [key, val] of Object.entries(updates)) {
        fields.push(`${key} = $${idx}`);
        values.push(val);
        idx++;
      }
      fields.push(`updated_at = $${idx}`);
      values.push(new Date().toISOString());
      values.push(id);
      const sql = `UPDATE enquiries SET ${fields.join(', ')} WHERE id = $${idx + 1} RETURNING *;`;
      const res = await pgPool.query(sql, values);
      return res.rows[0];
    } else {
      const store = loadLocalStore();
      const item = store.enquiries.find(e => e.id === id);
      if (!item) return null;
      Object.assign(item, updates, { updated_at: new Date().toISOString() });
      saveLocalStore(store);
      return item;
    }
  },

  // ---------------------------------------------------------------------------
  // LEARNING OPT-INS (OPERATOR ACADEMY)
  // ---------------------------------------------------------------------------
  async insertLearning(optin) {
    const record = {
      id: `lrn_${Date.now()}_${Math.random().toString(36).substr(2, 6)}`,
      status: 'subscribed',
      created_at: new Date().toISOString(),
      ...optin
    };

    const engine = await getActiveEngine();
    if (engine === 'mongodb') {
      await mongoDb.collection('learning_optins').insertOne({ ...record });
      return record;
    }
    if (engine === 'postgresql') {
      const sql = `
        INSERT INTO learning_optins (id, email, whatsapp, consent, ip_address, status, created_at)
        VALUES ($1, $2, $3, $4, $5, $6, $7)
        RETURNING *;
      `;
      const values = [record.id, record.email, record.whatsapp || '', record.consent, record.ip_address || '', record.status, record.created_at];
      const res = await pgPool.query(sql, values);
      return res.rows[0];
    } else {
      const store = loadLocalStore();
      store.learning_optins.unshift(record);
      saveLocalStore(store);
      return record;
    }
  },

  async getLearningOptins() {
    const engine = await getActiveEngine();
    if (engine === 'mongodb') {
      return await mongoDb.collection('learning_optins').find({}, { projection: { _id: 0 } }).sort({ created_at: -1 }).toArray();
    }
    if (engine === 'postgresql') {
      const res = await pgPool.query('SELECT * FROM learning_optins ORDER BY created_at DESC');
      return res.rows;
    } else {
      const store = loadLocalStore();
      return store.learning_optins;
    }
  },

  // ---------------------------------------------------------------------------
  // CLIENTS
  // ---------------------------------------------------------------------------
  async insertClient(client) {
    const record = {
      id: `cli_${Date.now()}_${Math.random().toString(36).substr(2, 6)}`,
      status: client.status || 'active',
      notes: client.notes || '',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      ...client
    };

    const engine = await getActiveEngine();
    if (engine === 'mongodb') {
      await mongoDb.collection('clients').insertOne({ ...record });
      return record;
    }
    if (engine === 'postgresql') {
      const sql = `
        INSERT INTO clients (id, name, company, email, phone, billing_address, country, vat_tax_number, marketplaces, service_tier, status, notes, created_at, updated_at)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14)
        RETURNING *;
      `;
      const values = [
        record.id, record.name, record.company, record.email, record.phone || '',
        record.billing_address || '', record.country || '', record.vat_tax_number || '',
        record.marketplaces || '', record.service_tier || '', record.status, record.notes,
        record.created_at, record.updated_at
      ];
      const res = await pgPool.query(sql, values);
      return res.rows[0];
    } else {
      const store = loadLocalStore();
      store.clients.unshift(record);
      saveLocalStore(store);
      return record;
    }
  },

  async getClients() {
    const engine = await getActiveEngine();
    if (engine === 'mongodb') {
      return await mongoDb.collection('clients').find({}, { projection: { _id: 0 } }).sort({ created_at: -1 }).toArray();
    }
    if (engine === 'postgresql') {
      const res = await pgPool.query('SELECT * FROM clients ORDER BY created_at DESC');
      return res.rows;
    } else {
      const store = loadLocalStore();
      return store.clients;
    }
  },

  async getClientById(id) {
    const engine = await getActiveEngine();
    if (engine === 'mongodb') {
      const client = await mongoDb.collection('clients').findOne({ id }, { projection: { _id: 0 } });
      if (!client) return null;
      const billings = await mongoDb.collection('billings').find({ client_id: id }, { projection: { _id: 0 } }).sort({ created_at: -1 }).toArray();
      return { ...client, billings };
    }
    if (engine === 'postgresql') {
      const res = await pgPool.query('SELECT * FROM clients WHERE id = $1', [id]);
      if (res.rows.length === 0) return null;
      const client = res.rows[0];
      const billingsRes = await pgPool.query('SELECT * FROM billings WHERE client_id = $1 ORDER BY created_at DESC', [id]);
      client.billings = billingsRes.rows;
      return client;
    } else {
      const store = loadLocalStore();
      const client = store.clients.find(c => c.id === id);
      if (!client) return null;
      const billings = store.billings.filter(b => b.client_id === id);
      return { ...client, billings };
    }
  },

  async updateClient(id, updates) {
    const engine = await getActiveEngine();
    if (engine === 'mongodb') {
      const result = await mongoDb.collection('clients').findOneAndUpdate(
        { id },
        { $set: { ...updates, updated_at: new Date().toISOString() } },
        { returnDocument: 'after', projection: { _id: 0 } }
      );
      return result;
    }
    if (engine === 'postgresql') {
      const fields = [];
      const values = [];
      let idx = 1;
      for (const [key, val] of Object.entries(updates)) {
        fields.push(`${key} = $${idx}`);
        values.push(val);
        idx++;
      }
      fields.push(`updated_at = $${idx}`);
      values.push(new Date().toISOString());
      values.push(id);
      const sql = `UPDATE clients SET ${fields.join(', ')} WHERE id = $${idx + 1} RETURNING *;`;
      const res = await pgPool.query(sql, values);
      return res.rows[0];
    } else {
      const store = loadLocalStore();
      const client = store.clients.find(c => c.id === id);
      if (!client) return null;
      Object.assign(client, updates, { updated_at: new Date().toISOString() });
      saveLocalStore(store);
      return client;
    }
  },

  // ---------------------------------------------------------------------------
  // BILLINGS & INVOICES
  // ---------------------------------------------------------------------------
  async insertBilling(billing) {
    let clientName = billing.client_name || '';
    let clientCompany = billing.client_company || '';

    if (billing.client_id) {
      const client = await this.getClientById(billing.client_id);
      if (client) {
        clientName = client.name;
        clientCompany = client.company;
      }
    }

    const amount = parseFloat(billing.amount) || 0;
    const taxAmount = parseFloat(billing.tax_amount) || 0;
    const totalAmount = parseFloat(billing.total_amount) || (amount + taxAmount);

    const record = {
      id: `inv_${Date.now()}_${Math.random().toString(36).substr(2, 6)}`,
      client_id: billing.client_id || null,
      client_name: clientName,
      client_company: clientCompany,
      invoice_number: billing.invoice_number || `JVK-${new Date().getFullYear()}-${Math.floor(100 + Math.random() * 900)}`,
      service_description: billing.service_description,
      amount,
      tax_amount: taxAmount,
      total_amount: totalAmount,
      currency: billing.currency || 'USD',
      issue_date: billing.issue_date || new Date().toISOString().split('T')[0],
      due_date: billing.due_date || new Date(Date.now() + 14 * 86400000).toISOString().split('T')[0],
      status: billing.status || 'pending',
      paid_at: billing.status === 'paid' ? new Date().toISOString() : null,
      payment_method: billing.payment_method || 'Bank Wire',
      notes: billing.notes || '',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    };

    const engine = await getActiveEngine();
    if (engine === 'mongodb') {
      await mongoDb.collection('billings').insertOne({ ...record });
      return record;
    }
    if (engine === 'postgresql') {
      const sql = `
        INSERT INTO billings (id, client_id, client_name, client_company, invoice_number, service_description, amount, tax_amount, total_amount, currency, issue_date, due_date, status, paid_at, payment_method, notes, created_at, updated_at)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18)
        RETURNING *;
      `;
      const values = [
        record.id, record.client_id, record.client_name, record.client_company,
        record.invoice_number, record.service_description, record.amount, record.tax_amount,
        record.total_amount, record.currency, record.issue_date, record.due_date,
        record.status, record.paid_at, record.payment_method, record.notes,
        record.created_at, record.updated_at
      ];
      const res = await pgPool.query(sql, values);
      return res.rows[0];
    } else {
      const store = loadLocalStore();
      store.billings.unshift(record);
      saveLocalStore(store);
      return record;
    }
  },

  async getBillings(filterStatus) {
    const engine = await getActiveEngine();
    if (engine === 'mongodb') {
      const query = filterStatus && filterStatus !== 'all' ? { status: filterStatus } : {};
      return await mongoDb.collection('billings').find(query, { projection: { _id: 0 } }).sort({ issue_date: -1, created_at: -1 }).toArray();
    }
    if (engine === 'postgresql') {
      let sql = 'SELECT * FROM billings ORDER BY issue_date DESC, created_at DESC';
      let params = [];
      if (filterStatus && filterStatus !== 'all') {
        sql = 'SELECT * FROM billings WHERE status = $1 ORDER BY issue_date DESC, created_at DESC';
        params = [filterStatus];
      }
      const res = await pgPool.query(sql, params);
      return res.rows;
    } else {
      const store = loadLocalStore();
      if (filterStatus && filterStatus !== 'all') {
        return store.billings.filter(b => b.status === filterStatus);
      }
      return store.billings;
    }
  },

  async getBillingById(id) {
    const engine = await getActiveEngine();
    if (engine === 'mongodb') {
      return await mongoDb.collection('billings').findOne({ id }, { projection: { _id: 0 } });
    }
    if (engine === 'postgresql') {
      const res = await pgPool.query('SELECT * FROM billings WHERE id = $1', [id]);
      return res.rows[0] || null;
    } else {
      const store = loadLocalStore();
      return store.billings.find(b => b.id === id) || null;
    }
  },

  async updateBilling(id, updates) {
    if (updates.status === 'paid' && !updates.paid_at) {
      updates.paid_at = new Date().toISOString();
    }

    const engine = await getActiveEngine();
    if (engine === 'mongodb') {
      const result = await mongoDb.collection('billings').findOneAndUpdate(
        { id },
        { $set: { ...updates, updated_at: new Date().toISOString() } },
        { returnDocument: 'after', projection: { _id: 0 } }
      );
      return result;
    }
    if (engine === 'postgresql') {
      const fields = [];
      const values = [];
      let idx = 1;
      for (const [key, val] of Object.entries(updates)) {
        fields.push(`${key} = $${idx}`);
        values.push(val);
        idx++;
      }
      fields.push(`updated_at = $${idx}`);
      values.push(new Date().toISOString());
      values.push(id);
      const sql = `UPDATE billings SET ${fields.join(', ')} WHERE id = $${idx + 1} RETURNING *;`;
      const res = await pgPool.query(sql, values);
      return res.rows[0];
    } else {
      const store = loadLocalStore();
      const billing = store.billings.find(b => b.id === id);
      if (!billing) return null;
      Object.assign(billing, updates, { updated_at: new Date().toISOString() });
      saveLocalStore(store);
      return billing;
    }
  },

  // ---------------------------------------------------------------------------
  // DASHBOARD AGGREGATES
  // ---------------------------------------------------------------------------
  async getDashboardStats() {
    const enquiries = await this.getEnquiries('all');
    const clients = await this.getClients();
    const billings = await this.getBillings('all');
    const learning = await this.getLearningOptins();

    const totalInvoiced = billings.reduce((sum, b) => sum + (parseFloat(b.total_amount) || 0), 0);
    const totalPaid = billings.filter(b => b.status === 'paid').reduce((sum, b) => sum + (parseFloat(b.total_amount) || 0), 0);
    const totalPending = billings.filter(b => b.status === 'pending').reduce((sum, b) => sum + (parseFloat(b.total_amount) || 0), 0);
    const newEnquiriesCount = enquiries.filter(e => e.status === 'new').length;

    return {
      overview: {
        total_clients: clients.length,
        total_enquiries: enquiries.length,
        new_enquiries: newEnquiriesCount,
        learning_subscribers: learning.length,
        total_invoiced_usd: totalInvoiced,
        total_collected_usd: totalPaid,
        total_pending_usd: totalPending
      },
      recent_enquiries: enquiries.slice(0, 5),
      recent_billings: billings.slice(0, 5)
    };
  }
};
