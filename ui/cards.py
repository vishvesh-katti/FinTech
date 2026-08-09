def metric_card(title, value, subtitle="", border_color="#1E2A3A"):
    """Returns HTML for a glassmorphism metric card."""
    return f"""
    <div style="
        background: rgba(30, 42, 58, 0.7);
        backdrop-filter: blur(10px);
        border: 1px solid {border_color};
        border-radius: 8px;
        padding: 20px;
        margin-bottom: 15px;
        color: #fff;
    ">
        <h4 style="margin:0; font-size:14px; color:#8899AA; font-weight:normal;">{title}</h4>
        <h2 style="margin:10px 0 5px 0; font-size:28px; font-family: 'JetBrains Mono', monospace;">{value}</h2>
        <p style="margin:0; font-size:12px; color:#aaa;">{subtitle}</p>
    </div>
    """

def alert_banner(message, alert_type="info"):
    colors = {
        "error": "#FF6B6B",
        "warning": "#FFD700",
        "success": "#00FF88",
        "info": "#00D4FF"
    }
    color = colors.get(alert_type, colors["info"])
    return f"""
    <div style="
        background: rgba(30, 42, 58, 0.5);
        border-left: 4px solid {color};
        padding: 15px;
        margin-bottom: 20px;
        border-radius: 4px;
        color: #fff;
    ">
        {message}
    </div>
    """
