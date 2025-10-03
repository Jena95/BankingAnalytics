CREATE OR REPLACE PROCEDURE `your_project.banking_dataset.flatten_pubsub_data`(project_id STRING)
BEGIN
  EXECUTE IMMEDIATE FORMAT("""
    INSERT INTO `%s.your_dataset.flat_transactions` (
      transaction_id,
      account_id,
      transaction_type,
      amount,
      transaction_timestamp,
      merchant,
      subscription_name,
      publish_time
    )
    SELECT
      JSON_VALUE(data, '$.transaction_id') AS transaction_id,
      JSON_VALUE(data, '$.account_id') AS account_id,
      JSON_VALUE(data, '$.transaction_type') AS transaction_type,
      CAST(JSON_VALUE(data, '$.amount') AS FLOAT64) AS amount,
      PARSE_TIMESTAMP('%%Y-%%m-%%dT%%H:%%M:%%E*S%%Ez', JSON_VALUE(data, '$.timestamp')) AS transaction_timestamp,
      JSON_VALUE(data, '$.merchant') AS merchant,
      subscription_name,
      publish_time
    FROM
      `%s.your_dataset.raw_pubsub_data`
    WHERE
      publish_time >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 1 DAY);
  """, project_id, project_id);
END;