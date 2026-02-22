# Modification & Maintenance Guide
*Where to change things if you need to modify the Project.*

This document maps common "I want to change X" requests to the specific files you need to edit.

## 1. Quick Reference Map

| If you want to change... | Go to File... | Specifically... |
| :--- | :--- | :--- |
| **Colors / Branding** | `config.py` | Search for `FIRM_BLUE`, `DARK_BG_COLOR` |
| **Project Types (Add New)** | `config.py` | Update `PROJECT_TEMPLATES` dictionary |
| **State / District Risks** | `config.py` | Update `STATE_PROFILE` or `JHARKHAND_MAP` |
| **Logic (Risk Formulas)** | `app/core/logic.py` | Edit `generate_granular_risk_assessment` |
| **Sidebar Options** | `app/ui/components.py` | Edit `render_sidebar` function |
| **PDF Report Format** | `app/ui/reports.py` | Edit `generate_pdf_report` function |
| **Simulated "Physics"** | `scripts/data_generation.py` | Edit `calculate_friction` function |

---

## 2. Common Modification Scenarios

### Scenario A: Adding a New Project Type (e.g., "Bridge Construction")
*You want the app to support a new type of project.*

1.  **Open `config.py`**.
2.  Find `PROJECT_TEMPLATES`.
3.  Add a new entry:
    ```python
    'Construction_Bridge': [
        ('Design', 60, 'Technical'),
        ('Piling', 90, 'Civil'),
        ('Deck Slab', 60, 'Civil'),
        ('Handover', 10, 'Admin')
    ],
    ```
4.  **Important:** You must **Regenerate Data** and **Retrain Model** for the AI to learn about this new project type (see Section 3).

### Scenario B: Changing the Risk Logic
*You think the "Monsoon" logic is too harsh or too weak.*

1.  **For Simulation (Training Data):**
    -   Open `scripts/data_generation.py`.
    -   Find `calculate_friction`.
    -   Change the multiplier (e.g., change `friction *= 1.5` to `1.2`).
2.  **For Explanation (App Text):**
    -   Open `app/core/logic.py`.
    -   Find `generate_granular_risk_assessment`.
    -   Update the text or the condition triggering the "Monsoon" blame.

### Scenario C: Updating District Security Risks
*A district is no longer LWE affected.*

1.  **Open `config.py`**.
2.  Find `JHARKHAND_MAP`.
3.  Change `"LWE": 1` to `"LWE": 0` for that district.

---

## 3. Maintenance: When to Run Scripts?

You do **NOT** need to run scripts for simple UI changes (colors, text, logic).
You **MUST** run scripts if you change **Data Definitions** (Projects, Districts, Friction logic).

### Routine Maintenance Workflow
If you added a new Project Template or changed Risk Factors:

1.  **Step 1: Regenerate History**
    ```bash
    python3 scripts/data_generation.py --count 2000
    ```
    *Why? To create a new history that includes your new project type.*

2.  **Step 2: Retrain Brain**
    ```bash
    python3 scripts/train_production_model.py
    ```
    *Why? The AI file (`pmis_model.pkl`) needs to learn the patterns from the new data.*

3.  **Step 3: Restart App**
    *Reload the Streamlit page to load the new config and model.*
