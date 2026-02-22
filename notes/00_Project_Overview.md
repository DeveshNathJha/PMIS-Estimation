# Project Overview & Architecture

## What is this project?
The **PMIS (Project Management Information System) Solution** is an AI-powered analytics platform designed to predict project delays in complex environments (like Indian infrastructure). It moves beyond static Gantt charts by incorporating "friction factors" like terrain, monsoon, and security risks into its estimates.

## Directory Structure
```
PMIS/
├── config.py                     # Central Configuration Hub
├── pmisapp.py                    # Application Entry Point
├── app/                          # Core Application Module
│   ├── main.py                   # App Orchestrator
│   ├── core/                     # Business Logic
│   ├── ui/                       # User Interface Views
│   └── utils/                    # Data Loading Utilities
├── data/                         # Data Storage (CSV, Models)
└── scripts/                      # Offline Scripts (Training, Data Gen)
```

## Module Breakdown

| Module | File | Purpose |
| :--- | :--- | :--- |
| **Configuration** | `config.py` | Stores all constants, paths, and hyperparameters. |
| **Entry Point** | `pmisapp.py` | The launcher script for Streamlit. |
| **Orchestrator** | `app/main.py` | Handles navigation, sidebar, and page routing. |
| **Logic Core** | `app/core/logic.py` | Contains the math: CPM, Risk Assessment, WBS generation. |
| **UI Components** | `app/ui/*.py` | Renders the specific screens (Estimator, Tracker, Audit). |
| **Data Generator** | `scripts/data_generation.py` | Creates synthetic history for training. |
| **Model Trainer** | `scripts/train_production_model.py` | Trains the CatBoost AI model. |
