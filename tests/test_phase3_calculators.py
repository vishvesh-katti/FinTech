import pytest
import pandas as pd
from calculators import calculate_dynamic_surplus

def test_surplus_calculation_logic():
    data = {
        "Date": pd.to_datetime(["2024-01-01", "2024-01-10", "2024-01-15"]),
        "clean_name": ["Salary", "Rent", "Groceries"],
        "category": ["Salary", "Rent", "Groceries"],
        "amount": [100000.0, 20000.0, 10000.0],
        "is_fixed_obligation": [False, True, False],
        "is_outflow": [False, True, True]
    }
    df = pd.DataFrame(data)
    
    # Balance: 100k - 20k - 10k = 70k
    # Deposits = 100k
    # Withdrawals = 30k
    # Current balance = 70k
    # Rent = 20k (1 month)
    # Variable = 10k (1 month) -> buffer = 11.5k
    # Emergency = 25k
    # Surplus = 70k - 20k - 11.5k - 25k = 13.5k
    
    result = calculate_dynamic_surplus(df)
    assert result["deployable_surplus"] == 13500.0
    assert result["is_surplus_zero"] == False

def test_negative_surplus():
    data = {
        "Date": pd.to_datetime(["2024-01-01", "2024-01-10", "2024-01-15"]),
        "clean_name": ["Salary", "Rent", "Groceries"],
        "category": ["Salary", "Rent", "Groceries"],
        "amount": [30000.0, 20000.0, 10000.0],
        "is_fixed_obligation": [False, True, False],
        "is_outflow": [False, True, True]
    }
    df = pd.DataFrame(data)
    
    # Balance: 30k - 30k = 0
    # Fixed = 20k
    # Variable = 10k -> buffer = 11.5k
    # Emergency = 25k
    # Formula gives negative, so surplus should be 0.
    
    result = calculate_dynamic_surplus(df)
    assert result["deployable_surplus"] == 0.0
    assert result["is_surplus_zero"] == True
