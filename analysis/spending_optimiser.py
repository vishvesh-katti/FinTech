def generate_savings_ladder(flow_metrics):
    """
    Generates the 3-Tier Savings Opportunity Ladder.
    Tier 1: Quick Wins (Unused Subscriptions)
    Tier 2: Medium Effort (Lifestyle adjustments)
    Tier 3: High Effort (Structural changes)
    """
    ladder = {
        "Tier 1 (Quick Wins)": [],
        "Tier 2 (Medium Effort)": [],
        "Tier 3 (High Effort)": []
    }
    
    subs = flow_metrics.get("subscription_audit", {})
    if len(subs) > 0:
        ladder["Tier 1 (Quick Wins)"].append({
            "action": f"Cancel 1-2 unused subscriptions from your {len(subs)} detected ones.",
            "est_savings": 500
        })
        
    leakage = flow_metrics.get("leakage_score", 0)
    if leakage > 20:
        ladder["Tier 2 (Medium Effort)"].append({
            "action": "Reduce discretionary dining/shopping by identifying 1 'No-Spend Day' per week.",
            "est_savings": 2000
        })
        
    ladder["Tier 3 (High Effort)"].append({
        "action": "Renegotiate major fixed obligations like Rent or Insurance premiums annually.",
        "est_savings": 5000
    })
    
    return ladder
