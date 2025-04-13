# -*- coding: utf-8 -*-
"""
Created on Sun Apr 13 16:45:17 2025

@author: user
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_manager import (
    get_expense_data, 
    get_input_data, 
    get_output_data, 
    calculate_profit_loss,
    get_expense_summary_by_category,
    get_output_summary_by_crop
)

# Set page config
st.set_page_config(
    page_title="Dashboard - Farm Management System",
    page_icon="📈",
    layout="wide"
)

st.title("📈 Farm Dashboard")
st.markdown("Your farm's financial performance at a glance.")

# Get data
expense_df = get_expense_data()
input_df = get_input_data()
output_df = get_output_data()

# Date range selector
col1, col2 = st.columns(2)
with col1:
    period = st.selectbox(
        "Select Period",
        ["Last 30 days", "Last 90 days", "Last 6 months", "Last year", "All time"]
    )

# Calculate start date based on period
today = datetime.now()
if period == "Last 30 days":
    start_date = today - timedelta(days=30)
elif period == "Last 90 days":
    start_date = today - timedelta(days=90)
elif period == "Last 6 months":
    start_date = today - timedelta(days=180)
elif period == "Last year":
    start_date = today - timedelta(days=365)
else:  # All time
    start_date = pd.Timestamp.min

# Filter data by date range
if not expense_df.empty:
    expense_df = expense_df[
        pd.to_datetime(expense_df['date']) >= start_date
    ]

if not input_df.empty:
    input_df = input_df[
        pd.to_datetime(input_df['date']) >= start_date
    ]

if not output_df.empty:
    output_df = output_df[
        pd.to_datetime(output_df['date']) >= start_date
    ]

# Calculate profit/loss
profit_loss_df = calculate_profit_loss(expense_df, output_df)

# Display key metrics
st.header("Key Metrics")

col1, col2, col3, col4 = st.columns(4)

with col1:
    total_expenses = expense_df['amount'].sum() if not expense_df.empty else 0
    st.metric(label="Total Expenses", value=f"₦{total_expenses:,.2f}")

with col2:
    total_sales = output_df['sales_amount'].sum() if not output_df.empty else 0
    st.metric(label="Total Sales", value=f"₦{total_sales:,.2f}")

with col3:
    net_profit = total_sales - total_expenses
    profit_status = "PROFIT" if net_profit >= 0 else "LOSS"
    st.metric(label=f"Net {profit_status}", value=f"₦{abs(net_profit):,.2f}", 
              delta=f"{net_profit/total_expenses*100:.1f}%" if total_expenses > 0 else "N/A")

with col4:
    roi = (net_profit / total_expenses * 100) if total_expenses > 0 else 0
    st.metric(label="ROI", value=f"{roi:.1f}%")

# Financial trends
st.header("Financial Trends")

if not profit_loss_df.empty:
    # Create area chart of expenses vs. sales
    fig = px.area(profit_loss_df, x='month_year', y=['total_expenses', 'total_sales'],
                 title='Monthly Expenses vs. Sales',
                 labels={'value': 'Amount (₦)', 'variable': 'Category', 'month_year': 'Month'},
                 color_discrete_sequence=['#FF6B6B', '#4ECDC4'])
    st.plotly_chart(fig, use_container_width=True)
    
    # Profit/Loss bar chart
    fig = px.bar(profit_loss_df, x='month_year', y='profit_loss',
                title='Monthly Profit/Loss',
                labels={'month_year': 'Month', 'profit_loss': 'Profit/Loss (₦)'},
                color='profit_loss',
                color_continuous_scale='RdYlGn')
    fig.update_layout(xaxis_title='Month', yaxis_title='Profit/Loss (₦)')
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No financial data available for the selected period.")

# Expense breakdown
st.header("Expense Breakdown")

expense_summary = get_expense_summary_by_category()

if not expense_summary.empty:
    col1, col2 = st.columns(2)
    
    with col1:
        # Pie chart
        fig = px.pie(expense_summary, values='total_amount', names='category', 
                    title='Expense Distribution by Category',
                    color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Bar chart of top expenses
        top_expenses = expense_summary.head(5)
        fig = px.bar(top_expenses, x='category', y='total_amount',
                    title='Top 5 Expense Categories',
                    color='category',
                    labels={'category': 'Category', 'total_amount': 'Amount (₦)'},
                    color_discrete_sequence=px.colors.qualitative.Pastel)
        fig.update_layout(xaxis_title='Category', yaxis_title='Amount (₦)')
        st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No expense data available for the selected period.")

# Output analysis
st.header("Output Analysis")

output_summary = get_output_summary_by_crop()

if not output_summary.empty:
    col1, col2 = st.columns(2)
    
    with col1:
        # Bar chart
        fig = px.bar(output_summary, x='crop_type', y='sales_amount',
                    title='Sales by Crop Type',
                    color='crop_type',
                    labels={'crop_type': 'Crop Type', 'sales_amount': 'Sales Amount (₦)'},
                    color_discrete_sequence=px.colors.qualitative.Safe)
        fig.update_layout(xaxis_title='Crop Type', yaxis_title='Sales Amount (₦)')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Bar chart for quantity
        fig = px.bar(output_summary, x='crop_type', y='quantity',
                    title='Harvest Quantity by Crop Type',
                    color='crop_type',
                    labels={'crop_type': 'Crop Type', 'quantity': 'Quantity'},
                    color_discrete_sequence=px.colors.qualitative.Pastel)
        fig.update_layout(xaxis_title='Crop Type', yaxis_title='Quantity')
        st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No output data available for the selected period.")

# Recent transactions
st.header("Recent Transactions")

tab1, tab2, tab3 = st.tabs(["Recent Expenses", "Recent Inputs", "Recent Outputs"])

with tab1:
    if not expense_df.empty:
        recent_expenses = expense_df.sort_values('date', ascending=False).head(5)
        st.dataframe(recent_expenses[['date', 'category', 'description', 'amount']], use_container_width=True)
    else:
        st.info("No recent expenses to display.")

with tab2:
    if not input_df.empty:
        recent_inputs = input_df.sort_values('date', ascending=False).head(5)
        st.dataframe(recent_inputs[['date', 'category', 'description', 'quantity', 'unit', 'total_cost']], use_container_width=True)
    else:
        st.info("No recent inputs to display.")

with tab3:
    if not output_df.empty:
        recent_outputs = output_df.sort_values('date', ascending=False).head(5)
        st.dataframe(recent_outputs[['date', 'crop_type', 'quantity', 'unit', 'sales_amount']], use_container_width=True)
    else:
        st.info("No recent outputs to display.")
