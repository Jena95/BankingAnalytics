provider "google" {
  project = var.project_id
  region  = var.region
}

resource "google_pubsub_topic" "banking_raw_data" {
  name = "banking-raw-data"
}

resource "google_bigquery_dataset" "raw_data" {
  dataset_id  = "raw_banking_data"
  location    = var.region
  description = "Dataset to store raw banking data ingested from Pub/Sub"
}

resource "google_bigquery_table" "customers" {
  dataset_id = google_bigquery_dataset.raw_data.dataset_id
  table_id   = "customers"
  schema     = file("schemas/customers.json")
  time_partitioning {
    type = "DAY"
  }
}

resource "google_bigquery_table" "accounts" {
  dataset_id = google_bigquery_dataset.raw_data.dataset_id
  table_id   = "accounts"
  schema     = file("schemas/accounts.json")
  time_partitioning {
    type = "DAY"
  }
}

resource "google_bigquery_table" "transactions" {
  dataset_id = google_bigquery_dataset.raw_data.dataset_id
  table_id   = "transactions"
  schema     = file("schemas/transactions.json")
  time_partitioning {
    type = "DAY"
  }
}

resource "google_bigquery_table" "loans" {
  dataset_id = google_bigquery_dataset.raw_data.dataset_id
  table_id   = "loans"
  schema     = file("schemas/loans.json")
  time_partitioning {
    type = "DAY"
  }
}

# Pub/Sub subscriptions with BigQuery as sink

resource "google_pubsub_subscription" "customers_subscription" {
  name  = "customers-subscription"
  topic = google_pubsub_topic.banking_raw_data.name

  bigquery_config {
    table              = "${var.project_id}.${google_bigquery_dataset.raw_data.dataset_id}.customers"
    use_topic_schema   = false
    write_metadata     = true
  }

  ack_deadline_seconds = 60
}

resource "google_pubsub_subscription" "accounts_subscription" {
  name  = "accounts-subscription"
  topic = google_pubsub_topic.banking_raw_data.name

  bigquery_config {
    table              = "${var.project_id}.${google_bigquery_dataset.raw_data.dataset_id}.accounts"
    use_topic_schema   = false
    write_metadata     = true
  }

  ack_deadline_seconds = 60
}

resource "google_pubsub_subscription" "transactions_subscription" {
  name  = "transactions-subscription"
  topic = google_pubsub_topic.banking_raw_data.name

  bigquery_config {
    table              = "${var.project_id}.${google_bigquery_dataset.raw_data.dataset_id}.transactions"
    use_topic_schema   = false
    write_metadata     = true
  }

  ack_deadline_seconds = 60
}

resource "google_pubsub_subscription" "loans_subscription" {
  name  = "loans-subscription"
  topic = google_pubsub_topic.banking_raw_data.name

  bigquery_config {
    table              = "${var.project_id}.${google_bigquery_dataset.raw_data.dataset_id}.loans"
    use_topic_schema   = false
    write_metadata     = true
  }

  ack_deadline_seconds = 60
}
