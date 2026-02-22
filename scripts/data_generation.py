import pandas as pd
import random
import argparse
import argparse
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import config
from datetime import datetime, timedelta

# ==============================================================================
# 1. HELPER FUNCTIONS
# ==============================================================================

def get_random_date(start_year, end_year):
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
    state_data = config.STATE_PROFILE.get(state, {'logistics_friction': 1.1, 'monsoon_severity': 'Medium'})
    friction *= state_data['logistics_friction']
    
    # 3. LWE (Security Risk)
    if lwe == 1:
        friction *= 1.4 # High security risk adds 40% time
        
    # 4. Land Type (Only affects Regulatory/Civil tasks)
    if task_category in ['Regulatory', 'Civil', 'Admin'] and land_type == config.LAND_TYPE_TRIBAL:
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
# 2. MAIN GENERATION ENGINE
# ==============================================================================

def generate_synthetic_data(num_projects=1500, start_year=None, end_year=None):
    data = []
    
    if start_year is None:
        start_year = datetime.now().year - 2
    if end_year is None:
        end_year = datetime.now().year

    project_types = list(config.PROJECT_TEMPLATES.keys())
    districts = list(config.JHARKHAND_MAP.keys())
    states = list(config.STATE_PROFILE.keys())
    
    print(f"Generating data for {num_projects} projects...")
    
    for i in range(num_projects):
        pid = f"PROJ_{1000+i}"
        
        # 1. Select Project Type
        p_type = random.choice(project_types)
        
        # 2. Context Logic (State & District)
        # If it's a Kumbh project, MUST be in specific cities
        if p_type == 'Mega_Event_Kumbh':
            loc = random.choice(config.KUMBH_LOCATIONS)
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
                lwe_flag = config.JHARKHAND_MAP[district]['LWE']
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
                lwe_flag = config.JHARKHAND_MAP[district]['LWE']
            else:
                district = "Generic_District"
                lwe_flag = 0
            city_tier = random.choice(["Tier 1", "Tier 2", "Tier 3"])

        # 3. Vendor & Land Config
        # 3. Vendor & Land Config
        vendor_tier = random.choices([1, 2, 3], weights=config.VENDOR_TIER_WEIGHTS)[0]
        vendor_name = config.VENDOR_TIER_MAPPING[vendor_tier]
        
        land_type = random.choice(config.LAND_TYPES)
        
        # 4. Timeline Simulation
        current_date = get_random_date(start_year, end_year)
        
        # Iterate through WBS Phases
        phases = config.PROJECT_TEMPLATES[p_type]
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
            if category == 'Regulatory' and land_type == config.LAND_TYPE_TRIBAL:
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
# 3. EXECUTION
# ==============================================================================
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate synthetic PMIS data.")
    parser.add_argument("--count", type=int, default=1500, help="Number of projects to generate")
    parser.add_argument("--output", type=str, default=config.DATA_FILE, help="Output CSV filename")
    parser.add_argument("--seed", type=int, default=config.RANDOM_SEED, help="Random seed for reproducibility")
    
    args = parser.parse_args()
    
    # Set seed
    random.seed(args.seed)
    # Note: If numpy were used, we'd seed it too: np.random.seed(args.seed)
    
    df = generate_synthetic_data(args.count)
    df.to_csv(args.output, index=False)
    print(f"Synthetic Data Generated: {args.output}")
    print(df.head())