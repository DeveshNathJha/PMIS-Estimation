import pandas as pd
from datetime import datetime, timedelta
import config

def get_nhm_districts(division, jharkhand_map):
    """Returns districts filtered by Division"""
    return [d for d, info in jharkhand_map.items() if info['Division'] == division]

def get_wbs_template_from_data(p_type, df):
    """
    Dynamically fetches the WBS (Tasks) for a Project Type from the Loaded Data.
    """
    # Check if required columns exist
    if 'Task_Sequence' not in df.columns:
        return None
    
    # Filter data for this project type
    subset = df[df['Project_Type'] == p_type].sort_values('Task_Sequence')
    
    # Get unique tasks in order
    tasks = subset[['Task_Name', 'Task_Category', 'Planned_Duration', 'Task_Sequence']].drop_duplicates('Task_Name')
    
    # Rename for App Table
    tasks = tasks.rename(columns={
        'Task_Sequence': 'Task_ID',
        'Planned_Duration': 'Planned_Duration'
    })
    
    # Add Predecessors Logic (Sequential: 2 depends on 1, 3 on 2...)
    tasks['Predecessors'] = tasks['Task_ID'].apply(lambda x: str(x-1) if x > 1 else '')
    
    return tasks.reset_index(drop=True)

def calculate_cpm(tasks_df):
    """
    Standard Critical Path Method (Forward & Backward Pass).
    Returns: (project_duration, critical_path_task_ids)
    """
    tasks = {}
    for _, row in tasks_df.iterrows():
        pid = str(row['Task_ID'])
        preds = str(row['Predecessors']).split(',') if row['Predecessors'] else []
        preds = [p.strip() for p in preds if p.strip() and p.strip() != '0']
        tasks[pid] = {'duration': row['Predicted_Duration'], 'predecessors': preds, 'es': 0, 'ef': 0, 'ls': 0, 'lf': 0}

    task_ids = sorted(list(tasks.keys()), key=lambda x: float(x))
    
    # FORWARD PASS: Calculate Early Start & Early Finish
    for _ in range(len(task_ids)): 
        for tid in task_ids:
            preds = tasks[tid]['predecessors']
            max_ef = 0
            for p in preds:
                if p in tasks: max_ef = max(max_ef, tasks[p]['ef'])
            tasks[tid]['es'] = max_ef
            tasks[tid]['ef'] = tasks[tid]['es'] + tasks[tid]['duration']

    project_duration = max([t['ef'] for t in tasks.values()]) if tasks else 0
    
    # BACKWARD PASS: Calculate Late Start & Late Finish
    for tid in task_ids:
        tasks[tid]['lf'] = project_duration
    
    for tid in reversed(task_ids):
        # Find successors
        successors_lf = []
        for other_tid in task_ids:
            if tid in tasks[other_tid]['predecessors']:
                successors_lf.append(tasks[other_tid]['ls'])
        
        if successors_lf:
            tasks[tid]['lf'] = min(successors_lf)
        else:
            tasks[tid]['lf'] = tasks[tid]['ef']  # End node
        
        tasks[tid]['ls'] = tasks[tid]['lf'] - tasks[tid]['duration']
    
    # CRITICAL PATH: Tasks with zero slack (LF - EF = 0)
    critical_path = [tid for tid, t in tasks.items() if abs((t['lf'] - t['ef'])) < 0.01]
    
    return project_duration, critical_path

def generate_granular_risk_assessment(row, predicted, planned, vendor_tier):
    """
    Logic:
    1. Compares Predicted vs Planned.
    2. If Predicted < Planned: It's an Efficiency Gain (Green).
    3. If Predicted > Planned: It checks specific flags (LWE, Land, Monsoon) to assign blame (Red).
    """
    # Safely coerce inputs to numeric and handle missing values
    try:
        pred_val = float(predicted) if predicted is not None else None
    except Exception:
        pred_val = None
    try:
        planned_val = float(planned) if planned is not None else None
    except Exception:
        planned_val = None

    if pd.isna(pred_val) or pd.isna(planned_val) or pred_val is None or planned_val is None:
        return 'Prediction unavailable'

    variance = pred_val - planned_val
    
    # CASE 1: EFFICIENCY GAIN
    if variance <= 0:
        if vendor_tier == 1:
            return "Efficiency Gain (Tier 1 Speed)"
        else:
            return "On Track / Fast Tracked"
            
    # CASE 2: MINOR VARIANCE
    if variance < (planned_val * 0.15): 
        return "Standard Variance"
        
    # CASE 3: SIGNIFICANT DELAY (Identify the Root Cause)
    reasons = []
    
    # Cause A: Land
    if str(row.get('Land_Type')) == config.LAND_TYPE_TRIBAL:
        reasons.append("CNT Act Land Issue")
    
    # Cause B: Security
    lwe_flag = row.get('LWE_Flag')
    if str(lwe_flag) == '1' or lwe_flag == 1:
        reasons.append("LWE Logistics Friction")
        
    # Cause C: Seasonality
    monsoon_flag = row.get('Monsoon_Flag')
    if str(monsoon_flag) == '1' or monsoon_flag == 1:
        reasons.append("Monsoon Slowdown")
        
    # Cause D: Procurement Complexity
    if str(row.get('Task_Category')) == config.TASK_CATEGORY_PROCUREMENT and variance > 20:
        reasons.append("Supply Chain/Import Delay")
        
    # Fallback if no specific flag but high delay
    if not reasons:
        reasons.append("Vendor Resource Constraints")
        
    return "DELAY: " + " + ".join(reasons) + f" (+{int(round(variance))} days)"
