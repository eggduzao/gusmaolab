Title: The Sunday Materialization - The Hidden Costs of Iceberg, Delta, and Hudi on Object Storage
Subtitle: When Your Lakehouse Table Format Is Powerful, But S3 Still Charges Rent
Date: 2025-09-28 07:00
Modified: 2025-09-28 07:00
Category: Sunday
Tags: data engineer, data platform engineer, data, data architecture, lakehouse, object storage, iceberg, delta lake, hudi
Slug: sunday-materialization-hidden-costs-lakehouse-object-storage
Authors: Eduardo G Gusmao
Summary: A weekly educational topic/lecture/discussion on Data Engineering topics that we all experienced at least once (or will!)
Status: final
Lang: en
Template: topic
Cadence: Biweekly
Scope: Data Engineering, Industry, Data Challenges
Tone: Analytical, Educational, Non-Sensational
Canonical: https://www.gusmaolab.org/blog/sunday-materialization-hidden-costs-lakehouse-object-storage/
Meta_description: Biweekly analysis of important Data Engineering concepts.
Meta_keywords: data concepts, topics, lectures, discussions, lakehouse, object storage, iceberg, delta lake, hudi
Cover: images/covers/hidden-costs-lakehouse-object-storage.png
Thumbnail: images/thumbnails/hidden-costs-lakehouse-object-storage-thumb.png

# The Hidden Costs of Iceberg, Delta, and Hudi on Object Storage

Modern lakehouse table formats are a genuine improvement.

Apache Iceberg, Delta Lake, and Apache Hudi solved a real problem: object storage is cheap, scalable, and durable, but plain files in object storage are not enough to behave like reliable analytical tables.

If you simply throw Parquet files into S3, ADLS, GCS, or MinIO, you quickly run into familiar problems:

- Which files belong to the current table?
- Which files were produced by failed jobs?
- How do we update or delete records?
- How do we handle schema evolution?
- How do we isolate concurrent readers and writers?
- How do we support time travel?
- How do we avoid corrupting a table during partial writes?
- How do query engines know which files to scan?
- How do we make the data lake feel less like a bucket-shaped junk drawer?

Lakehouse table formats help answer these questions.

They add metadata, transaction logs, snapshots, manifests, indexes, commit protocols, and table-level abstractions on top of object storage.

That is extremely useful.

But there is a catch.

> A lakehouse table format does not remove the physics of object storage. It builds a management layer on top of it.

And that management layer has costs.

Some are financial.
Some are operational.
Some are architectural.
Some are cognitive.
Some appear only after the platform becomes successful and everyone starts using it.

This is the uncomfortable middle ground: Iceberg, Delta, and Hudi are powerful, but they are not magic. They make object storage behave more like a database table, but object storage does not suddenly become a database.

The lakehouse is not free lunch.

It is lunch with metadata.

---

## 1. The Good News First: Why These Formats Exist

Before discussing hidden costs, we should be fair.

Iceberg, Delta, and Hudi exist because plain object-storage data lakes were painful.

A traditional data lake layout might look like this:

```
s3://company-data/orders/
    year=2026/
        month=07/
            day=01/
                part-0001.parquet
                part-0002.parquet
            day=02/
                part-0001.parquet
                part-0002.parquet
```

This looks reasonable.

But now imagine:

- one job fails halfway through writing;
- another job writes duplicate files;
- a schema changes;
- a partition is overwritten incorrectly;
- an analyst queries while a write is in progress;
- old files remain after updates;
- a backfill accidentally mixes old and new logic;
- one engine writes files another engine cannot interpret consistently.

Plain files do not know they are part of a table.

They are just files sitting in object storage, like very organized potatoes.

Lakehouse formats add table semantics.

They can provide:

- atomic commits;
- snapshot isolation;
- schema evolution;
- partition evolution;
- time travel;
- upserts and deletes;
- metadata pruning;
- compaction;
- incremental reads;
- multi-engine access;
- concurrency control;
- cleaner failure recovery.

That is why they matter.

They make large analytical datasets more reliable and manageable.

But every abstraction has a cost.

The key is not to avoid lakehouse formats. The key is to understand what they make easier, what they make harder, and what they move somewhere else.

---

## 2. Object Storage Is Not a Filesystem

Many hidden costs begin with a misunderstanding:

> Object storage looks like a filesystem, but it is not one.

Object storage systems organize data as objects in buckets or containers. They may display paths like:

```
s3://bucket/table/year=2026/month=07/file.parquet
```

But those “folders” are usually key prefixes, not real directories in the traditional filesystem sense.

This matters.

Object storage is excellent for:

- storing large immutable files;
- scaling capacity massively;
- decoupling storage from compute;
- durable archival;
- parallel analytical reads;
- cheap long-term storage;
- cloud-native data sharing.

But it is less naturally excellent at:

- frequent small writes;
- low-latency metadata operations;
- renames;
- many tiny files;
- transactional mutation;
- listing huge prefixes repeatedly;
- behaving like HDFS or a local POSIX filesystem.

Lakehouse formats compensate for these limitations using metadata layers and commit protocols.

That works.

But the compensation itself becomes part of the system.

In other words:

> The table format is partly a solution and partly a new subsystem you now operate.

Congratulations. The dragon is useful.

It still needs feeding.

---

## 3. The First Hidden Cost: Metadata Is Data Too

Iceberg, Delta, and Hudi all rely on metadata.

Not necessarily the same metadata, and not in the same structure, but the principle is shared:

> The table is not only the data files. The table is also the metadata describing which files are valid, current, historical, removed, partitioned, indexed, or part of a snapshot.

This metadata enables powerful features.

But metadata grows.

And when metadata grows, it must be:

- written;
- read;
- compacted;
- cleaned;
- cached;
- listed;
- versioned;
- synchronized;
- protected;
- understood by query engines.

A tiny table may have simple metadata.

A large high-churn table may have:

- many snapshots;
- many manifests;
- many transaction-log files;
- many file-level statistics;
- many delete files;
- many small data files;
- many commits;
- many partitions;
- many historical versions.

At small scale, metadata feels invisible.

At large scale, metadata becomes a performance domain.

This is the first surprise for many teams.

They thought they were managing Parquet files.

They are actually managing a distributed metadata system whose behavior influences every query.

The table format does not remove metadata complexity.

It formalizes it.

That is good.

But formalized complexity is still complexity.

---

## 4. The Second Hidden Cost: Small Files Still Hurt

Lakehouse formats do not eliminate the small files problem.

They may help manage it.
They may provide tools to compact files.
They may track files more intelligently.
They may allow query engines to skip irrelevant files.

But if your table contains millions of tiny files, the engine still has to deal with them somehow.

Small files hurt because they increase:

- metadata size;
- planning time;
- task scheduling overhead;
- object-store requests;
- file open operations;
- manifest or log size;
- query coordination overhead;
- compaction burden.

A table with 10 TB stored as 10,000 files is very different from 10 TB stored as 10 million files.

Same data volume. Different operational pain.

A simplified picture:

```
Healthy-ish table:
    10 TB data
    20,000 reasonably sized files

Unhealthy table:
    10 TB data
    8,000,000 tiny files
```

Both may be “valid” lakehouse tables.

Only one will make your query planner question its life choices.

Small files often come from:

- frequent micro-batches;
- streaming ingestion;
- high-cardinality partitioning;
- many concurrent writers;
- low-volume partitions;
- aggressive incremental writes;
- unoptimized writer settings;
- lack of compaction jobs;
- over-partitioning by time, region, customer, device, or other tempting columns.

The lakehouse format can track the files.

It cannot make millions of tiny files cheap.

The bill eventually arrives.

Sometimes as cloud cost.
Sometimes as query latency.
Sometimes as compaction load.
Sometimes as a senior engineer muttering near a whiteboard.

---

## 5. Compaction Is Not Optional Forever

Because small files accumulate, compaction becomes important.

Compaction rewrites many small files into fewer larger files.

Conceptually:

```
Before compaction:
    part-00001.parquet   2 MB
    part-00002.parquet   4 MB
    part-00003.parquet   1 MB
    part-00004.parquet   3 MB

After compaction:
    part-compact-001.parquet   256 MB
```

This improves scan efficiency and reduces metadata overhead.

But compaction has costs:

- it consumes compute;
- it reads and rewrites data;
- it creates new files;
- it may conflict with concurrent writes if poorly managed;
- it requires scheduling;
- it requires monitoring;
- it may temporarily increase storage usage;
- it may need table-format-specific commands or services;
- it can create operational noise in busy tables.

Compaction is maintenance.

And maintenance is work.

Many teams adopt a lakehouse table format thinking mainly about reads and writes. Then, months later, they discover they also need table hygiene.

That includes:

- compacting small files;
- removing obsolete files;
- expiring snapshots;
- cleaning old metadata;
- clustering or sorting data;
- optimizing partition layout;
- monitoring table size and file counts.

The table is not a static pile of Parquet files.

It is a garden.

You can let a garden grow wild.

But then do not act surprised when the query engine comes out covered in weeds.

---

## 6. Time Travel Is Wonderful Until History Becomes Heavy

Time travel is one of the most attractive features of lakehouse formats.

It lets you query older versions of a table.

That is extremely useful for:

- debugging;
- reproducibility;
- rollback;
- auditability;
- historical comparison;
- recovering from bad writes;
- ML training snapshots;
- regulated reporting;
- “what did the table look like before Bruno ran that backfill?”

But time travel works because old metadata and old files are retained.

Retaining history costs storage.

It also increases metadata management complexity.

If you never expire old snapshots or clean obsolete files, your table may carry a long historical tail.

That may be intentional.

But it should be intentional.

A platform needs retention policies.

For example:

```
Table type: operational analytics
Snapshot retention: 7–30 days

Table type: financial reporting
Snapshot retention: monthly or quarterly release snapshots

Table type: ML training features
Snapshot retention: aligned with experiment reproducibility needs

Table type: raw regulated healthcare data
Snapshot retention: governed by compliance and audit requirements
```

The mistake is treating time travel as free.

It is not free.

It is a storage and metadata retention feature.

Sometimes that cost is absolutely worth paying.

Sometimes it quietly becomes an archive of every mistake the platform ever made.

History is valuable.

But unlimited history is also a basement.

Eventually, someone has to clean it.

---

## 7. Deletes and Updates Are More Expensive Than Appends

Object storage likes immutable objects.

Appending new files is relatively natural.

Updating and deleting records are harder.

Lakehouse formats support updates and deletes through different mechanisms, such as rewriting files, using delete files, maintaining logs, indexing records, or applying merge-on-read/copy-on-write strategies.

This is powerful.

But it is not the same as updating rows in a traditional database.

Consider a single record update inside a large Parquet file.

The object store does not modify a tiny row in place.

The system may need to:

- write delete metadata;
- rewrite a file;
- create a new version of affected data;
- update table metadata;
- preserve old files for active readers or time travel;
- clean obsolete files later.

At scale, updates and deletes can become expensive.

This matters for use cases such as:

- GDPR deletion requests;
- CDC replication;
- slowly changing dimensions;
- high-frequency upserts;
- late-arriving corrections;
- record-level deduplication;
- mutable operational data;
- streaming change capture.

If your workload is mostly append-only, lakehouse formats are usually happier.

If your workload is update-heavy, you must understand the format’s write path.

A table format may support upserts.

That does not mean upserts are free.

“Supports” and “cheaply supports at your scale and workload pattern” are not the same sentence.

This is where many architectures get surprised.

---

## 8. Copy-on-Write vs Merge-on-Read: Pick Your Pain

A common design trade-off in lakehouse systems is between copy-on-write and merge-on-read behavior.

The exact implementation differs across formats and engines, but the conceptual trade-off is useful.

### Copy-on-write

When records are updated, affected data files are rewritten.

This tends to make reads simpler and faster because the latest data is already materialized in clean files.

But writes can be more expensive.

Conceptually:

```
Update record
    ↓
Find affected file
    ↓
Rewrite file with updated record
    ↓
Commit new table version
```

Good for:

- read-heavy workloads;
- dashboards;
- reporting tables;
- analytics marts;
- tables where query performance matters more than write speed.

Cost:

- more expensive updates;
- more rewrite activity;
- possible write amplification.

### Merge-on-read

Updates are written separately and merged during reads or during later compaction.

This can make writes faster.

But reads may become more expensive because the engine must combine base files and change/delete files.

Conceptually:

```
Write update/delete metadata
    ↓
Keep base file
    ↓
Merge base + changes during read or compaction
```

Good for:

- write-heavy workloads;
- frequent upserts;
- CDC ingestion;
- near-real-time updates.

Cost:

- more complex reads;
- compaction becomes important;
- query latency may vary;
- readers must understand how to merge correctly.

Neither is universally better.

The question is:

> Do you want to pay more at write time, read time, or maintenance time?

You will pay somewhere.

Distributed systems are not generous. They just let you choose the invoice category.

---

## 9. Partitioning Is Still Hard

Lakehouse formats improve partition management, but they do not make partition design irrelevant.

Bad partitioning still hurts.

Common mistakes include:

### Over-partitioning

Example:

```python
partition_by = ["year", "month", "day", "hour", "customer_id"]
```

This may create too many tiny partitions and files.

High-cardinality partitioning often causes pain.

Just because you can partition by `customer_id` does not mean you should.

### Under-partitioning

Example:

```python
partition_by = ["year"]
```

This may force queries to scan too much data when most workloads filter by day or month.

### Partitioning by the wrong access pattern

If users usually query by `event_date`, but the table is partitioned by `ingestion_date`, query performance may suffer.

Sometimes both dates matter, but they serve different purposes.

### Assuming partitioning solves everything

Partitioning helps skip large chunks of data.

But it does not replace:

- clustering;
- sorting;
- statistics;
- file sizing;
- query design;
- data skipping;
- materialized aggregates;
- good modeling.

Lakehouse formats can support hidden partitioning, partition evolution, or metadata-based pruning.

That is excellent.

But the platform still needs to understand how the data is queried.

Storage layout is a product decision disguised as an engineering detail.

---

## 10. Object-Store Request Costs Are Real

Object storage is cheap per GB compared with many alternatives.

But object storage also charges, directly or indirectly, for operations.

Typical operations include:

- listing objects;
- reading object metadata;
- reading files;
- writing files;
- deleting files;
- copying files;
- accessing many small objects.

Even when direct request costs are small, the operational effect can be large.

A query that touches thousands of files is different from one that touches millions.

A compaction job that rewrites terabytes is not free.

A table maintenance process that lists huge prefixes repeatedly can become expensive and slow.

Lakehouse formats often reduce unnecessary scanning through metadata pruning.

But metadata itself may require object reads.

A poorly maintained table may cause:

- expensive planning;
- slow metadata loading;
- high API request volume;
- increased latency;
- higher cloud bills;
- more fragile operations.

The lesson:

> Storage cost is not only bytes stored. It is also bytes read, files touched, metadata processed, and maintenance performed.

A lakehouse table can be cheap at rest and expensive in motion.

That distinction matters.

---

## 11. Query Planning Can Become the Bottleneck

In a traditional database, the engine has a catalog, indexes, statistics, and storage internals tightly integrated.

In a lakehouse, the query engine often needs to consult table metadata to determine which files to read.

For well-optimized tables, this is efficient.

For messy tables, planning can become slow.

Symptoms include:

- queries take a long time before reading data;
- query engines spend time loading metadata;
- planning time grows with snapshot/file count;
- simple queries feel strangely delayed;
- metadata caches become important;
- performance varies across engines.

This is especially visible when:

- tables have too many files;
- metadata is fragmented;
- snapshots are excessive;
- manifests or logs are large;
- partitions are too granular;
- cleanup has not run;
- many commits happen frequently.

The platform may say:

> “The query only scans 50 MB.”

But the user experiences:

> “Why did it take 40 seconds to start?”

That gap is often metadata planning overhead.

Again: metadata is not imaginary.

Metadata is part of the workload.

---

## 12. Multi-Engine Access Is Powerful, But Compatibility Is Work

One promise of lakehouse formats is that multiple engines can access the same tables.

For example:

- Spark;
- Trino;
- Flink;
- Presto;
- Athena-like engines;
- Databricks runtimes;
- Snowflake-style external table integrations;
- DuckDB or local readers in some contexts;
- custom jobs.

This is a major advantage.

It prevents data from being locked entirely inside one compute system.

But multi-engine access introduces compatibility questions:

- Does every engine support the same table features?
- Does every engine understand the same version of the format?
- Are deletes handled correctly?
- Are schema changes interpreted consistently?
- Are timestamp types handled the same way?
- Are generated columns or constraints supported?
- Are partition transforms understood?
- Are catalog operations consistent?
- Are write operations safe from every engine?
- Are some engines read-only for this table?

A table format may be open.

That does not mean every engine supports every feature equally.

This is one of the most important hidden costs.

You need a compatibility matrix.

For example:

| Feature | Spark | Trino | Flink | BI Query Engine |
|---|---|---|---|---|
| Read table | Yes | Yes | Yes | Yes |
| Write table | Yes | Limited | Yes | No |
| MERGE support | Yes | Partial | Depends | No |
| Row-level deletes | Yes | Depends | Depends | No |
| Time travel | Yes | Yes | Limited | Maybe |
| Schema evolution | Yes | Partial | Depends | Maybe |

The exact values depend on your stack.

The point is that the platform must know.

Otherwise, someone will write a table with one engine and discover another engine interprets it like a confused archaeologist.

Open table formats reduce lock-in.

They do not eliminate integration work.

---

## 13. Catalogs Become Critical Infrastructure

Lakehouse tables need catalogs.

A catalog tracks table names, locations, schemas, metadata pointers, namespaces, and sometimes permissions.

Examples of catalog-like components include:

- Hive Metastore;
- AWS Glue Catalog;
- Unity Catalog;
- Nessie;
- REST catalogs;
- cloud-native metadata services;
- platform-specific catalogs.

The catalog becomes a critical part of the system.

If the catalog is slow, misconfigured, inconsistent, unavailable, or poorly governed, the lakehouse suffers.

Hidden catalog costs include:

- permissions management;
- metadata consistency;
- migration between catalogs;
- engine compatibility;
- namespace design;
- table discovery;
- access control;
- audit logging;
- cross-environment promotion;
- disaster recovery;
- catalog API limits or latency.

A lakehouse is not just:

```
object storage + Parquet
```

It is more like:

```
object storage
+ table format
+ metadata files/logs
+ catalog
+ query engines
+ maintenance jobs
+ governance
+ access control
+ observability
```

That is a platform.

And platforms have operational surfaces.

The catalog is one of them.

Treat it casually, and it will eventually become the tiny hinge on which a large door falls off.

---

## 14. Concurrency Is Better, But Not Effortless

Lakehouse formats improve concurrent access compared with plain file writes.

They can support atomic commits and isolation.

But concurrent writes are still complex.

Potential issues include:

- commit conflicts;
- optimistic concurrency retries;
- multiple writers touching the same partitions;
- streaming and batch jobs writing together;
- compaction conflicting with ingestion;
- backfills racing with production updates;
- schema changes during active writes;
- long-running reads needing old snapshots;
- cleanup jobs removing files too aggressively.

A common scenario:

```
Streaming ingestion writes every few minutes.
A batch backfill rewrites historical partitions.
A compaction job optimizes small files.
An analyst runs time travel query.
A schema evolution PR lands at noon.
```

This is not impossible.

But it requires coordination.

A table format gives you mechanisms.

It does not give you governance automatically.

You still need rules:

- Which jobs may write to this table?
- Can multiple jobs write to the same partition?
- When do compaction jobs run?
- How are backfills isolated?
- How are schema changes approved?
- What happens if commits conflict?
- Who owns recovery?
- What is the rollback strategy?

Concurrent lakehouse writes are like multiple people cooking in the same kitchen.

A good kitchen can support that.

But someone still needs to decide who gets the oven.

---

## 15. Streaming Into Lakehouse Tables Has Special Costs

Streaming into lakehouse tables is attractive.

It lets teams land events continuously into an analytical table.

But streaming writes often create small files and frequent commits.

This can increase:

- metadata churn;
- snapshot count;
- file count;
- compaction requirements;
- commit overhead;
- reader planning overhead.

A streaming ingestion pattern might produce:

```
Every 1 minute:
    write small batch of records
    create new files
    commit new table version
```

After a day, this may create many commits and many files.

After a month, the table may be technically correct but operationally bloated.

This does not mean streaming into lakehouse tables is bad.

It means you must design around it.

Useful strategies include:

- tune micro-batch interval;
- control target file size;
- compact regularly;
- partition carefully;
- separate hot and cold data;
- use staging tables;
- aggregate before serving;
- avoid exposing raw high-churn tables directly to BI;
- expire snapshots according to policy.

Streaming plus lakehouse can be powerful.

But streaming plus object storage plus tiny files plus no maintenance is how data platforms become haunted.

---

## 16. Deletes for Compliance Are Not a Button You Press Once

Modern data platforms often need deletion support for privacy and compliance.

Examples:

- GDPR right to erasure;
- patient data correction;
- consent withdrawal;
- customer deletion;
- contractual retention rules;
- legal hold exceptions.

Lakehouse formats can help by supporting deletes and time travel management.

But compliance deletion is not only a table operation.

You must consider:

- raw data;
- curated tables;
- derived tables;
- feature stores;
- backups;
- snapshots;
- historical versions;
- cached query results;
- downstream exports;
- ML training datasets;
- logs and metadata;
- object versioning;
- replication;
- disaster recovery copies.

If a record is deleted from the current snapshot but remains accessible through time travel, old files, backups, or downstream copies, the compliance story may be incomplete.

This is subtle and important.

A table format can support deletion.

But the platform must define deletion semantics.

Questions include:

- Should deleted records disappear from time travel?
- How long are old snapshots retained?
- Are legal hold datasets exempt?
- How are derived datasets updated?
- How are delete operations audited?
- How do we prove deletion occurred?
- How do we handle backups?
- How do we coordinate across multiple tables?

This is where technical architecture meets governance.

And governance, unlike Parquet, does not compress well.

---

## 17. Data Skipping Helps, But It Depends on Good Statistics

Lakehouse formats may store file-level statistics such as min/max values, null counts, partition values, and other metadata that helps query engines skip irrelevant files.

This is one of their big strengths.

For example, a query asks:

```sql
WHERE event_date = '2026-07-01'
  AND country = 'BR'
```

If metadata shows that many files do not contain that date or country, the engine can skip them.

Wonderful.

But skipping depends on useful layout and useful statistics.

Data skipping works poorly when:

- files contain highly mixed values;
- clustering is poor;
- columns used in filters lack stats;
- stats are missing or stale;
- data is not sorted or grouped;
- files are too small or too chaotic;
- query predicates do not match available metadata.

For example:

```
File A:
    country values: BR, US, DE, FR, CN, IN, ZA, ...
    event_date: many months mixed together
```

This file is hard to skip.

Compare:

```
File B:
    country values: BR
    event_date: 2026-07-01 to 2026-07-03
```

This is easier to prune.

The lakehouse format can store statistics.

But data layout determines whether those statistics are useful.

The platform still needs physical design.

You cannot metadata your way out of all bad layout decisions.

That sentence is painful, but medicinal.

---

## 18. Schema Evolution Can Create Semantic Confusion

Lakehouse formats often support schema evolution.

That is excellent.

But schema evolution is not semantic evolution.

Adding, renaming, dropping, or changing columns affects downstream consumers.

A table may technically evolve successfully while breaking meaning.

Examples:

- `amount` changes from cents to currency units;
- `event_time` changes from local time to UTC;
- `user_id` changes from anonymous ID to account ID;
- `status` values change from uppercase to lowercase;
- `country` changes from full name to ISO code;
- `diagnosis_code` changes from ICD-9 to ICD-10;
- `genome_build` changes from GRCh37 to GRCh38.

The table format may accept the change.

But downstream logic may not.

This is why data contracts matter.

A table format manages structure and snapshots.

A data contract manages expectations between producers and consumers.

They are complementary.

Without contracts, schema evolution can become a polite way to break things.

The metadata says “commit successful.”

The dashboard says “why is Brazil gone?”

---

## 19. Table Maintenance Requires Scheduling and Ownership

Lakehouse tables need maintenance jobs.

Depending on the format and workload, maintenance may include:

- compact small files;
- rewrite data files;
- rewrite manifests or metadata;
- expire snapshots;
- clean orphan files;
- vacuum old files;
- cluster or sort data;
- update table statistics;
- validate table consistency;
- repair metadata;
- optimize partitions.

These jobs need:

- schedules;
- compute resources;
- permissions;
- monitoring;
- retries;
- alerting;
- conflict rules;
- cost tracking;
- ownership.

Who owns compaction?

The ingestion team?
The platform team?
The domain team?
The analytics engineering team?
The mysterious “data lake team” that exists only in architecture diagrams?

If nobody owns maintenance, maintenance does not happen consistently.

Then tables degrade.

Then queries slow down.

Then people blame the table format.

Sometimes the format is not the problem.

Sometimes the problem is that the table has not had a haircut since 2024.

---

## 20. Orphan Files Are the Ghosts of Failed Writes

Object storage does not automatically know which files are valid table data.

A failed job may leave files behind.

A canceled write may upload objects before the commit succeeds.

A manual operation may create files in the wrong place.

A buggy process may write files that are not referenced by current metadata.

These are orphan files.

They consume storage and create confusion.

Lakehouse formats generally rely on metadata to determine which files are part of the table.

Orphan files may not affect query correctness if they are not referenced.

But they still cost money.

They also complicate operations.

Cleaning them requires care.

If a cleanup job deletes files too aggressively, it may remove files still needed by active snapshots, time travel, or long-running queries.

If it is too conservative, junk accumulates.

Again, maintenance policy matters.

The data lake is not only about writing files.

It is also about knowing which files are no longer needed.

Object storage is patient.

It will keep your mistakes forever if you pay it.

---

## 21. Backfills Can Be Expensive and Dangerous

Backfills are common in data platforms.

You may need to:

- fix historical logic;
- add a new derived column;
- correct bad source data;
- regenerate partitions;
- rebuild features;
- reprocess a date range;
- migrate table format;
- change partitioning;
- recover from an incident.

Lakehouse formats support backfills better than plain file lakes.

But backfills can still be costly.

They may:

- rewrite huge amounts of data;
- create many new snapshots;
- invalidate cached results;
- conflict with streaming writes;
- increase object-store requests;
- create temporary duplicate storage;
- trigger downstream rebuilds;
- require snapshot cleanup later.

Backfills also create correctness questions:

- Are old outputs fully replaced?
- Are consumers reading mixed old/new logic?
- Is the backfill atomic from the consumer perspective?
- Do downstream tables need to be rebuilt?
- Can we roll back?
- How do we communicate the change?

A backfill is not just a big job.

It is a controlled historical rewrite.

The table format helps make that possible.

It does not remove the need for planning.

Backfills are where data platforms reveal whether they are engineered systems or just optimistic pipelines in a trench coat.

---

## 22. Migration Between Formats Is Not Trivial

Some teams start with plain Parquet, then move to Delta.
Or Delta to Iceberg.
Or Hudi to Iceberg.
Or Hive-style tables to a lakehouse format.
Or platform-specific tables to open formats.

Migration is possible.

But it is rarely just “change the table type.”

You must consider:

- metadata conversion;
- catalog registration;
- partition layout;
- schema compatibility;
- historical snapshots;
- delete semantics;
- writer compatibility;
- downstream query engines;
- permissions;
- data contracts;
- validation;
- rollback strategy;
- performance comparisons;
- user communication.

A migration can also reveal hidden assumptions.

For example:

- some jobs depend on folder layout directly;
- some users query files instead of tables;
- some partitions have inconsistent schemas;
- some historical files are corrupt;
- some timestamps are interpreted differently;
- some columns have illegal names for one engine;
- some dashboards rely on behavior specific to one runtime.

The lakehouse table format may be open, but your platform may have years of sediment.

Migration is geology with SQL.

---

## 23. Vendor and Runtime Differences Matter

Delta, Iceberg, and Hudi are table formats, but real-world behavior depends heavily on the runtime and platform.

The same format may behave differently depending on:

- Spark version;
- Databricks runtime;
- Trino version;
- Flink integration;
- cloud engine support;
- catalog implementation;
- configuration defaults;
- writer settings;
- supported table features;
- enabled protocol versions;
- storage backend behavior.

This means platform teams must test the actual stack.

Not the abstract format.

Not the conference diagram.

The actual combination of:

```
table format
+ engine
+ catalog
+ object store
+ permissions
+ workload
+ file sizes
+ partitioning
+ maintenance jobs
+ users
```

That is the system.

And the system is what fails.

Not the brochure.

---

## 24. Cost Visibility Is Often Weak

Many organizations do not know the true cost of individual lakehouse tables.

They may know the total cloud bill.

But not:

- cost per table;
- cost per pipeline;
- cost per query workload;
- cost per compaction job;
- cost per backfill;
- cost of small files;
- cost of snapshot retention;
- cost of streaming commits;
- cost of repeated metadata operations.

Without cost attribution, hidden costs stay hidden.

A platform should ideally track:

- storage size by table;
- file count by table;
- average file size;
- snapshot count;
- metadata size;
- number of commits;
- compaction frequency;
- read/query cost;
- write cost;
- maintenance cost;
- downstream usage.

Then you can ask useful questions:

- Which tables are expensive but rarely used?
- Which tables have too many small files?
- Which tables are queried heavily and need optimization?
- Which tables retain too much history?
- Which streaming tables create excessive commits?
- Which backfills created cost spikes?
- Which consumers drive the most spend?

Data platform cost is not only infrastructure accounting.

It is product analytics for your internal data products.

If nobody uses a table but it costs a lot to maintain, that is a product signal.

Possibly also a ghost story.

---

## 25. The Human Cost: Cognitive Load

Lakehouse formats add concepts.

Engineers must understand:

- snapshots;
- manifests;
- transaction logs;
- catalogs;
- table properties;
- metadata cleanup;
- compaction;
- partition evolution;
- schema evolution;
- delete files;
- commit conflicts;
- writer modes;
- time travel;
- vacuum/retention policies;
- multi-engine compatibility.

This is not a criticism.

Powerful tools require concepts.

But the platform should not assume every user understands them deeply.

Analysts should not need to know the difference between manifest rewrite and file compaction to query a business table.

Data scientists should not need to debug snapshot expiration to train a model.

Application teams should not invent their own write patterns to publish events.

This is where data platform engineering matters.

The platform should hide complexity where possible and expose it where necessary.

Good platform design provides:

- standard table templates;
- recommended defaults;
- safe write APIs;
- maintenance automation;
- documentation;
- observability dashboards;
- ownership metadata;
- cost reporting;
- compatibility guidelines;
- runbooks.

Otherwise, the lakehouse becomes powerful but artisanal.

Artisanal is nice for bread.

Less nice for enterprise data infrastructure.

---

## 26. The Three Formats Have Different Personalities

It is dangerous to reduce Iceberg, Delta, and Hudi to one sentence each, but it is useful to understand their general personalities.

### Apache Iceberg

Iceberg is often appreciated for its clean table abstraction, hidden partitioning, partition evolution, snapshot model, and strong multi-engine ambitions.

It is commonly attractive when teams want an open table format across multiple engines.

Hidden costs often involve:

- catalog choices;
- metadata maintenance;
- engine compatibility;
- manifest management;
- operational tuning;
- ensuring all engines support required features.

### Delta Lake

Delta Lake is closely associated with transaction logs, strong Spark integration, and broad adoption in Databricks-centered ecosystems.

It is often attractive when teams are heavily Spark/Databricks-oriented and want reliable ACID-style table behavior with good tooling.

Hidden costs often involve:

- runtime/platform coupling decisions;
- protocol compatibility;
- vacuum/retention management;
- small file optimization;
- feature support across non-native engines;
- governance of writes from multiple tools.

### Apache Hudi

Hudi has historically been strong around incremental processing, upserts, CDC-style ingestion, and copy-on-write/merge-on-read table types.

It is often attractive for high-churn data, streaming ingestion, and record-level mutation patterns.

Hidden costs often involve:

- indexing choices;
- compaction/clustering scheduling;
- read/write mode trade-offs;
- operational complexity;
- tuning for workload-specific behavior;
- ensuring readers interpret merge-on-read tables correctly.

This is not a ranking.

It is a reminder:

> The best table format depends on workload, ecosystem, operational maturity, and platform goals.

Choosing a format is not like choosing a favorite color.

It is more like choosing a transportation system for a city.

Roads, trains, bikes, and boats all move people.

The right answer depends on geography, budget, traffic, maintenance, and whether someone keeps driving trucks into tunnels.

---

## 27. A Practical Decision Framework

When evaluating Iceberg, Delta, or Hudi on object storage, ask these questions.

### 1. What is the dominant workload?

Is the table mostly:

- append-only?
- read-heavy?
- update-heavy?
- streaming ingestion?
- CDC replication?
- BI serving?
- ML feature generation?
- regulatory snapshotting?
- large historical backfills?

Different workloads favor different configurations and sometimes different formats.

### 2. How fresh must the data be?

If commits happen every minute, metadata churn and small files matter.

If data updates daily, maintenance is simpler.

### 3. How often do records change?

Append-only event logs are different from mutable customer profiles.

Update-heavy workloads need careful design.

### 4. Which engines must read and write?

A table used only by Spark has different requirements from a table shared by Spark, Trino, Flink, BI tools, and cloud query services.

### 5. How much history must be retained?

Time travel is useful, but retention must be explicit.

### 6. Who owns maintenance?

If nobody owns compaction, cleanup, and optimization, the table will age badly.

### 7. How will costs be measured?

Track storage, files, metadata, query cost, maintenance cost, and usage.

### 8. What happens when something goes wrong?

You need rollback, replay, incident response, and validation.

### 9. What is the governance model?

Consider ownership, permissions, contracts, schema evolution, deletion policies, and auditability.

### 10. Can the team operate this?

A slightly less elegant design that the team can operate is better than a theoretically superior system nobody understands.

Architecture is not a beauty contest.

It is a maintenance commitment.

---

## 28. Practical Signals That Your Lakehouse Table Is Getting Sick

Watch for these symptoms:

- query planning time increases;
- simple queries take longer to start;
- average file size decreases;
- file count grows faster than data volume;
- snapshot count grows without retention policy;
- compaction jobs become longer or fail often;
- metadata directories grow unexpectedly;
- storage cost rises faster than usage;
- BI dashboards become inconsistent or slow;
- different engines return different results;
- streaming writes create too many commits;
- backfills become risky;
- cleanup jobs are disabled because people fear deleting data;
- nobody knows who owns a table;
- users query raw high-churn tables directly;
- developers bypass the catalog and read paths directly.

These are not random annoyances.

They are platform health signals.

A mature data platform should monitor them.

Because the earlier you detect lakehouse table decay, the cheaper it is to fix.

Ignoring table maintenance is like ignoring dental care.

Eventually, the bill includes drilling.

---

## 29. What Good Looks Like

A healthy lakehouse setup usually has a few common properties.

### Tables have clear ownership

Every important table has a responsible team.

### Maintenance is automated

Compaction, cleanup, snapshot expiration, and optimization are scheduled and monitored.

### File sizes are controlled

Writers are configured to avoid pathological small files.

### Retention is explicit

Time travel and snapshot history follow policy.

### Catalogs are governed

Tables are discoverable, permissioned, and consistently registered.

### Compatibility is tested

Supported engines and operations are documented.

### Costs are visible

Storage, query, and maintenance costs can be attributed.

### Data contracts exist for critical tables

Schema and semantic changes are managed.

### Observability includes table health

The platform monitors freshness, volume, file count, metadata growth, and query performance.

### Users access curated tables

Raw high-churn internals are not exposed as primary business products unless intentionally designed.

In other words:

> A lakehouse table is treated like a product, not a folder.

That is the mature shift.

---

## 30. A Small Example: Table Health Checklist

A platform team might maintain a simple health summary like this:

```
table: analytics.orders_gold
owner: finance-data-platform

storage:
  total_size_tb: 8.4
  file_count: 42000
  average_file_size_mb: 205

metadata:
  snapshot_count: 42
  oldest_snapshot_retained_days: 14
  metadata_size_gb: 3.1

freshness:
  expected_by: "07:00"
  last_updated_at: "2026-07-12 06:41"
  status: ok

maintenance:
  compaction_enabled: true
  last_compaction: "2026-07-12 03:20"
  orphan_cleanup_enabled: true
  snapshot_expiration_enabled: true

usage:
  queries_last_7_days: 18320
  downstream_assets:
    - finance_daily_dashboard
    - executive_revenue_report
    - revenue_forecasting_features

risk:
  small_file_risk: low
  metadata_growth_risk: medium
  compatibility_risk: low
```

This is not glamorous.

It is very useful.

The platform now knows whether the table is operationally healthy.

Not just whether it exists.

---

## 31. The Healthcare and Biotech Angle

In healthcare and biotech, the hidden costs of lakehouse formats matter because the data is large, sensitive, and often governed.

Examples include:

- EHR extracts;
- claims data;
- clinical events;
- lab results;
- imaging metadata;
- genomic variant tables;
- RNA-seq matrices;
- cohort definitions;
- phenotype tables;
- model features;
- longitudinal patient histories.

These datasets may require:

- auditability;
- reproducibility;
- deletion policies;
- access control;
- stable releases;
- provenance;
- schema governance;
- semantic versioning;
- careful handling of sensitive data.

Lakehouse formats can help.

Time travel, snapshots, schema evolution, and table-level management are valuable.

But the hidden costs are also serious.

For example:

### Genomics

Variant tables may be huge and version-sensitive.

A table may depend on:

- reference genome build;
- variant caller version;
- annotation database version;
- filtering thresholds;
- sample cohort;
- pipeline release.

Time travel is useful, but retention and reproducibility must be governed.

### EHR data

Clinical tables may receive updates, corrections, late-arriving records, and source-specific schema changes.

Record-level updates and deletes matter.

So do patient-level access rules and auditability.

### ML features

Feature tables need consistency across training and inference.

Stale snapshots, inconsistent reads, or untracked schema changes can affect model behavior.

In these domains, table format choices should not be purely technical.

They are part of the trust architecture.

A healthcare lakehouse is not just a cheap place to store Parquet.

It is a governed analytical substrate.

Yes, that phrase sounds like it owns a blazer.

But it is true.

---

## 32. Anti-Patterns

### Anti-pattern 1: “We use Iceberg/Delta/Hudi, so the lake is solved”

No.

You solved one layer and introduced another.

A table format is not a complete data platform.

### Anti-pattern 2: No maintenance jobs

Without compaction, cleanup, and retention policies, tables degrade.

### Anti-pattern 3: Streaming tiny files forever

High-frequency writes without file-size control or compaction create long-term pain.

### Anti-pattern 4: Unlimited time travel

Useful for debugging. Expensive as a default forever policy.

### Anti-pattern 5: Everyone writes to the same table

Multiple writers without clear ownership and conflict rules cause chaos.

### Anti-pattern 6: Direct path access

Users bypass the catalog and query object paths directly.

This undermines table semantics.

### Anti-pattern 7: Format choice based only on trend

Choose based on workload, ecosystem, operations, and governance.

Not on which mascot is currently winning conference slides.

### Anti-pattern 8: No compatibility testing

Assuming every engine handles every feature correctly is how subtle bugs enter.

### Anti-pattern 9: Ignoring object-store costs

Request costs, metadata operations, compaction, and backfills all matter.

### Anti-pattern 10: Treating table health as invisible

If you do not monitor file counts, metadata growth, snapshots, and query planning, you are flying with one eye closed.

---

## 33. The Deeper Principle: Open Table Format Does Not Mean Low-Complexity Table

Open table formats are important.

They reduce lock-in, improve interoperability, and bring database-like capabilities to data lakes.

But open does not mean simple.

A well-run lakehouse requires:

- table design;
- metadata management;
- catalog governance;
- compute tuning;
- storage layout;
- workload isolation;
- compatibility testing;
- maintenance automation;
- observability;
- cost attribution;
- ownership.

The hidden cost is not that Iceberg, Delta, or Hudi are bad.

They are useful precisely because the underlying problem is hard.

The hidden cost is believing the format alone solves the platform problem.

It does not.

It gives you better building blocks.

You still need architecture.

You still need operations.

You still need discipline.

You still need someone to ask why a table has 19 million files and a dashboard loading like it is powered by candlelight.

---

## 34. Final Thought

Iceberg, Delta, and Hudi are major steps forward for data engineering.

They make object storage much more usable for analytical tables.

They support reliability patterns that plain data lakes struggled with for years:

- atomic commits;
- table snapshots;
- schema evolution;
- time travel;
- updates and deletes;
- incremental processing;
- better metadata pruning;
- multi-engine access.

But the lakehouse is not magic.

The hidden costs are real:

- metadata growth;
- small files;
- compaction;
- snapshot retention;
- object-store request overhead;
- query planning latency;
- catalog complexity;
- multi-engine compatibility;
- concurrency management;
- streaming write churn;
- compliance deletion semantics;
- maintenance ownership;
- cognitive load;
- cost visibility.

These costs are not reasons to avoid lakehouse formats.

They are reasons to operate them properly.

The mature view is not:

> “Which table format makes object storage behave like a database for free?”

The mature view is:

> “Which table format, with which catalog, engines, maintenance processes, contracts, and observability, best supports our workloads and governance needs?”

That is the real platform question.

A lakehouse table is not just a folder of Parquet files.

It is a living data product with metadata, history, consumers, owners, costs, and failure modes.

Treat it that way, and Iceberg, Delta, or Hudi can be powerful foundations.

Ignore that, and your elegant lakehouse may slowly become what every data platform fears becoming:

a very expensive bucket full of technically valid confusion.
