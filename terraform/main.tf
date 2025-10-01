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
