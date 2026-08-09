import streamlit as st
import pandas as pd
import numpy as np

# Imports for V3 Pipeline
from ingestion.data_loader import clean_bank_data
from analysis.categoriser import categorize_transactions
from analysis.flow_analyser import spending_quality_analysis
from market.data_fetcher import fetch_1h_market_data
from market.metrics_engine import compare_historical_returns
from market.quant_engine import analyze_asset_behavior, metals_stat_arb, optimize_portfolio
from projections.monte_carlo import run_monte_carlo_simulation
from projections.resolution_engine import calculate_resolution

from ui.charts import (plot_needs_wants_pie, plot_asset_comparison, 
                       plot_stat_arb_oscillator, plot_portfolio_donut, 
                       plot_monte_carlo_fan)
from ui.cards import metric_card, alert_banner
from config import format_inr

st.set_page_config(page_title="RetailQuant V3", layout="wide", initial_sidebar_state="expanded")

# Dark Theme CSS
st.markdown("""
<style>
    .stApp { background-color: #0A0F1E; color: #FFFFFF; }
    h1, h2, h3, h4 { color: #FFFFFF; font-family: 'Inter', sans-serif; }
    .gold-text { color: #FFD700; }
    hr { border-top: 1px solid #1E2A3A; }
    div[data-testid="stSidebar"] { background-color: #121A2F; }
</style>
""", unsafe_allow_html=True)

st.title("RetailQuant V3: Deterministic Quant Engine")
st.markdown("<hr>", unsafe_allow_html=True)

# Session State Initialization
if "raw_df" not in st.session_state: st.session_state.raw_df = None
if "cat_df" not in st.session_state: st.session_state.cat_df = None
if "market_data" not in st.session_state: st.session_state.market_data = None

# ---------------------------------------------------------
# STEP 1: PROGRAMMATIC CASHFLOW ENGINE
# ---------------------------------------------------------
st.header("Step 1: Cashflow Engine")
c1, c2 = st.columns([1, 2])

with c1:
    uploaded_file = st.file_uploader("Upload Bank Statement (CSV)", type=["csv"])
    if uploaded_file and st.session_state.raw_df is None:
        try:
            df = pd.read_csv(uploaded_file)
            clean_df = clean_bank_data(df)
            cat_df = categorize_transactions(clean_df)
            st.session_state.cat_df = cat_df
            st.session_state.raw_df = True
            st.rerun()
        except Exception as e:
            st.error(f"Error processing CSV: {e}")

if st.session_state.cat_df is not None:
    # 1B. Data Editor for Uncategorized
    st.subheader("1B. Categorization & Tagging")
    st.write("Tag any 'Uncategorized' transactions. Edits are processed automatically.")
    edited_df = st.data_editor(st.session_state.cat_df, use_container_width=True)
    
    # 1C & 1D. Quality of Spend & Baseline Burn
    flow_metrics = spending_quality_analysis(edited_df)
    
    st.subheader("1C. Quality of Spending")
    c3, c4 = st.columns([1, 1])
    with c3:
        st.markdown(metric_card("Total Inflows", format_inr(flow_metrics["total_inflow"])), unsafe_allow_html=True)
        st.markdown(metric_card("Total Outflows", format_inr(flow_metrics["total_outflow"])), unsafe_allow_html=True)
        st.info(flow_metrics["ratio_text"])
    with c4:
        st.plotly_chart(plot_needs_wants_pie(flow_metrics["needs_pct"], flow_metrics["wants_pct"]), use_container_width=True)
        
    st.subheader("1D. Surplus Calculator")
    total_balance = st.number_input("Current Total Bank Balance (₹)", min_value=0.0, value=500000.0, step=10000.0)
    baseline_burn = flow_metrics["baseline_burn"]
    safe_surplus = max(0, total_balance - baseline_burn)
    
    c5, c6, c7 = st.columns(3)
    c5.markdown(metric_card("Total Balance", format_inr(total_balance)), unsafe_allow_html=True)
    c6.markdown(metric_card("Baseline Burn (Next Month)", format_inr(baseline_burn), border_color="#FF6B6B"), unsafe_allow_html=True)
    c7.markdown(metric_card("Safe Surplus", format_inr(safe_surplus), border_color="#00FF88"), unsafe_allow_html=True)
    
    st.subheader("1E. Allocation Splitter")
    allocation_pct = st.slider("How much of this surplus will you allocate to investments?", 0, 100, 20)
    investable_capital = safe_surplus * (allocation_pct / 100.0)
    st.success(f"Investable Capital: {format_inr(investable_capital)}")
    idle_surplus = safe_surplus - investable_capital
    
    st.markdown("<hr>", unsafe_allow_html=True)
    
    # ---------------------------------------------------------
    # STEP 2: THE QUANT ENGINE
    # ---------------------------------------------------------
    st.header("Step 2: Deep Quant Engine")
    
    st.subheader("2A. Goal Definition")
    c8, c9 = st.columns(2)
    target_profit_pct = c8.number_input("Target Profit Goal (%)", min_value=1.0, value=15.0, step=1.0)
    time_horizon_months = c9.slider("Time Horizon (Months)", min_value=1, max_value=60, value=24)
    
    if st.button("Run Quant Engine & Fetch High-Freq Data"):
        with st.spinner("Fetching 2-Year 1H Data and Running Optimizations..."):
            market_data = fetch_1h_market_data()
            if market_data is not None and not market_data.empty:
                st.session_state.market_data = market_data
            else:
                st.error("Failed to fetch market data or data was empty. Please try again.")
            
    if st.session_state.market_data is not None and not st.session_state.market_data.empty:
        market_data = st.session_state.market_data
        
        st.subheader("2C. Asset vs FD Benchmark (2 Years)")
        benchmark_results = compare_historical_returns(market_data)
        st.plotly_chart(plot_asset_comparison(benchmark_results), use_container_width=True)
        
        st.subheader("2D-1. 1-Month Asset Profiling")
        df_1month = market_data.iloc[-187:] # approx 30 trading days of 1h
        profiles = analyze_asset_behavior(df_1month)
        st.dataframe(pd.DataFrame(profiles).T)
        
        st.subheader("2D-2. Precious Metals Statistical Arbitrage")
        stat_arb = metals_stat_arb(market_data)
        if stat_arb:
            st.plotly_chart(plot_stat_arb_oscillator(stat_arb), use_container_width=True)
            if "Buy Silver" in stat_arb["signal"]:
                st.markdown(alert_banner(stat_arb["signal"], "info"), unsafe_allow_html=True)
            elif "Buy Gold" in stat_arb["signal"]:
                st.markdown(alert_banner(stat_arb["signal"], "warning"), unsafe_allow_html=True)
            else:
                st.info("Stat Arb Signal: Neutral")
                
        st.subheader("2D-3. Denoised Optimizer Allocation")
        portfolio = optimize_portfolio(market_data)
        if portfolio:
            c10, c11 = st.columns([1, 1])
            with c10:
                st.markdown(metric_card("Expected CAGR", f"{portfolio['expected_cagr']*100:.1f}%"), unsafe_allow_html=True)
                st.markdown(metric_card("Expected Volatility", f"{portfolio['expected_volatility']*100:.1f}%"), unsafe_allow_html=True)
                st.markdown(metric_card("Sharpe Ratio", f"{portfolio['sharpe_ratio']:.2f}"), unsafe_allow_html=True)
            with c11:
                st.plotly_chart(plot_portfolio_donut(portfolio["weights"]), use_container_width=True)
                
            if portfolio["expected_cagr"] * 100 < target_profit_pct:
                st.markdown(alert_banner(f"Warning: To hit your aggressive target of {target_profit_pct}% in {time_horizon_months} months, you must take on risk outside the optimal Sharpe boundaries. Consider extending your horizon.", "error"), unsafe_allow_html=True)
                
            st.markdown("<hr>", unsafe_allow_html=True)
            
            # ---------------------------------------------------------
            # STEP 3: FORWARD SIMULATOR & RESOLUTION ENGINE
            # ---------------------------------------------------------
            st.header("Step 3: Forward Simulator & Resolution")
            
            target_capital = investable_capital * (1 + (target_profit_pct / 100.0))
            st.write(f"**Target Capital:** {format_inr(target_capital)}")
            
            with st.spinner("Running 10,000 GBM Jump-Diffusion Paths..."):
                mc_results = run_monte_carlo_simulation(
                    investable_capital, 
                    portfolio["expected_cagr"], 
                    portfolio["expected_volatility"], 
                    time_horizon_months
                )
                
                prob_success = np.sum(mc_results["final_values"] >= target_capital) / 10000.0
                
                st.plotly_chart(plot_monte_carlo_fan(mc_results, target_capital, time_horizon_months), use_container_width=True)
                
                if prob_success >= 0.8:
                    st.markdown(alert_banner(f"Plan is Safe! Probability of success: {prob_success*100:.1f}%", "success"), unsafe_allow_html=True)
                else:
                    st.markdown(alert_banner(f"Plan is Unsafe! Probability of success: {prob_success*100:.1f}%", "error"), unsafe_allow_html=True)
                    
                    resolution = calculate_resolution(
                        prob_success, investable_capital, idle_surplus, 
                        portfolio["expected_cagr"], portfolio["expected_volatility"], 
                        time_horizon_months, target_capital
                    )
                    
                    if resolution:
                        st.markdown(alert_banner(f"**Resolution Engine ({resolution['type']}):** {resolution['message']}", "warning"), unsafe_allow_html=True)
                        
            st.subheader("3E. Final Execution Summary")
            alloc_data = [{"Asset": k, "Weight (%)": v*100, "Allocation (₹)": v * investable_capital} for k, v in portfolio["weights"].items() if v > 0.01]
            st.table(pd.DataFrame(alloc_data))
            
            st.markdown(f"**Total Deployed Capital:** {format_inr(investable_capital)}")
            st.markdown(f"**Target Horizon:** {time_horizon_months} months")
