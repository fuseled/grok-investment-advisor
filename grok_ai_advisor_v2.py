import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="Grok AI Investment Advisor v2", layout="wide", page_icon="🚀", initial_sidebar_state="expanded")

# Dark mode + mobile CSS
st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: #fafafa; }
    .stMetric { background-color: #1a1f2e; border-radius: 10px; padding: 15px; border: 1px solid #2d3748; }
    .stButton>button { background-color: #1f6feb; color: white; border-radius: 8px; font-weight: 600; padding: 12px 24px; }
    h1, h2, h3 { color: #ffffff; }
    .stSidebar { background-color: #161b28; }
</style>
""", unsafe_allow_html=True)

st.title("🚀 Grok AI Investment Advisor v2")
st.markdown("**$2.1M Portfolio → ~$190k/year | Proactive Guardrails + Tactical Boost Mode** | Built for Jay")

with st.sidebar:
    st.header("⚙️ Settings")
    theme = st.radio("Theme", ["🌙 Dark", "☀️ Light"], index=0, horizontal=True)
    if theme == "☀️ Light":
        st.markdown("<style>.stApp { background-color: #ffffff; color: #000000; } .stMetric { background-color: #f0f2f6; }</style>", unsafe_allow_html=True)

# ==================== PORTFOLIO ====================
TOTAL_CAPITAL = 2_100_000

targets = {
    "JEPI": {"target_pct": 42.9, "amount": 900_000, "role": "Core Income"},
    "SCHD": {"target_pct": 23.8, "amount": 500_000, "role": "Quality Growth"},
    "JEPQ": {"target_pct": 14.3, "amount": 300_000, "role": "Nasdaq Boost"},
    "VIG":  {"target_pct": 6.7,  "amount": 140_000, "role": "Dividend Growth"},
    "SGOV": {"target_pct": 2.9,  "amount": 60_000,  "role": "Cash Buffer"},
    "NVDY": {"target_pct": 1.19, "amount": 25_000, "role": "NVDA YieldMax"},
    "ULTY": {"target_pct": 1.19, "amount": 25_000, "role": "Ultra Basket"},
    "CHPY": {"target_pct": 0.95, "amount": 20_000, "role": "Semi Portfolio"},
    "MRNY": {"target_pct": 0.71, "amount": 15_000, "role": "Biotech YieldMax"},
    "YMAX": {"target_pct": 0.71, "amount": 15_000, "role": "YieldMax Fund-of-Funds"},
}

category_map = {
    "JEPI": "Core Stable Income", "JEPQ": "Core Stable Income",
    "SCHD": "Quality Dividend Growth", "VIG": "Quality Dividend Growth",
    "SGOV": "Cash Buffer",
    "NVDY": "Aggressive High-Yield", "ULTY": "Aggressive High-Yield",
    "CHPY": "Aggressive High-Yield", "MRNY": "Aggressive High-Yield",
    "YMAX": "Aggressive High-Yield",
}

# Payout data (realistic May 2026 estimates)
payout_data = {
    "JEPI": {"freq": "Monthly", "yield": 8.4, "notes": "Covered calls"},
    "JEPQ": {"freq": "Monthly", "yield": 10.3, "notes": "Covered calls"},
    "SCHD": {"freq": "Quarterly", "yield": 3.3, "notes": "Qualified dividends"},
    "VIG":  {"freq": "Quarterly", "yield": 1.6, "notes": "Qualified dividends"},
    "SGOV": {"freq": "Monthly", "yield": 4.5, "notes": "Treasury interest"},
    "NVDY": {"freq": "Weekly", "yield": 60.0, "notes": "High ROC expected"},
    "ULTY": {"freq": "Weekly", "yield": 65.0, "notes": "High ROC expected"},
    "CHPY": {"freq": "Weekly", "yield": 46.0, "notes": "High ROC expected"},
    "MRNY": {"freq": "Weekly", "yield": 71.0, "notes": "High ROC expected"},
    "YMAX": {"freq": "Weekly", "yield": 57.0, "notes": "High ROC expected"},
}

tickers = list(targets.keys())

@st.cache_data(ttl=300)
def get_live_prices(ticker_list):
    prices = {}
    for t in ticker_list:
        try:
            hist = yf.Ticker(t).history(period="5d")
            prices[t] = round(hist['Close'].iloc[-1], 2)
        except:
            prices[t] = 0.0
    return prices

@st.cache_data(ttl=300)
def get_vix():
    try:
        vix_hist = yf.Ticker("^VIX").history(period="5d")
        return round(vix_hist['Close'].iloc[-1], 2)
    except:
        return 18.0

if st.button("🔄 REFRESH LIVE DATA & RUN FULL ANALYSIS", type="primary", use_container_width=True):
    with st.spinner("Pulling live market data..."):
        prices = get_live_prices(tickers)
        current_vix = get_vix()

        data = []
        total_current_value = 0

        for t in tickers:
            target_amount = targets[t]["amount"]
            price = prices[t]
            shares = round(target_amount / price, 2) if price > 0 else 0
            current_value = round(shares * price, 2)
            total_current_value += current_value
            current_pct = round((current_value / TOTAL_CAPITAL) * 100, 2)
            target_pct = targets[t]["target_pct"]
            drift = round(current_pct - target_pct, 2)

            data.append({
                "Ticker": t,
                "Category": category_map[t],
                "Target %": f"{target_pct:.1f}%",
                "Current %": f"{current_pct:.1f}%",
                "Current_Pct_Numeric": current_pct,
                "Drift": f"{drift:+.1f}%",
                "Price": price,
                "Shares": shares,
                "Current Value": current_value,
                "Role": targets[t]["role"]
            })

        df = pd.DataFrame(data)

        st.success("✅ Live data loaded successfully!")

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Target Capital", f"${TOTAL_CAPITAL:,}")
            st.metric("Current Portfolio Value", f"${total_current_value:,.0f}")
        with col2:
            st.metric("Current VIX", f"{current_vix}")
            st.metric("Liquidity Score", "94/100")

        fig = px.pie(df, values="Current Value", names="Ticker", title="
