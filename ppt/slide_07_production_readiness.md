# Slide 07: Codebase Maturation Status
## Engineering improvements applied to stabilise the Alpha prototype

---

### Slide Content
- **Dependency Pinning: requirements.txt (15 libraries):** All 15 production dependencies and their exact versions are declared in requirements.txt (e.g., `catboost==1.2.10`, `streamlit==1.54.0`, `pandas==2.3.3`, `shap==0.50.0`, `networkx==3.6.1`). This ensures any deployment environment reproduces the exact binary environment, eliminating 'works on my machine' failures.
- **Centralized Logging: Replacing print() Anti-pattern:** Raw `print()` statements were systematically replaced with the Python standard library `logging` module, configured at the orchestrator level (`app/main.py`). Log output goes simultaneously to stdout AND to `app.log` on disk. This enables severity-level filtering (INFO / WARNING / ERROR / CRITICAL), timestamped entries, and graceful silent failure for recoverable errors.
- **Dynamic Inference Substitution in Mid-Project Tracker:** The mid-project tracking module previously used hardcoded schedule estimates as placeholders. These were replaced with live CatBoost P50 inference calls, computing re-forecasted durations dynamically based on current session state inputs.
- **Testing Status: One Smoke Test, No Pytest Unit Tests:** A headless smoke test (`tests/smoke_test.py`) exists and validates the CPM critical path calculation logic independently of Streamlit. There are no Pytest unit tests for the ML inference functions, data transformation pipelines, or UI routing modules. There are no CI/CD triggers. Both Pytest coverage and CI/CD are formal next-phase prerequisites before any production deployment.

**Note:** No Pytest unit tests for ML inference or UI modules. One CPM smoke test (`tests/smoke_test.py`) exists but no CI/CD pipeline. Manual regression testing is the sole verification method currently.

**Key Insight:** Centralized logging to `app.log` and dependency pinning are foundational hygiene steps that make the system diagnosable and reproducible - critical preconditions before any handover to another team.

### Speaker Notes
"While the system remains an Alpha prototype, I have performed foundational stabilization work. All 15 production dependencies are pinned to exact versions - like pinning down the exact tools used to build a bridge so it can be perfectly replicated. I replaced raw print statements with a centralized logging system that writes to both the terminal and app.log on disk, giving a persistent audit trail of the application's behavior. I also replaced hardcoded estimates in the mid-project tracker with live P50 model inference. On testing: one headless smoke test exists to verify the CPM critical path math. However, there are zero Pytest unit tests for the ML inference layer or the UI routing logic. Automated test coverage is the first deliverable of the next phase."

### Possible Questions and Safe Answers
**Question:** "If there are no unit tests, how did you verify the dynamic inference substitution works?"
**Safe Answer:** "Verification relied on manual regression testing: running through all UI flows and comparing outputs against hand-calculated expected values. The CPM logic is covered by the smoke test. Establishing Pytest coverage for inference endpoints is the first action upon initiating the next phase."

**Question:** "What is in the smoke test?"
**Safe Answer:** "The smoke test (tests/smoke_test.py) runs entirely headless - no Streamlit dependency. It validates the CPM forward-pass and backward-pass calculations with a known 4-task network and asserts the project duration and critical path are correct. It also runs a minimal risk multiplier calculation check."
