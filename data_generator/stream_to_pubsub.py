import json
from typing import Dict, Any
from google.cloud import pubsub_v1

# Config - update your project and topic
PROJECT_ID = "brave-reason-421203"
TOPIC_ID = "banking-raw-data-topic"
BATCH_SIZE = 10

# Load your BQ schema from schema.json
with open("schema.json") as f:
    BQ_SCHEMA = json.load(f)

# Map BQ types to AVRO union type keys
BQ_TO_AVRO_TYPE = {
    "INTEGER": "long",
    "FLOAT": "double",
    "STRING": "string",
    "DATE": "string",       # Dates as ISO string
    "TIMESTAMP": "string",  # Timestamp as ISO string
}

def wrap_union_fields(record: dict) -> dict:
    """
    Wrap fields to match AVRO union type format required by Pub/Sub schema validation.
    Fields that are None remain None, others wrapped as { avro_type: value }
    """
    wrapped = {}
    # Get the 'record' fields definition from the schema
    record_fields = next(field for field in BQ_SCHEMA if field["name"] == "record")["fields"]

    for field_def in record_fields:
        field_name = field_def["name"]
        bq_type = field_def["type"]

        avro_type = BQ_TO_AVRO_TYPE.get(bq_type)
        value = record.get(field_name)

        if value is None:
            wrapped[field_name] = None
        else:
            # Wrap value as required for AVRO union
            wrapped[field_name] = {avro_type: value}

    return wrapped

def publish_to_pubsub(data: Dict[str, Any]):
    """
    Publishes data to Pub/Sub topic with correct schema validation wrapping.
    `data` should be dict where key=table name, value=list of records.
    """
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(PROJECT_ID, TOPIC_ID)

    futures = []

    for table_name, records in data.items():
        for record in records:
            try:
                wrapped_record = wrap_union_fields(record)
                message = {
                    "data": json.dumps(record),  # raw JSON string for "data" field
                    "table": table_name,
                    "record": wrapped_record  # matches the 'record' field in schema
                }

                message_data = json.dumps(message).encode("utf-8")

                future = publisher.publish(topic_path, data=message_data)
                futures.append(future)

                if len(futures) >= BATCH_SIZE:
                    for f in futures:
                        try:
                            print("Published message ID:", f.result())
                        except Exception as e:
                            print("Error publishing message:", e)
                    futures = []

            except Exception as e:
                print(f"Error preparing message: {e}")

    # Publish remaining messages
    for f in futures:
        try:
            print("Published message ID:", f.result())
        except Exception as e:
            print("Error publishing message:", e)

if __name__ == "__main__":
    # Example input data (replace with your actual data)
    input_data = {
        "customers": [
            {
                "customer_id": 123,
                "name": "John Doe",
                "address": "123 Elm St",
                "email": "john.doe@example.com",
                "phone": "555-1234",
                "date_joined": "2022-01-15",
                "account_id": 456,
                "account_number": "ACC123456",
                "account_type": "Checking",
                "balance": 1500.50,
                "open_date": "2021-12-01",
                "status": "Active",
                "transaction_id": 789,
                "transaction_date": "2023-09-01T12:00:00Z",
                "transaction_type": "Deposit",
                "amount": 500.0,
                "description": "Monthly deposit",
                "category": "Salary",
                "balance_after": 2000.50,
                "loan_id": None,
                "loan_type": None,
                "principal": None,
                "interest_rate": None,
                "term_months": None,
                "issue_date": None,
            }
        ]
    }

    publish_to_pubsub(input_data)
