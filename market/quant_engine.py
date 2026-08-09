import numpy as np
import pandas as pd
from scipy.optimize import minimize

def calculate_hurst_exponent(price_series, max_lag=20):
    lags = range(2, max_lag)
    log_returns = np.diff(np.log(price_series))
    
    rs_vals = []
    for lag in lags:
        chunks = len(log_returns) // lag
        if chunks == 0: continue
        trimmed = log_returns[:chunks * lag]
        reshaped = trimmed.reshape((chunks, lag))
        
        chunk_means = np.mean(reshaped, axis=1, keepdims=True)
        mean_adj = reshaped - chunk_means
        cum_dev = np.cumsum(mean_adj, axis=1)
        
        R = np.max(cum_dev, axis=1) - np.min(cum_dev, axis=1)
        S = np.std(reshaped, axis=1)
        S[S == 0] = 1e-10
        rs = R / S
        rs_vals.append(np.mean(rs))
        
    if len(rs_vals) < 2: return 0.5
    reg = np.polyfit(np.log(lags[:len(rs_vals)]), np.log(rs_vals), 1)
    return reg[0]

def analyze_asset_behavior(df_1month, fast_ema=10, slow_ema=30):
    """
    Profiles assets over the last month.
    """
    profiles = {}
    for asset in df_1month.columns:
        prices = df_1month[asset]
        if prices.empty: continue
        
        # 1. Momentum
        ema_fast = prices.ewm(span=fast_ema, adjust=False).mean().iloc[-1]
        ema_slow = prices.ewm(span=slow_ema, adjust=False).mean().iloc[-1]
        trend = "Bullish" if ema_fast > ema_slow else "Bearish"
        
        # 2. Regime (Hurst)
        hurst = calculate_hurst_exponent(prices.values)
        if hurst > 0.55:
            regime = "Trending"
        elif hurst < 0.45:
            regime = "Mean-Reverting"
        else:
            regime = "Random Walk"
            
        # 3. Volatility (Annualized intraday using 1575)
        log_returns = np.log(prices / prices.shift(1)).dropna()
        ann_vol = log_returns.std() * np.sqrt(1575)
        
        profiles[asset] = {
            "Trend": trend,
            "Regime": regime,
            "Hurst": float(hurst),
            "Volatility": float(ann_vol)
        }
    return profiles

def metals_stat_arb(df):
    """
    Isolates GoldBees and SilverBees to find stat-arb signals.
    """
    if df.empty or "GOLDBEES.NS" not in df.columns or "SILVERBEES.NS" not in df.columns:
        return None
        
    gold = df["GOLDBEES.NS"]
    silver = df["SILVERBEES.NS"]
    ratio = gold / silver
    
    # 30-day roughly equals 30 * 6.25 = 187 hours
    window = 187
    rolling_mean = ratio.rolling(window=window).mean()
    rolling_std = ratio.rolling(window=window).std()
    
    z_score = (ratio - rolling_mean) / rolling_std
    current_z = z_score.iloc[-1]
    
    signal = "Neutral"
    if current_z > 2.0:
        signal = "Buy Silver (Silver is undervalued relative to Gold)"
    elif current_z < -2.0:
        signal = "Buy Gold (Gold is undervalued relative to Silver)"
        
    # Return time series for plotting and current signal
    return {
        "ratio": ratio,
        "z_score": z_score,
        "current_z": float(current_z),
        "signal": signal
    }

def denoise_covariance_matrix(empirical_cov, T, N):
    """
    Clips noise eigenvalues using Marchenko-Pastur threshold.
    """
    # Calculate eigenvalues and eigenvectors
    vals, vecs = np.linalg.eigh(empirical_cov)
    
    # Marchenko-Pastur threshold
    q = T / N
    if q < 1: q = 1 # Fallback
    
    # Variance of the random part (approximate by median of eigenvalues)
    var = np.median(vals)
    lambda_max = var * (1 + (1/q)**0.5)**2
    
    # Clip eigenvalues
    denoised_vals = np.where(vals > lambda_max, vals, vals.mean())
    
    # Reconstruct
    denoised_cov = vecs @ np.diag(denoised_vals) @ vecs.T
    return denoised_cov

def optimize_portfolio(df):
    """
    Sharpe maximization with Marchenko-Pastur Denoising.
    """
    assets = list(df.columns)
    N = len(assets)
    T = len(df)
    
    if N == 0 or T == 0:
        return {}
        
    log_returns = np.log(df / df.shift(1)).dropna()
    
    # Annualization factor 1575
    mean_returns = log_returns.mean() * 1575
    empirical_cov = log_returns.cov() * 1575
    
    denoised_cov = denoise_covariance_matrix(empirical_cov.values, T, N)
    
    risk_free_rate = 0.07 # 7% FD
    
    def neg_sharpe(weights):
        p_ret = np.sum(mean_returns.values * weights)
        p_vol = np.sqrt(np.dot(weights.T, np.dot(denoised_cov, weights)))
        if p_vol == 0: return 0
        return -(p_ret - risk_free_rate) / p_vol
        
    constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
    bounds = tuple((0.0, 1.0) for _ in range(N))
    init_guess = np.ones(N) / N
    
    opt_results = minimize(neg_sharpe, init_guess, method='SLSQP', bounds=bounds, constraints=constraints)
    
    weights = opt_results.x
    
    expected_ret = np.sum(mean_returns.values * weights)
    expected_vol = np.sqrt(np.dot(weights.T, np.dot(denoised_cov, weights)))
    
    return {
        "weights": {assets[i]: float(weights[i]) for i in range(N)},
        "expected_cagr": float(expected_ret),
        "expected_volatility": float(expected_vol),
        "sharpe_ratio": float((expected_ret - risk_free_rate) / expected_vol) if expected_vol > 0 else 0
    }
