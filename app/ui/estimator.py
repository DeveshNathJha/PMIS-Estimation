import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import graphviz
import config

from app.core.logic import (
    get_wbs_template_from_data, 
    calculate_cpm, 
    generate_granular_risk_assessment
)
from app.ui.reports import generate_pdf_report

def render_estimator(df, models, context):
    st.title("Project Completion Estimator")
    st.markdown(f"#### Context: {context['app_context']} > {context['selected_district']}")

    PROJECT_TEMPLATES = list(df['Project_Type'].unique())

    # INPUT CARD
    st.markdown('<div class="card-box">', unsafe_allow_html=True)
    c1, c2 = st.columns([1, 2])
    
    with c1:
        st.subheader("1. Project Config")
        # Filter Project Types based on Context
        if context['app_context'] == "Jharkhand (NHM Focus)":
            nhm_projects = [p for p in PROJECT_TEMPLATES if "NHM" in p]
            p_type = st.selectbox("Project Template", nhm_projects)
        else:
            other_projects = [p for p in PROJECT_TEMPLATES if "NHM" not in p]
            p_type = st.selectbox("Project Template", other_projects)
            
        start_date = st.date_input("Planned Start Date", datetime.today())

    with c2:
        st.subheader("2. WBS & Dependencies")
        
        # DYNAMIC WBS LOADING
        default_wbs = get_wbs_template_from_data(p_type, df)
        category_options = sorted(df['Task_Category'].unique())

        st.info("Dependencies: Enter Task IDs (e.g., '1,2'). ID 1 is the first task.")

        # Prepare the data_editor
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

        
        # Inline WBS preview validation
        preview_issues = []
        if edited_wbs is not None and not edited_wbs.empty:
            if 'Task_ID' not in edited_wbs.columns:
                preview_issues.append('WBS requires a Task_ID column (numeric).')
            else:
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
            with st.spinner("Running Monte Carlo Simulation & CPM Analysis..."):
                input_rows = []
                v_val = 1 if "Tier 1" in context['global_vendor'] else (3 if "Tier 3" in context['global_vendor'] else 2)
                
                # --- STEP A: PREPARE MODEL INPUTS ---
                for _, task in edited_wbs.iterrows():
                    monsoon_flag = 1 if start_date.month in [6, 7, 8, 9] else 0
                    row = {
                        'Project_Type': p_type, 
                        'District': context['selected_district'],
                        'LWE_Flag': context['lwe_risk_flag'],
                        'Task_Category': task['Task_Category'],
                        'Land_Type': context['land_type'],
                        'Vendor_Tier': v_val,
                        'Planned_Duration': task['Planned_Duration'], 
                        'Monsoon_Flag': monsoon_flag
                    }
                    input_rows.append(row)
                
                input_df = pd.DataFrame(input_rows)[config.FEATURES]
                
                # --- STEP B: PREDICT DURATIONS ---
                predicted_durations = models['P50'].predict(input_df)
                edited_wbs['Predicted_Duration'] = predicted_durations.astype(int)

                # --- STEP C: GENERATE GRANULAR REASONS ---
                delay_reasons = []
                for i, row in input_df.iterrows():
                    pred = predicted_durations[i]
                    planned = row['Planned_Duration']
                    reason = generate_granular_risk_assessment(row, pred, planned, v_val)
                    delay_reasons.append(reason)
                
                edited_wbs['Risk Analysis'] = delay_reasons 
                
                # Calculate Totals
                p10_sum = models['P10'].predict(input_df).sum()
                p90_sum = models['P90'].predict(input_df).sum()
                
                # CPM Logic
                cpm_duration, critical_path = calculate_cpm(edited_wbs)
                finish_date = start_date + timedelta(days=int(cpm_duration))
                
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
                except Exception as e:
                    import logging
                    logging.warning(f"Failed to generate Graphviz diagram: {e}. Ensure Graphviz is installed on the system.")
                    st.warning("Could not generate the network diagram. Please ensure Graphviz is installed on the underlying system.")
                    final_img = None

                pdf_bytes = generate_pdf_report(
                    p_type,
                    context['selected_district'],
                    int(p10_sum),
                    int(cpm_duration),
                    int(p90_sum),
                    critical_path,
                    final_img
                )
                
                # --- RESULTS UI ---
                st.markdown('<div class="card-box">', unsafe_allow_html=True)
                c1, c2 = st.columns([2, 1])
                with c1: 
                    st.markdown("### Executive Summary")
                    st.metric("Estimated Completion Date", finish_date.strftime('%d %b %Y'), f"Total Duration: {int(cpm_duration)} Days")
                with c2: 
                    st.download_button("Download PDF Report", pdf_bytes, "Project_Report.pdf", "application/pdf")
                
                m1, m2, m3 = st.columns(3)
                m1.metric("Optimistic Case (P10)", f"{int(p10_sum)} Days")
                m2.metric("Critical Tasks Count", f"{len(critical_path)}")
                m3.metric("Worst Case Risk (P90)", f"{int(p90_sum)} Days", delta_color="inverse")
                
                st.markdown("#### Task-Level Risk Breakdown")
                st.dataframe(edited_wbs[['Task_ID','Task_Name', 'Planned_Duration', 'Predicted_Duration', 'Risk Analysis']], use_container_width=True)
                
                st.markdown("#### Dependency Network Diagram")
                st.graphviz_chart(graph, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
