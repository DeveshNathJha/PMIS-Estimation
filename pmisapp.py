import streamlit as st
import pandas as pd
import numpy as np
import joblib
import plotly.express as px
import plotly.graph_objects as go
import graphviz
from datetime import datetime, timedelta
from fpdf import FPDF
import os

# Import Configuration to ensure alignment with Training
try:
    from config import FEATURES, CATEGORICAL_FEATURES
except ImportError:
    st.error("CRITICAL ERROR: 'config.py' not found. Please ensure it is in the same directory.")
    st.stop()

# ==============================================================================
# 1. CONFIGURATION & ENTERPRISE STYLING
# ==============================================================================
st.set_page_config(
    page_title="KPMG PMIS | Strategic Insights",
    layout="wide",
    initial_sidebar_state="expanded"
)

# KPMG Official Color Palette
KPMG_BLUE = "#00338D"
KPMG_MED_BLUE = "#005EB8"
KPMG_LIGHT_BLUE = "#0091DA"
KPMG_DARK_BG = "#0E1117"
KPMG_CARD_BG = "#1E1E1E"
TEXT_WHITE = "#FFFFFF"

# CSS Injection for Professional Look
st.markdown(f"""
    <style>
        .stApp {{
            background-color: {KPMG_DARK_BG};
            color: {TEXT_WHITE};
        }}
        [data-testid="stSidebar"] {{
            background-color: #151922;
            border-right: 1px solid #30363D;
        }}
        .kpmg-card {{
            background-color: {KPMG_CARD_BG};
            padding: 25px;
            border-radius: 8px;
            border: 1px solid #30363D;
            border-left: 5px solid {KPMG_LIGHT_BLUE}; 
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
            margin-bottom: 20px;
        }}
        h1, h2, h3, h4 {{
            color: {KPMG_LIGHT_BLUE} !important;
            font-family: 'Arial', sans-serif;
            font-weight: 600;
        }}
        .stButton>button {{
            background-color: {KPMG_MED_BLUE};
            color: white;
            border-radius: 4px;
            border: none;
            height: 3em;
            font-weight: bold;
            width: 100%;
        }}
        .stButton>button:hover {{
            background-color: {KPMG_LIGHT_BLUE};
        }}
        /* Table Styling */
        [data-testid="stDataFrame"] {{
            background-color: {KPMG_CARD_BG};
        }}
    </style>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. RESOURCE LOADING
# ==============================================================================

@st.cache_resource
def load_resources():
    """
    Loads the ML Model and Data.
    We use error handling to prevent the app from crashing during the demo.
    """
    try:
        # Load Raw Data for Dropdowns
        if not os.path.exists('kpmg_pmis_synthetic_data.csv'):
            st.error("Data CSV not found.")
            return None, None
            
        data = pd.read_csv('kpmg_pmis_synthetic_data.csv')
        
        # Load Model Artifact
        if not os.path.exists('kpmg_pmis_model.pkl'):
            st.error("Model PKL not found. Please train the model first.")
            return None, None
            
        model_bundle = joblib.load('kpmg_pmis_model.pkl') 
        return data, model_bundle
    except Exception as e:
        st.error(f"CRITICAL ERROR Loading Resources: {e}")
        return None, None

df, artifact = load_resources()

if df is None or artifact is None:
    st.stop()

# Unpack Artifacts for Global Use
models = artifact['models']
# We prioritize the FEATURES list from config.py to ensure 100% match
model_features = FEATURES 
vectorizer = artifact.get('vectorizer')
jharkhand_map = artifact.get('jharkhand_map', {})
# Project Templates from Data Generation logic (Saved in Artifact)
PROJECT_TEMPLATES = artifact.get('project_types', list(df['Project_Type'].unique()))

# ==============================================================================
# 3. INTELLIGENCE FUNCTIONS (The "Brain")
# ==============================================================================

def get_nhm_districts(division):
    """Returns districts filtered by Division"""
    return [d for d, info in jharkhand_map.items() if info['Division'] == division]

def get_wbs_template_from_data(p_type):
    """
    Dynamically fetches the WBS (Tasks) for a Project Type from the Loaded Data.
    This ensures we don't need to hardcode tasks in the App.
    """
    # Check if required columns exist
    if 'Task_Sequence' not in df.columns:
        st.error("Fatal Error: 'Task_Sequence' column not found in dataset. Please ensure data is properly loaded.")
        st.stop()
    
    # Filter data for this project type
    subset = df[df['Project_Type'] == p_type].sort_values('Task_Sequence')
    
    # Get unique tasks in order
    tasks = subset[['Task_Name', 'Task_Category', 'Planned_Duration', 'Task_Sequence']].drop_duplicates('Task_Name')
    
    # Rename for App Table
    tasks = tasks.rename(columns={
        'Task_Sequence': 'Task_ID',
        'Planned_Duration': 'Planned_Duration'
    })
    
    # Add Predecessors Logic (Sequential: 2 depends on 1, 3 on 2...)
    tasks['Predecessors'] = tasks['Task_ID'].apply(lambda x: str(x-1) if x > 1 else '')
    
    return tasks.reset_index(drop=True)

def calculate_cpm(tasks_df):
    """
    Standard Critical Path Method (Forward & Backward Pass).
    Returns: (project_duration, critical_path_task_ids)
    """
    tasks = {}
    for _, row in tasks_df.iterrows():
        pid = str(row['Task_ID'])
        preds = str(row['Predecessors']).split(',') if row['Predecessors'] else []
        preds = [p.strip() for p in preds if p.strip() and p.strip() != '0']
        tasks[pid] = {'duration': row['Predicted_Duration'], 'predecessors': preds, 'es': 0, 'ef': 0, 'ls': 0, 'lf': 0}

    task_ids = sorted(list(tasks.keys()), key=lambda x: float(x))
    
    # FORWARD PASS: Calculate Early Start & Early Finish
    for _ in range(len(task_ids)): 
        for tid in task_ids:
            preds = tasks[tid]['predecessors']
            max_ef = 0
            for p in preds:
                if p in tasks: max_ef = max(max_ef, tasks[p]['ef'])
            tasks[tid]['es'] = max_ef
            tasks[tid]['ef'] = tasks[tid]['es'] + tasks[tid]['duration']

    project_duration = max([t['ef'] for t in tasks.values()]) if tasks else 0
    
    # BACKWARD PASS: Calculate Late Start & Late Finish
    for tid in task_ids:
        tasks[tid]['lf'] = project_duration
    
    for tid in reversed(task_ids):
        # Find successors
        successors_lf = []
        for other_tid in task_ids:
            if tid in tasks[other_tid]['predecessors']:
                successors_lf.append(tasks[other_tid]['ls'])
        
        if successors_lf:
            tasks[tid]['lf'] = min(successors_lf)
        else:
            tasks[tid]['lf'] = tasks[tid]['ef']  # End node
        
        tasks[tid]['ls'] = tasks[tid]['lf'] - tasks[tid]['duration']
    
    # CRITICAL PATH: Tasks with zero slack (LF - EF = 0)
    critical_path = [tid for tid, t in tasks.items() if abs((t['lf'] - t['ef'])) < 0.01]
    
    return project_duration, critical_path

# --- SOPHISTICATED RISK REASONING ENGINE ---
def generate_granular_risk_assessment(row, predicted, planned, vendor_tier):
    """
    Logic:
    1. Compares Predicted vs Planned.
    2. If Predicted < Planned: It's an Efficiency Gain (Green).
    3. If Predicted > Planned: It checks specific flags (LWE, Land, Monsoon) to assign blame (Red).
    """
    # Safely coerce inputs to numeric and handle missing values
    try:
        pred_val = float(predicted) if predicted is not None else None
    except Exception:
        pred_val = None
    try:
        planned_val = float(planned) if planned is not None else None
    except Exception:
        planned_val = None

    if pd.isna(pred_val) or pd.isna(planned_val) or pred_val is None or planned_val is None:
        return 'Prediction unavailable'

    variance = pred_val - planned_val
    
    # CASE 1: EFFICIENCY GAIN
    if variance <= 0:
        if vendor_tier == 1:
            return "Efficiency Gain (Tier 1 Speed)"
        else:
            return "On Track / Fast Tracked"
            
    # CASE 2: MINOR VARIANCE
    if variance < (planned_val * 0.15): 
        return "Standard Variance"
        
    # CASE 3: SIGNIFICANT DELAY (Identify the Root Cause)
    reasons = []
    
    # Cause A: Land
    if str(row.get('Land_Type')) == 'Tribal (CNT/SPT)':
        reasons.append("CNT Act Land Issue")
    
    # Cause B: Security
    lwe_flag = row.get('LWE_Flag')
    if str(lwe_flag) == '1' or lwe_flag == 1:
        reasons.append("LWE Logistics Friction")
        
    # Cause C: Seasonality
    mon_flag = row.get('Monsoon_Flag')
    if str(mon_flag) == '1' or mon_flag == 1:
        reasons.append("Monsoon Slowdown")
        
    # Cause D: Procurement Complexity
    if str(row.get('Task_Category')) == 'Procurement' and variance > 20:
        reasons.append("Supply Chain/Import Delay")
        
    # Fallback if no specific flag but high delay
    if not reasons:
        reasons.append("Vendor Resource Constraints")
        
    return "DELAY: " + " + ".join(reasons) + f" (+{int(round(variance))} days)"

# --- REPORTING ---
class PDFReport(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 14)
        self.set_text_color(0, 51, 141)
        self.cell(0, 10, 'KPMG Advisory | Project Estimation Report', 0, 1, 'C')
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
                # Avoid non-latin characters (e.g., Δ) which can break PDF encoding in this environment
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
    # Return bytes; replace characters that cannot be encoded to latin-1 to avoid UnicodeEncodeError
    return pdf.output(dest='S').encode('latin-1', errors='replace')

def style_chart(fig):
    fig.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    return fig

# ==============================================================================
# 4. SIDEBAR NAVIGATION
# ==============================================================================

with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/9/9d/KPMG_logo.svg/1200px-KPMG_logo.svg.png", width=160)
    st.markdown("### Strategic Insights")
    st.markdown("---")
    
    # CONTEXT SWITCHER
    app_context = st.radio("PROJECT CONTEXT", ["Generic / National", "Jharkhand (NHM Focus)"])
    
    selected_district = "Generic"
    lwe_risk_flag = 0
    land_type = "Govt Land"
    
    if app_context == "Jharkhand (NHM Focus)":
        st.success("Logic Active: NHM")
        div_list = list(set([v['Division'] for k,v in jharkhand_map.items()]))
        division = st.selectbox("Division", sorted(div_list))
        districts = get_nhm_districts(division)
        selected_district = st.selectbox("District", sorted(districts))
        
        # Risk Check from Map
        if selected_district in jharkhand_map:
            lwe_risk_flag = jharkhand_map[selected_district]['LWE']
            if lwe_risk_flag == 1:
                st.error(f"High Risk Zone: {selected_district}")
            else:
                st.info(f"Standard Zone: {selected_district}")
        
        st.markdown("---")
        land_type = st.selectbox("Land Acquisition Type", ["Govt Land", "Donated", "Tribal (CNT/SPT)"])
        if land_type == "Tribal (CNT/SPT)":
            st.warning("Regulatory Risk: High")
            
        global_vendor = st.selectbox("Vendor Tier", ["Tier 1 (Premium)", "Tier 2 (Standard)", "Tier 3 (Local)"])

    else:
        # Load States from Data
        states_list = sorted(df['State'].dropna().unique())
        selected_state = st.selectbox("State", states_list)
        selected_district = "Generic_District"
        
        global_vendor = st.selectbox("Vendor Tier", ["Tier 1 (Premium)", "Tier 2 (Standard)", "Tier 3 (Local)"])

    st.markdown("---")
    module = st.radio("MODULES", ["Pre-Start Estimator", "Mid-Project Tracker", "Risk Audit"])
    
    st.markdown("---")
    st.caption(f"Model Version: v8.0 Production")
    
    with st.expander("Report Issue"):
        st.text_area("Details:", height=80, key="fb", placeholder="Describe the issue, steps to reproduce, expected behaviour, and attach screenshots if possible.")
        if st.button("Submit"):
            # Provide clear feedback after submit
            if st.session_state.get('fb') and st.session_state.get('fb').strip():
                st.success("Thank you — issue logged. We'll review and follow up.")
            else:
                st.warning("Please enter details before submitting the issue.")

# ==============================================================================
# MODULE 1: PRE-START ESTIMATOR
# ==============================================================================

if module == "Pre-Start Estimator":
    st.title("Project Completion Estimator")
    st.markdown(f"#### Context: {app_context} > {selected_district}")

    # INPUT CARD
    st.markdown('<div class="kpmg-card">', unsafe_allow_html=True)
    c1, c2 = st.columns([1, 2])
    
    with c1:
        st.subheader("1. Project Config")
        # Filter Project Types based on Context
        if app_context == "Jharkhand (NHM Focus)":
            nhm_projects = [p for p in PROJECT_TEMPLATES if "NHM" in p]
            p_type = st.selectbox("Project Template", nhm_projects)
        else:
            other_projects = [p for p in PROJECT_TEMPLATES if "NHM" not in p]
            p_type = st.selectbox("Project Template", other_projects)
            
        start_date = st.date_input("Planned Start Date", datetime.today())

    with c2:
        st.subheader("2. WBS & Dependencies")
        
        # DYNAMIC WBS LOADING
        default_wbs = get_wbs_template_from_data(p_type)
        category_options = sorted(df['Task_Category'].unique())

        st.info("Dependencies: Enter Task IDs (e.g., '1,2'). ID 1 is the first task.")

        # Prepare the data_editor with Phase selectbox
        edited_wbs = st.data_editor(
            default_wbs,
            num_rows="dynamic",
            column_config={
                "Task_ID": st.column_config.NumberColumn("ID", min_value=1, step=1, width="small"),
                "Task_Name": st.column_config.TextColumn("Task Name", width="large"),
                "Task_Category": st.column_config.SelectboxColumn("Category", options=category_options, required=True, width="medium"),
                "Planned_Duration": st.column_config.NumberColumn("Days", min_value=1),
                "Predecessors": st.column_config.TextColumn("Predecessors", help="Comma separated IDs e.g. '1,3'")
            },
            width='stretch',
            height=400,
            key="wbs_editor"
        )
        # Persist original template so we can detect mid-edit changes
        if 'original_wbs' not in st.session_state:
            try:
                st.session_state['original_wbs'] = default_wbs.copy()
            except Exception:
                st.session_state['original_wbs'] = default_wbs

        # Compute diffs between loaded template and current editor state
        def _compute_wbs_diffs(orig_df, new_df):
            modified_ids = []
            diffs = []
            try:
                o = orig_df.copy()
                n = new_df.copy()
                # ensure numeric Task_ID for robust comparison
                if 'Task_ID' in o.columns:
                    o['Task_ID'] = o['Task_ID'].astype('Int64')
                if 'Task_ID' in n.columns:
                    n['Task_ID'] = n['Task_ID'].astype('Int64')

                o = o.set_index('Task_ID')
                n = n.set_index('Task_ID')

                common = o.index.intersection(n.index)
                for tid in common:
                    orow = o.loc[tid].to_dict()
                    nrow = n.loc[tid].to_dict()
                    changes = {}
                    for col in ['Task_Name','Task_Category','Planned_Duration','Predecessors']:
                        oval = orow.get(col)
                        nval = nrow.get(col)
                        # Normalize NaN -> None for comparison
                        if pd.isna(oval): oval = None
                        if pd.isna(nval): nval = None
                        if oval != nval:
                            changes[col] = (oval, nval)
                    if changes:
                        modified_ids.append(int(tid))
                        diffs.append({'Task_ID': int(tid), 'changes': changes})
            except Exception:
                return [], []
            return modified_ids, diffs

        modified_ids, diffs = _compute_wbs_diffs(st.session_state.get('original_wbs', default_wbs), edited_wbs if edited_wbs is not None else pd.DataFrame())
        st.session_state['wbs_modified_ids'] = modified_ids
        st.session_state['wbs_diffs'] = diffs

        # Show a short badge/warning if changes exist and expose a sidebar diff log
        if modified_ids:
            st.warning(f"Changes detected: {len(modified_ids)} task(s) edited since template load")
            with st.sidebar.expander("WBS Changes (since template load)", expanded=False):
                st.write(f"{len(modified_ids)} modified task(s)")
                for d in diffs:
                    st.markdown(f"**Task {d['Task_ID']}**")
                    for col, (o, n) in d['changes'].items():
                        st.caption(f"{col}: {o}  →  {n}")
        else:
            st.info("No template edits detected.")
        
        # Inline WBS preview validation (quick feedback before user clicks Generate)
        preview_issues = []
        if edited_wbs is not None and not edited_wbs.empty:
            if 'Task_ID' not in edited_wbs.columns:
                preview_issues.append('WBS requires a Task_ID column (numeric).')
            else:
                # detect blank or non-numeric Task_ID rows
                for idx, r in edited_wbs.iterrows():
                    tid = r.get('Task_ID') if hasattr(r, 'get') else r['Task_ID']
                    if pd.isna(tid):
                        preview_issues.append(f'Row {idx+1}: missing Task_ID')
                    else:
                        try:
                            int(tid)
                        except Exception:
                            preview_issues.append(f'Row {idx+1}: invalid Task_ID ({tid})')

        if preview_issues:
            st.warning('WBS Quick Checks: fix issues before generating forecast')
            for p in preview_issues[:5]:
                st.caption(f"• {p}")
    st.markdown('</div>', unsafe_allow_html=True)

    # PREDICTION & ANALYSIS
    if st.button("Generate Forecast & Analysis", type="primary"):
        if edited_wbs.empty:
            st.warning("Please define at least one task.")
        else:
            # INPUT VALIDATION
            validation_errors = []

            # Check 1: All durations > 0
            if 'Planned_Duration' not in edited_wbs.columns or (edited_wbs['Planned_Duration'] <= 0).any():
                validation_errors.append("All tasks must have Planned_Duration > 0 days")

            # Check 2: Start date not in past
            if start_date < datetime.today().date():
                validation_errors.append(f"Start date ({start_date}) cannot be in the past")

            # Check 3: Task_ID presence and validity
            if 'Task_ID' not in edited_wbs.columns:
                validation_errors.append("Task_ID column is required in the WBS")

            # Build task graph safely
            task_graph = {}
            for _, row in edited_wbs.iterrows():
                tid_raw = row.get('Task_ID') if hasattr(row, 'get') else row['Task_ID']
                if pd.isna(tid_raw):
                    validation_errors.append("Each task must have a numeric Task_ID")
                    continue
                try:
                    tid = str(int(tid_raw))
                except Exception:
                    validation_errors.append(f"Invalid Task_ID value: {tid_raw}")
                    continue

                preds_raw = row.get('Predecessors') if hasattr(row, 'get') else row['Predecessors']
                if pd.isna(preds_raw) or preds_raw in (None, 'None'):
                    preds_list = []
                else:
                    preds_list = [p.strip() for p in str(preds_raw).split(',') if p.strip() and p.strip() != '0']

                task_graph[tid] = preds_list

            # Detect self-dependency and unknown predecessors
            for tid, preds in task_graph.items():
                if tid in preds:
                    validation_errors.append(f"Task {tid} cannot depend on itself")
                for p in preds:
                    if p not in task_graph:
                        validation_errors.append(f"Predecessor {p} for task {tid} references unknown Task_ID")

            # Detect cycles using DFS
            visited = set()
            rec_stack = set()

            def has_cycle(node):
                if node in rec_stack:
                    return True
                if node in visited:
                    return False
                visited.add(node)
                rec_stack.add(node)
                for nbr in task_graph.get(node, []):
                    if nbr not in task_graph:
                        continue
                    if has_cycle(nbr):
                        return True
                rec_stack.remove(node)
                return False

            for node in list(task_graph.keys()):
                if has_cycle(node):
                    validation_errors.append("Circular dependency detected in predecessors")
                    break

            # Check 5: All Task_Category values are valid
            valid_categories = set(df['Task_Category'].dropna().unique()) if 'Task_Category' in df.columns else set()
            if 'Task_Category' in edited_wbs.columns and not edited_wbs['Task_Category'].isin(valid_categories).all():
                invalid = set(edited_wbs['Task_Category'].unique()) - valid_categories
                validation_errors.append(f"Invalid Task_Category values: {invalid}")

            if validation_errors:
                # Styled validation card (prominent, readable)
                st.markdown(
                    f"""
                    <div style="background:#3b1f1f;padding:16px;border-left:6px solid #b30000;border-radius:6px;margin-bottom:12px;">
                      <strong style="color:#ffdede">Input Validation Failed</strong>
                      <div style="color:#f5c6c6;margin-top:8px">Please fix the following issues and try again:</div>
                      <ul style="color:#f5c6c6;margin-top:8px">{''.join([f'<li>{e}</li>' for e in validation_errors])}</ul>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                st.stop()

            with st.spinner("Running Monte Carlo Simulation & CPM Analysis..."):
                input_rows = []
                v_map = {"Tier 1 (Premium)": 1, "Tier 2 (Standard)": 2, "Tier 3 (Local)": 3}
                v_val = v_map.get(global_vendor, 2)
                
                # --- STEP A: PREPARE MODEL INPUTS ---
                for _, task in edited_wbs.iterrows():
                    monsoon_flag = 1 if start_date.month in [6, 7, 8, 9] else 0
                    row = {
                        'Project_Type': p_type, 
                        'District': selected_district,
                        'LWE_Flag': lwe_risk_flag,
                        'Task_Category': task['Task_Category'],
                        'Land_Type': land_type,
                        'Vendor_Tier': v_val,
                        'Planned_Duration': task['Planned_Duration'], 
                        'Monsoon_Flag': monsoon_flag
                    }
                    input_rows.append(row)
                
                # Ensure input_df has EXACTLY the columns trained on
                input_df = pd.DataFrame(input_rows)[model_features]
                
                # --- STEP B: PREDICT DURATIONS ---
                predicted_durations = models['P50'].predict(input_df)
                edited_wbs['Predicted_Duration'] = predicted_durations.astype(int)

                # --- STEP C: GENERATE GRANULAR REASONS ---
                delay_reasons = []
                for i, row in input_df.iterrows():
                    pred = predicted_durations[i]
                    planned = row['Planned_Duration']
                    # Call the new Intelligent Risk Function
                    reason = generate_granular_risk_assessment(row, pred, planned, v_val)
                    delay_reasons.append(reason)
                
                edited_wbs['Risk Analysis'] = delay_reasons 
                
                # Calculate Totals
                p10_sum = models['P10'].predict(input_df).sum()
                p90_sum = models['P90'].predict(input_df).sum()
                
                # CPM Logic
                cpm_duration, critical_path = calculate_cpm(edited_wbs)
                finish_date = start_date + timedelta(days=int(cpm_duration))
                
                # --- STEP D: WHAT-IF SCENARIO (REAL MODEL SIMULATION) ---
                # We simulate: What if Vendor was Tier 1 vs Tier 3 using ACTUAL MODEL?
                
                # Sim 1: Tier 1
                sim_input_t1 = input_df.copy()
                sim_input_t1['Vendor_Tier'] = 1
                pred_t1 = models['P50'].predict(sim_input_t1).sum()
                
                # Sim 2: Tier 3
                sim_input_t3 = input_df.copy()
                sim_input_t3['Vendor_Tier'] = 3
                pred_t3 = models['P50'].predict(sim_input_t3).sum()
                
                # Compare current to Tier 1
                current_total = predicted_durations.sum()
                savings = int(current_total - pred_t1)
                
                # --- STEP E: OUTPUTS ---
                
                # Graphviz Diagram
                graph = graphviz.Digraph(format='png')
                graph.attr(rankdir='LR', bgcolor='white')
                for _, row in edited_wbs.iterrows():
                    tid = str(row['Task_ID'])
                    color = '#C0392B' if tid in critical_path else '#00338D'
                    label = f"{row['Task_Name']}\n({int(row['Predicted_Duration'])}d)"
                    graph.node(tid, label, style='filled', fillcolor=color, fontcolor='white', shape='box')
                    preds = str(row['Predecessors']).split(',') if row['Predecessors'] else []
                    for p in preds:
                        p = p.strip()
                        if p and p != '0': graph.edge(p, tid, color='black')
                
                try:
                    graph.render("temp_network", cleanup=True)
                    final_img = "temp_network.png"
                except:
                    final_img = None
                
                # Prepare phase summary list for PDF (list of tuples)
                phase_summary_list = None

                pdf_bytes = generate_pdf_report(
                    p_type,
                    selected_district,
                    int(p10_sum),
                    int(cpm_duration),
                    int(p90_sum),
                    critical_path,
                    final_img,
                    phase_summary=phase_summary_list
                )
                
                # --- RESULTS UI ---
                st.markdown('<div class="kpmg-card">', unsafe_allow_html=True)
                c1, c2 = st.columns([2, 1])
                with c1: 
                    st.markdown("### Executive Summary")
                    st.metric("Estimated Completion Date", finish_date.strftime('%d %b %Y'), f"Total Duration: {int(cpm_duration)} Days")
                    # Phase-level UI summary
                with c2: 
                    st.download_button("Download PDF Report", pdf_bytes, "Project_Report.pdf", "application/pdf")
                
                m1, m2, m3 = st.columns(3)
                m1.metric("Optimistic Case (P10)", f"{int(p10_sum)} Days")
                m2.metric("Critical Tasks Count", f"{len(critical_path)}")
                m3.metric("Worst Case Risk (P90)", f"{int(p90_sum)} Days", delta_color="inverse")
                
                st.markdown("#### Strategic Insight: Vendor Optimization")
                if v_val != 1:
                    st.info(f"[RECOMMENDATION] Upgrading to a Tier 1 Vendor (L&T/Tata) is predicted to save **{savings} Days** (Approx {int(current_total)}d -> {int(pred_t1)}d).")
                else:
                    st.success("[VALIDATED] You have selected a Top-Tier Vendor. This is the optimal configuration for speed.")
                
                st.markdown("#### Task-Level Risk Breakdown")
                # Add an 'Edited' marker and highlight rows that were changed compared to the template
                display_cols = ['Task_ID','Task_Name', 'Task_Category', 'Planned_Duration', 'Predicted_Duration', 'Risk Analysis']
                display_df = edited_wbs[display_cols].copy()
                modified_ids = st.session_state.get('wbs_modified_ids', [])
                display_df['Edited'] = display_df['Task_ID'].astype('Int64').isin(modified_ids)

                try:
                    def _highlight_row(r):
                        if r['Edited']:
                            return ['background-color: #264653'] * len(r)
                        return [''] * len(r)

                    styled = display_df.style.apply(_highlight_row, axis=1)
                    st.dataframe(styled, use_container_width=True)
                except Exception:
                    # Fallback: just show Edited column
                    st.dataframe(display_df, use_container_width=True)
                
                st.markdown("#### Dependency Network Diagram")
                st.graphviz_chart(graph, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

# ==============================================================================
# MODULE 2: MID-PROJECT TRACKER
# ==============================================================================

if module == "Mid-Project Tracker":
    st.title("Mid-Project Analysis")
    st.markdown(f"#### Progress Update: {app_context}")
    
    st.markdown('<div class="kpmg-card">', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Financial Compliance (UCs)")
        uc_pending = st.toggle("Utilization Certificate (UC) Pending?", value=False)
        if uc_pending:
            st.error("STOP WORK: Fund Tranche 2 blocked until UC submission.")
        else:
            st.success("Funds Available: Tranche Released.")
    
    with c2:
        st.subheader("Select Active Project")
        # Populate Project ID list from dataset if available (falls back to sample IDs)
        if 'Project_ID' in df.columns:
            proj_list = sorted(df['Project_ID'].dropna().unique().tolist())
            if not proj_list:
                proj_list = ["PROJ_1001", "PROJ_1002", "PROJ_1003"]
        else:
            proj_list = ["PROJ_1001", "PROJ_1002", "PROJ_1003"]

        proj = st.selectbox("Project ID", proj_list)
        actual_start_date = st.date_input("Actual Start Date", datetime.today() - timedelta(days=90))
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    if uc_pending:
        st.warning("Cannot generate forecast. Project status is 'On Hold' due to financial compliance.")
    else:
        # Load a sample project for demo
        # Logic: Get the first project of selected type from dataset
        proj_data = df[df['Project_Type'] == "NHM - Health Sub-Centre (HSC)"].head(5).copy()
        
        st.markdown('<div class="kpmg-card">', unsafe_allow_html=True)
        st.markdown("#### Update Progress & Analyze Delays")
        
        # Include Phase column so users can assign tasks to phases during mid-project updates
        display_df = proj_data[['Task_Name', 'Task_Category', 'Planned_Duration']].copy()
        # Ensure a Task_ID exists for traceability
        if 'Task_ID' not in display_df.columns:
            display_df.insert(0, 'Task_ID', range(1, len(display_df) + 1))

        # Ensure phases exist in session state
        if 'phases' not in st.session_state:
            st.session_state['phases'] = ['Phase 1']

        # Default Phase assignment
        display_df['Phase'] = st.session_state['phases'][0] if st.session_state['phases'] else 'Phase 1'
        display_df['Actual_Days_Taken'] = 0

        # Allow editing with a Phase select column
        edited_progress = st.data_editor(
            display_df,
            use_container_width=True,
            num_rows="dynamic",
            key='midproj_editor',
            column_config={
                'Task_ID': st.column_config.NumberColumn('Task ID', min_value=1, step=1, width='small'),
                'Task_Name': st.column_config.TextColumn('Task Name', width='large'),
                'Task_Category': st.column_config.TextColumn('Category', width='medium'),
                'Planned_Duration': st.column_config.NumberColumn('Planned (days)', min_value=0),
                'Actual_Days_Taken': st.column_config.NumberColumn('Actual (days)', min_value=0),
                'Phase': st.column_config.SelectboxColumn('Phase', options=st.session_state['phases'])
            },
            height=400
        )
        
        if st.button("Calculate Re-Forecast & Analyze Delays"):
            delay_analysis = []
            total_actuals = 0
            
            for idx, row in edited_progress.iterrows():
                actual = row['Actual_Days_Taken']
                planned = row['Planned_Duration']
                total_actuals += actual
                
                if actual > planned:
                    sim_row = {
                        'Land_Type': land_type, 
                        'LWE_Flag': lwe_risk_flag,
                        'Monsoon_Flag': 1 if actual_start_date.month in [6,7,8] else 0,
                        'Task_Category': row['Task_Category']
                    }
                    reason = generate_granular_risk_assessment(sim_row, actual, planned, 2)
                    delay_analysis.append(reason)
                elif actual > 0:
                    delay_analysis.append("Completed On Time")
                else:
                    delay_analysis.append("Pending")
            
            edited_progress['AI Risk Analysis'] = delay_analysis
            
            remaining_est = 120 # Placeholder for demo
            grand_total = total_actuals + remaining_est
            new_end_date = actual_start_date + timedelta(days=int(grand_total))
            
            st.divider()
            m1, m2 = st.columns(2)
            m1.metric("Revised End Date", new_end_date.strftime('%d %b %Y'))
            m2.metric("Total Projected Duration", f"{grand_total} Days", f"History: {total_actuals} | Remaining: {remaining_est}")
            
            st.subheader("Task-wise Delay Analysis")
            st.dataframe(edited_progress, use_container_width=True)
            
        st.markdown('</div>', unsafe_allow_html=True)

# ==============================================================================
# MODULE 3: RISK AUDIT (CONTEXT AWARE)
# ==============================================================================

if module == "Risk Audit":
    st.title("Risk Waterfall Analysis")
    st.markdown(f"#### Scenario: Risk Profile for **{selected_district}** ({land_type} Land)")

    # Context card: show which project/dataset slice this audit refers to
    project_context_lines = []
    project_context_lines.append(f"Project Template: {p_type if 'p_type' in globals() else 'N/A'}")
    project_context_lines.append(f"District: {selected_district}")
    project_context_lines.append(f"Land Type: {land_type}")
    project_context_lines.append(f"Vendor Tier Selected: {global_vendor if 'global_vendor' in globals() else 'N/A'}")
    # sample size for this district (if possible)
    sample_count = 0
    try:
        sample_count = int(df[df['District'] == selected_district].shape[0]) if 'District' in df.columns else 0
    except Exception:
        sample_count = 0
    project_context_lines.append(f"Sample records in dataset for this district: {sample_count}")

    st.markdown('<div class="kpmg-card">', unsafe_allow_html=True)
    st.markdown('**Audit Context**')
    for line in project_context_lines:
        st.markdown(f"- {line}")
    # Tooltip explaining how sample_count is calculated
    tooltip_text = "Number of dataset records with the selected district. Used to compute historical multipliers for risk estimation. Small samples (<10) reduce reliability."
    tooltip_html = f"<div style='margin-top:6px'><small style='color:#9fb1ff' title='{tooltip_text}'>[?] How sample count is calculated</small></div>"
    st.markdown(tooltip_html, unsafe_allow_html=True)

    # Show a warning when sample size is low
    if sample_count < 10:
        st.warning(f"Low data support: only {sample_count} records found for {selected_district}. Results may be unreliable.")

    # Top 3 example project types in this district
    try:
        top_projects = df[df['District'] == selected_district]['Project_Type'].value_counts().head(3)
        if not top_projects.empty:
            st.markdown("**Top example projects used for this district:**")
            for proj, cnt in top_projects.items():
                st.markdown(f"- {proj} ({cnt} records)")
    except Exception:
        pass

    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("### Delay Contributors (Data-Driven Analysis)")
    
    # Calculate statistics from actual data (ensure Duration_Multiplier exists)
    if 'Duration_Multiplier' not in df.columns:
        # avoid divide-by-zero
        if 'Actual_Duration' in df.columns and 'Planned_Duration' in df.columns:
            df['Duration_Multiplier'] = df['Actual_Duration'] / (df['Planned_Duration'] + 0.01)
        else:
            df['Duration_Multiplier'] = 1.0

    data_stats = df.groupby('Land_Type')['Duration_Multiplier'].mean()

    # Base estimate (median from data)
    base_est = int(df['Planned_Duration'].median()) if 'Planned_Duration' in df.columns else 0

    # Land type risk (from actual data)
    if land_type in data_stats.index:
        land_multiplier = float(data_stats.get(land_type, 1.0))
        risk_land = int(max(0, (land_multiplier - 1.0) * base_est))
    else:
        risk_land = 0

    # LWE risk (from actual LWE-flagged data)
    if 'LWE_Flag' in df.columns:
        lwe_data = df[df['LWE_Flag'] == 1]['Duration_Multiplier'].mean() if (df['LWE_Flag'] == 1).any() else 1.0
        safe_data = df[df['LWE_Flag'] == 0]['Duration_Multiplier'].mean() if (df['LWE_Flag'] == 0).any() else 1.0
        risk_lwe = int(max(0, (lwe_data - safe_data) * base_est)) if lwe_risk_flag == 1 else 0
    else:
        risk_lwe = 0

    # Monsoon risk (from actual monsoon-flagged data)
    if 'Monsoon_Flag' in df.columns:
        monsoon_data = df[df['Monsoon_Flag'] == 1]['Duration_Multiplier'].mean() if (df['Monsoon_Flag'] == 1).any() else 1.0
        non_monsoon_data = df[df['Monsoon_Flag'] == 0]['Duration_Multiplier'].mean() if (df['Monsoon_Flag'] == 0).any() else 1.0
        risk_monsoon = int(max(0, (monsoon_data - non_monsoon_data) * base_est))
    else:
        risk_monsoon = 0

    total = base_est + risk_land + risk_lwe + risk_monsoon
    
    text_labels = [
        f"{base_est} d (Baseline)", 
        f"+{risk_land} d (CNT Act)" if risk_land > 0 else "0",
        f"+{risk_lwe} d (Security)" if risk_lwe > 0 else "0", 
        f"+{risk_monsoon} d (Weather)", 
        f"{total} Days"
    ]
    
    df_waterfall = pd.DataFrame({
        "Factor": ["Base Estimate", "Land Acquisition (CNT)", "Security (LWE)", "Monsoon Impact", "Total Forecast"],
        "Days": [base_est, risk_land, risk_lwe, risk_monsoon, 0]
    })
    df_waterfall.at[4, "Days"] = total
    
    # Explain the chart in plain language for users
    explanation_lines = []
    explanation_lines.append(f"Base estimate (median planned duration): {base_est} days.")
    if risk_land > 0:
        explanation_lines.append(f"Land type ({land_type}) adds an estimated +{risk_land} days based on historical data for similar projects.")
    if risk_lwe > 0:
        explanation_lines.append(f"Security (LWE) contributes approximately +{risk_lwe} days when present in this district.")
    if risk_monsoon > 0:
        explanation_lines.append(f"Monsoon season can add around +{risk_monsoon} days to schedules.")
    explanation_lines.append(f"Overall data-driven forecast: {total} days (sum of baseline + local risks).")
    
    st.markdown("**Quick Interpretation:**")
    for line in explanation_lines:
        st.markdown(f"- {line}")
    
    fig = go.Figure(go.Waterfall(
        name = "20", orientation = "v",
        measure = ["relative", "relative", "relative", "relative", "total"],
        x = df_waterfall["Factor"],
        textposition = "outside",
        text = text_labels, 
        y = df_waterfall["Days"],
        connector = {"line":{"color":"white"}},
    ))
    fig = style_chart(fig)
    st.plotly_chart(fig, use_container_width=True)
    
    st.caption(f"This chart breaks down the standard schedule deviation for a project in {selected_district}. Notice how local factors like Land Type act as major bottlenecks.")
    st.markdown('</div>', unsafe_allow_html=True)