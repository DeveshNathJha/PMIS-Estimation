# Mid-Project Tracker UI (`app/ui/tracker.py`)

## What is it?
The **Tracker** is for ongoing execution. It allows a project manager to say "We are 50% done with Foundation", and the tool re-forecasts the remaining timeline based on actual velocity.

## Why is it needed?
Plans are never static. As a project progresses, we learn about the *actual* conditions on the ground. The Tracker calibrates the remaining forecast based on this reality.

## How does it work?

### Function: `render_tracker(df, context)`
1.  **Task Selection:**
    -   The user views tasks and assigns actual completion days.
2.  **Re-Forecasting Logic (ML Inference):**
    -   Calculates total actual days spent so far.
    -   Constructs feature vectors for all remaining/pending tasks (incorporating shifting monsoon windows based on the new timeline).
    -   Passes these remaining tasks back through the **CatBoost P50 Model** to generate a live, dynamic estimate of the remaining duration.
3.  **Outputs:**
    -   Generates AI-driven risk explanations for delayed tasks.
    -   Produces an updated "Revised End Date" and mid-project PDF report.
