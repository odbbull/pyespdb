AI/ML AGENT INJECTION POINTS — PyESPDB
=======================================

Based on analysis of the full application workflow (pyespLoadFile, pyespWorkload,
pyespLineGraph, pyespHome, pyespSide), the following areas are candidates for
AI or ML agent integration.


WORKFLOW STAGES & INJECTION POINTS
------------------------------------

1. FILE LOAD — app/pyespLoadFile.py
   Raw AWR/ESCP ZIP files → sp_dbmetric, sp_dbidentity

   - Data quality agent: validate incoming metric data — flag missing intervals,
     duplicate snapshots, truncated collections, implausible values before they
     corrupt downstream analysis.
   - AWR interval auto-detection: currently the user manually types the interval
     (default 3600s); an agent could infer it from the timestamp deltas in
     sp_dbmetric rather than requiring user input.


2. METRIC GENERATION — app/pyespWorkload.py → sp_metricplot
   sp_dbmetric → (delta/scale via sp_category) → sp_metricplot

   - Anomaly detection: after generate_metrics() completes, scan the resulting
     sp_metricplot rows for outliers — CPU spikes, sustained I/O saturation,
     memory pressure events — and tag or flag them.
   - Workload classifier: label each database as OLTP / batch / mixed / read-heavy
     based on the shape of key metric traces (CPU pattern, wait event distribution,
     read/write ratio).
   - Category configuration suggester: when metric names arrive in sp_dbmetric that
     don't match any active sp_category row, an agent could propose is_static_fg,
     cat_yaxis_divisor, etc. based on metric name patterns.


3. LINE GRAPH — app/pyespLineGraph.py
   User selects collection → databases → category → acronym → Plotly chart

   - Natural language query interface: replace the 4-step dropdown chain with a
     plain-English input ("show CPU for PRODDB over the last week") that resolves
     to the correct collection/category/acronym selection.
   - Auto-annotation: after the chart renders, overlay detected anomalies, peak
     periods, or regime changes as vertical markers on the Plotly figure.


4. ASSESSMENT — /assessment route (currently a stub in app/pyespSide.py:234)
   Currently renders: html.H2("Assessment") + placeholder text only.

   THIS IS THE HIGHEST-VALUE BLANK CANVAS. Natural home for:

   - AI sizing recommendation: given processed sp_metricplot data (peak CPU %,
     avg/max I/O, memory high-watermark), invoke Claude API to produce a target
     platform recommendation with narrative justification — Exadata model, Cloud
     VM shape, equivalent on-prem spec.
   - Narrative workload summary: prose description of the collection's workload
     characteristics, suitable for inclusion in a client deliverable.
   - Cross-database comparison: identify which databases in a collection are most/
     least similar and group them for consolidated sizing.


5. HOME DASHBOARD — app/pyespHome.py
   Stat cards + bar/donut charts

   - Portfolio-level insight: after enough collections accumulate, an agent could
     surface trends — e.g. "collections have grown 40% over the past quarter" or
     "3 of 5 clients have databases with anomalous I/O patterns."


PRIORITY RANKING
-----------------

  1. Assessment page          — Highest; direct client deliverable output
  2. Post-generation anomaly  — Catches issues before analysis misleads
  3. Workload classifier      — Informs sizing without manual interpretation
  4. AWR interval detection   — Removes a common user error
  5. NL query on Line Graph   — UX improvement, lower business value


NOTES
------
- The Assessment stub is wired into the sidebar nav and has a route defined.
  It is the clearest immediate target: a Claude API call with sp_metricplot
  aggregates for the selected database could produce a complete sizing narrative
  with no UI restructuring required.
- All metric data needed for ML features lives in sp_metricplot (processed)
  and sp_dbmetric (raw). Both are keyed by sp_database_db_id.
- sp_category drives the transformation logic and is the right place to store
  agent-suggested category configurations for human review before activation.
