import requests
import json
import argparse
from google.cloud import pubsub_v1

TOPIC_ID = "banking-raw-data"

def run_manual_ingest(project_id, api_url, num_customers=10, transactions_per_account=5):
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(project_id, TOPIC_ID)

    print(f"Calling API: {api_url} with num_customers={num_customers}, transactions_per_account={transactions_per_account}")
    response = requests.post(api_url, json={
        "num_customers": num_customers,
        "transactions_per_account": transactions_per_account
    })
    response.raise_for_status()
    data = response.json()

    customers = data.get("data", {}).get("customers", [])
    print(f"Publishing {len(customers)} customers to Pub/Sub topic {topic_path}")

    for customer in customers:
        msg = json.dumps(customer).encode("utf-8")
        publisher.publish(topic_path, msg)
    print("Publish complete.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Manual data ingestion script")
    parser.add_argument("--project_id", type=str, required=True, help="GCP Project ID")
    parser.add_argument("--api_url", type=str, default="http://localhost:5000/generate_data", help="Data generator API URL")
    parser.add_argument("--num_customers", type=int, default=10, help="Number of customers to generate")
    parser.add_argument("--transactions_per_account", type=int, default=5, help="Transactions per account")

    args = parser.parse_args()

    run_manual_ingest(args.project_id, args.api_url, args.num_customers, args.transactions_per_account)
