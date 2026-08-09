import numpy as np
from scipy.optimize import minimize
from config import BASE_ALLOCATION_GRID
from market.denoiser import denoise_covariance_matrix

def build_portfolio(market_analysis, daily_returns_dict, risk_profile, regime_info, goal_horizon=None):
    """
    Constructs portfolio using 4-step process:
    1. Base Allocation by Risk Profile
    2. Marchenko-Pastur Denoising + Sharpe Maximization
    3. Regime Overlay (Dual-Adaptive Momentum)
    4. Horizon Tilt
    """
    # Step 1: Base Allocation
    base_alloc = BASE_ALLOCATION_GRID.get(risk_profile, BASE_ALLOCATION_GRID["Moderate"])
    assets = list(base_alloc.keys())
    
    try:
        returns_list = [daily_returns_dict[asset] for asset in assets if asset in daily_returns_dict]
        
        min_len = min(len(r) for r in returns_list)
        if min_len < 200: raise ValueError("Not enough data points")
        
        trimmed_returns = np.array([r[-min_len:] for r in returns_list])
        # transpose for denoiser: (days, assets)
        returns_matrix = trimmed_returns.T 
        
        mean_returns = np.array([market_analysis[asset]["cagr"] for asset in assets if asset in market_analysis])
        
        if len(mean_returns) != len(assets):
            raise ValueError("Asset mismatch")
            
        # Step 2: Denoise Covariance Matrix
        cov_matrix = denoise_covariance_matrix(returns_matrix)
        
        num_assets = len(assets)
        risk_free_rate = 0.065
        
        # Objective function: Negative Sharpe
        def neg_sharpe(weights):
            p_ret = np.sum(mean_returns * weights)
            p_vol = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
            return -(p_ret - risk_free_rate) / p_vol
            
        # Constraints: sum to 1
        constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
        
        # Bounds: max = base * 1.5
        bounds = tuple((0, min(1.0, base_alloc[assets[i]] * 1.5 + 0.05)) for i in range(num_assets))
        
        init_guess = np.array([base_alloc[a] for a in assets])
        # normalize
        if np.sum(init_guess) > 0:
            init_guess = init_guess / np.sum(init_guess)
        
        opt_results = minimize(neg_sharpe, init_guess, method='SLSQP', bounds=bounds, constraints=constraints)
        optimized_weights = opt_results.x
        
        # Blend 60/40
        final_weights = np.zeros(num_assets)
        for i, asset in enumerate(assets):
            final_weights[i] = (base_alloc[asset] * 0.6) + (optimized_weights[i] * 0.4)
            
        # Step 3: Regime Overlay
        if regime_info.get("bear_signal", False):
            # Reduce equity by 50%, reallocate to fixed income and gold
            equity_keys = ["indian_large_equity", "indian_mid_equity", "global_equity"]
            freed_weight = 0
            for i, asset in enumerate(assets):
                if asset in equity_keys:
                    reduction = final_weights[i] * 0.5
                    final_weights[i] -= reduction
                    freed_weight += reduction
            
            # Reallocate 50% to liquid, 50% to gold
            if "cash_equivalents" in assets:
                idx = assets.index("cash_equivalents")
                final_weights[idx] += freed_weight * 0.5
            if "gold" in assets:
                idx = assets.index("gold")
                final_weights[idx] += freed_weight * 0.5
                
        elif regime_info.get("hurst_exponent", 0.5) < 0.45:
            # Mean reverting - bump cash equivalents
            if "cash_equivalents" in assets:
                idx = assets.index("cash_equivalents")
                current = final_weights[idx]
                bump = min(0.15, 0.30 - current)
                if bump > 0:
                    final_weights[idx] += bump
                    # proportionally reduce others
                    others_sum = np.sum(final_weights) - final_weights[idx]
                    if others_sum > 0:
                        for i in range(num_assets):
                            if i != idx:
                                final_weights[i] -= final_weights[i] * (bump / others_sum)
                                
        # Step 4: Horizon Tilt
        if goal_horizon is not None:
            if goal_horizon < 3:
                # Shift 20% equity to fixed income
                equity_keys = ["indian_large_equity", "indian_mid_equity", "global_equity"]
                freed = 0
                for i, asset in enumerate(assets):
                    if asset in equity_keys:
                        reduction = final_weights[i] * 0.2
                        final_weights[i] -= reduction
                        freed += reduction
                if "fixed_income" in assets:
                    idx = assets.index("fixed_income")
                    final_weights[idx] += freed
            elif goal_horizon > 7:
                # Shift 10% fixed income to equity
                if "fixed_income" in assets:
                    idx = assets.index("fixed_income")
                    reduction = final_weights[idx] * 0.1
                    final_weights[idx] -= reduction
                    if "indian_large_equity" in assets:
                        eq_idx = assets.index("indian_large_equity")
                        final_weights[eq_idx] += reduction
                        
        # Normalize final weights
        if np.sum(final_weights) > 0:
            final_weights = final_weights / np.sum(final_weights)
        
        blended_allocation = {assets[i]: final_weights[i] for i in range(num_assets)}
        
        # Calculate expected metrics
        expected_p_ret = np.sum(mean_returns * final_weights)
        expected_p_vol = np.sqrt(np.dot(final_weights.T, np.dot(cov_matrix, final_weights)))
        blended_sharpe = (expected_p_ret - risk_free_rate) / expected_p_vol if expected_p_vol > 0 else 0
        
        return {
            "allocation": blended_allocation,
            "expected_cagr": float(expected_p_ret),
            "expected_volatility": float(expected_p_vol),
            "expected_sharpe": float(blended_sharpe)
        }
        
    except Exception as e:
        print(f"Optimization failed: {e}. Falling back to Base Allocation.")
        
        expected_cagr = 0
        expected_vol = 0
        for asset, w in base_alloc.items():
            if asset in market_analysis:
                expected_cagr += w * market_analysis[asset]["cagr"]
                expected_vol += w * market_analysis[asset]["volatility"] 
                
        return {
            "allocation": base_alloc,
            "expected_cagr": float(expected_cagr),
            "expected_volatility": float(expected_vol),
            "expected_sharpe": (expected_cagr - 0.065) / expected_vol if expected_vol > 0 else 0
        }
