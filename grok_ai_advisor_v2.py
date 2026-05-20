import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="Grok AI Investment Advisor v2", layout="wide", page_icon="📈", initial_sidebar_state="expanded")

# Tight professional styling - header flush to top
st.markdown("""
<style>
    .stApp { 
        background-color: #0e1117; 
        color: #fafafa; 
        padding-top: 0rem !important;
        margin-top: 0 !important;
    }
    .block-container {
        padding-top: 0rem !important;
        margin-top: 0 !important;
    }
    .stMetric { background-color: #1a1f2e; border-radius: 12px; padding: 18px; border: 1px solid #2d3748; }
    .stButton>button { background-color: #1f6feb; color: white; border-radius: 8px; font-weight: 600; padding: 14px 28px; }
    h1, h2, h3 { 
        color: #ffffff; 
        margin-top: 0 !important; 
        padding-top: 0 !important; 
    }
    .stSidebar { background-color: #161b28; }
</style>
""", unsafe_allow_html=True)

# ==================== SIDEBAR NAVIGATION ====================
st.sidebar.title("Grok AI Advisor")
page = st.sidebar.radio(
    "Navigate",
    ["Portfolio Overview",
     "Income Projections",
     "Holding Details",
     "Portfolio Combined",
     "Reinvestment Strategy",
     "Guardrails & Alerts"]
)

st.title("Grok AI Investment Advisor v2")
st.markdown("**$2.1M Portfolio → ~$190k/year** | Built for Jay")

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
    "CHPY": {"target_pct": 0.95, "amount":
