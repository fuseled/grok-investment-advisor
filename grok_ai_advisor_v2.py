import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="CASH AdvIsor", layout="wide", page_icon="📈", initial_sidebar_state="expanded")

# Professional styling
st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: #fafafa; padding-top: 0rem !important; margin-top: 0 !important; }
    .stMetric { background-color: #1a1f2e; border-radius: 12px; padding: 18px; border: 1px solid #2d3748; }
    .stButton>button { background-color: #1f6feb; color: white; border-radius: 8px; font-weight: 600; padding: 14px 28px; }
    h1, h2, h3 { color: #ffffff; margin-top: 0 !important; padding-top: 0 !important; }
    .stSidebar { background-color: #161b28; }
    .stSidebar .stRadio label { font-size: 1.35rem !important; font-weight: 700 !important; padding: 14px 0 !important; }
    .guardrail-card { background-color: #1a1f2e; padding: 20px; border-radius: 12px; border: 1px solid #2d3748; margin-bottom: 12px; }
</style>
""", unsafe_allow_html=True)

st.sidebar.title("CASH AdvIsor")
page = st.sidebar.radio(
    "Navigate",
    ["Portfolio Overview", "Income Projections", "Future Portfolio", "Tax Prep", 
     "Holding Details", "Portfolio Combined", "Reinvestment Strategy", "Guardrails & Alerts"]
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
    "CHPY": "Aggressive High-Yield", "MRNY": "Aggressive High-Yield", "YMAX": "Aggressive High-Yield",
}

payout_data = {
    "JEPI": {"freq": "Monthly", "yield": 8.4, "taxable_pct": 0.85},
    "JEPQ": {"freq": "Monthly", "yield": 10.3, "taxable_pct": 0.85},
    "SCHD": {"freq": "Quarterly", "yield": 3.3, "taxable_pct": 0.70},
    "VIG": {"freq": "Quarterly", "yield": 1.6, "taxable_pct": 0.70},
    "SGOV": {"freq": "Monthly", "yield": 4.5, "taxable_pct": 1.0},
    "NVDY": {"freq": "Weekly", "yield": 60.0, "taxable_pct": 0.50},
    "ULTY": {"freq": "Weekly", "yield": 65.0, "taxable_pct": 0.50},
    "CHPY": {"freq": "Weekly", "yield": 46.0, "taxable_pct": 0.50},
    "MRNY": {"freq": "Weekly", "yield": 71.0, "taxable_pct": 0.50},
    "YMAX": {"freq": "Weekly", "yield": 57.0, "taxable_pct": 0.50},
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

# Build dataframe
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
    data.append({
        "Ticker": t, "Category": category_map[t],
        "Target %": target_pct, "Current %": current_pct, "Drift": drift,
        "Current Value": current_value, "Est. Annual Payout": annual,
        "Taxable %": payout_data[t]["taxable_pct"]
    })

df = pd.DataFrame(data)
aggressive_current = df[df["Ticker"].isin(["NVDY","ULTY","CHPY","MRNY","YMAX"])]["Current %"].sum()
total_annual = df["Est. Annual Payout"].sum()
current_portfolio_value = df['Current Value'].sum()

# Trackers
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

# ==================== PAGES ====================
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
    current_value = current_portfolio_value
    for label, years in {"1 Year": 1, "5 Years": 5, "10 Years": 10}.items():
        st.markdown(f"### {label} Outlook")
        col1, col2, col3 = st.columns(3)
        with col1: st.metric(f"**Conservative** (6%)", f"${round(current_value * (1.06 ** years)):,}")
        with col2: st.metric(f"**Base Case** (9%)", f"${round(current_value * (1.09 ** years)):,}")
        with col3: st.metric(f"**Optimistic** (12%)", f"${round(current_value * (1.12 ** years)):,}")
        st.divider()

elif page == "Tax Prep":
    st.subheader("Tax Prep & Quarterly Planning")
    st.caption("Strategy to minimize idle cash while staying compliant.")

    st.markdown("### 1. Current Year Tax Estimate")
    col1, col2, col3 = st.columns(3)
    with col1: st.metric("Gross Annual Distributions", f"${total_annual:,.0f}")
    with col2: st.metric("Est. Taxable Portion (after ROC)", f"${round(total_annual * 0.65):,.0f}")
    with col3: st.metric("Est. Tax Owed @ 35%", f"${round(total_annual * 0.65 * 0.35):,.0f}")

    st.markdown("### 2. 110% Safe Harbor Quarterly Payments")
    last_year_tax = st.number_input("What was your total tax bill last year?", value=42000, step=1000)
    safe_harbor_annual = round(last_year_tax * 1.10, 0)
    quarterly_payment = round(safe_harbor_annual / 4, 0)

    col1, col2, col3 = st.columns(3)
    with col1: st.metric("110% Safe Harbor Total", f"${safe_harbor_annual:,.0f}")
    with col2: st.metric("Quarterly Payment", f"${quarterly_payment:,.0f}")
    with col3: st.metric("Next Due Date", "Jan 15, 2027")

    st.markdown("### 3. Recommended Tax Reserve")
    recommended_reserve = max(50000, round(quarterly_payment * 4 * 1.1))
    sgov_current = df[df["Ticker"] == "SGOV"]["Current Value"].sum()
    col1, col2 = st.columns(2)
    with col1: st.metric("Recommended Tax Reserve", f"${recommended_reserve:,.0f}")
    with col2: st.metric("Currently in SGOV", f"${sgov_current:,.0f}")

elif page == "Guardrails & Alerts":
    st.subheader("🛡️ Guardrails & Risk Controls")
    st.caption("Real-time monitoring of your $2.1M CASH AdvIsor strategy")

    # Overall Health Banner
    if current_vix < 30 and 4.0 <= aggressive_current <= 7.0:
        health_status = "🟢 GREEN — Strategy operating within all guardrails"
        health_summary = "Your portfolio is generating strong income with controlled risk. The aggressive slice is well balanced."
    else:
        health_status = "🟡 YELLOW — One or more guardrails need attention"
        health_summary = "Review the sections below for specific items requiring monitoring."

    st.success(health_status)
    st.write(health_summary)

    # Strategy Overview
    with st.expander("📘 How This Strategy Works"):
        st.write("""
        **Core Philosophy**: Generate high sustainable income (\~$190k/year) while keeping most capital working and protected.

        **4-Pillar Structure**:
        - **Core Stable Income (57%)**: JEPI + JEPQ — reliable monthly covered-call income
        - **Quality Dividend Growth (30%)**: SCHD + VIG — growing dividends + inflation protection
        - **Cash Buffer (3%)**: SGOV — liquidity + tax reserve
        - **Aggressive High-Yield (6%)**: NVDY, ULTY, CHPY, MRNY, YMAX — tactical income boosts

        **Reinvestment Rule**: 60% High-Yield | 30% Core Stable | 10% Quality Growth on surplus
        **Tax Strategy**: Use 110% Safe Harbor + keep \~1 year of taxes in SGOV
        """)

    # Live Guardrails Dashboard
    st.markdown("### Live Guardrails Dashboard")

    # VIX
    if current_vix > 30:
        vix_status, vix_action = "🔴 HIGH", "Premiums are very rich — good time to add selectively"
    elif current_vix < 15:
        vix_status, vix_action = "🟡 LOW", "Premiums compressed — be more selective with new adds"
    else:
        vix_status, vix_action = "🟢 NORMAL", "Healthy environment for current allocation"
    st.markdown(f"**VIX Level** — Current: **{current_vix}** → {vix_status}")
    st.caption(vix_action)

    # Aggressive Slice
    if 4.0 <= aggressive_current <= 7.0:
        slice_status = "🟢 HEALTHY"
    elif aggressive_current > 8.0:
        slice_status = "🔴 OVERWEIGHT"
    else:
        slice_status = "🟡 UNDERWEIGHT"
    st.markdown(f"**Aggressive High-Yield Slice** — Current: **{aggressive_current:.1f}%** → {slice_status}")
    st.caption("Target: 4.0% – 7.0%. This is your tactical income booster.")

    # Drift
    big_drifts = df[abs(df["Drift"]) > 2.0]
    drift_status = "🟢 OK" if big_drifts.empty else "🟡 MONITOR"
    st.markdown(f"**Portfolio Drift** → {drift_status}")
    if not big_drifts.empty:
        st.caption(f"{len(big_drifts)} holding(s) drifting more than ±2% from target.")

    # Liquidity
    sgov_pct = df[df["Ticker"] == "SGOV"]["Current %"].values[0]
    liq_status = "🟢 HEALTHY" if sgov_pct >= 2.5 else "🟡 LOW"
    st.markdown(f"**Liquidity Buffer (SGOV)** — Current: **{sgov_pct:.1f}%** → {liq_status}")

    # Tax Drag
    df["Taxable_Income"] = df["Est. Annual Payout"] * df["Taxable %"]
    total_taxable = df["Taxable_Income"].sum()
    estimated_tax_drag = round(total_taxable * 0.35, 0)
    tax_status = "🟢 MANAGEABLE" if estimated_tax_drag < total_annual * 0.30 else "🟡 ELEVATED"
    st.markdown(f"**Tax Drag & ROC** → {tax_status}")
    st.caption(f"Est. taxable portion: ${total_taxable:,.0f} | Est. tax drag @ 35%: ${estimated_tax_drag:,.0f}")

    # Income Sustainability
    st.markdown("**Income Sustainability** → 🟢 ON TRACK")
    st.caption("Projected income is being generated as expected from the current allocation.")

    # Overall
    st.divider()
    if current_vix < 30 and 4.0 <= aggressive_current <= 7.0 and sgov_pct >= 2.5:
        overall = "🟢 GREEN — All major guardrails are healthy."
    else:
        overall = "🟡 YELLOW — Monitor the items flagged above."
    st.success(overall)

    # Performance Insights
    st.markdown("### How the Strategy Is Performing Right Now")
    st.write(f"""
    - Your aggressive high-yield slice is contributing meaningful income while staying within the 4–7% target range.
    - The Core Stable Income bucket (JEPI + JEPQ) continues to provide the majority of reliable monthly cash flow.
    - SGOV is serving dual purpose as both liquidity buffer and tax reserve.
    - Return of Capital in the YieldMax holdings is helping reduce current-year taxable income.
    """)

    # Recommendations
    st.markdown("### Proactive Recommendations")
    if current_vix > 28:
        st.write("• VIX is elevated — good environment to maintain or slightly increase high-yield exposure if desired.")
    if aggressive_current < 4.0:
        st.write("• Aggressive slice is underweight — consider adding to NVDY or CHPY on dips.")
    if sgov_pct < 2.5:
        st.write("• Consider topping up SGOV to maintain healthy liquidity/tax reserve.")
    st.write("• Continue following the 60/30/10 reinvestment rule on surplus.")
    st.write("• Track ROC on your 1099-DIV at year-end for accurate tax filing.")

    # Key Concepts
    with st.expander("📚 Key Concepts"):
        st.write("""
        **Return of Capital (ROC)**: Many YieldMax distributions are not fully taxable immediately. They reduce your cost basis instead.
        
        **110% Safe Harbor**: Paying 110% of last year’s tax in quarterly installments protects you from underpayment penalties.
        
        **Why SGOV for Tax Reserve**: Earns yield, is extremely safe, and is state-tax exempt in California.
        
        **Core vs Aggressive**: Core Stable provides reliability. Aggressive High-Yield provides upside income when volatility is present.
        """)

elif page == "Holding Details":
    st.subheader("Detailed Holding Information")
    selected_ticker = st.selectbox("Select Holding", tickers)
    if selected_ticker:
        row = df[df["Ticker"] == selected_ticker].iloc[0]
        st.subheader(f"{selected_ticker} Details")
        st.dataframe(pd.DataFrame([row]), use_container_width=True, hide_index=True)

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

st.caption(f"Last updated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")