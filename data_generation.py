import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

# ==============================================================================
# 1. GEOGRAPHIC INTELLIGENCE (STATES & DISTRICTS)
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

# ==============================================================================
# 2. PROJECT TEMPLATES (WBS - Work Breakdown Structure)
# ==============================================================================

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

# ==============================================================================
# 3. HELPER FUNCTIONS
# ==============================================================================

def get_random_date(start_year=2022, end_year=2024):
    start = datetime(start_year, 1, 1)
    end = datetime(end_year, 12, 31)
    return start + timedelta(days=random.randint(0, (end - start).days))

def calculate_friction(state, terrain, lwe, vendor_tier, land_type, task_category, current_date):
    """
    The 'Physics Engine' of the simulation.
    Calculates delay multipliers based on Reality.
    """
    friction = 1.0
    
    # 1. Vendor Capability (Tier 1 is fast, Tier 3 is slow)
    if vendor_tier == 1: friction *= 0.85  # 15% Faster
    elif vendor_tier == 2: friction *= 1.0
    elif vendor_tier == 3: friction *= 1.3  # 30% Slower
    
    # 2. Logistics & Terrain
    # Get State friction from profile
    state_data = STATE_PROFILE.get(state, {'logistics_friction': 1.1, 'monsoon_severity': 'Medium'})
    friction *= state_data['logistics_friction']
    
    # 3. LWE (Security Risk)
    if lwe == 1:
        friction *= 1.4 # High security risk adds 40% time
        
    # 4. Land Type (Only affects Regulatory/Civil tasks)
    if task_category in ['Regulatory', 'Civil', 'Admin'] and land_type == 'Tribal (CNT/SPT)':
        # This is an "Adder", handled in the main loop, but friction adds stress
        friction *= 1.2
        
    # 5. Monsoon Seasonality
    # Check if current month is June(6) to Sept(9)
    if 6 <= current_date.month <= 9:
        severity = state_data['monsoon_severity']
        if severity == 'Very High': friction *= 1.5
        elif severity == 'High': friction *= 1.3
        elif severity == 'Medium': friction *= 1.1
        
    return friction

# ==============================================================================
# 4. MAIN GENERATION ENGINE
# ==============================================================================

def generate_synthetic_data(num_projects=1500):
    data = []
    
    project_types = list(PROJECT_TEMPLATES.keys())
    districts = list(JHARKHAND_MAP.keys())
    states = list(STATE_PROFILE.keys())
    
    print(f"Generating data for {num_projects} projects...")
    
    for i in range(num_projects):
        pid = f"PROJ_{1000+i}"
        
        # 1. Select Project Type
        p_type = random.choice(project_types)
        
        # 2. Context Logic (State & District)
        # If it's a Kumbh project, MUST be in specific cities
        if p_type == 'Mega_Event_Kumbh':
            loc = random.choice(KUMBH_LOCATIONS)
            state = loc['State']
            city_tier = "Tier 2" # Religious cities are usually Tier 2
            # District is Generic for non-Jharkhand states in this map, so use City name
            district = loc['City'] 
            lwe_flag = 0 # Kumbh cities are generally safe/controlled
        
        # If it's NHM, Prioritize Jharkhand (Client Focus)
        elif "NHM" in p_type:
            # 80% chance it's Jharkhand, 20% other states (for model robustness)
            if random.random() < 0.8:
                state = "Jharkhand"
                district = random.choice(districts)
                lwe_flag = JHARKHAND_MAP[district]['LWE']
            else:
                state = random.choice(states)
                district = "Generic_District"
                lwe_flag = 0
            city_tier = random.choice(["Tier 2", "Tier 3"])
            
        # General Projects
        else:
            state = random.choice(states)
            if state == "Jharkhand":
                district = random.choice(districts)
                lwe_flag = JHARKHAND_MAP[district]['LWE']
            else:
                district = "Generic_District"
                lwe_flag = 0
            city_tier = random.choice(["Tier 1", "Tier 2", "Tier 3"])

        # 3. Vendor & Land Config
        vendor_tier = random.choices([1, 2, 3], weights=[0.2, 0.5, 0.3])[0]
        # Vendor Names mapping
        v_names = {1: "L&T / Tata Projects", 2: "NCC / Nagarjuna", 3: "Local Contractor"}
        vendor_name = v_names[vendor_tier]
        
        land_type = random.choice(["Govt Land", "Donated", "Tribal (CNT/SPT)"])
        
        # 4. Timeline Simulation
        current_date = get_random_date()
        
        # Iterate through WBS Phases
        phases = PROJECT_TEMPLATES[p_type]
        for seq, (task_name, base_duration, category) in enumerate(phases, 1):
            if base_duration == 0: continue # Skip Milestones for training data
            
            # A. Calculate Planned
            planned_start = current_date
            # Simple Planned: Base Duration (No friction assumed in planning)
            planned_end = planned_start + timedelta(days=base_duration)
            
            # B. Calculate Actuals (Applying Physics)
            friction = calculate_friction(state, "Generic", lwe_flag, vendor_tier, land_type, category, planned_start)
            
            actual_duration = int(base_duration * friction)
            
            # C. Inject Specific Event Delays (The "Why")
            delay_reason = "None"
            
            # Event 1: CNT Act Delay
            if category == 'Regulatory' and land_type == 'Tribal (CNT/SPT)':
                delay = random.randint(60, 120)
                actual_duration += delay
                delay_reason = "CNT Act Land Acquisition"
            
            # Event 2: Vendor Rework (Tier 3)
            elif vendor_tier == 3 and category == 'Civil' and random.random() < 0.3:
                delay = random.randint(15, 45)
                actual_duration += delay
                delay_reason = "Quality Rework"
                
            # Event 3: Procurement Delay
            elif category == 'Procurement' and random.random() < 0.2:
                delay = random.randint(20, 50)
                actual_duration += delay
                delay_reason = "Supply Chain Issue"
            
            actual_end = planned_start + timedelta(days=actual_duration)
            
            # D. Append to Data
            data.append({
                'Project_ID': pid,
                'Project_Type': p_type,
                'State': state,
                'District': district,
                'LWE_Flag': lwe_flag,
                'Vendor_Tier': vendor_tier,
                'Vendor_Name': vendor_name,
                'Land_Type': land_type,
                'Task_Name': task_name,
                'Task_Category': category,
                'Task_Sequence': seq,
                'Planned_Start_Date': planned_start,
                'Planned_Duration': base_duration,
                'Actual_Duration': actual_duration,
                'Delay_Reason': delay_reason,
                # Helper Flags for Model
                'Monsoon_Flag': 1 if 6 <= planned_start.month <= 9 else 0
            })
            
            # Move date forward for next task (Sequential dependency)
            current_date = actual_end + timedelta(days=random.randint(0, 5)) # 0-5 days buffer between tasks

    return pd.DataFrame(data)

# ==============================================================================
# 5. EXECUTION
# ==============================================================================
if __name__ == "__main__":
    df = generate_synthetic_data(1500)
    df.to_csv("kpmg_pmis_synthetic_data.csv", index=False)
    print("SUCCESS: High-Fidelity Data Generated.")
    print(df.head())