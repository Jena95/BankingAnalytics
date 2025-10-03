CREATE TABLE IF NOT EXISTS `banking_dataset.banking_clean` (
  transaction_id STRING,
  account_id STRING,
  transaction_type STRING,
  amount FLOAT64,
  transaction_timestamp TIMESTAMP,
  merchant STRING,
  subscription_name STRING,
  publish_time TIMESTAMP
)
PARTITION BY DATE(publish_time);


