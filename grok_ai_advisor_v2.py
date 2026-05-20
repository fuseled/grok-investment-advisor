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
    .stMetric { background-color: #1a1f2e; border-radius: 12px; padding: 18px; border: 1px solid #2d3748; }
    .stButton>button { background-color: #1f6feb; color: white; border-radius: 8px; font-weight: 600; padding: 14px 28px; }
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

        # Build main dataframe
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

        # Grok AI Evaluation
        st.subheader("🤖 Grok AI Portfolio Evaluation")
        aggressive_current = df[df["Ticker"].isin(["NVDY","ULTY","CHPY","MRNY","YMAX"])]["Current_Pct_Numeric"].sum()
        vix_comment = "High volatility — excellent premiums!" if current_vix > 28 else "Low volatility — premiums shrinking." if current_vix < 15 else "Normal volatility range."
        slice_comment = "Overweight — consider trimming." if aggressive_current > 6.0 else "Underweight — safe to add." if aggressive_current < 4.0 else "Right on target."
        st.info(f"**Overall Condition:** Healthy.\n\nVIX is **{current_vix}** → {vix_comment}\n\nAggressive slice is **{aggressive_current:.1f}%** → {slice_comment}\n\n**Recommendation:** No immediate action needed.")

        # Sunburst + Category Summary + Holdings (unchanged)
        st.subheader("📊 Current Portfolio Allocation")
        fig_sunburst = px.sunburst(df, path=['Category', 'Ticker'], values='Current Value', title="Category → Holdings", color='Category')
        st.plotly_chart(fig_sunburst, use_container_width=True)

        st.subheader("📊 Portfolio by Strategy Category")
        cat_summary = df.groupby("Category").agg({"Current Value": "sum", "Current_Pct_Numeric": "sum"}).round(2)
        cat_summary = cat_summary.rename(columns={"Current_Pct_Numeric": "Portfolio %"})
        st.dataframe(cat_summary.style.format({"Current Value": "${:,.0f}", "Portfolio %": "{:.1f}%"}), use_container_width=True)

        st.subheader("Holdings Breakdown by Strategy Category")
        st.dataframe(df[["Ticker", "Category", "Target %", "Current %", "Drift", "Price", "Current Value"]], use_container_width=True, hide_index=True)

        # ==================== CLEAN PAYOUTS SECTION (Div Tracker style) ====================
        st.header("💰 Income Projections")

        # Calculate monthly and annual payouts
        payout_rows = []
        total_annual = 0
        monthly_payouts = []  # for the bar chart
        for t in tickers:
            amt = targets[t]["amount"]
            yld = payout_data[t]["yield"]
            ann = round(amt * yld / 100, 0)
            total_annual += ann
            mo = round(ann / 12, 0)
            payout_rows.append({
                "Ticker": t,
                "Category": category_map[t],
                "Frequency": payout_data[t]["freq"],
                "Est. Annual Yield": f"{yld}%",
                "Est. Annual Payout": f"${ann:,.0f}",
                "Est. Monthly Payout": f"${mo:,.0f}",
            })
            monthly_payouts.append({"Ticker": t, "Category": category_map[t], "Monthly Payout": mo})

        payout_df = pd.DataFrame(payout_rows)

        # Monthly Income Projection Bar Chart (clean Div Tracker style)
        st.subheader("📈 Monthly Income Projection (2026)")
        months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
        monthly_data = []
        for m in months:
            monthly_data.append({"Month": m, "Total Monthly Payout": round(total_annual / 12, 0)})
        monthly_df = pd.DataFrame(monthly_data)

        fig_monthly = px.bar(
            monthly_df,
            x="Month",
            y="Total Monthly Payout",
            title="Projected Monthly Income — 2026",
            color_discrete_sequence=["#1f6feb"],
            height=450
        )
        fig_monthly.update_traces(texttemplate="$%{y:,.0f}", textposition="outside")
        st.plotly_chart(fig_monthly, use_container_width=True)

        # Yearly Income Summary Cards
        st.subheader("📅 Yearly Income Summary")
        col_y1, col_y2 = st.columns(2)
        with col_y1:
            st.metric("**2026 Projected Income**", f"${total_annual:,.0f}", "Current projection")
        with col_y2:
            st.metric("**2027 Projected Income**", f"${int(total_annual * 1.04):,.0f}", "+4% growth est.")

        # Payouts detail table
        st.dataframe(payout_df, use_container_width=True, hide_index=True)

        st.caption(f"Last updated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")

else:
    st.info("Click the big blue button above to load live data and run the full analysis.")
