import argparse
import requests
import json
from google.cloud import pubsub_v1

def fetch_data(api_url, num_customers, transactions_per_account):
    try:
        response = requests.post(
            api_url,
            json={
                "num_customers": num_customers,
                "transactions_per_account": transactions_per_account
            }
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None

def publish_to_pubsub(data, topic_path, data_type_filter=None):
    publisher = pubsub_v1.PublisherClient()
    count = 0

    for data_type, records in data.items():
        if data_type_filter and data_type != data_type_filter:
            continue  # Skip other types

        for record in records:
            try:
                message_bytes = json.dumps({"data": record}).encode("utf-8")
                future = publisher.publish(topic_path, message_bytes)
                future.result(timeout=10)
                count += 1
            except Exception as e:
                print(f"Failed to publish {data_type} record: {e}")

    print(f"✅ Published {count} record(s) to Pub/Sub topic: {topic_path}")

def main():
    parser = argparse.ArgumentParser(description="Fetch synthetic banking data and publish to Google Pub/Sub.")

    parser.add_argument('--num_customers', type=int, default=100,
                        help='Number of customers to generate (default: 100)')

    parser.add_argument('--transactions_per_account', type=int, default=10,
                        help='Number of transactions per account (default: 10)')

    parser.add_argument('--api_url', type=str, default='http://localhost:5000/generate_data',
                        help='URL of the Flask API endpoint (default: http://localhost:5000/generate_data)')

    parser.add_argument('--project_id', type=str, required=True,
                        help='Google Cloud project ID')

    parser.add_argument('--topic_id', type=str, default='banking-raw-data',
                        help='Pub/Sub topic ID (default: banking-raw-data)')

    parser.add_argument('--data_type', type=str, choices=['customers', 'accounts', 'transactions', 'loans'],
                        required=True, help='Type of data to publish to the topic (required)')

    args = parser.parse_args()

    topic_path = f"projects/{args.project_id}/topics/{args.topic_id}"

    api_response = fetch_data(args.api_url, args.num_customers, args.transactions_per_account)

    if api_response and api_response.get("success"):
        data = api_response["data"]
        publish_to_pubsub(data, topic_path, args.data_type)
    else:
        print("❌ Failed to retrieve or publish data.")

if __name__ == "__main__":
    main()
