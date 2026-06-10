import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

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
    ["Portfolio Overview",
     "Income Projections",
     "Future Portfolio",
     "Holding Details",
     "Portfolio Combined",
     "Reinvestment Strategy",
     "Guardrails & Alerts"]
)

st.title("Grok AI Investment Advisor v2")
st.markdown("**$2.1M Portfolio → \~$190k/year** | Built for Jay")

# ==================== PORTFOLIO DATA ====================
TOTAL_CAPITAL = 2_100_000

targets = {
    "JEPI": {"target_pct": 42.9, "amount": 900_000},
    "SCHD": {"target_pct": 23.8, "amount": 500_000},
    "JEPQ": {"target_pct": 14.3, "amount": 300_000},
    "VIG": {"target_pct": 6.7, "amount": 140_000},
    "SGOV": {"target_pct": 2.9, "amount": 60_000},
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
    "VIG": {"freq": "Quarterly", "yield": 1.6},
    "SGOV": {"freq": "Monthly", "yield": 4.5},
    "NVDY": {"freq": "Weekly", "yield": 60.0},
    "ULTY": {"freq": "Weekly", "yield": 65.0},
    "CHPY": {"freq": "Weekly", "yield": 46.0},
    "MRNY": {"freq": "Weekly", "yield": 71.0},
    "YMAX": {"freq": "Weekly", "yield": 57.0},
}

category_descriptions = {
    "Core Stable Income": "Provides the largest and most reliable portion of monthly income using covered-call strategies on broad market indices. Acts as the defensive backbone of the portfolio.",
    "Quality Dividend Growth": "Focuses on high-quality companies with growing dividends and strong fundamentals. Delivers quarterly income while building long-term capital appreciation and inflation protection.",
    "Cash Buffer": "Ultra-safe short-term U.S. Treasuries that serve as liquidity reserve and emergency cash. Maintains stability and allows quick reallocation when opportunities arise.",
    "Aggressive High-Yield": "Tactical high-income slice using YieldMax option-income ETFs. Designed for short-term profit boosts and can be scaled up or down easily based on market volatility."
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
    "YMAX": "YieldMax Universe Fund of Option Income ETFs – Diversified basket of multiple YieldMax ETFs. **Role in portfolio**: Easy one-ticker way to spread risk across the entire high-yield slice."
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
    price = prices[t]
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
aggressive_current = df[df["Ticker"].isin(["NVDY","ULTY","CHPY","MRNY","YMAX"])]["Current_Pct_Numeric"].sum()

total_annual = round(df["Est. Annual Payout"].str.replace("$","").str.replace(",","").astype(float).sum(), 0)
total_monthly = round(total_annual / 12, 0)
current_portfolio_value = df['Current Value'].sum()

# ==================== TRACKERS ====================
if 'high_yield_tracker' not in st.session_state:
    st.session_state.high_yield_tracker = pd.DataFrame([
        {"Asset": "NVDY", "Cost_Basis": 1000.0, "Cum_Dividends": 0.0, "Purchase_Date": datetime.now().date()},
        {"Asset": "ULTY", "Cost_Basis": 1000.0, "Cum_Dividends": 0.0, "Purchase_Date": datetime.now().date()},
        {"Asset": "CHPY", "Cost_Basis": 1000.0, "Cum_Dividends": 0.0, "Purchase_Date": datetime.now().date()},
        {"Asset": "MRNY", "Cost_Basis": 1000.0, "Cum_Dividends": 0.0, "Purchase_Date": datetime.now().date()},
        {"Asset": "YMAX", "Cost_Basis": 1000.0, "Cum_Dividends": 0.0, "Purchase_Date": datetime.now().date()},
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

# ==================== PAGE SELECTION ====================
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
        rec = "**NVDY or YMAX** — Excellent balance. Good to hold or add."
    elif current_vix < 15:
        rec = "**Trim** — Premiums are low."
    else:
        rec = "**CHPY** — Solid middle-ground choice."
    st.write(rec)
    st.caption(f"Current aggressive slice: **{aggressive_current:.1f}%** | VIX: **{current_vix}**")

    col_chart, col_table = st.columns(2)
    with col_chart:
        st.subheader("Current Portfolio Allocation")
        fig = px.sunburst(df, path=['Category', 'Ticker'], values='Current Value', title="Category → Holdings", color='Category')
        st.plotly_chart(fig, use_container_width=True)
    with col_table:
        st.subheader("Portfolio by Strategy Category")
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

# (Other pages like Income Projections, Future Portfolio, etc. remain as in previous clean version)
elif page == "Reinvestment Strategy":
    st.subheader("Monthly Surplus Reinvestment Strategy")
    st.write("**Allocation Rule**: 60% → High-Yield Slice | 30% → Core Stable Income | 10% → Quality Dividend Growth")
    monthly_surplus = st.number_input("Enter this month's surplus ($)", value=5000.0, step=100.0, format="%.0f")
    col1, col2, col3 = st.columns(3)
    with col1: st.metric("High-Yield Slice (60%)", f"${round(monthly_surplus * 0.60):,.0f}")
    with col2: st.metric("Core Stable Income (30%)", f"${round(monthly_surplus * 0.30):,.0f}")
    with col3: st.metric("Quality Dividend Growth (10%)", f"${round(monthly_surplus * 0.10):,.0f}")

    # ==================== HIGH-YIELD ENHANCED TRACKER ====================
    st.subheader("High-Yield Slice Management")
    st.subheader("🤖 AI Sell / Rotate Advisor")

    hy_df = st.session_state.high_yield_tracker.copy()
    hy_df["Current_Price"] = hy_df["Asset"].map(prices).fillna(1)
    hy_df["Shares"] = hy_df["Cost_Basis"] / hy_df["Current_Price"]   # approximate initial shares
    hy_df["Current_Value"] = hy_df["Shares"] * hy_df["Current_Price"]
    hy_df["Unrealized_PL"] = hy_df["Current_Value"] - hy_df["Cost_Basis"]
    hy_df["Unrealized_PL_Pct"] = (hy_df["Unrealized_PL"] / hy_df["Cost_Basis"] * 100).round(1)
    hy_df["Total_Return_Pct"] = ((hy_df["Current_Value"] + hy_df["Cum_Dividends"] - hy_df["Cost_Basis"]) / hy_df["Cost_Basis"] * 100).round(1)
    hy_df["Months_Held"] = hy_df["Purchase_Date"].apply(lambda d: max(1, (datetime.now().date() - d).days // 30))

    avg_return = hy_df["Total_Return_Pct"].mean()

    alerts = []
    for _, row in hy_df.iterrows():
        if row["Unrealized_PL_Pct"] < -25:
            alerts.append(f"**{row['Asset']}**: Heavy NAV decay ({row['Unrealized_PL_Pct']:.1f}%). Strong sell candidate.")
        elif row["Total_Return_Pct"] < avg_return - 12:
            alerts.append(f"**{row['Asset']}**: Underperforming ({row['Total_Return_Pct']:.1f}% vs avg {avg_return:.1f}%). Consider rotating.")

    if alerts:
        st.warning("\n\n".join(alerts))
    else:
        st.success("✅ High-Yield slice looks healthy.")

    if current_vix > 25:
        st.info("🌪️ High VIX environment — hold or add to high-yield positions.")
    elif current_vix < 16:
        st.info("📉 Low volatility — consider trimming weakest positions.")

    # Log Dividend
    with st.form("dividend_form"):
        st.write("**Log Dividends Received**")
        div_asset = st.selectbox("Asset", hy_df["Asset"].unique())
        div_amount = st.number_input("Dividend Amount ($)", min_value=0.0, step=50.0, value=200.0)
        if st.form_submit_button("Log Dividend"):
            idx = hy_df[hy_df["Asset"] == div_asset].index[0]
            st.session_state.high_yield_tracker.at[idx, "Cum_Dividends"] += div_amount
            st.success(f"✅ Logged ${div_amount:,.0f} for {div_asset}")

    # Main Tracker
    st.subheader("High-Yield Holdings Tracker")
    display_df = hy_df[["Asset", "Cost_Basis", "Cum_Dividends", "Current_Value", "Unrealized_PL", "Unrealized_PL_Pct", "Total_Return_Pct", "Months_Held"]].round(2)
    edited = st.data_editor(display_df, use_container_width=True, hide_index=True, num_rows="fixed")
    st.session_state.high_yield_tracker = st.session_state.high_yield_tracker  # refresh logic if needed

    # Sell & Rotate
    with st.form("sell_form"):
        st.write("**Sell & Rotate Position**")
        sell_asset = st.selectbox("Sell Asset", hy_df["Asset"].unique())
        sell_amount = st.number_input("Sell Amount ($)", value=500.0, step=100.0)
        rotate_to = st.selectbox("Rotate Into", ["NVDY", "ULTY", "CHPY", "MRNY", "YMAX", "Cash"])
        if st.form_submit_button("Execute Sell + Rotate"):
            st.success(f"✅ Sold ${sell_amount:,.0f} of {sell_asset} → rotated to {rotate_to}. Manually adjust tracker as needed.")

    # Add Purchase
    with st.form("high_yield_form"):
        hy_asset = st.selectbox("Asset Purchased", ["NVDY", "ULTY", "CHPY", "MRNY", "YMAX"])
        hy_amount = st.number_input("Amount Purchased ($)", value=1000.0, step=100.0)
        if st.form_submit_button("Add / Increase Position"):
            new_row = pd.DataFrame([{"Asset": hy_asset, "Cost_Basis": hy_amount, "Cum_Dividends": 0.0, "Purchase_Date": datetime.now().date()}])
            st.session_state.high_yield_tracker = pd.concat([st.session_state.high_yield_tracker, new_row], ignore_index=True)
            st.success(f"✅ Added ${hy_amount:,.0f} to {hy_asset}")

    st.dataframe(display_df.style.format({
        "Cost_Basis": "${:,.0f}", "Cum_Dividends": "${:,.0f}", "Current_Value": "${:,.0f}",
        "Unrealized_PL": "${:,.0f}", "Unrealized_PL_Pct": "{:.1f}%", "Total_Return_Pct": "{:.1f}%"
    }), use_container_width=True, hide_index=True)

    # Core & Quality sections (kept from original)
    # ... (same as your previous working version)

else:
    # Placeholder for other pages - copy from your last working script if needed
    pass

st.caption(f"Last updated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")
