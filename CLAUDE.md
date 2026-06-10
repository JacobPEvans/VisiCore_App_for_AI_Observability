# VisiCore App for AI Observability

Splunk App package providing Dashboard Studio v2 dashboards for AI coding tool observability.

## Structure

Repo root IS the Splunk package root. `default/`, `metadata/` are at the top level.

## Development Rules

- All config goes in `default/` only (no `local/`) for Splunk Cloud compatibility
- Dashboards use Dashboard Studio v2 format (`<dashboard version="2">` with JSON CDATA);
  standalone `.json` files are not loadable — the XML wrapper is the canonical packaging
- Base data sources must be transforming searches (end in `timechart`/`stats`); derived panels
  use `ds.chain` with `options.extend` (never `ds.search` + `extend`); chains never set
  `queryParameters`; max 10 chains per base, one chain level
- All metric SPL routes through TA macros — zero inline pricing or token math; pricing lives only
  in the TA's `ai_model_pricing.csv` lookup (enforced by `scripts/validate_dashboards.py`)
- Filter tokens are consumed only in base searches; every input declares a `defaultValue`
- Macros are defined in the companion TA ([VisiCore_TA_AI_Observability](https://github.com/JacobPEvans/VisiCore_TA_AI_Observability)) and referenced here

## Companion TA

Knowledge objects (props, transforms, macros, lookups) live in a separate repo:
`~/git/public/VisiCore_TA_AI_Observability/`

## Packaging

```bash
./scripts/package.sh
```

## Testing

1. Validate manifest: `jq . app.manifest`
2. Validate dashboards: `python3 scripts/validate_dashboards.py default/data/ui/views/*.xml`
3. Package: `./scripts/package.sh`
4. Deploy via ansible-splunk to Docker Splunk instance (or the local verification harness)
5. Verify dashboards render without errors
