Title: The Sunday Materialization - Idempotency in Data Pipelines
Subtitle: The One Concept That Saves Your Weekends, Your Backfills, and Your Blood Pressure
Date: 2025-10-26 07:00
Modified: 2025-10-26 07:00
Category: Sunday
Tags: data engineer, data platform engineer, data, data architecture, idempotency, data pipelines, reliability, backfills, orchestration
Slug: sunday-materialization-idempotency-data-pipelines
Authors: Eduardo G Gusmao
Summary: A weekly educational topic/lecture/discussion on Data Engineering topics that we all experienced at least once (or will!)
Status: final
Lang: en
Template: topic
Cadence: Biweekly
Scope: Data Engineering, Industry, Data Challenges
Tone: Analytical, Educational, Non-Sensational
Canonical: https://www.gusmaolab.org/blog/sunday-materialization-idempotency-data-pipelines/
Meta_description: Biweekly analysis of important Data Engineering concepts.
Meta_keywords: data concepts, topics, lectures, discussions, idempotency, data pipelines, data reliability
Cover: images/covers/idempotency-data-pipelines.png
Thumbnail: images/thumbnails/idempotency-data-pipelines-thumb.png

# Idempotency in Data Pipelines: The One Concept That Saves Your Weekends

There are many beautiful concepts in data engineering.

Partition pruning.
Schema evolution.
Columnar storage.
Exactly-once processing.
Data contracts.
Slowly changing dimensions.
The sacred feeling of a DAG that finishes before breakfast.

But if I had to choose one concept that quietly saves more weekends than almost any other, it would be **idempotency**.

Idempotency is one of those words that sounds more intimidating than it is. It has the energy of a legal clause wearing a lab coat.

But the idea is simple:

> An operation is idempotent if running it once or running it many times produces the same final result.

That is it.

If you run the pipeline today and it succeeds, great.

If you run it again because the orchestrator retried it, the final table should not be duplicated, corrupted, inflated, partially overwritten, or transformed into a mysterious business artifact known as “why are there 2x more customers today?”

Idempotency is the difference between:

> “The job failed. No problem, rerun it.”

and:

> “The job failed. Nobody touch anything. We need to inspect twelve tables, three S3 prefixes, two dashboards, and the emotional state of Finance.”

This is why idempotency matters.

It turns failure from a crisis into a routine event.

And in data engineering, failure will happen.

The question is not whether jobs fail.

The question is whether jobs fail safely.

---

## 1. The Simplest Definition

An operation is **idempotent** when repeating it does not change the final result after the first successful application.

Classic example:

```python
x = 10
x = 10
x = 10
```

No matter how many times we assign `10` to `x`, the final value is still `10`.

That operation is idempotent.

Now compare:

```python
x = 10
x += 10
x += 10
x += 10
```

Each time we run it, the result changes.

That operation is not idempotent.

In data engineering terms:

- **overwrite partition with the correct data** can be idempotent;
- **append the same records again** is usually not idempotent;
- **upsert by stable primary key** can be idempotent;
- **insert without deduplication** is usually not idempotent;
- **set a status field to `processed`** can be idempotent;
- **increment a counter** is usually not idempotent.

The difference looks small in code.

In production, it is the difference between calm reruns and incident archaeology.

---

## 2. Why Data Pipelines Need Idempotency

Data pipelines fail for boring reasons.

Not grand, cinematic reasons.

Boring ones.

- a network timeout;
- an API returns HTTP 503;
- a worker dies;
- a Spark executor runs out of memory;
- an object-store write partially succeeds;
- a database connection drops;
- the orchestrator retries a task;
- a file arrives late;
- a source system sends duplicate records;
- a warehouse query times out;
- a cloud service has a Tuesday;
- someone deploys a change at 17:58 because optimism is apparently free.

When a pipeline fails, the natural response is to rerun it.

But rerunning is only safe if the pipeline is designed to tolerate repetition.

If the pipeline is not idempotent, reruns can make the situation worse.

A failed job may have already written half its output.

A retry may write the same records again.

A backfill may recompute some partitions but not others.

A sync may update some destination records and fail on the rest.

A streaming job may reprocess messages after a checkpoint rollback.

Without idempotency, recovery becomes fragile.

With idempotency, recovery becomes boring.

And boring recovery is a gift.

A truly mature data platform is not one where nothing fails.

It is one where common failures can be retried safely.

---

## 3. The Weekend Scenario

Imagine this pipeline:

```
Extract transactions from source API
    ↓
Transform transactions
    ↓
Append transactions to warehouse table
    ↓
Build daily revenue dashboard
```

The job runs daily at 03:00.

At 03:12, it extracts 100,000 transactions.

At 03:18, it appends them to `fact_transactions`.

At 03:19, the process crashes before marking the run as complete.

The orchestrator retries.

The retry extracts the same 100,000 transactions.

Then it appends them again.

Now the table contains 200,000 rows for the same business events.

The DAG eventually turns green.

Finance wakes up to a miracle: revenue doubled overnight.

Everyone is excited for nine seconds.

Then someone notices the business did not actually double.

Congratulations. The pipeline is non-idempotent.

Now imagine a different design:

```
Extract transactions from source API
    ↓
Write to staging table for run_date
    ↓
Deduplicate by transaction_id
    ↓
Merge into target table by transaction_id
    ↓
Mark run as complete
```

If the job retries, the same `transaction_id` values are merged again.

The final table remains correct.

The retry does not duplicate business events.

That is idempotency saving your weekend.

Not dramatically.

Quietly.

Like a good lock on a door.

---

## 4. Idempotency Is About Final State

The important phrase is **final state**.

Idempotency does not mean nothing happens on retry.

A retry may:

- read the same files again;
- call the same API again;
- stage the same data again;
- recompute the same transformation;
- rewrite the same partition;
- update the same records;
- send the same payload.

But after all that, the final result should be the same as if the operation had succeeded once.

This is why idempotency is often easier when pipelines are designed around **state replacement** rather than uncontrolled mutation.

For example:

### Less safe

```sql
INSERT INTO daily_sales_summary
SELECT
    sale_date,
    SUM(amount) AS total_sales
FROM raw_sales
WHERE sale_date = DATE '2026-08-09'
GROUP BY sale_date;
```

If this runs twice, it may insert duplicate summary rows.

### Safer

```sql
DELETE FROM daily_sales_summary
WHERE sale_date = DATE '2026-08-09';

INSERT INTO daily_sales_summary
SELECT
    sale_date,
    SUM(amount) AS total_sales
FROM raw_sales
WHERE sale_date = DATE '2026-08-09'
GROUP BY sale_date;
```

This is closer to idempotent because the partition is cleared before insertion.

But even this has risks if the delete succeeds and the insert fails.

### Better

Use an atomic overwrite or table-format-supported replace operation when available:

```sql
INSERT OVERWRITE TABLE daily_sales_summary
PARTITION (sale_date = DATE '2026-08-09')
SELECT
    sale_date,
    SUM(amount) AS total_sales
FROM raw_sales
WHERE sale_date = DATE '2026-08-09'
GROUP BY sale_date;
```

The exact syntax depends on the engine, but the principle is:

> Replace the output for a known scope with a deterministic result.

This is one of the most common idempotency patterns in batch data engineering.

---

## 5. Determinism: Idempotency’s Best Friend

Idempotency is easier when transformations are deterministic.

A deterministic transformation produces the same output from the same input.

For example:

```sql
SELECT
    customer_id,
    COUNT(*) AS purchase_count
FROM purchases
GROUP BY customer_id;
```

Same input, same output.

Now compare:

```sql
SELECT
    customer_id,
    RANDOM() AS customer_score
FROM customers;
```

Same input, different output each time.

Or:

```sql
SELECT
    customer_id,
    CURRENT_TIMESTAMP AS processed_at
FROM customers;
```

Same input, but `processed_at` changes every run.

This does not mean you can never use timestamps or randomness. But you must understand how they affect reruns.

If `processed_at` is metadata about the pipeline run, fine.

If it is part of business logic or used downstream for incremental sync, repeated runs may behave differently.

A good rule:

> Business outputs should be deterministic whenever possible. Pipeline metadata can record when the computation happened.

Separate business data from operational metadata.

Example:

```sql
SELECT
    customer_id,
    purchase_count,
    DATE '2026-08-09' AS business_date,
    CURRENT_TIMESTAMP AS pipeline_processed_at
FROM customer_features;
```

Here, `business_date` is stable.
`pipeline_processed_at` is run metadata.

That distinction prevents a surprising amount of pain.

---

## 6. Idempotency and Primary Keys

Idempotency often depends on stable keys.

A stable key lets the pipeline know whether two records represent the same business entity or event.

Examples:

- `transaction_id`;
- `order_id`;
- `customer_id`;
- `account_id`;
- `event_id`;
- `claim_id`;
- `sample_id`;
- `encounter_id`;
- `variant_id`;
- composite key such as `(patient_id, encounter_date, diagnosis_code)`.

Without stable keys, pipelines struggle to deduplicate or upsert safely.

Suppose you ingest orders.

If each order has a stable `order_id`, you can merge:

```sql
MERGE INTO fact_orders AS target
USING staging_orders AS source
ON target.order_id = source.order_id
WHEN MATCHED THEN UPDATE SET
    target.status = source.status,
    target.amount = source.amount,
    target.updated_at = source.updated_at
WHEN NOT MATCHED THEN INSERT (
    order_id,
    status,
    amount,
    updated_at
)
VALUES (
    source.order_id,
    source.status,
    source.amount,
    source.updated_at
);
```

If the same batch runs twice, the second run updates the same rows rather than inserting duplicates.

But if there is no reliable key, the pipeline may be forced to guess.

Guessing identity is how duplicates become family members.

Stable keys are the skeleton of idempotent pipelines.

No skeleton, no posture.

---

## 7. Natural Keys, Surrogate Keys, and Generated IDs

Keys deserve care.

A **natural key** comes from the business domain.

Examples:

- `email`;
- `national_id`;
- `order_number`;
- `invoice_number`;
- `sample_barcode`;
- `transaction_reference`.

A **surrogate key** is generated by the system.

Examples:

- integer sequence;
- UUID;
- hash key;
- warehouse-specific synthetic ID.

Both can be useful.

But generated keys can break idempotency if they are regenerated on every run.

Example of a dangerous pattern:

```sql
SELECT
    UUID() AS row_id,
    customer_id,
    purchase_date,
    amount
FROM raw_purchases;
```

If the pipeline reruns, the same business record receives a different `row_id`.

Downstream, it may look like a new record.

A safer pattern is to generate deterministic keys from stable business fields:

```sql
SELECT
    MD5(CONCAT(customer_id, '|', purchase_date, '|', source_transaction_id)) AS row_id,
    customer_id,
    purchase_date,
    amount
FROM raw_purchases;
```

This hash is deterministic.

Same input fields, same key.

But be careful: deterministic hashes are only as good as the fields used.

If the fields are not truly unique or stable, the hash will faithfully encode your mistake with mathematical confidence.

Very elegant. Still wrong.

---

## 8. Append-Only Is Not Automatically Idempotent

Append-only pipelines are common.

They are simple and efficient when the source truly emits immutable unique events.

But append-only does not automatically mean safe.

Unsafe append:

```
Run 1:
    append events from 00:00–01:00

Retry:
    append the same events from 00:00–01:00 again

Result:
    duplicates
```

Safe append requires one of these:

- source guarantees unique events and no repeated extraction;
- pipeline deduplicates by event ID;
- target enforces uniqueness;
- staging layer tracks already processed files or offsets;
- write operation is transactional;
- downstream models are designed to deduplicate.

For event logs, a common pattern is:

```sql
SELECT *
FROM (
    SELECT
        *,
        ROW_NUMBER() OVER (
            PARTITION BY event_id
            ORDER BY ingestion_timestamp DESC
        ) AS rn
    FROM raw_events
)
WHERE rn = 1;
```

This creates a deduplicated view or table based on `event_id`.

But again: this depends on `event_id` being reliable.

If the source sends no event ID, the platform may need to derive one.

For example:

```sql
MD5(CONCAT(user_id, '|', event_type, '|', event_timestamp, '|', session_id))
```

This may work.

Or it may collapse distinct events that happen at the same timestamp.

Or fail when timestamps are rounded.

Idempotency is not just syntax.

It is business identity plus engineering discipline.

---

## 9. Idempotent Batch Pipelines

Batch pipelines are often easier to make idempotent because the processing scope is bounded.

A daily batch has a natural boundary:

```
business_date = 2026-08-09
```

An hourly batch has:

```
hour = 2026-08-09 13:00
```

A monthly report has:

```
month = 2026-08
```

If the pipeline output is scoped to that boundary, you can replace that output deterministically.

Common idempotent batch patterns include:

### Partition overwrite

Replace one partition at a time.

```sql
INSERT OVERWRITE TABLE fact_events
PARTITION (event_date = DATE '2026-08-09')
SELECT *
FROM staging_events
WHERE event_date = DATE '2026-08-09';
```

### Staging then swap

Write output to a temporary table or location, validate it, then atomically promote it.

```text
Write new output to:
    s3://bucket/table/_staging/run_id=abc123/

Validate:
    row counts
    schema
    quality checks

Promote:
    update metadata pointer
    or replace target partition
```

### Delete and insert within a transaction

Use when the storage engine supports transactions.

```sql
BEGIN;

DELETE FROM daily_metrics
WHERE metric_date = DATE '2026-08-09';

INSERT INTO daily_metrics
SELECT *
FROM staging_daily_metrics
WHERE metric_date = DATE '2026-08-09';

COMMIT;
```

### Merge/upsert

Use stable keys to update existing records and insert new ones.

```sql
MERGE INTO customers AS target
USING staging_customers AS source
ON target.customer_id = source.customer_id
WHEN MATCHED THEN UPDATE SET
    target.email = source.email,
    target.status = source.status
WHEN NOT MATCHED THEN INSERT (
    customer_id,
    email,
    status
)
VALUES (
    source.customer_id,
    source.email,
    source.status
);
```

The common theme:

> Define the scope, compute the desired state, and write it safely.

---

## 10. Idempotent Streaming Pipelines

Streaming makes idempotency harder because the input is unbounded.

Instead of “process this date,” you process a continuous flow.

Still, the concept is the same:

> Reprocessing the same message or window should not corrupt the final output.

Streaming systems often need to handle:

- duplicate messages;
- out-of-order events;
- late arrivals;
- checkpoint recovery;
- sink retries;
- partial writes;
- consumer restarts;
- replayed events.

Common patterns include:

### Stable event IDs

Each event has a unique ID.

```json
{
  "event_id": "evt_123",
  "user_id": "u_456",
  "event_type": "purchase",
  "event_time": "2026-08-09T12:03:00Z"
}
```

The sink can deduplicate by `event_id`.

### Idempotent sink writes

Write using upsert semantics rather than blind append.

```text
key = event_id
operation = upsert
```

### Checkpointing

Track processed offsets or progress.

```text
Kafka topic: purchases
Partition: 0
Processed offset: 92817382
```

### Windowed aggregation with deterministic keys

For example:

```text
metric_key = event_type + window_start + window_end
```

Then each aggregate updates the same output row for the same window.

### Exactly-once or effectively-once semantics

Many systems advertise exactly-once processing, but practical correctness still depends on source, processing engine, sink, checkpointing, and idempotent writes working together.

A useful phrase is **effectively once**:

> Even if processing happens more than once internally, the externally visible result behaves as if it happened once.

That is often what we really need.

Exactly-once is a promise.
Idempotency is how you survive when the promise meets reality.

---

## 11. Idempotency and Orchestrators

Orchestrators like Airflow, Dagster, Prefect, and cloud-native workflow systems retry tasks.

That is good.

But retries are safe only when tasks are safe to retry.

A task may fail after producing side effects.

Example:

```python
def load_data() -> None:
    data = extract_data()
    append_to_table(data)
    mark_success()
```

If `append_to_table(data)` succeeds but `mark_success()` fails, the orchestrator sees the task as failed.

It retries.

Then `append_to_table(data)` runs again.

Duplicate data.

Better design:

```python
def load_data(run_date: str) -> None:
    data = extract_data(run_date=run_date)
    write_to_staging(data=data, run_date=run_date)
    validate_staging(run_date=run_date)
    replace_target_partition(run_date=run_date)
    mark_success(run_date=run_date)
```

Now the task is scoped by `run_date`.

The output can be replaced rather than appended blindly.

The retry is safer.

An orchestrator can manage dependencies and retries.

But it cannot magically make unsafe code safe.

A retry button without idempotency is just a button labeled “maybe make it worse.”

---

## 12. Idempotency and Backfills

Backfills are where idempotency proves its worth.

A backfill means reprocessing historical data.

Examples:

- recompute January to March;
- fix a bug in customer segmentation;
- rebuild a feature table;
- reload a vendor file;
- regenerate a revenue mart;
- migrate from one table format to another;
- repair missing partitions;
- apply a new business rule historically.

Backfills are dangerous when pipelines are not idempotent.

A non-idempotent backfill may:

- duplicate records;
- mix old and new logic;
- partially overwrite outputs;
- create inconsistent partitions;
- trigger downstream workflows repeatedly;
- inflate metrics;
- destroy reproducibility.

A good backfill design asks:

- What is the scope?
- Which partitions will be replaced?
- Is the transformation deterministic?
- Are outputs validated before publishing?
- Can the backfill be restarted safely?
- Can it run in parallel with current production?
- Are downstream dependencies paused or aware?
- Is there a rollback plan?

A backfill-friendly pipeline is usually idempotent by design.

Example pattern:

```text
For each date in backfill range:
    compute output for date
    write to staging/date
    validate staging/date
    atomically replace target/date
    record successful date
```

If the process fails on day 17 of 90, you can restart from day 17.

You do not need to panic.

That is the vibe we want.

---

## 13. Idempotency and Staging Layers

Staging layers are one of the most useful tools for idempotency.

Instead of writing directly into the final table, write into a temporary or intermediate location first.

Example:

```text
Raw input
    ↓
Staging table for run
    ↓
Validation
    ↓
Final table update
```

Why this helps:

- you can inspect staged data;
- you can validate row counts;
- you can deduplicate before final write;
- you can retry staging without touching production;
- you can promote only after checks pass;
- you can isolate partial failures;
- you can keep run metadata.

Example naming pattern:

```text
staging.orders/run_id=2026-08-09T030000/
```

Or in a warehouse:

```sql
CREATE OR REPLACE TABLE staging.orders_2026_08_09 AS
SELECT *
FROM raw.orders
WHERE order_date = DATE '2026-08-09';
```

Then:

```sql
MERGE INTO fact_orders AS target
USING staging.orders_2026_08_09 AS source
ON target.order_id = source.order_id
WHEN MATCHED THEN UPDATE SET
    target.status = source.status,
    target.amount = source.amount
WHEN NOT MATCHED THEN INSERT (
    order_id,
    status,
    amount
)
VALUES (
    source.order_id,
    source.status,
    source.amount
);
```

Staging gives you a safe place to be wrong before publishing.

This is extremely valuable.

Production should not be the first place a pipeline discovers its output is nonsense.

---

## 14. Idempotency and Atomicity

Idempotency is related to atomicity, but they are not the same.

**Atomicity** means an operation happens completely or not at all.

**Idempotency** means repeating the operation leads to the same final result.

They work beautifully together.

Example of a dangerous non-atomic operation:

```text
Step 1: delete old partition
Step 2: insert new partition
```

If step 1 succeeds and step 2 fails, the partition is gone.

This may be idempotent-ish if rerun later, but during the failure window, the data is missing.

A better design uses an atomic replace if supported.

In lakehouse table formats or transactional warehouses, you may be able to commit a new snapshot atomically.

Conceptually:

```text
Prepare new files
Validate new files
Commit metadata pointer to new snapshot
```

Readers either see the old version or the new version.

Not a half-version.

That is powerful.

A mature platform tries to make important writes both:

- **idempotent**, so retries are safe;
- **atomic**, so partial states are not exposed.

This is how you avoid tables that are technically “between moods.”

---

## 15. Idempotency and External APIs

External APIs are a frequent source of non-idempotent pain.

Suppose a pipeline sends records to a SaaS tool.

Unsafe operation:

```text
POST /tickets
{
  "customer_id": "C123",
  "message": "Customer is high risk"
}
```

If the request succeeds but the client times out before receiving the response, the pipeline may retry.

Now two tickets are created.

Safer operation:

```text
PUT /tickets/customer-risk-C123-2026-08-09
{
  "customer_id": "C123",
  "message": "Customer is high risk"
}
```

Or use an idempotency key:

```text
Idempotency-Key: customer-risk-C123-2026-08-09
```

This tells the target system:

> If you see this operation again, treat it as the same request.

Many payment APIs, SaaS APIs, and internal services support some form of idempotency key.

If not, you may need to create your own deduplication layer.

External side effects are dangerous because they may not be easy to undo.

Creating duplicate rows in a warehouse is bad.

Sending duplicate customer emails is worse.

Creating duplicate invoices is the kind of thing that gives incident reviews a special flavor.

For outbound operations, idempotency is not optional.

It is a seatbelt.

---

## 16. Idempotency and Reverse ETL

Reverse ETL deserves special mention.

When sending warehouse data back into SaaS tools, idempotency determines whether retries are safe.

Safe pattern:

```text
Update Salesforce Account A123:
    Churn_Risk_Segment__c = "high"
```

If the sync retries, the same field is set to the same value.

Usually safe.

Unsafe pattern:

```text
Create new Salesforce task:
    "Call this customer because churn risk is high"
```

If the sync retries, multiple tasks may be created.

Better:

```text
Upsert task with external_id:
    "churn-risk-call:A123:2026-08-09"
```

Now the destination can recognize the same logical task.

Reverse ETL should prefer:

- upserts over creates;
- deterministic external IDs;
- field updates over side-effect actions;
- sync hashes to avoid unnecessary writes;
- record-level sync logs;
- retries with idempotency keys;
- dry runs for large changes;
- validation before sync.

A Reverse ETL job should never behave like a confetti cannon pointed at Salesforce.

Fun once. Expensive later.

---

## 17. Idempotency and Data Quality

Data quality checks should also be idempotent.

A check should not create duplicate records, repeatedly mutate state, or produce conflicting outputs when rerun.

For example, a quality check that logs failures should avoid duplicating the same failure endlessly.

Unsafe:

```sql
INSERT INTO data_quality_failures
SELECT
    'orders' AS table_name,
    order_id,
    'missing_customer_id' AS failure_type,
    CURRENT_TIMESTAMP AS detected_at
FROM orders
WHERE customer_id IS NULL;
```

If the check runs repeatedly, the same failure may be inserted many times.

Safer:

```sql
MERGE INTO data_quality_failures AS target
USING (
    SELECT
        'orders' AS table_name,
        order_id,
        'missing_customer_id' AS failure_type
    FROM orders
    WHERE customer_id IS NULL
) AS source
ON target.table_name = source.table_name
AND target.record_id = source.order_id
AND target.failure_type = source.failure_type
WHEN NOT MATCHED THEN INSERT (
    table_name,
    record_id,
    failure_type,
    first_detected_at
)
VALUES (
    source.table_name,
    source.order_id,
    source.failure_type,
    CURRENT_TIMESTAMP
);
```

Now repeated runs do not create duplicate failure records.

This matters for observability too.

If your monitoring tables are non-idempotent, your incident system may inflate the problem.

Nothing like a monitoring system that creates its own anomalies.

Very avant-garde. Not recommended.

---

## 18. Idempotency and File Processing

File-based pipelines are everywhere.

A common pattern:

```text
Incoming files:
    s3://landing/orders/orders_2026_08_09.csv
    s3://landing/orders/orders_2026_08_10.csv
```

A non-idempotent file pipeline might:

- read all files in the landing folder;
- append them to a target table;
- move files to an archive folder.

If the move fails after append, the next run may read the same files again.

Duplicate data.

Safer patterns include:

### Track processed file IDs

Keep a metadata table:

```sql
CREATE TABLE pipeline.processed_files (
    file_path STRING,
    file_checksum STRING,
    processed_at TIMESTAMP,
    status STRING
);
```

Before processing a file, check whether it was already successfully processed.

### Use file checksums

If a file path is reused with different contents, detect it.

### Write by partition replacement

If each file corresponds to a date partition, overwrite that partition instead of appending blindly.

### Use landing, processing, archive, and quarantine zones

Conceptual layout:

```text
landing/
    new files arrive here

processing/
    files currently being processed

archive/
    successfully processed files

quarantine/
    invalid or rejected files
```

### Make final writes idempotent

Even if the file is processed twice, the target should not duplicate records.

File movement alone is not enough.

File movement can fail too.

The final data write must still be safe.

---

## 19. Idempotency and Object Storage

Object storage complicates some traditional assumptions.

In object storage, operations like renames are often implemented as copy plus delete.

That means they are not always cheap or atomic.

A pipeline that relies on “move file after success” may behave differently on object storage than on a local filesystem or HDFS.

Safer patterns include:

- write to unique staging paths;
- commit by updating table metadata;
- avoid exposing partial output paths;
- use table formats with atomic commit semantics;
- use manifest files to declare completed outputs;
- separate temporary and published locations;
- clean up orphan files carefully.

Example:

```text
Temporary output:
    s3://bucket/orders/_tmp/run_id=abc123/

Published output:
    s3://bucket/orders/date=2026-08-09/
```

The pipeline writes temporary files, validates them, then publishes them through a controlled commit process.

Object storage is reliable, but it is not a traditional filesystem.

Treating it like one is how mysterious partial outputs are born.

They are small at first.

Then they grow teeth.

---

## 20. Idempotency in Lakehouse Table Formats

Lakehouse formats such as Iceberg, Delta Lake, and Hudi can help with idempotency.

They provide mechanisms such as:

- atomic commits;
- snapshots;
- MERGE operations;
- partition replacement;
- transaction logs;
- time travel;
- concurrent write handling;
- delete/update support.

This makes safe reruns easier.

But the format does not automatically make your pipeline idempotent.

You still need to design:

- stable keys;
- deterministic transformations;
- correct merge conditions;
- safe partition scopes;
- snapshot retention;
- compaction;
- retry behavior;
- backfill strategy.

For example, this merge is only as good as its key:

```sql
MERGE INTO target AS t
USING source AS s
ON t.customer_id = s.customer_id
WHEN MATCHED THEN UPDATE SET *
WHEN NOT MATCHED THEN INSERT *;
```

If `customer_id` is not unique in `source`, the merge may fail or behave unexpectedly depending on the engine.

If the wrong key is used, records may overwrite each other.

Lakehouse formats give you better tools.

They do not replace thinking.

A hammer is useful.

It will still happily hit your thumb if instructed.

---

## 21. Idempotency and Incremental Models

Incremental models are common in modern ELT workflows.

They process only new or changed data.

This is efficient, but can become non-idempotent if not carefully designed.

Example incremental filter:

```sql
SELECT *
FROM raw_events
WHERE ingestion_time > (
    SELECT MAX(ingestion_time)
    FROM target_events
);
```

This seems reasonable.

But it can fail if:

- late-arriving records have old `ingestion_time`;
- previous run partially wrote data;
- timestamps are not unique;
- clock skew exists;
- target table was manually edited;
- the max timestamp advanced before all records were loaded.

A safer incremental strategy may use:

- source offsets;
- immutable event IDs;
- overlap windows;
- deduplication;
- merge by key;
- run state tables;
- high-watermark plus safety buffer.

Example with overlap and deduplication:

```sql
WITH candidate_events AS (
    SELECT *
    FROM raw_events
    WHERE ingestion_time >= (
        SELECT last_successful_watermark - INTERVAL '2 hours'
        FROM pipeline_state
        WHERE pipeline_name = 'events_incremental'
    )
),

deduplicated AS (
    SELECT *
    FROM (
        SELECT
            *,
            ROW_NUMBER() OVER (
                PARTITION BY event_id
                ORDER BY ingestion_time DESC
            ) AS rn
        FROM candidate_events
    )
    WHERE rn = 1
)

MERGE INTO target_events AS target
USING deduplicated AS source
ON target.event_id = source.event_id
WHEN MATCHED THEN UPDATE SET *
WHEN NOT MATCHED THEN INSERT *;
```

The overlap catches late or missed records.

The merge prevents duplicates.

The pipeline state advances only after a successful run.

This is the kind of boring robustness that saves future you.

Future you is tired.

Be kind.

---

## 22. Watermarks and Pipeline State

Many idempotent incremental pipelines depend on watermarks.

A watermark records progress.

Examples:

- last processed timestamp;
- last processed file;
- last processed ID;
- last Kafka offset;
- last successful partition;
- last source version.

A simple pipeline state table:

```sql
CREATE TABLE pipeline_state (
    pipeline_name STRING,
    last_successful_watermark TIMESTAMP,
    last_successful_run_id STRING,
    updated_at TIMESTAMP
);
```

Important rule:

> Advance the watermark only after the output is safely committed.

Unsafe:

```text
1. Read data up to 10:00
2. Update watermark to 10:00
3. Write data
4. Write fails
```

Now the pipeline believes it processed data that was not written.

Safer:

```text
1. Read data up to 10:00
2. Write data to staging
3. Validate staging
4. Commit output
5. Update watermark to 10:00
```

The ordering matters.

Watermarks are small pieces of metadata with large consequences.

They are like bookmarks.

Move the bookmark before reading the page, and you will lose the story.

---

## 23. Idempotency and Side Effects

Data pipelines do not always only write tables.

They may also:

- send emails;
- publish messages;
- create tickets;
- trigger dashboards;
- call APIs;
- update SaaS fields;
- send Slack alerts;
- start downstream jobs;
- generate files for customers;
- submit regulatory extracts;
- update caches.

These are side effects.

Side effects are where idempotency gets tricky.

Writing a deterministic table partition is one thing.

Sending the same email twice is another.

For side effects, ask:

- Can this operation be repeated safely?
- Can we detect whether it already happened?
- Can we use an idempotency key?
- Can we separate computation from activation?
- Can we require approval before activation?
- Can we log every side effect?
- Can we compensate or roll back?

A useful pattern is the **outbox pattern**.

Instead of sending side effects directly during computation, write intended actions to an outbox table.

```sql
CREATE TABLE activation_outbox (
    action_id STRING,
    action_type STRING,
    target_system STRING,
    payload STRING,
    status STRING,
    created_at TIMESTAMP,
    sent_at TIMESTAMP
);
```

Then a separate sender process reads pending actions and sends them idempotently.

The `action_id` is deterministic.

If the sender retries, it can check whether the action was already sent.

This separates data computation from operational effects.

Separation is good.

It gives the system fewer opportunities to become a soup.

---

## 24. Idempotency and “Exactly Once”

People love saying “exactly once.”

It sounds perfect.

But in distributed systems, exactly-once behavior is subtle.

A pipeline may read a message once, process it once, and write it once only if the source, processing engine, checkpointing, and sink all cooperate.

That is a lot of cooperation.

Like organizing dinner with twelve academics.

In practice, many robust systems aim for **at-least-once processing plus idempotent writes**.

At-least-once means a record may be processed more than once.

Idempotent writes ensure duplicates do not corrupt the final state.

This is often easier to reason about.

Example:

```text
Source may deliver event twice.
Processor may retry event.
Sink upserts by event_id.
Final table contains one event.
```

From the outside, the result behaves correctly.

This is the key:

> If duplication is possible, make duplication harmless.

That is the idempotency mindset.

Not “duplicates will never happen.”

Rather:

> “Duplicates may happen, but they will not win.”

A very healthy attitude, honestly.

---

## 25. Idempotency in Healthcare and Biotech Pipelines

In healthcare and biotech, idempotency is especially important because pipelines often support reproducibility, auditability, and high-stakes analysis.

Examples:

- EHR ingestion;
- claims processing;
- laboratory result harmonization;
- patient cohort generation;
- phenotype extraction;
- genomic variant calling;
- sample metadata processing;
- clinical registry updates;
- ML feature generation for biomedical models.

Imagine an EHR pipeline that ingests diagnosis records.

If a daily extract is processed twice, the platform may duplicate diagnoses.

Then cohort logic may incorrectly count a patient as having repeated events.

Or a claims pipeline may duplicate billing records.

Or a genomics metadata pipeline may duplicate samples.

Or a variant annotation table may mix outputs from two pipeline versions.

These are not small errors.

They can affect:

- cohort sizes;
- statistical analysis;
- model training;
- quality indicators;
- reporting;
- clinical operations;
- scientific conclusions.

A safe biomedical data pipeline should:

- preserve source identifiers;
- track source file versions;
- record pipeline versions;
- write deterministic outputs;
- support reruns;
- isolate backfills;
- avoid duplicate clinical events;
- validate entity counts;
- maintain audit metadata;
- separate raw, staged, curated, and released data.

Example release pattern:

```text
raw_ehr_extracts/
    immutable source files

staging_ehr/
    parsed and normalized records by extract_id

curated_clinical_events/
    deduplicated and harmonized events

release_2026_08/
    validated cohort-ready snapshot
```

This structure helps protect reproducibility.

In science and healthcare, “just rerun it” is not enough.

You need to know whether rerunning produces the same result and why.

Idempotency is part of scientific hygiene.

And scientific hygiene is preferable to analytical mildew.

---

## 26. Idempotency and Observability

You should observe idempotency-related signals.

Useful metrics include:

- duplicate rate;
- records inserted;
- records updated;
- records deleted;
- records skipped;
- merge matched count;
- merge unmatched count;
- partition overwrite count;
- retry count;
- backfill progress;
- processed file count;
- late-arriving record count;
- source-to-target reconciliation;
- row count before and after;
- checksum or hash comparison;
- run status;
- watermark changes.

For example, a daily run report:

```text
pipeline: daily_orders
run_date: 2026-08-09
input_rows: 918,240
staged_rows: 918,240
deduplicated_rows: 917,882
duplicates_removed: 358
target_rows_inserted: 12,430
target_rows_updated: 905,452
target_rows_deleted: 0
watermark_before: 2026-08-08T23:59:59Z
watermark_after: 2026-08-09T23:59:59Z
status: success
```

This gives confidence.

It also helps detect suspicious behavior.

If a normal run updates 20,000 records and today updates 9 million, maybe that is real.

Or maybe someone changed a field hash and every record appears “changed.”

Observability turns idempotency from a hidden assumption into an operational property.

A pipeline should be able to explain what it changed.

If it cannot, we are back to vibes.

Vibes are not a recovery strategy.

---

## 27. Testing for Idempotency

Idempotency should be tested.

A simple test strategy:

> Run the same pipeline twice with the same input and verify the final output is unchanged.

Conceptually:

```python
from __future__ import annotations

import pandas as pd
from pandas.testing import assert_frame_equal


def normalize_output(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize output for deterministic comparison.

    Parameters
    ----------
    df
        Output DataFrame.

    Returns
    -------
    pd.DataFrame
        Sorted DataFrame with stable column order.
    """
    return (
        df
        .sort_values(list(df.columns))
        .reset_index(drop=True)
    )


def test_pipeline_is_idempotent(
    input_df: pd.DataFrame,
) -> None:
    """Check that running the transformation twice is stable.

    Parameters
    ----------
    input_df
        Input test data.
    """
    first_output = run_pipeline(input_df)
    second_output = run_pipeline(input_df)

    assert_frame_equal(
        normalize_output(first_output),
        normalize_output(second_output),
    )
```

For real pipelines, testing may involve:

- running a task twice in a test warehouse;
- comparing row counts;
- comparing checksums;
- checking primary-key uniqueness;
- verifying no duplicate files;
- validating merge behavior;
- testing retry after partial failure;
- testing backfill restart;
- testing late-arriving data;
- testing API retry with idempotency keys.

A stronger test:

```text
1. Run pipeline.
2. Simulate failure after staging but before final commit.
3. Rerun pipeline.
4. Verify final output is correct.
```

This kind of test catches failure modes that happy-path tests miss.

Happy-path tests are nice.

Failure-path tests are where reliability lives.

---

## 28. A Practical Idempotency Checklist

Before declaring a pipeline production-ready, ask:

1. Can this task run twice without duplicating data?
2. Can it fail halfway and be safely retried?
3. Does it write to staging before final output?
4. Is the final write atomic or close to atomic?
5. Are output partitions clearly scoped?
6. Are transformations deterministic?
7. Are primary keys stable and unique?
8. Are generated IDs deterministic when needed?
9. Are watermarks updated only after successful commits?
10. Are input files tracked by path and checksum?
11. Are duplicate source records handled?
12. Are late-arriving records handled?
13. Are merge conditions correct?
14. Are side effects idempotent?
15. Are API calls protected with idempotency keys?
16. Can backfills be restarted?
17. Can the pipeline explain what changed?
18. Are retries safe?
19. Are row counts and checksums monitored?
20. Is there a rollback or recovery plan?

If the answer to many of these is “no,” the pipeline may work.

But it may not be weekend-safe.

And weekend-safe is a real engineering quality.

Maybe not in the job description.

Definitely in the soul.

---

## 29. Common Anti-Patterns

### Anti-pattern 1: Blind append

Appending records without deduplication, keys, or processed-file tracking.

This is the classic duplicate factory.

### Anti-pattern 2: Updating watermarks too early

Advancing pipeline state before output is committed.

This creates missing data after failures.

### Anti-pattern 3: Random IDs for stable entities

Generating new IDs on every run for the same logical record.

This breaks deduplication and downstream joins.

### Anti-pattern 4: Non-atomic delete-then-insert

Deleting production data before new data is safely ready.

This creates failure windows.

### Anti-pattern 5: Side effects inside transformations

Sending emails, creating tickets, or calling APIs from inside a transformation job without idempotency.

This is how retries become dangerous.

### Anti-pattern 6: No staging layer

Writing directly from source to final table with no validation or recovery boundary.

Fast, until it is not.

### Anti-pattern 7: Trusting orchestrator retries blindly

Retries are only helpful when the task is safe to retry.

Otherwise, retries automate damage.

Very efficient. Very bad.

### Anti-pattern 8: Backfills using different logic from production

Historical rebuilds should use controlled, versioned logic.

Otherwise, history becomes interpretive art.

### Anti-pattern 9: No unique constraints or uniqueness checks

If the platform cannot detect duplicates, duplicates become normal.

### Anti-pattern 10: Treating idempotency as an implementation detail

It is not.

It is a reliability property of the data product.

---

## 30. What Good Looks Like

A good idempotent data pipeline usually has these traits:

### Clear processing scope

Each run knows what it is processing.

Example:

```text
run_date = 2026-08-09
source_system = billing
partition = invoice_date
```

### Stable input tracking

The pipeline knows which files, offsets, records, or source versions it processed.

### Staging before publishing

Intermediate outputs are isolated.

### Deterministic transformation

Same input produces same business output.

### Safe final write

The target is updated by overwrite, merge, or atomic commit.

### Stable keys

Records can be matched reliably across reruns.

### Post-write validation

The pipeline checks row counts, uniqueness, and quality.

### Watermark discipline

Progress is recorded only after success.

### Observability

Each run records what changed.

### Safe retries

The orchestrator can retry without fear.

That last one is the emotional reward.

When a job fails, you want to say:

> “Rerun it.”

Not:

> “Nobody breathe.”

---

## 31. The Deeper Principle: Design for Repetition

Idempotency is really about designing for repetition.

A pipeline will run again.

It will be retried.
It will be backfilled.
It will be replayed.
It will be tested.
It will be migrated.
It will be restarted after failure.
It will be executed by someone who did not write it.
It will be invoked during an incident by someone whose coffee has not yet entered the bloodstream.

Designing for repetition means accepting that data engineering is not a one-shot activity.

Data pipelines are recurring systems.

Recurring systems must behave safely under recurrence.

That sounds obvious, but many pipelines are written as if they will run once in a perfect universe.

We do not live in that universe.

We live in the universe where the source API changes pagination, the object store has temporary errors, and someone asks for a 14-month backfill during quarter close.

In this universe, idempotency is not elegance.

It is survival.

---

## 32. Final Thought

Idempotency is one of the most important concepts in data engineering because it changes the emotional texture of operations.

Without idempotency, every failure is suspicious.

Can we retry?
Did it already write data?
Did it duplicate records?
Did it advance the watermark?
Did it send the email?
Did it partially update Salesforce?
Did it corrupt the dashboard?
Did it make Finance believe revenue tripled?

With idempotency, the system becomes calmer.

Failures still happen.

But recovery is safer.

Retries become normal.
Backfills become manageable.
Restarts become less terrifying.
Partial failures become diagnosable.
Data products become more trustworthy.

The core idea is simple:

> Running the same operation once or many times should produce the same final result.

But that simple idea influences everything:

- table writes;
- file processing;
- API calls;
- orchestration;
- backfills;
- streaming;
- watermarks;
- lakehouse commits;
- data quality checks;
- Reverse ETL;
- ML features;
- healthcare pipelines;
- observability.

Idempotency is not a fancy distributed-systems word to sprinkle into architecture meetings.

It is a practical design principle.

It is what lets a data engineer look at a failed job, take a breath, and say:

> “Rerun it. It is safe.”

That sentence is worth a lot.

Sometimes it is worth an entire weekend.
