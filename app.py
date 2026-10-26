
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


# =========================================================
# 1. CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="NOVA | E-Commerce Analytics",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded",
)

DB_PATH = Path("data/ecommerce.db")

BG = "#080E1B"
PANEL = "#101A2B"
PANEL2 = "#142238"
ACCENT = "#38E5C3"
BLUE = "#69A7FF"
PURPLE = "#B39AFF"
ORANGE = "#FFB86B"
TEXT = "#F0F5FF"
MUTED = "#92A4BC"
BORDER = "#263750"

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
        background: #0C1525;
        border-right: 1px solid {BORDER};
    }}

    [data-testid="stSidebar"] * {{
        color: {TEXT};
    }}

    .nova-logo {{
        color: {ACCENT};
        font-size: 27px;
        font-weight: 800;
        letter-spacing: 4px;
    }}

    .nova-caption {{
        color: {MUTED};
        font-size: 11px;
        letter-spacing: 2px;
        text-transform: uppercase;
    }}

    .hero {{
        background: linear-gradient(115deg, #142B43, #10353C 65%, #16304B);
        border: 1px solid #2A5261;
        border-radius: 18px;
        padding: 26px 30px;
        margin-bottom: 20px;
    }}

    .eyebrow {{
        color: {ACCENT};
        font-size: 11px;
        font-weight: 800;
        letter-spacing: 3px;
    }}

    .hero-title {{
        color: {TEXT};
        font-size: 31px;
        font-weight: 800;
        margin: 10px 0;
    }}

    .hero-sub {{
        color: #B9C9DA;
        font-size: 13px;
    }}

    .metric {{
        background: {PANEL};
        border: 1px solid {BORDER};
        border-radius: 15px;
        padding: 17px;
        min-height: 128px;
    }}

    .metric-label {{
        color: {MUTED};
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 1px;
    }}

    .metric-value {{
        color: {TEXT};
        font-size: 25px;
        font-weight: 800;
        margin: 12px 0 5px;
        overflow-wrap: anywhere;
    }}

    .metric-foot {{
        color: {ACCENT};
        font-size: 11px;
    }}

    .section-head {{
        color: {TEXT};
        font-size: 19px;
        font-weight: 750;
        margin-top: 22px;
        margin-bottom: 4px;
    }}

    .section-sub {{
        color: {MUTED};
        font-size: 12px;
        margin-bottom: 13px;
    }}

    .info-card {{
        background: {PANEL};
        border: 1px solid {BORDER};
        border-radius: 14px;
        padding: 17px;
    }}

    .status-pill {{
        color: {ACCENT};
        background: #12352F;
        padding: 5px 9px;
        border-radius: 20px;
        font-size: 10px;
        font-weight: 700;
    }}

    div[data-testid="stPlotlyChart"] {{
        background: {PANEL};
        border: 1px solid {BORDER};
        border-radius: 14px;
        padding: 5px;
    }}

    div[data-testid="stDataFrame"] {{
        border: 1px solid {BORDER};
        border-radius: 12px;
    }}

    div.stButton > button,
    div.stDownloadButton > button {{
        border-radius: 9px;
        min-height: 38px;
    }}

    div.stButton > button[kind="primary"] {{
        background: {ACCENT};
        color: #06131A;
        border: none;
        font-weight: 800;
    }}

    hr {{
        border-color: {BORDER};
    }}

    #MainMenu, footer {{
        visibility: hidden;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# 2. DEMO DATA
# =========================================================

@st.cache_data
def make_demo_data():
    rng = np.random.default_rng(42)

    n = 1200
    dates = pd.date_range(
        end=pd.Timestamp.today().normalize(),
        periods=365,
        freq="D",
    )

    categories = [
        "Electronics",
        "Fashion",
        "Home & Living",
        "Beauty",
        "Sports",
    ]

    products = {
        "Electronics": [
            "Wireless Headphones",
            "Smart Watch",
            "Bluetooth Speaker",
            "Laptop Stand",
        ],
        "Fashion": [
            "Classic Sneakers",
            "Urban Backpack",
            "Cotton T-Shirt",
            "Premium Jacket",
        ],
        "Home & Living": [
            "Desk Lamp",
            "Ceramic Mug",
            "Storage Organizer",
            "Modern Chair",
        ],
        "Beauty": [
            "Skincare Set",
            "Daily Moisturizer",
            "Face Cleanser",
            "Beauty Kit",
        ],
        "Sports": [
            "Yoga Mat",
            "Fitness Bottle",
            "Resistance Bands",
            "Training Bag",
        ],
    }

    regions = [
        "North America",
        "Europe",
        "Asia Pacific",
        "Middle East",
        "North Africa",
    ]

    records = []

    for i in range(n):
        category = rng.choice(categories)
        product = rng.choice(products[category])
        quantity = int(rng.integers(1, 5))
        price = float(rng.uniform(18, 320))
        discount = float(rng.choice([0, 0, 0.05, 0.10, 0.15]))
        status = rng.choice(
            ["Delivered", "Delivered", "Delivered", "Processing", "Cancelled"]
        )

        records.append({
            "order_id": f"ORD-{10001 + i}",
            "order_date": pd.Timestamp(
                rng.choice(dates)
            ),
            "customer_id": f"CUST-{int(rng.integers(1000, 1460))}",
            "product_name": product,
            "category": category,
            "region": rng.choice(regions),
            "quantity": quantity,
            "unit_price": round(price, 2),
            "discount": discount,
            "status": status,
        })

    data = pd.DataFrame(records)
    data["revenue"] = (
        data["quantity"]
        * data["unit_price"]
        * (1 - data["discount"])
    ).round(2)

    return data


# =========================================================
# 3. DATABASE LOADING
# =========================================================

@st.cache_data
def load_database(path):
    if not Path(path).exists():
        return None

    try:
        with sqlite3.connect(path) as connection:
            tables = pd.read_sql_query(
                "SELECT name FROM sqlite_master WHERE type='table'",
                connection,
            )

            if "orders" not in tables["name"].tolist():
                return None

            return pd.read_sql_query(
                'SELECT * FROM "orders"',
                connection,
            )
    except Exception:
        return None


def prepare_data(data):
    if data is None or data.empty:
        return None

    data = data.copy()
    data.columns = [
        str(col).strip().lower()
        for col in data.columns
    ]

    if not {"order_id", "order_date", "unit_price"}.issubset(data.columns):
        return None

    data["order_date"] = pd.to_datetime(
        data["order_date"], errors="coerce"
    )
    data["unit_price"] = pd.to_numeric(
        data["unit_price"], errors="coerce"
    )

    data = data.dropna(
        subset=["order_id", "order_date", "unit_price"]
    ).copy()

    if data.empty:
        return None

    if "customer_id" not in data.columns:
        data["customer_id"] = "Unknown"

    if "quantity" not in data.columns:
        data["quantity"] = 1

    data["quantity"] = pd.to_numeric(
        data["quantity"], errors="coerce"
    ).fillna(0)

    if "revenue" not in data.columns:
        data["revenue"] = (
            data["quantity"] * data["unit_price"]
        )
    else:
        data["revenue"] = pd.to_numeric(
            data["revenue"], errors="coerce"
        )
        data["revenue"] = data["revenue"].fillna(
            data["quantity"] * data["unit_price"]
        )

    for col, default in {
        "category": "Unclassified",
        "region": "Unknown",
        "product_name": "Unknown product",
        "status": "Unknown",
    }.items():
        if col not in data.columns:
            data[col] = default
        else:
            data[col] = data[col].fillna(default).astype(str)

    data["month"] = data["order_date"].dt.to_period("M").astype(str)

    return data


real_data = load_database(str(DB_PATH))
df = prepare_data(real_data)

demo_mode = df is None

if demo_mode:
    df = make_demo_data()

df = prepare_data(df)


# =========================================================
# 4. DEMO AUTHENTICATION UI
# =========================================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user_email" not in st.session_state:
    st.session_state.user_email = "analyst@nova.demo"


def login_screen():
    st.markdown("<br><br>", unsafe_allow_html=True)

    left, right = st.columns([1.15, 0.85], gap="large")

    with left:
        st.markdown(
            """
            <div class="hero" style="padding:45px 35px; min-height:400px;">
                <div class="eyebrow">✦ NOVA INTELLIGENCE</div>
                <div class="hero-title" style="font-size:42px;">
                    Your business.<br>Your next move.
                </div>
                <div class="hero-sub" style="font-size:15px; line-height:1.9;">
                    One intelligent workspace to understand your sales,
                    discover customer trends and make data-driven decisions.
                </div>
                <br>
                <div style="color:#38E5C3; font-weight:700;">
                    SALES ANALYTICS &nbsp; · &nbsp; CUSTOMER INSIGHTS
                </div>
                <br>
                <div style="color:#B9C9DA;">
                    Built for modern e-commerce teams.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with right:
        st.markdown("### Welcome back")
        st.caption("Sign in to access your analytics workspace.")

        with st.form("login_form"):
            email = st.text_input(
                "Work email",
                placeholder="you@company.com",
            )

            password = st.text_input(
                "Password",
                type="password",
                placeholder="Enter your password",
            )

            remember = st.checkbox("Remember me")

            submitted = st.form_submit_button(
                "Sign in →",
                type="primary",
                use_container_width=True,
            )

            if submitted:
                if email.strip() and password:
                    st.session_state.logged_in = True
                    st.session_state.user_email = email.strip()
                    st.rerun()
                else:
                    st.error("Enter an email and password to preview the dashboard.")

        st.info(
            "Portfolio demo: this sign-in screen is a visual prototype. "
            "It does not verify passwords or provide secure authentication."
        )

        st.caption("NOVA · E-Commerce Analytics · Demo edition")


if not st.session_state.logged_in:
    login_screen()
    st.stop()


# =========================================================
# 5. SIDEBAR & NAVIGATION
# =========================================================

with st.sidebar:
    st.markdown(
        """
        <div class="nova-logo">NOVA</div>
        <div class="nova-caption">E-Commerce Analytics</div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()

    st.markdown("**WORKSPACE**")

    page = st.radio(
        "Navigation",
        [
            "Overview",
            "Sales Analytics",
            "Products",
            "Customers",
            "Orders & Reports",
            "Notifications",
            "Account",
        ],
        label_visibility="collapsed",
    )

    st.divider()

    st.markdown("**DATA SOURCE**")

    if demo_mode:
        st.warning("Demo dataset active")
    else:
        st.success("Database connected")

    st.caption("NOVA Intelligence Platform")

    if st.button("Sign out", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()


# =========================================================
# 6. GLOBAL FILTERS
# =========================================================

min_date = df["order_date"].min().date()
max_date = df["order_date"].max().date()

with st.sidebar:
    date_range = st.date_input(
        "Analysis period",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )

    if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
        start_date, end_date = date_range
    else:
        start_date, end_date = min_date, max_date

    period_df = df[
        df["order_date"].dt.date.between(start_date, end_date)
    ].copy()

    category_options = sorted(
        period_df["category"].astype(str).unique()
    )

    selected_categories = st.multiselect(
        "Categories",
        category_options,
        default=category_options,
    )

    region_options = sorted(
        period_df["region"].astype(str).unique()
    )

    selected_regions = st.multiselect(
        "Regions",
        region_options,
        default=region_options,
    )

filtered = period_df[
    period_df["category"].astype(str).isin(selected_categories)
    & period_df["region"].astype(str).isin(selected_regions)
].copy()


# =========================================================
# 7. COMMON HELPERS
# =========================================================

def money(value):
    return f"{value:,.2f}"


def metric(label, value, note, color=ACCENT):
    st.markdown(
        f"""
        <div class="metric">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-foot" style="color:{color};">{note}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section(title, subtitle=""):
    st.markdown(
        f'<div class="section-head">{title}</div>'
        f'<div class="section-sub">{subtitle}</div>',
        unsafe_allow_html=True,
    )


def style_fig(fig, height=350):
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor=PANEL,
        plot_bgcolor=PANEL,
        font=dict(color=TEXT, family="Inter"),
        height=height,
        margin=dict(l=20, r=20, t=55, b=25),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            orientation="h",
            y=-0.2,
        ),
        xaxis=dict(showgrid=False, zeroline=False),
        yaxis=dict(gridcolor=BORDER, zeroline=False),
    )
    return fig


# =========================================================
# 8. HEADER AND NOTIFICATIONS
# =========================================================

notifications = [
    ("Revenue report", "Your analytics workspace is ready to explore.", "INFO"),
    ("Customer insights", "Review your highest-value customers.", "INSIGHT"),
    ("Data status", "Check the current dataset mode before sharing reports.", "SYSTEM"),
]

header_left, header_right = st.columns([4, 1])

with header_left:
    st.markdown(
        f"""
        <div style="padding:5px 0 18px;">
            <div style="color:{MUTED}; font-size:12px;">
                NOVA / {page.upper()}
            </div>
            <div style="font-size:23px; font-weight:800; color:{TEXT};">
                Good to see you again.
            </div>
            <div style="color:{MUTED}; font-size:12px; margin-top:5px;">
                {datetime.now().strftime("%d %B %Y")}
                &nbsp; · &nbsp; Business intelligence workspace
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with header_right:
    st.markdown(
        f"""
        <div style="text-align:right; padding:8px 0;">
            <div style="font-size:12px; color:{MUTED};">SIGNED IN AS</div>
            <div style="font-size:13px; color:{ACCENT}; font-weight:700;">
                {st.session_state.user_email}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

if demo_mode:
    st.warning(
        "DEMO MODE — sample data is displayed because a compatible database "
        "was not detected. Do not present these figures as real business results."
    )

with st.expander("🔔 Notifications · 3 updates"):
    for title, message, tag in notifications:
        st.markdown(
            f"""
            <div class="info-card" style="margin-bottom:8px;">
                <strong>{title}</strong>
                <span class="status-pill" style="float:right;">{tag}</span>
                <div style="color:{MUTED}; font-size:12px; margin-top:7px;">
                    {message}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# =========================================================
# 9. OVERVIEW
# =========================================================

if page == "Overview":
    section(
        "Executive Overview",
        "A consolidated view of sales, customer activity and operations.",
    )

    revenue = filtered["revenue"].sum()
    order_count = filtered["order_id"].nunique()
    customer_count = filtered["customer_id"].nunique()
    units = filtered["quantity"].sum()
    aov = revenue / order_count if order_count else 0

    k1, k2, k3, k4, k5 = st.columns(5)

    with k1:
        metric("TOTAL REVENUE", money(revenue), "Selected period")

    with k2:
        metric("ORDERS", f"{order_count:,}", "Unique orders", BLUE)

    with k3:
        metric("CUSTOMERS", f"{customer_count:,}", "Unique customer IDs", PURPLE)

    with k4:
        metric("AVERAGE ORDER", money(aov), "Revenue per order", ORANGE)

    with k5:
        metric("UNITS SOLD", f"{units:,.0f}", "Total quantity")

    section("Revenue Intelligence", "Monthly trends and category contribution.")

    left, right = st.columns([1.65, 1])

    with left:
        monthly = (
            filtered.groupby("month", as_index=False)
            .agg(revenue=("revenue", "sum"))
            .sort_values("month")
        )

        fig = px.area(
            monthly,
            x="month",
            y="revenue",
            title="Revenue Evolution",
            markers=True,
            color_discrete_sequence=[ACCENT],
        )

        fig.update_traces(
            fillcolor="rgba(56,229,195,0.13)",
            line=dict(width=3),
        )

        st.plotly_chart(
            style_fig(fig),
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
            hole=0.66,
            title="Category Mix",
            color_discrete_sequence=[
                ACCENT, BLUE, PURPLE, ORANGE, "#F472B6"
            ],
        )

        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor=PANEL,
            font=dict(color=TEXT),
            height=350,
            margin=dict(l=15, r=15, t=55, b=20),
        )

        st.plotly_chart(fig, use_container_width=True)

    section("Markets & Products", "Identify your strongest regions and products.")

    left, right = st.columns(2)

    with left:
        regional = (
            filtered.groupby("region", as_index=False)
            .agg(revenue=("revenue", "sum"))
            .sort_values("revenue")
        )

        fig = px.bar(
            regional,
            x="revenue",
            y="region",
            orientation="h",
            title="Revenue by Region",
            color="revenue",
            color_continuous_scale=["#164E63", ACCENT],
        )

        fig.update_layout(coloraxis_showscale=False)

        st.plotly_chart(
            style_fig(fig, 330),
            use_container_width=True,
        )

    with right:
        products = (
            filtered.groupby("product_name", as_index=False)
            .agg(
                revenue=("revenue", "sum"),
                units=("quantity", "sum"),
            )
            .sort_values("revenue", ascending=False)
            .head(8)
            .sort_values("revenue")
        )

        fig = px.bar(
            products,
            x="revenue",
            y="product_name",
            orientation="h",
            title="Top Products",
            color="revenue",
            color_continuous_scale=["#164E63", ACCENT],
        )

        fig.update_layout(coloraxis_showscale=False)

        st.plotly_chart(
            style_fig(fig, 330),
            use_container_width=True,
        )

    section("Recent Orders", "Latest transactions in the selected dataset.")

    recent = filtered.sort_values(
        "order_date", ascending=False
    ).head(10).copy()

    recent["order_date"] = recent["order_date"].dt.strftime("%Y-%m-%d")

    st.dataframe(
        recent[
            [
                "order_id", "order_date", "customer_id",
                "product_name", "category", "region",
                "quantity", "revenue", "status",
            ]
        ],
        use_container_width=True,
        hide_index=True,
    )


# =========================================================
# 10. SALES ANALYTICS
# =========================================================

elif page == "Sales Analytics":
    section(
        "Sales Analytics",
        "Explore sales patterns, order value and business performance.",
    )

    total_revenue = filtered["revenue"].sum()
    order_count = filtered["order_id"].nunique()
    avg_order = total_revenue / order_count if order_count else 0

    a, b, c = st.columns(3)

    with a:
        metric("REVENUE", money(total_revenue), "Filtered revenue")

    with b:
        metric("ORDERS", f"{order_count:,}", "Distinct orders", BLUE)

    with c:
        metric("AVERAGE ORDER VALUE", money(avg_order), "Revenue / orders", PURPLE)

    monthly = (
        filtered.groupby("month", as_index=False)
        .agg(
            revenue=("revenue", "sum"),
            orders=("order_id", "nunique"),
        )
        .sort_values("month")
    )

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=monthly["month"],
            y=monthly["revenue"],
            mode="lines+markers",
            name="Revenue",
            line=dict(color=ACCENT, width=3),
            fill="tozeroy",
            fillcolor="rgba(56,229,195,0.08)",
        )
    )

    fig.update_layout(title="Revenue Trend Over Time")

    st.plotly_chart(
        style_fig(fig, 400),
        use_container_width=True,
    )

    fig = px.bar(
        monthly,
        x="month",
        y="orders",
        title="Monthly Order Volume",
        color_discrete_sequence=[BLUE],
    )

    st.plotly_chart(
        style_fig(fig),
        use_container_width=True,
    )

    st.dataframe(monthly, use_container_width=True, hide_index=True)


# =========================================================
# 11. PRODUCTS
# =========================================================

elif page == "Products":
    section(
        "Product Intelligence",
        "Analyze product performance, volume and category contribution.",
    )

    products = (
        filtered.groupby(["product_name", "category"], as_index=False)
        .agg(
            revenue=("revenue", "sum"),
            units=("quantity", "sum"),
            orders=("order_id", "nunique"),
        )
        .sort_values("revenue", ascending=False)
    )

    left, right = st.columns(2)

    with left:
        fig = px.bar(
            products.head(12).sort_values("revenue"),
            x="revenue",
            y="product_name",
            orientation="h",
            title="Top 12 Products by Revenue",
            color_discrete_sequence=[ACCENT],
        )

        st.plotly_chart(
            style_fig(fig, 430),
            use_container_width=True,
        )

    with right:
        fig = px.scatter(
            products,
            x="units",
            y="revenue",
            size="orders",
            color="category",
            hover_name="product_name",
            title="Product Revenue vs Units Sold",
        )

        st.plotly_chart(
            style_fig(fig, 430),
            use_container_width=True,
        )

    st.dataframe(
        products,
        use_container_width=True,
        hide_index=True,
    )


# =========================================================
# 12. CUSTOMERS
# =========================================================

elif page == "Customers":
    section(
        "Customer Intelligence",
        "Understand customer value and purchasing behavior.",
    )

    customers = (
        filtered.groupby("customer_id", as_index=False)
        .agg(
            revenue=("revenue", "sum"),
            orders=("order_id", "nunique"),
            units=("quantity", "sum"),
        )
        .sort_values("revenue", ascending=False)
    )

    a, b, c = st.columns(3)

    with a:
        metric("CUSTOMERS", f"{len(customers):,}", "Unique customer IDs")

    with b:
        metric(
            "REVENUE / CUSTOMER",
            money(customers["revenue"].mean()) if len(customers) else "0.00",
            "Average customer revenue",
            BLUE,
        )

    with c:
        metric(
            "REPEAT CUSTOMERS",
            f"{int((customers['orders'] > 1).sum()):,}",
            "More than one distinct order",
            PURPLE,
        )

    left, right = st.columns(2)

    with left:
        fig = px.histogram(
            customers,
            x="revenue",
            nbins=25,
            title="Customer Revenue Distribution",
            color_discrete_sequence=[ACCENT],
        )

        st.plotly_chart(
            style_fig(fig),
            use_container_width=True,
        )

    with right:
        fig = px.scatter(
            customers,
            x="orders",
            y="revenue",
            title="Orders vs Customer Revenue",
            color_discrete_sequence=[BLUE],
        )

        st.plotly_chart(
            style_fig(fig),
            use_container_width=True,
        )

    st.markdown("### Highest-value customers")

    st.dataframe(
        customers.head(20),
        use_container_width=True,
        hide_index=True,
    )


# =========================================================
# 13. ORDERS & REPORTS
# =========================================================

elif page == "Orders & Reports":
    section(
        "Orders & Reports",
        "Inspect transactions and export filtered records.",
    )

    statuses = (
        filtered.groupby("status", as_index=False)
        .agg(orders=("order_id", "nunique"))
        .sort_values("orders", ascending=False)
    )

    fig = px.bar(
        statuses,
        x="status",
        y="orders",
        color="status",
        title="Order Status Distribution",
    )

    st.plotly_chart(
        style_fig(fig),
        use_container_width=True,
    )

    search = st.text_input(
        "Search order, customer or product",
        placeholder="Enter a keyword...",
    )

    view = filtered.copy()

    if search.strip():
        mask = view.astype(str).apply(
            lambda col: col.str.contains(
                search.strip(),
                case=False,
                na=False,
            )
        ).any(axis=1)

        view = view[mask]

    st.dataframe(
        view,
        use_container_width=True,
        hide_index=True,
    )

    st.download_button(
        "⬇ Download CSV report",
        data=view.to_csv(index=False).encode("utf-8"),
        file_name="nova_ecommerce_report.csv",
        mime="text/csv",
        use_container_width=True,
    )


# =========================================================
# 14. NOTIFICATIONS
# =========================================================

elif page == "Notifications":
    section(
        "Notification Center",
        "A centralized place for system messages and business insights.",
    )

    st.markdown(
        f"""
        <div class="info-card">
            <div style="color:{ACCENT}; font-size:11px; font-weight:800;">
                SYSTEM · WORKSPACE
            </div>
            <h3>Welcome to NOVA</h3>
            <div style="color:{MUTED};">
                Your analytics workspace is ready.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.write("")

    st.info(
        "Demo notification: connect a real notification service or configure "
        "business rules to receive genuine alerts."
    )

    if st.button("Mark demo notifications as read"):
        st.success("Demo notifications marked as read for this session.")


# =========================================================
# 15. ACCOUNT
# =========================================================

elif page == "Account":
    section(
        "Account & Preferences",
        "View the current demo session and workspace status.",
    )

    st.markdown(
        f"""
        <div class="info-card">
            <div style="color:{MUTED}; font-size:11px;">SIGNED-IN EMAIL</div>
            <div style="font-size:20px; font-weight:800; margin:8px 0 18px;">
                {st.session_state.user_email}
            </div>
            <div style="color:{MUTED}; font-size:11px;">APPLICATION</div>
            <div style="font-size:15px; font-weight:700; margin:8px 0 18px;">
                NOVA | E-Commerce Analytics
            </div>
            <div style="color:{MUTED}; font-size:11px;">DATA SOURCE</div>
            <div style="font-size:15px; font-weight:700; margin-top:8px;">
                {"Demo data" if demo_mode else "SQLite database"}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.write("")
    st.warning(
        "The current login is a demonstration only. "
        "It does not implement secure user authentication, password storage, "
        "password reset or multi-user permissions."
    )


# =========================================================
# 16. FOOTER
# =========================================================

st.divider()

st.markdown(
    f"""
    <div style="text-align:center; padding:12px; color:{MUTED}; font-size:11px;">
        <span style="color:{ACCENT}; font-weight:800; letter-spacing:2px;">
            NOVA
        </span>
        &nbsp; | &nbsp; E-Commerce Analytics
        <br><br>
        SALES INTELLIGENCE · CUSTOMER INSIGHTS · BUSINESS PERFORMANCE
    </div>
    """,
    unsafe_allow_html=True,
)
