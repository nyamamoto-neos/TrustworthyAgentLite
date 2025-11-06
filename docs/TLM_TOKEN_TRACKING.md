# TLM Token Usage and Cost Tracking

This document explains the token usage tracking and cost calculation features added to `TrustworthyAgent`.

## Overview

The `TrustworthyAgent` now automatically tracks:
- **Input tokens**: Tokens sent to Cleanlab TLM API
- **Output tokens**: Tokens received from Cleanlab TLM API
- **Cost**: Calculated based on TLM quality preset pricing
- **Cumulative totals**: Running totals across all interactions

## Configuration

### TLM Pricing Configuration

Pricing information is stored in `agentlite/config/tlm_pricing.json`:

```json
{
  "pricing": {
    "base": {
      "input_per_1m_tokens": 0.50,
      "output_per_1m_tokens": 1.70,
      "description": "Fastest responses, suitable for simple tasks"
    },
    "medium": {
      "input_per_1m_tokens": 1.50,
      "output_per_1m_tokens": 5.00,
      "description": "Balanced performance and quality"
    },
    "high": {
      "input_per_1m_tokens": 3.00,
      "output_per_1m_tokens": 10.00,
      "description": "High quality for complex tasks"
    },
    "best": {
      "input_per_1m_tokens": 5.00,
      "output_per_1m_tokens": 17.00,
      "description": "Maximum quality and accuracy"
    }
  },
  "default_quality": "base"
}
```

### Setting Quality Preset

Specify the TLM quality preset when creating the agent:

```python
from agentlite.agents import TrustworthyAgent

agent = TrustworthyAgent(
    name="MyAgent",
    role="Assistant",
    llm=my_llm,
    tlm_quality="base",  # Options: "base", "medium", "high", "best"
    # ... other parameters
)
```

## Usage

### Automatic Tracking

Token usage and costs are automatically tracked during agent execution:

```python
# Execute tasks as normal
result = agent(task)

# Token usage is logged automatically to console:
# "TLM Token Usage - Input: 1,234, Output: 567, Cost: $0.001585 (Total: $0.003456)"
```

### CSV Logging

Each interaction is logged to the CSV file with token and cost information:

| Column | Description |
|--------|-------------|
| `task_id` | Unique task identifier |
| `step` | Step number in the task |
| `prompt` | Input prompt sent to TLM |
| `raw_action` | Response from TLM |
| `trust_score` | Trustworthiness score (0-1) |
| `input_tokens` | Number of input tokens |
| `output_tokens` | Number of output tokens |
| `cost_usd` | Cost in USD for this interaction |

### Getting Usage Summary

Retrieve cumulative token usage and cost statistics:

```python
summary = agent.get_token_usage_summary()

print(f"Total input tokens: {summary['total_input_tokens']:,}")
print(f"Total output tokens: {summary['total_output_tokens']:,}")
print(f"Total tokens: {summary['total_tokens']:,}")
print(f"Total cost: ${summary['total_cost_usd']:.6f}")
print(f"Quality preset: {summary['quality_preset']}")
print(f"Input price: ${summary['pricing']['input_per_1m_tokens']}/1M tokens")
print(f"Output price: ${summary['pricing']['output_per_1m_tokens']}/1M tokens")
```

## Token Estimation

Token counts are obtained from the TLM API response when available. If not provided by the API, tokens are estimated using the formula:

```
tokens ≈ character_count / 4
```

This is a common approximation for English text. Actual token counts may vary slightly.

## Cost Calculation

Cost is calculated using the formula:

```
cost = (input_tokens / 1,000,000) × input_price + (output_tokens / 1,000,000) × output_price
```

Where prices are in USD per 1 million tokens based on the selected quality preset.

## Example Output

Console log during execution:
```
[2025-01-15 10:30:45] INFO: Using TLM quality preset: base (Input: $0.5/1M, Output: $1.7/1M)
[2025-01-15 10:30:47] INFO: TLM Token Usage - Input: 856, Output: 124, Cost: $0.000639 (Total: $0.000639)
[2025-01-15 10:30:50] INFO: TLM Token Usage - Input: 1,203, Output: 289, Cost: $0.001093 (Total: $0.001732)
[2025-01-15 10:30:53] INFO: TLM Token Usage - Input: 945, Output: 156, Cost: $0.000738 (Total: $0.002470)
```

Summary at the end:
```python
summary = agent.get_token_usage_summary()
# {
#     'total_input_tokens': 3004,
#     'total_output_tokens': 569,
#     'total_tokens': 3573,
#     'total_cost_usd': 0.002470,
#     'quality_preset': 'base',
#     'pricing': {'input_per_1m_tokens': 0.5, 'output_per_1m_tokens': 1.7}
# }
```

## Pricing Information

Current Cleanlab TLM pricing (as of implementation):

| Quality Preset | Input ($/1M tokens) | Output ($/1M tokens) | Use Case |
|---------------|---------------------|----------------------|----------|
| **base** | $0.50 | $1.70 | Simple tasks, fastest responses |
| **medium** | $1.50 | $5.00 | Balanced performance |
| **high** | $3.00 | $10.00 | Complex tasks requiring accuracy |
| **best** | $5.00 | $17.00 | Maximum quality and accuracy |

**Note**: Always verify current pricing at https://tlm.cleanlab.ai/account

## Updating Pricing

To update pricing information:

1. Edit `agentlite/config/tlm_pricing.json`
2. Update the pricing values for each quality preset
3. No code changes are needed - the agent automatically loads the config

## Skip Actions

Certain actions (like local plotting) are skipped from TLM scoring to avoid unnecessary costs:

```python
agent = TrustworthyAgent(
    name="MyAgent",
    role="Assistant",
    llm=my_llm,
    skip_trust_actions=["DrawFigure", "LocalPlot"],  # These won't incur TLM costs
)
```

## Best Practices

1. **Choose appropriate quality preset**: Start with "base" for simple tasks
2. **Monitor costs**: Check the token usage summary regularly
3. **Use skip_trust_actions**: Exclude local operations that don't need validation
4. **Analyze CSV logs**: Review token usage patterns to optimize prompts
5. **Update pricing**: Keep `tlm_pricing.json` current with latest TLM pricing

## Troubleshooting

### Config file not found
If you see a warning about missing config file, the agent will use default base pricing. Ensure `tlm_pricing.json` exists in `agentlite/config/`.

### Invalid quality preset
If an unknown quality preset is specified, the agent falls back to "base" and logs a warning.

### Token count accuracy
Token counts are estimates if not provided by the TLM API. For exact counts, check if your TLM API version returns token information in the response.
