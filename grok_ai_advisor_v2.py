import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="Grok AI Investment Advisor v2", layout="wide", page_icon="📈", initial_sidebar_state="expanded")

# [Your existing CSS - unchanged]
st.markdown("""<style> ... your full CSS here ... </style>""", unsafe_allow_html=True)

st.sidebar.title("CASH AdvIsor")
page = st.sidebar.radio(
    "Navigate",
    ["Portfolio Overview", "Income Projections", "Future Portfolio", "Holding Details",
     "Portfolio Combined", "Reinvestment Strategy", "Guardrails & Alerts"]
)

st.title("Grok AI Investment Advisor v2")
st.markdown("**$2.1M Portfolio → ~$190k/year** | Built for Jay")

# ==================== UPDATED PORTFOLIO DATA ====================
TOTAL_CAPITAL = 2_100_000

targets = {
    "JEPI": {"target_pct": 40.0, "amount": 840_000},
    "SCHD": {"target_pct": 22.0, "amount": 462_000},
    "JEPQ": {"target_pct": 13.3, "amount": 280_000},
    "VIG":  {"target_pct": 6.2,  "amount": 130_000},
    "SGOV": {"target_pct": 2.9,  "amount": 60_000},
    "NVDY": {"target_pct": 1.19, "amount": 25_000},
    "ULTY": {"target_pct": 1.19, "amount": 25_000},
    "CHPY": {"target_pct": 0.95, "amount": 20_000},
    "MRNY": {"target_pct": 0.71, "amount": 15_000},
    "YMAX": {"target_pct": 0.71, "amount": 15_000},
    "IBHJ": {"target_pct": 5.0,  "amount": 105_000},   # New: High Yield Bond Ladder
    "EVHY": {"target_pct": 5.71, "amount": 120_000},   # New: Active High Yield Bond
}

category_map = {
    "JEPI": "Core Stable Income", "JEPQ": "Core Stable Income",
    "SCHD": "Quality Dividend Growth", "VIG": "Quality Dividend Growth",
    "SGOV": "Cash Buffer",
    "NVDY": "Aggressive High-Yield", "ULTY": "Aggressive High-Yield",
    "CHPY": "Aggressive High-Yield", "MRNY": "Aggressive High-Yield",
    "YMAX": "Aggressive High-Yield",
    "IBHJ": "Quality Dividend Growth",   # Bond ladder for stability
    "EVHY": "Aggressive High-Yield",     # Active high yield
}

payout_data = {
    "JEPI": {"freq": "Monthly", "yield": 8.4},
    "JEPQ": {"freq": "Monthly", "yield": 10.3},
    "SCHD": {"freq": "Quarterly", "yield": 3.3},
    "VIG":  {"freq": "Quarterly", "yield": 1.6},
    "SGOV": {"freq": "Monthly", "yield": 4.5},
    "NVDY": {"freq": "Weekly", "yield": 60.0},
    "ULTY": {"freq": "Weekly", "yield": 65.0},
    "CHPY": {"freq": "Weekly", "yield": 46.0},
    "MRNY": {"freq": "Weekly", "yield": 71.0},
    "YMAX": {"freq": "Weekly", "yield": 57.0},
    "IBHJ": {"freq": "Monthly", "yield": 6.7},   # Approx current yield
    "EVHY": {"freq": "Monthly", "yield": 7.2},   # Approx current yield
}

# Update holding_descriptions with new ones
holding_descriptions = {
    # ... your existing ones ...
    "IBHJ": "iShares iBonds 2030 Term High Yield and Income ETF – A target-maturity high-yield bond ETF maturing in 2030. Provides diversified high-yield corporate bond exposure with a defined maturity date for principal protection and steady monthly income.",
    "EVHY": "Eaton Vance High Yield ETF – Actively managed high-yield bond ETF focusing on higher-quality (BB/B) issuers. Delivers competitive monthly income with professional credit selection and lower volatility than single-stock option strategies.",
    # ... rest of your descriptions ...
}

# [Rest of your code: get_live_prices, get_vix, dataframe building, trackers, etc. remains the same]

# Just make sure tickers includes the new ones:
tickers = list(targets.keys())

# ... (continue with the rest of your existing page logic - it will automatically pick up the new holdings) ...
