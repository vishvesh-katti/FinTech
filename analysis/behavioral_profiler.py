def profile_behavior(flow_metrics, health_score, current_balance=0):
    """
    Categorizes the user into one of 6 financial personality types.
    Calculates the 'Cost of Idle Cash' for The Accumulator.
    """
    leakage = flow_metrics.get("leakage_score", 0)
    savings_rate = health_score.get("components", {}).get("savings_rate_score", 0) / 212.0 # roughly normalize to percentage potential
    
    # 6 Personality Types as per PRD
    profile = "The Balancer"
    insight = "You have a healthy split between needs, wants, and savings."
    action = "Focus on optimizing your asset allocation to maximize returns."
    cost_of_idle_cash = 0
    
    if savings_rate > 0.8 and leakage < 15:
        profile = "The Accumulator"
        insight = "You save aggressively and keep discretionary spending low."
        action = "Ensure you're investing efficiently to beat inflation, not just hoarding cash."
        if current_balance > 500000:
            # Opportunity cost: 12% equity proxy vs 4% savings rate
            cost_of_idle_cash = current_balance * (0.12 - 0.04)
            insight += f" Note: Holding ₹{current_balance:,.0f} in idle cash costs you ~₹{cost_of_idle_cash:,.0f} per year in lost compounding."
            
    elif leakage > 40:
        profile = "The Impulse Spender"
        insight = "Your discretionary spending heavily outweighs your structural savings."
        action = "Implement a 24-hour rule before making non-essential purchases."
        
    elif flow_metrics.get("total_outflow", 0) > 0 and savings_rate < 0.2:
        dsr = health_score.get("components", {}).get("dsr", 0)
        if dsr > 35:
            profile = "The Debt Juggler"
            insight = "High fixed obligations (EMIs) are severely restricting your ability to build wealth."
            action = "Focus entirely on debt reduction (avalanche method) to free up cash flow."
        else:
            profile = "The Neglectful Saver"
            insight = "You have the capacity to save, but lack a systematic structure."
            action = "Automate your savings directly on payday so it's out of sight."
            
    elif health_score.get("components", {}).get("stability_score", 127) < 50:
        profile = "The Freelancer"
        insight = "Your income exhibits high volatility month-to-month."
        action = "Build a larger 6-month emergency buffer before locking capital in equity."
        
    return {
        "personality_type": profile,
        "insight": insight,
        "action": action,
        "cost_of_idle_cash": float(cost_of_idle_cash)
    }
