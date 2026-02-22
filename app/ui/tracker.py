import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import logging
import config

from app.core.logic import generate_granular_risk_assessment
from app.ui.reports import generate_pdf_report

def render_tracker(df, models, context):
    st.title("Mid-Project Analysis")
    st.markdown(f"#### Progress Update: {context['app_context']}")
    
    st.markdown('<div class="card-box">', unsafe_allow_html=True)
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
        
        st.markdown('<div class="card-box">', unsafe_allow_html=True)
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
                        'Land_Type': context['land_type'], 
                        'LWE_Flag': context['lwe_risk_flag'],
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
            
            v_val = 1 if "Tier 1" in context['global_vendor'] else (3 if "Tier 3" in context['global_vendor'] else 2)
            remaining_input_rows = []
            for idx, row in edited_progress.iterrows():
                actual = row['Actual_Days_Taken']
                if actual == 0:
                    sim_row = {
                        'Project_Type': proj_data['Project_Type'].iloc[0],
                        'District': context['selected_district'],
                        'LWE_Flag': context['lwe_risk_flag'],
                        'Task_Category': row['Task_Category'],
                        'Land_Type': context['land_type'],
                        'Vendor_Tier': v_val,
                        'Planned_Duration': row['Planned_Duration'],
                        'Monsoon_Flag': 1 if (actual_start_date + timedelta(days=total_actuals)).month in [6,7,8,9] else 0
                    }
                    remaining_input_rows.append(sim_row)

            remaining_est = 0
            if remaining_input_rows:
                input_df = pd.DataFrame(remaining_input_rows)[config.FEATURES]
                predicted_durations = models['P50'].predict(input_df)
                remaining_est = int(predicted_durations.sum())

            grand_total = total_actuals + remaining_est
            new_end_date = actual_start_date + timedelta(days=int(grand_total))
            
            # --- NEW: Generate PDF for Mid-Project ---
            try:
                mid_risk_ctx = {
                    "Land Type": "N/A (Mid-Project)", # Or use global if applicable
                    "Vendor Tier": context['global_vendor'],
                    "Project Stage": "Mid-Project Execution",
                    "Status": "On Track" if total_actuals <= (grand_total/2) else "At Risk"
                }
                
                mid_pdf_bytes = generate_pdf_report(
                    proj,
                    context['selected_district'],
                    int(grand_total * 0.9),
                    int(grand_total),
                    int(grand_total * 1.1),
                    critical_path=["Re-forecast based on actuals"],
                    risk_context=mid_risk_ctx
                )
                
                st.download_button("Download Status Report", mid_pdf_bytes, f"{proj}_Status_Report.pdf", "application/pdf")
            except Exception as e:
                logging.error(f"Mid-project PDF generation failed: {e}")
            
            st.divider()
            m1, m2 = st.columns(2)
            m1.metric("Revised End Date", new_end_date.strftime('%d %b %Y'))
            m2.metric("Total Projected Duration", f"{grand_total} Days", f"History: {total_actuals} | Remaining: {remaining_est}")
            
            st.subheader("Task-wise Delay Analysis")
            st.dataframe(edited_progress, use_container_width=True)
            
        st.markdown('</div>', unsafe_allow_html=True)
