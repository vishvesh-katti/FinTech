import pandas as pd
import numpy as np

def clean_bank_data(df):
    """
    Standardizes and cleans raw bank CSV data.
    """
    # 1. Standardize column names
    df.columns = df.columns.str.strip().str.lower()
    
    # 2. Identify and parse date column
    date_col = next((col for col in df.columns if 'date' in col), None)
    if date_col:
        df["date"] = pd.to_datetime(df[date_col], format="mixed", dayfirst=True, errors="coerce")
        df = df.dropna(subset=["date"])
    
    # 3. Resolve single vs dual column amounts
    withdrawal_col = next((col for col in df.columns if col in ['withdrawal', 'withdrawal amt', 'debit', 'dr']), None)
    deposit_col = next((col for col in df.columns if col in ['deposit', 'deposit amt', 'credit', 'cr']), None)
    amount_col = next((col for col in df.columns if col in ['amount', 'txn amount', 'transaction amount']), None)
    
    if withdrawal_col and deposit_col:
        df[withdrawal_col] = pd.to_numeric(df[withdrawal_col].fillna(0).replace(r'[^\d.-]', '', regex=True))
        df[deposit_col] = pd.to_numeric(df[deposit_col].fillna(0).replace(r'[^\d.-]', '', regex=True))
        df["transaction_amount"] = df[deposit_col] - df[withdrawal_col]
    elif amount_col:
        df["transaction_amount"] = pd.to_numeric(df[amount_col].fillna(0).replace(r'[^\d.-]', '', regex=True))
    else:
        # Fallback if no known amount columns are found
        df["transaction_amount"] = 0.0
        
    # 4. Standardize description
    narration_col = next((col for col in df.columns if col in ['narration', 'particulars', 'description']), None)
    if narration_col:
        df["description"] = df[narration_col].fillna("").astype(str)
    else:
        df["description"] = ""
        
    # 5. Drop internal bank artifacts (sweep in, auto-sweep)
    sweep_pattern = r'(?i)sweep in|auto-sweep|auto sweep|sweep-in'
    df = df[~df["description"].str.contains(sweep_pattern, na=False)]
    
    # Sort and reset index
    if "date" in df.columns:
        df = df.sort_values('date').reset_index(drop=True)
        
    return df[["date", "description", "transaction_amount"]]
