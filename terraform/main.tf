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

# ------------------------
# BigQuery Dataset
# ------------------------
resource "google_bigquery_dataset" "demo_dataset" {
  dataset_id = "demo_dataset"
  location   = "US"
}

# ------------------------
# BigQuery Table
# ------------------------
resource "google_bigquery_table" "demo_table" {
  dataset_id = google_bigquery_dataset.demo_dataset.dataset_id
  table_id   = "demo_table"
  schema     = <<EOF
[
  {
    "name": "message",
    "type": "STRING",
    "mode": "NULLABLE"
  },
  {
    "name": "timestamp",
    "type": "TIMESTAMP",
    "mode": "NULLABLE"
  }
]
EOF

  time_partitioning {
    type  = "DAY"
    field = "timestamp"
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

# ------------------------
# IAM: Allow Pub/Sub to Write to BigQuery
# ------------------------

data "google_project" "project" {}

data "google_service_account" "pubsub_sa" {
  account_id = "service-${data.google_project.project.number}@gcp-sa-pubsub.iam.gserviceaccount.com"
}

resource "google_project_iam_member" "pubsub_bigquery_writer" {
  project = var.project_id
  role    = "roles/bigquery.dataEditor"
  member  = "serviceAccount:${data.google_service_account.pubsub_sa.email}"
}
