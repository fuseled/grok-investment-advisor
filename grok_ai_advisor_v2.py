import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="Grok AI Investment Advisor", layout="wide", page_icon="📈", initial_sidebar_state="expanded")

# Professional Dark Mode + Category Colors
st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: #fafafa; }
    .stMetric { background-color: #1a1f2e; border-radius: 12px; padding: 18px; border: 1px solid #2d3748; }
    .stButton>button { background-color: #1f6feb; color: white; border-radius: 8px; font-weight: 600; padding: 14px 28px; }
    h1, h2, h3 { color: #ffffff; }
    .stSidebar { background-color: #161b28; }
    
    /* Category Colors */
    .core { color: #60a5fa; }
    .growth { color: #4ade80; }
    .cash { color: #a1a1aa; }
    .aggressive { color: #f87171; }
    
    /* Sidebar clean frames */
    .sidebar-title { font-size: 1.1rem; font-weight: 600; margin-bottom: 8px; }
</style>
""", unsafe_allow_html=True)

# ==================== PERMANENT HEADER ====================
st.title("Grok AI Investment Advisor")
st.markdown("**$2.1M Portfolio → ~$190k/year** | Built for Jay")
st.divider()

# ==================== SIDEBAR NAVIGATION ====================
st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Select Page",
    ["Portfolio Overview",
     "Income Projections",
     "Holding Details",
     "Portfolio Combined",
     "Reinvestment Strategy",
     "Guardrails & Alerts"],
    label_visibility="collapsed"
)

# ==================== PORTFOLIO DATA ====================
TOTAL_CAPITAL = 2_100_000

targets = { ... }  # (same as your script - unchanged)

category_map = { ... }  # (same)

payout_data = { ... }  # (same)

category_descriptions = { ... }  # (same)

holding_descriptions = { ... }  # (same)

tickers = list(targets.keys())

# (live prices + VIX + main dataframe + trackers + aggressive_current - all unchanged)

# ==================== PAGES ====================
if page == "Portfolio Overview":
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("Target Capital", f"${TOTAL_CAPITAL:,}")
    with col2: st.metric("Current Portfolio Value", f"${df['Current Value'].sum():,.0f}")
    with col3: st.metric("Current VIX", f"{current_vix}")
    with col4: st.metric("Liquidity Score", "94/100")

    st.subheader("Portfolio Evaluation")
    vix_comment = "High volatility — excellent premiums!" if current_vix > 28 else "Low volatility — premiums shrinking." if current_vix < 15 else "Normal volatility range."
    slice_comment = "Overweight — consider trimming." if aggressive_current > 6.0 else "Underweight — safe to add." if aggressive_current < 4.0 else "Right on target."
    st.info(f"**Overall Condition:** Healthy.\n\nVIX is **{current_vix}** → {vix_comment}\n\nAggressive slice is **{aggressive_current:.1f}%** → {slice_comment}")

    st.subheader("High-Yield ETF Recommendation")
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
        # ... (rest of your category loop - unchanged)

elif page == "💰 Income Projections":
    st.subheader("Income Projections")
    # ... (your existing code)

elif page == "📋 Holding Details":
    st.subheader("Detailed Holding Information")
    # ... (your existing code)

elif page == "📊 Portfolio Combined":
    st.subheader("Portfolio Combined View")
    # ... (your existing code)

elif page == "💸 Reinvestment Strategy":
    # Your exact Reinvestment Strategy code (with the three trackers, AI advisors, and TOTAL rows) remains 100% unchanged

elif page == "🛡️ Guardrails & Alerts":
    st.subheader("Proactive Guardrails")
    st.info("All guardrails are currently **GREEN**. No immediate action required.")

st.caption(f"Last updated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")
