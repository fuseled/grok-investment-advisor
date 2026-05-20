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

st.title("🚀 Grok AI Investment Advisor v2")
st.markdown("**$2.1M Portfolio → ~$190k/year | Proactive Guardrails + Tactical Boost Mode** | Built for Jay")

with st.sidebar:
    st.header("⚙️ Settings")
    theme = st.radio("Theme", ["🌙 Dark", "☀️ Light"], index=0, horizontal=True)
    if theme == "☀️ Light":
        st.markdown("<style>.stApp { background-color: #ffffff; color: #000000; } .stMetric { background-color: #f0f2f6; }</style>", unsafe_allow_html=True)

# ==================== PORTFOLIO ====================
TOTAL_CAPITAL = 2_100_000

targets = { ... }   # (same as previous version - keeping it short here for space)

# ... (all the previous targets, category_map, payout_data, get_live_prices, get_vix functions are unchanged)

if st.button("🔄 REFRESH LIVE DATA & RUN FULL ANALYSIS", type="primary", use_container_width=True):
    with st.spinner("Pulling live market data..."):
        prices = get_live_prices(tickers)
        current_vix = get_vix()

        # ... (main dataframe creation remains the same)

        st.success("✅ Live data loaded successfully!")

        # Grok AI Evaluation, Sunburst, Category Summary, Holdings Breakdown (unchanged)

        # ==================== NEW YEARLY INCOME SECTION ====================
        st.header("💰 Yearly Income Summary & Monthly Breakdown")

        # Calculate annual totals
        total_annual_2026 = round(sum(targets[t]["amount"] * payout_data[t]["yield"] / 100 for t in tickers), 0)

        col_y1, col_y2 = st.columns(2)
        with col_y1:
            st.metric("**2026 Projected Income**", f"${total_annual_2026:,.0f}")
        with col_y2:
            st.metric("**2027 Projected Income**", f"${int(total_annual_2026 * 1.04):,.0f}", "+4% growth est.")

        # 2026 Detailed Monthly Breakdown (click to expand)
        with st.expander("📆 Click to view 2026 Detailed Monthly Payout Schedule", expanded=True):
            st.subheader("2026 Monthly Payout Calendar")
            months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
            quarterly_months = ["Mar","Jun","Sep","Dec"]

            cols = st.columns(4)
            for i, month in enumerate(months):
                with cols[i % 4]:
                    # Calculate this month's payout
                    month_payout = 0
                    paying_holdings = []
                    for t in tickers:
                        annual = targets[t]["amount"] * payout_data[t]["yield"] / 100
                        if payout_data[t]["freq"] in ["Monthly", "Weekly"]:
                            month_payout += annual / 12
                            paying_holdings.append(t)
                        elif payout_data[t]["freq"] == "Quarterly" and month in quarterly_months:
                            month_payout += annual / 4
                            paying_holdings.append(t)

                    month_payout = round(month_payout, 0)

                    st.markdown(f"""
                    <div class="month-box">
                        <strong>{month}</strong><br>
                        <span style="font-size: 1.4em; color:#1f6feb;">${month_payout:,.0f}</span><br>
                        <small>{', '.join(paying_holdings[:3]) if paying_holdings else '—'}</small>
                    </div>
                    """, unsafe_allow_html=True)

        # Progress bars
        st.subheader("📊 Progress This Year")
        progress_cols = st.columns(2)
        with progress_cols[0]:
            st.progress(5/12)  # Assuming we are in May 2026
            st.caption("2026 YTD Progress (5 of 12 months)")
        with progress_cols[1]:
            st.progress(0.42)  # Example: 42% of 2026 income already "earned"
            st.caption("2026 Income Progress")

        st.caption(f"Last updated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")

else:
    st.info("Click the big blue button above to load live data and run the full analysis.")
