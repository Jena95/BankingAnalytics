provider "google" {
  project = var.project_id
  region  = var.region
}

# Variables
variable "project_id" {
  description = "GCP Project ID"
  type        = string
  default     = "brave-reason-421203"
}

variable "region" {
  description = "GCP Region"
  type        = string
  default     = "us-central1"
}

variable "project_number" {
  description = "GCP Project Number"
  type        = string
  default     = "185017523924"
}

# Pub/Sub Schema
resource "google_pubsub_schema" "raw_data_schema" {
  name    = "raw-data-schema"
  project = var.project_id
  type    = "AVRO"
  definition = jsonencode({
    type = "record",
    name = "RawData",
    fields = [
      {
        name = "data",
        type = "string"
      },
      {
        name = "table",
        type = "string"
      },
      {
        name = "record",
        type = ["null", {
          type = "record",
          name = "Record",
          fields = [
            { name = "customer_id", type = ["null", "long"] },
            { name = "name", type = ["null", "string"] },
            { name = "address", type = ["null", "string"] },
            { name = "email", type = ["null", "string"] },
            { name = "phone", type = ["null", "string"] },
            { name = "date_joined", type = ["null", "string"] },
            { name = "account_id", type = ["null", "long"] },
            { name = "account_number", type = ["null", "string"] },
            { name = "account_type", type = ["null", "string"] },
            { name = "balance", type = ["null", "double"] },
            { name = "open_date", type = ["null", "string"] },
            { name = "status", type = ["null", "string"] },
            { name = "transaction_id", type = ["null", "long"] },
            { name = "transaction_date", type = ["null", "string"] },
            { name = "transaction_type", type = ["null", "string"] },
            { name = "amount", type = ["null", "double"] },
            { name = "description", type = ["null", "string"] },
            { name = "category", type = ["null", "string"] },
            { name = "balance_after", type = ["null", "double"] },
            { name = "loan_id", type = ["null", "long"] },
            { name = "loan_type", type = ["null", "string"] },
            { name = "principal", type = ["null", "double"] },
            { name = "interest_rate", type = ["null", "double"] },
            { name = "term_months", type = ["null", "long"] },
            { name = "issue_date", type = ["null", "string"] }
          ]
        }]
      }
    ]
  })
}

# Pub/Sub Topic
resource "google_pubsub_topic" "raw_data_topic" {
  name    = "banking-raw-data-topic"
  project = var.project_id
  labels = {
    env = "dev"
  }
  schema_settings {
    schema   = google_pubsub_schema.raw_data_schema.id
    encoding = "JSON"
  }
  depends_on = [google_pubsub_schema.raw_data_schema]
}

# BigQuery Dataset
resource "google_bigquery_dataset" "banking_raw" {
  dataset_id                 = "banking_raw"
  project                   = var.project_id
  location                  = var.region
  delete_contents_on_destroy = true
}

# BigQuery Table
resource "google_bigquery_table" "raw_data" {
  dataset_id          = google_bigquery_dataset.banking_raw.dataset_id
  table_id           = "raw_data"
  project            = var.project_id
  deletion_protection = false
  schema             = file("schema.json")
  time_partitioning {
    type = "DAY"
  }
  depends_on = [google_bigquery_dataset.banking_raw]
}

# Pub/Sub Subscription
resource "google_pubsub_subscription" "raw_data_sub" {
  name    = "raw-data-sub"
  topic   = google_pubsub_topic.raw_data_topic.name
  project = var.project_id
  bigquery_config {
    table            = "${var.project_id}.${google_bigquery_dataset.banking_raw.dataset_id}.${google_bigquery_table.raw_data.table_id}"
    use_topic_schema = true
  }
  message_retention_duration = "604800s"
  depends_on = [google_bigquery_table.raw_data, google_pubsub_topic.raw_data_topic]
}

# IAM
resource "google_bigquery_dataset_iam_member" "pubsub_editor" {
  dataset_id = google_bigquery_dataset.banking_raw.dataset_id
  project    = var.project_id
  role       = "roles/bigquery.dataEditor"
  member     = "serviceAccount:service-${var.project_number}@gcp-sa-pubsub.iam.gserviceaccount.com"
  depends_on = [google_bigquery_dataset.banking_raw]
}

resource "google_bigquery_dataset_iam_member" "pubsub_viewer" {
  dataset_id = google_bigquery_dataset.banking_raw.dataset_id
  project    = var.project_id
  role       = "roles/bigquery.metadataViewer"
  member     = "serviceAccount:service-${var.project_number}@gcp-sa-pubsub.iam.gserviceaccount.com"
  depends_on = [google_bigquery_dataset.banking_raw]
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