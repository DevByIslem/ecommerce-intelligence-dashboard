
from pathlib import Path
import sqlite3

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


# =========================================================
# 1. PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="NOVA | E-Commerce Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =========================================================
# 2. THEME
# =========================================================

BG = "#0B1120"
PANEL = "#111827"
PANEL_LIGHT = "#182235"
ACCENT = "#2DD4BF"
ACCENT_BLUE = "#60A5FA"
TEXT = "#F1F5F9"
MUTED = "#94A3B8"
BORDER = "#263449"
GREEN = "#34D399"
ORANGE = "#FBBF24"
RED = "#FB7185"

st.markdown(
    f"""
    <style>
    .stApp {{
        background: {BG};
        color: {TEXT};
    }}

    [data-testid="stSidebar"] {{
        background: #0D1627;
        border-right: 1px solid {BORDER};
    }}

    [data-testid="stSidebar"] * {{
        color: {TEXT};
    }}

    .block-container {{
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        max-width: 1600px;
    }}

    h1, h2, h3 {{
        color: {TEXT} !important;
    }}

    p, label {{
        color: {MUTED};
    }}

    div[data-testid="stMetric"] {{
        background: {PANEL};
        border: 1px solid {BORDER};
        border-radius: 14px;
        padding: 18px;
    }}

    div[data-testid="stMetricLabel"] {{
        color: {MUTED};
    }}

    div[data-testid="stMetricValue"] {{
        color: {TEXT};
    }}

    .nova-card {{
        background: {PANEL};
        border: 1px solid {BORDER};
        border-radius: 14px;
        padding: 20px;
        margin-bottom: 12px;
    }}

    .nova-label {{
        color: {MUTED};
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 1.5px;
        text-transform: uppercase;
    }}

    .nova-value {{
        color: {TEXT};
        font-size: 26px;
        font-weight: 800;
        margin-top: 8px;
    }}

    .nova-caption {{
        color: {MUTED};
        font-size: 12px;
        margin-top: 6px;
    }}

    .nova-header {{
        background: linear-gradient(120deg, #111827, #15253A);
        border: 1px solid {BORDER};
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 22px;
    }}

    .nova-brand {{
        color: {ACCENT};
        font-size: 12px;
        font-weight: 800;
        letter-spacing: 3px;
    }}

    .nova-title {{
        color: {TEXT};
        font-size: 30px;
        font-weight: 800;
        margin-top: 8px;
    }}

    .nova-subtitle {{
        color: {MUTED};
        font-size: 13px;
        margin-top: 6px;
    }}

    .demo-banner {{
        background: #302719;
        border: 1px solid #765C25;
        color: #FDE68A;
        padding: 12px 16px;
        border-radius: 10px;
        margin-bottom: 18px;
        font-size: 13px;
    }}

    .status-pill {{
        display: inline-block;
        background: #10352F;
        color: {ACCENT};
        border: 1px solid #1F5A50;
        padding: 5px 10px;
        border-radius: 20px;
        font-size: 11px;
        font-weight: 700;
    }}

    div.stButton > button {{
        background: {PANEL_LIGHT};
        color: {TEXT};
        border: 1px solid {BORDER};
        border-radius: 9px;
    }}

    div.stButton > button:hover {{
        border-color: {ACCENT};
        color: {ACCENT};
    }}

    div[data-testid="stDownloadButton"] button {{
        background: {ACCENT};
        color: #06221E;
        border: none;
        border-radius: 9px;
        font-weight: 700;
    }}

    hr {{
        border-color: {BORDER};
    }}

    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# 3. DATA GENERATION
# =========================================================

@st.cache_data
def make_demo_data(n=1500):
    """Generate sample orders for demonstration."""

    rng = np.random.default_rng(42)

    start_date = pd.Timestamp("2025-01-01")
    end_date = pd.Timestamp("2026-10-01")

    date_range = (
        end_date - start_date
    ).days

    order_dates = (
        start_date
        + pd.to_timedelta(
            rng.integers(0, date_range + 1, n),
            unit="D",
        )
    )

    categories = [
        "Electronics",
        "Fashion",
        "Home & Kitchen",
        "Beauty",
        "Sports",
        "Books",
    ]

    regions = [
        "North America",
        "Europe",
        "Asia Pacific",
        "Middle East",
        "Africa",
    ]

    products = {
        "Electronics": [
            "Wireless Headphones",
            "Smart Watch",
            "Laptop Stand",
            "Bluetooth Speaker",
        ],
        "Fashion": [
            "Running Shoes",
            "Classic T-Shirt",
            "Leather Bag",
            "Winter Jacket",
        ],
        "Home & Kitchen": [
            "Coffee Maker",
            "Desk Lamp",
            "Storage Organizer",
            "Air Fryer",
        ],
        "Beauty": [
            "Skin Care Set",
            "Hair Dryer",
            "Face Cleanser",
            "Perfume",
        ],
        "Sports": [
            "Yoga Mat",
            "Fitness Tracker",
            "Water Bottle",
            "Resistance Bands",
        ],
        "Books": [
            "Business Strategy",
            "Data Science Guide",
            "Personal Finance",
            "Productivity Journal",
        ],
    }

    selected_categories = rng.choice(
        categories,
        size=n,
    )

    selected_products = [
        rng.choice(products[category])
        for category in selected_categories
    ]

    prices = rng.uniform(15, 450, n).round(2)
    quantities = rng.integers(1, 5, n)
    discounts = rng.choice(
        [0, 0.05, 0.10, 0.15, 0.20],
        size=n,
        p=[0.45, 0.15, 0.20, 0.12, 0.08],
    )

    revenue = (
        prices * quantities * (1 - discounts)
    ).round(2)

    statuses = rng.choice(
        ["Delivered", "Processing", "Shipped", "Cancelled"],
        size=n,
        p=[0.77, 0.10, 0.08, 0.05],
    )

    customers = [
        f"CUST-{number:04d}"
        for number in rng.integers(1, 500, n)
    ]

    df = pd.DataFrame(
        {
            "order_id": [
                f"ORD-{number:06d}"
                for number in range(1, n + 1)
            ],
            "order_date": order_dates,
            "customer_id": customers,
            "product": selected_products,
            "category": selected_categories,
            "region": rng.choice(regions, size=n),
            "quantity": quantities,
            "unit_price": prices,
            "discount": discounts,
            "revenue": revenue,
            "status": statuses,
        }
    )

    return df


# =========================================================
# 4. LOAD DATA
# =========================================================

DB_PATH = Path(__file__).parent / "data" / "ecommerce.db"


def normalize_columns(df):
    """Standardize common column names."""

    df = df.copy()
    df.columns = [
        str(column).strip().lower().replace(" ", "_")
        for column in df.columns
    ]

    aliases = {
        "orderid": "order_id",
        "orderdate": "order_date",
        "customerid": "customer_id",
        "productname": "product",
        "product_category": "category",
        "sales": "revenue",
        "total": "revenue",
        "amount": "revenue",
        "quantity_ordered": "quantity",
        "unitprice": "unit_price",
    }

    df = df.rename(
        columns={
            column: aliases[column]
            for column in df.columns
            if column in aliases
        }
    )

    return df


@st.cache_data
def load_data(db_path):
    """Load orders from SQLite when available."""

    if not Path(db_path).exists():
        return make_demo_data(), True

    try:
        with sqlite3.connect(db_path) as connection:
            tables = pd.read_sql_query(
                """
                SELECT name
                FROM sqlite_master
                WHERE type='table'
                """,
                connection,
            )["name"].tolist()

            if "orders" not in tables:
                return make_demo_data(), True

            df = pd.read_sql_query(
                "SELECT * FROM orders",
                connection,
            )

        if df.empty:
            return make_demo_data(), True

        df = normalize_columns(df)

        required = {
            "order_date",
            "revenue",
        }

        if not required.issubset(df.columns):
            return make_demo_data(), True

        if "order_id" not in df.columns:
            df["order_id"] = [
                f"ORD-{number:06d}"
                for number in range(1, len(df) + 1)
            ]

        if "customer_id" not in df.columns:
            df["customer_id"] = "Unknown"

        if "product" not in df.columns:
            df["product"] = "Unknown Product"

        if "category" not in df.columns:
            df["category"] = "Uncategorized"

        if "region" not in df.columns:
            df["region"] = "Unknown"

        if "quantity" not in df.columns:
            df["quantity"] = 1

        if "unit_price" not in df.columns:
            df["unit_price"] = df["revenue"]

        if "discount" not in df.columns:
            df["discount"] = 0

        if "status" not in df.columns:
            df["status"] = "Delivered"

        df["order_date"] = pd.to_datetime(
            df["order_date"],
            errors="coerce",
        )

        numeric_columns = [
            "revenue",
            "quantity",
            "unit_price",
            "discount",
        ]

        for column in numeric_columns:
            df[column] = pd.to_numeric(
                df[column],
                errors="coerce",
            ).fillna(0)

        df = df.dropna(subset=["order_date"])

        if df.empty:
            return make_demo_data(), True

        return df, False

    except (
        sqlite3.Error,
        pd.errors.DatabaseError,
        ValueError,
        TypeError,
    ):
        return make_demo_data(), True


df, demo_mode = load_data(str(DB_PATH))


# =========================================================
# 5. GENERAL HELPERS
# =========================================================

def money(value):
    return f"${value:,.2f}"


def number(value):
    return f"{value:,.0f}"


def section(title, subtitle=None):
    st.markdown(
        f"<h2 style='margin-bottom:4px'>{title}</h2>",
        unsafe_allow_html=True,
    )

    if subtitle:
        st.markdown(
            f"<p style='margin-top:0'>{subtitle}</p>",
            unsafe_allow_html=True,
        )


def make_chart_dark(fig, height=350):
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(
            color=TEXT,
            family="Arial",
        ),
        height=height,
        margin=dict(l=10, r=10, t=35, b=10),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
        ),
    )

    fig.update_xaxes(
        gridcolor=BORDER,
        zerolinecolor=BORDER,
    )

    fig.update_yaxes(
        gridcolor=BORDER,
        zerolinecolor=BORDER,
    )

    return fig


def kpi_card(label, value, caption=""):
    st.markdown(
        f"""
        <div class="nova-card">
            <div class="nova-label">{label}</div>
            <div class="nova-value">{value}</div>
            <div class="nova-caption">{caption}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def safe_sum(data, column):
    if data.empty or column not in data.columns:
        return 0
    return float(data[column].sum())


def safe_mean(data, column):
    if data.empty or column not in data.columns:
        return 0
    return float(data[column].mean())


# =========================================================
# 6. SIDEBAR NAVIGATION
# =========================================================

with st.sidebar:
    st.markdown(
        f"""
        <div style="padding:10px 0 24px">
            <div style="
                color:{ACCENT};
                font-size:12px;
                font-weight:800;
                letter-spacing:4px;
            ">
                NOVA
            </div>
            <div style="
                color:{TEXT};
                font-size:20px;
                font-weight:800;
                margin-top:5px;
            ">
                Analytics
            </div>
            <div style="
                color:{MUTED};
                font-size:11px;
                margin-top:5px;
            ">
                E-COMMERCE INTELLIGENCE
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("---")

    pages = [
        "Overview",
        "Sales Analytics",
        "Products",
        "Customers",
        "Orders & Reports",
        "Notifications",
        "Account",
    ]

    page = st.radio(
        "NAVIGATION",
        pages,
        label_visibility="visible",
    )

    st.markdown("---")
    st.markdown("**DATA FILTERS**")

    min_date = df["order_date"].min().date()
    max_date = df["order_date"].max().date()

    selected_dates = st.date_input(
        "Order date range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )

    selected_categories = st.multiselect(
        "Categories",
        options=sorted(
            df["category"].dropna().astype(str).unique()
        ),
        default=sorted(
            df["category"].dropna().astype(str).unique()
        ),
    )

    selected_regions = st.multiselect(
        "Regions",
        options=sorted(
            df["region"].dropna().astype(str).unique()
        ),
        default=sorted(
            df["region"].dropna().astype(str).unique()
        ),
    )

    st.markdown("---")

    st.markdown(
        f"""
        <div style="font-size:11px;color:{MUTED}">
            WORKSPACE
        </div>
        <div style="font-size:13px;font-weight:700;margin-top:5px">
            NOVA Analytics
        </div>
        <div style="font-size:11px;color:{ACCENT};margin-top:8px">
            ● Dashboard available
        </div>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# 7. APPLY FILTERS
# =========================================================

filtered_df = df.copy()

if isinstance(selected_dates, (tuple, list)):
    if len(selected_dates) == 2:
        start_date, end_date = selected_dates

        filtered_df = filtered_df[
            (filtered_df["order_date"].dt.date >= start_date)
            & (filtered_df["order_date"].dt.date <= end_date)
        ]

if selected_categories:
    filtered_df = filtered_df[
        filtered_df["category"].astype(str).isin(
            selected_categories
        )
    ]
else:
    filtered_df = filtered_df.iloc[0:0]

if selected_regions:
    filtered_df = filtered_df[
        filtered_df["region"].astype(str).isin(
            selected_regions
        )
    ]
else:
    filtered_df = filtered_df.iloc[0:0]


# =========================================================
# 8. HEADER
# =========================================================

st.markdown(
    f"""
    <div class="nova-header">
        <div class="nova-brand">
            NOVA / BUSINESS INTELLIGENCE
        </div>
        <div class="nova-title">
            E-Commerce Analytics
        </div>
        <div class="nova-subtitle">
            Monitor sales performance, customer behavior,
            product trends and order operations.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

header_left, header_right = st.columns([3, 1])

with header_left:
    st.markdown(
        f"""
        <div style="padding:5px 0 15px">
            <span class="status-pill">● DASHBOARD ACTIVE</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

with header_right:
    st.markdown(
        f"""
        <div style="text-align:right;padding:5px 0 15px">
            <div style="font-size:11px;color:{MUTED}">
                WORKSPACE STATUS
            </div>
            <div style="font-size:13px;color:{ACCENT};font-weight:700">
                NOVA Analytics
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# 9. DEMO MODE NOTICE
# =========================================================

if demo_mode:
    st.markdown(
        """
        <div class="demo-banner">
            <strong>DEMO MODE</strong> — Sample data is being displayed
            because a compatible SQLite database was not found.
            Figures shown in this mode are illustrative, not real business results.
        </div>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# 10. OVERVIEW
# =========================================================

if page == "Overview":
    section(
        "Business Overview",
        "A high-level view of your e-commerce performance.",
    )

    total_revenue = safe_sum(filtered_df, "revenue")
    total_orders = len(filtered_df)
    total_customers = filtered_df["customer_id"].nunique()
    average_order = (
        total_revenue / total_orders
        if total_orders
        else 0
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        kpi_card(
            "TOTAL REVENUE",
            money(total_revenue),
            "Revenue for the selected filters",
        )

    with col2:
        kpi_card(
            "TOTAL ORDERS",
            number(total_orders),
            "Orders in the selected period",
        )

    with col3:
        kpi_card(
            "UNIQUE CUSTOMERS",
            number(total_customers),
            "Distinct customer IDs",
        )

    with col4:
        kpi_card(
            "AVERAGE ORDER VALUE",
            money(average_order),
            "Revenue divided by order count",
        )

    st.markdown("")

    left, right = st.columns([1.65, 1])

    with left:
        section("Revenue Trend", "Revenue by month")

        if not filtered_df.empty:
            monthly = (
                filtered_df
                .assign(
                    month=filtered_df["order_date"].dt.to_period("M")
                    .astype(str)
                )
                .groupby("month", as_index=False)["revenue"]
                .sum()
                .sort_values("month")
            )

            fig = px.line(
                monthly,
                x="month",
                y="revenue",
                markers=True,
                labels={
                    "month": "Month",
                    "revenue": "Revenue ($)",
                },
            )

            fig.update_traces(
                line=dict(color=ACCENT, width=3),
                marker=dict(size=7),
            )

            st.plotly_chart(
                make_chart_dark(fig),
                use_container_width=True,
            )
        else:
            st.info("No data matches the selected filters.")

    with right:
        section("Revenue by Category")

        if not filtered_df.empty:
            category_revenue = (
                filtered_df
                .groupby("category", as_index=False)["revenue"]
                .sum()
                .sort_values("revenue", ascending=False)
            )

            fig = px.pie(
                category_revenue,
                names="category",
                values="revenue",
                hole=0.62,
            )

            fig.update_traces(
                textposition="inside",
                textinfo="percent",
            )

            st.plotly_chart(
                make_chart_dark(fig),
                use_container_width=True,
            )
        else:
            st.info("No category data available.")

    st.markdown("")

    left, right = st.columns(2)

    with left:
        section("Order Status")

        if not filtered_df.empty:
            status_counts = (
                filtered_df["status"]
                .fillna("Unknown")
                .value_counts()
                .rename_axis("status")
                .reset_index(name="orders")
            )

            fig = px.bar(
                status_counts,
                x="status",
                y="orders",
                color="status",
                labels={
                    "status": "Order status",
                    "orders": "Number of orders",
                },
            )

            st.plotly_chart(
                make_chart_dark(fig, 300),
                use_container_width=True,
            )
        else:
            st.info("No order status data available.")

    with right:
        section("Top Products")

        if not filtered_df.empty:
            top_products = (
                filtered_df
                .groupby("product", as_index=False)["revenue"]
                .sum()
                .nlargest(8, "revenue")
                .sort_values("revenue")
            )

            fig = px.bar(
                top_products,
                x="revenue",
                y="product",
                orientation="h",
                labels={
                    "revenue": "Revenue ($)",
                    "product": "Product",
                },
            )

            fig.update_traces(marker_color=ACCENT_BLUE)

            st.plotly_chart(
                make_chart_dark(fig, 300),
                use_container_width=True,
            )
        else:
            st.info("No product data available.")


# =========================================================
# 11. SALES ANALYTICS
# =========================================================

elif page == "Sales Analytics":
    section(
        "Sales Analytics",
        "Explore revenue, order volume and sales performance over time.",
    )

    if filtered_df.empty:
        st.info("No sales data matches the selected filters.")
    else:
        total_revenue = safe_sum(filtered_df, "revenue")
        total_orders = len(filtered_df)
        average_order = (
            total_revenue / total_orders
            if total_orders
            else 0
        )

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Revenue", money(total_revenue))

        with col2:
            st.metric("Orders", number(total_orders))

        with col3:
            st.metric("Average Order Value", money(average_order))

        st.markdown("")

        sales = filtered_df.copy()
        sales["month"] = (
            sales["order_date"].dt.to_period("M").astype(str)
        )

        monthly_sales = (
            sales.groupby("month", as_index=False)
            .agg(
                revenue=("revenue", "sum"),
                orders=("order_id", "nunique"),
            )
            .sort_values("month")
        )

        section("Monthly Performance")

        fig = go.Figure()

        fig.add_trace(
            go.Bar(
                x=monthly_sales["month"],
                y=monthly_sales["revenue"],
                name="Revenue",
                marker_color=ACCENT,
            )
        )

        fig.add_trace(
            go.Scatter(
                x=monthly_sales["month"],
                y=monthly_sales["orders"],
                name="Orders",
                mode="lines+markers",
                yaxis="y2",
                line=dict(color=ACCENT_BLUE, width=3),
            )
        )

        fig.update_layout(
            yaxis=dict(title="Revenue ($)"),
            yaxis2=dict(
                title="Orders",
                overlaying="y",
                side="right",
                showgrid=False,
            ),
            legend=dict(orientation="h", y=1.12),
        )

        st.plotly_chart(
            make_chart_dark(fig, 430),
            use_container_width=True,
        )

        left, right = st.columns(2)

        with left:
            section("Revenue by Region")

            region_sales = (
                filtered_df
                .groupby("region", as_index=False)["revenue"]
                .sum()
                .sort_values("revenue", ascending=False)
            )

            fig = px.bar(
                region_sales,
                x="region",
                y="revenue",
                labels={
                    "region": "Region",
                    "revenue": "Revenue ($)",
                },
            )

            st.plotly_chart(
                make_chart_dark(fig, 340),
                use_container_width=True,
            )

        with right:
            section("Discount Analysis")

            discount_sales = (
                filtered_df
                .assign(
                    discount_band=(
                        filtered_df["discount"] * 100
                    ).round().astype(int).astype(str) + "%"
                )
                .groupby("discount_band", as_index=False)
                .agg(
                    revenue=("revenue", "sum"),
                    orders=("order_id", "nunique"),
                )
            )

            fig = px.bar(
                discount_sales,
                x="discount_band",
                y="revenue",
                labels={
                    "discount_band": "Discount",
                    "revenue": "Revenue ($)",
                },
            )

            st.plotly_chart(
                make_chart_dark(fig, 340),
                use_container_width=True,
            )


# =========================================================
# 12. PRODUCTS
# =========================================================

elif page == "Products":
    section(
        "Product Intelligence",
        "Analyze product revenue, quantity sold and category performance.",
    )

    if filtered_df.empty:
        st.info("No product data matches the selected filters.")
    else:
        product_summary = (
            filtered_df
            .groupby(["product", "category"], as_index=False)
            .agg(
                revenue=("revenue", "sum"),
                units_sold=("quantity", "sum"),
                orders=("order_id", "nunique"),
            )
            .sort_values("revenue", ascending=False)
        )

        total_products = product_summary["product"].nunique()
        total_units = product_summary["units_sold"].sum()

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Products", number(total_products))

        with col2:
            st.metric("Units Sold", number(total_units))

        with col3:
            st.metric(
                "Top Product Revenue",
                money(product_summary["revenue"].max()),
            )

        st.markdown("")

        section("Top Products by Revenue")

        top_products = product_summary.head(15).sort_values("revenue")

        fig = px.bar(
            top_products,
            x="revenue",
            y="product",
            color="category",
            orientation="h",
            labels={
                "revenue": "Revenue ($)",
                "product": "Product",
                "category": "Category",
            },
        )

        st.plotly_chart(
            make_chart_dark(fig, 500),
            use_container_width=True,
        )

        section("Product Performance Table")

        display_products = product_summary.copy()
        display_products["revenue"] = (
            display_products["revenue"].map(money)
        )

        st.dataframe(
            display_products,
            use_container_width=True,
            hide_index=True,
        )


# =========================================================
# 13. CUSTOMERS
# =========================================================

elif page == "Customers":
    section(
        "Customer Analytics",
        "Understand customer contribution and purchasing behavior.",
    )

    if filtered_df.empty:
        st.info("No customer data matches the selected filters.")
    else:
        customer_summary = (
            filtered_df
            .groupby("customer_id", as_index=False)
            .agg(
                revenue=("revenue", "sum"),
                orders=("order_id", "nunique"),
                last_order=("order_date", "max"),
            )
            .sort_values("revenue", ascending=False)
        )

        unique_customers = len(customer_summary)
        repeat_customers = int(
            (customer_summary["orders"] > 1).sum()
        )
        repeat_rate = (
            repeat_customers / unique_customers * 100
            if unique_customers
            else 0
        )

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "Unique Customers",
                number(unique_customers),
            )

        with col2:
            st.metric(
                "Repeat Customers",
                number(repeat_customers),
            )

        with col3:
            st.metric(
                "Repeat Customer Rate",
                f"{repeat_rate:.1f}%",
            )

        left, right = st.columns(2)

        with left:
            section("Top Customers")

            top_customers = (
                customer_summary.head(10)
                .sort_values("revenue")
            )

            fig = px.bar(
                top_customers,
                x="revenue",
                y="customer_id",
                orientation="h",
                labels={
                    "revenue": "Revenue ($)",
                    "customer_id": "Customer",
                },
            )

            fig.update_traces(marker_color=ACCENT)

            st.plotly_chart(
                make_chart_dark(fig, 400),
                use_container_width=True,
            )

        with right:
            section("Orders per Customer")

            order_distribution = (
                customer_summary["orders"]
                .value_counts()
                .sort_index()
                .rename_axis("orders_per_customer")
                .reset_index(name="customers")
            )

            fig = px.bar(
                order_distribution,
                x="orders_per_customer",
                y="customers",
                labels={
                    "orders_per_customer": "Number of orders",
                    "customers": "Number of customers",
                },
            )

            st.plotly_chart(
                make_chart_dark(fig, 400),
                use_container_width=True,
            )

        section("Customer Details")

        display_customers = customer_summary.copy()
        display_customers["revenue"] = (
            display_customers["revenue"].map(money)
        )
        display_customers["last_order"] = (
            display_customers["last_order"].dt.strftime("%Y-%m-%d")
        )

        st.dataframe(
            display_customers,
            use_container_width=True,
            hide_index=True,
        )


# =========================================================
# 14. ORDERS & REPORTS
# =========================================================

elif page == "Orders & Reports":
    section(
        "Orders & Reports",
        "Search, inspect and export the filtered order records.",
    )

    if filtered_df.empty:
        st.info("No orders match the selected filters.")
    else:
        search_term = st.text_input(
            "Search orders",
            placeholder="Enter order ID, customer ID or product name...",
        )

        orders_view = filtered_df.copy()

        if search_term.strip():
            term = search_term.strip().lower()

            mask = (
                orders_view["order_id"].astype(str).str.lower().str.contains(
                    term, na=False
                )
                | orders_view["customer_id"].astype(str).str.lower().str.contains(
                    term, na=False
                )
                | orders_view["product"].astype(str).str.lower().str.contains(
                    term, na=False
                )
            )

            orders_view = orders_view[mask]

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Matching Orders", number(len(orders_view)))

        with col2:
            st.metric("Revenue", money(safe_sum(orders_view, "revenue")))

        with col3:
            st.metric(
                "Average Order",
                money(
                    safe_sum(orders_view, "revenue") / len(orders_view)
                    if len(orders_view)
                    else 0
                ),
            )

        display_orders = orders_view.copy()

        display_orders["order_date"] = (
            display_orders["order_date"].dt.strftime("%Y-%m-%d")
        )

        display_orders["revenue"] = (
            display_orders["revenue"].map(money)
        )

        st.dataframe(
            display_orders,
            use_container_width=True,
            hide_index=True,
        )

        csv_data = orders_view.to_csv(index=False).encode("utf-8")

        st.download_button(
            label="Download filtered orders (CSV)",
            data=csv_data,
            file_name="nova_filtered_orders.csv",
            mime="text/csv",
            use_container_width=True,
        )

        st.markdown("")

        section("Export Summary")

        summary = pd.DataFrame(
            {
                "Metric": [
                    "Number of orders",
                    "Total revenue",
                    "Unique customers",
                    "Number of products",
                ],
                "Value": [
                    len(orders_view),
                    round(safe_sum(orders_view, "revenue"), 2),
                    orders_view["customer_id"].nunique(),
                    orders_view["product"].nunique(),
                ],
            }
        )

        st.dataframe(
            summary,
            use_container_width=True,
            hide_index=True,
        )

        st.download_button(
            label="Download summary (CSV)",
            data=summary.to_csv(index=False).encode("utf-8"),
            file_name="nova_summary.csv",
            mime="text/csv",
        )


# =========================================================
# 15. NOTIFICATIONS
# =========================================================

elif page == "Notifications":
    section(
        "Notifications & Insights",
        "Review data quality notices and quick business observations.",
    )

    if demo_mode:
        st.warning(
            "The dashboard is using illustrative demo data. "
            "Connect a compatible database before relying on the figures."
        )
    else:
        st.success(
            "A compatible SQLite database was loaded successfully."
        )

    if filtered_df.empty:
        st.info(
            "There are no orders in the current filter selection. "
            "Try changing the date range, categories or regions."
        )
    else:
        missing_values = int(
            filtered_df.isna().sum().sum()
        )

        duplicate_orders = int(
            filtered_df["order_id"].duplicated().sum()
        )

        if missing_values:
            st.warning(
                f"Missing values detected in the filtered dataset: "
                f"{missing_values}."
            )
        else:
            st.success("No missing values found in the filtered dataset.")

        if duplicate_orders:
            st.warning(
                f"Potential duplicate order IDs: {duplicate_orders}."
            )
        else:
            st.success("No duplicate order IDs found in the filtered dataset.")

        top_category = (
            filtered_df.groupby("category")["revenue"]
            .sum()
            .idxmax()
        )

        top_region = (
            filtered_df.groupby("region")["revenue"]
            .sum()
            .idxmax()
        )

        st.markdown(
            f"""
            <div class="nova-card">
                <div class="nova-label">BUSINESS INSIGHT</div>
                <div style="font-size:16px;font-weight:700;margin-top:10px">
                    Best-performing category
                </div>
                <div style="color:{ACCENT};font-size:22px;font-weight:800">
                    {top_category}
                </div>
            </div>

            <div class="nova-card">
                <div class="nova-label">GEOGRAPHIC INSIGHT</div>
                <div style="font-size:16px;font-weight:700;margin-top:10px">
                    Leading region by revenue
                </div>
                <div style="color:{ACCENT_BLUE};font-size:22px;font-weight:800">
                    {top_region}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# =========================================================
# 16. ACCOUNT / WORKSPACE
# =========================================================

elif page == "Account":
    section(
        "Workspace & Preferences",
        "Application information and current data source.",
    )

    source_name = (
        "Demo dataset"
        if demo_mode
        else "SQLite database"
    )

    st.markdown(
        f"""
        <div class="nova-card">
            <div class="nova-label">APPLICATION</div>
            <div style="font-size:22px;font-weight:800;margin:8px 0 22px">
                NOVA | E-Commerce Analytics
            </div>

            <div class="nova-label">ACCESS</div>
            <div style="font-size:15px;font-weight:700;margin:8px 0 22px">
                Open dashboard — no login required
            </div>

            <div class="nova-label">DATA SOURCE</div>
            <div style="font-size:15px;font-weight:700;margin:8px 0 22px">
                {source_name}
            </div>

            <div class="nova-label">DATABASE PATH</div>
            <div style="font-size:13px;margin-top:8px;overflow-wrap:anywhere">
                {DB_PATH}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("")

    st.markdown(
        f"""
        <div class="nova-card">
            <div class="nova-label">ABOUT NOVA</div>
            <p style="margin-top:12px">
                NOVA is an e-commerce analytics dashboard for exploring
                sales, products, customers and order operations.
            </p>
            <p>
                Use the sidebar to navigate between pages and apply
                filters to the displayed results.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# 17. FOOTER
# =========================================================

st.markdown("---")

footer_left, footer_right = st.columns(2)

with footer_left:
    st.markdown(
        f"""
        <div style="font-size:11px;color:{MUTED}">
            NOVA | E-COMMERCE ANALYTICS
        </div>
        """,
        unsafe_allow_html=True,
    )

with footer_right:
    st.markdown(
        f"""
        <div style="font-size:11px;color:{MUTED};text-align:right">
            BUSINESS INTELLIGENCE · DATA ANALYTICS
        </div>
        """,
        unsafe_allow_html=True,
    )
