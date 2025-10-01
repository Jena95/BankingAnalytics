provider "google" {
  project = var.project_id
  region  = var.region
}

# -----------------------
# BigQuery Dataset
# -----------------------
resource "google_bigquery_dataset" "banking_dataset" {
  dataset_id                  = var.dataset_id
  friendly_name               = "Banking Dataset"
  location                    = var.region
  delete_contents_on_destroy = true
}

# -----------------------
# BigQuery Table
# -----------------------
resource "google_bigquery_table" "banking_table" {
  dataset_id = google_bigquery_dataset.banking_dataset.dataset_id
  table_id   = var.table_id

  schema = jsonencode([
    { name = "type",           type = "STRING",  mode = "REQUIRED" },
    { name = "account_id",     type = "INTEGER", mode = "NULLABLE" },
    { name = "account_number", type = "STRING",  mode = "NULLABLE" },
    { name = "account_type",   type = "STRING",  mode = "NULLABLE" },
    { name = "balance",        type = "FLOAT",   mode = "NULLABLE" },
    { name = "customer_id",    type = "INTEGER", mode = "NULLABLE" },
    { name = "open_date",      type = "DATE",    mode = "NULLABLE" },
    { name = "status",         type = "STRING",  mode = "NULLABLE" }
  ])

  deletion_protection = false
}


# -----------------------
# Pub/Sub Topic (optional)
# -----------------------
resource "google_pubsub_topic" "banking_topic" {
  name = var.pubsub_topic_name
}

# -----------------------
# Pub/Sub → BigQuery Subscription
# -----------------------
resource "google_pubsub_subscription" "bq_subscription" {
  name  = var.subscription_name
  topic = google_pubsub_topic.banking_topic.id

  bigquery_config {
    table            = "${var.project_id}.${google_bigquery_dataset.banking_dataset.dataset_id}.${var.table_id}"
    use_topic_schema = false
    write_metadata   = false
}


  ack_deadline_seconds        = 20
  message_retention_duration  = "604800s" # 7 days
}