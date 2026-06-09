Title: The Sunday Materialization - Change Data Capture Is Powerful
Subtitle: Why CDC Pipelines Need Ordering, Idempotency, and Respect for the Timeline
Date: 2026-02-01 07:00
Modified: 2026-02-01 07:00
Category: Sunday
Tags: data engineer, data platform engineer, data, data architecture, change data capture, CDC, event ordering, streaming, data reliability
Slug: sunday-materialization-cdc-ordering
Authors: Eduardo G Gusmao
Summary: A weekly educational topic/lecture/discussion on Data Engineering topics that we all experienced at least once (or will!)
Status: final
Lang: en
Template: topic
Cadence: Biweekly
Scope: Data Engineering, Industry, Data Challenges
Tone: Analytical, Educational, Non-Sensational
Canonical: https://www.gusmaolab.org/blog/sunday-materialization-cdc-ordering/
Meta_description: Biweekly analysis of important Data Engineering concepts.
Meta_keywords: data concepts, topics, lectures, discussions, CDC, change data capture, event ordering, data reliability
Cover: images/covers/cdc-ordering.png
Thumbnail: images/thumbnails/cdc-ordering-thumb.png

# Change Data Capture (CDC) Is Powerful - And Dangerous If You Ignore Ordering

Change Data Capture, usually called **CDC**, is one of those ideas that sounds obvious after you understand it.

Instead of repeatedly asking a database:

> "What changed since yesterday?"

CDC says:

> "Tell me every insert, update, and delete as it happens."

That is powerful.

It allows data platforms to move from periodic extraction toward continuous replication, near-real-time analytics, event-driven architectures, operational synchronization, audit trails, and fresh data products.

CDC can feed:

* data warehouses;
* lakehouses;
* search indexes;
* caches;
* ML feature stores;
* audit logs;
* event streams;
* reverse ETL systems;
* downstream services;
* operational data stores;
* real-time dashboards.

It is one of the central bridges between operational systems and analytical systems.

But CDC has a dangerous charm.

It makes change look like a clean stream of events.

Insert.
Update.
Delete.
Insert.
Update.
Delete.

Very neat.

Very modern.

Very conference-slide friendly.

The reality is less polite.

CDC is not just "data updates, but streaming."

CDC is a timeline.

And timelines have rules.

If you ignore ordering, you can produce data that is technically processed, fully automated, beautifully orchestrated, and completely wrong.

Example:

```text
1. Customer is created.
2. Customer changes email.
3. Customer is deleted.
```

If your downstream system receives those events as:

```text
1. Customer is deleted.
2. Customer is created.
3. Customer changes email.
```

you have not replicated the source.

You have written a small piece of fiction.

CDC is powerful because it captures change.

CDC is dangerous because change only makes sense in order.

This post is about why CDC matters, where ordering goes wrong, and how to design pipelines that respect time enough to avoid turning operational history into abstract art.

---

## 1. What Is Change Data Capture?

Change Data Capture is a pattern for identifying and propagating changes from a source system.

Instead of periodically extracting full tables, CDC captures row-level changes.

The source system may produce changes like:

* insert;
* update;
* delete.

A CDC event might look conceptually like this:

```json
{
  "operation": "update",
  "table": "customers",
  "primary_key": {
    "customer_id": "C123"
  },
  "before": {
    "email": "old@example.com",
    "status": "trial"
  },
  "after": {
    "email": "new@example.com",
    "status": "active"
  },
  "source_timestamp": "2026-11-15T08:42:17Z",
  "log_position": "0000002A/00000F10"
}
```

The event says:

> At this point in the source database log, customer `C123` changed from this previous state to this new state.

CDC can be implemented in different ways:

* database transaction logs;
* write-ahead logs;
* binary logs;
* triggers;
* timestamp-based polling;
* version columns;
* event outbox tables;
* application-level events;
* managed replication tools.

The best CDC systems preserve the source database's transaction order.

The weaker CDC systems approximate change by polling or comparing timestamps.

That difference matters.

A lot.

CDC is not one technology.

It is a family of patterns.

Some are robust.

Some are fragile.

Some are robust until you scale them, parallelize them, retry them, or let three teams consume them differently.

As usual, the architecture is in the details.

---

## 2. Why CDC Is So Useful

CDC is popular because it solves real problems.

### Freshness

Instead of waiting for a daily batch, downstream systems can receive changes quickly.

Example:

```text
Operational database
    ↓ CDC
Streaming platform
    ↓
Warehouse/lakehouse table updated every few minutes
```

This supports fresher dashboards, monitoring, and operational analytics.

### Efficiency

Instead of copying entire tables repeatedly, CDC moves only changes.

That can reduce load on source systems.

### Auditability

CDC can preserve a history of changes.

Useful for:

* debugging;
* compliance;
* investigation;
* slowly changing dimensions;
* historical reconstruction;
* data lineage.

### Synchronization

CDC can keep downstream systems aligned with operational systems.

Examples:

* customer profile index;
* search engine;
* cache;
* CRM mirror;
* analytics warehouse;
* feature store.

### Event-driven architectures

CDC can turn database changes into events consumed by other services.

Example:

```text
orders table change
    ↓
OrderUpdated event
    ↓
inventory service
    ↓
warehouse analytics
    ↓
customer notification workflow
```

CDC is especially attractive because it connects existing operational systems to modern data platforms without requiring every application to be rewritten as event-native.

It is practical.

And practical things become popular.

Then they become overused.

Then we discover the edge cases.

Welcome to engineering.

---

## 3. CDC Is Not the Same as Business Events

A CDC event is usually a **data change event**.

A business event is a **domain event**.

They are related, but not identical.

CDC event:

> Row in `orders` table changed.

Business event:

> Customer completed checkout.

CDC event:

> `status` column changed from `pending` to `paid`.

Business event:

> Payment was captured.

CDC event:

> Row deleted from `customers`.

Business event:

> Customer requested account deletion.

This distinction matters.

CDC reflects database mutations.

It may not explain business intent.

Example:

```json
{
  "operation": "update",
  "table": "orders",
  "before": {
    "status": "pending"
  },
  "after": {
    "status": "paid"
  }
}
```

This may mean:

* payment succeeded;
* manual correction;
* replayed transaction;
* migration script;
* source-system repair;
* delayed status synchronization.

The row changed.

But why?

CDC may not know.

This is why CDC is excellent for replication and analytical reconstruction, but not always sufficient for domain behavior.

If downstream systems need business meaning, you may need:

* domain events;
* event outbox pattern;
* semantic transformation layer;
* enrichment;
* explicit event types;
* source metadata;
* business process context.

CDC gives you "what changed."

It does not always give you "what happened."

Sometimes that is enough.

Sometimes it is not.

A database row is not a novel.

It has plot holes.

---

## 4. The Central Problem: Ordering

CDC events are meaningful because of their order.

For a given entity, the sequence matters.

Example:

```text
Event 1:
    customer_id = C123
    status: trial -> active

Event 2:
    customer_id = C123
    status: active -> cancelled
```

Final state:

```text
status = cancelled
```

If processed in reverse:

```text
Event 2:
    status = cancelled

Event 1:
    status = active
```

Final state becomes:

```text
status = active
```

Wrong.

Same events.

Wrong order.

Different result.

This is why ordering is not a minor implementation detail.

Ordering determines truth.

In CDC, there are several kinds of order:

* order within one row/entity;
* order within one table;
* order across tables;
* order within one transaction;
* order across transactions;
* order as seen by the source database;
* order as consumed by downstream systems;
* order after retries and parallel processing.

These are not always the same.

A CDC pipeline must know which ordering guarantees it needs.

Otherwise, it may accidentally preserve the wrong timeline.

And a wrong timeline is how you get zombie customers, negative inventories, duplicated revenue, and dashboards that appear to have been curated by a time traveler with poor documentation.

---

## 5. A Simple Ordering Failure

Suppose a source database has an `orders` table.

Initial state:

```text
order_id = O100
status = pending
amount = 100
```

Then two updates happen:

```text
T1:
    status = paid

T2:
    status = refunded
```

Correct final state:

```text
status = refunded
```

CDC events:

```json
{
  "order_id": "O100",
  "operation": "update",
  "after": {
    "status": "paid"
  },
  "sequence": 101
}
```

```json
{
  "order_id": "O100",
  "operation": "update",
  "after": {
    "status": "refunded"
  },
  "sequence": 102
}
```

If the consumer applies sequence `102` first, then `101`, the final state becomes `paid`.

That is incorrect.

A downstream table might show:

```text
order_id = O100
status = paid
amount = 100
```

Finance may count the order as revenue.

Customer support may see the wrong status.

ML features may treat the customer as paid.

Reverse ETL may sync the wrong lifecycle stage.

All because two events were processed in the wrong order.

The pipeline did not "fail."

It succeeded incorrectly.

This is the most annoying species of success.

---

## 6. Why Events Arrive Out of Order

Events may arrive out of order for many reasons.

### Parallelism

To increase throughput, systems process events in parallel.

Parallel processing can reorder events unless controlled.

### Partitioning

Streams such as Kafka preserve order within a partition, not globally across all partitions.

If related events go to different partitions, ordering can break.

### Retries

A failed event may be retried later, after newer events have already processed.

### Network delays

Distributed systems do not guarantee equal travel time for every message.

Packets are small drama artists.

### Multiple source connectors

Different tables or shards may be captured by different tasks.

Their outputs may not align perfectly.

### Batch flush behavior

Connectors may buffer events and flush them in chunks.

Different chunks may arrive at different times.

### Snapshot plus streaming transition

CDC systems often begin with an initial snapshot, then switch to log streaming.

The transition can introduce duplicates or ordering complexity.

### Rebalancing

Stream processors may rebalance partitions across workers.

In-flight events may be retried or delayed.

### Sink latency

Writes to the destination may complete out of order if parallelized.

The source may produce changes correctly.

The pipeline may still apply them incorrectly.

That is the key point.

Ordering must be preserved end-to-end where correctness depends on it.

Not just captured at the source.

A timestamp on the event is not enough if nobody uses it correctly.

That is like putting a seatbelt in the car and never wearing it.

Very decorative safety.

---

## 7. Ordering Scope: Global Order Is Often Too Expensive

Not all CDC pipelines need global ordering.

Global ordering means every event across every table and entity is processed in exact source order.

This is hard and often unnecessary.

Many systems only need **per-key ordering**.

Example:

For a `customers` table, all events for the same `customer_id` must be ordered.

But events for different customers can be processed independently.

This is much more scalable.

Example:

```text
customer_id = C1:
    event 1 -> event 2 -> event 3

customer_id = C2:
    event 1 -> event 2

C1 and C2 can process in parallel.
But C1's own events must stay ordered.
```

In Kafka-like systems, this often means partitioning by the entity key.

Example:

```text
Kafka topic: customers_cdc
Partition key: customer_id
```

Then all events for the same customer go to the same partition, preserving per-customer order.

That is usually what you want for entity state.

But be careful.

If you partition by the wrong key, you may lose ordering where it matters.

Example:

```text
Partition by random UUID:
    bad for per-customer ordering

Partition by event type:
    bad if one customer has events across types

Partition by customer_id:
    good for customer state

Partition by order_id:
    good for order state
```

The partition key is not just a scaling choice.

It is a correctness choice.

Pick it like you mean it.

---

## 8. Cross-Table Ordering Is Harder

Per-row ordering is one thing.

Cross-table ordering is harder.

Suppose a database transaction inserts an order and an order item:

```text
Transaction T100:
    INSERT INTO orders(order_id = O1)
    INSERT INTO order_items(order_id = O1, item_id = I1)
```

Downstream needs both tables.

If `order_items` arrives before `orders`, a referential check may fail.

Or a transformation may miss the item because the parent order is not visible yet.

Example CDC stream:

```text
1. order_items insert
2. orders insert
```

But in the source transaction, these are part of the same commit.

Depending on the CDC tool, events may include transaction metadata:

```json
{
  "transaction_id": "T100",
  "operation": "insert",
  "table": "orders",
  "sequence_in_transaction": 1
}
```

```json
{
  "transaction_id": "T100",
  "operation": "insert",
  "table": "order_items",
  "sequence_in_transaction": 2
}
```

If consumers need transaction-level consistency, they must use this metadata or process commits carefully.

Many analytical pipelines tolerate short temporary inconsistencies.

For example:

> The order item arrives one second before the order. The next batch fixes it.

That may be acceptable.

But for operational sync, search indexes, or strict integrity pipelines, it may not be.

Ask:

* Do consumers require cross-table consistency?
* Is temporary inconsistency acceptable?
* Are transformations run after all related changes arrive?
* Are transactions represented in the CDC stream?
* Are tables consumed independently or as a coordinated unit?
* Should the sink apply transaction boundaries atomically?

CDC across multiple tables is not just many single-table CDC streams.

Relationships matter.

The database knew those relationships.

Your downstream system may not.

You must decide whether to teach it.

---

## 9. Snapshot Plus CDC: The First Trap

Many CDC pipelines begin with an initial snapshot.

The pipeline copies the current table state, then starts streaming changes.

Conceptually:

```text
Step 1:
    snapshot existing rows

Step 2:
    stream changes from transaction log

Step 3:
    keep target updated
```

This is common and useful.

But the boundary between snapshot and stream is dangerous.

Suppose snapshot starts at 10:00.

A row changes at 10:01.

Snapshot reads the old version at 10:02.

CDC stream also sends the update.

Depending on ordering, the target may end with old or new state.

A robust CDC system records a log position for the snapshot.

Example:

```text
Start snapshot at log position L100.
Read table snapshot consistent as of L100.
Then stream changes after L100.
```

This ensures the snapshot and stream are coordinated.

But not every homegrown CDC pipeline does this correctly.

Bad snapshot pattern:

```text
1. SELECT * FROM source_table
2. Start polling for changes by updated_at
```

Problems:

* updates during snapshot may be missed;
* updates may be duplicated;
* deletes may be missed;
* ordering may be ambiguous;
* rows may be read in inconsistent states.

Snapshot-to-stream handoff is one of the classic CDC danger zones.

If you get the beginning wrong, the target starts with a lie.

Then the pipeline spends its life maintaining that lie very efficiently.

---

## 10. Deletes Are Not Optional

CDC must handle deletes deliberately.

Deletes are often represented as:

* delete events;
* tombstone records;
* soft delete flags;
* operation codes;
* before-image only events;
* null payloads;
* separate deletion logs.

Example delete event:

```json
{
  "operation": "delete",
  "table": "customers",
  "primary_key": {
    "customer_id": "C123"
  },
  "before": {
    "customer_id": "C123",
    "email": "a@example.com",
    "status": "active"
  },
  "after": null,
  "sequence": 500
}
```

If downstream ignores deletes, deleted records remain alive.

This may be okay for audit history.

It is not okay for current-state tables.

CDC sinks often maintain at least two kinds of tables:

### Current-state table

One row per entity, reflecting the latest known state.

Deletes remove or mark the row as deleted.

```text
customers_current
    one row per customer
```

### History table

One row per change event or validity interval.

Deletes are preserved as events or end dates.

```text
customers_history
    one row per change/version
```

Do not confuse these.

A history table should remember deletes.

A current table should reflect them.

If you build only append-only history and call it current state, consumers will eventually count ghosts.

Ghost customers are bad for metrics.

Also for horror films, but that is outside today's scope.

---

## 11. Operation Types Matter

CDC events usually carry operation types.

Common operation codes:

```text
c = create / insert
u = update
d = delete
r = read / snapshot
```

Or:

```text
INSERT
UPDATE
DELETE
SNAPSHOT
```

The operation type determines how the sink should behave.

Example sink logic:

```text
insert:
    create row if missing

update:
    update row if event is newer than current row

delete:
    delete row or mark as deleted

snapshot/read:
    insert initial state, but do not overwrite newer streamed changes
```

That last line is important.

Snapshot events may arrive near streaming events.

If a snapshot event is older than a streamed update, it should not overwrite the update.

Therefore, event ordering or sequence comparison is necessary.

Bad sink logic:

```sql
MERGE INTO customers_current AS target
USING cdc_events AS source
ON target.customer_id = source.customer_id
WHEN MATCHED THEN UPDATE SET *
WHEN NOT MATCHED THEN INSERT *;
```

This may apply older events over newer ones.

Better sink logic uses source ordering metadata:

```sql
MERGE INTO customers_current AS target
USING cdc_events AS source
ON target.customer_id = source.customer_id
WHEN MATCHED
  AND source.sequence_number > target.sequence_number
  THEN UPDATE SET *
WHEN NOT MATCHED
  THEN INSERT *;
```

The exact SQL depends on your platform.

The principle is stable:

> Do not let older events overwrite newer state.

This is the CDC version of "respect your elders," except backwards.

Respect the newest valid event.

The elders can stay in history.

---

## 12. Idempotency Is Not Optional

CDC pipelines must be idempotent.

An idempotent pipeline can process the same event more than once without changing the final result incorrectly.

Why?

Because CDC systems may produce duplicates due to:

* retries;
* connector restarts;
* at-least-once delivery;
* reprocessing;
* checkpoint recovery;
* snapshot overlap;
* sink write failures;
* stream replay.

If the same update arrives twice, the target should not duplicate rows or double-count metrics.

Bad pattern:

```sql
INSERT INTO order_events_history
SELECT *
FROM incoming_cdc_events;
```

This may be fine for raw event logs if duplicates are expected and later deduplicated.

But if the target assumes uniqueness, duplicates are bad.

Better pattern:

* assign event IDs;
* use log position;
* use transaction ID + sequence;
* deduplicate by source event identity;
* apply events only if newer than target state;
* make writes transactional where possible.

Example event identity:

```text
event_id = source_database + table + transaction_id + sequence_in_transaction
```

Or:

```text
event_id = source_log_file + source_log_position + row_sequence
```

For history tables, deduplicate events.

For current-state tables, compare sequence numbers.

Idempotency is what lets you retry without fear.

Without idempotency, every retry is a small gamble.

And distributed systems love giving you reasons to retry.

They are generous like that.

---

## 13. Event Time, Processing Time, and Commit Time

CDC pipelines involve multiple notions of time.

### Event time

When the business event happened.

Example:

```text
order_created_at = 2026-11-15 09:00:00
```

### Source update time

When the row was updated in the source table.

Example:

```text
updated_at = 2026-11-15 09:01:00
```

### Commit time

When the database transaction committed.

Example:

```text
commit_timestamp = 2026-11-15 09:01:05
```

### Capture time

When the CDC connector captured the change.

Example:

```text
captured_at = 2026-11-15 09:01:07
```

### Processing time

When the downstream pipeline processed it.

Example:

```text
processed_at = 2026-11-15 09:01:12
```

These are different.

Using the wrong one can break logic.

For ordering CDC changes, commit/log position is usually more reliable than business event time.

For business metrics, event time may matter more.

For freshness monitoring, capture or processing time may matter.

Example:

A customer places an order offline at 08:00.
The device syncs at 10:00.
The database commits at 10:01.
CDC captures at 10:02.
The warehouse processes at 10:05.

Which date should revenue use?

Probably event time or order time.

Which order should CDC apply updates?

Probably commit/log order.

Which latency should platform monitoring use?

Probably capture/processing delay.

Time fields have jobs.

Do not make one timestamp do all of them.

That is how time gets unionized.

---

## 14. The Updated-At Trap

Some teams implement "CDC" using `updated_at`.

Example:

```sql
SELECT *
FROM source.orders
WHERE updated_at > :last_watermark;
```

This is not log-based CDC.

It is timestamp-based incremental extraction.

It can be useful.

But it has risks:

* clock skew;
* missing deletes;
* updates with unchanged timestamp;
* multiple updates with same timestamp;
* late commits;
* transaction isolation issues;
* timezone problems;
* low timestamp precision;
* out-of-order writes;
* manual corrections;
* backdated timestamps.

Example failure:

```text
last_watermark = 10:00:00

Row A updated at 10:00:00.500
Row B updated at 10:00:00.700

If timestamp precision is seconds:
    both appear as 10:00:00

Next query:
    WHERE updated_at > 10:00:00

Rows may be missed depending on watermark handling.
```

Safer pattern:

* use `>=` with overlap;
* deduplicate by primary key and latest timestamp;
* include secondary ordering key;
* maintain high-watermark carefully;
* process lookback windows;
* handle deletes separately.

Example:

```sql
SELECT *
FROM source.orders
WHERE updated_at >= :last_watermark - INTERVAL '5 minutes';
```

Then downstream deduplicates.

Timestamp incremental extraction is not evil.

But do not confuse it with database-log CDC.

It has weaker guarantees.

Call it what it is.

Names matter because guarantees matter.

A pipeline named `cdc_orders` that cannot capture deletes is not CDC.

It is "updated rows wearing sunglasses."

---

## 15. Ordering in Kafka-Like Systems

Kafka and similar systems preserve ordering within a partition.

Not across all partitions.

This is crucial.

Example:

```text
Topic: orders_cdc

Partition 0:
    O1 event 1
    O1 event 2

Partition 1:
    O2 event 1
    O2 event 2
```

Within partition 0, order is preserved.

Within partition 1, order is preserved.

Across partitions, there is no single global order.

If all events for `order_id = O1` go to partition 0, per-order ordering is safe.

That requires keying by `order_id`.

Example:

```text
message key = order_id
```

If instead messages are keyed randomly, events for the same order may go to different partitions.

Then ordering can break.

Important rule:

> Choose the partition key according to the state you need to preserve.

If building current state by `customer_id`, key by `customer_id`.

If building order state by `order_id`, key by `order_id`.

If joining related tables, the problem becomes harder.

For example, `orders` keyed by `order_id` and `customers` keyed by `customer_id` may not align.

That is normal.

It means cross-entity consistency requires additional design.

Kafka gives you partition ordering.

It does not give you a universal timeline fairy.

Those are expensive.

And usually fictional.

---

## 16. The Sink Can Break Ordering Too

Even if the stream preserves order, the sink may break it.

Suppose events arrive correctly:

```text
sequence 101: status = paid
sequence 102: status = refunded
```

The sink writes them in parallel.

If write for `102` completes first, then write for `101` completes second, final state may become `paid`.

The consumer received events correctly.

The sink applied them incorrectly.

This is common when:

* sink writes are asynchronous;
* upserts are parallelized;
* batches overlap;
* multiple workers write same keys;
* retries occur out of order;
* merge jobs run concurrently;
* target table lacks sequence checks.

Correct sink logic should guard against stale writes.

Example current-state table includes:

```text
order_id
status
amount
source_sequence
source_commit_timestamp
```

Then an update applies only if the event is newer.

Conceptual SQL:

```sql
MERGE INTO orders_current AS target
USING orders_cdc_batch AS source
ON target.order_id = source.order_id
WHEN MATCHED
  AND source.source_sequence > target.source_sequence
  THEN UPDATE SET
      status = source.status,
      amount = source.amount,
      source_sequence = source.source_sequence
WHEN NOT MATCHED
  THEN INSERT (
      order_id,
      status,
      amount,
      source_sequence
  )
  VALUES (
      source.order_id,
      source.status,
      source.amount,
      source.source_sequence
  );
```

This protects against old events overwriting new state.

The sink must be order-aware.

Otherwise, the stream can behave perfectly and the table can still lie.

That is rude, but common.

---

## 17. Current-State Tables vs History Tables

CDC commonly produces two useful table types.

### Current-state table

Represents the latest known state of each entity.

Example:

```text
customers_current
- customer_id
- email
- status
- updated_at
- source_sequence
- is_deleted
```

One row per customer.

Useful for:

* current dashboards;
* operational lookup;
* dimensional modeling;
* reverse ETL;
* serving current profiles.

### Change history table

Stores every change event.

Example:

```text
customers_cdc_history
- event_id
- customer_id
- operation
- before_payload
- after_payload
- source_sequence
- commit_timestamp
- processed_at
```

One row per change event.

Useful for:

* audit;
* debugging;
* reconstructing history;
* SCD tables;
* replay;
* compliance.

Both are valuable.

But they have different correctness rules.

History table:

* append events;
* deduplicate event IDs;
* preserve order metadata;
* do not collapse changes prematurely.

Current table:

* apply latest event per key;
* handle deletes;
* reject stale updates;
* maintain one current row.

Do not build current-state logic by simply selecting the latest `updated_at` unless you trust the timestamp.

Better to use log position or source sequence when available.

The latest timestamp is not always the latest change.

Time, again, is sneaky.

---

## 18. Building Slowly Changing Dimensions From CDC

CDC is excellent for building slowly changing dimensions.

A Type 2 slowly changing dimension preserves historical versions of an entity.

Example:

```text
customer_id = C123

Version 1:
    status = trial
    valid_from = 2026-01-01
    valid_to = 2026-03-10

Version 2:
    status = active
    valid_from = 2026-03-10
    valid_to = 2026-09-02

Version 3:
    status = cancelled
    valid_from = 2026-09-02
    valid_to = null
```

CDC provides the changes needed to create these intervals.

But ordering is essential.

If updates arrive out of order, validity intervals may become wrong.

Example:

```text
Correct order:
    trial -> active -> cancelled

Wrong order:
    trial -> cancelled -> active
```

Now historical joins produce wrong states.

Point-in-time analysis breaks.

ML features may leak or misrepresent history.

A robust SCD builder needs:

* primary key;
* event sequence;
* commit timestamp;
* deduplication;
* ordering by source sequence;
* handling of deletes;
* correction strategy for late/out-of-order events;
* validation for overlapping intervals.

Validation example:

```sql
SELECT
    customer_id,
    COUNT(*) AS n_overlaps
FROM dim_customer_history
WHERE valid_to > LEAD(valid_from) OVER (
    PARTITION BY customer_id
    ORDER BY valid_from
)
GROUP BY customer_id;
```

Exact syntax depends on platform, but the principle matters:

> History tables need temporal integrity checks.

A history table with overlapping or inverted intervals is not history.

It is a chronology accident.

---

## 19. CDC and Deletes in SCD Tables

Deletes in SCD logic require a decision.

If a customer is deleted, do you:

* remove the customer from current state?
* mark `is_deleted = true`;
* close the current validity interval;
* keep a tombstone row;
* preserve full history;
* anonymize sensitive fields;
* propagate deletion downstream?

Example SCD delete handling:

```text
Before delete:
    customer_id = C123
    status = active
    valid_from = 2026-03-10
    valid_to = null
    is_deleted = false

After delete:
    customer_id = C123
    status = active
    valid_from = 2026-03-10
    valid_to = 2026-11-15
    is_deleted = true
```

But governance may require more.

For privacy or legal deletion, you may need to remove or mask personal fields while preserving aggregate or audit-safe records.

This is domain-specific.

CDC gives you the delete signal.

It does not tell you the policy.

Data engineering must meet governance here.

Especially in healthcare, finance, and other regulated domains.

A delete event is both a technical operation and sometimes a legal instruction.

Treat it with respect.

---

## 20. CDC and Exactly-Once Semantics

People love saying "exactly once."

It sounds comforting.

In distributed systems, exactly-once semantics are subtle.

Many pipelines are actually:

* at-least-once delivery plus idempotent writes;
* exactly-once within a processing framework but not end-to-end;
* effectively-once at the final table;
* exactly-once under specific assumptions that nobody reads.

For CDC, the practical target is often:

> The final target state is correct even if events are retried, duplicated, or replayed.

That is **effectively-once** behavior.

You get it through:

* stable event IDs;
* idempotent sink writes;
* sequence checks;
* transactional commits;
* checkpointing;
* deduplication;
* deterministic transformations.

Example:

```text
Event delivered twice:
    event_id = E123

History sink:
    stores E123 once

Current-state sink:
    applies E123 once or applies twice with same final state
```

This is what matters.

Do not rely only on marketing phrases.

Ask:

* What happens if the connector restarts?
* What happens if the sink write succeeds but checkpoint fails?
* What happens if an event is replayed?
* What happens if a batch is partially written?
* What happens if a newer event is applied before an older event?
* What is the event identity?
* What is the ordering field?

Exactly-once is not a spell.

It is an end-to-end design property.

Spells are easier.

Less reliable.

---

## 21. CDC and Checkpointing

CDC pipelines need checkpoints.

A checkpoint records how far the pipeline has processed.

Examples:

* source log position;
* Kafka offset;
* transaction ID;
* LSN;
* binlog file and position;
* commit timestamp plus tie-breaker;
* batch ID;
* stream processing checkpoint.

Checkpointing enables recovery.

If the process crashes, it resumes from the checkpoint.

But checkpointing must align with sink commits.

Dangerous sequence:

```text
1. Read events 100-200.
2. Write events 100-200 to target.
3. Fail before checkpoint update.
4. Restart from event 100.
5. Reprocess events 100-200.
```

This creates duplicates unless the sink is idempotent.

Opposite dangerous sequence:

```text
1. Read events 100-200.
2. Update checkpoint to 200.
3. Fail before writing target.
4. Restart from 201.
5. Events 100-200 are lost.
```

This is worse.

A robust pipeline coordinates checkpoint and sink write.

Often through transactional processing or idempotent writes.

The practical rule:

> Assume events may be replayed. Design the sink so replay is safe.

Checkpointing reduces repeated work.

Idempotency protects correctness.

They are friends.

Not substitutes.

---

## 22. CDC and Watermarks

Watermarks are often used in streaming to reason about event completeness.

But in CDC, be careful.

Watermarks can mean different things:

* source log position processed;
* event time completeness;
* ingestion time progress;
* commit timestamp progress;
* Kafka offset progress;
* table partition completeness.

For current-state replication, source log position may be more important.

For analytical event-time windows, event time watermarks may matter.

Example:

```text
CDC log position watermark:
    processed all database changes through LSN 5000

Event-time watermark:
    processed all events with event_time before 10:00, allowing 10 minutes lateness
```

These are not the same.

A CDC event may contain an order from yesterday committed today.

For business metrics, it belongs yesterday.

For CDC ordering, it is processed today in commit order.

Do not confuse event-time completeness with CDC log completeness.

A pipeline can be caught up to the source log and still produce changes for old business dates.

That is normal.

This is why CDC-fed analytical tables often need partition update strategies that handle historical dates.

The stream is current.

The business event may be old.

Reality loves this trick.

---

## 23. CDC and Late-Arriving Business Events

CDC captures database changes when they occur.

But the business event represented by the row may have happened earlier.

Example:

```text
event_time: 2026-11-10
database_commit_time: 2026-11-15
cdc_processed_at: 2026-11-15
```

This happens with:

* offline systems;
* mobile sync;
* vendor uploads;
* delayed billing;
* claims adjudication;
* clinical data entry;
* lab result updates;
* manual corrections;
* backdated records.

If downstream partitions by event date, a CDC update today may modify a partition from five days ago.

Example:

```text
CDC arrives on 2026-11-15.
Record belongs to event_date = 2026-11-10.
Target partition to update:
    event_date = 2026-11-10
```

This affects:

* partition overwrite;
* incremental models;
* dashboard freshness;
* backfill windows;
* late-data correction logic;
* data quality expectations.

A CDC pipeline should identify affected business dates.

Example:

```sql
SELECT DISTINCT
    event_date
FROM incoming_cdc_events;
```

Then downstream transformations can update affected partitions.

CDC freshness does not mean only today's partition changes.

Fresh changes can rewrite old history.

The past is surprisingly active.

---

## 24. CDC and Compaction

CDC streams can generate many small changes.

When written to object storage or lakehouse tables, this may create many small files.

Example:

```text
Every minute:
    500 updates
    written as small files

After one day:
    thousands of small files
```

Small files hurt:

* query planning;
* metadata size;
* object-store operations;
* compaction cost;
* table maintenance;
* downstream performance.

CDC pipelines often need compaction.

Patterns:

* micro-batch changes into larger files;
* compact target partitions periodically;
* write to staging then merge in batches;
* separate raw CDC log from curated current-state table;
* optimize hot partitions frequently;
* optimize cold partitions less often.

Example architecture:

```text
CDC stream
    ↓
raw CDC append table
    ↓
micro-batch merge
    ↓
current-state table
    ↓
periodic compaction
```

Compaction is not optional at scale.

CDC can make data fresh and physically messy.

A platform must manage both freshness and layout.

Otherwise, your lakehouse becomes a confetti archive.

Festive, but slow.

---

## 25. CDC and Merge Cost

Maintaining current-state tables often requires `MERGE`.

Merges can be expensive.

Especially on large tables with frequent updates.

Cost depends on:

* table size;
* partitioning;
* clustering;
* file sizes;
* update distribution;
* number of changed keys;
* merge predicate;
* table format;
* compute engine;
* frequency of merges.

Bad pattern:

```sql
MERGE INTO huge_customer_table
USING tiny_cdc_batch
ON huge_customer_table.customer_id = tiny_cdc_batch.customer_id
```

If the engine scans too much of the target table, each merge is expensive.

Better design may include:

* partitioning by update date or domain-specific key;
* clustering by primary key;
* batching changes;
* maintaining current table in a database/warehouse optimized for upserts;
* using table formats with efficient merge support;
* separating hot and cold data;
* using stateful stream processing;
* applying changes to a key-value serving store;
* periodically rebuilding current-state tables from compacted history.

CDC is not free just because events are small.

A tiny update can cause a large merge.

This is one of the cruel jokes of lakehouse CDC.

The event is small.

The table is not.

---

## 26. CDC and Data Quality

CDC pipelines need data quality checks too.

Quality checks for CDC include:

### Event-level checks

* valid operation type;
* non-null primary key;
* valid sequence/log position;
* valid before/after payload;
* known table name;
* schema version compatibility.

### Ordering checks

* sequence increases per key;
* no stale events applied to current table;
* no gaps in source log if required;
* no unexpected partition reordering.

### Current-state checks

* one row per primary key;
* no duplicate active records;
* delete handling correct;
* target row sequence equals latest source sequence.

### History checks

* event ID uniqueness;
* no duplicate event records;
* SCD intervals do not overlap;
* valid_from before valid_to.

### Freshness checks

* connector lag;
* processing lag;
* sink update lag;
* source log delay.

Example check:

```sql
SELECT
    order_id,
    COUNT(*) AS n_current_rows
FROM orders_current
WHERE is_deleted = false
GROUP BY order_id
HAVING COUNT(*) > 1;
```

Example stale update detection:

```sql
SELECT
    event_id,
    order_id,
    source_sequence,
    target_sequence
FROM rejected_cdc_events
WHERE rejection_reason = 'stale_sequence';
```

CDC quality is not only "did records arrive?"

It is "did changes arrive, in a valid order, and produce correct state?"

That is a stronger question.

Ask it.

---

## 27. CDC and Observability

CDC needs observability across the full path.

Track:

* source log lag;
* connector status;
* events per second;
* bytes per second;
* error rate;
* retry rate;
* duplicate rate;
* out-of-order event count;
* stale event rejection count;
* sink write latency;
* merge duration;
* checkpoint age;
* dead-letter queue size;
* schema change events;
* delete event counts;
* target freshness;
* table compaction health;
* current-state row counts.

A useful CDC dashboard might show:

```text
CDC pipeline: orders

Source:
    log lag: 12 seconds
    connector status: running
    events/sec: 1,240

Stream:
    consumer lag: 4,000 messages
    duplicate events: 12
    out-of-order rejected: 3

Sink:
    last successful merge: 2026-11-15 07:58
    merge duration: 42 seconds
    current table freshness: 2 minutes
    dead-letter queue: 0

Quality:
    duplicate current keys: 0
    invalid operation types: 0
    stale updates rejected: 3
```

This tells a story.

Without observability, CDC failures are hard to debug.

A batch pipeline fails loudly.

A CDC pipeline may drift quietly.

CDC is a continuous system.

Continuous systems need continuous visibility.

The stream is alive.

Please check its pulse.

---

## 28. CDC and Dead-Letter Queues

Some CDC events cannot be processed safely.

Reasons:

* schema mismatch;
* missing primary key;
* unknown operation type;
* invalid payload;
* deserialization failure;
* target constraint violation;
* incompatible enum value;
* unexpected null;
* stale sequence;
* delete for missing key;
* malformed source event.

A dead-letter queue, or DLQ, stores failed events for investigation.

Example DLQ record:

```json
{
  "event_id": "E123",
  "table": "orders",
  "primary_key": "O100",
  "reason": "missing_primary_key",
  "raw_payload": {
    "operation": "update",
    "after": {
      "status": "paid"
    }
  },
  "failed_at": "2026-11-15T08:10:00Z"
}
```

DLQs are useful only if someone monitors them.

An unmonitored DLQ is just a trash can with retention.

Good DLQ practice:

* alert on growth;
* classify errors;
* support replay after fix;
* preserve raw payload;
* include failure reason;
* track owner;
* define retention;
* document handling.

DLQs are not failure avoidance.

They are failure containment.

The pipeline says:

> "I cannot safely process this event, so I will isolate it instead of poisoning the target."

That is maturity.

Very adult.

Almost suspicious.

---

## 29. CDC and Schema Evolution

CDC streams are sensitive to schema evolution.

Source schemas change.

CDC payloads change.

Consumers must handle it.

Examples:

* column added;
* column removed;
* type changed;
* nullable changed;
* enum value added;
* nested payload changed;
* before-image configuration changed;
* delete payload format changed;
* primary key changed.

A schema change can break CDC consumers.

Example:

```text
Before:
    customer_id

After:
    account_id
```

If the stream key still expects `customer_id`, ordering and upserts may break.

Schema evolution in CDC requires:

* schema registry or contract;
* compatibility checks;
* versioned payloads;
* migration windows;
* consumer updates;
* source connector configuration review;
* sink schema handling;
* backfill or replay plan.

Primary-key changes are especially dangerous.

If the key changes, partitioning, ordering, deduplication, and merge logic may all change.

That is not a small schema change.

That is a bloodstream change.

Treat it carefully.

---

## 30. CDC and Replays

A major benefit of CDC history is replay.

If you store the raw CDC log, you can rebuild downstream state.

Example:

```text
raw CDC history
    ↓ replay
customers_current
```

Replays are useful for:

* fixing bugs;
* rebuilding targets;
* testing new logic;
* recovering from corruption;
* backfilling new tables;
* migrating systems;
* auditing past behavior.

But replay requires ordering.

If you replay events out of order, you rebuild the wrong state.

A replay process should define:

* source event range;
* ordering key;
* deduplication strategy;
* target write mode;
* starting state;
* delete handling;
* schema version handling;
* validation checks;
* checkpointing;
* replay isolation.

Example replay plan:

```yaml
replay:
  source_table: raw.orders_cdc_history
  target_table: rebuild.orders_current_candidate
  ordering:
    key: source_sequence
    partition_by: order_id
  range:
    start_sequence: 0
    end_sequence: 9823312
  validation:
    - one_current_row_per_order
    - latest_sequence_matches_source
    - status_distribution_compare
  publish:
    mode: swap_after_validation
```

A raw CDC log is only useful if it can be replayed deterministically.

Otherwise, it is a very large diary written in shuffled pages.

Literary, but not operational.

---

## 31. CDC and Backfills

CDC and backfills are closely related.

Sometimes you need to backfill CDC targets.

Reasons:

* target table corrupted;
* schema changed;
* sink logic changed;
* history table added later;
* initial snapshot was wrong;
* old events were dropped;
* compaction or merge bug;
* new downstream data product needs historical changes.

Backfill options:

### Re-snapshot current source

Good for rebuilding current-state table.

Bad for reconstructing history.

### Replay raw CDC history

Good if history was stored and ordered.

### Re-extract from source audit tables

Useful if source has audit logs.

### Recompute from analytical snapshots

Possible if snapshots exist.

### Hybrid snapshot plus CDC replay

Common for rebuilding current state as of now.

CDC backfills need careful boundaries.

Example:

```text
1. Snapshot source table at log position L500.
2. Load snapshot into target.
3. Replay CDC events after L500.
4. Apply sequence-aware merges.
```

This prevents missing changes during the snapshot.

If you simply snapshot and then start CDC "around the same time," you may miss or duplicate changes.

Backfilling CDC is not just "reload the table."

It is rebuilding a timeline.

Timelines are jealous creatures.

They dislike approximation.

---

## 32. CDC and Healthcare/Biotech

CDC is extremely useful in healthcare and biotech platforms.

Potential sources:

* EHR operational databases;
* lab information systems;
* claims processing systems;
* sample tracking systems;
* clinical trial systems;
* registry systems;
* consent management systems;
* hospital administrative systems;
* sequencing workflow metadata stores.

Use cases:

* near-real-time patient cohort updates;
* claims status tracking;
* lab result propagation;
* sample processing visibility;
* audit trails;
* operational dashboards;
* research data marts;
* phenotype refresh;
* consent-aware data access;
* longitudinal patient histories.

But ordering and semantics are critical.

### Example: lab results

A lab result may go through states:

```text
ordered -> collected -> processing -> preliminary -> final -> corrected
```

If `corrected` arrives before `final` downstream, the final state may overwrite the correction.

That is dangerous.

### Example: consent

Consent status changes must be ordered.

```text
consented -> withdrawn
```

If processed in reverse, a patient may appear eligible when they are not.

That is not just a data issue.

That is governance risk.

### Example: claims

Claims may be submitted, denied, adjusted, paid, reversed.

Ordering determines financial state.

### Example: genomics workflow metadata

Sample state may progress:

```text
received -> extracted -> sequenced -> aligned -> variant_called -> released
```

Out-of-order updates may show incorrect pipeline status.

Biomedical CDC systems should track:

* source transaction order;
* event/entity keys;
* operation type;
* source system;
* code system versions;
* correction flags;
* consent constraints;
* audit metadata;
* processed timestamp;
* target state sequence.

In regulated domains, CDC correctness is not only technical.

It is part of trust, compliance, and scientific reproducibility.

A stream that is fast but wrong is not impressive.

It is a liability with low latency.

---

## 33. CDC and Reverse ETL

CDC often feeds Reverse ETL.

Example:

```text
warehouse customer_current
    ↓
Reverse ETL
Salesforce / HubSpot / Braze / Zendesk
```

If CDC ordering is wrong, Reverse ETL may send wrong changes to operational tools.

Example:

Correct order:

```text
customer lifecycle:
    trial -> active -> cancelled
```

Wrongly applied order:

```text
trial -> cancelled -> active
```

Reverse ETL syncs `active` to Salesforce.

Sales team contacts a cancelled customer.

Marketing enrolls them in the wrong campaign.

Support sees wrong account status.

This is not merely an analytical error.

It becomes operational behavior.

Before CDC-fed Reverse ETL, ensure:

* current-state tables are sequence-safe;
* deletes are handled;
* stale events do not overwrite newer state;
* syncs use stable identity keys;
* allowed values are compatible with SaaS fields;
* major replays do not trigger unwanted workflows;
* backfills can pause activation;
* sync logs are auditable.

Reverse ETL turns data changes into business actions.

CDC ordering errors become business action errors.

That is when small stream bugs grow teeth.

---

## 34. Choosing the Right CDC Architecture

A CDC architecture should match the use case.

### Use case: analytical freshness

Goal:

* keep warehouse/lakehouse reasonably fresh.

Architecture:

```text
source database log
    ↓
CDC connector
    ↓
raw CDC topic/table
    ↓
micro-batch merge
    ↓
analytics current/history tables
```

Ordering need:

* per-key ordering;
* sequence-aware merge;
* replayable raw log.

### Use case: operational replication

Goal:

* keep a downstream operational store synchronized.

Architecture:

```text
source database
    ↓
CDC stream
    ↓
stateful processor
    ↓
serving database/search index/cache
```

Ordering need:

* strict per-key ordering;
* idempotent writes;
* low-latency monitoring.

### Use case: audit history

Goal:

* preserve all changes.

Architecture:

```text
source log
    ↓
append-only CDC history
    ↓
queryable audit table
```

Ordering need:

* complete event identity;
* source order metadata;
* immutable append.

### Use case: SCD dimensions

Goal:

* maintain historical versions.

Architecture:

```text
CDC history
    ↓
ordered per entity
    ↓
SCD Type 2 builder
    ↓
dimension history table
```

Ordering need:

* strong per-entity ordering;
* interval validation.

### Use case: event-driven services

Goal:

* trigger domain actions.

Architecture:

```text
application outbox
    ↓
event stream
    ↓
consumers
```

Ordering need:

* domain-specific;
* often per-aggregate ordering;
* business event semantics.

CDC from database logs may not be ideal for domain actions unless transformed carefully.

The architecture should follow the contract.

Not the other way around.

---

## 35. A Small Python Sketch: Rejecting Stale CDC Events

Below is a small teaching sketch showing how one might reason about stale CDC events before applying them to a current-state store.

```python
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class Operation(StrEnum):
    """CDC operation type."""

    INSERT = "insert"
    UPDATE = "update"
    DELETE = "delete"


@dataclass(frozen=True)
class CdcEvent:
    """A simplified CDC event.

    Parameters
    ----------
    entity_id
        Primary key of the changed entity.
    operation
        CDC operation type.
    sequence
        Monotonically increasing source sequence for this entity or log.
    payload
        New state payload for insert/update events.
    """

    entity_id: str
    operation: Operation
    sequence: int
    payload: dict[str, object] | None


@dataclass(frozen=True)
class CurrentState:
    """Current state stored for an entity.

    Parameters
    ----------
    entity_id
        Primary key of the entity.
    sequence
        Latest source sequence applied to this state.
    payload
        Current payload.
    is_deleted
        Whether the entity is currently deleted.
    """

    entity_id: str
    sequence: int
    payload: dict[str, object] | None
    is_deleted: bool = False


def should_apply_event(
    event: CdcEvent,
    current_state: CurrentState | None,
) -> bool:
    """Return whether a CDC event should update current state.

    Parameters
    ----------
    event
        Incoming CDC event.
    current_state
        Existing current state for the entity, if present.

    Returns
    -------
    bool
        ``True`` if the event is newer than the current state.
    """
    if current_state is None:
        return True

    return event.sequence > current_state.sequence


def apply_event(
    event: CdcEvent,
    current_state: CurrentState | None,
) -> CurrentState:
    """Apply a CDC event to current state if it is not stale.

    Parameters
    ----------
    event
        Incoming CDC event.
    current_state
        Existing current state for the entity, if present.

    Returns
    -------
    CurrentState
        Updated or unchanged current state.

    Raises
    ------
    ValueError
        If a stale event is received for a missing current state edge case.
    """
    if not should_apply_event(event, current_state):
        if current_state is None:
            raise ValueError("Unexpected missing current state.")
        return current_state

    if event.operation == Operation.DELETE:
        return CurrentState(
            entity_id=event.entity_id,
            sequence=event.sequence,
            payload=None,
            is_deleted=True,
        )

    return CurrentState(
        entity_id=event.entity_id,
        sequence=event.sequence,
        payload=event.payload,
        is_deleted=False,
    )
```

The code is deliberately simple.

Real systems need more:

* transaction handling;
* duplicate detection;
* schema versions;
* dead-letter queues;
* partition-aware ordering;
* durable checkpoints;
* batch semantics;
* target database transactions;
* observability.

But the principle is crucial:

> Current state should only move forward in source order.

If an old event arrives late, preserve it in history if needed.

Do not let it overwrite the present.

That sentence alone prevents many CDC disasters.

---

## 36. Common Anti-Patterns

### Anti-pattern 1: Treating CDC as just streaming rows

CDC is ordered change, not just a fast table export.

### Anti-pattern 2: Ignoring deletes

Deleted records become zombie rows.

Zombies are bad for metrics and worse for governance.

### Anti-pattern 3: Partitioning by the wrong key

Events for the same entity land in different partitions and process out of order.

### Anti-pattern 4: Blind upserts

Older events overwrite newer state.

### Anti-pattern 5: No event identity

Duplicates cannot be detected.

### Anti-pattern 6: No raw CDC history

You cannot replay or debug properly.

### Anti-pattern 7: Confusing event time with commit order

Business time and source change order are different.

### Anti-pattern 8: Timestamp polling called CDC

`updated_at` extraction has weaker guarantees and often misses deletes.

### Anti-pattern 9: No dead-letter handling

Bad events either poison the target or vanish.

### Anti-pattern 10: No observability

Lag, duplicates, stale events, and ordering problems stay invisible.

### Anti-pattern 11: Applying CDC directly to business actions

Reverse ETL or operational workflows trigger from unvalidated state.

### Anti-pattern 12: No schema evolution plan

Source changes break consumers or corrupt payload interpretation.

These anti-patterns are common because CDC looks simpler than it is.

The stream is easy to start.

Correctness is harder to keep.

---

## 37. What Good Looks Like

A healthy CDC pipeline usually has these traits.

### Clear source ordering metadata

Events include log position, sequence number, commit timestamp, or equivalent.

### Correct partitioning

Events are partitioned by the key whose order must be preserved.

### Idempotent writes

Duplicates and retries do not corrupt output.

### Sequence-aware current-state updates

Older events cannot overwrite newer state.

### Delete handling

Deletes are explicitly represented and applied according to policy.

### Raw history preservation

CDC events are stored in an append-only form for replay and audit.

### Dead-letter strategy

Invalid events are isolated, monitored, and replayable after correction.

### Checkpointing

Progress is durable and aligned with sink safety.

### Schema governance

Schema changes are versioned, validated, and communicated.

### Observability

Lag, ordering issues, duplicates, stale events, and sink health are visible.

### Replay strategy

The system can rebuild targets from stored history or coordinated snapshots.

### Downstream awareness

Dashboards, marts, ML features, and Reverse ETL consumers understand CDC semantics.

In short:

> Good CDC is not merely fast. It is ordered, idempotent, observable, replayable, and semantically understood.

Fast wrong is still wrong.

It just arrives sooner.

---

## 38. A Practical CDC Design Checklist

Before building or approving a CDC pipeline, ask:

1. What source system produces the changes?
2. Is this log-based CDC, trigger-based CDC, polling, or application events?
3. What operation types are captured?
4. Are deletes captured?
5. What is the primary key?
6. What is the ordering field?
7. Is ordering global, per-table, per-transaction, or per-key?
8. What partition key is used in the stream?
9. Can events for the same entity arrive out of order?
10. Can events be duplicated?
11. What is the event identity?
12. How are retries handled?
13. How are checkpoints stored?
14. What happens if sink write succeeds but checkpoint fails?
15. Is the sink idempotent?
16. Can stale events overwrite newer state?
17. Is raw CDC history stored?
18. Can the target be replayed?
19. How is the initial snapshot coordinated with the stream?
20. How are schema changes handled?
21. How are invalid events quarantined?
22. How are deletes represented in current and history tables?
23. What freshness and lag metrics are monitored?
24. What data quality checks protect the target?
25. Which downstream consumers depend on this pipeline?
26. Does Reverse ETL consume the output?
27. Are backfills and replays documented?
28. What is the expected merge cost?
29. How is compaction handled?
30. Who owns the pipeline?

This checklist is not short.

CDC is not small.

It only looks small because each event is small.

A million small events can still create one large incident.

---

## 39. CDC Is a Timeline, Not a Table Dump

The deeper lesson is this:

> CDC is not mainly about moving rows. It is about preserving the meaning of change over time.

Rows have states.

CDC has transitions.

A table dump says:

> Here is what the world looks like now.

CDC says:

> Here is how the world changed.

Those are different forms of truth.

If you only need current state, you may collapse CDC into a current table.

If you need history, you must preserve transitions.

If you need auditability, you must preserve source metadata.

If you need operational sync, you must preserve ordering and idempotency.

If you need analytics, you must map change events into business time and data products.

If you need ML features, you must avoid leakage and preserve point-in-time correctness.

CDC is not automatically analytics-ready.

It is raw change material.

The platform must shape it carefully.

Otherwise, you get a warehouse full of technically correct events and analytically confusing tables.

That is not modernization.

That is a timeline compost heap.

Potentially useful.

Definitely needs processing.

---

## 40. Final Thought

Change Data Capture is powerful.

It can make data platforms fresher, more efficient, more auditable, and more responsive.

It can connect operational systems to analytical systems.

It can support near-real-time dashboards, current-state tables, SCD dimensions, feature stores, audit trails, and downstream synchronization.

But CDC is dangerous when treated casually.

The central danger is ignoring order.

If events are applied out of order, the final state can be wrong.

If deletes are ignored, ghosts remain.

If duplicates are not handled, counts inflate.

If snapshots are not coordinated with streams, changes are missed.

If stale events overwrite newer ones, history attacks the present.

If schema changes are unmanaged, consumers misinterpret payloads.

If Reverse ETL consumes unstable state, data mistakes become business actions.

The mature CDC mindset is:

> Capture every change, preserve its identity and order, apply it idempotently, monitor it continuously, and make downstream semantics explicit.

CDC is not just a connector setting.

It is a distributed data correctness problem.

A good CDC pipeline knows:

* what changed;
* where it changed;
* when it changed in source order;
* what entity it belongs to;
* whether it is newer than current state;
* whether it has been processed before;
* how to handle deletes;
* how to recover after failure;
* how to replay history;
* how to alert when reality gets weird.

That is the difference between a stream of changes and a reliable data product.

CDC gives you the timeline.

Data engineering makes sure the timeline still makes sense.

Because in data platforms, as in life, order matters.

Especially when someone says:

> "It is just an update."

It is never just an update.

It is a tiny historical event with consequences.
