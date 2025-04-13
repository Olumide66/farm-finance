# -*- coding: utf-8 -*-
"""
Created on Sun Apr 13 16:45:57 2025

@author: user
"""
import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_manager import get_expense_data, add_expense_record, delete_record, get_expense_summary_by_category
from utils import get_expense_categories, get_payment_methods, get_current_date

# Set page config
st.set_page_config(
    page_title="Expenses - Farm Management System",
    page_icon="💰",
    layout="wide"
)

st.title("💰 Farm Expenses Management")
st.markdown("Track all farm-related expenses including salaries, repairs, fuel, and other operational costs.")

# Form for adding new expense
st.subheader("Add New Expense")

with st.form("expense_form"):
    col1, col2 = st.columns(2)
    
    with col1:
        date = st.date_input("Date", datetime.now())
        category = st.selectbox("Category", get_expense_categories())
        description = st.text_input("Description")
        
    with col2:
        amount = st.number_input("Amount (₦)", min_value=0.0, step=10.0)
        payment_method = st.selectbox("Payment Method", get_payment_methods())
        
    notes = st.text_area("Notes")
    
    submitted = st.form_submit_button("Add Expense Record")
    
    if submitted:
        if description and amount > 0:
            success = add_expense_record(
                date=date.strftime('%Y-%m-%d'),
                category=category,
                description=description,
                amount=amount,
                payment_method=payment_method,
                notes=notes
            )
            
            if success:
                st.success("Expense record added successfully!")
            else:
                st.error("Failed to add expense record.")
        else:
            st.warning("Please fill all required fields (description and amount).")

# Display existing expense records
st.subheader("Expense Records")

# Filter options
st.markdown("### Filter Records")
col1, col2, col3 = st.columns(3)

with col1:
    filter_category = st.multiselect("Filter by Category", get_expense_categories())
    
with col2:
    date_range = st.date_input("Date Range", 
                               value=[datetime.now().replace(day=1), datetime.now()],
                               key="expense_date_range")
    
with col3:
    search_term = st.text_input("Search Description")

# Get expense data
expense_df = get_expense_data()

if not expense_df.empty:
    # Apply filters
    filtered_df = expense_df.copy()
    
    if filter_category:
        filtered_df = filtered_df[filtered_df['category'].isin(filter_category)]
    
    if len(date_range) == 2:
        start_date, end_date = date_range
        filtered_df = filtered_df[
            (pd.to_datetime(filtered_df['date']) >= pd.to_datetime(start_date.strftime('%Y-%m-%d'))) &
            (pd.to_datetime(filtered_df['date']) <= pd.to_datetime(end_date.strftime('%Y-%m-%d')))
        ]
    
    if search_term:
        filtered_df = filtered_df[
            filtered_df['description'].str.contains(search_term, case=False, na=False)
        ]
    
    # Sort by date (newest first)
    filtered_df = filtered_df.sort_values('date', ascending=False)
    
    # Display filtered data
    st.dataframe(filtered_df, use_container_width=True)
    
    # Summary statistics
    st.subheader("Expense Summary")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Expenses", len(filtered_df))
        
    with col2:
        total_amount = filtered_df['amount'].sum()
        st.metric("Total Amount", f"₦{total_amount:,.2f}")
        
    with col3:
        avg_amount = total_amount / len(filtered_df) if len(filtered_df) > 0 else 0
        st.metric("Average Expense", f"₦{avg_amount:,.2f}")
    
    # Expense breakdown by category
    st.subheader("Expense Breakdown by Category")
    
    expense_summary = get_expense_summary_by_category()
    
    if not expense_summary.empty:
        # Create pie chart
        fig = px.pie(expense_summary, 
                     values='total_amount', 
                     names='category', 
                     title='Expense Distribution by Category',
                     color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig, use_container_width=True)
        
        # Show table summary
        st.dataframe(expense_summary, use_container_width=True)
    
    # Delete record option
    st.subheader("Delete Expense Record")
    delete_id = st.number_input("Enter ID to delete", min_value=1, step=1)
    if st.button("Delete Record"):
        if delete_id in expense_df['id'].values:
            if delete_record('expenses', delete_id):
                st.success(f"Record with ID {delete_id} deleted successfully.")
                st.rerun()
            else:
                st.error("Failed to delete record.")
        else:
            st.warning(f"No record found with ID {delete_id}.")
    
else:
    st.info("No expense records found. Add some expenses to get started!")
