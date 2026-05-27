import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="Grok AI Investment Advisor v2", layout="wide", page_icon="📈", initial_sidebar_state="expanded")

# Tight professional styling
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
    .stSidebar .stRadio label {
        font-size: 1.35rem !important;
        font-weight: 700 !important;
        padding: 14px 0 !important;
        line-height: 1.4;
    }
    .stSidebar .stRadio label div {
        font-size: 1.35rem !important;
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
st.markdown("**$2.1M Portfolio → \~$190k/year** | Built for Jay")

# ==================== PORTFOLIO DATA (unchanged) ====================
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

category_map = { ... }   # (same as before - unchanged)
payout_data = { ... }     # (same as before - unchanged)
category_descriptions = { ... }  # (same)
holding_descriptions = { ... }   # (same)

tickers = list(targets.keys())

@st.cache_data(ttl=60)
def get_live_prices(ticker_list): ...   # (same)
@st.cache_data(ttl=60)
def get_vix(): ...                     # (same)

prices = get_live_prices(tickers)
current_vix = get_vix()

# Build main dataframe (unchanged)
data = []  # ... (same code as before)
df = pd.DataFrame(data)
aggressive_current = df[df["Ticker"].isin(["NVDY","ULTY","CHPY","MRNY","YMAX"])]["Current_Pct_Numeric"].sum()

total_annual = round(df["Est. Annual Payout"].str.replace("$","").str.replace(",","").astype(float).sum(), 0)
total_monthly = round(total_annual / 12, 0)
current_portfolio_value = df['Current Value'].sum()

# Trackers (unchanged - full entry adders restored)
if 'high_yield_tracker' not in st.session_state: ...   # (full code as in previous working version)
if 'core_stable_tracker' not in st.session_state: ...
if 'quality_growth_tracker' not in st.session_state: ...

# ==================== PAGE SELECTION ====================
if page == "Portfolio Overview":
    # (exactly as before - unchanged)

elif page == "Income Projections":
    # (exactly as before - unchanged)

elif page == "Future Portfolio":
    st.subheader("Future Portfolio Outlook")
    st.caption("Long-term growth and income projections assuming surplus is reinvested per your 60/30/10 rule")

    current_value = current_portfolio_value
    current_income = total_annual

    horizons = {
        "1 Year": 1,
        "5 Years": 5,
        "10 Years": 10
    }

    for label, years in horizons.items():
        st.markdown(f"### {label} Outlook")
        col1, col2, col3 = st.columns(3)
        
        # Conservative 6%
        cons_value = round(current_value * (1.06 ** years), 0)
        cons_income = round(current_income * (1.03 ** years), 0)
        with col1:
            st.metric(f"**Conservative** (6% return)", f"${cons_value:,.0f}", f"Income: ${cons_income:,.0f}/yr")
        
        # Base 9%
        base_value = round(current_value * (1.09 ** years), 0)
        base_income = round(current_income * (1.03 ** years), 0)
        with col2:
            st.metric(f"**Base Case** (9% return)", f"${base_value:,.0f}", f"Income: ${base_income:,.0f}/yr")
        
        # Optimistic 12%
        opt_value = round(current_value * (1.12 ** years), 0)
        opt_income = round(current_income * (1.03 ** years), 0)
        with col3:
            st.metric(f"**Optimistic** (12% return)", f"${opt_value:,.0f}", f"Income: ${opt_income:,.0f}/yr")
        
        st.divider()

    # 12-month growth chart (kept for near-term view)
    st.subheader("Next 12 Months – Base Case Growth")
    months = list(range(1, 13))
    base_growth = [current_value * (1 + 0.09 * (m / 12)) for m in months]
    fig = px.line(x=months, y=base_growth, markers=True,
                  labels={"x": "Months Ahead", "y": "Projected Portfolio Value ($)"},
                  title="Portfolio Value Growth Over Next 12 Months (Base Case)")
    st.plotly_chart(fig, use_container_width=True)

    st.info("""
    **Key Assumptions:**
    • Base case = 9% annual total return (capital growth + reinvested income)
    • Income grows \~3% per year (dividend growth + active management)
    • Surplus is reinvested 60/30/10 every month
    • Does NOT include taxes or major market crashes
    """)

elif page == "Holding Details":
    # (unchanged)

elif page == "Portfolio Combined":
    # (unchanged)

elif page == "Reinvestment Strategy":
    # (full working version with all three purchase forms and trackers - unchanged)

elif page == "Guardrails & Alerts":
    # (unchanged)

st.caption(f"Last updated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")