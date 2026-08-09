import numpy as np
import pandas as pd

def calculate_hurst_exponent(price_series, max_lag=20):
    """
    Calculates the Hurst Exponent of a price series using Rescaled Range Analysis.
    price_series: 1D array of prices (e.g. hourly close)
    """
    lags = range(2, max_lag)
    # Calculate log returns
    log_returns = np.diff(np.log(price_series))
    
    # Calculate RS
    rs_vals = []
    for lag in lags:
        # Split into chunks
        chunks = len(log_returns) // lag
        if chunks == 0:
            continue
        trimmed_returns = log_returns[:chunks * lag]
        reshaped = trimmed_returns.reshape((chunks, lag))
        
        # Calculate mean for each chunk
        chunk_means = np.mean(reshaped, axis=1, keepdims=True)
        # Mean adjusted series
        mean_adj = reshaped - chunk_means
        # Cumulative deviations
        cum_dev = np.cumsum(mean_adj, axis=1)
        # Range
        R = np.max(cum_dev, axis=1) - np.min(cum_dev, axis=1)
        # Standard deviation
        S = np.std(reshaped, axis=1)
        
        # Avoid division by zero
        S[S == 0] = 1e-10
        rs = R / S
        rs_vals.append(np.mean(rs))
        
    if len(rs_vals) < 2:
        return 0.5
        
    # Fit line to log-log plot
    reg = np.polyfit(np.log(lags[:len(rs_vals)]), np.log(rs_vals), 1)
    hurst = reg[0]
    return hurst

def detect_market_regime(nifty_hourly_df, nifty_daily_df):
    """
    Implements Dual-Adaptive EMA crossover and Hurst Exponent regime detection.
    """
    if nifty_hourly_df is None or nifty_daily_df is None or len(nifty_daily_df) < 200:
        return {
            "regime": "UNKNOWN",
            "hurst_exponent": 0.5,
            "bear_signal": False,
            "stp_recommended": False,
            "context_note": "Live data unavailable — using cached signals. Regime assessment may be stale."
        }
        
    # 1. Hurst Exponent on hourly log-returns
    hourly_prices = nifty_hourly_df["Close"].values
    hurst = calculate_hurst_exponent(hourly_prices, max_lag=20)
    
    # 2. Dual-Adaptive EMA on daily close
    daily_close = nifty_daily_df["Close"]
    current_price = daily_close.iloc[-1]
    
    ema_50 = daily_close.ewm(span=50, adjust=False).mean()
    ema_200 = daily_close.ewm(span=200, adjust=False).mean()
    
    current_ema_50 = ema_50.iloc[-1]
    current_ema_200 = ema_200.iloc[-1]
    
    # BEAR SIGNAL: Death cross + price < 200 EMA
    bear_signal = (current_ema_50 < current_ema_200) and (current_price < current_ema_200)
    
    # Synthetic P/E for froth detection (in real app, fetched from API)
    synthetic_pe = 22.0
    
    # Regime Classification
    stp_recommended = False
    
    if bear_signal:
        regime = "BEAR"
        note = "Nifty is below its 200 DMA with a bearish crossover. Markets are in a bearish phase. Equity allocation reduced."
        stp_recommended = True
    elif current_price >= current_ema_200 and hurst > 0.55 and synthetic_pe > 25:
        regime = "FROTHY"
        note = f"Markets are extended. Nifty PE at ~{synthetic_pe}. Consider deploying via STP rather than lump sum."
        stp_recommended = True
    elif current_price > current_ema_200 and ema_50.iloc[-2] < ema_200.iloc[-2] and current_ema_50 >= current_ema_200:
        regime = "RECOVERY"
        note = "Nifty has just crossed above its 200 DMA from below. This is a strong recovery signal."
    else:
        regime = "BULL"
        note = "Markets are above the 200 DMA. Trend is positive."
        
    if hurst < 0.45 and not bear_signal:
        note += " Market is choppy/mean-reverting. STP is recommended."
        stp_recommended = True
        
    return {
        "regime": regime,
        "hurst_exponent": float(hurst),
        "bear_signal": bool(bear_signal),
        "stp_recommended": bool(stp_recommended),
        "context_note": note,
        "current_price": float(current_price),
        "ema_50": float(current_ema_50),
        "ema_200": float(current_ema_200)
    }
