CREATE OR REPLACE PROCEDURE `banking_dataset.flatten_pubsub_data`(project_id STRING)
BEGIN
  DECLARE target_table STRING;
  DECLARE source_table STRING;
  DECLARE sql_statement STRING;

  -- Define table names dynamically
  SET target_table = FORMAT('%s.banking_dataset.banking_clean', project_id);
  SET source_table = FORMAT('%s.banking_dataset.banking_raw', project_id);

  -- Compose the dynamic SQL
  SET sql_statement = FORMAT("""
    INSERT INTO `%s` (
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
      `%s`
    WHERE
      publish_time >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 1 DAY);
  """, target_table, source_table);

  -- Run the query
  EXECUTE IMMEDIATE sql_statement;
END;
