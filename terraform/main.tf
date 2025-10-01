terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = ">= 5.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# Variables
variable "project_id" {
  description = "GCP Project ID"
  type        = string
  default     = "your-project-id"  # Replace
}

variable "region" {
  description = "GCP Region"
  type        = string
  default     = "us-central1"
}

variable "project_number" {
  description = "GCP Project Number (run `gcloud projects describe [PROJECT_ID] --format='value(projectNumber)'`)"
  type        = string
  default     = ""  # Replace with actual number
}

# Pub/Sub Topic
resource "google_pubsub_topic" "raw_data_topic" {
  name     = "banking-raw-data-topic"
  project  = var.project_id
  labels = {
    env = "dev"
  }
}

# BigQuery Dataset
resource "google_bigquery_dataset" "banking_raw" {
  dataset_id                  = "banking_raw"
  project                     = var.project_id
  location                    = var.region
  delete_contents_on_destroy  = true  # For dev; set false in prod
}

# BigQuery Table with schema for raw JSON (table + record struct)
resource "google_bigquery_table" "raw_data" {
  dataset_id = google_bigquery_dataset.banking_raw.dataset_id
  table_id   = "raw_data"
  project    = var.project_id
  deletion_protection = false  # For dev; set true in prod

  schema = jsonencode([
    {
      name     = "table"
      type     = "STRING"
      mode     = "REQUIRED"
      description = "Source table (customers, accounts, transactions, loans)"
    },
    {
      name     = "record"
      type     = "RECORD"
      mode     = "REQUIRED"
      fields = [
        # Common fields; extend based on your data
        { name = "id", type = "INTEGER", mode = "REQUIRED" },
        { name = "name", type = "STRING", mode = "NULLABLE" },  # For customers
        { name = "address", type = "STRING", mode = "NULLABLE" },
        { name = "balance", type = "FLOAT", mode = "NULLABLE" },  # For accounts
        { name = "amount", type = "FLOAT", mode = "NULLABLE" },  # For transactions
        { name = "principal", type = "FLOAT", mode = "NULLABLE" },  # For loans
        # Add more fields as needed (e.g., dates as TIMESTAMP)
        { name = "date", type = "TIMESTAMP", mode = "NULLABLE" }
      ]
    }
  ])

  time_partitioning {
    type = "DAY"  # Partition by ingestion date for efficiency
  }

  depends_on = [google_bigquery_dataset.banking_raw]
}

# Pub/Sub Subscription with BigQuery Sink
resource "google_pubsub_subscription" "raw_data_sub" {
  name  = "raw-data-sub"
  topic = google_pubsub_topic.raw_data_topic.name
  project = var.project_id

  bigquery_config {
    table = "${var.project_id}.${google_bigquery_dataset.banking_raw.dataset_id}.${google_bigquery_table.raw_data.table_id}"
    use_table_insert = true  # Use streaming inserts
  }

  # Retention policy (7 days default)
  message_retention_duration = "7d"

  depends_on = [google_bigquery_table.raw_data]
}

# IAM: Grant Pub/Sub SA access to BigQuery
resource "google_bigquery_dataset_iam_member" "pubsub_editor" {
  dataset_id = google_bigquery_dataset.banking_raw.dataset_id
  project    = var.project_id
  role       = "roles/bigquery.dataEditor"
  member     = "serviceAccount:service-${var.project_number}@gcp-sa-pubsub.iam.gserviceaccount.com"
}

resource "google_bigquery_dataset_iam_member" "pubsub_viewer" {
  dataset_id = google_bigquery_dataset.banking_raw.dataset_id
  project    = var.project_id
  role       = "roles/bigquery.metadataViewer"
  member     = "serviceAccount:service-${var.project_number}@gcp-sa-pubsub.iam.gserviceaccount.com"
}

# Outputs
output "topic_name" {
  value = google_pubsub_topic.raw_data_topic.name
}

output "subscription_name" {
  value = google_pubsub_subscription.raw_data_sub.name
}

output "bigquery_table" {
  value = "${var.project_id}.${google_bigquery_dataset.banking_raw.dataset_id}.${google_bigquery_table.raw_data.table_id}"
}