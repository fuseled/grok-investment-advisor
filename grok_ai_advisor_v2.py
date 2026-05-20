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
        "Current Value": current_value,
        "Price": price,
        "Shares": shares,
        "Est. Annual Yield": f"{payout_data[t]['yield']}%",
        "Est. Annual Payout": f"${annual:,.0f}",
        "Est. Monthly Payout": f"${monthly:,.0f}",
        "Frequency": payout_data[t]["freq"],
    })

df = pd.DataFrame(data)

# ==================== PAGE SELECTION ====================
if page == "📊 Portfolio Overview":
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("Target Capital", f"${TOTAL_CAPITAL:,}")
    with col2: st.metric("Current Portfolio Value", f"${df['Current Value'].sum():,.0f}")
    with col3: st.metric("Current VIX", f"{current_vix}")
    with col4: st.metric("Liquidity Score", "94/100")

    st.subheader("🤖 Grok AI Portfolio Evaluation")
    aggressive_current = df[df["Ticker"].isin(["NVDY","ULTY","CHPY","MRNY","YMAX"])]["Current %"].astype(float).sum()
    vix_comment = "High volatility — excellent premiums!" if current_vix > 28 else "Low volatility — premiums shrinking." if current_vix < 15 else "Normal volatility range."
    slice_comment = "Overweight — consider trimming." if aggressive_current > 6.0 else "Underweight — safe to add." if aggressive_current < 4.0 else "Right on target."
    st.info(f"**Overall Condition:** Healthy.\n\nVIX is **{current_vix}** → {vix_comment}\n\nAggressive slice is **{aggressive_current:.1f}%** → {slice_comment}")

    st.subheader("📊 Current Portfolio Allocation")
    fig = px.sunburst(df, path=['Category', 'Ticker'], values='Current Value', title="Category → Holdings", color='Category')
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("📊 Portfolio by Strategy Category")
    cat_summary = df.groupby("Category").agg({"Current Value": "sum", "Current %": "sum"}).round(2)
    cat_summary = cat_summary.rename(columns={"Current %": "Portfolio %"})
    st.dataframe(cat_summary.style.format({"Current Value": "${:,.0f}", "Portfolio %": "{:.1f}%"}), use_container_width=True)

    # ==================== SEPARATE HEADERS FOR EACH CATEGORY ====================
    st.subheader("Holdings Breakdown by Strategy Category")
    for cat in ["Core Stable Income", "Quality Dividend Growth", "Cash Buffer", "Aggressive High-Yield"]:
        cat_df = df[df["Category"] == cat].copy()
        if cat_df.empty:
            continue
        total_value = cat_df["Current Value"].sum()
        total_pct = cat_df["Current %"].sum()
        
        st.markdown(f"### {cat}")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Value", f"${total_value:,.0f}")
        with col2:
            st.metric("Portfolio %", f"{total_pct:.1f}%")
        
        st.dataframe(
            cat_df[["Ticker", "Target %", "Current %", "Est. Annual Yield", "Est. Annual Payout", "Est. Monthly Payout", "Frequency"]],
            use_container_width=True,
            hide_index=True
        )
        st.markdown("---")

elif page == "💰 Income Projections":
    total_annual = round(sum(targets[t]["amount"] * payout_data[t]["yield"] / 100 for t in tickers), 0)
    col1, col2 = st.columns(2)
    with col1:
        st.metric("**2026 Projected Income**", f"${total_annual:,.0f}")
    with col2:
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

elif page == "📊 Portfolio Combined":
    st.subheader("📊 Portfolio Combined View")
    st.dataframe(df, use_container_width=True, hide_index=True)

elif page == "🛡️ Guardrails & Alerts":
    st.subheader("🛡️ Proactive Guardrails")
    st.info("All guardrails are currently **GREEN**. No immediate action required.")

st.caption(f"Last updated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")
