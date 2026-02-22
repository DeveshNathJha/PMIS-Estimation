# Strategic Project Analytics: Context-Aware Risk Engine

## 1. Project Overview

**Strategic Project Analytics (SPA)** is an advanced predictive module designed to integrate with Project Management Information Systems (PMIS). It bridges the gap between *planned* timelines and *ground realities* by using historical data to forecast delays caused by friction factors like terrain, security risks, and implementation capability.

### Business Context
Standard Gantt charts often fail in complex geographies where "friction" (e.g., LWE risks, hilly terrain, monsoon) causes significant invisible delays. This engine quantifies that friction.

### Module Objectives
- **Predictive Intelligence:** Move from deterministic scheduling to probabilistic forecasting (P10/P50/P90).
- **Risk Quantification:** Isolate impacts of vendor capability, security risks, and weather.
- **Decision Support:** Enable "What-If" scenarios for vendor selection and risk mitigation.

---

## 2. Project Structure

The project follows a modular, production-ready architecture.

PMIS/
├── config.py                     # Central Configuration Hub
├── pmisapp.py                    # Application Entry Point
├── app/                          # Core Application Module
│   ├── main.py                   # App Orchestrator
│   ├── ui/                       # User Interface Modules
├── data/                         # Data Storage
│   ├── synthetic_project_data.csv
│   └── pmis_model.pkl
└── scripts/                      # Utility Scripts
    ├── data_generation.py        # Synthetic Data Engine
    ├── train_production_model.py # Production Training Pipeline
    └── model.py                  # Interactive Notebook Generator

### Key Components

#### 1. Configuration (`config.py`)
- **Purpose:** Source of Truth for all constants, file paths, and model hyperparameters. Centralization ensures consistency across training and inference.

#### 2. Data Generation (`data_generation.py`)
- **Purpose:** simulating realistic project history to train the AI.
- **Mechanism:** Uses a "Physics Engine" to calculate friction based on terrain, security flags, and vendor tiers.

#### 3. Model Training (`train_production_model.py`)
- **Purpose:** Trains the production **CatBoost Regressor** models.
- **Outputs:** A serialized artifact (`pmis_model.pkl`) containing the P10, P50, and P90 models + vectorizers.

#### 4. Application Core (`app/`)
- **`app/main.py`**: Orchestrates the application flow.
- **`app/ui/estimator.py`**: The "Pre-Start Estimator" module for planning phase predictions.
- **`app/ui/tracker.py`**: The "Mid-Project Tracker" for re-forecasting based on actual progress.
- **`app/ui/risk_audit.py`**: The "Risk Audit" module for post-mortem analysis.

---

## 3. End-to-End Workflow

1.  **User Input:** Select Project Type, District, and Vendor Tier.
2.  **Preprocessing:** Map District to latent risk features (Terrain, LWE) and calculate Seasonality flags.
3.  **Inference:**
    *   **P10 (Optimistic):** Best-case scenario.
    *   **P50 (Realistic):** Most likely outcome.
    *   **P90 (Pessimistic):** Risk scenario.
4.  **CPM Analysis:** Sequence tasks using P50 estimates to derive the Critical Path.
5.  **Output:** Visual network diagrams, PDF reports, and executive risk summaries.

---

## 4. Limitations & Future Scope

### Limitations
1.  **Synthetic Data Bias:** Current model is trained on synthetic data. Real-world validation is required.
2.  **Static Logic:** The WBS templates are static; dynamic dependency modeling is a future enhancement.

### Future Roadmap
1.  **Database Integration:** Replace CSVs with PostgreSQL.
2.  **MLOps:** Containerize with Docker and implement MLflow for model tracking.
3.  **Real-time Integration:** Connect to live ERP systems for automated actuals data.

---

## 5. Installation

```bash
pip install -r requirements.txt
python data_generation.py  # Generate Data
python train_production_model.py  # Train Model
streamlit run pmisapp.py  # Launch App
```