output "pubsub_topic" {
  value = google_pubsub_topic.banking_topic.name
}

output "bigquery_table" {
  value = "${google_bigquery_dataset.banking_dataset.dataset_id}.${google_bigquery_table.banking_table.table_id}"
}

output "subscription_name" {
  value = google_pubsub_subscription.banking_table_subscription.name
}
