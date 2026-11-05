# JVK Commerce — Autonomous E-Commerce Specialist Automation System (AESAS)

A production-grade, multi-agent autonomous framework engineered to execute and automate all **15 Specialist Service Areas** across Amazon, Walmart, eBay, Noon, TikTok Shop, and Shopify.

Powered by a hybrid intelligence architecture:
- **Nous Hermes 3**: Low-latency tool-calling, JSON schema extraction, and deterministic execution.
- **Claude 3.7 / Frontier**: High-converting listing copywriting, visual A+ blueprints, and formal Plan of Action (POA) appeals.
- **DeepSeek-R1 / Quant**: Mathematical PPC bid elasticity ($\text{Optimal Bid} = \text{Target ACoS} \times AOV \times CR$), FBA inventory forecasting, and financial unit-economics balance sheets.

---

## 15 Specialist Service Modules

| ID | Module Name | Specialist Agent Class | Primary Intelligence Engine | Focus |
|:---|:---|:---|:---|:---|
| **1** | Seller & Vendor Central Setup | [`AccountSetupAgent`](file:///automation/agents/account_setup_agent.py) | **Hermes 3** | Onboarding, entity tax compliance (W-8BEN/VAT/IOSS), shipping templates, DF EDI |
| **2** | Marketplace Account Management | [`MarketplaceAccountManagerAgent`](file:///automation/agents/account_manager_agent.py) | **Hermes 3** | 24/7 case log triage, daily operational checklist, multi-region heartbeat |
| **3** | Product Listing Creation & Opt. | [`ListingOptimizerAgent`](file:///automation/agents/listing_optimizer_agent.py) | **Claude 3.7 / Hermes** | Byte-constrained titles, 5 benefit bullets, <=249 byte backend search terms |
| **4** | SEO & Keyword Research | [`SEOKeywordAgent`](file:///automation/agents/seo_keyword_agent.py) | **DeepSeek-R1 / Hermes** | Reverse-ASIN harvesting, search volume clustering, SQP gap analysis |
| **5** | PPC Campaign Management | [`PPCManagerAgent`](file:///automation/agents/ppc_manager_agent.py) | **DeepSeek-R1** | Automated search term harvesting, target ACoS bid math, negative keyword isolation |
| **6** | A+ Content & Brand Store | [`APlusContentAgent`](file:///automation/agents/aplus_content_agent.py) | **Claude 3.7** | Modular layouts, cross-sell comparison tables, generative visual asset prompts |
| **7** | Catalog & Variations | [`CatalogVariationAgent`](file:///automation/agents/catalog_variation_agent.py) | **Hermes 3** | Parent-child Twister trees, Error 8572/5665/8007 diagnostics and remediation |
| **8** | Inventory & FBA Forecasting | [`InventoryForecasterAgent`](file:///automation/agents/inventory_forecaster_agent.py) | **DeepSeek-R1** | Reorder Points (ROP), Days of Supply (DOS), Aged Surcharge fee prevention |
| **9** | FBA, FBM & Seller Flex | [`FulfillmentAgent`](file:///automation/agents/fulfillment_agent.py) | **Hermes 3** | Send-to-Amazon inbound manifests, FBM rate shopping, Seller Flex cutoffs |
| **10** | Order & Customer Service | [`CustomerCareAgent`](file:///automation/agents/customer_care_agent.py) | **Hermes 3** | Review solicitation triggers (5-30 days), sentiment analysis, Safe-T claims |
| **11** | Account Health & Performance | [`AccountHealthAgent`](file:///automation/agents/account_health_agent.py) | **Claude 3.7** | ODR/LDR/VTR tracking, policy violation detection, 3-part Root Cause POA appeals |
| **12** | Promotions, Deals & Pricing | [`RepricerPromoAgent`](file:///automation/agents/repricer_promo_agent.py) | **Hermes 3** | Algorithmic Buy Box repricing with margin floors, Prime Exclusive Discounts |
| **13** | Sales Growth & Business Dev | [`GrowthExpansionAgent`](file:///automation/agents/growth_expansion_agent.py) | **DeepSeek-R1** | International expansion (UK/EU/UAE/AU), landed cost models, B2B quantity tiers |
| **14** | Marketplace Audits & Reporting | [`MarketplaceAuditsReportingAgent`](file:///automation/agents/audit_reporting_agent.py) | **DeepSeek-R1** | Consolidated 360 P&L, TACoS vs ACoS balance, Listing Quality Score (LQS) |
| **15** | Brand Registry & Support | [`BrandRegistryAgent`](file:///automation/agents/brand_registry_agent.py) | **Claude 3.7** | Trademark protection, Report a Violation (RAV) filing, hijacker elimination |

---

## Quickstart & CLI Commands

### 1. View all 15 Specialist Agents
```bash
python -m automation.cli list
```

### 2. Run an Individual Specialist Agent
```bash
# Run Listing Optimizer (Area #3)
python -m automation.cli run 3

# Run PPC Bid Optimizer (Area #5)
python -m automation.cli run 5

# Run Account Health & POA Generator (Area #11)
python -m automation.cli run 11
```

### 3. Run the Full 360-Degree Account Audit Swarm
Executes all core specialist agents in sequence and saves structured audit logs to `automation/data/`:
```bash
python -m automation.cli audit
```

### 4. Run the Automated Test Suite
```bash
python -m unittest automation.tests.test_agents
```
