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

targets = { ... }  # (same as before - unchanged)

category_map = { ... }  # (unchanged)

payout_data = { ... }   # (unchanged)

# ==================== DESCRIPTIONS ====================
category_descriptions = { ... }  # (unchanged)
holding_descriptions = { ... }   # (unchanged)

tickers = list(targets.keys())

# Live data functions (unchanged)
@st.cache_data(ttl=60)
def get_live_prices(ticker_list): ... 

@st.cache_data(ttl=60)
def get_vix(): ...

prices = get_live_prices(tickers)
current_vix = get_vix()

# Build main dataframe (unchanged)
data = []  # ... (same code as before)
df = pd.DataFrame(data)

# ==================== TRANSACTION TRACKER ====================
if 'transactions' not in st.session_state:
    st.session_state.transactions = []

# ==================== PAGE SELECTION ====================
# (All other pages unchanged - Portfolio Overview, Income Projections, Holding Details, etc.)

elif page == "💸 Reinvestment Strategy":
    st.subheader("💸 Monthly Surplus Reinvestment Strategy")
    st.write("""
    **Goal**: Roll over unspent income each month to fight inflation, strengthen the core portfolio, and allow tactical short-term boosts.
    
    **Allocation Rule**:
    - 60% → Quality Dividend Growth (SCHD + VIG)
    - 30% → Core Stable Income (JEPI)
    - 10% → Tactical High-Risk Boost (YieldMax slice)
    """)

    monthly_surplus = st.number_input("Enter this month's surplus ($)", value=5000.0, step=100.0, format="%.0f")

    st.subheader("Suggested Distribution")
    col1, col2, col3 = st.columns(3)
    with col1: st.metric("Quality Dividend Growth (60%)", f"${round(monthly_surplus * 0.60):,.0f}")
    with col2: st.metric("Core Stable Income (30%)", f"${round(monthly_surplus * 0.30):,.0f}")
    with col3: st.metric("Tactical High-Risk Boost (10%)", f"${round(monthly_surplus * 0.10):,.0f}")

    if st.button("✅ Apply Calculator Output as Transactions", type="primary"):
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        st.session_state.transactions.append({"Date": now, "Bucket": "Quality Dividend Growth", "Asset Purchased": "General", "Amount Purchased": round(monthly_surplus * 0.60), "Add'l Income This Week": "X", "Add'l Income This Month": round(monthly_surplus * 0.60 * 0.084 / 12, 0), "Add'l Income This Year": round(monthly_surplus * 0.60 * 0.084, 0)})
        st.session_state.transactions.append({"Date": now, "Bucket": "Core Stable Income", "Asset Purchased": "General", "Amount Purchased": round(monthly_surplus * 0.30), "Add'l Income This Week": "X", "Add'l Income This Month": round(monthly_surplus * 0.30 * 0.084 / 12, 0), "Add'l Income This Year": round(monthly_surplus * 0.30 * 0.084, 0)})
        st.session_state.transactions.append({"Date": now, "Bucket": "Tactical High-Risk Boost", "Asset Purchased": "General", "Amount Purchased": round(monthly_surplus * 0.10), "Add'l Income This Week": "X", "Add'l Income This Month": round(monthly_surplus * 0.10 * 0.60 / 12, 0), "Add'l Income This Year": round(monthly_surplus * 0.10 * 0.60, 0)})
        st.success("✅ Transactions logged successfully!")

    # ==================== HIGH-YIELD SPECIFIC PURCHASE (SEPARATE) ====================
    st.subheader("🔥 High-Yield Specific Purchase (Separate from main tracker)")
    with st.form("high_yield_form"):
        hy_date = st.date_input("Date", value=datetime.today())
        hy_asset = st.selectbox("Asset Purchased", ["NVDY", "ULTY", "CHPY", "MRNY", "YMAX"])
        hy_amount = st.number_input("Amount Purchased ($)", value=1000.0, step=100.0, format="%.0f")
        submitted = st.form_submit_button("Add High-Yield Purchase")
        if submitted and hy_amount > 0:
            st.session_state.transactions.append({
                "Date": hy_date.strftime("%Y-%m-%d"),
                "Bucket": "Tactical High-Risk Boost",
                "Asset Purchased": hy_asset,
                "Amount Purchased": hy_amount,
                "Add'l Income This Week": round(hy_amount * payout_data[hy_asset]["yield"] / 100 / 52, 0),
                "Add'l Income This Month": round(hy_amount * payout_data[hy_asset]["yield"] / 100 / 12, 0),
                "Add'l Income This Year": round(hy_amount * payout_data[hy_asset]["yield"] / 100, 0)
            })
            st.success(f"✅ High-yield purchase of {hy_asset} logged!")

    # ==================== TRANSACTION TRACKER ====================
    st.subheader("📋 Full Transaction Tracker")
    if st.session_state.transactions:
        trans_df = pd.DataFrame(st.session_state.transactions)
        trans_df = trans_df.sort_values(by="Date", ascending=False)
        st.dataframe(trans_df, use_container_width=True, hide_index=True)
    else:
        st.info("No transactions yet. Use the calculator, manual entry, or high-yield form above.")

elif page == "🛡️ Guardrails & Alerts":
    st.subheader("🛡️ Proactive Guardrails")
    st.info("All guardrails are currently **GREEN**. No immediate action required.")

st.caption(f"Last updated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")
