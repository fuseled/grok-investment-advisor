import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
from datetime import datetime
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils.dataframe import dataframe_to_rows
from io import BytesIO

st.set_page_config(page_title="Grok AI Investment Advisor v2", layout="wide", page_icon="🚀", initial_sidebar_state="expanded")

# Dark mode CSS
st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: #fafafa; }
    .stMetric { background-color: #1a1f2e; border-radius: 12px; padding: 18px; border: 1px solid #2d3748; }
    .stButton>button { background-color: #1f6feb; color: white; border-radius: 8px; font-weight: 600; padding: 14px 28px; }
    h1, h2, h3 { color: #ffffff; }
    .stSidebar { background-color: #161b28; }
</style>
""", unsafe_allow_html=True)

# ==================== SIDEBAR ====================
st.sidebar.title("🚀 Grok AI Advisor")
page = st.sidebar.radio(
    "Navigate",
    ["📊 Portfolio Overview", "💰 Income Projections", "📋 Holding Details",
     "📊 Portfolio Combined", "💸 Reinvestment Strategy", "🛡️ Guardrails & Alerts",
     "📊 Tax & High-Yield Advisor"]  # ← NEW PAGE
)

st.title("Grok AI Investment Advisor v2")
st.markdown("**$2.1M Portfolio → ~$190k/year** | Built for Jay")

# ==================== PORTFOLIO DATA (same as before) ====================
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
    "JEPI": {"freq": "Monthly", "yield": 8.4}, "JEPQ": {"freq": "Monthly", "yield": 10.3},
    "SCHD": {"freq": "Quarterly", "yield": 3.3}, "VIG": {"freq": "Quarterly", "yield": 1.6},
    "SGOV": {"freq": "Monthly", "yield": 4.5},
    "NVDY": {"freq": "Weekly", "yield": 60.0}, "ULTY": {"freq": "Weekly", "yield": 65.0},
    "CHPY": {"freq": "Weekly", "yield": 46.0}, "MRNY": {"freq": "Weekly", "yield": 71.0},
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
aggressive_current = df[df["Ticker"].isin(["NVDY","ULTY","CHPY","MRNY","YMAX"])]["Current_Pct_Numeric"].sum()

# Trackers (unchanged)
if 'high_yield_tracker' not in st.session_state:
    st.session_state.high_yield_tracker = [{"Asset": a, "Position": 1000, "Action": "Keep"} for a in ["NVDY","ULTY","CHPY","MRNY","YMAX"]]

# ==================== EXCEL DOWNLOAD (in-memory) ====================
def create_investment_workbook(df, current_vix, aggressive_current):
    wb = Workbook()
    ws = wb.active
    ws.title = "Dashboard"
    for r in dataframe_to_rows(df, index=False, header=True):
        ws.append(r)
    ws['G1'] = "Current VIX"
    ws['H1'] = current_vix
    buffer = BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    return buffer

if st.button("📥 Download Full Excel / Google Sheets Version"):
    excel_buffer = create_investment_workbook(df, current_vix, aggressive_current)
    st.download_button(
        label="⬇️ Download Grok_AI_Investment_Advisor.xlsx",
        data=excel_buffer,
        file_name=f"Grok_AI_Investment_Advisor_{datetime.now().strftime('%Y-%m-%d')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# ==================== NEW: TAX & HIGH-YIELD ADVISOR PAGE ====================
if page == "📊 Tax & High-Yield Advisor":
    st.subheader("📊 Tax & High-Yield Advisor")
    st.write("**Optimized for Jay** — Focus on maximizing monthly cash flow while managing tax drag and NAV decay.")

    col1, col2 = st.columns([3, 2])
    with col1:
        st.metric("Current VIX", f"{current_vix}", "Higher VIX = Better option premiums")
        st.metric("Aggressive High-Yield Slice", f"{aggressive_current:.1f}%", "Target: 4–8%")

    with col2:
        st.metric("Est. Annual High-Yield Income", f"${int(aggressive_current/100 * TOTAL_CAPITAL * 0.55):,}", "From YieldMax ETFs")

    st.info("**Tax Note**: YieldMax ETFs (NVDY, ULTY, etc.) often distribute **Return of Capital (ROC)** which is tax-deferred until sale. However, they can create complex K-1s and potential wash-sale issues. JEPI/JEPQ are generally more tax-efficient covered-call ETFs.")

    # High-Yield AI Advisor
    st.subheader("🔥 Grok High-Yield AI Recommendation")
    if current_vix > 28:
        rec = "🚀 **ULTY + MRNY** — Max premiums in high vol. Allocate fresh capital here."
    elif current_vix > 22:
        rec = "✅ **NVDY + YMAX** — Best risk/reward balance right now."
    elif current_vix < 15:
        rec = "⚠️ **Reduce exposure** — Premiums too low. Consider rotating to JEPI/JEPQ."
    else:
        rec = "🟡 **CHPY** — Solid diversified semiconductor play."
    st.success(rec)

    # Tax Optimization Tips
    st.subheader("🧾 Tax Optimization Strategies")
    st.markdown("""
    - **Hold in Tax-Advantaged Accounts** (IRA/401k) when possible — especially YieldMax ETFs.
    - **Tax-Loss Harvesting** on individual high-yield positions that decay.
    - **ROC Tracking** — YieldMax often returns capital (lowers cost basis).
    - **State Tax** (CA): Consider municipal bond alternatives or moving to lower-tax state long-term.
    - **Reinvestment Rule**: Put 60% of surplus into high-yield only after tax planning.
    """)

    st.subheader("High-Yield Tracker + Purchases")
    with st.form("hy_tax_form"):
        hy_asset = st.selectbox("Asset", ["NVDY", "ULTY", "CHPY", "MRNY", "YMAX"])
        hy_amount = st.number_input("Amount ($)", value=1000, step=500)
        if st.form_submit_button("Log Purchase"):
            st.session_state.high_yield_tracker.append({"Asset": hy_asset, "Position": hy_amount, "Action": "Buy"})
            st.success("Logged!")

    st.dataframe(pd.DataFrame(st.session_state.high_yield_tracker), use_container_width=True)

# ==================== OTHER PAGES (keep your original logic here) ====================
# ... (Portfolio Overview, Income Projections, etc. — same as before)

st.caption(f"Last updated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")
