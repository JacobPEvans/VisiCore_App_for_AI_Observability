# VisiCore App for AI Observability

Splunk App providing Dashboard Studio v2 dashboards for AI coding tool observability.

This app ships **dashboards only**. It expects a companion technology add-on (TA) to already be
installed on the search head — the TA supplies the index-time/search-time knowledge objects the
dashboards depend on: the per-provider index macros, the CIM-mapped metric event fields, the
reporting macros (`claude_metric_events`, `extract_tools`, `calculate_cost`, …), and the pricing
lookup (`ai_model_pricing.csv`). See [Installation](#installation) for the exact contract.

## Architecture

```text
Filesystem -> Cribl Edge -> Cribl Stream -> Splunk HEC -> Splunk Enterprise
   (JSON)     (collect)      (routing)       (port 8088)    (index=claude)
```

The dashboards sit at the right-hand end of this pipeline: they only query the Splunk indexes the
data lands in. Any collection path that delivers the expected JSON events to those indexes works —
the diagram above shows the reference path, not a hard requirement.

## Dashboards

- **AI Overview** (landing page) - Cross-provider single pane: Claude KPIs, Gemini/Copilot feed status,
  activity by provider. Providers without data show explicit "No data" status rows instead of empty panels.
- **Claude Code Overview** - KPIs, token trends, cost, cache, model distribution, tool usage, top sessions
- **Token Usage** - Token mix across input, output, cache read, cache creation; per-model and per-session
- **Cost Analysis** - Lookup-driven spend by model, session, and project, with an Unpriced Messages KPI
  that surfaces models missing from the add-on's pricing lookup
- **Tool Activity** - Tool call patterns and file operations
- **Sessions** - Session-level analysis with duration, project attribution, and drill-down filtering
- **Cache Performance** - Prompt caching efficiency and model-aware estimated savings

## Dashboard conventions (Splunk 10.x Dashboard Studio)

- **Transforming base searches + `ds.chain`**: every base data source ends in a transforming command
  (`timechart`/`stats`); derived panels are `ds.chain` data sources that extend the base. Chains never set
  their own `queryParameters` and stay within Splunk's documented limits (max 10 chains per base, one level).
- **Shared `defaults` block** supplies the global time range to all base searches; filter tokens are consumed
  only in base searches.
- **All metric SPL routes through add-on macros** (`claude_metric_events`, `extract_tools`, ...). Zero
  inline pricing or token math — pricing lives only in the add-on's `ai_model_pricing.csv` lookup. CI
  enforces this via `scripts/validate_dashboards.py`.
- **Packaging format**: Dashboard Studio definitions ship as JSON inside
  `<dashboard version="2">` XML CDATA under `default/data/ui/views/`. Standalone `.json` files are not
  loadable by Splunk app packaging — the XML wrapper with embedded JSON is the canonical on-disk format.
- Cross-dashboard drilldowns via `drilldown.linkToDashboard` (e.g. session tables link into Sessions with
  the session pre-filtered).

## Installation

These dashboards have **no inline SPL logic of their own** — every search resolves through macros and a
lookup that a companion technology add-on (TA) must provide on the same search head. Install that add-on
first, then this app:

```bash
splunk install app <ai-observability-add-on>-*.tar.gz   # provides the contract below
splunk install app VisiCore_App_for_AI_Observability-*.tar.gz
splunk restart
```

### Add-on contract

The dashboards will not render until a search-head add-on supplies:

- **Indexes / data**: CIM-aligned AI metric events landing in `claude`, `gemini`
  (plus `vscode`/`openai` for Copilot/OpenAI feeds). Each provider's index is selected by a
  macro — `claude_index` / `gemini_index` / `copilot_index` / `openai_index` — so locations are
  overridable without editing the dashboards.
- **Reporting macros**: `claude_metric_events`, `extract_tools`, `calculate_cost`, and the
  per-provider event/index macros referenced throughout the dashboards.
- **Pricing lookup**: `ai_model_pricing.csv`, keyed by model, used by `calculate_cost`. Models absent
  from this lookup surface on the Unpriced Messages KPI rather than silently costing $0.

Any add-on that satisfies this contract works; the dashboards do not hard-code an add-on name. Ensure
the listed indexes exist (or are remapped via the `*_index` macros) before loading the app.

## Usage

Navigate to the VisiCore app in Splunk Web. **AI Overview** is the landing page:

1. **AI Overview** - Cross-provider status; start here to see which feeds are live
2. **Claude Code Overview** - Summary of all Claude Code activity, with drilldowns into every detail page
3. **Token Usage** - Drill into token consumption patterns (filter by model)
4. **Cost Analysis** - Track spend by model, session, and project; watch the Unpriced Messages KPI
5. **Tool Activity** - Monitor tool call patterns and file operations
6. **Sessions** - Analyze individual coding sessions (filter by project or session ID)
7. **Cache Performance** - Evaluate prompt caching efficiency and savings

All dashboards share a global time range picker (default: last 7 days).

## Validation

```bash
python3 scripts/validate_dashboards.py default/data/ui/views/*.xml
```

Checks CDATA JSON validity, data-source referential integrity, `ds.chain` resolution, and the
no-inline-pricing guard. CI runs this plus Splunk AppInspect on every push.

## Packaging

```bash
./scripts/package.sh
```

Produces a versioned tarball in `build/`.

## Release Notes

### 0.2.0

- All six Claude dashboards rebuilt to Splunk 10.x Dashboard Studio best practices: transforming base
  searches with `ds.chain` post-processing (previously non-transforming bases with `ds.search`+`extend`),
  shared `defaults` block, null-safe KPI chains ending in `| fields`.
- New **AI Overview** cross-provider landing dashboard with graceful no-data provider status.
- Inline pricing math removed everywhere; cost flows through the add-on's `calculate_cost` lookup macro,
  with new Unpriced Messages visibility on Cost Analysis.
- Model/project filter inputs added (Token Usage, Cost Analysis, Cache Performance, Sessions);
  cross-dashboard drilldowns added.
- CI added: AppInspect + dashboard structural validation.
- Requires a companion add-on providing the v0.2.0 contract: canonical token field names and the
  `claude_metric_events` macro (see [Installation](#installation)).

## References

- [OTel GenAI Semantic Conventions](https://opentelemetry.io/docs/specs/semconv/gen-ai/)
- [AI Agent Observability](https://opentelemetry.io/blog/2025/ai-agent-observability/)
- [Anthropic-specific conventions](https://opentelemetry.io/docs/specs/semconv/gen-ai/anthropic/)
- [ccusage](https://github.com/ryoppippi/ccusage) - Token model reference
- [Splunk CIM](https://help.splunk.com/en/splunk-enterprise/common-information-model/5.3/data-models/cim-fields-per-associated-data-model)
- [Chain searches (Splunk 10.x)](https://help.splunk.com/en/splunk-enterprise/create-dashboards-and-reports/dashboard-studio/10.0/use-data-sources/chain-searches-together-with-a-base-search-and-chain-searches)

---

> Part of a [larger ecosystem of ~40 repos](https://docs.jacobpevans.com) — see how it all fits together.
