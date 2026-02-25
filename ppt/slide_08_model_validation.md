# Slide 08: Validation Methodology and Metrics
## How model quality was measured and what the results actually tell us

---

### Slide Content
- **Evaluation Metrics: MAE, R2, RMSE on 20% Hold-out Set:** The training pipeline (`config.py`: `TEST_SIZE=0.2`, `RANDOM_STATE=42`) produces MAE, R2, and RMSE metrics for all four models - P10, P50, P90, and the Bayesian Ridge baseline - on a held-out 20% test split. These metrics are logged during each training run and saved inside the model artifact dictionary under the `model_metrics` key.
- **Bayesian Ridge as Comparison Baseline:** A scikit-learn BayesianRidge model is trained alongside CatBoost on the same train/test split. This allows a direct comparison: if CatBoost's MAE and R2 are not clearly superior to the baseline, the added complexity is not justified. The training script prints a side-by-side comparison of all four models.
- **SHAP Explainability on P50 Model:** SHAP (SHapley Additive exPlanations) is computed on the P50 (median) model using `shap.TreeExplainer`. Two plots are generated: a global bar chart of mean absolute SHAP values per feature, and a beeswarm plot showing impact direction. Output correctly identifies Vendor_Tier and Monsoon_Flag as the primary delay drivers.
- **Handling Incorrect Predictions: Feedback Loop:** When a prediction diverges significantly from the actual outcome, the correction path is: (1) log the actual outcome alongside the model's prediction in a feedback ledger, (2) accumulate a set of such records, (3) include them in the next scheduled retraining cycle as additional ground-truth data. This closes the learning loop over time without requiring structural code changes. Once connected to real ERP data, this process becomes systematic via a scheduled retrain trigger.

**Note:** Metrics are on synthetic data only. Results will shift on real ERP data - this is expected, and the retraining pipeline is already built to handle it seamlessly.

**Key Insight:** SHAP output aligning with domain knowledge (Vendor Tier and Monsoon as top drivers) is the strongest quality signal at this stage - it confirms the model learned the right relationships.

### Speaker Notes
"The model's structural viability has been evaluated and it performs as designed. The evaluation uses a strict 20/80 train-test split defined in config.py. I compute MAE, R-squared, and RMSE for four models: the three CatBoost quantile models and a Bayesian Ridge statistical baseline. SHAP is applied specifically to the P50 (median) model. The SHAP output correctly attributes delay impact to Vendor_Tier and Monsoon_Flag as the primary friction multipliers - this aligns directly with the physics baked into the data generator, which validates the model learned the right relationships. Regarding wrong predictions: when the model is off, the actual outcome is recorded and fed back into the next retraining cycle. The system is set up to learn and self-correct over time. However, I must be explicit: these metrics prove the pipeline correctly learned the synthetic rules. The real test is real ERP data - and the retraining pipeline is already ready for it."

### Possible Questions and Safe Answers
**Question:** "If the data is synthetic, isn't this model completely useless?"
**Safe Answer:** "The specific prediction weights are uncalibrated for production, yes. But the pipeline logic - from feature ingestion to quantile prediction to SHAP explanation to the feedback loop - is fully functional. The infrastructure is built; only the training data source needs to change. Updating to real ERP data requires changing the data source and triggering a retrain cycle."

**Question:** "What happens when the model gives a wrong prediction in a real deployment?"
**Safe Answer:** "The actual outcome is recorded alongside the predicted value in a feedback ledger. As these records accumulate, they are included in the next retraining cycle as ground-truth data. This is the standard approach for supervised ML systems - the model improves over time as it sees more real cases. On real ERP data, this process can be scheduled and automated."

**Question:** "Why compare to Bayesian Ridge?"
**Safe Answer:** "A comparison baseline tells us whether the complexity of CatBoost is justified. If a simple linear model achieved the same accuracy, we would not need the more complex approach. Including the baseline comparison is standard ML validation practice and demonstrates engineering rigor."
