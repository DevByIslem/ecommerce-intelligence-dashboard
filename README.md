
# E-commerce Intelligence Dashboard

An interactive Business Intelligence dashboard built with Python, SQL, SQLite, Pandas, Plotly, and Streamlit.

This project transforms e-commerce transaction data into actionable insights through interactive visualizations, performance indicators, and automated business analysis.

> **Note:** This portfolio project uses synthetic data for demonstration purposes. It does not represent real business transactions.

## Overview

The E-commerce Intelligence Dashboard provides an interactive view of sales performance across products, categories, regions, and time periods.

Users can filter the dataset, monitor key performance indicators, compare revenue trends, identify top-performing products, and export filtered data for further analysis.

## Key Features

### Executive KPI Dashboard
- Total revenue
- Number of delivered orders
- Unique customers
- Average order value
- Units sold
- Weighted average discount
- Revenue growth compared with the previous period

### Interactive Data Visualizations
- Monthly revenue trends
- Revenue by product category
- Revenue by region
- Interactive charts with hover details

### Automated Business Insights
- Highest-revenue category
- Best-performing region
- Month with the highest revenue
- Month-over-month revenue change and alerts

### Product and Transaction Analysis
- Top 10 products ranked by revenue
- Detailed view of filtered transactions
- Filters for date range, region, and category
- CSV export of filtered data

### User Interface
- Modern dark BI interface
- Responsive dashboard layout
- Interactive filters
- Consistent visual design

## Tech Stack

| Technology | Purpose |
|---|---|
| Python | Data processing and application logic |
| SQL | Querying transactional data |
| SQLite | Relational database |
| Pandas | Data cleaning and aggregation |
| Plotly | Interactive data visualizations |
| Streamlit | Interactive dashboard interface |

## Project Structure

```text
ecommerce-intelligence-dashboard/
├── .streamlit/
│   └── config.toml
├── app.py
├── requirements.txt
├── README.md
├── data/
│   └── ecommerce.db
└── src/
    └── generate_data.py
```

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/DevByIslem/ecommerce-intelligence-dashboard.git
cd ecommerce-intelligence-dashboard
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Linux or macOS:

```bash
source .venv/bin/activate
```

Activate it on Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the dashboard

```bash
streamlit run app.py
```

Open the local URL displayed in the terminal.

## Data

The dashboard reads delivered orders from a SQLite database located at:

```text
data/ecommerce.db
```

The application expects an `orders` table containing fields such as order date, customer ID, product name, category, region, quantity, unit price, discount, status, and revenue.

If the database is not included in a fresh clone, generate it using the project's data-generation script:

```bash
python src/generate_data.py
```

**Warning:** Run the data-generation script only when you intentionally want to create or regenerate the synthetic database. It may replace the existing demo data.

## Key Analytical Metrics

- **Total Revenue:** Sum of revenue from delivered orders.
- **Average Order Value:** Total revenue divided by the number of delivered orders.
- **Unique Customers:** Number of distinct customer IDs.
- **Weighted Average Discount:** Average discount weighted by quantity.
- **Revenue Growth:** Percentage change compared with the immediately preceding period of equal duration.
- **Category and Regional Performance:** Revenue contribution by category and region.

## Business Value

This project demonstrates practical skills in:

- SQL-based data retrieval
- Data cleaning and transformation
- KPI definition and calculation
- Exploratory data analysis
- Interactive data visualization
- Business performance monitoring
- Automated insight generation
- Dashboard development and data export

## Future Improvements

- Add customer segmentation and retention analysis.
- Introduce sales forecasting.
- Add automated data-quality checks.
- Deploy the dashboard online.
- Add automated testing and continuous integration.

## Author

**Islem Naimi**

Data Analyst | Business Intelligence | Python | SQL | Power BI

GitHub: [DevByIslem](https://github.com/DevByIslem)

---

*Built as a data analytics and business intelligence portfolio project.*
