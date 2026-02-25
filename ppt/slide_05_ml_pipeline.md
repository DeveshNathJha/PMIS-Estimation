# Slide 05: ML Pipeline and Feature Engineering
## How the model is built, serialised, and deployed for inference

---

### Slide Content
- **Algorithm: CatBoost Quantile Regression + Bayesian Ridge Baseline:** CatBoost was chosen for its native handling of high-cardinality categoricals without manual one-hot encoding. Three separate CatBoost models are trained - one per quantile (P10, P50, P90) - each with `loss_function='Quantile:alpha=q'`. A Bayesian Ridge model is also trained as a statistical comparison baseline. The final deployed artifact contains all four trained models plus metadata bundled as `data/pmis_model.pkl` (PMIS v8.0) via joblib.
- **Training / Inference Separation:** Model training runs offline via `scripts/PMIS_Training_Pipeline.ipynb`. Trained models are exported as a single serialized artifact: `data/pmis_model.pkl`. The production Streamlit application loads this artifact at startup via `@st.cache_resource`. The application runtime contains zero training code - it is a pure inference consumer.
- **Active Feature Set (8 Features from config.py):** `FEATURES = [Project_Type, District, LWE_Flag, Task_Category, Land_Type, Vendor_Tier, Planned_Duration, Monsoon_Flag]`. Vendor_Tier is a 3-tier integer rating: 1 = L&T / Tata Projects (premium), 2 = NCC / Nagarjuna (mid-tier), 3 = Local Contractor. Target variable: Actual_Duration.
- **Engineered but Inactive: TF-IDF NLP Layer:** A TF-IDF vectorisation layer (`max_features=100`) is implemented and tested against the `Task_Name` column. The integration code exists in the training notebook (CELL 7b) but is commented out - a documented future improvement. It is disabled to maintain baseline model stability and interpretability during this validation phase.

**Note:** TF-IDF NLP layer is engineered but commented out in training (CELL 7b). MLflow experiment tracking is not yet active - versioning is file-system based using timestamped artifact folders.

**Key Insight:** Strict training-inference separation means updating the model requires only replacing `pmis_model.pkl` - the live Streamlit application requires zero code changes to pick up a retrained model.

### Speaker Notes
"For the machine learning pipeline, I selected CatBoost due to its efficiency with high-cardinality categorical variables, which dominate our dataset. A strict separation of concerns is enforced: the training notebook operates offline, outputting a single serialized artifact (pmis_model.pkl, PMIS v8.0) that the application loads at runtime. The active feature set is 8 features defined in config.py - all fields that already exist in project records, so no new data collection is required. I also trained a Bayesian Ridge model as a formal statistical baseline to verify that CatBoost adds genuine value over a simpler approach. The TF-IDF text analysis layer is built and tested but commented out in training - it is queued for future activation once we have real data and the pipeline is more stable."

### Possible Questions and Safe Answers
**Question:** "How are you tracking model versions?"
**Safe Answer:** "Currently, versioning is file-system based: artifacts are stored in timestamped folders and the active model is pmis_model.pkl with version metadata stored inside the artifact dictionary. Formal experiment tracking via MLflow is planned for Phase 3, once we connect to live ERP data feeds."

**Question:** "Why 8 features? Could the model use more?"
**Safe Answer:** "These 8 features represent the highest-signal variables identified by domain knowledge and confirmed by the SHAP attribution output. All 8 are fields already available in existing project records, meaning no new data collection infrastructure is required. A TF-IDF layer for free-text task descriptions is already built and waiting to be activated as a Phase 3 enhancement."
