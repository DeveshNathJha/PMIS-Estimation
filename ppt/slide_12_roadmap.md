# Slide 12: Technical Execution Roadmap
## Phased transition from Alpha prototype to production-ready connected system

---

### Slide Content

**Phase 01: Logic Validation - COMPLETE**
- Functional Streamlit monolith with full UI flow and interactive outputs delivered.
- CatBoost Quantile Regression for P10/P50/P90 inference confirmed stable on synthetic dataset.
- SHAP integrated and correctly identifying Vendor Tier and Monsoon as primary friction drivers.
- Logging, dependency pinning, and dynamic inference substitution completed.

**Phase 02: Architecture Decoupling - NEXT PHASE**
- Stand up FastAPI + Uvicorn async backend absorbing all ML inference and data transformation calls.
- Strict HTTP schema validation via Pydantic: reject malformed payloads before reaching inference engine.
- Package frontend and API containers for environment-agnostic deployment.
- Establish automated unit test coverage for all inference endpoints and data transforms.

**Phase 03: Async Scaling and ERP Data - EVALUATING**
- Offload heavy Monte Carlo and CPM computations to async Celery worker processes.
- Replace in-memory session state and CSVs with a persistent relational PostgreSQL schema.
- Map, normalise, and ingest real historical project execution data from ERP to trigger true-variance model retrain.
- Formal experiment tracking, model versioning, and data drift monitoring via MLflow.

**Key Insight:** Phase 2 FastAPI decoupling is the critical-path milestone. Every Phase 3 capability - async scaling, ERP data, persistent state - depends on the API layer being in place first.

### Speaker Notes
"The roadmap is strictly phased to manage architectural risk. Phase 1, validating the ML logic via this prototype, is complete. Phase 2 focuses entirely on technical debt: decoupling the backend into a FastAPI microservice and establishing Pydantic data contracts. This is the foundation everything else depends on. Phase 3 then addresses the integration of asynchronous Celery task queues for computation loads, alongside the critical business milestone of swapping the synthetic training data for normalized historical ERP project data. The biggest risk to Phase 3 is data normalization: the pipeline expects clean categorical tags for Vendor Tier, Land Type, and similar fields. If the ERP system uses unstructured text for these fields, the data engineering required to map them will take additional time."

### Possible Questions and Safe Answers
**Question:** "What is the biggest risk to hitting the ERP integration milestone?"
**Safe Answer:** "Data normalization constraint. The pipeline expects clean categorical tags for 'Vendor Tier' and 'Land Type'. If the legacy ERP system uses unstructured text for these fields, the data engineering required to map those fields will require additional time and coordination with the ERP team."

**Question:** "Why not do FastAPI and ERP data at the same time?"
**Safe Answer:** "Attempting both simultaneously would mean debugging two unknown variables at once: whether the API integration is correct AND whether the data mapping is correct. Keeping them as separate phases means if something breaks, we know exactly which change caused it."
