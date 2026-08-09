import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")

if not ANTHROPIC_API_KEY:
    print("Warning: ANTHROPIC_API_KEY is missing from your .env file. AI Categorization will use fallback.")

def format_inr(amount: float) -> str:
    """Format amount in Indian numbering system."""
    if amount < 1_00_000:
        return f"₹{amount:,.0f}"
    elif amount < 1_00_00_000:
        return f"₹{amount/1_00_000:.1f} Lakhs"
    else:
        return f"₹{amount/1_00_00_000:.2f} Crore"

# Stage 5 Constants - Asset Universe (12 assets total)
ASSET_UNIVERSE = {
    # CLASS 1 — INDIAN EQUITY
    "indian_large_equity": "^NSEI",
    "indian_mid_equity": "NIFTYMIDCAP150.NS",
    "indian_emerging": "JUNIORBEES.NS",
    # CLASS 2 — GLOBAL EQUITY
    "global_equity": "CSPX.L", # Requires INR=X conversion
    "tech_equity": "MAFANG.NS",
    # CLASS 3 — DEBT & FIXED INCOME
    "fixed_income": "ABCBF.NS",
    "cash_equivalents": "LIQUIDBEES.NS",
    # CLASS 4 — COMMODITIES
    "gold": "GOLDBEES.NS",
    "silver": "SILVERBEES.NS",
    # CLASS 5 — REAL ESTATE
    "reit": "EMBASSY.NS",
    "reit_alt": "MINDSPACE.NS",
    # CLASS 6 — ALTERNATIVE
    "infra": "INFRABEES.NS"
}

# Base Allocation Grid (Mapped to 8 primary classes as per PRD)
BASE_ALLOCATION_GRID = {
    "Ultra-Conservative": {
        "indian_large_equity": 0.05, "indian_mid_equity": 0.00, "global_equity": 0.00,
        "fixed_income": 0.60, "gold": 0.20, "silver": 0.05, "reit": 0.00, "cash_equivalents": 0.10
    },
    "Conservative": {
        "indian_large_equity": 0.15, "indian_mid_equity": 0.05, "global_equity": 0.05,
        "fixed_income": 0.45, "gold": 0.15, "silver": 0.05, "reit": 0.05, "cash_equivalents": 0.05
    },
    "Moderate": {
        "indian_large_equity": 0.30, "indian_mid_equity": 0.10, "global_equity": 0.10,
        "fixed_income": 0.25, "gold": 0.10, "silver": 0.05, "reit": 0.05, "cash_equivalents": 0.05
    },
    "Growth": {
        "indian_large_equity": 0.45, "indian_mid_equity": 0.15, "global_equity": 0.10,
        "fixed_income": 0.10, "gold": 0.10, "silver": 0.05, "reit": 0.05, "cash_equivalents": 0.00
    },
    "Aggressive": {
        "indian_large_equity": 0.50, "indian_mid_equity": 0.20, "global_equity": 0.10,
        "fixed_income": 0.05, "gold": 0.05, "silver": 0.05, "reit": 0.05, "cash_equivalents": 0.00
    }
}
