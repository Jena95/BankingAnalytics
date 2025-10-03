import json
import requests
from google.cloud import pubsub_v1
import os

# Set your environment variables or hardcode them here for testing
GCP_PROJECT_ID = os.getenv('GCP_PROJECT_ID', 'your-project-id')
PUBSUB_TOPIC_ID = os.getenv('PUBSUB_TOPIC_ID', 'banking-raw-topic')
API_URL = os.getenv('API_URL', 'http://localhost:5000/generate_data')

# Pub/Sub Publisher client
publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(GCP_PROJECT_ID, PUBSUB_TOPIC_ID)

def fetch_banking_data(num_customers=100, transactions_per_account=10):
    response = requests.post(API_URL, json={
        'num_customers': num_customers,
        'transactions_per_account': transactions_per_account
    })
    response.raise_for_status()
    return response.json()['data']  # Contains customers, accounts, transactions, loans

def stream_to_pubsub(data):
    for table_name, records in data.items():
        for record in records:
            record['record_type'] = table_name  # Add metadata to route in BigQuery
            payload = json.dumps(record).encode('utf-8')
            future = publisher.publish(topic_path, data=payload)
            future.result()  # Wait for publish confirmation (can be async for performance)

    print("Data streamed successfully to Pub/Sub.")

if __name__ == "__main__":
    print("Fetching and streaming data to Pub/Sub...")
    data = fetch_banking_data(num_customers=100, transactions_per_account=10)
    stream_to_pubsub(data)
