# Pre-Start Estimator UI (`app/ui/estimator.py`)

## What is it?
The **Pre-Start Estimator** is the planning tool. It allows a user to define a new project (Type, Location, Vendor) and get a probabilistic forecast *before* the project begins.

## Why is it needed?
This is the core value proposition of the tool: moving from "Deterministic" estimation (everything will go perfectly) to "Probabilistic" estimation (what are the P10, P50, P90 scenarios based on historical friction).

## How does it work?

### Key Logic Flow in `render_estimator(df, models, context)`
1.  **Input Form:**
    -   Takes inputs from the Sidebar (State, Vendor, LWE risk).
    -   User enters a "Project Start Date".
2.  **WBS Generation:**
    -   Calls `logic.get_wbs_template_from_data` to get the standard list of tasks for the selected project type.
    -   Displays this in an editable `st.data_editor`.
3.  **Feature Engineering (The "Magic"):**
    -   It creates a feature row for *each task*.
    -   **Crucial Step:** It calculates if a specific task hits the **Monsoon Season** (June-Sept) based on its planned start date. This is dynamic.
4.  **Prediction Loop:**
    -   It iterates through every task and asks the AI Model: *"Given this task is in Jharkhand (High Friction) + Monsoon + Tier 3 Vendor, how long will it take?"*
    -   It does this for P10 (Optimistic), P50 (Realistic), and P90 (Pessimistic) scenarios.
5.  **Critical Path Calculation:**
    -   It takes the P50 predictions and uses `logic.calculate_cpm` to sequence them.
    -   It identifies which tasks are "Critical" (cannot be delayed).
6.  **Visualization:**
    -   **Gantt Chart:** Draws the timeline using Plotly.
    -   Uses `try-except` blocks around Graphviz rendering, falling back gracefully with warnings instead of crashing if host dependencies are missing.
