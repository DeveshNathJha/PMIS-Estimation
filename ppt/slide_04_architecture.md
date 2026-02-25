# Slide 04: Current System Architecture (Alpha Build)
## Understanding the deliberate design trade-offs of the monolithic prototype

---

### Slide Content
- **Technology Stack: Streamlit Monolith:** The Alpha prototype is built as a single Streamlit Python application. Streamlit converts Python scripts directly into interactive web UIs, allowing rapid iteration on ML output visualizations without building a separate frontend. The entire application - UI definitions, data routing logic, and ML inference calls - runs inside a single Python process.
- **Data Flow: Synchronous Execution Model:** User interactions trigger Streamlit's re-execution model, which re-runs the entire Python script top-to-bottom. Data transformations, feature engineering, and CatBoost inference all execute sequentially in this single thread before the page re-renders.
- **Memory Management: Model Caching:** The three CatBoost model bundles (P10, P50, P90) are loaded and held in server memory via `@st.cache_resource`. Without this, each page interaction would trigger a fresh disk read and model deserialization, adding 2-3 seconds of latency per inference call.
- **Critical Architectural Constraint: Single-Threaded Blocking:** Because all computation shares one OS thread, any heavy operation blocks the entire application. Running a 500-node Monte Carlo network simulation freezes the UI for every active user until completion. This is the primary architectural debt that prevents production deployment.

**Note:** The application is single-threaded and single-process. Concurrent users will cause blocking, latency spikes, and potential timeouts. Not suitable for multi-user production.

**Key Insight:** This monolithic architecture was the correct choice for rapid prototype validation. It allowed the ML logic to be proven in weeks rather than months. Phase 2 dismantles it systematically.

### Speaker Notes
"The current architecture is a tightly coupled monolith using Streamlit. The UI definitions, business routing logic, and ML inference calls are all executed in sequence within a single Python process. This was a deliberate engineering trade-off taken to accelerate visual validation - not a mistake. We implemented memory caching to hold the four model bundles efficiently. However, because it is single-threaded, if the system computes a heavy 500-node Monte Carlo simulation, the entire event loop blocks. Think of it as a one-person shop: it works perfectly when one customer is being served, but if ten people walk in simultaneously, they all have to wait. The next phase specifically addresses this bottleneck."

### Possible Questions and Safe Answers
**Question:** "What happens if 10 project managers try to generate reports at the exact same time right now?"
**Safe Answer:** "The server thread will block and queue the requests sequentially. The latency will spike linearly, and the application will likely time out or crash for later users. This architecture cannot handle concurrent loads - and that is exactly why Phase 2 is focused on decoupling."
