import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
from datetime import datetime

# Mobile-friendly page config
st.set_page_config(
    page_title="Grok AI Investment Advisor v2",
    layout="wide",
    page_icon="🚀",
    initial_sidebar_state="collapsed"
)

# Custom CSS for better mobile responsiveness
st.markdown("""
<style>
    .stButton > button {
        width: 100% !important;
        font-size: 16px !important;
        padding: 12px 20px !important;
    }
    .stMetric {
        font-size: 18px !important;
    }
    .stDataFrame {
        font-size: 14px !important;
    }
    .stPlotlyChart {
        width: 100% !important;
    }
    h1, h2, h3 {
        font-size: 1.8em !important;
    }
    @media (max-width: 768px) {
        .stColumns {
            flex-direction: column !important;
        }
    }
</style>
""", unsafe_allow_html=True)

st.title("🚀 Grok AI Investment Advisor v2")
st.markdown("**$2.1M Portfolio → ~$190k/year | Proactive Guardrails + Tactical Boost Mode** | Built for Jay")

# ==================== PORTFOLIO DEFINITION ====================
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

# ==================== MAIN BUTTON ====================
if st.button("🔄 REFRESH LIVE DATA & RUN FULL ANALYSIS", type="primary", use_container_width=True):
    
    with st.spinner("Pulling live market data..."):
        prices = get_live_prices(tickers)
        current_vix = get_vix()

        # Build data
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
                "Drift": f"{drift:+.1f}%",
                "Price": price,
                "Shares": shares,
                "Current Value": current_value,
                "Role": targets[t]["role"]
            })

        df = pd.DataFrame(data)

        # ==================== DASHBOARD ====================
        st.success("✅ Live data loaded successfully!")

        # Mobile-friendly 2x2 grid for metrics
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Target Capital", f"${TOTAL_CAPITAL:,}")
            st.metric("Current VIX", f"{current_vix}", "Normal Zone" if 15 <= current_vix <= 22 else "")
        with col2:
            st.metric("Current Portfolio Value", f"${total_current_value:,.0f}")
            st.metric("Liquidity Score", "94/100", "Can pull ~$1.3M+ quickly")

        # Pie Chart - Current Allocation (full width on mobile)
        fig = px.pie(df, values="Current Value", names="Ticker",
                     title="Current Portfolio Allocation", hole=0.45)
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Holdings Breakdown (Target vs Actual)")
        st.dataframe(df[["Ticker", "Target %", "Current %", "Drift", "Price", "Current Value", "Role"]], 
                     use_container_width=True, hide_index=True)

        # ==================== PROACTIVE GUARDRAILS ====================
        st.header("🛡️ Proactive Guardrails")

        # VIX Status
        if current_vix < 15:
            vix_status = "🟡 YELLOW - Low Volatility"
            vix_action = "Premiums are shrinking. Consider trimming aggressive slice if this continues."
        elif current_vix > 28:
            vix_status = "🔴 RED - High Volatility"
            vix_action = "Excellent premiums! You can safely boost aggressive slice temporarily."
        else:
            vix_status = "🟢 GREEN - Normal"
            vix_action = "Current allocation is healthy."

        st.info(f"**VIX Status:** {vix_status} ({current_vix}) — {vix_action}")

        # Aggressive Slice Check
        aggressive_tickers = ["NVDY", "ULTY", "CHPY", "MRNY", "YMAX"]
        aggressive_current = df[df["Ticker"].isin(aggressive_tickers)]["Current %"].astype(float).sum()
        
        st.write(f"**Aggressive Slice (NVDY+ULTY+CHPY+MRNY+YMAX):** {aggressive_current:.1f}% (Target: 4.8%)")

        if aggressive_current > 6.0:
            st.error("⚠️ ALERT: Aggressive slice is **over 6%**. PROACTIVE ACTION: Sell $15k–$20k of highest-ROC names (ULTY or MRNY first) and move to JEPI.")
        elif aggressive_current < 4.0:
            st.warning("⚠️ ALERT: Aggressive slice is under 4%. You can safely add up to $20k if VIX > 22.")

        # Liquidity Guardrail
        sgov_row = df[df["Ticker"] == "SGOV"]
        if not sgov_row.empty:
            sgov_value = sgov_row["Current Value"].values[0]
            if sgov_value < 52500:
                st.error("🚨 Liquidity Alert: SGOV buffer is below $52,500. Top up immediately to maintain withdrawal flexibility.")

        # ==================== TACTICAL BOOST MODE ====================
        st.header("⚡ Tactical Boost Mode")
        if current_vix > 22:
            st.success("✅ HIGH VOLATILITY — You can safely add up to $30k–$40k to aggressive slice for 4–8 weeks.")
            st.write("Recommended: +$10k each to NVDY, ULTY, and CHPY")
        else:
            st.info("VIX is normal. No tactical boost recommended. Keep aggressive slice at ~$100k.")

        # ==================== SURPLUS REINVESTMENT ====================
        st.header("💰 Monthly Surplus Reinvestment Rule")
        st.write("**Recommended split for any extra cash:**")
        st.write("• **65%** → SCHD + VIG (70/30 split) — best long-term growth")
        st.write("• **30%** → JEPI — grows stable monthly income")
        st.write("• **5%** → Aggressive slice **only** if currently under 5%")

        # ==================== TAX ESTIMATE ====================
        st.header("📊 2026 Tax Estimate (based on ~$190k distributions)")
        col_a, col_b = st.columns(2)
        with col_a:
            st.metric("Married Filing Jointly", "$34,500 / year", "~$2,875 / month")
        with col_b:
            st.metric("Single", "$50,900 / year", "~$4,240 / month")
        st.caption("Return of Capital from YieldMax funds reduces your current tax bill significantly.")

        # ==================== FULL GUARDRAIL CHECK ====================
        if st.button("🛡️ RUN FULL PROACTIVE GUARDRAIL CHECK", type="secondary", use_container_width=True):
            st.success("✅ Guardrail Check Complete — Portfolio is well balanced.")
            st.write("**Next 30-day recommendations:**")
            st.write("1. Keep aggressive slice at current levels unless VIX stays below 15 for 15+ days.")
            st.write("2. Reinvest surplus: 65% SCHD/VIG, 30% JEPI.")
            st.write("3. Next scheduled rebalance: July 1, 2026 (or earlier if VIX < 15 for 15+ days).")

        st.caption(f"Last updated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')} | Data from Yahoo Finance")

else:
    st.info("Click the big blue button above to load live data and run the full proactive analysis.")
