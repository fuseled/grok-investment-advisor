import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

st.set_page_config(page_title="Grok AI Investment Advisor v2", layout="wide", page_icon="🚀", initial_sidebar_state="expanded")

# Dark mode + mobile CSS
st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: #fafafa; }
    .stMetric { background-color: #1a1f2e; border-radius: 12px; padding: 18px; border: 1px solid #2d3748; }
    .stButton>button { background-color: #1f6feb; color: white; border-radius: 8px; font-weight: 600; padding: 14px 28px; }
    h1, h2, h3 { color: #ffffff; }
    .stSidebar { background-color: #161b28; }
    .month-box { background-color: #1a1f2e; padding: 15px; border-radius: 10px; border: 1px solid #2d3748; text-align: center; }
</style>
""", unsafe_allow_html=True)

# ==================== SIDEBAR NAVIGATION ====================
st.sidebar.title("🚀 Grok AI Advisor")
page = st.sidebar.radio(
    "Navigate",
    ["📊 Portfolio Overview", 
     "💰 Income Projections", 
     "📋 Holding Details",
     "📊 Portfolio Combined",
     "💸 Reinvestment Strategy",
     "🛡️ Guardrails & Alerts"]
)

st.title("Grok AI Investment Advisor v2")
st.markdown("**$2.1M Portfolio → ~$190k/year** | Built for Jay")

# ==================== PORTFOLIO DATA ====================
TOTAL_CAPITAL = 2_100_000

targets = {
    "JEPI": {"target_pct": 42.9, "amount": 900_000},
    "SCHD": {"target_pct": 23.8, "amount": 500_000},
    "JEPQ": {"target_pct": 14.3, "amount": 300_000},
    "VIG":  {"target_pct": 6.7,  "amount": 140_000},
    "SGOV": {"target_pct": 2.9,  "amount": 60_000},
    "NVDY": {"target_pct": 1.19, "amount": 25_000},
    "ULTY": {"target_pct": 1.19, "amount": 25_000},
    "CHPY": {"target_pct": 0.95, "amount": 20_000},
    "MRNY": {"target_pct": 0.71, "amount": 15_000},
    "YMAX": {"target_pct": 0.71, "amount": 15_000},
}

category_map = {
    "JEPI": "Core Stable Income", "JEPQ": "Core Stable Income",
    "SCHD": "Quality Dividend Growth", "VIG": "Quality Dividend Growth",
    "SGOV": "Cash Buffer",
    "NVDY": "Aggressive High-Yield", "ULTY": "Aggressive High-Yield",
    "CHPY": "Aggressive High-Yield", "MRNY": "Aggressive High-Yield",
    "YMAX": "Aggressive High-Yield",
}

payout_data = {
    "JEPI": {"freq": "Monthly", "yield": 8.4},
    "JEPQ": {"freq": "Monthly", "yield": 10.3},
    "SCHD": {"freq": "Quarterly", "yield": 3.3},
    "VIG":  {"freq": "Quarterly", "yield": 1.6},
    "SGOV": {"freq": "Monthly", "yield": 4.5},
    "NVDY": {"freq": "Weekly", "yield": 60.0},
    "ULTY": {"freq": "Weekly", "yield": 65.0},
    "CHPY": {"freq": "Weekly", "yield": 46.0},
    "MRNY": {"freq": "Weekly", "yield": 71.0},
    "YMAX": {"freq": "Weekly", "yield": 57.0},
}

# ==================== DESCRIPTIONS ====================
category_descriptions = {
    "Core Stable Income": "Provides the largest and most reliable portion of monthly income using covered-call strategies on broad market indices. Acts as the defensive backbone of the portfolio.",
    "Quality Dividend Growth": "Focuses on high-quality companies with growing dividends and strong fundamentals. Delivers quarterly income while building long-term capital appreciation and inflation protection.",
    "Cash Buffer": "Ultra-safe short-term U.S. Treasuries that serve as liquidity reserve and emergency cash. Maintains stability and allows quick reallocation when opportunities arise.",
    "Aggressive High-Yield": "Tactical high-income slice using YieldMax option-income ETFs. Designed for short-term profit boosts and can be scaled up or down easily based on market volatility."
}

holding_descriptions = { ... }  # (same as previous stable version)

tickers = list(targets.keys())

@st.cache_data(ttl=60)
def get_live_prices(ticker_list): ...  # (same as previous stable version)

@st.cache_data(ttl=60)
def get_vix(): ...  # (same as previous stable version)

prices = get_live_prices(tickers)
current_vix = get_vix()

# Build main dataframe (same as previous stable version)
data = []  # ... (unchanged)
df = pd.DataFrame(data)

aggressive_current = df[df["Ticker"].isin(["NVDY","ULTY","CHPY","MRNY","YMAX"])]["Current_Pct_Numeric"].sum()

# ==================== TRANSACTION TRACKER (High-Yield Specific) ====================
if 'high_yield_tracker' not in st.session_state:
    # Initialize each high-yield holding with $1,000
    st.session_state.high_yield_tracker = [
        {"Asset": "NVDY", "Position": 1000, "Action": "Keep"},
        {"Asset": "ULTY", "Position": 1000, "Action": "Keep"},
        {"Asset": "CHPY", "Position": 1000, "Action": "Keep"},
        {"Asset": "MRNY", "Position": 1000, "Action": "Keep"},
        {"Asset": "YMAX", "Position": 1000, "Action": "Keep"}
    ]

# ==================== PAGE SELECTION ====================
if page == "📊 Portfolio Overview":
    # (All your existing overview code + AI Analyst)
    # ... [same as previous stable version]

    st.subheader("🔍 AI Analyst: High-Yield ETF Recommendation")
    if current_vix > 28:
        rec = "🚀 **ULTY or MRNY** — Highest premiums right now. Strong buy."
    elif current_vix > 22:
        rec = "✅ **NVDY or YMAX** — Excellent balance. Good to hold or add."
    elif current_vix < 15:
        rec = "⚠️ **Trim** — Premiums are low. Consider reducing."
    else:
        rec = "🟡 **CHPY** — Solid middle-ground choice."
    st.write(rec)
    st.caption(f"Current aggressive slice: **{aggressive_current:.1f}%** | VIX: **{current_vix}**")

    # (rest of overview unchanged)

elif page == "💸 Reinvestment Strategy":
    st.subheader("💸 Monthly Surplus Reinvestment Strategy")
    st.write("**60% High Yield Switch** (toggle on to allocate 60% of surplus to high-yield slice instead of 10%)")
    high_yield_mode = st.toggle("60% High Yield Mode", value=False)

    allocation_high = 0.60 if high_yield_mode else 0.10

    monthly_surplus = st.number_input("Enter this month's surplus ($)", value=5000.0, step=100.0, format="%.0f")

    st.subheader("Suggested Distribution")
    col1, col2, col3 = st.columns(3)
    with col1: st.metric("Quality Dividend Growth (60%)", f"${round(monthly_surplus * 0.60):,.0f}")
    with col2: st.metric("Core Stable Income (30%)", f"${round(monthly_surplus * 0.30):,.0f}")
    with col3: st.metric(f"Tactical High-Yield ({int(allocation_high*100)}%)", f"${round(monthly_surplus * allocation_high):,.0f}")

    # AI Analyst on this page too
    st.subheader("🔍 AI Analyst: High-Yield ETF Recommendation")
    if current_vix > 28:
        rec = "🚀 **ULTY or MRNY** — Highest premiums right now. Strong buy."
    elif current_vix > 22:
        rec = "✅ **NVDY or YMAX** — Excellent balance. Good to hold or add."
    elif current_vix < 15:
        rec = "⚠️ **Trim** — Premiums are low."
    else:
        rec = "🟡 **CHPY** — Solid middle-ground choice."
    st.write(rec)

    # High-Yield Tracker with $1k starter
    st.subheader("🔥 High-Yield Holdings Tracker ($1k starter each)")
    for i, holding in enumerate(st.session_state.high_yield_tracker):
        col_a, col_b, col_c = st.columns([3,2,2])
        with col_a:
            st.write(f"**{holding['Asset']}**")
        with col_b:
            new_pos = st.number_input(f"Position $", value=holding["Position"], step=100.0, key=f"pos_{i}")
        with col_c:
            action = st.selectbox("Action", ["Keep", "Buy", "Sell"], key=f"act_{i}")
            if action == "Buy":
                holding["Position"] = new_pos
            elif action == "Sell" and new_pos < holding["Position"]:
                holding["Position"] = new_pos

    st.dataframe(pd.DataFrame(st.session_state.high_yield_tracker), use_container_width=True, hide_index=True)

else:
    # (All other pages unchanged)
    pass

st.caption(f"Last updated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")
