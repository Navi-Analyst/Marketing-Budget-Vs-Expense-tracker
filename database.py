import streamlit as st  # pip install streamlit
from deta import Deta  # pip install deta


# Load with your Deta key
DETA_KEY = "sample data key"

# Initialize with a project key
deta = Deta(DETA_KEY)

# This is how to create/connect a database
db = deta.Base("marketing_expenses_monthly")


def insert_period(period, budgets, expenses, comment):
    """Returns the report on a successful creation, otherwise raises an error"""
    return db.put({"key": period, "budgets": budgets, "expenses": expenses, "comment": comment})


def fetch_all_periods():
    """Returns a dict of all periods"""
    res = db.fetch()
    return res.items


def get_period(period):
    """If not found, the function will return None"""
    return db.get(period)