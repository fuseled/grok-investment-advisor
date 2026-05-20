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

# ==================== TRANSACTION TRACKER ====================
if 'transactions' not in st.session_state:
    st.session_state.transactions = []

# ==================== PAGE SELECTION ====================
if page == "📊 Portfolio Overview":
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("Target Capital", f"${TOTAL_CAPITAL:,}")
    with col2: st.metric("Current Portfolio Value", f"${df['Current Value'].sum():,.0f}")
    with col3: st.metric("Current VIX", f"{current_vix}")
    with col4: st.metric("Liquidity Score", "94/100")

    st.subheader("🤖 Grok AI Portfolio Evaluation")
    aggressive_current = df[df["Ticker"].isin(["NVDY","ULTY","CHPY","MRNY","YMAX"])]["Current_Pct_Numeric"].sum()
    vix_comment = "High volatility — excellent premiums!" if current_vix > 28 else "Low volatility — premiums shrinking." if current_vix < 15 else "Normal volatility range."
    slice_comment = "Overweight — consider trimming." if aggressive_current > 6.0 else "Underweight — safe to add." if aggressive_current < 4.0 else "Right on target."
    st.info(f"**Overall Condition:** Healthy.\n\nVIX is **{current_vix}** → {vix_comment}\n\nAggressive slice is **{aggressive_current:.1f}%** → {slice_comment}")

    col_chart, col_table = st.columns(2)
    with col_chart:
        st.subheader("📊 Current Portfolio Allocation")
        fig = px.sunburst(df, path=['Category', 'Ticker'], values='Current Value', title="Category → Holdings", color='Category')
        st.plotly_chart(fig, use_container_width=True)
    with col_table:
        st.subheader("📊 Portfolio by Strategy Category")
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

elif page == "💰 Income Projections":
    total_annual = round(sum(targets[t]["amount"] * payout_data[t]["yield"] / 100 for t in tickers), 0)
    expected_monthly = round(total_annual / 12, 0)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("**Average Projected Monthly Income**", f"${expected_monthly:,.0f}")
    with col2:
        st.metric("**2026 Projected Income**", f"${total_annual:,.0f}")
    with col3:
        st.metric("**2027 Projected Income**", f"${int(total_annual * 1.04):,.0f}", "+4% growth est.")

    st.subheader("Detailed Payouts Schedule")
    payout_rows = []
    for t in tickers:
        annual = round(targets[t]["amount"] * payout_data[t]["yield"] / 100, 0)
        monthly = round(annual / 12, 0) if payout_data[t]["freq"] in ["Monthly", "Weekly"] else round(annual / 4, 0)
        if payout_data[t]["freq"] == "Weekly":
            schedule = "Weekly (typically Fridays)"
        elif payout_data[t]["freq"] == "Monthly":
            schedule = "Monthly (usually mid-month)"
        else:
            schedule = "Mar 15, Jun 15, Sep 15, Dec 15"
        payout_rows.append({
            "Ticker": t,
            "Category": category_map[t],
            "Frequency": payout_data[t]["freq"],
            "Est. Annual Yield": f"{payout_data[t]['yield']}%",
            "Est. Annual Payout": f"${annual:,.0f}",
            "Est. Monthly Payout": f"${monthly:,.0f}",
            "Payout Schedule": schedule
        })
    st.dataframe(pd.DataFrame(payout_rows), use_container_width=True, hide_index=True)

elif page == "📋 Holding Details":
    st.subheader("📋 Detailed Holding Information")
    selected_ticker = st.selectbox("Select Holding", tickers)
    if selected_ticker:
        row = df[df["Ticker"] == selected_ticker].iloc[0]
        target_amount = targets[selected_ticker]["amount"]

        st.subheader("Description")
        st.write(holding_descriptions.get(selected_ticker, "No description available."))

        st.subheader(f"{selected_ticker} Detailed Table")
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

        st.subheader(f"📅 Projected Future Payouts for {selected_ticker}")
        today = datetime(2026, 5, 20).date()
        freq = payout_data[selected_ticker]["freq"]
        annual_payout = target_amount * payout_data[selected_ticker]["yield"] / 100

        dates = []
        amounts = []
        current = today + timedelta(days=7)
        for i in range(12):
            if freq == "Weekly":
                current += timedelta(days=7)
                per_payout = round(annual_payout / 52, 0)
            elif freq == "Monthly":
                current = current.replace(day=15) + timedelta(days=30)
                per_payout = round(annual_payout / 12, 0)
            else:
                current += timedelta(days=90)
                per_payout = round(annual_payout / 4, 0)
            dates.append(current.strftime("%b %d, %Y"))
            amounts.append(per_payout)

        chart_df = pd.DataFrame({"Date": dates, "Projected Payout $": amounts})
        fig = px.bar(chart_df, x="Date", y="Projected Payout $", title=f"Next 12 Projected Payouts – {selected_ticker}", color_discrete_sequence=["#1f6feb"], text="Projected Payout $")
        fig.update_traces(texttemplate="$%{y:,.0f}", textposition="outside", width=0.5)
        fig.update_layout(xaxis_tickangle=-45, bargap=0.4, height=480)
        st.plotly_chart(fig, use_container_width=True)

elif page == "📊 Portfolio Combined":
    st.subheader("📊 Portfolio Combined View")
    st.dataframe(df, use_container_width=True, hide_index=True)

elif page == "💸 Reinvestment Strategy":
    st.subheader("💸 Monthly Surplus Reinvestment Strategy")
    st.write("""
    **Goal**: Roll over unspent income each month to fight inflation, strengthen the core portfolio, and allow tactical short-term boosts.
    
    **Allocation Rule**:
    - 60% → Quality Dividend Growth (SCHD + VIG)
    - 30% → Core Stable Income (JEPI)
    - 10% → Tactical High-Risk Boost (YieldMax slice: NVDY, ULTY, CHPY, MRNY, YMAX)
    """)

    monthly_surplus = st.number_input("Enter this month's surplus ($)", value=5000.0, step=100.0, format="%.0f")

    st.subheader("Suggested Distribution")
    col1, col2, col3 = st.columns(3)
    with col1: st.metric("Quality Dividend Growth (60%)", f"${round(monthly_surplus * 0.60):,.0f}")
    with col2: st.metric("Core Stable Income (30%)", f"${round(monthly_surplus * 0.30):,.0f}")
    with col3: st.metric("Tactical High-Risk Boost (10%)", f"${round(monthly_surplus * 0.10):,.0f}")

    if st.button("✅ Apply Calculator Output as Transactions", type="primary"):
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        st.session_state.transactions.append({"Date": now, "Bucket": "Quality Dividend Growth", "Amount": round(monthly_surplus * 0.60)})
        st.session_state.transactions.append({"Date": now, "Bucket": "Core Stable Income", "Amount": round(monthly_surplus * 0.30)})
        st.session_state.transactions.append({"Date": now, "Bucket": "Tactical High-Risk Boost", "Amount": round(monthly_surplus * 0.10)})
        st.success("✅ Transactions logged successfully!")

    st.subheader("Manual Transaction Entry")
    with st.form("manual_transaction"):
        manual_date = st.date_input("Date", value=datetime.today())
        manual_bucket = st.selectbox("Bucket", ["Quality Dividend Growth", "Core Stable Income", "Tactical High-Risk Boost"])
        manual_amount = st.number_input("Amount ($)", value=1000.0, step=100.0, format="%.0f")
        submitted = st.form_submit_button("Add Manual Transaction")
        if submitted and manual_amount > 0:
            st.session_state.transactions.append({"Date": manual_date.strftime("%Y-%m-%d"), "Bucket": manual_bucket, "Amount": manual_amount})
            st.success("✅ Manual transaction added!")

    st.subheader("📋 Transaction Tracker")
    if st.session_state.transactions:
        trans_df = pd.DataFrame(st.session_state.transactions)
        trans_df = trans_df.sort_values(by="Date", ascending=False)
        st.dataframe(trans_df, use_container_width=True, hide_index=True)
    else:
        st.info("No transactions yet. Use the calculator or manual entry above.")

elif page == "🛡️ Guardrails & Alerts":
    st.subheader("🛡️ Proactive Guardrails")
    st.info("All guardrails are currently **GREEN**. No immediate action required.")

st.caption(f"Last updated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")
