Title: The Sunday Materialization - Why Your dbt Project Turned Into a Spaghetti Monster
Subtitle: How Good SQL Intentions Become a Tangled DAG, and How to Refactor Your Analytics Engineering Before It Starts Demanding Sacrifices
Date: 2026-01-18 07:00
Modified: 2026-01-18 07:00
Category: Sunday
Tags: data engineer, data platform engineer, data, data architecture, dbt, analytics engineering, data modeling, ELT, maintainability
Slug: sunday-materialization-dbt-spaghetti-monster
Authors: Eduardo G Gusmao
Summary: A weekly educational topic/lecture/discussion on Data Engineering topics that we all experienced at least once (or will!)
Status: final
Lang: en
Template: topic
Cadence: Biweekly
Scope: Data Engineering, Industry, Data Challenges
Tone: Analytical, Educational, Non-Sensational
Canonical: https://www.gusmaolab.org/blog/sunday-materialization-dbt-spaghetti-monster/
Meta_description: Biweekly analysis of important Data Engineering concepts.
Meta_keywords: data concepts, topics, lectures, discussions, dbt, analytics engineering, data modeling
Cover: images/covers/dbt-spaghetti-monster.png
Thumbnail: images/thumbnails/dbt-spaghetti-monster-thumb.png

# Why Your dbt Project Turned Into a Spaghetti Monster

dbt projects rarely start as monsters.

They usually start beautifully.

A few source tables.
A few staging models.
A clean mart.
Some tests.
A charming little DAG.
Everyone says "analytics engineering" with hope in their eyes.

At the beginning, it feels like order has finally arrived.

SQL transformations are versioned.
Models are documented.
Tests are close to the code.
Lineage is visible.
The warehouse stops being a swamp and starts becoming a garden.

Then time passes.

A stakeholder asks for a new metric.
A dashboard needs a small exception.
Finance wants revenue "almost the same, but not exactly."
Marketing needs campaign attribution with custom logic.
Product wants event funnels.
Customer Success wants account health.
Someone adds a model called `customer_revenue_v2_final`.
Someone else creates `int_orders_enriched_new`.
A staging model starts joining six tables.
A mart references another mart.
A model has 420 lines of SQL and a `CASE WHEN` block that looks like a legal contract.
A macro exists, but nobody knows whether it is safe to use.
A source freshness test fails, but "it always fails," so people ignore it.
A dashboard depends on a model marked deprecated.
A new engineer asks where customer logic lives and five people say "it depends."

Congratulations.

Your dbt project has become a spaghetti monster.

Not because dbt is bad.

dbt is a useful tool.

The monster appears when the project grows faster than its architecture, ownership, conventions, and modeling discipline.

dbt gives you structure.

It does not guarantee structure.

It gives you a DAG.

It does not guarantee the DAG makes sense.

It gives you tests.

It does not guarantee you test the right things.

It gives you documentation.

It does not guarantee anyone writes useful documentation.

The tool creates the opportunity for good analytics engineering.

The team still has to do the engineering.

This post is about why dbt projects become tangled, how to recognize the warning signs, and how to refactor them into something boring, trustworthy, and maintainable.

Boring, in data platforms, is a compliment.

Boring means your revenue table does not require a séance.

---

## 1. What dbt Is Really Good At

dbt is excellent at organizing SQL-based transformations.

At its best, dbt helps teams:

* version-control analytical transformations;
* define dependencies between models;
* materialize tables and views;
* test assumptions;
* document models and columns;
* manage environments;
* build reusable macros;
* expose lineage;
* structure ELT workflows;
* create curated data products.

A simple dbt flow might look like this:

```text
sources
    ↓
staging models
    ↓
intermediate models
    ↓
marts
    ↓
dashboards / ML / reverse ETL / reports
```

This layered approach can be very healthy.

For example:

```text
raw.stripe_payments
    ↓
stg_stripe__payments
    ↓
int_payments_enriched
    ↓
fct_payments
    ↓
mart_revenue_daily
```

Each layer has a purpose.

Sources represent raw inputs.
Staging cleans and standardizes source-specific data.
Intermediate models combine and transform concepts.
Marts serve business use cases.

When the project is small, this is delightful.

The trouble begins when the layers become decorative rather than meaningful.

Then dbt becomes a SQL warehouse with folders.

And folders alone do not save anyone.

A folder named `marts` does not make a model a mart.

A folder named `staging` does not prevent someone from writing a 12-table business transformation inside it.

The names help.

The discipline matters more.

---

## 2. The First Symptom: Everything Depends on Everything

A healthy dbt DAG has understandable flow.

A spaghetti DAG has models pointing everywhere.

Bad smell:

```text
staging -> mart
mart -> intermediate
intermediate -> staging
mart -> mart
dashboard_model -> source
random_model -> everything
```

When everything depends on everything, several problems appear:

* changes become risky;
* builds become slower;
* lineage becomes confusing;
* tests are harder to interpret;
* ownership becomes unclear;
* refactoring becomes frightening;
* circular business logic appears;
* models become impossible to reason about.

A healthy layered DAG usually flows in one direction:

```text
source
  ↓
staging
  ↓
intermediate
  ↓
mart
  ↓
exposure
```

That does not mean every project must use exactly these names.

But it does mean the dependency direction should be intentional.

A `mart` model should usually not be an upstream dependency for another core transformation unless it is explicitly designed as a reusable data product.

A staging model should usually not contain complex business logic.

A dashboard-specific model should usually not become a dependency for half the company.

The DAG is not just a build graph.

It is an architecture diagram.

If it looks like someone dropped noodles on a subway map, the project is telling you something.

Listen to the noodles.

---

## 3. The Second Symptom: Staging Models Are Doing Too Much

Staging models should usually be boring.

Their job is to create a clean, standardized interface over raw source data.

Typical staging tasks:

* rename columns;
* cast types;
* standardize timestamps;
* normalize booleans;
* handle source-specific naming;
* expose source freshness;
* apply light cleaning;
* preserve source grain;
* avoid heavy business logic.

Example staging model:

```sql
SELECT
    id AS order_id,
    customer_id,
    created_at::timestamp AS order_created_at,
    status AS order_status,
    total_amount::decimal(12, 2) AS order_total_amount
FROM {{ source('stripe', 'orders') }}
```

This is fine.

Now compare:

```sql
SELECT
    o.id AS order_id,
    c.customer_segment,
    p.plan_type,
    SUM(i.amount) AS total_invoice_amount,
    CASE
        WHEN SUM(i.amount) > 10000 AND c.country = 'BR' THEN 'enterprise_br'
        WHEN p.plan_type = 'trial' AND COUNT(e.event_id) > 5 THEN 'activated_trial'
        ELSE 'other'
    END AS strategic_customer_bucket
FROM {{ source('stripe', 'orders') }} AS o
JOIN {{ source('crm', 'customers') }} AS c
    ON o.customer_id = c.customer_id
JOIN {{ source('billing', 'plans') }} AS p
    ON c.plan_id = p.plan_id
LEFT JOIN {{ source('billing', 'invoices') }} AS i
    ON o.order_id = i.order_id
LEFT JOIN {{ source('product', 'events') }} AS e
    ON c.customer_id = e.customer_id
GROUP BY
    o.id,
    c.customer_segment,
    p.plan_type,
    c.country
```

This is not staging.

This is a business transformation wearing a staging hat.

Staging should reduce source chaos.

It should not become the place where revenue, segmentation, activation, and customer strategy all hold hands in a 300-line query.

When staging becomes too smart, downstream layers inherit confusion.

A good staging layer says:

> "Here is the source, cleaned and standardized."

It should not say:

> "Here is the company's entire business model in a trench coat."

---

## 4. The Third Symptom: Marts Depend on Marts Without Rules

A mart is usually a consumer-facing model.

Examples:

* `fct_orders`;
* `dim_customers`;
* `mart_daily_revenue`;
* `mart_customer_health`;
* `mart_marketing_attribution`;
* `mart_product_usage`.

Marts are often used by dashboards, reports, reverse ETL, ML features, or analysts.

Sometimes it is okay for one mart to depend on another.

But when this happens casually, you can create hidden coupling.

Example:

```text
mart_customer_health
    depends on mart_daily_revenue
        depends on mart_orders
            depends on mart_customer_health_old
```

This kind of structure can create circular semantics.

Revenue depends on customer health.
Customer health depends on revenue.
Everyone depends on a model named `old`.

This is where the DAG begins whispering.

A safer pattern is to separate reusable business foundations from serving marts.

Example:

```text
intermediate reusable models:
    int_orders_enriched
    int_customer_activity_daily
    int_invoice_status

core dimensional models:
    dim_customers
    fct_orders
    fct_invoices

serving marts:
    mart_daily_revenue
    mart_customer_health
    mart_marketing_attribution
```

Marts can share intermediate or core models.

But mart-to-mart dependencies should be intentional and documented.

A good rule:

> If a mart becomes a dependency for many other models, it may not be just a mart anymore. It may be a core data product and deserves stronger ownership, tests, and documentation.

Names should reflect responsibility.

If your "dashboard helper" model becomes the canonical revenue source, rename it, document it, and treat it like production infrastructure.

Do not let critical business logic live under a name that sounds temporary.

Temporary names are where permanent pain grows.

---

## 5. The Fourth Symptom: Business Logic Is Duplicated Everywhere

One of the most common dbt spaghetti problems is duplicated logic.

Example:

```sql
CASE
    WHEN status IN ('paid', 'settled') THEN 'completed'
    WHEN status IN ('cancelled', 'refunded') THEN 'lost'
    ELSE 'open'
END AS order_state
```

This appears in one model.

Then another.

Then a dashboard model.

Then a feature table.

Then a reverse ETL model.

Then someone changes the logic in one place but not the others.

Now different teams have different definitions of `order_state`.

The company enters semantic jazz.

Duplicated business logic creates:

* inconsistent metrics;
* hard-to-debug dashboards;
* broken trust;
* slow refactoring;
* hidden dependencies;
* different answers to the same question.

A healthier pattern is to centralize canonical logic.

Example:

```sql
-- int_orders_with_state.sql
SELECT
    order_id,
    customer_id,
    order_date,
    amount,
    status,
    CASE
        WHEN status IN ('paid', 'settled') THEN 'completed'
        WHEN status IN ('cancelled', 'refunded') THEN 'lost'
        ELSE 'open'
    END AS order_state
FROM {{ ref('stg_orders') }}
```

Then downstream models reuse `int_orders_with_state`.

If logic is complex and reusable, it may deserve:

* a dedicated intermediate model;
* a macro;
* a semantic layer definition;
* a data contract;
* documentation;
* tests.

Do not copy-paste business definitions casually.

Copy-paste is fast.

Inconsistency is faster.

---

## 6. The Fifth Symptom: Model Names Stop Meaning Anything

Model names are part of the architecture.

When names become unclear, the project becomes harder to navigate.

Bad names:

```text
orders_new
orders_v2
orders_final
orders_final_fixed
orders_joined
orders_dashboard
orders_temp
customer_data
customer_data_new
customer_master_revised
```

These names reveal uncertainty.

What is final?
What is new?
New compared to when?
Is `orders_v2` production?
Is `orders_final_fixed` newer than `orders_final_v2`?
Why is there a `temp` model from 2023?

Names should communicate:

* domain;
* entity;
* layer;
* grain;
* purpose;
* source when relevant.

Examples:

```text
stg_stripe__orders
stg_salesforce__accounts
int_orders_with_refunds
int_customer_activity_daily
dim_customers
fct_orders
mart_daily_revenue
mart_customer_health_daily
```

These are not perfect, but they tell a story.

A useful naming convention might include:

* `stg_` for staging;
* `int_` for intermediate transformations;
* `dim_` for dimensions;
* `fct_` for facts;
* `mart_` for serving marts;
* source prefix for staging models;
* grain suffix when helpful, such as `_daily`, `_monthly`, `_by_customer`.

Example:

```text
stg_<source>__<entity>
int_<entity>_<transformation>
dim_<entity>
fct_<event_or_process>
mart_<business_process>_<grain>
```

Naming cannot fix bad architecture.

But bad naming can hide good architecture.

And if the project is already messy, unclear names make cleanup much harder.

Names are signs in the city.

A city with bad signs becomes a labyrinth.

Then someone builds a shortcut through the accounting department.

---

## 7. The Sixth Symptom: The Grain Is Unclear

Grain means:

> What does one row represent?

This is one of the most important questions in data modeling.

For every model, you should be able to say:

* one row per order;
* one row per customer;
* one row per customer per day;
* one row per account per month;
* one row per event;
* one row per invoice line;
* one row per patient encounter;
* one row per sample per variant.

If the grain is unclear, joins become dangerous.

Example:

```text
orders_enriched
```

What is one row?

* one order?
* one order item?
* one order per customer?
* one order per payment?
* one order per day?
* one order joined to multiple events?

If a model has duplicate rows relative to its assumed key, downstream metrics inflate.

Example:

```sql
SELECT
    customer_id,
    SUM(order_amount) AS total_revenue
FROM {{ ref('orders_enriched') }}
GROUP BY customer_id;
```

If `orders_enriched` has one row per order item, not one row per order, revenue may be duplicated.

This is a classic problem.

Every important dbt model should document:

* grain;
* primary key;
* expected uniqueness;
* allowed nulls;
* source of truth status;
* known caveats.

Example YAML:

```yaml
models:
  - name: fct_orders
    description: One row per completed order.
    columns:
      - name: order_id
        description: Unique identifier for an order.
        tests:
          - unique
          - not_null
```

But documentation alone is not enough.

Test the grain.

If one row should equal one order, test uniqueness of `order_id`.

If one row should equal one customer per day, test uniqueness of `(customer_id, snapshot_date)`.

Grain is not a paragraph.

It is a contract.

---

## 8. The Seventh Symptom: Too Many Models Exist Only for One Dashboard

Dashboard-specific models are sometimes useful.

But if your dbt project becomes a dashboard factory, the modeling layer may be weak.

Bad pattern:

```text
dashboard_sales_overview_model
dashboard_sales_overview_model_v2
dashboard_finance_revenue_chart
dashboard_finance_revenue_chart_fixed
dashboard_ceo_metric_cards
```

These models often encode business logic that should live in reusable marts or semantic definitions.

Dashboard models should usually be thin.

Better pattern:

```text
fct_orders
fct_payments
dim_customers
mart_daily_revenue
mart_customer_growth

dashboard:
    queries mart_daily_revenue and mart_customer_growth
```

If every dashboard needs a custom dbt model, ask:

* Are marts too raw?
* Are metrics not standardized?
* Are dimensions missing?
* Are dashboard tools being used as modeling layers?
* Are analysts compensating for poor data products?
* Are semantic definitions unclear?

Sometimes dashboard-specific models exist because users cannot get the data they need from curated layers.

That is product feedback.

The answer is not "ban dashboard models."

The answer is to identify repeated dashboard logic and promote it upstream into proper models.

A dashboard model used by one dashboard is fine.

A dashboard model copied into seven dashboards is a data product trying to be born.

Help it.

Name it.

Test it.

Document it.

Raise it well.

---

## 9. The Eighth Symptom: Tests Exist, But They Do Not Protect You

dbt makes tests easy to define.

But easy tests are not necessarily meaningful tests.

Common weak testing pattern:

```yaml
columns:
  - name: id
    tests:
      - not_null
```

That is better than nothing.

But many projects stop there.

A mature dbt project should test important assumptions:

* primary-key uniqueness;
* not-null constraints;
* accepted values;
* referential integrity;
* freshness;
* row-count anomalies;
* value ranges;
* relationships between fields;
* business rules;
* metric sanity;
* grain consistency;
* source availability;
* schema expectations.

Example:

```yaml
models:
  - name: fct_orders
    description: One row per order.
    columns:
      - name: order_id
        tests:
          - unique
          - not_null

      - name: order_status
        tests:
          - accepted_values:
              values:
                - pending
                - paid
                - cancelled
                - refunded

      - name: customer_id
        tests:
          - not_null
          - relationships:
              to: ref('dim_customers')
              field: customer_id
```

But even this is not enough for important metrics.

You may need custom tests:

```sql
-- test_no_negative_revenue.sql
SELECT
    order_id,
    revenue
FROM {{ ref('fct_orders') }}
WHERE revenue < 0
  AND order_status != 'refunded'
```

Or anomaly checks:

```sql
SELECT
    order_date,
    COUNT(*) AS n_orders
FROM {{ ref('fct_orders') }}
GROUP BY order_date
HAVING COUNT(*) < 100
```

Tests should match the risk.

If a model feeds executive revenue reporting, it needs more than `not_null`.

A green dbt run with weak tests is not a guarantee.

It is a polite suggestion.

---

## 10. The Ninth Symptom: Sources Are Not Treated as Contracts

Sources are not just raw inputs.

They are boundaries between upstream systems and your dbt project.

If sources are not defined clearly, everything downstream is fragile.

A good source definition includes:

* source name;
* table name;
* owner;
* freshness;
* loaded timestamp;
* descriptions;
* column expectations;
* source-specific caveats.

Example:

```yaml
sources:
  - name: stripe
    database: raw
    schema: stripe
    tables:
      - name: payments
        loaded_at_field: _loaded_at
        freshness:
          warn_after:
            count: 2
            period: hour
          error_after:
            count: 6
            period: hour
        columns:
          - name: id
            description: Stripe payment identifier.
          - name: amount
            description: Payment amount in cents.
```

That `amount in cents` detail matters.

Without it, someone will eventually divide or not divide by 100 incorrectly.

Then Finance will summon everyone.

Sources should also be monitored.

If a source is stale, downstream data may be stale even if dbt models build successfully.

A dbt project can produce fresh tables from stale sources.

That is a very elegant way to be wrong.

Fresh transformation does not imply fresh data.

Source freshness matters.

---

## 11. The Tenth Symptom: Macros Become a Secret Language

Macros are powerful.

They help reuse logic.

But macros can also become a hidden layer of complexity.

Good macro use:

* repeated SQL patterns;
* standard date spine generation;
* reusable surrogate keys;
* common safe casts;
* standardized test logic;
* warehouse-specific abstraction;
* consistent metadata fields.

Bad macro use:

* hiding complex business logic;
* making SQL unreadable;
* creating magical side effects;
* over-abstracting simple queries;
* using macros when a model would be clearer;
* undocumented macro behavior;
* macros that change depending on environment in surprising ways.

Example useful macro:

```sql
{{ generate_surrogate_key(['customer_id', 'order_date']) }}
```

Example suspicious macro:

```sql
{{ calculate_revenue_everything(customer_id, order_date, true, false, 'legacy') }}
```

What does that do?

Nobody knows.

The macro knows.

The macro will not speak.

A macro should make common logic clearer, not more mysterious.

If a macro contains business-critical logic, document it and test it.

If a macro requires five boolean arguments, consider whether it should be several clearer macros or a model.

Boolean flags in macros are tiny fog machines.

---

## 12. The Eleventh Symptom: Incremental Models Are Treated as Magic

Incremental models are useful.

They can reduce compute cost and build time by processing only new or changed data.

But incremental models are also a common source of subtle bugs.

Example:

```sql
SELECT
    order_id,
    customer_id,
    order_date,
    amount,
    updated_at
FROM {{ ref('stg_orders') }}

{% if is_incremental() %}
WHERE updated_at > (
    SELECT MAX(updated_at)
    FROM {{ this }}
)
{% endif %}
```

This looks reasonable.

But it can fail if:

* late-arriving records have old `updated_at`;
* previous run partially failed;
* records are deleted upstream;
* updates arrive out of order;
* timestamps are not unique;
* business logic changes historically;
* schema changes require full refresh;
* the model depends on another model that changed historically.

Incremental models need clear rules:

* What is the unique key?
* What is the update timestamp?
* Are late-arriving records expected?
* Is there a lookback window?
* When is full refresh required?
* Are deletes handled?
* Is the model idempotent?
* Are schema changes handled?

Safer pattern with a lookback:

```sql
{% if is_incremental() %}
WHERE updated_at >= (
    SELECT DATEADD(day, -3, MAX(updated_at))
    FROM {{ this }}
)
{% endif %}
```

This reprocesses a small recent window to catch late updates.

But the window must match source behavior.

Incremental models are not magic.

They are stateful transformations.

Stateful transformations require discipline.

Otherwise, they become wrong slowly.

Slow wrong is the worst wrong because it has time to become trusted.

---

## 13. The Twelfth Symptom: Full Refresh Is Terrifying

A healthy dbt model should usually be rebuildable.

Not always cheaply.

But conceptually.

If nobody can run `full-refresh` because it would break the world, that is a warning sign.

Reasons full refresh becomes scary:

* models are not idempotent;
* sources are no longer available;
* historical logic depends on current state;
* incremental models accumulated unreproducible changes;
* old schemas are incompatible;
* downstream consumers cannot handle restatements;
* compute cost is unknown;
* build order is fragile;
* tests are weak;
* nobody knows what will change.

A rebuildable project is more trustworthy.

Backfills, bug fixes, migrations, and schema changes all depend on rebuildability.

A good question:

> If we had to rebuild this model from scratch, could we?

If the answer is no, ask why.

Sometimes the answer is legitimate.

Maybe raw data retention expired.

Maybe the source does not provide history.

Maybe cost is too high.

But then this limitation should be documented.

A model that cannot be rebuilt should not pretend to be fully reproducible.

Data honesty is underrated.

---

## 14. The Thirteenth Symptom: The Project Has No Domain Boundaries

As dbt projects grow, domain boundaries matter.

Without boundaries, every model lives in one giant conceptual bucket.

Example messy project:

```text
models/
    staging/
    intermediate/
    marts/
```

This may work for small teams.

But at scale, you may need domain structure:

```text
models/
    finance/
        staging/
        intermediate/
        marts/

    product/
        staging/
        intermediate/
        marts/

    customer/
        staging/
        intermediate/
        marts/

    marketing/
        staging/
        intermediate/
        marts/
```

Or another structure depending on your organization.

Domain boundaries help clarify:

* ownership;
* business definitions;
* model purpose;
* consumer expectations;
* access control;
* documentation;
* review responsibility.

But domain boundaries should not create duplication.

If every domain defines `customer` differently, the project becomes semantically fragmented.

You may need shared core models:

```text
models/
    core/
        dim_customers
        dim_accounts
        fct_orders

    finance/
        marts/

    marketing/
        marts/

    product/
        marts/
```

The right structure depends on team size, data domains, and ownership model.

The principle:

> Organize models around ownership and business meaning, not only technical layer.

A dbt project is not just a folder tree.

It is a map of how the organization understands data.

If the map is wrong, people get lost.

Then they build shortcuts.

Then the shortcuts become production.

Then the monster eats the map.

---

## 15. The Four-Layer Model That Usually Helps

Many dbt projects benefit from a clear layered architecture.

One common pattern:

```text
sources
    ↓
staging
    ↓
intermediate
    ↓
marts
```

Let's define them carefully.

### Sources

Raw upstream tables or external inputs.

They are not transformed by dbt, but defined and documented.

Purpose:

* declare raw inputs;
* track freshness;
* document upstream ownership;
* provide lineage boundary.

### Staging

One-to-one or near-one-to-one cleaned models over sources.

Purpose:

* standardize names;
* cast types;
* normalize simple values;
* expose source data in a consistent way;
* avoid complex joins;
* preserve source grain.

### Intermediate

Reusable transformation models.

Purpose:

* combine staging models;
* implement business logic;
* calculate reusable concepts;
* prepare facts and dimensions;
* reduce duplication.

### Marts

Consumer-facing models.

Purpose:

* serve dashboards, reports, ML, reverse ETL, and analytics;
* expose clear grain and semantics;
* provide stable data products.

Example:

```text
source('stripe', 'payments')
    ↓
stg_stripe__payments
    ↓
int_payments_with_refunds
    ↓
fct_payments
    ↓
mart_daily_revenue
```

This structure is not sacred.

But it is useful.

The key is that each layer has a job.

When layers lose purpose, spaghetti begins.

A staging model should not become a mart.

A mart should not become a staging layer for another random mart.

Architecture is partly saying no to convenient shortcuts.

---

## 16. Refactoring Step One: Draw the DAG Like a Human

Before fixing the project, understand it.

dbt can show lineage, but large DAGs can be overwhelming.

You need human-scale maps.

Start by identifying:

* key sources;
* key marts;
* critical business metrics;
* high-dependency models;
* long-running models;
* models with many downstream consumers;
* models with no consumers;
* deprecated models;
* models with unclear ownership;
* models with weak tests.

Create a simplified map:

```text
raw.orders
    ↓
stg_orders
    ↓
int_orders_enriched
    ↓
fct_orders
    ↓
mart_daily_revenue
    ↓
finance_dashboard
```

Then map the messy areas.

Ask:

* Why does this model exist?
* Who uses it?
* What is its grain?
* What business logic does it contain?
* Can it be merged, deleted, or promoted?
* Does it violate layer boundaries?
* Does it duplicate logic?
* Does it need tests?
* Is it actually production?

Do not start refactoring by moving files.

Start by understanding dependencies.

Otherwise, you are just rearranging noodles.

Neater noodles, maybe.

Still noodles.

---

## 17. Refactoring Step Two: Identify Critical Paths

Not all models are equally important.

Some models are experimental.

Some feed executive dashboards.

Some feed reverse ETL.

Some feed ML features.

Some are unused.

Refactoring should prioritize critical paths.

A critical path might be:

```text
source('billing', 'invoices')
    ↓
stg_billing__invoices
    ↓
int_invoices_with_status
    ↓
fct_invoices
    ↓
mart_monthly_recurring_revenue
    ↓
finance_dashboard
```

For each critical path, document:

* owner;
* business purpose;
* grain;
* primary keys;
* freshness needs;
* tests;
* downstream consumers;
* known issues;
* refactoring risk.

Critical paths deserve stronger guarantees.

Examples:

* revenue;
* customer identity;
* subscription status;
* product usage;
* clinical cohorts;
* claims facts;
* experiment metrics;
* feature tables;
* operational syncs.

Do not spend three weeks cleaning unused models while revenue logic remains duplicated in seven places.

Refactoring is product work.

Prioritize by impact and risk.

---

## 18. Refactoring Step Three: Delete or Archive Dead Models

Dead models are models nobody uses.

They create confusion.

They slow builds.

They pollute lineage.

They scare new engineers.

But deletion should be careful.

Steps:

1. identify models with no downstream dependencies;
2. check query logs if possible;
3. check dashboard usage;
4. ask owners;
5. mark as deprecated;
6. wait a defined window;
7. delete or archive.

Example deprecation note:

```yaml
models:
  - name: mart_daily_revenue_old
    description: Deprecated. Use mart_daily_revenue instead.
    meta:
      status: deprecated
      replacement: mart_daily_revenue
      removal_date: 2026-12-31
```

Dead model cleanup is not glamorous.

But it makes the project easier to reason about.

A dbt project with too many dead models becomes a haunted house.

Every room might matter.

Most do not.

But nobody knows which.

So everyone tiptoes.

---

## 19. Refactoring Step Four: Promote Reused Logic

Find repeated SQL logic.

Common repeated logic:

* revenue definitions;
* customer status;
* active user definitions;
* order state;
* plan normalization;
* country normalization;
* time zone conversion;
* refund handling;
* deleted-record filtering;
* event classification;
* identity mapping.

If repeated logic appears in multiple models, promote it.

Options:

### Intermediate model

Best when logic produces a reusable relation.

```text
int_orders_with_state
int_customers_with_lifecycle
int_events_classified
```

### Macro

Best when logic is expression-like and reused across models.

```sql
{{ normalize_country_code('country') }}
```

### Seed/reference table

Best when logic is mapping data.

```text
seed_status_mapping
seed_country_mapping
```

### Semantic layer metric

Best when logic defines a metric.

```text
gross_revenue
net_revenue
active_customers
```

Example using a mapping table instead of repeated CASE statements:

```sql
SELECT
    o.order_id,
    o.status,
    m.order_state
FROM {{ ref('stg_orders') }} AS o
LEFT JOIN {{ ref('seed_order_status_mapping') }} AS m
    ON o.status = m.raw_status
```

This is often easier to maintain than a giant CASE block in seven models.

When business logic changes, update one place.

The goal is not abstraction for its own sake.

The goal is one definition, many consumers.

That is how trust begins.

---

## 20. Refactoring Step Five: Make Grain Explicit

For important models, document and test grain.

Example model documentation:

```yaml
models:
  - name: fct_orders
    description: One row per order.
    columns:
      - name: order_id
        description: Primary key. Unique order identifier.
        tests:
          - unique
          - not_null

      - name: customer_id
        description: Customer who placed the order.
        tests:
          - not_null
```

For compound grain:

```yaml
models:
  - name: mart_customer_activity_daily
    description: One row per customer per activity date.
    tests:
      - dbt_utils.unique_combination_of_columns:
          combination_of_columns:
            - customer_id
            - activity_date
```

A model without a known grain is dangerous.

It can still be useful for exploration.

But it should not become a production data product.

If a model feeds dashboards or downstream transformations, grain must be explicit.

Grain is the difference between:

> "This table is useful."

and:

> "This table multiplies revenue by 3 when joined to invoices."

That is a meaningful difference.

Finance tends to notice.

---

## 21. Refactoring Step Six: Separate Business Logic From Presentation Logic

dbt models should not become dashboard layout engines.

Business logic and presentation logic should be separated.

Business logic:

* revenue calculation;
* customer segment;
* lifecycle status;
* churn risk bucket;
* product activation;
* refund handling;
* order state.

Presentation logic:

* dashboard labels;
* chart grouping;
* display ordering;
* filter-specific formatting;
* UI-specific fields.

Bad pattern:

```sql
SELECT
    customer_id,
    CASE
        WHEN revenue > 10000 THEN '🔥 Enterprise'
        WHEN revenue > 1000 THEN '⭐ Growth'
        ELSE 'Small'
    END AS dashboard_customer_label
FROM {{ ref('mart_customer_revenue') }}
```

Maybe fine for a dashboard-specific model.

But not for a core mart.

Core models should expose stable business fields:

```sql
SELECT
    customer_id,
    revenue,
    customer_segment
FROM {{ ref('mart_customer_revenue') }}
```

The dashboard can decorate.

Or a thin presentation model can decorate.

Do not contaminate canonical models with UI-specific logic unless that logic is truly part of the business definition.

Otherwise, your data mart starts wearing emoji to meetings.

Charming, but questionable.

---

## 22. Refactoring Step Seven: Split Giant Models

A 500-line SQL model is not automatically bad.

But it is a smell.

Giant models often contain multiple conceptual steps:

* clean source fields;
* join dimensions;
* compute business statuses;
* aggregate metrics;
* apply filters;
* deduplicate records;
* handle exceptions;
* format output.

Splitting can improve readability and testing.

Example giant model flow:

```text
raw orders
    ↓
deduplicate orders
    ↓
join customers
    ↓
join payments
    ↓
calculate refund status
    ↓
calculate revenue
    ↓
aggregate daily
```

Instead of one huge model, use steps:

```text
stg_orders
int_orders_deduplicated
int_orders_with_customer
int_orders_with_payment_status
fct_orders
mart_daily_revenue
```

Each model has a clear purpose.

But do not split excessively.

Too many tiny models can also create confusion.

The goal is not maximum fragmentation.

The goal is conceptual clarity.

A model should be small enough to understand and large enough to represent a meaningful transformation.

Like a paragraph.

Not a novel.

Not a fortune cookie.

---

## 23. Refactoring Step Eight: Fix Materializations

dbt lets models be materialized as views, tables, incremental models, ephemeral models, and sometimes more depending on adapter.

Bad materialization choices cause performance and maintainability problems.

### Views

Good for lightweight transformations.

Risk:

* repeated computation;
* slow dashboards;
* dependency chains of views can become expensive.

### Tables

Good for stable, reused, expensive transformations.

Risk:

* storage cost;
* refresh time.

### Incremental models

Good for large append/update datasets.

Risk:

* state bugs;
* late-arriving data;
* full-refresh complexity.

### Ephemeral models

Good for simple reusable logic inlined into downstream SQL.

Risk:

* hard-to-debug compiled SQL;
* repeated computation;
* overly complex downstream queries.

A common dbt spaghetti issue:

> Everything is a view until queries become slow, then everything becomes a table, then builds become slow, then someone makes it incremental, then nobody can full-refresh it.

Materialization should be chosen based on:

* model size;
* reuse;
* query frequency;
* build cost;
* freshness needs;
* downstream consumers;
* rebuildability;
* late-arriving data;
* storage cost.

Example guidance:

```text
staging:
    views or tables depending on source size and reuse

intermediate:
    views for light logic
    tables for expensive/reused logic

facts/marts:
    tables or incremental models

dashboard-specific:
    tables if performance-critical
    views if lightweight
```

Materialization is part of architecture.

Not an afterthought.

The warehouse bill agrees.

---

## 24. Refactoring Step Nine: Add Exposures for Real Consumers

dbt exposures let you document downstream consumers such as dashboards, notebooks, applications, or ML jobs.

This helps answer:

* What depends on this model?
* Who owns the downstream asset?
* Which models support critical reporting?
* What breaks if this model changes?
* Which dashboards use deprecated models?

Example:

```yaml
exposures:
  - name: finance_revenue_dashboard
    type: dashboard
    maturity: high
    url: https://bi.example.com/dashboards/revenue
    depends_on:
      - ref('mart_daily_revenue')
    owner:
      name: Finance Analytics
      email: finance-analytics@example.com
```

Exposures make invisible consumers visible.

This is extremely helpful for refactoring.

Without exposures or lineage, you do not know what matters.

With exposures, you can prioritize and communicate.

A model feeding one abandoned dashboard is different from a model feeding the CEO dashboard.

Both are tables.

Only one can ruin your morning.

---

## 25. Refactoring Step Ten: Use Contracts Where They Matter

dbt model contracts can help enforce column names and types.

This is especially valuable for production-facing models.

A contract says:

> This model promises to produce this schema.

Example:

```yaml
models:
  - name: mart_daily_revenue
    config:
      contract:
        enforced: true
    columns:
      - name: revenue_date
        data_type: date
      - name: gross_revenue
        data_type: numeric
      - name: net_revenue
        data_type: numeric
```

Contracts are useful for:

* marts;
* facts;
* dimensions;
* reverse ETL source models;
* ML feature tables;
* external exports;
* cross-team data products.

Contracts may be too heavy for early exploratory models.

That is fine.

Use strictness where the risk justifies it.

Not every model needs a formal contract.

But models that other people depend on should not change shape casually.

A production mart is an interface.

Interfaces need promises.

Otherwise, consumers are just hoping.

Hope is not a schema strategy.

---

## 26. Refactoring Step Eleven: Introduce Ownership

Every important model should have an owner.

Ownership means someone is responsible for:

* correctness;
* documentation;
* freshness;
* tests;
* incident response;
* schema changes;
* deprecation;
* consumer communication.

Ownership can be represented in metadata:

```yaml
models:
  - name: mart_customer_health_daily
    description: Daily customer health scoring table.
    meta:
      owner: customer-data-platform
      business_owner: customer-success-ops
      slack_channel: "#data-customer-health"
      status: production
```

Ownership helps with:

* support;
* refactoring;
* incidents;
* access requests;
* schema changes;
* roadmap decisions.

A model without an owner is not a shared asset.

It is abandoned infrastructure.

Abandoned infrastructure is how ghosts enter the DAG.

---

## 27. Refactoring Step Twelve: Create a Style Guide

A dbt style guide reduces arguments and improves consistency.

It should cover:

* model naming;
* folder structure;
* SQL formatting;
* CTE naming;
* source naming;
* column naming;
* materialization rules;
* testing expectations;
* documentation expectations;
* macro usage;
* incremental model patterns;
* deprecation process.

Example CTE style:

```sql
WITH source AS (

    SELECT *
    FROM {{ ref('stg_orders') }}

),

renamed AS (

    SELECT
        order_id,
        customer_id,
        order_date,
        amount
    FROM source

),

final AS (

    SELECT *
    FROM renamed

)

SELECT *
FROM final
```

Some people dislike this style.

That is okay.

The specific style matters less than consistency.

A style guide prevents every model from feeling like it was written by a different civilization.

Because sometimes it was.

But still.

---

## 28. Refactoring Step Thirteen: Review Pull Requests for Architecture, Not Just Syntax

dbt pull requests should not only ask:

* Does the SQL run?
* Are tests passing?
* Is formatting okay?

They should also ask:

* Does this model belong in this layer?
* Is the grain clear?
* Is business logic duplicated?
* Are tests meaningful?
* Is the materialization appropriate?
* Does this create mart-to-mart coupling?
* Does it use `SELECT *` across a boundary?
* Are source assumptions documented?
* Is ownership clear?
* Are downstream consumers affected?
* Is this model reusable or dashboard-specific?
* Will this be maintainable in six months?

PR review is where architecture is protected.

If every PR is approved because "it works," the project will slowly become unworkable.

A dbt project does not become spaghetti in one dramatic commit.

It becomes spaghetti one reasonable shortcut at a time.

Every shortcut has a story.

Architecture is what remembers the pattern.

---

## 29. Refactoring Step Fourteen: Use CI Properly

CI should protect the project.

Useful CI checks include:

* SQL compilation;
* model selection builds;
* unit tests where available;
* data tests on changed models;
* schema contract checks;
* SQL linting;
* naming conventions;
* documentation checks;
* dependency checks;
* exposure impact;
* detection of unexpected full-refresh needs;
* model owner requirement.

Example conceptual CI output:

```text
Changed models:
    int_orders_with_state
    mart_daily_revenue

Downstream affected:
    finance_revenue_dashboard
    monthly_board_report

Tests:
    fct_orders.unique_order_id: passed
    mart_daily_revenue.no_negative_net_revenue: failed

Status:
    blocked
```

CI should give useful feedback.

Not just:

```text
dbt build failed.
```

A good CI pipeline teaches users how to fix problems.

Bad CI produces riddles.

Riddles are fun in literature.

Less fun when deploying revenue logic.

---

## 30. dbt Spaghetti in Healthcare and Biotech

Healthcare and biotech dbt projects can become especially tangled because domain logic is complex.

Common data sources:

* EHR tables;
* claims data;
* laboratory results;
* registries;
* genomic metadata;
* clinical trial data;
* sample tracking systems;
* public health datasets;
* operational hospital data.

Common modeling challenges:

* patient identity resolution;
* encounter-level vs patient-level grain;
* longitudinal windows;
* diagnosis/procedure code systems;
* lab units;
* phenotype definitions;
* cohort inclusion/exclusion criteria;
* claims adjustment;
* genomic reference builds;
* sample-to-patient mapping;
* consent and governance restrictions.

A seemingly simple model name like:

```text
mart_patient_cohort
```

may hide many assumptions:

* Which patients?
* Which time period?
* Which phenotype definition?
* Which code system?
* Which data sources?
* Which exclusions?
* Which consent rules?
* Which lab thresholds?
* Which encounter types?
* Which version?

In biomedical contexts, dbt spaghetti is not just annoying.

It can affect scientific reproducibility.

A phenotype definition duplicated across models can lead to inconsistent cohorts.

A lab unit conversion hidden in a staging model can alter downstream analyses.

A genomic build mismatch can invalidate variant joins.

A patient-level model accidentally joined to encounter-level data can inflate counts.

For healthcare and biotech dbt projects, make these especially explicit:

* grain;
* code systems;
* units;
* reference builds;
* cohort definitions;
* phenotype versions;
* source provenance;
* consent restrictions;
* release versions;
* data quality assumptions.

A biomedical dbt model should be boringly clear.

Science already has enough uncertainty.

The SQL should not add mystery.

---

## 31. A Small Python Sketch: Model Metadata Audit

Below is a small teaching sketch showing how one might audit model metadata outside dbt.

This is not production code. It is a conceptual example.

```python
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class ModelLayer(StrEnum):
    """Logical layer of a dbt model."""

    STAGING = "staging"
    INTERMEDIATE = "intermediate"
    MART = "mart"


@dataclass(frozen=True)
class ModelMetadata:
    """Minimal metadata for auditing a dbt model.

    Parameters
    ----------
    name
        Model name.
    layer
        Logical model layer.
    owner
        Owning team or person.
    has_description
        Whether the model has a useful description.
    has_tests
        Whether the model has at least one test.
    downstream_count
        Number of known downstream dependencies.
    """

    name: str
    layer: ModelLayer
    owner: str | None
    has_description: bool
    has_tests: bool
    downstream_count: int


def find_high_risk_models(
    models: tuple[ModelMetadata, ...],
) -> list[ModelMetadata]:
    """Find models that are important but weakly governed.

    Parameters
    ----------
    models
        Collection of dbt model metadata.

    Returns
    -------
    list[ModelMetadata]
        Models with downstream usage but missing ownership, tests, or docs.
    """
    high_risk: list[ModelMetadata] = []

    for model in models:
        is_used_downstream = model.downstream_count > 0
        lacks_governance = (
            model.owner is None
            or not model.has_description
            or not model.has_tests
        )

        if is_used_downstream and lacks_governance:
            high_risk.append(model)

    return high_risk
```

The principle is simple:

> Important models with weak metadata are risk hotspots.

A dbt project should make risk visible.

If a model has 40 downstream dependencies and no owner, that is not a model.

That is a future incident with a table name.

---

## 32. A Practical dbt Project Health Checklist

Ask these questions.

### Structure

1. Are model layers clearly defined?
2. Do dependencies flow in the expected direction?
3. Are staging models simple?
4. Are marts consumer-facing and stable?
5. Are domain boundaries clear?

### Naming

6. Do model names communicate purpose?
7. Are temporary names removed or deprecated?
8. Are versions used intentionally?

### Grain and semantics

9. Is the grain documented for important models?
10. Are primary keys tested?
11. Are business definitions centralized?
12. Are units and time zones documented?

### Testing

13. Do critical models have meaningful tests?
14. Are accepted values tested?
15. Are relationships tested?
16. Are custom business tests used where needed?

### Materialization

17. Are expensive models materialized appropriately?
18. Are incremental models safe and documented?
19. Can important models be full-refreshed or rebuilt?

### Ownership

20. Do production models have owners?
21. Are support channels visible?
22. Are deprecated models marked?

### Documentation

23. Are sources documented?
24. Are marts documented?
25. Do docs explain meaning, not just column names?

### Operations

26. Are source freshness checks used?
27. Are exposures defined?
28. Does CI catch meaningful problems?
29. Are build times reasonable?
30. Are high-cost models known?

### Governance

31. Are sensitive fields documented?
32. Are production models contract-aware?
33. Are schema changes coordinated?
34. Are downstream consumers visible?

If many answers are "no," the project may still work.

But it may not be maintainable.

Working and maintainable are different.

A chair can stand with three legs.

You may not want to sit on it during a board meeting.

---

## 33. How to Fix the Monster Without Freezing the Business

The biggest mistake in refactoring is trying to stop all work until the project is clean.

That rarely works.

The business keeps moving.

Instead, refactor incrementally.

### Step 1: Freeze only the worst patterns

For example:

* no new `SELECT *` in production marts;
* no new undocumented production models;
* no new mart-to-mart dependencies without review;
* no new models without owners.

### Step 2: Identify critical paths

Start with revenue, customer, product usage, or whatever matters most.

### Step 3: Improve tests and documentation first

Before moving models, make behavior visible.

### Step 4: Centralize duplicated logic

Pick one repeated definition and promote it.

### Step 5: Deprecate dead models

Remove confusion gradually.

### Step 6: Introduce conventions for new work

New models follow the clean architecture.

Old models are migrated over time.

### Step 7: Communicate changes

Refactoring can affect users.

Document migration paths.

The strategy is:

> Stop making the monster bigger, then slowly make it smaller.

This is less satisfying than a heroic rewrite.

It is also more likely to succeed.

Heroic rewrites are where teams go to rediscover all the weird edge cases the old system had already learned.

Respect old systems.

Then improve them carefully.

---

## 34. When a Rewrite Is Justified

Sometimes incremental refactoring is not enough.

A rewrite may be justified when:

* the current DAG is impossible to reason about;
* critical metrics are inconsistent;
* performance is unacceptable;
* ownership is absent;
* business logic is duplicated everywhere;
* source schemas changed fundamentally;
* new architecture is needed;
* data products cannot be trusted;
* compliance or audit requires stronger guarantees.

But rewrites need caution.

A successful rewrite should include:

* clear scope;
* old/new comparison;
* validation metrics;
* stakeholder alignment;
* migration plan;
* parallel run period;
* rollback plan;
* documentation;
* deprecation of old models.

Bad rewrite:

> "Let's rebuild everything properly."

Better rewrite:

> "We will rebuild the revenue modeling path from raw payments to `mart_daily_revenue`, compare old and new outputs for 12 months, validate differences with Finance, run dashboards in parallel for two weeks, then deprecate old models."

That is a plan.

The first one is a feeling.

Feelings can start projects.

They should not be the architecture.

---

## 35. Common Anti-Patterns

### Anti-pattern 1: Staging models with business logic

Staging should standardize sources, not encode half the company strategy.

### Anti-pattern 2: Mart-to-mart dependency chaos

Consumer-facing models become upstream dependencies without design.

### Anti-pattern 3: Duplicated CASE statements

Business definitions diverge quietly.

### Anti-pattern 4: Unclear grain

Nobody knows what one row means.

### Anti-pattern 5: Everything is incremental

Builds are faster until correctness becomes unknowable.

### Anti-pattern 6: No source freshness

Models build successfully from stale data.

### Anti-pattern 7: Tests that only check not-null IDs

Better than nothing, but insufficient for critical data products.

### Anti-pattern 8: Macros that hide business logic

Reusable does not mean understandable.

### Anti-pattern 9: No ownership

Models become abandoned dependencies.

### Anti-pattern 10: Never deleting old models

The project becomes a museum of outdated assumptions.

### Anti-pattern 11: Dashboard-specific models becoming canonical

A dashboard helper quietly becomes the source of truth.

### Anti-pattern 12: Refactoring without lineage

You change a model and discover consumers through panic.

This list is not meant to shame anyone.

Most dbt projects accumulate at least some of these.

The goal is to notice early.

Spaghetti is easier to untangle before it dries.

---

## 36. What Good Looks Like

A healthy dbt project usually has these traits.

### Clear layer semantics

Sources, staging, intermediate, and marts have distinct responsibilities.

### Intentional DAG flow

Dependencies move in understandable directions.

### Explicit grain

Important models document and test what one row means.

### Centralized business logic

Core definitions are reusable and not duplicated everywhere.

### Meaningful tests

Tests protect business assumptions, not only syntax.

### Good naming

Model names reveal layer, domain, entity, and purpose.

### Appropriate materializations

Views, tables, incremental models, and ephemeral models are used intentionally.

### Ownership

Production models have owners and support channels.

### Useful documentation

Docs explain meaning, caveats, freshness, and usage.

### Exposures and lineage

Important consumers are visible.

### CI/CD

Changes are tested before production.

### Deprecation process

Old models are removed safely.

### Refactoring discipline

The project improves continuously instead of waiting for collapse.

In short:

> A healthy dbt project is not one with the most models. It is one where the right models exist, mean clear things, and can be safely changed.

That is analytics engineering maturity.

---

## 37. A Practical Refactoring Checklist

When your dbt project feels tangled, ask:

1. Which models are business-critical?
2. Which models have the most downstream dependencies?
3. Which models are unused?
4. Which models have unclear ownership?
5. Which models have unclear grain?
6. Which models contain duplicated business logic?
7. Which staging models are doing too much?
8. Which marts depend on other marts?
9. Which models are slow or expensive?
10. Which incremental models cannot be safely full-refreshed?
11. Which models lack tests?
12. Which tests are too weak?
13. Which sources lack freshness checks?
14. Which dashboard models should become marts?
15. Which marts should become core facts or dimensions?
16. Which models should be deprecated?
17. Which macros are poorly understood?
18. Which definitions should move into reusable models?
19. Which domains need clearer folder ownership?
20. Which model names are misleading?
21. Which exposures are missing?
22. Which contracts should be enforced?
23. Which documentation pages are unhelpful?
24. Which repeated support questions reveal architecture problems?
25. Which new conventions should apply from today onward?

Do not try to fix everything at once.

Pick one critical path.

Make it cleaner.

Then the next.

That is how the monster loses tentacles.

One at a time.

---

## 38. dbt Is Not the Semantic Layer by Default

This is important.

dbt helps define transformations.

It can support metrics and semantic definitions depending on the ecosystem and setup.

But a pile of dbt models is not automatically a semantic layer.

A semantic layer should define consistent business concepts:

* active customer;
* net revenue;
* churned account;
* product-qualified lead;
* monthly recurring revenue;
* retained user;
* clinical cohort;
* claim allowed amount.

If these definitions are scattered across dbt models, dashboards, notebooks, and reverse ETL syncs, then the company does not have a semantic layer.

It has semantic confetti.

dbt can be part of the solution.

But you still need:

* canonical definitions;
* ownership;
* documentation;
* metric governance;
* consumer communication;
* consistency across tools.

A model named `mart_daily_revenue` is not enough.

You need to know:

* gross or net?
* refunded or not?
* tax included?
* currency normalized?
* timezone?
* recognition date?
* source systems?
* late-arriving corrections?
* restatement policy?

Data products need semantics.

Otherwise, everyone has numbers.

Nobody has agreement.

---

## 39. The Cultural Part: Do Not Reward Only Speed

dbt spaghetti often appears because teams reward fast delivery without enough architectural care.

A stakeholder asks for a metric.

A model is created quickly.

Then another.

Then another.

Each shortcut is understandable.

The project becomes messy gradually.

If the organization rewards only speed, maintainability loses.

A healthy culture values:

* reusable models;
* documentation;
* tests;
* code review;
* ownership;
* deprecation;
* refactoring;
* clear semantics;
* performance;
* consumer communication.

These are not "extra."

They are the work.

Shipping a dashboard quickly with inconsistent logic is not faster if the team spends three weeks later arguing about which number is correct.

Fast wrong is not fast.

It is debt with a demo.

The goal is not perfection.

The goal is sustainable delivery.

Good analytics engineering makes future work easier, not harder.

That is the standard.

---

## 40. Final Thought

Your dbt project turned into a spaghetti monster because success created complexity.

More users.
More models.
More metrics.
More dashboards.
More sources.
More exceptions.
More business logic.
More urgency.

That is normal.

The problem is not growth.

The problem is growth without architecture.

dbt gives you powerful tools:

* lineage;
* modular SQL;
* testing;
* documentation;
* macros;
* materializations;
* sources;
* exposures;
* contracts;
* CI integration.

But tools do not automatically create a maintainable project.

The team must define:

* layers;
* naming conventions;
* ownership;
* grain;
* tests;
* materialization strategy;
* business logic reuse;
* documentation expectations;
* refactoring habits;
* deprecation policies;
* review standards.

A healthy dbt project is one where a new engineer can answer:

> Where does this data come from?
> What does one row mean?
> Who owns this model?
> What depends on it?
> What tests protect it?
> Is it production-ready?
> Can I change it safely?

If those questions are impossible, the monster is already awake.

Do not panic.

Start with critical paths.

Make grain explicit.

Centralize duplicated logic.

Simplify staging.

Clarify marts.

Add meaningful tests.

Document ownership.

Deprecate dead models.

Review architecture in pull requests.

Refactor gradually.

The goal is not a perfect DAG.

The goal is a project that humans can understand, trust, and safely evolve.

Because analytics engineering is not just writing SQL that runs.

It is building a shared analytical system that can survive new questions, new data, new teammates, and new mistakes.

A dbt project should be a map.

Not a maze.

And definitely not a spaghetti monster with revenue logic in its teeth.
