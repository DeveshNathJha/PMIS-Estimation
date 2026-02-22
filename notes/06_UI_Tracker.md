# Mid-Project Tracker UI (`app/ui/tracker.py`)

## What is it?
The **Tracker** is for ongoing execution. It allows a project manager to say "We are 50% done with Foundation", and the tool re-forecasts the remaining timeline based on actual velocity.

## Why is it needed?
Plans are never static. As a project progresses, we learn about the *actual* conditions on the ground. The Tracker calibrates the remaining forecast based on this reality.

## How does it work?

### Function: `render_tracker(df, context)`
1.  **Task Selection:**
    -   The user selects a "Current Phase" (e.g., Foundation).
2.  **Progress Input:**
    -   User inputs: *"Task started on X date. We are Y% complete."*
3.  **Re-Forecasting Logic:**
    -   It calculates the **Burn Rate** or "Velocity".
    -   If the project is behind schedule on early tasks, it assumes this "friction" will continue for future tasks (unless mitigation is applied).
    -   It updates the Start Dates of all future (dependent) tasks.
4.  **Outputs:**
    -   **Recovery Plan:** Suggests if "Crashing" (adding resources) is needed to catch up.
    -   **New Est. Completion Date:** The updated finish line.
