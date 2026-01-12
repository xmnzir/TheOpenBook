import streamlit as st
import pandas as pd
from pathlib import Path

from core.schema import IFRS_SCHEMA, validate_schema, map_schema
from core.accounting import generate_ledger, trial_balance
from core.reporting import profit_and_loss
from core.budgeting import *
from core.anomalies import detect_anomalies
from core.forecasting import ml_forecast
from core.ai_narratives import explain_variance

from ui.sidebar import sidebar
from ui.dashboards import revenue_expense_chart

# ------------------- PATHS -------------------
LOGO_PATH = Path("ui/assets/logo.png")

# ------------------- PAGE SETUP -------------------
st.set_page_config(
    layout="wide",
    page_title="The Open Account",
    page_icon=str(LOGO_PATH),
)

st.markdown(
    """
    <style>
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    h1, h2, h3 {
        font-weight: 600;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ------------------- MAIN LOGO -------------------

st.title("The Open Account")
st.caption("Enterprise IFRS Accounting & AI Intelligence Platform")

# ------------------- SIDEBAR -------------------
st.sidebar.image(str(LOGO_PATH), width=180)
st.sidebar.markdown("---")
section = sidebar()

# ------------------- DATA INGESTION -------------------
if section == "Data Ingestion":
    uploaded = st.file_uploader("Upload CSV (IFRS format)", type="csv")

    if uploaded:
        raw = pd.read_csv(uploaded)
        mapping = {}
        for k, v in IFRS_SCHEMA.items():
            mapping[k] = st.selectbox(v, [""] + list(raw.columns))
        if "" not in mapping.values():
            st.session_state["df"] = map_schema(raw, mapping)
    else:
        st.session_state["df"] = pd.read_csv(
            "data/transactions_ifrs.csv",
            parse_dates=["date"],
        )

    st.subheader("Data Preview")
    st.dataframe(st.session_state["df"], use_container_width=True)

# Ensure df is available globally
df = st.session_state.get("df")

# ------------------- PRE-COMPUTE FINANCIALS -------------------
if df is not None and not df.empty:
    revenue, expenses = profit_and_loss(df)
else:
    revenue, expenses = pd.Series(dtype=float), pd.Series(dtype=float)

# ------------------- GENERAL LEDGER -------------------
if section == "General Ledger" and df is not None:
    ledger = generate_ledger(df)
    st.subheader("General Ledger")
    st.dataframe(ledger, use_container_width=True)

# ------------------- TRIAL BALANCE -------------------
if section == "Trial Balance" and df is not None:
    tb = trial_balance(generate_ledger(df))
    st.subheader("Trial Balance")
    st.dataframe(tb, use_container_width=True)

# ------------------- FINANCIAL STATEMENTS -------------------
if section == "Financial Statements" and df is not None:
    st.subheader("Revenue vs Expenses")
    st.pyplot(revenue_expense_chart(revenue, expenses))

# ------------------- BUDGETING & FORECASTING -------------------
if section == "Budgeting & Forecasting" and df is not None:

    # -------- FORECAST --------
    st.subheader("Revenue Forecast (ML-Based)")
    rev_forecast = ml_forecast(revenue)
    st.line_chart(
        pd.concat(
            [
                revenue.reset_index(drop=True),
                rev_forecast.reset_index(drop=True),
            ],
            axis=1,
        )
    )

    st.subheader("Expense Forecast (ML-Based)")
    exp_forecast = ml_forecast(expenses)
    st.line_chart(
        pd.concat(
            [
                expenses.reset_index(drop=True),
                exp_forecast.reset_index(drop=True),
            ],
            axis=1,
        )
    )

    # -------- BUDGET & VARIANCE --------
    st.subheader("Budget & Variance Analysis")

    budget_df = create_budget(revenue, expenses)  # columns: type, budget

    actual_df = pd.DataFrame(
        {
            "type": ["Revenue", "Expense"],
            "actual": [revenue.sum(), expenses.sum()],
        }
    )

    var_df = pd.merge(actual_df, budget_df, on="type")

    var_df["Explanation"] = var_df.apply(
        lambda row: explain_variance(row["actual"], row["budget"]),
        axis=1,
    )

    st.dataframe(var_df, use_container_width=True)

# ------------------- ANOMALY DETECTION -------------------
if section == "Anomaly Detection" and df is not None:
    st.subheader("Detected Anomalies")
    anomalies = detect_anomalies(df)
    st.dataframe(anomalies, use_container_width=True)

# ------------------- AI INSIGHTS -------------------
if section == "Insights" and df is not None:
    st.subheader("Platform Insights & Explanations")

    with st.expander(" Narrative Insights", expanded=True):

        total_txns = len(df)
        period_start = df["date"].min().date()
        period_end = df["date"].max().date()

        total_revenue = revenue.sum()
        total_expenses = expenses.sum()
        net_result = total_revenue - total_expenses

        top_revenue_period = revenue.idxmax() if not revenue.empty else None
        top_expense_period = expenses.idxmax() if not expenses.empty else None

        st.write(
            f"""
            During the period from **{period_start}** to **{period_end}**, the system
            processed **{total_txns:,} transactions**, generating a total revenue of
            **{total_revenue:,.2f}** and total expenses of **{total_expenses:,.2f}**.
            """
        )

        st.write(
            f"""
            This resulted in a **{'net profit' if net_result >= 0 else 'net loss'}**
            of **{abs(net_result):,.2f}**, indicating
            {'positive operational performance' if net_result >= 0 else 'cost pressure exceeding revenue'}.
            """
        )

        if top_revenue_period is not None:
            st.write(
                f"""
                Revenue peaked during **{top_revenue_period}**, suggesting a period
                of stronger commercial activity or improved pricing and volume dynamics.
                """
            )

        if top_expense_period is not None:
            st.write(
                f"""
                Expenses were highest during **{top_expense_period}**, which may reflect
                increased operational activity, one-off costs, or scaling investments.
                """
            )

        st.markdown("---")
        st.markdown("### Variance Explanation")

        st.write(
            """
            The narrative layer converts numerical variances into plain-English
            explanations, enabling faster understanding by executives, investors,
            and non-finance stakeholders.
            """
        )

        st.markdown("**Current Period Variance Explanation:**")
        st.write(explain_variance(total_revenue, total_expenses))



    with st.expander(" Data Ingestion (IFRS-Aligned)"):
        st.write(
            """
            This module ingests transaction-level data and maps it to a standardized
            IFRS-compliant schema. It ensures consistency, reduces manual errors,
            and provides a validated foundation for all downstream accounting,
            reporting, and analytics.
            """
        )

    with st.expander(" General Ledger"):
        st.write(
            """
            The General Ledger is automatically generated using double-entry accounting
            principles. Every transaction is traceable, auditable, and systematically
            classified, forming the core accounting record of the organization.
            """
        )

    with st.expander(" Trial Balance"):
        st.write(
            """
            The Trial Balance aggregates ledger balances to confirm that total debits
            equal total credits. This control step detects posting or classification
            issues before financial statements are produced.
            """
        )

    with st.expander(" Financial Statements"):
        st.write(
            """
            Revenue and expense data are summarized to provide a high-level view of
            financial performance. This enables margin analysis, cost monitoring,
            and executive-level insight into operational health.
            """
        )

    with st.expander(" Budgeting & Forecasting"):
        st.write(
            """
            Machine learning models forecast future revenue and expenses based on
            historical patterns. Budget comparisons highlight deviations between
            planned and actual performance, supporting proactive financial management.
            """
        )

    with st.expander(" Anomaly Detection"):
        st.write(
            """
            This module detects unusual or unexpected transactions using statistical
            and behavioral patterns. Anomalies may indicate errors, fraud risks,
            or exceptional business events requiring review.
            """
        )

    