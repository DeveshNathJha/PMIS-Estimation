import streamlit as st
import pandas as pd
import joblib
import os
import sys

# Ensure root directory is in path to import config
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
import config

@st.cache_resource(show_spinner="Loading ML Models & Data from Disk...")
def load_resources():
    """
    Loads the ML Model and Data securely with caching.
    We use error handling to prevent the app from crashing during the demo.
    """
    try:
        # Load Raw Data for Dropdowns
        # Paths are relative to where the app is run (usually root)
        if not os.path.exists(config.DATA_FILE):
            st.error(f"Data CSV not found: {config.DATA_FILE}")
            return None, None
            
        data = pd.read_csv(config.DATA_FILE)
        
        # Load Model Artifact
        if not os.path.exists(config.MODEL_OUTPUT_FILE):
            st.error(f"Model PKL not found: {config.MODEL_OUTPUT_FILE}. Please train the model first.")
            return None, None
            
        model_bundle = joblib.load(config.MODEL_OUTPUT_FILE) 
        return data, model_bundle
    except Exception as e:
        st.error(f"CRITICAL ERROR Loading Resources: {e}")
        return None, None
