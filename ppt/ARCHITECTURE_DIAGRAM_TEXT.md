# PMIS Architecture and Pipeline - Diagram Reference
> Based on the system architecture diagram. No file names - components described by function only.

---

## 1. CURRENT ARCHITECTURE (Alpha Prototype)

### Overview
Single-process Streamlit monolith. Everything runs in one Python process on localhost. No database, no API layer, no background workers. Single-threaded - one user at a time.

### Data Flow (Top to Bottom)

```
USER (Browser)
  |
  | HTTP request (localhost)
  v
STREAMLIT APPLICATION
  |
  |-- Loads central configuration (feature lists, district maps, project templates)
  |
  v
DATA LOADER
  |
  |-- Memory caching (loaded once, cached across sessions)
  |-- Reads: training data CSV (Pandas DataFrame)
  |-- Reads: serialised model artifact (joblib - 4 CatBoost + 1 Baseline models)
  |
  v
SIDEBAR / MODULE ROUTER
  |
  |-- User selects: Project Type, District, Vendor Tier, Land Type, etc.
  |-- User picks module: Pre-Start Estimator | Mid-Project Tracker | Risk Audit
  |
  +-------------------------------+-------------------------------+
  |                               |                               |
  v                               v                               v
PRE-START ESTIMATOR          MID-PROJECT TRACKER            RISK AUDIT
  |                               |                               |
  |-- Builds 8-feature vector     |-- Builds 8-feature vector     |-- Fetches WBS template
  |-- Calls CatBoost P10/P50/P90  |-- Calls CatBoost P50          |-- Runs CPM (Forward+Backward Pass)
  |-- Calls SHAP TreeExplainer    |-- Recalculates on param change |-- Monte Carlo simulation
  |-- Renders Plotly charts        |-- Renders Gantt-style timeline |-- Generates risk assessment per task
  |                               |                               |-- Renders critical path network
  v                               v                               v
STREAMLIT UI RENDER (browser)
  |
  |-- All rendering is synchronous, single-threaded
  |-- Session state holds user selections (lost on server restart)
  |-- No persistent storage - everything is in-memory
```

### ML Inference Pipeline (Current)

```
USER INPUT (from Streamlit sidebar widgets)
  |
  | 8 Features:
  |   1. Project_Type (categorical)
  |   2. District (categorical - mapped from state)
  |   3. LWE_Flag (binary - 0 or 1, from district lookup)
  |   4. Task_Category (categorical - Civil, Procurement, Technical, etc.)
  |   5. Land_Type (categorical - Govt Land, Donated, Tribal CNT/SPT)
  |   6. Vendor_Tier (integer - 1=premium, 2=mid-tier, 3=local)
  |   7. Planned_Duration (integer - baseline days from WBS template)
  |   8. Monsoon_Flag (binary - 0 or 1, derived from start month)
  |
  v
FEATURE VECTOR CONSTRUCTION
  |
  | pd.DataFrame with 1 row, 8 columns
  | Categorical features handled natively by CatBoost (cat_features parameter)
  |
  v
CATBOOST INFERENCE (3 models from serialised artifact)
  |
  |-- P10 model  -->  Optimistic estimate
  |-- P50 model  -->  Median expected duration
  |-- P90 model  -->  Conservative planning buffer
  |
  | Each model: CatBoost Quantile Regressor
  | Training: 80/20 split, fixed random seed
  |
  v
OUTPUT: Duration_Multiplier (float)
  |
  | Actual_Duration = Planned_Duration x Duration_Multiplier
  |
  v
POST-PROCESSING
  |
  +-- SHAP TreeExplainer on P50 model
  |     |-- Global feature importance (bar chart)
  |     |-- Per-prediction force plot
  |     |-- Identifies top delay drivers (typically Vendor_Tier, Monsoon_Flag)
  |
  +-- CPM Integration (in Risk Audit module)
  |     |-- Each task gets P50 predicted duration
  |     |-- Forward pass: Early Start, Early Finish
  |     |-- Backward pass: Late Start, Late Finish
  |     |-- Critical path = tasks with zero slack
  |
  +-- Risk Assessment
        |-- Compares Predicted vs Planned per task
        |-- If delay > 15% of planned: checks LWE_Flag, Monsoon_Flag, Land_Type, Task_Category
        |-- Outputs root cause string: e.g. "DELAY: LWE Logistics Friction + Monsoon Slowdown (+28 days)"
```

### Training Pipeline (Offline)

```
SYNTHETIC DATA GENERATION
  |
  |-- Uses central configuration: state profiles, district maps, project templates
  |-- Generates ~10,000 task records with realistic friction multipliers
  |-- Outputs: training data CSV
  |
  v
MODEL TRAINING
  |
  |-- Reads: training data CSV
  |-- Feature columns: 8 features from central configuration
  |-- Target: Duration_Multiplier (Actual/Planned ratio)
  |-- Train/Test split: 80/20, fixed random seed
  |
  |-- Trains 3 CatBoost Quantile Regressors:
  |     - alpha=0.1 (P10 - optimistic)
  |     - alpha=0.5 (P50 - median)
  |     - alpha=0.9 (P90 - conservative)
  |
  |-- Trains 1 BayesianRidge baseline (scikit-learn) for comparison
  |
  |-- Logs metrics: MAE, R2, RMSE for all 4 models
  |
  |-- SHAP analysis on P50 model (TreeExplainer)
  |
  |-- Bundles everything into model artifact dict:
  |     {
  |       'models': {0.1: catboost_p10, 0.5: catboost_p50, 0.9: catboost_p90},
  |       'baseline_model': bayesian_ridge,
  |       'metrics': {...},
  |       'district_map': {...}
  |     }
  |
  |-- Serialises via joblib (~4 MB)
```

### Current Constraints
- Single-threaded: heavy operations (Monte Carlo, CPM) block UI for all users
- No concurrent access: one user at a time
- No database: session state + CSV files only, server restart loses everything
- No input validation beyond Streamlit widget constraints
- No API: frontend and backend are the same process
- No CI/CD: one CPM smoke test exists, no Pytest coverage
- Model versioning: file-system based (timestamped folders), no MLflow

### Active Tech Stack
- Python 3.11
- Streamlit
- CatBoost
- Scikit-learn
- SHAP
- Pandas / NumPy
- Matplotlib
- Plotly
- NetworkX (for CPM graph visualisation)
- Graphviz
- FPDF (PDF report generation)
- OpenPyXL
- SciPy

---

## 2. PLANNED ARCHITECTURE (Phase 2 / Phase 3)

### Phase 2: API Decoupling (Next planned sprint)

```
BROWSER / FRONTEND CLIENT
  |
  | HTTP / REST API calls (JSON)
  |
  v
FASTAPI + UVICORN (ASGI Server)
  |
  |-- Pydantic models validate every request payload
  |-- Invalid data rejected with 422 before reaching inference
  |-- async/await enables concurrent request handling
  |-- Multiple workers via Uvicorn
  |
  |-- Endpoints (planned):
  |     POST /predict          --> Single task P10/P50/P90 prediction
  |     POST /predict/batch    --> Batch prediction for full WBS
  |     POST /cpm              --> CPM calculation on predicted durations
  |     POST /shap             --> SHAP explanation for a prediction
  |     GET  /health           --> Health check
  |     GET  /model/info       --> Model metadata and metrics
  |
  v
CATBOOST INFERENCE (same 3 models, loaded at startup)
  |
  |-- Models loaded once at FastAPI startup (lifespan event)
  |-- Same serialised model artifact
  |-- Same 8-feature schema
  |
  v
RESPONSE (JSON)
  |
  |-- { "p10": 25.2, "p50": 31.7, "p90": 44.1, "multiplier": {...} }
```

Phase 2 also includes:
- Docker containerisation
- Pytest unit tests for all inference endpoints
- Streamlit becomes a thin HTTP client (calls FastAPI instead of direct function calls)

### Phase 3: Async Scaling and Persistence

```
BROWSER / FRONTEND CLIENT
  |
  v
FASTAPI + UVICORN (ASGI)
  |
  |-- Pydantic validation (same as Phase 2)
  |
  +---------------------------+---------------------------+
  |                           |                           |
  v                           v                           v
CATBOOST INFERENCE       CELERY + REDIS              POSTGRESQL
(sync - fast tasks)      (async - heavy tasks)        (persistent storage)
  |                           |                           |
  |-- P10/P50/P90 predict     |-- Monte Carlo simulation  |-- Project records
  |-- SHAP explain            |-- Batch CPM analysis      |-- Prediction history
  |-- < 100ms response        |-- 500-node simulations    |-- Session tokens
  |                           |-- Returns task_id         |-- User preferences
  |                           |-- Client polls for result |-- Feedback ledger
  |                           |                           |
  v                           v                           v
         All containerised via Docker Compose
         |
         |-- Container 1: FastAPI app
         |-- Container 2: Celery worker(s)
         |-- Container 3: Redis (message broker)
         |-- Container 4: PostgreSQL
         |
         Ready for deployment to AWS ECS / Azure AKS
```

Phase 3 also includes:
- MLflow for experiment tracking, model versioning, data drift monitoring
- ERP data ingestion: map real historical project data to the 8-feature schema, retrain
- Feedback loop: incorrect predictions logged, accumulated, included in next retrain cycle

### Phase 3 Tech Additions (not yet installed)
- FastAPI + Uvicorn (ASGI)
- Pydantic (input validation)
- Docker + docker-compose
- Pytest
- Celery + Redis (async task queue)
- PostgreSQL (persistent storage)
- MLflow (experiment tracking)

---

## 3. SUMMARY COMPARISON

| Aspect | Current (Alpha) | Target (Phase 2/3) |
|--------|-----------------|---------------------|
| Frontend | Streamlit (UI + logic combined) | Thin client (Streamlit or other, calls API) |
| Backend | None (same process as frontend) | FastAPI + Uvicorn (async ASGI) |
| Input Validation | Streamlit widget constraints only | Pydantic data contracts (422 rejection) |
| ML Inference | Direct function call, synchronous | REST API endpoint, concurrent |
| Heavy Computation | Blocks UI thread (8-12 sec for Monte Carlo) | Celery background workers, non-blocking |
| Data Storage | Session state + CSV files (lost on restart) | PostgreSQL (persistent, multi-user) |
| Deployment | localhost only, manual start | Docker containers, cloud-deployable |
| Concurrency | Single-threaded, one user | Multi-worker, concurrent requests |
| Testing | 1 smoke test, no Pytest | Pytest coverage for all endpoints |
| Model Versioning | Timestamped artifact folders | MLflow experiment tracking |
| Monitoring | Application log (Python logging module) | MLflow + structured logging |
