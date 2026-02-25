# Slide 14: Appendix - Technical Review and Q&A
## Anticipated questions and prepared responses for the review panel

---

### Slide Content (Q&A Cards)

**Q: Is this production ready?**
No - deliberately. This is a validated Alpha build prioritising ML logic correctness over infrastructure robustness. FastAPI decoupling and Pydantic validation must be completed before exposing this system to network traffic with multiple concurrent users.

**Q: Why was Streamlit chosen over a proper web framework?**
Streamlit converts Python data science code into an interactive UI without requiring frontend engineering. It allowed rapid visual iteration between the ML outputs and stakeholder feedback cycles. It is a temporary monolithic presentation layer, not the intended final architecture.

**Q: What happens if multiple users access it simultaneously right now?**
The server thread will block and serve users sequentially. Under heavy loads (3+ users triggering CPM simulations concurrently), response times will spike linearly and later requests will likely timeout. This is the primary next-phase engineering target.

**Q: If the AI is trained on fake data, why should we trust it at all?**
The specific prediction weights are uncalibrated. But the pipeline infrastructure - feature ingestion, quantile inference, SHAP attribution, CPM integration - is fully functional and architecturally sound. Transitioning to real ERP data requires only updating the data source and triggering a retrain cycle. The infrastructure investment is not wasted.

**Q: Are you tracking model performance over time (data drift)?**
Not currently. MLflow experiment tracking and data drift alerting are scoped for Phase 3, post-ERP integration. At this stage, model versioning is managed via timestamped file-system artifact folders.

**Q: What are the 3 things you need from leadership today?**
1) Approval of the Phase 2 FastAPI sprint. 2) A channel to begin ERP data access discussions for Phase 3 data integration. 3) Agreement on the architectural limitations detailed today - this system is not ready for production as-is.

**Key Insight:** The strongest answer to any tough question today: "I know the limitation. It was built this way deliberately to validate the ML logic fast. The roadmap addresses it directly."

### Speaker Notes
"This concludes the technical review of the Alpha prototype. I have outlined the current monolithic limitations, the synthetic data constraint, and the exact roadmap to resolve them via FastAPI and eventual ERP integration. I am happy to open the floor to discuss the Phase 2 architecture, input validation schemas, or any questions regarding the underlying machine learning mechanisms."

### Additional Safe Answers Reference
- **On data drift monitoring:** "MLflow integration is planned post-Phase 2 to track experiment accuracy and data drift once we connect to live ERP data feeds."
- **On the feedback loop:** "When the model is wrong, the actual outcome is recorded and fed back into the next retraining cycle. The system learns and self-corrects over time. On real ERP data, this process can be scheduled and automated."
- **On the timeline:** "Phase 1 is complete. The next phase is the API decoupling work, which has a well-defined scope. Phase 3 timing depends on ERP data access, which is why that conversation is one of the three asks today."
