# Application Entry Points (`pmisapp.py` & `app/main.py`)

## What are they?
These two files work together to launch the Streamlit web application. `pmisapp.py` is the simplified entry point, while `app/main.py` contains the actual layout and routing logic.

## Why are they needed?
1.  **`pmisapp.py`**: Needed because Streamlit runs a script execution model. Keeping the root file simple allows us to cleanly import the rest of the app from a package (`app/`).
2.  **`app/main.py`**: Separates the "View" orchestration from the root. It handles the "Navigation" state.

## How do they work?

### 1. `pmisapp.py`
This is the file you run: `streamlit run pmisapp.py`.
-   **Job:** It imports `main()` from `app.main` and executes it.
-   **Logic:**
    ```python
    from app.main import main
    if __name__ == "__main__":
        main()
    ```

### 2. `app/main.py`
This dictates the structure of the webpage.
-   **Setup:** Sets page title, layout (Wide mode), and injects CSS.
-   **Resource Loading:** Calls `load_resources()` to get data and the AI model into memory.
-   **Sidebar Rendering:** Calls `render_sidebar` (from `app.ui.components`) to draw the inputs on the left.
-   **Routing (The Switcher):** This is the core logic that decides which screen to show.
    ```python
    if module == "Pre-Start Estimator":
        render_estimator(...)
    elif module == "Mid-Project Tracker":
        render_tracker(...)
    ```
    This "Router" pattern allows the app to feel like a multi-page tool even though it's a single-page app (SPA).
