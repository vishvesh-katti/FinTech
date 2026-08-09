import pandas as pd
import numpy as np

def compare_historical_returns(df):
    """
    Calculates cumulative return for each asset over the dataset's exact timeframe
    and compares it to a synthetic 7.0% annualized Fixed Deposit benchmark.
    """
    if df.empty or len(df) < 2:
        return {}
        
    results = {}
    
    # Timeframe calculation (in years)
    start_date = df.index.min()
    end_date = df.index.max()
    duration_years = (end_date - start_date).days / 365.25
    
    if duration_years <= 0:
        duration_years = 2.0 # fallback
        
    for asset in df.columns:
        start_price = df[asset].iloc[0]
        end_price = df[asset].iloc[-1]
        
        if start_price > 0:
            cum_return = (end_price / start_price) - 1.0
        else:
            cum_return = 0.0
            
        results[asset] = float(cum_return)
        
    # FD Baseline (7.0% annualized)
    fd_cum_return = ((1 + 0.07) ** duration_years) - 1.0
    results["Synthetic Bank FD"] = float(fd_cum_return)
    
    return results
