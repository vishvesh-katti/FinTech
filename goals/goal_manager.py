import numpy as np

def analyze_goals(goals_list, lump_sum, monthly_surplus, is_real=False, inflation_rate=0.06):
    """
    Analyzes a list of user goals against their deployable lump sum and monthly surplus.
    Supports Nominal vs Real targets.
    """
    sorted_goals = sorted(goals_list, key=lambda x: x["priority"])
    analysis = []
    
    for goal in sorted_goals:
        years = goal["years"]
        months = max(1, years * 12)
        
        target = goal["target_amount"]
        
        # If real, we must inflate the target amount to its future value based on inflation
        if is_real:
            target = target * ((1 + inflation_rate) ** years)
            
        # Conservative assumption for feasibility gating before optimization
        # Use a flat 10% CAGR
        r = 0.10 / 12  
        
        fv_lump_sum = lump_sum * ((1 + r) ** months)
        
        # Required SIP to hit the remainder
        shortfall_fv = target - fv_lump_sum
        required_sip = 0
        if shortfall_fv > 0:
            # PMT = FV * r / ((1+r)^n - 1)
            required_sip = shortfall_fv * r / (((1 + r) ** months) - 1)
            
        is_feasible = required_sip <= monthly_surplus
        
        analysis.append({
            "name": goal["name"],
            "target_amount_nominal": goal["target_amount"],
            "target_amount_future": target,
            "years": years,
            "required_sip": required_sip,
            "is_feasible": is_feasible,
            "is_real_adjusted": is_real
        })
        
    has_conflict = not analysis[0]["is_feasible"]
    conflict_message = ""
    if has_conflict:
        req_sip = analysis[0]["required_sip"]
        conflict_message = f"Goal '{analysis[0]['name']}' requires a SIP of ₹{req_sip:,.0f}/mo, which exceeds your deployable monthly surplus (₹{monthly_surplus:,.0f}). Please reduce the target or extend the horizon before proceeding."
        
    return {
        "goal_analysis": analysis,
        "has_conflict": has_conflict,
        "conflict_message": conflict_message
    }
