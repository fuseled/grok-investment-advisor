import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="Aggressive Income Portfolio", layout="wide", page_icon="📊")

# ========================
# SHARED PORTFOLIO DATA
# ========================
portfolio_data = {
    "Ticker": ["JEPI", "JEPQ", "IBHJ", "EVHY"],
    "Target %": [40.0, 20.0, 20.0, 15.0],
    "Current %": [42.9, 14.3, 20.0, 15.0],
    "Est. Annual Yield %": [8.4, 10.3, 6.7, 7.2],
    "Est. Annual Income": [75600, 30900, 20100, 16200],
    "Unrealized P/L %": [2.1, 4.5, 1.8, 0.9],
}

df_base = pd.DataFrame(portfolio_data)
total_portfolio_value = 1_250_000  # ← CHANGE TO YOUR ACTUAL VALUE

# ========================
# SIDEBAR NAVIGATION
# ========================
st.sidebar.title("📊 Portfolio Dashboard")
page = st.sidebar.radio("Go to Page:", 
    ["Overview", "Holdings Breakdown", "ETF Decision Engine", 
     "Tax Loss Harvest Simulator", "Portfolio Growth & Optimization"])

st.sidebar.divider()
st.sidebar.caption("Aggressive but Safe High-Yield Strategy • June 2026")

# ========================
# PAGE 1: OVERVIEW
# ========================
if page == "Overview":
    st.title("📊 Aggressive Income Portfolio Dashboard")
    st.markdown(f"**JEPI + JEPQ + IBHJ + EVHY** | Updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

    portfolio_yield = (df_base["Current %"] / 100 * df_base["Est. Annual Yield %"]).sum()
    expected_yearly = int(total_portfolio_value * (portfolio_yield / 100))
    expected_quarterly = expected_yearly // 4
    expected_monthly = expected_yearly // 12
    portfolio_pct = 57.1

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Portfolio %", f"{portfolio_pct:.1f}%")
    with col2:
        st.metric("Expected Yearly", f"${expected_yearly:,.0f}")
    with col3:
        st.metric("Expected Quarterly", f"${expected_quarterly:,.0f}")
    with col4:
        st.metric("Expected Monthly", f"${expected_monthly:,.0f}")

    st.divider()
    st.subheader("Holdings Breakdown by Specific Category")

    col_a, col_b = st.columns([3, 2])
    with col_a:
        st.dataframe(
            df_base.style.format({
                "Target %": "{:.1f}%", "Current %": "{:.1f}%",
                "Est. Annual Yield %": "{:.1f}%",
                "Est. Annual Income": "${:,.0f}",
                "Unrealized P/L %": "{:.1f}%"
            }),
            use_container_width=True, hide_index=True
        )
    with col_b:
        fig = px.pie(df_base, names="Ticker", values="Current %", title="Current Allocation")
        st.plotly_chart(fig, use_container_width=True)

# ========================
# PAGE 2: HOLDINGS BREAKDOWN
# ========================
elif page == "Holdings Breakdown":
    st.title("📋 Detailed Holdings Breakdown")

    st.dataframe(
        df_base.style.format({
            "Target %": "{:.1f}%", "Current %": "{:.1f}%",
            "Est. Annual Yield %": "{:.1f}%",
            "Est. Annual Income": "${:,.0f}",
            "Unrealized P/L %": "{:.1f}%"
        }),
        use_container_width=True, hide_index=True
    )

    col1, col2 = st.columns(2)
    with col1:
        fig_bar = px.bar(df_base, x="Ticker", y=["Target %", "Current %"], 
                        barmode="group", title="Target vs Current Allocation")
        st.plotly_chart(fig_bar, use_container_width=True)
    with col2:
        fig_income = px.bar(df_base, x="Ticker", y="Est. Annual Income", 
                           title="Estimated Annual Income")
        st.plotly_chart(fig_income, use_container_width=True)

# ========================
# PAGE 3: ETF DECISION ENGINE
# ========================
elif page == "ETF Decision Engine":
    st.title("🤖 ETF Decision Engine - Hold / Buy / Dump")

    df = df_base.copy()

    def calculate_score(row):
        yield_score = 10 if row["Est. Annual Yield %"] > 9 else 8 if row["Est. Annual Yield %"] > 7 else 5
        nav_score = 9 if row["Unrealized P/L %"] > 0 else 6
        vol_score = 9 if row["Ticker"] in ["JEPI", "IBHJ"] else 7
        return round(yield_score*0.25 + nav_score*0.25 + vol_score*0.15 + 8*0.10 + 8*0.10 + 8*0.10 + 7*0.05, 1)

    df["Calculated Score"] = df.apply(calculate_score, axis=1)
    decision_map = lambda s: "🟢 STRONG BUY / ADD" if s >= 78 else "🟡 HOLD" if s >= 65 else "🔴 REDUCE / DUMP"
    df["Recommendation"] = df["Calculated Score"].apply(decision_map)

    st.dataframe(
        df[["Ticker", "Calculated Score", "Recommendation", "Est. Annual Yield %", "Unrealized P/L %"]]
        .style.format({
            "Calculated Score": "{:.1f}",
            "Est. Annual Yield %": "{:.1f}%",
            "Unrealized P/L %": "{:.1f}%"
        }),
        use_container_width=True, hide_index=True
    )

    st.info("""
    **Recommended Strategy**  
    • Core: 40% JEPI + 20% JEPQ  
    • Strong Bond Buffer: 20% IBHJ + 15% EVHY  
    • Rebalance when Score drops below 65
    """)

# ========================
# PAGE 4: TAX LOSS HARVEST SIMULATOR
# ========================
elif page == "Tax Loss Harvest Simulator":
    st.title("🧾 Tax Loss Harvest Simulator")

    st.markdown("### Year-End Tax Loss Harvesting Strategy")

    loss_amount = st.slider("Unrealized Loss to Harvest ($)", 0, 100000, 20000, step=1000)
    tax_rate = st.slider("Your Marginal Tax Rate (%)", 10, 40, 32)

    savings = int(loss_amount * (tax_rate / 100))

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Estimated Tax Savings", f"${savings:,.0f}")
    with col2:
        st.metric("Net Cost After Tax Benefit", f"${loss_amount - savings:,.0f}")

    st.subheader("Recommended Swaps (Avoid Wash-Sale Rule)")
    st.write("""
    - JEPI → JEPQ or SCHD  
    - JEPQ → JEPI or another Nasdaq income ETF  
    - IBHJ → SPHY or USHY  
    - EVHY → HYG or JNK  
    **Wait 31 days** before rotating back.
    """)

    st.warning("**Only for taxable accounts** • Consult your CPA • Avoid substantially identical securities.")

# ========================
# PAGE 5: PORTFOLIO GROWTH & OPTIMIZATION
# ========================
elif page == "Portfolio Growth & Optimization":
    st.title("📈 Portfolio Growth & Optimization")
    st.markdown(f"YTD Performance Tracker & Maximization Strategies | {datetime.now().strftime('%Y-%m-%d')}")

    st.sidebar.header("Growth Inputs")
    ytd_start_value = st.sidebar.number_input("Portfolio Value at Start of 2026 ($)", 
                                            value=1_050_000, step=10_000)

    current_value = total_portfolio_value
    ytd_growth_pct = ((current_value - ytd_start_value) / ytd_start_value) * 100
    ytd_growth_dollar = current_value - ytd_start_value

    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
    monthly_returns = [2.1, 1.8, -0.4, 3.2, 2.5, 1.9]

    df_growth = pd.DataFrame({
        "Month": months,
        "Monthly Return %": monthly_returns,
        "Running Total Value": [ytd_start_value * (1 + sum(monthly_returns[:i+1])/100) for i in range(len(months))]
    })

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("YTD Growth %", f"{ytd_growth_pct:.1f}%", f"${ytd_growth_dollar:,.0f}")
    with col2:
        st.metric("Current Value", f"${current_value:,.0f}")
    with col3:
        st.metric("Avg Monthly Return", f"{sum(monthly_returns)/len(monthly_returns):.2f}%")
    with col4:
        projected = int(current_value * (1 + (ytd_growth_pct/100) * (12/6)))
        st.metric("Projected Year-End", f"${projected:,.0f}")

    st.subheader("Running Total Portfolio Growth YTD")
    fig_line = px.line(df_growth, x="Month", y="Running Total Value", 
                      title="Portfolio Value Growth 2026", markers=True)
    fig_line.update_layout(yaxis_tickprefix="$", yaxis_tickformat=",")
    st.plotly_chart(fig_line, use_container_width=True)

    st.dataframe(df_growth.style.format({
        "Monthly Return %": "{:.2f}%",
        "Running Total Value": "${:,.0f}"
    }), use_container_width=True, hide_index=True)

    st.subheader("💡 Optimization & Maximization Recommendations")
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("""
        **Immediate Actions:**
        1. Rebalance to exact target weights
        2. Increase IBHJ position (strong term structure)
        3. Tax-loss harvest any losers before Dec
        4. Add 5-10% SCHD for growth + qualified dividends
        """)
    with col_b:
        st.markdown("""
        **Advanced Strategies:**
        - Enable DRIP on all holdings
        - Add small 5% YieldMax satellite on dips
        - Build Treasury ladder for dry powder
        - Maximize tax-advantaged accounts (Roth/IRA)
        """)

    st.info("**Top Recommendation Right Now:** Add to IBHJ and rebalance JEPI/JEPQ.")

st.caption("Single-file dashboard • Update `total_portfolio_value` at the top for accurate numbers")
