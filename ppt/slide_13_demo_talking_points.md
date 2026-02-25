# Slide 13: Prototype Capabilities Demonstration
## Live navigation of the PMIS Alpha build - two-scenario walkthrough

---

### Slide Content
Run the prototype with: `streamlit run pmisapp.py`

**Step 1 - Baseline:** Set parameters: Tier 1 Vendor, Low LWE Risk District, April start (pre-monsoon). Observe P50 duration as the ideal-condition baseline reference.

**Step 2 - Friction:** Modify: switch to Tier 3 Vendor, High LWE Risk Zone, June start (deep monsoon). Observe P90 bound stretch dramatically - each parameter multiplies delay risk.

**Step 3 - SHAP:** Open SHAP explainability panel for the friction scenario. Review per-feature attribution: which factor contributed most days of delay.

**Step 4 - CPM:** Navigate to the Critical Path view. Observe how the delay distributes across the task network and shifts the project end date.

**Key Insight:** The two-scenario walkthrough makes the AI's sensitivity to environmental friction immediately tangible - even for non-technical stakeholders watching the numbers change in real time.

### Speaker Notes
"I am going to transition to the live Alpha build now. To demonstrate the inference engine's sensitivity to environmental metadata, I will run two scenarios. First, a baseline project with a premium vendor in a safe operating environment. Then, I will inject friction: simulating a Tier 3 vendor operating during monsoon season in an LWE conflict zone. You will see the pipeline dynamically stretch the Critical Path schedule based on the probabilistic assumptions learned during training. The SHAP panel then shows a breakdown of exactly which factor contributed how many days of delay."

### Possible Questions and Safe Answers
**Question:** "The model pushed the delay by 45 days. Why exactly 45?"
**Safe Answer:** "The model relies on the variance distributed in the synthetic training data. In this run, the SHAP values indicate that the combination of Tier 3 capability overlaid with monsoon season friction drove the majority of that 45-day penalty. In a real deployment, that exact figure will calibrate to our historical ERP baselines."
