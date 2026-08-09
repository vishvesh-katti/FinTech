from projections.monte_carlo import run_monte_carlo_simulation
import numpy as np

def calculate_resolution(prob_success, investable_capital, idle_surplus, expected_return, volatility, time_horizon_months, target_capital):
    """
    Algorithmic intervention if probability of success < 80%.
    """
    if prob_success >= 0.80:
        return None
        
    # Iteration Logic 1: Capital Fix
    # Incrementally add from idle surplus in steps of 5000
    current_capital = investable_capital
    max_capital = investable_capital + idle_surplus
    step_size = 5000
    
    while current_capital < max_capital:
        current_capital += step_size
        if current_capital > max_capital:
            current_capital = max_capital
            
        res = run_monte_carlo_simulation(current_capital, expected_return, volatility, time_horizon_months, simulations=2000)
        prob = np.sum(res["final_values"] >= target_capital) / 2000.0
        
        if prob >= 0.80:
            extra_needed = current_capital - investable_capital
            return {
                "type": "Capital Fix",
                "message": f"Your current plan only has a {prob_success*100:.1f}% chance of success. To reach an 80% safe threshold, you must deploy an additional ₹{extra_needed:,.0f} from your remaining bank surplus today."
            }
            
    # Iteration Logic 2: Time Fix
    # If we exhaust idle surplus, reset capital to max and increase time
    current_time = time_horizon_months
    
    while current_time <= time_horizon_months + 120: # cap at extra 10 years
        current_time += 1
        res = run_monte_carlo_simulation(max_capital, expected_return, volatility, current_time, simulations=2000)
        prob = np.sum(res["final_values"] >= target_capital) / 2000.0
        
        if prob >= 0.80:
            extra_months = current_time - time_horizon_months
            total_extra_capital = max_capital - investable_capital
            
            msg = f"Your current plan only has a {prob_success*100:.1f}% chance of success. To reach an 80% safe threshold, you must deploy your remaining surplus (₹{total_extra_capital:,.0f}) AND extend your timeline by {extra_months} months."
            if total_extra_capital <= 0:
                msg = f"Your current plan only has a {prob_success*100:.1f}% chance of success. To reach an 80% safe threshold, you must extend your timeline by {extra_months} months."
                
            return {
                "type": "Time Fix",
                "message": msg
            }
            
    return {
        "type": "Unresolvable",
        "message": f"Your goal is mathematically unsafe (Prob: {prob_success*100:.1f}%). Even after deploying all surplus and extending time by 10 years, it remains below 80%. Please significantly reduce your Target Profit."
    }
