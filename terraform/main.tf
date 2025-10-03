provider "google" {
  project = var.project_id
  region  = var.region
}

# ------------------------
# Pub/Sub Topic
# ------------------------
resource "google_pubsub_topic" "demo_topic" {
  name = "demo-topic"
}

resource "google_pubsub_topic" "banking_topic" {
  name = "banking-topic"
}


# ------------------------
# BigQuery Dataset
# ------------------------
resource "google_bigquery_dataset" "demo_dataset" {
  dataset_id = "demo_dataset"
  location   = "US"
}

resource "google_bigquery_dataset" "banking_dataset" {
  dataset_id = "banking_dataset"
  location   = "US"
}

# ------------------------
# BigQuery Table
# ------------------------
resource "google_bigquery_table" "demo_table" {
  dataset_id = google_bigquery_dataset.demo_dataset.dataset_id
  table_id   = "demo_table"

  deletion_protection = false

  schema = <<EOF
[
  { "name": "data", "type": "STRING", "mode": "NULLABLE" },
  { "name": "subscription_name", "type": "STRING", "mode": "NULLABLE" },
  { "name": "message_id", "type": "STRING", "mode": "NULLABLE" },
  { "name": "attributes", "type": "STRING", "mode": "NULLABLE" },
  { "name": "publish_time", "type": "TIMESTAMP", "mode": "NULLABLE" }
]
EOF

  time_partitioning {
    type = "DAY"
    field = "publish_time"
  }
}


resource "google_bigquery_table" "banking_table" {
  dataset_id = google_bigquery_dataset.demo_dataset.dataset_id
  table_id   = "banking_raw"

  deletion_protection = false

  schema = <<EOF
[
  { "name": "data", "type": "STRING", "mode": "NULLABLE" },
  { "name": "subscription_name", "type": "STRING", "mode": "NULLABLE" },
  { "name": "message_id", "type": "STRING", "mode": "NULLABLE" },
  { "name": "attributes", "type": "STRING", "mode": "NULLABLE" },
  { "name": "publish_time", "type": "TIMESTAMP", "mode": "NULLABLE" }
]
EOF

  time_partitioning {
    type = "DAY"
    field = "publish_time"
  }
}


# ------------------------
# Pub/Sub Subscription → BigQuery
# ------------------------
resource "google_pubsub_subscription" "bigquery_subscription" {
  name  = "demo-subscription"
  topic = google_pubsub_topic.demo_topic.name

  bigquery_config {
    table                  = "${var.project_id}:${google_bigquery_dataset.demo_dataset.dataset_id}.${google_bigquery_table.demo_table.table_id}"
    write_metadata         = true
  }

  ack_deadline_seconds = 60
}

resource "google_pubsub_subscription" "bigquery_subscription" {
  name  = "banking-subscription"
  topic = google_pubsub_topic.banking_topic.name

  bigquery_config {
    table                  = "${var.project_id}:${google_bigquery_dataset.demo_dataset.dataset_id}.${google_bigquery_table.demo_table.table_id}"
    write_metadata         = true
  }

  ack_deadline_seconds = 60
}


# ------------------------
# IAM: Allow Pub/Sub to Write to BigQuery
# ------------------------
# This is the Google-managed service account used by Pub/Sub for BigQuery streaming
# Format: service-<project-number>@gcp-sa-pubsub.iam.gserviceaccount.com


data "google_project" "project" {}

resource "google_project_iam_member" "pubsub_bigquery_writer" {
  project = var.project_id
  role    = "roles/bigquery.dataEditor"
  member  = "serviceAccount:service-${data.google_project.project.number}@gcp-sa-pubsub.iam.gserviceaccount.com"
}
