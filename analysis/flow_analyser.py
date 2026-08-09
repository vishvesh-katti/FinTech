import pandas as pd
import numpy as np

def spending_quality_analysis(df):
    """
    Analyzes the quality of spending (Needs vs Wants) and calculates baseline metrics.
    """
    if df.empty:
        return {
            "total_inflow": 0.0,
            "total_outflow": 0.0,
            "needs_total": 0.0,
            "wants_total": 0.0,
            "needs_pct": 0.0,
            "wants_pct": 0.0,
            "baseline_burn": 0.0,
            "ratio_text": "No spending data available."
        }
        
    inflows = df[df["transaction_amount"] > 0]["transaction_amount"].sum()
    
    outflows_df = df[df["transaction_amount"] < 0].copy()
    outflows_df["transaction_amount"] = outflows_df["transaction_amount"].abs()
    
    total_outflow = outflows_df["transaction_amount"].sum()
    
    needs_total = outflows_df[outflows_df["type"] == "Need"]["transaction_amount"].sum()
    wants_total = outflows_df[outflows_df["type"] == "Want"]["transaction_amount"].sum()
    
    # Needs vs Wants ratio
    if total_outflow > 0:
        needs_pct = (needs_total / total_outflow) * 100
        wants_pct = (wants_total / total_outflow) * 100
    else:
        needs_pct = 0.0
        wants_pct = 0.0
        
    ratio_text = f"You spend {needs_pct:.1f}% on Essentials and {wants_pct:.1f}% on Discretionary."
    
    # Calculate Baseline Burn Rate (Monthly average of Housing, Utilities, Food)
    # Get number of unique months in dataset
    if len(df) > 0 and 'date' in df.columns:
        months = df['date'].dt.to_period('M').nunique()
        months = max(1, months)
    else:
        months = 1
        
    baseline_categories = ["Housing", "Utilities", "Food & Dining"]
    baseline_spend = outflows_df[outflows_df["category"].isin(baseline_categories)]["transaction_amount"].sum()
    baseline_burn = baseline_spend / months
    
    return {
        "total_inflow": float(inflows),
        "total_outflow": float(total_outflow),
        "needs_total": float(needs_total),
        "wants_total": float(wants_total),
        "needs_pct": float(needs_pct),
        "wants_pct": float(wants_pct),
        "baseline_burn": float(baseline_burn),
        "ratio_text": ratio_text
    }
