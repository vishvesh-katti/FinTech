import yfinance as yf
import pandas as pd
import numpy as np

def fetch_market_data():
    """Fetches 5-year historical data for Nifty, GoldBeES, and SilverBeES to calculate reliable CAGRs"""
    assets = {
        "Nifty 50": "^NSEI",
        "Gold BeES": "GOLDBEES.NS",
        "Silver BeES": "SILVERBEES.NS"
    }
    
    results = {}
    for name, ticker_symbol in assets.items():
        try:
            ticker = yf.Ticker(ticker_symbol)
            # Fetching 5 years for a more stable historical CAGR
            df = ticker.history(period="5y", auto_adjust=True)
            if not df.empty and len(df) > 200:
                results[name] = df
                continue
        except Exception as e:
            print(f"Warning: yfinance failed to fetch {ticker_symbol}. Error: {e}")
            
        # Fallback data if API fails or returns insufficient data
        print(f"Using fallback data for {name}.")
        # Generate dummy 5-year data simulating typical returns
        # Nifty ~12%, Gold ~9%, Silver ~11%
        days = 252 * 5
        if name == "Nifty 50":
            daily_return = 0.12 / 252
            volatility = 0.15 / np.sqrt(252)
        elif name == "Gold BeES":
            daily_return = 0.09 / 252
            volatility = 0.12 / np.sqrt(252)
        else:
            daily_return = 0.11 / 252
            volatility = 0.18 / np.sqrt(252)
            
        returns = np.random.normal(daily_return, volatility, days)
        price_series = 100 * np.exp(np.cumsum(returns))
        results[name] = pd.DataFrame({"Close": price_series})
        
    return results

def analyze_market_assets(market_data_dict):
    """Calculates historical CAGR and annualized volatility for each asset."""
    analysis = {}
    for name, df in market_data_dict.items():
        prices = df["Close"].values
        start_price = prices[0]
        end_price = prices[-1]
        
        # Calculate years assuming 252 trading days per year
        years = len(prices) / 252.0
        if years < 1:
            years = 1.0 # fallback to prevent division errors
            
        # CAGR calculation
        cagr = (end_price / start_price) ** (1 / years) - 1
        
        # Volatility calculation (annualized standard deviation of daily returns)
        daily_returns = np.diff(prices) / prices[:-1]
        volatility = np.std(daily_returns) * np.sqrt(252)
        
        analysis[name] = {
            "cagr": float(cagr),
            "volatility": float(volatility)
        }
    return analysis

def project_growth(deployable_surplus, years, asset_analysis):
    """Projects future wealth based on deployable surplus and historical asset performance."""
    projections = {}
    for name, metrics in asset_analysis.items():
        cagr = metrics["cagr"]
        
        # Basic deterministic compound growth: FV = PV * (1 + r)^n
        # Assuming deployable surplus is invested monthly. 
        # Future value of an annuity formula: P * [((1 + r/12)^(12*t) - 1) / (r/12)] * (1 + r/12)
        # But wait, deployable surplus in the app is calculated as a single lump sum representing the *current* balance minus locked capital.
        # It's a lump sum investment.
        projected_amount = deployable_surplus * ((1 + cagr) ** years)
        
        projections[name] = {
            "cagr": cagr,
            "projected_amount": float(projected_amount)
        }
    return projections

