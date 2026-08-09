import plotly.graph_objects as go
import plotly.express as px
import numpy as np

# Institutional Dark Palette
BG_COLOR = "#0A0F1E"
GRID_COLOR = "#1E2A3A"
TEXT_COLOR = "#FFFFFF"
PRIMARY = "#00D4FF"
GOLD = "#FFD700"
CORAL = "#FF6B6B"
GREEN = "#00FF88"

def apply_dark_theme(fig):
    fig.update_layout(
        paper_bgcolor=BG_COLOR,
        plot_bgcolor=BG_COLOR,
        font=dict(color=TEXT_COLOR, family="Inter, sans-serif"),
        margin=dict(l=40, r=40, t=40, b=40),
        xaxis=dict(showgrid=True, gridcolor=GRID_COLOR, zeroline=False),
        yaxis=dict(showgrid=True, gridcolor=GRID_COLOR, zeroline=False),
    )
    return fig

def plot_needs_wants_pie(needs_pct, wants_pct):
    fig = go.Figure(data=[go.Pie(
        labels=["Essentials (Needs)", "Discretionary (Wants)"],
        values=[needs_pct, wants_pct],
        hole=.5,
        marker_colors=[PRIMARY, CORAL]
    )])
    fig.update_layout(title_text="Quality of Spending")
    return apply_dark_theme(fig)

def plot_asset_comparison(returns_dict):
    assets = list(returns_dict.keys())
    returns = [v * 100 for v in returns_dict.values()]
    
    colors = [GOLD if "Synthetic" in a else PRIMARY for a in assets]
    
    fig = go.Figure(data=[go.Bar(
        x=assets, y=returns, marker_color=colors
    )])
    
    # Add horizontal line for FD benchmark
    fd_ret = returns_dict.get("Synthetic Bank FD", 0) * 100
    fig.add_hline(y=fd_ret, line_dash="dash", line_color=GOLD, annotation_text="FD Benchmark")
    
    fig.update_layout(title="2-Year Cumulative Return Comparison (%)")
    return apply_dark_theme(fig)

def plot_stat_arb_oscillator(stat_arb_data):
    z_score = stat_arb_data["z_score"]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=z_score.index, y=z_score.values, mode='lines', name='Z-Score', line=dict(color=PRIMARY)))
    
    fig.add_hline(y=2.0, line_dash="dash", line_color=CORAL, annotation_text="+2 Std Dev (Sell Gold/Buy Silver)")
    fig.add_hline(y=-2.0, line_dash="dash", line_color=GREEN, annotation_text="-2 Std Dev (Buy Gold/Sell Silver)")
    
    fig.update_layout(title="Gold/Silver Stat Arb Oscillator (30-Day Rolling)")
    return apply_dark_theme(fig)

def plot_portfolio_donut(allocation_dict):
    labels = list(allocation_dict.keys())
    values = list(allocation_dict.values())
    
    fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.5, marker_colors=[PRIMARY, GOLD, CORAL, GREEN, "#8899AA", "#FFFFFF", "#1E2A3A"])])
    fig.update_layout(title_text="Optimized Portfolio Distribution")
    return apply_dark_theme(fig)

def plot_monte_carlo_fan(mc_results, target_capital, time_horizon_months):
    months = np.arange(0, time_horizon_months + 1)
    
    p10 = mc_results["p10_path"]
    p50 = mc_results["p50_path"]
    p90 = mc_results["p90_path"]
    
    fig = go.Figure()
    
    # Upper Bound (90th)
    fig.add_trace(go.Scatter(
        x=months, y=p90,
        mode='lines',
        line=dict(width=0),
        showlegend=False
    ))
    
    # Lower Bound (10th) with fill to upper
    fig.add_trace(go.Scatter(
        x=months, y=p10,
        mode='lines',
        fill='tonexty',
        fillcolor='rgba(0, 212, 255, 0.2)',
        line=dict(width=0),
        name='10th - 90th Percentile Range'
    ))
    
    # Median
    fig.add_trace(go.Scatter(
        x=months, y=p50,
        mode='lines',
        name='Median Path',
        line=dict(color=PRIMARY, width=3)
    ))
    
    # Target Line
    fig.add_hline(y=target_capital, line_dash="dash", line_color=GOLD, annotation_text="Target Capital")
    
    fig.update_layout(title="Monte Carlo Stochastic Simulation (10,000 Paths)", xaxis_title="Months", yaxis_title="Portfolio Value (₹)")
    return apply_dark_theme(fig)
