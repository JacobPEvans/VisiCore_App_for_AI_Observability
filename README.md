# VisiCore App for AI Observability

Splunk App providing Dashboard Studio v2 dashboards for AI coding tool observability. Companion to [VisiCore_TA_AI_Observability](https://github.com/JacobPEvans/VisiCore_TA_AI_Observability).

## Architecture

```
Filesystem -> Cribl Edge -> Cribl Stream -> Splunk HEC -> Splunk Enterprise
   (JSON)      (packs)      (routing)       (port 8088)    (index=claude)
```

## Dashboards

- **Overview** - KPIs, token trends, model distribution, tool usage, session activity
- **Token Usage** - Token consumption across input, output, cache read, cache creation
- **Cost Analysis** - Dollar cost estimation by model, session, and project
- **Tool Activity** - Tool call patterns and file operations
- **Sessions** - Session-level analysis with duration and project attribution
- **Cache Performance** - Prompt caching efficiency and estimated token savings

All dashboards use the base search + extend pattern for efficient search execution.

## Installation

Requires the companion TA installed first:

```bash
splunk install app VisiCore_TA_AI_Observability-*.tar.gz
splunk install app VisiCore_App_for_AI_Observability-*.tar.gz
splunk restart
```

Ensure indexes exist: `claude`, `gemini`. Configure data inputs via Cribl Edge packs.

## Usage

Navigate to the VisiCore app in Splunk Web. Six dashboards are available:

1. **Overview** - Start here for a summary of all AI activity
2. **Token Usage** - Drill into token consumption patterns
3. **Cost Analysis** - Track spend by model, session, and project
4. **Tool Activity** - Monitor tool call patterns and file operations
5. **Sessions** - Analyze individual coding sessions
6. **Cache Performance** - Evaluate prompt caching efficiency and savings

All dashboards support a time range picker and use the base search + extend pattern for efficient search execution.

## Packaging

```bash
./scripts/package.sh
```

Produces a versioned tarball in `build/`.

## References

- [OTel GenAI Semantic Conventions](https://opentelemetry.io/docs/specs/semconv/gen-ai/)
- [AI Agent Observability](https://opentelemetry.io/blog/2025/ai-agent-observability/)
- [Anthropic-specific conventions](https://opentelemetry.io/docs/specs/semconv/gen-ai/anthropic/)
- [semantic-conventions v1.36.0](https://github.com/open-telemetry/semantic-conventions/blob/v1.36.0/docs/gen-ai/README.md)
- [ccusage](https://github.com/ryoppippi/ccusage) - Token model reference
- [Splunk CIM](https://help.splunk.com/en/splunk-enterprise/common-information-model/5.3/data-models/cim-fields-per-associated-data-model)
