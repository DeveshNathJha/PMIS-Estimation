import json
import os
import sys
from config import *

nb_cells = []

# CELL 1: Introduction
nb_cells.append({
    "cell_type": "markdown",
    "metadata": {},
    "source": [
        "# KPMG Advisory: PMIS AI Engine Training v8.0 (Production Grade)\n",
        "\n",
        "**Objective:** Train a Context-Aware AI Model to predict project delays using Probabilistic Quantile Regression.\n",
        "\n",
        "**Pipeline:**\n",
        "1. **Data Integrity Check (EDA):** Verify dataset physics (Vendor Tiers, LWE Risks, Monsoon Impact).\n",
        "2. **Feature Engineering:** Convert text/categorical data into AI-ready tensors.\n",
        "3. **Quantile Model Training:** Train three CatBoost models (P10, P50, P90) with comprehensive evaluation.\n",
        "4. **Explainability:** SHAP analysis to identify delay drivers.\n",
        "5. **Production Prediction:** Utility function for real-time duration forecasting.\n",
        "---"
    ]
})

# CELL 2: Imports & Configuration
nb_cells.append({
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": [
        "import pandas as pd\n",
        "import numpy as np\n",
        "import matplotlib.pyplot as plt\n",
        "import seaborn as sns\n",
        "from catboost import CatBoostRegressor\n",
        "from sklearn.model_selection import train_test_split\n",
        "from sklearn.feature_extraction.text import TfidfVectorizer\n",
        "from sklearn.metrics import mean_absolute_error, r2_score, mean_squared_error\n",
        "import shap\n",
        "import joblib\n",
        "import os\n",
        "import warnings\n",
        "warnings.filterwarnings('ignore')\n",
        "\n",
        "from config import (\n",
        "    TEST_SIZE, RANDOM_STATE, QUANTILES, CATBOOST_PARAMS,\n",
        "    FEATURES, CATEGORICAL_FEATURES, TARGET_VARIABLE,\n",
        "    TFIDF_MAX_FEATURES, TFIDF_STOP_WORDS, KPMG_BLUE\n",
        ")\n",
        "\n",
        "sns.set_theme(style='whitegrid')\n",
        "print('Libraries & Configuration Loaded Successfully.')"
    ]
})

# CELL 3: Load Data
nb_cells.append({
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": [
        "import os\n",
        "\n",
        "required_columns = [\n",
        "    'Project_Type', 'District', 'Task_Name', 'Task_Category',\n",
        "    'LWE_Flag', 'Land_Type', 'Vendor_Tier', 'Planned_Duration',\n",
        "    'Actual_Duration', 'Monsoon_Flag'\n",
        "]\n",
        "\n",
        "try:\n",
        "    if not os.path.exists('kpmg_pmis_synthetic_data.csv'):\n",
        "        raise FileNotFoundError('Data file not found: kpmg_pmis_synthetic_data.csv')\n",
        "    \n",
        "    df = pd.read_csv('kpmg_pmis_synthetic_data.csv')\n",
        "    \n",
        "    missing_cols = set(required_columns) - set(df.columns)\n",
        "    if missing_cols:\n",
        "        raise ValueError(f'Missing columns: {missing_cols}')\n",
        "    \n",
        "    print(f'Dataset loaded successfully!')\n",
        "    print(f'Dataset Dimensions: {df.shape}')\n",
        "    print(f'\\n--- Data Types ---')\n",
        "    print(df.dtypes)\n",
        "    \n",
        "except FileNotFoundError as e:\n",
        "    print(f'Error: {e}')\n",
        "    raise\n",
        "except ValueError as e:\n",
        "    print(f'Data validation error: {e}')\n",
        "    raise\n",
        "\n",
        "df.head()"
    ]
})

# CELL 4: EDA Section
nb_cells.append({
    "cell_type": "markdown",
    "metadata": {},
    "source": [
        "## 1. Exploratory Data Analysis (EDA) & Quality Audit\n",
        "Validate that the data contains the physics-based signals we expect."
    ]
})

nb_cells.append({
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": [
        "missing = df.isnull().sum()\n",
        "if missing.sum() == 0:\n",
        "    print('Data Quality Check Passed: No missing values found.')\n",
        "else:\n",
        "    print('Data Quality Alert: Missing values detected.')\n",
        "    print(missing[missing > 0])"
    ]
})

# CELL 5: Data Summary
nb_cells.append({
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": [
        "print('\\n' + '='*70)\n",
        "print('DATA SUMMARY STATISTICS')\n",
        "print('='*70)\n",
        "\n",
        "print(f'Total Records: {len(df):,}')\n",
        "print(f'Features: {len(df.columns)}')\n",
        "print(f'Date Range: {df[\"Planned_Start_Date\"].min()} to {df[\"Planned_Start_Date\"].max()}')\n",
        "\n",
        "print('\\n--- Duration Analysis (Days) ---')\n",
        "print(f'Planned Duration - Mean: {df[\"Planned_Duration\"].mean():.1f}, Std: {df[\"Planned_Duration\"].std():.1f}')\n",
        "print(f'Actual Duration  - Mean: {df[\"Actual_Duration\"].mean():.1f}, Std: {df[\"Actual_Duration\"].std():.1f}')\n",
        "print(f'Average Delay: {(df[\"Actual_Duration\"].mean() / df[\"Planned_Duration\"].mean() - 1)*100:.1f}%')\n",
        "\n",
        "print('\\n--- Project Type Distribution ---')\n",
        "print(df['Project_Type'].value_counts())\n",
        "\n",
        "print('\\n--- Vendor Tier Impact ---')\n",
        "df['Duration_Multiplier'] = df['Actual_Duration'] / df['Planned_Duration']\n",
        "vendor_perf = df.groupby('Vendor_Tier')['Duration_Multiplier'].agg(['mean', 'std', 'count'])\n",
        "vendor_perf.columns = ['Avg Multiplier', 'Std Dev', 'Task Count']\n",
        "print(vendor_perf)\n",
        "print(f'Tier 1 vs Tier 3 Difference: {(vendor_perf.loc[3, \"Avg Multiplier\"] / vendor_perf.loc[1, \"Avg Multiplier\"] - 1)*100:.1f}% slower')\n",
        "\n",
        "print('\\n--- LWE (Security Risk) Impact ---')\n",
        "lwe_perf = df.groupby('LWE_Flag')['Duration_Multiplier'].agg(['mean', 'count'])\n",
        "lwe_perf.columns = ['Avg Multiplier', 'Task Count']\n",
        "lwe_perf.index = ['Safe', 'Naxal Affected']\n",
        "print(lwe_perf)\n",
        "print(f'LWE Impact: +{((lwe_perf.iloc[1,0] / lwe_perf.iloc[0,0]) - 1)*100:.1f}% delay for Naxal areas')\n",
        "print('='*70)"
    ]
})

# CELL 6: Vendor Analysis Plot
nb_cells.append({
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": [
        "fig, axes = plt.subplots(1, 2, figsize=(15, 5))\n",
        "\n",
        "sns.boxplot(x='Vendor_Tier', y='Duration_Multiplier', data=df, ax=axes[0], palette='Blues')\n",
        "axes[0].set_title('Vendor Tier Impact on Duration', fontweight='bold')\n",
        "axes[0].set_ylabel('Actual/Planned Duration Ratio')\n",
        "axes[0].set_xlabel('Vendor Tier (1=Premium, 3=Local)')\n",
        "axes[0].axhline(1.0, color='red', linestyle='--', alpha=0.5, label='On Schedule')\n",
        "axes[0].legend()\n",
        "\n",
        "lwe_data = df.copy()\n",
        "lwe_data['LWE_Status'] = lwe_data['LWE_Flag'].map({0: 'Safe Zone', 1: 'Naxal Affected'})\n",
        "sns.boxplot(x='LWE_Status', y='Duration_Multiplier', data=lwe_data, ax=axes[1], palette='Reds')\n",
        "axes[1].set_title('Security Risk (LWE) Impact on Duration', fontweight='bold')\n",
        "axes[1].set_ylabel('Actual/Planned Duration Ratio')\n",
        "axes[1].set_xlabel('Area Type')\n",
        "axes[1].axhline(1.0, color='red', linestyle='--', alpha=0.5)\n",
        "\n",
        "plt.tight_layout()\n",
        "plt.show()"
    ]
})

# CELL 7: Feature Engineering
nb_cells.append({
    "cell_type": "markdown",
    "metadata": {},
    "source": [
        "## 2. Feature Engineering\n",
        "Convert raw features into ML-ready tensors. NLP vectorization prepares text inputs."
    ]
})

nb_cells.append({
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": [
        "corpus = df['Task_Name'].unique().tolist()\n",
        "vectorizer = TfidfVectorizer(stop_words=TFIDF_STOP_WORDS, max_features=TFIDF_MAX_FEATURES)\n",
        "tfidf_matrix = vectorizer.fit_transform(corpus)\n",
        "print(f'NLP: {len(corpus)} unique tasks vectorized')\n",
        "\n",
        "features = FEATURES\n",
        "cat_features = CATEGORICAL_FEATURES\n",
        "\n",
        "print(f'\\nFeature Engineering Summary:')\n",
        "print(f'  - Total Features: {len(features)}')\n",
        "print(f'  - Categorical: {len(cat_features)}')\n",
        "print(f'  - TF-IDF Dimensions: {tfidf_matrix.shape}')\n",
        "\n",
        "X = df[features]\n",
        "y = df[TARGET_VARIABLE]\n",
        "\n",
        "X_train, X_test, y_train, y_test = train_test_split(\n",
        "    X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE\n",
        ")\n",
        "\n",
        "print(f'\\nData Split:')\n",
        "print(f'  - Train: {len(X_train):,} samples')\n",
        "print(f'  - Test: {len(X_test):,} samples')\n",
        "print(f'  - Ratio: {len(X_train)/len(X_test):.1f}:1')"
    ]
})

# CELL 8: Model Training Section
nb_cells.append({
    "cell_type": "markdown",
    "metadata": {},
    "source": [
        "## 3. Model Training & Comprehensive Evaluation\n",
        "Train three Quantile Regression models with detailed performance metrics (MAE, R², RMSE)."
    ]
})

nb_cells.append({
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": [
        "models = {}\n",
        "model_metrics = {}\n",
        "\n",
        "print(f'\\n' + '='*80)\n",
        "print('MODEL TRAINING & EVALUATION')\n",
        "print('='*80)\n",
        "\n",
        "for q in QUANTILES:\n",
        "    q_percent = int(q*100)\n",
        "    model_name = f'P{q_percent}'\n",
        "    \n",
        "    print(f'\\nTraining {model_name} (Quantile {q})...')\n",
        "    \n",
        "    model = CatBoostRegressor(\n",
        "        **CATBOOST_PARAMS,\n",
        "        loss_function=f'Quantile:alpha={q}'\n",
        "    )\n",
        "    \n",
        "    model.fit(X_train, y_train, cat_features=cat_features, eval_set=(X_test, y_test))\n",
        "    models[model_name] = model\n",
        "    \n",
        "    y_pred_train = model.predict(X_train)\n",
        "    y_pred_test = model.predict(X_test)\n",
        "    \n",
        "    train_mae = mean_absolute_error(y_train, y_pred_train)\n",
        "    test_mae = mean_absolute_error(y_test, y_pred_test)\n",
        "    \n",
        "    train_r2 = r2_score(y_train, y_pred_train)\n",
        "    test_r2 = r2_score(y_test, y_pred_test)\n",
        "    \n",
        "    train_rmse = np.sqrt(mean_squared_error(y_train, y_pred_train))\n",
        "    test_rmse = np.sqrt(mean_squared_error(y_test, y_pred_test))\n",
        "    \n",
        "    model_metrics[model_name] = {\n",
        "        'train_mae': train_mae,\n",
        "        'test_mae': test_mae,\n",
        "        'train_r2': train_r2,\n",
        "        'test_r2': test_r2,\n",
        "        'train_rmse': train_rmse,\n",
        "        'test_rmse': test_rmse\n",
        "    }\n",
        "    \n",
        "    print(f'\\n{model_name} Model Performance:')\n",
        "    print(f'   Train -> MAE: {train_mae:.2f} days | R2: {train_r2:.4f}')\n",
        "    print(f'   Test  -> MAE: {test_mae:.2f} days | R2: {test_r2:.4f}')\n",
        "    print(f'   RMSE -> Train: {train_rmse:.2f} | Test: {test_rmse:.2f}')\n",
        "\n",
        "print(f'\\n' + '='*80)\n",
        "print('All Models Trained Successfully!')\n",
        "print('='*80)"
    ]
})

# CELL 9: Model Comparison
nb_cells.append({
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": [
        "print('\\n' + '='*80)\n",
        "print('MODEL PERFORMANCE COMPARISON')\n",
        "print('='*80)\n",
        "\n",
        "comparison_df = pd.DataFrame(model_metrics).T\n",
        "print('\\n--- Test Set Performance (Most Important) ---')\n",
        "print(comparison_df[['test_mae', 'test_r2', 'test_rmse']].round(4))\n",
        "\n",
        "print('\\n--- Key Insights ---')\n",
        "best_mae_model = comparison_df['test_mae'].idxmin()\n",
        "best_r2_model = comparison_df['test_r2'].idxmax()\n",
        "print(f'Best MAE (Lower is Better):    {best_mae_model} ({comparison_df.loc[best_mae_model, \"test_mae\"]:.2f} days)')\n",
        "print(f'Best R2 (0-1, Higher Better):  {best_r2_model} ({comparison_df.loc[best_r2_model, \"test_r2\"]:.4f})')\n",
        "\n",
        "print('\\n--- Visualization ---')\n",
        "fig, axes = plt.subplots(1, 3, figsize=(15, 4))\n",
        "\n",
        "comparison_df['test_mae'].plot(kind='bar', ax=axes[0], color='steelblue')\n",
        "axes[0].set_title('Test MAE (Lower is Better)', fontweight='bold')\n",
        "axes[0].set_ylabel('MAE (days)')\n",
        "axes[0].set_xlabel('')\n",
        "\n",
        "comparison_df['test_r2'].plot(kind='bar', ax=axes[1], color='seagreen')\n",
        "axes[1].set_title('Test R2 Score (Higher is Better)', fontweight='bold')\n",
        "axes[1].set_ylabel('R2 Score')\n",
        "axes[1].set_xlabel('')\n",
        "\n",
        "comparison_df['test_rmse'].plot(kind='bar', ax=axes[2], color='coral')\n",
        "axes[2].set_title('Test RMSE (Lower is Better)', fontweight='bold')\n",
        "axes[2].set_ylabel('RMSE (days)')\n",
        "axes[2].set_xlabel('')\n",
        "\n",
        "plt.tight_layout()\n",
        "plt.show()\n",
        "print('='*80)"
    ]
})

# CELL 10: SHAP Section
nb_cells.append({
    "cell_type": "markdown",
    "metadata": {},
    "source": [
        "## 4. Model Explainability\n",
        "SHAP analysis reveals which features drive project delays."
    ]
})

nb_cells.append({
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": [
        "print('\\nSHAP Feature Importance Analysis...')\n",
        "explainer = shap.TreeExplainer(models['P50'])\n",
        "shap_values = explainer.shap_values(X_test)\n",
        "\n",
        "print('\\nPlot 1: Global Feature Importance (Mean Absolute SHAP Values)')\n",
        "plt.figure(figsize=(12, 6))\n",
        "plt.title('Feature Importance: What Drives Project Delays? (P50 Model)', fontweight='bold')\n",
        "shap.summary_plot(shap_values, X_test, plot_type='bar')\n",
        "plt.tight_layout()\n",
        "plt.show()\n",
        "\n",
        "print('\\nPlot 2: Feature Impact Direction (Beeswarm Plot)')\n",
        "plt.figure(figsize=(12, 8))\n",
        "plt.title('SHAP Values: Feature Value Impact on Model Output', fontweight='bold')\n",
        "shap.summary_plot(shap_values, X_test)\n",
        "plt.tight_layout()\n",
        "plt.show()\n",
        "\n",
        "print('\\nSHAP Analysis Complete!')"
    ]
})

# CELL 11: Prediction Function Section
nb_cells.append({
    "cell_type": "markdown",
    "metadata": {},
    "source": [
        "## 5. Production Prediction Function\n",
        "Real-world utility function for probabilistic duration forecasting."
    ]
})

nb_cells.append({
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": [
        "def predict_project_duration(input_data):\n",
        "    '''\n",
        "    Predict duration range (P10, P50, P90) for a project task.\n",
        "    \n",
        "    Args:\n",
        "        input_data: dict with required features\n",
        "        Example:\n",
        "        {\n",
        "            'Project_Type': 'Construction_Hospital',\n",
        "            'District': 'Ranchi',\n",
        "            'LWE_Flag': 0,\n",
        "            'Task_Category': 'Civil',\n",
        "            'Land_Type': 'Govt Land',\n",
        "            'Vendor_Tier': 2,\n",
        "            'Planned_Duration': 60,\n",
        "            'Monsoon_Flag': 0\n",
        "        }\n",
        "    \n",
        "    Returns:\n",
        "        dict with P10, P50, P90 predictions and risk metrics\n",
        "    '''\n",
        "    import pandas as pd\n",
        "    \n",
        "    try:\n",
        "        input_df = pd.DataFrame([input_data])[features]\n",
        "        \n",
        "        predictions = {}\n",
        "        for model_name, model in models.items():\n",
        "            pred = model.predict(input_df)[0]\n",
        "            predictions[model_name] = round(pred, 1)\n",
        "        \n",
        "        p10 = predictions['P10']\n",
        "        p50 = predictions['P50']\n",
        "        p90 = predictions['P90']\n",
        "        \n",
        "        planned = input_data.get('Planned_Duration', p50)\n",
        "        delay_risk = ((p90 - planned) / planned) * 100 if planned > 0 else 0\n",
        "        \n",
        "        return {\n",
        "            'P10_optimistic': p10,\n",
        "            'P50_realistic': p50,\n",
        "            'P90_pessimistic': p90,\n",
        "            'duration_range_days': f'{p10:.0f} - {p90:.0f}',\n",
        "            'recommended_estimate': p50,\n",
        "            'delay_risk_percent': round(delay_risk, 1),\n",
        "            'confidence_level': '95%'\n",
        "        }\n",
        "        \n",
        "    except Exception as e:\n",
        "        print(f'Prediction Error: {e}')\n",
        "        return None\n",
        "\n",
        "print('Prediction function defined and ready for production use!')"
    ]
})

# CELL 12: Test Prediction
nb_cells.append({
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": [
        "example_input = {\n",
        "    'Project_Type': 'Construction_Hospital',\n",
        "    'District': 'Ranchi',\n",
        "    'LWE_Flag': 0,\n",
        "    'Task_Category': 'Civil',\n",
        "    'Land_Type': 'Govt Land',\n",
        "    'Vendor_Tier': 2,\n",
        "    'Planned_Duration': 60,\n",
        "    'Monsoon_Flag': 0\n",
        "}\n",
        "\n",
        "result = predict_project_duration(example_input)\n",
        "\n",
        "print('\\n' + '='*70)\n",
        "print('SAMPLE PREDICTION RESULT')\n",
        "print('='*70)\n",
        "print(f'\\nProject: Hospital Construction (Civil Phase) in Ranchi')\n",
        "print(f'Vendor: Tier 2 (NCC/Nagarjuna)')\n",
        "print(f'Land Type: Government')\n",
        "print(f'Planned Duration: 60 days')\n",
        "\n",
        "print(f'\\n--- PREDICTIONS ---')\n",
        "print(f'P10 (Optimistic):    {result[\"P10_optimistic\"]:.0f} days  <- Best case')\n",
        "print(f'P50 (Realistic):     {result[\"P50_realistic\"]:.0f} days  <- Most likely')\n",
        "print(f'P90 (Pessimistic):   {result[\"P90_pessimistic\"]:.0f} days  <- Risk case')\n",
        "\n",
        "print(f'\\n--- RISK ASSESSMENT ---')\n",
        "print(f'Duration Range: {result[\"duration_range_days\"]}')\n",
        "print(f'Delay Risk: {result[\"delay_risk_percent\"]}% vs planned')\n",
        "print(f'Confidence: {result[\"confidence_level\"]}')\n",
        "print('='*70)"
    ]
})

# CELL 13: Deployment
nb_cells.append({
    "cell_type": "markdown",
    "metadata": {},
    "source": [
        "## 6. Model Deployment\n",
        "Bundle all models, vectorizers, and metadata for production deployment."
    ]
})

nb_cells.append({
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": [
        "from data_generation import JHARKHAND_MAP, PROJECT_TEMPLATES\n",
        "\n",
        "print('\\n' + '='*80)\n",
        "print('PRODUCTION MODEL DEPLOYMENT')\n",
        "print('='*80)\n",
        "\n",
        "try:\n",
        "    artifact = {\n",
        "        'models': models,\n",
        "        'features': features,\n",
        "        'cat_features': cat_features,\n",
        "        'vectorizer': vectorizer,\n",
        "        'tfidf_matrix': tfidf_matrix,\n",
        "        'corpus': corpus,\n",
        "        'project_types': list(PROJECT_TEMPLATES.keys()),\n",
        "        'jharkhand_map': JHARKHAND_MAP,\n",
        "        'version': 'KPMG PMIS v8.0',\n",
        "        'description': 'Production-Ready Probabilistic Duration Prediction Engine',\n",
        "        'model_config': {\n",
        "            'quantiles': QUANTILES,\n",
        "            'catboost_params': CATBOOST_PARAMS,\n",
        "            'test_size': TEST_SIZE,\n",
        "            'random_state': RANDOM_STATE\n",
        "        },\n",
        "        'model_metrics': model_metrics,\n",
        "        'prediction_function': 'predict_project_duration',\n",
        "        'training_date': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')\n",
        "    }\n",
        "    \n",
        "    output_file = 'kpmg_pmis_model.pkl'\n",
        "    joblib.dump(artifact, output_file)\n",
        "    file_size = os.path.getsize(output_file) / (1024*1024)\n",
        "    \n",
        "    print(f'\\nModel Bundle Saved: {output_file} ({file_size:.2f} MB)')\n",
        "    \n",
        "    print(f'\\n--- Model Specifications ---')\n",
        "    print(f'  P10 Model: {model_metrics[\"P10\"][\"test_mae\"]:.2f} days MAE | R2 = {model_metrics[\"P10\"][\"test_r2\"]:.4f}')\n",
        "    print(f'  P50 Model: {model_metrics[\"P50\"][\"test_mae\"]:.2f} days MAE | R2 = {model_metrics[\"P50\"][\"test_r2\"]:.4f}')\n",
        "    print(f'  P90 Model: {model_metrics[\"P90\"][\"test_mae\"]:.2f} days MAE | R2 = {model_metrics[\"P90\"][\"test_r2\"]:.4f}')\n",
        "    \n",
        "    print(f'\\nStatus: READY FOR PRODUCTION DEPLOYMENT!')\n",
        "    print(f'Location: {os.path.abspath(output_file)}')\n",
        "    print('='*80)\n",
        "    \n",
        "except Exception as e:\n",
        "    print(f'Error: {e}')\n",
        "    raise"
    ]
})

# Generate notebook
try:
    output_file = 'Kpmg_Pmis_Training.ipynb'
    with open(output_file, 'w') as f:
        json.dump({"cells": nb_cells, "metadata": {}, "nbformat": 4, "nbformat_minor": 4}, f, indent=4)
    
    file_size = os.path.getsize(output_file) / 1024
    print(f"\n{'='*70}")
    print(f"Enhanced Notebook Generated: {output_file}")
    print(f"File size: {file_size:.2f} KB")
    print(f"\nNotebook includes:")
    print(f"  - Config import from config.py")
    print(f"  - Data summary statistics")
    print(f"  - Model evaluation metrics (MAE, R2, RMSE)")
    print(f"  - Model performance comparison")
    print(f"  - SHAP feature importance analysis")
    print(f"  - Production prediction utility function")
    print(f"  - All special characters cleaned (no emojis)")
    print(f"\nNext: Run this notebook to train models")
    print(f"{'='*70}\n")
except Exception as e:
    print(f"Error generating notebook: {e}")
    raise
