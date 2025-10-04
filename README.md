# GCP Pub/Sub → BigQuery Streaming (POC)

This project is about streaming data directly from Google Cloud Pub/Sub to BigQuery for data analysis using Terraform.

It sets up:

A Pub/Sub topic

A BigQuery dataset and table

A subscription that directly streams data from the topic to BigQuery

Required IAM permissions for streaming to succeed

1. Clone this repository


2. Initialize Terraform `terraform init`

3. Create Resources

`
terraform apply -var="project_id=your-gcp-project-id"
`


4. Test Pubsub to Bigquery Flow.

```
gcloud pubsub topics publish banking-topic --message="Hello from Pub/Sub!
```

```
SELECT 
  publish_time, 
  data, 
  message_id, 
  attributes, 
  subscription_name
FROM `your-gcp-project-id.banking_dataset.banking_raw`
ORDER BY publish_time DESC
```

5. In data simulation folder we have a python program that streams data to pubsub when run.

```
python dataStream.py your-project-id banking-topic
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


__________________________________________________________________________________

Now we will use the raw streamed data for data analysis.

To do this we will convert the pubsub json data format into flat format.
Goto etl folder, then run below command or take the sql queries and run in console.

1. Create a table (banking_clean) to store the converted data.
    
    `
    bq query --use_legacy_sql=false < createTable.sql
`

2. Create a procedure(flatten_pubsub_data) that converts the json fields into flat table.

    `
  bq query --use_legacy_sql=false < createProcedure.sql
`
3. Schedule the procedure call.
    
   ``` CALL `banking_dataset.flatten_pubsub_data`('your-project-id');```
