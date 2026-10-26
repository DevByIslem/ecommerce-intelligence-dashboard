
from pathlib import Path
import sqlite3

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


# =========================================================
# 1. PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="NOVA | E-Commerce Analytics",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded",
)

DB_PATH = Path("data/ecommerce.db")

BG = "#0B1120"
PANEL = "#111B2E"
ACCENT = "#2DD4BF"
BLUE = "#60A5FA"
PURPLE = "#A78BFA"
TEXT = "#F1F5F9"
MUTED = "#94A3B8"
BORDER = "#26364D"


# =========================================================
# 2. CUSTOM DESIGN
# =========================================================

st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {{
        font-family: Inter, sans-serif;
    }}

    .stApp {{
        background: {BG};
        color: {TEXT};
    }}

    [data-testid="stSidebar"] {{
        background: #0D1728;
        border-right: 1px solid {BORDER};
    }}

    [data-testid="stSidebar"] * {{
        color: {TEXT};
    }}

    .nova-hero {{
        background: linear-gradient(120deg, #14263D, #123A42);
        border: 1px solid #25465A;
        border-radius: 20px;
        padding: 30px;
        margin-bottom: 22px;
    }}

    .nova-label {{
        color: {ACCENT};
        font-size: 12px;
        font-weight: 800;
        letter-spacing: 3px;
    }}

    .nova-title {{
        color: {TEXT};
        font-size: 34px;
        font-weight: 800;
        margin: 12px 0 8px;
    }}

    .nova-subtitle {{
        color: #B8C7D9;
        font-size: 14px;
    }}

    .metric-card {{
        background: {PANEL};
        border: 1px solid {BORDER};
        border-radius: 16px;
        padding: 19px;
        min-height: 125px;
    }}

    .metric-label {{
        color: {MUTED};
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 1px;
        text-transform: uppercase;
    }}

    .metric-value {{
        color: {TEXT};
        font-size: 27px;
        font-weight: 800;
        margin-top: 12px;
        overflow-wrap: anywhere;
    }}

    .metric-note {{
        color: {ACCENT};
        font-size: 12px;
        margin-top: 7px;
    }}

    .section-caption {{
        color: {MUTED};
        font-size: 13px;
        margin-top: -8px;
        margin-bottom: 15px;
    }}

    div[data-testid="stPlotlyChart"] {{
        background: {PANEL};
        border: 1px solid {BORDER};
        border-radius: 15px;
        padding: 8px;
    }}

    div[data-testid="stDataFrame"] {{
        border: 1px solid {BORDER};
        border-radius: 12px;
    }}

    div.stButton > button,
    div.stDownloadButton > button {{
        border-radius: 9px;
    }}

    h1, h2, h3 {{
        color: {TEXT};
    }}

    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# 3. DATA LOADING
# =========================================================

@st.cache_data
def load_data(db_path):
    if not Path(db_path).exists():
        return None, f"Database not found: {db_path}"

    try:
        with sqlite3.connect(db_path) as connection:
            tables = pd.read_sql_query(
                "SELECT name FROM sqlite_master WHERE type='table'",
                connection,
            )

            if "orders" not in tables["name"].tolist():
                available = ", ".join(tables["name"].tolist())
                return None, (
                    "The table 'orders' was not found. "
                    f"Available tables: {available or 'none'}"
                )

            data = pd.read_sql_query(
                'SELECT * FROM "orders"',
                connection,
            )

        if data.empty:
            return None, "The orders table is empty."

        return data, None

    except Exception as error:
        return None, f"Unable to load database: {error}"


df, load_error = load_data(str(DB_PATH))


# =========================================================
# 4. HEADER
# =========================================================

st.markdown(
    """
    <div class="nova-hero">
        <div class="nova-label">✦ NOVA ANALYTICS PLATFORM</div>
        <div class="nova-title">NOVA | E-Commerce Analytics</div>
        <div class="nova-subtitle">
            Business intelligence for sales, products, customers and markets
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


if load_error:
    st.error(load_error)
    st.info(
        "Check the database path and table structure. "
        "If your project uses a CSV file instead of SQLite, "
        "the data-loading section must be adapted."
    )
    st.stop()


# =========================================================
# 5. DATA PREPARATION
# =========================================================

df.columns = [str(col).strip().lower() for col in df.columns]

required = [
    "order_id",
    "order_date",
    "customer_id",
    "unit_price",
]

missing = [col for col in required if col not in df.columns]

if missing:
    st.error("Missing required columns: " + ", ".join(missing))
    st.write("Available columns:", df.columns.tolist())
    st.stop()

df["order_date"] = pd.to_datetime(
    df["order_date"], errors="coerce"
)

df["unit_price"] = pd.to_numeric(
    df["unit_price"], errors="coerce"
)

df = df.dropna(
    subset=["order_date", "unit_price", "order_id"]
).copy()

if df.empty:
    st.error("No valid order records are available.")
    st.stop()

if "quantity" not in df.columns:
    df["quantity"] = 1

df["quantity"] = pd.to_numeric(
    df["quantity"], errors="coerce"
).fillna(0)

if "revenue" in df.columns:
    df["revenue"] = pd.to_numeric(
        df["revenue"], errors="coerce"
    )
    df["revenue"] = df["revenue"].fillna(
        df["quantity"] * df["unit_price"]
    )
else:
    df["revenue"] = df["quantity"] * df["unit_price"]

defaults = {
    "category": "Unclassified",
    "region": "Unknown",
    "product_name": "Unknown product",
    "status": "Unknown",
}

for column, default in defaults.items():
    if column not in df.columns:
        df[column] = default
    else:
        df[column] = df[column].fillna(default).astype(str)

if df["customer_id"].isna().all():
    st.warning("Customer IDs are missing; customer metrics may be incomplete.")

df["month"] = df["order_date"].dt.to_period("M").astype(str)
df["year"] = df["order_date"].dt.year


# =========================================================
# 6. SIDEBAR FILTERS
# =========================================================

st.sidebar.markdown("## ✦ NOVA")
st.sidebar.caption("E-Commerce Analytics")
st.sidebar.divider()

min_date = df["order_date"].min().date()
max_date = df["order_date"].max().date()

date_range = st.sidebar.date_input(
    "Date range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)

if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date, end_date = min_date, max_date

filtered = df[
    df["order_date"].dt.date.between(start_date, end_date)
].copy()


def multiselect_filter(frame, column, label):
    options = sorted(frame[column].dropna().astype(str).unique())
    return st.sidebar.multiselect(
        label,
        options,
        default=options,
    )


selected_categories = multiselect_filter(
    filtered, "category", "Product category"
)

selected_regions = multiselect_filter(
    filtered, "region", "Region"
)

selected_statuses = multiselect_filter(
    filtered, "status", "Order status"
)

filtered = filtered[
    filtered["category"].astype(str).isin(selected_categories)
    & filtered["region"].astype(str).isin(selected_regions)
    & filtered["status"].astype(str).isin(selected_statuses)
].copy()

st.sidebar.divider()
st.sidebar.caption("Interactive analytics dashboard")


# =========================================================
# 7. HELPER FUNCTIONS
# =========================================================

def money(value):
    return f"{value:,.2f}"


def metric_card(label, value, note):
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-note">{note}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def style_chart(fig, height=360):
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor=PANEL,
        plot_bgcolor=PANEL,
        font=dict(
            family="Inter, sans-serif",
            color=TEXT,
        ),
        title_font_size=17,
        height=height,
        margin=dict(l=20, r=20, t=55, b=25),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
        ),
        xaxis=dict(
            showgrid=False,
            zeroline=False,
        ),
        yaxis=dict(
            gridcolor=BORDER,
            zeroline=False,
        ),
    )
    return fig


# =========================================================
# 8. KEY PERFORMANCE INDICATORS
# =========================================================

revenue = filtered["revenue"].sum()
orders_count = filtered["order_id"].nunique()
customers_count = filtered["customer_id"].nunique()
units_sold = filtered["quantity"].sum()

average_order_value = (
    revenue / orders_count if orders_count else 0
)

k1, k2, k3, k4 = st.columns(4)

with k1:
    metric_card(
        "Total Revenue",
        money(revenue),
        "Revenue in dataset currency",
    )

with k2:
    metric_card(
        "Total Orders",
        f"{orders_count:,}",
        "Unique orders",
    )

with k3:
    metric_card(
        "Unique Customers",
        f"{customers_count:,}",
        "Distinct customer IDs",
    )

with k4:
    metric_card(
        "Average Order Value",
        money(average_order_value),
        f"{units_sold:,.0f} units sold",
    )

st.write("")


# =========================================================
# 9. SALES PERFORMANCE
# =========================================================

st.markdown("## Sales Performance")
st.markdown(
    '<div class="section-caption">'
    'Monitor revenue trends and category contributions.'
    '</div>',
    unsafe_allow_html=True,
)

left, right = st.columns([1.6, 1])

with left:
    monthly = (
        filtered.groupby("month", as_index=False)
        .agg(revenue=("revenue", "sum"))
        .sort_values("month")
    )

    fig = px.line(
        monthly,
        x="month",
        y="revenue",
        markers=True,
        title="Monthly Revenue Trend",
        labels={
            "month": "Month",
            "revenue": "Revenue",
        },
    )

    fig.update_traces(
        line=dict(color=ACCENT, width=3),
        marker=dict(size=7),
        fill="tozeroy",
        fillcolor="rgba(45,212,191,0.08)",
    )

    st.plotly_chart(
        style_chart(fig),
        use_container_width=True,
    )

with right:
    category_data = (
        filtered.groupby("category", as_index=False)
        .agg(revenue=("revenue", "sum"))
        .sort_values("revenue", ascending=False)
    )

    fig = px.pie(
        category_data,
        names="category",
        values="revenue",
        hole=0.65,
        title="Revenue by Category",
        color_discrete_sequence=[
            ACCENT, BLUE, PURPLE, "#F59E0B",
            "#F472B6", "#34D399",
        ],
    )

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor=PANEL,
        font=dict(color=TEXT),
        height=360,
        margin=dict(l=15, r=15, t=55, b=25),
        legend=dict(orientation="h", y=-0.15),
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )


# =========================================================
# 10. REGIONAL ANALYSIS
# =========================================================

st.markdown("## Regional Performance")

region_data = (
    filtered.groupby("region", as_index=False)
    .agg(
        revenue=("revenue", "sum"),
        orders=("order_id", "nunique"),
    )
    .sort_values("revenue", ascending=False)
)

if not region_data.empty:
    fig = px.bar(
        region_data,
        x="region",
        y="revenue",
        title="Revenue by Region",
        color="revenue",
        labels={
            "region": "Region",
            "revenue": "Revenue",
        },
        color_continuous_scale=["#164E63", ACCENT],
        hover_data=["orders"],
    )

    fig.update_layout(coloraxis_showscale=False)

    st.plotly_chart(
        style_chart(fig),
        use_container_width=True,
    )
else:
    st.info("No regional data for the selected filters.")


# =========================================================
# 11. PRODUCT INSIGHTS
# =========================================================

st.markdown("## Product Insights")

product_data = (
    filtered.groupby("product_name", as_index=False)
    .agg(
        revenue=("revenue", "sum"),
        quantity=("quantity", "sum"),
        orders=("order_id", "nunique"),
    )
    .sort_values("revenue", ascending=False)
)

if not product_data.empty:
    top_products = product_data.head(10).sort_values("revenue")

    fig = px.bar(
        top_products,
        x="revenue",
        y="product_name",
        orientation="h",
        title="Top 10 Products by Revenue",
        color="revenue",
        labels={
            "revenue": "Revenue",
            "product_name": "Product",
        },
        color_continuous_scale=["#164E63", ACCENT],
        hover_data=["quantity", "orders"],
    )

    fig.update_layout(coloraxis_showscale=False)

    st.plotly_chart(
        style_chart(fig, height=430),
        use_container_width=True,
    )

    st.markdown("### Best-selling products")

    st.dataframe(
        product_data.sort_values(
            "quantity", ascending=False
        ).head(10),
        use_container_width=True,
        hide_index=True,
    )


# =========================================================
# 12. CUSTOMER ANALYSIS
# =========================================================

st.markdown("## Customer Insights")

customer_data = (
    filtered.groupby("customer_id", as_index=False)
    .agg(
        revenue=("revenue", "sum"),
        orders=("order_id", "nunique"),
        units=("quantity", "sum"),
    )
    .sort_values("revenue", ascending=False)
)

c1, c2 = st.columns(2)

with c1:
    st.markdown("### Top customers by revenue")
    st.dataframe(
        customer_data.head(10),
        use_container_width=True,
        hide_index=True,
    )

with c2:
    if not customer_data.empty:
        fig = px.histogram(
            customer_data,
            x="revenue",
            nbins=20,
            title="Customer Revenue Distribution",
            labels={"revenue": "Revenue per customer"},
            color_discrete_sequence=[ACCENT],
        )

        st.plotly_chart(
            style_chart(fig),
            use_container_width=True,
        )
    else:
        st.info("No customer data available.")


# =========================================================
# 13. ORDER STATUS ANALYSIS
# =========================================================

st.markdown("## Order Status Overview")

status_data = (
    filtered.groupby("status", as_index=False)
    .agg(orders=("order_id", "nunique"))
    .sort_values("orders", ascending=False)
)

if not status_data.empty:
    fig = px.bar(
        status_data,
        x="status",
        y="orders",
        title="Orders by Status",
        color="status",
        labels={
            "status": "Order status",
            "orders": "Number of orders",
        },
        color_discrete_sequence=[
            ACCENT, BLUE, PURPLE, "#F59E0B",
        ],
    )

    fig.update_layout(showlegend=False)

    st.plotly_chart(
        style_chart(fig),
        use_container_width=True,
    )


# =========================================================
# 14. DETAILED DATA & EXPORT
# =========================================================

st.markdown("## Data Explorer")
st.caption(
    "Review filtered records and export the results for further analysis."
)

with st.expander("Open detailed order data"):
    st.write(f"Records displayed: {len(filtered):,}")

    st.dataframe(
        filtered,
        use_container_width=True,
        hide_index=True,
    )

    csv_data = filtered.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="Download filtered data (CSV)",
        data=csv_data,
        file_name="nova_ecommerce_analytics.csv",
        mime="text/csv",
    )


# =========================================================
# 15. FOOTER
# =========================================================

st.markdown(
    f"""
    <div style="
        text-align:center;
        padding:26px 0 12px;
        color:{MUTED};
        font-size:12px;
        border-top:1px solid {BORDER};
        margin-top:32px;
    ">
        <strong style="color:{ACCENT}">
            NOVA | E-Commerce Analytics
        </strong>
        <br><br>
        Interactive Business Intelligence · Sales · Customers · Products
    </div>
    """,
    unsafe_allow_html=True,
)
