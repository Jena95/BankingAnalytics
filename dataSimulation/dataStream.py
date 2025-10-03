from google.cloud import pubsub_v1
import json
import sys

def main(project_id, topic_id):
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(project_id, topic_id)

    message_dict = {
        "transaction_id": "txn123",
        "account_id": "acc456",
        "transaction_type": "debit",
        "amount": 250.75,
        "timestamp": "2025-10-03T15:34:00Z",
        "merchant": "Amazon"
    }

    # ⚠️ DO NOT encode to JSON string here — send as a dict
    # Instead, use the json argument (requires newer google-cloud-pubsub library)
    future = publisher.publish(topic_path, json=message_dict)
    print(f"Published message ID: {future.result()}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python publish_message.py <project_id> <topic_id>")
        sys.exit(1)

    main(sys.argv[1], sys.argv[2])
