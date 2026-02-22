print("DEBUG: Starting script execution...")
import pandas as pd
print("DEBUG: Pandas imported")
import numpy as np
print("DEBUG: Numpy imported")
import matplotlib.pyplot as plt
import seaborn as sns
from catboost import CatBoostRegressor
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import mean_absolute_error, r2_score, mean_squared_error
from sklearn.linear_model import BayesianRidge
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import shap
import joblib
import os
import warnings
warnings.filterwarnings('ignore')

import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config import (
    TEST_SIZE, RANDOM_STATE, QUANTILES, CATBOOST_PARAMS,
    FEATURES, CATEGORICAL_FEATURES, TARGET_VARIABLE,
    TFIDF_MAX_FEATURES, TFIDF_STOP_WORDS
)
import config

sns.set_theme(style='whitegrid')
print('Libraries & Configuration Loaded Successfully.')

# --- LOAD DATA ---
required_columns = [
    'Project_Type', 'District', 'Task_Name', 'Task_Category',
    'LWE_Flag', 'Land_Type', 'Vendor_Tier', 'Planned_Duration',
    'Actual_Duration', 'Monsoon_Flag'
]

if not os.path.exists(config.DATA_FILE):
    raise FileNotFoundError(f'Data file not found: {config.DATA_FILE}')

df = pd.read_csv(config.DATA_FILE)
print(f'Dataset loaded successfully! Dimensions: {df.shape}')

# --- FEATURE ENGINEERING ---
corpus = df['Task_Name'].unique().tolist()
vectorizer = TfidfVectorizer(stop_words=TFIDF_STOP_WORDS, max_features=TFIDF_MAX_FEATURES)
tfidf_matrix = vectorizer.fit_transform(corpus)
print(f'NLP: {len(corpus)} unique tasks vectorized')

# Placeholder for future NLP integration (Commented out as requested)
# tfidf_df = pd.DataFrame(tfidf_matrix.toarray(), columns=vectorizer.get_feature_names_out())
# X = df[FEATURES]
# # ... concatenation logic ...

X = df[FEATURES]
y = df[TARGET_VARIABLE]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE
)
print(f'Train size: {len(X_train)}, Test size: {len(X_test)}')

# --- MODEL TRAINING ---
models = {}
model_metrics = {}

print('\n' + '='*80)
print('MODEL TRAINING & EVALUATION')
print('='*80)

for q in QUANTILES:
    q_percent = int(q*100)
    model_name = f'P{q_percent}'
    
    print(f'\nTraining {model_name} (Quantile {q})...')
    
    model = CatBoostRegressor(
        **CATBOOST_PARAMS,
        loss_function=f'Quantile:alpha={q}'
    )
    
    model.fit(X_train, y_train, cat_features=CATEGORICAL_FEATURES, eval_set=(X_test, y_test), verbose=False)
    models[model_name] = model
    
    y_pred_train = model.predict(X_train)
    y_pred_test = model.predict(X_test)
    
    metrics = {
        'train_mae': mean_absolute_error(y_train, y_pred_train),
        'test_mae': mean_absolute_error(y_test, y_pred_test),
        'train_r2': r2_score(y_train, y_pred_train),
        'test_r2': r2_score(y_test, y_pred_test),
        'train_rmse': np.sqrt(mean_squared_error(y_train, y_pred_train)),
        'test_rmse': np.sqrt(mean_squared_error(y_test, y_pred_test))
    }
    model_metrics[model_name] = metrics
    
    print(f'{model_name} Test MAE: {metrics["test_mae"]:.2f} | R2: {metrics["test_r2"]:.4f}')

# --- BAYESIAN RIDGE (COMPARISON) ---
print(f'\nTraining Bayesian Ridge (Baseline Comparison)...')
preprocessor = ColumnTransformer(
    transformers=[
        ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), CATEGORICAL_FEATURES)
    ],
    remainder='passthrough'
)

bayesian_model = Pipeline(steps=[
    ('preprocessor', preprocessor),
    ('regressor', BayesianRidge())
])

bayesian_model.fit(X_train, y_train)
models['BayesianRidge'] = bayesian_model

y_pred_test_bayes = bayesian_model.predict(X_test)
b_metrics = {
    'test_mae': mean_absolute_error(y_test, y_pred_test_bayes),
    'test_r2': r2_score(y_test, y_pred_test_bayes),
    'test_rmse': np.sqrt(mean_squared_error(y_test, y_pred_test_bayes))
}
model_metrics['BayesianRidge'] = b_metrics
print(f'BayesianRidge Test MAE: {b_metrics["test_mae"]:.2f} | R2: {b_metrics["test_r2"]:.4f}')

# --- COMPARISON OUTPUT ---
print('\n' + '='*80)
print('MODEL PERFORMANCE SUMMARY')
print('='*80)
comparison_df = pd.DataFrame(model_metrics).T
print(comparison_df[['test_mae', 'test_r2', 'test_rmse']].round(4))

# --- DEPLOYMENT ---
# from data_generation import JHARKHAND_MAP, PROJECT_TEMPLATES (Removed)
# Uses config.JHARKHAND_MAP directly below

artifact = {
    'models': models,
    'features': FEATURES,
    'cat_features': CATEGORICAL_FEATURES,
    'vectorizer': vectorizer,
    'tfidf_matrix': tfidf_matrix,
    'corpus': corpus,
    'project_types': list(config.PROJECT_TEMPLATES.keys()),
    'jharkhand_map': config.JHARKHAND_MAP,
    'version': 'PMIS v8.0',
    'description': 'Production-Ready Probabilistic Duration Prediction Engine',
    'model_config': {
        'quantiles': QUANTILES,
        'catboost_params': CATBOOST_PARAMS,
        'test_size': TEST_SIZE,
        'random_state': RANDOM_STATE
    },
    'model_metrics': model_metrics,
    'prediction_function': 'predict_project_duration',
    'training_date': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
}

output_file = config.MODEL_OUTPUT_FILE
joblib.dump(artifact, output_file)
print(f'\nModel Bundle Saved: {output_file}')
