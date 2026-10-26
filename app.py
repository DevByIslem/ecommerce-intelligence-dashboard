
import sqlite3
from pathlib import Path
from html import escape

import pandas as pd
import plotly.express as px
import streamlit as st

# ============================================================
# NEXUS COMMERCE INTELLIGENCE
# Premium Dark | Navy + Turquoise
# SQLite | Pandas | Plotly | Streamlit
# ============================================================

st.set_page_config(
    page_title="NEXUS | Commerce Intelligence",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ------------------------- THEME -----------------------------

BG = "#08111F"
SIDEBAR = "#0B1728"
PANEL = "#101F32"
PANEL_ALT = "#14263B"
BORDER = "#263A50"
TEXT = "#F3F7FC"
MUTED = "#93A8BE"
TEAL = "#42E8C4"
BLUE = "#70A7FF"
PURPLE = "#B59AFF"
AMBER = "#FFC76A"
RED = "#FF8297"

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "data" / "ecommerce.db"

# ------------------------- DESIGN ---------------------------

st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');

    :root {{
        --bg: {BG};
        --panel: {PANEL};
        --border: {BORDER};
        --text: {TEXT};
        --muted: {MUTED};
        --teal: {TEAL};
    }}

    html, body, [class*="css"] {{
        font-family: 'DM Sans', sans-serif;
    }}

    .stApp {{
        color: var(--text);
        background:
            radial-gradient(ellipse at 80% -10%,
            rgba(66,232,196,.10), transparent 34%),
            {BG};
    }}

    [data-testid="stHeader"] {{
        background: rgba(8,17,31,.88);
    }}

    [data-testid="stSidebar"] {{
        background: {SIDEBAR};
        border-right: 1px solid {BORDER};
    }}

    .block-container {{
        max-width: 1500px;
        padding-top: 1.4rem;
        padding-bottom: 2.5rem;
    }}

    h1, h2, h3, h4 {{
        font-family: 'Manrope', sans-serif;
        color: {TEXT};
        letter-spacing: -.5px;
    }}

    p, label {{
        color: {TEXT};
    }}

    [data-testid="stMetric"] {{
        background: linear-gradient(145deg, {PANEL_ALT}, {PANEL});
        border: 1px solid {BORDER};
        border-radius: 16px;
        padding: 16px 18px;
        min-height: 112px;
    }}

    [data-testid="stMetricLabel"] p {{
        color: {MUTED} !important;
        font-size: 10px !important;
        font-weight: 700;
        letter-spacing: 1.15px;
        text-transform: uppercase;
    }}

    [data-testid="stMetricValue"] {{
        color: {TEXT} !important;
        font-family: 'Manrope', sans-serif;
        font-weight: 800;
    }}

    [data-testid="stMetricDelta"] {{
        font-size: 12px;
    }}

    .brand {{
        display: flex;
        align-items: center;
        gap: 11px;
        padding: 5px 0 18px;
    }}

    .brand-mark {{
        width: 41px;
        height: 41px;
        border-radius: 13px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: linear-gradient(135deg, {TEAL}, #8AF5DB);
        color: {BG};
        font-size: 22px;
        font-weight: 900;
        box-shadow: 0 8px 24px rgba(66,232,196,.16);
    }}

    .brand-name {{
        color: {TEXT};
        font: 800 18px 'Manrope', sans-serif;
        letter-spacing: -.5px;
    }}

    .brand-sub {{
        color: {MUTED};
        font-size: 9px;
        letter-spacing: 1.7px;
        text-transform: uppercase;
    }}

    .hero {{
        border: 1px solid {BORDER};
        border-radius: 22px;
        padding: 27px 29px;
        margin-bottom: 22px;
        background:
            radial-gradient(circle at 85% 15%,
                rgba(66,232,196,.16), transparent 28%),
            radial-gradient(circle at 100% 100%,
                rgba(112,167,255,.10), transparent 34%),
            linear-gradient(125deg, #12243A, #0D1B2B 65%, #102A35);
    }}

    .hero-eyebrow {{
        color: {TEAL};
        font-size: 10px;
        font-weight: 800;
        letter-spacing: 2px;
        text-transform: uppercase;
    }}

    .hero-title {{
        margin-top: 14px;
        color: {TEXT};
        font: 800 clamp(28px, 3.2vw, 41px)/1.2 'Manrope', sans-serif;
        letter-spacing: -1.3px;
    }}

    .hero-title span {{
        color: {TEAL};
    }}

    .hero-copy {{
        max-width: 780px;
        margin-top: 12px;
        color: {MUTED};
        font-size: 13px;
        line-height: 1.8;
    }}

    .chips {{
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-top: 18px;
    }}

    .chip {{
        display: inline-block;
        padding: 6px 10px;
        border: 1px solid #30465D;
        border-radius: 999px;
        background: rgba(7,17,30,.32);
        color: #D0DCE9;
        font-size: 10px;
        font-weight: 600;
    }}

    .eyebrow {{
        margin: 26px 0 5px;
        color: {TEAL};
        font-size: 10px;
        font-weight: 800;
        letter-spacing: 2px;
        text-transform: uppercase;
    }}

    .section-heading {{
        margin-bottom: 4px;
        color: {TEXT};
        font: 700 21px 'Manrope', sans-serif;
        letter-spacing: -.5px;
    }}

    .section-note {{
        margin-bottom: 15px;
        color: {MUTED};
        font-size: 12px;
        line-height: 1.6;
    }}

    .insight-card {{
        min-height: 139px;
        padding: 17px 18px;
        border: 1px solid {BORDER};
        border-radius: 15px;
        background: linear-gradient(145deg, {PANEL_ALT}, {PANEL});
    }}

    .insight-label {{
        font-size: 10px;
        font-weight: 800;
        letter-spacing: 1.4px;
        text-transform: uppercase;
    }}

    .insight-value {{
        margin-top: 10px;
        color: {TEXT};
        font: 800 20px 'Manrope', sans-serif;
        overflow-wrap: anywhere;
    }}

    .insight-description {{
        margin-top: 7px;
        color: {MUTED};
        font-size: 11px;
        line-height: 1.7;
    }}

    div[data-testid="stPlotlyChart"] {{
        padding: 5px;
        border: 1px solid {BORDER};
        border-radius: 16px;
        background: {PANEL};
    }}

    div[data-testid="stDataFrame"] {{
        overflow: hidden;
        border: 1px solid {BORDER};
        border-radius: 12px;
    }}

    .stDownloadButton button {{
        border: 1px solid {TEAL} !important;
        border-radius: 10px !important;
        background: rgba(66,232,196,.08) !important;
        color: {TEAL} !important;
        font-weight: 700 !important;
    }}

    .stDownloadButton button:hover {{
        background: rgba(66,232,196,.17) !important;
        color: {TEXT} !important;
    }}

    div[data-testid="stExpander"] {{
        border: 1px solid {BORDER};
        border-radius: 12px;
        background: rgba(16,31,50,.55);
    }}

    .footer {{
        margin-top: 35px;
        padding-top: 17px;
        border-top: 1px solid {BORDER};
        color: {MUTED};
        font-size: 10px;
        line-height: 1.9;
        text-align: center;
    }}

    </style>
    """,
    unsafe_allow_html=True,
)

# ------------------------- DATA -----------------------------

@st.cache_data
def load_data(db_path: str, modified_time: float) -> pd.DataFrame:
    """Load delivered orders from the existing SQLite database."""
    del modified_time  # Included in the cache key to refresh when DB changes.

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

    for column in ["quantity", "unit_price", "discount", "revenue"]:
        data[column] = pd.to_numeric(
            data[column], errors="coerce"
        ).fillna(0)

    for column in ["product_name", "category", "region"]:
        data[column] = data[column].fillna("Unknown").astype(str)

    data = data.dropna(subset=["order_date"]).copy()
    return data


if not DB_PATH.exists():
    st.error(f"Database not found: `{DB_PATH}`")
    st.info(
        "Vérifie que le fichier SQLite existe dans le dossier "
        "`data/ecommerce.db`."
    )
    st.stop()

try:
    df = load_data(str(DB_PATH), DB_PATH.stat().st_mtime)
except Exception as exc:
    st.error(f"Impossible de charger la base SQLite : {exc}")
    st.info(
        "Vérifie le nom de la table et les colonnes utilisées "
        "dans la requête SQL."
    )
    st.stop()

if df.empty:
    st.warning("Aucune commande livrée n'a été trouvée dans la base.")
    st.stop()

# ------------------------- SIDEBAR --------------------------

with st.sidebar:
    st.markdown(
        f"""
        <div class="brand">
            <div class="brand-mark">N</div>
            <div>
                <div class="brand-name">NEXUS</div>
                <div class="brand-sub">Commerce Intelligence</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("---")
    st.markdown("##### CONTROL CENTER")
    st.caption("Affinez les données affichées.")

    all_regions = sorted(df["region"].unique().tolist())
    all_categories = sorted(df["category"].unique().tolist())

    selected_regions = st.multiselect(
        "🌍 Regions",
        options=all_regions,
        default=all_regions,
    )

    selected_categories = st.multiselect(
        "▦ Categories",
        options=all_categories,
        default=all_categories,
    )

    min_date = df["order_date"].min().date()
    max_date = df["order_date"].max().date()

    date_range = st.date_input(
        "◷ Analysis period",
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

    st.markdown("---")
    st.markdown("##### DATA STATUS")

    st.markdown(
        f"<span style='color:{TEAL};font-size:11px;font-weight:700'>"
        "● Connected</span>",
        unsafe_allow_html=True,
    )
    st.caption("Source · SQLite")
    st.caption("Order status · Delivered")
    st.caption("Dataset · Existing project database")

    if st.button("↻ Refresh dashboard", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    st.markdown("---")
    st.caption("Python · Pandas · Plotly · Streamlit")

# ------------------------- FILTERS --------------------------

filtered = df[
    df["region"].isin(selected_regions)
    & df["category"].isin(selected_categories)
    & (df["order_date"].dt.date >= start_date)
    & (df["order_date"].dt.date <= end_date)
].copy()

if filtered.empty:
    st.markdown(
        f"""
        <div class="hero">
            <div class="hero-eyebrow">NEXUS / COMMERCE INTELLIGENCE</div>
            <div class="hero-title">No results <span>found.</span></div>
            <div class="hero-copy">
                Aucune commande ne correspond à cette sélection.
                Modifie la période, les régions ou les catégories.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.stop()

# ------------------------- KPI ------------------------------

total_revenue = float(filtered["revenue"].sum())
total_orders = int(filtered["order_id"].nunique())
unique_customers = int(filtered["customer_id"].nunique())
total_units = float(filtered["quantity"].sum())

average_order_value = (
    total_revenue / total_orders if total_orders else 0
)

quantity_for_discount = float(filtered["quantity"].sum())

weighted_discount = (
    float(
        (filtered["discount"] * filtered["quantity"]).sum()
        / quantity_for_discount
    )
    if quantity_for_discount > 0
    else 0
)

# Compare with the immediately preceding period of equal duration.
current_start = pd.Timestamp(start_date).normalize()
current_end = pd.Timestamp(end_date).normalize()
period_days = (current_end - current_start).days + 1

previous_start = current_start - pd.Timedelta(days=period_days)
previous_end = current_start - pd.Timedelta(days=1)

previous_period = df[
    df["region"].isin(selected_regions)
    & df["category"].isin(selected_categories)
    & (df["order_date"].dt.normalize() >= previous_start)
    & (df["order_date"].dt.normalize() <= previous_end)
].copy()

previous_revenue = float(previous_period["revenue"].sum())

revenue_growth = (
    (total_revenue - previous_revenue) / previous_revenue * 100
    if previous_revenue > 0
    else None
)

# ------------------------- HERO -----------------------------

st.markdown(
    f"""
    <div class="hero">
        <div class="hero-eyebrow">
            ◉ &nbsp; Business Intelligence / Performance Monitor
        </div>
        <div class="hero-title">Commerce, <span>decoded.</span></div>
        <div class="hero-copy">
            A clear view of e-commerce performance. Track revenue,
            understand customer activity, compare category and regional
            results, and uncover business signals through interactive analytics.
        </div>
        <div class="chips">
            <span class="chip">✦ Executive overview</span>
            <span class="chip">◷ {start_date:%d %b %Y} — {end_date:%d %b %Y}</span>
            <span class="chip">▤ Delivered orders only</span>
            <span class="chip">⌘ Interactive analytics</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ------------------------- OVERVIEW -------------------------

st.markdown(
    '<div class="eyebrow">01 / EXECUTIVE OVERVIEW</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="section-heading">Performance at a glance</div>',
    unsafe_allow_html=True,
)
st.markdown(
    f'<div class="section-note">Showing {len(filtered):,} records '
    f'across {len(selected_regions)} region(s) and '
    f'{len(selected_categories)} categor(y/ies).</div>',
    unsafe_allow_html=True,
)

k1, k2, k3, k4 = st.columns(4)

k1.metric(
    "Total revenue",
    f"{total_revenue:,.2f}",
    help="Somme du revenu pour la sélection actuelle.",
)
k2.metric(
    "Delivered orders",
    f"{total_orders:,}",
    help="Nombre de commandes distinctes.",
)
k3.metric(
    "Unique customers",
    f"{unique_customers:,}",
    help="Nombre de clients distincts.",
)
k4.metric(
    "Average order value",
    f"{average_order_value:,.2f}",
    help="Revenu total divisé par le nombre de commandes distinctes.",
)

m1, m2, m3 = st.columns(3)

m1.metric("Units sold", f"{total_units:,.0f}")
m2.metric("Weighted average discount", f"{weighted_discount * 100:.1f}%")

m3.metric(
    "Revenue vs previous period",
    f"{revenue_growth:+.1f}%" if revenue_growth is not None else "N/A",
    help=(
        "Compare la période sélectionnée à la période immédiatement "
        "précédente de même durée, avec les mêmes filtres région/catégorie."
    ),
)

# ------------------------- CHART THEME ----------------------

chart_layout = dict(
    paper_bgcolor=PANEL,
    plot_bgcolor=PANEL,
    font=dict(
        family="DM Sans, sans-serif",
        color=TEXT,
        size=11,
    ),
    margin=dict(l=18, r=22, t=38, b=20),
    xaxis=dict(
        showgrid=False,
        zeroline=False,
        linecolor=BORDER,
        tickfont=dict(color=MUTED),
    ),
    yaxis=dict(
        showgrid=True,
        gridcolor="#20334A",
        zeroline=False,
        linecolor=BORDER,
        tickfont=dict(color=MUTED),
    ),
)

# ------------------------- REVENUE --------------------------

st.markdown(
    '<div class="eyebrow">02 / REVENUE ANALYTICS</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="section-heading">Follow the money</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="section-note">Monthly revenue trends and category contribution.</div>',
    unsafe_allow_html=True,
)

monthly = (
    filtered.assign(
        month=filtered["order_date"].dt.to_period("M").dt.to_timestamp()
    )
    .groupby("month", as_index=False)
    .agg(
        revenue=("revenue", "sum"),
        orders=("order_id", "nunique"),
    )
    .sort_values("month")
)

category_revenue = (
    filtered.groupby("category", as_index=False)
    .agg(revenue=("revenue", "sum"))
    .sort_values("revenue", ascending=False)
)

left, right = st.columns([1.55, 1])

with left:
    fig_monthly = px.area(
        monthly,
        x="month",
        y="revenue",
        markers=True,
        custom_data=["orders"],
    )

    fig_monthly.update_traces(
        line=dict(color=TEAL, width=3),
        marker=dict(
            size=6,
            color=TEAL,
            line=dict(color=BG, width=1),
        ),
        fillcolor="rgba(66,232,196,0.13)",
        hovertemplate=(
            "<b>%{x|%B %Y}</b><br>"
            "Revenue: %{y:,.2f}<br>"
            "Orders: %{customdata[0]:,.0f}"
            "<extra></extra>"
        ),
    )

    fig_monthly.update_layout(
        **chart_layout,
        height=350,
        xaxis_title="",
        yaxis_title="Revenue",
        showlegend=False,
    )

    st.plotly_chart(
        fig_monthly,
        use_container_width=True,
        config={"displayModeBar": False},
    )

with right:
    fig_donut = px.pie(
        category_revenue,
        names="category",
        values="revenue",
        hole=0.70,
        color_discrete_sequence=[
            TEAL, BLUE, PURPLE, AMBER,
            "#FF8D9B", "#7DD3FC", "#A3E635",
        ],
    )

    fig_donut.update_traces(
        textposition="inside",
        textinfo="percent",
        textfont=dict(color=TEXT, size=10),
        hovertemplate=(
            "<b>%{label}</b><br>"
            "Revenue: %{value:,.2f}<br>"
            "Share: %{percent}"
            "<extra></extra>"
        ),
        marker=dict(line=dict(color=PANEL, width=3)),
    )

    fig_donut.update_layout(
        **chart_layout,
        height=350,
        showlegend=True,
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            font=dict(color=MUTED, size=10),
            orientation="h",
            yanchor="bottom",
            y=-0.12,
            xanchor="center",
            x=0.5,
        ),
    )

    fig_donut.add_annotation(
        text=(
            f"<b>{total_revenue:,.0f}</b>"
            "<br><span style='font-size:10px'>TOTAL REVENUE</span>"
        ),
        x=0.5,
        y=0.5,
        showarrow=False,
        font=dict(family="Manrope", size=17, color=TEXT),
    )

    st.plotly_chart(
        fig_donut,
        use_container_width=True,
        config={"displayModeBar": False},
    )

# ------------------------- BREAKDOWN -----------------------

st.markdown(
    '<div class="eyebrow">03 / PERFORMANCE BREAKDOWN</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="section-heading">Where results happen</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="section-note">Compare revenue contribution by category and region.</div>',
    unsafe_allow_html=True,
)

c1, c2 = st.columns(2)

with c1:
    cat_chart = category_revenue.sort_values("revenue", ascending=True)

    fig_category = px.bar(
        cat_chart,
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
        hovertemplate="<b>%{y}</b><br>Revenue: %{x:,.2f}<extra></extra>",
    )

    fig_category.update_layout(
        **chart_layout,
        height=330,
        xaxis_title="Revenue",
        yaxis_title="",
        showlegend=False,
    )

    st.plotly_chart(
        fig_category,
        use_container_width=True,
        config={"displayModeBar": False},
    )

with c2:
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
        hovertemplate="<b>%{y}</b><br>Revenue: %{x:,.2f}<extra></extra>",
    )

    fig_region.update_layout(
        **chart_layout,
        height=330,
        xaxis_title="Revenue",
        yaxis_title="",
        showlegend=False,
    )

    st.plotly_chart(
        fig_region,
        use_container_width=True,
        config={"displayModeBar": False},
    )

# ------------------------- INSIGHTS ------------------------

st.markdown(
    '<div class="eyebrow">04 / INTELLIGENCE LAYER</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="section-heading">Signals worth noticing</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="section-note">Insights calculated from the filtered dataset.</div>',
    unsafe_allow_html=True,
)

category_rank = category_revenue.sort_values("revenue", ascending=False)
region_rank = region_revenue.sort_values("revenue", ascending=False)
monthly_rank = monthly.sort_values("month")

best_category = category_rank.iloc[0]
best_region = region_rank.iloc[0]
best_month = monthly_rank.loc[monthly_rank["revenue"].idxmax()]

category_share = (
    best_category["revenue"] / total_revenue * 100
    if total_revenue else 0
)
region_share = (
    best_region["revenue"] / total_revenue * 100
    if total_revenue else 0
)

# Compare the last two months present in the selected data.
if len(monthly_rank) >= 2:
    last_month = monthly_rank.iloc[-1]
    previous_month = monthly_rank.iloc[-2]

    if previous_month["revenue"] > 0:
        monthly_change = (
            (last_month["revenue"] - previous_month["revenue"])
            / previous_month["revenue"] * 100
        )

        if monthly_change < 0:
            signal_color = RED
            signal_title = "MONTHLY REVENUE DECLINE"
            signal_text = (
                f"Revenue decreased by {abs(monthly_change):.1f}% "
                f"from {previous_month['month']:%b %Y} "
                f"to {last_month['month']:%b %Y}."
            )
        elif monthly_change > 0:
            signal_color = TEAL
            signal_title = "MONTHLY REVENUE INCREASE"
            signal_text = (
                f"Revenue increased by {monthly_change:.1f}% "
                f"from {previous_month['month']:%b %Y} "
                f"to {last_month['month']:%b %Y}."
            )
        else:
            signal_color = AMBER
            signal_title = "MONTHLY REVENUE STABLE"
            signal_text = (
                "Revenue was unchanged between the last two "
                "months in the selected data."
            )
    else:
        signal_color = AMBER
        signal_title = "MONTHLY COMPARISON"
        signal_text = (
            "The previous month had zero revenue; percentage "
            "change cannot be calculated."
        )
else:
    signal_color = AMBER
    signal_title = "MORE DATA NEEDED"
    signal_text = (
        "At least two months are needed to compare monthly revenue."
    )

ins1, ins2, ins3 = st.columns(3)

with ins1:
    st.markdown(
        f"""
        <div class="insight-card">
            <div class="insight-label" style="color:{TEAL}">
                TOP CATEGORY
            </div>
            <div class="insight-value">
                {escape(str(best_category['category']))}
            </div>
            <div class="insight-description">
                Revenue: {best_category['revenue']:,.2f}<br>
                {category_share:.1f}% of filtered revenue.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with ins2:
    st.markdown(
        f"""
        <div class="insight-card">
            <div class="insight-label" style="color:{BLUE}">
                TOP REGION
            </div>
            <div class="insight-value">
                {escape(str(best_region['region']))}
            </div>
            <div class="insight-description">
                Revenue: {best_region['revenue']:,.2f}<br>
                {region_share:.1f}% of filtered revenue.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with ins3:
    st.markdown(
        f"""
        <div class="insight-card">
            <div class="insight-label" style="color:{signal_color}">
                {signal_title}
            </div>
            <div class="insight-value">
                {best_month['month']:%B %Y}
            </div>
            <div class="insight-description">
                Peak month: {best_month['revenue']:,.2f}<br>
                {escape(signal_text)}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ------------------------- TOP PRODUCTS --------------------

st.markdown(
    '<div class="eyebrow">05 / PRODUCT INTELLIGENCE</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="section-heading">Products leading performance</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="section-note">Top 10 products ranked by revenue, with '
    'units sold and distinct orders for context.</div>',
    unsafe_allow_html=True,
)

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

# ------------------------- DATA EXPLORER -------------------

st.markdown(
    '<div class="eyebrow">06 / DATA EXPLORER</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="section-heading">Explore the underlying records</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="section-note">Inspect and export the records that match '
    'your current filters.</div>',
    unsafe_allow_html=True,
)

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
display_df["order_date"] = display_df["order_date"].dt.strftime("%Y-%m-%d")

with st.expander("Open filtered transaction table"):
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
    )

# Export the filtered dataset, including all source columns.
csv_data = filtered.to_csv(index=False).encode("utf-8-sig")

st.download_button(
    label="↓  Export filtered data (CSV)",
    data=csv_data,
    file_name="nexus_commerce_filtered_data.csv",
    mime="text/csv",
)

# ------------------------- FOOTER --------------------------

st.markdown(
    f"""
    <div class="footer">
        <b style="color:{TEXT}">NEXUS COMMERCE INTELLIGENCE</b><br>
        Portfolio project · Python · SQLite · Pandas · Plotly · Streamlit<br>
        Metrics reflect the current filter selection and existing database.
    </div>
    """,
    unsafe_allow_html=True,
)
