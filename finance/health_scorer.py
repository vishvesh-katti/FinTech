import numpy as np

def calculate_health_score(metrics, surplus_data):
    """
    Calculates the 6-dimension Financial Health Score (0-850).
    """
    monthly_income = metrics.get("average_monthly_income", 100000)
    
    # Calculate savings rate
    monthly_savings = surplus_data.get("monthly_sip_surplus", 0) + (surplus_data.get("lock_e_short_term", 0) / 12.0)
    savings_rate = monthly_savings / monthly_income if monthly_income > 0 else 0
    
    # 1. Savings Rate (25% -> max 212 pts)
    if savings_rate < 0.10: score_1 = 0
    elif savings_rate < 0.20: score_1 = 150
    elif savings_rate < 0.35: score_1 = 175
    else: score_1 = 212
    
    # 2. Debt Service Ratio (20% -> max 170 pts)
    total_emis = metrics.get("monthly_emi_obligations", 0)
    dsr = total_emis / monthly_income if monthly_income > 0 else 0
    if dsr < 0.20: score_2 = 170
    elif dsr <= 0.35: score_2 = 100
    else: score_2 = 30
    
    # 3. Expense Diversification (15% -> max 127 pts)
    hhi = metrics.get("expense_hhi", 0.30)
    if hhi < 0.20: score_3 = 127
    elif hhi > 0.50: score_3 = 0
    else:
        score_3 = int(127 * (1 - (hhi - 0.20) / 0.30))
        
    # 4. Income Stability (15% -> max 127 pts)
    cv_income = metrics.get("income_cv", 0.05)
    if cv_income < 0.05: score_4 = 127
    elif cv_income > 0.30: score_4 = 0
    else:
        score_4 = int(127 * (1 - (cv_income - 0.05) / 0.25))
        
    # 5. Investment Activity (15% -> max 127 pts)
    inv_activity = metrics.get("has_investments", False)
    if inv_activity:
        score_5 = 127
    else:
        score_5 = 0
        
    # 6. Emergency Fund Adequacy (10% -> max 87 pts)
    current_liquid = surplus_data.get("current_balance", 0)
    monthly_fixed = metrics.get("monthly_fixed_obligations", 30000)
    ef_ratio = current_liquid / monthly_fixed if monthly_fixed > 0 else 6
    if ef_ratio >= 6: score_6 = 87
    elif ef_ratio >= 3: score_6 = 50
    else: score_6 = 0
    
    total_score = score_1 + score_2 + score_3 + score_4 + score_5 + score_6
    total_score = min(total_score, 850)
    
    # Grade
    if total_score >= 750: grade = "A+"
    elif total_score >= 650: grade = "A"
    elif total_score >= 500: grade = "B"
    elif total_score >= 350: grade = "C"
    else: grade = "F"
    
    # Generate Improvement Roadmap
    roadmap = []
    if score_5 == 0:
        roadmap.append("Start a ₹5,000/month SIP. This alone adds +127 points to Investment Activity.")
    if score_6 < 87:
        roadmap.append(f"Build emergency fund to 6x monthly fixed expenses (target: ₹{monthly_fixed * 6:,.0f}).")
    if score_2 < 170:
        roadmap.append("Focus surplus on prepaying high-interest debt to lower your Debt Service Ratio below 20%.")
    if score_1 < 175 and len(roadmap) < 3:
        roadmap.append("Reduce discretionary spending to push your savings rate above 20%.")
        
    # Pad to 3 steps if needed
    if len(roadmap) < 3:
        roadmap.append("Continue tracking expenses monthly to maintain high data quality.")
        
    return {
        "total_score": total_score,
        "grade": grade,
        "components": {
            "savings_rate_score": score_1,
            "dsr_score": score_2,
            "diversification_score": score_3,
            "stability_score": score_4,
            "investment_score": score_5,
            "emergency_fund_score": score_6,
            "dsr": dsr * 100
        },
        "roadmap": roadmap[:3]
    }
