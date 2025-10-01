variable "project_id" {
  description = "GCP project ID"
  type        = string
}

variable "region" {
  description = "GCP region"
  type        = string
  default     = "us-central1"
}

variable "dataset_id" {
  description = "BigQuery dataset ID"
  type        = string
}

variable "table_id" {
  description = "BigQuery table ID"
  type        = string
}

variable "pubsub_topic_name" {
  description = "Pub/Sub topic name (must already exist if manually created)"
  type        = string
}

variable "subscription_name" {
  description = "Pub/Sub subscription name"
  type        = string
}
