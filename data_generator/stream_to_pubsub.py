import json
import requests
from google.cloud import pubsub_v1
from typing import Dict, Any

# Configuration
API_URL = "http://localhost:5000/generate_data"  # Update to your Flask API URL
PROJECT_ID = "brave-reason-421203"  # Replace with your GCP project ID
TOPIC_ID = "banking-raw-data-topic"  # Matches Terraform below
BATCH_SIZE = 100  # Pub/Sub batch size for efficiency

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
    
    # Publish in batches
    batch_messages = []
    for i, record in enumerate(records):
        message_data = json.dumps(record).encode("utf-8")
        batch_messages.append(
            pubsub_v1.types.PubsubMessage(data=message_data)
        )
        
        if len(batch_messages) == BATCH_SIZE or i == len(records) - 1:
            try:
                future = publisher.publish(topic_path, batch_messages)
                print(f"Published batch of {len(batch_messages)} messages. Message ID: {future.result()}")
            except Exception as e:
                print(f"Error publishing batch: {e}")
            batch_messages = []  # Reset batch
    
    publisher.close()

if __name__ == "__main__":
    # Generate and stream data
    generated_data = call_api_generate_data(num_customers=1000, transactions_per_account=50)
    publish_to_pubsub(generated_data)
    print("Data streaming to Pub/Sub complete.")