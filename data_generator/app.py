import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import string
from flask import Flask, request, jsonify

# Seed for reproducibility
np.random.seed(42)
random.seed(42)

app = Flask(__name__)

# --- Helper Functions ---

def generate_random_name():
    first_names = ['John', 'Jane', 'Alice', 'Bob', 'Charlie', 'Diana', 'Eve', 'Frank', 'Grace', 'Henry',
                   'Ivy', 'Jack', 'Kara', 'Leo', 'Mia', 'Noah', 'Olivia', 'Paul', 'Quinn', 'Riley']
    last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Rodriguez', 'Martinez',
                  'Hernandez', 'Lopez', 'Gonzalez', 'Wilson', 'Anderson', 'Thomas', 'Taylor', 'Moore', 'Jackson', 'Martin']
    return f"{random.choice(first_names)} {random.choice(last_names)}"

def generate_random_address():
    streets = ['Main St', 'Oak Ave', 'Pine Rd', 'Elm St', 'Maple Dr', 'Cedar Ln', 'Birch Blvd', 'Willow Way']
    cities = ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix', 'Philadelphia', 'San Antonio', 'San Diego']
    states = ['NY', 'CA', 'IL','TX', 'AZ', 'PA', 'TX', 'CA']
    zip_codes = [random.randint(10000, 99999) for _ in range(8)]
    street_num = random.randint(100, 9999)
    city_idx = random.randint(0, 7)
    return f"{street_num} {random.choice(streets)}, {cities[city_idx]}, {states[city_idx]} {zip_codes[city_idx]}"

def generate_account_number():
    return ''.join(random.choices(string.digits, k=10))

# --- Data Generation Functions ---

def generate_customers(num_customers):
    customers = []
    for i in range(1, num_customers + 1):
        customer = {
            'customer_id': i,
            'name': generate_random_name(),
            'address': generate_random_address(),
            'email': f"{''.join(random.choices(string.ascii_lowercase, k=5))}@example.com",
            'phone': f"({random.randint(100,999)}) {random.randint(100,999)}-{random.randint(1000,9999)}",
            'date_joined': (datetime.now() - timedelta(days=random.randint(365*5, 365*20))).strftime('%Y-%m-%d')
        }
        customers.append(customer)
    return pd.DataFrame(customers)

def generate_accounts(customers_df):
    accounts = []
    for _, customer in customers_df.iterrows():
        for _ in range(random.randint(1, 3)):
            account_type = random.choice(['Checking', 'Savings', 'Credit'])
            initial_balance = round(np.random.normal(5000, 3000), 2) if account_type != 'Credit' else 0
            if initial_balance < 0:
                initial_balance = 0
            account = {
                'account_id': len(accounts) + 1,
                'customer_id': customer['customer_id'],
                'account_number': generate_account_number(),
                'account_type': account_type,
                'balance': initial_balance,
                'open_date': (datetime.now() - timedelta(days=random.randint(365, 365*10))).strftime('%Y-%m-%d'),
                'status': random.choice(['Active', 'Active', 'Active', 'Dormant'])
            }
            accounts.append(account)
    return pd.DataFrame(accounts)

def generate_transactions(accounts_df, num_transactions_per_account=100):
    transactions = []
    categories = ['Salary Deposit', 'Grocery', 'Rent', 'Utility', 'Transfer', 'ATM Withdrawal', 'Online Purchase', 'Bill Payment']
    transaction_types = ['Deposit', 'Withdrawal', 'Transfer']

    for _, account in accounts_df.iterrows():
        start_date = datetime.strptime(account['open_date'], '%Y-%m-%d')
        end_date = datetime.now()

        for _ in range(num_transactions_per_account):
            days_diff = (end_date - start_date).days
            transaction_date = start_date + timedelta(days=random.randint(0, days_diff))

            if account['account_type'] == 'Credit':
                amount = round(random.uniform(10, 500), 2)
                trans_type = random.choice(['Purchase', 'Payment'])
                amount = -amount if trans_type == 'Purchase' else abs(amount)
            else:
                amount = round(random.uniform(-200, 1000), 2)
                trans_type = 'Deposit' if amount > 0 else 'Withdrawal'
                if amount == 0:
                    trans_type = random.choice(transaction_types)
                    amount = round(random.uniform(10, 100), 2)

            category = random.choice(categories)
            description = f"{category} - {''.join(random.choices(string.ascii_letters, k=5))}"

            transaction = {
                'transaction_id': len(transactions) + 1,
                'account_id': account['account_id'],
                'transaction_date': transaction_date.strftime('%Y-%m-%d %H:%M:%S'),
                'transaction_type': trans_type,
                'amount': amount,
                'description': description,
                'category': category,
                'balance_after': account['balance'] + random.uniform(-1000, 1000)
            }
            transactions.append(transaction)

    transactions_df = pd.DataFrame(transactions)
    transactions_df['transaction_date'] = pd.to_datetime(transactions_df['transaction_date'])
    transactions_df = transactions_df.sort_values('transaction_date').reset_index(drop=True)
    return transactions_df

def generate_loans(customers_df, loan_probability=0.1):
    loans = []
    for _, customer in customers_df.iterrows():
        if random.random() < loan_probability:
            loan = {
                'loan_id': len(loans) + 1,
                'customer_id': customer['customer_id'],
                'loan_type': random.choice(['Personal', 'Mortgage', 'Auto']),
                'principal': round(np.random.uniform(5000, 200000), 2),
                'interest_rate': round(random.uniform(3.0, 15.0), 2),
                'term_months': random.choice([12, 24, 36, 60, 120, 360]),
                'issue_date': (datetime.now() - timedelta(days=random.randint(365, 365*5))).strftime('%Y-%m-%d'),
                'status': random.choice(['Active', 'Active', 'Paid Off', 'Defaulted'])
            }
            loans.append(loan)
    return pd.DataFrame(loans)

def generate_banking_data(num_customers=10000, transactions_per_account=50):
    customers = generate_customers(num_customers)
    accounts = generate_accounts(customers)
    transactions = generate_transactions(accounts, transactions_per_account)
    loans = generate_loans(customers)
    return {
        'customers': customers,
        'accounts': accounts,
        'transactions': transactions,
        'loans': loans
    }

# --- Flask API Endpoints ---

@app.route('/generate_data', methods=['POST'])
def api_generate_data():
    data = request.get_json() or {}
    num_customers = data.get('num_customers', 1000)
    transactions_per_account = data.get('transactions_per_account', 50)

    try:
        generated = generate_banking_data(num_customers, transactions_per_account)

        response = {
            'success': True,
            'message': 'Data generated successfully',
            'customers_count': len(generated['customers']),
            'accounts_count': len(generated['accounts']),
            'transactions_count': len(generated['transactions']),
            'loans_count': len(generated['loans']),
            'data': {
                'customers': generated['customers'].to_dict(orient='records'),
                'accounts': generated['accounts'].to_dict(orient='records'),
                'transactions': generated['transactions'].to_dict(orient='records'),
                'loans': generated['loans'].to_dict(orient='records'),
            }
        }

        return jsonify(response)

    except Exception as e:
        return jsonify({ 
            'success': False,
            'message': str(e)
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'})

# --- Run App ---

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
