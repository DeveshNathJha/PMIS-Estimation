# Slide 01: Predictive Project Management Information System (PMIS)
## ML-Assisted Delay Forecasting | Alpha Prototype Review

**Project Lead:** Devesh Jha
**Phase:** Alpha Validation
**Focus:** ML Pipeline and Architecture
**Status:** Prototype: Logic Validated

---

### Slide Content
- **What is this?** An AI system built to predict when a construction project will be delayed, before it actually gets delayed.
- **Current Status:** The core math and AI logic has been tested and validated. This review is to share findings and discuss the path forward.
- **Goal of Today:** Get alignment on current architecture trade-offs and discuss the Phase 2 stabilisation plan.

### Speaker Notes
"Good morning. I am presenting the technical assessment of the Predictive PMIS module I have been building. The objective has been to validate whether Machine Learning can quantify environmental friction to predict project delays. What you will see today is an Alpha prototype - a functional, monolithic application used strictly to validate the data science and ML logic. The goal of this review is to transparently discuss the prototype's architectural limitations and outline the proposed engineering roadmap to decouple and stabilize the system."

### Possible Questions and Safe Answers
**Question:** "What exactly do you mean by Alpha Prototype?"
**Safe Answer:** "It means the core ML mathematics and inference pipelines are functional and producing expected outputs, but the surrounding software architecture is currently monolithic and not designed to handle concurrent network traffic or real-world data loads. Think of it as a proof-of-concept that is now ready for the next engineering phase."
