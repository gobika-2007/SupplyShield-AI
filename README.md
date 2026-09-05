

# SupplyShield AI

## AI-Powered Supply Chain Disruption Response Assistant

SupplyShield AI is an intelligent decision-support application designed to help distributors respond to supply-chain disruptions quickly and reliably.

The system converts unstructured disruption notices such as supplier shutdowns, carrier delays, warehouse incidents, and operational disruptions into structured intelligence. It then traces affected supply-chain entities, identifies customer orders at risk, evaluates inventory availability, prioritizes impacted orders, and recommends response actions.

The system combines Generative AI for understanding disruption notices with deterministic business logic for impact analysis and decision support.

---

## Problem Statement

### PS08 — Supply Chain: Disruption Response Assistant

A distributor receives an unstructured disruption notice, such as:

- Supplier production halt
- Carrier delay
- Warehouse incident
- Factory shutdown
- Operational disruption

The distributor needs to quickly understand:

1. What happened?
2. Which suppliers, carriers, warehouses, products, or shipments are affected?
3. Which inventory is at risk?
4. Which customer orders are affected?
5. Which orders require immediate attention?
6. What response options are available?
7. Which action should be considered?
8. What evidence supports the impact assessment?

SupplyShield AI addresses this complete workflow through an explainable, human-in-the-loop decision-support system.

---

# Solution Overview

SupplyShield AI follows this pipeline:

Unstructured Disruption Notice
        ↓
Gemini AI Extraction
        ↓
Structured Disruption Facts
        ↓
Entity Mapping
        ↓
Deterministic Impact Engine
        ↓
Orders / Inventory / Shipments at Risk
        ↓
Priority Assessment
        ↓
Action Option Comparison
        ↓
Recommended Response
        ↓
Human Approval / Review
        ↓
Evidence & Traceability

---

# Key Features

## 1. AI Disruption Notice Understanding

Users can enter an unstructured disruption notice in natural language.

Example:

> Nova Components Ltd has announced a complete production shutdown due to a major factory incident. All shipments of Motor Controller products are expected to be delayed for 10 days.

Gemini extracts structured information including:

- Disruption type
- Supplier
- Carrier
- Warehouse
- Products
- Product codes
- Shipments
- Duration
- Severity language
- Raw facts
- Uncertain fields
- No-impact signals

---

## 2. Supply Chain Impact Analysis

After extraction, SupplyShield AI deterministically maps the disruption to local supply-chain data.

It identifies:

- Affected suppliers
- Affected products
- Affected shipments
- Affected inventory
- Customer orders
- Available stock
- Reserved stock
- Shortages
- Order deadlines
- Order priorities

---

## 3. Order Risk Prioritization

Affected orders are ranked using deterministic business rules.

Priority levels include:

- Critical
- High
- Medium
- Low

Orders with higher business priority and earlier deadlines receive greater attention.

---

## 4. Inventory Risk Detection

The system calculates usable inventory using:

Available Stock = Total Inventory - Reserved Inventory

It then compares available inventory with affected customer demand to identify shortages.

---

## 5. Action Planning

SupplyShield AI evaluates multiple response options:

### Expedite

Move affected supply through a faster route at potentially higher cost.

### Reallocate

Use available inventory from another suitable supply-chain location.

### Part-Ship

Ship the currently available quantity while waiting for the remaining supply.

### Prioritize

Prioritize critical customer orders over lower-priority orders.

### Notify Customers

Inform affected customers about expected delays or partial fulfillment.

### Wait

Continue monitoring when the disruption does not justify immediate intervention.

The system recommends an action but does not automatically execute operational changes.

---

# Human-in-the-Loop Safety

SupplyShield AI is designed as a decision-support system rather than an autonomous execution system.

Human review is triggered when:

- Supplier cannot be identified
- Product cannot be identified
- Carrier or warehouse cannot be mapped
- Information is ambiguous
- Important information conflicts
- Insufficient data is available
- No suitable response can be determined
- AI extraction fails
- An unusual disruption is detected

Instead of inventing missing information, the system escalates the case for human review.

---

# Explainability and Traceability

Every impact assessment is connected to supply-chain data.

The system provides evidence references for:

- Supplier records
- Product records
- Shipment records
- Inventory records
- Customer orders
- Deadlines
- Quantities
- Priority levels

This makes the recommendation auditable and allows an analyst to understand why an order was classified as at risk.

---

# Architecture

Web Frontend
HTML / CSS / JavaScript
        ↓
FastAPI Backend
        ↓
┌──────────────────────────────┐
│ Gemini AI Extraction         │
│ Deterministic Impact Engine  │
│ Deterministic Action Planner │
└──────────────────────────────┘
        ↓
Local Supply Chain Data

---

# Technology Stack

### Frontend

- HTML5
- CSS3
- JavaScript

### Backend

- Python
- FastAPI
- Uvicorn

### AI

- Google Gemini API
- Gemini generative model

### Data

- Local JSON data
- Deterministic rule-based analysis

### Authentication

- FastAPI authentication routes
- Local user storage
- SHA-256 password hashing

### Development

- Visual Studio Code
- Git
- GitHub

---

# Project Structure

SupplyShield-AI/
│
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── backend/
│   ├── routes/
│   │   ├── auth_routes.py
│   │   ├── case_router.py
│   │   ├── dashboard_routes.py
│   │   └── disruption_routes.py
│   │
│   └── services/
│       ├── action_planner.py
│       ├── auth_service.py
│       ├── case_store.py
│       ├── gemini_extractor.py
│       └── impact_engine.py
│
├── data/
│   ├── cases.json
│   ├── supply_chain.json
│   └── users.json
│
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── app.js
│
└── tests/

---

# AI Workflow

The AI layer is responsible for interpreting natural-language disruption notices.

Example:

BlueDart Logistics has reported a 3-day carrier delay affecting the shipment of Motor Controller products from Nova Components Ltd.

The AI extracts information such as:

- Disruption Type: Carrier Delay
- Carrier: BlueDart Logistics
- Supplier: Nova Components Ltd
- Product: Motor Controller
- Duration: 3 days

The extracted entities are then passed to deterministic backend logic.

The deterministic layer checks the local supply-chain records and calculates the actual operational impact.

This separation reduces the risk of hallucinated business decisions.

---

# Demo Scenarios

## Scenario 1 — Major Supplier Shutdown

Nova Components Ltd has announced a complete production shutdown due to a major factory incident. All shipments of Motor Controller products are expected to be delayed for 10 days.

Expected behavior:

- Supplier identified
- Product identified
- Shipments identified
- Orders at risk identified
- Shortage calculated
- Critical orders prioritized
- Response actions recommended

---

## Scenario 2 — Carrier Delay

BlueDart Logistics has reported a 3-day carrier delay affecting the shipment of Motor Controller products from Nova Components Ltd.

Expected behavior:

- Carrier identified
- Supplier identified
- Product identified
- Related shipment identified
- Downstream impact calculated

---

## Scenario 3 — Warehouse Incident

Chennai Central Warehouse has suffered a flooding incident. Warehouse operations are temporarily suspended.

Expected behavior:

- Warehouse identified
- Related inventory identified
- Related orders identified
- Critical impact detected
- Response plan generated
- Human approval required

---

## Scenario 4 — Unknown Supplier

UnknownTech Industries has completely stopped production because of a major factory incident. All shipments are expected to be delayed for 10 days.

Expected behavior:

HUMAN REVIEW

The system does not invent a supplier mapping when the entity is absent from the local data.

---

## Scenario 5 — No Impact

There is a temporary weather advisory near a supplier, but all shipments and warehouse operations are continuing normally with no expected delays.

Expected behavior:

NO IMPACT

NO ACTION REQUIRED

---

# API Endpoints

| Endpoint | Method | Purpose |
|---|---|---|
| `/api/health` | GET | Backend health check |
| `/api/auth/signup` | POST | Create user account |
| `/api/auth/login` | POST | Authenticate user |
| `/api/dashboard` | GET | Dashboard information |
| `/api/disruption/analyze` | POST | Analyze disruption notice |
| `/api/disruption/{case_id}/impact` | GET | Retrieve impact analysis |
| `/api/disruption/{case_id}/actions` | GET | Retrieve action plan |
| `/api/cases` | GET | Retrieve analyzed cases |
| `/api/cases/{case_id}` | GET | Retrieve individual case |
| `/api/orders/at-risk` | GET | Retrieve orders at risk |
| `/api/evidence/{case_id}` | GET | Retrieve evidence |

---

# Installation

## 1. Clone the repository

git clone https://github.com/gobika-2007/SupplyShield-AI.git

cd SupplyShield-AI

## 2. Create a virtual environment

python -m venv venv

## 3. Activate the virtual environment

Windows:

.\venv\Scripts\Activate.ps1

## 4. Install dependencies

pip install -r requirements.txt

## 5. Configure Gemini API

Create a local `.env` file:

GEMINI_API_KEY=YOUR_API_KEY

Do not commit `.env` to GitHub.

## 6. Start the application

python app.py

Open:

http://localhost:8000

---

# Security

API credentials are stored locally in environment variables.

The `.env` file is excluded from Git using `.gitignore`.

No API keys or credentials should be included in the public repository.

---

# Design Principles

### 1. AI for Interpretation

Use Generative AI where natural-language understanding is required.

### 2. Deterministic Business Logic

Use backend rules for calculations and operational impact.

### 3. Evidence-Based Decisions

Impact claims are traceable to available supply-chain data.

### 4. Human-in-the-Loop

Uncertain or unsupported situations are escalated instead of guessed.

### 5. Decision Support

The system recommends actions while leaving final operational decisions to authorized humans.

---

# Future Enhancements

- Real-time ERP integration
- Live carrier tracking
- Advanced inventory optimization
- Cost-aware optimization
- Supplier risk scoring
- Historical disruption analytics
- Automated notification workflows
- Multi-warehouse reallocation optimization
- Role-based enterprise access control

---

# Project Status

**Working Prototype**

The current prototype supports:

- User registration and login
- Natural-language disruption analysis
- AI-assisted information extraction
- Supply-chain entity mapping
- Impact assessment
- Inventory and order risk analysis
- Priority-based order ranking
- Response option comparison
- Human-review escalation
- Evidence and traceability
- Case history
- Dashboard visualization

---

# Team

**Project:** SupplyShield AI

**Problem Statement:** PS08 — Supply Chain: Disruption Response Assistant

**Track:** NexusTiq24

---

# Repository

GitHub: https://github.com/gobika-2007/SupplyShield-AI
