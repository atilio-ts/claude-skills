# Gap Analysis — Finding What Should Be Documented

A directory listing tells you what files exist. It does not tell you what a developer
needs to understand to safely change the system. The gap that matters most is usually
invisible to `ls`: a subsystem that's fully wired into the runtime via configuration, a
scheduled job, a webhook handler, a background worker — things that don't show up as a
prominent source file but absolutely show up in an entry-point or config layer.

The core technique: **find the project's own map of what it runs, then check doc coverage
against that map — not against the source tree.**

---

## Where the real map lives, by project shape

Different architectures declare "what exists" in different places. Identify which of
these applies (a project can match more than one) and read that layer in full before
judging coverage:

**Declarative/config-driven backends** (jPOS, Spring beans/XML config, dependency-injection
containers, Airflow DAGs, Kubernetes manifests): the wiring files themselves are the
component list. Every `<participant>`, `<bean>`, `<job>`, `<sender>` entry is a candidate
component. Read every config file in the deploy/config directory fully, not just the ones
that look familiar — the ones you've never seen referenced anywhere are exactly the gaps.

**Web APIs / BFFs**: the route table (OpenAPI/Swagger spec, router file, controller
annotations) is the map. Enumerate every endpoint group and check whether each has more
than a one-line mention. Pay special attention to admin/internal endpoints and webhooks —
they're commonly under-documented relative to the main CRUD surface.

**CLIs**: the command registry (subcommand list, argument parser setup) is the map. Every
subcommand is a candidate unit of documentation.

**Libraries**: the public API surface (exported symbols, `__all__`, public class/interface
list) is the map. Internal-only code is lower priority.

**Scheduled/background work** (cron jobs, queue consumers, event listeners): these are
easy to miss entirely because they have no caller in the request-handling sense. Find them
via the scheduler config (cron XML, `@Scheduled` annotations, systemd timers, message queue
subscriptions) — don't rely on stumbling across the class while reading something else.

**Notification/observability wiring** (alerting, logging sinks, metrics exporters): often
there are multiple distinct channels that superficially look similar (e.g. three different
notification senders configured for three different purposes) and nothing explains how
they differ. If you find more than one instance of a similar-looking integration, that's a
strong signal a "how these differ" doc is missing even if each one individually has some
mention somewhere.

---

## Building the coverage table

For each candidate component found in the map:

1. Grep the existing docs tree for the component's class name / config key / route path.
2. Classify:
   - **No mention anywhere** → gap, needs a new doc.
   - **One-line mention in an overview file, no deep-dive** → thin coverage; decide via
     `structure-and-splitting.md` whether it earns its own file.
   - **Already has a dedicated doc** → covered, skip (don't re-investigate in create mode;
     in audit mode, this is a candidate for `audit-existing-docs.md` instead).
3. Don't stop at the first mention — a class can be *mentioned* in three different files
   and still have zero explanation of what it actually does, how it fails, or what config
   controls it. Presence of the name is not evidence of documentation.

## Dead-but-configured code is still worth documenting

Config-driven systems often have a wired-but-inactive path: a group/route/handler that's
registered but never reached in the active flow (feature flagged off, commented-out
routing, a stub with no real implementation behind it). Document these explicitly as
inactive rather than silently omitting them or silently documenting them as if they were
live — a future reader needs to know "this exists in config but nothing uses it today,
here's why" so they don't waste time chasing a dead end, and so they know where to plug in
if the feature gets finished later.

## Don't let this become a redesign

Gap analysis finds what's undocumented. It is not license to propose refactors, flag every
code smell, or redesign the architecture. Note dead code, footguns, and inconsistencies you
observe while reading — but the deliverable is documentation of what exists, not a
change proposal. If something looks like an active bug (not just an undocumented area),
mention it once, plainly, and move on; don't turn the docs pass into a code review.