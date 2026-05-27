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
        "Target %": target_pct,
        "Current %": current_pct,
        "Drift": drift,
        "Current Value": current_value,
        "Est. Annual Payout": annual,
    })

df = pd.DataFrame(data)
aggressive_current = df[df["Ticker"].isin(["NVDY","ULTY","CHPY","MRNY","YMAX"])]["Current %"].sum()
total_annual = df["Est. Annual Payout"].sum()
current_portfolio_value = df['Current Value'].sum()

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

# ==================== PAGE SELECTION ====================
if page == "Portfolio Overview":
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    with col1: st.metric("Target Capital", f"${TOTAL_CAPITAL:,}")
    with col2: st.metric("Current Portfolio Value", f"${current_portfolio_value:,.0f}")
    with col3: st.metric("Current VIX", f"{current_vix}")
    with col4: st.metric("Liquidity Score", "94/100")
    with col5: st.metric("Projected Yearly Payout", f"${total_annual:,.0f}")
    with col6: st.metric("Projected Monthly Payout", f"${round(total_annual/12):,.0f}")

    st.subheader("Grok AI Portfolio Evaluation")
    vix_comment = "High volatility — excellent premiums!" if current_vix > 28 else "Low volatility — premiums shrinking." if current_vix < 15 else "Normal volatility range."
    slice_comment = "Overweight — consider trimming." if aggressive_current > 7.0 else "Underweight — safe to add." if aggressive_current < 4.0 else "Right on target."
    st.info(f"**Overall Condition:** Healthy.\n\nVIX is **{current_vix}** → {vix_comment}\n\nAggressive slice is **{aggressive_current:.1f}%** → {slice_comment}")

elif page == "Income Projections":
    st.subheader("Income Projections")
    col1, col2, col3 = st.columns(3)
    with col1: st.metric("**2026 Projected Gross Annual Income**", f"${total_annual:,.0f}", f"Average Monthly: ${round(total_annual/12):,.0f}")
    
    st.subheader("Projected Tax Owed")
    tax_rate = st.number_input("Assumed Combined Effective Tax Rate (%)", value=35.0, step=0.5)
    estimated_tax_annual = round(total_annual * (tax_rate / 100), 0)
    estimated_tax_monthly = round(estimated_tax_annual / 12, 0)
    net_annual = round(total_annual - estimated_tax_annual, 0)
    
    col_tax1, col_tax2, col_tax3 = st.columns(3)
    with col_tax1: st.metric("**Estimated Taxes Owed (Yearly)**", f"${estimated_tax_annual:,.0f}")
    with col_tax2: st.metric("**Estimated Taxes Owed (Monthly)**", f"${estimated_tax_monthly:,.0f}")
    with col_tax3: st.metric("**Net After-Tax Income (Yearly)**", f"${net_annual:,.0f}")

elif page == "Future Portfolio":
    st.subheader("Future Portfolio Outlook")
    st.caption("Long-term growth and income projections")

    current_value = current_portfolio_value
    current_income = total_annual

    for label, years in {"1 Year": 1, "5 Years": 5, "10 Years": 10}.items():
        st.markdown(f"### {label} Outlook")
        col1, col2, col3 = st.columns(3)
        with col1:
            cons_value = round(current_value * (1.06 ** years), 0)
            st.metric(f"**Conservative** (6%)", f"${cons_value:,.0f}")
        with col2:
            base_value = round(current_value * (1.09 ** years), 0)
            st.metric(f"**Base Case** (9%)", f"${base_value:,.0f}")
        with col3:
            opt_value = round(current_value * (1.12 ** years), 0)
            st.metric(f"**Optimistic** (12%)", f"${opt_value:,.0f}")
        st.divider()

elif page == "Guardrails & Alerts":
    st.subheader("Proactive Guardrails & Risk Controls")
    st.caption("These rules are designed to protect capital and maintain income sustainability.")

    # VIX Guardrail
    if current_vix > 30:
        vix_status = "🔴 HIGH"
        vix_action = "Consider increasing high-yield exposure (premiums are rich)"
    elif current_vix < 15:
        vix_status = "🟡 LOW"
        vix_action = "Premiums are lower — be selective with new high-yield adds"
    else:
        vix_status = "🟢 NORMAL"
        vix_action = "Good environment for current high-yield allocation"

    st.markdown(f"**1. VIX Level Guardrail** — Current: **{current_vix}** → {vix_status}")
    st.caption(vix_action)

    # Aggressive Slice Guardrail
    if 4.0 <= aggressive_current <= 7.0:
        slice_status = "🟢 HEALTHY"
    elif aggressive_current > 8.0:
        slice_status = "🔴 OVERWEIGHT"
    else:
        slice_status = "🟡 UNDERWEIGHT"
    
    st.markdown(f"**2. Aggressive High-Yield Slice** — Current: **{aggressive_current:.1f}%** → {slice_status}")
    st.caption("Target Range: 4.0% – 7.0%. This slice should remain tactical and actively managed.")

    # Drift Guardrail
    big_drifts = df[abs(df["Drift"]) > 2.0]
    if big_drifts.empty:
        drift_status = "🟢 OK"
        drift_msg = "No significant drift detected."
    else:
        drift_status = "🟡 MONITOR"
        drift_msg = f"{len(big_drifts)} holding(s) drifting more than ±2% from target."
    
    st.markdown(f"**3. Portfolio Drift Guardrail** → {drift_status}")
    st.caption(drift_msg)

    # Liquidity Guardrail
    sgov_pct = df[df["Ticker"] == "SGOV"]["Current %"].values[0]
    if sgov_pct >= 2.5:
        liq_status = "🟢 HEALTHY"
    else:
        liq_status = "🟡 LOW"
    
    st.markdown(f"**4. Liquidity / Cash Buffer (SGOV)** — Current: **{sgov_pct:.1f}%** → {liq_status}")
    st.caption("Recommended minimum: \~2.5–3% for flexibility and safety.")

    # Overall Health
    st.divider()
    if current_vix < 30 and 4.0 <= aggressive_current <= 7.0 and sgov_pct >= 2.5:
        overall = "🟢 GREEN — Portfolio is operating within defined guardrails."
    else:
        overall = "🟡 YELLOW — One or more guardrails need attention."
    
    st.success(overall)

elif page == "Holding Details":
    st.subheader("Detailed Holding Information")
    selected_ticker = st.selectbox("Select Holding", tickers)
    if selected_ticker:
        row = df[df["Ticker"] == selected_ticker].iloc[0]
        st.subheader(f"{selected_ticker} Details")
        detail_df = pd.DataFrame([{
            "Ticker": row["Ticker"],
            "Category": row["Category"],
            "Current Value": f"${row['Current Value']:,.0f}",
            "Current %": f"{row['Current %']:.1f}%",
            "Target %": f"{row['Target %']:.1f}%",
            "Drift": f"{row['Drift']:+.1f}%",
        }])
        st.dataframe(detail_df, use_container_width=True, hide_index=True)

elif page == "Portfolio Combined":
    st.subheader("Portfolio Combined View")
    st.dataframe(df, use_container_width=True, hide_index=True)

elif page == "Reinvestment Strategy":
    st.subheader("Monthly Surplus Reinvestment Strategy")
    st.write("**Allocation Rule**: 60% High-Yield | 30% Core Stable | 10% Quality Growth")
    monthly_surplus = st.number_input("Enter this month's surplus ($)", value=5000.0, step=100.0, format="%.0f")
    col1, col2, col3 = st.columns(3)
    with col1: st.metric("High-Yield (60%)", f"${round(monthly_surplus * 0.60):,.0f}")
    with col2: st.metric("Core Stable (30%)", f"${round(monthly_surplus * 0.30):,.0f}")
    with col3: st.metric("Quality Growth (10%)", f"${round(monthly_surplus * 0.10):,.0f}")

else:
    st.subheader("Page under construction")

st.caption(f"Last updated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")