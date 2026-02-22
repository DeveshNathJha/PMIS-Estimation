# Risk Audit UI (`app/ui/risk_audit.py`)

## What is it?
The **Risk Audit** is the historical analysis module. It looks at the *past* projects in the dataset to identify systemic patterns of failure.

## Why is it needed?
To prevent future mistakes, we must understand past ones. This module answers questions like: *"Is Latehar district always delayed?"* or *"Do Tier 3 vendors fail during Monsoons?"*

## How does it work?

### Key Components

1.  **Filters:**
    -   Allows filtering the historical data by State, Vendor, or Project Type.

2.  **Visualizations (Plotly):**
    -   **Distribution Plots:** Histograms showing Predicted vs. Actual durations. If the "Actual" curve is shifted right, it means consistent delays.
    -   **Box Plots:** Comparison of Vendor Performance. Shows the spread (uncertainty) of different vendors.

3.  **Risk Factor Analysis:**
    -   This mimics a "SHAP" (SHapley Additive exPlanations) analysis but simplified.
    -   It calculates the average delay contributed by specific factors (e.g., "Tasks in Monsoon take +22% longer on average").

4.  **"Root Cause" Table:**
    -   Displays a detailed table of past "Bad" projects (High Delay).
    -   Uses `logic.generate_granular_risk_assessment` to auto-tag the causes for each row (e.g., "LWE + Land Issue").
