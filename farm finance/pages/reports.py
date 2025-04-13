# -*- coding: utf-8 -*-
"""
Created on Sun Apr 13 16:48:47 2025

@author: user
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys
import os
import io
import base64

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
    page_title="Reports - Farm Management System",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Farm Reports")
st.markdown("Generate comprehensive reports for your farm operations.")

# Get data
expense_df = get_expense_data()
input_df = get_input_data()
output_df = get_output_data()

# Date range selector for all reports
start_date = st.date_input(
    "Start Date",
    value=(datetime.now() - timedelta(days=365)).replace(day=1),
    key="report_start_date"
)
end_date = st.date_input(
    "End Date",
    value=datetime.now(),
    key="report_end_date"
)

# Filter data by date range
if not expense_df.empty:
    expense_df = expense_df[
        (pd.to_datetime(expense_df['date']) >= pd.to_datetime(start_date)) &
        (pd.to_datetime(expense_df['date']) <= pd.to_datetime(end_date))
    ]

if not input_df.empty:
    input_df = input_df[
        (pd.to_datetime(input_df['date']) >= pd.to_datetime(start_date)) &
        (pd.to_datetime(input_df['date']) <= pd.to_datetime(end_date))
    ]

if not output_df.empty:
    output_df = output_df[
        (pd.to_datetime(output_df['date']) >= pd.to_datetime(start_date)) &
        (pd.to_datetime(output_df['date']) <= pd.to_datetime(end_date))
    ]

# Report tabs
report_tabs = st.tabs([
    "Financial Summary", 
    "Expense Analysis", 
    "Output Analysis", 
    "Monthly Trends",
    "Export Reports"
])

# Financial Summary Report Tab
with report_tabs[0]:
    st.header("Financial Summary Report")
    
    # Calculate profit/loss
    profit_loss_df = calculate_profit_loss(expense_df, output_df)
    
    # Key financial metrics
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
        margin = (net_profit / total_sales * 100) if total_sales > 0 else 0
        st.metric(label="Profit Margin", value=f"{margin:.1f}%")
    
    # Monthly financial performance
    st.subheader("Monthly Financial Performance")
    
    if not profit_loss_df.empty:
        fig = px.bar(profit_loss_df, x='month_year', y=['total_expenses', 'total_sales', 'profit_loss'], 
                    title='Monthly Revenue, Expenses, and Profit/Loss',
                    barmode='group',
                    labels={'value': 'Amount (₦)', 'variable': 'Category', 'month_year': 'Month'},
                    color_discrete_sequence=px.colors.qualitative.Safe)
        st.plotly_chart(fig, use_container_width=True)
        
        # Table view
        st.dataframe(profit_loss_df, use_container_width=True)
    else:
        st.info("No financial data available for the selected date range.")

# Expense Analysis Report Tab
with report_tabs[1]:
    st.header("Expense Analysis Report")
    
    if not expense_df.empty:
        # Expense by category
        expense_by_category = expense_df.groupby('category')['amount'].sum().reset_index()
        expense_by_category.sort_values('amount', ascending=False, inplace=True)
        
        # Pie chart
        fig = px.pie(expense_by_category, values='amount', names='category', 
                    title='Expense Distribution by Category',
                    color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig, use_container_width=True)
        
        # Top expenses table
        st.subheader("Top Expense Categories")
        st.dataframe(expense_by_category.head(10), use_container_width=True)
        
        # Monthly expense trend by category
        st.subheader("Monthly Expense Trend by Category")
        
        # Create month column
        expense_df['month'] = pd.to_datetime(expense_df['date']).dt.strftime('%Y-%m')
        
        # Group by month and category
        monthly_expense_by_category = expense_df.pivot_table(
            index='month', 
            columns='category', 
            values='amount', 
            aggfunc='sum'
        ).fillna(0)
        
        # Convert to long format for plotting
        monthly_expense_long = monthly_expense_by_category.reset_index().melt(
            id_vars=['month'], 
            var_name='category', 
            value_name='amount'
        )
        
        # Plot
        fig = px.line(monthly_expense_long, x='month', y='amount', color='category',
                     title='Monthly Expenses by Category',
                     labels={'month': 'Month', 'amount': 'Amount (₦)', 'category': 'Category'},
                     markers=True)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No expense data available for the selected date range.")

# Output Analysis Report Tab
with report_tabs[2]:
    st.header("Output Analysis Report")
    
    if not output_df.empty:
        # Output by crop type
        output_by_crop = output_df.groupby('crop_type').agg({
            'quantity': 'sum',
            'sales_amount': 'sum'
        }).reset_index()
        output_by_crop.sort_values('sales_amount', ascending=False, inplace=True)
        
        # Bar chart
        fig = px.bar(output_by_crop, x='crop_type', y='sales_amount',
                    title='Sales by Crop Type',
                    color='crop_type',
                    labels={'crop_type': 'Crop Type', 'sales_amount': 'Sales Amount (₦)'},
                    color_discrete_sequence=px.colors.qualitative.Pastel)
        fig.update_layout(xaxis_title='Crop Type', yaxis_title='Sales Amount (₦)')
        st.plotly_chart(fig, use_container_width=True)
        
        # Output summary table
        st.subheader("Output Summary by Crop")
        st.dataframe(output_by_crop, use_container_width=True)
        
        # Monthly output trend
        st.subheader("Monthly Output Trend")
        
        # Create month column
        output_df['month'] = pd.to_datetime(output_df['date']).dt.strftime('%Y-%m')
        
        # Group by month
        monthly_output = output_df.groupby('month').agg({
            'quantity': 'sum',
            'sales_amount': 'sum'
        }).reset_index()
        
        # Plot
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=monthly_output['month'],
            y=monthly_output['sales_amount'],
            name='Sales Amount',
            marker_color='indianred'
        ))
        fig.add_trace(go.Scatter(
            x=monthly_output['month'],
            y=monthly_output['quantity'],
            name='Quantity',
            yaxis='y2',
            marker_color='royalblue'
        ))
        
        fig.update_layout(
            title='Monthly Output (Sales and Quantity)',
            xaxis_title='Month',
            yaxis_title='Sales Amount (₦)',
            yaxis2=dict(
                title='Quantity',
                overlaying='y',
                side='right'
            ),
            legend=dict(x=0.1, y=1.1, orientation='h')
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No output data available for the selected date range.")

# Monthly Trends Report Tab
with report_tabs[3]:
    st.header("Monthly Trends Report")
    
    if not profit_loss_df.empty:
        # Cumulative profit/loss
        profit_loss_df['cumulative_profit'] = profit_loss_df['profit_loss'].cumsum()
        
        # Plot
        fig = px.line(profit_loss_df, x='month_year', y='cumulative_profit',
                     title='Cumulative Profit/Loss Over Time',
                     labels={'month_year': 'Month', 'cumulative_profit': 'Cumulative Profit/Loss (₦)'},
                     markers=True)
        
        # Add horizontal line at y=0
        fig.add_hline(y=0, line_dash="dash", line_color="red")
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Profit margin trend
        if 'total_sales' in profit_loss_df.columns and 'profit_loss' in profit_loss_df.columns:
            profit_loss_df['profit_margin'] = profit_loss_df.apply(
                lambda x: (x['profit_loss'] / x['total_sales'] * 100) if x['total_sales'] > 0 else 0, 
                axis=1
            )
            
            fig = px.bar(profit_loss_df, x='month_year', y='profit_margin',
                        title='Monthly Profit Margin (%)',
                        labels={'month_year': 'Month', 'profit_margin': 'Profit Margin (%)'},
                        color='profit_margin',
                        color_continuous_scale='RdYlGn')
            fig.update_layout(xaxis_title='Month', yaxis_title='Profit Margin (%)')
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No financial data available for the selected date range.")

# Export Reports Tab
with report_tabs[4]:
    st.header("Export Reports")
    
    export_type = st.selectbox(
        "Select Report to Export",
        ["Financial Summary", "Expense Details", "Output Details", "Input Details"]
    )
    
    # Function to create a download link
    def get_csv_download_link(df, filename):
        csv = df.to_csv(index=False)
        b64 = base64.b64encode(csv.encode()).decode()
        href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">Download {filename}</a>'
        return href
    
    if export_type == "Financial Summary":
        if not profit_loss_df.empty:
            st.markdown(get_csv_download_link(profit_loss_df, "financial_summary.csv"), unsafe_allow_html=True)
        else:
            st.warning("No financial data available to export.")
    
    elif export_type == "Expense Details":
        if not expense_df.empty:
            st.markdown(get_csv_download_link(expense_df, "expense_details.csv"), unsafe_allow_html=True)
        else:
            st.warning("No expense data available to export.")
    
    elif export_type == "Output Details":
        if not output_df.empty:
            st.markdown(get_csv_download_link(output_df, "output_details.csv"), unsafe_allow_html=True)
        else:
            st.warning("No output data available to export.")
    
    elif export_type == "Input Details":
        if not input_df.empty:
            st.markdown(get_csv_download_link(input_df, "input_details.csv"), unsafe_allow_html=True)
        else:
            st.warning("No input data available to export.")
