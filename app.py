import os
import re
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Optional Gemini SDK
try:
    from google import genai
except Exception:
    genai = None


# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="Superstore AI",
    page_icon="🌌",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# CONSTANTS
# ============================================================
BASE_DIR = Path(__file__).resolve().parent
DEFAULT_CSV = BASE_DIR / "Sample - Superstore.csv"

MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-3-flash-preview")
API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY".upper())

if not API_KEY:
    # If the user already exported GEMINI_API_KEY in PowerShell,
    # this will pick it up. Otherwise they can enter it in the sidebar.
    API_KEY = st.session_state.get("gemini_key", "")


# ============================================================
# GLOBAL CSS
# ============================================================
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

:root {
    --bg: #050816;
    --panel: rgba(12, 20, 43, 0.82);
    --panel2: rgba(15, 27, 55, 0.88);
    --line: rgba(122, 166, 255, 0.20);
    --text: #f5f7ff;
    --muted: #8ea2c8;
    --cyan: #42d9ff;
    --blue: #5b7cff;
    --purple: #a77bff;
    --green: #48e6a1;
    --pink: #ff6ec7;
}

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background:
        radial-gradient(circle at 80% 10%, rgba(74, 105, 255, 0.16), transparent 28%),
        radial-gradient(circle at 15% 80%, rgba(168, 82, 255, 0.12), transparent 30%),
        linear-gradient(135deg, #03050e 0%, #071027 48%, #030612 100%);
    color: var(--text);
}

/* Hide Streamlit chrome */
#MainMenu, footer {visibility: hidden;}
header[data-testid="stHeader"] {background: transparent;}

/* Sidebar */
section[data-testid="stSidebar"] {
    background:
        radial-gradient(circle at 50% 0%, rgba(77, 112, 255, 0.16), transparent 30%),
        linear-gradient(180deg, #060a19 0%, #03050d 100%);
    border-right: 1px solid rgba(100, 150, 255, 0.15);
}

.sidebar-brand {
    padding: 12px 4px 25px 4px;
}

.brand-row {
    display: flex;
    align-items: center;
    gap: 11px;
}

.brand-orbit {
    width: 38px;
    height: 38px;
    border-radius: 12px;
    background: linear-gradient(135deg, #35d7ff, #6c63ff);
    box-shadow: 0 0 25px rgba(55, 190, 255, .35);
    position: relative;
}

.brand-orbit:after {
    content: "";
    position: absolute;
    width: 18px;
    height: 18px;
    border: 2px solid white;
    border-radius: 50%;
    top: 8px;
    left: 8px;
    opacity: .85;
}

.brand-name {
    font-size: 22px;
    font-weight: 800;
    color: white;
}

.brand-sub {
    color: #7184aa;
    font-size: 11px;
    margin-top: 5px;
}

.nav-title {
    color: #60739b;
    letter-spacing: 2px;
    font-size: 10px;
    font-weight: 700;
    margin: 24px 0 8px 4px;
}

.system-card {
    margin-top: 20px;
    padding: 14px;
    border: 1px solid rgba(90, 170, 255, .15);
    border-radius: 16px;
    background: rgba(12, 22, 45, .55);
}

.system-line {
    display: flex;
    align-items: center;
    gap: 9px;
    color: #cbd7f2;
    font-size: 12px;
    margin: 9px 0;
}

.dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    display: inline-block;
    box-shadow: 0 0 12px currentColor;
}
.dot.green {color: #48e6a1; background: #48e6a1;}
.dot.blue {color: #42d9ff; background: #42d9ff;}
.dot.purple {color: #a77bff; background: #a77bff;}

/* Hero */
.hero {
    min-height: 330px;
    position: relative;
    overflow: hidden;
    border: 1px solid rgba(112, 170, 255, .25);
    border-radius: 28px;
    padding: 58px 58px;
    background:
        radial-gradient(circle at 82% 24%, rgba(72, 217, 255, .22), transparent 20%),
        radial-gradient(circle at 70% 75%, rgba(139, 86, 255, .20), transparent 27%),
        linear-gradient(135deg, rgba(10, 20, 48, .96), rgba(6, 12, 31, .88));
    box-shadow: 0 25px 80px rgba(0,0,0,.40);
}

.hero:before,
.hero:after {
    content: "";
    position: absolute;
    border-radius: 50%;
    pointer-events: none;
}

.hero:before {
    width: 220px;
    height: 220px;
    right: 80px;
    top: 45px;
    background: radial-gradient(circle at 35% 30%, #78e9ff, #3865ff 48%, #19144c 72%);
    box-shadow: 0 0 70px rgba(54, 177, 255, .35);
    opacity: .85;
}

.hero:after {
    width: 330px;
    height: 90px;
    right: 15px;
    top: 110px;
    border: 2px solid rgba(150, 190, 255, .35);
    transform: rotate(-20deg);
    box-shadow: 0 0 18px rgba(100, 180, 255, .15);
}

.space-star {
    position: absolute;
    width: 4px;
    height: 4px;
    border-radius: 50%;
    background: white;
    box-shadow: 0 0 10px white;
    opacity: .7;
}

.star1 {left: 8%; top: 20%;}
.star2 {left: 28%; top: 13%;}
.star3 {left: 43%; top: 72%;}
.star4 {left: 58%; top: 18%;}
.star5 {left: 73%; top: 76%;}
.star6 {right: 6%; top: 38%;}

.hero-content {
    position: relative;
    z-index: 5;
    max-width: 720px;
}

.hero-kicker {
    color: #7fe7ff;
    letter-spacing: 2.5px;
    font-size: 12px;
    font-weight: 800;
    margin-bottom: 16px;
}

.hero-title {
    font-size: clamp(34px, 4.2vw, 58px);
    line-height: 1.02;
    font-weight: 800;
    letter-spacing: -2px;
    background: linear-gradient(90deg, #fff, #a9eaff 55%, #a88cff);
    -webkit-background-clip: text;
    color: transparent;
}

.hero-description {
    color: #aebbd5;
    font-size: 16px;
    line-height: 1.8;
    max-width: 650px;
    margin-top: 20px;
}

.hero-status {
    display: inline-flex;
    align-items: center;
    gap: 9px;
    margin-top: 25px;
    padding: 10px 16px;
    border-radius: 999px;
    border: 1px solid rgba(72,230,161,.35);
    background: rgba(72,230,161,.08);
    color: #8ff2c3;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 1px;
}

.status-dot {
    width: 8px;
    height: 8px;
    background: #48e6a1;
    border-radius: 50%;
    box-shadow: 0 0 14px #48e6a1;
}

/* Section headings */
.section-header {
    margin: 34px 0 18px;
}

.section-title {
    color: white;
    font-size: 25px;
    font-weight: 800;
}

.section-subtitle {
    color: #7186ad;
    font-size: 12px;
    margin-top: 5px;
}

/* KPI */
.kpi-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
    margin-bottom: 28px;
}

.kpi-card {
    min-height: 155px;
    padding: 22px;
    border-radius: 20px;
    border: 1px solid rgba(111, 163, 255, .18);
    background:
        linear-gradient(145deg, rgba(20, 32, 67, .92), rgba(7, 14, 31, .92));
    box-shadow: 0 15px 35px rgba(0,0,0,.28);
    transition: .25s ease;
}

.kpi-card:hover {
    transform: translateY(-5px);
    border-color: rgba(66,217,255,.48);
    box-shadow: 0 20px 45px rgba(0,170,255,.13);
}

.kpi-top {
    display: flex;
    align-items: center;
    gap: 10px;
}

.kpi-icon {font-size: 22px;}
.kpi-label {
    color: #7e94ba;
    font-size: 10px;
    letter-spacing: 1.5px;
    font-weight: 800;
}
.kpi-value {
    color: white;
    font-size: 30px;
    font-weight: 800;
    margin-top: 16px;
}
.kpi-meta {
    color: #63779c;
    font-size: 11px;
    margin-top: 5px;
}

/* Glass panels */
.glass-panel {
    border: 1px solid rgba(105, 160, 255, .17);
    border-radius: 22px;
    background: rgba(10, 19, 40, .68);
    padding: 22px;
    box-shadow: 0 18px 45px rgba(0,0,0,.25);
}

.panel-title {
    color: white;
    font-size: 16px;
    font-weight: 800;
}

.panel-sub {
    color: #7186aa;
    font-size: 11px;
    margin-top: 4px;
}

/* Buttons */
.stButton > button {
    border-radius: 12px !important;
    border: 1px solid rgba(94, 171, 255, .28) !important;
    background: linear-gradient(135deg, rgba(30, 52, 101, .95), rgba(17, 29, 62, .95)) !important;
    color: #eaf4ff !important;
    font-weight: 700 !important;
    min-height: 42px !important;
    transition: .2s ease !important;
}

.stButton > button:hover {
    border-color: #42d9ff !important;
    box-shadow: 0 0 20px rgba(66,217,255,.16) !important;
    transform: translateY(-1px);
}

.analyze-btn button {
    background: linear-gradient(90deg, #267bff, #784dff) !important;
    border: none !important;
    box-shadow: 0 10px 30px rgba(86, 94, 255, .25) !important;
}

/* Inputs */
.stTextInput input,
.stTextArea textarea,
.stSelectbox div[data-baseweb="select"] > div,
.stMultiSelect div[data-baseweb="select"] > div {
    background: rgba(9, 17, 37, .86) !important;
    color: white !important;
    border-color: rgba(112, 163, 255, .20) !important;
    border-radius: 12px !important;
}

label {
    color: #9db0d2 !important;
}

/* Dataframe */
[data-testid="stDataFrame"] {
    border: 1px solid rgba(110,160,255,.15);
    border-radius: 16px;
    overflow: hidden;
}

/* Make Data Explorer metric labels and numbers clearly visible */
[data-testid="stMetric"] label,
[data-testid="stMetricLabel"] {
    color: #dbe7ff !important;
}

[data-testid="stMetricValue"] {
    color: #ffffff !important;
    opacity: 1 !important;
    font-weight: 800 !important;
}

[data-testid="stMetricDelta"] {
    color: #9fc8ff !important;
}

/* Keep select-box text readable on the dark space theme */
.stSelectbox [data-baseweb="select"] *,
.stMultiSelect [data-baseweb="select"] * {
    color: #ffffff !important;
}

.stSelectbox [data-baseweb="select"] input,
.stMultiSelect [data-baseweb="select"] input {
    color: #ffffff !important;
}

/* Plotly legend and chart text */
.js-plotly-plot .legendtext {
    fill: #ffffff !important;
}


/* --- Floating space objects behind the hero --- */
.hero {
    position: relative !important;
    overflow: hidden !important;
    min-height: 330px !important;
    isolation: isolate !important;
    padding: 42px 48px !important;
}

/* Keep hero content above the floating objects */
.hero > * {
    position: relative;
    z-index: 3;
}

.hero::before,
.hero::after {
    content: "";
    position: absolute;
    pointer-events: none;
    z-index: 1;
    border-radius: 50%;
    filter: blur(.2px);
    opacity: .75;
}

.hero::before {
    width: 128px;
    height: 128px;
    right: 10%;
    top: 20%;
    background:
        radial-gradient(circle at 35% 30%, rgba(255,255,255,.65) 0 2px, transparent 3px),
        radial-gradient(circle at 65% 60%, rgba(255,255,255,.35) 0 1.5px, transparent 2.5px),
        radial-gradient(circle at 50% 50%, #149ee8 0%, #0874c7 48%, #081b49 100%);
    box-shadow: 0 0 55px rgba(20,158,232,.45);
}

.hero::after {
    width: 95px;
    height: 95px;
    left: 7%;
    bottom: 8%;
    background:
        radial-gradient(circle at 30% 25%, rgba(255,255,255,.7) 0 2px, transparent 3px),
        radial-gradient(circle at 70% 65%, rgba(255,255,255,.35) 0 1px, transparent 2px),
        radial-gradient(circle, #684cff 0%, #29215f 62%, #0b1230 100%);
    box-shadow: 0 0 40px rgba(104,76,255,.35);
}

/* Orbit around the large floating planet */
.hero .hero-title::after {
    content: "";
    position: absolute;
    width: 155px;
    height: 46px;
    right: 8%;
    top: 40%;
    border: 2px solid rgba(110,220,255,.28);
    border-radius: 50%;
    transform: rotate(-18deg);
    pointer-events: none;
    z-index: 2;
}

/* Small stars */
.hero .hero-description::before {
    content: "✦   ·       ✧          ·   ✦       ·";
    position: absolute;
    right: 7%;
    top: 7%;
    color: rgba(170,225,255,.55);
    font-size: 18px;
    letter-spacing: 10px;
    pointer-events: none;
    z-index: 2;
}

@media (max-width: 900px) {
    .hero {
        min-height: 300px !important;
        padding: 34px 30px !important;
    }

    .hero::before {
        width: 110px;
        height: 110px;
        right: 5%;
    }

    .hero::after {
        width: 70px;
        height: 70px;
    }
}


/* Final chart readability fix */
.js-plotly-plot .xtick text,
.js-plotly-plot .ytick text,
.js-plotly-plot .axis-title,
.js-plotly-plot .legendtext,
.js-plotly-plot .gtitle {
    fill: #ffffff !important;
}

/* FINAL PLANET: contained planet + complete orbit ring */
.hero::before, .hero::after {
    content: none !important;
}
.hero-planet {
    position: absolute !important;
    z-index: 1 !important;
    width: 150px !important;
    height: 150px !important;
    right: 9% !important;
    top: 18% !important;
    border-radius: 50% !important;
    background:
        radial-gradient(circle at 30% 26%, rgba(180,245,255,.95) 0 2px, transparent 3px),
        radial-gradient(circle at 68% 62%, rgba(255,255,255,.30) 0 2px, transparent 3px),
        radial-gradient(circle at 42% 38%, #27d8ff 0%, #1499e6 42%, #3159d8 68%, #10184d 100%) !important;
    box-shadow: 0 0 65px rgba(32,190,255,.48), inset -18px -14px 35px rgba(4,15,60,.35) !important;
}
.planet-orbit-back, .planet-orbit-front {
    position: absolute !important;
    z-index: 2 !important;
    width: 218px !important;
    height: 62px !important;
    right: 6.5% !important;
    top: 34% !important;
    border: 2px solid rgba(151,226,255,.62) !important;
    border-radius: 50% !important;
    transform: rotate(-18deg) !important;
    pointer-events: none !important;
    box-shadow: 0 0 14px rgba(73,190,255,.16) !important;
}
.planet-orbit-back {
    clip-path: inset(0 0 53% 0) !important;
    opacity: .75 !important;
}
.planet-orbit-front {
    clip-path: inset(47% 0 0 0) !important;
    opacity: .95 !important;
}
.hero .hero-title::after { content: none !important; }
/* Absolute guarantee: Plotly must never render a chart title. */
.js-plotly-plot .gtitle, .js-plotly-plot .gtitle * {
    display: none !important;
}


/* FINAL DATA EXPLORER METRIC VISIBILITY */
[data-testid="stMetric"] [data-testid="stMetricValue"],
[data-testid="stMetricValue"] div,
[data-testid="stMetricValue"] p {
    color: #ffffff !important;
    opacity: 1 !important;
    -webkit-text-fill-color: #ffffff !important;
}

/* Responsive */
@media (max-width: 1000px) {
    .kpi-grid {grid-template-columns: repeat(2, 1fr);}
    .hero {padding: 40px 30px;}
    .hero:before, .hero:after {opacity: .25;}
}
</style>
""",
    unsafe_allow_html=True,
)


# ============================================================
# DATA LOADING
# ============================================================
@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    try:
        df = pd.read_csv(path, encoding="utf-8")
    except UnicodeDecodeError:
        df = pd.read_csv(path, encoding="cp1252")

    # Clean column names
    df.columns = [str(c).strip() for c in df.columns]

    # Convert common numeric columns
    for col in ["Sales", "Profit", "Quantity", "Discount"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Date handling
    for col in ["Order Date", "Ship Date"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    return df


# Find default dataset
if DEFAULT_CSV.exists():
    DATA_PATH = DEFAULT_CSV
else:
    csv_files = list(BASE_DIR.glob("*.csv"))
    DATA_PATH = csv_files[0] if csv_files else None


# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.markdown(
        """
        <div class="sidebar-brand">
            <div class="brand-row">
                <div class="brand-orbit"></div>
                <div class="brand-name">Superstore AI</div>
            </div>
            <div class="brand-sub">Intelligent Business Analytics</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="nav-title">NAVIGATION</div>', unsafe_allow_html=True)

    if "page" not in st.session_state:
        st.session_state.page = "Dashboard"

    if st.button("🏠  Dashboard", use_container_width=True):
        st.session_state.page = "Dashboard"
        st.rerun()

    if st.button("🤖  AI Analyst", use_container_width=True):
        st.session_state.page = "AI Analyst"
        st.rerun()

    if st.button("📊  Data Explorer", use_container_width=True):
        st.session_state.page = "Data Explorer"
        st.rerun()

    st.markdown(
        """
        <div class="system-card">
            <div class="nav-title" style="margin-top:0;">SYSTEM</div>
            <div class="system-line"><span class="dot green"></span> AI Engine · Gemini</div>
            <div class="system-line"><span class="dot blue"></span> Data Engine · Pandas</div>
            <div class="system-line"><span class="dot purple"></span> Knowledge · RAG</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="nav-title">GEMINI API</div>', unsafe_allow_html=True)

    key_input = st.text_input(
        "API key",
        value=st.session_state.get("gemini_key", API_KEY or ""),
        type="password",
        placeholder="Paste Gemini API key",
        label_visibility="collapsed",
    )

    if key_input:
        st.session_state.gemini_key = key_input

    if st.button("🔌 Test Gemini Connection", use_container_width=True):
        if not st.session_state.get("gemini_key"):
            st.warning("Enter your Gemini API key first.")
        elif genai is None:
            st.error("Install the Gemini SDK: pip install google-genai")
        else:
            try:
                client = genai.Client(api_key=st.session_state.gemini_key)
                response = client.models.generate_content(
                    model=MODEL_NAME,
                    contents="Reply with exactly: ONLINE",
                )
                st.success("Gemini connection is working.")
            except Exception as e:
                st.error(f"Gemini connection failed: {e}")

    st.markdown(
        """
        <div style="margin-top:25px;color:#5f7297;font-size:11px;line-height:1.7;">
        <b style="color:#90a5ca;">ABOUT</b><br><br>
        AI-powered Superstore analytics with natural-language questions,
        RAG-style context, interactive charts and business KPIs.
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# DATA CHECK
# ============================================================
if DATA_PATH is None:
    st.error(
        "No CSV dataset was found. Put your Superstore CSV in the same folder "
        "as app.py, preferably named 'Sample - Superstore.csv'."
    )
    st.stop()

df = load_data(str(DATA_PATH))

# Basic metrics
total_sales = float(df["Sales"].sum()) if "Sales" in df else 0
total_profit = float(df["Profit"].sum()) if "Profit" in df else 0
total_quantity = float(df["Quantity"].sum()) if "Quantity" in df else 0

if "Order ID" in df:
    total_orders = int(df["Order ID"].nunique())
else:
    total_orders = len(df)


# ============================================================
# HELPERS
# ============================================================
def build_context(question: str) -> str:
    """Create a compact RAG-style context from the dataset."""
    q = question.lower()
    parts = []

    numeric_cols = [c for c in ["Sales", "Profit", "Quantity", "Discount"] if c in df.columns]
    category_cols = [
        c for c in [
            "Region", "Category", "Sub-Category", "Segment",
            "State", "City", "Ship Mode", "Customer Name", "Product Name"
        ]
        if c in df.columns
    ]

    selected_categories = [
        c for c in category_cols
        if c.lower().replace("-", " ") in q
        or c.lower() in q
    ]

    # Add obvious groupings
    grouping_map = {
        "region": "Region",
        "category": "Category",
        "sub-category": "Sub-Category",
        "segment": "Segment",
        "state": "State",
        "ship mode": "Ship Mode",
    }

    group_col = None
    for word, col in grouping_map.items():
        if word in q and col in df.columns:
            group_col = col
            break

    if group_col:
        metric = "Sales" if "sales" in q else "Profit" if "profit" in q else "Quantity"
        if metric in df.columns:
            summary = (
                df.groupby(group_col)[metric]
                .sum()
                .sort_values(ascending=False)
                .head(15)
            )
            parts.append(f"{metric} by {group_col}:\n{summary.to_string()}")

    if "top" in q or "highest" in q or "best" in q:
        if "Product Name" in df.columns and "Sales" in df.columns:
            top_products = (
                df.groupby("Product Name")["Sales"]
                .sum()
                .sort_values(ascending=False)
                .head(10)
            )
            parts.append("Top products by sales:\n" + top_products.to_string())

    if "trend" in q or "over time" in q or "monthly" in q:
        if "Order Date" in df.columns and "Sales" in df.columns:
            temp = df.dropna(subset=["Order Date"]).copy()
            monthly = (
                temp.set_index("Order Date")
                .resample("ME")["Sales"]
                .sum()
                .tail(18)
            )
            parts.append("Recent monthly sales:\n" + monthly.to_string())

    # Dataset profile
    profile = {
        "rows": len(df),
        "columns": len(df.columns),
        "total_sales": round(total_sales, 2),
        "total_profit": round(total_profit, 2),
        "total_quantity": round(total_quantity, 2),
        "total_orders": total_orders,
        "numeric_columns": numeric_cols,
        "category_columns": category_cols,
    }
    parts.append("Dataset profile:\n" + str(profile))

    return "\n\n".join(parts)


def ask_gemini(question: str) -> str:
    key = st.session_state.get("gemini_key") or API_KEY

    if not key:
        return (
            "Gemini API key is not connected. Enter your key in the sidebar. "
            "The dashboard itself is working correctly."
        )

    if genai is None:
        return "The Gemini SDK is missing. Run: pip install google-genai"

    context = build_context(question)

    prompt = f"""
You are Superstore AI, a professional business analytics assistant.

Answer the user's question using ONLY the supplied dataset context.
Be concise but useful.
If calculations are present, report important values clearly.
If comparing categories, identify the highest and lowest where appropriate.
Do not invent data.

USER QUESTION:
{question}

DATASET / RAG CONTEXT:
{context}
"""

    try:
        client = genai.Client(api_key=key)
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
        )
        return response.text.strip()
    except Exception as e:
        return f"Gemini error: {e}"


def make_chart(question: str):
    q = question.lower()

    # Sales by region
    if "region" in q and "sales" in q and "Region" in df.columns:
        data = (
            df.groupby("Region", as_index=False)["Sales"]
            .sum()
            .sort_values("Sales", ascending=False)
        )
        fig = px.bar(
            data,
            x="Region",
            y="Sales",
            text_auto=".2s",
            template="plotly_dark",
        )
        return fig

    # Profit by category
    if "category" in q and "profit" in q and "Category" in df.columns:
        data = (
            df.groupby("Category", as_index=False)["Profit"]
            .sum()
            .sort_values("Profit", ascending=False)
        )
        fig = px.pie(
            data,
            names="Category",
            values="Profit",
            hole=.58,
            template="plotly_dark",
            color_discrete_sequence=[
                "#42d9ff",
                "#8b7cff",
                "#ff6ec7",
            ],
        )
        fig.update_traces(
            textinfo="percent+label",
            textfont=dict(color="#ffffff", size=13),
            marker=dict(
                line=dict(color="#071027", width=2)
            ),
        )
        fig.update_layout(
            legend=dict(font=dict(color="#ffffff", size=12)),
        )
        return fig

    # Sales trend
    if ("trend" in q or "over time" in q or "monthly" in q) and "Order Date" in df.columns:
        temp = df.dropna(subset=["Order Date"]).copy()
        monthly = (
            temp.set_index("Order Date")
            .resample("ME")["Sales"]
            .sum()
            .reset_index()
        )
        fig = px.line(
            monthly,
            x="Order Date",
            y="Sales",
            markers=True,
            template="plotly_dark",
        )
        return fig

    # Profit by sub-category
    if "sub" in q and "profit" in q and "Sub-Category" in df.columns:
        data = (
            df.groupby("Sub-Category", as_index=False)["Profit"]
            .sum()
            .sort_values("Profit", ascending=False)
        )
        fig = px.bar(
            data,
            x="Profit",
            y="Sub-Category",
            orientation="h",
            template="plotly_dark",
        )
        return fig

    return None



def clean_chart_text(value, fallback=""):
    """Return safe chart text; never allow None/undefined to reach the UI."""
    if value is None:
        return fallback
    value = str(value).strip()
    if value.lower() in {"undefined", "none", "nan"}:
        return fallback
    return value

def chart_style(fig):
    # Never allow Plotly to display an accidental "undefined" title.
    current_title = getattr(getattr(fig.layout, "title", None), "text", None)
    if current_title is None or str(current_title).strip().lower() == "undefined":
        fig.update_layout(title=None)

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#ffffff"),
        title_font=dict(size=18, color="#ffffff"),
        title=None,
        margin=dict(l=30, r=25, t=25, b=30),
        hoverlabel=dict(
            bgcolor="#0b1732",
            font_color="#ffffff",
        ),
        legend=dict(
            font=dict(color="#ffffff", size=12),
            title_font=dict(color="#ffffff"),
        ),
    )
    return fig


# ============================================================
# DASHBOARD
# ============================================================
if st.session_state.page == "Dashboard":

    st.html(
        """
        <div class="hero">
            <span class="planet-orbit-back"></span>
            <span class="hero-planet"></span>
            <span class="planet-orbit-front"></span>
            <span class="space-star star1"></span>
            <span class="space-star star2"></span>
            <span class="space-star star3"></span>
            <span class="space-star star4"></span>
            <span class="space-star star5"></span>
            <span class="space-star star6"></span>

            <div class="hero-content">
                <div class="hero-kicker">✦ AI-POWERED BUSINESS INTELLIGENCE</div>
                <div class="hero-title">Superstore AI Analyst</div>
                <div class="hero-description">
                    Explore your business data through natural language.
                    Discover patterns, compare performance and generate
                    intelligent insights using Gemini AI, RAG and advanced analytics.
                </div>
                <div class="hero-status">
                    <span class="status-dot"></span>
                    AI ANALYTICS ENGINE ONLINE
                </div>
            </div>
        </div>
        """
    )

    st.markdown(
        """
        <div class="section-header">
            <div class="section-title">Business Overview</div>
            <div class="section-subtitle">
                Live metrics calculated directly from your Superstore dataset
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # KPI cards — rendered with st.html so the HTML is NEVER shown as text.
    st.html(
        f"""
        <div class="kpi-grid">

            <div class="kpi-card">
                <div class="kpi-top">
                    <div class="kpi-icon">💰</div>
                    <div class="kpi-label">TOTAL SALES</div>
                </div>
                <div class="kpi-value">${total_sales:,.0f}</div>
                <div class="kpi-meta">Overall revenue</div>
            </div>

            <div class="kpi-card">
                <div class="kpi-top">
                    <div class="kpi-icon">📈</div>
                    <div class="kpi-label">TOTAL PROFIT</div>
                </div>
                <div class="kpi-value">${total_profit:,.0f}</div>
                <div class="kpi-meta">Net profit generated</div>
            </div>

            <div class="kpi-card">
                <div class="kpi-top">
                    <div class="kpi-icon">📦</div>
                    <div class="kpi-label">TOTAL QUANTITY</div>
                </div>
                <div class="kpi-value">{total_quantity:,.0f}</div>
                <div class="kpi-meta">Units sold</div>
            </div>

            <div class="kpi-card">
                <div class="kpi-top">
                    <div class="kpi-icon">🧾</div>
                    <div class="kpi-label">ORDERS</div>
                </div>
                <div class="kpi-value">{total_orders:,.0f}</div>
                <div class="kpi-meta">Unique orders</div>
            </div>

        </div>
        """
    )

    # Dashboard charts
    c1, c2 = st.columns(2)

    with c1:
        st.markdown(
            '<div class="panel-title">🌍 Sales by Region</div>'
            '<div class="panel-sub">Revenue distribution across regions</div>',
            unsafe_allow_html=True,
        )
        if "Region" in df.columns and "Sales" in df.columns:
            region_data = (
                df.groupby("Region", as_index=False)["Sales"]
                .sum()
                .sort_values("Sales", ascending=False)
            )
            fig = px.bar(
                region_data,
                x="Region",
                y="Sales",
                text_auto=".2s",
                template="plotly_dark",
                title=None,
            )
            fig.update_traces(
                marker=dict(
                    color="#35c8ff",
                    line=dict(color="#91eaff", width=1),
                )
            )
            st.plotly_chart(chart_style(fig), use_container_width=True)

    with c2:
        st.markdown(
            '<div class="panel-title">💎 Profit by Category</div>'
            '<div class="panel-sub">Profit contribution by category</div>',
            unsafe_allow_html=True,
        )
        if "Category" in df.columns and "Profit" in df.columns:
            cat_data = (
                df.groupby("Category", as_index=False)["Profit"]
                .sum()
            )
            fig = px.pie(
                cat_data,
                names="Category",
                values="Profit",
                hole=.60,
                template="plotly_dark",
                title=None,
                color_discrete_sequence=[
                    "#42d9ff",
                    "#8b7cff",
                    "#ff6ec7",
                ],
            )
            fig.update_traces(
                textinfo="percent+label",
                textfont=dict(color="#ffffff", size=13),
                marker=dict(
                    line=dict(color="#071027", width=2)
                ),
            )
            fig.update_layout(
                title=None,
                showlegend=True,
                legend=dict(
                    font=dict(color="#ffffff", size=12)
                ),
            )
            st.plotly_chart(chart_style(fig), use_container_width=True)

    # Sales trend
    if "Order Date" in df.columns and "Sales" in df.columns:
        st.markdown(
            '<div class="panel-title">🚀 Sales Trajectory</div>'
            '<div class="panel-sub">Monthly sales performance over time</div>',
            unsafe_allow_html=True,
        )

        trend = (
            df.dropna(subset=["Order Date"])
            .set_index("Order Date")
            .resample("ME")["Sales"]
            .sum()
            .reset_index()
        )

        fig = px.area(
            trend,
            x="Order Date",
            y="Sales",
            template="plotly_dark",
            title=None,
        )
        fig.update_traces(
            line=dict(color="#5b7cff", width=3),
            fillcolor="rgba(91,124,255,.16)",
        )
        st.plotly_chart(chart_style(fig), use_container_width=True)

    # Quick actions
    st.markdown(
        '<div class="section-header">'
        '<div class="section-title">Quick Analysis</div>'
        '<div class="section-subtitle">Jump directly into a business question</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    q1, q2, q3 = st.columns(3)

    with q1:
        if st.button("🌍 Highest Sales Region", use_container_width=True):
            st.session_state.page = "AI Analyst"
            st.session_state.question = "Which region had the highest sales?"
            st.rerun()

    with q2:
        if st.button("💰 Profit by Category", use_container_width=True):
            st.session_state.page = "AI Analyst"
            st.session_state.question = "What is the total profit by category?"
            st.rerun()

    with q3:
        if st.button("📈 Sales Trend", use_container_width=True):
            st.session_state.page = "AI Analyst"
            st.session_state.question = "Show sales trends over time."
            st.rerun()


# ============================================================
# AI ANALYST
# ============================================================
elif st.session_state.page == "AI Analyst":

    st.markdown(
        """
        <div class="section-header">
            <div class="section-title">🤖 AI Analyst</div>
            <div class="section-subtitle">
                Ask questions about your Superstore data in natural language
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if "question" not in st.session_state:
        st.session_state.question = ""

    question = st.text_area(
        "Your question",
        value=st.session_state.question,
        height=100,
        placeholder="Example: Which region had the highest sales?",
    )

    st.markdown("**Try a question**")

    e1, e2, e3, e4 = st.columns(4)

    examples = [
        "Which region had the highest sales?",
        "What is the total profit by category?",
        "Show sales trends over time.",
        "Which sub-category is most profitable?",
    ]

    for col, text in zip([e1, e2, e3, e4], examples):
        with col:
            if st.button(text, use_container_width=True):
                st.session_state.question = text
                st.rerun()

    st.markdown("")

    a1, a2 = st.columns([4, 1])

    with a1:
        analyze = st.button(
            "✨  ANALYZE WITH GEMINI",
            use_container_width=True,
            type="primary",
        )

    with a2:
        clear = st.button("↻ Clear", use_container_width=True)

    if clear:
        st.session_state.question = ""
        st.rerun()

    if analyze:
        if not question.strip():
            st.warning("Please enter a question first.")
        else:
            with st.spinner("Analyzing your Superstore data..."):
                answer = ask_gemini(question)

            st.markdown(
                '<div class="glass-panel">'
                '<div class="panel-title">🧠 AI Insight</div>'
                '<div class="panel-sub">Gemini + dataset context</div>'
                '</div>',
                unsafe_allow_html=True,
            )

            st.markdown(answer)

            fig = make_chart(question)

            if fig is not None:
                st.markdown(
                    '<div class="section-header">'
                    '<div class="section-title">📊 Visual Insight</div>'
                    '</div>',
                    unsafe_allow_html=True,
                )
                st.plotly_chart(
                    chart_style(fig),
                    use_container_width=True,
                )

            with st.expander("🔎 View RAG context"):
                st.code(build_context(question))


# ============================================================
# DATA EXPLORER
# ============================================================
elif st.session_state.page == "Data Explorer":

    st.markdown(
        """
        <div class="section-header">
            <div class="section-title">📊 Data Explorer</div>
            <div class="section-subtitle">
                Inspect, filter and understand the Superstore dataset
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric("Rows", f"{len(df):,}")

    with c2:
        st.metric("Columns", f"{len(df.columns):,}")

    with c3:
        st.metric("Missing values", f"{int(df.isna().sum().sum()):,}")

    st.markdown("### Filters")

    filtered = df.copy()

    f1, f2, f3 = st.columns(3)

    if "Region" in filtered.columns:
        with f1:
            regions = st.multiselect(
                "Region",
                sorted(filtered["Region"].dropna().unique()),
            )
            if regions:
                filtered = filtered[filtered["Region"].isin(regions)]

    if "Category" in filtered.columns:
        with f2:
            categories = st.multiselect(
                "Category",
                sorted(filtered["Category"].dropna().unique()),
            )
            if categories:
                filtered = filtered[filtered["Category"].isin(categories)]

    if "Segment" in filtered.columns:
        with f3:
            segments = st.multiselect(
                "Segment",
                sorted(filtered["Segment"].dropna().unique()),
            )
            if segments:
                filtered = filtered[filtered["Segment"].isin(segments)]

    st.markdown(
        f"**Showing {len(filtered):,} of {len(df):,} rows**"
    )

    st.dataframe(
        filtered,
        use_container_width=True,
        height=520,
    )

    st.download_button(
        "⬇️ Download filtered CSV",
        data=filtered.to_csv(index=False).encode("utf-8"),
        file_name="superstore_filtered.csv",
        mime="text/csv",
        use_container_width=True,
    )

    st.markdown("### Dataset profile")

    p1, p2 = st.columns(2)

    with p1:
        st.write("**Columns**")
        st.write(list(df.columns))

    with p2:
        st.write("**Data types**")
        st.dataframe(
            pd.DataFrame({
                "Column": df.columns,
                "Type": [str(df[c].dtype) for c in df.columns],
            }),
            use_container_width=True,
            hide_index=True,
        )


# ============================================================
# FOOTER
# ============================================================
st.markdown(
    """
    <div style="
        margin-top:50px;
        padding:25px 0;
        border-top:1px solid rgba(100,150,255,.12);
        text-align:center;
        color:#536888;
        font-size:11px;
        letter-spacing:.5px;
    ">
        🌌 SUPERSTORE AI &nbsp; • &nbsp;
        GEMINI AI &nbsp; • &nbsp;
        RAG &nbsp; • &nbsp;
        PANDAS &nbsp; • &nbsp;
        PLOTLY &nbsp; • &nbsp;
        STREAMLIT
    </div>
    """,
    unsafe_allow_html=True,
)
