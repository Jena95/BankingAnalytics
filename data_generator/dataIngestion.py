import requests
import json
from google.cloud import pubsub_v1

FLASK_API_URL = "http://localhost:5000/generate_data"
PUBSUB_TOPIC = "projects/YOUR_PROJECT_ID/topics/banking-raw-data"

NUM_CUSTOMERS = 100
TRANSACTIONS_PER_ACCOUNT = 10

def fetch_data():
    try:
        response = requests.post(
            FLASK_API_URL,
            json={
                "num_customers": NUM_CUSTOMERS,
                "transactions_per_account": TRANSACTIONS_PER_ACCOUNT
            }
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None

def publish_to_pubsub(data):
    publisher = pubsub_v1.PublisherClient()

    for data_type, records in data.items():
        for record in records:
            message_json = json.dumps({
                "type": data_type,
                "payload": record
            })
            message_bytes = message_json.encode("utf-8")
            future = publisher.publish(PUBSUB_TOPIC, message_bytes)
            future.result()

    print("Data published to Pub/Sub successfully.")

if __name__ == "__main__":
    api_response = fetch_data()
    if api_response and api_response.get("success"):
        data = api_response["data"]
        publish_to_pubsub(data)
    else:
        print("Failed to retrieve or publish data.")
