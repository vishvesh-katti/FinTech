import pandas as pd
import numpy as np

def categorize_transactions(df):
    """
    Applies rule-based regex categorisation to bank transactions.
    """
    if df.empty:
        return df
        
    # Default everything to Uncategorized
    df["category"] = "Uncategorized"
    df["type"] = "Unknown"
    
    # Needs Mapping
    housing_pattern = r'(?i)rent|landlord|estate'
    utilities_pattern = r'(?i)bescom|electricity|airtel|jio|water|gas|broadband|wifi'
    
    # Wants Mapping
    food_pattern = r'(?i)swiggy|zomato|mcdonalds|grocery|supermarket|instamart|blinkit|zepto|starbucks|cafe'
    lifestyle_pattern = r'(?i)amazon|flipkart|myntra|netflix|spotify|movie|pvr|inox|uber|ola'
    
    # Income Mapping
    income_pattern = r'(?i)salary|neft|imps|upi/receive|credit interest'
    
    # Apply Rules
    # Note: Using case=False in str.contains is handled by (?i) or explicit flag, but let's use case=False
    
    desc = df["description"].str.lower()
    
    # Outflows (amounts <= 0)
    outflow_mask = df["transaction_amount"] <= 0
    
    df.loc[outflow_mask & desc.str.contains(housing_pattern, regex=True), "category"] = "Housing"
    df.loc[outflow_mask & desc.str.contains(housing_pattern, regex=True), "type"] = "Need"
    
    df.loc[outflow_mask & desc.str.contains(utilities_pattern, regex=True), "category"] = "Utilities"
    df.loc[outflow_mask & desc.str.contains(utilities_pattern, regex=True), "type"] = "Need"
    
    df.loc[outflow_mask & desc.str.contains(food_pattern, regex=True), "category"] = "Food & Dining"
    df.loc[outflow_mask & desc.str.contains(food_pattern, regex=True), "type"] = "Want"
    
    df.loc[outflow_mask & desc.str.contains(lifestyle_pattern, regex=True), "category"] = "Lifestyle & Discretionary"
    df.loc[outflow_mask & desc.str.contains(lifestyle_pattern, regex=True), "type"] = "Want"
    
    # Inflows (amounts > 0)
    inflow_mask = df["transaction_amount"] > 0
    df.loc[inflow_mask & desc.str.contains(income_pattern, regex=True), "category"] = "Income"
    df.loc[inflow_mask & desc.str.contains(income_pattern, regex=True), "type"] = "Income"
    
    # If it's an inflow but didn't match income patterns, tag as General Income
    df.loc[inflow_mask & (df["category"] == "Uncategorized"), "category"] = "General Income"
    df.loc[inflow_mask & (df["type"] == "Unknown"), "type"] = "Income"
    
    return df
