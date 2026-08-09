import pandas as pd

def validate_transactions(df):
    """
    Validates the dataframe and returns a data quality report.
    Returns: (is_valid, report_dict)
    """
    report = {
        "score": 100,
        "warnings": [],
        "errors": []
    }
    
    if len(df) == 0:
        report["errors"].append("No transactions found.")
        report["score"] = 0
        return False, report
        
    # Check for duplicates
    duplicates = df.duplicated(subset=['date', 'raw_description', 'amount']).sum()
    if duplicates > 0:
        report["warnings"].append(f"Found {duplicates} duplicate transactions. These will be kept but verify statement integrity.")
        report["score"] -= (duplicates * 2)

    # Date gap analysis
    df = df.sort_values('date')
    date_diffs = df['date'].diff().dt.days
    max_gap = date_diffs.max()
    
    if max_gap > 30:
        report["warnings"].append(f"Large gap detected: {max_gap} days between transactions. Statement may be incomplete.")
        report["score"] -= 20
        
    duration_days = (df['date'].max() - df['date'].min()).days
    if duration_days < 90:
        report["warnings"].append(f"Less than 3 months of data ({duration_days} days). Projections may be unreliable.")
        report["score"] -= 10
        
    report["score"] = max(0, report["score"])
    
    is_valid = len(report["errors"]) == 0
    return is_valid, report
