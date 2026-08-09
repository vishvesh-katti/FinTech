from config import BASE_ALLOCATION_GRID

def assess_risk_profile(answers_dict, current_balance=0):
    """
    Assesses risk profile based on questionnaire answers.
    Generates rupee-anchored shortfall explanations to ground the user.
    """
    total_score = sum(answers_dict.values())
    
    if total_score <= 15:
        profile = "Ultra-Conservative"
        description = "Capital preservation is your sole priority. You cannot tolerate any negative returns."
        shortfall_note = f"If the market drops 20%, your portfolio of ₹{current_balance:,.0f} would only drop to roughly ₹{current_balance*0.95:,.0f}."
    elif total_score <= 25:
        profile = "Conservative"
        description = "You prefer steady returns and low volatility over high growth."
        shortfall_note = f"If the market drops 20%, your portfolio of ₹{current_balance:,.0f} would drop to roughly ₹{current_balance*0.92:,.0f}."
    elif total_score <= 35:
        profile = "Moderate"
        description = "You want balanced growth and stability, willing to accept moderate short-term fluctuations."
        shortfall_note = f"If the market drops 20%, your portfolio of ₹{current_balance:,.0f} would drop to roughly ₹{current_balance*0.88:,.0f}."
    elif total_score <= 45:
        profile = "Growth"
        description = "You seek long-term compounding and are comfortable with equity market volatility."
        shortfall_note = f"If the market drops 20%, your portfolio of ₹{current_balance:,.0f} would drop to roughly ₹{current_balance*0.83:,.0f}."
    else:
        profile = "Aggressive"
        description = "You have high risk tolerance and prioritize maximum capital appreciation."
        shortfall_note = f"If the market drops 20%, your portfolio of ₹{current_balance:,.0f} would drop to roughly ₹{current_balance*0.80:,.0f}."
        
    return {
        "profile": profile,
        "score": total_score,
        "description": description,
        "shortfall_note": shortfall_note
    }

def get_base_allocation(profile):
    """Returns the base allocation grid defined in config.py."""
    return BASE_ALLOCATION_GRID.get(profile, BASE_ALLOCATION_GRID["Moderate"])
