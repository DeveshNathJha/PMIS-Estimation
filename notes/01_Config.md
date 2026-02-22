# Configuration (`config.py`)

## What is it?
`config.py` is the central repository for all "hardcoded" values, settings, file paths, and algorithm parameters used across the entire application and scripts.

## Why is it needed?
1.  **Single Source of Truth:** If we need to change a file path (e.g., moving data to `data/`), we change it here once, and all 10+ other files update automatically.
2.  ** Consistency:** Ensures the *Training* script and the *Inference* app use the exact same feature list and hyperparameters.
3.  **Maintainability:** Keeps magic numbers / strings out of the logic code.

## How does it work?
It is a plain Python file with uppercase variable names (constants).

### Key Sections:
1.  **File Paths:** Uses `os.path.join` to create cross-platform paths.
    ```python
    DATA_FILE = os.path.join('data', 'synthetic_project_data.csv')
    ```
2.  **Model Params:** Defines how the CatBoost AI learns.
    ```python
    CATBOOST_PARAMS = {'iterations': 1000, 'depth': 6, ...}
    ```
3.  **Visuals:** Defines the brand colors.
    ```python
    FIRM_BLUE = "#00338D"  # Corporate Identity
    DARK_BG_COLOR = "#0E1117"
    TEXT_COLOR = "#FAFAFA"
    ```
4.  **Business Logic Maps:**
    -   `STATE_PROFILE`: Defines friction for each state (Terrain, Monsoon severity).
    -   `JHARKHAND_MAP`: Defines detailed security risks for specific districts.
    -   `PROJECT_TEMPLATES`: Defines the standard phases (WBS) for different project types (e.g., Hospital, Road).
