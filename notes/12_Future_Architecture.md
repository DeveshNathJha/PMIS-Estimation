# Future Architecture Strategy: Cloud & Database

*Current Status: The Prototype uses Flat Files (CSV) and Local Hosting.*
*Target Status: Enterprise-Grade Cloud Solution with Relational Database.*

This document outlines the roadmap for Phase 2: Production Readiness.

## 1. Database Integration Strategy

We **do not** need to create SQL files right now, but we must plan for the migration from `synthetic_project_data.csv` to a proper Relational Database Management System (RDBMS).

**Recommended Tech:** PostgreSQL (Open Source, Robust, JSON support)

### Logical Schema Design (Proposed)

Instead of one giant table, we will normalize the data into proper relationships:

1.  **Table: Projects**
    -   `project_id` (PK), `project_type`, `district_id`, `state`, `budget`, `status`
2.  **Table: Tasks** (WBS)
    -   `task_id` (PK), `project_id` (FK), `task_name`, `category`, `sequence_order`
3.  **Table: Execution_Log** (The Tracking Data)
    -   `log_id` (PK), `task_id` (FK), `planned_start`, `actual_start`, `planned_duration`, `actual_duration`, `vendor_id`, `delay_reason`
4.  **Table: Vendors**
    -   `vendor_id` (PK), `name`, `tier_level`, `performance_rating`

### Migration Path
1.  **Step 1:** Define models using an ORM like **SQLAlchemy** (Python).
2.  **Step 2:** Write a script to "seed" the database using our existing `synthetic_project_data.csv`.
3.  **Step 3:** Change `app/utils/data_loader.py` to fetch from SQL instead of `pd.read_csv`.

---

## 2. Cloud Deployment Strategy

Yes, for a real-world client (Government or Enterprise), you will need a Cloud Environment.

**Recommended Providers:**
1.  **AWS (Amazon Web Services):** Industry standard, huge ecosystem.
2.  **Azure (Microsoft):** Often preferred by large enterprises/govts already using Microsoft/Office 365.

### Deployment Architecture (Phase 2)

**A. The App (Streamlit)**
-   **Method:** Docker Container.
-   **Service:** AWS ECS (Fargate) or Azure App Service.
-   *Why?* Containerization allows the app to run exactly the same way on the cloud as it does on your laptop.

**B. The Brain (AI Model)**
-   **Method:** Model API (FastAPI) or Embedded.
-   *Recommendation:* Keep it embedded in the App Container for now (Model is small ~200MB). If it grows, move to a dedicated Model Server (TFServing/TorchServe).

**C. The Data**
-   **Service:** AWS RDS (PostgreSQL) or Azure SQL Database.
-   *Why?* Managed backups, security, and scaling without manual headaches.

---

## 3. Summary of Changes Needed

| Component | Current State | Future State | Action Required |
| :--- | :--- | :--- | :--- |
| **Data Storage** | `data/synthetic_project_data.csv` | **PostgreSQL Database** | Learn SQLAlchemy, Design Schema |
| **Hosting** | Local `localhost:8501` | **Azure App Service / AWS** | Dockerize Application (`Dockerfile`) |
| **Authentication** | None | **SSO / OAuth2** | Integrate with Client Active Directory |
