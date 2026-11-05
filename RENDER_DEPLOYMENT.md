# JVK Commerce — Render Backend & Deployment Guide

This guide details how to deploy the JVK Commerce website, API backend, and Billing Management system to **[Render](https://render.com/)**.

---

## Architecture Overview

* **Runtime**: Node.js (v18+) with Express.js.
* **Unified Serving**: The Express server simultaneously serves the high-performance client-facing static website (`/`), the Admin & Billing Dashboard (`/admin`), and the secure REST API (`/api/*`).
* **Database Engine**:
  * **Render Managed PostgreSQL**: Automatically utilized when `DATABASE_URL` is set.
  * **Standalone Disk Store**: Gracefully falls back to atomic local persistence (`data/jvk_store.json`) when running standalone or without an external database.
* **Authentication**: JWT (JSON Web Tokens) with 7-day session validity.

---

## 1-Click Deployment on Render (Blueprint)

Because this repository includes a [`render.yaml`](./render.yaml) blueprint specification, deployment takes under 2 minutes:

1. Log into your [Render Dashboard](https://dashboard.render.com/).
2. Click **New +** &rarr; Select **Blueprint**.
3. Connect your GitHub repository: `https://github.com/tysonsingh19929/JVK-Commerce-Website.git`.
4. Render will detect `render.yaml` and configure:
   * **Web Service**: `jvk-commerce-portal`
   * **Database**: `jvk-commerce-db` (Free PostgreSQL instance)
5. Click **Apply**.
6. Render will automatically build, provision the PostgreSQL tables, and launch your live URL (e.g. `https://jvk-commerce-portal.onrender.com`).

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
   * `DATABASE_URL`: *(Optional)* If you create a Render PostgreSQL database, paste its Internal Connection String here.
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
