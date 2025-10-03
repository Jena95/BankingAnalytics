# GCP Pub/Sub → BigQuery Streaming (POC)

This project is a Proof of Concept (POC) for streaming data directly from Google Cloud Pub/Sub to BigQuery using Terraform.

It sets up:

A Pub/Sub topic

A BigQuery dataset and table

A subscription that directly streams data from the topic to BigQuery

Required IAM permissions for streaming to succeed

1. Clone this repository


2. Initialize Terraform
``` terraform init

3. Create Resources
``` terraform apply -var="project_id=your-gcp-project-id"

4. Test Pubsub to Bigquery Flow.

```
gcloud pubsub topics publish demo-topic --message="Hello from Pub/Sub!"
```

```
SELECT 
  publish_time, 
  data, 
  message_id, 
  attributes, 
  subscription_name
FROM `your-gcp-project-id.demo_dataset.demo_table`
ORDER BY publish_time DESC
```


# Alternative Approach for each decision points.

| Step              | Approach Used             | Alternatives / Trade-offs                                 |
| ----------------- | ------------------------- | --------------------------------------------------------- |
| Provisioning      | Terraform (IaC)           | `gcloud`, Console UI — less reproducible                  |
| Data ingestion    | Direct Pub/Sub → BigQuery | Use **Dataflow**, **Cloud Functions** for transformations |
| Schema management | Static JSON schema        | Use **schema auto-detect** or **external JSON file**      |
| Permissions       | Manual IAM binding        | Use **custom roles**, **least privilege** model           |
| Partitioning      | BQ `publish_time` field   | Use ingestion time or a custom timestamp                  |
| Message format    | Simple strings            | Use structured **JSON**, **AVRO**, **Protobuf**           |
| Metadata          | `write_metadata=true`     | Set `false` to simplify table schema                      |




