output "pubsub_topic" {
  value = google_pubsub_topic.demo_topic.name
}

output "bigquery_table" {
  value = "${google_bigquery_dataset.demo_dataset.dataset_id}.${google_bigquery_table.demo_table.table_id}"
}

output "subscription_name" {
  value = google_pubsub_subscription.bigquery_subscription.name
}
