
import sqlite3
from pathlib import Path

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

BG = "#0B1120"
PANEL = "#111B2E"
ACCENT = "#25D9C3"
BLUE = "#6495FF"
TEXT = "#F1F5F9"
MUTED = "#91A1B7"


# =========================================================
# 2. DESIGN
# =========================================================

st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {{
        font-family: 'Inter', sans-serif;
    }}

    .stApp {{
        background: {BG};
        color: {TEXT};
    }}

    [data-testid="stSidebar"] {{
        background: #0D1728;
        border-right: 1px solid #233149;
    }}

    [data-testid="stSidebar"] * {{
        color: {TEXT};
    }}

    .nova-hero {{
        background: linear-gradient(120deg, #14263D 0%, #102D3B 55%, #123A42 100%);
        border: 1px solid #25465A;
        border-radius: 20px;
        padding: 30px 32px;
        margin-bottom: 24px;
    }}

    .nova-label {{
        color: {ACCENT};
        font-size: 12px;
        font-weight: 800;
        letter-spacing: 3px;
        text-transform: uppercase;
    }}

    .nova-title {{
        font-size: 34px;
        font-weight: 800;
        color: {TEXT};
        margin: 10px 0 6px 0;
    }}

    .nova-subtitle {{
        font-size: 14px;
        color: #B8C7D9;
    }}

    .metric-card {{
        background: {PANEL};
        border: 1px solid #24334A;
        border-radius: 15px;
        padding: 20px;
        min-height: 125px;
    }}

    .metric-label {{
        color: {MUTED};
        font-size: 12px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
    }}

    .metric-value {{
        color: {TEXT};
        font-size: 27px;
        font-weight: 800;
        margin-top: 12px;
    }}

    .metric-note {{
        color: {ACCENT};
        font-size: 12px;
        margin-top: 6px;
    }}

    div[data-testid="stPlotlyChart"] {{
        background: {PANEL};
        border: 1px solid #24334A;
        border-radius: 15px;
        padding: 8px;
    }}

    h1, h2, h3 {{
        color: {TEXT};
    }}

    .stCaption {{
        color: {MUTED};
    }}

    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# 3. CHARGEMENT DES DONNÉES
# =========================================================

@st.cache_data
def load_data():
    if not DB_PATH.exists():
        return None, f"Base de données introuvable : {DB_PATH}"

    try:
        with sqlite3.connect(DB_PATH) as connection:
            tables = pd.read_sql_query(
                "SELECT name FROM sqlite_master WHERE type='table'",
                connection,
            )

            if "orders" not in tables["name"].tolist():
                return None, "La table 'orders' n'existe pas dans la base."

            data = pd.read_sql_query(
                'SELECT * FROM "orders"',
                connection,
            )

        if data.empty:
            return None, "La table orders ne contient aucune donnée."

        return data, None

    except Exception as error:
        return None, f"Erreur lors du chargement des données : {error}"


df, load_error = load_data()


# =========================================================
# 4. EN-TÊTE
# =========================================================

st.markdown(
    """
    <div class="nova-hero">
        <div class="nova-label">✦ NOVA ANALYTICS PLATFORM</div>
        <div class="nova-title">NOVA | E-Commerce Analytics</div>
        <div class="nova-subtitle">
            Interactive business intelligence · Sales performance · Customer insights
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# 5. VÉRIFICATION DES DONNÉES
# =========================================================

if load_error:
    st.error(load_error)

    st.markdown(
        """
        **Pour connecter ton dashboard :**
        1. Vérifie que le fichier `data/ecommerce.db` existe dans ton dépôt.
        2. Vérifie que la base contient une table `orders`.
        3. Vérifie les noms des colonnes dans cette table.
        """
    )

    st.stop()


# =========================================================
# 6. PRÉPARATION DES DONNÉES
# =========================================================

df.columns = [str(column).strip().lower() for column in df.columns]

required_columns = ["order_id", "order_date", "customer_id"]

missing_columns = [
    column for column in required_columns
    if column not in df.columns
]

if missing_columns:
    st.error(
        "Colonnes obligatoires manquantes : "
        + ", ".join(missing_columns)
    )
    st.write("Colonnes disponibles :", df.columns.tolist())
    st.stop()

df["order_date"] = pd.to_datetime(
    df["order_date"],
    errors="coerce",
)

df = df.dropna(subset=["order_date"]).copy()

if df.empty:
    st.error("Aucune date de commande valide n'a été trouvée.")
    st.stop()

if "quantity" not in df.columns:
    df["quantity"] = 1

df["quantity"] = pd.to_numeric(
    df["quantity"],
    errors="coerce",
).fillna(0)

if "unit_price" not in df.columns:
    st.error("La colonne 'unit_price' est nécessaire pour calculer le chiffre d'affaires.")
    st.write("Colonnes disponibles :", df.columns.tolist())
    st.stop()

df["unit_price"] = pd.to_numeric(
    df["unit_price"],
    errors="coerce",
).fillna(0)

if "revenue" in df.columns:
    df["revenue"] = pd.to_numeric(
        df["revenue"],
        errors="coerce",
    )
    df["revenue"] = df["revenue"].fillna(
        df["quantity"] * df["unit_price"]
    )
else:
    df["revenue"] = df["quantity"] * df["unit_price"]

if "category" not in df.columns:
    df["category"] = "Unclassified"

if "region" not in df.columns:
    df["region"] = "Unknown"

if "product_name" not in df.columns:
    df["product_name"] = "Unknown product"

if "status" not in df.columns:
    df["status"] = "Unknown"

if "discount" not in df.columns:
    df["discount"] = 0

df["discount"] = pd.to_numeric(
    df["discount"],
    errors="coerce",
).fillna(0)

df["month"] = df["order_date"].dt.to_period("M").astype(str)


# =========================================================
# 7. FILTRES
# =========================================================

st.sidebar.markdown("## ✦ NOVA")
st.sidebar.caption("E-Commerce Analytics")
st.sidebar.divider()

min_date = df["order_date"].min().date()
max_date = df["order_date"].max().date()

date_range = st.sidebar.date_input(
    "Période",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)

if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date, end_date = min_date, max_date

filtered = df[
    (df["order_date"].dt.date >= start_date)
    & (df["order_date"].dt.date <= end_date)
].copy()

categories = sorted(
    filtered["category"].dropna().astype(str).unique().tolist()
)
regions = sorted(
    filtered["region"].dropna().astype(str).unique().tolist()
)
statuses = sorted(
    filtered["status"].dropna().astype(str).unique().tolist()
)

selected_categories = st.sidebar.multiselect(
    "Catégorie",
    categories,
    default=categories,
)

selected_regions = st.sidebar.multiselect(
    "Région",
    regions,
    default=regions,
)

selected_statuses = st.sidebar.multiselect(
    "Statut de commande",
    statuses,
    default=statuses,
)

filtered = filtered[
    filtered["category"].astype(str).isin(selected_categories)
    & filtered["region"].astype(str).isin(selected_regions)
    & filtered["status"].astype(str).isin(selected_statuses)
].copy()

st.sidebar.divider()
st.sidebar.caption("NOVA · Business intelligence")


# =========================================================
# 8. INDICATEURS CLÉS
# =========================================================

revenue = filtered["revenue"].sum()
orders_count = filtered["order_id"].nunique()
customers_count = filtered["customer_id"].nunique()
units_sold = filtered["quantity"].sum()

average_order_value = (
    revenue / orders_count if orders_count else 0
)


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


col1, col2, col3, col4 = st.columns(4)

with col1:
    metric_card(
        "Total Revenue",
        f"{revenue:,.2f}",
        "Revenue in dataset currency",
    )

with col2:
    metric_card(
        "Total Orders",
        f"{orders_count:,}",
        "Unique order IDs",
    )

with col3:
    metric_card(
        "Unique Customers",
        f"{customers_count:,}",
        "Distinct customer IDs",
    )

with col4:
    metric_card(
        "Units Sold",
        f"{units_sold:,.0f}",
        f"Average order value: {average_order_value:,.2f}",
    )


# =========================================================
# 9. GRAPHIQUES
# =========================================================

st.markdown("## Sales Performance")
st.caption("Explore revenue trends and business performance.")

chart_left, chart_right = st.columns([1.6, 1])

with chart_left:
    monthly = (
        filtered.groupby("month", as_index=False)["revenue"]
        .sum()
        .sort_values("month")
    )

    fig_trend = px.line(
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

    fig_trend.update_traces(
        line=dict(color=ACCENT, width=3),
        marker=dict(size=7),
        fill="tozeroy",
        fillcolor="rgba(37,217,195,0.08)",
    )

    fig_trend.update_layout(
        template="plotly_dark",
        paper_bgcolor=PANEL,
        plot_bgcolor=PANEL,
        font=dict(color=TEXT),
        margin=dict(l=20, r=20, t=55, b=20),
        title_font_size=17,
        xaxis=dict(showgrid=False),
        yaxis=dict(gridcolor="#26364D"),
    )

    st.plotly_chart(fig_trend, use_container_width=True)

with chart_right:
    category_data = (
        filtered.groupby("category", as_index=False)["revenue"]
        .sum()
        .sort_values("revenue", ascending=False)
    )

    fig_category = px.pie(
        category_data,
        names="category",
        values="revenue",
        hole=0.65,
        title="Revenue by Category",
        color_discrete_sequence=[
            ACCENT, BLUE, "#A78BFA", "#F59E0B",
            "#F472B6", "#60A5FA",
        ],
    )

    fig_category.update_layout(
        template="plotly_dark",
        paper_bgcolor=PANEL,
        font=dict(color=TEXT),
        margin=dict(l=15, r=15, t=55, b=15),
        legend=dict(orientation="h", y=-0.12),
    )

    st.plotly_chart(fig_category, use_container_width=True)


# =========================================================
# 10. RÉPARTITION GÉOGRAPHIQUE
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
    fig_region = px.bar(
        region_data,
        x="region",
        y="revenue",
        color="revenue",
        title="Revenue by Region",
        labels={
            "region": "Region",
            "revenue": "Revenue",
        },
        color_continuous_scale=["#164E63", ACCENT],
    )

    fig_region.update_layout(
        template="plotly_dark",
        paper_bgcolor=PANEL,
        plot_bgcolor=PANEL,
        font=dict(color=TEXT),
        margin=dict(l=20, r=20, t=55, b=20),
        coloraxis_showscale=False,
        xaxis=dict(showgrid=False),
        yaxis=dict(gridcolor="#26364D"),
    )

    st.plotly_chart(fig_region, use_container_width=True)
else:
    st.info("Aucune donnée régionale pour les filtres sélectionnés.")


# =========================================================
# 11. TOP PRODUITS
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
    .head(10)
)

if not product_data.empty:
    fig_products = px.bar(
        product_data.sort_values("revenue"),
        x="revenue",
        y="product_name",
        orientation="h",
        title="Top 10 Products by Revenue",
        labels={
            "revenue": "Revenue",
            "product_name": "Product",
        },
        color="revenue",
        color_continuous_scale=["#164E63", ACCENT],
    )

    fig_products.update_layout(
        template="plotly_dark",
        paper_bgcolor=PANEL,
        plot_bgcolor=PANEL,
        font=dict(color=TEXT),
        margin=dict(l=20, r=20, t=55, b=20),
        coloraxis_showscale=False,
        yaxis=dict(showgrid=False),
        xaxis=dict(gridcolor="#26364D"),
    )

    st.plotly_chart(fig_products, use_container_width=True)


# =========================================================
# 12. TABLEAU DE DONNÉES
# =========================================================

with st.expander("View filtered order data"):
    st.dataframe(
        filtered,
        use_container_width=True,
        hide_index=True,
    )

    csv_data = filtered.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="Download CSV",
        data=csv_data,
        file_name="nova_ecommerce_analytics.csv",
        mime="text/csv",
    )


# =========================================================
# 13. FOOTER
# =========================================================

st.markdown(
    """
    <div style="
        text-align:center;
        padding:28px 0 10px 0;
        color:#91A1B7;
        font-size:12px;
        border-top:1px solid #24334A;
        margin-top:30px;
    ">
        NOVA | E-Commerce Analytics · Interactive Business Intelligence
    </div>
    """,
    unsafe_allow_html=True,
)
