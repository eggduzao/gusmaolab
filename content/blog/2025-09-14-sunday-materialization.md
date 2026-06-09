Title: The Sunday Materialization - Data Observability 101
Subtitle: Moving Beyond “Is the DAG Green?” Toward Knowing Whether the Data Is Actually Trustworthy
Date: 2026-06-28 07:00
Modified: 2026-06-28 07:00
Category: Sunday
Tags: data engineer, data platform engineer, data, data architecture, data observability, data quality, pipelines, monitoring, reliability
Slug: sunday-materialization-data-observability-101
Authors: Eduardo G Gusmao
Summary: A weekly educational topic/lecture/discussion on Data Engineering topics that we all experienced at least once (or will!)
Status: final
Lang: en
Template: topic
Cadence: Biweekly
Scope: Data Engineering, Industry, Data Challenges
Tone: Analytical, Educational, Non-Sensational
Canonical: https://www.gusmaolab.org/blog/sunday-materialization-data-observability-101/
Meta_description: Biweekly analysis of important Data Engineering concepts.
Meta_keywords: data concepts, topics, lectures, discussions, data observability, data quality, pipeline monitoring
Cover: images/covers/data-observability-101.png
Thumbnail: images/thumbnails/data-observability-101-thumb.png

# Data Observability 101: Moving Beyond “Is the DAG Green?”

There is a dangerous sentence in data engineering:

> “The DAG is green, so everything is fine.”

It sounds responsible. It sounds operational. It has the calm confidence of someone looking at a successful Airflow run and deciding the universe is in order.

Unfortunately, it is often wrong.

A green DAG means the workflow completed.

It does **not** necessarily mean:

- the data arrived on time;
- the data was complete;
- the data was correct;
- the data had the expected volume;
- the schema stayed compatible;
- the business meaning remained stable;
- downstream dashboards are trustworthy;
- machine learning features are safe to use;
- no upstream system quietly changed behavior;
- no consumer is currently preparing a Slack message beginning with “Quick question…”

A pipeline can succeed technically while failing semantically.

That is the whole reason data observability exists.

Data observability is the practice of understanding the health, quality, freshness, lineage, and reliability of data as it moves through a platform.

It is not just pipeline monitoring.
It is not just data quality testing.
It is not just logging.
It is not just a dashboard with many green squares and one suspiciously unlabeled metric.

Data observability asks a broader question:

> Can we trust this data product right now, and if not, do we know where, why, and who is affected?

That is a much better question than “Did the DAG run?”

---

## 1. Why “Green DAG” Thinking Is Not Enough

Workflow orchestrators are excellent at answering workflow questions.

For example:

- Did the task start?
- Did the task finish?
- Did the task fail?
- How long did it run?
- Did it retry?
- Which dependency came before it?
- Which task comes next?

These are important questions.

But they are not enough.

A workflow orchestrator can tell you that a pipeline ran successfully. It may not tell you that the resulting table contains half the expected rows.

Imagine this:

```
Task: load_customer_events
Status: success
Runtime: 8 minutes
Rows loaded: 0
```

Technically, the task succeeded.

Practically, the platform just published a beautiful empty table.

Or:

```
Task: build_daily_revenue
Status: success
Runtime: 11 minutes
Revenue total: -42,000,000
```

Again, the DAG is green.

The business, however, may have questions.

The core issue is simple:

> Pipeline success and data correctness are different things.

A task can complete without producing trustworthy data.

That distinction is the doorway into data observability.

---

## 2. Monitoring vs Data Observability

Traditional monitoring usually focuses on system behavior.

Examples:

- CPU usage;
- memory usage;
- job runtime;
- disk space;
- query latency;
- cluster health;
- container restarts;
- task failure rates;
- service availability.

This is necessary.

But data platforms also need to monitor the data itself.

Data observability focuses on questions like:

- Is the data fresh?
- Is the volume normal?
- Did the schema change?
- Are key fields complete?
- Are distributions unusual?
- Did duplicates increase?
- Did a foreign key relationship break?
- Which downstream assets depend on this table?
- Which users or reports are affected?
- When did the anomaly begin?
- Which upstream source likely caused it?

System monitoring says:

> The machine is alive.

Data observability says:

> The data flowing through the machine still makes sense.

Both are needed.

A perfectly healthy machine can faithfully process nonsense.

This is, incidentally, also a decent description of many meetings.

---

## 3. The Five Classic Pillars of Data Observability

Many teams organize data observability around five broad dimensions:

1. freshness;
2. volume;
3. schema;
4. quality;
5. lineage.

Different companies and tools may name these differently, but the core ideas are stable.

Let’s walk through them.

---

## 4. Freshness: Did the Data Arrive on Time?

Freshness measures whether data is up to date enough for its intended use.

A dataset can be correct but stale.

Example:

```
daily_sales_summary
last_updated_at: 2026-06-27 07:01
expected_update_time: 2026-06-28 07:00
current_time: 2026-06-28 09:30
status: stale
```

The table may contain valid rows.
The schema may be perfect.
The values may be correct.

But if users expect today’s sales and only yesterday’s data is available, the data product is failing.

Freshness should be defined per dataset.

Not all datasets need the same freshness.

| Dataset | Reasonable freshness expectation |
|---|---|
| Fraud signals | Seconds or minutes |
| Operational dashboard | Minutes |
| Product analytics | Hourly |
| Executive sales report | Daily |
| Financial close | Scheduled cutoff |
| Historical cohort table | Weekly or on demand |
| Regulatory extract | Reproducible release |

A good observability system does not merely ask:

> Is the table updated?

It asks:

> Is the table updated according to its contract and business need?

A daily revenue table that updates every morning at 07:00 has a different freshness expectation from a streaming fraud table.

Freshness without context is just a timestamp.

Freshness with expectations becomes reliability.

---

## 5. Volume: Did We Receive the Expected Amount of Data?

Volume observability checks whether the amount of data looks normal.

Examples:

- number of rows ingested;
- number of events per hour;
- file sizes;
- number of partitions;
- number of distinct customers;
- number of transactions;
- number of source records;
- output-to-input ratios.

Volume anomalies are often early warning signs.

For example:

```
Expected daily events: 10,000,000–13,000,000
Observed daily events: 2,100,000
```

The pipeline may still succeed.

But something is wrong.

Possible causes:

- upstream extraction failed partially;
- vendor sent incomplete files;
- API pagination broke;
- source system changed filters;
- ingestion job skipped partitions;
- timezone boundary shifted;
- event producer stopped emitting some event types;
- authentication expired for one source.

Volume checks are especially useful because they catch problems that do not violate schema.

A table can have the right columns, right types, and zero useful rows.

A green DAG will smile politely at this disaster.

A volume monitor should not.

---

## 6. Schema: Did the Shape of the Data Change?

Schema observability tracks structural changes.

Examples:

- column added;
- column removed;
- column renamed;
- type changed;
- nullable field became required;
- nested structure changed;
- enum values changed;
- precision changed;
- timestamp representation changed.

Some schema changes are harmless.

Adding a nullable column may be fine.

Some changes are dangerous.

Renaming `customer_id` to `client_id` can break every downstream join, dashboard, and feature pipeline that depends on the original field.

A simple schema contract might look like this:

```yaml
dataset: customer_events
version: 1.4.0

fields:
  - name: customer_id
    type: string
    nullable: false

  - name: event_type
    type: string
    nullable: false
    allowed_values:
      - signup
      - login
      - purchase
      - cancellation

  - name: event_timestamp
    type: timestamp
    nullable: false
    timezone: UTC
```

A schema observability system should detect:

- unexpected missing fields;
- incompatible type changes;
- new fields that need review;
- changes to nullability;
- incompatible enum modifications.

But schema is only part of the story.

A field can keep the same name and type while changing meaning.

That is where quality and semantics enter.

---

## 7. Quality: Does the Data Still Make Sense?

Data quality is broad.

It includes checks like:

- null rates;
- uniqueness;
- valid ranges;
- accepted categories;
- referential integrity;
- duplicate detection;
- distribution drift;
- business rule validation;
- consistency across tables;
- reconciliation against source totals.

For example:

```
Check: customer_id is not null
Expected: null_rate <= 0.001
Observed: null_rate = 0.184
Status: violation
```

Or:

```
Check: transaction_amount >= 0
Expected: true
Observed: 3.7% negative values
Status: violation
```

Or:

```
Check: order_status values
Expected: pending, paid, shipped, cancelled
Observed: pending, paid, shipped, cancelled, unknown_error
Status: warning
```

Quality checks should be tied to business meaning.

A generic null check is useful, but a semantic check is better.

For example:

```
If event_type = 'purchase', transaction_id must not be null.
```

That is more meaningful than simply saying every field must be non-null.

Good data observability requires knowing what correctness means for that dataset.

This is why observability and data contracts are natural friends.

A data contract defines expectations.
Observability checks whether reality still matches them.

---

## 8. Lineage: What Is Affected?

Lineage tells us how data flows through the platform.

It answers:

- Where did this dataset come from?
- Which upstream sources feed it?
- Which transformations produced it?
- Which downstream tables depend on it?
- Which dashboards use it?
- Which ML features depend on it?
- Which reports are affected?
- Who owns each piece?

Lineage turns an anomaly from a vague panic into a targeted response.

Without lineage, the incident looks like this:

> “Something is wrong with customer data. Good luck, everyone.”

With lineage, the incident looks like this:

> “The `customer_events` ingestion dropped 60% in volume starting at 02:10. It affects `daily_active_users`, `conversion_funnel`, the Growth dashboard, and the churn feature table. The likely upstream source is the mobile event producer.”

That is a different level of maturity.

Lineage also helps with prioritization.

If a low-use experimental table has an anomaly, maybe it can wait.

If a table feeds executive revenue reporting, fraud detection, and regulatory extracts, the response should be immediate.

Not all data incidents are equal.

Lineage tells us the blast radius.

---

## 9. The Difference Between Data Quality and Data Observability

Data quality and data observability are related, but not identical.

Data quality asks:

> Is this data good?

Data observability asks:

> How do we continuously know whether data is good, where it became bad, and who is affected?

A data quality check may be a test.

A data observability system is the broader operational layer around tests, metrics, alerts, history, lineage, ownership, and incident response.

For example:

```md
Data quality:
- customer_id must not be null.

Data observability:
- customer_id null rate increased from 0.01% to 17%.
- anomaly started at 03:15.
- upstream source was mobile_events_v2.
- affected tables include customer_sessions and conversion_funnel.
- affected dashboard is Growth Weekly KPIs.
- owner is Growth Platform Team.
- alert sent to #data-growth-alerts.
```

The second version is operationally useful.

It tells you not only that something is wrong, but also where to look and what is affected.

A single test says “fire.”

Observability says “fire in kitchen, smoke spreading to dining room, call this person, do not serve the soup.”

Much better.

---

## 10. Why Data Incidents Are Different From Software Incidents

Software incidents often affect services directly.

Examples:

- API unavailable;
- latency increased;
- deployment broke;
- authentication failed;
- database connection pool exhausted.

Data incidents are trickier because they can be delayed and silent.

A bad data event today may affect:

- tomorrow’s dashboard;
- next week’s model training;
- next month’s financial report;
- a regulatory submission;
- a cohort analysis;
- a business decision made by someone who never saw the pipeline.

The failure may not be visible immediately.

The pipeline may continue running.

The dashboard may continue loading.

The model may continue predicting.

That is why data observability needs historical context.

You need to know not only whether today’s values are valid, but whether they are unusual compared with previous behavior.

For example:

```md
Average daily purchases:
- Last 30 days: 820,000 ± 60,000
- Today: 311,000
```

This may indicate a real business event.
Or an ingestion failure.
Or a tracking bug.
Or a holiday.
Or a product launch gone terribly wrong.

Observability does not automatically know the answer.

But it tells you where reality diverged from expectation.

That is where investigation begins.

---

## 11. A Green DAG With Bad Data: A Small Example

Imagine a daily pipeline.

```
extract_orders
    ↓
load_orders_raw
    ↓
transform_orders_clean
    ↓
build_revenue_summary
    ↓
refresh_dashboard
```

The DAG succeeds.

But the source API changed pagination behavior. The extraction job only fetched the first page.

The result:

- pipeline status: success;
- rows extracted: 1,000;
- normal daily rows: 850,000;
- dashboard refreshed: yes;
- dashboard values: catastrophically wrong.

Airflow says success.

The business sees revenue collapse.

The data engineer says “but the DAG is green.”

This is exactly the gap data observability fills.

A volume check should have noticed.

```
dataset: orders_raw
check: daily_row_count
expected_range: 700000-1000000
observed: 1000
severity: critical
```

A freshness check might still pass.
A schema check might still pass.
A task status check definitely passes.

But the data is not trustworthy.

This is why observability must monitor the data, not only the workflow.

---

## 12. What Should We Observe?

A practical data observability system should collect metrics at several levels.

### Dataset-level metrics

Examples:

- row count;
- partition count;
- file count;
- total size;
- last updated timestamp;
- freshness delay;
- schema version;
- number of columns;
- duplicate rate.

### Column-level metrics

Examples:

- null rate;
- distinct count;
- min/max;
- mean/median;
- standard deviation;
- percentiles;
- value distribution;
- allowed value violations;
- pattern violations.

### Pipeline-level metrics

Examples:

- runtime;
- retries;
- failure rate;
- queue time;
- input/output counts;
- data scanned;
- shuffle size;
- memory pressure;
- SLA misses.

### Business-level metrics

Examples:

- total revenue;
- number of active users;
- conversion rate;
- claim count;
- lab result count;
- transaction count;
- average order value.

This last category is crucial.

Sometimes the best data quality signal is a business metric.

If total daily transactions suddenly fall by 80%, that may be more informative than any generic column-level test.

Data observability should combine technical signals and domain signals.

Otherwise, you get a system that knows a column is a string, but not that the business just vanished from the table.

---

## 13. Alerting: The Art of Not Annoying Everyone

Observability without alerting is passive.

Alerting without discipline is torture.

A bad alerting system sends too many notifications, too often, with too little context.

Then people ignore it.

This is how alert fatigue begins.

Good data observability alerts should be:

- actionable;
- specific;
- routed to the right owner;
- severity-aware;
- deduplicated;
- connected to lineage;
- linked to run history;
- clear about impact;
- quiet when the issue is non-critical.

A weak alert says:

```
Data quality failure detected.
```

A better alert says:

```md
Critical data freshness violation

Dataset: daily_revenue_summary
Expected by: 07:00 America/Recife
Current delay: 94 minutes
Last successful update: 2026-06-27 06:58

Likely upstream blocker:
- load_orders_raw did not receive today's partition

Affected assets:
- Executive Revenue Dashboard
- Finance Daily Close Report

Owner:
- finance-data-platform
```

That alert is useful.

It gives context.
It gives impact.
It gives ownership.
It gives a place to start.

A good alert should reduce confusion, not merely announce that confusion exists.

---

## 14. Severity Levels Matter

Not every data issue should page someone.

A small anomaly in an exploratory dataset is not the same as a broken revenue table.

A practical severity model might look like this:

| Severity | Meaning | Example |
|---|---|---|
| Critical | Major business or regulatory impact | Revenue report missing before executive meeting |
| High | Important data product degraded | Customer events volume dropped 40% |
| Medium | Issue affects limited consumers | Null rate increased in non-critical field |
| Low | Informational or early warning | New optional column detected |
| Info | No action required yet | Volume slightly above normal range |

Severity should depend on:

- dataset importance;
- downstream consumers;
- business impact;
- freshness requirement;
- data contract violation;
- historical behavior;
- whether the issue is persistent;
- whether the issue affects critical reports or models.

This is another reason lineage matters.

You cannot assess severity well if you do not know who depends on the data.

---

## 15. Ownership: Every Alert Needs a Human Address

A data incident without an owner becomes a group mystery.

Everyone sees the alert.
Nobody owns it.
Three people investigate in parallel.
A fourth person asks whether this is expected.
A fifth person says “maybe upstream changed something.”
Someone opens a ticket.
The ticket reproduces by mitosis.

Good observability requires ownership metadata.

For each important dataset, know:

- producing team;
- consuming teams;
- technical owner;
- business owner;
- escalation channel;
- runbook link;
- expected freshness;
- severity policy.

A simple ownership block might look like this:

```md
dataset: customer_events
owner:
  team: growth-platform
  slack: "#data-growth-alerts"
  technical_contact: data-growth-oncall
  business_contact: growth-analytics-lead

freshness:
  expected_delay_minutes: 15

critical_consumers:
  - conversion_funnel_dashboard
  - churn_feature_table
  - campaign_attribution_model
```

Ownership turns observability from passive measurement into operational responsibility.

Without ownership, observability becomes a museum of problems.

Beautifully displayed. Nobody fixing them.

---

## 16. Observability and Data Contracts

Data contracts define expectations.

Data observability measures whether those expectations are being met.

A contract might say:

```yaml
dataset: payment_transactions
freshness:
  max_delay_minutes: 10

schema:
  - name: transaction_id
    type: string
    nullable: false
  - name: transaction_amount
    type: decimal(12, 2)
    nullable: false
  - name: currency_code
    type: string
    nullable: false
    allowed_values:
      - BRL
      - USD
      - EUR

quality:
  transaction_id:
    unique: true
  transaction_amount:
    min: 0
```

Observability turns that into continuous signals:

- Is freshness within 10 minutes?
- Does the schema still match?
- Are transaction IDs unique?
- Are amounts non-negative?
- Are currency codes valid?
- Did volume change unexpectedly?
- Which downstream reports are affected if this fails?

The contract is the promise.

Observability is the surveillance camera politely asking whether the promise is still being kept.

Not glamorous. Extremely useful.

---

## 17. Observability and Lineage Together

Lineage is often treated as a catalog feature.

But lineage becomes much more powerful when connected to observability.

Suppose a source table has a schema change.

Without lineage:

> “Column removed from `raw_customer_events`.”

With lineage:

> “Column removed from `raw_customer_events`. This affects 14 downstream models, 3 dashboards, and 2 ML feature tables. The most critical affected asset is `daily_active_users`, used in the executive product dashboard.”

That is a completely different incident.

Lineage helps answer:

- What broke?
- What may break next?
- Who should be notified?
- Which assets should be paused?
- Which outputs should be marked stale or unreliable?
- How far did the bad data propagate?

In mature platforms, lineage should support impact analysis.

Before changing a dataset, you should be able to ask:

> What will this break?

After an incident, you should be able to ask:

> What did this affect?

These are not luxuries.

They are how data platforms stop operating by superstition.

---

## 18. Observability in Batch Pipelines

Batch observability focuses on bounded runs.

Typical questions:

- Did today’s partition arrive?
- Did the job process the expected number of rows?
- Did the output partition get written?
- Did the runtime change?
- Did null rates change?
- Did key metrics reconcile?
- Did the job publish before the SLA?
- Did downstream models refresh?

Example batch observability record:

```
pipeline: daily_orders_pipeline
run_date: 2026-06-28
status: success

input:
  source_files: 12
  raw_rows: 918234

output:
  clean_rows: 917982
  rejected_rows: 252

freshness:
  expected_by: "07:00"
  completed_at: "06:42"
  status: ok

quality:
  duplicate_order_id_rate: 0.0001
  null_customer_id_rate: 0.0003
  invalid_status_count: 0
```

This is much richer than “success.”

It tells the story of the run.

A mature batch pipeline should leave behind enough evidence that future engineers can understand what happened.

A pipeline run without metadata is like a lab experiment without notes.

Technically it happened. Scientifically, good luck.

---

## 19. Observability in Streaming Pipelines

Streaming observability has additional concerns.

Because streaming jobs are continuous, you monitor different signals:

- consumer lag;
- throughput;
- event-time delay;
- processing-time delay;
- checkpoint health;
- state size;
- late event rate;
- dropped event count;
- duplicate event count;
- watermark progression;
- sink write failures;
- backpressure;
- restart count.

A streaming job can be “running” but unhealthy.

For example:

```
stream: payment_events_processor
status: running
consumer_lag: 18,000,000 events
watermark_delay: 47 minutes
checkpoint_age: 52 minutes
late_event_rate: 14%
```

The job is alive.

But the output is not fresh.

Again, “green” is not enough.

For streaming, observability must distinguish:

- process is running;
- process is keeping up;
- process is producing correct outputs;
- process is recovering correctly;
- process is maintaining state safely.

A streaming system that is technically alive but 90 minutes behind may be operationally dead for real-time use cases.

Alive is not the same as useful.

This is also true before coffee.

---

## 20. Observability in the Warehouse and Lakehouse

Many data incidents surface in warehouses and lakehouses.

Useful observability checks include:

- table freshness;
- partition freshness;
- table size;
- file count;
- small file growth;
- schema drift;
- query performance;
- clustering quality;
- partition skew;
- failed merges;
- stale statistics;
- materialized view refresh failures;
- permissions changes;
- unexpected cost spikes.

For lakehouse systems, metadata observability is especially important.

A table may become slow because:

- too many small files accumulated;
- compaction did not run;
- partitioning is too granular;
- old snapshots were not cleaned;
- clustering no longer matches access patterns.

These are not classic data quality problems.

But they affect data product reliability.

A table that is correct but painfully slow may still fail user expectations.

Data observability should care about usability, not only correctness.

---

## 21. Observability for Machine Learning Features

ML systems add another layer.

Feature observability should monitor:

- feature freshness;
- feature null rates;
- distribution drift;
- training-serving skew;
- feature availability;
- feature computation failures;
- label delays;
- join coverage;
- entity key mismatch;
- online/offline consistency.

A feature pipeline can be green while producing a distribution that no longer resembles training data.

Example:

```
feature: user_7d_purchase_count
training_mean: 2.4
production_mean_last_24h: 0.1
status: drift_detected
```

Possible causes:

- event ingestion dropped purchases;
- join key changed;
- feature logic changed;
- source system changed event names;
- user behavior genuinely changed;
- bot filtering was introduced upstream.

For ML, observability is not just about pipeline health.

It is about whether the model’s inputs still live in the same universe as the training data.

Models are very literal creatures.

Feed them nonsense with confidence, and they will return nonsense with confidence.

---

## 22. Data Observability in Healthcare and Biotech

Healthcare and biotech make observability especially important because data is complex, heterogeneous, and often high-stakes.

Consider clinical data.

A pipeline may ingest diagnosis codes successfully, but observability should ask:

- Did the expected number of patients arrive?
- Did diagnosis code distributions change?
- Did a hospital stop sending one department’s records?
- Did ICD-10 codes suddenly appear where ICD-9 was expected?
- Did encounter dates shift because of timezone or export logic?
- Did patient identifiers lose mapping coverage?
- Did lab values change units?
- Did a source system update its extraction rules?

For genomics, observability may include:

- sample count;
- file arrival;
- FASTQ/BAM/VCF completeness;
- reference genome version;
- variant count distributions;
- missing metadata;
- failed quality thresholds;
- batch effects;
- annotation version changes.

A genomics pipeline can produce files successfully while silently changing scientific interpretation.

For example:

```yaml
reference_genome: GRCh37
```

versus:

```yaml
reference_genome: GRCh38
```

That is not a cosmetic difference.

A data observability system in biomedical contexts should monitor not only technical fields, but also domain-critical metadata.

Because in these domains, “the file exists” is nowhere near enough.

---

## 23. Practical Example: A Minimal Data Observability Check in Python

Below is a simplified example of dataset-level checks using Pandas.

This is not a full observability platform. It is a teaching sketch.

```python
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

import pandas as pd


@dataclass(frozen=True)
class DatasetExpectation:
    """Basic expectations for a dataset."""

    name: str
    min_rows: int
    max_rows: int
    max_freshness_delay_minutes: int
    required_columns: set[str]


@dataclass(frozen=True)
class ObservabilityResult:
    """Result from a simple observability validation."""

    dataset_name: str
    passed: bool
    messages: list[str]


def check_dataset_observability(
    df: pd.DataFrame,
    expectation: DatasetExpectation,
    last_updated_at: datetime,
    current_time: datetime | None = None,
) -> ObservabilityResult:
    """
    Run simple observability checks for a dataset.

    Parameters
    ----------
    df
        Dataset to validate.
    expectation
        Dataset-level expectations.
    last_updated_at
        Timestamp indicating when the dataset was last updated.
    current_time
        Current timestamp. If ``None``, current UTC time is used.

    Returns
    -------
    ObservabilityResult
        Validation result containing pass/fail status and messages.
    """
    now = current_time or datetime.now(timezone.utc)
    messages: list[str] = []

    row_count = len(df)
    if row_count < expectation.min_rows or row_count > expectation.max_rows:
        messages.append(
            f"Row count out of expected range: "
            f"observed={row_count}, "
            f"expected=[{expectation.min_rows}, {expectation.max_rows}]"
        )

    observed_columns = set(df.columns)
    missing_columns = expectation.required_columns - observed_columns
    if missing_columns:
        messages.append(
            f"Missing required columns: {sorted(missing_columns)}"
        )

    freshness_delay = now - last_updated_at
    max_delay = timedelta(minutes=expectation.max_freshness_delay_minutes)
    if freshness_delay > max_delay:
        messages.append(
            f"Freshness violation: "
            f"delay={freshness_delay}, max_allowed={max_delay}"
        )

    return ObservabilityResult(
        dataset_name=expectation.name,
        passed=len(messages) == 0,
        messages=messages,
    )
```

This tiny function checks only three things:

- row count;
- required columns;
- freshness.

Even this simple version already goes beyond “did the job run?”

In real platforms, these checks would be:

- metadata-driven;
- versioned;
- connected to data contracts;
- stored historically;
- connected to lineage;
- routed to owners;
- visualized in dashboards;
- used for alerting.

But the heart of the idea is already here:

> Observe the data product, not only the task that created it.

---

## 24. The Maturity Ladder

Data observability maturity usually evolves in stages.

### Stage 0: Hope

The platform runs.

Nobody knows whether the data is good until someone complains.

This is common.

Not ideal. Very human.

### Stage 1: Pipeline monitoring

Teams monitor job failures, retries, and runtimes.

This is necessary, but still workflow-focused.

### Stage 2: Basic data quality checks

Teams add tests for nulls, uniqueness, row counts, and schemas.

This catches many obvious problems.

### Stage 3: Dataset observability

Teams monitor freshness, volume, schema drift, and historical anomalies across key datasets.

Now the platform begins to see data health.

### Stage 4: Lineage-aware observability

Alerts include upstream causes and downstream impact.

Now incidents become easier to triage.

### Stage 5: Contract-driven observability

Expectations are defined in data contracts and automatically enforced.

This creates alignment between producers and consumers.

### Stage 6: Product-level reliability

Data products have SLOs, ownership, incident processes, runbooks, and consumer-facing trust indicators.

At this stage, data observability becomes part of platform engineering.

Not an add-on.

Not a side quest.

A core reliability layer.

---

## 25. Common Anti-Patterns

### Anti-pattern 1: Only monitoring DAG status

This catches task failures but misses bad data.

It is necessary but insufficient.

### Anti-pattern 2: Too many low-value alerts

If every small anomaly alerts everyone, nobody listens.

Alert quality matters more than alert quantity.

### Anti-pattern 3: No ownership

An alert without an owner is just a notification-shaped problem.

### Anti-pattern 4: No historical baseline

A row count of 500,000 means little without knowing whether normal is 5,000 or 5,000,000.

### Anti-pattern 5: Monitoring only technical metrics

A table can have valid types and still contain business nonsense.

Include domain metrics.

### Anti-pattern 6: No lineage

Without lineage, impact analysis becomes detective work with worse lighting.

### Anti-pattern 7: Treating observability as a tool purchase

Tools help. But observability also requires contracts, ownership, processes, runbooks, and platform culture.

Buying a thermometer does not automatically make a hospital.

---

## 26. What Good Looks Like

A healthy data observability setup should help answer questions quickly.

For example:

### Is the data fresh?

```
daily_revenue_summary was expected at 07:00.
It was published at 06:48.
Freshness status: OK.
```

### Did volume change?

```
orders_raw received 912,442 rows today.
Expected range based on previous 30 days: 780,000–980,000.
Volume status: OK.
```

### Did the schema change?

```
New nullable column detected: discount_campaign_id.
Compatibility status: non-breaking.
Review required: yes.
```

### Did quality degrade?

```
customer_id null rate increased from 0.02% to 8.4%.
Severity: high.
Started after mobile app release 5.18.
```

### What is affected?

```
Affected downstream assets:
- conversion_funnel_dashboard
- churn_training_features
- marketing_attribution_mart
```

### Who owns it?

```
Owner: growth-platform-team
Alert channel: #data-growth-alerts
Runbook: growth/customer-events-null-rate
```

This is what separates observability from vibes.

And data platforms should not be operated by vibes.

Vibes are for playlists, not revenue reports.

---

## 27. Observability Is Also a Trust Layer

The deeper purpose of data observability is trust.

People use data when they believe it.

They stop using data when they repeatedly find surprises.

Trust is hard to build and easy to damage.

A single visible data incident can make users skeptical for months.

A dashboard that is wrong twice becomes “that dashboard.”
A table that breaks weekly becomes “that table.”
A platform that often surprises users becomes “the data team’s problem.”

Observability helps protect trust by making problems visible earlier and explainable faster.

It also helps communicate honestly.

Sometimes the right behavior is not to hide an issue, but to mark a dataset as stale or unreliable.

A mature platform can say:

> “This table is delayed. The issue is upstream. The affected dashboards are these. The owner has been alerted. Last reliable update was yesterday at 07:02.”

That is much better than silently serving stale data with a confident smile.

Trust does not require perfection.

It requires visibility, accountability, and recovery.

---

## 28. Final Thought

Data observability begins when a team stops asking only:

> “Did the DAG run?”

and starts asking:

> “Can the business trust what the DAG produced?”

That is the real shift.

A green DAG is useful information.

But it is only one signal.

Modern data platforms need to know whether data is fresh, complete, valid, stable, meaningful, and safe for downstream use.

They need to know who owns each dataset.

They need to know what depends on what.

They need to know when a change is harmless, suspicious, or dangerous.

They need to know whether an incident affects one experimental notebook or the company’s executive dashboard.

Data observability is not about making dashboards for data engineers to admire.

It is about reducing surprise.

It is about finding problems before users do.

It is about shortening the distance between detection and explanation.

It is about treating data products with the same seriousness we already give to software services.

Because in a modern organization, data is not a passive artifact.

Data is infrastructure.
Data is product.
Data is interface.
Data is decision fuel.

And if the DAG is green but the data is wrong, the platform is not healthy.

It is merely failing politely.
