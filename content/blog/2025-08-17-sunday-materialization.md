Title: The Sunday Materialization - Why Your Data Platform Feels Slow
Subtitle: When Nothing Is Broken, But Everything Feels Like Walking Through Syrup
Date: 2025-08-17 07:00
Modified: 2025-08-17 07:00
Category: Sunday
Tags: data engineer, data platform engineer, data, data architecture, performance, latency, observability, data pipelines, platform engineering
Slug: sunday-materialization-slow-data-platform
Authors: Eduardo G Gusmao
Summary: A weekly educational topic/lecture/discussion on Data Engineering topics that we all experienced at least once (or will!)
Status: final
Lang: en
Template: topic
Cadence: Biweekly
Scope: Data Engineering, Industry, Data Challenges
Tone: Analytical, Educational, Non-Sensational
Canonical: https://www.gusmaolab.org/blog/sunday-materialization-slow-data-platform/
Meta_description: Biweekly analysis of important Data Engineering concepts.
Meta_keywords: data concepts, topics, lectures, discussions, data platform performance, data latency, observability
Cover: images/covers/slow-data-platform.png
Thumbnail: images/thumbnails/slow-data-platform-thumb.png

# Why Your Data Platform Feels Slow Even When Nothing Is “Broken”

There is a special kind of data platform pain that does not announce itself with a red dashboard.

No failed DAG.
No crashed Spark job.
No unavailable warehouse.
No angry exception trace with the emotional stability of a cursed scroll.

Everything is technically working.

And yet, the platform feels slow.

Dashboards take too long to refresh.
Pipelines finish, but not when people need them.
Analysts wait for tables.
Data scientists wait for features.
Product teams wait for metrics.
Executives wait for “the latest number.”
The data engineering team says, honestly, “Nothing is failing.”
The business says, also honestly, “This is unusable.”

Both sides are right.

That is what makes this problem interesting.

A slow data platform is often not slow because one thing is broken. It is slow because many individually reasonable things accumulate into a system that behaves like it has ankle weights.

Performance problems in data platforms are rarely just technical. They are usually architectural, operational, organizational, and semantic at the same time.

In other words: the villain is not always one bad query.

Sometimes the villain is the entire shape of the platform.

---

## 1. Broken Is Easy. Slow Is Political.

When something breaks, the system gives you a clear signal.

A task fails.
A table is missing.
A service returns an error.
A job exceeds memory limits.
A Kafka consumer stops consuming.
A warehouse query fails.

This is painful, but at least it is visible.

Slowness is harder.

A slow platform can keep producing outputs. It can pass tests. It can satisfy service-level agreements on paper. It can be “green” in every dashboard while still making everyone miserable.

That is because slowness is often experienced at the human workflow level, not just the machine level.

For example:

- the pipeline completes in four hours, but the business needs the data in one;
- the dashboard loads in twenty seconds, but users expect three;
- a feature table is updated daily, but model retraining needs hourly freshness;
- an ad hoc query runs successfully, but takes so long nobody wants to explore;
- incident recovery works, but requires three engineers and a goat sacrifice.

Nothing is broken in the narrow technical sense.

But the platform is failing in the practical sense.

A system can be available and still be too slow to be useful.

That is a brutal little sentence. We should keep it nearby.

---

## 2. The First Question: Slow for Whom?

Before optimizing anything, ask:

> Who experiences the platform as slow?

This matters because “slow” is not one metric.

For a data engineer, slow may mean a Spark job taking six hours.

For an analyst, slow may mean a dashboard taking thirty seconds.

For a data scientist, slow may mean waiting two days for a training dataset.

For a product manager, slow may mean yesterday’s experiment metrics are still unavailable.

For compliance, slow may mean a required report takes too long to reproduce.

For finance, slow may mean month-end numbers are delayed.

Same platform. Different pain.

So the first job is not tuning.
The first job is diagnosis.

A useful classification is:

| User | What “slow” usually means |
|---|---|
| Data engineer | Long pipeline runtime, shuffle bottlenecks, retry storms |
| Analytics engineer | Slow model builds, excessive dependencies, warehouse contention |
| Analyst | Slow dashboards, blocked exploration, stale marts |
| Data scientist | Slow feature generation, expensive joins, missing reusable datasets |
| Product team | Metrics arrive too late for decisions |
| Executives | Trusted numbers are not available when needed |
| Platform team | Too much manual intervention and operational drag |

If you do not know who is suffering, you will optimize the wrong layer.

And nothing says “enterprise comedy” like spending two weeks optimizing a Spark join while the real problem was that the dashboard refresh schedule was misaligned with the business meeting.

---

## 3. Latency Is Not One Thing

A common mistake is treating platform slowness as a single latency problem.

But data latency has many layers.

### Source latency

How long until the data exists in the source system?

Example: a hospital system may only export files once per day. No downstream architecture can make that truly real-time. You cannot stream yesterday’s batch file by believing harder.

### Ingestion latency

How long until the platform receives the data?

This includes API polling, file arrival, CDC replication, queue consumption, vendor delivery, and extraction windows.

### Processing latency

How long do transformations take?

This includes Spark jobs, dbt models, SQL transformations, feature pipelines, quality checks, enrichment, deduplication, and aggregations.

### Orchestration latency

How long does the system wait between tasks?

This is the silent villain: schedules, sensors, dependencies, retries, backfills, queue availability, and poor DAG design.

### Serving latency

How long until users can query the final data?

This includes warehouse performance, BI cache refresh, semantic layer updates, materialized views, indexing, clustering, and access patterns.

### Decision latency

How long until the data reaches the person who needs it?

This is the human-facing end of the system. If data is ready at 07:00 but nobody sees it until 14:00 because the report is buried in a tool nobody checks, the platform still feels slow.

A platform can optimize one latency layer and still feel bad overall.

That is why “the Spark job is fast now” is not always a solution.

It may be true.
It may also be irrelevant.

---

## 4. The Platform Is Slow Because Everything Is Waiting for Everything Else

One of the most common causes of slowness is excessive dependency chaining.

A simplified platform might look like this:

"""
Raw ingestion
    ↓
Bronze tables
    ↓
Silver cleaned tables
    ↓
Gold business marts
    ↓
Feature tables
    ↓
Dashboards
    ↓
Executive reports
"""

This looks reasonable.

But in practice, the dependency graph may become a giant plate of spaghetti wearing a tiny architect hat.

A dashboard depends on a mart.
The mart depends on five intermediate models.
Those models depend on twenty staging tables.
Those staging tables depend on six ingestion jobs.
One ingestion job waits for a vendor file.
The vendor file arrives late.
Everything waits.

Nothing is broken.

But the entire platform now moves at the speed of the slowest upstream dependency.

This is especially dangerous when teams create “god tables” or “universal marts” that try to serve everyone.

At first, these tables feel convenient.

Later, they become bottlenecks.

Everyone depends on them.
Nobody wants to change them.
They take forever to build.
They contain columns used by three people in 2021 and feared by everyone since.

The platform feels slow because the architecture has too many shared choke points.

---

## 5. The Hidden Cost of Over-Batching

Batch processing is not bad.

Batch processing is wonderful when the business rhythm matches the data rhythm.

Daily revenue report? Batch is fine.
Monthly compliance extract? Batch is fine.
Weekly model retraining? Batch is fine.
Large historical backfill? Batch is your loyal tractor.

But many platforms become slow because everything is treated as one big batch, even when only a small part of the data changed.

This creates unnecessary work.

Imagine rebuilding a full customer mart every hour because 0.3% of customers changed.

That is not engineering.
That is cardio for computers.

Better patterns include:

- incremental processing;
- change data capture;
- partition-aware updates;
- merge/upsert strategies;
- streaming ingestion with batch serving;
- materialized aggregates;
- stateful transformations;
- event-driven triggers.

The point is not “stream everything.”

That is another common mistake.

The point is:

> Match the processing strategy to the freshness requirement and data-change pattern.

Some data should be batch.
Some data should be incremental.
Some data should be streaming.
Some data should be computed once and left alone like a sleeping cat.

---

## 6. The Platform Is Slow Because It Recomputes the Past

A classic source of slowness is repeatedly recomputing historical data.

This happens when pipelines do not distinguish between:

- new data;
- changed data;
- historical immutable data;
- late-arriving data;
- corrected data.

A naive pipeline may process everything every time.

"""
Read all historical transactions
Clean all transactions
Join all transactions to all customers
Aggregate all transactions by customer
Write complete output table
"""

This is simple.

It is also a good way to turn your platform into a space heater.

A more mature pipeline asks:

- Which partitions changed?
- Which records are new?
- Which records were corrected?
- Which downstream aggregates are affected?
- Can we update only those?
- Do we need a full rebuild, or only a targeted refresh?

This is where table formats and warehouse features matter.

Lakehouse formats such as Delta Lake, Apache Iceberg, and Apache Hudi became important partly because they support more controlled updates, snapshots, schema evolution, time travel, and incremental patterns.

But the tool alone does not solve the design.

You can use a modern table format and still rebuild the universe every morning because the DAG was written during a spiritually difficult sprint.

---

## 7. Queries Are Slow Because Storage Was Not Designed for Access

A platform can ingest and transform data beautifully, then serve it terribly.

This usually happens when data layout ignores access patterns.

For example:

- tables are not partitioned by common filters;
- files are too small;
- files are too large;
- clustering does not match query patterns;
- frequently joined keys are poorly organized;
- dashboards scan massive raw tables;
- users query nested semi-structured data directly;
- statistics are stale;
- indexes or materialized views are missing where appropriate.

The result:

> The data exists, but every query has to dig through a mountain to find a spoon.

In analytical systems, storage layout matters enormously.

A few practical questions help:

- What are the most common filters?
- What are the most common joins?
- What are the most common dashboard queries?
- Which tables are scanned most often?
- Which columns are selected most often?
- Which queries are repeated every day?
- Which workloads are exploratory versus production?
- Which queries need fresh data and which can use cached data?

If nobody asks these questions, the platform may be technically correct but physically inefficient.

Data architecture is not only logical modeling.

It is also arranging bytes so that the system does not need to perform interpretive dance for every query.

---

## 8. The Small Files Problem: Death by a Thousand Parquets

In data lakes and lakehouses, one famous cause of slowness is the small files problem.

Distributed systems like parallelism, but they do not like managing millions of tiny files.

If each file is tiny, the engine spends too much time on metadata, listing, scheduling, opening, and planning rather than actual computation.

The symptoms are familiar:

- queries take a long time to start;
- metadata operations are slow;
- Spark jobs have too many tiny tasks;
- object storage listing becomes expensive;
- compaction becomes necessary;
- partition directories become chaotic little museums of bad decisions.

This often happens with streaming writes, frequent micro-batches, high-cardinality partitions, or poorly configured ingestion jobs.

A common simplified pattern:

"""
Too many tiny files
    ↓
Too much metadata overhead
    ↓
Too many tasks
    ↓
Slow planning and execution
    ↓
Users wonder why a simple query takes forever
"""

Solutions include:

- file compaction;
- optimized write sizes;
- partition strategy review;
- clustering or ordering;
- avoiding high-cardinality partitions;
- periodic maintenance jobs;
- table format optimization commands.

The principle is simple:

> Analytical engines like fewer, reasonably sized files more than a confetti cannon of tiny files.

A data lake should not look like someone dropped a bag of rice into S3.

---

## 9. The Platform Is Slow Because It Has No Workload Isolation

Another subtle cause: everyone shares the same compute resources.

Scheduled pipelines, BI dashboards, ad hoc analyst queries, data science experiments, backfills, and executive reports all compete for the same cluster or warehouse.

Then someone runs a massive exploratory query at 08:55.

At 09:00, the CEO opens the dashboard.

The dashboard spins.

A meeting becomes theatre.

Nothing is broken.
The platform is just congested.

This is a workload management problem.

Useful strategies include:

- separate compute for production pipelines;
- separate compute for BI dashboards;
- separate compute for exploration;
- priority queues;
- concurrency limits;
- autoscaling policies;
- query timeouts;
- budget controls;
- workload-specific warehouses or clusters;
- resource tagging and chargeback/showback.

The deeper lesson:

> A shared data platform needs traffic rules.

Without workload isolation, the platform behaves like a city where ambulances, bicycles, buses, trucks, and drunk scooters all share one lane.

Technically democratic. Operationally cursed.

---

## 10. Orchestration Can Make Fast Tasks Feel Slow

Sometimes each individual task is reasonably fast, but the workflow is slow.

This is orchestration latency.

Example:

"""
Task A: 5 minutes
Task B: 7 minutes
Task C: 4 minutes
Task D: 6 minutes
Total expected: maybe 22 minutes
Actual DAG runtime: 90 minutes
"""

Why?

Possible reasons:

- tasks are unnecessarily sequential;
- sensors wait too long;
- retries use excessive delay;
- tasks wait in a saturated queue;
- dependencies are too broad;
- one upstream task blocks unrelated downstream tasks;
- schedules are misaligned;
- backfills interfere with current runs;
- external data arrival is not handled efficiently.

A DAG may look organized but behave slowly because it encodes unnecessary waiting.

For example, if three transformations are independent but run sequentially, the platform is donating time to the void.

Better design:

"""
        ┌── Model B ──┐
Raw ────┼── Model C ──┼── Final mart
        └── Model D ──┘
"""

Instead of:

"""
Raw
 ↓
Model B
 ↓
Model C
 ↓
Model D
 ↓
Final mart
"""

Parallelism is not free, but artificial sequentiality is expensive.

A good orchestration design asks:

- What must wait?
- What can run independently?
- What can be event-driven?
- What can be skipped if inputs did not change?
- What should be retried?
- What should fail fast?
- What should degrade gracefully?

The orchestrator should coordinate work, not create a bureaucratic queue where tasks stand in line holding tiny forms.

---

## 11. Data Quality Checks Can Become the Bottleneck

Data quality is essential.

But poorly designed quality checks can slow a platform dramatically.

Examples:

- full-table scans for every run;
- expensive uniqueness checks on huge tables;
- referential integrity checks across massive datasets;
- repeated validations on unchanged partitions;
- row-by-row validation in Python;
- quality checks running after all transformations instead of earlier;
- checks that block pipelines without severity levels.

The solution is not “remove quality checks.”

That is how we summon chaos.

The solution is designing quality checks with performance and criticality in mind.

A good approach separates:

### Critical blocking checks

These prevent dangerous data from being published.

Examples:

- required columns missing;
- primary key completely broken;
- freshness outside acceptable range;
- severe schema violation.

### Warning checks

These alert but do not necessarily block.

Examples:

- null rate increased slightly;
- volume lower than expected;
- distribution changed moderately.

### Exploratory checks

These are useful for analysis but should not sit directly in the critical path.

Examples:

- detailed profiling;
- expensive distribution comparisons;
- full anomaly reports.

Quality should be layered.

Do not put every possible check on the main highway.

Some checks are traffic lights.
Some are road signs.
Some belong in a weekly inspection report.
Not every check needs to jump in front of the car.

---

## 12. The Dashboard Is Slow Because the Data Model Is Wrong

BI slowness is often blamed on the BI tool.

Sometimes that is fair.

But often the real problem is the serving model.

Dashboards become slow when they query data that is too raw, too large, too flexible, or too poorly modeled.

A dashboard should usually not need to perform heavy business logic at read time.

If every dashboard load requires:

- joining ten tables;
- filtering raw events;
- computing business metrics;
- resolving slowly changing dimensions;
- deduplicating records;
- parsing JSON fields;
- calculating rolling windows;
- applying complex permissions;

then the dashboard is no longer a dashboard.

It is an emotional support ETL pipeline.

Better patterns include:

- curated marts;
- aggregate tables;
- semantic layers;
- materialized views;
- precomputed metrics;
- dimensional modeling;
- cache-aware dashboard design;
- query reduction;
- separating interactive and heavy analytical workloads.

The goal is not to remove flexibility.

The goal is to avoid making every user pay the full computational cost of business logic every time they click a filter.

Dashboards should serve decisions, not reenact the entire data pipeline in miniature.

---

## 13. Freshness Expectations Are Often Undefined

Sometimes the platform feels slow because nobody agreed what “fresh” means.

One team expects data every five minutes.
Another team thinks daily is fine.
The pipeline runs every six hours.
The dashboard says “latest.”
Nobody knows what latest means.
Everyone becomes mildly suspicious.

Freshness needs explicit definitions.

For example:

| Dataset | Freshness expectation |
|---|---|
| Fraud alerts | Seconds to minutes |
| Product usage dashboard | 15–60 minutes |
| Sales dashboard | Hourly or daily |
| Financial close report | Daily or monthly |
| Historical cohort table | Weekly or on demand |
| Regulatory extract | Scheduled, reproducible, audited |

Not every dataset needs real-time freshness.

In fact, forcing real-time architecture onto slow-moving business processes is a wonderful way to spend money and age visibly.

But critical datasets should have clear freshness expectations.

A practical contract might say:

"""
dataset: daily_revenue_summary
freshness:
  expected_by: "07:00"
  timezone: "America/Recife"
  max_delay_minutes: 30
  severity_if_late: "warning"
  owner: "finance-data-platform"
"""

This gives everyone a shared language.

Without freshness definitions, “slow” becomes a feeling.

And feelings are hard to debug.

---

## 14. Observability: You Cannot Optimize What You Cannot See

A platform that feels slow often lacks good observability.

You need to know where time is going.

Useful observability dimensions include:

- pipeline runtime;
- task-level duration;
- queue waiting time;
- retry count;
- input data volume;
- output data volume;
- shuffle size;
- skew indicators;
- query runtime;
- warehouse concurrency;
- cache hit rate;
- data freshness;
- SLA/SLO violations;
- downstream consumer impact;
- cost per workload.

The important trick is to separate:

### Execution time

How long the task actually ran.

### Waiting time

How long it waited before running.

### Data delay

How long before input data arrived.

### Availability delay

How long before output was usable.

A job may execute in ten minutes but wait in a queue for fifty.

If you only measure execution time, you will optimize the wrong thing.

A good platform dashboard should answer:

- Which datasets are late?
- Which tasks are slowest?
- Which tasks are most variable?
- Which jobs are waiting, not running?
- Which queries consume the most resources?
- Which downstream assets are affected?
- Which workloads are getting slower over time?

Otherwise, performance work becomes folklore.

And folklore is charming in literature, not in production operations.

---

## 15. The Difference Between Throughput and Latency

A platform can have high throughput and still feel slow.

Throughput asks:

> How much data can we process?

Latency asks:

> How quickly can a specific result become available?

These are not the same.

A nightly batch platform may process terabytes efficiently. Great throughput.

But if a user needs updated fraud features in five minutes, the platform is too slow for that use case.

Likewise, a streaming platform may provide low-latency events but struggle with huge historical backfills.

Good architecture does not maximize one metric blindly.

It matches system design to workload needs.

Some workloads need:

- low latency;
- high throughput;
- high concurrency;
- reproducibility;
- low cost;
- strong consistency;
- eventual consistency;
- interactive exploration;
- batch reliability.

You rarely get all of them at once.

Platform engineering is the art of deciding which trade-offs are acceptable, making them explicit, and preventing every workload from being forced through the same pipe.

---

## 16. Cost Optimization Can Make Platforms Slow

A painful truth:

Sometimes the platform feels slow because it was optimized too aggressively for cost.

Examples:

- clusters are too small;
- autoscaling is too conservative;
- warehouses suspend too quickly;
- spot instances interrupt important workloads;
- concurrency is limited;
- compaction jobs are skipped;
- maintenance tasks are delayed;
- production and exploration share underpowered compute;
- pipelines run serially to save resources.

Cost control is necessary.

But if cost optimization creates constant waiting, delayed decisions, and engineer firefighting, the savings may be fake.

The real cost of a slow platform includes:

- lost analyst time;
- delayed business decisions;
- lower trust;
- manual workarounds;
- duplicated datasets;
- shadow pipelines;
- failed experiments;
- operational stress;
- missed opportunities.

A slow platform often creates hidden cost outside the cloud bill.

This does not mean “spend wildly.”

It means cost optimization should consider business value and human time.

A cheap platform that nobody can use is not efficient.

It is just inexpensive sadness.

---

## 17. The Danger of Shadow Data Platforms

When the official platform feels slow, users create workarounds.

They export CSVs.
They build local notebooks.
They create spreadsheet pipelines.
They copy data into personal databases.
They run unscheduled scripts.
They create “temporary” tables that live for three years and acquire political importance.

This is how shadow data platforms are born.

Shadow platforms are often a symptom, not merely a governance failure.

They appear when the official path is too slow, too rigid, too expensive, or too hard to use.

The correct response is not only “ban the spreadsheets.”

The correct response is to ask:

> What need is the shadow system satisfying that the official platform does not?

Maybe users need:

- faster access;
- easier exploration;
- simpler publishing;
- temporary sandboxes;
- self-service datasets;
- clearer ownership;
- better documentation;
- shorter turnaround time.

A good data platform reduces the need for shadow systems by making the correct path usable.

Governance without usability creates rebellion.

And in data, rebellion usually has `.xlsx` at the end.

---

## 18. A Practical Diagnostic Framework

When a platform feels slow, investigate in layers.

### Layer 1: User pain

Ask:

- Who says it is slow?
- What are they trying to do?
- What response time do they expect?
- What happens when it is late?
- Is the pain constant or occasional?

### Layer 2: Freshness

Ask:

- When does source data arrive?
- When is processed data available?
- What are the freshness expectations?
- Which datasets are regularly late?

### Layer 3: Orchestration

Ask:

- Where do tasks wait?
- Which dependencies are unnecessary?
- Which tasks could run in parallel?
- Which sensors or retries add delay?
- Are schedules aligned with business needs?

### Layer 4: Processing

Ask:

- Which jobs consume most runtime?
- Are jobs incremental?
- Are we recomputing unchanged history?
- Are joins skewed?
- Are shuffles excessive?
- Are partitions sensible?

### Layer 5: Storage

Ask:

- Are files too small?
- Are tables partitioned and clustered appropriately?
- Are statistics maintained?
- Are high-usage tables optimized?
- Are old snapshots or metadata slowing operations?

### Layer 6: Serving

Ask:

- Are dashboards querying curated models?
- Are metrics precomputed?
- Are common queries cached or materialized?
- Are users scanning raw data unnecessarily?

### Layer 7: Workload management

Ask:

- Are production and exploration isolated?
- Is concurrency sufficient?
- Are critical workloads prioritized?
- Are backfills interfering with current workloads?

### Layer 8: Governance and ownership

Ask:

- Who owns performance for each data product?
- Are SLOs defined?
- Are expectations documented?
- Are consumers informed about delays?

This framework prevents random optimization.

Random optimization is how teams spend three days tuning a job that contributes 2% of user-perceived latency.

Very educational. Not always useful.

---

## 19. Performance Is a Product Feature

A data platform is not just infrastructure.

It is a product used by internal customers.

Performance is part of that product.

A dashboard that loads in two seconds feels different from one that loads in twenty.

A feature table available at 07:00 creates different behavior from one available at 11:30.

A self-service dataset that is easy to query creates different culture from one that requires asking the data team for help every time.

Platform performance shapes behavior.

Fast platforms encourage exploration.
Slow platforms encourage hoarding.
Fast platforms increase trust.
Slow platforms create screenshots in Slack.
Fast platforms make data feel alive.
Slow platforms make data feel ceremonial.

This is why performance is not only a backend concern.

It is part of the user experience of data.

---

## 20. Final Thought

A data platform can be slow even when nothing is broken because slowness often emerges from the system as a whole.

Not one failed job.
Not one bad query.
Not one missing index.
Not one underpowered cluster.

Instead, it comes from accumulated friction:

- unclear freshness expectations;
- excessive dependency chains;
- over-batching;
- recomputing history;
- poor storage layout;
- small files;
- weak workload isolation;
- inefficient orchestration;
- expensive quality checks;
- dashboard logic pushed too late;
- missing observability;
- cost decisions that ignore human waiting time.

The fix is not simply “make Spark faster” or “buy a bigger warehouse.”

The fix is to understand the platform as a living system of producers, consumers, contracts, workloads, storage, compute, orchestration, and expectations.

A slow data platform is trying to tell you something.

Sometimes it says: “Your partitions are bad.”
Sometimes it says: “Your DAG dependencies are too broad.”
Sometimes it says: “Your dashboards are doing transformation work.”
Sometimes it says: “Your organization never agreed what fresh means.”

And sometimes it says:

> “I am not broken. I am designed exactly this way. That is the problem.”

That is the moment where data engineering becomes data platform engineering.

Because the goal is not only to make pipelines run.

The goal is to make data arrive, transform, serve, and support decisions at the speed the organization actually needs — without turning the platform team into permanent firefighters with SQL-shaped helmets.

Nothing may be broken.

But if everyone is waiting, something still needs to be fixed.
