# Slide 11: System Constraints and Failure Scenarios
## Transparent assessment of current architectural risks and known failure modes

---

### Slide Content
- **Concurrency Failure: Single-Threaded Blocking:** The Streamlit application runs as a single Python process with one synchronous execution thread. For heavy computations - Monte Carlo simulations, CPM network regeneration on 500+ node graphs - the main thread can block for 8-12 seconds. During this window, all other active users experience a frozen, unresponsive UI. Under three or more simultaneous users with heavy workloads, the server will queue requests linearly, causing cascading timeouts.
- **Input Vulnerability: No Backend Data Contract:** The system's only data validation layer is the Streamlit UI widget configuration (select boxes, numeric sliders). If a user bypasses the UI - via direct session state mutation, automated scripting, or UI modification - malformed data will reach the CatBoost inference engine without sanitisation, causing an unhandled Python exception that crashes the server process.
- **Feature Completeness: NLP Layer Disabled:** The TF-IDF vectorisation layer that processes free-text task descriptions is engineered and present in the codebase but disabled at inference time. This means the model currently ignores semantic signals in unstructured task descriptions - information that could significantly improve prediction accuracy for novel task types.
- **Production Suitability Assessment:** This system in its current form is unsuited for any production deployment involving concurrent network access. It is explicitly scoped as a single-user local validation tool. Concurrent user support, input validation robustness, and persistent state management are all next-phase prerequisites before any network exposure.

**Note:** Multi-user concurrent access will cause application blocking and potential crashes. Bypassing the Streamlit UI can inject malformed data directly into the inference engine.

**Key Insight:** Full transparency about these failure modes demonstrates engineering maturity. Every constraint listed here has a concrete, planned resolution in the Phase 2 and Phase 3 roadmap.

### Speaker Notes
"To maintain engineering transparency, I must address the system's current failure scenarios. Because it is monolithic, heavy graph recalculations block the main execution thread. Think of it as a toll booth with only one lane: one car at a time is fine, but if ten cars arrive together, nine are stuck waiting. Secondly, there is no robust backend data contract. The system relies on the frontend UI to ensure users do not type text into numeric fields; if they bypass that, the Python process crashes. Phase 2 (FastAPI + Pydantic) builds a proper security checkpoint. Finally, the NLP text features are disabled to ensure baseline stability, meaning the model is currently ignoring raw task descriptions - a deliberate trade-off for this validation phase. Bottom line: this is a validated prototype, not a deployed product. The roadmap addresses every item listed here."

### Possible Questions and Safe Answers
**Question:** "If the UI is the only validation, how easily can this break?"
**Safe Answer:** "Very easily if accessed via script or if the UI rules are modified incorrectly. This architectural fragility is exactly why the next phase mandates a FastAPI layer with Pydantic validation before the inference node."
