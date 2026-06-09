Title: The Sunday Materialization - Z-Ordering vs. Partitioning
Subtitle: What No One Tells You About Query Speed, Data Layout, and the Fine Art of Not Scanning the Universe
Date: 2025-11-09 07:00
Modified: 2025-11-09 07:00
Category: Sunday
Tags: data engineer, data platform engineer, data, data architecture, z-ordering, partitioning, data skipping, lakehouse, query optimization
Slug: sunday-materialization-z-ordering-vs-partitioning
Authors: Eduardo G Gusmao
Summary: A weekly educational topic/lecture/discussion on Data Engineering topics that we all experienced at least once (or will!)
Status: final
Lang: en
Template: topic
Cadence: Biweekly
Scope: Data Engineering, Industry, Data Challenges
Tone: Analytical, Educational, Non-Sensational
Canonical: https://www.gusmaolab.org/blog/sunday-materialization-z-ordering-vs-partitioning/
Meta_description: Biweekly analysis of important Data Engineering concepts.
Meta_keywords: data concepts, topics, lectures, discussions, z-ordering, partitioning, data skipping, lakehouse optimization
Cover: images/covers/z-ordering-vs-partitioning.png
Thumbnail: images/thumbnails/z-ordering-vs-partitioning-thumb.png

# Z-Ordering vs. Partitioning: What No One Tells You About Query Speed

There is a classic moment in every data platform's life.

A table gets big.

Not "cute big."
Not "the CSV takes a while to open" big.
Actually big.

Millions of rows become billions.
Gigabytes become terabytes.
Dashboards begin to sigh before loading.
Queries that once felt instant now behave like they are walking through airport security with twelve laptops.

Someone asks:

> "Can we make this faster?"

And then the ancient words appear:

> "Let's partition the table."

Partitioning is often the first optimization people reach for. And sometimes it is exactly right.

But sometimes it is not.

Sometimes the table is already partitioned, and queries are still slow.

Sometimes partitioning helps one query and hurts five others.

Sometimes the partition layout creates thousands of tiny files.

Sometimes everyone filters by columns that are not the partition columns.

Sometimes the query engine scans too much data even though the table is "optimized."

And then someone says:

> "Maybe we should Z-order it."

At this point, several people nod.

One person pretends to know exactly what Z-ordering means.

Another opens documentation.

A third quietly wonders whether Z-ordering is a cousin of Pokémon.

So let's make it clear.

**Partitioning** and **Z-ordering** are both data layout strategies. They help query engines avoid reading unnecessary data. But they work differently, solve different problems, and fail in different ways.

The goal is not to choose one forever.

The goal is to understand what each one does, where each one helps, and how to avoid turning your lakehouse into an expensive filing cabinet designed by a committee of raccoons.

---

## 1. The Core Problem: Query Engines Hate Scanning Useless Data

Analytical query performance depends heavily on how much data the engine must read.

Suppose you have a table with 10 TB of customer events.

You run:

```sql
SELECT
    COUNT(*) AS purchase_events
FROM events
WHERE event_date = DATE '2026-08-23'
  AND event_type = 'purchase';
```

The logical query is simple.

But physically, the engine must answer:

> Which files might contain rows for `event_date = 2026-08-23` and `event_type = purchase`?

If the table is poorly organized, the engine may scan far too many files.

If the table is well organized, it can skip most of them.

That is the heart of query speed in lakehouses and warehouses:

> Fast queries often come from reading less data, not from heroic computation.

This is especially true for object storage and columnar formats like Parquet.

Parquet helps because it stores data by column and includes statistics. Lakehouse formats like Delta Lake, Iceberg, and Hudi help because they manage metadata, snapshots, files, and sometimes additional statistics.

But the physical layout still matters.

A query engine cannot skip data efficiently if related data is scattered everywhere like glitter after a birthday party.

Partitioning and Z-ordering are two ways to reduce unnecessary scanning.

They are both about making data easier to skip.

---

## 2. What Partitioning Actually Does

Partitioning splits a table into separate physical groups based on one or more columns.

For example:

```text
events/
    event_date=2026-08-21/
        part-0001.parquet
        part-0002.parquet

    event_date=2026-08-22/
        part-0001.parquet
        part-0002.parquet

    event_date=2026-08-23/
        part-0001.parquet
        part-0002.parquet
```

If a query filters by `event_date`, the engine can skip entire directories or partition groups.

Example:

```sql
SELECT *
FROM events
WHERE event_date = DATE '2026-08-23';
```

The engine does not need to inspect partitions for `2026-08-21` or `2026-08-22`.

That is partition pruning.

Partition pruning is powerful because it removes large chunks of data before scanning files.

In plain English:

> Partitioning puts data into labeled boxes. If your query asks for one box, the engine does not open the others.

Very useful.

Very simple.

Very easy to misuse.

---

## 3. Partitioning Works Best for Low-to-Medium Cardinality Columns

A good partition column usually has a manageable number of distinct values.

Common examples:

- date;
- month;
- region;
- country;
- source system;
- organization;
- tenant, sometimes;
- data domain;
- event type, sometimes.

The most classic partition column is a date.

Example:

```text
partition_by = event_date
```

This works well because many analytical queries filter by date.

But partitioning by high-cardinality columns can be disastrous.

Example:

```text
partition_by = customer_id
```

If you have 50 million customers, you may create millions of tiny partitions.

That leads to:

- too many directories or metadata entries;
- too many small files;
- slow planning;
- expensive object-store listing;
- painful maintenance;
- poor compaction behavior;
- sad data engineers staring into the distance.

High-cardinality partitioning feels intuitive because it sounds selective.

But physical systems care about manageability.

A partition should be large enough to be useful and small enough to prune.

If each partition contains three rows and a dream, you have not optimized the table.

You have shredded it.

---

## 4. The Partitioning Trap: One Layout, Many Query Patterns

Partitioning is powerful, but it is rigid.

A table usually has one primary partition layout.

Suppose you partition events by date:

```text
events/
    event_date=2026-08-21/
    event_date=2026-08-22/
    event_date=2026-08-23/
```

This is great for queries like:

```sql
SELECT *
FROM events
WHERE event_date = DATE '2026-08-23';
```

But what about this?

```sql
SELECT *
FROM events
WHERE customer_id = 'C123';
```

If customer `C123` has events across many dates, the engine may need to inspect many date partitions.

Partitioning by date helps date queries.

It does not automatically help customer queries.

Now suppose you partition by customer.

Customer queries improve, but date queries may suffer. Also, you probably create a horrifying number of partitions.

This is the problem:

> Partitioning is excellent when your dominant filter pattern matches your partition columns.

But data products often have multiple access patterns.

For an event table, users may filter by:

- event date;
- customer ID;
- account ID;
- event type;
- country;
- device;
- product area;
- campaign;
- session ID.

You cannot partition efficiently by everything.

Well, technically you can try.

But the result may look like this:

```text
event_date=2026-08-23/
    country=BR/
        event_type=purchase/
            customer_id=C123/
                part-0001.parquet
```

This may look organized, but it can easily become over-partitioned.

A table layout is not a decorative taxonomy.

It is a performance structure.

---

## 5. What Z-Ordering Actually Does

Z-ordering is a clustering technique.

Instead of splitting data into separate partitions based on a column, Z-ordering tries to colocate related records within files based on one or more columns.

In simplified terms:

> Z-ordering rearranges data so that rows with similar values in selected columns are stored close together.

This improves data skipping.

Suppose you Z-order by `customer_id`.

Then records for the same or nearby customer IDs are more likely to be stored in the same files or nearby file ranges.

When you query:

```sql
SELECT *
FROM events
WHERE customer_id = 'C123';
```

the engine may skip many files because file-level statistics show that most files do not contain the relevant customer range.

Z-ordering is especially useful when:

- partitioning by a column would create too many partitions;
- queries filter by high-cardinality columns;
- queries use multiple filter columns;
- the table is large;
- file-level statistics are available;
- the engine can use data skipping.

In plain English:

> Partitioning puts data into boxes with labels. Z-ordering arranges the contents inside the boxes so related things sit near each other.

That is the key distinction.

Partitioning is coarse-grained layout.

Z-ordering is fine-grained clustering.

---

## 6. A Simple Mental Model

Imagine a giant library.

Partitioning is like putting books into separate rooms.

One room for 2024.
One room for 2025.
One room for 2026.

If you need books from 2026, you skip the other rooms.

Great.

Z-ordering is like organizing books **inside a room** so that related books are near each other.

Within the 2026 room, books about Brazil are near each other.
Books about healthcare are near each other.
Books about Spark are near each other.

If you need 2026 healthcare books, you enter the 2026 room and quickly find the relevant shelf.

Partitioning chooses the room.

Z-ordering organizes the shelves.

If you only have rooms but no shelf organization, you may still search a lot inside the room.

If you only organize shelves but all books are in one gigantic room, you may still have too much to navigate.

Used together, they can be powerful.

Used badly, they can create a library where every book has its own room and the librarian has resigned.

---

## 7. Partitioning vs. Z-Ordering in One Table

| Feature | Partitioning | Z-Ordering |
|---|---|---|
| Main idea | Split data into physical partitions | Cluster related records within files |
| Best for | Low/medium-cardinality filters | High-cardinality or multi-column filters |
| Typical columns | Date, region, source, tenant | Customer ID, account ID, user ID, event type |
| Main benefit | Partition pruning | File/data skipping |
| Risk | Too many partitions, small files | Maintenance cost, imperfect clustering |
| Granularity | Coarse | Fine |
| Query dependency | Works best when query filters partition column | Works when query filters clustered columns and stats help |
| Maintenance | Partition management, compaction | Re-optimization / clustering jobs |
| Good default? | Date partitioning often is | Depends strongly on query patterns |
| Bad use case | High-cardinality partition column | Columns rarely used in filters |

This table is useful, but the real world is messier.

The true question is:

> Which layout minimizes the amount of data read for the workloads that matter most?

That is the game.

Not "partitioning good" or "Z-ordering fancy."

The query workload decides.

---

## 8. Why Z-Ordering Helps With Multi-Column Queries

Z-ordering is related to a space-filling curve.

That sounds like mathematics wearing a cape.

The intuition is simple enough.

Suppose you often filter by two columns:

```sql
WHERE customer_id = 'C123'
  AND event_type = 'purchase'
```

If data is sorted only by `customer_id`, records for a customer may be near each other, but event types may still be mixed.

If data is sorted only by `event_type`, purchases may be near each other, but customer IDs may be scattered.

Z-ordering tries to preserve locality across multiple columns.

It creates an ordering where records similar across selected dimensions tend to be near each other.

This is useful for compound filters.

Example:

```sql
WHERE account_id = 'A900'
  AND event_date BETWEEN DATE '2026-08-01' AND DATE '2026-08-23'
  AND event_type = 'upgrade'
```

If the table is partitioned by date and Z-ordered by `account_id, event_type`, the engine may:

1. prune irrelevant date partitions;
2. skip files inside relevant partitions that do not contain the account or event type.

That is a strong combination.

Partitioning reduces the search space.

Z-ordering improves skipping inside the remaining search space.

This is where people start to see significant performance gains.

Not because the query engine became smarter by magic.

Because the data layout stopped being hostile.

---

## 9. The Thing No One Tells You: Z-Ordering Is Not an Index

Z-ordering is sometimes explained like an index.

That is not quite right.

A database index is a separate access structure that points to rows or pages.

Z-ordering physically reorganizes data files so that file-level statistics and locality become more useful.

This distinction matters.

With Z-ordering, the engine is not usually doing a direct index lookup like:

> "Go exactly to row 912,332."

Instead, it is more like:

> "These files are likely relevant; those files can be skipped."

Z-ordering improves pruning, but it does not make point lookups behave like a transactional database.

If you need millisecond lookups by primary key, a lakehouse table with Z-ordering may not be the right serving system.

Use a database, key-value store, search index, feature store, cache, or serving layer designed for that access pattern.

This is a common mistake:

> "We Z-ordered by customer_id, so now customer lookups should be instant."

No.

They may be much faster.

But the lakehouse is still an analytical storage system.

A warehouse table wearing a Z-order jacket is not suddenly Redis.

---

## 10. The Other Thing No One Tells You: Partitioning Can Make Queries Slower

Partitioning is not automatically good.

Bad partitioning can make queries slower.

How?

### Too many partitions

The engine spends too much time planning, listing, and managing metadata.

Example:

```text
partition_by = user_id
```

Millions of users may produce millions of partitions.

Terrible.

### Too many small files

Each partition may contain many tiny files.

This increases overhead.

### Partition columns do not match queries

If users rarely filter by the partition column, partition pruning does not help much.

### Skewed partitions

Some partitions are huge, others tiny.

Example:

```text
country=US/
    8 TB

country=LU/
    4 MB
```

Queries touching the large partition may still be slow.

### Over-nested partitions

Partitioning by many columns can create a sparse directory explosion.

Example:

```text
date / country / device / event_type / campaign
```

This may produce thousands or millions of tiny combinations.

A bad partition layout is like a filing cabinet where every page has its own drawer.

Very organized.

Completely unusable.

---

## 11. Cardinality: The Word That Quietly Decides Everything

Cardinality means the number of distinct values in a column.

For example:

| Column | Cardinality |
|---|---|
| `event_date` | Low/medium |
| `country` | Low/medium |
| `event_type` | Low |
| `customer_id` | High |
| `user_id` | Very high |
| `session_id` | Extremely high |
| `transaction_id` | Extremely high |

Partitioning likes low-to-medium cardinality.

Z-ordering is often useful for high-cardinality columns.

Why?

Because partitioning by high-cardinality columns creates too many partitions.

But Z-ordering can cluster high-cardinality values without making each value its own partition.

Example:

- partition by `event_date`;
- Z-order by `customer_id`.

This is often better than:

- partition by `event_date` and `customer_id`.

The latter may explode the partition count.

The former keeps date-based pruning while improving customer-based skipping within each date.

This is one of the most practical rules:

> Partition by columns that define large useful chunks. Z-order by columns that help skip inside those chunks.

That sentence should probably be printed and taped near someone's Databricks workspace.

---

## 12. A Practical Example: Event Table

Suppose we have a large event table:

```text
events
- event_id
- customer_id
- account_id
- event_type
- event_timestamp
- event_date
- country
- device_type
- session_id
```

Common queries:

### Query A: Daily dashboard

```sql
SELECT
    event_date,
    event_type,
    COUNT(*) AS n_events
FROM events
WHERE event_date BETWEEN DATE '2026-08-01' AND DATE '2026-08-23'
GROUP BY event_date, event_type;
```

### Query B: Customer investigation

```sql
SELECT *
FROM events
WHERE customer_id = 'C123'
  AND event_date >= DATE '2026-08-01';
```

### Query C: Account-level product analytics

```sql
SELECT
    account_id,
    COUNT(*) AS n_events
FROM events
WHERE event_date >= DATE '2026-08-01'
  AND event_type = 'purchase'
GROUP BY account_id;
```

A reasonable layout might be:

```text
Partition by:
    event_date

Z-order by:
    customer_id, account_id, event_type
```

Why?

- `event_date` is used in most queries and has manageable cardinality.
- `customer_id` and `account_id` are high-cardinality and useful for selective filters.
- `event_type` is low-cardinality but often used with other filters.

This layout allows:

- date partition pruning;
- file skipping for customer/account/event-type queries within date ranges.

Would this be perfect for every query?

No.

There is no universal perfect layout.

But it is aligned with common access patterns.

That is the point.

---

## 13. A Bad Example: Partitioning by Too Much

Suppose someone says:

> "Let's partition by date, country, event type, and customer ID."

The layout becomes:

```text
event_date=2026-08-23/
    country=BR/
        event_type=purchase/
            customer_id=C123/
                part-0001.parquet
```

This looks specific.

But it may create a huge number of partitions.

Problems:

- many partition directories;
- small files;
- slow metadata operations;
- difficult compaction;
- sparse partitions;
- expensive writes;
- poor performance for broad scans;
- painful schema/table maintenance.

If most customers generate only a few events per day, each customer partition may be tiny.

The query engine may spend more time opening and planning files than reading meaningful data.

This is why "more partitioning" is not always better.

Optimization is not seasoning.

You cannot just keep adding it.

---

## 14. A Better Example: Partition Coarse, Cluster Fine

Instead:

```text
Partition by:
    event_date

Cluster / Z-order by:
    customer_id, event_type
```

The physical layout is simpler:

```text
event_date=2026-08-23/
    part-0001.parquet
    part-0002.parquet
    part-0003.parquet
```

But inside the files, records are organized so similar `customer_id` and `event_type` values are near each other.

Now the table keeps manageable partitions and still supports selective skipping.

This is a useful design principle:

> Use partitioning to eliminate obvious large chunks. Use clustering/Z-ordering to improve locality within those chunks.

Coarse outside. Smart inside.

Like a coconut.

Or a well-designed data platform.

---

## 15. Z-Ordering Is Maintenance, Not a One-Time Blessing

Z-ordering is not something you do once and forget forever.

As new data arrives, clustering quality may degrade.

Streaming writes, micro-batches, incremental updates, and frequent merges can introduce new files that are not well clustered.

Over time, the table may need re-optimization.

Conceptually:

```sql
OPTIMIZE events
ZORDER BY (customer_id, account_id);
```

Exact syntax depends on platform and table format support.

The important part is operational:

- When do you run Z-order optimization?
- How often?
- On which partitions?
- With how much compute?
- Who owns the cost?
- How do you avoid conflicts with writes?
- How do you monitor whether it helped?
- How do you decide which columns deserve it?

Z-ordering is not free.

It rewrites data.

It consumes compute.

It may create temporary storage pressure.

It may need scheduling.

It may need table maintenance windows.

Therefore, Z-ordering should be used where the benefit justifies the maintenance.

Do not Z-order every table by every column because it sounds advanced.

That is not optimization.

That is ritual.

---

## 16. How File Statistics Make Skipping Work

Columnar file formats like Parquet often store statistics at the file or row-group level.

Examples:

- minimum value;
- maximum value;
- null count;
- sometimes distinct counts or other metadata depending on system.

Suppose a Parquet file has:

```text
file: part-0007.parquet
customer_id_min: C100
customer_id_max: C199
event_date_min: 2026-08-23
event_date_max: 2026-08-23
```

A query asks:

```sql
WHERE customer_id = 'C900'
```

The engine can skip that file because `C900` cannot be inside the `C100-C199` range.

But this only works well if values are clustered.

If every file contains a wide range:

```text
file: part-0007.parquet
customer_id_min: C001
customer_id_max: C999999
```

Then the engine cannot skip much.

Z-ordering improves the usefulness of file statistics by making each file cover a narrower region of the selected columns.

That is the practical magic.

Not magic-magic.

Metadata magic.

The best kind. Usually.

---

## 17. Why Sorting Is Not the Same as Z-Ordering

You may wonder:

> Why not just sort by columns?

Sorting can help.

If you sort by `customer_id`, records with the same customer are near each other.

But if you frequently filter by multiple columns, simple sorting has limitations.

Sort order is hierarchical.

Example:

```text
ORDER BY customer_id, event_type
```

This primarily groups by `customer_id`, then by `event_type` within each customer.

But if a query filters by `event_type` without filtering by `customer_id`, this ordering may not help as much.

Z-ordering tries to preserve locality across multiple dimensions more evenly than simple lexicographic sorting.

That said, sorting can be perfectly useful in many systems.

The right choice depends on engine support and workload.

The broader lesson:

> Physical clustering improves skipping when clustered columns match query filters.

Whether this is done by Z-ordering, sorting, clustering, bucketing, or engine-specific layout optimization depends on the platform.

Do not worship the name.

Understand the mechanism.

---

## 18. Z-Ordering Too Many Columns Can Dilute the Benefit

A common mistake:

> "Let's Z-order by every column users might filter."

Please do not.

Z-ordering across too many columns can dilute locality.

If you choose ten columns, the clustering may become less effective for the most important two or three.

Also, optimization becomes more expensive.

Better approach:

- identify the most common selective filters;
- choose columns that appear frequently in high-value queries;
- prefer high-cardinality or moderately selective columns;
- avoid columns rarely used in filters;
- avoid columns with low utility for skipping;
- measure before and after.

Good candidates:

- `customer_id`;
- `account_id`;
- `user_id`;
- `device_id`;
- `order_id`, sometimes;
- `event_type`, when combined with other filters;
- `country`, sometimes;
- `tenant_id`, depending on layout.

Bad candidates:

- columns rarely used in `WHERE` clauses;
- columns with constant or near-constant values;
- columns used only in `SELECT`;
- columns used only after massive aggregation;
- columns whose statistics are not collected or not useful;
- too many columns at once.

A good Z-order column is not just important.

It must help the engine skip files.

That is the test.

---

## 19. Partitioning by Date Is Common, But Not Always Enough

Date partitioning is the default instinct for many event and fact tables.

And often it is correct.

Most analytical workloads filter by time.

Example:

```sql
WHERE event_date BETWEEN DATE '2026-08-01' AND DATE '2026-08-23'
```

Date partitioning helps the engine ignore other dates.

But if each date contains huge amounts of data, scanning one day may still be expensive.

Example:

```text
event_date=2026-08-23
    size: 700 GB
```

If users often query one customer within one day, date partitioning still leaves too much data.

Query:

```sql
SELECT *
FROM events
WHERE event_date = DATE '2026-08-23'
  AND customer_id = 'C123';
```

Partitioning gets you to the right day.

Z-ordering by `customer_id` helps avoid scanning all 700 GB inside that day.

This is the practical reason partitioning and Z-ordering often complement each other.

Partitioning says:

> "Only look at this day."

Z-ordering says:

> "Inside this day, look near this customer."

Together, they prevent the engine from reading the whole haystack when you asked for one needle and the needle has a customer ID.

---

## 20. Partitioning Can Help Writes Too

Partitioning is not only about reads.

It can also help writes and maintenance.

For example, if your pipeline processes one day at a time, date partitioning lets you overwrite or replace one day.

```sql
INSERT OVERWRITE TABLE events
PARTITION (event_date = DATE '2026-08-23')
SELECT *
FROM staging_events
WHERE event_date = DATE '2026-08-23';
```

This is operationally convenient.

It supports:

- daily ingestion;
- backfills;
- partition-level validation;
- partition replacement;
- easier cleanup;
- lifecycle management;
- retention policies.

Z-ordering does not replace this.

Z-ordering improves clustering and skipping, but partitioning often defines operational boundaries.

This is an underrated point.

Partitioning is not only a performance tool.

It is also a lifecycle tool.

If you need to delete, archive, replace, or backfill data by date, date partitions are useful even if query performance is not the only concern.

Data layout serves operations too.

---

## 21. But Partitioning Can Hurt Writes

Partitioning can also make writes worse if the partition design is too granular.

Suppose a streaming job writes events every minute.

Partitioned by date only:

```text
event_date=2026-08-23/
    many micro-batch files
```

This may create small files but is manageable with compaction.

Partitioned by date, country, event type, and customer segment:

```text
event_date=2026-08-23/
    country=BR/
        event_type=click/
            customer_segment=trial/
                tiny_file_1.parquet
                tiny_file_2.parquet
```

Now each micro-batch may write tiny files into many partition combinations.

This creates:

- small files;
- metadata growth;
- slow planning;
- more expensive compaction;
- more object-store operations;
- uneven partition sizes.

So partitioning affects both read and write patterns.

A partition strategy that looks good for one query may be terrible for ingestion.

Always ask:

- How is data written?
- How often?
- In what batch size?
- Which partitions are touched per write?
- Are writes append-only or upserts?
- Do we compact?
- Do we backfill?
- Do we stream?

Physical design is a negotiation between readers, writers, and maintenance.

Like most negotiations, everyone leaves slightly disappointed but functional.

That is architecture.

---

## 22. Data Skipping Is Not Guaranteed

Data skipping depends on several things:

- file statistics exist;
- the query engine uses them;
- the filter predicate can be pushed down;
- the data is clustered enough for stats to be selective;
- files are not too broad in value ranges;
- the query is written in a way the optimizer understands.

Example:

```sql
WHERE customer_id = 'C123'
```

This is easy to use for skipping.

But this may be harder:

```sql
WHERE LOWER(customer_id) = 'c123'
```

The function may prevent simple predicate pushdown depending on engine.

Similarly:

```sql
WHERE CAST(customer_id AS STRING) = 'C123'
```

or:

```sql
WHERE SUBSTRING(customer_id, 1, 3) = 'C12'
```

These may reduce skipping effectiveness.

Even with good layout, query shape matters.

This is why performance tuning is not only storage design.

It includes:

- data types;
- query predicates;
- optimizer behavior;
- statistics;
- file layout;
- engine configuration;
- table maintenance.

One bad cast can ruin a beautiful layout.

Data platforms are humbling like that.

---

## 23. Measuring Whether Partitioning or Z-Ordering Helped

Never assume optimization worked because it sounds correct.

Measure.

Useful metrics:

- bytes scanned;
- files scanned;
- files skipped;
- partitions scanned;
- query planning time;
- execution time;
- shuffle size;
- task count;
- cache usage;
- cost per query;
- dashboard refresh time;
- table file count;
- average file size;
- compaction/optimization cost.

Before optimizing, capture baseline queries.

Example benchmark table:

| Query | Before | After | Improvement |
|---|---:|---:|---:|
| Daily dashboard | 90 sec | 25 sec | 3.6x |
| Customer lookup | 180 sec | 12 sec | 15x |
| Account usage report | 240 sec | 55 sec | 4.4x |
| Full monthly scan | 300 sec | 310 sec | Slightly worse |

That last row matters.

Some optimizations improve selective queries but do nothing for full scans.

If a query must read the whole table, Z-ordering may not help much.

You cannot skip data if the query asks for all of it.

A forklift does not help if your goal is to move the entire warehouse across the street.

Actually, it helps a little.

But you get the point.

---

## 24. When Partitioning Is the Right Answer

Partitioning is usually the right first tool when:

- queries frequently filter by the same low/medium-cardinality column;
- the column defines natural lifecycle boundaries;
- partitions are large enough to avoid tiny files;
- backfills and retention happen by that column;
- ingestion naturally arrives by that column;
- partition pruning removes large amounts of data.

Common good choices:

### Date/time partitioning

```text
event_date
transaction_date
ingestion_date
reporting_month
```

### Source or domain partitioning

```text
source_system
data_domain
organization_id, if cardinality is controlled
```

### Region/country, sometimes

Useful if queries often filter by geography and partitions are not too skewed.

Partitioning is especially good when the question is:

> Can we avoid entire chunks of the table based on a clear boundary?

If yes, partitioning may help a lot.

---

## 25. When Z-Ordering Is the Right Answer

Z-ordering is often useful when:

- the table is already partitioned but partitions are still large;
- queries filter by high-cardinality columns;
- partitioning by those columns would create too many partitions;
- common queries filter by multiple columns;
- file-level statistics can support skipping;
- the cost of optimization is justified by read performance gains.

Good candidates:

- customer lookup in large event table;
- account-level analytics inside date partitions;
- user-level behavioral investigation;
- product-event filtering;
- tenant filtering in multi-tenant datasets;
- selective queries on large fact tables.

Example:

```text
Partition by:
    event_date

Z-order by:
    account_id, user_id
```

Good when:

- most queries have date filters;
- many queries also filter by account or user;
- daily partitions are large;
- account/user IDs are too high-cardinality for partitioning.

Z-ordering is especially good when the question is:

> Inside the partitions we already need to read, can we skip most files using selective columns?

If yes, Z-ordering may help.

---

## 26. When Neither Is Enough

Sometimes partitioning and Z-ordering are not enough.

A query may be slow because:

- it scans too much by design;
- it performs expensive joins;
- it aggregates huge data;
- it has skew;
- it uses complex UDFs;
- it needs pre-aggregation;
- it lacks a semantic/modeling layer;
- it queries raw data instead of curated data;
- it joins on poorly distributed keys;
- it runs on underpowered compute;
- it competes with other workloads;
- statistics are stale;
- files are too small;
- the query engine is misconfigured.

Example:

```sql
SELECT
    customer_id,
    COUNT(*) AS n_events,
    COUNT(DISTINCT session_id) AS n_sessions,
    COUNT(DISTINCT product_id) AS n_products
FROM events
WHERE event_date BETWEEN DATE '2025-01-01' AND DATE '2026-08-23'
GROUP BY customer_id;
```

This query may legitimately need to scan a lot of data.

Partitioning can prune outside the date range.

Z-ordering may help some.

But the query is fundamentally large.

Better solutions may include:

- precomputed aggregates;
- materialized views;
- summary tables;
- cube/rollup tables;
- approximate distinct counts;
- incremental aggregation;
- dedicated serving marts;
- workload-specific data models.

Data layout helps.

It does not repeal computational reality.

The laws of physics remain annoyingly employed.

---

## 27. Z-Ordering vs. Liquid Clustering, Bucketing, Sorting, and Other Cousins

Depending on your platform, you may hear related terms:

- clustering;
- liquid clustering;
- bucketing;
- sorting;
- sort keys;
- distribution keys;
- data skipping;
- ordering;
- clustering keys;
- multidimensional clustering.

These are not identical, but they live in the same neighborhood.

They all ask:

> How should data be physically organized so queries read less and run faster?

Different systems implement different mechanisms.

For example:

- warehouses may use clustering keys or sort keys;
- Spark tables may use bucketing or sorting;
- Delta ecosystems may use Z-ordering or liquid clustering depending on platform;
- Iceberg tables may use partition transforms, sorting, and metadata pruning;
- Hudi may use clustering and indexing strategies;
- BigQuery has partitioning and clustering;
- Snowflake has micro-partitions and optional clustering behavior.

Do not get trapped by vocabulary.

Ask the practical questions:

- What metadata does the engine store?
- What can the optimizer skip?
- Which columns are used for pruning?
- How is clustering maintained?
- What is the write cost?
- What is the read benefit?
- How does this interact with partitioning?
- Does this work across our engines?

The names differ.

The principle remains:

> Put related data close enough that the engine can avoid reading unrelated data.

That is the whole opera.

---

## 28. The Healthcare and Biotech Angle

In healthcare and biotech, physical layout choices can matter enormously.

Consider clinical events.

A table may include:

- patient ID;
- encounter ID;
- diagnosis code;
- procedure code;
- lab test code;
- event date;
- hospital;
- department;
- source system.

Common queries:

- all events for one patient;
- all patients with a diagnosis code;
- lab results in a date range;
- encounters for one hospital;
- cohort extraction over several years;
- quality indicators by month;
- phenotype definitions using codes and dates.

A reasonable design might partition by event month or year, then cluster by patient ID and clinical code.

Example:

```text
Partition by:
    event_month

Z-order / cluster by:
    patient_id, diagnosis_code
```

This helps queries that filter by time and patient/code.

But there are trade-offs.

If cohort definitions scan many years and many codes, layout may help less than a curated phenotype index or precomputed cohort table.

For genomics, consider variant tables.

Columns may include:

- chromosome;
- position;
- sample ID;
- gene;
- variant ID;
- consequence;
- cohort;
- genome build.

Common layout:

```text
Partition by:
    chromosome

Cluster / sort by:
    position
```

This makes genomic interval queries efficient.

But if users often query by `sample_id` across the genome, clustering by sample may help different workloads.

There is no universal layout.

The access pattern decides.

Biomedical data makes this especially clear:

- patient-centric queries want patient locality;
- gene-centric queries want gene/position locality;
- cohort queries want cohort/release locality;
- longitudinal queries want time locality.

One table layout may not serve all of these equally.

Sometimes the right answer is multiple curated tables optimized for different use cases.

Duplication? Yes.

Wasteful? Not necessarily.

A serving table optimized for a real workload is often cheaper than forcing every query through one universal mega-table that performs equally badly for everyone.

The universal table is a seductive myth.

Like "one ontology to rule them all."

We keep trying. The universe keeps laughing.

---

## 29. Data Modeling Still Matters

Physical layout cannot fix bad modeling.

If dashboards query raw event tables directly, they may be slow even with good partitioning and Z-ordering.

If users repeatedly compute the same metrics from scratch, the table layout is not the only problem.

If every query joins fifteen tables to calculate a business KPI, maybe the platform needs curated marts.

Example:

Instead of every dashboard running:

```sql
SELECT
    DATE_TRUNC('day', e.event_timestamp) AS event_day,
    c.customer_segment,
    COUNT(DISTINCT e.user_id) AS active_users
FROM raw.events e
JOIN raw.customers c
    ON e.customer_id = c.customer_id
WHERE e.event_date >= DATE '2026-08-01'
  AND e.event_type IN ('login', 'purchase', 'feature_use')
GROUP BY
    DATE_TRUNC('day', e.event_timestamp),
    c.customer_segment;
```

Create a curated daily aggregate:

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
WHERE event_date >= DATE '2026-08-01';
```

No amount of Z-ordering can fully compensate for making every dashboard redo the same heavy transformation.

Data layout helps the engine.

Data modeling helps the user and the engine.

Both matter.

---

## 30. The Cost Side: Optimization Is Not Free

Partitioning has costs.

Z-ordering has costs.

Compaction has costs.

Clustering has costs.

Optimization is a trade-off between write cost, maintenance cost, storage layout, and query performance.

### Partitioning costs

- more metadata;
- more directories or partition entries;
- small files if overused;
- slower writes if many partitions are touched;
- harder partition evolution;
- skewed partition sizes.

### Z-ordering costs

- compute to rewrite files;
- temporary storage during optimization;
- scheduling maintenance jobs;
- possible write conflicts;
- degraded clustering as new data arrives;
- need for monitoring and re-optimization.

### Over-optimization costs

- complex table maintenance;
- confusing platform behavior;
- unnecessary compute spend;
- optimizing low-value queries;
- making writes slower for marginal read gains.

This is why the question should not be:

> Can we optimize this table?

The question should be:

> Which queries matter enough to justify physical optimization?

A table used once per month by one analyst does not need the same care as a table powering executive dashboards, ML features, and customer-facing metrics.

Performance work is product work.

Prioritize by impact.

---

## 31. A Practical Decision Framework

Here is a simple framework.

### Step 1: Identify the critical queries

Do not optimize abstractly.

Collect actual queries:

- dashboards;
- scheduled reports;
- analyst workflows;
- ML feature generation;
- customer investigations;
- reverse ETL source models;
- regulatory extracts.

### Step 2: Find common filters

Look at `WHERE` clauses.

Which columns appear often?

Examples:

- date;
- customer;
- account;
- event type;
- region;
- source system.

### Step 3: Estimate cardinality

For each candidate column, ask:

- How many distinct values?
- Is it skewed?
- Does it grow over time?
- Would partitioning create too many partitions?

### Step 4: Choose partition columns

Pick columns that:

- are commonly filtered;
- have manageable cardinality;
- define useful operational boundaries;
- avoid tiny partitions;
- align with ingestion/backfill/retention.

Usually one or two partition columns are enough.

Often one is enough.

### Step 5: Choose clustering/Z-order columns

Pick columns that:

- are commonly filtered inside partitions;
- are selective;
- are too high-cardinality for partitioning;
- help important queries skip files.

Usually a small number of columns is best.

### Step 6: Measure

Compare before and after:

- bytes scanned;
- files skipped;
- query time;
- planning time;
- cost;
- maintenance overhead.

### Step 7: Monitor decay

Optimization quality changes over time.

Track:

- file count;
- average file size;
- clustering effectiveness;
- query performance trends;
- optimization job cost.

A layout decision is not a tattoo.

It can evolve.

Please do not tattoo table layouts.

---

## 32. Practical Rules of Thumb

Here are useful rules, with the usual warning that rules of thumb are not laws of nature.

### Rule 1: Partition by date when time filtering dominates

Most event/fact tables benefit from date partitioning if queries and lifecycle operations are date-based.

### Rule 2: Avoid partitioning by very high-cardinality IDs

Do not partition by `user_id`, `session_id`, `transaction_id`, or similar columns unless you have a very specific reason.

### Rule 3: Z-order high-cardinality columns used in selective filters

Good examples: `customer_id`, `account_id`, `user_id`.

### Rule 4: Do not Z-order by everything

Choose a few important columns.

Too many columns dilute locality and increase maintenance cost.

### Rule 5: Partitioning helps most when queries filter the partition column

If users do not filter by the partition column, partitioning may not help.

### Rule 6: Z-ordering helps most when data skipping can use file statistics

If the engine cannot use the stats, the layout may not matter.

### Rule 7: Optimize important tables, not every table

Maintenance costs money.

Spend it where performance matters.

### Rule 8: Watch small files

Bad file sizes can ruin both partitioning and Z-ordering benefits.

### Rule 9: Pre-aggregate when queries are fundamentally large

If the query needs massive aggregation every time, physical layout alone may not save it.

### Rule 10: Measure, or it did not happen

Performance tuning without measurement is astrology with SQL.

Fun, but not a platform strategy.

---

## 33. Example: Diagnosing a Slow Query

Suppose this query is slow:

```sql
SELECT
    customer_id,
    COUNT(*) AS purchases
FROM events
WHERE event_date BETWEEN DATE '2026-08-01' AND DATE '2026-08-23'
  AND event_type = 'purchase'
GROUP BY customer_id;
```

Questions:

### Does the table partition by `event_date`?

If yes, irrelevant dates can be pruned.

If no, the engine may scan much more data.

### How large are the date partitions?

If each day is huge, date pruning alone may not be enough.

### Is `event_type` selective?

If purchases are 2% of events, clustering or Z-ordering by `event_type` may help.

If purchases are 80% of events, it may help less.

### Is the table Z-ordered by `event_type` or `customer_id`?

If yes, file skipping may improve.

### Is this query repeated often?

If yes, maybe create a daily purchases aggregate.

```sql
CREATE TABLE mart.daily_customer_purchases AS
SELECT
    event_date,
    customer_id,
    COUNT(*) AS purchases
FROM events
WHERE event_type = 'purchase'
GROUP BY event_date, customer_id;
```

Then query:

```sql
SELECT
    customer_id,
    SUM(purchases) AS purchases
FROM mart.daily_customer_purchases
WHERE event_date BETWEEN DATE '2026-08-01' AND DATE '2026-08-23'
GROUP BY customer_id;
```

This may beat any layout optimization on raw events.

The lesson:

> First reduce unnecessary scanning. Then reduce unnecessary computation. Then consider whether the query should exist at that granularity at all.

A beautiful raw table does not eliminate the need for marts.

---

## 34. Example: Multi-Tenant SaaS Analytics

Suppose a company has a multi-tenant application.

Table:

```text
events
- tenant_id
- user_id
- event_type
- event_timestamp
- event_date
```

Queries often filter by tenant:

```sql
SELECT *
FROM events
WHERE tenant_id = 'T123'
  AND event_date >= DATE '2026-08-01';
```

Should we partition by `tenant_id`?

Maybe.

But it depends.

If there are 50 tenants, partitioning by tenant may be fine.

If there are 500,000 tenants, probably not.

A common pattern:

```text
Partition by:
    event_date

Z-order by:
    tenant_id, user_id
```

This supports date pruning and tenant/user skipping.

But if tenant isolation is operationally important - separate retention, separate exports, separate access control - then tenant partitioning may be considered for some tables.

Again, performance is not the only factor.

Partitioning can also support governance and lifecycle operations.

Physical design is where performance, cost, and governance awkwardly shake hands.

---

## 35. Example: Claims Data

In healthcare claims data, common filters may include:

- service date;
- payer;
- provider;
- patient/member;
- diagnosis code;
- procedure code.

A table might be partitioned by `service_month` because claims analysis is often time-bound and backfills happen by period.

But analysts may often ask:

```sql
WHERE member_id = 'M123'
```

or:

```sql
WHERE diagnosis_code IN ('E11', 'E11.9')
```

Partitioning by `member_id` or `diagnosis_code` may be problematic.

A reasonable approach:

```text
Partition by:
    service_month

Cluster / Z-order by:
    member_id, diagnosis_code, provider_id
```

But if diagnosis-code queries are central and code-based cohorts are frequent, the platform may also create specialized cohort index tables.

For example:

```text
member_diagnosis_index
- member_id
- diagnosis_code
- first_seen_date
- last_seen_date
- claim_count
```

This avoids repeatedly scanning raw claims for common cohort definitions.

Physical layout helps.

Purpose-built models help more.

The trick is knowing when to stop optimizing the raw table and start building the right derived table.

---

## 36. The "One Big Table" Problem

Many platforms create one enormous table intended to serve everyone.

It contains every event, every attribute, every timestamp, every flag, every ID, and perhaps the hopes and disappointments of several teams.

Then everyone queries it.

Performance becomes difficult because different users want different access patterns.

- Analysts want time aggregates.
- Support wants customer history.
- Product wants feature events.
- ML wants training features.
- Finance wants revenue events.
- Compliance wants reproducible extracts.

One layout cannot optimize all of that equally.

Partitioning and Z-ordering help, but they cannot turn one table into every possible serving model.

Sometimes the right answer is multiple physical representations:

- raw event table;
- cleaned event table;
- customer activity mart;
- account usage mart;
- daily aggregate table;
- feature table;
- audit snapshot;
- search/index table.

This may duplicate data.

That is okay if it reduces repeated computation and improves reliability.

Storage is often cheaper than everyone scanning the universe every morning.

The "single source of truth" should mean shared definitions and governed lineage.

It does not have to mean one physical table for every workload.

One physical table to rule them all is how Mordor gets a cloud bill.

---

## 37. Common Anti-Patterns

### Anti-pattern 1: Partitioning by high-cardinality ID

Usually creates too many partitions and small files.

### Anti-pattern 2: Partitioning by columns no one filters

Looks organized. Does not help.

### Anti-pattern 3: Too many partition columns

Creates sparse partition combinations and metadata overhead.

### Anti-pattern 4: Z-ordering every table

Wastes compute when query patterns do not justify it.

### Anti-pattern 5: Z-ordering too many columns

Dilutes clustering benefit.

### Anti-pattern 6: Ignoring file size

Small files can ruin the performance benefits of good layout.

### Anti-pattern 7: Optimizing without measuring

You may improve nothing and still pay for maintenance.

### Anti-pattern 8: Expecting Z-ordering to behave like an index

It helps skipping. It does not make a lakehouse a low-latency key-value store.

### Anti-pattern 9: Using raw tables for every dashboard

Physical layout cannot replace proper data modeling.

### Anti-pattern 10: Forgetting maintenance

Data layout decays as new data arrives.

Optimization needs ownership.

---

## 38. What Good Looks Like

A healthy table optimization strategy usually has these traits:

### Workload-aware design

Partitioning and Z-ordering choices come from real query patterns.

### Conservative partitioning

Few partition columns, chosen carefully.

### Clustering for selective filters

Z-ordering or clustering used for columns that drive file skipping.

### Good file sizes

Compaction keeps files reasonably sized.

### Regular maintenance

Optimization jobs run where needed, not everywhere blindly.

### Observability

The platform tracks query time, bytes scanned, files skipped, and maintenance cost.

### Clear ownership

Someone owns table health.

### Derived models where appropriate

Heavy repeated queries become marts or aggregates.

### Governance awareness

Partitioning may also support retention, deletion, access control, or release boundaries.

In short:

> Good physical design is not about making the table look organized. It is about making important workloads cheaper, faster, and safer.

---

## 39. A Small Practical Checklist

Before partitioning or Z-ordering a table, ask:

1. What are the top 10 most important queries?
2. Which columns do they filter by?
3. Which filters are most selective?
4. Which filters appear in nearly every query?
5. What is the cardinality of each candidate column?
6. Are values evenly distributed or skewed?
7. How is data ingested?
8. How often is data updated or merged?
9. What partitions are touched during writes?
10. Are there many small files?
11. What is the current average file size?
12. What is the current query planning time?
13. How many files are scanned per query?
14. How many bytes are scanned?
15. Are users querying raw data when they should use marts?
16. Would an aggregate table solve the problem better?
17. What is the maintenance cost of optimization?
18. Who owns optimization jobs?
19. How will we measure improvement?
20. How will we know when the layout stops working?

This checklist is not glamorous.

It is better than guessing.

And guessing is how tables become expensive folklore.

---

## 40. Final Thought

Partitioning and Z-ordering are not rivals.

They are different tools for the same deeper goal:

> Help the query engine avoid reading data that does not matter.

Partitioning works at the coarse level.

It divides data into large physical chunks that can be pruned when queries filter by partition columns.

Z-ordering works at the finer level.

It clusters related records so file-level statistics become more selective and the engine can skip more files inside the relevant partitions.

Partitioning is usually best for low-to-medium-cardinality columns with strong lifecycle or query boundaries, especially dates.

Z-ordering is often best for high-cardinality or multi-column filters where partitioning would explode the table into tiny fragments.

But neither is magic.

Bad partitioning can make tables slower.

Z-ordering requires maintenance.

Small files can ruin everything.

Query shape matters.

Data modeling still matters.

And sometimes the right answer is not a cleverer layout, but a better mart, aggregate, index, serving layer, or data product.

The mature approach is not:

> Should we partition or Z-order?

The mature approach is:

> What are our critical workloads, what data do they actually need to read, and how should the table be physically organized so they read as little unnecessary data as possible?

That is the real question.

Query speed is not only about compute.

It is about layout.

It is about metadata.

It is about access patterns.

It is about maintenance.

It is about refusing to scan the entire lake every time someone asks for one glass of water.

Partition wisely.

Z-order selectively.

Measure always.

And never trust a table that looks organized but makes every query read the universe.
