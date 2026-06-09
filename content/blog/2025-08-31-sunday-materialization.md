Title: The Sunday Materialization - Batch Is Dead, Long Live Batch
Subtitle: When Streaming Is Overkill, and the Nightly Job Is Still a Hero
Date: 2026-06-14 07:00
Modified: 2026-06-14 07:00
Category: Sunday
Tags: data engineer, data platform engineer, data, data architecture, batch processing, streaming, data pipelines, orchestration, platform design
Slug: sunday-materialization-batch-is-dead-long-live-batch
Authors: Eduardo G Gusmao
Summary: A weekly educational topic/lecture/discussion on Data Engineering topics that we all experienced at least once (or will!)
Status: final
Lang: en
Template: topic
Cadence: Biweekly
Scope: Data Engineering, Industry, Data Challenges
Tone: Analytical, Educational, Non-Sensational
Canonical: https://www.gusmaolab.org/blog/sunday-materialization-batch-is-dead-long-live-batch/
Meta_description: Biweekly analysis of important Data Engineering concepts.
Meta_keywords: data concepts, topics, lectures, discussions, batch processing, streaming, data pipelines
Cover: images/covers/batch-is-dead-long-live-batch.png
Thumbnail: images/thumbnails/batch-is-dead-long-live-batch-thumb.png

# Batch Is Dead, Long Live Batch: When Streaming Is Overkill

Every few years, the data world announces the death of something.

Data warehouses are dead.
ETL is dead.
Batch is dead.
SQL is dead.
Data lakes are dead.
Dashboards are dead.
Probably someone, somewhere, has declared CSV dead while uploading a CSV to production.

And yet, somehow, the corpse keeps attending meetings.

Batch processing is one of these supposedly dead ideas.

In the age of Kafka, Flink, Spark Structured Streaming, real-time feature stores, event-driven architectures, and dashboards that promise "live" metrics, batch can sound old-fashioned. Almost suspicious. Like showing up to a cloud-native architecture review with a fax machine and a confident smile.

But here is the uncomfortable truth:

> Most business decisions do not require streaming.

Some do. Absolutely. Streaming is essential for fraud detection, real-time personalization, operational monitoring, high-frequency logistics, online recommendations, observability, real-time bidding, and many event-driven systems.

But many data workloads are not like that.

They are daily.
They are hourly.
They are weekly.
They are monthly.
They are retrospective.
They are analytical.
They are reporting-oriented.
They are audit-oriented.
They are "please make sure the numbers are correct by tomorrow morning."

For these workloads, batch is not dead.

Batch is calm.
Batch is predictable.
Batch is cheaper.
Batch is easier to debug.
Batch is easier to reproduce.
Batch is often exactly what the organization needs.

The problem is not batch.

The problem is using batch where the business needs immediacy - and using streaming where the business needs reliability, simplicity, and a good night's sleep.

---

## 1. The False War: Batch vs Streaming

The data industry often frames batch and streaming as enemies.

Batch is "old."
Streaming is "modern."
Batch is "slow."
Streaming is "real-time."
Batch is "legacy."
Streaming is "event-driven and therefore morally superior."

This framing is too simplistic.

Batch and streaming are not moral categories. They are processing strategies.

A better question is not:

> Should we use batch or streaming?

A better question is:

> What is the required freshness, correctness, cost, complexity, and operational model for this data product?

That question changes everything.

Because sometimes the answer is streaming.

And sometimes the answer is:

> Run the job at 03:00, validate it, publish the table at 06:30, and let everyone have coffee like civilized mammals.

The point is not to worship batch.
The point is to choose deliberately.

---

## 2. What Batch Really Means

Batch processing means data is collected and processed in bounded chunks.

The chunk may be:

- one day of sales;
- one hour of logs;
- one month of claims;
- one folder of vendor files;
- one partition of transactions;
- one snapshot from a source database;
- one genomic cohort;
- one hospital export;
- one backfill range.

The defining feature is that the system processes a finite set of records, then finishes.

A batch job has a beginning, middle, and end.

That may sound obvious, but it has huge operational consequences.

Because the job ends, you can ask:

- Did it succeed?
- How many records did it process?
- What was the input?
- What was the output?
- Can we rerun it?
- Can we compare today with yesterday?
- Can we reproduce last month's report?
- Can we validate the complete result before publishing?

This is why batch remains powerful.

It fits naturally with many analytical and reporting workflows.

A batch job is like baking bread. You prepare ingredients, run the process, inspect the result, and serve it.

Streaming is more like running a restaurant kitchen during dinner rush. More immediate, more responsive, but also more complex. Nobody wants the kitchen to "eventually converge" while the customers stare into the void.

---

## 3. What Streaming Really Means

Streaming means processing data as it arrives, usually as an unbounded sequence of events.

Instead of waiting for a full day of records, the system continuously receives and processes events.

Examples:

- user clicks;
- payment attempts;
- sensor readings;
- application logs;
- financial transactions;
- location updates;
- clinical device signals;
- inventory changes;
- real-time alerts.

Streaming is powerful because it reduces latency.

It allows systems to respond quickly.

For example:

- detect fraud while the transaction is still happening;
- update product recommendations during a user session;
- trigger an alert when a system metric crosses a threshold;
- monitor live operational events;
- update near-real-time dashboards;
- process IoT signals continuously.

But streaming is not just "batch, but faster."

Streaming introduces a different set of problems:

- event ordering;
- late-arriving data;
- duplicate events;
- replay semantics;
- exactly-once or effectively-once processing;
- checkpointing;
- state management;
- windowing;
- watermarking;
- backpressure;
- schema evolution;
- continuous deployment;
- operational monitoring;
- recovery from partial failure.

Streaming is not free magic.

Streaming is a trade-off.

It buys lower latency at the cost of higher complexity.

Sometimes that trade-off is worth it.

Sometimes it is like using a Formula 1 car to buy bread three blocks away.

Impressive? Yes.
Necessary? No.
Expensive when you hit a speed bump? Also yes.

---

## 4. Freshness Is the Real Requirement

Most arguments about batch and streaming are confused because people say "real-time" when they mean "faster than we have now."

But "real-time" is not one thing.

Freshness requirements exist on a spectrum.

| Use case | Typical freshness need |
|---|---|
| Fraud detection | Seconds or less |
| Real-time personalization | Milliseconds to seconds |
| Operational monitoring | Seconds to minutes |
| Inventory updates | Minutes |
| Product analytics | Minutes to hours |
| Sales dashboards | Hourly to daily |
| Executive reporting | Daily |
| Financial close | Daily to monthly |
| Regulatory reporting | Scheduled and reproducible |
| Historical cohort analysis | On demand or periodic |
| ML offline training dataset | Daily, weekly, or triggered |

The key question is:

> How stale can the data be before it stops being useful?

If the answer is "one day," streaming is probably unnecessary.

If the answer is "one hour," micro-batch or incremental batch may be enough.

If the answer is "five minutes," streaming may be useful, but not always required.

If the answer is "five seconds," now we are talking.

Freshness should be defined explicitly.

A dataset contract might say:

```yaml
dataset: sales_daily_summary
freshness:
  expected_by: "07:00"
  timezone: "America/Recife"
  max_delay_minutes: 30
  processing_mode: batch
```

Another might say:

```yaml
dataset: payment_fraud_signals
freshness:
  max_delay_seconds: 5
  processing_mode: streaming
```

These are different products.

They deserve different architectures.

---

## 5. Streaming Is Overkill When the Business Clock Is Slow

A common architectural mistake is building for machine-time when the business operates in human-time.

For example:

- A finance team reviews revenue once every morning.
- A hospital quality team reviews indicators weekly.
- A marketing team checks campaign performance twice per day.
- A data science team retrains a model every Sunday.
- A regulatory report is submitted monthly.
- A board report is generated quarterly.

In these cases, streaming may not create meaningful value.

It may produce fresher data that nobody uses.

That is an expensive form of theatre.

The correct metric is not:

> How fast can we update the table?

The correct metric is:

> How fast does the organization need the data to make a better decision?

If the decision cycle is daily, a reliable daily batch is often better than a fragile streaming pipeline.

Freshness without actionability is just expensive decoration.

---

## 6. The Hidden Cost of Streaming

Streaming systems are seductive because they promise immediacy.

But they come with operational cost.

A streaming platform usually requires thinking about:

### Continuous availability

A batch job can fail, be fixed, and rerun.

A streaming job is supposed to keep running.

That changes the operational model. You now need monitoring, alerting, recovery, checkpoint management, lag tracking, and deployment strategies for long-running jobs.

### State management

Many streaming jobs need state.

Examples:

- count events per user in the last 10 minutes;
- detect repeated failed login attempts;
- aggregate purchases by session;
- track device status over time;
- calculate rolling metrics.

State must be stored, updated, checkpointed, recovered, and sometimes expired.

State is where streaming grows teeth.

### Late and out-of-order data

Events may arrive late.

Example:

A mobile app records an event at 10:01 but uploads it at 10:17 because the device was offline.

Should the 10:00-10:05 window be updated?
Should the dashboard change retroactively?
Should alerts be recalculated?
Should reports be corrected?

These are not minor details.

They define correctness.

### Reprocessing

In batch, reprocessing is usually conceptually simple:

> Rerun the job for a date range.

In streaming, reprocessing may require replaying events from a log, resetting checkpoints, handling idempotency, avoiding duplicate writes, and making sure outputs remain consistent.

This is possible.

But it is not trivial.

### Debugging

Batch debugging is often easier because the input is bounded.

You can inspect a partition.
You can rerun locally.
You can compare outputs.
You can snapshot intermediate tables.

Streaming debugging involves moving time, state, event order, replay, and partial failures.

Wonderful if needed. Painful if unnecessary.

Streaming is not bad.

But streaming complexity must be earned.

---

## 7. Batch Is Often Better for Reproducibility

Reproducibility matters.

Especially in:

- finance;
- healthcare;
- biotech;
- insurance;
- compliance;
- ML training;
- experimentation;
- scientific analytics;
- regulated reporting.

Batch processing is naturally aligned with reproducibility because it works with bounded inputs.

You can say:

> This report was generated from data available at this date and time, using this code version, over this input partition range.

That is powerful.

In healthcare, for example, a cohort extraction may need to be reproducible.

If a clinical phenotype table changes continuously throughout the day, downstream analysis becomes harder to audit.

For genomics, a variant table may depend on reference genome version, variant caller version, filtering thresholds, sample metadata, and release date. Batch releases are often more appropriate than continuous mutation of analytical truth.

In financial reporting, numbers often need stable cutoffs.

If revenue changes every second, the business still needs to close the books at a defined moment.

Batch creates boundaries.

Boundaries are not always limitations.
Sometimes they are guarantees.

---

## 8. Batch Can Be Fast Enough

Batch does not necessarily mean slow.

A batch can run every day, every hour, every 15 minutes, or every 5 minutes.

At that point, people may call it micro-batch.

But conceptually, it is still bounded processing.

Many modern systems use micro-batching as a practical compromise:

```
Collect events for 5 minutes
Process bounded batch
Write results
Repeat
```

This can deliver near-real-time freshness without adopting the full complexity of continuous event-by-event processing.

Spark Structured Streaming, for example, often operates in micro-batch mode. Many "streaming" pipelines in the wild are actually controlled repeated batches with checkpointing and incremental offsets.

And that is fine.

The name matters less than the operational behavior.

If the platform can produce trustworthy updates every 5 or 15 minutes, many business use cases are satisfied.

Do not let architecture vocabulary bully you.

A five-minute batch that works is better than a real-time pipeline that occasionally invents new forms of grief.

---

## 9. The Spectrum: Batch, Incremental Batch, Micro-Batch, Streaming

It helps to think of processing modes as a spectrum, not a binary choice.

### Full batch

Reprocess everything in a bounded dataset.

Good for:

- small datasets;
- simple daily jobs;
- full refresh marts;
- reproducible reports;
- backfills;
- source snapshots.

Bad for:

- huge frequently changing datasets;
- low-latency requirements;
- unnecessary recomputation.

### Incremental batch

Process only new or changed data.

Good for:

- large tables;
- daily/hourly updates;
- warehouse transformations;
- lakehouse pipelines;
- cost control;
- slowly changing business datasets.

Bad for:

- highly stateful real-time logic;
- complex late-arriving event semantics if not designed carefully.

### Micro-batch

Process small bounded chunks frequently.

Good for:

- near-real-time dashboards;
- event ingestion;
- log processing;
- moderate freshness requirements;
- practical compromise architectures.

Bad for:

- ultra-low-latency systems;
- cases where every second matters.

### True streaming

Process events continuously as they arrive.

Good for:

- fraud detection;
- real-time recommendations;
- online features;
- operational alerting;
- sensor/IoT streams;
- real-time monitoring.

Bad for:

- simple reporting;
- low-change datasets;
- monthly analytics;
- teams without operational maturity;
- cases where correctness and reproducibility matter more than immediacy.

This spectrum is more useful than tribal debates.

---

## 10. The Architecture Question: What Happens If Data Is Late?

A beautiful way to decide between batch and streaming is to ask:

> What happens if this data arrives late?

If the answer is:

> Nothing serious. We can include it tomorrow.

Then batch is likely fine.

If the answer is:

> The dashboard should update later, but no operational action depends on it.

Then incremental batch or micro-batch may be fine.

If the answer is:

> A user may see the wrong recommendation.

Streaming may be justified.

If the answer is:

> A fraudulent transaction may be approved.

Streaming is probably necessary.

If the answer is:

> A patient safety alert may be missed.

Streaming or near-real-time architecture may be necessary, with serious reliability guarantees.

The business consequence of delay should drive architecture.

Not fashion.
Not vendor slides.
Not the engineer's desire to finally use Flink in anger.

---

## 11. The Architecture Question: What Happens If Data Is Wrong?

There is a second question:

> What happens if the data is wrong?

Streaming often optimizes latency. Batch often makes validation easier.

If wrong data is more dangerous than late data, batch may be preferable.

For example:

- regulatory reports;
- financial statements;
- clinical cohort definitions;
- scientific analyses;
- model training datasets;
- executive KPIs.

In these cases, it may be better to publish validated data at 07:00 than questionable data at 06:00.

Fast wrong data is not a feature.

It is just misinformation with good infrastructure.

Batch allows stronger pre-publication validation:

```
Extract data
    ↓
Transform data
    ↓
Run quality checks
    ↓
Compare with previous runs
    ↓
Approve or publish
    ↓
Notify consumers
```

Streaming validation exists, of course.

But continuous correctness is harder than bounded correctness.

Sometimes the right architecture is not the fastest one.

It is the one that fails safely.

---

## 12. Batch and Streaming Can Coexist

Real platforms often need both.

A common pattern is the Lambda Architecture:

```
Raw events
    ├── Batch layer for complete historical accuracy
    └── Speed layer for low-latency approximate or recent results
            ↓
        Serving layer combines both
```

This can work, but it may create duplicated logic: one implementation for batch and another for streaming.

That duplication is dangerous.

Another pattern is the Kappa Architecture:

```
Event log
    ↓
Stream processor
    ↓
Serving tables
```

The idea is to treat the event log as the source of truth and replay when needed.

This can simplify some systems but may be unsuitable when data sources are not naturally event streams or when batch snapshots remain important.

A more practical modern view is:

> Use the simplest processing model that satisfies the product requirement, and make batch and streaming share definitions where possible.

For example:

- stream raw events into a lakehouse;
- process near-real-time aggregates for operational dashboards;
- run daily batch jobs for audited business reporting;
- use the same metric definitions in both paths;
- reconcile streaming estimates with batch truth.

This is common.

The streaming layer serves immediacy.
The batch layer serves correctness and completeness.

They are not enemies.

They are different instruments.

Not every song needs drums at 200 BPM.

---

## 13. The "Real-Time Dashboard" Trap

Many teams ask for real-time dashboards.

Often they do not actually need real-time dashboards.

They need one of these:

- the dashboard should not be yesterday's data;
- the dashboard should refresh before the morning meeting;
- the dashboard should show current operational status;
- the dashboard should update every 15 minutes;
- the dashboard should feel responsive when filters are changed;
- the dashboard should not require someone to manually refresh a spreadsheet.

These are different requirements.

A dashboard can feel "real-time" to users if it is updated every 15 minutes and loads quickly.

Meanwhile, a truly streaming dashboard that takes 45 seconds to query may feel slow.

Freshness is only one part of user experience.

Dashboard usefulness depends on:

- freshness;
- query latency;
- metric trust;
- visual clarity;
- availability;
- consistency;
- interactivity.

A daily dashboard that is ready every morning and loads in two seconds may be more valuable than a streaming dashboard that updates constantly but nobody trusts.

Real-time confusion often begins with a vague sentence:

> "We need live data."

Before building, ask:

> Live enough for what decision?

That one question can save months.

---

## 14. The Healthcare Example: Batch Is Often the Responsible Choice

Healthcare data is a wonderful example because it punishes naive real-time enthusiasm.

Some healthcare workflows need near-real-time processing:

- ICU monitoring;
- patient safety alerts;
- medical device signals;
- emergency department capacity;
- infection surveillance in operational settings.

But many healthcare analytics workflows are naturally batch:

- cohort construction;
- claims analysis;
- hospital quality indicators;
- registry reporting;
- research datasets;
- phenotype extraction;
- retrospective outcomes analysis;
- genomic analysis releases;
- population-level dashboards.

For example, a weekly cohort table for cancer outcomes research does not need streaming. It needs clear definitions, reproducibility, quality checks, provenance, and stable snapshots.

Similarly, a genomic variant annotation pipeline may process large files through several stages:

```
FASTQ
    ↓
Alignment
    ↓
BAM/CRAM
    ↓
Variant calling
    ↓
VCF/BCF
    ↓
Annotation
    ↓
Curated analytical table
```

This is not naturally a streaming business problem.

It is a staged computational workflow.

Trying to "stream" this just because streaming sounds modern would be like putting racing stripes on a microscope.

The microscope remains unimpressed.

---

## 15. The Finance Example: Cutoffs Matter

Finance also shows why batch remains essential.

Financial reporting often depends on cutoffs:

- daily revenue close;
- monthly close;
- quarter-end reporting;
- invoice reconciliation;
- tax reporting;
- audit snapshots.

These processes need stable numbers.

A CFO does not want revenue changing every seven seconds during a board meeting because some late event arrived from a payment gateway.

The business may need a defined reporting state:

> These are the numbers as of close of business on this date, after reconciliation and validation.

That is batch thinking.

It creates a controlled version of reality.

Reality may keep changing, but the report needs a boundary.

This is not old-fashioned.

This is governance.

---

## 16. When Streaming Is Actually Worth It

Streaming is worth it when low latency changes the outcome.

Good candidates include:

### Fraud detection

The system must act before or during a transaction.

### Real-time personalization

Recommendations change while the user is active.

### Operational alerting

Teams need to know immediately when something abnormal happens.

### IoT and sensor systems

Events represent physical processes that must be monitored continuously.

### Real-time logistics

Routing, supply chain, delivery, and inventory systems may need rapid updates.

### Online ML features

Some models need features computed from very recent behavior.

### Security monitoring

Threat detection may depend on rapid event correlation.

In these cases, batch may be too slow.

The cost and complexity of streaming can be justified because the value of immediate action is high.

The key word is action.

If the system does not act differently because the data arrived faster, streaming may not be buying much.

---

## 17. When Batch Is Probably Better

Batch is probably better when:

- decisions are daily, weekly, or monthly;
- correctness matters more than immediacy;
- data arrives naturally in files or snapshots;
- sources update periodically;
- consumers need reproducible outputs;
- the team needs simple operations;
- cost matters more than ultra-low latency;
- backfills are common;
- late-arriving data is easier to handle in bounded windows;
- data quality validation is complex;
- workloads are analytical rather than operational.

Batch is especially strong when the question is:

> What happened?

Streaming is strongest when the question is:

> What is happening right now, and what must we do immediately?

Different questions. Different machinery.

---

## 18. The Role of Orchestration

Batch processing is often orchestrated.

Tools like Airflow, Dagster, Prefect, cloud-native schedulers, and warehouse-native task systems coordinate jobs over time.

A batch pipeline may look like this:

```
Wait for source files
    ↓
Validate raw input
    ↓
Load into bronze/raw tables
    ↓
Transform into silver/clean tables
    ↓
Build gold/business marts
    ↓
Run quality checks
    ↓
Publish datasets
    ↓
Notify consumers
```

This is an excellent fit for many business workflows.

Orchestration gives visibility:

- which task failed;
- which input was missing;
- which run produced which output;
- how long each step took;
- what can be retried;
- what depends on what.

Streaming orchestration is different.

A long-running streaming job may not have a simple daily "success" state. It may be healthy, lagging, checkpointing, recovering, or silently producing suspicious outputs.

Both models need orchestration and observability.

But batch workflows often make operational boundaries easier.

For many teams, that simplicity is not a weakness.

It is the difference between a platform people can operate and a platform people merely admire from a safe distance.

---

## 19. Incremental Batch: The Underappreciated Middle Path

Many teams do not need full streaming.

They need incremental batch.

Instead of processing all history, process only what changed.

For example:

```
Read new transactions from yesterday
Merge into transaction table
Update affected customer aggregates
Refresh daily revenue mart
```

Or:

```
Read records updated since last successful run
Validate changed records
Apply upserts
Recompute affected partitions
Publish updated table
```

This gives many benefits:

- lower cost;
- faster processing;
- simpler debugging than streaming;
- easier backfills;
- better freshness than daily full refresh;
- good compatibility with warehouses and lakehouses.

A simple conceptual incremental pipeline might use a watermark:

```python
last_processed_timestamp = read_pipeline_state("transactions")

new_records = source.read(
    where=f"updated_at > '{last_processed_timestamp}'"
)

validated_records = validate(new_records)

target.merge(
    source=validated_records,
    key="transaction_id"
)

write_pipeline_state(
    "transactions",
    max(validated_records.updated_at)
)
```

This is not as glamorous as a real-time event-processing engine.

But glamour is not an architecture requirement.

Incremental batch is often the boring correct answer.

And in data engineering, "boring correct answer" is a compliment of the highest order.

---

## 20. The Operational Maturity Test

Before adopting streaming, a team should ask some uncomfortable questions.

Can we monitor consumer lag?

Can we replay events safely?

Can we handle duplicates?

Can we handle late events?

Can we evolve schemas without breaking consumers?

Can we debug stateful processing?

Can we deploy streaming jobs without losing checkpoints?

Can we define exactly-once or idempotent output behavior?

Can we backfill historical data consistently?

Can we explain the output when streaming and batch numbers differ?

Can we afford the operational complexity?

If the answer to most of these is "not yet," streaming may still be possible, but the team should be careful.

Streaming is not just a technology choice.

It is an operational commitment.

It is adopting a pet dragon.

The dragon may fly beautifully.
It may also require specialized feeding, monitoring, and incident runbooks.

Do not adopt the dragon because someone said batch is dead.

---

## 21. The Cost Model

Batch and streaming often have different cost profiles.

Batch cost is usually concentrated.

You run compute for a period, then stop.

Streaming cost is continuous.

The system keeps running, consuming resources even when event volume is low.

This does not mean streaming is always more expensive. At high scale, streaming may be efficient and necessary. But for moderate workloads, continuous compute can be wasteful.

A simplified comparison:

| Dimension | Batch | Streaming |
|---|---|---|
| Compute pattern | Periodic | Continuous |
| Operational model | Runs and finishes | Always running |
| Debugging | Easier with bounded inputs | Harder with time/state |
| Freshness | Minutes to days | Milliseconds to minutes |
| Reproducibility | Strong natural fit | Requires careful design |
| Backfills | Usually straightforward | Requires replay strategy |
| Complexity | Lower to moderate | Moderate to high |
| Best for | Analytics/reporting | Operational reaction |

Architecture should consider total cost:

- infrastructure cost;
- engineering cost;
- incident cost;
- debugging cost;
- cognitive cost;
- governance cost;
- opportunity cost.

Sometimes a streaming architecture costs more than the problem it solves.

That is not innovation.

That is invoices wearing sunglasses.

---

## 22. The Correctness Model

Streaming correctness is subtle.

Suppose we compute purchases per user in 10-minute windows.

Questions appear immediately:

- What if an event arrives 20 minutes late?
- What if the same purchase event is sent twice?
- What if events arrive out of order?
- What if the payment is later refunded?
- What if the user ID is merged later?
- What if the schema changes?
- What if the stream processor restarts mid-window?
- What if the sink write succeeds but the checkpoint fails?

Batch has its own correctness challenges, of course.

But because the data is bounded, many checks are easier:

- count input records;
- count output records;
- validate uniqueness;
- compare totals;
- inspect partitions;
- rerun the batch;
- reproduce a specific run.

Streaming can be correct.

But correctness must be engineered deliberately.

When teams adopt streaming casually, they often end up with "fast approximate confusion."

That may be acceptable for operational estimates.

It is less acceptable for finance, compliance, and high-stakes analytics.

---

## 23. The Human Side: Streaming Can Increase Cognitive Load

Architecture affects people.

A batch pipeline is often easier for new engineers and analysts to understand:

```
Every morning, this job reads yesterday's data, transforms it, validates it, and publishes the daily table.
```

A streaming pipeline may require understanding:

- event time;
- processing time;
- watermarks;
- state;
- checkpoints;
- offsets;
- replay;
- idempotency;
- windows;
- triggers;
- sink guarantees;
- consumer lag.

This is not a reason to avoid streaming when it is needed.

But it is a reason not to use streaming casually.

Complexity is a tax paid by every future maintainer.

The person maintaining the system in 18 months may be you, someone junior, or a tired engineer at 02:00 reading logs with the emotional expression of a haunted spoon.

Be kind to that person.

Choose the simplest architecture that satisfies the requirement.

---

## 24. A Simple Decision Framework

Here is a practical way to decide.

### Step 1: Define freshness

Ask:

> How fresh must the data be to support the decision or action?

If the answer is days or hours, batch or incremental batch is likely enough.

If the answer is minutes, consider micro-batch or streaming.

If the answer is seconds or milliseconds, streaming is likely necessary.

### Step 2: Define consequence of delay

Ask:

> What happens if the data is late?

If the consequence is inconvenience, batch may be fine.

If the consequence is financial loss, user harm, fraud, or operational failure, lower-latency processing may be justified.

### Step 3: Define consequence of wrongness

Ask:

> What happens if the data is wrong?

If wrongness is more dangerous than lateness, prioritize validation, reproducibility, and controlled publishing.

### Step 4: Examine source behavior

Ask:

> Does the source produce events continuously, or snapshots periodically?

Do not force streaming onto naturally batch sources without a reason.

### Step 5: Estimate operational maturity

Ask:

> Can we operate this reliably?

A simple batch system operated well may outperform a sophisticated streaming system operated poorly.

### Step 6: Choose the least complex sufficient model

The hierarchy often looks like this:

```
Full batch
    ↓ if too slow or too expensive
Incremental batch
    ↓ if freshness still insufficient
Micro-batch
    ↓ if latency/action requirements demand it
Streaming
```

Do not jump to the last level unless the requirements deserve it.

Architecture is not a ladder where the top is always better.

Sometimes the best design is lower on the ladder, holding a sandwich and causing no incidents.

---

## 25. Example: Sales Dashboard

Suppose a company asks for a "real-time sales dashboard."

Before building streaming, ask what they mean.

Possible answers:

### Case A: Daily executive sales

The executive team checks sales every morning at 08:00.

Best fit:

```
Nightly batch
    ↓
Validated sales mart
    ↓
Dashboard refreshed before 07:30
```

Streaming is overkill.

### Case B: Sales operations monitoring

The operations team checks sales during the day and wants updates every 15 minutes.

Best fit:

```
Incremental or micro-batch ingestion
    ↓
Frequent aggregate refresh
    ↓
Dashboard cache update
```

Full streaming may still be unnecessary.

### Case C: Fraud-sensitive transaction monitoring

The system must detect suspicious payment behavior immediately.

Best fit:

```
Event stream
    ↓
Real-time fraud features
    ↓
Decision service / alerting
```

Streaming is justified.

Same phrase: "sales dashboard."
Three different architectures.

This is why requirements matter.

---

## 26. Example: Machine Learning Features

Machine learning pipelines often mix batch and streaming.

Offline training features are frequently batch:

```
Historical events
    ↓
Feature engineering
    ↓
Training dataset
    ↓
Model training
```

Online inference features may need streaming:

```
Recent user events
    ↓
Streaming feature computation
    ↓
Online feature store
    ↓
Real-time prediction
```

The important part is consistency.

Training and serving features should mean the same thing.

If offline features are computed in batch and online features are computed in streaming, the definitions must be aligned.

Otherwise, you get training-serving skew.

The model learns one version of reality and sees another in production.

This is generally considered bad, in the same way that "the bridge learned physics differently during deployment" is bad.

Batch and streaming can coexist, but shared semantics are essential.

---

## 27. Example: Data Platform Layers

A mature platform might support several processing modes.

```
                 ┌──────────────────────┐
                 │  Source Systems       │
                 └──────────┬───────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
 Batch ingestion      CDC / micro-batch      Event streams
        │                   │                   │
        ▼                   ▼                   ▼
 Raw lakehouse        Incremental tables     Streaming topics
        │                   │                   │
        └──────────────┬────┴──────────────┬────┘
                       ▼                   ▼
              Curated analytical     Real-time operational
                  datasets                views
                       │                   │
                       ▼                   ▼
                  BI / ML / reports    Alerts / online features
```

The platform does not need one universal processing style.

It needs clear patterns.

The problem is not having batch and streaming.

The problem is not knowing why each one exists.

---

## 28. Anti-Patterns

### Anti-pattern 1: Streaming because it sounds modern

This is architecture by LinkedIn headline.

Avoid.

### Anti-pattern 2: Batch because the team fears streaming

Sometimes low latency is genuinely required.

Avoid hiding behind simplicity when the product needs immediacy.

### Anti-pattern 3: Real-time raw data, slow curated data

A platform ingests events in seconds but updates business metrics once per day.

This may be fine if intentional.

It is bad if everyone assumes ingestion freshness equals analytical freshness.

### Anti-pattern 4: Two definitions of the same metric

The streaming dashboard says one thing.
The batch report says another.
Nobody knows which one is correct.

This is how trust goes to a farm upstate.

### Anti-pattern 5: Streaming without replay

If you cannot replay events, recover state, or rebuild outputs, your streaming system may become fragile.

### Anti-pattern 6: Batch without incrementality

If every run recomputes everything forever, batch may become unnecessarily slow and expensive.

Batch is good. Wasteful batch is not.

---

## 29. The Best Architecture Is Usually Boring

A lot of excellent data engineering looks boring from the outside.

A daily job runs.
It validates inputs.
It writes partitioned tables.
It updates marts.
It publishes metrics.
It alerts on freshness.
It supports backfills.
It documents ownership.
It does not wake anyone up.

Beautiful.

Not every system needs to be a cathedral of distributed event processing.

Sometimes the best platform feature is:

> The numbers are correct every morning.

That sounds simple.

It is not always easy.

But it is valuable.

Engineering maturity is not choosing the most advanced tool.

Engineering maturity is choosing the right tool and making it reliable.

---

## 30. Final Thought

Batch is not dead.

Bad batch is dead.

Or at least, it should be.

The old style of batch - giant opaque nightly jobs, no observability, no contracts, no ownership, no incremental logic, no validation, no clear freshness expectations - deserves criticism.

But modern batch is different.

Modern batch can be:

- incremental;
- observable;
- contract-aware;
- versioned;
- orchestrated;
- reproducible;
- cost-efficient;
- lakehouse-native;
- warehouse-native;
- connected to data quality checks;
- aligned with business freshness needs.

Streaming is also powerful.

But streaming should be used when low latency changes the outcome enough to justify the complexity.

The goal is not batch everywhere.
The goal is not streaming everywhere.

The goal is architectural honesty.

Ask what the data product needs.
Ask how fresh the data must be.
Ask what happens if it is late.
Ask what happens if it is wrong.
Ask who will operate the system.
Ask whether complexity is buying value or merely wearing a cool jacket.

Sometimes the answer will be streaming.

Sometimes the answer will be incremental batch.

Sometimes the answer will be a calm nightly job that runs at 03:00, validates everything, publishes at 07:00, and lets the organization start the day with trustworthy numbers.

Batch is dead?

No.

Batch just stopped trying to impress people at conferences.

Long live batch.
