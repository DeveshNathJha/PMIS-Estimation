# Core Logic (`app/core/logic.py`)

## What is it?
This file contains the "Business Intelligence" and mathematical algorithms. It does not know about Streamlit or UI; it just processes data.

## Why is it needed?
**Separation of Concerns:** We keep complex math out of the UI files. This makes the code testing easier and keeps the UI files clean and focused on rendering.

## How does it work?

### Key Functions

1.  **`get_wbs_template_from_data(p_type, df)`**
    -   **Goal:** Fetch the standard tasks for a project (e.g., "Hospital") directly from the dataset.
    -   **Logic:** Filters the dataframe for that project type, sorts by sequence, and returns a clean table of tasks and their *planned* durations.

2.  **`calculate_cpm(tasks_df)`**
    -   **Goal:** Calculate the **Critical Path** and total Project Duration.
    -   **Algorithm:** Implements the standard Project Management Critical Path Method (CPM).
        -   **Forward Pass:** Calculates Early Start (ES) and Early Finish (EF).
        -   **Backward Pass:** Calculates Late Start (LS) and Late Finish (LF).
        -   **Slack/Float:** `LF - EF`. If 0, the task is Critical.
    -   **Output:** Returns the total days and the list of critical task IDs.

3.  **`generate_granular_risk_assessment(row, ...)`**
    -   **Goal:** Explain *WHY* a task is delayed.
    -   **Logic:** This is the "Artificial Intelligence" reasoning layer (Rule-Based).
        -   It calculates `Variance = Predicted - Planned`.
        -   If Variance > 0 (Delay), it checks flags:
            -   Is `LWE_Flag` on? -> Blame "Security/LWE".
            -   Is `Land_Type` Tribal? -> Blame "CNT Act".
            -   Is `Monsoon_Flag` on? -> Blame "Weather".
    -   **Result:** Returns a human-readable string like *"DELAY: LWE Friction + Monsoon (+45 days)"*.
