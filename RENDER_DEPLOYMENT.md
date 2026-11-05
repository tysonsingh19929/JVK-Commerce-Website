# JVK Commerce — Render Backend & Deployment Guide

This guide details how to deploy the JVK Commerce website, API backend, and Billing Management system to **[Render](https://render.com/)**, connected to **MongoDB Atlas**.

---

## Architecture Overview

* **Runtime**: Node.js (v18+) with Express.js.
* **Unified Serving**: The Express server simultaneously serves the high-performance client-facing static website (`/`), the Admin & Billing Dashboard (`/admin`), and the secure REST API (`/api/*`).
* **Database Engine**:
  * **MongoDB Atlas (Primary)**: Seamlessly connects when `MONGODB_URI` (or `MONGO_URI`) is set. Stores all enquiries, learning subscribers, client directories, and billing invoices in cloud document collections with automated indexes.
  * **Render Managed PostgreSQL (Alternative)**: Automatically utilized when `DATABASE_URL` is set (if MongoDB URI is not set).
  * **Standalone Disk Store (Fallback)**: Gracefully falls back to atomic local persistence (`data/jvk_store.json`) when running standalone or offline.
* **Authentication**: JWT (JSON Web Tokens) with 7-day session validity.

---

## Connecting MongoDB Atlas to Render

### Step 1: Create Free MongoDB Cluster in MongoDB Atlas
1. In [cloud.mongodb.com](https://cloud.mongodb.com), complete organization creation:
   * Leave Security/Operations email optional or enter your email.
   * Click **Create Organization**.
2. Click **Create Project** (e.g. name it `JVK-Commerce`).
3. Click **Deploy Database** &rarr; select **M0 (Free forever)** tier &rarr; Click **Create**.

### Step 2: Set Username, Password & Network Access
1. Under **Quickstart / Security**:
   * **Username**: e.g. `jvkadmin`
   * **Password**: Click **Autogenerate Secure Password** or set a strong password (copy and save this password!).
   * Click **Create User**.
2. Under **Network Access** / **Where would you like to connect from?**:
   * Select **Allow Access from Anywhere** (`0.0.0.0/0`).
   * *(This is required so Render's cloud servers can connect to your MongoDB cluster)*.
   * Click **Add Entry**.

### Step 3: Get Connection String
1. Click **Connect** (or go to Database Deployments &rarr; click **Connect** on your cluster).
2. Choose **Drivers** &rarr; Driver: **Node.js**.
3. Copy the connection string:
   ```
   mongodb+srv://jvkadmin:<password>@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0
   ```
4. Replace `<password>` with the password you created in Step 2.

### Step 4: Add to Render Environment Variables
1. Go to your [Render Dashboard](https://dashboard.render.com).
2. Click your Web Service: `jvk-commerce-portal`.
3. Go to **Environment** in the left menu.
4. Click **Add Environment Variable**:
   * **Key**: `MONGODB_URI`
   * **Value**: *(paste your complete connection string)*
5. Click **Save Changes**. Render will automatically redeploy and connect to MongoDB Atlas!

---

## 1-Click Deployment on Render (Blueprint)

Because this repository includes a [`render.yaml`](./render.yaml) blueprint specification, deployment takes under 2 minutes:

1. Log into your [Render Dashboard](https://dashboard.render.com/).
2. Click **New +** &rarr; Select **Blueprint**.
3. Connect your GitHub repository: `https://github.com/tysonsingh19929/JVK-Commerce-Website.git`.
4. Render will detect `render.yaml` and configure your Web Service.
5. Click **Apply**.
6. Render will automatically build and launch your live URL (e.g. `https://jvk-commerce-portal.onrender.com`).

---

## Manual Deployment on Render (Alternative)

If you prefer to configure a standard Web Service manually:

1. In Render, click **New +** &rarr; **Web Service**.
2. Connect `https://github.com/tysonsingh19929/JVK-Commerce-Website.git`.
3. Set the following settings:
   * **Name**: `jvk-commerce-portal`
   * **Language / Environment**: `Node`
   * **Branch**: `main`
   * **Build Command**: `npm install`
   * **Start Command**: `node server.js`
   * **Plan**: `Free`
4. Add **Environment Variables**:
   * `NODE_ENV`: `production`
   * `ADMIN_USERNAME`: `admin`
   * `ADMIN_PASSWORD`: Your chosen secure password (e.g. `JVKAdmin2026!`)
   * `JWT_SECRET`: A random string (e.g. `jvk_jwt_secret_render_production_2026`)
   * `MONGODB_URI`: Your MongoDB connection string
5. Click **Deploy Web Service**.

---

## Admin Portal & Billing Dashboard

Once deployed, navigate to:
```
https://<your-render-app-url>/admin
```

* **Default Username**: `admin`
* **Default Password**: `JVKAdmin2026!` *(or the password set in your Render environment variables)*

### Capabilities Inside the Admin Portal:
1. **Overview**: Live revenue tracking (Total Invoiced, Total Collected, Pending Balance), active client count, and new leads.
2. **Enquiries**: View, manage, and update the status of contact submissions (*New*, *In Progress*, *Contacted*, *Qualified*, *Closed*). Direct 1-click WhatsApp follow-up button to chat with the lead.
3. **Clients**: Register brand accounts, primary contact details, VAT/Tax numbers, locations, and active marketplaces (Amazon, Noon, Walmart, etc.).
4. **Invoices & Billings**:
   * Generate formal invoices with invoice number, line items, currency (USD, AED, EUR, GBP), issue date, and due date.
   * Update payment status (*Pending* &rarr; *Paid*).
   * Print or export clean invoice summary cards.
5. **Learning Subscribers**: View all work emails and WhatsApp numbers from the Operator Academy opt-in form, with 1-click **Export to CSV**.

---

## API Endpoints Reference

Complete OpenAPI 3.1 specification available at [`openapi.yaml`](./openapi.yaml) and runnable Postman collection at [`postman_collection.json`](./postman_collection.json).

| Method | Endpoint | Access | Purpose |
|---|---|---|---|
| `GET` | `/api/health` | Public | Health check and database engine status |
| `POST` | `/api/enquiries` | Public | Submit client enquiry from website |
| `GET` | `/api/enquiries` | Admin | List all leads (filterable by status) |
| `PATCH`| `/api/enquiries/:id` | Admin | Update status or notes |
| `POST` | `/api/learning` | Public | Submit Operator Academy opt-in |
| `GET` | `/api/learning` | Admin | List learning subscribers |
| `GET` | `/api/clients` | Admin | List all brand client accounts |
| `POST` | `/api/clients` | Admin | Create a new client profile |
| `GET` | `/api/clients/:id` | Admin | View client details and invoices |
| `GET` | `/api/billings` | Admin | List all invoices and billings |
| `POST` | `/api/billings` | Admin | Create a new billing record / invoice |
| `PATCH`| `/api/billings/:id` | Admin | Update billing status (e.g. mark Paid) |
| `GET` | `/api/dashboard/stats` | Admin | Real-time financial and operational metrics |
| `POST` | `/api/auth/login` | Public | Admin login (returns JWT token) |
