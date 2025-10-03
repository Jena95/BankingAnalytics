import json
import sys
from google.cloud import pubsub_v1

def main(project_id, topic_id):
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(project_id, topic_id)

    message = {
        "transaction_id": "txn123",
        "account_id": "acc456",
        "transaction_type": "debit",
        "amount": 250.75,
        "timestamp": "2025-10-03T15:34:00Z",
        "merchant": "Amazon"
    }

    # Serialize the message to a JSON string (this is correct)
    data = json.dumps(message).encode("utf-8")

    # Publish as a byte string (Pub/Sub will decode and validate against schema)
    future = publisher.publish(topic_path, data=data)
    print(f"Published message ID: {future.result()}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python publish_message.py <project_id> <topic_id>")
        sys.exit(1)

    main(sys.argv[1], sys.argv[2])
