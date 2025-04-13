# -*- coding: utf-8 -*-
"""
Created on Sun Apr 13 16:47:09 2025

@author: user
"""
import streamlit as st
import pandas as pd
from datetime import datetime
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_manager import get_input_data, add_input_record, delete_record
from utils import get_input_categories, get_units, get_current_date

# Set page config
st.set_page_config(
    page_title="Farm Inputs - Farm Management System",
    page_icon="🌱",
    layout="wide"
)

st.title("🌱 Farm Inputs Management")
st.markdown("Record all inputs used on your farm including seeds, fertilizers, and other materials.")

# Form for adding new input
st.subheader("Add New Input")

with st.form("input_form"):
    col1, col2 = st.columns(2)
    
    with col1:
        date = st.date_input("Date", datetime.now())
        category = st.selectbox("Category", get_input_categories())
        description = st.text_input("Description")
        
    with col2:
        quantity = st.number_input("Quantity", min_value=0.0, step=0.1)
        unit = st.selectbox("Unit", get_units())
        cost_per_unit = st.number_input("Cost per Unit (₦)", min_value=0.0, step=0.1)
        
    notes = st.text_area("Notes")
    
    submitted = st.form_submit_button("Add Input Record")
    
    if submitted:
        if description and quantity > 0 and cost_per_unit > 0:
            success = add_input_record(
                date=date.strftime('%Y-%m-%d'),
                category=category,
                description=description,
                quantity=quantity,
                unit=unit,
                cost_per_unit=cost_per_unit,
                notes=notes
            )
            
            if success:
                st.success("Input record added successfully!")
                st.info("This input has also been automatically added to your expenses.")
            else:
                st.error("Failed to add input record.")
        else:
            st.warning("Please fill all required fields (description, quantity, cost per unit).")

# Display existing input records
st.subheader("Input Records")

# Filter options
st.markdown("### Filter Records")
col1, col2, col3 = st.columns(3)

with col1:
    filter_category = st.multiselect("Filter by Category", get_input_categories())
    
with col2:
    date_range = st.date_input("Date Range", 
                               value=[datetime.now().replace(day=1), datetime.now()],
                               key="input_date_range")
    
with col3:
    search_term = st.text_input("Search Description")

# Get input data
input_df = get_input_data()

if not input_df.empty:
    # Apply filters
    filtered_df = input_df.copy()
    
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
    st.subheader("Input Summary")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Inputs", len(filtered_df))
        
    with col2:
        total_cost = filtered_df['total_cost'].sum()
        st.metric("Total Cost", f"₦{total_cost:,.2f}")
        
    with col3:
        avg_cost = total_cost / len(filtered_df) if len(filtered_df) > 0 else 0
        st.metric("Average Cost per Input", f"₦{avg_cost:,.2f}")
    
    # Delete record option
    st.subheader("Delete Input Record")
    delete_id = st.number_input("Enter ID to delete", min_value=1, step=1)
    if st.button("Delete Record"):
        if delete_id in input_df['id'].values:
            if delete_record('inputs', delete_id):
                st.success(f"Record with ID {delete_id} deleted successfully.")
                st.warning("Note: This only removes the input record, not the corresponding expense record.")
                st.rerun()
            else:
                st.error("Failed to delete record.")
        else:
            st.warning(f"No record found with ID {delete_id}.")
    
else:
    st.info("No input records found. Add some inputs to get started!")
