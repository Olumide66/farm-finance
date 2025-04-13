# -*- coding: utf-8 -*-
"""
Created on Sun Apr 13 16:14:48 2025

@author: user
"""
import pandas as pd
import os
from datetime import datetime

def ensure_data_files_exist():
    """Ensure all necessary data files exist and have correct headers."""
    data_dir = 'data'
    
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    
    # Define files and their headers
    files_and_headers = {
        'inputs.csv': ['id', 'date', 'category', 'description', 'quantity', 'unit', 'cost_per_unit', 'total_cost', 'notes'],
        'expenses.csv': ['id', 'date', 'category', 'description', 'amount', 'payment_method', 'notes'],
        'outputs.csv': ['id', 'date', 'crop_type', 'quantity', 'unit', 'sales_amount', 'buyer', 'notes']
    }
    
    # Create files if they don't exist
    for filename, headers in files_and_headers.items():
        filepath = os.path.join(data_dir, filename)
        if not os.path.exists(filepath):
            df = pd.DataFrame(columns=headers)
            df.to_csv(filepath, index=False)

def generate_id(df):
    """Generate a new unique ID for a dataframe."""
    if df.empty:
        return 1
    else:
        return df['id'].max() + 1

def format_currency(amount):
    """Format a number as currency in Naira."""
    return f"₦{amount:,.2f}"

def get_current_date():
    """Get the current date in YYYY-MM-DD format."""
    return datetime.now().strftime('%Y-%m-%d')

def get_month_year_from_date(date_str):
    """Extract month-year from a date string."""
    date_obj = pd.to_datetime(date_str)
    return date_obj.strftime('%b %Y')

def get_expense_categories():
    """Return a list of expense categories."""
    return [
        "Weeding",
        "Planting",
        "Seeds",
        "Fertilizer",
        "Food",
        "Tractor Repair",
        "Equipment Repair",
        "Salaries",
        "Diesel (Tractor)",
        "Diesel (Other)",
        "Petrol",
        "Contract Labor",
        "Worker Feeding",
        "Pesticides",
        "Irrigation",
        "Tools",
        "Utilities",
        "Transportation",
        "Other"
    ]

def get_input_categories():
    """Return a list of farm input categories."""
    return [
        "Seeds",
        "Fertilizer",
        "Pesticides",
        "Herbicides",
        "Water",
        "Labor",
        "Equipment",
        "Fuel",
        "Other"
    ]

def get_crop_types():
    """Return a list of crop types."""
    return [
        "Palm Oil",
        "Palm Kernel",
        "Palm Kernel Oil",
        "Palm Cake",
        "Cashew Nut",
        "Soybeans",
        "Tomatoes",
        "Potatoes",
        "Maize",
        "Rice",
        "Wheat",
        "Beans",
        "Cassava",
        "Vegetables",
        "Fruits",
        "Other"
    ]

def get_units():
    """Return a list of units for measurement."""
    return [
        "kg",
        "tons",
        "bags",
        "buckets",
        "crates",
        "pieces",
        "acres",
        "hectares",
        "liters",
        "gallons",
        "hours",
        "days"
    ]

def get_payment_methods():
    """Return a list of payment methods."""
    return [
        "Cash",
        "Bank Transfer",
        "Mobile Money",
        "Check",
        "Credit",
        "Other"
    ]
