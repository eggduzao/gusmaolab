Title: The Sunday Materialization - Separation of Compute and Storage
Subtitle: The Reality, Not the Hype, Behind the Cloud Data Platform's Favorite Promise
Date: 2025-11-23 07:00
Modified: 2025-11-23 07:00
Category: Sunday
Tags: data engineer, data platform engineer, data, data architecture, compute storage separation, cloud data platforms, lakehouse, warehouse, scalability
Slug: sunday-materialization-separation-compute-storage
Authors: Eduardo G Gusmao
Summary: A weekly educational topic/lecture/discussion on Data Engineering topics that we all experienced at least once (or will!)
Status: final
Lang: en
Template: topic
Cadence: Biweekly
Scope: Data Engineering, Industry, Data Challenges
Tone: Analytical, Educational, Non-Sensational
Canonical: https://www.gusmaolab.org/blog/sunday-materialization-separation-compute-storage/
Meta_description: Biweekly analysis of important Data Engineering concepts.
Meta_keywords: data concepts, topics, lectures, discussions, compute storage separation, cloud data platforms, lakehouse, warehouse
Cover: images/covers/separation-compute-storage.png
Thumbnail: images/thumbnails/separation-compute-storage-thumb.png

# Separation of Compute and Storage - The Reality, Not the Hype

There are phrases in data engineering that sound so clean they almost feel suspicious.

"Serverless."
"Lakehouse."
"Zero-copy."
"Real-time."
"Single source of truth."
"Separation of compute and storage."

That last one is one of the most important architectural shifts in modern data platforms.

It is also one of the most over-simplified.

The usual pitch is elegant:

> Store data cheaply in one place. Scale compute independently whenever you need it.

That sounds wonderful.

And honestly, it often is wonderful.

Separating compute and storage is one reason modern cloud warehouses, lakehouses, query engines, and data platforms can scale so flexibly. It allows multiple engines to read the same data. It allows storage to grow without keeping idle clusters alive. It allows teams to create different compute pools for different workloads. It allows the platform to support batch, BI, ML, exploration, and backfills without pretending one cluster should do everything.

But there is a catch.

Actually, several catches.

Separating compute and storage does not remove complexity.

It moves complexity.

Sometimes it moves complexity from infrastructure to metadata.
Sometimes from clusters to network I/O.
Sometimes from storage cost to query cost.
Sometimes from hardware provisioning to workload governance.
Sometimes from "we cannot scale" to "we scaled and now the bill is writing poetry."

So this post is not about the hype.

This is about the practical reality.

Separation of compute and storage is powerful. But like most powerful architectural ideas, it works best when you understand what it gives you, what it costs you, and what it absolutely does not magically solve.

---

## 1. The Old World: Compute and Storage Together

In older data systems, compute and storage were often tightly coupled.

A database, Hadoop cluster, or analytical appliance might have a fixed set of machines. Those machines provided both:

* CPU and memory for processing;
* disks for storing data.

A simplified cluster looked like this:

```text
Node 1: compute + storage
Node 2: compute + storage
Node 3: compute + storage
Node 4: compute + storage
```

This architecture has advantages.

Data is physically close to compute.
Local disk access can be fast.
The system can optimize around known hardware.
Data locality becomes a real performance feature.

But it also creates constraints.

If you need more storage, you may need to add more nodes - even if you do not need more compute.

If you need more compute, you may need to add more nodes - even if you do not need more storage.

If the cluster is idle, storage and compute may still be tied to running infrastructure.

If one workload consumes the cluster, other workloads suffer.

This coupling can become expensive and rigid.

Example:

> Your historical data grows by 10x, but query volume stays the same. In a coupled architecture, scaling storage may also mean scaling compute you do not need.

Or:

> Your analysts run heavy queries during business hours, but ingestion mostly happens overnight. You may need enough cluster capacity for peak workloads, even if most of it sits underused later.

The old world was not stupid.

It was often efficient for its time and hardware assumptions.

But cloud platforms changed the economic and architectural terrain.

---

## 2. The Modern Promise: Store Once, Compute Many Ways

In modern cloud data platforms, storage is often placed in a separate durable storage layer.

Examples include object storage systems such as:

* Amazon S3;
* Azure Data Lake Storage;
* Google Cloud Storage;
* MinIO or S3-compatible storage in private/cloud-native setups.

Compute engines then read from and write to that storage.

A simplified architecture:

```text
                  ┌──────────────────────┐
                  │   Object Storage      │
                  │   Data files/tables   │
                  └──────────┬───────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        ▼                    ▼                    ▼
   Spark cluster        SQL warehouse        ML workload
        │                    │                    │
        ▼                    ▼                    ▼
 Batch processing       BI queries        Feature generation
```

The data lives in storage.

Compute comes and goes.

This is the foundation behind many modern patterns:

* cloud data warehouses;
* data lakes;
* lakehouses;
* serverless query engines;
* independent SQL warehouses;
* elastic Spark clusters;
* multi-engine analytics;
* workload-specific compute pools.

The promise is:

> Data persists independently. Compute is rented when needed.

This is a big deal.

It changes platform design.

It means a team can store huge amounts of data without keeping huge compute clusters running all the time.

It means different workloads can use different compute profiles.

It means one dataset can serve multiple consumers.

It means the platform can scale storage and compute differently.

That is the good part.

And it is genuinely good.

---

## 3. What "Separation" Really Means

Separation of compute and storage does not mean compute and storage have no relationship.

It means they are **independently managed and scaled**.

Storage handles persistence.

Compute handles processing.

But compute still needs to read data from storage, write results back, inspect metadata, cache files, maintain table state, and coordinate with catalogs.

So the relationship becomes:

```text
Compute:
    ephemeral, scalable, workload-specific

Storage:
    durable, shared, persistent

Metadata/catalog:
    tells compute what data exists, where it is, and how to interpret it
```

That third piece - metadata - is often underappreciated.

Once compute and storage are separated, metadata becomes the glue.

Without good metadata, compute engines do not know:

* which files belong to a table;
* which snapshot is current;
* what schema applies;
* which partitions exist;
* which files can be skipped;
* who has permission;
* which data is stale;
* which version should be read.

In a separated architecture, you should think in three layers:

```text
Compute layer
    Spark, SQL warehouses, Trino, Flink, Python jobs, BI engines

Metadata/catalog layer
    table formats, transaction logs, catalogs, schemas, permissions, lineage

Storage layer
    object storage, files, snapshots, historical data
```

The hype often talks about two layers.

The real platform has at least three.

And the metadata layer is where many dragons live.

Not evil dragons.

Administrative dragons.

Worse.

---

## 4. The Main Benefit: Independent Scaling

The most obvious benefit is independent scaling.

Suppose your storage needs grow.

You can store more data in object storage without necessarily increasing compute.

Suppose your compute needs grow temporarily.

You can spin up more compute without permanently changing storage.

Example:

```text
Normal day:
    1 small SQL warehouse
    1 medium Spark cluster

Month-end close:
    3 SQL warehouses
    2 large Spark clusters
    1 temporary backfill cluster

After month-end:
    shut temporary compute down
    keep storage unchanged
```

That flexibility is powerful.

It supports bursty workloads.

Data platforms are often bursty:

* analysts query heavily during business hours;
* batch jobs run overnight;
* backfills happen occasionally;
* ML training runs periodically;
* dashboards refresh around meetings;
* finance has month-end and quarter-end spikes;
* incident recovery may need temporary extra compute.

In a tightly coupled architecture, you may provision for the peak.

In a separated architecture, you can often scale compute for the peak and release it later.

That is the dream.

Of course, dreams have invoices.

But the architectural flexibility is real.

---

## 5. The Second Benefit: Workload Isolation

Separation of compute and storage makes workload isolation easier.

If multiple teams share one cluster, they compete.

Analysts, pipelines, dashboards, ML jobs, and backfills all fight for the same resources.

That leads to familiar pain:

* dashboards become slow during backfills;
* ingestion jobs delay analyst queries;
* analyst experiments slow production workloads;
* one huge query consumes cluster memory;
* everyone learns the phrase "resource contention" emotionally.

With separated compute, you can create different compute pools.

Example:

```text
Shared storage:
    curated warehouse/lakehouse tables

Compute pools:
    BI warehouse
    ELT warehouse
    ML feature cluster
    Ad hoc exploration cluster
    Backfill cluster
    Streaming cluster
```

Now workloads can be isolated.

A giant backfill does not need to starve executive dashboards.

A data scientist's experiment does not need to delay revenue reporting.

A BI workload does not need to run on the same cluster as a Spark transformation.

This is one of the most practical reasons separation matters.

It is not just scaling.

It is political peace.

Compute isolation is how you prevent one team's innocent experiment from becoming another team's incident.

In data platforms, peace is an architecture feature.

---

## 6. The Third Benefit: Multiple Engines on the Same Data

Another major benefit is multi-engine access.

If data is stored in open or shared formats, different engines can read it.

For example:

```text
Object storage / lakehouse tables
    ├── Spark for large transformations
    ├── Trino for interactive SQL
    ├── Flink for streaming
    ├── Python/R notebooks for data science
    ├── BI tools through SQL engines
    └── ML pipelines for training features
```

This is attractive because different engines are good at different things.

Spark is strong for distributed transformation and large-scale batch.
Trino/Presto-style engines are strong for interactive distributed SQL.
Cloud warehouses are strong for managed analytics and BI workloads.
Flink is strong for streaming and stateful processing.
Python/R are useful for scientific and ML workflows.

The old dream was one engine for everything.

The modern reality is more pluralistic.

Or, less poetically:

> One engine to rule them all usually becomes one engine to annoy everyone differently.

Separated storage allows teams to use workload-appropriate compute.

But this only works if the shared data layer is well-governed.

Otherwise, multi-engine access becomes multi-engine confusion.

---

## 7. The First Reality Check: Network Is the New Disk

When compute and storage are separated, compute often reads data over the network.

This changes performance assumptions.

In a coupled cluster, compute may read from local disks or nearby distributed storage.

In a separated cloud architecture, compute may read from object storage across the network.

That means query performance depends on:

* network bandwidth;
* object-store throughput;
* file sizes;
* request rates;
* metadata operations;
* caching;
* data skipping;
* compression;
* column pruning;
* locality between compute and storage region;
* concurrent workloads.

The phrase "storage is separate" sounds clean.

But every query still has to move bytes.

If a query scans 10 TB, those bytes must be read from somewhere.

Separation does not eliminate I/O.

It makes I/O more explicit and often more remote.

That is why layout matters so much in cloud data platforms.

Partitioning, clustering, Z-ordering, file compaction, statistics, materialized views, and data skipping are all attempts to reduce unnecessary reads.

The best query is not the one that reads 10 TB very heroically.

The best query is the one that realizes it only needed 40 GB.

Network is not evil.

But it is not imaginary.

Cloud architecture sometimes hides cables from the diagram.

The packets still know.

---

## 8. The Second Reality Check: Object Storage Is Not a Database

Object storage is excellent.

It is durable, scalable, relatively cheap, cloud-native, and operationally convenient.

But object storage is not a database.

It does not naturally provide all database behaviors by itself.

Plain object storage does not automatically give you:

* table transactions;
* row-level updates;
* efficient small writes;
* indexes;
* constraints;
* query planning;
* schema enforcement;
* snapshot isolation;
* concurrent write control;
* time travel;
* semantic metadata.

Lakehouse table formats and warehouse systems add many of these capabilities.

But the capabilities come from layers above object storage.

For example:

```text
Object storage:
    stores files

Table format:
    tracks which files belong to a table/snapshot

Catalog:
    exposes table names, schemas, permissions, metadata

Compute engine:
    reads metadata, plans query, scans files, writes results
```

This layered architecture is powerful.

But it means more moving parts.

If someone says:

> "We store everything in S3, so we have a data platform."

The correct answer is:

> "You have storage. Congratulations. The platform starts now."

Object storage is the foundation.

It is not the whole house.

---

## 9. The Third Reality Check: Metadata Becomes Critical

Once storage is shared and compute is ephemeral, metadata becomes central.

Metadata tells compute engines how to understand storage.

It includes:

* table definitions;
* schemas;
* partitions;
* file lists;
* snapshots;
* transaction logs;
* statistics;
* permissions;
* ownership;
* lineage;
* freshness;
* contracts;
* retention policies;
* data classifications.

Without good metadata, shared storage becomes a bucket of files.

A bucket of files is not a data product.

It is a storage situation.

Modern table formats such as Iceberg, Delta, and Hudi exist partly because files alone are not enough. They add transactional and table-level metadata over object storage.

But metadata has costs:

* it must be maintained;
* it can grow large;
* it can become slow;
* it can be inconsistent across engines;
* it can require catalogs;
* it can create compatibility issues;
* it can become a bottleneck.

In a separated architecture, metadata is not decorative.

It is load-bearing.

Treat your catalog and table metadata like critical infrastructure.

Because they are.

A data platform without reliable metadata is just a lake with rumors.

---

## 10. The Fourth Reality Check: Cost Moves Around

Separation of compute and storage is often sold as cost-efficient.

And it can be.

But cost does not disappear.

It moves.

In a coupled system, you may pay for always-on clusters.

In a separated system, you may pay for:

* object storage;
* compute per query;
* compute per job;
* data scanned;
* object-store requests;
* metadata operations;
* egress, if data crosses regions/clouds;
* caching layers;
* table maintenance;
* compaction;
* catalog services;
* idle but configured warehouses;
* concurrency scaling;
* failed jobs;
* repeated exploratory queries;
* backfills;
* data duplication in curated marts.

The cost model becomes more granular.

That is both good and dangerous.

Good because you can scale and attribute costs more precisely.

Dangerous because teams may create compute everywhere and forget that every query has a price.

A separated architecture can reduce waste.

It can also democratize waste.

Now every team can spin up compute and scan the lake.

Very empowering.

Potentially very expensive.

Cloud platforms make it easy to scale.

They do not make it automatically wise.

---

## 11. The "Infinite Scale" Myth

Separation of compute and storage often arrives with a subtle promise:

> Scale is basically solved.

No.

Scale is changed.

You can scale compute more flexibly, yes.

But real systems still face limits:

* query planning limits;
* metadata size;
* object-store request limits;
* network throughput;
* file count;
* small files;
* skewed joins;
* inefficient SQL;
* high concurrency;
* catalog latency;
* permissions checks;
* downstream bottlenecks;
* cost constraints.

If a table has 90 million tiny files, adding more compute may not solve the main problem.

If a query joins two huge skewed datasets, separation does not remove skew.

If every dashboard queries raw events, more compute may simply make bad design more expensive.

If a table's metadata is bloated, planning may dominate execution.

If object storage is in another region, latency and egress may become unpleasant.

Modern platforms scale impressively.

But "scale" is not a force field against bad physical design.

Architecture still matters.

Data modeling still matters.

Query design still matters.

File sizes still matter.

The universe continues to charge for bytes.

---

## 12. Storage Is Cheap, Until You Read It Constantly

Object storage is often described as cheap.

Compared with traditional high-performance storage, yes.

But cheap storage can become expensive when accessed inefficiently.

A table may be cheap to store but expensive to query.

Example:

```text
Table size:
    100 TB

Storage cost:
    acceptable

Daily queries:
    repeatedly scan 30 TB

Compute and scan cost:
    painful
```

The problem is not storing the data.

The problem is reading too much of it too often.

This is where data engineering design matters.

You may need:

* partition pruning;
* clustering;
* column pruning;
* file compaction;
* precomputed aggregates;
* materialized views;
* query result caching;
* workload-specific marts;
* semantic layers;
* retention policies;
* cold/hot data separation.

The mature view:

> Storage cost is only one part of data cost. Access cost is where many surprises live.

A data lake can be cheap at rest and expensive in motion.

Like a sleeping dragon that bills by the wingbeat.

---

## 13. Compute Is Elastic, But People Are Not

Elastic compute allows teams to scale resources quickly.

But teams still need operational discipline.

If every workload can create compute independently, you need governance.

Questions appear:

* Who can create compute?
* Which workloads get priority?
* Which teams pay for which compute?
* What are the budget limits?
* What happens when a query scans 80 TB accidentally?
* Should exploration use different compute than production?
* Should dashboards use reserved capacity?
* Should backfills run during business hours?
* How are idle clusters shut down?
* Who owns runaway jobs?
* How are costs attributed?

Separation of compute and storage makes compute more flexible.

It also makes compute sprawl easier.

Compute sprawl is what happens when everyone creates clusters, warehouses, endpoints, or jobs, and nobody knows which ones matter.

At first, this feels like productivity.

Later, it becomes a bill and an inventory problem.

The platform should provide:

* standard compute templates;
* workload classes;
* autoscaling policies;
* auto-shutdown;
* budget alerts;
* usage attribution;
* tagging;
* priority queues;
* approved sizes;
* clear ownership.

Elasticity without governance becomes elastic chaos.

Very stretchy. Not very comforting.

---

## 14. Workload Classes Matter

Not every workload should use the same compute.

A healthy platform often separates workloads into classes.

Example:

```text
BI / dashboards:
    low-latency, high-concurrency, stable compute

ELT transformations:
    scheduled, predictable, batch-oriented compute

Backfills:
    temporary, high-throughput, isolated compute

Data science:
    exploratory, flexible, sandboxed compute

Streaming:
    long-running, stateful, monitored compute

Reverse ETL:
    API-aware, rate-limited, reliable sync compute
```

Each workload has different needs.

BI wants responsiveness and concurrency.

Batch transformations want throughput and reliability.

Backfills want temporary heavy capacity.

Data science wants flexibility but should not accidentally starve production.

Streaming wants continuous health and checkpoint safety.

Reverse ETL wants controlled outbound side effects.

Separation of compute and storage enables these classes.

But the platform must define them.

Otherwise, every workload becomes "whatever cluster someone found."

That is not architecture.

That is a garage sale.

---

## 15. The Cache Layer Becomes Important

If compute is ephemeral and storage is remote, caching becomes important.

Caches may exist at many levels:

* query result cache;
* local disk cache;
* remote disk cache;
* metadata cache;
* file footer cache;
* data skipping indexes;
* BI tool cache;
* materialized views;
* warehouse cache;
* engine-specific cache.

Caching can make separated architectures feel fast.

But caches create their own realities.

Questions:

* Is the cache fresh?
* When is it invalidated?
* Is the query using cached results?
* Are two users seeing the same version?
* Does cache hide poor table design?
* What happens when cache is cold?
* How expensive is cache warm-up?
* Does scaling compute lose local cache benefits?

A common surprise:

> Yesterday's query was fast. Today's identical query is slow.

Possible reason:

> Yesterday it hit cache. Today it did not.

Caching is useful.

But performance claims should distinguish warm-cache from cold-cache behavior.

A platform that only feels fast after the cache is warm may still struggle with ad hoc workloads, backfills, and new queries.

Cache is seasoning.

Good storage layout is food.

Please do not serve a bowl of seasoning.

---

## 16. The Data Locality Trade-Off

Older distributed systems often emphasized data locality.

The idea:

> Move compute to where the data lives.

With separate compute and object storage, locality changes.

Compute is not necessarily on the same machines as the data.

Instead, the system relies on:

* high-throughput network;
* parallel reads;
* object-store scalability;
* caching;
* columnar formats;
* predicate pushdown;
* file pruning;
* distributed execution;
* elastic compute.

This can work very well.

But it means the platform needs to minimize unnecessary data movement.

Bad design causes excessive remote reads.

Good design reduces reads using metadata and layout.

That is why modern cloud performance often depends less on "where is the disk?" and more on:

* which files are read;
* which columns are read;
* which partitions are pruned;
* which row groups are skipped;
* which results are cached;
* how many bytes cross the network;
* how much parallelism is useful;
* whether the query is properly modeled.

Data locality is not gone.

It has been transformed into **data minimization**.

Do not ask only:

> Is compute close to storage?

Also ask:

> Why are we reading this much data at all?

---

## 17. Separation Helps Backfills - But Can Also Make Them Too Easy

Separated compute is wonderful for backfills.

Need to reprocess two years of data?

Spin up temporary compute.

Need to rebuild a feature table?

Use a dedicated cluster.

Need to repair historical partitions?

Run a backfill warehouse isolated from production.

This is excellent.

But because backfills become easier to launch, they may become easier to abuse.

A poorly planned backfill can:

* scan huge data volumes;
* rewrite large tables;
* create small files;
* conflict with production writes;
* invalidate caches;
* trigger downstream refreshes;
* consume budget;
* confuse users if partial outputs are visible;
* produce inconsistent historical logic.

Separation of compute lets you throw power at the problem.

But the problem still needs a safe plan.

A good backfill should define:

* scope;
* input versions;
* output partitions;
* table format behavior;
* validation rules;
* isolation from production;
* rollback strategy;
* expected cost;
* downstream impact;
* communication plan.

Backfills are not just "run bigger compute."

They are controlled rewrites of history.

History deserves a changelog.

---

## 18. Separation Makes Data Sharing Easier

When storage is separated and standardized, sharing becomes easier.

Multiple teams can access the same data without copying it into every compute environment.

This supports:

* shared curated datasets;
* cross-team analytics;
* multi-engine access;
* governed data products;
* feature reuse;
* self-service analytics;
* central storage with distributed compute.

But sharing data also creates governance demands.

If many engines can read the same data, you need:

* consistent permissions;
* row/column-level access policies;
* data classification;
* audit logs;
* lineage;
* ownership;
* schema contracts;
* usage tracking;
* environment separation;
* production vs development boundaries.

Otherwise, "shared data" becomes "everyone can query everything and nobody knows who broke what."

Data sharing is not only a storage problem.

It is a governance problem.

Separation of compute and storage makes sharing technically easier.

It does not make sharing automatically safe.

---

## 19. The Multi-Engine Dream Has Compatibility Costs

Using multiple engines on shared storage is powerful.

But engines may not behave identically.

Questions:

* Do all engines understand the same table format?
* Do they support the same protocol version?
* Do they handle deletes the same way?
* Do they support schema evolution?
* Do they interpret timestamps consistently?
* Do they respect the same permissions?
* Can all engines write safely?
* Are some engines read-only?
* Are there differences in decimal precision?
* Are partition transforms interpreted consistently?
* Are case-sensitive column names handled the same way?

Example:

```text
Spark writes table.
Trino reads table.
Flink streams updates.
BI tool queries through SQL endpoint.
Compaction job rewrites files.
Catalog enforces permissions.
```

This can work.

But it needs testing.

A platform should maintain a compatibility matrix.

Example:

| Capability | Spark | Trino | Flink | BI SQL Endpoint |
|---|---:|---:|---:|---:|
| Read table | Yes | Yes | Yes | Yes |
| Write table | Yes | Limited | Yes | No |
| MERGE | Yes | Depends | Depends | No |
| Time travel | Yes | Yes | Limited | Maybe |
| Row-level deletes | Yes | Depends | Depends | No |
| Schema evolution | Yes | Partial | Depends | Maybe |

The exact values depend on your platform.

The point is that compatibility must be known.

"Open format" does not mean "all engines support all features perfectly."

Reality remains rude.

---

## 20. Storage Layout Becomes a Platform Concern

When storage is shared, physical layout affects many compute engines.

A badly laid-out table can harm:

* BI dashboards;
* Spark jobs;
* Trino queries;
* ML feature pipelines;
* reverse ETL models;
* ad hoc exploration;
* data quality checks.

This makes table layout a platform concern.

Important layout choices include:

* file format;
* compression;
* partitioning;
* clustering;
* sorting;
* file size;
* table format;
* compaction policy;
* snapshot retention;
* statistics collection;
* metadata cleanup;
* hot/cold data separation.

In a tightly integrated warehouse, many physical details may be hidden or automated.

In a lakehouse or open-table architecture, teams often need to be more explicit.

This does not mean everyone should micromanage files.

It means the platform should define standards.

Example standards:

```text
Large fact tables:
    file format: Parquet
    target file size: 128-512 MB
    partition: event_date or event_month
    clustering: customer_id/account_id where useful
    compaction: daily for hot partitions
    snapshot retention: 7-30 days depending on table class

Small dimension tables:
    avoid excessive partitioning
    optimize for joins
    validate uniqueness
    consider broadcast behavior in Spark
```

These standards prevent every team from reinventing physical design.

Without standards, separated storage becomes shared entropy.

---

## 21. The "One Copy of Data" Myth

Separation of compute and storage sometimes comes with another promise:

> Store one copy of data and use it everywhere.

This is partly true and partly fantasy.

It is true that central storage can reduce unnecessary duplication.

But in practice, data platforms still create multiple physical representations.

Examples:

* raw data;
* cleaned data;
* curated marts;
* aggregated tables;
* feature tables;
* search indexes;
* BI extracts;
* materialized views;
* training datasets;
* regulatory snapshots;
* anonymized copies;
* public data products;
* sandbox copies.

Why?

Because different workloads need different shapes.

A raw event table is not the same thing as a BI mart.

A feature table is not the same thing as a regulatory extract.

A low-latency serving index is not the same thing as a historical lakehouse table.

Trying to force all workloads to use one physical representation often creates slow queries, messy semantics, and overloaded tables.

The mature version of "one copy" is not literally one table.

It is:

> One governed source of truth, with derived representations that are documented, versioned, and lineage-connected.

Duplication is not always bad.

Uncontrolled duplication is bad.

Purposeful duplication is data modeling.

This distinction prevents many ideological architecture arguments.

---

## 22. Compute Separation Helps Teams Move Faster

A practical benefit: teams can work independently.

Data science can use its own compute environment.
Analytics engineering can run transformations separately.
BI can have stable query capacity.
Platform teams can run maintenance jobs.
Backfills can run in isolation.
Experimental workloads can be sandboxed.

This reduces operational coupling.

It also supports self-service.

But self-service requires guardrails.

Otherwise, teams may:

* create expensive clusters;
* query raw data inefficiently;
* bypass curated models;
* produce inconsistent metrics;
* create untracked datasets;
* duplicate sensitive data;
* forget to shut compute down;
* run production-like workloads in development spaces;
* accidentally expose data.

Self-service without standards becomes self-service chaos.

Good platforms provide paved roads.

Example:

```text
Approved compute profiles:
    small-exploration
    medium-analytics
    large-backfill
    bi-production
    ml-training
    streaming-production

Each profile includes:
    cost tags
    auto-shutdown
    permissions
    network policy
    logging
    monitoring
    allowed data zones
```

The goal is not to block users.

The goal is to make the safe path easy.

A platform should feel like a well-designed city, not an empty field with power tools.

---

## 23. Compute Separation Does Not Remove Data Modeling

One common mistake is assuming architecture can compensate for poor modeling.

It cannot.

If users query raw events for every dashboard, compute separation does not save you.

It may allow you to throw more compute at the query, but the query is still doing too much.

Example raw query:

```sql
SELECT
    DATE_TRUNC('day', event_timestamp) AS event_day,
    customer_segment,
    COUNT(DISTINCT user_id) AS active_users
FROM raw.events
WHERE event_type IN ('login', 'purchase', 'feature_use')
GROUP BY
    DATE_TRUNC('day', event_timestamp),
    customer_segment;
```

If this runs constantly, create a curated model:

```sql
CREATE TABLE mart.daily_active_users_by_segment AS
SELECT
    event_date,
    customer_segment,
    COUNT(DISTINCT user_id) AS active_users
FROM clean.events_enriched
WHERE event_type IN ('login', 'purchase', 'feature_use')
GROUP BY
    event_date,
    customer_segment;
```

Then dashboards query:

```sql
SELECT *
FROM mart.daily_active_users_by_segment
WHERE event_date >= DATE '2026-09-01';
```

Separated compute makes compute flexible.

It does not replace semantic modeling, aggregation, or dimensional design.

A bigger engine can make a bad query faster.

A better model can make the query unnecessary.

That second one is usually more elegant.

Also cheaper.

---

## 24. The Warehouse Version of Separation

Cloud data warehouses popularized separation of compute and storage in a managed form.

The user experience is often:

* data is stored in managed storage;
* compute warehouses can be scaled independently;
* multiple warehouses can access the same data;
* compute can suspend and resume;
* query concurrency can be isolated;
* caching and optimization are handled internally.

This is a very productive model.

It hides many operational details.

The trade-off is that the platform may become more vendor-managed and less transparent.

Questions still matter:

* How are costs attributed?
* Which warehouse runs which workload?
* Are warehouses over-sized?
* Are users scanning too much data?
* Are dashboards using appropriate aggregates?
* Are materializations well-designed?
* Are transformations isolated from BI?
* Are permissions and data sharing governed?
* Are result caches masking inefficient queries?

Managed separation reduces infrastructure burden.

It does not eliminate architecture work.

The warehouse may manage storage internals.

You still manage data products.

---

## 25. The Lakehouse Version of Separation

Lakehouse architectures expose more of the storage layer.

Data often lives in object storage using open file formats and table formats.

Compute engines read and write tables through catalogs and metadata.

Example:

```text
Object storage:
    Parquet files

Table format:
    Iceberg / Delta / Hudi

Catalog:
    Glue / Hive Metastore / Unity Catalog / Nessie / REST catalog

Compute:
    Spark / Trino / Flink / SQL engines / ML jobs
```

This gives flexibility and openness.

But it also exposes more operational concerns:

* file sizing;
* compaction;
* metadata growth;
* catalog management;
* table maintenance;
* engine compatibility;
* object-store request patterns;
* concurrent writes;
* snapshot expiration;
* small files;
* delete/update strategies.

In a lakehouse, separation is more visible.

That is not bad.

It is powerful.

But the team needs platform maturity.

A lakehouse is not just "warehouse but cheaper."

It is a different operational model.

If you want the openness, you must also accept more responsibility for table health.

Open architecture is not free-range magic.

It is freedom plus chores.

---

## 26. The Streaming Version of Separation

Streaming systems also interact with separated storage.

A streaming pipeline may:

* consume events from Kafka or another broker;
* process them with Flink or Spark Structured Streaming;
* write outputs to object storage/lakehouse tables;
* update serving systems;
* checkpoint state to durable storage.

Example:

```text
Kafka topic
    ↓
Streaming compute
    ↓
Lakehouse table on object storage
    ↓
BI / ML / downstream processing
```

The benefit:

* streaming compute can be managed separately;
* storage remains durable and shared;
* downstream batch/BI engines can read results.

The challenge:

* frequent small writes;
* checkpoint management;
* commit frequency;
* exactly-once/effectively-once semantics;
* table format compatibility;
* compaction requirements;
* late-arriving events;
* streaming vs batch consistency.

Streaming into object storage often creates many small files unless carefully managed.

Separation helps architecture.

It does not remove streaming's operational sharp edges.

A stream writing tiny files every few seconds into a lakehouse table is still a tiny-file factory.

Very modern.

Still a factory.

---

## 27. The Machine Learning Version of Separation

ML workflows benefit greatly from separated storage.

Training jobs can read large datasets from shared storage.

Feature engineering jobs can use separate compute.

Experimentation environments can access snapshots.

Model training can scale compute temporarily.

Feature stores can materialize offline and online representations.

Example:

```text
Lakehouse feature table
    ├── Offline training compute
    ├── Batch scoring compute
    ├── Feature validation jobs
    └── Online serving pipeline
```

This is powerful for reproducibility.

A model can train on a specific data snapshot.

Backfills can regenerate features.

Different training jobs can use different compute sizes.

But ML also adds requirements:

* dataset versioning;
* feature freshness;
* training-serving consistency;
* access control;
* lineage;
* reproducibility;
* cost control for training jobs;
* large read optimization;
* avoiding accidental full-table scans.

Separated storage gives ML teams access to large data.

But without curated feature tables, they may repeatedly compute expensive features from raw data.

That becomes slow and expensive.

The pattern should be:

> Use separated storage for shared durable data. Use curated feature/data products to prevent every model from rediscovering the same joins.

Otherwise, every training run becomes a personal data warehouse.

That is not research productivity.

That is distributed duplication with GPUs, or worse, without GPUs and with sadness.

---

## 28. The Healthcare and Biotech Angle

Healthcare and biotech data platforms are excellent examples of why compute-storage separation matters.

These domains often have:

* large raw files;
* sensitive data;
* multiple processing modalities;
* heavy batch workflows;
* reproducibility needs;
* strict governance;
* multiple user types;
* long retention requirements;
* variable compute demands.

Consider genomics.

Raw and intermediate data may include:

* FASTQ;
* BAM/CRAM;
* VCF/BCF;
* annotation tables;
* expression matrices;
* sample metadata;
* cohort definitions.

A genomics platform may need:

* CPU-heavy alignment;
* memory-heavy variant calling;
* Spark-based cohort analytics;
* SQL-based metadata queries;
* Python/R notebooks;
* ML training jobs;
* archival storage.

The compute needs vary wildly.

Keeping all compute tied to all storage would be inefficient.

A separated architecture allows:

```text
Shared durable storage:
    raw and processed genomic data

Compute:
    alignment cluster
    variant calling workflow
    Spark analytics cluster
    notebook environment
    ML training jobs
    lightweight metadata SQL engine
```

This is exactly where separation shines.

But healthcare and biotech also show the governance reality.

Sensitive data cannot simply be readable by every compute engine.

You need:

* access controls;
* audit logging;
* data zones;
* encryption;
* consent-aware policies;
* project-level isolation;
* controlled exports;
* reproducible releases;
* metadata lineage;
* retention rules.

In clinical data, the same applies.

EHR-derived tables may be stored centrally, but compute access must be governed.

A notebook, BI dashboard, ML pipeline, and external collaboration environment should not automatically have the same permissions.

Separation of compute and storage gives flexibility.

Governance decides who may flex.

---

## 29. Security Boundaries Become More Subtle

When compute is separated, access control must cover both storage and compute.

It is not enough to ask:

> Who can access the bucket?

You also need to ask:

* Who can create compute?
* Which compute roles can access which data?
* Can development compute read production data?
* Can temporary clusters access sensitive zones?
* Are credentials short-lived?
* Are secrets managed properly?
* Are query results cached securely?
* Are logs leaking sensitive values?
* Are exports controlled?
* Can users copy data into unmanaged locations?
* Are cross-region reads allowed?
* Are network paths restricted?

A separated architecture often has more combinations:

```text
User
    + compute role
    + data catalog permission
    + storage permission
    + network policy
    + table policy
    + row/column policy
    + environment

That is powerful, but complex.

Security should be designed into the platform.

Not added later with a spreadsheet named `permissions_v4_final_revised.xlsx`.

A good platform makes access explicit, auditable, and least-privilege.

Because once compute is flexible, unauthorized compute becomes a real risk.

---

## 30. Environment Separation: Dev, Stage, Prod

Separation of compute and storage also affects environments.

You may have:

* development compute;
* staging compute;
* production compute;
* shared storage zones;
* environment-specific tables;
* production data replicas;
* masked data;
* synthetic data;
* sandbox outputs.

The danger is accidental crossing.

Examples:

* dev jobs writing into production tables;
* staging compute reading sensitive production data;
* test backfills overwriting real partitions;
* notebooks creating unmanaged production outputs;
* temporary tables becoming unofficial dependencies.

A healthy architecture defines clear zones:

```text
raw/
    immutable source data

staging/
    intermediate processing

curated/
    validated data products

sandbox/
    experimental user outputs

prod/
    production-serving datasets

archive/
    retained historical data
```

And clear compute permissions:

```text
dev compute:
    can read masked/sandbox data
    cannot write curated/prod

prod compute:
    can write production tables
    monitored and governed

backfill compute:
    temporary access
    scoped to specific tables/partitions

exploration compute:
    read-only access to approved data products
```

This may sound bureaucratic.

It is less bureaucratic than explaining why an experiment overwrote the executive revenue table.

---

## 31. Separation and Data Product Thinking

Compute-storage separation fits naturally with data product thinking.

A data product is not just a file or table.

It has:

* owner;
* schema;
* contract;
* freshness expectation;
* quality checks;
* access policy;
* documentation;
* lineage;
* consumption patterns;
* cost profile;
* serving expectations.

In a separated architecture, the storage layer may hold the product, while different compute engines consume it.

Example:

```text
Data product:
    mart.customer_360

Storage:
    lakehouse table

Consumers:
    BI warehouse
    reverse ETL sync
    ML feature job
    customer success dashboard
    ad hoc SQL engine

Contract:
    stable schema
    daily freshness
    customer_id uniqueness
    governed fields
```

The product must be reliable regardless of which compute reads it.

That means the product boundary should be defined at the data level, not at the cluster level.

This is a major shift.

The old question:

> Which cluster owns this table?

The better question:

> Which team owns this data product, and which compute workloads are allowed to consume or produce it?

That is data platform engineering.

---

## 32. The Operational Failure Modes

Separated architectures have their own failure modes.

Examples:

### Storage is available, compute is not

Data exists, but the warehouse or cluster is down, misconfigured, or quota-limited.

### Compute is available, storage access fails

Permissions, network policy, object-store outage, expired credentials, or region issues block reads.

### Metadata/catalog is unavailable

Data and compute exist, but tables cannot be resolved.

### One compute engine writes incompatible data

Another engine fails or returns inconsistent results.

### Small files explode

Queries slow down despite more compute.

### Cache hides a problem

Users see old or cached results and mistake them for fresh data.

### Cost anomaly

A workload scales compute unexpectedly or scans too much storage.

### Permission drift

Temporary compute gains access it should not have.

### Maintenance lag

Compaction, snapshot cleanup, or statistics updates fall behind.

In a coupled architecture, failures may be concentrated.

In a separated architecture, failures can occur at the boundaries.

Therefore, observability must cover:

* compute health;
* storage health;
* metadata/catalog health;
* table health;
* query performance;
* access failures;
* cost;
* workload behavior;
* data freshness;
* data quality.

"Is the cluster running?" is not enough.

The cluster may be running beautifully while reading the wrong snapshot slowly and expensively.

Modern platforms require modern paranoia.

The useful kind.

---

## 33. Observability in Separated Architectures

Observability should answer:

### Compute questions

* Which workloads are running?
* How much compute are they consuming?
* Are clusters/warehouses idle?
* Are queries queued?
* Are jobs spilling memory?
* Are workloads isolated?

### Storage questions

* How much data is stored?
* Which tables are growing fastest?
* Are files too small?
* Are old snapshots retained?
* Are storage costs increasing?

### Metadata questions

* Are catalogs available?
* Are table metadata files growing?
* Are schemas changing?
* Are manifests/logs healthy?
* Are statistics fresh?

### Query questions

* Which queries scan the most bytes?
* Which dashboards are slow?
* Which tables are expensive to query?
* Are users scanning raw data unnecessarily?

### Governance questions

* Who accessed sensitive data?
* Which compute roles read which zones?
* Are permissions aligned with policy?
* Are data exports controlled?

### Data product questions

* Is the data fresh?
* Are quality checks passing?
* Which consumers are affected by delay or failure?

A separated architecture gives flexibility.

Observability gives control.

Without observability, flexibility becomes a fog machine.

Looks dramatic. Hard to navigate.

---

## 34. A Practical Example: Same Storage, Different Compute

Suppose we have an event table:

```text
lakehouse.events
- event_id
- customer_id
- event_type
- event_timestamp
- event_date
- account_id
```

Different workloads use it.

### BI dashboard

Needs daily aggregates.

```sql
SELECT
    event_date,
    event_type,
    COUNT(*) AS n_events
FROM lakehouse.events
WHERE event_date >= DATE '2026-09-01'
GROUP BY event_date, event_type;
```

### Data science

Needs customer behavior features.

```sql
SELECT
    customer_id,
    COUNT(*) AS events_30d,
    COUNT(DISTINCT event_type) AS distinct_event_types_30d
FROM lakehouse.events
WHERE event_date >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY customer_id;
```

### Backfill

Needs two years of historical reprocessing.

```sql
SELECT *
FROM lakehouse.events
WHERE event_date BETWEEN DATE '2024-01-01' AND DATE '2025-12-31';
```

All read the same underlying data product.

But they should not necessarily use the same compute.

Better:

```text
BI:
    stable SQL warehouse with cache and concurrency

Data science:
    exploratory compute with quotas

Backfill:
    temporary isolated large cluster

Production transformations:
    scheduled ELT compute with monitoring
```

Separation makes this possible.

But the platform must also prevent the backfill from destroying BI performance or budget.

That is the reality.

The architecture gives you the option.

Governance makes it safe.

---

## 35. A Small Python Sketch: Cost-Aware Workload Metadata

A data platform can track compute/storage usage metadata for workloads.

This tiny example is not production code. It simply shows the kind of metadata thinking that separated architectures encourage.

```python
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


class WorkloadClass(StrEnum):
    """Types of data platform workloads."""

    BI = "bi"
    ELT = "elt"
    BACKFILL = "backfill"
    ML = "ml"
    EXPLORATION = "exploration"
    STREAMING = "streaming"


@dataclass(frozen=True)
class WorkloadRun:
    """Metadata about one compute workload run."""

    run_id: str
    workload_name: str
    workload_class: WorkloadClass
    owner_team: str
    started_at: datetime
    finished_at: datetime
    bytes_scanned: int
    compute_seconds: float
    tables_read: tuple[str, ...]
    tables_written: tuple[str, ...]


def compute_gb_scanned(run: WorkloadRun) -> float:
    """Return scanned data volume in GiB.

    Parameters
    ----------
    run
        Workload run metadata.

    Returns
    -------
    float
        Number of GiB scanned by the workload.
    """
    gib = 1024**3
    return run.bytes_scanned / gib


def is_expensive_exploration_run(
    run: WorkloadRun,
    threshold_gib: float = 1_000.0,
) -> bool:
    """Check whether an exploratory run scanned unusually much data.

    Parameters
    ----------
    run
        Workload run metadata.
    threshold_gib
        Threshold in GiB above which exploration is considered expensive.

    Returns
    -------
    bool
        ``True`` if the run is an exploratory workload above the threshold.
    """
    return (
        run.workload_class == WorkloadClass.EXPLORATION
        and compute_gb_scanned(run) > threshold_gib
    )
```

The point is not this code.

The point is the metadata mindset.

When compute is elastic and storage is shared, the platform should know:

* who ran what;
* against which tables;
* using which compute class;
* scanning how much data;
* producing which outputs;
* at what cost;
* with what business purpose.

Otherwise, separation gives you freedom without memory.

And systems without memory repeat mistakes.

Very human. Not ideal for infrastructure.

---

## 36. When Separation Is Not the Best Fit

Separation of compute and storage is powerful, but not universally ideal.

Some workloads may prefer tighter coupling.

Examples:

### Ultra-low-latency transactional systems

Operational databases often keep compute and storage closely integrated for predictable low-latency reads and writes.

### High-performance specialized systems

Some analytical appliances or HPC workloads benefit from tightly optimized local storage and compute.

### Small simple systems

For small datasets, a single database may be simpler and cheaper than a cloud lakehouse architecture.

### Heavy iterative workloads

Some workloads repeatedly access the same data and may benefit from local caching or colocated storage.

### Edge or disconnected environments

Compute may need local storage due to network constraints.

The mature view is not:

> Separation is always better.

The mature view is:

> Separation is excellent when independent scaling, shared storage, multi-workload access, and elastic compute matter more than tight locality and simplicity.

Architectures have contexts.

Anyone selling one universal answer is either simplifying or invoicing.

Possibly both.

---

## 37. Common Anti-Patterns

### Anti-pattern 1: Treating object storage as a complete data platform

Storage is not enough.

You need metadata, governance, compute, quality, lineage, and access control.

### Anti-pattern 2: One compute pool for everything

This wastes the main benefit of separation.

Isolate workloads.

### Anti-pattern 3: No cost attribution

If teams can create compute but nobody sees cost, the bill becomes a horror anthology.

### Anti-pattern 4: Multi-engine chaos

Many engines reading and writing shared tables without compatibility rules.

That is not openness. That is gambling.

### Anti-pattern 5: Ignoring metadata

Catalogs, table formats, statistics, and schemas are critical.

Metadata is not paperwork. It is infrastructure.

### Anti-pattern 6: Too many small files

Separated compute does not fix bad file layout.

### Anti-pattern 7: Using raw storage for every query

Curated models, marts, and aggregates still matter.

### Anti-pattern 8: No workload governance

Elastic compute without guardrails becomes compute sprawl.

### Anti-pattern 9: Assuming cache means performance is solved

Cold-cache performance still matters.

### Anti-pattern 10: Confusing shared storage with shared truth

Shared files do not automatically produce shared definitions.

Semantic governance is still needed.

---

## 38. What Good Looks Like

A healthy compute-storage-separated platform usually has these traits.

### Shared durable storage

Data is stored in a reliable, scalable storage layer with clear zones.

### Governed metadata

Catalogs, table formats, schemas, ownership, and permissions are managed seriously.

### Workload-specific compute

BI, ELT, ML, streaming, exploration, and backfills use appropriate compute profiles.

### Cost visibility

Usage is attributed by team, workload, table, and environment.

### Table health management

File sizes, compaction, partitioning, clustering, and metadata growth are monitored.

### Strong data modeling

Raw data is not the only serving layer. Curated marts and products exist.

### Security by design

Compute access and storage access are aligned with data sensitivity.

### Multi-engine compatibility rules

Supported engines and operations are documented and tested.

### Observability across layers

Compute, storage, metadata, data quality, freshness, and cost are visible.

### Clear ownership

Every important data product and workload has an owner.

In short:

> Separation of compute and storage is not a complete architecture. It is a powerful architectural principle that still needs platform engineering around it.

That is the difference between a cloud bill and a cloud platform.

---

## 39. A Practical Checklist

Before designing or evaluating a separated compute-storage platform, ask:

1. Where does durable data live?
2. Which compute engines will read it?
3. Which compute engines are allowed to write it?
4. Which table formats are supported?
5. Which catalog manages metadata?
6. How are permissions enforced?
7. How are workloads isolated?
8. How are compute costs attributed?
9. How are idle resources shut down?
10. How are file sizes maintained?
11. How are table snapshots cleaned?
12. How are schemas evolved?
13. How are multi-engine compatibility issues tested?
14. How are raw, staged, curated, and sandbox zones separated?
15. How are sensitive datasets protected?
16. How are backfills isolated from production?
17. How are query costs monitored?
18. Which tables need curated marts or aggregates?
19. How is cache behavior understood?
20. Who owns each data product?

This checklist is not glamorous.

But glamour is not what saves data platforms.

Clear ownership, boring metadata, and sensible workload isolation save data platforms.

Glamour mostly creates conference talks.

---

## 40. Final Thought

Separation of compute and storage is one of the defining ideas of modern data platforms.

It enables flexibility that older architectures struggled to provide:

* independent scaling;
* elastic compute;
* shared durable storage;
* workload isolation;
* multi-engine access;
* lower idle compute cost;
* easier backfills;
* more adaptable platform design.

But the reality is more nuanced than the slogan.

Separation does not remove I/O.

It does not make object storage a database.

It does not eliminate data modeling.

It does not solve governance.

It does not prevent bad queries.

It does not remove metadata complexity.

It does not guarantee low cost.

It does not mean one physical copy of data serves every workload perfectly.

What it does is give the platform a more flexible set of building blocks.

And flexibility is valuable only when paired with discipline.

The mature view is:

> Separate compute and storage so each can scale and evolve independently, but invest seriously in metadata, governance, workload isolation, data modeling, observability, security, and cost control.

That is the real architecture.

Not the hype version.

The hype version says:

> "Store everything cheaply and scale compute infinitely."

The real version says:

> "Store data durably, expose it through governed metadata, run the right compute for the right workload, avoid scanning nonsense, monitor costs, and make sure someone owns the tables before the lake becomes a swamp."

Less shiny.

Much more useful.

Separation of compute and storage is not magic.

It is leverage.

Use it well, and your platform becomes more scalable, flexible, and sane.

Use it carelessly, and you get a distributed system where storage is cheap, compute is everywhere, metadata is confused, and the bill arrives with dramatic lighting.

The architecture gives you freedom.

Platform engineering makes that freedom survivable.
