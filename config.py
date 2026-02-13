# ===== KPMG PMIS Configuration =====
# Centralized configuration for model training and inference

# ===== FILE PATHS =====
DATA_FILE = 'kpmg_pmis_synthetic_data.csv'
MODEL_OUTPUT_FILE = 'kpmg_pmis_model.pkl'
NOTEBOOK_OUTPUT_FILE = 'Kpmg_Pmis_Training.ipynb'

# ===== MODEL TRAINING PARAMETERS =====
TEST_SIZE = 0.2
RANDOM_STATE = 42
QUANTILES = [0.1, 0.5, 0.9]  # P10, P50, P90

# ===== CATBOOST HYPERPARAMETERS =====
CATBOOST_PARAMS = {
    'iterations': 1000,
    'learning_rate': 0.05,
    'depth': 6,
    'verbose': 100,
    'random_seed': RANDOM_STATE,
    'allow_writing_files': False
}

# ===== FEATURE CONFIGURATION =====
FEATURES = [
    'Project_Type', 'District', 'LWE_Flag', 
    'Task_Category', 'Land_Type', 'Vendor_Tier', 
    'Planned_Duration', 'Monsoon_Flag'
]

CATEGORICAL_FEATURES = [
    'Project_Type', 'District', 'Task_Category', 'Land_Type'
]

TARGET_VARIABLE = 'Actual_Duration'

# ===== REQUIRED DATA COLUMNS =====
REQUIRED_COLUMNS = [
    'Project_Type', 'District', 'Task_Name', 'Task_Category',
    'LWE_Flag', 'Land_Type', 'Vendor_Tier', 'Planned_Duration',
    'Actual_Duration', 'Monsoon_Flag'
]

# ===== NLP VECTORIZER PARAMETERS =====
TFIDF_MAX_FEATURES = 100
TFIDF_STOP_WORDS = 'english'

# ===== VISUALIZATION SETTINGS =====
KPMG_BLUE = "#00338D"
PLOT_STYLE = "whitegrid"
FIGURE_SIZE_SINGLE = (10, 6)
FIGURE_SIZE_DOUBLE = (16, 6)

# ===== MODEL IDENTIFIERS =====
MODEL_NAMES = {
    0.1: 'P10',
    0.5: 'P50',
    0.9: 'P90'
}
