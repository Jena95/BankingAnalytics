import json
import sys
import random
import uuid
from datetime import datetime, timezone

from google.cloud import pubsub_v1

# Predefined merchant names
MERCHANTS = ["Amazon", "Visa", "Razorpay", "SBI", "Google", "Netflix"]

# Transaction types
TRANSACTION_TYPES = ["debit", "credit"]

def get_current_utc_timestamp():
    return datetime.now(timezone.utc).isoformat()

def generate_transaction():
    return {
        "transaction_id": str(uuid.uuid4()),
        "account_id": f"acc{random.randint(1000, 9999)}",
        "transaction_type": random.choice(TRANSACTION_TYPES),
        "amount": round(random.uniform(10.0, 10000.0), 2),
        "timestamp": get_current_utc_timestamp(),
        "merchant": random.choice(MERCHANTS)
    }

def main(project_id, topic_id):
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(project_id, topic_id)

    for _ in range(10):  # Generate and publish 10 messages
        message = generate_transaction()
        data = json.dumps(message).encode("utf-8")
        future = publisher.publish(topic_path, data=data)
        print(f"Published message ID: {future.result()} | Data: {message}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python publish_message.py <project_id> <topic_id>")
        sys.exit(1)

    main(sys.argv[1], sys.argv[2])
