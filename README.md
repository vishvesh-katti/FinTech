# RetailQuant V3 - Deterministic Quant Engine

RetailQuant V3 is a comprehensive financial planning and quantitative analysis dashboard built with Streamlit. It automates personal cash flow analysis, categorizes spending using AI, optimizes portfolio allocations based on real market data, and simulates future growth probabilities to ensure financial goals are met.

## 🚀 Features & Workflow

The platform operates in three primary steps:

### Step 1: Programmatic Cashflow Engine
1. **Data Ingestion:** Upload your raw bank statement (CSV). The system cleans and normalizes the data.
2. **AI Categorization:** Powered by Anthropic's Claude (`claude-3-5-haiku`), transactions are automatically categorized (e.g., Food, Shopping, Rent) and flagged as fixed obligations or variable expenses.
3. **Quality of Spend:** Analyzes inflows vs. outflows and visualizes your Needs vs. Wants ratio.
4. **Surplus Calculation:** Automatically calculates your "Baseline Burn" and determines your **Safe Surplus** after accounting for an emergency fund and variable buffers.
5. **Allocation Splitter:** Decide what percentage of your safe surplus to deploy as investable capital.

### Step 2: The Deep Quant Engine
1. **Goal Definition:** Define your target profit percentage and time horizon (in months).
2. **Market Data Fetching:** Fetches live historical data for an asset universe including Indian Equities (NIFTY), Global Equities, Fixed Income, Commodities (Gold/Silver), and REITs via `yfinance`.
3. **Statistical Arbitrage:** Runs short-term stat-arb algorithms on precious metals (Gold/Silver) to generate tactical Buy/Sell signals.
4. **Denoised Optimization:** Allocates your capital across the asset universe to maximize the Sharpe Ratio, generating an Expected CAGR and Volatility profile.

### Step 3: Forward Simulator & Resolution
1. **Monte Carlo Simulation:** Runs 10,000 Geometric Brownian Motion (GBM) jump-diffusion paths based on your optimized portfolio's expected CAGR and volatility.
2. **Probability of Success:** Calculates the exact probability of hitting your financial goal.
3. **Resolution Engine:** If the probability of success is low (<80%), the engine intervenes to recommend actionable resolutions (e.g., extending the time horizon, increasing capital, or adjusting the target).
4. **Final Execution:** Provides the exact rupee amount to allocate to each asset.

---

## 🛠️ Tech Stack & Architecture

- **Frontend/UI:** [Streamlit](https://streamlit.io/) (`app.py`, `ui/`)
- **AI Integration:** Anthropic API (`ai_parser.py`)
- **Financial Calculations:** Pandas, NumPy (`calculators.py`)
- **Market Data:** `yfinance` (`market_routing.py`, `market/`)
- **Database (Optional/Phase 2):** Supabase (`db_setup.py`)

### Key Files
- `app.py`: The main entry point for the Streamlit dashboard.
- `config.py`: Contains API keys, UI formatting tools, and the Base Allocation grids.
- `ai_parser.py`: The prompt engineering and API logic for transaction categorization.
- `calculators.py`: Core logic for determining fixed vs. variable spending and dynamic surplus.
- `generate_transactions.py`: A robust mock data generator to simulate different user profiles (e.g., *accumulator*, *impulse buyer*, *debt juggler*) for stress testing.

---

## ⚙️ Setup & Installation

**1. Clone the repository**
```bash
git clone https://github.com/vishvesh-katti/FinTech.git
cd FinTech
```

**2. Install dependencies**
Make sure you have a `requirements.txt` with `streamlit`, `pandas`, `numpy`, `yfinance`, `python-dotenv`, and `anthropic` installed.
```bash
pip install -r requirements.txt
```

**3. Environment Variables**
Create a `.env` file in the root directory and add your Anthropic API Key:
```env
ANTHROPIC_API_KEY=your-api-key-here
```
*(Optionally add Supabase credentials if you plan to use `db_setup.py`)*

**4. Database Setup (Optional)**
If you wish to store users and transactions in Supabase, run the setup script to get the required SQL schema:
```bash
python db_setup.py
```

**5. Run the Application**
```bash
streamlit run app.py
```

---

## 🧪 Testing with Mock Data
Don't want to use real bank statements? You can generate realistic mock data to test the platform.
Run the synthetic data generator:
```bash
python generate_transactions.py
```
This will populate the `data/` folder with CSVs matching various financial personalities (e.g., `stress_accumulator.csv`, `stress_balancer.csv`) which you can upload into the app.
