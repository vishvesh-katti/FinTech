import pytest
import pandas as pd
from market_routing import calculate_required_cagr, fetch_nifty50_1year_data

def test_cagr_math():
    surplus = 100000
    target = 200000
    years = 7
    # 2^(1/7) - 1 approx 0.104
    cagr = calculate_required_cagr(surplus, target, years)
    assert abs(cagr - 0.104) < 0.001

def test_yfinance_fetch():
    # Note: This test hits the network, might want to mock in real CI/CD, but instructions say:
    # "Assert that the yfinance fetch function returns a non-empty DataFrame with a Close column."
    try:
        df = fetch_nifty50_1year_data()
        assert not df.empty
        assert "Close" in df.columns
    except ConnectionError:
        pytest.skip("No internet connection for yfinance")
