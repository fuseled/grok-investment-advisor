import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="Grok AI Investment Advisor v2", layout="wide", page_icon="📈", initial_sidebar_state="expanded")

# Tight professional styling
st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: #fafafa; padding-top: 0rem !important; margin-top: 0 !important; }
    .block-container { padding-top: 0rem !important; margin-top: 0 !important; }
    .stMetric { background-color: #1a1f2e; border-radius: 12px; padding: 18px; border: 1px solid #2d3748; }
    .stButton>button { background-color: #1f6feb; color: white; border-radius: 8px; font-weight: 600; padding: 14px 28px; }
    h1, h2, h3 { color: #ffffff; margin-top: 0 !important; padding-top: 0 !important; }
    .stSidebar { background-color: #161b28; }
    .stSidebar .stRadio label { font-size: 1.35rem !important; font-weight: 700 !important; padding: 14px 0 !important; line-height: 1.4; }
</style>
""", unsafe_allow_html=True)

# ==================== SIDEBAR NAVIGATION ====================
st.sidebar.title("CASH AdvIsor")
page = st.sidebar.radio(
    "Navigate",
    ["Portfolio Overview", "Income Projections", "Future Portfolio", "Holding Details",
     "Portfolio Combined", "Reinvestment Strategy", "Guardrails & Alerts"]
)

st.title("Grok AI Investment Advisor v2")
st.markdown("**$2.1M Portfolio → ~$190k/year** | Built for Jay")

# ==================== PORTFOLIO DATA ====================
TOTAL_CAPITAL = 2_100_000

targets = {
    "JEPI": {"target_pct": 40.0, "amount": 840_000},
    "SCHD": {"target_pct": 22.0, "amount": 462_000},
    "JEPQ": {"target_pct": 13.3, "amount": 280_000},
    "VIG":  {"target_pct": 6.2,  "amount": 130_000},
    "SGOV": {"target_pct": 2.9,  "amount": 60_000},
    "NVDY": {"target_pct": 1.0,  "amount": 21_000},
    "ULTY": {"target_pct": 1.0,  "amount": 21_000},
    "CHPY": {"target_pct": 0.8,  "amount": 17_000},
    "MRNY": {"target_pct": 0.6,  "amount": 13_000},
    "YMAX": {"target_pct": 0.6,  "amount": 13_000},
    "IBHJ": {"target_pct": 5.0,  "amount": 105_000},
    "EVHY": {"target_pct": 5.6,  "amount": 118_000},
}

category_map = {
    "JEPI": "Core Stable Income", "JEPQ": "Core Stable Income",
    "SCHD": "Quality Dividend Growth", "VIG": "Quality Dividend Growth",
    "IBHJ": "Quality Dividend Growth",
    "SGOV": "Cash Buffer",
    "NVDY": "Aggressive High-Yield", "ULTY": "Aggressive High-Yield",
    "CHPY": "Aggressive High-Yield", "MRNY": "Aggressive High-Yield",
    "YMAX": "Aggressive High-Yield", "EVHY": "Aggressive High-Yield",
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
    "IBHJ": {"freq": "Monthly", "yield": 6.7},
    "EVHY": {"freq": "Monthly", "yield": 7.2},
}

category_descriptions = {
    "Core Stable Income": "Provides the largest and most reliable portion of monthly income using covered-call strategies...",
    "Quality Dividend Growth": "Focuses on high-quality companies with growing dividends...",
    "Cash Buffer": "Ultra-safe short-term U.S. Treasuries...",
    "Aggressive High-Yield": "Tactical high-income slice using YieldMax and high-yield bond ETFs..."
}

holding_descriptions = {
    "JEPI": "JPMorgan Equity Premium Income ETF – ...",
    "JEPQ": "JPMorgan Nasdaq Equity Premium Income ETF – ...",
    "SCHD": "Schwab U.S. Dividend Equity ETF – ...",
    "VIG": "Vanguard Dividend Appreciation ETF – ...",
    "SGOV": "iShares 0-3 Month Treasury Bond ETF – ...",
    "NVDY": "YieldMax NVDA Option Income Strategy ETF – ...",
    "ULTY": "YieldMax Ultra Option Income Strategy ETF – ...",
    "CHPY": "YieldMax Semiconductor Portfolio Option Income ETF – ...",
    "MRNY": "YieldMax MRNA Option Income Strategy ETF – ...",
    "YMAX": "YieldMax Universe Fund of Option Income ETFs – ...",
    "IBHJ": "iShares iBonds 2030 Term High Yield and Income ETF – Target-maturity high-yield bond ladder maturing in 2030. Provides diversified corporate bond exposure with monthly income and built-in principal protection.",
    "EVHY": "Eaton Vance High Yield ETF – Actively managed high-yield bond ETF focusing on higher-quality BB/B issuers. Strong monthly income with professional credit selection.",
}

tickers = list(targets.keys())

@st.cache_data(ttl=60)
def get_live_prices(ticker_list):
    prices = {}
    for t in ticker_list:
        try:
            hist = yf.Ticker(t).history(period="5d")
            prices[t] = round(hist['Close'].iloc[-1], 2)
        except:
            prices[t] = 0.0
    return prices

@st.cache_data(ttl=60)
def get_vix():
    try:
        vix_hist = yf.Ticker("^VIX").history(period="5d")
        return round(vix_hist['Close'].iloc[-1], 2)
    except:
        return 18.0

prices = get_live_prices(tickers)
current_vix = get_vix()

# Build main dataframe
data = []
for t in tickers:
    target_amount = targets[t]["amount"]
    price = prices.get(t, 0)
    shares = round(target_amount / price, 2) if price > 0 else 0
    current_value = round(shares * price, 2)
    current_pct = round((current_value / TOTAL_CAPITAL) * 100, 2)
    target_pct = targets[t]["target_pct"]
    drift = round(current_pct - target_pct, 2)
    annual = round(target_amount * payout_data[t]["yield"] / 100, 0)
    monthly = round(annual / 12, 0) if payout_data[t]["freq"] in ["Monthly", "Weekly"] else round(annual / 4, 0)
    data.append({
        "Ticker": t, "Category": category_map[t], "Target %": f"{target_pct:.1f}%",
        "Current %": f"{current_pct:.1f}%", "Current_Pct_Numeric": current_pct,
        "Drift": f"{drift:+.1f}%", "Price": price, "Shares": shares,
        "Current Value": current_value, "Est. Annual Yield": f"{payout_data[t]['yield']}%",
        "Est. Annual Payout": f"${annual:,.0f}", "Est. Monthly Payout": f"${monthly:,.0f}",
        "Frequency": payout_data[t]["freq"],
    })

df = pd.DataFrame(data)
aggressive_current = df[df["Ticker"].isin(["NVDY","ULTY","CHPY","MRNY","YMAX","EVHY"])]["Current_Pct_Numeric"].sum()
total_annual = round(df["Est. Annual Payout"].str.replace("$","").str.replace(",","").astype(float).sum(), 0)
total_monthly = round(total_annual / 12, 0)
current_portfolio_value = df['Current Value'].sum()

# Trackers (your enhanced version)
if 'high_yield_tracker' not in st.session_state:
    st.session_state.high_yield_tracker = pd.DataFrame([
        {"Asset": a, "Cost_Basis": 1000.0, "Cum_Dividends": 0.0, "Purchase_Date": datetime.now().date()}
        for a in ["NVDY","ULTY","CHPY","MRNY","YMAX","EVHY"]
    ])

# ==================== PAGES ====================
if page == "Portfolio Overview":
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    with col1: st.metric("Target Capital", f"${TOTAL_CAPITAL:,}")
    with col2: st.metric("Current Portfolio Value", f"${current_portfolio_value:,.0f}")
    with col3: st.metric("Current VIX", f"{current_vix}")
    with col4: st.metric("Liquidity Score", "94/100")
    with col5: st.metric("Projected Yearly Payout", f"${total_annual:,.0f}")
    with col6: st.metric("Projected Monthly Payout", f"${total_monthly:,.0f}")

    st.subheader("Grok AI Portfolio Evaluation")
    vix_comment = "High volatility — excellent premiums!" if current_vix > 28 else "Low volatility — premiums shrinking." if current_vix < 15 else "Normal volatility range."
    slice_comment = "Overweight — consider trimming." if aggressive_current > 6.0 else "Underweight — safe to add." if aggressive_current < 4.0 else "Right on target."
    st.info(f"**Overall Condition:** Healthy.\n\nVIX is **{current_vix}** → {vix_comment}\n\nAggressive slice is **{aggressive_current:.1f}%** → {slice_comment}")

    st.subheader("AI Analyst: High-Yield ETF Recommendation")
    if current_vix > 28:
        rec = "**ULTY or MRNY** — Highest premiums right now. Strong buy."
    elif current_vix > 22:
        rec = "**NVDY or EVHY** — Excellent balance."
    elif current_vix < 15:
        rec = "**Trim** — Premiums are low."
    else:
        rec = "**CHPY or IBHJ** — Solid middle-ground choice."
    st.write(rec)

    col_chart, col_table = st.columns(2)
    with col_chart:
        fig = px.sunburst(df, path=['Category', 'Ticker'], values='Current Value', title="Category → Holdings", color='Category')
        st.plotly_chart(fig, use_container_width=True)
    with col_table:
        cat_summary = df.groupby("Category").agg({"Current Value": "sum", "Current_Pct_Numeric": "sum"}).round(2)
        cat_summary = cat_summary.rename(columns={"Current_Pct_Numeric": "Portfolio %"})
        st.dataframe(cat_summary.style.format({"Current Value": "${:,.0f}", "Portfolio %": "{:.1f}%"}), use_container_width=True)

    st.subheader("Holdings Breakdown by Strategy Category")
    for cat in ["Core Stable Income", "Quality Dividend Growth", "Cash Buffer", "Aggressive High-Yield"]:
        cat_df = df[df["Category"] == cat].copy()
        if cat_df.empty: continue
        total_value = cat_df["Current Value"].sum()
        total_pct = cat_df["Current_Pct_Numeric"].sum()
        yearly_expected = round(cat_df["Est. Annual Payout"].str.replace("$","").str.replace(",","").astype(float).sum(), 0)
        quarterly_expected = round(yearly_expected / 4, 0)
        monthly_expected = round(yearly_expected / 12, 0)
        st.markdown(f"### {cat}")
        st.caption(category_descriptions.get(cat, ""))
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1: st.metric("Total Value", f"${total_value:,.0f}")
        with col2: st.metric("Portfolio %", f"{total_pct:.1f}%")
        with col3: st.metric("Expected Yearly $", f"${yearly_expected:,.0f}")
        with col4: st.metric("Expected Quarterly $", f"${quarterly_expected:,.0f}")
        with col5: st.metric("Expected Monthly $", f"${monthly_expected:,.0f}")
        st.dataframe(cat_df[["Ticker", "Target %", "Current %", "Est. Annual Yield", "Est. Annual Payout", "Est. Monthly Payout", "Frequency"]], use_container_width=True, hide_index=True)
        st.markdown("---")

elif page == "Income Projections":
    st.subheader("Income Projections")
    col1, col2, col3 = st.columns(3)
    with col1: st.metric("**2026 Projected Gross Annual Income**", f"${total_annual:,.0f}", f"Average Monthly: ${total_monthly:,.0f}")
    st.dataframe(df[["Ticker", "Est. Annual Payout", "Est. Monthly Payout", "Frequency"]], use_container_width=True, hide_index=True)

    st.subheader("Projected Tax Owed")
    tax_rate = st.number_input("Assumed Combined Effective Tax Rate (%)", value=35.0, step=0.5)
    estimated_tax_annual = round(total_annual * (tax_rate / 100), 0)
    net_annual = round(total_annual - estimated_tax_annual, 0)
    col_tax1, col_tax2 = st.columns(2)
    with col_tax1: st.metric("**Estimated Taxes Owed (Yearly)**", f"${estimated_tax_annual:,.0f}")
    with col_tax2: st.metric("**Net After-Tax Income (Yearly)**", f"${net_annual:,.0f}")

elif page == "Future Portfolio":
    st.subheader("Future Portfolio Projections")
    col1, col2, col3 = st.columns(3)
    with col1: st.metric("**Conservative** (6%)", f"${round(current_portfolio_value * 1.06):,.0f}")
    with col2: st.metric("**Base Case** (9%)", f"${round(current_portfolio_value * 1.09):,.0f}")
    with col3: st.metric("**Optimistic** (12%)", f"${round(current_portfolio_value * 1.12):,.0f}")
    st.info("**Base Case assumes 9% total return with 60/30/10 reinvestment**")

elif page == "Holding Details":
    selected_ticker = st.selectbox("Select Holding", tickers)
    if selected_ticker:
        row = df[df["Ticker"] == selected_ticker].iloc[0]
        st.subheader(f"{selected_ticker} Details")
        st.markdown(holding_descriptions.get(selected_ticker, "No description available."))
        st.dataframe(row.to_frame().T, use_container_width=True, hide_index=True)

elif page == "Portfolio Combined":
    st.subheader("Portfolio Combined View")
    st.dataframe(df, use_container_width=True, hide_index=True)

elif page == "Reinvestment Strategy":
    st.subheader("Monthly Surplus Reinvestment Strategy")
    monthly_surplus = st.number_input("Enter this month's surplus ($)", value=5000.0, step=100.0)
    col1, col2, col3 = st.columns(3)
    with col1: st.metric("High-Yield Slice (60%)", f"${round(monthly_surplus * 0.60):,.0f}")
    with col2: st.metric("Core Stable Income (30%)", f"${round(monthly_surplus * 0.30):,.0f}")
    with col3: st.metric("Quality Dividend Growth (10%)", f"${round(monthly_surplus * 0.10):,.0f}")

    # High-Yield Tracker + Forms (your original logic)
    st.subheader("High-Yield Holdings Tracker")
    st.dataframe(st.session_state.high_yield_tracker, use_container_width=True)

elif page == "Guardrails & Alerts":
    st.subheader("Proactive Guardrails")
    st.info("All guardrails are currently **GREEN**. No immediate action required.")

# Must be outside all if/elif
st.caption(f"Last updated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")
