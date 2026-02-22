from fpdf import FPDF
from datetime import datetime
import os

class PDFReport(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 14)
        self.set_text_color(0, 51, 141)
        self.cell(0, 10, 'Strategic Advisory | Project Estimation Report', 0, 1, 'C')
        self.ln(5)

def generate_pdf_report(project_name, location, p10, p50, p90, critical_path, diagram_path=None, phase_summary=None):
    pdf = PDFReport()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 12)
    pdf.set_fill_color(240, 240, 240)
    pdf.set_text_color(0)
    pdf.cell(0, 10, "1. Executive Summary", 1, 1, 'L', 1)
    
    pdf.set_font("Arial", '', 10)
    pdf.ln(2)
    pdf.cell(0, 8, f"Project: {project_name}", 0, 1)
    pdf.cell(0, 8, f"Location: {location}", 0, 1)
    pdf.cell(0, 8, f"Date: {datetime.now().strftime('%d-%b-%Y')}", 0, 1)
    pdf.ln(5)
    
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "2. AI Forecast", 1, 1, 'L', 1)
    pdf.ln(2)
    pdf.set_font("Arial", '', 10)
    pdf.cell(0, 10, f"Optimistic (P10): {p10} Days", 0, 1)
    pdf.cell(0, 10, f"Realistic (P50): {p50} Days", 0, 1)
    pdf.cell(0, 10, f"Pessimistic (P90): {p90} Days", 0, 1)
    
    pdf.ln(5)
    # Phase-level summary if provided
    if phase_summary is not None:
        try:
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(0, 10, "2.a Phase Summaries", 1, 1, 'L', 1)
            pdf.set_font("Arial", '', 10)
            for row in phase_summary:
                # each row: (phase, planned_sum, predicted_sum)
                phase, planned_sum, pred_sum = row
                diff = int(pred_sum - planned_sum)
                # Avoid non-latin characters
                pdf.cell(0, 8, f"Phase: {phase} | Planned: {int(planned_sum)}d | Predicted: {int(pred_sum)}d | Delta {diff}d", 0, 1)
            pdf.ln(5)
        except Exception:
            pass
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "3. Critical Path", 1, 1, 'L', 1)
    pdf.set_font("Arial", '', 10)
    pdf.multi_cell(0, 8, f"Tasks IDs: {', '.join(critical_path)}")
    
    if diagram_path and os.path.exists(diagram_path):
        pdf.add_page()
        pdf.image(diagram_path, x=10, w=190)
    
    return pdf.output(dest='S').encode('latin-1', errors='replace')
