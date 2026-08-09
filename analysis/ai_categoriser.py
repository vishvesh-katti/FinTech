import json
import anthropic
import pandas as pd
import re
from config import ANTHROPIC_API_KEY
import os
import time

# Phase A: Local Regex Cache Rules
LOCAL_RULES = {
    r'(?i)zomato|swiggy|mcdonalds|starbucks': {
        "clean_merchant": "Food Delivery/Dining", "category": "Food & Dining",
        "subcategory": "Dining Out", "necessity_flag": "discretionary",
        "spending_signal": "lifestyle", "recurrence": "frequent",
        "is_fixed": False, "is_investment": False
    },
    r'(?i)amazon|flipkart|myntra': {
        "clean_merchant": "E-Commerce", "category": "Entertainment & Lifestyle",
        "subcategory": "Shopping", "necessity_flag": "discretionary",
        "spending_signal": "lifestyle", "recurrence": "frequent",
        "is_fixed": False, "is_investment": False
    },
    r'(?i)netflix|spotify|prime|hotstar': {
        "clean_merchant": "OTT Subscription", "category": "Entertainment & Lifestyle",
        "subcategory": "Subscriptions", "necessity_flag": "discretionary",
        "spending_signal": "lifestyle", "recurrence": "monthly",
        "is_fixed": True, "is_investment": False
    },
    r'(?i)uber|ola|rapido': {
        "clean_merchant": "Ride Hailing", "category": "Transportation & Mobility",
        "subcategory": "Taxi", "necessity_flag": "necessity",
        "spending_signal": "lifestyle", "recurrence": "frequent",
        "is_fixed": False, "is_investment": False
    },
    r'(?i)zerodha|groww|upstox|mutual fund|amc|sip': {
        "clean_merchant": "Investment", "category": "Savings & Investments",
        "subcategory": "Equity/MF", "necessity_flag": "savings",
        "spending_signal": "investment", "recurrence": "monthly",
        "is_fixed": False, "is_investment": True
    },
    r'(?i)salary|payroll|NEFT.*Salary': {
        "clean_merchant": "Salary Income", "category": "Income",
        "subcategory": "Salary", "necessity_flag": "necessity",
        "spending_signal": "income", "recurrence": "monthly",
        "is_fixed": False, "is_investment": False
    }
}

SYSTEM_PROMPT = """You are a financial transaction categorizer for Indian bank statements.
You must respond ONLY with a valid JSON object matching the exact schema provided.
No preamble, no markdown formatting blocks, just raw JSON.

Output Schema:
{
  "transactions": [
    {
      "tx_id": "row_001",
      "clean_merchant": "Swiggy",
      "category": "Food & Dining",
      "subcategory": "Food Delivery",
      "necessity_flag": "discretionary", 
      "spending_signal": "lifestyle",
      "recurrence": "frequent", 
      "is_fixed": false,
      "is_investment": false,
      "confidence": 0.95
    }
  ]
}
"""

def scrub_pii(text):
    """Simple PII scrubber: removes 10 digit numbers (phone), UPI IDs, and account numbers."""
    text = str(text)
    text = re.sub(r'\b\d{10}\b', '[PHONE]', text)
    text = re.sub(r'[a-zA-Z0-9.\-_]+@[a-zA-Z]+', '[UPI]', text)
    text = re.sub(r'\b\d{11,16}\b', '[ACCOUNT]', text)
    return text

def parse_all_transactions(df, use_api=True):
    """
    Phase A: Local Regex
    Phase B: Batch Claude API for remaining
    """
    results = {}
    unresolved = []
    
    # Phase A: Local Regex
    for i, row in df.iterrows():
        raw = str(row["raw_description"])
        tx_id = f"row_{i}"
        
        matched = False
        for pattern, attrs in LOCAL_RULES.items():
            if re.search(pattern, raw):
                res = attrs.copy()
                res["tx_id"] = tx_id
                res["confidence"] = 0.99
                results[tx_id] = res
                matched = True
                break
                
        if not matched:
            unresolved.append({"tx_id": tx_id, "raw_description": scrub_pii(raw)})
            
    # Phase B: API Batching
    if use_api and ANTHROPIC_API_KEY and len(unresolved) > 0:
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        
        batch_size = 20
        for i in range(0, len(unresolved), batch_size):
            batch = unresolved[i:i+batch_size]
            prompt = f"Categorize these transactions:\n{json.dumps(batch, indent=2)}"
            
            try:
                response = client.messages.create(
                    model="claude-3-5-haiku-20241022",
                    system=SYSTEM_PROMPT,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=2000,
                    temperature=0
                )
                
                content = response.content[0].text.strip()
                if content.startswith("```json"):
                    content = content[7:-3]
                elif content.startswith("```"):
                    content = content[3:-3]
                    
                parsed = json.loads(content)
                for tx in parsed.get("transactions", []):
                    results[tx["tx_id"]] = tx
                    
                time.sleep(0.5) 
                
            except Exception as e:
                print(f"Warning: Batch API failed. Error: {e}")
                for tx in batch:
                    results[tx["tx_id"]] = {
                        "tx_id": tx["tx_id"],
                        "clean_merchant": "Unknown",
                        "category": "Other",
                        "subcategory": "Other",
                        "necessity_flag": "discretionary",
                        "spending_signal": "lifestyle",
                        "recurrence": "occasional",
                        "is_fixed": False,
                        "is_investment": False,
                        "confidence": 0.1
                    }
    else:
        # Fallback if API off or missing
        for tx in unresolved:
            results[tx["tx_id"]] = {
                "tx_id": tx["tx_id"],
                "clean_merchant": "Unknown",
                "category": "Other",
                "subcategory": "Other",
                "necessity_flag": "discretionary",
                "spending_signal": "lifestyle",
                "recurrence": "occasional",
                "is_fixed": False,
                "is_investment": False,
                "confidence": 0.1
            }
            
    # Reconstruct DF
    out_rows = []
    for i in range(len(df)):
        tx_id = f"row_{i}"
        if tx_id in results:
            out_rows.append(results[tx_id])
        else:
            out_rows.append({
                "tx_id": tx_id,
                "clean_merchant": "Unknown",
                "category": "Other",
                "subcategory": "Other",
                "necessity_flag": "discretionary",
                "spending_signal": "lifestyle",
                "recurrence": "occasional",
                "is_fixed": False,
                "is_investment": False,
                "confidence": 0.0
            })
            
    results_df = pd.DataFrame(out_rows)
    for col in results_df.columns:
        if col != "tx_id":
            df[col] = results_df[col]
            
    return df
