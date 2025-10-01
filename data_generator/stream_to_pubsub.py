import json
import requests
from google.cloud import pubsub_v1
from typing import Dict, Any

# Configuration
API_URL = "http://localhost:5000/generate_data"  # Update to your Flask API URL
PROJECT_ID = "your-project-id"  # Replace with your GCP project ID
TOPIC_ID = "banking-raw-data-topic"  # Matches Terraform below
BATCH_SIZE = 100  # Number of messages to process before waiting for completion

def call_api_generate_data(num_customers: int = 1000, transactions_per_account: int = 50) -> Dict[str, Any]:
    """Call the Flask API to generate banking data."""
    payload = {
        "num_customers": num_customers,
        "transactions_per_account": transactions_per_account
    }
    response = requests.post(API_URL, json=payload)
    response.raise_for_status()
    data = response.json()
    if not data.get("success"):
        raise ValueError(f"API error: {data.get('message')}")
    return data["data"]

def publish_to_pubsub(data: Dict[str, Any]):
    """Publish records from generated data to Pub/Sub topic."""
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(PROJECT_ID, TOPIC_ID)
    
    # Prepare records with table identifier
    records = []
    for table_name, table_data in data.items():
        for record in table_data:
            records.append({
                "table": table_name,
                "record": record
            })
    
    # Publish messages in batches
    futures = []
    for i, record in enumerate(records):
        message_data = json.dumps(record).encode("utf-8")  # Convert to bytestring
        try:
            future = publisher.publish(topic_path, data=message_data)
            futures.append(future)
            if len(futures) >= BATCH_SIZE or i == len(records) - 1:
                # Wait for all futures in the current batch to complete
                for f in futures:
                    try:
                        message_id = f.result()  # Block until published
                        print(f"Published message ID: {message_id}")
                    except Exception as e:
                        print(f"Error publishing message: {e}")
                futures = []  # Reset for next batch
        except Exception as e:
            print(f"Error preparing message {i + 1}: {e}")
    
    # Ensure all remaining futures are resolved
    for f in futures:
        try:
            message_id = f.result()
            print(f"Published message ID: {message_id}")
        except Exception as e:
            print(f"Error publishing message: {e}")

    print(f"Published {len(records)} messages to {topic_path}")

if __name__ == "__main__":
    # Generate and stream data
    try:
        generated_data = call_api_generate_data(num_customers=1000, transactions_per_account=50)
        publish_to_pubsub(generated_data)
        print("Data streaming to Pub/Sub complete.")
    except Exception as e:
        print(f"Error in streaming process: {e}")