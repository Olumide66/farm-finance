# -*- coding: utf-8 -*-
"""
Created on Sun Apr 13 16:48:21 2025

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

from data_manager import get_output_data, add_output_record, delete_record, get_output_summary_by_crop
from utils import get_crop_types, get_units, get_current_date

# Set page config
st.set_page_config(
    page_title="Farm Outputs - Farm Management System",
    page_icon="🌾",
    layout="wide"
)

st.title("🌾 Farm Outputs Management")
st.markdown("Record all harvests and sales from your farm production.")

# Form for adding new output
st.subheader("Add New Output/Sale")

with st.form("output_form"):
    col1, col2 = st.columns(2)
    
    with col1:
        date = st.date_input("Date", datetime.now())
        crop_type = st.selectbox("Crop Type", get_crop_types())
        quantity = st.number_input("Quantity", min_value=0.0, step=0.1)
        
    with col2:
        unit = st.selectbox("Unit", get_units())
        sales_amount = st.number_input("Sales Amount (₦)", min_value=0.0, step=10.0)
        buyer = st.text_input("Buyer/Customer")
        
    notes = st.text_area("Notes")
    
    submitted = st.form_submit_button("Add Output Record")
    
    if submitted:
        if crop_type and quantity > 0:
            success = add_output_record(
                date=date.strftime('%Y-%m-%d'),
                crop_type=crop_type,
                quantity=quantity,
                unit=unit,
                sales_amount=sales_amount,
                buyer=buyer,
                notes=notes
            )
            
            if success:
                st.success("Output record added successfully!")
            else:
                st.error("Failed to add output record.")
        else:
            st.warning("Please fill all required fields (crop type and quantity).")

# Display existing output records
st.subheader("Output Records")

# Filter options
st.markdown("### Filter Records")
col1, col2, col3 = st.columns(3)

with col1:
    filter_crop = st.multiselect("Filter by Crop Type", get_crop_types())
    
with col2:
    date_range = st.date_input("Date Range", 
                               value=[datetime.now().replace(day=1), datetime.now()],
                               key="output_date_range")
    
with col3:
    min_sales = st.number_input("Minimum Sales Amount", min_value=0.0, step=100.0)

# Get output data
output_df = get_output_data()

if not output_df.empty:
    # Apply filters
    filtered_df = output_df.copy()
    
    if filter_crop:
        filtered_df = filtered_df[filtered_df['crop_type'].isin(filter_crop)]
    
    if len(date_range) == 2:
        start_date, end_date = date_range
        filtered_df = filtered_df[
            (pd.to_datetime(filtered_df['date']) >= pd.to_datetime(start_date.strftime('%Y-%m-%d'))) &
            (pd.to_datetime(filtered_df['date']) <= pd.to_datetime(end_date.strftime('%Y-%m-%d')))
        ]
    
    if min_sales > 0:
        filtered_df = filtered_df[filtered_df['sales_amount'] >= min_sales]
    
    # Sort by date (newest first)
    filtered_df = filtered_df.sort_values('date', ascending=False)
    
    # Display filtered data
    st.dataframe(filtered_df, use_container_width=True)
    
    # Summary statistics
    st.subheader("Output Summary")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Harvest Records", len(filtered_df))
        
    with col2:
        total_sales = filtered_df['sales_amount'].sum()
        st.metric("Total Sales", f"₦{total_sales:,.2f}")
        
    with col3:
        avg_price_per_unit = total_sales / filtered_df['quantity'].sum() if filtered_df['quantity'].sum() > 0 else 0
        st.metric("Average Price", f"₦{avg_price_per_unit:,.2f} per unit")
    
    # Output summary by crop
    st.subheader("Output Summary by Crop")
    
    output_summary = get_output_summary_by_crop()
    
    if not output_summary.empty:
        # Create bar chart
        fig = px.bar(output_summary, 
                     x='crop_type', 
                     y='sales_amount',
                     color='crop_type',
                     title='Sales by Crop Type',
                     text_auto=True,
                     labels={'sales_amount': 'Sales Amount (₦)', 'crop_type': 'Crop Type'},
                     color_discrete_sequence=px.colors.qualitative.Safe)
        fig.update_traces(texttemplate='₦%{y:,.2f}', textposition='outside')
        st.plotly_chart(fig, use_container_width=True)
        
        # Show table summary
        st.dataframe(output_summary, use_container_width=True)
    
    # Delete record option
    st.subheader("Delete Output Record")
    delete_id = st.number_input("Enter ID to delete", min_value=1, step=1)
    if st.button("Delete Record"):
        if delete_id in output_df['id'].values:
            if delete_record('outputs', delete_id):
                st.success(f"Record with ID {delete_id} deleted successfully.")
                st.rerun()
            else:
                st.error("Failed to delete record.")
        else:
            st.warning(f"No record found with ID {delete_id}.")
    
else:
    st.info("No output records found. Add some outputs to get started!")
