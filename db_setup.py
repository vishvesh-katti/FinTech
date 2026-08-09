from config import supabase_client
import sys

def setup_database():
    print("=== RetailQuant Database Setup ===")
    print("Please run the following SQL in your Supabase SQL Editor:\n")
    
    users_table_sql = """
    CREATE TABLE IF NOT EXISTS users (
        id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
        name TEXT NOT NULL,
        target_goal_amount NUMERIC(15, 2) NOT NULL DEFAULT 0,
        target_timeframe_years INTEGER NOT NULL DEFAULT 5,
        created_at TIMESTAMPTZ DEFAULT NOW()
    );
    """
    
    transactions_table_sql = """
    CREATE TABLE IF NOT EXISTS transactions (
        id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
        user_id UUID REFERENCES users(id),
        date DATE NOT NULL,
        raw_description TEXT NOT NULL,
        amount NUMERIC(15, 2) NOT NULL,
        is_outflow BOOLEAN NOT NULL DEFAULT TRUE,
        category TEXT,
        is_fixed_obligation BOOLEAN NOT NULL DEFAULT FALSE,
        clean_name TEXT,
        created_at TIMESTAMPTZ DEFAULT NOW()
    );
    """
    
    print("--- SQL FOR 'users' TABLE ---")
    print(users_table_sql.strip())
    print("\n--- SQL FOR 'transactions' TABLE ---")
    print(transactions_table_sql.strip())
    print("\nAfter running the SQL, your database is ready.")
    
    try:
        # Attempt a test connection
        response = supabase_client.table("users").select("*").limit(1).execute()
        print("\n✓ Supabase connection verified successfully.")
    except Exception as e:
        print(f"\nFailed to connect to Supabase or query the 'users' table.")
        print(f"Error details: {str(e)}")
        print("Please ensure your .env keys are correct and you have created the tables.")

if __name__ == "__main__":
    setup_database()
