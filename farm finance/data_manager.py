# -*- coding: utf-8 -*-
"""
Created on Sun Apr 13 16:13:44 2025

@author: user
"""
import pandas as pd
import os
from utils import ensure_data_files_exist, generate_id, get_month_year_from_date

# Ensure data files exist
ensure_data_files_exist()

def get_input_data():
    """Load input data from CSV file."""
    try:
        df = pd.read_csv('data/inputs.csv')
        return df
    except (pd.errors.EmptyDataError, FileNotFoundError):
        # Return empty DataFrame with correct column structure
        return pd.DataFrame(columns=['id', 'date', 'category', 'description', 'quantity', 'unit', 'cost_per_unit', 'total_cost', 'notes'])

def get_expense_data():
    """Load expense data from CSV file."""
    try:
        df = pd.read_csv('data/expenses.csv')
        return df
    except (pd.errors.EmptyDataError, FileNotFoundError):
        # Return empty DataFrame with correct column structure
        return pd.DataFrame(columns=['id', 'date', 'category', 'description', 'amount', 'payment_method', 'notes'])

def get_output_data():
    """Load output data from CSV file."""
    try:
        df = pd.read_csv('data/outputs.csv')
        return df
    except (pd.errors.EmptyDataError, FileNotFoundError):
        # Return empty DataFrame with correct column structure
        return pd.DataFrame(columns=['id', 'date', 'crop_type', 'quantity', 'unit', 'sales_amount', 'buyer', 'notes'])

def add_input_record(date, category, description, quantity, unit, cost_per_unit, notes):
    """Add a new input record to the inputs CSV file."""
    # Load existing data
    df = get_input_data()
    
    # Calculate total cost
    total_cost = float(quantity) * float(cost_per_unit)
    
    # Create new record
    new_record = {
        'id': generate_id(df),
        'date': date,
        'category': category,
        'description': description,
        'quantity': quantity,
        'unit': unit,
        'cost_per_unit': cost_per_unit,
        'total_cost': total_cost,
        'notes': notes
    }
    
    # Append new record
    df = pd.concat([df, pd.DataFrame([new_record])], ignore_index=True)
    
    # Save updated data
    df.to_csv('data/inputs.csv', index=False)
    
    # Add to expenses as well
    add_expense_record(
        date=date, 
        category=f"Input: {category}", 
        description=description, 
        amount=total_cost, 
        payment_method="", 
        notes=f"Auto-added from input: {quantity} {unit} of {description}"
    )
    
    return True

def add_expense_record(date, category, description, amount, payment_method, notes):
    """Add a new expense record to the expenses CSV file."""
    # Load existing data
    df = get_expense_data()
    
    # Create new record
    new_record = {
        'id': generate_id(df),
        'date': date,
        'category': category,
        'description': description,
        'amount': float(amount),
        'payment_method': payment_method,
        'notes': notes
    }
    
    # Append new record
    df = pd.concat([df, pd.DataFrame([new_record])], ignore_index=True)
    
    # Save updated data
    df.to_csv('data/expenses.csv', index=False)
    
    return True

def add_output_record(date, crop_type, quantity, unit, sales_amount, buyer, notes):
    """Add a new output record to the outputs CSV file."""
    # Load existing data
    df = get_output_data()
    
    # Create new record
    new_record = {
        'id': generate_id(df),
        'date': date,
        'crop_type': crop_type,
        'quantity': quantity,
        'unit': unit,
        'sales_amount': float(sales_amount),
        'buyer': buyer,
        'notes': notes
    }
    
    # Append new record
    df = pd.concat([df, pd.DataFrame([new_record])], ignore_index=True)
    
    # Save updated data
    df.to_csv('data/outputs.csv', index=False)
    
    return True

def delete_record(file_type, record_id):
    """Delete a record from the specified CSV file."""
    if file_type == 'inputs':
        df = get_input_data()
        file_path = 'data/inputs.csv'
    elif file_type == 'expenses':
        df = get_expense_data()
        file_path = 'data/expenses.csv'
    elif file_type == 'outputs':
        df = get_output_data()
        file_path = 'data/outputs.csv'
    else:
        return False
    
    # Filter out the record to delete
    df = df[df['id'] != record_id]
    
    # Save updated data
    df.to_csv(file_path, index=False)
    
    return True

def calculate_profit_loss(expense_df, output_df):
    """Calculate monthly profit/loss based on expenses and sales."""
    if expense_df.empty and output_df.empty:
        return pd.DataFrame()
    
    # Prepare dataframes
    if not expense_df.empty:
        expense_df['date'] = pd.to_datetime(expense_df['date'])
        expense_df['month_year'] = expense_df['date'].dt.strftime('%b %Y')
        monthly_expenses = expense_df.groupby('month_year')['amount'].sum().reset_index()
        monthly_expenses.rename(columns={'amount': 'total_expenses'}, inplace=True)
    else:
        monthly_expenses = pd.DataFrame(columns=['month_year', 'total_expenses'])
    
    if not output_df.empty:
        output_df['date'] = pd.to_datetime(output_df['date'])
        output_df['month_year'] = output_df['date'].dt.strftime('%b %Y')
        monthly_sales = output_df.groupby('month_year')['sales_amount'].sum().reset_index()
        monthly_sales.rename(columns={'sales_amount': 'total_sales'}, inplace=True)
    else:
        monthly_sales = pd.DataFrame(columns=['month_year', 'total_sales'])
    
    # Merge the two dataframes
    if not monthly_expenses.empty and not monthly_sales.empty:
        result = pd.merge(monthly_expenses, monthly_sales, on='month_year', how='outer').fillna(0)
    elif not monthly_expenses.empty:
        result = monthly_expenses.copy()
        result['total_sales'] = 0
    elif not monthly_sales.empty:
        result = monthly_sales.copy()
        result['total_expenses'] = 0
    else:
        return pd.DataFrame()
    
    # Calculate profit/loss
    result['profit_loss'] = result['total_sales'] - result['total_expenses']
    
    # Convert month-year strings to datetime for proper sorting
    result['sort_date'] = pd.to_datetime(result['month_year'], format='%b %Y')
    result.sort_values('sort_date', inplace=True)
    result.drop('sort_date', axis=1, inplace=True)
    
    return result

def get_expense_summary_by_category():
    """Get summary of expenses grouped by category."""
    df = get_expense_data()
    if df.empty:
        return pd.DataFrame()
    
    summary = df.groupby('category')['amount'].agg(['sum', 'count']).reset_index()
    summary.rename(columns={'sum': 'total_amount', 'count': 'transaction_count'}, inplace=True)
    summary.sort_values('total_amount', ascending=False, inplace=True)
    
    return summary

def get_output_summary_by_crop():
    """Get summary of outputs grouped by crop type."""
    df = get_output_data()
    if df.empty:
        return pd.DataFrame()
    
    summary = df.groupby('crop_type').agg({
        'quantity': 'sum',
        'sales_amount': 'sum',
        'id': 'count'
    }).reset_index()
    
    summary.rename(columns={'id': 'harvest_count'}, inplace=True)
    summary.sort_values('sales_amount', ascending=False, inplace=True)
    
    return summary
