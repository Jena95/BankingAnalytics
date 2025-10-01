# BankingAnalytics
Data Engineering and Data Analytics on Simulated Bank Data

# Data Generator
pip install -r requirements.txt

# Test Data Generator in Local.

Run the API:

python app.py

Make a test request:

curl -X POST http://localhost:5000/generate_data \
     -H "Content-Type: application/json" \
     -d '{"num_customers": 100, "transactions_per_account": 10}'

# Ingest the data to pubsub

python dataIngestion.py --project_id=my-gcp-project --api_url=http://localhost:5000/generate_data --num_customers=20 --transactions_per_account=50
