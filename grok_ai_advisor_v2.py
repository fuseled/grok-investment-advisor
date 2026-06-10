# ========================
# OVERVIEW.py  (Main File)
# ========================

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="High Yield Portfolio", layout="wide", page_icon="📊")

st.title("📊 Aggressive Income Portfolio Dashboard")
st.markdown("**JEPI + JEPQ + IBHJ + EVHY** | Updated: " + datetime.now().strftime("%Y-%m-%d"))

# ========================
# Portfolio Data (Editable)
# ========================

portfolio_data = {
    "Ticker": ["JEPI", "JEPQ", "IBHJ", "EVHY"],
    "Target %": [40.0, 20.0, 20.0, 15.0],
    "Current %": [42.9, 14.3, 20.0, 15.0],
    "Est. Annual Yield %": [8.4, 10.3, 6.7, 7.2],
    "Est. Annual Income": [75600, 30900, 20100, 16200],
    "Unrealized P/L %": [2.1, 4.5, 1.8, 0.9],
    "Score": [82, 78, 80, 74]
}

df = pd.DataFrame(portfolio_data)

total_portfolio_value = 1_250_000  # Update this with your actual value
portfolio_yield = (df["Current %"] / 100 * df["Est. Annual Yield %"]).sum()

expected_yearly = int(total_portfolio_value * (portfolio_yield / 100))
expected_quarterly = expected_yearly // 4
expected_monthly = expected_yearly // 12
portfolio_pct = 57.1  # From your screenshot

# ========================
# TOP METRICS
# ========================

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

# ========================
# HOLDINGS TABLE
# ========================

st.subheader("Holdings Breakdown by Specific Category")

col_a, col_b = st.columns([3, 2])

with col_a:
    st.dataframe(
        df.style.format({
            "Target %": "{:.1f}%",
            "Current %": "{:.1f}%",
            "Est. Annual Yield %": "{:.1f}%",
            "Est. Annual Income": "${:,.0f}",
            "Unrealized P/L %": "{:.1f}%"
        }),
        use_container_width=True,
        hide_index=True
    )

with col_b:
    fig = px.pie(df, names="Ticker", values="Current %", title="Allocation")
    st.plotly_chart(fig, use_container_width=True)

# ========================
# ETF DECISION ENGINE
# ========================

st.subheader("ETF Decision Engine (Hold / Buy / Dump)")

def calculate_score(row):
    yield_score = 10 if row["Est. Annual Yield %"] > 9 else 8 if row["Est. Annual Yield %"] > 7 else 5
    nav_score = 9 if row["Unrealized P/L %"] > 0 else 6
    vol_score = 9 if row["Ticker"] in ["JEPI", "IBHJ"] else 7
    return round((yield_score*0.25 + nav_score*0.25 + vol_score*0.15 + 8*0.1 + 8*0.1 + 8*0.1 + 7*0.05), 1)

df["Score"] = df.apply(calculate_score, axis=1)

decision_map = lambda s: "🟢 STRONG BUY / ADD" if s >= 78 else "🟡 HOLD" if s >= 65 else "🔴 REDUCE / DUMP"

df["Recommendation"] = df["Score"].apply(decision_map)

st.dataframe(
    df[["Ticker", "Score", "Recommendation", "Est. Annual Yield %", "Unrealized P/L %"]].style.format({
        "Score": "{:.1f}",
        "Est. Annual Yield %": "{:.1f}%",
        "Unrealized P/L %": "{:.1f}%"
    }),
    use_container_width=True,
    hide_index=True
)

st.info("**Strategy**: Keep JEPI/JEPQ core. Strong IBHJ/EVHY positions for bond buffer. Rebalance when Score drops below 65.")

st.caption("Data as of June 2026 • Always verify latest yields")
