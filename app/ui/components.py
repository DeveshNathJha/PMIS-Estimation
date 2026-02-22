import streamlit as st
import plotly.graph_objects as go
import config

def inject_custom_css():
    st.markdown(f"""
        <style>
            .stApp {{
                background-color: {config.DARK_BG_COLOR};
                color: {config.TEXT_COLOR};
            }}
            [data-testid="stSidebar"] {{
                background-color: #151922;
                border-right: 1px solid #30363D;
            }}
            .card-box {{
                background-color: {config.CARD_BG_COLOR};
                padding: 25px;
                border-radius: 8px;
                border: 1px solid #30363D;
                border-left: 5px solid {config.ACCENT_COLOR}; 
                box-shadow: 0 4px 6px rgba(0,0,0,0.3);
                margin-bottom: 20px;
            }}
            h1, h2, h3, h4 {{
                color: {config.ACCENT_COLOR} !important;
                font-family: 'Arial', sans-serif;
                font-weight: 600;
            }}
            .stButton>button {{
                background-color: {config.SECONDARY_COLOR};
                color: white;
                border-radius: 4px;
                border: none;
                height: 3em;
                font-weight: bold;
                width: 100%;
            }}
            .stButton>button:hover {{
                background-color: {config.ACCENT_COLOR};
            }}
            /* Table Styling */
            [data-testid="stDataFrame"] {{
                background-color: {config.CARD_BG_COLOR};
            }}
        </style>
    """, unsafe_allow_html=True)

def style_chart(fig):
    fig.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    return fig

def render_sidebar(jharkhand_map, df):
    with st.sidebar:
        st.markdown("### Strategic Risk Engine")
        st.caption("PMIS Analytics Module v2.0")
        st.markdown("---")
        
        # CONTEXT SWITCHER
        app_context = st.radio("PROJECT CONTEXT", ["Generic / National", "Jharkhand (NHM Focus)"])
        
        selected_district = "Generic"
        lwe_risk_flag = 0
        land_type = "Govt Land"
        
        # Helper to get NHM districts
        def _get_nhm_districts(division):
            return [d for d, info in jharkhand_map.items() if info['Division'] == division]

        if app_context == "Jharkhand (NHM Focus)":
            st.success("Logic Active: NHM")
            div_list = list(set([v['Division'] for k,v in jharkhand_map.items()]))
            division = st.selectbox("Division", sorted(div_list))
            districts = _get_nhm_districts(division)
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
        
        with st.expander("Report Issue"):
            st.text_area("Details:", height=80, key="fb", placeholder="Describe the issue...")
            if st.button("Submit"):
                if st.session_state.get('fb'):
                    st.success("Thank you — issue logged.")
        
        return {
            "app_context": app_context,
            "selected_district": selected_district,
            "lwe_risk_flag": lwe_risk_flag,
            "land_type": land_type,
            "global_vendor": global_vendor,
            "module": module
        }
