def calculate_deployable_surplus(current_balance, metrics, short_term_goal_amt=0):
    """
    Calculates the 5-Lock Deployable Surplus system based on user flow metrics.
    """
    # LOCK A: Fixed Obligations Reserve (1 month buffer)
    lock_a = metrics.get("monthly_fixed_obligations", 0)
    
    # LOCK B: Dynamic Variable Reserve
    avg_variable = metrics.get("monthly_variable_spend", 0)
    cv_disc = metrics.get("discretionary_cv", 0.20)
    multiplier = max(1.15, min(1.40, 1 + cv_disc))
    lock_b = avg_variable * multiplier
    
    # LOCK C: Emergency Fund
    cv_income = metrics.get("income_cv", 0.05)
    # Freelancers (high volatility) get strict 6x minimum
    if cv_income > 0.20:
        lock_c_base = lock_a * 6
        lock_c_cons = lock_a * 6
    else:
        lock_c_base = lock_a * 3
        lock_c_cons = lock_a * 6
        
    # LOCK D: Tax Liability Reserve
    is_self_employed = metrics.get("is_self_employed", False)
    if is_self_employed:
        # Rough proxy: 30% of net surplus reserved for advance tax
        net = metrics.get("average_monthly_income", 0) - lock_a - avg_variable
        lock_d = net * 0.30 if net > 0 else 0
    else:
        lock_d = 0
        
    # LOCK E: Short-Term Goal Reserve
    lock_e = short_term_goal_amt
    
    # Calculate Surpluses
    total_locks_base = lock_a + lock_b + lock_c_base + lock_d + lock_e
    total_locks_cons = lock_a + lock_b + lock_c_cons + lock_d + lock_e
    
    surplus_base = max(0, current_balance - total_locks_base)
    surplus_cons = max(0, current_balance - total_locks_cons)
    
    # Optimistic Surplus: assumes Tier-1 savings (unused subscriptions) are redirected
    tier_1_savings = metrics.get("tier_1_savings_potential", 0)
    # Multiply by 12 since surplus is typically a lump sum calculated from balance over time
    # but tier_1 is monthly. So we just assume 1 month of savings for the immediate optimistic view.
    surplus_opt = surplus_base + tier_1_savings
    
    return {
        "current_balance": float(current_balance),
        "lock_a_fixed": float(lock_a),
        "lock_b_variable": float(lock_b),
        "lock_c_emergency_base": float(lock_c_base),
        "lock_c_emergency_cons": float(lock_c_cons),
        "lock_d_tax": float(lock_d),
        "lock_e_short_term": float(lock_e),
        "deployable_surplus": {
            "conservative": float(surplus_cons),
            "base": float(surplus_base),
            "optimistic": float(surplus_opt)
        },
        "monthly_sip_surplus": float(surplus_base / 12.0) if surplus_base > 0 else 0.0
    }
