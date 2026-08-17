# Enterprise Sales & Customer Intelligence Platform
> **Production-Grade Data Analytics, Machine Learning, SQL, Business Intelligence & Automated Reporting Ecosystem**

[![Python 3.12](https://img.shields.io/badge/Python-3.12+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.3+-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-1.3+-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)](https://scikit-learn.org/)
[![MySQL](https://img.shields.io/badge/MySQL-8.0+-4479A1?style=for-the-badge&logo=mysql&logoColor=white)](https://mysql.com)
[![Power BI Ready](https://img.shields.io/badge/Power_BI-Ready-F2C811?style=for-the-badge&logo=powerbi&logoColor=black)](https://powerbi.microsoft.com/)
[![ReportLab](https://img.shields.io/badge/ReportLab-PDF_Engine-FF6F00?style=for-the-badge)](https://www.reportlab.com/)

---

## 📌 Executive Overview
The **Enterprise Sales & Customer Intelligence Platform** is an end-to-end analytics and predictive intelligence platform designed to eliminate enterprise revenue leakage, optimize product portfolio margins, predict customer churn before contract expiration, and forecast quarterly demand with statistical confidence intervals.

Unlike simple dashboard prototypes with hardcoded figures, this system features a **production ETL pipeline**, **normalized 3NF relational data warehouse** (supporting MySQL & SQLite), **real Scikit-Learn supervised classification models**, **Holt-Winters time-series forecasting**, **RFM customer segmentation with K-Means clustering**, a **real-time What-If scenario financial simulator**, **dynamic automated business insights**, and **programmatic PDF report generation via ReportLab**.

---

## 🏛️ System Architecture

```mermaid
graph TD
    A[Raw CSV Transaction Streams / Data Upload] --> B[Automated ETL & Data Cleaner Module]
    B --> C[(Relational Warehouse: MySQL / SQLAlchemy)]
    C --> D[SQL Analytics & Aggregation Engine]
    C --> E[Machine Learning Engine: Churn, RFM, Holt-Winters]
    D --> F[Flask REST API & Business Insights Engine]
    E --> F
    F --> G[Interactive Enterprise SaaS Web Interface]
    F --> H[ReportLab Automated C-Suite PDF Reports]
    B --> I[Cleaned Power BI-Ready CSV Export]
```

---

## 🚀 Key Modules & Capabilities

### 1. 📊 Executive C-Suite Dashboard
- **8 Core Financial & Operational KPI Cards:** Total Revenue, Total Net Profit, Operating Profit Margin %, Total Orders, Customer Count, Average Order Value (AOV), Customer Retention Rate %, and High Churn Risk %.
- **Multi-Parameter Dynamic Filter Bar:** Filter analytics on the fly by Date Range, Geographic Region, Product Category, and Customer Segment.
- **Interactive Visualizations:** Monthly Revenue/Profit trend lines, Regional Market Share donuts, Category revenue bars, and RFM segment distributions.
- **Top 10 Rankings:** Real-time leaderboards for top grossing enterprise products and highest-spend customer accounts.

### 2. 📈 Sales Analytics & Rep Quota Performance
- **Sales Velocity:** Daily, weekly, monthly, and yearly transaction aggregates with gross margin analysis.
- **Month-over-Month (MoM) Growth:** Automatic calculation of percentage revenue acceleration and contraction.
- **Sales Representative Quota Leaderboard:** Individual annual sales quota attainment tracker with status badges (*Quota Exceeded*, *On Track*, *Underperforming*).

### 3. 👥 Customer Analytics & RFM Segmentation
- **5-Quintile Mathematical RFM Scoring:** Recency (days since last purchase), Frequency (order volume), and Monetary (total customer spend) with score calculation ($111 \text{ to } 555$).
- **Customer Segmentation Tiers:** *Champions, Loyal Customers, Potential Loyalists, New Customers, At Risk, Lost Customers*.
- **Unsupervised K-Means Behavioral Clustering:** 4 distinct multi-dimensional customer behavioral profiles.
- **Searchable Customer Intelligence Table:** Paginated, searchable directory displaying account codes, company names, RFM quintiles, lifetime value (CLV), and individual churn risk probabilities.

### 4. 🤖 Customer Churn Machine Learning Prediction
- **Classification Algorithms:** Supervised **Random Forest Classifier** and **Gradient Boosting** trained on actual customer behavioral matrices.
- **Genuine Evaluation Transparency:** Real Accuracy, Precision, Recall, F1 Score, ROC-AUC score, Confusion Matrix (TP, FP, TN, FN), and ROC curve coordinates.
- **Live Account Churn Scorer:** Interactive tester allowing analysts to input any Customer ID to retrieve live churn probabilities, identified behavioral risk drivers, and tailored prescriptive retention recommendations.

### 5. 🔮 Time-Series Sales Demand Forecasting
- **Forecasting Algorithm:** **Holt-Winters Exponential Smoothing** with additive trend damping and seasonal cycles.
- **Multi-Horizon Planning:** Selectable forward horizons for **30 Days**, **90 Days (Quarter)**, and **180 Days (6 Months)**.
- **Confidence Intervals:** 95% upper and lower statistical confidence bounds.
- **Executive Demand Outlook:** Automatic generation of projected growth percentages and operational supply chain interpretations.

### 6. 📦 Product Profitability & 4-Quadrant Matrix
- **4-Quadrant Classification:**
  - 🌟 **Star Performers:** High Revenue + High Profit
  - 📦 **Volume Drivers:** High Revenue + Low Profit (identifies margin dilutive SKUs)
  - 💎 **Niche High Margin:** Low Revenue + High Profit (expansion candidates)
  - ⚠️ **Underperformers:** Low Revenue + Low Profit (phase-out candidates)
- **Discount Sensitivity & Return Rate:** SKU-level return percentages and average discount tracking.

### 7. 🌍 Regional Intelligence & Market Territories
- **Geographic Coverage:** North America East, West, Central, and South territories.
- **Territory Standouts:** Automated classification of Best-Performing, Worst-Performing, Fastest-Growing, and Declining regions.

### 8. 🎛️ Interactive What-If Scenario Financial Simulator
- **Dynamic Financial Levers:** Real-time sliders for Price Adjustment (-20% to +30%), Discount Allowance (-10% to +20%), Sales Volume Shift (-30% to +50%), and Incremental Marketing Budget ($0 to $200k).
- **Instant Financial Projections:** Live side-by-side comparison of baseline vs. simulated Revenue, Operating Cost, Net Profit, Profit Margin %, and Marketing Return on Investment (ROI).

### 9. 📥 Data Ingestion, Quality Audits & ETL Pipeline
- **Dataset Upload:** Drag-and-drop CSV upload with automated data cleaning, missing value imputation, duplicate removal, and schema validation summary.
- **Power BI Ready Export:** Automatic generation of flattened, cleaned dataset at `data/processed/powerbi_sales_intelligence.csv`.

### 10. 📑 Programmatic PDF Report Generator
- **ReportLab Engine:** Generates styled multi-page PDF reports for *Executive C-Suite Briefing*, *Sales Performance*, *Customer Churn Risk*, and *Demand Forecasting*.

---

## 🗄️ Relational Database Schema

```
database/
├── schema.sql    # Standard ANSI/MySQL DDL with Primary Keys, Foreign Keys & Indexes
└── seed.sql      # Seed definitions for users, roles, categories, and territories
```

### Advanced SQL Query Highlights
- **RFM Quintile Scoring with `NTILE()`:**
  ```sql
  SELECT customer_id, customer_name,
         NTILE(5) OVER (ORDER BY recency_days DESC) AS r_score,
         NTILE(5) OVER (ORDER BY total_orders ASC) AS f_score,
         NTILE(5) OVER (ORDER BY total_spend ASC) AS m_score
  FROM customer_aggregates;
  ```
- **MoM Revenue Growth with `LAG()`:**
  ```sql
  SELECT sales_month, monthly_revenue,
         LAG(monthly_revenue, 1) OVER (ORDER BY sales_month) AS prev_month_revenue,
         ROUND(((monthly_revenue - LAG(monthly_revenue, 1) OVER (ORDER BY sales_month)) 
               / LAG(monthly_revenue, 1) OVER (ORDER BY sales_month)) * 100, 2) AS mom_growth_pct
  FROM monthly_sales;
  ```

---

## 🛠️ Tech Stack & Dependencies

| Layer | Technologies |
| :--- | :--- |
| **Backend** | Python 3.12+, Flask 2.3+, Flask-Login, Werkzeug |
| **Database & ORM** | MySQL 8.0+, SQLite (Zero-Config Fallback), SQLAlchemy 2.0+, PyMySQL |
| **Data Science & ML** | Pandas 2.2+, NumPy, Scikit-Learn 1.3+, Statsmodels 0.14+, SciPy |
| **Visualization & UI** | HTML5, CSS3 (Custom Design System), JavaScript ES6, Chart.js 4.4, Plotly.js |
| **Reporting & Export** | ReportLab 4.0+ (PDF Generator), Power BI-Ready CSV Export |
| **Testing** | Pytest |

---

## ⚙️ Installation & Setup Guide

### 1. Clone Repository & Navigate
```bash
git clone https://github.com/your-username/Enterprise-Sales-Customer-Intelligence.git
cd Enterprise-Sales-Customer-Intelligence
```

### 2. Set Up Virtual Environment (Recommended)
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy the template configuration:
```bash
cp .env.example .env
```
*(Default configuration runs out-of-the-box using local SQLite; to connect to MySQL, set `DATABASE_URL=mysql+pymysql://root:password@localhost:3306/sales_intelligence_db` in `.env`)*.

### 5. Run Database Initialization & Production ETL Pipeline
```bash
python etl/pipeline.py
```
*This command will generate 10,000+ realistic customers and 30,000+ multi-year orders, clean and normalize all records, compute customer RFM scores, and export the Power BI dataset.*

### 6. Train Machine Learning Models
```bash
python -c "from services.churn_model import train_churn_model; from services.forecasting import generate_forecast_models; train_churn_model(); generate_forecast_models()"
```

### 7. Launch Web Application
```bash
python app.py
```
Open your browser and navigate to: **`http://127.0.0.1:5000`**

---

## 🔑 Default Demo User Credentials

| Role | Username | Password | Permissions |
| :--- | :--- | :--- | :--- |
| **Administrator** | `admin` | `Admin@123` | Full access: View all dashboards, User Management, Dataset Upload, ETL triggers |
| **Data Analyst** | `analyst` | `Analyst@123` | View dashboards, Churn prediction, Forecasting, Customer RFM, What-If simulator, Download PDF reports |

---

## 🔌 REST API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/auth/login` | Authenticate user session |
| `GET` | `/api/dashboard` | Executive KPIs, monthly trends, regional breakdown & insights |
| `GET` | `/api/sales` | Sales analytics, growth rates, and rep quota performance |
| `GET` | `/api/customers` | Searchable, paginated customer directory with RFM scores |
| `GET` | `/api/segments` | RFM segment distributions and K-Means clusters |
| `GET` | `/api/products` | 4-quadrant product profitability matrix & SKU data |
| `GET` | `/api/regions` | Regional intelligence and territory growth rates |
| `GET` | `/api/churn/overview` | ML Churn evaluation metrics, ROC-AUC, confusion matrix |
| `GET` | `/api/churn/predict/<id>` | Live single-customer churn risk inference & recommendations |
| `GET` | `/api/forecast` | Time-series forecast for 30, 90, or 180-day horizons |
| `GET/POST` | `/api/what-if` | Dynamic business scenario financial simulation |
| `POST` | `/api/upload` | Upload & validate new CSV dataset |
| `GET` | `/api/reports/download/<type>` | Download generated executive PDF reports |

---

## 🧪 Running Automated Unit Tests
```bash
pytest tests/
```

---

## 📄 Final-Year Academic Documentation
Detailed academic documentation is included in the [`docs/`](file:///c:/Users/mr/Desktop/Enterprise-Sales-Customer-Intelligence/docs/) folder:
- **[Comprehensive Project Report](file:///c:/Users/mr/Desktop/Enterprise-Sales-Customer-Intelligence/docs/PROJECT_REPORT.md)** (Abstract, Problem Statement, Methodology, Algorithms, Mathematical Formulations, Results, Future Scope).
- **[System Architecture & DFD Diagrams](file:///c:/Users/mr/Desktop/Enterprise-Sales-Customer-Intelligence/docs/ARCHITECTURE_DIAGRAMS.md)** (System Architecture, DFD Level 0/1, Relational ER Diagram).

---

## 👨‍💻 Author & Portfolio Details
- **Project:** Enterprise Sales & Customer Intelligence Platform
- **Role Target:** Data Analyst / Business Intelligence Engineer / Junior Data Scientist
- **Submission:** Final-Year Engineering Capstone Project & Data Analytics Portfolio
