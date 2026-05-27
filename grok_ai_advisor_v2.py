import streamlit as st

# Your calculated values (example)
expected_yearly = 106500
expected_quarterly = 26625
expected_monthly = 8875
portfolio_pct = 57.1

st.subheader("Holdings breakdown by specific category")

# === Top metrics row ===
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="Portfolio %",
        value=f"{portfolio_pct:.1f}%"
    )

with col2:
    st.metric(
        label="Expected Yearly",
        value=f"${expected_yearly:,.0f}"
    )

with col3:
    st.metric(
        label="Expected Quarterly",
        value=f"${expected_quarterly:,.0f}"
    )

with col4:
    st.metric(
        label="Expected Monthly",
        value=f"${expected_monthly:,.0f}"
    )