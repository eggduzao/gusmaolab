Title: The Sunday Materialization - Backfills Are Not Boring
Subtitle: How to Design Pipelines That Survive Reprocessing, History, and the Dangerous Sentence "Can We Just Rerun Everything?"
Date: 2026-09-20 07:00
Modified: 2026-09-20 07:00
Category: Sunday
Tags: data engineer, data platform engineer, data, data architecture, backfills, data pipelines, idempotency, reliability, orchestration
Slug: sunday-materialization-backfills-are-not-boring
Authors: Eduardo G Gusmao
Summary: A weekly educational topic/lecture/discussion on Data Engineering topics that we all experienced at least once (or will!)
Status: final
Lang: en
Template: topic
Cadence: Biweekly
Scope: Data Engineering, Industry, Data Challenges
Tone: Analytical, Educational, Non-Sensational
Canonical: https://www.gusmaolab.org/blog/sunday-materialization-backfills-are-not-boring/
Meta_description: Biweekly analysis of important Data Engineering concepts.
Meta_keywords: data concepts, topics, lectures, discussions, backfills, data pipelines, data reliability
Cover: images/covers/backfills-are-not-boring.png
Thumbnail: images/thumbnails/backfills-are-not-boring-thumb.png

# Backfills Are Not Boring: How to Design Pipelines That Survive Them

There is a sentence that appears innocent until you have lived inside a data platform for long enough:

> "Can we just backfill it?"

The word "just" is doing a lot of unpaid labor there.

Backfills sound simple.

A job processed data incorrectly.
A new column was added.
A business rule changed.
A bug affected three months of metrics.
A new model needs historical features.
A late vendor file arrived.
A source API changed.
A table migration is needed.
A regulatory report needs reproducible history.

So someone says:

> "Let's rerun the pipeline for the past year."

On a whiteboard, this is one arrow going backward in time.

In production, this is a controlled historical rewrite involving compute, storage, orchestration, data quality, idempotency, lineage, cost, stakeholder communication, and the emotional stability of everyone who depends on the output.

Backfills are not boring.

Backfills are where data platforms reveal whether they were designed as reliable systems or merely as pipelines that worked yesterday.

A normal pipeline run asks:

> Can we process today's data?

A backfill asks:

> Can we safely reprocess history without corrupting the present?

That is a much harder question.

And if the answer is "probably," congratulations: you have discovered a risk, not a plan.

---

## 1. What Is a Backfill?

A **backfill** is the process of reprocessing historical data to produce, repair, or update outputs for a past time range or historical scope.

Examples:

- recompute the last 90 days of revenue;
- rebuild customer features for the last two years;
- reload missing partitions from source files;
- regenerate a data mart after a business-rule change;
- repair a corrupted ingestion window;
- apply a new schema to historical data;
- migrate from one table format to another;
- rebuild aggregates after a deduplication fix;
- recompute historical ML training features;
- produce a regulatory snapshot for a past period.

A simple backfill may look like this:

```text
For each date from 2026-01-01 to 2026-03-31:
    read source data for date
    transform data
    validate output
    replace target partition for date
```

That sounds manageable.

But real backfills involve awkward questions:

- Is the source data still available?
- Is the old schema still readable?
- Has the transformation logic changed?
- Should we use today's code or historical code?
- Are downstream tables affected?
- Can we overwrite existing outputs?
- Will dashboards show partial backfill results?
- Can the job be safely retried?
- How much will it cost?
- Will this compete with production workloads?
- Who needs to know the numbers changed?
- What happens if day 43 of 180 fails?

Backfills are not just reruns.

They are historical surgery.

And surgery requires more than optimism and a large Spark cluster.

---

## 2. Why Backfills Happen

Backfills happen because data platforms are living systems.

Data changes.
Business rules change.
Bugs happen.
Sources arrive late.
Schemas evolve.
Models improve.
Products launch.
Regulators ask questions.
Executives request "the same metric as last quarter, but corrected."

Common reasons include the following.

### Bug fixes

A transformation was wrong.

Example:

```sql
-- Old incorrect logic
WHERE status != 'cancelled'

-- New corrected logic
WHERE status NOT IN ('cancelled', 'refunded')
```

Now historical metrics need to be recomputed.

### Late-arriving data

A vendor sends files late.

Or a source system delays records.

Or mobile events arrive after devices reconnect.

The platform needs to incorporate records that belong to past periods.

### Schema changes

A new source field becomes available.

Historical outputs need to include it.

### Business-rule changes

The company changes how a metric is defined.

Example:

> "Active customer" now means usage in the last 30 days, not 14 days.

Historical dashboards need consistency.

### New data products

A team wants a new feature table or mart, and it must cover past periods.

### Data correction

The source system corrected records retroactively.

The downstream platform must reflect those corrections.

### Migration

The platform changes storage format, table format, partition strategy, or transformation framework.

Historical tables may need to be rebuilt.

### Compliance or audit

A past reporting period must be reproduced or corrected.

Backfills are common because history is not as stable as we pretend.

Data history is less like stone and more like wet cement with stakeholders.

---

## 3. The Dangerous Backfill Mindset

The dangerous mindset is:

> "A backfill is just the same pipeline, but with old dates."

Sometimes that is true.

Often it is not.

Historical data may differ from current data.

Old partitions may have:

- different schemas;
- missing fields;
- different source semantics;
- different code systems;
- different time zones;
- different null behavior;
- different ID mappings;
- different file formats;
- corrupted files;
- incomplete data;
- duplicate records;
- deprecated business definitions.

A pipeline designed only for today may not understand yesterday.

Example:

```sql
SELECT
    customer_id,
    event_type,
    event_timestamp,
    product_area
FROM raw.events
WHERE event_date = DATE '2024-01-01';
```

But `product_area` did not exist in 2024.

Now what?

Options:

- set it to null;
- infer it from another field;
- join a historical mapping table;
- exclude old data;
- fail the backfill;
- create versioned logic by period.

None of these choices is automatic.

Historical compatibility is a design problem.

Backfills become risky when the pipeline assumes the past looks like the present.

The past rarely cooperates.

It has old schemas and bad posture.

---

## 4. Backfills Test Idempotency

A pipeline is **idempotent** if running it once or many times produces the same final result.

Backfills require idempotency.

If you backfill January twice, January should not contain duplicate rows.

If the job fails on day 17 and you restart it, days 1-16 should remain correct.

If a partition is replaced, it should be replaced deterministically.

Unsafe pattern:

```sql
INSERT INTO fact_orders
SELECT *
FROM staging_orders
WHERE order_date BETWEEN DATE '2026-01-01' AND DATE '2026-01-31';
```

If this runs twice, rows may duplicate.

Safer pattern:

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

Or, when the pipeline is partition-scoped:

```sql
INSERT OVERWRITE TABLE daily_orders
PARTITION (order_date = DATE '2026-01-17')
SELECT *
FROM staging_daily_orders
WHERE order_date = DATE '2026-01-17';
```

The core principle:

> A backfill should be restartable without making the data worse.

This is one of the most important properties of a reliable pipeline.

A pipeline that cannot survive reruns is not production-grade.

It is a one-time script with a calendar invite.

---

## 5. Backfills Test Determinism

Backfills also test whether transformations are deterministic.

A deterministic transformation produces the same output from the same input.

Example:

```sql
SELECT
    customer_id,
    COUNT(*) AS purchase_count
FROM purchases
GROUP BY customer_id;
```

Same input, same output.

Non-deterministic behavior appears when logic uses:

- current timestamp;
- random values;
- unstable ordering;
- current dimension values;
- external APIs;
- mutable reference tables;
- non-versioned lookup tables;
- model predictions from a changing model endpoint;
- code that depends on "today."

Example problem:

```sql
SELECT
    customer_id,
    CURRENT_DATE AS computed_date,
    CASE
        WHEN last_purchase_date >= CURRENT_DATE - INTERVAL '30 days'
        THEN true
        ELSE false
    END AS is_active
FROM customers;
```

If you run this today for data from 2024, it uses today's date.

That may be wrong.

For a historical backfill, you likely need:

```sql
SELECT
    customer_id,
    DATE '2024-06-30' AS as_of_date,
    CASE
        WHEN last_purchase_date >= DATE '2024-06-30' - INTERVAL '30 days'
        THEN true
        ELSE false
    END AS is_active
FROM customers;
```

The difference is huge.

Backfills often need an explicit **as-of date**.

Without it, the pipeline may accidentally compute historical data using present-day assumptions.

That is not a backfill.

That is time travel with poor supervision.

---

## 6. The As-Of Date Is Sacred

Many historical computations require an `as_of_date`.

The `as_of_date` answers:

> From which point in time are we pretending to observe the world?

This matters for:

- customer status;
- active user flags;
- churn risk features;
- account health;
- subscription state;
- eligibility;
- cohort membership;
- clinical phenotype status;
- financial balances;
- slowly changing dimensions.

Example:

```sql
SELECT
    customer_id,
    plan_type,
    valid_from,
    valid_to
FROM dim_customer_plan
WHERE valid_from <= DATE '2026-01-31'
  AND (
      valid_to > DATE '2026-01-31'
      OR valid_to IS NULL
  );
```

This gives the customer plan as of January 31, 2026.

If instead you join to the current customer plan table, you may use today's plan for historical events.

That breaks history.

For backfills, this question is everywhere:

> Are we using the version of the data that was true then, or the version we know now?

Both may be valid for different use cases.

### Point-in-time truth

What did we know at the time?

Useful for:

- ML training without leakage;
- historical dashboards as seen then;
- operational replay;
- audit of past decisions.

### Corrected historical truth

What do we now believe was true for that past date?

Useful for:

- corrected financial reporting;
- late-arriving facts;
- revised business metrics;
- regulatory corrections;
- cleaned analytical history.

These are not the same.

Backfill design must say which truth it is producing.

Data has philosophy. Annoyingly, it also has deadlines.

---

## 7. Backfills and Late-Arriving Data

Late-arriving data is one of the most common reasons for backfills.

Suppose events are generated on January 10 but arrive on January 12.

Should the January 10 partition be updated?

Usually yes.

But how?

A naive daily pipeline processes only records received that day.

That may place late events in the wrong business date.

Better:

```text
event_time:
    when the event happened

ingestion_time:
    when the platform received it
```

Both matter.

A pipeline may use `ingestion_time` to find new records, but write them into partitions by `event_date`.

Example:

```sql
WITH new_records AS (
    SELECT *
    FROM raw_events
    WHERE ingestion_time > :last_successful_watermark
),

affected_dates AS (
    SELECT DISTINCT event_date
    FROM new_records
)

-- Recompute or merge affected event_date partitions.
```

This handles late events by identifying which historical partitions changed.

A common pattern is a rolling backfill window.

Example:

```text
Every daily run:
    process today
    also reprocess the previous 7 days
```

This captures late-arriving records without requiring a full historical backfill every time.

But the window must match the source behavior.

If data can arrive 30 days late, a 7-day window may not be enough.

If data almost never arrives late, a 30-day window may be wasteful.

Late-arriving data is not a technical detail.

It is a contract with reality.

Reality sometimes uploads files on Tuesday.

---

## 8. Backfills and Slowly Changing Dimensions

Backfills become tricky when facts join to dimensions.

Suppose you have an orders table:

```text
fact_orders
- order_id
- customer_id
- order_date
- amount
```

And a customer dimension:

```text
dim_customer
- customer_id
- customer_segment
- region
- updated_at
```

If you backfill historical orders, which customer segment should you use?

The current segment?

Or the segment at the time of the order?

If a customer moved from `small_business` to `enterprise`, historical reports may change depending on the chosen logic.

A slowly changing dimension table may preserve history:

```text
dim_customer_scd
- customer_id
- customer_segment
- region
- valid_from
- valid_to
- is_current
```

Then the backfill can join point-in-time:

```sql
SELECT
    o.order_id,
    o.order_date,
    o.customer_id,
    d.customer_segment,
    o.amount
FROM fact_orders AS o
JOIN dim_customer_scd AS d
    ON o.customer_id = d.customer_id
   AND o.order_date >= d.valid_from
   AND (
       o.order_date < d.valid_to
       OR d.valid_to IS NULL
   );
```

This is more correct for historical analysis.

But it depends on having historical dimension data.

If your dimension table only stores current values, you cannot reconstruct the past reliably.

Backfills expose whether the platform preserved enough history.

If not, the answer may be:

> We can rebuild the table, but not the historical truth.

Painful. Better than lying.

---

## 9. Backfills and ML Feature Engineering

Backfills are central to machine learning.

When training a model, we often need historical features.

Example:

- number of purchases in the previous 30 days;
- average session duration before prediction date;
- support tickets before churn date;
- lab values before diagnosis date;
- claims before enrollment date;
- account usage before renewal date.

The critical phrase is **before prediction date**.

Backfilled features must avoid leakage.

Bad feature:

```sql
SELECT
    customer_id,
    COUNT(*) AS total_purchases
FROM purchases
GROUP BY customer_id;
```

This may count purchases that happened after the prediction point.

Better:

```sql
SELECT
    customer_id,
    prediction_date,
    COUNT(*) AS purchases_30d
FROM purchases
WHERE purchase_date < prediction_date
  AND purchase_date >= prediction_date - INTERVAL '30 days'
GROUP BY customer_id, prediction_date;
```

Historical feature backfills must be point-in-time correct.

Otherwise, the model learns from the future.

Models love cheating.

They will not confess.

Backfills for ML should track:

- feature computation date;
- prediction/entity date;
- source data availability;
- label windows;
- leakage boundaries;
- feature version;
- training dataset version;
- code version;
- data snapshot.

An ML backfill is not merely historical transformation.

It is the construction of a reproducible training reality.

That phrase is dramatic, but correct.

---

## 10. Backfills and Data Contracts

Data contracts define expectations between producers and consumers.

Backfills can violate those expectations if not communicated.

For example, a data contract might say:

```yaml
dataset: daily_revenue
freshness:
  expected_by: "07:00"
schema:
  revenue_date: date
  total_revenue: decimal
quality:
  total_revenue:
    min: 0
```

A backfill may preserve the schema and quality checks, but change historical values.

Consumers need to know.

If a dashboard's January revenue changes in September, stakeholders may ask:

- Why did the number change?
- Which logic changed?
- Is the old number wrong?
- Which reports are affected?
- Should we update downstream exports?
- Is this a correction or a restatement?
- Can we compare old and new versions?

Backfills should have a communication contract.

For important datasets, track:

- reason for backfill;
- affected date range;
- affected tables;
- logic/version change;
- expected impact;
- validation result;
- owner;
- start/end time;
- downstream consumers notified;
- rollback plan.

A backfill is a data event.

Treat it like one.

If a metric changes history silently, users lose trust.

And once trust is gone, every dashboard becomes a suspect.

---

## 11. Backfills Need Scope

A good backfill starts with scope.

Bad request:

> "Backfill customers."

Better request:

> "Backfill `mart.customer_health_daily` from 2026-01-01 to 2026-03-31 using logic version 2.3.1, replacing existing partitions, validating row counts and churn segment distributions, without triggering reverse ETL."

That is a plan.

Backfill scope should define:

- source datasets;
- target datasets;
- date range or entity range;
- transformation version;
- write mode;
- validation criteria;
- downstream dependencies;
- operational isolation;
- expected cost;
- owner;
- rollback strategy;
- communication plan.

A scope document can be short.

But it should exist.

Example:

```yaml
backfill:
  name: customer_health_v2_backfill
  reason: "Fix churn-risk threshold bug"
  owner: data-platform
  target_table: mart.customer_health_daily
  date_range:
    start: 2026-01-01
    end: 2026-03-31
  write_mode: replace_partitions
  logic_version: v2.3.1
  downstream:
    pause_reverse_etl: true
    refresh_dashboards_after_completion: true
  validation:
    - row_count_by_day
    - customer_id_uniqueness_by_day
    - churn_segment_distribution
  rollback:
    restore_previous_snapshot: true
```

This is not bureaucracy.

This is how you avoid accidentally rewriting history with the wrong code and a cheerful Slack message.

---

## 12. Backfills Need Isolation

A backfill should not casually interfere with production.

Backfills can consume heavy compute, rewrite tables, invalidate caches, and update downstream models.

Isolation strategies include:

- separate compute cluster/warehouse;
- separate queue or resource pool;
- staging tables;
- temporary output locations;
- table snapshots;
- feature branches/environments;
- disabled downstream triggers;
- explicit promotion step;
- limited date partitions;
- off-peak scheduling;
- concurrency controls.

Unsafe:

```text
Production pipeline and backfill both write to the same table at the same time.
```

Better:

```text
Backfill writes to staging table
    ↓
Validation
    ↓
Atomic partition replacement
    ↓
Downstream refresh
```

Or:

```text
Backfill uses isolated compute
Production dashboards continue reading current table
After validation, promote new snapshot
```

The goal is:

> Users should not see half-backfilled history unless you intentionally expose it.

Partial backfills are dangerous.

They create mixed logic periods.

Example:

- January uses new logic;
- February uses old logic;
- March is halfway rebuilt;
- dashboard says trend improved;
- everyone learns nothing except pain.

A backfill should have a boundary between work-in-progress and published truth.

---

## 13. Backfills Need Checkpoints

Large backfills may run for hours or days.

They need checkpoints.

If a 180-day backfill fails on day 137, you do not want to restart everything.

A checkpoint records progress.

Example:

```sql
CREATE TABLE ops.backfill_progress (
    backfill_id STRING,
    target_table STRING,
    partition_key STRING,
    partition_value STRING,
    status STRING,
    started_at TIMESTAMP,
    finished_at TIMESTAMP,
    row_count BIGINT,
    validation_status STRING,
    error_message STRING
);
```

Conceptual flow:

```text
For each partition:
    if partition status is success:
        skip
    else:
        process partition
        validate partition
        publish partition
        mark success
```

This makes the backfill resumable.

It also makes progress visible.

Without progress tracking, backfills become anxious guessing.

Someone asks:

> "How far along is it?"

And the answer is:

> "The logs are still moving."

That is not observability.

That is campfire watching.

---

## 14. Backfills Need Validation

A backfill without validation is just a historical overwrite with confidence.

Validation should happen before publishing when possible.

Useful validation checks include:

- row count by partition;
- primary-key uniqueness;
- null rates;
- value ranges;
- referential integrity;
- distribution comparison;
- source-to-target reconciliation;
- metric comparison before/after;
- file count and size;
- schema compatibility;
- business rule checks;
- downstream sample queries.

Example validation SQL:

```sql
-- Check uniqueness by business key.
SELECT
    order_date,
    COUNT(*) AS n_rows,
    COUNT(DISTINCT order_id) AS n_distinct_orders
FROM staging.orders_backfill
GROUP BY order_date
HAVING COUNT(*) != COUNT(DISTINCT order_id);
```

Example metric comparison:

```sql
SELECT
    old.revenue_date,
    old.total_revenue AS old_revenue,
    new.total_revenue AS new_revenue,
    new.total_revenue - old.total_revenue AS difference
FROM mart.daily_revenue_old_snapshot AS old
JOIN staging.daily_revenue_backfill AS new
    ON old.revenue_date = new.revenue_date
WHERE ABS(new.total_revenue - old.total_revenue) > 1000;
```

A difference may be expected.

But it should be explained.

Validation is not only pass/fail.

It is evidence.

A good backfill leaves behind proof that it did what it intended.

---

## 15. Backfills Need Observability

Backfills should be observable like production pipelines.

Track:

- partitions processed;
- partitions remaining;
- runtime per partition;
- input rows;
- output rows;
- validation results;
- failed partitions;
- retry counts;
- compute cost;
- bytes scanned;
- files written;
- table snapshots created;
- downstream assets affected;
- current status;
- owner.

Example run summary:

```text
Backfill: customer_health_v2_backfill
Target: mart.customer_health_daily
Range: 2026-01-01 to 2026-03-31

Partitions:
    total: 90
    succeeded: 87
    failed: 2
    running: 1

Rows:
    input: 184,300,221
    output: 91,442,120

Validation:
    uniqueness: passed
    null thresholds: passed
    segment distribution: warning

Cost:
    bytes scanned: 12.4 TB
    compute hours: 41.2

Status:
    paused before publish due to distribution warning
```

This tells a useful story.

Compare that with:

> "The job is still running."

A data platform should not make humans infer reality from spinning logs.

Logs are not a user interface.

They are a distress signal with timestamps.

---

## 16. Backfills Need Write Strategy

A backfill must define how it writes output.

Common strategies include:

### Append

Usually dangerous unless records are immutable and deduplicated.

```text
Append new historical records.
```

Useful for:

- event logs with stable event IDs;
- append-only facts;
- immutable source corrections handled as new records.

Risk:

- duplicates;
- mixed old/new logic;
- hard cleanup.

### Merge/upsert

Update existing records and insert missing ones by key.

```sql
MERGE INTO target AS t
USING source AS s
ON t.record_id = s.record_id
WHEN MATCHED THEN UPDATE SET *
WHEN NOT MATCHED THEN INSERT *;
```

Useful for:

- mutable facts;
- dimensions;
- corrected records;
- CDC-style backfills.

Risk:

- wrong merge key;
- duplicate source keys;
- expensive updates;
- non-deterministic matches.

### Partition overwrite

Replace full partitions.

```sql
INSERT OVERWRITE TABLE target
PARTITION (event_date = DATE '2026-01-01')
SELECT *
FROM staging
WHERE event_date = DATE '2026-01-01';
```

Useful for:

- daily/hourly/monthly fact tables;
- reproducible partitions;
- deterministic transformations.

Risk:

- partial delete/insert if not atomic;
- wrong partition scope;
- missing late records if source selection incomplete.

### Snapshot replacement

Build a new table version and promote it.

```text
Build target_v2
Validate target_v2
Swap view or metadata pointer
```

Useful for:

- large semantic changes;
- major migrations;
- high-risk restatements;
- full-table rebuilds.

Risk:

- storage cost;
- migration complexity;
- downstream compatibility.

The write strategy should match the table's identity model and operational risk.

Do not let the write mode be an accidental default.

Defaults are where incidents hide wearing casual clothes.

---

## 17. Backfills and Table Formats

Lakehouse table formats such as Iceberg, Delta Lake, and Hudi can help backfills.

They may provide:

- atomic commits;
- snapshot isolation;
- time travel;
- rollback;
- MERGE support;
- partition replacement;
- delete/update operations;
- schema evolution;
- incremental reads;
- metadata tracking.

This is valuable.

But table formats do not design the backfill for you.

You still need:

- correct keys;
- correct partition scope;
- deterministic transformations;
- validation;
- maintenance;
- compaction;
- snapshot retention;
- downstream communication;
- rollback strategy.

A table format may let you restore a previous snapshot.

That is wonderful.

But rollback still has questions:

- Were downstream tables already refreshed?
- Did reverse ETL already sync data out?
- Did dashboards cache new results?
- Did ML features get rebuilt?
- Did users export reports?
- Did a compliance file get sent?

A table rollback is not always a business rollback.

This is one reason backfills should be treated as coordinated platform events, not isolated table rewrites.

The table is not the whole ecosystem.

It is just the part that stores evidence.

---

## 18. Backfills and Downstream Dependencies

A backfill rarely affects only one table.

If you backfill a raw or intermediate table, downstream assets may need rebuilding.

Example:

```text
raw.orders
    ↓
clean.orders
    ↓
mart.daily_revenue
    ↓
finance_dashboard
    ↓
executive_report
```

If `raw.orders` changes historically, should all downstream tables be backfilled?

Probably.

But maybe not all at once.

You need lineage.

Lineage answers:

- Which tables depend on this?
- Which dashboards depend on this?
- Which ML features depend on this?
- Which reverse ETL syncs depend on this?
- Which reports depend on this?
- Which consumers should be notified?
- Which rebuild order is required?

Without lineage, backfills become detective work.

With lineage, they become planned propagation.

Example propagation plan:

```text
1. Backfill clean.orders
2. Validate clean.orders
3. Backfill mart.daily_revenue
4. Compare old vs new revenue
5. Refresh finance_dashboard extract
6. Notify Finance of corrected dates
7. Resume downstream scheduled jobs
```

A backfill is often a graph operation.

Not a single job.

The DAG matters.

And if nobody knows the DAG, the DAG will explain itself through failure.

---

## 19. Backfills and Reverse ETL

Backfills can be dangerous when downstream activation exists.

Suppose a table feeds Salesforce, HubSpot, Zendesk, Braze, or another SaaS tool.

A historical backfill may produce many changed records.

If Reverse ETL is still active, it may sync all those changes.

That may trigger:

- sales tasks;
- customer emails;
- campaign enrollment;
- support priority changes;
- account health changes;
- lifecycle stage updates;
- Slack alerts;
- workflow automations.

Sometimes this is desired.

Often it is not.

A backfill plan should explicitly say:

- Should Reverse ETL be paused?
- Should only current records sync?
- Should historical changes be ignored?
- Should sync resume after validation?
- Should downstream fields be updated gradually?
- Are automations triggered by field updates?
- Is there an approval gate before activation?

Example:

```yaml
downstream_activation:
  reverse_etl_syncs:
    - salesforce_account_health
    - hubspot_lifecycle_stage
  action: pause_during_backfill
  resume_after_validation: true
  require_business_approval: true
```

Backfills should not accidentally become business actions.

A historical repair should not wake up Sales with 80,000 new tasks.

Unless Sales asked for that.

And even then, ask twice.

---

## 20. Backfills and Dashboards

Dashboards can mislead during backfills.

If users see partially backfilled data, trends may look strange.

Example:

- January and February use old logic;
- March is backfilled with new logic;
- April onward uses old logic;
- dashboard shows a sudden March spike;
- business team writes a narrative around a data artifact.

This is how dashboards become fiction with filters.

Strategies:

### Hide work-in-progress outputs

Backfill into staging first.

Promote only after completion.

### Mark data as under maintenance

Show a banner or metadata status.

### Use versioned datasets

Keep old and new versions separate until approved.

### Refresh dashboards only after publishing

Avoid partial exposure.

### Communicate expected metric changes

Tell stakeholders which periods will change and why.

A dashboard is not just a query result.

It is a decision surface.

If a backfill changes historical data, the decision surface changes too.

Handle that deliberately.

---

## 21. Backfills and Cost

Backfills can be expensive.

They may scan and rewrite large historical ranges.

Cost drivers include:

- data volume scanned;
- compute hours;
- shuffle size;
- output data written;
- object-store requests;
- table metadata growth;
- compaction after writes;
- downstream rebuilds;
- cache invalidation;
- duplicate temporary storage;
- retries after failure.

Before a large backfill, estimate cost.

You do not need perfect accuracy.

You need enough to avoid surprise.

Questions:

- How many partitions?
- How much input data?
- How much output data?
- How long does one partition take?
- Can partitions run in parallel?
- What compute size is needed?
- What is the expected total runtime?
- What is the expected cloud cost?
- Will compaction be needed afterward?
- Will downstream tables also rebuild?

Example estimate:

```text
Sample partition:
    date: 2026-01-01
    input: 120 GB
    runtime: 18 minutes
    compute: medium cluster

Full range:
    90 days
    estimated input: 10.8 TB
    estimated runtime serial: 27 hours
    estimated runtime with 6-way parallelism: 4.5-6 hours
    estimated post-compaction: 1.5 hours
```

This kind of estimate prevents magical thinking.

Cloud platforms are elastic.

Budgets are not infinitely elastic.

The cloud will happily process your mistake at scale.

Very professional. Very expensive.

---

## 22. Backfills and Parallelism

Backfills often tempt engineers to parallelize aggressively.

If one date takes 20 minutes, why not run 100 dates at once?

Maybe you can.

But parallelism has constraints:

- source system limits;
- warehouse concurrency;
- object-store request rates;
- table write conflicts;
- partition locks;
- catalog pressure;
- cluster capacity;
- downstream dependencies;
- cost spikes;
- small file creation;
- monitoring complexity.

Safe parallelism usually requires independent partitions.

Example:

```text
Safe-ish:
    process one date partition per task
    each task writes only its own date
```

Risky:

```text
Many tasks merge into the same table partitions simultaneously
```

A good backfill framework controls concurrency.

Example:

```text
max_parallel_partitions = 8
retry_failed_partitions = true
write_conflict_policy = fail_and_retry
```

Parallelism is useful.

Unbounded parallelism is a denial-of-service attack against your own platform, but with YAML.

---

## 23. Backfills and Source Systems

Sometimes backfills require reading from source systems.

Be careful.

Operational source systems may not enjoy historical extraction at scale.

Risks:

- API rate limits;
- database load;
- production performance impact;
- pagination bugs;
- historical retention gaps;
- changed schemas;
- deleted records;
- archived data;
- vendor costs;
- source-side throttling.

A backfill should avoid hammering production systems if possible.

Better patterns:

- backfill from raw immutable storage;
- use source snapshots;
- use CDC logs;
- use archived exports;
- use replicas;
- use read-only analytical copies;
- coordinate with source-system owners.

If your platform stores raw immutable inputs, backfills become much easier.

Example:

```text
source API
    ↓
raw immutable landing zone
    ↓
staging
    ↓
curated tables
```

Then the backfill reads from raw storage, not the live API.

This is one of the strongest arguments for keeping raw historical data.

Raw storage is not clutter.

It is insurance.

As with insurance, you hope you do not need it.

Then one day you really need it.

---

## 24. Backfills and Raw Data Retention

Backfills depend on data availability.

If raw data is deleted too early, historical reprocessing may be impossible.

Retention policies should consider:

- regulatory requirements;
- storage cost;
- reproducibility;
- business correction windows;
- ML training needs;
- late-arriving data;
- audit requirements;
- privacy deletion obligations.

There is a tension.

Keeping raw data helps backfills.

Keeping sensitive data forever is risky and may be illegal or inappropriate.

The platform needs explicit retention classes.

Example:

```text
Raw public data:
    retain indefinitely

Raw operational logs:
    retain 180 days

Raw sensitive clinical data:
    retain according to governance policy

Curated analytical snapshots:
    retain release versions

Temporary staging:
    retain 7-30 days

Backfill outputs:
    retain until validation + rollback window expires
```

The answer is not "keep everything forever."

The answer is "keep what is justified, governed, and useful."

Backfills are easier with history.

Governance decides how much history you are allowed to keep.

---

## 25. Backfills and Schema Evolution

Historical data often has old schemas.

Example:

```text
2024 events:
    user_id
    event_type
    timestamp

2025 events:
    user_id
    event_type
    event_timestamp
    device_type

2026 events:
    user_id
    account_id
    event_type
    event_timestamp
    device_type
    product_area
```

A backfill over 2024-2026 must handle schema differences.

Strategies:

### Schema normalization

Map old fields into a canonical schema.

```sql
SELECT
    user_id,
    NULL AS account_id,
    event_type,
    timestamp AS event_timestamp,
    NULL AS device_type,
    NULL AS product_area
FROM raw_events_2024;
```

### Version-specific parsers

Use different parsing logic by source version.

```text
if schema_version == "v1":
    parse_v1()
elif schema_version == "v2":
    parse_v2()
```

### Contract-based ingestion

Validate and evolve schemas explicitly.

### Backfill only compatible periods

Sometimes older periods cannot support the new output fully.

This should be documented.

Do not pretend historical fields exist if they do not.

Null is better than fictional precision.

A null says "unknown."

A made-up value says "future incident."

---

## 26. Backfills and Code Versioning

Which code should a backfill use?

There are two common approaches.

### Use current corrected code

This creates a consistent restated history under today's logic.

Good for:

- corrected metrics;
- updated business definitions;
- unified analytical history;
- data mart rebuilds.

### Use historical code versions

This reproduces what the system would have produced at the time.

Good for:

- audit;
- incident investigation;
- ML experiment reproducibility;
- regulatory reconstruction;
- comparing old and new logic.

A robust platform tracks:

- code version;
- transformation version;
- dependency versions;
- source snapshot;
- table snapshot;
- run ID;
- configuration.

Example metadata:

```yaml
backfill_run:
  id: bf_2026_09_customer_health_v2
  code_version: git:8f31ac2
  transformation_version: customer_health_v2.3.1
  source_snapshot: raw_events_snapshot_2026_09_19
  target_table: mart.customer_health_daily
  mode: corrected_history
```

Without versioning, a backfill may be hard to reproduce.

And if nobody can reproduce it, nobody can fully trust it.

Reproducibility is not an academic luxury.

It is production self-defense.

---

## 27. Backfills and Feature Flags

Sometimes backfills need controlled rollout.

A new logic version may be computed but not immediately exposed.

Feature flags or versioned views can help.

Example:

```text
mart.customer_health_v1
mart.customer_health_v2

View:
    mart.customer_health_current
```

Initially:

```sql
CREATE OR REPLACE VIEW mart.customer_health_current AS
SELECT *
FROM mart.customer_health_v1;
```

After validation:

```sql
CREATE OR REPLACE VIEW mart.customer_health_current AS
SELECT *
FROM mart.customer_health_v2;
```

This allows:

- building new history separately;
- validating before exposure;
- comparing old and new;
- switching consumers atomically;
- rolling back by restoring the view.

This pattern is useful for high-risk changes.

It treats data products more like software releases.

That is a good thing.

Data releases need release engineering too.

Otherwise, we are just flinging tables over a wall.

A noble tradition. Not a reliable one.

---

## 28. Backfills and Branching

Some modern table formats and catalogs support branching, versioning, or isolated snapshots.

Even without native branching, you can simulate it with staging tables.

Conceptually:

```text
main table:
    mart.daily_revenue

backfill branch:
    mart.daily_revenue_backfill_candidate
```

The branch is built and validated.

Then promoted.

Benefits:

- production remains stable;
- validation is easier;
- old/new comparison is explicit;
- rollback is simpler;
- users do not see partial results.

This resembles software development:

```text
feature branch
    ↓
tests
    ↓
review
    ↓
merge to main
```

Data platforms increasingly need this style.

Not for every tiny table.

But for important data products, historical rewrites should be staged and reviewed.

Backfilling production directly is sometimes fine.

But for critical datasets, staging is safer.

Production is not a sandbox.

Production is where dashboards have consequences.

---

## 29. Backfills and Orchestration

A good orchestrator helps backfills.

But only if the DAG is designed for it.

Bad DAG design:

```text
daily_pipeline()
    always processes today
```

Better:

```text
daily_pipeline(processing_date)
    processes explicit date
```

Parameterization is essential.

A backfillable pipeline should accept:

- processing date;
- start date;
- end date;
- source version;
- target table;
- write mode;
- dry-run flag;
- validation mode;
- downstream trigger flag.

Example conceptual CLI:

```bash
python -m pipelines.customer_health \
    --start-date 2026-01-01 \
    --end-date 2026-03-31 \
    --target-table mart.customer_health_daily \
    --write-mode replace-partitions \
    --validate \
    --disable-reverse-etl
```

This is much better than editing code to change dates.

A pipeline that requires code edits for backfills is asking for mistakes.

Dates should be parameters.

Modes should be explicit.

Backfills should be first-class operations, not improvised rituals.

---

## 30. A Small Python Sketch: Backfill Plan Objects

Below is a small teaching sketch showing how a backfill can be represented as an explicit plan.

```python
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from enum import StrEnum
from typing import Iterator


class WriteMode(StrEnum):
    """Write modes supported by a backfill."""

    APPEND = "append"
    MERGE = "merge"
    REPLACE_PARTITIONS = "replace_partitions"
    BUILD_AND_SWAP = "build_and_swap"


@dataclass(frozen=True)
class BackfillPlan:
    """Explicit plan for a historical data backfill."""

    backfill_id: str
    target_table: str
    start_date: date
    end_date: date
    write_mode: WriteMode
    owner_team: str
    disable_downstream_activation: bool = True


def iter_backfill_dates(plan: BackfillPlan) -> Iterator[date]:
    """Yield each processing date included in a backfill plan.

    Parameters
    ----------
    plan
        Backfill plan containing the inclusive date range.

    Yields
    ------
    date
        One processing date at a time.
    """
    current_date = plan.start_date

    while current_date <= plan.end_date:
        yield current_date
        current_date += timedelta(days=1)


def validate_backfill_plan(plan: BackfillPlan) -> None:
    """Validate basic safety properties of a backfill plan.

    Parameters
    ----------
    plan
        Backfill plan to validate.

    Raises
    ------
    ValueError
        If the plan is unsafe or malformed.
    """
    if plan.end_date < plan.start_date:
        raise ValueError("Backfill end_date cannot be before start_date.")

    if not plan.backfill_id:
        raise ValueError("Backfill plan must include a backfill_id.")

    if plan.write_mode == WriteMode.APPEND:
        raise ValueError(
            "APPEND backfills require additional duplicate-safety checks."
        )
```

The code is simple.

The idea is important:

> Backfills should be explicit, validated operations with metadata, not informal reruns.

A backfill plan is a contract with future you.

Future you appreciates paperwork only when it prevents disaster.

This is one of those times.

---

## 31. Backfills and Dry Runs

Dry runs are extremely useful.

A dry run computes what would happen without publishing final outputs.

A dry run may:

- list affected partitions;
- estimate input size;
- count expected rows;
- validate source availability;
- compute sample outputs;
- compare old/new metrics;
- estimate cost;
- detect schema issues;
- produce a backfill report.

Example dry-run output:

```text
Backfill dry run: daily_revenue_v3
Range: 2026-01-01 to 2026-03-31

Affected partitions: 90
Missing source partitions: 0
Estimated input: 4.2 TB
Estimated output: 28 GB

Metric comparison sample:
    average revenue difference: +1.8%
    max daily difference: +12.4%
    days with >5% difference: 7

Recommendation:
    proceed with validation gate
```

A dry run gives teams confidence before writing.

It also reveals surprises early.

Backfills should surprise as little as possible.

They are already powerful enough.

---

## 32. Backfills and Rollback

Every serious backfill needs a rollback story.

Rollback options include:

- restore previous table snapshot;
- restore previous partitions;
- switch view back to old table;
- keep old and new versions side by side;
- use backup table;
- replay previous release;
- reverse merge changes;
- disable downstream outputs.

Best rollback depends on the write strategy.

If you use a table format with time travel, rollback may be:

```sql
RESTORE TABLE mart.daily_revenue TO VERSION AS OF 12345;
```

Syntax depends on platform.

If using versioned views:

```sql
CREATE OR REPLACE VIEW mart.daily_revenue_current AS
SELECT *
FROM mart.daily_revenue_v1;
```

If using partition replacement, keep old partition snapshots until validation passes.

Important:

> Rollback should be tested before you need it.

A rollback plan that exists only in someone's confidence is not a rollback plan.

It is a mood.

Moods do not restore tables.

---

## 33. Backfills and Communication

Technical correctness is not enough.

If a backfill changes business-facing numbers, communicate.

Tell stakeholders:

- what changed;
- why it changed;
- which dates are affected;
- which metrics are affected;
- whether old values were wrong;
- when new values will be available;
- whether reports need refreshing;
- who owns questions;
- whether downstream tools are paused;
- whether action is required.

Example message:

```text
We are backfilling mart.daily_revenue for 2026-01-01 to 2026-03-31 to correct refund handling logic.

Expected impact:
    total revenue for affected dates may decrease by 0.5%-2.0%.
    gross revenue is unchanged.
    net revenue and refund-adjusted revenue are affected.

Timeline:
    backfill starts 2026-09-20 20:00.
    dashboards will refresh after validation.
    reverse ETL syncs are paused during the backfill.

Owner:
    finance-data-platform
```

This is clear.

Compare with:

> "Some revenue numbers may change."

No.

Do not release mystery.

Stakeholders tolerate corrections much better when they understand them.

Surprise is the enemy of trust.

---

## 34. Backfills in Healthcare and Biotech

Healthcare and biotech make backfills especially serious.

Data may support:

- patient cohorts;
- clinical phenotypes;
- quality indicators;
- claims analytics;
- registry reporting;
- genomic variant annotation;
- sample tracking;
- laboratory workflows;
- ML models;
- research publications;
- regulatory submissions.

Backfills can change scientific or clinical conclusions.

Examples:

### EHR phenotype backfill

A diabetes phenotype definition changes.

Backfilling historical patients may change cohort membership.

Questions:

- Which ICD codes changed?
- Were lab thresholds updated?
- Are medication rules included?
- Are dates point-in-time correct?
- Are exclusion criteria applied historically?
- Which studies used the old definition?

### Claims backfill

A payer sends corrected claims files.

Questions:

- Are old claims replaced or versioned?
- Are financial reports restated?
- Are provider-level aggregates affected?
- Are downstream dashboards refreshed?

### Genomics annotation backfill

A variant annotation database updates.

Questions:

- Which reference genome?
- Which annotation version?
- Which samples are affected?
- Are old annotations preserved?
- Are research outputs reproducible?
- Are model features rebuilt?

In these domains, backfills need strong metadata:

- source version;
- pipeline version;
- code version;
- reference database version;
- cohort version;
- release ID;
- audit trail;
- validation report.

A biomedical backfill is not just data repair.

It may be scientific provenance.

And provenance is not optional unless you enjoy irreproducible arguments with very smart people.

---

## 35. Common Anti-Patterns

### Anti-pattern 1: Blind append backfills

Appending historical data without deduplication or partition replacement.

This creates duplicates.

### Anti-pattern 2: Backfilling production directly

Writing to production tables before validation.

This exposes partial or wrong outputs.

### Anti-pattern 3: No checkpointing

A failure forces the entire backfill to restart.

Painful and wasteful.

### Anti-pattern 4: No downstream awareness

Changing upstream history without rebuilding or notifying downstream consumers.

This creates inconsistent data products.

### Anti-pattern 5: Using current dimensions for historical facts

This breaks point-in-time correctness.

### Anti-pattern 6: No rollback plan

If the backfill is wrong, recovery becomes improvisation.

Improvisation is good in jazz. Less good in production data.

### Anti-pattern 7: No cost estimate

The backfill finishes successfully and the cloud bill files a complaint.

### Anti-pattern 8: Triggering Reverse ETL accidentally

Historical recomputation causes operational actions.

This can be very bad.

### Anti-pattern 9: No old/new comparison

You changed history but cannot explain how.

That is how trust erodes.

### Anti-pattern 10: Treating backfills as rare exceptions

They are not rare.

Design for them.

---

## 36. What Good Looks Like

A backfill-ready pipeline usually has the following traits.

### Explicit time parameters

The pipeline can process any date or date range.

### Idempotent writes

Reruns do not duplicate or corrupt data.

### Deterministic logic

Historical outputs are reproducible from known inputs.

### Staging before publish

Backfill outputs can be validated before exposure.

### Partition-aware processing

The pipeline can replace or rebuild scoped partitions.

### Checkpointing

Long runs can resume after failure.

### Validation

The platform checks row counts, uniqueness, distributions, and business metrics.

### Observability

Progress, cost, failures, and affected assets are visible.

### Lineage awareness

Downstream dependencies are known.

### Rollback

Previous versions can be restored.

### Communication

Stakeholders know what changed and why.

### Governance

Sensitive data, auditability, and retention are handled correctly.

In short:

> A backfill-ready pipeline treats history as something that can be safely rebuilt, not something that must never be touched because everyone is afraid.

That is maturity.

---

## 37. A Practical Backfill Checklist

Before running a backfill, ask:

1. Why is this backfill needed?
2. What table or data product is affected?
3. What date/entity range is in scope?
4. Which code version will be used?
5. Which source data version will be used?
6. Is this corrected history or point-in-time reproduction?
7. Is the source data still available?
8. Are old schemas compatible?
9. What write mode will be used?
10. Is the operation idempotent?
11. Can the backfill resume after failure?
12. Where will temporary outputs be written?
13. What validation checks must pass?
14. What metrics should be compared before and after?
15. Which downstream tables depend on this output?
16. Should downstream jobs be paused?
17. Should Reverse ETL be paused?
18. Will dashboards show partial results?
19. What compute will be used?
20. What is the estimated cost?
21. What is the expected runtime?
22. What is the rollback plan?
23. Who approves publishing?
24. Who must be notified?
25. Where will the backfill report be stored?

This checklist may feel long.

It is shorter than an incident review.

---

## 38. Backfills Are a Design Requirement, Not an Exception

The deeper lesson is this:

> Backfills should be designed into the pipeline from the beginning.

A production pipeline should not only answer:

- Can it process today?
- Can it run on schedule?
- Can it alert on failure?

It should also answer:

- Can it reprocess history?
- Can it rerun safely?
- Can it repair missing data?
- Can it handle schema evolution?
- Can it rebuild outputs under new logic?
- Can it validate before publishing?
- Can it avoid corrupting downstream systems?
- Can it explain what changed?

This is part of data platform reliability.

Backfills are not weird.

Backfills are normal.

The abnormal thing is pretending history never needs to be touched.

That is a lovely fantasy.

Unfortunately, data platforms live in reality, where bugs, late data, and changed business definitions gather regularly like a small committee.

---

## 39. The Real Difference Between Fragile and Mature Pipelines

A fragile pipeline works when everything goes right.

A mature pipeline survives when something went wrong yesterday and must be corrected today.

Fragile pipeline:

```text
Processes today's data.
Fails if rerun.
Duplicates if retried.
Cannot rebuild old partitions.
No source snapshots.
No validation.
No rollback.
No lineage.
```

Mature pipeline:

```text
Processes explicit dates.
Writes idempotently.
Stages before publishing.
Tracks progress.
Validates outputs.
Supports rollback.
Knows downstream dependencies.
Documents changes.
```

The difference is not glamour.

It is engineering discipline.

Most users do not see this discipline directly.

They see the result:

- fewer incidents;
- more reliable metrics;
- safer corrections;
- better reproducibility;
- less fear around historical repair;
- more trust in the platform.

That is the quiet success of good data engineering.

Nobody applauds the backfill framework when it works.

They simply do not lose their weekend.

That is applause in infrastructure language.

---

## 40. Final Thought

Backfills are not boring.

They are one of the clearest tests of data platform maturity.

A backfill asks the platform to do something difficult:

> Reprocess history safely, correctly, observably, and without breaking the present.

That requires more than a rerun button.

It requires:

- idempotency;
- deterministic logic;
- point-in-time thinking;
- staging;
- validation;
- checkpointing;
- lineage;
- rollback;
- cost control;
- communication;
- governance;
- operational discipline.

The hype version of data engineering loves real-time streaming, AI features, lakehouse tables, and shiny dashboards.

All useful.

But one of the most practical questions remains:

> Can we fix the past without causing a new incident?

If the answer is yes, your platform is stronger than most.

If the answer is no, the next bug, schema change, late file, or metric correction will eventually expose it.

Backfills are not side quests.

They are reliability drills.

They are historical repair mechanisms.

They are trust-preserving operations.

They are the reason a data engineer can hear "we need to recompute the last six months" and respond with a plan instead of a thousand-yard stare.

Design pipelines that survive backfills.

Future you would like at least one peaceful weekend.
