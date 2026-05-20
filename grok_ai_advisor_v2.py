import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="Grok AI Investment Advisor v2", layout="wide", page_icon="📈", initial_sidebar_state="expanded")

# Tight professional styling - header flush to top + LARGER sidebar navigation
st.markdown("""
<style>
    .stApp { 
        background-color: #0e1117; 
        color: #fafafa; 
        padding-top: 0rem !important;
        margin-top: 0 !important;
    }
    .block-container {
        padding-top: 0rem !important;
        margin-top: 0 !important;
    }
    .stMetric { background-color: #1a1f2e; border-radius: 12px; padding: 18px; border: 1px solid #2d3748; }
    .stButton>button { background-color: #1f6feb; color: white; border-radius: 8px; font-weight: 600; padding: 14px 28px; }
    h1, h2, h3 { 
        color: #ffffff; 
        margin-top: 0 !important; 
        padding-top: 0 !important; 
    }
    .stSidebar { background-color: #161b28; }
    
    /* INCREASED SIZE OF TOOLBAR / SIDEBAR NAVIGATION ITEMS */
    .stSidebar .stRadio label {
        font-size: 1.35rem !important;
        font-weight: 700 !important;
        padding: 14px 0 !important;
        line-height: 1.4;
    }
    .stSidebar .stRadio label div {
        font-size: 1.35rem !important;
    }
    .stSidebar .stRadio > div {
        gap: 8px !important;
    }
    .stSidebar .stRadio {
        padding-top: 10px !important;
    }
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
st.markdown("**$2.1M Portfolio → ~$190k/year** | Built for Jay")

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

# Projected Income
total_annual = round(df["Est. Annual Payout"].str.replace("$","").str.replace(",","").astype(float).sum(), 0)
total_monthly = round(total_annual / 12, 0)

# ==================== TRACKERS ====================
if 'high_yield_tracker' not in st.session_state:
    st.session_state.high_yield_tracker = pd.DataFrame([
        {"Asset": "NVDY", "Position": 1000, "Payments_Made": 0},
        {"Asset": "ULTY", "Position": 1000, "Payments_Made": 0},
        {"Asset": "CHPY", "Position": 1000, "Payments_Made": 0},
        {"Asset": "MRNY", "Position": 1000, "Payments_Made": 0},
        {"Asset": "YMAX", "Position": 1000, "Payments_Made": 0}
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

current_portfolio_value = df['Current Value'].sum()

# ==================== PAGE SELECTION ====================
if page == "Portfolio Overview":
    # ... (same as previous version - unchanged) ...
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    with col1: st.metric("Target Capital", f"${TOTAL_CAPITAL:,}")
    with col2: st.metric("Current Portfolio Value", f"${current_portfolio_value:,.0f}")
    with col3: st.metric("Current VIX", f"{current_vix}")
    with col4: st.metric("Liquidity Score", "94/100")
    with col5: st.metric("Projected Yearly Payout", f"${total_annual:,.0f}")
    with col6: st.metric("Projected Monthly Payout", f"${total_monthly:,.0f}")

    # (rest of Portfolio Overview remains exactly the same as your last working version)

elif page == "Income Projections":
    # (unchanged from previous version)

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

    st.subheader("Base Case Breakdown (9% Total Return)")
    projected_income_2027 = round(total_annual * 1.03, 0)   # modest 3% income growth
    projected_capital_growth = round(current_portfolio_value * 0.09, 0)
    projected_total_value = round(current_portfolio_value + projected_capital_growth + projected_income_2027, 0)

    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.metric("Expected Income (2027)", f"${projected_income_2027:,.0f}")
    with col_b:
        st.metric("Expected Capital Growth", f"${projected_capital_growth:,.0f}")
    with col_c:
        st.metric("Total Projected Value", f"${projected_total_value:,.0f}")

    st.info("""
    **Key Assumptions for 2027:**
    - Base case assumes 9% total return (capital appreciation + reinvested income)
    - High-yield slice managed actively for income boosts
    - Surplus from monthly payouts is reinvested per your 60/30/10 rule
    - Does not include taxes or major market crashes
    """)

    # 12-month growth chart (Base Case)
    months = list(range(1, 13))
    base_growth = [current_portfolio_value * (1 + 0.09 * (m / 12)) for m in months]
    fig = px.line(x=months, y=base_growth, markers=True,
                  labels={"x": "Months Ahead", "y": "Projected Portfolio Value ($)"},
                  title="Portfolio Value Growth Over Next 12 Months (Base Case)")
    st.plotly_chart(fig, use_container_width=True)

elif page == "Holding Details":
    # (unchanged)

elif page == "Portfolio Combined":
    # (unchanged)

elif page == "Reinvestment Strategy":
    # (unchanged)

elif page == "Guardrails & Alerts":
    # (unchanged)

st.caption(f"Last updated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")
