Title: The Sunday Materialization - Shuffle Partitions in Spark
Subtitle: The Small Configuration Knob That Quietly Controls Parallelism, File Counts, Cost, and Pain
Date: 2026-03-15 07:00
Modified: 2026-03-15 07:00
Category: Sunday
Tags: data engineer, data platform engineer, data, data architecture, Apache Spark, PySpark, shuffle, performance tuning, distributed computing
Slug: sunday-materialization-spark-shuffle-partitions
Authors: Eduardo G Gusmao
Summary: A weekly educational topic/lecture/discussion on Data Engineering topics that we all experienced at least once (or will!)
Status: final
Lang: en
Template: topic
Cadence: Biweekly
Scope: Data Engineering, Industry, Data Challenges
Tone: Analytical, Educational, Non-Sensational
Canonical: https://www.gusmaolab.org/blog/sunday-materialization-spark-shuffle-partitions/
Meta_description: Biweekly analysis of important Data Engineering concepts.
Meta_keywords: data concepts, topics, lectures, discussions, Spark, PySpark, shuffle partitions
Cover: images/covers/spark-shuffle-partitions.png
Thumbnail: images/thumbnails/spark-shuffle-partitions-thumb.png

# Shuffle Partitions in Spark: The Knob You Keep Misunderstanding

Spark has many configuration knobs.

Some are obviously scary.

Memory fractions.
Executor cores.
Dynamic allocation.
Broadcast thresholds.
Serializer choices.
Adaptive Query Execution.
Speculative execution.
Garbage collection.
Cluster manager settings.
The kind of knobs that make people say, "Let us ask the senior data engineer," and then the senior data engineer quietly opens six browser tabs.

But one Spark setting looks deceptively simple:

```text
spark.sql.shuffle.partitions
```

It looks like a number.

Just a number.

The default historically appears as `200` in many Spark SQL contexts.

So people learn a ritual:

> "If Spark is slow, change shuffle partitions."

Then they ask:

> "Should I set it to 200, 400, 800, 2000, or something else?"

And because distributed systems enjoy comedy, the answer is:

> It depends.

Not the lazy kind of "it depends."

The real kind.

It depends on:

* data volume;
* shuffle size;
* cluster size;
* executor cores;
* query shape;
* skew;
* file size targets;
* output format;
* downstream table layout;
* Adaptive Query Execution;
* whether the job is CPU-bound or I/O-bound;
* whether the shuffle is large or tiny;
* whether the problem is too few partitions or too many;
* whether the bottleneck is shuffle, write, join, aggregation, or planning.

Shuffle partitions are misunderstood because people treat them as a speed knob.

They are not merely a speed knob.

They are a **parallelism and data distribution knob**.

They affect how Spark splits shuffled data after operations such as joins, aggregations, window operations, distincts, repartitions, and sorts.

Set too low, and tasks become huge.

Set too high, and overhead explodes.

Set randomly, and Spark will still run, because Spark is polite.

But it may run slowly, expensively, and produce thousands of tiny files.

This post is about what shuffle partitions really do, why the setting matters, why changing it blindly is dangerous, and how to reason about it like an engineer rather than a config astrologer.

---

## 1. The Short Version

`spark.sql.shuffle.partitions` controls the number of partitions Spark creates after many wide transformations in Spark SQL/DataFrame operations.

Examples of operations that often trigger shuffle:

* `groupBy`;
* `join`;
* `distinct`;
* `dropDuplicates`;
* `orderBy`;
* `repartition`;
* many window functions;
* aggregations;
* some set operations.

A shuffle means Spark must redistribute data across the cluster.

Conceptually:

```text
Before shuffle:
    each worker has some rows

Shuffle:
    rows are redistributed by key or ordering rule

After shuffle:
    rows are grouped into new output partitions
```

The number of output partitions after the shuffle affects:

* number of downstream tasks;
* task size;
* parallelism;
* scheduler overhead;
* shuffle file count;
* memory pressure;
* spill behavior;
* write parallelism;
* output file count;
* query duration;
* cost.

So the setting is important.

But the correct value is not universal.

The correct value is workload-specific.

A small aggregation may not need 200 partitions.

A massive join may need far more than 200.

A job writing a table may need partitions aligned with target file sizes.

A skewed job may still be slow even if partitions are "correct" on average.

Shuffle partitions are not magic.

They are a lever.

A lever can move a heavy object.

It can also hit you in the chin.

---

## 2. What Is a Spark Partition?

A Spark partition is a chunk of data processed by one task.

If a DataFrame has 100 partitions, Spark can create roughly 100 tasks for a stage.

Each task processes one partition.

Example:

```text
DataFrame:
    100 partitions

Stage:
    100 tasks
```

Partitions are Spark's unit of parallelism.

More partitions can mean more parallelism.

But more partitions also mean more overhead.

Each task has scheduling cost, metadata, execution overhead, and potential shuffle/file overhead.

A useful mental model:

```text
Too few partitions:
    big tasks
    poor parallelism
    high memory pressure
    long straggler tasks

Too many partitions:
    tiny tasks
    scheduling overhead
    many small files
    metadata overhead
    inefficient execution
```

Spark performance tuning often means finding a reasonable middle.

Not too few.

Not too many.

The Goldilocks zone.

Spark is very much a porridge system.

---

## 3. What Is a Shuffle?

A shuffle is a redistribution of data across the cluster.

Spark needs a shuffle when rows must be rearranged based on keys, grouping, ordering, or partitioning.

Example:

```python
from pyspark.sql import functions as F

result = (
    df.groupBy("customer_id")
    .agg(F.sum("amount").alias("total_amount"))
)
```

To compute this correctly, Spark must ensure all rows for the same `customer_id` meet in the same place.

Before shuffle:

```text
Partition 1:
    customer A, customer B

Partition 2:
    customer A, customer C

Partition 3:
    customer B, customer C
```

After shuffle by `customer_id`:

```text
Partition X:
    all rows for customer A

Partition Y:
    all rows for customer B

Partition Z:
    all rows for customer C
```

That redistribution is the shuffle.

Shuffle is expensive because it may involve:

* disk writes;
* network transfer;
* sorting;
* serialization;
* deserialization;
* memory pressure;
* spilling;
* many temporary files;
* coordination across executors.

A narrow transformation, such as `filter`, can usually process each partition independently.

A wide transformation, such as `groupBy`, needs data movement.

Example narrow transformation:

```python
filtered = df.filter(F.col("amount") > 0)
```

Each partition can filter its own rows.

Example wide transformation:

```python
totals = df.groupBy("customer_id").agg(F.sum("amount"))
```

Rows must move by `customer_id`.

Shuffle is where Spark reminds you that distributed computing is not just Pandas with a logo.

---

## 4. Where `spark.sql.shuffle.partitions` Enters

After a shuffle, Spark must decide how many output partitions to create.

For Spark SQL/DataFrame operations, that is often controlled by:

```text
spark.sql.shuffle.partitions
```

Example:

```python
spark.conf.set("spark.sql.shuffle.partitions", "400")
```

Now many shuffle stages will produce 400 partitions, unless Adaptive Query Execution or specific operations change the behavior.

Conceptually:

```text
Input data
    ↓
groupBy / join / distinct / orderBy
    ↓
shuffle
    ↓
400 output partitions
```

This means the next stage may have around 400 tasks.

If those 400 partitions are written to a table, the write may produce around 400 output files, depending on format, partitioning, coalescing, and write behavior.

This setting therefore affects both computation and output layout.

That is why it matters.

People often think:

> "More partitions means faster."

Sometimes yes.

Sometimes no.

More partitions can improve parallelism if tasks are too large.

But if tasks are already tiny, more partitions only adds overhead.

A small dataset with 200 shuffle partitions may produce 200 tiny tasks.

A huge dataset with 200 shuffle partitions may produce 200 enormous tasks.

Same setting.

Different pain.

The setting does not know your data.

You must.

---

## 5. Why the Default Is Often Wrong

The default value may be reasonable as a generic starting point.

But generic starting points are not workload tuning.

A default cannot know whether your job shuffles:

* 10 MB;
* 1 GB;
* 100 GB;
* 10 TB.

A default cannot know whether your cluster has:

* 4 cores;
* 40 cores;
* 400 cores;
* dynamic allocation;
* autoscaling;
* constrained executors.

A default cannot know whether the output should produce:

* 10 files;
* 100 files;
* 1000 files;
* one file per business partition;
* compacted lakehouse files.

Example:

```text
Shuffle size:
    20 MB

shuffle.partitions:
    200

Average partition:
    0.1 MB
```

That is probably too many partitions.

Now example:

```text
Shuffle size:
    2 TB

shuffle.partitions:
    200

Average partition:
    about 10 GB
```

That is probably too few partitions.

Same value.
Opposite problem.

Defaults are designed to be safe-ish.

Not optimal.

A default is a seat adjustment in a rental car.

You still need to move it.

Unless you enjoy driving with your knees at philosophical angles.

---

## 6. Too Few Shuffle Partitions

If shuffle partitions are too low, each partition becomes large.

Symptoms:

* long task duration;
* executor memory pressure;
* spill to disk;
* out-of-memory errors;
* slow joins;
* slow aggregations;
* straggler tasks;
* low cluster utilization;
* few tasks running while many cores sit idle;
* large output files, sometimes too large;
* poor parallelism.

Example:

```text
Cluster:
    100 total cores

Shuffle partitions:
    20

Result:
    only about 20 tasks in the shuffle stage
    many cores idle
```

Even if the cluster has 100 cores, Spark can only run about 20 tasks for that stage.

You paid for parallelism and then gave Spark too little work to distribute.

Another example:

```text
Shuffle size:
    1 TB

Shuffle partitions:
    50

Average partition:
    20 GB
```

Each task may need to process a large amount of data.

That can cause spills, memory pressure, and long tasks.

Too few partitions make each task heavy.

Heavy tasks are slow.

Heavy tasks also create stragglers.

One unlucky task becomes the final boss of the stage.

Everyone waits.

The Spark UI says 199 tasks complete, 1 task running.

You stare at it.

The task stares back.

---

## 7. Too Many Shuffle Partitions

If shuffle partitions are too high, each partition becomes tiny.

Symptoms:

* many tiny tasks;
* scheduler overhead;
* high task launch overhead;
* many shuffle files;
* many output files;
* slow metadata operations;
* small-file problems in object storage;
* inefficient writes;
* longer planning time;
* cluster busy doing overhead rather than useful work.

Example:

```text
Shuffle size:
    1 GB

Shuffle partitions:
    10,000

Average partition:
    0.1 MB
```

That is ridiculous for most jobs.

Spark spends too much time managing tasks.

If this writes output, it may produce many tiny files.

Tiny files hurt lakehouses and data lakes because query engines must open and plan many files.

This causes:

* slow reads;
* high metadata overhead;
* expensive compaction;
* object storage request overhead;
* slower downstream jobs.

Too many partitions can make one job seem okay while poisoning the table for everyone else.

That is rude.

A Spark job should not leave confetti in production storage.

Unless you are building a birthday pipeline.

Even then, compact your confetti.

---

## 8. The Average Partition Size Mental Model

A common tuning approach is to think in terms of target partition size.

Very rough mental model:

```text
average shuffle partition size =
    total shuffle data size / number of shuffle partitions
```

If a shuffle writes 100 GB and you use 200 partitions:

```text
100 GB / 200 = 0.5 GB per partition
```

That may be okay or too large depending on workload, cluster memory, and operation.

If a shuffle writes 10 GB and you use 200 partitions:

```text
10 GB / 200 = 50 MB per partition
```

Possibly reasonable.

If a shuffle writes 100 MB and you use 200 partitions:

```text
100 MB / 200 = 0.5 MB per partition
```

Probably too many.

This is only a rough model.

It ignores:

* skew;
* compression;
* serialization;
* memory overhead;
* CPU cost;
* file layout;
* operation type;
* adaptive execution;
* executor resources.

But it is a useful starting point.

A practical target may often be somewhere around tens to hundreds of MB per shuffle partition, depending on environment.

Do not treat this as a law.

Treat it as a smell detector.

If your average partition is 10 KB, something is probably silly.

If your average partition is 20 GB, something is probably suffering.

Spark tuning is partly math and partly listening to the suffering.

---

## 9. Shuffle Partitions and Cluster Cores

Another useful mental model:

```text
number of shuffle partitions should usually be at least enough
to keep the cluster busy
```

If your cluster has 64 total executor cores and your shuffle stage has 8 partitions, only 8 tasks can run concurrently.

The rest of the cores wait.

Example:

```text
Cluster:
    8 executors
    8 cores each
    total = 64 cores

Shuffle partitions:
    8

Maximum parallel tasks in that stage:
    about 8
```

Bad.

Now:

```text
Shuffle partitions:
    256

Maximum parallel tasks:
    enough to keep 64 cores busy across multiple waves
```

Better.

Why multiple waves?

Because tasks do not all take exactly the same time.

Having more partitions than cores gives Spark more scheduling flexibility.

But too many partitions create overhead.

A common intuition:

```text
shuffle partitions should often be some multiple of total cores
```

Maybe 2x, 3x, 4x, or more, depending on task size and workload.

But this is not enough alone.

You must also consider data size.

A tiny shuffle does not need 2,000 partitions just because the cluster has many cores.

A huge shuffle probably should not run with 8 partitions just because the developer was feeling minimalist.

A better heuristic is:

> Choose enough shuffle partitions to keep the cluster busy, but not so many that scheduling overhead, tiny tasks, and tiny files become the bottleneck.

That sentence is annoying because it does not give one magic number.

Spark rarely rewards magic numbers.

Spark rewards measurement.

Which is rude, but fair.

---

## 10. The Default Value Problem

Historically, many Spark examples mention:

```text
spark.sql.shuffle.partitions = 200
```

This value became almost mythological.

Many people see 200 and assume:

> Spark knows best.

Sometimes 200 is fine.

Sometimes it is absurdly low.

Sometimes it is absurdly high.

It depends on the workload.

For a tiny local dataset, 200 partitions may create too many small tasks.

For a 5 TB production aggregation, 200 partitions may create enormous tasks.

The default is not a recommendation for your specific job.

It is a generic starting point.

Generic starting points are useful.

They are not architecture.

Example:

```text
Data size:
    2 GB

Shuffle partitions:
    200

Average partition:
    about 10 MB
```

Maybe fine, maybe too small.

Now:

```text
Data size:
    2 TB

Shuffle partitions:
    200

Average partition:
    about 10 GB
```

That is much more suspicious.

Same setting.

Different reality.

Spark configuration without workload context is astrology with JVMs.

---

## 11. Why Spark Needs Shuffle Partitions at All

Spark processes data in partitions.

A partition is a chunk of distributed work.

When Spark reads data, input partitions often come from files or source splits.

Example:

```text
Input files:
    file_1.parquet
    file_2.parquet
    file_3.parquet

Spark creates input partitions based on file sizes and splits.
```

But after a shuffle, Spark needs to decide how many output partitions the shuffled data should be divided into.

That is what `spark.sql.shuffle.partitions` influences.

Example:

```text
Before groupBy:
    partitions are based on input layout

After groupBy:
    Spark redistributes rows by grouping key

Result:
    number of reduce-side partitions is controlled by shuffle partition settings
```

Without such a setting, Spark would not know how many reduce tasks to create for wide operations.

Too few reduce tasks means too much data per task.

Too many reduce tasks means too much scheduling overhead.

So shuffle partitions are Spark's way of asking:

> After data movement, how many pieces should this work become?

That is a deceptively deep question.

Like many deceptively deep questions, the answer is not "200."

---

## 12. Narrow vs Wide Transformations

To understand shuffle partitions, you need narrow vs wide transformations.

### Narrow transformation

Each output partition depends on one input partition.

Examples:

```python
df.select("customer_id", "amount")

df.filter(df.amount > 0)

df.withColumn("amount_with_tax", df.amount * 1.1)
```

These usually do not require shuffling data across the cluster.

Each partition can be processed independently.

### Wide transformation

Output partitions depend on many input partitions.

Examples:

```python
df.groupBy("customer_id").count()

orders.join(customers, on="customer_id")

df.dropDuplicates(["order_id"])

df.orderBy("created_at")
```

These often require shuffle.

Rows must move across executors so related records end up together.

Example:

```text
groupBy("customer_id")

All rows for customer C123 must meet in the same reduce-side partition.
```

This movement is expensive.

It involves:

* network transfer;
* disk spill;
* serialization;
* sorting;
* task scheduling;
* memory pressure;
* shuffle file management.

Shuffle partitions matter because they shape this expensive distributed movement.

A shuffle is where Spark stops being elegant and starts moving furniture.

Large furniture.

Across the network.

---

## 13. What Actually Happens During a Shuffle

A simplified shuffle has two sides:

### Map side

Spark reads input partitions and writes shuffle data grouped by target partition.

### Reduce side

Spark reads shuffled data and computes the final operation.

Conceptually:

```text
Input partitions
    ↓
map tasks write shuffle files
    ↓
data redistributed by key/hash/range
    ↓
reduce tasks read shuffled data
    ↓
aggregation/join/sort result
```

If you set:

```text
spark.sql.shuffle.partitions = 200
```

Spark may create around 200 reduce-side partitions for many SQL shuffle operations.

That means around 200 reduce tasks.

Each reduce task gets one piece of the shuffled data.

If the data is evenly distributed, that can work well.

If the data is skewed, some reduce tasks get much more data.

Example:

```text
Partition 1:
    500 MB

Partition 2:
    480 MB

Partition 3:
    520 MB

Partition 4:
    75 GB
```

Partition 4 becomes the villain.

Spark jobs often wait for a few slow tasks.

This is why shuffle tuning and skew diagnosis are connected.

The partition count controls how many buckets exist.

The data distribution controls how full each bucket becomes.

Buckets are innocent.

Data is chaotic.

---

## 14. Why "More Partitions" Is Not Always Better

A beginner often thinks:

> More partitions means more parallelism, so more is better.

Reasonable.

Wrong, eventually.

More partitions can increase parallelism, but each partition becomes a task.

Tasks have overhead.

Spark must:

* schedule tasks;
* serialize task descriptions;
* launch tasks;
* track task status;
* collect metrics;
* manage shuffle metadata;
* write task outputs;
* coordinate retries.

If each task processes meaningful data, this overhead is fine.

If each task processes 500 KB, overhead dominates.

Example:

```text
Shuffle data:
    1 GB

Shuffle partitions:
    10,000

Average partition:
    about 0.1 MB
```

This is usually ridiculous.

Spark spends more time managing tiny tasks than processing data.

Also, if this result is written to files, you may create many tiny files.

So more partitions can produce:

* more task overhead;
* more metadata;
* more shuffle files;
* more output files;
* more driver pressure;
* more scheduling cost.

Parallelism is good.

Microscopic tasks are not.

Spark likes parallel work.

Spark does not like being asked to organize a million crumbs.

---

## 15. Why "Fewer Partitions" Is Not Always Better

Another beginner reaction:

> Too many partitions are bad, so fewer is better.

Also reasonable.

Also wrong, eventually.

Fewer partitions mean fewer tasks.

But each task may process more data.

If partitions become too large, tasks may:

* run for a long time;
* spill to disk;
* exceed memory;
* create garbage collection pressure;
* fail and retry expensively;
* underuse cluster cores;
* create stragglers.

Example:

```text
Shuffle data:
    1 TB

Shuffle partitions:
    16

Average partition:
    about 64 GB
```

That is usually too large for many workloads.

Even if it technically runs, it may run slowly and spill heavily.

A failed task may need to reprocess 64 GB.

That is painful.

Fewer partitions can also reduce parallelism.

Example:

```text
Cluster:
    100 cores

Shuffle partitions:
    10

Only 10 reduce tasks exist.
```

At most 10 tasks run in that stage.

Ninety cores are effectively spectators.

Very expensive spectators.

The correct direction is not "more" or "fewer."

The correct direction is "appropriate."

A very boring word.

Most performance engineering lives there.

---

## 16. The Two-Dimensional Mental Model

A better mental model has two dimensions:

```text
1. Enough partitions to use available cores.
2. Reasonable data size per partition.
```

The first dimension is parallelism.

The second dimension is task size.

You need both.

Example:

```text
Cluster:
    64 cores

Shuffle data:
    1 TB
```

If you set 64 shuffle partitions:

```text
Parallelism:
    okay-ish, one wave of tasks

Average partition:
    about 16 GB
```

That may be too large.

If you set 4,096 shuffle partitions:

```text
Parallelism:
    plenty

Average partition:
    about 256 MB
```

That may be more reasonable.

If you set 100,000 shuffle partitions:

```text
Parallelism:
    excessive

Average partition:
    about 10 MB
```

That may create too much overhead.

So the practical reasoning is:

```text
total shuffle data size
    ÷ target partition size
    = approximate shuffle partition count
```

Then compare this with cluster cores.

If the result is much smaller than total cores, you may underuse the cluster.

If the result is massively larger than needed, you may create overhead.

This gives you a starting point.

Not an answer carved into stone.

Spark stone tablets are expensive to maintain.

---

## 17. A Small Rule-of-Thumb Formula

A practical starting formula:

```text
shuffle_partitions ≈ total_shuffle_size / target_partition_size
```

Then sanity-check against cluster cores:

```text
shuffle_partitions should often be at least:
    total_executor_cores × 2
```

Maybe 2x, 3x, 4x, or more, depending on task size and workload.

But this is not enough alone.

You must also consider data size.

A tiny shuffle does not need 2,000 partitions just because the cluster has many cores.

A huge shuffle probably should not run with 8 partitions just because the developer was feeling minimalist.

A better heuristic is:

> Choose enough shuffle partitions to keep the cluster busy, but not so many that scheduling overhead, tiny tasks, and tiny files become the bottleneck.

That sentence is annoying because it does not give one magic number.

Spark rarely rewards magic numbers.

Spark rewards measurement.

Which is rude, but fair.

---

## 18. The Data-Size Heuristic

A practical way to think about shuffle partitions is target data size per partition.

Common rough targets:

```text
Small/simple workloads:
    64 MB - 128 MB per partition

General Spark SQL workloads:
    128 MB - 256 MB per partition

Large analytical workloads:
    256 MB - 512 MB per partition

Very heavy per-row processing:
    smaller partitions may be safer
```

These are not laws.

They are starting points.

Suppose a shuffle stage processes 1 TB of data.

If you want roughly 256 MB per partition:

```text
1 TB = 1,024 GB = 1,048,576 MB

1,048,576 MB / 256 MB ≈ 4,096 partitions
```

So 4,000-ish shuffle partitions may be reasonable.

If you used Spark's old default of 200 partitions:

```text
1,048,576 MB / 200 ≈ 5,243 MB per partition
```

That means each task may process around 5 GB.

Depending on memory, joins, aggregation complexity, and spill behavior, that may be too large.

If you used 20,000 partitions:

```text
1,048,576 MB / 20,000 ≈ 52 MB per partition
```

That might be too many tiny tasks.

So the right number is a balance.

Not too few.

Not too many.

Spark tuning is Goldilocks with logs.

---

## 19. But Partition Size Is Not Just Bytes

Bytes matter.

But bytes are not everything.

Two partitions with the same byte size can have very different costs.

A 256 MB partition with simple numeric columns may be easy.

A 256 MB partition with huge nested JSON strings may be painful.

A 256 MB partition used in a simple projection is different from a 256 MB partition used in:

* sort;
* aggregation;
* window function;
* skewed join;
* Python UDF;
* expensive parsing;
* high-cardinality groupBy;
* distinct count;
* explode;
* complex nested transformation.

So when choosing shuffle partitions, consider:

* data size;
* row count;
* column width;
* operation type;
* memory pressure;
* skew;
* serialization cost;
* spill;
* output file size;
* cluster cores;
* executor memory;
* downstream operations.

This is why "one partition = X MB" is only a heuristic.

A partition is not just a bag of bytes.

It is work.

And some work is spicy.

---

## 20. Why Too Few Shuffle Partitions Hurt

Too few shuffle partitions usually means each task gets too much data.

Symptoms:

* long-running tasks;
* executor memory pressure;
* spilling to disk;
* failed tasks;
* garbage collection overhead;
* uneven task durations;
* poor parallelism;
* slow joins;
* slow aggregations;
* low CPU utilization across the cluster.

Example:

```text
Cluster:
    40 total cores

Shuffle partitions:
    8

Result:
    only 8 tasks can run for that shuffle stage
    32 cores may sit idle
```

That is bad.

You are paying for 40 cores and using 8.

The cluster is basically watching a small group project.

Another example:

```text
Shuffle data:
    800 GB

Shuffle partitions:
    100

Average partition size:
    8 GB
```

That may cause large tasks, spills, and memory issues.

Too few partitions often produce "elephant tasks."

Large, slow, heavy tasks that dominate the stage.

Spark stages complete when the slowest tasks finish.

So a few huge tasks can delay everything.

A Spark job is not done when most tasks finish.

It is done when the last task finally stops dragging its enormous suitcase across the cluster.

---

## 21. Why Too Many Shuffle Partitions Hurt

Too many shuffle partitions creates the opposite problem.

Each task is tiny.

Symptoms:

* high scheduler overhead;
* too many tasks;
* tiny output files;
* slow metadata operations;
* excessive task startup cost;
* inefficient writes;
* inefficient downstream reads;
* small file problem;
* driver overhead;
* unnecessary shuffle metadata.

Example:

```text
Shuffle data:
    10 GB

Shuffle partitions:
    10,000

Average partition size:
    1 MB
```

That is usually silly.

Spark now has to schedule 10,000 tiny tasks.

The overhead of managing tasks may become larger than the actual computation.

Also, if the shuffle result is written to storage, you may produce many tiny files.

Tiny files are a classic data lake/lakehouse disease.

They hurt:

* query planning;
* metadata management;
* object-store listing;
* downstream Spark jobs;
* compaction cost.

Too many partitions make Spark look busy while doing inefficient work.

Like someone opening 100 browser tabs to write one paragraph.

Relatable.

Still inefficient.

---

## 22. Shuffle Partitions and Output Files

A very practical consequence:

> Shuffle partitions often influence the number of output files.

If a DataFrame has 1,000 partitions when written, Spark may produce up to 1,000 output files, depending on the write path and partitioning.

Example:

```python
df.write.mode("overwrite").parquet("s3://bucket/output/")
```

If `df` has 2,000 partitions, you may get many files.

If the data is also partitioned by a column:

```python
df.write.partitionBy("event_date").parquet("s3://bucket/events/")
```

then files may be distributed across physical partition directories.

This can create many small files if each Spark partition writes small amounts into many output partitions.

Example:

```text
Spark partitions:
    2,000

Physical partition column:
    event_date

Dates touched:
    30

Potential result:
    many files across many event_date directories
```

This is why tuning shuffle partitions is connected to table layout.

The question is not only:

> How fast does the job run?

It is also:

> What physical data does the job leave behind?

A fast job that creates 80,000 tiny files is not finished.

It has simply transferred pain to the future.

Very generous.

Very bad.

---

## 23. Shuffle Partitions and groupBy

A `groupBy` often triggers a shuffle.

Example:

```python
from pyspark.sql import functions as F

daily_revenue = (
    orders
    .groupBy("order_date")
    .agg(F.sum("amount").alias("total_revenue"))
)
```

Spark must bring rows with the same `order_date` together.

The number of shuffle partitions determines how many reduce-side tasks process the grouped data.

If `spark.sql.shuffle.partitions = 200`, Spark usually creates 200 reduce partitions for the shuffle.

But if `order_date` has only 7 distinct values, many partitions may be empty or tiny.

If `customer_id` has 50 million distinct values, 200 partitions may be too few.

So the grouping key matters.

Low-cardinality groupBy:

```text
groupBy("country")
```

May not need many partitions.

High-cardinality groupBy:

```text
groupBy("customer_id")
```

May need many more.

But cardinality alone is not enough.

Distribution matters.

If 90% of rows belong to one customer, the job is skewed.

More partitions alone may not fix it.

Spark tuning always finds a way to say:

> "It depends."

Deeply irritating.

Technically correct.

---

## 24. Shuffle Partitions and Joins

Joins often trigger shuffles.

Example:

```python
joined = orders.join(customers, on="customer_id", how="inner")
```

If neither side is already partitioned appropriately and no broadcast join is used, Spark may shuffle both sides by `customer_id`.

The shuffle partition count determines how many partitions are used for the join.

Too few partitions:

* large join tasks;
* memory pressure;
* spills;
* long-running tasks.

Too many partitions:

* tiny tasks;
* scheduler overhead;
* too many output files later.

A join also has additional concerns:

* join type;
* join key cardinality;
* key skew;
* broadcast eligibility;
* table sizes;
* filter pushdown;
* partition pruning;
* input file sizes;
* adaptive execution.

If one side is small, a broadcast join may avoid shuffle:

```python
from pyspark.sql import functions as F

joined = orders.join(F.broadcast(customers), on="customer_id")
```

This changes the whole problem.

Instead of tuning shuffle partitions for a large join, Spark broadcasts the small table to executors.

So before tuning shuffle partitions, ask:

> Should this operation shuffle at all?

Sometimes the best shuffle tuning is removing the shuffle.

That is very Spark.

The fastest shuffle is the one that never happened.

---

## 25. Shuffle Partitions and Distinct

Operations like `distinct()` and `dropDuplicates()` often trigger shuffles.

Example:

```python
unique_customers = orders.select("customer_id").distinct()
```

Spark must bring equal values together to remove duplicates.

Similarly:

```python
deduped_orders = orders.dropDuplicates(["order_id"])
```

This may shuffle by `order_id`.

If the dataset is large and the key is high-cardinality, partition count matters.

But deduplication also raises correctness questions.

Example:

```python
orders.dropDuplicates(["order_id"])
```

Which row is kept?

If duplicates differ, this may be nondeterministic unless you define ordering.

Better pattern:

```python
from pyspark.sql import Window
from pyspark.sql import functions as F

window = Window.partitionBy("order_id").orderBy(F.col("updated_at").desc())

deduped_orders = (
    orders
    .withColumn("row_number", F.row_number().over(window))
    .filter(F.col("row_number") == 1)
    .drop("row_number")
)
```

This also triggers shuffle and sort-like work.

So shuffle partitions are part of performance.

But logic is part of correctness.

Performance tuning cannot rescue ambiguous deduplication.

It can only make the ambiguity faster.

A terrifying achievement.

---

## 26. Shuffle Partitions and Window Functions

Window functions often require data to be partitioned and sorted.

Example:

```python
from pyspark.sql import Window
from pyspark.sql import functions as F

window = Window.partitionBy("customer_id").orderBy("event_timestamp")

events_with_rank = (
    events
    .withColumn("event_rank", F.row_number().over(window))
)
```

Spark needs all rows for each `customer_id` together and ordered by `event_timestamp`.

This may involve shuffle and sort.

Shuffle partitions affect how many tasks process the window partitions.

Window functions can be expensive because they may require:

* shuffle;
* sort within partition;
* memory for frame computation;
* skew handling;
* large per-key groups.

If one customer has millions of events, one task may become huge even if shuffle partitions are high.

This is data skew.

Example:

```text
customer_id = normal customers:
    100 events each

customer_id = C_BIG:
    500 million events
```

Partition count alone cannot split one key across multiple reduce tasks for a standard window partitioned by that key.

All rows for `C_BIG` must be together.

So the problem is not only partition count.

It is key distribution and algorithm design.

Sometimes you need:

* salting;
* pre-aggregation;
* special handling for heavy keys;
* different window logic;
* approximate methods;
* filtering;
* separate processing for large entities.

Shuffle partitions are a knob.

They are not a magic wand.

Spark has knobs.

Not miracles.

---

## 27. Adaptive Query Execution Changes the Game

Adaptive Query Execution, or AQE, allows Spark to adjust query plans at runtime.

AQE can:

* coalesce shuffle partitions;
* handle skewed joins;
* switch join strategies;
* optimize based on runtime statistics.

This means `spark.sql.shuffle.partitions` may become an initial value rather than the final number of partitions.

Example:

```text
spark.sql.shuffle.partitions = 2000

AQE observes shuffle partitions are too small.
AQE coalesces them to fewer partitions.
```

This is extremely useful.

AQE can reduce the penalty of setting shuffle partitions too high.

A common strategy with AQE enabled:

> Set `spark.sql.shuffle.partitions` somewhat higher, then let AQE coalesce small partitions.

But do not become careless.

AQE helps.

It does not remove the need to understand the workload.

AQE may not fully solve:

* severe skew;
* bad data modeling;
* bad joins;
* Python UDF slowness;
* small input files;
* bad output layout;
* wrong partitioning strategy;
* insufficient cluster resources.

AQE is a smart assistant.

Not a babysitter.

Although sometimes we wish Spark had a babysitter.

Preferably one with cluster admin privileges.

---

## 28. Coalescing Shuffle Partitions

AQE can coalesce small shuffle partitions.

Suppose Spark starts with 2,000 shuffle partitions.

After seeing actual shuffle sizes, it may combine small partitions into fewer tasks.

This helps avoid tiny tasks.

Conceptually:

```text
Before AQE:
    2,000 tiny shuffle partitions

After AQE coalescing:
    350 reasonably sized partitions
```

This can improve performance.

It can also reduce small output files if the coalesced result is written.

Important settings include concepts like:

```text
adaptive execution enabled
target post-shuffle partition size
minimum number of partitions
coalescing enabled
```

The exact names vary by Spark version and environment, but the idea is stable.

AQE tries to create better-sized partitions after observing real data.

This is useful because before execution, Spark may not know exact shuffle sizes.

Statistics may be stale or incomplete.

Runtime truth beats planning guesses.

As it often does.

---

## 29. Skew and Shuffle Partitions

Data skew happens when some partitions get much more data than others.

Example:

```text
Partition 1:
    100 MB

Partition 2:
    120 MB

Partition 3:
    95 MB

Partition 4:
    80 GB
```

The stage waits for partition 4.

This is skew.

Increasing shuffle partitions may help if skew is caused by many keys being unevenly distributed across too few partitions.

But it may not help if one key dominates.

Example:

```text
customer_id = C_BIG
contains 60% of all rows
```

All rows for `C_BIG` go to the same hash partition when grouped or joined by `customer_id`.

Increasing partitions from 200 to 2,000 does not split `C_BIG`.

It still belongs to one partition.

Solutions may include:

* AQE skew join handling;
* salting skewed keys;
* pre-aggregating;
* filtering;
* splitting heavy keys into special workflows;
* broadcasting small tables;
* redesigning joins;
* using approximate methods;
* using domain-specific partitioning.

Salting example:

```python
from pyspark.sql import functions as F

salted_events = events.withColumn(
    "salt",
    (F.rand(seed=42) * 10).cast("int"),
)
```

But salting must be used carefully.

It changes grouping/join strategy and usually requires recombining results.

Do not salt randomly in production because a blog post said so.

Salt is seasoning.

Too much ruins the dish.

And possibly the join.

---

## 30. Diagnosing Shuffle Partition Problems

To diagnose shuffle partition problems, inspect the Spark UI.

Look at:

* number of tasks per stage;
* task duration distribution;
* shuffle read size;
* shuffle write size;
* spill to memory;
* spill to disk;
* input size per task;
* executor CPU utilization;
* garbage collection time;
* skewed tasks;
* failed tasks;
* output file count.

Symptoms of too few partitions:

```text
Few tasks
Large shuffle read per task
Long task duration
High spill
Low cluster parallelism
Executor memory pressure
```

Symptoms of too many partitions:

```text
Many tiny tasks
Short task duration but large scheduler overhead
Tiny shuffle read per task
Many output files
Driver/scheduler overhead
Slow metadata operations
```

Symptoms of skew:

```text
Most tasks finish quickly
A few tasks run much longer
A few tasks have huge shuffle read
Stage waits on stragglers
```

The Spark UI is not optional for serious tuning.

Logs are useful.

Metrics are useful.

But the Spark UI shows the shape of work.

And Spark performance is mostly about the shape of work.

Not vibes.

Never tune Spark by vibes.

Unless the vibe is "open the Spark UI."

That vibe is approved.

---

## 31. A Practical Tuning Workflow

A practical workflow:

### Step 1: Enable AQE if appropriate

Modern Spark workloads often benefit from AQE.

Check whether your environment enables it by default.

### Step 2: Start with a reasonable shuffle partition value

Do not blindly use 200 for everything.

For larger workloads, start higher.

Example:

```text
Small local/dev job:
    8-64

Moderate job:
    200-800

Large cluster/job:
    1,000-5,000+

Huge workloads:
    depends heavily on data size and cluster
```

These are rough starting points, not sacred numbers.

### Step 3: Run and inspect Spark UI

Look at task sizes, durations, spill, and skew.

### Step 4: Estimate partition size

Use shuffle read/write bytes divided by task count.

### Step 5: Adjust

If tasks are huge and spilling, increase partitions.

If tasks are tiny and overhead dominates, decrease partitions or let AQE coalesce.

If skew dominates, fix skew, not just partition count.

### Step 6: Check output files

The job can be fast and still produce bad files.

### Step 7: Re-measure

Do not declare victory because the config looks smarter.

Measure runtime, cost, file count, and downstream performance.

Spark tuning is empirical.

The cluster does not care about your theory.

Rude machine.

Honest machine.

---

## 32. Example: Too Few Partitions

Suppose:

```text
Cluster:
    20 executors
    4 cores each
    total cores = 80

Shuffle data:
    800 GB

spark.sql.shuffle.partitions:
    100
```

Average shuffle partition size:

```text
800 GB / 100 = 8 GB per partition
```

Only 100 tasks exist.

With 80 cores, Spark can run 80 tasks at once, then only 20 remaining tasks.

Each task may be huge.

Possible symptoms:

* spilling;
* long task duration;
* memory pressure;
* slow stage;
* poor failure recovery.

Try:

```text
spark.sql.shuffle.partitions = 1600
```

Average partition size:

```text
800 GB / 1600 = 512 MB
```

Still large, but much more manageable.

With AQE, Spark may coalesce if partitions are too small.

You would then inspect:

* did spills decrease?
* did task time improve?
* did scheduler overhead remain acceptable?
* did output file count become too high?
* did cost improve?

Do not tune only for runtime.

Tune for the whole pipeline.

Spark can make one stage faster and make downstream storage worse.

Spark is talented like that.

---

## 33. Example: Too Many Partitions

Suppose:

```text
Cluster:
    16 cores

Shuffle data:
    4 GB

spark.sql.shuffle.partitions:
    5000
```

Average partition size:

```text
4 GB / 5000 ≈ 0.8 MB
```

This is likely too many partitions.

Symptoms:

* thousands of tiny tasks;
* high scheduling overhead;
* slow job despite small data;
* many tiny output files.

A better value might be:

```text
spark.sql.shuffle.partitions = 64
```

Average partition size:

```text
4 GB / 64 = 64 MB
```

This is more reasonable.

But again, measure.

If the operation is CPU-heavy, maybe smaller partitions help.

If the operation is simple, fewer partitions may be better.

The point is not "64 is correct."

The point is that 5,000 partitions for 4 GB is probably chaos with a config key.

A small job does not need a thousand-task opera.

---

## 34. Example: Skewed Join

Suppose you join events to customers by `customer_id`.

Most customers have modest event counts.

One customer has enormous volume because it is a test account, bot, tenant, or aggregation artifact.

Spark UI shows:

```text
Stage tasks:
    999 tasks finish in under 30 seconds
    1 task runs for 45 minutes
```

This is not primarily a shuffle partition count problem.

This is skew.

Options:

### Filter bad entity

If the key is internal/test/noise:

```python
events_filtered = events.filter(F.col("customer_id") != "C_BIG")
```

### Process heavy key separately

```text
normal customers:
    standard join

heavy customer:
    separate workflow
```

### Salt the join key

Use salt to split one heavy key across multiple partitions.

### Broadcast the smaller side

If customers table is small:

```python
joined = events.join(F.broadcast(customers), "customer_id")
```

### Enable AQE skew join handling

Modern Spark may split skewed partitions automatically.

The right answer depends on why the skew exists.

Do not blindly increase shuffle partitions.

If one key has 60% of the data, more partitions do not magically create more keys.

Spark cannot hash one elephant into many elephants unless you change the logic.

That sentence is weird.

But true.

---

## 35. Shuffle Partitions and Repartition

`spark.sql.shuffle.partitions` controls default shuffle partitions for Spark SQL operations.

But you can also explicitly repartition.

Example:

```python
df_repartitioned = df.repartition(800, "customer_id")
```

This creates a shuffle and partitions by `customer_id`.

Useful when:

* you want to control downstream parallelism;
* you want to align data by a join/group key;
* you want to influence output file count;
* you need to rebalance data.

But repartition is expensive because it shuffles.

Do not add it casually.

Bad pattern:

```python
df = df.repartition(1000)
df = df.filter(...)
df = df.repartition(1000)
df = df.groupBy(...).agg(...)
df = df.repartition(1000)
```

This may create unnecessary shuffles.

Each shuffle is expensive.

A pipeline with too many repartitions is a cardio workout for the cluster.

Healthy for nobody.

Use repartition when it has a purpose.

And document the purpose.

Future engineers should not have to infer whether `repartition(937)` was science, superstition, or a typo.

---

## 36. Shuffle Partitions and Coalesce

`coalesce()` reduces the number of partitions without a full shuffle in many cases.

Example:

```python
small_output = df.coalesce(10)
```

This is often used before writing small outputs.

Difference:

### repartition

```text
Can increase or decrease partitions.
Usually causes full shuffle.
Can rebalance data.
```

### coalesce

```text
Usually decreases partitions.
Avoids full shuffle when possible.
May produce uneven partitions.
```

Use `coalesce()` when:

* reducing partition count before write;
* data is already reasonably balanced;
* avoiding full shuffle matters.

Use `repartition()` when:

* increasing parallelism;
* rebalancing data;
* partitioning by key;
* preparing for join/group/write layout.

Example:

```python
result = small_result.coalesce(1)
```

This writes one file.

Sometimes useful for tiny exports.

Usually bad for large data.

`coalesce(1)` is the duct tape of Spark.

Convenient.

Dangerous.

Often found at crime scenes.

---

## 37. Shuffle Partitions and Local Development

In local development, the default 200 shuffle partitions can be silly.

If you run Spark locally on a laptop with small data:

```python
spark.conf.set("spark.sql.shuffle.partitions", "8")
```

or:

```python
spark.conf.set("spark.sql.shuffle.partitions", "16")
```

may make jobs much faster.

Why?

Because a local toy dataset does not need 200 shuffle tasks.

Example:

```text
Data size:
    10 MB

Default shuffle partitions:
    200

Average:
    0.05 MB per partition
```

That is task overhead theater.

For local learning, reduce shuffle partitions.

For production, tune based on cluster and data size.

Do not copy local configs into production blindly.

A laptop config and a 50-node cluster config are different animals.

One is a cat.

One is a warehouse full of cats with JVMs.

---

## 38. Shuffle Partitions in Interviews

In interviews, a good answer is not:

> "Set shuffle partitions to 200."

A better answer:

> "Shuffle partitions control the number of reduce-side partitions created after wide transformations like joins and aggregations. Too few partitions creates large tasks, spills, and poor parallelism. Too many creates tiny tasks, scheduler overhead, and small files. I tune it based on data size, cluster cores, operation type, skew, and Spark UI metrics. With AQE enabled, I may start with a higher value and let Spark coalesce partitions, but I still inspect task sizes, spills, skew, and output file counts."

That answer shows seniority.

It says you understand:

* wide transformations;
* shuffle cost;
* parallelism;
* task sizing;
* AQE;
* skew;
* measurement;
* downstream file layout.

A shorter version:

> "It is the default number of partitions after a shuffle. I tune it to balance parallelism and overhead. Too low means huge slow tasks and spills; too high means too many tiny tasks and files. I use data size, cluster cores, Spark UI, and AQE behavior to choose a reasonable value."

That is interview-ready.

Not too long.

Not junior.

No magic number worship.

Very important.

Magic number worship is how clusters become expensive shrines.

---

## 39. Practical Rules of Thumb

Here are practical rules.

### Rule 1: Do not blindly accept 200

For large production jobs, 200 may be too low.

For local jobs, 200 may be too high.

### Rule 2: Think in cores and bytes

You need enough partitions for parallelism and reasonable partition sizes.

### Rule 3: Use AQE when possible

AQE can coalesce small shuffle partitions and help with skew.

### Rule 4: Too few partitions cause large tasks

Symptoms include spills, memory pressure, and low parallelism.

### Rule 5: Too many partitions cause overhead

Symptoms include tiny tasks, scheduler overhead, and small files.

### Rule 6: Skew is not solved only by partition count

If one key dominates, you need skew-specific strategies.

### Rule 7: Watch output files

Shuffle partition count can affect file counts and downstream performance.

### Rule 8: Tune per workload

A setting that works for one job may be bad for another.

### Rule 9: Measure using Spark UI

Task duration, shuffle bytes, spills, and skew tell the truth.

### Rule 10: Prefer removing unnecessary shuffles

Broadcast joins, pre-aggregation, filtering, and better modeling may beat tuning.

The best Spark tuning is often not changing a knob.

It is changing the plan.

---

## 40. Final Thought

`spark.sql.shuffle.partitions` is one of the most misunderstood Spark settings.

It looks like a simple number.

It is not.

It controls how Spark divides work after wide transformations like joins, aggregations, distincts, and window operations.

Set it too low, and Spark creates huge tasks that spill, run slowly, underuse the cluster, and fail more easily.

Set it too high, and Spark creates thousands of tiny tasks, scheduler overhead, metadata pain, and small files.

The right value depends on:

* data size;
* cluster cores;
* operation type;
* row width;
* shuffle size;
* skew;
* memory;
* AQE;
* output layout;
* downstream usage.

This is why "just set it to X" is usually weak advice.

The mature approach is:

> Estimate reasonable partition sizes, ensure enough parallelism, enable adaptive execution when appropriate, inspect Spark UI metrics, watch for skew and spill, and validate output file layout.

Spark is not asking for a lucky number.

It is asking you to understand the work.

The knob matters.

But the knob is not the system.

The system is the data, the DAG, the cluster, the shuffle, the skew, the memory, the file layout, and the downstream consumers who will inherit whatever your job writes.

So tune shuffle partitions carefully.

Not emotionally.

Not superstitiously.

Not by copying a Stack Overflow answer from 2016.

Use the Spark UI.

Measure the workload.

Respect the shuffle.

And remember:

A shuffle is where Spark stops being a polite DataFrame API and becomes a distributed systems exam.

With invoices.
