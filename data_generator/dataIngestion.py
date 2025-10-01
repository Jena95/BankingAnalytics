import argparse
import requests
import json
import os
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

def publish_to_pubsub(data, topic_path):
    publisher = pubsub_v1.PublisherClient()

    for data_type, records in data.items():
        for record in records:
            message_json = json.dumps({
                "type": data_type,
                "payload": record
            })
            message_bytes = message_json.encode("utf-8")
            try:
                future = publisher.publish(topic_path, message_bytes)
                future.result(timeout=10)
            except Exception as e:
                print(f"Failed to publish message of type {data_type}: {e}")
    
    print("Data published to Pub/Sub successfully.")

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

    args = parser.parse_args()

    topic_path = f"projects/{args.project_id}/topics/{args.topic_id}"

    api_response = fetch_data(args.api_url, args.num_customers, args.transactions_per_account)
    
    if api_response and api_response.get("success"):
        data = api_response["data"]
        publish_to_pubsub(data, topic_path)
    else:
        print("Failed to retrieve or publish data.")

if __name__ == "__main__":
    main()
