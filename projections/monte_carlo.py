import numpy as np

def run_monte_carlo_simulation(initial_capital, expected_return, volatility, time_horizon_months, simulations=10000):
    """
    Vectorized Geometric Brownian Motion with Merton Jump Diffusion.
    """
    # Time in years
    T = time_horizon_months / 12.0
    dt = 1.0 / 12.0 # monthly timesteps
    N_steps = time_horizon_months
    
    # Pre-allocate paths
    paths = np.zeros((simulations, N_steps + 1))
    paths[:, 0] = initial_capital
    
    drift = expected_return - (volatility**2) / 2.0
    
    # Generate all standard normal random variables at once
    Z = np.random.standard_normal((simulations, N_steps))
    
    # Merton Jump Parameters
    lambda_jump = 0.05 / 12.0 # 5% per year chance, converted to monthly probability
    mu_j = -0.20
    sigma_j = 0.05
    
    # Generate jump occurrences (Poisson)
    jump_mask = np.random.uniform(0, 1, (simulations, N_steps)) < lambda_jump
    # Generate jump sizes (Normal centered at -0.20)
    jump_sizes = np.random.normal(mu_j, sigma_j, (simulations, N_steps))
    
    for t in range(N_steps):
        # Base GBM step return
        step_return = np.exp(drift * dt + volatility * Z[:, t] * np.sqrt(dt))
        
        # Apply jump multiplier if jump occurred
        jump_multiplier = np.where(jump_mask[:, t], 1 + jump_sizes[:, t], 1.0)
        
        paths[:, t+1] = paths[:, t] * step_return * jump_multiplier
        
    final_values = paths[:, -1]
    
    # Calculate percentiles for charting
    # Percentile arrays along the time axis
    p10_path = np.percentile(paths, 10, axis=0)
    p50_path = np.percentile(paths, 50, axis=0)
    p90_path = np.percentile(paths, 90, axis=0)
    
    return {
        "final_values": final_values,
        "p10_path": p10_path.tolist(),
        "p50_path": p50_path.tolist(),
        "p90_path": p90_path.tolist()
    }
