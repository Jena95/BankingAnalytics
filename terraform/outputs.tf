output "pubsub_topic" {
  value = google_pubsub_topic.banking_topic.name
}

output "bigquery_table" {
  value = google_bigquery_table.banking_raw_table.id
}
