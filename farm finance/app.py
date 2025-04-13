# -*- coding: utf-8 -*-
"""
Created on Sun Apr 13 16:11:46 2025

@author: user
"""
import streamlit as st
import os
import pandas as pd
from datetime import datetime
import plotly.express as px

# Make sure the data directory exists
if not os.path.exists('data'):
    os.makedirs('data')

# Set page config
st.set_page_config(
    page_title="Farm Management System",
    page_icon="🚜",
    layout="wide",
    initial_sidebar_state="expanded"
)

# App title and description
st.title("🚜 Farm Management System")
st.markdown("""
This application helps you manage your farm operations by tracking:
- Farm inputs (weeding, planting, seeds, fertilizer, etc.)
- Expenses (salaries, diesel, repairs, etc.)
- Farm outputs (harvest quantities and sales)
- Financial performance and analysis
""")

# Main dashboard content
st.header("Farm Dashboard")

# Load data
from data_manager import get_expense_data, get_input_data, get_output_data, calculate_profit_loss

expense_df = get_expense_data()
input_df = get_input_data()
output_df = get_output_data()

# Calculate profit/loss
profit_loss_df = calculate_profit_loss(expense_df, output_df)

# Display summary metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    total_expenses = expense_df['amount'].sum() if not expense_df.empty else 0
    st.metric(label="Total Expenses", value=f"₦{total_expenses:,.2f}")

with col2:
    total_sales = output_df['sales_amount'].sum() if not output_df.empty else 0
    st.metric(label="Total Sales", value=f"₦{total_sales:,.2f}")

with col3:
    net_profit = total_sales - total_expenses
    st.metric(label="Net Profit/Loss", 
              value=f"₦{net_profit:,.2f}", 
              delta=f"{net_profit/total_expenses*100:.1f}%" if total_expenses > 0 else "N/A")

with col4:
    last_month = datetime.now().month - 1 if datetime.now().month > 1 else 12
    last_month_expense = expense_df[pd.to_datetime(expense_df['date']).dt.month == last_month]['amount'].sum() if not expense_df.empty else 0
    st.metric(label="Last Month Expenses", value=f"₦{last_month_expense:,.2f}")

# Recent activities
st.subheader("Recent Activities")
tab1, tab2, tab3 = st.tabs(["Recent Expenses", "Recent Inputs", "Recent Outputs"])

with tab1:
    if not expense_df.empty:
        st.dataframe(expense_df.sort_values('date', ascending=False).head(5))
    else:
        st.info("No expense data available. Add some expenses to see them here.")

with tab2:
    if not input_df.empty:
        st.dataframe(input_df.sort_values('date', ascending=False).head(5))
    else:
        st.info("No input data available. Add some inputs to see them here.")

with tab3:
    if not output_df.empty:
        st.dataframe(output_df.sort_values('date', ascending=False).head(5))
    else:
        st.info("No output data available. Add some outputs to see them here.")

# Charts
st.subheader("Financial Overview")

# Expense breakdown chart
if not expense_df.empty:
    expense_by_category = expense_df.groupby('category')['amount'].sum().reset_index()
    fig = px.pie(expense_by_category, values='amount', names='category', 
                title='Expense Breakdown by Category',
                color_discrete_sequence=px.colors.qualitative.Pastel)
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Add expense data to see expense breakdown chart.")

# Monthly profit/loss chart
if not profit_loss_df.empty:
    fig = px.bar(profit_loss_df, x='month_year', y=['total_expenses', 'total_sales', 'profit_loss'], 
                title='Monthly Financial Performance',
                barmode='group',
                labels={'value': 'Amount (₦)', 'variable': 'Category'},
                color_discrete_sequence=px.colors.qualitative.Safe)
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Add expense and sales data to see monthly financial performance chart.")

# Navigation info
st.sidebar.title("Navigation")
st.sidebar.info("""
Use the pages in the sidebar to:
- Record farm inputs
- Track expenses
- Record farm outputs
- Generate reports
- View financial dashboard
""")

# App created date in the sidebar footer
st.sidebar.markdown("---")
st.sidebar.caption("Farm Management System © 2023")
