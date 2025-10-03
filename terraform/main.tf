provider "google" {
  project = var.project_id
  region  = var.region
}

# Pub/Sub Topic
resource "google_pubsub_topic" "banking_topic" {
  name = "banking-raw-topic"
  message_storage_policy {
    allowed_persistence_regions = [var.region]
  }
  schema_settings {
    schema = google_pubsub_schema.banking_schema.id
    encoding = "JSON"
  }
}

# Pub/Sub Schema
resource "google_pubsub_schema" "banking_schema" {
  name       = "banking-schema"
  type       = "AVRO"
  definition = file("schema.avsc")
}


# BigQuery Dataset
resource "google_bigquery_dataset" "banking_dataset" {
  dataset_id                  = "banking_raw"
  location                    = var.region
  delete_contents_on_destroy = true
}

# BigQuery Table (Raw landing table)
resource "google_bigquery_table" "banking_raw_table" {
  dataset_id = google_bigquery_dataset.banking_dataset.dataset_id
  table_id   = "raw_banking_data"

  schema = file("bq_schema.json")

  deletion_protection = false
}

# Pub/Sub -> BigQuery Subscription
resource "google_pubsub_subscription" "banking_subscription" {
  name  = "banking-subscription"
  topic = google_pubsub_topic.banking_topic.id

  bigquery_config {
    table            = "projects/${var.project_id}/datasets/banking_raw/tables/raw_banking_data"
    use_topic_schema = true
    write_metadata   = true
  }

  ack_deadline_seconds = 20
}


# IAM: Grant Pub/Sub Service Account BigQuery Data Editor
data "google_project" "project" {}

resource "google_project_iam_member" "pubsub_to_bq_writer" {
  project = var.project_id
  role    = "roles/bigquery.dataEditor"
  member  = "serviceAccount:service-${data.google_project.project.number}@gcp-sa-pubsub.iam.gserviceaccount.com"
}
