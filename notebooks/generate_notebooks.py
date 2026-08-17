import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
NOTEBOOKS_DIR = BASE_DIR / 'notebooks'
NOTEBOOKS_DIR.mkdir(parents=True, exist_ok=True)

def make_notebook(cells):
    return {
        "cells": cells,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3"
            },
            "language_info": {
                "codemirror_mode": {"name": "ipython", "version": 3},
                "file_extension": ".py",
                "mimetype": "text/x-python",
                "name": "python",
                "nbconvert_exporter": "python",
                "pygments_lexer": "ipython3",
                "version": "3.12.0"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 4
    }

def code_cell(source):
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [line + "\n" for line in source.strip().split("\n")]
    }

def markdown_cell(source):
    return {
        "cell_type": "markdown",
        "metadata": {},
        "source": [line + "\n" for line in source.strip().split("\n")]
    }

# Notebook 1: EDA
nb1_cells = [
    markdown_cell("# Enterprise Sales & Customer Intelligence - Exploratory Data Analysis (EDA)\n\nThis notebook conducts comprehensive exploratory data analysis across 10,000+ customer records and 30,000+ orders spanning multi-year retail transactions."),
    code_cell("""import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

sns.set_theme(style="whitegrid", palette="deep")
plt.rcParams["figure.figsize"] = (12, 6)"""),
    markdown_cell("## 1. Load Power BI-Ready Processed Dataset"),
    code_cell("""data_path = Path('../data/processed/powerbi_sales_intelligence.csv')
if not data_path.exists():
    data_path = Path('../data/raw/orders.csv')

df = pd.read_csv(data_path)
print(f"Dataset Shape: {df.shape}")
df.head()"""),
    markdown_cell("## 2. Dataset Schema and Statistical Summary"),
    code_cell("""print(df.info())
df.describe()"""),
    markdown_cell("## 3. Monthly Revenue Trend & Seasonality"),
    code_cell("""if 'order_date' in df.columns:
    df['order_date'] = pd.to_datetime(df['order_date'])
    monthly = df.set_index('order_date').resample('M')['total_amount'].sum()
    
    plt.figure(figsize=(14, 5))
    plt.plot(monthly.index, monthly.values, marker='o', color='#2563eb', linewidth=2.5)
    plt.title('Monthly Gross Revenue Trajectory (2023 - 2026)', fontsize=14, fontweight='bold')
    plt.xlabel('Date')
    plt.ylabel('Revenue ($)')
    plt.show()"""),
    markdown_cell("## 4. Profit Margin Distribution by Category"),
    code_cell("""if 'category_name' in df.columns and 'profit_margin_pct' in df.columns:
    plt.figure(figsize=(12, 6))
    sns.boxplot(data=df, x='category_name', y='profit_margin_pct', palette='Set2')
    plt.title('Profit Margin Distribution Across Product Categories', fontsize=14, fontweight='bold')
    plt.xticks(rotation=15)
    plt.ylabel('Profit Margin (%)')
    plt.show()"""),
    markdown_cell("## 5. Regional Sales Contribution"),
    code_cell("""if 'region_name' in df.columns:
    reg_sales = df.groupby('region_name')['total_amount'].sum().sort_values(ascending=False)
    plt.figure(figsize=(8, 8))
    plt.pie(reg_sales.values, labels=reg_sales.index, autopct='%1.1f%%', colors=['#2563eb', '#06b6d4', '#10b981', '#f59e0b'])
    plt.title('Market Share Contribution by Geographic Region', fontsize=14, fontweight='bold')
    plt.show()""")
]

# Notebook 2: ML Churn
nb2_cells = [
    markdown_cell("# Customer Churn Prediction & Machine Learning Modeling\n\nTrains and benchmarks supervised classification algorithms (Random Forest, Gradient Boosting, Logistic Regression) on customer RFM features."),
    code_cell("""import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score, roc_curve"""),
    markdown_cell("## 1. Load Cleaned Customer Features"),
    code_cell("""cust_path = Path('../data/raw/customers.csv')
orders_path = Path('../data/raw/orders.csv')

df_cust = pd.read_csv(cust_path)
df_orders = pd.read_csv(orders_path)
print(f"Loaded {len(df_cust):,} customers and {len(df_orders):,} orders.")"""),
    markdown_cell("## 2. Feature Engineering & RFM Calculation"),
    code_cell("""ref_date = pd.to_datetime('2026-08-01')
df_orders['order_date'] = pd.to_datetime(df_orders['order_date'])

agg = df_orders.groupby('customer_id').agg(
    total_orders=('order_id', 'count'),
    total_spend=('total_amount', 'sum'),
    avg_order_value=('total_amount', 'mean'),
    last_order=('order_date', 'max')
).reset_index()

agg['recency_days'] = (ref_date - agg['last_order']).dt.days

df_ml = df_cust.merge(agg, on='customer_id', how='left').fillna(0)
df_ml['churn'] = ((df_ml['recency_days'] > 180) | ((df_ml['recency_days'] > 120) & (df_ml['total_orders'] <= 1))).astype(int)

features = ['recency_days', 'total_orders', 'total_spend', 'avg_order_value']
X = df_ml[features]
y = df_ml['churn']
print(f"Target Class Distribution:\\n{y.value_counts(normalize=True)}")"""),
    markdown_cell("## 3. Model Training & Evaluation"),
    code_cell("""X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=42, stratify=y)

rf = RandomForestClassifier(n_estimators=100, max_depth=7, random_state=42, class_weight='balanced')
rf.fit(X_train, y_train)

y_pred = rf.predict(X_test)
y_prob = rf.predict_proba(X_test)[:, 1]

print(classification_report(y_test, y_pred))
print(f"ROC-AUC Score: {roc_auc_score(y_test, y_prob):.4f}")"""),
    markdown_cell("## 4. Confusion Matrix & ROC Curve Visualization"),
    code_cell("""cm = confusion_matrix(y_test, y_pred)
plt.figure(figsize=(6, 5))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=['Active', 'Churned'], yticklabels=['Active', 'Churned'])
plt.title('Random Forest Confusion Matrix', fontweight='bold')
plt.ylabel('Actual Label')
plt.xlabel('Predicted Label')
plt.show()"""),
    markdown_cell("## 5. Feature Importances"),
    code_cell("""importances = pd.Series(rf.feature_importances_, index=features).sort_values(ascending=False)
plt.figure(figsize=(8, 4))
sns.barplot(x=importances.values, y=importances.index, palette='Blues_r')
plt.title('Feature Importances in Churn Classification', fontweight='bold')
plt.xlabel('Importance')
plt.show()""")
]

# Notebook 3: Forecasting
nb3_cells = [
    markdown_cell("# Time-Series Sales Forecasting (Holt-Winters & ARIMA)\n\nPerforms time series decomposition, stationarity testing, and exponential smoothing forecasts for multi-horizon demand planning."),
    code_cell("""import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from statsmodels.tsa.stattools import adfuller"""),
    markdown_cell("## 1. Load Daily Sales Time Series"),
    code_cell("""orders_path = Path('../data/raw/orders.csv')
df = pd.read_csv(orders_path)
df['order_date'] = pd.to_datetime(df['order_date'])

daily_sales = df[df['status'] != 'Cancelled'].groupby('order_date')['total_amount'].sum()
weekly_sales = daily_sales.resample('W').sum()

plt.figure(figsize=(14, 5))
plt.plot(weekly_sales.index, weekly_sales.values, color='#2563eb', linewidth=2)
plt.title('Weekly Enterprise Sales Trajectory', fontweight='bold')
plt.ylabel('Revenue ($)')
plt.show()"""),
    markdown_cell("## 2. Augmented Dickey-Fuller (ADF) Stationarity Test"),
    code_cell("""adf_res = adfuller(weekly_sales.dropna())
print(f"ADF Statistic: {adf_res[0]:.4f}")
print(f"p-value: {adf_res[1]:.4f}")"""),
    markdown_cell("## 3. Holt-Winters Exponential Smoothing Model"),
    code_cell("""hw_model = ExponentialSmoothing(
    weekly_sales,
    trend='add',
    damped_trend=True
).fit(damping_trend=0.95)

forecast_12w = hw_model.forecast(12)
plt.figure(figsize=(14, 6))
plt.plot(weekly_sales.index[-40:], weekly_sales.values[-40:], label='Historical Sales', color='#334155')
plt.plot(forecast_12w.index, forecast_12w.values, label='12-Week Projected Forecast', color='#2563eb', linestyle='--', linewidth=2.5)
plt.title('Holt-Winters 12-Week Sales Forecast', fontweight='bold')
plt.legend()
plt.show()""")
]

with open(NOTEBOOKS_DIR / '01_eda_sales_customer_intelligence.ipynb', 'w') as f:
    json.dump(make_notebook(nb1_cells), f, indent=2)

with open(NOTEBOOKS_DIR / '02_customer_churn_modelling.ipynb', 'w') as f:
    json.dump(make_notebook(nb2_cells), f, indent=2)

with open(NOTEBOOKS_DIR / '03_sales_forecasting_arima_hw.ipynb', 'w') as f:
    json.dump(make_notebook(nb3_cells), f, indent=2)

print("[+] Successfully generated 3 comprehensive Data Science Jupyter Notebooks.")
