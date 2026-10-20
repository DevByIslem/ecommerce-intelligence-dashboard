
import sqlite3
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="E-commerce Intelligence Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =========================================================
# THEME
# =========================================================

BG = "#0B1220"
PANEL = "#172337"
PANEL_ALT = "#111C2E"
BORDER = "#293B52"
TEXT = "#F1F5F9"
MUTED = "#A7B6C9"
TEAL = "#35D0BA"
BLUE = "#60A5FA"
PURPLE = "#A78BFA"
AMBER = "#FBBF24"
RED = "#FB7185"

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "data" / "ecommerce.db"


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown(
    f"""
    <style>
    @import url(
      'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap'
    );

    html, body, [class*="css"] {{
        font-family: 'Inter', sans-serif;
    }}

    .stApp {{
        background: {BG};
        color: {TEXT};
    }}

    [data-testid="stSidebar"] {{
        background: #0E1929;
        border-right: 1px solid {BORDER};
    }}

    [data-testid="stHeader"] {{
        background: rgba(11, 18, 32, 0.92);
    }}

    h1, h2, h3, h4 {{
        color: {TEXT} !important;
        letter-spacing: -0.5px;
    }}

    .hero {{
        padding: 28px 30px;
        border: 1px solid {BORDER};
        border-radius: 18px;
        background:
            radial-gradient(
                circle at top right,
                rgba(53, 208, 186, 0.15),
                transparent 35%
            ),
            linear-gradient(135deg, #172337, #101B2D);
        margin-bottom: 24px;
    }}

    .hero-label {{
        color: {TEAL};
        font-size: 11px;
        font-weight: 800;
        letter-spacing: 2px;
    }}

    .hero-title {{
        font-size: 32px;
        line-height: 1.25;
        font-weight: 800;
        color: {TEXT};
        margin-top: 10px;
    }}

    .hero-subtitle {{
        color: {MUTED};
        font-size: 14px;
        margin-top: 10px;
        line-height: 1.7;
    }}

    .section-label {{
        color: {TEAL};
        font-size: 10px;
        font-weight: 800;
        letter-spacing: 2px;
        margin-top: 12px;
        margin-bottom: 4px;
    }}

    .kpi-card {{
        background: linear-gradient(145deg, {PANEL}, {PANEL_ALT});
        border: 1px solid {BORDER};
        border-radius: 14px;
        padding: 19px;
        min-height: 135px;
    }}

    .kpi-label {{
        color: {MUTED};
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
    }}

    .kpi-value {{
        color: {TEXT};
        font-size: 27px;
        font-weight: 800;
        margin-top: 13px;
        overflow-wrap: anywhere;
    }}

    .kpi-caption {{
        color: {MUTED};
        font-size: 11px;
        margin-top: 7px;
    }}

    .insight-card {{
        background: linear-gradient(135deg, #172337, #132A36);
        border: 1px solid {BORDER};
        border-radius: 12px;
        padding: 18px;
        min-height: 145px;
        margin-bottom: 12px;
    }}

    .insight-label {{
        font-size: 10px;
        font-weight: 800;
        letter-spacing: 1.5px;
    }}

    .insight-value {{
        color: {TEXT};
        font-size: 21px;
        font-weight: 800;
        margin-top: 10px;
        overflow-wrap: anywhere;
    }}

    .insight-description {{
        color: {MUTED};
        font-size: 12px;
        margin-top: 8px;
        line-height: 1.7;
    }}

    div[data-testid="stPlotlyChart"] {{
        border: 1px solid {BORDER};
        border-radius: 14px;
        padding: 8px;
        background: {PANEL_ALT};
    }}

    div[data-testid="stDataFrame"] {{
        border: 1px solid {BORDER};
        border-radius: 12px;
        overflow: hidden;
    }}

    div[data-testid="stDownloadButton"] button {{
        border-radius: 9px;
        border: 1px solid {TEAL};
        color: {TEAL};
        background: transparent;
        font-weight: 700;
    }}

    div[data-testid="stDownloadButton"] button:hover {{
        background: rgba(53, 208, 186, 0.12);
        color: {TEXT};
    }}

    .footer {{
        color: {MUTED};
        font-size: 11px;
        text-align: center;
        padding: 25px 0 10px 0;
        border-top: 1px solid {BORDER};
        margin-top: 35px;
        line-height: 1.8;
    }}

    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# LOAD DATABASE
# =========================================================

@st.cache_data
def load_data(db_path, modified_time):
    del modified_time

    with sqlite3.connect(db_path) as connection:
        data = pd.read_sql_query(
            """
            SELECT
                order_id,
                order_date,
                customer_id,
                product_name,
                category,
                region,
                quantity,
                unit_price,
                discount,
                status,
                revenue
            FROM orders
            WHERE status = 'Delivered'
            """,
            connection,
        )

    if data.empty:
        return data

    data["order_date"] = pd.to_datetime(
        data["order_date"], errors="coerce"
    )

    for column in [
        "quantity",
        "unit_price",
        "discount",
        "revenue",
    ]:
        data[column] = pd.to_numeric(
            data[column], errors="coerce"
        ).fillna(0)

    for column in [
        "product_name",
        "category",
        "region",
    ]:
        data[column] = data[column].fillna("Unknown")

    data = data.dropna(subset=["order_date"]).copy()

    return data


if not DB_PATH.exists():
    st.error(f"Database not found: {DB_PATH}")
    st.info("Check that data/ecommerce.db exists in your project.")
    st.stop()

try:
    df = load_data(
        str(DB_PATH),
        DB_PATH.stat().st_mtime,
    )
except Exception as error:
    st.error(f"Could not load the database: {error}")
    st.stop()

if df.empty:
    st.warning("No delivered orders were found.")
    st.stop()


# =========================================================
# SIDEBAR FILTERS
# =========================================================

st.sidebar.markdown("## 📊 Intelligence")
st.sidebar.caption("E-commerce analytics platform")
st.sidebar.divider()
st.sidebar.markdown("### Filters")

all_regions = sorted(df["region"].unique().tolist())
all_categories = sorted(df["category"].unique().tolist())

selected_regions = st.sidebar.multiselect(
    "Region",
    options=all_regions,
    default=all_regions,
)

selected_categories = st.sidebar.multiselect(
    "Category",
    options=all_categories,
    default=all_categories,
)

min_date = df["order_date"].min().date()
max_date = df["order_date"].max().date()

date_range = st.sidebar.date_input(
    "Order date range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)

if isinstance(date_range, (tuple, list)):
    if len(date_range) >= 2:
        start_date, end_date = date_range[0], date_range[1]
    elif len(date_range) == 1:
        start_date = end_date = date_range[0]
    else:
        start_date, end_date = min_date, max_date
else:
    start_date = end_date = date_range

if start_date > end_date:
    start_date, end_date = end_date, start_date

st.sidebar.divider()
st.sidebar.caption("Source: SQLite database")
st.sidebar.caption("Status: Delivered orders")
st.sidebar.caption("Dataset: Synthetic demonstration data")


# =========================================================
# FILTER DATA
# =========================================================

filtered = df[
    df["region"].isin(selected_regions)
    & df["category"].isin(selected_categories)
    & (df["order_date"].dt.date >= start_date)
    & (df["order_date"].dt.date <= end_date)
].copy()

if filtered.empty:
    st.markdown(
        """
        <div class="hero">
            <div class="hero-label">E-COMMERCE INTELLIGENCE</div>
            <div class="hero-title">No data for this selection</div>
            <div class="hero-subtitle">
                Change the filters in the sidebar.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.stop()


# =========================================================
# KPI CALCULATIONS
# =========================================================

total_revenue = float(filtered["revenue"].sum())
total_orders = len(filtered)
unique_customers = int(filtered["customer_id"].nunique())
total_units = int(filtered["quantity"].sum())

average_order_value = (
    total_revenue / total_orders if total_orders else 0
)

total_quantity = float(filtered["quantity"].sum())

average_discount = (
    float(
        (filtered["discount"] * filtered["quantity"]).sum()
        / total_quantity
    )
    if total_quantity > 0
    else 0
)

current_start = pd.Timestamp(start_date).normalize()
current_end = pd.Timestamp(end_date).normalize()

period_days = (current_end - current_start).days + 1

previous_start = current_start - pd.Timedelta(days=period_days)
previous_end = current_start - pd.Timedelta(days=1)

previous_period = df[
    df["region"].isin(selected_regions)
    & df["category"].isin(selected_categories)
    & (
        df["order_date"].dt.normalize() >= previous_start
    )
    & (
        df["order_date"].dt.normalize() <= previous_end
    )
].copy()

previous_revenue = float(previous_period["revenue"].sum())

if previous_revenue > 0:
    revenue_growth = (
        (total_revenue - previous_revenue)
        / previous_revenue
    ) * 100
    growth_label = f"{revenue_growth:+.1f}%"
else:
    growth_label = "N/A"


# =========================================================
# HERO HEADER
# =========================================================

st.markdown(
    """
    <div class="hero">
        <div class="hero-label">
            BUSINESS INTELLIGENCE · ANALYTICS
        </div>
        <div class="hero-title">
            E-commerce Intelligence Dashboard
        </div>
        <div class="hero-subtitle">
            Transform transactional data into actionable business insights.
            Monitor revenue, understand customer activity, and explore
            product and regional performance.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="section-label">PERFORMANCE OVERVIEW</div>',
    unsafe_allow_html=True,
)
st.subheader("Executive summary")

st.caption(
    f"Period: {start_date} — {end_date} · "
    f"{len(selected_regions)} region(s) · "
    f"{len(selected_categories)} categor(ies)"
)


# =========================================================
# MAIN KPI CARDS
# =========================================================

kpi1, kpi2, kpi3, kpi4 = st.columns(4)

kpis = [
    (
        kpi1,
        "Total revenue",
        f"{total_revenue:,.2f}",
        "Delivered orders · simulated units",
    ),
    (
        kpi2,
        "Delivered orders",
        f"{total_orders:,}",
        "Orders matching current filters",
    ),
    (
        kpi3,
        "Unique customers",
        f"{unique_customers:,}",
        "Distinct customer IDs",
    ),
    (
        kpi4,
        "Average order value",
        f"{average_order_value:,.2f}",
        "Revenue divided by order count",
    ),
]

for column, label, value, caption in kpis:
    with column:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-label">{label}</div>
                <div class="kpi-value">{value}</div>
                <div class="kpi-caption">{caption}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# =========================================================
# ADVANCED KPIS
# =========================================================

st.markdown("")
advanced1, advanced2, advanced3 = st.columns(3)

with advanced1:
    st.metric("Units sold", f"{total_units:,}")

with advanced2:
    st.metric(
        "Weighted average discount",
        f"{average_discount * 100:.1f}%",
    )

with advanced3:
    st.metric(
        "Revenue growth vs previous period",
        growth_label,
        help=(
            "Compares the selected period with the immediately "
            "preceding period of equal duration, keeping the "
            "region and category filters."
        ),
    )


# =========================================================
# CHART STYLE
# =========================================================

chart_layout = dict(
    paper_bgcolor=PANEL_ALT,
    plot_bgcolor=PANEL_ALT,
    font=dict(family="Inter, sans-serif", color=TEXT, size=11),
    margin=dict(l=20, r=20, t=35, b=20),
    legend=dict(
        bgcolor="rgba(0,0,0,0)",
        font=dict(color=MUTED),
    ),
    xaxis=dict(
        showgrid=False,
        zeroline=False,
        linecolor=BORDER,
        tickfont=dict(color=MUTED),
    ),
    yaxis=dict(
        gridcolor=BORDER,
        zeroline=False,
        linecolor=BORDER,
        tickfont=dict(color=MUTED),
    ),
)


# =========================================================
# MONTHLY REVENUE TREND
# =========================================================

st.markdown("")
st.markdown(
    '<div class="section-label">REVENUE ANALYTICS</div>',
    unsafe_allow_html=True,
)
st.subheader("Revenue performance")

monthly = (
    filtered.assign(
        month=filtered["order_date"]
        .dt.to_period("M")
        .dt.to_timestamp()
    )
    .groupby("month", as_index=False)
    .agg(
        revenue=("revenue", "sum"),
        orders=("order_id", "nunique"),
    )
    .sort_values("month")
)

fig_monthly = px.line(
    monthly,
    x="month",
    y="revenue",
    markers=True,
    custom_data=["orders"],
)

fig_monthly.update_traces(
    line=dict(color=TEAL, width=3),
    marker=dict(size=7, color=TEAL),
    fill="tozeroy",
    fillcolor="rgba(53, 208, 186, 0.08)",
    hovertemplate=(
        "<b>%{x|%B %Y}</b><br>"
        "Revenue: %{y:,.2f}<br>"
        "Orders: %{customdata[0]:,.0f}"
        "<extra></extra>"
    ),
)

fig_monthly.update_layout(
    **chart_layout,
    height=360,
    xaxis_title="Month",
    yaxis_title="Revenue",
)

st.plotly_chart(
    fig_monthly,
    use_container_width=True,
    config={"displayModeBar": False},
)


# =========================================================
# CATEGORY AND REGION CHARTS
# =========================================================

chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.subheader("Revenue by category")

    category_revenue = (
        filtered.groupby("category", as_index=False)
        .agg(revenue=("revenue", "sum"))
        .sort_values("revenue", ascending=True)
    )

    fig_category = px.bar(
        category_revenue,
        x="revenue",
        y="category",
        orientation="h",
        text="revenue",
    )

    fig_category.update_traces(
        marker_color=TEAL,
        texttemplate="%{x:,.0f}",
        textposition="outside",
        cliponaxis=False,
        hovertemplate=(
            "<b>%{y}</b><br>Revenue: %{x:,.2f}<extra></extra>"
        ),
    )

    fig_category.update_layout(
        **chart_layout,
        height=350,
        xaxis_title="Revenue",
        yaxis_title="",
    )

    st.plotly_chart(
        fig_category,
        use_container_width=True,
        config={"displayModeBar": False},
    )

with chart_col2:
    st.subheader("Revenue by region")

    region_revenue = (
        filtered.groupby("region", as_index=False)
        .agg(revenue=("revenue", "sum"))
        .sort_values("revenue", ascending=True)
    )

    fig_region = px.bar(
        region_revenue,
        x="revenue",
        y="region",
        orientation="h",
        text="revenue",
    )

    fig_region.update_traces(
        marker_color=BLUE,
        texttemplate="%{x:,.0f}",
        textposition="outside",
        cliponaxis=False,
        hovertemplate=(
            "<b>%{y}</b><br>Revenue: %{x:,.2f}<extra></extra>"
        ),
    )

    fig_region.update_layout(
        **chart_layout,
        height=350,
        xaxis_title="Revenue",
        yaxis_title="",
    )

    st.plotly_chart(
        fig_region,
        use_container_width=True,
        config={"displayModeBar": False},
    )


# =========================================================
# AUTOMATED BUSINESS INSIGHTS
# =========================================================

st.markdown("")
st.markdown(
    '<div class="section-label">INTELLIGENCE & DISCOVERY</div>',
    unsafe_allow_html=True,
)
st.subheader("Automated business insights")
st.caption(
    "Insights are calculated from the current selection. "
    "The dataset is simulated for portfolio demonstration."
)

category_insights = (
    filtered.groupby("category", as_index=False)
    .agg(revenue=("revenue", "sum"))
    .sort_values("revenue", ascending=False)
)

region_insights = (
    filtered.groupby("region", as_index=False)
    .agg(revenue=("revenue", "sum"))
    .sort_values("revenue", ascending=False)
)

monthly_insights = (
    filtered.assign(
        month=filtered["order_date"]
        .dt.to_period("M")
        .dt.to_timestamp()
    )
    .groupby("month", as_index=False)
    .agg(revenue=("revenue", "sum"))
    .sort_values("month")
)

insight1, insight2 = st.columns(2)

with insight1:
    best_category = category_insights.iloc[0]
    category_share = (
        best_category["revenue"] / total_revenue * 100
        if total_revenue > 0 else 0
    )

    st.markdown(
        f"""
        <div class="insight-card" style="border-left:4px solid {TEAL};">
            <div class="insight-label" style="color:{TEAL};">
                TOP CATEGORY
            </div>
            <div class="insight-value">
                {best_category["category"]}
            </div>
            <div class="insight-description">
                Revenue: {best_category["revenue"]:,.2f}<br>
                Represents {category_share:.1f}% of filtered revenue.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    best_region = region_insights.iloc[0]
    region_share = (
        best_region["revenue"] / total_revenue * 100
        if total_revenue > 0 else 0
    )

    st.markdown(
        f"""
        <div class="insight-card" style="border-left:4px solid {BLUE};">
            <div class="insight-label" style="color:{BLUE};">
                TOP REGION
            </div>
            <div class="insight-value">
                {best_region["region"]}
            </div>
            <div class="insight-description">
                Revenue: {best_region["revenue"]:,.2f}<br>
                Represents {region_share:.1f}% of filtered revenue.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with insight2:
    best_month = monthly_insights.loc[
        monthly_insights["revenue"].idxmax()
    ]

    st.markdown(
        f"""
        <div class="insight-card" style="border-left:4px solid {PURPLE};">
            <div class="insight-label" style="color:{PURPLE};">
                BEST REVENUE MONTH
            </div>
            <div class="insight-value">
                {best_month["month"].strftime("%B %Y")}
            </div>
            <div class="insight-description">
                Highest monthly revenue:
                {best_month["revenue"]:,.2f}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if len(monthly_insights) >= 2:
        last_month = monthly_insights.iloc[-1]
        previous_month = monthly_insights.iloc[-2]

        if previous_month["revenue"] > 0:
            monthly_change = (
                (
                    last_month["revenue"]
                    - previous_month["revenue"]
                )
                / previous_month["revenue"]
            ) * 100

            if monthly_change < 0:
                alert_color = RED
                alert_title = "REVENUE DECLINE"
                alert_message = (
                    f"Revenue decreased by {abs(monthly_change):.1f}% "
                    f"from {previous_month['month'].strftime('%B %Y')} "
                    f"to {last_month['month'].strftime('%B %Y')}."
                )
            elif monthly_change > 0:
                alert_color = TEAL
                alert_title = "REVENUE INCREASE"
                alert_message = (
                    f"Revenue increased by {monthly_change:.1f}% "
                    f"from {previous_month['month'].strftime('%B %Y')} "
                    f"to {last_month['month'].strftime('%B %Y')}."
                )
            else:
                alert_color = AMBER
                alert_title = "REVENUE STABLE"
                alert_message = (
                    "Revenue was unchanged between the last two months."
                )
        else:
            alert_color = AMBER
            alert_title = "MONTHLY COMPARISON"
            alert_message = (
                "The previous month had zero revenue, so percentage "
                "change cannot be calculated."
            )
    else:
        alert_color = AMBER
        alert_title = "NOT ENOUGH MONTHS"
        alert_message = (
            "At least two months with orders are needed for comparison."
        )

    st.markdown(
        f"""
        <div class="insight-card" style="border-left:4px solid {alert_color};">
            <div class="insight-label" style="color:{alert_color};">
                {alert_title}
            </div>
            <div class="insight-value">
                Monthly revenue analysis
            </div>
            <div class="insight-description">
                {alert_message}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# TOP PRODUCTS
# =========================================================

st.markdown("")
st.markdown(
    '<div class="section-label">PRODUCT INTELLIGENCE</div>',
    unsafe_allow_html=True,
)
st.subheader("Top-performing products")

top_products = (
    filtered.groupby("product_name", as_index=False)
    .agg(
        revenue=("revenue", "sum"),
        units_sold=("quantity", "sum"),
        orders=("order_id", "nunique"),
    )
    .sort_values("revenue", ascending=False)
    .head(10)
    .reset_index(drop=True)
)

top_products.index = top_products.index + 1
top_products.index.name = "Rank"

st.dataframe(
    top_products.style.format(
        {
            "revenue": "{:,.2f}",
            "units_sold": "{:,.0f}",
            "orders": "{:,.0f}",
        }
    ),
    use_container_width=True,
)


# =========================================================
# ORDER DETAILS
# =========================================================

st.markdown("")
st.markdown(
    '<div class="section-label">DATA EXPLORATION</div>',
    unsafe_allow_html=True,
)
st.subheader("Delivered order details")

with st.expander("Explore filtered transactions"):
    display_columns = [
        column
        for column in [
            "order_id",
            "order_date",
            "customer_id",
            "product_name",
            "category",
            "region",
            "quantity",
            "unit_price",
            "discount",
            "revenue",
            "status",
        ]
        if column in filtered.columns
    ]

    display_df = filtered[display_columns].copy()
    display_df["order_date"] = (
        display_df["order_date"].dt.strftime("%Y-%m-%d")
    )

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
    )

st.download_button(
    label="⬇ Export filtered data to CSV",
    data=filtered.to_csv(index=False).encode("utf-8"),
    file_name="ecommerce_filtered_data.csv",
    mime="text/csv",
)


# =========================================================
# FOOTER
# =========================================================

st.markdown(
    """
    <div class="footer">
        E-commerce Intelligence Dashboard · Python · SQLite ·
        Pandas · Plotly · Streamlit<br>
        Portfolio project · Synthetic data for demonstration purposes
    </div>
    """,
    unsafe_allow_html=True,
)
