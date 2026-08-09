def generate_action_plan(health_score, flow_metrics, surplus_data, portfolio, probability_of_success, monthly_sip_amount):
    """
    Generates a customized, prioritized action checklist gated by probability of success.
    """
    plan = {
        "Immediate (This Week)": [],
        "Short-Term (This Month)": [],
        "Medium-Term (This Quarter)": [],
        "Long-Term (Annual)": []
    }
    
    if probability_of_success < 0.50:
        plan["Immediate (This Week)"].append("Re-evaluate Goal Parameters: This plan is not mathematically viable. Please use the Resolution Engine below to adjust your target, horizon, or SIP amount.")
        return plan # Return early, do not suggest execution steps
        
    # Immediate
    leakage = flow_metrics.get("leakage_score", 0)
    subs = flow_metrics.get("subscription_audit", {})
    if leakage > 30 or len(subs) > 3:
        plan["Immediate (This Week)"].append("Audit and cancel identified unused subscriptions to unlock monthly surplus.")
        
    if health_score.get("components", {}).get("dsr", 0) > 35:
        plan["Immediate (This Week)"].append("Review credit card statements and set auto-pay for full amount to avoid interest traps.")
    else:
        plan["Immediate (This Week)"].append("Set up an auto-sweep FD or LIQUIDBEES to earn interest on your idle liquid buffer.")
        
    if probability_of_success < 0.80:
        plan["Immediate (This Week)"].append("Note: This plan is viable but has a high risk of failure. Consider using the sliders above to raise your probability before executing.")
        return plan # Hold execution steps pending
        
    # Short-Term (Execution)
    if surplus_data.get("is_surplus_zero", True) and monthly_sip_amount <= 0:
        plan["Short-Term (This Month)"].append("Identify discretionary spending to cut to create a deployable surplus.")
    else:
        plan["Short-Term (This Month)"].append("Open a Demat/Brokerage account (e.g., Zerodha, Groww) if not already active.")
        
        lump_sum = surplus_data.get('deployable_surplus_base', 0)
        stp_note = " via STP (Systematic Transfer Plan) over the next 12 weeks" if portfolio.get("stp_recommended", False) else " as a lump sum"
        plan["Short-Term (This Month)"].append(f"Deploy ₹{lump_sum:,.0f}{stp_note} towards your recommended portfolio allocation.")
        
    if surplus_data.get("locked_capital", {}).get("emergency_fund_base", 0) > surplus_data.get("current_balance", 0):
         plan["Short-Term (This Month)"].append("Direct all new savings toward building your 3-month emergency fund before investing in equity.")
         
    # Medium-Term
    if monthly_sip_amount > 0:
        plan["Medium-Term (This Quarter)"].append(f"Initiate your core portfolio deployment with a ₹{monthly_sip_amount:,.0f} monthly SIP.")
        
    plan["Medium-Term (This Quarter)"].append("Review your term insurance and health insurance coverage to ensure dependents are protected.")
    plan["Medium-Term (This Quarter)"].append("Set a calendar reminder for a portfolio review in 6 months.")
    
    # Long-Term
    plan["Long-Term (Annual)"].append("Step up your SIP amount by 10% next year to match salary growth.")
    plan["Long-Term (Annual)"].append("Rebalance your portfolio if any asset class drifts more than 5% from its target allocation.")
    
    return plan
