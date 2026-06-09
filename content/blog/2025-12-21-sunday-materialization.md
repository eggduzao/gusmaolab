Title: The Sunday Materialization - Data Platform as a Product
Subtitle: Treating Your Internal Engineers as Customers, Not Captive Users of a Beautifully Complicated Maze
Date: 2025-12-21 07:00
Modified: 2025-12-21 07:00
Category: Sunday
Tags: data engineer, data platform engineer, data, data architecture, platform engineering, data platform, developer experience, internal tools, data products
Slug: sunday-materialization-data-platform-as-a-product
Authors: Eduardo G Gusmao
Summary: A weekly educational topic/lecture/discussion on Data Engineering topics that we all experienced at least once (or will!)
Status: final
Lang: en
Template: topic
Cadence: Biweekly
Scope: Data Engineering, Industry, Data Challenges
Tone: Analytical, Educational, Non-Sensational
Canonical: https://www.gusmaolab.org/blog/sunday-materialization-data-platform-as-a-product/
Meta_description: Biweekly analysis of important Data Engineering concepts.
Meta_keywords: data concepts, topics, lectures, discussions, data platform as product, platform engineering, developer experience
Cover: images/covers/data-platform-as-product.png
Thumbnail: images/thumbnails/data-platform-as-product-thumb.png

# Data Platform as a Product: Treating Your Internal Engineers as Customers

There is a strange thing that happens inside many organizations.

A company would never ship a customer-facing product without thinking about usability, onboarding, reliability, documentation, support, feedback, and adoption.

But the same company may happily ship an internal data platform that requires:

* tribal knowledge;
* undocumented conventions;
* mysterious permissions;
* unclear ownership;
* five Slack channels;
* a wiki last updated during the Bronze Age;
* a deployment process known only to three engineers and one retired contractor;
* a command-line tool that works if you run it from the correct directory under the correct moon.

Then, when internal users struggle, the platform team says:

> "They are using it wrong."

Maybe.

But also: maybe the platform was not designed as a product.

That is the core idea of **Data Platform as a Product**.

A data platform is not just infrastructure.

It is an internal product used by engineers, analysts, data scientists, analytics engineers, ML engineers, product teams, compliance teams, and business stakeholders.

If the platform is hard to use, people route around it.

They create shadow pipelines.
They export CSVs.
They duplicate tables.
They run notebooks manually.
They build unofficial dashboards.
They keep "temporary" scripts alive for three years.
They ask the same engineer for help every Thursday.
They form a small civilization around a spreadsheet.

And then leadership asks:

> "Why is our data ecosystem so fragmented?"

Because the official path was not usable enough.

A platform that nobody wants to use is not a platform.

It is a set of infrastructure components with good intentions.

The shift from "data platform as infrastructure" to "data platform as product" is a shift in responsibility:

> The platform team is not only responsible for making the platform exist. It is responsible for making the platform useful, understandable, reliable, and adoptable.

That is a much harder job.

It is also the real job.

---

## 1. What Does "Platform as a Product" Mean?

A product exists to solve user problems.

A data platform product exists to solve internal data problems repeatedly, safely, and at scale.

It provides reusable capabilities such as:

* data ingestion;
* workflow orchestration;
* transformation frameworks;
* data quality checks;
* metadata and cataloging;
* access control;
* storage standards;
* compute environments;
* deployment templates;
* observability;
* lineage;
* cost visibility;
* self-service datasets;
* feature generation;
* reverse ETL;
* sandbox environments;
* documentation and support.

But the product mindset changes the framing.

Without product thinking:

> "We built an Airflow cluster."

With product thinking:

> "We provide a reliable workflow orchestration service that lets teams schedule, monitor, retry, and backfill data pipelines safely, with clear templates, ownership, alerting, and support."

Without product thinking:

> "We have a data lake."

With product thinking:

> "We provide governed storage zones where teams can publish raw, staged, curated, and production-ready data products with clear contracts, retention policies, lineage, and access controls."

Without product thinking:

> "We support Spark."

With product thinking:

> "We provide standard Spark execution environments for batch processing, including packaging, dependency management, logging, resource profiles, cost tracking, and production deployment patterns."

The technology may be the same.

The responsibility is different.

A platform-as-product team does not stop at provisioning tools.

It asks:

> Can internal users successfully achieve their goals without heroic support?

If not, the product is incomplete.

---

## 2. Internal Users Are Still Users

A dangerous phrase:

> "Our customers are internal, so UX matters less."

No.

Internal users are still users.

They have limited time, different skill levels, competing priorities, and frustration thresholds. They may be smart, but smart people still suffer when the system is unnecessarily confusing.

Your internal users may include:

| User | What they need from the platform |
|---|---|
| Data engineers | Reliable ingestion, orchestration, deployment, observability |
| Analytics engineers | SQL transformations, testing, documentation, lineage, marts |
| Data scientists | Clean datasets, feature tables, notebooks, reproducible training data |
| ML engineers | Feature pipelines, model inputs, batch scoring, serving integrations |
| Backend engineers | Event schemas, APIs, CDC, operational data contracts |
| Analysts | Trusted tables, metrics, dashboards, semantic definitions |
| Product teams | Experiment data, usage metrics, behavioral funnels |
| Compliance teams | Auditability, access control, reproducible reports |
| Business stakeholders | Reliable numbers, freshness, explainability |

These users are not interchangeable.

A platform that works for senior data engineers may still fail analysts.

A platform that works for analysts may not support production ML.

A platform that works for batch pipelines may fail streaming use cases.

A platform that works for one domain team may not scale across the company.

Internal customers have segments.

Product thinking starts by understanding those segments.

Otherwise, the platform becomes a buffet where every dish is Kubernetes.

---

## 3. The Captive User Trap

Internal platforms often suffer from the **captive user trap**.

Because the users are internal, they may not be able to "leave" the product officially.

So adoption looks successful.

People use the platform because they have to.

But forced usage is not the same as product success.

Signs of captive-user failure:

* users constantly ask for help with the same tasks;
* teams create unofficial workarounds;
* onboarding takes weeks;
* people avoid deploying changes;
* users copy old pipelines instead of using templates;
* platform documentation is ignored or distrusted;
* every new project requires platform-team intervention;
* users complain privately but dashboards show "adoption";
* the platform team becomes a ticket factory;
* internal NPS would require emergency medical attention.

The platform may be mandatory.

But if people avoid it whenever possible, it is not healthy.

A good internal platform should make the correct path easier than the workaround.

That sentence matters.

Governance alone does not create adoption.

Usability creates adoption.

If the official path is painful, shadow systems become rational.

This is not user rebellion.

It is user survival.

---

## 4. The Platform Is a Product, Not a Project

A project has an end.

A product has a lifecycle.

Many data platforms are funded and managed like projects:

```text
Build platform
    ↓
Launch platform
    ↓
Declare success
    ↓
Move team to next initiative
```

This fails because platforms are never "done."

New users arrive.
New workloads appear.
New compliance rules emerge.
New tools are adopted.
Costs change.
Data volumes grow.
Pipelines break.
Schemas evolve.
Security requirements tighten.
Backfills happen.
Dashboards multiply.
ML teams ask for features.
Leadership asks for "real-time."
Someone discovers the old CRM export is still feeding a critical metric.

A platform needs continuous product management.

That means:

* roadmap;
* prioritization;
* user research;
* support model;
* product metrics;
* documentation;
* deprecation policy;
* adoption strategy;
* feedback loops;
* release notes;
* migration plans;
* reliability targets;
* cost management;
* governance updates.

A platform is not a one-time build.

It is an internal product that evolves with the organization.

Treating it as a project is how you get an impressive launch followed by years of slow decay.

Infrastructure decays quietly.

Then one day a dashboard takes 12 minutes to load and nobody knows who owns the table.

---

## 5. The Platform Team's Real Job

The platform team's job is not to own all data work.

That would not scale.

The platform team's job is to make data work easier, safer, faster, and more consistent for other teams.

A good platform team provides paved roads.

A paved road is an approved, documented, supported path for a common task.

Examples:

* creating a new ingestion pipeline;
* deploying a dbt model;
* publishing a curated table;
* scheduling a Spark job;
* adding a data quality check;
* requesting access to a dataset;
* running a backfill;
* creating a dashboard-ready mart;
* publishing an ML feature table;
* syncing data to a SaaS tool;
* monitoring freshness;
* handling schema changes.

A paved road should include:

* templates;
* defaults;
* documentation;
* examples;
* validation;
* observability;
* support;
* ownership model;
* security controls;
* cost guardrails.

The goal is not to remove flexibility.

The goal is to make common things easy and dangerous things explicit.

A platform without paved roads forces every team to become road construction workers.

That is inefficient.

Also, most people came to move data, not pour asphalt.

---

## 6. Self-Service Does Not Mean "No Support"

Many organizations say they want self-service data.

This is good.

But self-service is often misunderstood.

Bad self-service:

> "Here are the tools. Good luck."

Good self-service:

> "Here is a supported path that lets you complete the task safely without waiting on the platform team."

Self-service requires design.

It needs:

* clear entry points;
* permissions;
* templates;
* documentation;
* guardrails;
* examples;
* validation;
* error messages;
* observability;
* support escalation;
* ownership metadata;
* cost transparency.

For example, a self-service pipeline template might include:

```text
New pipeline template:
    config.yaml
    transformation.sql
    quality_checks.yaml
    deployment.yaml
    README.md
    owner metadata
    alert routing
    cost tags
    backfill parameters
```

This is self-service because a team can use it independently.

But it is not unsupported.

It is productized.

The platform team has encoded best practices into the path.

Self-service is not abandonment.

Self-service is support through design.

---

## 7. Developer Experience Is a Data Platform Feature

Developer experience, or DevEx, matters.

A data platform with poor developer experience creates slow teams.

Symptoms:

* hard local setup;
* unclear deployment;
* painful dependency management;
* confusing errors;
* slow test feedback;
* no templates;
* no environment parity;
* unclear logs;
* no reproducible examples;
* permission errors that require ritual interpretation;
* difficult rollback;
* fragile CI/CD;
* manual release steps;
* undocumented conventions.

A good developer experience answers:

* How do I start?
* How do I test?
* How do I deploy?
* How do I monitor?
* How do I debug?
* How do I backfill?
* How do I request access?
* How do I publish a table?
* How do I know if I broke something?
* How do I recover?

If users need to ask a senior platform engineer for every basic task, the platform has a product problem.

Documentation helps.

Templates help more.

Good defaults help even more.

Clear errors are gold.

For example, this error is bad:

```text
AccessDeniedException: Access denied.
```

This is better:

```text
Access denied for table mart.customer_360.

Reason:
    Your compute role analytics-dev-reader does not have access to data class PII.

How to request access:
    Submit access request with business justification:
    internal-data-access/customer-360

Owner:
    customer-data-platform
```

Same failure.

Different experience.

One creates confusion.

The other creates a path.

That is product design.

---

## 8. The Platform Should Reduce Cognitive Load

A good platform hides unnecessary complexity and exposes necessary complexity.

Bad platform design exposes everything:

* storage internals;
* cluster configuration;
* IAM roles;
* table formats;
* file sizes;
* retry policies;
* orchestration details;
* networking;
* serialization;
* metadata;
* deployment mechanics;
* secret handling;
* cost attribution;
* logging conventions.

Some users need to understand some of these things.

Most users do not need all of them all the time.

A productized platform offers layers.

### Beginner path

Use templates and defaults.

### Intermediate path

Customize common settings.

### Advanced path

Override lower-level behavior intentionally.

Example:

```yaml
pipeline:
  name: daily_orders
  owner: finance-data-platform
  schedule: "0 6 * * *"
  source: raw.orders
  target: mart.daily_orders
  write_mode: replace_partition
  partition_key: order_date
  quality_profile: standard
  alert_channel: "#data-finance-alerts"
```

This is much easier than forcing every user to define Airflow operators, Spark configuration, IAM roles, logging, retries, and deployment from scratch.

Good platforms provide abstraction.

Bad platforms provide exposure.

Exposure is not empowerment.

Sometimes it is just a cold wind.

---

## 9. Opinionated Defaults Are Kindness

Platform teams sometimes avoid opinionated defaults because they want flexibility.

But too much flexibility creates decision fatigue.

Users do not want to decide everything.

They want sane defaults.

Good defaults might include:

* default file format: Parquet;
* default table format: Iceberg/Delta/Hudi depending on stack;
* default partitioning guidance;
* default retry policy;
* default freshness checks;
* default alert routing;
* default data quality profile;
* default logging format;
* default cost tags;
* default CI checks;
* default deployment pattern;
* default access request workflow.

The key is:

> Defaults should be easy to use and possible to override with justification.

Example:

```yaml
compute:
  profile: standard-batch

quality:
  profile: standard

observability:
  freshness_check: true
  volume_check: true
  schema_check: true
```

A user should not need to become a platform expert to create a normal pipeline.

Opinionated defaults are not authoritarian.

They are hospitality.

They say:

> "We thought about the common case so you do not have to."

That is a beautiful sentence.

Almost suspiciously adult.

---

## 10. The Platform Should Make the Safe Path the Easy Path

Governance often fails when the safe path is harder than the unsafe path.

If publishing a governed table takes three weeks, but creating a private spreadsheet takes three minutes, users will choose the spreadsheet.

If requesting access is painful, people will share credentials.

If deploying a pipeline requires platform-team intervention, people will run notebooks manually.

If data quality checks are hard to add, teams will skip them.

If cost tagging is manual and annoying, tags will be missing.

The platform must make safe behavior easy.

Examples:

### Data quality by default

Every new published table gets basic checks unless explicitly disabled.

### Ownership required

A table cannot be published without owner metadata.

### Cost tags automatic

Compute jobs inherit team and project tags from deployment config.

### Access requests standardized

Users request access through a clear workflow with data owner approval.

### Backfills parameterized

Backfills are executed through supported controls, not code edits.

### Secrets managed automatically

Users do not paste tokens into notebooks like cursed confetti.

The platform should reduce the gap between "correct" and "convenient."

If correct is inconvenient, convenient will win.

Convenient is undefeated in most organizations.

---

## 11. Internal Documentation Is Part of the Product

Documentation is not a side task.

It is part of the product surface.

A platform without documentation is a platform that requires oral tradition.

Oral tradition is lovely for folklore.

Less lovely for incident response.

Good platform documentation includes:

* quickstart guides;
* conceptual architecture;
* task-based tutorials;
* reference docs;
* examples;
* common errors;
* troubleshooting guides;
* runbooks;
* ownership model;
* service-level expectations;
* cost guidance;
* security rules;
* migration guides;
* deprecation notices;
* release notes.

But documentation must be maintained.

Old documentation is worse than no documentation because it creates false confidence.

A useful documentation structure might look like:

```text
docs/
    getting-started/
        create-your-first-pipeline.md
        request-data-access.md

    concepts/
        data-zones.md
        data-contracts.md
        backfills.md
        table-ownership.md

    how-to/
        add-quality-checks.md
        run-a-backfill.md
        publish-a-data-product.md
        debug-a-failed-job.md

    reference/
        pipeline-config.md
        compute-profiles.md
        table-standards.md

    runbooks/
        freshness-incident.md
        failed-ingestion.md
        schema-change.md
```

Good documentation lets users self-serve.

Great documentation reduces repeated support questions.

Legendary documentation includes examples that actually work.

A rare species. Protect it.

---

## 12. Documentation Alone Is Not Enough

Documentation is necessary, but it cannot carry the whole product.

If the platform requires users to read 40 pages before doing anything, the product is too hard.

Documentation should support usability, not compensate for bad design.

Bad pattern:

> Complex manual process + long documentation.

Better pattern:

> Simple workflow + short documentation + templates + validation.

Example:

Bad:

```text
To deploy a pipeline:
    1. Create a YAML file.
    2. Create an Airflow DAG.
    3. Configure IAM manually.
    4. Add logging.
    5. Add retries.
    6. Add alerting.
    7. Add data quality checks.
    8. Create deployment script.
    9. Ask platform team to review.
```

Better:

```bash
data-platform create pipeline daily_orders --template batch-sql
```

Then the generated project includes the correct structure.

The documentation explains how to customize it.

Documentation should explain the paved road.

It should not be the road.

---

## 13. The Platform Needs Product Metrics

If the data platform is a product, it needs product metrics.

Not vanity metrics.

Useful metrics.

Examples:

### Adoption metrics

* number of active teams;
* number of pipelines using standard templates;
* number of data products registered;
* percentage of tables with owners;
* percentage of pipelines with quality checks;
* percentage of workloads with cost tags.

### Reliability metrics

* pipeline success rate;
* freshness SLA/SLO compliance;
* mean time to detect incidents;
* mean time to recover;
* number of repeated incidents;
* data quality failure rate;
* backfill success rate.

### Usability metrics

* onboarding time for new teams;
* time to create a new pipeline;
* time to request and receive access;
* support tickets per team;
* repeated support questions;
* user satisfaction surveys;
* documentation search failures.

### Cost metrics

* cost per workload;
* cost per table;
* idle compute spend;
* bytes scanned by top queries;
* cost of backfills;
* storage growth by domain.

### Governance metrics

* tables without owners;
* datasets without classifications;
* access requests pending;
* sensitive datasets queried;
* policy violations;
* deprecated assets still used.

A platform team should know whether the product is getting better.

Otherwise, "platform maturity" becomes a feeling.

Feelings are useful.

But for platform roadmaps, metrics are better.

---

## 14. Product Metrics Can Be Dangerous Too

Metrics can distort behavior.

If the platform team measures only adoption, it may push teams onto bad tooling too early.

If it measures only ticket reduction, it may discourage users from asking for help.

If it measures only cost reduction, it may make the platform slower.

If it measures only reliability, it may avoid useful change.

Good product metrics need balance.

A healthy scorecard includes:

* adoption;
* reliability;
* usability;
* cost;
* governance;
* delivery speed.

Example:

```text
Platform scorecard:
    adoption: increasing standard pipeline usage
    reliability: 99% freshness SLO for critical marts
    usability: median access request time under 1 day
    cost: idle compute under 5% of monthly spend
    governance: 98% critical tables have owners
    delivery: new pipeline template creation under 30 minutes
```

No single metric tells the full story.

Product management is the art of preventing one metric from becoming a tiny dictator.

---

## 15. Support Is a Product Surface

Support is not separate from the platform.

Support is part of the platform experience.

Users need to know:

* where to ask questions;
* what support is available;
* what response time to expect;
* what information to provide;
* which issues are self-service;
* which issues are platform incidents;
* which team owns which dataset;
* how escalation works.

Bad support model:

```text
Ask in #data-random and hope someone answers.
```

Better support model:

```text
Support channels:
    #data-platform-help
    #data-access-requests
    #data-incidents
    #data-quality-alerts

Ticket categories:
    access
    pipeline failure
    new data product
    backfill request
    performance issue
    platform bug
    documentation gap

Expected response:
    critical incident: immediate
    production blocker: same business day
    general question: 1-2 business days
```

Support also generates product insight.

Repeated support questions reveal product gaps.

If users keep asking how to run backfills, the backfill interface is not clear enough.

If users keep asking where a dataset lives, catalog discovery is weak.

If users keep asking why permissions fail, access errors need better explanations.

Support is user research with a queue.

Do not waste it.

---

## 16. The Platform Needs a Roadmap

A data platform without a roadmap becomes reactive.

It chases incidents, tickets, migrations, and executive requests.

A product roadmap helps prioritize.

But platform roadmaps are tricky because users ask for everything:

* faster queries;
* cheaper compute;
* more connectors;
* better dashboards;
* easier backfills;
* more self-service;
* stricter governance;
* fewer approval steps;
* more flexibility;
* more standardization;
* real-time everything;
* no incidents;
* no cloud bill;
* magical lineage;
* probably AI.

The roadmap must balance:

* user pain;
* business impact;
* technical debt;
* reliability risks;
* compliance needs;
* cost optimization;
* strategic platform direction;
* team capacity.

Roadmap items should be framed as user outcomes.

Weak roadmap item:

> "Implement metadata service v2."

Better:

> "Reduce time to discover and understand trusted datasets by creating a searchable metadata service with ownership, freshness, lineage, and access request links."

Weak:

> "Add Spark template."

Better:

> "Let domain teams create production-ready Spark batch jobs with logging, retries, cost tags, and standard deployment in under 30 minutes."

Product framing keeps the platform honest.

Technology work should connect to user value.

Otherwise, platform teams can become very busy building things nobody asked for and everyone must now maintain.

---

## 17. Product Discovery for Data Platforms

Product discovery means understanding user problems before building solutions.

For data platforms, discovery can include:

* interviews with data engineers;
* shadowing analysts;
* reviewing support tickets;
* studying incident reports;
* measuring onboarding time;
* analyzing query patterns;
* looking at cost anomalies;
* reviewing failed pipeline deployments;
* mapping manual workflows;
* observing how teams request access;
* identifying repeated Slack questions.

Good discovery questions:

* What task is hardest today?
* Where do you lose the most time?
* What do you avoid doing because the platform makes it painful?
* What workarounds have you created?
* What do you not trust?
* What requires platform-team help?
* What breaks most often?
* What do you wish were self-service?
* What is unclear in the documentation?
* What scares you about deploying changes?

The goal is to find real friction.

Not imagined friction.

Platform engineers are often tempted to solve technically interesting problems.

Product discovery forces the question:

> Is this the problem users actually have?

Sometimes the answer is humbling.

Good.

Humility is cheaper than building the wrong abstraction.

---

## 18. Internal Customers Are Not Always Right

Product thinking does not mean doing everything users ask.

Internal customers know their pain.

They may not know the best platform solution.

A user may ask:

> "Can I get admin access to the production warehouse?"

Their underlying need may be:

> "I need to debug a production data issue quickly."

The right solution may be:

* better logs;
* read-only debug access;
* temporary break-glass access;
* queryable run metadata;
* improved lineage;
* a support escalation path.

Another user may ask:

> "Can you create a custom cluster for my team?"

Their underlying need may be:

> "Our jobs are slow and competing with dashboards."

The solution may be:

* workload isolation;
* better compute profile;
* query optimization;
* table compaction;
* partitioning changes;
* scheduled backfill windows.

Users describe symptoms and desired fixes.

Platform teams must diagnose.

Product thinking is not order-taking.

It is problem-solving with users.

A platform team should be empathetic, but not obedient to every requested implementation.

If the platform becomes a pile of one-off requests, product coherence dies.

And then everyone gets a custom button.

A custom button for every team is how internal tools become haunted furniture.

---

## 19. Platform APIs Matter

A productized platform exposes stable interfaces.

These may be:

* command-line tools;
* configuration files;
* SDKs;
* templates;
* APIs;
* web portals;
* catalogs;
* Terraform modules;
* CI/CD actions;
* workflow components.

The goal is to let users interact with the platform through supported interfaces instead of copying internal implementation details.

Example CLI:

```bash
data-platform pipeline create \
    --name daily_orders \
    --template batch-sql \
    --owner finance-data-platform \
    --schedule "0 6 * * *"
```

Example pipeline config:

```yaml
pipeline:
  name: daily_orders
  owner: finance-data-platform
  schedule: "0 6 * * *"

source:
  table: raw.orders

target:
  table: mart.daily_orders
  write_mode: replace_partition
  partition_key: order_date

quality:
  profile: standard

observability:
  alert_channel: "#data-finance-alerts"
```

Example Python SDK interface:

```python
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DataProduct:
    """Metadata for a published data product."""

    name: str
    owner: str
    domain: str
    freshness_slo_hours: int
    contains_sensitive_data: bool
```

The specific interface depends on the organization.

The principle is stable:

> Do not make users depend on platform internals when they can depend on product interfaces.

Good interfaces create stability.

Bad interfaces leak complexity.

---

## 20. Golden Paths and Escape Hatches

A productized platform needs both golden paths and escape hatches.

### Golden paths

Recommended, supported ways to do common tasks.

Examples:

* standard batch pipeline;
* standard streaming ingestion;
* standard dbt model;
* standard data quality profile;
* standard reverse ETL sync;
* standard ML feature generation;
* standard backfill flow.

Golden paths should be easy, documented, and reliable.

### Escape hatches

Controlled ways to handle unusual needs.

Examples:

* custom compute configuration;
* advanced scheduling;
* unusual table format settings;
* custom connector;
* special security requirements;
* experimental workload;
* high-volume backfill.

Escape hatches prevent the platform from becoming too rigid.

But they should be visible and governed.

A good platform says:

> "Use the golden path unless you have a reason not to. If you need to leave it, here is the safe way."

A bad platform says either:

> "Anything goes."

or:

> "Nothing outside the template is allowed."

The first creates chaos.

The second creates shadow systems.

Balance is the platform art.

A platform should have rails, not prison bars.

---

## 21. Data Products Need Owners

A data platform as a product should encourage data products with owners.

A table without an owner is a future incident.

Ownership should include:

* technical owner;
* business owner;
* support channel;
* freshness expectation;
* quality expectations;
* access policy;
* documentation;
* lifecycle status.

Example data product metadata:

```yaml
data_product:
  name: mart.customer_360
  domain: customer
  technical_owner: customer-data-platform
  business_owner: customer-success-ops
  support_channel: "#data-customer-help"
  freshness:
    expected_by: "07:00"
    timezone: "America/Recife"
  quality:
    primary_key: customer_id
    required_checks:
      - uniqueness
      - freshness
      - volume
      - schema
  status: production
```

This lets users know whether the dataset is trustworthy.

It also prevents the classic question:

> "Who owns this table?"

followed by 20 minutes of Slack archaeology.

Ownership is not optional.

Ownership is how data stops being abandoned furniture.

---

## 22. The Catalog Is the Storefront

If the data platform is a product ecosystem, the catalog is the storefront.

Users need to discover data products.

A useful catalog should answer:

* What does this dataset mean?
* Who owns it?
* Is it production-ready?
* How fresh is it?
* What fields does it contain?
* Which fields are sensitive?
* What quality checks run?
* What upstream sources feed it?
* What downstream assets depend on it?
* How do I request access?
* Are there examples?
* Is this deprecated?
* Are there better alternatives?

A weak catalog is just a table list.

A strong catalog is a product discovery interface.

Example catalog entry:

```text
Dataset:
    mart.customer_360

Description:
    Curated customer-level table combining account, billing, support, and product usage attributes.

Status:
    Production

Owner:
    customer-data-platform

Freshness:
    Daily by 07:00 America/Recife

Primary key:
    customer_id

Sensitive fields:
    email, billing_status

Common use cases:
    customer success dashboard
    churn modeling
    account segmentation

Access:
    request via data-access/customer-360
```

This is useful.

Compare that with:

```text
mart.customer_360
```

Thank you, catalog. Very mysterious.

A catalog should reduce ambiguity.

Not provide a prettier place to be confused.

---

## 23. The Platform Should Support the Full Data Product Lifecycle

Data products have lifecycles.

They are created, used, improved, deprecated, and eventually removed.

A platform-as-product mindset supports this lifecycle.

### Creation

Templates, standards, contracts, quality checks.

### Publication

Catalog registration, ownership, access policy, documentation.

### Operation

Freshness monitoring, quality checks, lineage, alerts.

### Evolution

Schema changes, versioning, migration, consumer communication.

### Deprecation

Warnings, replacement guidance, usage tracking, removal plan.

### Removal

Archive, delete, or retire safely.

Without lifecycle management, old datasets accumulate.

Then nobody knows which table is correct.

Example:

```text
daily_revenue
daily_revenue_new
daily_revenue_v2
daily_revenue_final
daily_revenue_corrected
daily_revenue_prod
daily_revenue_prod_DO_NOT_USE
```

This is not a data platform.

This is a museum of organizational anxiety.

A good platform makes lifecycle state explicit:

* experimental;
* staging;
* production;
* deprecated;
* archived.

Users should know which tables are safe to use.

The platform should not make them guess based on table names like `final_v3`.

---

## 24. Deprecation Is a Product Skill

Deprecation is hard.

People depend on old things.

A platform team cannot simply delete old tables, pipelines, APIs, or templates without understanding impact.

Good deprecation includes:

* usage analysis;
* downstream lineage;
* replacement path;
* communication;
* migration guide;
* timeline;
* warnings;
* final removal date;
* support window.

Example deprecation notice:

```text
Dataset deprecated:
    mart.daily_revenue_v1

Replacement:
    mart.daily_revenue_v2

Reason:
    v2 includes corrected refund handling and standardized timezone logic.

Timeline:
    v1 will remain available until 2026-12-31.

Action required:
    Update dashboards and pipelines to use v2.

Owner:
    finance-data-platform
```

Deprecation is not cleanup.

It is change management.

Good deprecation protects users while reducing platform clutter.

Bad deprecation creates surprise.

And surprise, as usual, is how trust goes outside to smoke a cigarette.

---

## 25. Platform Reliability Is Product Reliability

If users depend on the platform, platform reliability is product reliability.

Important questions:

* Are pipelines completing on time?
* Are critical datasets fresh?
* Are quality checks passing?
* Are jobs retrying safely?
* Are compute environments available?
* Are access requests working?
* Are catalogs online?
* Are dashboards reading trusted data?
* Are backfills safe?
* Are incidents communicated?
* Are users alerted when data is stale?

A platform-as-product team defines SLOs.

Examples:

```text
Critical production data products:
    99% freshness by agreed deadline

Access requests:
    95% completed within 1 business day

Pipeline deployment:
    standard pipeline template deploys in under 30 minutes

Catalog availability:
    99.9% monthly uptime

Backfill framework:
    resumable partition backfills with progress tracking
```

SLOs should match user needs.

Not every table needs the same reliability.

An experimental dataset does not need executive-report guarantees.

But critical data products should have explicit expectations.

Without reliability targets, users experience the platform as a mood.

And platforms should not have moods.

That is what humans are for.

---

## 26. Data Quality as Product Trust

Data quality is not only an engineering practice.

It is part of product trust.

Users trust datasets when they know:

* what the data means;
* when it was updated;
* whether checks passed;
* who owns it;
* how to report issues;
* whether it is production-ready;
* what changed recently.

A useful data product page might show:

```text
Data product: mart.customer_360

Freshness:
    last updated: 2026-10-04 06:42
    expected: daily by 07:00
    status: OK

Quality:
    uniqueness(customer_id): passed
    null_rate(email): passed
    volume: warning, 8% below expected
    schema: passed

Lineage:
    upstream: raw.crm_accounts, raw.billing_customers, clean.product_events
    downstream: customer_success_dashboard, churn_feature_table

Owner:
    customer-data-platform
```

This gives users confidence.

Or, if something is wrong, it gives them context.

A platform that hides data quality status forces users to discover issues manually.

That is not self-service.

That is self-defense.

---

## 27. The Platform Should Make Cost Visible

Cost is part of product experience.

If users cannot see the cost of their work, they cannot make informed decisions.

A platform should expose cost in useful ways:

* cost by team;
* cost by pipeline;
* cost by table;
* cost by query;
* cost by dashboard;
* cost by compute profile;
* cost by environment;
* cost by backfill;
* idle compute cost;
* storage growth.

Cost visibility should not be punitive.

It should help teams choose better patterns.

Example:

```text
Top cost drivers this week:
    1. ad_hoc_customer_events_query: 42 TB scanned
    2. daily_feature_backfill: 31 compute hours
    3. raw_events_dashboard: 18 TB scanned daily
    4. unused_large_cluster: 26 idle hours
```

This reveals product opportunities:

* create aggregate table;
* optimize query;
* add partition filter;
* shut down idle compute;
* move dashboard to curated mart;
* improve feature pipeline.

Cost is feedback.

Without feedback, platforms become expensive silently.

Silent expense is still expense.

It just wears socks.

---

## 28. The Platform Should Prevent Repeated Mistakes

A platform product should learn.

If users repeatedly make the same mistake, the platform should change.

Examples:

### Users forget partition filters

Add query warnings or templates.

### Users create tables without owners

Make owner metadata required.

### Users deploy pipelines without alerts

Add default alerting.

### Users run expensive backfills during business hours

Add backfill scheduling policies.

### Users create small files

Add writer defaults and compaction automation.

### Users use raw tables in dashboards

Promote curated marts and catalog recommendations.

### Users send bad values to Reverse ETL

Add pre-sync validation.

The platform should absorb organizational learning.

Otherwise, every team relearns the same lesson through pain.

Pain is educational.

But repeating preventable pain is bad platform design.

---

## 29. Data Platform as Product vs. Data Mesh

The phrase "data platform as a product" often appears near "data mesh," but they are not the same thing.

Data mesh emphasizes domain ownership of data products, federated governance, and self-serve data infrastructure.

A data platform as product is the self-serve infrastructure part treated seriously as an internal product.

In a mesh-like organization:

* domain teams own data products;
* platform team provides tools and paved roads;
* governance is federated;
* data products are discoverable and contract-aware.

But even outside data mesh, platform-as-product thinking is useful.

You do not need a full data mesh transformation to ask:

* Who are our internal users?
* What problems do they have?
* How usable is the platform?
* What are our product metrics?
* What are our golden paths?
* How do we reduce support burden?
* How do we improve trust and adoption?

The platform-as-product mindset is practical.

It does not require adopting every fashionable organizational framework.

Very refreshing, honestly.

---

## 30. The Relationship Between Platform Team and Domain Teams

A healthy model separates responsibilities.

### Platform team owns

* shared infrastructure;
* platform standards;
* templates;
* orchestration services;
* compute profiles;
* storage zones;
* governance mechanisms;
* observability systems;
* deployment frameworks;
* access workflows;
* platform documentation;
* golden paths.

### Domain teams own

* business definitions;
* domain data products;
* source-specific knowledge;
* data quality expectations;
* consumer communication;
* domain-specific transformations;
* metric semantics;
* lifecycle of their datasets.

The platform team should not own every metric.

Domain teams should not reinvent infrastructure.

The boundary matters.

Bad model:

> Platform team becomes a bottleneck for every data request.

Also bad:

> Domain teams each build their own mini-platform.

Good model:

> Platform team provides the paved roads. Domain teams use them to build and operate domain data products.

This is scalable.

It also prevents the platform team from becoming the company's permanent data janitorial service.

Janitorial work is honorable.

Permanent preventable janitorial work is a process smell.

---

## 31. Platform Governance Should Be Embedded, Not Bolted On

Governance works best when embedded into platform workflows.

Instead of asking users to remember governance manually, build it into the product.

Examples:

### Access control

Access requests go through catalog-integrated approval.

### Data classification

Publishing a table requires sensitivity classification.

### Ownership

Production datasets require owner metadata.

### Quality checks

Critical tables require freshness and uniqueness checks.

### Lineage

Pipelines automatically register inputs and outputs.

### Cost tags

Compute jobs automatically inherit owner and project tags.

### Retention

Storage zones enforce retention policies.

### Schema changes

Breaking changes require contract review.

This is governance as product design.

Not governance as a PDF.

PDF governance is where good intentions go to become unread.

Embedded governance makes the correct behavior natural.

---

## 32. A Small Example: Productized Pipeline Configuration

Here is a simple example of what productized pipeline configuration might look like.

```yaml
pipeline:
  name: daily_customer_health
  owner: customer-data-platform
  domain: customer
  status: production

schedule:
  cron: "0 6 * * *"
  timezone: "America/Recife"

source:
  tables:
    - clean.customer_accounts
    - clean.product_usage_daily
    - clean.support_tickets

target:
  table: mart.customer_health_daily
  write_mode: replace_partition
  partition_key: snapshot_date

quality:
  checks:
    - type: freshness
      max_delay_hours: 24
    - type: uniqueness
      column: customer_id
    - type: not_null
      columns:
        - customer_id
        - health_segment
    - type: accepted_values
      column: health_segment
      values:
        - green
        - yellow
        - red

observability:
  alert_channel: "#data-customer-alerts"
  severity: high

cost:
  compute_profile: standard-batch
  cost_center: customer-success

backfill:
  enabled: true
  max_parallel_partitions: 8
  require_approval_for_days_over: 90

governance:
  contains_sensitive_data: true
  data_classification: internal-confidential
  access_policy: customer-domain-approved
```

This configuration is more than execution metadata.

It captures ownership, quality, cost, backfill behavior, and governance.

That is productization.

The platform can use this metadata to generate:

* orchestration jobs;
* quality checks;
* alerts;
* catalog entries;
* access policies;
* cost reports;
* backfill controls.

The user provides intent.

The platform handles the standardized mechanics.

That is the dream.

A practical dream, not a vendor-slide dream.

---

## 33. A Small Python Sketch: Data Product Metadata

Below is a small teaching sketch for representing data product metadata.

```python
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class DataProductStatus(StrEnum):
    """Lifecycle status of a data product."""

    EXPERIMENTAL = "experimental"
    STAGING = "staging"
    PRODUCTION = "production"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"


class DataClassification(StrEnum):
    """Simplified data classification levels."""

    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    SENSITIVE = "sensitive"


@dataclass(frozen=True)
class DataProductMetadata:
    """Metadata describing an internal data product.

    Parameters
    ----------
    name
        Fully qualified data product name.
    owner_team
        Team responsible for technical operation.
    business_owner
        Business-facing owner or steward.
    status
        Lifecycle status of the data product.
    classification
        Data sensitivity classification.
    freshness_slo_hours
        Maximum expected delay in hours.
    support_channel
        Channel where users can ask for help.
    ```

    name: str
    owner_team: str
    business_owner: str
    status: DataProductStatus
    classification: DataClassification
    freshness_slo_hours: int
    support_channel: str


def is_production_ready(product: DataProductMetadata) -> bool:
    """Return whether a data product is production-ready.

    Parameters
    ----------
    product
        Data product metadata.

    Returns
    -------
    bool
        ``True`` if the data product is marked as production.
    ```
    return product.status == DataProductStatus.PRODUCTION


def requires_strict_access_control(product: DataProductMetadata) -> bool:
    """Return whether a data product needs stricter access control.

    Parameters
    ----------
    product
        Data product metadata.

    Returns
    -------
    bool
        ``True`` for confidential or sensitive data products.
    ```
    return product.classification in {
        DataClassification.CONFIDENTIAL,
        DataClassification.SENSITIVE,
    }
```

The point is not the class itself.

The point is the mindset:

> A data product should carry metadata that makes it operable, discoverable, governable, and trustworthy.

A table name alone is not enough.

A table name is a label on a box.

A data product needs an instruction manual, an owner, a warranty, and a support desk.

Maybe not literally.

But spiritually, yes.

---

## 34. Healthcare and Biotech: Platform as Product Matters Even More

In healthcare and biotech, treating the data platform as a product is not just a productivity improvement.

It is a trust and governance requirement.

Users may include:

* bioinformaticians;
* clinical data scientists;
* epidemiologists;
* ML researchers;
* physicians;
* lab teams;
* regulatory teams;
* data engineers;
* hospital IT;
* research coordinators.

The data may include:

* EHR records;
* claims;
* lab results;
* diagnoses;
* medications;
* imaging metadata;
* genomic variants;
* gene expression;
* sample metadata;
* cohort definitions;
* clinical outcomes.

The platform must help users answer:

* Which dataset should I use?
* Is it approved for research?
* Is it de-identified?
* What consent restrictions apply?
* Which genome build was used?
* Which annotation version?
* Which phenotype definition?
* Which patients are included?
* What is the refresh schedule?
* Can I export this?
* Who owns it?
* Can this be used for ML training?
* Can this be shared externally?

Without product thinking, users rely on personal networks and hidden knowledge.

That is dangerous in regulated or scientific environments.

A biomedical data platform should productize:

* cohort discovery;
* data access requests;
* dataset documentation;
* provenance tracking;
* reproducible releases;
* pipeline versioning;
* quality checks;
* audit trails;
* compute environments;
* approved export paths.

The goal is not to make the platform bureaucratic.

The goal is to make correct, reproducible, governed work easier than informal work.

In biomedical data, convenience without governance is risky.

Governance without usability creates workarounds.

The product challenge is to provide both.

---

## 35. Common Anti-Patterns

### Anti-pattern 1: Tool-first platform

The team says:

> "We have Spark, Airflow, dbt, Kafka, and a lakehouse."

That describes tools.

Not user outcomes.

### Anti-pattern 2: No product owner

Nobody owns platform prioritization across users, reliability, adoption, and roadmap.

The platform becomes reactive.

### Anti-pattern 3: Documentation as apology

The platform is hard to use, so documentation becomes a giant workaround.

### Anti-pattern 4: No golden paths

Every team invents its own patterns.

Standardization arrives only during incidents.

### Anti-pattern 5: Platform team as ticket factory

The team spends all its time manually helping users instead of improving the product.

### Anti-pattern 6: Governance by friction

Security and quality processes are so painful that users avoid them.

### Anti-pattern 7: No lifecycle management

Old datasets, pipelines, and templates never die.

They just become confusing.

### Anti-pattern 8: One-size-fits-all compute

BI, backfills, ML, streaming, and exploration all compete for the same resources.

### Anti-pattern 9: No cost visibility

Everyone uses the platform, nobody knows what costs what.

### Anti-pattern 10: Captive-user complacency

Users must use the platform, so leadership assumes the product is successful.

Mandatory usage is not love.

It is just mandatory.

---

## 36. What Good Looks Like

A healthy data-platform-as-product practice has the following traits.

### Clear internal customer segments

The platform team knows who uses the platform and what they need.

### Golden paths

Common tasks have supported, documented, easy workflows.

### Strong developer experience

Setup, testing, deployment, monitoring, and debugging are clear.

### Self-service with guardrails

Users can move independently without bypassing governance.

### Opinionated defaults

Common cases are easy; advanced cases are possible.

### Product metrics

Adoption, reliability, usability, cost, and governance are measured.

### Active support model

Users know where to get help and what to expect.

### Roadmap

Platform evolution is prioritized by user value and business impact.

### Embedded governance

Ownership, access, classification, quality, and lineage are part of workflows.

### Lifecycle management

Data products and platform features can be created, evolved, deprecated, and removed safely.

### Cost transparency

Teams understand the cost of workloads and can optimize.

### Trust indicators

Users can see freshness, quality status, ownership, and documentation.

In short:

> A good data platform makes the right thing easy, the risky thing explicit, and the unsupported thing rare.

That is platform product maturity.

---

## 37. A Practical Checklist

If you want to treat your data platform as a product, ask:

1. Who are the platform's main user groups?
2. What are their most common tasks?
3. Which tasks are painful today?
4. Which tasks require platform-team intervention?
5. Where do users create workarounds?
6. What are the golden paths?
7. Are templates available and maintained?
8. How long does onboarding take?
9. How long does it take to create a production pipeline?
10. How does a user request access to data?
11. How does a user publish a data product?
12. How does a user run a backfill?
13. How does a user know if data is fresh?
14. How does a user know who owns a table?
15. How are data products discovered?
16. How are costs attributed?
17. How are incidents communicated?
18. How are platform features deprecated?
19. What product metrics are tracked?
20. Who owns the platform roadmap?
21. What repeated support questions indicate product gaps?
22. Where is governance embedded into workflows?
23. Which unsafe actions are still too easy?
24. Which safe actions are still too hard?
25. What would make users choose the platform even if it were not mandatory?

That last question is brutal.

It is also the right question.

A good internal platform should earn adoption, not merely enforce it.

---

## 38. The Cultural Shift

Treating the data platform as a product requires cultural change.

The platform team stops thinking only in terms of components:

* clusters;
* buckets;
* DAGs;
* tables;
* connectors;
* jobs;
* permissions;
* catalogs.

And starts thinking in terms of user outcomes:

* faster onboarding;
* safer deployment;
* easier discovery;
* more trustworthy datasets;
* fewer repeated questions;
* lower incident rate;
* clearer ownership;
* easier backfills;
* better cost control;
* more productive teams.

The platform team still needs deep engineering.

This is not a move away from technical excellence.

It is technical excellence aimed at user success.

A platform can be technically impressive and still fail as a product.

A complex platform that users avoid is not mature.

A simple platform that lets users safely accomplish valuable work is much closer.

The goal is not to build the most sophisticated internal machine.

The goal is to make the organization better at using data.

That is a different scoreboard.

---

## 39. The Real Test: What Happens Without the Platform Team in the Room?

A strong data platform lets teams accomplish common tasks without constant platform-team presence.

Ask:

* Can a new team onboard using documentation and templates?
* Can they create a pipeline safely?
* Can they publish a data product?
* Can they understand quality status?
* Can they request access?
* Can they debug common failures?
* Can they run a supported backfill?
* Can they estimate cost?
* Can they find the right dataset?
* Can they know who owns it?
* Can they avoid sensitive-data mistakes?

If every action requires a platform engineer in the room, the platform is not self-service.

It may be powerful.

But it is not productized.

The platform team should be needed for:

* advanced cases;
* new capabilities;
* platform evolution;
* incidents;
* architecture guidance;
* unusual requirements.

Not every ordinary pipeline.

If the platform team is always the bottleneck, the product is incomplete.

A good platform team scales itself through product design.

That is the difference between engineering labor and platform leverage.

---

## 40. Final Thought

Data Platform as a Product is not a slogan.

It is a discipline.

It means treating internal engineers, analysts, data scientists, and business users as real customers of the platform.

Not because they are always right.

Not because every request should be fulfilled.

Not because internal tools need fancy branding.

But because a data platform only creates value when people can use it successfully.

A platform is not successful because it has modern tools.

It is successful when it makes good data work easier:

* easier to ingest data;
* easier to transform data;
* easier to test data;
* easier to publish data products;
* easier to discover trusted datasets;
* easier to request access;
* easier to monitor pipelines;
* easier to run backfills;
* easier to control cost;
* easier to follow governance;
* easier to recover from incidents;
* easier to build without breaking everyone downstream.

The mature platform team asks:

> What are our users trying to accomplish, and how can the platform make the correct path simpler, safer, and more reliable?

That question changes everything.

It turns infrastructure into experience.

It turns tools into workflows.

It turns governance into guardrails.

It turns support tickets into product feedback.

It turns internal users from "people who keep bothering us" into customers whose success defines the platform's value.

A data platform is not a warehouse, a lakehouse, an orchestrator, a catalog, or a cluster.

Those are components.

The platform is the product experience that connects those components into something people can trust and use.

Build it like a product.

Operate it like a product.

Improve it like a product.

Because if your internal engineers are forced to use the platform but secretly work around it, you did not build a product.

You built a maze with invoices.

And somewhere, quietly, someone is exporting another CSV.
