# Shared UI Components & Reports (`app/ui/components.py`, `app/ui/reports.py`)

## What are they?
These are the helper modules. `components.py` handles the reusable visual elements (Sidebar, CSS styling), and `reports.py` handles the PDF generation.

## Why are they needed?
1.  **D.R.Y. (Don't Repeat Yourself):** Instead of writing the CSS or Sidebar code in every page, we write it once here.
2.  **Corporate Identity:** This ensures the "Firm Blue" branding and styling is consistent across the entire app.
3.  **PDF Reports:** Professional PDF generation is complex; isolating it keeps the main app logic clean.

## How do they work?

### `app/ui/components.py`
-   **`inject_custom_css()`**: Injects raw HTML `<style>` blocks to override Streamlit's default look (e.g., dark mode sidebar, specific font colors).
-   **`render_sidebar(jharkhand_map, df)`**:
    -   Draws the common inputs (District, Vendor Tier).
    -   Handles the logic for switching between "Generic National Mode" and "Jharkhand Specific Mode".
    -   Returns a dictionary `context` containing all user selections.

### `app/ui/reports.py`
-   **Library:** Uses `fpdf` (a Python library for creating PDFs).
-   **Class `PDFReport`**: Inherits from `FPDF` to define a custom Header/Footer with the "Strategic Advisory" logo.
-   **Function `generate_pdf_report(...)`**:
    -   Takes the *Inputs* and *Predictions*.
    -   Constructs a formatted PDF with sections for "Executive Summary", "AI Forecast", "Critical Path".
    -   Embeds the Network Diagram image (if generated).
    -   Returns the binary bytes of the PDF for download.
