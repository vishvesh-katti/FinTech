import yfinance as yf
import pandas as pd

def fetch_1h_market_data():
    """
    Fetches 2 years of 1-hour data for the Indian asset universe.
    """
    tickers = ["^NSEI", "GOLDBEES.NS", "SILVERBEES.NS", "RELIANCE.NS", "TCS.NS", "ITC.NS", "TATAMOTORS.NS"]
    
    # yfinance enforces a 730d limit on 1h data
    try:
        data = yf.download(tickers, period="730d", interval="1h", group_by="ticker", auto_adjust=False)
        
        # Extract Close prices (or Adj Close if available, but 1h data often just uses Close)
        close_data = pd.DataFrame()
        for ticker in tickers:
            if ticker in data.columns.levels[0]:
                if 'Adj Close' in data[ticker]:
                    close_data[ticker] = data[ticker]['Adj Close']
                else:
                    close_data[ticker] = data[ticker]['Close']
                    
        # Data Cleaning:
        # First, drop any tickers that completely failed to download (all NaNs)
        close_data = close_data.dropna(axis=1, how='all')
        
        # Then forward-fill missing intraday hours
        # and drop rows that still have NaNs (to align the time series)
        clean_data = close_data.ffill().dropna()
        
        return clean_data
        
    except Exception as e:
        print(f"Error fetching data: {e}")
        return pd.DataFrame()
