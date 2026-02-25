# Slide 03: Probabilistic Forecasting via Quantile Regression
## Replacing single-point estimates with ML-derived confidence intervals

---

### Slide Content
- **Algorithm: CatBoost Quantile Regression:** CatBoost - a gradient-boosted tree algorithm - is configured with Quantile Regression loss functions. It trains three separate models: one for the optimistic case (P10), one for the most likely case (P50), and one for the conservative planning scenario (P90). Each quantile model independently learns the relevant portion of the outcome distribution.
- **Output: Three Confidence Bounds (P10 / P50 / P90):** P10 = 10% probability (optimistic). P50 = 50% probability (median expected completion). P90 = 90% probability (conservative planning buffer). This replaces subjective PM intuition with a statistically grounded confidence interval for every task in the schedule.
- **Feature Integration: Environmental Friction Variables:** The model dynamically incorporates: monsoon season overlap (exact day-count), LWE zone security friction multipliers, vendor tier performance scores, and terrain/geographic difficulty factors. All are automatically combined at inference time.
- **Real Data Acquisition Plan:** The model is currently trained on a synthetic dataset designed to simulate real-world variance patterns. The path to real data: (1) Extract historical task records from the ERP system (task type, actual vs planned duration, contractor, location). (2) Map to the 8-feature schema defined in config.py. (3) Trigger a retrain cycle. The pipeline architecture is ready - only the data source needs to be switched.

**Note:** The model is currently trained on a synthetic dataset, not live ERP history. The pipeline architecture is validated; calibration to real data is the defined next milestone.

**Key Insight:** Moving from a single-point estimate to P10/P50/P90 bounds gives decision-makers a mathematically grounded basis for contingency budgeting - not guesswork.

### Speaker Notes
"Our approach uses CatBoost for Quantile Regression. Instead of outputting a single mean prediction, the algorithm provides a confidence-bounded distribution: P10, P50, and P90. Think of it like a weather forecast - '70% chance of rain' is more useful than just 'it might rain'. The inference engine evaluates the specific task category against the project's geographic and temporal context, dynamically checking: Is this task scheduled during monsoon? Is the vendor reliable? Is the site in a high-risk zone? These factors adjust the forecast automatically. I want to be upfront about the data: the current model is trained on synthetic data designed to mimic real-world variance patterns. The path to real data is clearly defined - extract ERP records, map to the 8-feature schema, retrain. It is a well-defined, executable step, not a research problem."

### Possible Questions and Safe Answers
**Question:** "Why did you use synthetic data instead of historical data from the start?"
**Safe Answer:** "Historical data extraction requires significant data engineering and cleansing cycles. Using a synthetic physics engine to validate the mathematical pipeline first allows us to isolate logic errors from raw data quality issues. Now that the pipeline architecture is proven, we can switch the data source cleanly."

**Question:** "How exactly will you get the real data from ERP?"
**Safe Answer:** "The 8 features the model needs - Project Type, District, LWE Flag, Task Category, Land Type, Vendor Tier, Planned Duration, and Monsoon Flag - are all fields that already exist in our project records. The engineering task is to extract and clean these fields from the ERP system and feed them into the existing training pipeline."
