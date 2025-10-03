import json
import sys
from google.cloud import pubsub_v1

def main(project_id, topic_id):
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(project_id, topic_id)

    data = {
        "transaction_id": "txn123",
        "account_id": "acc456",
        "transaction_type": "debit",
        "amount": 250.75,
        "timestamp": "2025-10-03T15:34:00Z",
        "merchant": "Amazon"
    }

    data_bytes = json.dumps(data).encode("utf-8")

    future = publisher.publish(topic_path, data=data_bytes)
    print(f"Published message ID: {future.result()}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python publish_message.py <project_id> <topic_id>")
        sys.exit(1)

    project_id_arg = sys.argv[1]
    topic_id_arg = sys.argv[2]
    main(project_id_arg, topic_id_arg)
