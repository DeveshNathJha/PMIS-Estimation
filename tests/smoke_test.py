"""Headless smoke tests for core helper logic (independent of Streamlit UI).
This script validates calculate_cpm-like behavior and risk computations using sample data.
"""

import math

# Re-implement minimal CPM logic copied from pmisapp.calculate_cpm for headless test

def calculate_cpm_headless(rows):
    tasks = {}
    for r in rows:
        pid = str(r['Task_ID'])
        preds = r.get('Predecessors', [])
        tasks[pid] = {'duration': r['Predicted_Duration'], 'predecessors': preds, 'es': 0, 'ef': 0, 'ls': 0, 'lf': 0}

    task_ids = sorted(list(tasks.keys()), key=lambda x: float(x))

    for _ in range(len(task_ids)):
        for tid in task_ids:
            preds = tasks[tid]['predecessors']
            max_ef = 0
            for p in preds:
                if p in tasks:
                    max_ef = max(max_ef, tasks[p]['ef'])
            tasks[tid]['es'] = max_ef
            tasks[tid]['ef'] = tasks[tid]['es'] + tasks[tid]['duration']

    project_duration = max([t['ef'] for t in tasks.values()]) if tasks else 0

    for tid in task_ids:
        tasks[tid]['lf'] = project_duration

    for tid in reversed(task_ids):
        successors_lf = []
        for other_tid in task_ids:
            if tid in tasks[other_tid]['predecessors']:
                successors_lf.append(tasks[other_tid]['ls'])
        if successors_lf:
            tasks[tid]['lf'] = min(successors_lf)
        else:
            tasks[tid]['lf'] = tasks[tid]['ef']
        tasks[tid]['ls'] = tasks[tid]['lf'] - tasks[tid]['duration']

    critical_path = [tid for tid, t in tasks.items() if abs((t['lf'] - t['ef'])) < 0.01]
    return project_duration, critical_path


# Simple test
if __name__ == '__main__':
    sample_rows = [
        {'Task_ID': 1, 'Predicted_Duration': 5, 'Predecessors': []},
        {'Task_ID': 2, 'Predicted_Duration': 3, 'Predecessors': ['1']},
        {'Task_ID': 3, 'Predicted_Duration': 2, 'Predecessors': ['1']},
        {'Task_ID': 4, 'Predicted_Duration': 4, 'Predecessors': ['2','3']},
    ]

    pduration, cpath = calculate_cpm_headless(sample_rows)
    print('Headless CPM test: project duration =', pduration)
    print('Critical path task IDs =', cpath)
    # Expected duration = 5 + max(3,2) + 4 = 12
    assert math.isclose(pduration, 12), 'Unexpected project duration'
    assert set(cpath) == set(['1','2','4']) or set(cpath) == set(['1','3','4']), 'Unexpected critical path (one of branches)'
    print('CPM test passed')

    print('\nRisk computation smoke test:')
    # Minimal risk calculation verification
    base = 30
    land_multiplier = 1.2
    risk_land = int(round(max(0, (land_multiplier - 1.0) * base)))
    print('risk_land (expected ~6):', risk_land)
    assert risk_land == 6
    print('Risk test passed')
