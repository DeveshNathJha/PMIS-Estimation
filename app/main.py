import streamlit as st
import os
import sys
import logging

# Configure central logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(os.path.join(os.path.dirname(__file__), '..', 'app.log'))
    ]
)
logger = logging.getLogger(__name__)

# Add root directory to path to import config
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    import config
except ImportError as e:
    logger.critical(f"Config module not found: {e}")
    st.error("CRITICAL ERROR: 'config.py' not found. Please ensure it is in the root directory.")
    st.stop()

from app.utils.data_loader import load_resources
from app.ui.components import (
    inject_custom_css, 
    render_sidebar, 
)

# Import new UI Modules
from app.ui.estimator import render_estimator
from app.ui.tracker import render_tracker
from app.ui.risk_audit import render_risk_audit

def main():
    # ==============================================================================
    # 1. SETUP & CONFIGURATION
    # ==============================================================================
    st.set_page_config(
        page_title="Strategic Project Analytics",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    logger.info("Starting PMIS Application")
    inject_custom_css()

    # ==============================================================================
    # 2. RESOURCE LOADING
    # ==============================================================================
    df, artifact = load_resources()

    if df is None or artifact is None:
        st.stop()

    # Unpack Artifacts
    models = artifact['models']
    # If jharkhand_map is in artifact, use it, else load from config or fallback
    jharkhand_map = artifact.get('jharkhand_map', {})

    # ==============================================================================
    # 3. SIDEBAR & NAVIGATION
    # ==============================================================================
    context = render_sidebar(jharkhand_map, df)
    module = context['module']

    # ==============================================================================
    # 4. MODULE ROUTING
    # ==============================================================================
    if module == "Pre-Start Estimator":
        render_estimator(df, models, context)
        
    elif module == "Mid-Project Tracker":
        render_tracker(df, models, context)

    elif module == "Risk Audit":
        render_risk_audit(df, context)

if __name__ == "__main__":
    main()
