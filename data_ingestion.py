import pandas as pd
import os

def load_transactions(filepath):
    if isinstance(filepath, str):
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Cannot find transaction file at: {filepath}")
    
    # Read CSV
    df = pd.read_csv(filepath)
    
    # Strip leading/trailing whitespace from column names
    df.columns = df.columns.str.strip()
    
    # Fill NaN values in Withdrawal and Deposit with 0
    df["Withdrawal"] = df["Withdrawal"].fillna(0).astype(float)
    df["Deposit"] = df["Deposit"].fillna(0).astype(float)
    
    # Convert Date column to datetime objects
    df["Date"] = pd.to_datetime(df["Date"], format="%Y-%m-%d", errors="coerce")
    
    # Drop rows with NaT dates
    df = df.dropna(subset=["Date"])
    
    # Add is_outflow and amount columns
    df["is_outflow"] = df["Withdrawal"] > 0
    df["amount"] = df.apply(lambda row: row["Withdrawal"] if row["is_outflow"] else row["Deposit"], axis=1)
    
    # Rename Narration
    df = df.rename(columns={"Narration": "raw_description"})
    
    # Return specific columns
    df = df[["Date", "raw_description", "amount", "is_outflow"]]
    df = df.reset_index(drop=True)
    
    return df

def get_summary_stats(df):
    total_deposits = df[~df["is_outflow"]]["amount"].sum()
    total_withdrawals = df[df["is_outflow"]]["amount"].sum()
    
    return {
        "total_rows": len(df),
        "total_deposits": float(total_deposits),
        "total_withdrawals": float(total_withdrawals),
        "date_range_start": df["Date"].min().strftime("%Y-%m-%d"),
        "date_range_end": df["Date"].max().strftime("%Y-%m-%d")
    }
