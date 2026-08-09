def project_scenarios(portfolio, lump_sum, monthly_investment, years):
    """
    Projects Bear, Base, and Bull case scenarios.
    Returns year-by-year corpus values.
    """
    base_cagr = portfolio["expected_cagr"]
    volatility = portfolio["expected_volatility"]
    
    # Define scenarios
    scenarios = {
        "Pessimistic (Bad decade)": base_cagr - volatility,
        "Expected (Historical average)": base_cagr,
        "Optimistic (Strong decade)": base_cagr + (0.5 * volatility)
    }
    
    months = years * 12
    projections = {}
    
    for name, rate in scenarios.items():
        monthly_rate = rate / 12
        corpus_path = []
        current_corpus = float(lump_sum)
        
        for m in range(1, months + 1):
            current_corpus = current_corpus * (1 + monthly_rate) + monthly_investment
            if m % 12 == 0:
                corpus_path.append(current_corpus)
                
        projections[name] = {
            "cagr": float(rate),
            "final_corpus": float(current_corpus),
            "path": [float(x) for x in corpus_path]
        }
        
    return projections
