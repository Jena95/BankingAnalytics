import json
import requests
from google.cloud import pubsub_v1
from typing import Dict, Any

# Configuration
API_URL = "http://localhost:5000/generate_data"  # Update if needed
PROJECT_ID = "brave-reason-421203"
TOPIC_ID = "banking-raw-data-topic"
BATCH_SIZE = 100

# === HELPER FUNCTIONS ===

def wrap_union_fields(record: dict) -> dict:
    """
    Wrap each field value in AVRO union format, e.g., {"long": 123}, {"string": "abc"}.
    """
    wrapped = {}
    for key, value in record.items():
        if value is None:
            wrapped[key] = None
        elif isinstance(value, int):
            wrapped[key] = {"long": value}
        elif isinstance(value, float):
            wrapped[key] = {"double": value}
        elif isinstance(value, str):
            wrapped[key] = {"string": value}
        else:
            # Leave nested or unexpected types as-is
            wrapped[key] = value
    return wrapped

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
    """Publish messages to Pub/Sub, conforming to AVRO JSON encoding rules."""
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(PROJECT_ID, TOPIC_ID)
    
    records = []
    for table_name, table_data in data.items():
        for record in table_data:
            wrapped_record = wrap_union_fields(record)

            # Construct the AVRO-compatible message
            message = {
                "data": json.dumps(record),  # raw data as string
                "table": table_name,
                "record": {
                    "Record": wrapped_record  # must match AVRO record wrapping
                }
            }
            records.append(message)

    futures = []
    for i, record in enumerate(records):
        try:
            message_data = json.dumps(record).encode("utf-8")
            future = publisher.publish(topic_path, data=message_data)
            futures.append(future)

            # Wait for a batch to finish
            if len(futures) >= BATCH_SIZE or i == len(records) - 1:
                for f in futures:
                    try:
                        message_id = f.result()
                        print(f"Published message ID: {message_id}")
                    except Exception as e:
                        print(f"Error publishing message: {e}")
                futures = []
        except Exception as e:
            print(f"Error preparing message {i + 1}: {e}")

    print(f"✅ Published {len(records)} messages to {topic_path}")

# === MAIN ===
if __name__ == "__main__":
    try:
        print("🚀 Generating data from API...")
        generated_data = call_api_generate_data(num_customers=1000, transactions_per_account=50)
        print("📤 Publishing to Pub/Sub...")
        publish_to_pubsub(generated_data)
        print("✅ Data streaming to Pub/Sub complete.")
    except Exception as e:
        print(f"❌ Error in streaming process: {e}")
