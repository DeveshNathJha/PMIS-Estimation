# ===== KPMG PMIS Configuration =====
# Centralized configuration for model training and inference
import os

# ===== FILE PATHS =====
DATA_FILE = os.path.join('data', 'synthetic_project_data.csv')
MODEL_OUTPUT_FILE = os.path.join('data', 'pmis_model.pkl')
NOTEBOOK_OUTPUT_FILE = os.path.join('scripts', 'PMIS_Training_Pipeline.ipynb')

# ===== MODEL TRAINING PARAMETERS =====
TEST_SIZE = 0.2
RANDOM_STATE = 42
RANDOM_SEED = RANDOM_STATE  # Alias for data generation
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
FIRM_BLUE = "#00338D"
PLOT_STYLE = "whitegrid"
FIGURE_SIZE_SINGLE = (10, 6)
FIGURE_SIZE_DOUBLE = (16, 6)

# ===== UI COLORS =====
DARK_BG_COLOR = "#0E1117"
TEXT_COLOR = "#FAFAFA"
CARD_BG_COLOR = "#1E2530"
ACCENT_COLOR = FIRM_BLUE
SECONDARY_COLOR = "#005EB8"

# ===== MODEL IDENTIFIERS =====
MODEL_NAMES = {
    0.1: 'P10',
    0.5: 'P50',
    0.9: 'P90'
}

# ==============================================================================
# DATA GENERATION CONSTANTS
# ==============================================================================

# Complete State Profile (Terrain & Logistics Friction)
STATE_PROFILE = {
    # --- NORTH INDIA ---
    'Himachal Pradesh': {'terrain': 'Hilly', 'monsoon_severity': 'High', 'logistics_friction': 1.4},
    'Uttarakhand':      {'terrain': 'Hilly', 'monsoon_severity': 'High', 'logistics_friction': 1.35},
    'Punjab':           {'terrain': 'Plain', 'monsoon_severity': 'Medium', 'logistics_friction': 1.0},
    'Haryana':          {'terrain': 'Plain', 'monsoon_severity': 'Low', 'logistics_friction': 1.0},
    'Uttar Pradesh':    {'terrain': 'Plain', 'monsoon_severity': 'Medium', 'logistics_friction': 1.1},
    'Rajasthan':        {'terrain': 'Desert', 'monsoon_severity': 'Low', 'logistics_friction': 1.15},
    'Delhi':            {'terrain': 'Urban', 'monsoon_severity': 'Medium', 'logistics_friction': 0.9},
    'Jammu & Kashmir':  {'terrain': 'Hilly', 'monsoon_severity': 'Medium', 'logistics_friction': 1.5},
    'Ladakh':           {'terrain': 'Hilly/Desert', 'monsoon_severity': 'Low', 'logistics_friction': 1.8},

    # --- EAST & NORTH EAST (High Logistics Risk) ---
    'Bihar':            {'terrain': 'Plain/Flood-Prone', 'monsoon_severity': 'High', 'logistics_friction': 1.25},
    'West Bengal':      {'terrain': 'Plain/Coastal', 'monsoon_severity': 'High', 'logistics_friction': 1.1},
    'Odisha':           {'terrain': 'Coastal', 'monsoon_severity': 'High', 'logistics_friction': 1.2},
    'Jharkhand':        {'terrain': 'Plateau/Forest', 'monsoon_severity': 'Medium', 'logistics_friction': 1.3},
    'Arunachal Pradesh':{'terrain': 'Hilly/Forest', 'monsoon_severity': 'Very High', 'logistics_friction': 1.7},
    'Assam':            {'terrain': 'Plain/Flood-Prone', 'monsoon_severity': 'Very High', 'logistics_friction': 1.4},
    'Manipur':          {'terrain': 'Hilly', 'monsoon_severity': 'High', 'logistics_friction': 1.6},
    'Meghalaya':        {'terrain': 'Hilly', 'monsoon_severity': 'Very High', 'logistics_friction': 1.5},
    'Mizoram':          {'terrain': 'Hilly', 'monsoon_severity': 'High', 'logistics_friction': 1.65},
    'Nagaland':         {'terrain': 'Hilly', 'monsoon_severity': 'High', 'logistics_friction': 1.6},
    'Sikkim':           {'terrain': 'Hilly', 'monsoon_severity': 'High', 'logistics_friction': 1.55},
    'Tripura':          {'terrain': 'Hilly/Plain', 'monsoon_severity': 'High', 'logistics_friction': 1.45},

    # --- CENTRAL INDIA ---
    'Madhya Pradesh':   {'terrain': 'Plateau/Plain', 'monsoon_severity': 'Medium', 'logistics_friction': 1.1},
    'Chhattisgarh':     {'terrain': 'Forest/Plateau', 'monsoon_severity': 'Medium', 'logistics_friction': 1.3},

    # --- WEST INDIA ---
    'Gujarat':          {'terrain': 'Plain/Coastal', 'monsoon_severity': 'Medium', 'logistics_friction': 1.05},
    'Maharashtra':      {'terrain': 'Coastal/Plain', 'monsoon_severity': 'High', 'logistics_friction': 1.0},
    'Goa':              {'terrain': 'Coastal', 'monsoon_severity': 'Very High', 'logistics_friction': 1.1},

    # --- SOUTH INDIA ---
    'Andhra Pradesh':   {'terrain': 'Coastal/Plain', 'monsoon_severity': 'High', 'logistics_friction': 1.1},
    'Telangana':        {'terrain': 'Plateau', 'monsoon_severity': 'Medium', 'logistics_friction': 1.05},
    'Karnataka':        {'terrain': 'Plateau/Coastal', 'monsoon_severity': 'High', 'logistics_friction': 1.05},
    'Kerala':           {'terrain': 'Coastal/Hilly', 'monsoon_severity': 'Very High', 'logistics_friction': 1.2},
    'Tamil Nadu':       {'terrain': 'Coastal/Plain', 'monsoon_severity': 'High', 'logistics_friction': 1.05},
}

# Complete Jharkhand 24 Districts with Security Risk (LWE)
# LWE = 1 (Left Wing Extremism / Naxal Affected) -> High Risk
# LWE = 0 (Safe Zone)
JHARKHAND_MAP = {
    "Palamu": {"Division": "Palamu", "LWE": 1},
    "Garhwa": {"Division": "Palamu", "LWE": 1},
    "Latehar": {"Division": "Palamu", "LWE": 1},
    "Chatra": {"Division": "North Chotanagpur", "LWE": 1},
    "Hazaribagh": {"Division": "North Chotanagpur", "LWE": 0},
    "Giridih": {"Division": "North Chotanagpur", "LWE": 1},
    "Koderma": {"Division": "North Chotanagpur", "LWE": 0},
    "Dhanbad": {"Division": "North Chotanagpur", "LWE": 0},
    "Bokaro": {"Division": "North Chotanagpur", "LWE": 0},
    "Ramgarh": {"Division": "North Chotanagpur", "LWE": 0},
    "Ranchi": {"Division": "South Chotanagpur", "LWE": 0},
    "Lohardaga": {"Division": "South Chotanagpur", "LWE": 1},
    "Gumla": {"Division": "South Chotanagpur", "LWE": 1},
    "Simdega": {"Division": "South Chotanagpur", "LWE": 1},
    "Khunti": {"Division": "South Chotanagpur", "LWE": 1},
    "West Singhbhum": {"Division": "Kolhan", "LWE": 1},
    "East Singhbhum": {"Division": "Kolhan", "LWE": 0},
    "Seraikela-Kharsawan": {"Division": "Kolhan", "LWE": 0},
    "Dumka": {"Division": "Santhal Pargana", "LWE": 0},
    "Jamtara": {"Division": "Santhal Pargana", "LWE": 0},
    "Deoghar": {"Division": "Santhal Pargana", "LWE": 0},
    "Godda": {"Division": "Santhal Pargana", "LWE": 0},
    "Sahebganj": {"Division": "Santhal Pargana", "LWE": 0},
    "Pakur": {"Division": "Santhal Pargana", "LWE": 0}
}

# Specific Locations for Kumbh Mela (To avoid mapping Kumbh to Tamil Nadu)
KUMBH_LOCATIONS = [
    {'City': 'Prayagraj', 'State': 'Uttar Pradesh'},
    {'City': 'Haridwar', 'State': 'Uttarakhand'},
    {'City': 'Nashik', 'State': 'Maharashtra'},
    {'City': 'Ujjain', 'State': 'Madhya Pradesh'}
]

PROJECT_TEMPLATES = {
    # --- GENERAL INFRASTRUCTURE ---
    'Construction_Hospital': [
        ('Budget & Approval', 30, 'Admin'),
        ('Land Acquisition', 60, 'Regulatory'),
        ('Tendering', 45, 'Procurement'),
        ('Mobilization', 20, 'Logistics'),
        ('Excavation', 40, 'Civil'),
        ('Foundation', 60, 'Civil'),
        ('Superstructure', 120, 'Civil'),
        ('MEP Works', 90, 'Technical'),
        ('Finishing', 60, 'Civil'),
        ('Handover', 30, 'Admin')
    ],
    'Linear_Highway': [
        ('DPR & Survey', 90, 'Technical'),
        ('Land Acquisition & ROW', 180, 'Regulatory'),
        ('Forest Clearance', 120, 'Regulatory'),
        ('Tendering', 60, 'Procurement'),
        ('Earthwork', 100, 'Civil'),
        ('Pavement Layering', 90, 'Civil'),
        ('Signages & Safety', 30, 'Civil'),
        ('Commercial Ops Date', 0, 'Milestone')
    ],
    'Mega_Event_Kumbh': [
        ('Master Planning', 60, 'Technical'),
        ('Tendering', 45, 'Procurement'),
        ('Ground Prep', 40, 'Civil'),
        ('Temporary Structures', 50, 'Civil'),
        ('Electrical Grid', 30, 'Technical'),
        ('Safety Audit', 15, 'Regulatory'),
        ('Go-Live', 0, 'Milestone')
    ],
    'Indus_Factory': [
        ('Feasibility Study', 45, 'Technical'),
        ('Env Impact Assessment', 90, 'Regulatory'),
        ('Civil Construction', 150, 'Civil'),
        ('Machine Procurement', 120, 'Procurement'),
        ('Installation', 60, 'Technical'),
        ('Trial Runs', 30, 'Technical'),
        ('Commissioning', 0, 'Milestone')
    ],

    # --- NHM SPECIALIZED PROJECTS (Detailed Phases) ---
    'NHM - Health Sub-Centre (HSC)': [
        ('Site Identification', 15, 'Admin'),
        ('Land Handover', 30, 'Regulatory'),
        ('Plinth Work', 30, 'Civil'),
        ('Roof Casting', 30, 'Civil'),
        ('Electrical & Plumbing', 20, 'Technical'),
        ('Finishing & Painting', 20, 'Civil'),
        ('Handover', 10, 'Admin')
    ],
    'NHM - Maternal & Child Health (MCH) Wing': [
        ('Soil Testing & Design', 30, 'Technical'),
        ('Foundation Works', 60, 'Civil'),
        ('Structure (G+2)', 120, 'Civil'),
        ('Medical Gas Pipeline', 45, 'Technical'),
        ('OT & ICU Setup', 60, 'Technical'),
        ('Fire Safety Install', 30, 'Technical'),
        ('Final Inspection', 15, 'Regulatory')
    ],
    'NHM - Trauma Care Centre': [
        ('Site Clearance', 20, 'Civil'),
        ('Structure Construction', 90, 'Civil'),
        ('Radiation Shielding (X-Ray)', 30, 'Technical'),
        ('Equipment Supply (CT/Ventilator)', 60, 'Procurement'),
        ('Installation & Calibration', 30, 'Technical'),
        ('AERB Approval', 45, 'Regulatory'),
        ('Staff Training', 15, 'Admin')
    ],
    'NHM - Oxygen Plant (PSA)': [
        ('Site Platform Readiness', 20, 'Civil'),
        ('Plant Manufacturing/Import', 45, 'Procurement'),
        ('Delivery to Site', 15, 'Logistics'),
        ('Installation', 10, 'Technical'),
        ('Copper Piping', 20, 'Technical'),
        ('Pressure Testing', 5, 'Technical'),
        ('Drug Inspector Approval', 15, 'Regulatory')
    ],
    'NHM - Drug Warehouse (District Level)': [
        ('Land Acquisition', 60, 'Regulatory'),
        ('Warehousing Structure', 90, 'Civil'),
        ('HVAC & Cold Chain Setup', 45, 'Technical'),
        ('Racking System Install', 20, 'Technical'),
        ('Fire & Safety Audit', 15, 'Regulatory'),
        ('Stocking', 30, 'Logistics')
    ]
}

# Fillers for other NHM types to ensure they work if selected
GENERIC_NHM_PHASES = [
    ('Site Survey', 15, 'Technical'),
    ('Civil Works', 90, 'Civil'),
    ('Equipment Install', 45, 'Technical'),
    ('Handover', 15, 'Admin')
]

for nhm_type in [
    "NHM - Primary Health Centre (PHC) 24x7", "NHM - Community Health Centre (CHC)",
    "NHM - District Hospital Expansion", "NHM - Critical Care Block (CCB)",
    "NHM - Diagnostic Lab (IPHL)"
]:
    if nhm_type not in PROJECT_TEMPLATES:
        PROJECT_TEMPLATES[nhm_type] = GENERIC_NHM_PHASES

# Vendor Tiers and Names
VENDOR_TIER_MAPPING = {1: "L&T / Tata Projects", 2: "NCC / Nagarjuna", 3: "Local Contractor"}
VENDOR_TIER_WEIGHTS = [0.2, 0.5, 0.3]

# Land Types
LAND_TYPE_GOVT = "Govt Land"
LAND_TYPE_DONATED = "Donated"
LAND_TYPE_TRIBAL = "Tribal (CNT/SPT)"
LAND_TYPES = [LAND_TYPE_GOVT, LAND_TYPE_DONATED, LAND_TYPE_TRIBAL]

TASK_CATEGORY_PROCUREMENT = 'Procurement'
