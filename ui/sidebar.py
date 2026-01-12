import streamlit as st

def sidebar():
    return st.sidebar.radio(
        "Platform Modules",
        [
            "Data Ingestion",
            "General Ledger",
            "Trial Balance",
            "Financial Statements",
            "Budgeting & Forecasting",
            "Anomaly Detection",
            "Insights"
        ]
    )
