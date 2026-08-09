import pandas as pd
import math

def calculate_dynamic_surplus(transactions_df):
    # STEP A: Current Balance
    total_deposits = transactions_df[~transactions_df["is_outflow"]]["amount"].sum()
    total_withdrawals = transactions_df[transactions_df["is_outflow"]]["amount"].sum()
    current_balance = total_deposits - total_withdrawals
    
    # STEP B: Fixed Obligations
    fixed_df = transactions_df[(transactions_df["is_fixed_obligation"] == True) & (transactions_df["is_outflow"] == True)]
    fixed_group = fixed_df.groupby("clean_name")["amount"].agg(['sum', 'count'])
    fixed_group["monthly_avg"] = fixed_group["sum"] / fixed_group["count"]
    fixed_obligations_next_30_days = fixed_group["monthly_avg"].sum()
    
    # For breakdown
    fixed_items = [{"name": name, "amount": float(row["monthly_avg"])} for name, row in fixed_group.iterrows()]
    
    # STEP C: Variable Expense Buffer
    var_df = transactions_df[(transactions_df["is_fixed_obligation"] == False) & (transactions_df["is_outflow"] == True)]
    
    min_date = transactions_df["Date"].min()
    max_date = transactions_df["Date"].max()
    
    # Determine months
    if pd.isna(min_date) or pd.isna(max_date):
        months = 1
    else:
        days = (max_date - min_date).days
        months = max(1, math.ceil(days / 30.0))
        
    total_variable_spend = var_df["amount"].sum()
    avg_monthly_variable = total_variable_spend / months
    variable_expense_buffer = avg_monthly_variable * 1.15
    
    # For breakdown
    var_group = var_df.groupby("category")["amount"].sum() / months
    variable_categories = [{"category": cat, "monthly_avg": float(amt)} for cat, amt in var_group.items()]
    
    # STEP D: Emergency Fund
    emergency_fund = 25000.0
    
    # STEP E: Deployable Surplus
    deployable_surplus = current_balance - fixed_obligations_next_30_days - variable_expense_buffer - emergency_fund
    
    is_surplus_zero = False
    if deployable_surplus < 0:
        deployable_surplus = 0.0
        is_surplus_zero = True
        
    return {
        "current_balance": float(current_balance),
        "fixed_obligations_next_30_days": float(fixed_obligations_next_30_days),
        "variable_expense_buffer": float(variable_expense_buffer),
        "emergency_fund": emergency_fund,
        "deployable_surplus": float(deployable_surplus),
        "is_surplus_zero": is_surplus_zero,
        "breakdown": {
            "fixed_items": fixed_items,
            "variable_categories": variable_categories
        }
    }

def format_inr(amount):
    amount_str = f"{amount:.2f}"
    integer_part, decimal_part = amount_str.split(".")
    
    res = ""
    count = 0
    for i in range(len(integer_part) - 1, -1, -1):
        res = integer_part[i] + res
        count += 1
        if count == 3 and i > 0:
            res = "," + res
        elif count > 3 and (count - 3) % 2 == 0 and i > 0:
            res = "," + res
            
    return f"₹{res}.{decimal_part}"
