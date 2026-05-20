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

# ==================== PORTFOLIO DATA (unchanged) ====================
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

category_map = { ... }   # (kept the same as previous version)

payout_data = { ... }    # (kept the same)

# ==================== DESCRIPTIONS (kept the same) ====================
category_descriptions = { ... }
holding_descriptions = { ... }

tickers = list(targets.keys())

# ==================== LIVE DATA ====================
@st.cache_data(ttl=60)
def get_live_prices(ticker_list): ...   # (same as before)

@st.cache_data(ttl=60)
def get_vix(): ...   # (same as before)

prices = get_live_prices(tickers)
current_vix = get_vix()

# Build main dataframe (same as before)
data = []   # ... (unchanged)
df = pd.DataFrame(data)

# ==================== TRANSACTION TRACKER (NEW) ====================
if 'transactions' not in st.session_state:
    st.session_state.transactions = []

# ==================== PAGE SELECTION ====================
if page == "📊 Portfolio Overview":
    # (Your existing overview code - unchanged)
    # ... [same as last working version]

elif page == "💰 Income Projections":
    # (Your existing income projections - unchanged)

elif page == "📋 Holding Details":
    # (Your existing holding details with payout chart - unchanged)

elif page == "📊 Portfolio Combined":
    # (unchanged)

elif page == "💸 Reinvestment Strategy":
    st.subheader("💸 Monthly Surplus Reinvestment Strategy")
    st.write("""
    **Goal**: Roll over unspent income each month to fight inflation, strengthen the core, and allow tactical boosts.
    
    **Allocation Rule**:
    - 60% → Quality Dividend Growth (SCHD + VIG)
    - 30% → Core Stable Income (JEPI)
    - 10% → Tactical High-Risk Boost (YieldMax slice)
    """)

    monthly_surplus = st.number_input("Enter this month's surplus ($)", value=5000.0, step=100.0, format="%.0f")

    st.subheader("Suggested Distribution")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Quality Dividend Growth (60%)", f"${round(monthly_surplus * 0.60):,.0f}")
    with col2:
        st.metric("Core Stable Income (30%)", f"${round(monthly_surplus * 0.30):,.0f}")
    with col3:
        st.metric("Tactical High-Risk Boost (10%)", f"${round(monthly_surplus * 0.10):,.0f}")

    # === ONE-CLICK APPLY BUTTON ===
    if st.button("✅ Apply Calculator Output as Transactions", type="primary"):
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        st.session_state.transactions.append({"Date": now, "Bucket": "Quality Dividend Growth", "Amount": round(monthly_surplus * 0.60)})
        st.session_state.transactions.append({"Date": now, "Bucket": "Core Stable Income", "Amount": round(monthly_surplus * 0.30)})
        st.session_state.transactions.append({"Date": now, "Bucket": "Tactical High-Risk Boost", "Amount": round(monthly_surplus * 0.10)})
        st.success("✅ Transactions logged successfully!")

    # === MANUAL ENTRY ===
    st.subheader("Manual Transaction Entry")
    with st.form("manual_transaction"):
        manual_date = st.date_input("Date", value=datetime.today())
        manual_bucket = st.selectbox("Bucket", ["Quality Dividend Growth", "Core Stable Income", "Tactical High-Risk Boost"])
        manual_amount = st.number_input("Amount ($)", value=1000.0, step=100.0, format="%.0f")
        submitted = st.form_submit_button("Add Manual Transaction")
        if submitted and manual_amount > 0:
            st.session_state.transactions.append({
                "Date": manual_date.strftime("%Y-%m-%d"),
                "Bucket": manual_bucket,
                "Amount": manual_amount
            })
            st.success("✅ Manual transaction added!")

    # === TRANSACTION TRACKER TABLE ===
    st.subheader("📋 Transaction Tracker")
    if st.session_state.transactions:
        trans_df = pd.DataFrame(st.session_state.transactions)
        trans_df = trans_df.sort_values(by="Date", ascending=False)
        st.dataframe(trans_df, use_container_width=True, hide_index=True)
    else:
        st.info("No transactions yet. Use the calculator or manual entry above.")

elif page == "🛡️ Guardrails & Alerts":
    # (unchanged)

st.caption(f"Last updated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")
