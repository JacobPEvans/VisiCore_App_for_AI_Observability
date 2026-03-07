# VisiCore App for AI Observability

Splunk App package providing Dashboard Studio v2 dashboards for AI coding tool observability.

## Structure

Repo root IS the Splunk package root. `default/`, `metadata/`, `static/` are at the top level.

## Development Rules

- All config goes in `default/` only (no `local/`) for Splunk Cloud compatibility
- Dashboards use Dashboard Studio v2 format (`<dashboard version="2">` with JSON CDATA)
- Use base search + extend pattern to minimize search load
- Macros are defined in the companion TA (`VisiCore_TA_AI_Observability`) and referenced here

## Companion TA

Knowledge objects (props, transforms, macros, lookups) live in a separate repo:
`~/git/VisiCore_TA_AI_Observability/`

## Packaging

```bash
./scripts/package.sh
```

## Testing

1. Validate manifest: `jq . app.manifest`
2. Package: `./scripts/package.sh`
3. Deploy via ansible-splunk to Docker Splunk instance
4. Verify dashboards render without errors
