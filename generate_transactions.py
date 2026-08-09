import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os

# Ensure data directory exists
os.makedirs("data", exist_ok=True)

START_DATE = datetime(2024, 1, 1)

MERCHANTS = {
    "Food": [("Zomato", 300, 800), ("Swiggy", 300, 800), ("Starbucks", 250, 500), ("McDonalds", 200, 600)],
    "Grocery": [("BigBasket", 1000, 3000), ("Blinkit", 300, 800), ("D-Mart", 2000, 5000), ("Instamart", 200, 900)],
    "Transport": [("Uber", 150, 400), ("Ola Cabs", 150, 400), ("Namma Metro", 50, 200), ("Indian Oil", 1000, 3000)],
    "Shopping": [("Amazon", 500, 3000), ("Myntra", 1000, 4000), ("Flipkart", 500, 2000)],
    "Health": [("Apollo Pharmacy", 200, 1000), ("Practo", 500, 1000), ("Cult Fit", 1500, 1500)],
    "UPI_Transfers": [("UPI: Rahul Split", 200, 1000), ("UPI: Mom", 2000, 5000), ("UPI: Maid", 1500, 3000)],
    "Cash": [("ATM Withdrawal", 2000, 10000)]
}

def generate_tx(months, profile):
    transactions = []
    end_date = START_DATE + timedelta(days=30 * months)
    total_days = (end_date - START_DATE).days
    
    salary = 200000
    if profile == "accumulator":
        rent, emi, sip = 40000, 0, 80000
        discretionary_freq = 5
    elif profile == "impulse":
        rent, emi, sip = 40000, 10000, 5000
        discretionary_freq = 30
    elif profile == "debt_juggler":
        rent, emi, sip = 30000, 90000, 0
        discretionary_freq = 15
    elif profile == "neglectful":
        rent, emi, sip = 40000, 0, 0
        discretionary_freq = 20
    elif profile == "freelancer":
        rent, emi, sip = 30000, 0, 10000
        discretionary_freq = 15
    else: # balancer
        rent, emi, sip = 40000, 20000, 20000
        discretionary_freq = 15

    # Running balance tracking (just a rough estimate)
    balance = 100000.0

    # Base fixed transactions
    for m in range(months):
        month_date = START_DATE + timedelta(days=m * 30)
        
        if profile == "freelancer":
            for _ in range(random.randint(2, 6)):
                d = month_date + timedelta(days=random.randint(1, 28))
                amt = round(random.uniform(30000, 80000), 2)
                balance += amt
                transactions.append({"Date": d.strftime("%d-%m-%Y"), "Narration": "NEFT: CLIENT PAYMENT", "Withdrawal": 0.0, "Deposit": amt, "Balance": balance})
            if m % 3 == 0:
                d = month_date + timedelta(days=15)
                balance -= 25000.0
                transactions.append({"Date": d.strftime("%d-%m-%Y"), "Narration": "UPI: GST PAYMENT", "Withdrawal": 25000.0, "Deposit": 0.0, "Balance": balance})
        else:
            d = month_date.replace(day=1)
            balance += salary
            transactions.append({"Date": d.strftime("%d-%m-%Y"), "Narration": "NEFT: SALARY CREDIT", "Withdrawal": 0.0, "Deposit": salary, "Balance": balance})

        # Rent
        if rent > 0:
            d = month_date.replace(day=2)
            balance -= rent
            transactions.append({"Date": d.strftime("%d-%m-%Y"), "Narration": "UPI: RENT", "Withdrawal": rent, "Deposit": 0.0, "Balance": balance})
        
        # EMI
        if emi > 0:
            d = month_date.replace(day=5)
            balance -= emi
            transactions.append({"Date": d.strftime("%d-%m-%Y"), "Narration": "ACH: LOAN EMI", "Withdrawal": emi, "Deposit": 0.0, "Balance": balance})
            if profile == "debt_juggler":
                d = month_date.replace(day=12)
                balance -= 30000.0
                transactions.append({"Date": d.strftime("%d-%m-%Y"), "Narration": "ACH: PERSONAL LOAN EMI", "Withdrawal": 30000.0, "Deposit": 0.0, "Balance": balance})
                d = month_date.replace(day=18)
                balance -= 40000.0
                transactions.append({"Date": d.strftime("%d-%m-%Y"), "Narration": "CREDIT CARD BILL", "Withdrawal": 40000.0, "Deposit": 0.0, "Balance": balance})
                
        # SIP
        if sip > 0:
            d = month_date.replace(day=7)
            balance -= sip
            transactions.append({"Date": d.strftime("%d-%m-%Y"), "Narration": "ACH: MUTUAL FUND SIP", "Withdrawal": sip, "Deposit": 0.0, "Balance": balance})
            
        # Subs
        d = month_date.replace(day=10)
        balance -= 649.0
        transactions.append({"Date": d.strftime("%d-%m-%Y"), "Narration": "POS: NETFLIX", "Withdrawal": 649.0, "Deposit": 0.0, "Balance": balance})
        
        # Variable
        for _ in range(discretionary_freq):
            d = month_date + timedelta(days=random.randint(1, 28))
            
            # Impulse spender does more weekend spending
            if profile == "impulse" and d.weekday() >= 5:
                # 3x more transactions on weekend
                for _ in range(3):
                    merchant, min_amt, max_amt = random.choice(MERCHANTS["Food"] + MERCHANTS["Shopping"])
                    amt = round(random.uniform(min_amt, max_amt), 2)
                    balance -= amt
                    transactions.append({"Date": d.strftime("%d-%m-%Y"), "Narration": f"POS: {merchant.upper()}", "Withdrawal": amt, "Deposit": 0.0, "Balance": balance})
            
            cat = random.choice(list(MERCHANTS.keys()))
            merchant, min_amt, max_amt = random.choice(MERCHANTS[cat])
            amt = round(random.uniform(min_amt, max_amt), 2)
            balance -= amt
            transactions.append({"Date": d.strftime("%d-%m-%Y"), "Narration": f"UPI/POS: {merchant.upper()}", "Withdrawal": amt, "Deposit": 0.0, "Balance": balance})

    # Convert to DataFrame
    df = pd.DataFrame(transactions)
    df["DateObj"] = pd.to_datetime(df["Date"], format="%d-%m-%Y")
    df = df.sort_values("DateObj").drop(columns=["DateObj"])
    
    # Recalculate true running balance properly over time
    final_balance = 100000.0
    for idx in df.index:
        final_balance += df.loc[idx, "Deposit"] - df.loc[idx, "Withdrawal"]
        df.loc[idx, "Balance"] = final_balance

    return df

def map_columns(df, format_type):
    if format_type == "HDFC":
        return df.rename(columns={"Date": "Txn Date", "Narration": "Description", "Withdrawal": "Debit", "Deposit": "Credit", "Balance": "Closing Balance"})
    elif format_type == "SBI":
        return df.rename(columns={"Date": "Txn Date", "Narration": "Description", "Withdrawal": "Debit", "Deposit": "Credit", "Balance": "Balance"})
    elif format_type == "ICICI":
        return df.rename(columns={"Date": "Value Date", "Narration": "Transaction Remarks", "Withdrawal": "Withdrawal Amt (INR)", "Deposit": "Deposit Amt (INR)", "Balance": "Balance (INR)"})
    elif format_type == "MERGED":
        # Create a single "Amount" column with +/-
        df2 = df.copy()
        df2["Amount"] = df2["Deposit"] - df2["Withdrawal"]
        df2 = df2.drop(columns=["Withdrawal", "Deposit"])
        return df2.rename(columns={"Date": "Date", "Narration": "Particulars", "Amount": "Amount", "Balance": "Balance"})
    return df

def generate_data_issues():
    df = generate_tx(6, "balancer")
    
    # 1. Duplicates
    dupes = df.sample(5).copy()
    df = pd.concat([df, dupes], ignore_index=True)
    
    # 2. Extreme Outlier (Massive cash withdrawal)
    outlier = pd.DataFrame([{"Date": START_DATE.strftime("%d-%m-%Y"), "Narration": "ATM WITHDRAWAL", "Withdrawal": 500000.0, "Deposit": 0.0, "Balance": 0.0}])
    df = pd.concat([df, outlier], ignore_index=True)
    
    # 3. Gaps - drop a whole month
    df["DateObj"] = pd.to_datetime(df["Date"], format="%d-%m-%Y")
    df = df[df["DateObj"].dt.month != 3] # drop march
    df = df.sort_values("DateObj").drop(columns=["DateObj"])
    
    return df

def generate_short_history():
    return generate_tx(2, "balancer")

if __name__ == "__main__":
    profiles_and_formats = {
        "accumulator": "HDFC",
        "impulse": "ICICI",
        "debt_juggler": "SBI",
        "neglectful": "MERGED",
        "freelancer": "DEFAULT",
        "balancer": "HDFC"
    }
    
    for p, fmt in profiles_and_formats.items():
        df = generate_tx(12, p)
        df = map_columns(df, fmt)
        filename = f"data/stress_{p}.csv"
        df.to_csv(filename, index=False)
        print(f"✅ Generated 12 months for {p} ({fmt} format): {len(df)} transactions at {filename}")
        
    df_issues = generate_data_issues()
    df_issues = map_columns(df_issues, "HDFC")
    df_issues.to_csv("data/stress_data_issues.csv", index=False)
    print(f"✅ Generated data issues case: {len(df_issues)} transactions at data/stress_data_issues.csv")
    
    df_short = generate_short_history()
    df_short = map_columns(df_short, "ICICI")
    df_short.to_csv("data/stress_short_history.csv", index=False)
    print(f"✅ Generated short history case: {len(df_short)} transactions at data/stress_short_history.csv")
