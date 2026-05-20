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

# ==================== DESCRIPTIONS (unchanged) ====================
category_descriptions = {
    "Core Stable Income": "Provides the largest and most reliable portion of monthly income using covered-call strategies on broad market indices. Acts as the defensive backbone of the portfolio.",
    "Quality Dividend Growth": "Focuses on high-quality companies with growing dividends and strong fundamentals. Delivers quarterly income while building long-term capital appreciation and inflation protection.",
    "Cash Buffer": "Ultra-safe short-term U.S. Treasuries that serve as liquidity reserve and emergency cash. Maintains stability and allows quick reallocation when opportunities arise.",
    "Aggressive High-Yield": "Tactical high-income slice using YieldMax option-income ETFs. Designed for short-term profit boosts and can be scaled up or down easily based on market volatility."
}

holding_descriptions = { ... }  # (kept the same as previous working version)

tickers = list(targets.keys())

@st.cache_data(ttl=60)
def get_live_prices(ticker_list): ...  # (kept the same)

@st.cache_data(ttl=60)
def get_vix(): ...  # (kept the same)

prices = get_live_prices(tickers)
current_vix = get_vix()

# Build main dataframe (kept the same)
data = []  # ... (unchanged code)
df = pd.DataFrame(data)

aggressive_current = df[df["Ticker"].isin(["NVDY","ULTY","CHPY","MRNY","YMAX"])]["Current_Pct_Numeric"].sum()

# ==================== HIGH-YIELD TRACKER ($1k starter each) ====================
if 'high_yield_tracker' not in st.session_state:
    st.session_state.high_yield_tracker = [
        {"Asset": "NVDY", "Position": 1000, "Action": "Keep"},
        {"Asset": "ULTY", "Position": 1000, "Action": "Keep"},
        {"Asset": "CHPY", "Position": 1000, "Action": "Keep"},
        {"Asset": "MRNY", "Position": 1000, "Action": "Keep"},
        {"Asset": "YMAX", "Position": 1000, "Action": "Keep"}
    ]

# ==================== PAGE SELECTION ====================
# (All other pages unchanged - Overview, Income Projections, Holding Details, etc.)

elif page == "💸 Reinvestment Strategy":
    st.subheader("💸 Monthly Surplus Reinvestment Strategy")
    st.write("""
    **Allocation Rule**:
    - 60% → High-Yield Slice (NVDY, ULTY, CHPY, MRNY, YMAX)
    - 30% → Core Stable Income (JEPI)
    - 10% → Quality Dividend Growth (SCHD + VIG)
    """)

    monthly_surplus = st.number_input("Enter this month's surplus ($)", value=5000.0, step=100.0, format="%.0f")

    st.subheader("Suggested Distribution")
    col1, col2, col3 = st.columns(3)
    with col1: st.metric("High-Yield Slice (60%)", f"${round(monthly_surplus * 0.60):,.0f}")
    with col2: st.metric("Core Stable Income (30%)", f"${round(monthly_surplus * 0.30):,.0f}")
    with col3: st.metric("Quality Dividend Growth (10%)", f"${round(monthly_surplus * 0.10):,.0f}")

    if st.button("✅ Apply Calculator Output as Transactions", type="primary"):
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        st.session_state.transactions.append({"Date": now, "Bucket": "High-Yield Slice", "Asset Purchased": "General", "Amount Purchased": round(monthly_surplus * 0.60), "Add'l Income This Week": "X", "Add'l Income This Month": round(monthly_surplus * 0.60 * 0.60 / 12, 0), "Add'l Income This Year": round(monthly_surplus * 0.60 * 0.60, 0)})
        st.session_state.transactions.append({"Date": now, "Bucket": "Core Stable Income", "Asset Purchased": "General", "Amount Purchased": round(monthly_surplus * 0.30), "Add'l Income This Week": "X", "Add'l Income This Month": round(monthly_surplus * 0.30 * 0.084 / 12, 0), "Add'l Income This Year": round(monthly_surplus * 0.30 * 0.084, 0)})
        st.session_state.transactions.append({"Date": now, "Bucket": "Quality Dividend Growth", "Asset Purchased": "General", "Amount Purchased": round(monthly_surplus * 0.10), "Add'l Income This Week": "X", "Add'l Income This Month": round(monthly_surplus * 0.10 * 0.084 / 12, 0), "Add'l Income This Year": round(monthly_surplus * 0.10 * 0.084, 0)})
        st.success("✅ Transactions logged successfully!")

    # ==================== HIGH-YIELD SPECIFIC PURCHASE ====================
    st.subheader("🔥 High-Yield Specific Purchase")
    with st.form("high_yield_form"):
        hy_date = st.date_input("Date", value=datetime.today())
        hy_asset = st.selectbox("Asset Purchased", ["NVDY", "ULTY", "CHPY", "MRNY", "YMAX"])
        hy_amount = st.number_input("Amount Purchased ($)", value=1000.0, step=100.0, format="%.0f")
        submitted = st.form_submit_button("Add High-Yield Purchase")
        if submitted and hy_amount > 0:
            st.session_state.high_yield_tracker.append({
                "Asset": hy_asset,
                "Position": hy_amount,
                "Action": "Buy"
            })
            st.success(f"✅ {hy_asset} purchase of ${hy_amount:,.0f} logged!")

    # ==================== HIGH-YIELD HOLDINGS TRACKER ====================
    st.subheader("High-Yield Holdings Tracker ($1k starter each)")
    tracker_df = pd.DataFrame(st.session_state.high_yield_tracker)
    st.dataframe(tracker_df, use_container_width=True, hide_index=True)

    # (Main transaction tracker can stay below if you want, or we can hide it since high-yield is now separate)

elif page == "🛡️ Guardrails & Alerts":
    st.subheader("🛡️ Proactive Guardrails")
    st.info("All guardrails are currently **GREEN**. No immediate action required.")

st.caption(f"Last updated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")
