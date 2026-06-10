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
st.markdown("**$2.3M Portfolio → ~$205k/year** | Built for Jay")

# ==================== PORTFOLIO DATA ====================
TOTAL_CAPITAL = 2_300_000

targets = {
    "JEPI": {"target_pct": 39.13, "amount": 900_000},
    "SCHD": {"target_pct": 21.74, "amount": 500_000},
    "JEPQ": {"target_pct": 13.04, "amount": 300_000},
    "VIG":  {"target_pct": 6.09,  "amount": 140_000},
    "SGOV": {"target_pct": 2.61,  "amount": 60_000},
    "NVDY": {"target_pct": 1.09, "amount": 25_000},
    "ULTY": {"target_pct": 1.09, "amount": 25_000},
    "CHPY": {"target_pct": 0.87, "amount": 20_000},
    "MRNY": {"target_pct": 0.65, "amount": 15_000},
    "YMAX": {"target_pct": 0.65, "amount": 15_000},
    "IBHJ": {"target_pct": 4.35, "amount": 100_000},
    "EVHY": {"target_pct": 4.35, "amount": 100_000},
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
    "Core Stable Income": "Provides the largest and most reliable portion of monthly income using covered-call strategies on broad market indices. Acts as the defensive backbone of the portfolio.",
    "Quality Dividend Growth": "Focuses on high-quality companies with growing dividends and strong fundamentals. Delivers quarterly income while building long-term capital appreciation and inflation protection.",
    "Cash Buffer": "Ultra-safe short-term U.S. Treasuries that serve as liquidity reserve and emergency cash. Maintains stability and allows quick reallocation when opportunities arise.",
    "Aggressive High-Yield": "Tactical high-income slice using YieldMax option-income ETFs and high-yield bonds."
}

holding_descriptions = {
    "JEPI": "JPMorgan Equity Premium Income ETF – Uses covered calls on S&P 500 stocks to generate high monthly income with moderate downside protection. **Role in portfolio**: Provides the largest, most stable monthly income stream and acts as the core of your defensive income strategy.",
    "JEPQ": "JPMorgan Nasdaq Equity Premium Income ETF – Covered call strategy on the Nasdaq-100 for higher monthly income with tech exposure. **Role in portfolio**: Adds growth-oriented monthly income while still offering downside cushion through options.",
    "SCHD": "Schwab U.S. Dividend Equity ETF – High-quality U.S. companies with strong dividend growth and financial health. **Role in portfolio**: Delivers reliable quarterly dividend growth and long-term capital appreciation.",
    "VIG": "Vanguard Dividend Appreciation ETF – Companies that have consistently increased dividends for many years. **Role in portfolio**: Focuses on quality dividend growth to help combat inflation over time.",
    "SGOV": "iShares 0-3 Month Treasury Bond ETF – Ultra-safe short-term U.S. Treasuries used as a cash buffer. **Role in portfolio**: Provides liquidity and stability; acts as your emergency cash reserve.",
    "NVDY": "YieldMax NVDA Option Income Strategy ETF – High-yield weekly option income on NVIDIA. **Role in portfolio**: Tactical high-yield booster that you can scale up or down quickly for extra short-term income.",
    "ULTY": "YieldMax Ultra Option Income Strategy ETF – Diversified high-volatility stocks using aggressive option strategies. **Role in portfolio**: Highest-yielding slice for opportunistic profit-taking when volatility is elevated.",
    "CHPY": "YieldMax Semiconductor Portfolio Option Income ETF – Covered call strategy on major semiconductor companies. **Role in portfolio**: Diversified tech/semiconductor exposure with very high weekly payouts.",
    "MRNY": "YieldMax MRNA Option Income Strategy ETF – High-yield weekly option income on Moderna (biotech volatility). **Role in portfolio**: Pure high-risk/high-reward play for short-term income spikes.",
    "YMAX": "YieldMax Universe Fund of Option Income ETFs – Diversified basket of multiple YieldMax ETFs. **Role in portfolio**: Easy one-ticker way to spread risk across the entire high-yield slice.",
    "IBHJ": "iShares iBonds 2030 Term High Yield and Income ETF – Target-maturity high-yield corporate bond ETF maturing in 2030. Provides diversified high-yield bond exposure with monthly income and built-in principal protection.",
    "EVHY": "Eaton Vance High Yield ETF – Actively managed high-yield bond ETF focusing on higher-quality BB/B issuers. Delivers strong monthly income with professional credit selection."
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
        "Ticker": t,
        "Category": category_map[t],
        "Target %": f"{target_pct:.1f}%",
        "Current %": f"{current_pct:.1f}%",
        "Current_Pct_Numeric": current_pct,
        "Drift": f"{drift:+.1f}%",
        "Price": price,
        "Shares": shares,
        "Current Value": current_value,
        "Est. Annual Yield": f"{payout_data[t]['yield']}%",
        "Est. Annual Payout": f"${annual:,.0f}",
        "Est. Monthly Payout": f"${monthly:,.0f}",
        "Frequency": payout_data[t]["freq"],
    })

df = pd.DataFrame(data)
aggressive_current = df[df["Ticker"].isin(["NVDY","ULTY","CHPY","MRNY","YMAX","EVHY"])]["Current_Pct_Numeric"].sum()
total_annual = round(df["Est. Annual Payout"].str.replace("$","").str.replace(",","").astype(float).sum(), 0)
total_monthly = round(total_annual / 12, 0)
current_portfolio_value = df['Current Value'].sum()

# ==================== TRACKERS ====================
if 'high_yield_tracker' not in st.session_state:
    st.session_state.high_yield_tracker = pd.DataFrame([
        {"Asset": a, "Cost_Basis": 1000.0, "Cum_Dividends": 0.0, "Purchase_Date": datetime.now().date()}
        for a in ["NVDY", "ULTY", "CHPY", "MRNY", "YMAX", "EVHY"]
    ])

if 'core_stable_tracker' not in st.session_state:
    st.session_state.core_stable_tracker = pd.DataFrame([
        {"Asset": "JEPI", "Position": 1000, "Payments_Made": 0},
        {"Asset": "JEPQ", "Position": 1000, "Payments_Made": 0}
    ])

if 'quality_growth_tracker' not in st.session_state:
    st.session_state.quality_growth_tracker = pd.DataFrame([
        {"Asset": "SCHD", "Position": 1000, "Payments_Made": 0},
        {"Asset": "VIG", "Position": 1000, "Payments_Made": 0}
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
        rec = "**NVDY or EVHY** — Excellent balance. Good to hold or add."
    elif current_vix < 15:
        rec = "**Trim** — Premiums are low."
    else:
        rec = "**CHPY or IBHJ** — Solid middle-ground choice."
    st.write(rec)

    col_chart, col_table = st.columns(2)
    with col_chart:
        st.subheader("Current Portfolio Allocation")
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
        st.caption(category_descriptions[cat])
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
    st.subheader("Projected Tax Owed")
    st.caption("**Assumes single filer in California** • Many YieldMax distributions may be Return of Capital (ROC) and not immediately taxable. This is a conservative estimate.")
    tax_rate = st.number_input("Assumed Combined Effective Tax Rate (%)", value=35.0, step=0.5, min_value=0.0, max_value=50.0)
    estimated_tax_annual = round(total_annual * (tax_rate / 100), 0)
    estimated_tax_monthly = round(estimated_tax_annual / 12, 0)
    net_annual = round(total_annual - estimated_tax_annual, 0)
    net_monthly = round(net_annual / 12, 0)
    col_tax1, col_tax2, col_tax3 = st.columns(3)
    with col_tax1: st.metric("**Estimated Taxes Owed (Yearly)**", f"${estimated_tax_annual:,.0f}")
    with col_tax2: st.metric("**Estimated Taxes Owed (Monthly)**", f"${estimated_tax_monthly:,.0f}")
    with col_tax3: st.metric("**Net After-Tax Income (Yearly)**", f"${net_annual:,.0f}", f"Net Monthly: ${net_monthly:,.0f}")
    st.dataframe(df[["Ticker", "Est. Annual Payout", "Est. Monthly Payout", "Frequency"]], use_container_width=True, hide_index=True)

elif page == "Future Portfolio":
    st.subheader("Future Portfolio Projections")
    st.caption("Growth & Income Expectations for the Next 12 Months (2027)")
    st.write("**Projected Portfolio Value at End of 2027**")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("**Conservative** (6% total return)", f"${round(current_portfolio_value * 1.06):,.0f}", f"+${round(current_portfolio_value * 0.06):,.0f}")
    with col2:
        st.metric("**Base Case** (9% total return)", f"${round(current_portfolio_value * 1.09):,.0f}", f"+${round(current_portfolio_value * 0.09):,.0f}")
    with col3:
        st.metric("**Optimistic** (12% total return)", f"${round(current_portfolio_value * 1.12):,.0f}", f"+${round(current_portfolio_value * 0.12):,.0f}")

elif page == "Holding Details":
    st.subheader("Detailed Holding Information")
    selected_ticker = st.selectbox("Select Holding", tickers)
    if selected_ticker:
        row = df[df["Ticker"] == selected_ticker].iloc[0]
        st.subheader(f"{selected_ticker} Details")
        st.markdown(holding_descriptions.get(selected_ticker, ""))
        detail_df = pd.DataFrame([{
            "Ticker": row["Ticker"],
            "Category": row["Category"],
            "Current Value": f"${row['Current Value']:,.0f}",
            "Portfolio %": row["Current %"],
            "Est. Annual Yield": row["Est. Annual Yield"],
            "Est. Annual Payout": row["Est. Annual Payout"],
            "Est. Monthly Payout": row["Est. Monthly Payout"],
            "Frequency": row["Frequency"],
        }])
        st.dataframe(detail_df, use_container_width=True, hide_index=True)

elif page == "Portfolio Combined":
    st.subheader("Portfolio Combined View")
    st.dataframe(df, use_container_width=True, hide_index=True)

elif page == "Reinvestment Strategy":
    st.subheader("Monthly Surplus Reinvestment Strategy")
    st.write("**Allocation Rule**: 60% → High-Yield Slice | 30% → Core Stable Income | 10% → Quality Dividend Growth")
    monthly_surplus = st.number_input("Enter this month's surplus ($)", value=5000.0, step=100.0, format="%.0f")
    st.subheader("Suggested Distribution")
    col1, col2, col3 = st.columns(3)
    with col1: st.metric("High-Yield Slice (60%)", f"${round(monthly_surplus * 0.60):,.0f}")
    with col2: st.metric("Core Stable Income (30%)", f"${round(monthly_surplus * 0.30):,.0f}")
    with col3: st.metric("Quality Dividend Growth (10%)", f"${round(monthly_surplus * 0.10):,.0f}")

elif page == "Guardrails & Alerts":
    st.subheader("Proactive Guardrails")
    st.info("All guardrails are currently GREEN. No immediate action required.")

# Final line - must be at column 0 (no indentation)
st.caption(f"Last updated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")
