# System Architecture & Diagrams Specification

## 1. High-Level System Architecture Diagram

```mermaid
graph TB
    subgraph Client Layer
        UI[Interactive SaaS Web UI: HTML5 / CSS3 / JavaScript / Chart.js / Plotly]
        PDF[ReportLab Automated PDF Reports]
        PBI[Power BI Desktop / Power BI Service Integration]
    end

    subgraph Application & Service Layer
        Flask[Flask REST API Server & Application Factory]
        Auth[RBAC Security: Admin & Analyst Roles]
        ETL[Automated ETL & Data Cleaning Service]
        Insights[Dynamic Business Intelligence & Anomaly Engine]
        WhatIf[What-If Business Scenario Simulator Engine]
    end

    subgraph Machine Learning & Analytics Layer
        RFM[RFM Segmentation & K-Means Clustering]
        Churn[Supervised Churn Model: Random Forest / Gradient Boosting]
        Forecast[Time-Series Demand Forecasting: Holt-Winters Additive]
    end

    subgraph Database Layer
        ORM[SQLAlchemy 2.0 ORM & Query Optimizer]
        DB[(Relational Database: MySQL & SQLite Fallback)]
        CleanCSV[data/processed/powerbi_sales_intelligence.csv]
    end

    UI <-->|HTTP REST / JSON| Flask
    Flask --> Auth
    Flask --> Insights
    Flask --> WhatIf
    Flask --> RFM
    Flask --> Churn
    Flask --> Forecast
    Flask --> PDF
    ETL --> CleanCSV
    ETL --> ORM
    RFM --> ORM
    Churn --> ORM
    Forecast --> ORM
    ORM <--> DB
    CleanCSV -.->|Ingestion| PBI
```

---

## 2. Entity-Relationship (ER) Relational Schema Diagram

```mermaid
erDiagram
    USERS {
        int user_id PK
        string username UK
        string email UK
        string password_hash
        string full_name
        string role
        boolean is_active
        timestamp created_at
    }

    REGIONS {
        int region_id PK
        string region_name UK
        string country
        string market_tier
        decimal target_growth_rate
    }

    SALES_REPS {
        int rep_id PK
        string rep_code UK
        string rep_name
        string email UK
        int region_id FK
        decimal quota_annual
        date hire_date
    }

    CATEGORIES {
        int category_id PK
        string category_name UK
        text description
        decimal target_margin
    }

    PRODUCTS {
        int product_id PK
        string product_sku UK
        string product_name
        int category_id FK
        decimal unit_cost
        decimal unit_price
        int stock_quantity
    }

    CUSTOMERS {
        int customer_id PK
        string customer_code UK
        string customer_name
        string email
        string company_name
        string segment
        int region_id FK
        date signup_date
        int total_orders_count
        decimal total_spend
        decimal average_order_value
        int recency_days
        int rfm_score
        decimal churn_risk_score
        string churn_risk_level
    }

    ORDERS {
        int order_id PK
        string order_number UK
        int customer_id FK
        int rep_id FK
        int region_id FK
        date order_date
        string status
        decimal subtotal_amount
        decimal discount_amount
        decimal total_amount
        decimal total_cost
        decimal net_profit
        decimal profit_margin_pct
    }

    ORDER_ITEMS {
        int item_id PK
        int order_id FK
        int product_id FK
        int quantity
        decimal unit_price
        decimal unit_cost
        decimal discount_pct
        decimal item_total_amount
        decimal item_profit
        decimal item_margin_pct
    }

    PREDICTIONS {
        int prediction_id PK
        int customer_id FK
        string model_name
        decimal churn_probability
        string predicted_risk_level
        json key_drivers
        text recommended_action
    }

    REGIONS ||--o{ SALES_REPS : "employs"
    REGIONS ||--o{ CUSTOMERS : "locates"
    REGIONS ||--o{ ORDERS : "fulfills"
    CATEGORIES ||--o{ PRODUCTS : "contains"
    CUSTOMERS ||--o{ ORDERS : "places"
    SALES_REPS ||--o{ ORDERS : "manages"
    ORDERS ||--|{ ORDER_ITEMS : "contains"
    PRODUCTS ||--o{ ORDER_ITEMS : "ordered_in"
    CUSTOMERS ||--o{ PREDICTIONS : "scored_in"
```

---

## 3. Data Flow Diagram (DFD Level 1)

```mermaid
graph LR
    Source[CSV / Transaction Upload] -->|Raw Records| Cleaner[Data Cleaner Module]
    Cleaner -->|Validation & Deduplication| Staging[Cleaned DataFrame]
    Staging -->|Bulk Insert| DB[(Relational DB)]
    DB --> Aggs[RFM & Metrics Aggregator]
    Aggs --> ML[Churn & Forecast Models]
    ML --> Cache[Model Cache & DB Predictions]
    Cache --> API[Flask REST APIs]
    API --> Client[Interactive Web Dashboard]
```
