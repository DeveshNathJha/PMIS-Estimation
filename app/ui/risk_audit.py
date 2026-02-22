import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import config

from app.core.logic import (
    get_wbs_template_from_data, 
    calculate_cpm
)
from app.ui.components import style_chart

def render_risk_audit(df, context):
    st.title("Risk Waterfall Analysis")
    st.markdown(f"#### Scenario: Risk Profile for **{context['selected_district']}** ({context['land_type']})")

    p_type = st.session_state.get('p_type_audit', list(df['Project_Type'].unique())[0]) # Fallback or need to select

    # We need to know the Project Type to do a specific audit
    # In pmisapp.py it reused p_type from the sidebar or previous context. 
    # Let's add a local selector if not clear, or rely on a default.
    # For now, let's expose a selector inside the audit if not passed.
    
    # Context card: show which project/dataset slice this audit refers to
    project_context_lines = []
    project_context_lines.append(f"District: {context['selected_district']}")
    project_context_lines.append(f"Land Type: {context['land_type']}")
    project_context_lines.append(f"Vendor Tier Selected: {context['global_vendor']}")
    
    # sample size for this district (if possible)
    sample_count = 0
    try:
        sample_count = int(df[df['District'] == context['selected_district']].shape[0]) if 'District' in df.columns else 0
    except Exception:
        sample_count = 0
    project_context_lines.append(f"Sample records in dataset for this district: {sample_count}")

    st.markdown('<div class="card-box">', unsafe_allow_html=True)
    st.markdown('**Audit Context**')
    for line in project_context_lines:
        st.markdown(f"- {line}")
    
    # Tooltip explaining how sample_count is calculated
    tooltip_text = "Number of dataset records with the selected district. Used to compute historical multipliers for risk estimation. Small samples (<10) reduce reliability."
    tooltip_html = f"<div style='margin-top:6px'><small style='color:#9fb1ff' title='{tooltip_text}'>[?] How sample count is calculated</small></div>"
    st.markdown(tooltip_html, unsafe_allow_html=True)

    # Show a warning when sample size is low
    if sample_count < 10:
        st.warning(f"Low data support: only {sample_count} records found for {context['selected_district']}. Results may be unreliable.")

    # Select Project Type for Audit
    project_types = list(df['Project_Type'].unique())
    p_type = st.selectbox("Select Project Template for Audit", project_types, key="audit_p_type")

    # Top 3 example project types in this district
    try:
        top_projects = df[df['District'] == context['selected_district']]['Project_Type'].value_counts().head(3)
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

    data_stats = df.groupby('Land_Type').agg({'Duration_Multiplier': 'mean'})['Duration_Multiplier']

    # --- PROFESSIONAL BASELINE CALCULATION (CPM) ---
    try:
        # Pass the DataFrame to get_wbs_template_from_data
        sim_wbs = get_wbs_template_from_data(p_type, df) 
        # We assume predicted duration = planned for baseline
        sim_wbs['Predicted_Duration'] = sim_wbs['Planned_Duration']
        base_est, _ = calculate_cpm(sim_wbs)
        base_est = int(base_est)
    except Exception:
        base_est = int(df['Planned_Duration'].median()) if 'Planned_Duration' in df.columns else 40

    # Land type risk (from actual data)
    if context['land_type'] in data_stats.index:
        land_multiplier = float(data_stats.get(context['land_type'], 1.0))
        risk_land = int(max(0, (land_multiplier - 1.0) * base_est))
    else:
        risk_land = 0

    # LWE risk (from actual LWE-flagged data)
    if 'LWE_Flag' in df.columns:
        lwe_data = df[df['LWE_Flag'] == 1]['Duration_Multiplier'].mean() if (df['LWE_Flag'] == 1).any() else 1.0
        safe_data = df[df['LWE_Flag'] == 0]['Duration_Multiplier'].mean() if (df['LWE_Flag'] == 0).any() else 1.0
        risk_lwe = int(max(0, (lwe_data - safe_data) * base_est)) if context['lwe_risk_flag'] == 1 else 0
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
    explanation_lines.append(f"Project Baseline (Critical Path): {base_est} days (based on {p_type} template).")
    if risk_land > 0:
        explanation_lines.append(f"Land Acquisition ({context['land_type']}): Projected +{risk_land} days delay based on district historical data.")
    if risk_lwe > 0:
        explanation_lines.append(f"Security Logistics (LWE): Projected +{risk_lwe} days delay due to friction in this zone.")
    if risk_monsoon > 0:
        explanation_lines.append(f"Monsoon Seasonality: Projected +{risk_monsoon} days delay.")
    explanation_lines.append(f"Total Risk-Adjusted Forecast: {total} days.")
    
    st.markdown("**Executive Risk Summary:**")
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
    
    st.caption(f"This chart breaks down the standard schedule deviation for a project in {context['selected_district']}. Notice how local factors like Land Type act as major bottlenecks.")
    st.markdown('</div>', unsafe_allow_html=True)
