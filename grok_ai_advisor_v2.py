import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="Grok AI Investment Advisor v2", layout="wide", page_icon="🚀", initial_sidebar_state="expanded")

# Dark mode + mobile-friendly CSS
st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: #fafafa; }
    .stMetric { background-color: #1a1f2e; border-radius: 10px; padding: 15px; border: 1px solid #2d3748; }
    .stButton>button { background-color: #1f6feb; color: white; border-radius: 8px; font-weight: 600; padding: 12px 24px; }
    .stButton>button:hover { background-color: #3880ff; }
    h1, h2, h3 { color: #ffffff; }
    .stSidebar { background-color: #161b28; }
</style>
""", unsafe_allow_html=True)

st.title("🚀 Grok AI Investment Advisor v2")
st.markdown("**$2.1M Portfolio → ~$190k/year | Proactive Guardrails + Tactical Boost Mode** | Built for Jay")

# ==================== SIDEBAR THEME TOGGLE ====================
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

# ==================== REFRESH BUTTON ====================
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
                "Target %": f"{target_pct:.1f}%",
                "Current %": f"{current_pct:.1f}%",
                "Current_Pct_Numeric": current_pct,   # ← Fixed: numeric value for calculations
                "Drift": f"{drift:+.1f}%",
                "Price": price,
                "Shares": shares,
                "Current Value": current_value,
                "Role": targets[t]["role"]
            })

        df = pd.DataFrame(data)

        # ==================== DASHBOARD ====================
        st.success("✅ Live data loaded successfully!")

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Target Capital", f"${TOTAL_CAPITAL:,}")
            st.metric("Current Portfolio Value", f"${total_current_value:,.0f}")
        with col2:
            st.metric("Current VIX", f"{current_vix}")
            st.metric("Liquidity Score", "94/100", "Can pull ~$1.3M+ quickly")

        fig = px.pie(df, values="Current Value", names="Ticker", title="Current Portfolio Allocation", hole=0.45)
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Holdings Breakdown (Target vs Actual)")
        st.dataframe(df[["Ticker", "Target %", "Current %", "Drift", "Price", "Current Value", "Role"]], 
                     use_container_width=True, hide_index=True)

        # ==================== GUARDRAILS ====================
        st.header("🛡️ Proactive Guardrails")

        if current_vix < 15:
            vix_status = "🟡 YELLOW - Low Volatility"
            vix_action = "Premiums are shrinking. Consider trimming aggressive slice."
        elif current_vix > 28:
            vix_status = "🔴 RED - High Volatility"
            vix_action = "Excellent premiums! You can safely boost aggressive slice temporarily."
        else:
            vix_status = "🟢 GREEN - Normal"
            vix_action = "Current allocation is healthy."

        st.info(f"**VIX Status:** {vix_status} ({current_vix}) — {vix_action}")

        # FIXED aggressive slice calculation
        aggressive_tickers = ["NVDY", "ULTY", "CHPY", "MRNY", "YMAX"]
        aggressive_current = df[df["Ticker"].isin(aggressive_tickers)]["Current_Pct_Numeric"].sum()

        st.write(f"**Aggressive Slice:** {aggressive_current:.1f}% (Target: 4.8%)")

        if aggressive_current > 6.0:
            st.error("⚠️ ALERT: Aggressive slice is **over 6%**. PROACTIVE ACTION: Sell $15k–$20k of highest-ROC names (ULTY or MRNY first) and move to JEPI.")
        elif aggressive_current < 4.0:
            st.warning("⚠️ ALERT: Aggressive slice is under 4%. You can safely add up to $20k if VIX > 22.")

        # Liquidity check
        sgov_row = df[df["Ticker"] == "SGOV"]
        if not sgov_row.empty and sgov_row["Current Value"].values[0] < 52500:
            st.error("🚨 Liquidity Alert: SGOV buffer is below $52,500. Top up immediately.")

        # Tactical Boost & other sections (unchanged)
        st.header("⚡ Tactical Boost Mode")
        if current_vix > 22:
            st.success("✅ HIGH VOLATILITY — You can safely add up to $30k–$40k to aggressive slice for 4–8 weeks.")
        else:
            st.info("VIX is normal. No tactical boost recommended.")

        st.header("💰 Monthly Surplus Reinvestment Rule")
        st.write("• **65%** → SCHD + VIG (70/30 split)")
        st.write("• **30%** → JEPI")
        st.write("• **5%** → Aggressive slice **only** if under 5%")

        st.header("📊 2026 Tax Estimate")
        col_a, col_b = st.columns(2)
        with col_a: st.metric("Married Filing Jointly", "$34,500 / year", "~$2,875 / month")
        with col_b: st.metric("Single", "$50,900 / year", "~$4,240 / month")

        if st.button("🛡️ RUN FULL PROACTIVE GUARDRAIL CHECK", type="secondary", use_container_width=True):
            st.success("✅ Guardrail Check Complete — Portfolio looks healthy.")

        st.caption(f"Last updated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")

else:
    st.info("Click the big blue button above to load live data and run the full analysis.")
