# Data Generation Script (`scripts/data_generation.py`)

## What is it?
This is the **Simulation Engine**. It generates the synthetic dataset (`data/synthetic_project_data.csv`) used to train the AI model.

## Why is it needed?
Real-world infrastructure data is sensitive and hard to get. To demonstrate the PMIS capabilities, we need a realistic "proxy" dataset that reflects the actual challenges (Monsoon delays, LWE risks) without exposing client data.

## How does it work?

### The "Physics" Engine
It doesn't just output random numbers. It simulates a project's life:
1.  **Base Case:** Retrieves the "Planned Duration" from the standard template (in `config.py`).
2.  **Applies Friction:**
    -   **Geography:** Multiplies duration by `config.STATE_PROFILE[state]['logistics_friction']` (e.g., 1.5x for Hilly areas).
    -   **Vendor:** Multiplies by 0.85 (Tier 1) or 1.3 (Tier 3).
    -   **Security:** Adds +40% if the district has `LWE=1`.
3.  **Event Injection:**
    -   Randomly decides if a "Land Acquisition Issue" occurs (based on probabilities).
    -   Determines if the task happens during Monsoon season.
4.  **Result:** Calculates `Actual_Duration` = `Planned` * `Friction` + `Events`.

### Key Output
A CSV file containing thousands of these simulated projects, which the AI then "reads" to learn the patterns we just simulated.
