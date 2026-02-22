# Data Loader (`app/utils/data_loader.py`)

## What is it?
This utility script is responsible for safely loading the heavy assets (Machine Learning Model and Dataset) into memory at startup.

## Why is it needed?
1.  **Error Handling:** It prevents the entire app from crashing if a file is missing. It wraps the loading in a `try-except` block to show a friendly error message instead of a stack trace.
2.  **Caching (Optimization):** In Streamlit, we use `@st.cache_resource` (implied or explicit in larger apps) to load the model only once, not on every user click. This file isolates that logic.

## How does it work?

### Function: `load_resources()`
1.  **Sys Path Check:** It adds the root directory to `sys.path` so it can import `config`.
2.  **Data Loading:**
    -   Checks if `data/synthetic_project_data.csv` exists.
    -   Reads it with `pandas`.
3.  **Model Loading:**
    -   Checks if `data/pmis_model.pkl` exists.
    -   Loads it using `joblib` (a specialized library for saving Python objects efficiently).
4.  **Returns:** A tuple `(dataframe, model_artifact)` to the main app.
