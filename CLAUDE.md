# VisiCore App for AI Observability

## Structure

Two Splunk packages in one repo:
- `VisiCore_App_for_AI_Observability/` - Dashboards (Dashboard Studio v2)
- `VisiCore_TA_AI_Observability/` - Knowledge objects (props, transforms, macros, lookups)

## Development Rules

- All config goes in `default/` only (no `local/`) for Splunk Cloud compatibility
- Dashboards use Dashboard Studio v2 format (`<dashboard version="2">` with JSON CDATA)
- Use base search + extend pattern to minimize search load
- Macros are defined in the TA and referenced by the App
- Token model follows ccusage: input_tokens, output_tokens, cache_read_input_tokens, cache_creation_input_tokens

## Packaging

```bash
./scripts/package.sh
```

Produces tarballs in `build/` directory.

## Testing

1. Validate manifests: `jq . */app.manifest`
2. Package: `./scripts/package.sh`
3. Deploy via ansible-splunk to Docker Splunk instance
4. Verify dashboards render without errors

## Key Macros (from TA)

- `` `claude_assistant_events` `` - Base filter for assistant messages
- `` `extract_tokens` `` - Extract 4 token types
- `` `calculate_cost` `` - Model-aware cost calculation
- `` `extract_tools` `` - Tool use extraction with CIM fields
