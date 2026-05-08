"""Streamlit web interface for the personal budget tracker."""

from datetime import date

import pandas as pd
import plotly.express as px
import streamlit as st

import database as db

st.set_page_config(
    page_title="Personal Budget Tracker",
    page_icon="💰",
    layout="wide",
)

db.init_db()

# ---------- Sidebar: filters and budget ----------
st.sidebar.title("⚙️ Filters & Budget")

current_budget = db.get_budget()
new_budget = st.sidebar.number_input(
    "Monthly budget (£)",
    min_value=0.0,
    value=float(current_budget),
    step=50.0,
    format="%.2f",
)
if new_budget != current_budget:
    db.set_budget(new_budget)
    st.sidebar.success(f"Budget updated to £{new_budget:,.2f}")

st.sidebar.divider()
st.sidebar.subheader("🔍 Filter expenses")

filter_category = st.sidebar.selectbox(
    "Category",
    ["All"] + db.CATEGORIES,
)

today = date.today()
default_start = today.replace(day=1)
date_range = st.sidebar.date_input(
    "Date range",
    value=(default_start, today),
)
if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date, end_date = default_start, today

# ---------- Header: total spent + budget progress ----------
st.title("💰 Personal Budget Tracker")

month_spent = db.month_total()
budget = db.get_budget()
percent_used = (month_spent / budget) if budget > 0 else 0

st.markdown(
    f"<h1 style='text-align:center; font-size:3rem;'>"
    f"Total spent this month: <span style='color:#2E86AB'>"
    f"£{month_spent:,.2f}</span></h1>",
    unsafe_allow_html=True,
)

# Pick a colour for the progress bar based on how much of the budget is used.
if percent_used >= 1.0:
    bar_color = "#E63946"   # red — over budget
    status_msg = f"⚠️ Over budget! You've spent £{month_spent - budget:,.2f} more than planned."
elif percent_used >= 0.8:
    bar_color = "#F4A261"   # yellow/orange — getting close
    status_msg = f"⚡ Heads up — you've used {percent_used:.0%} of your budget."
else:
    bar_color = "#2A9D8F"   # green — comfortable
    status_msg = f"✅ Looking good — {percent_used:.0%} of budget used."

display_pct = min(percent_used, 1.0) * 100
st.markdown(
    f"""
    <div style="background:#eee; border-radius:8px; height:30px; width:100%; overflow:hidden;">
        <div style="
            width:{display_pct}%;
            background:{bar_color};
            height:100%;
            text-align:center;
            color:white;
            line-height:30px;
            font-weight:bold;
        ">{percent_used:.0%}</div>
    </div>
    """,
    unsafe_allow_html=True,
)
st.caption(status_msg)

st.divider()

# ---------- Add expense form ----------
st.subheader("➕ Add a new expense")

with st.form("add_expense_form", clear_on_submit=True):
    col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
    with col1:
        name = st.text_input("Name", placeholder="e.g. coffee, groceries, uber")
    with col2:
        category = st.selectbox("Category", db.CATEGORIES)
    with col3:
        amount = st.number_input("Amount (£)", min_value=0.0, step=1.0, format="%.2f")
    with col4:
        spent_on = st.date_input("Date", value=date.today())

    submitted = st.form_submit_button("Add Expense", width="stretch")
    if submitted:
        if not name.strip():
            st.error("Please enter a name for the expense.")
        elif amount <= 0:
            st.error("Amount must be greater than zero.")
        else:
            db.add_expense(name, category, amount, spent_on)
            st.success(f"Added '{name}' — £{amount:,.2f}")
            st.rerun()

st.divider()

# ---------- Charts ----------
filtered = db.fetch_expenses(
    category=filter_category,
    start=start_date,
    end=end_date,
)
df = pd.DataFrame(filtered)

chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.subheader("🥧 Spending by category")
    if df.empty:
        st.info("No expenses match your filters yet.")
    else:
        cat_totals = df.groupby("category", as_index=False)["amount"].sum()
        fig = px.pie(
            cat_totals,
            values="amount",
            names="category",
            hole=0.4,
        )
        fig.update_traces(textinfo="percent+label")
        st.plotly_chart(fig, width="stretch")

with chart_col2:
    st.subheader("📊 Daily spending (current month)")
    month_rows = db.fetch_expenses(start=today.replace(day=1), end=today)
    month_df = pd.DataFrame(month_rows)
    if month_df.empty:
        st.info("No expenses recorded this month yet.")
    else:
        month_df["spent_on"] = pd.to_datetime(month_df["spent_on"])
        daily = month_df.groupby("spent_on", as_index=False)["amount"].sum()
        fig = px.bar(
            daily,
            x="spent_on",
            y="amount",
            labels={"spent_on": "Date", "amount": "Amount (£)"},
        )
        st.plotly_chart(fig, width="stretch")

st.divider()

# ---------- Expense table ----------
st.subheader("📋 All expenses")

if df.empty:
    st.info("No expenses to show. Add one above or change your filters.")
else:
    display_df = df.rename(
        columns={
            "spent_on": "Date",
            "name": "Name",
            "category": "Category",
            "amount": "Amount (£)",
        }
    )[["Date", "Name", "Category", "Amount (£)"]]

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Amount (£)": st.column_config.NumberColumn(format="£%.2f"),
        },
    )

    # Quick delete via id picker — keeps the UI tidy without a delete button per row.
    with st.expander("🗑️ Remove an expense"):
        ids = {f"{r['spent_on']} — {r['name']} (£{r['amount']:.2f})": r["id"]
               for r in filtered}
        choice = st.selectbox("Pick an expense to remove", list(ids.keys()))
        if st.button("Delete selected"):
            db.delete_expense(ids[choice])
            st.success("Expense removed.")
            st.rerun()
