# Model Training Script (`scripts/train_production_model.py`)

## What is it?
This script reads the synthetic data and trains the Machine Learning models that power the app.

## Why is it needed?
The application (`pmisapp.py`) does not *train* the model; it only *uses* (inferences) it. This script is the "Factory" that builds the "Brain" (`pmis_model.pkl`) that the app uses.

## How does it work?

### The Algorithm: CatBoost Regressor
We use **CatBoost** (Categorical Boosting) because it handles categorical data (District names, Vendor types) natively and extremely well without complex preprocessing.

### Quantile Regression (The "Three Brains")
We don't train just one model. We train *three*:
1.  **Lower Bound (alpha=0.1):** Learns to predict the *best-case* scenario (P10).
2.  **Median (alpha=0.5):** Learns to predict the *most likely* outcome (P50).
3.  **Upper Bound (alpha=0.9):** Learns to predict the *worst-case* scenario (P90).

### Process Flow
1.  **Load Data:** Reads `data/synthetic_project_data.csv`.
2.  **Feature Selection:** Keeps only relevant columns defined in `config.FEATURES`.
3.  **Training Loop:**
    -   Iterates through `[0.1, 0.5, 0.9]`.
    -   Trains a `CatBoostRegressor` with `loss_function='Quantile:alpha=...'`.
4.  **Saving:**
    -   Bundles the three models into a dictionary: `{'P10': model1, 'P50': model2, 'P90': model3}`.
    -   Saves this bundle as a pickle file (`data/pmis_model.pkl`).

## 3. Model Selection Rationale

### Why CatBoost?
We chose **CatBoost** (Categorical Boosting) over other algorithms (Random Forest, XGBoost) for three specific reasons:
1.  **Native Categorical Support:** Our data is heavy on categories (`District`, `Vendor_Name`, `Project_Type`). CatBoost handles these natively without needing massive One-Hot Encoding (which creates thousands of empty columns).
2.  **Quantile Support:** We need P10, P50, and P90 confidence intervals. CatBoost has a built-in `Quantile` loss function that is mathematically rigorous for this purpose.
3.  **Robustness:** It is less prone to overfitting on small datasets compared to deep learning approaches.

### The Baseline: Bayesian Ridge
The script *also* trains a **Bayesian Ridge** model, but only as a **Baseline**.
-   **What is it?** A probabilistic linear regression model.
-   **Why use it?** If our fancy CatBoost model cannot beat this simple linear model, then our approach is over-engineered.
-   **Result:** In our tests, CatBoost consistently outperforms Bayesian Ridge because infrastructure delays are *non-linear* (e.g., Rain + Hill + Bad Road = Exponential Delay, not just Additive).
