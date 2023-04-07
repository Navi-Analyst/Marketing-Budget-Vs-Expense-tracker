import calendar  
from datetime import datetime 
import pandas as pd
import plotly.graph_objects as go  
import plotly.express as px
import streamlit as st  
from streamlit_option_menu import option_menu  

import database as db  

# -------------- Schema and settings --------------
budgets = ["Brand Marketing", "Digital Marketing", "Functional Marketing", "Product Marketing", "Other budget"]
expenses = ["Social ads", "Search ads", "Display ads", "Video ads", "Affiliate ads", "TV ads", "Radio ads", "Print ads", "Email marketing", "Influencers", "Tech subscriptions", "Other expenses"]
currency = "USD"
page_title = "Budget and Expense Tracker by NaviLabs"
page_icon = ":money_with_wings:" 
layout = "centered"
# --------------------------------------

st.set_page_config(page_title=page_title, page_icon=page_icon, layout=layout)
st.title(page_title + " " + page_icon)

# --- DROP DOWN VALUES FOR SELECTING THE PERIOD ---
years = [datetime.today().year, datetime.today().year + 1]
months = list(calendar.month_name[1:])


# --- DATABASE INTERFACE ---
def get_all_periods():
    items = db.fetch_all_periods()
    periods = [item["key"] for item in items]
    return periods


# --- HIDE STREAMLIT STYLE ---
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# --- NAVIGATION MENU ---
selected = option_menu(
    menu_title=None,
    options=["Data Entry", "Data Visualization"],
    icons=["pencil-fill", "bar-chart-fill"],  # https://icons.getbootstrap.com/
    orientation="horizontal",
)

# --- INPUT & SAVE PERIODS ---
if selected == "Data Entry":
    st.header(f"Marketing Budget and expenses in {currency}")
    with st.form("entry_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        col1.selectbox("Select Month:", months, key="month")
        col2.selectbox("Select Year:", years, key="year")

        "---"
        with st.expander("Budget"):
            for budget in budgets:
                st.number_input(f"{budget}:", min_value=0, format="%i", step=100, key=budget)
        with st.expander("Expenses"):
            for expense in expenses:
                st.number_input(f"{expense}:", min_value=0, format="%i", step=100, key=expense)
        with st.expander("Comment"):
            comment = st.text_area("", placeholder="Enter a comment here ...")

        "---"
        submitted = st.form_submit_button("Save Data")
        if submitted:
            period = str(st.session_state["year"]) + "_" + str(st.session_state["month"])
            budgets = {budget: st.session_state[budget] for budget in budgets}
            expenses = {expense: st.session_state[expense] for expense in expenses}
            db.insert_period(period, budgets, expenses, comment)
            st.success("Data saved!")


# --- PLOT PERIODS ---
if selected == "Data Visualization":
    st.header("Data Visualization")
    with st.form("saved_periods"):
        period = st.selectbox("Select Period:", get_all_periods())
         # Get data from database
        period_data = db.get_period(period)
        comment = period_data.get("comment")
        expenses = period_data.get("expenses")
        budgets = period_data.get("budgets")

        # Create metrics
        total_budget = sum(budgets.values())
        total_expense = sum(expenses.values())
        remaining_budget = total_budget - total_expense
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Budget", f"{total_budget} {currency}")
        col2.metric("Total Expense", f"{total_expense} {currency}")
        col3.metric("Remaining Budget", f"{remaining_budget} {currency}")
        st.text(f"Comment: {comment}")    
        submitted = st.form_submit_button(f"Plot {period}")
        if submitted:
                # Create sankey chart
                label = list(budgets.keys()) + ["Total budget"] + list(expenses.keys())
                source = list(range(len(budgets))) + [len(budgets)] * len(expenses)
                target = [len(budgets)] * len(budgets) + [label.index(expense) for expense in expenses.keys()]
                value = list(budgets.values()) + list(expenses.values())

                # Data to dict, dict to sankey
                link = dict(source=source, target=target, value=value)
                node = dict(label=label, pad=20, thickness=30, color="#E694FF")
                data = go.Sankey(link=link, node=node)

                # Plot it!
                fig = go.Figure(data)
                fig.update_layout(margin=dict(l=0, r=0, t=5, b=5))
                st.plotly_chart(fig, use_container_width=True)
           
                # Bar chart
                chart_data=pd.DataFrame(
                    [list(budgets.values())],
                    columns=list(budgets.keys())
                )
                st.bar_chart(chart_data)
            