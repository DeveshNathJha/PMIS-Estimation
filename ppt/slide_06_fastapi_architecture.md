# Slide 06: Proposed Backend Decoupling (Phase 2 Architecture)
## Engineering the transition from monolith to microservice

---

### Slide Content
- **The Core Problem: Tight Coupling:** Currently, the ML inference engine, data transformation logic, and UI rendering all share the same Python execution context. A slow inference call directly degrades UI responsiveness. An API crash takes down the entire application. There is no separation of concerns, no independent scaling, and no contract between the frontend and the data pipeline.
- **Proposed Solution: FastAPI Microservice:** A FastAPI application running under Uvicorn ASGI server will be built. FastAPI natively supports Python's async/await paradigm, enabling non-blocking I/O and concurrent request handling. The ML inference endpoint will accept a structured JSON payload and return a structured JSON response. The Streamlit UI will become a thin client, consuming the API via HTTP requests instead of calling Python functions directly.
- **Data Contracts via Pydantic Schemas:** Every API endpoint will define strict Pydantic input models enforcing field types, required vs optional fields, and value range validation (e.g., lwe_flag must be 0 or 1). Invalid payloads will be rejected with structured 422 responses before they ever reach the inference engine. This eliminates the current vulnerability of relying solely on Streamlit UI constraints for data validation.
- **Current Implementation Status:** FastAPI is not yet implemented. Phase 1 deliberately excluded it to reduce development overhead during ML logic validation. All API architecture designs exist as documented specifications. Full FastAPI implementation is the milestone-one deliverable of the next phase.

**Note:** FastAPI is not yet implemented. The system currently relies solely on Streamlit UI constraints for input validation, which is a fragile and bypassable mechanism.

**Key Insight:** Decoupling the API from the UI is the single highest-priority next-phase action - it unlocks concurrent access, independent scaling, and eliminates the current input validation vulnerability.

### Speaker Notes
"Because the monolith restricts scaling, the next phase is centered entirely around backend decoupling. The proposed solution is to stand up a FastAPI microservice to absorb all ML inference and data transformation responsibilities. Think of it like splitting a restaurant's kitchen from its dining room: right now the UI and the AI brain are in the same room. FastAPI provides native asynchronous processing capabilities. Furthermore, Pydantic schemas establish strict data contracts - acting as a bouncer at the door that rejects garbage data before it ever reaches the inference engine. Right now, if a user bypasses the Streamlit constraints, invalid data hits the model and causes a runtime failure. A dedicated API gateway will prevent that entirely."

### Possible Questions and Safe Answers
**Question:** "Why wasn't an API built for Phase 1?"
**Safe Answer:** "Building an API layer prematurely would have introduced network overhead and slowed down the direct iteration cycle between the data science logic and visual validation. Now that the logic is proven, API construction is the immediate priority."

**Question:** "How long will FastAPI implementation take?"
**Safe Answer:** "The architectural design is already documented. The implementation involves standing up the FastAPI app, defining the Pydantic schemas for the 8 input fields, and wiring the CatBoost inference call behind the endpoint. The scope is well-defined and manageable within the next phase sprint."
