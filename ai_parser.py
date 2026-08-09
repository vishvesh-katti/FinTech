import json
import anthropic
from config import ANTHROPIC_API_KEY
import pandas as pd

# Initialize Anthropic client
client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

def parse_single_transaction(raw_description):
    system_prompt = """You are a financial transaction categorizer for Indian bank statements.
You will receive a raw bank transaction narration string.
You must respond ONLY with a valid JSON object and nothing else.
No preamble, no explanation, no markdown, no code blocks.
Just the raw JSON object.
The JSON must have exactly these three fields:
- clean_name: A human-readable merchant or payee name (e.g., 'Zomato', 'HDFC Home Loan', 'Spotify')
- category: One of these exact values only: Food, Groceries, Transport, Shopping, Entertainment, Utilities, Rent, Loan EMI, Salary, Investment, Other
- is_fixed_obligation: A boolean (true or false). Set to true ONLY for Rent, Loan EMI, and Subscription payments that recur every month. Set to false for variable spending like Food, Shopping, Transport."""

    user_prompt = f"Categorize this Indian bank transaction: {raw_description}"
    
    safe_default = {
        "clean_name": raw_description,
        "category": "Other",
        "is_fixed_obligation": False
    }

    try:
        response = client.messages.create(
            model="claude-3-5-haiku-20241022",
            system=system_prompt,
            messages=[
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=150,
            temperature=0
        )
        
        content = response.content[0].text.strip()
        parsed = json.loads(content)
        
        # Validate keys
        if "clean_name" in parsed and "category" in parsed and "is_fixed_obligation" in parsed:
            return parsed
        else:
            return safe_default
            
    except Exception as e:
        print(f"Warning: Failed to parse transaction '{raw_description}'. Error: {str(e)}")
        return safe_default

def parse_all_transactions(df):
    clean_names = []
    categories = []
    is_fixed_obligations = []
    
    total = len(df)
    for i, row in df.iterrows():
        result = parse_single_transaction(row["raw_description"])
        clean_names.append(result["clean_name"])
        categories.append(result["category"])
        is_fixed_obligations.append(result["is_fixed_obligation"])
        
        if (i + 1) % 10 == 0:
            print(f"Parsed {i + 1}/{total} transactions...")
            
    df["clean_name"] = clean_names
    df["category"] = categories
    df["is_fixed_obligation"] = is_fixed_obligations
    
    return df
