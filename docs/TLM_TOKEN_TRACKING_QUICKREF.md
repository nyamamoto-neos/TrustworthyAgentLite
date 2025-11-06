# TLM Token Tracking - Quick Reference

## Quick Start

```python
from agentlite.agents import TrustworthyAgent

# Create agent with token tracking
agent = TrustworthyAgent(
    name="MyAgent",
    role="Assistant",
    llm=my_llm,
    tlm_quality="base",  # or "medium", "high", "best"
)

# Run tasks (tokens tracked automatically)
result = agent(task)

# Get usage summary
summary = agent.get_token_usage_summary()
print(f"Total cost: ${summary['total_cost_usd']:.6f}")
```

## Quality Presets

| Preset | Input $/1M | Output $/1M | When to Use |
|--------|-----------|-------------|-------------|
| `base` | $0.50 | $1.70 | Simple tasks, cost-sensitive |
| `medium` | $1.50 | $5.00 | Balanced quality/cost |
| `high` | $3.00 | $10.00 | Complex analysis required |
| `best` | $5.00 | $17.00 | Maximum accuracy needed |

## Configuration File

Location: `agentlite/config/tlm_pricing.json`

```json
{
  "pricing": {
    "base": {
      "input_per_1m_tokens": 0.50,
      "output_per_1m_tokens": 1.70
    }
  },
  "default_quality": "base"
}
```

## CSV Output

The agent logs to CSV with these columns:
- `input_tokens`: Number of input tokens used
- `output_tokens`: Number of output tokens generated  
- `cost_usd`: Cost in USD for this interaction

## Usage Summary API

```python
summary = agent.get_token_usage_summary()

# Returns:
{
    "total_input_tokens": 3004,
    "total_output_tokens": 569, 
    "total_tokens": 3573,
    "total_cost_usd": 0.002470,
    "quality_preset": "base",
    "pricing": {
        "input_per_1m_tokens": 0.5,
        "output_per_1m_tokens": 1.7
    }
}
```

## Console Output

During execution, you'll see logs like:
```
[INFO] Using TLM quality preset: base (Input: $0.5/1M, Output: $1.7/1M)
[INFO] TLM Token Usage - Input: 856, Output: 124, Cost: $0.000639 (Total: $0.000639)
[INFO] TLM Token Usage - Input: 1,203, Output: 289, Cost: $0.001093 (Total: $0.001732)
```

## Cost Optimization Tips

1. **Start with base**: Use `base` quality for development and testing
2. **Skip local actions**: Exclude operations that don't need validation
   ```python
   skip_trust_actions=["DrawFigure", "LocalPlot"]
   ```
3. **Score strategically**: Use `score_last_only=True` to only validate final outputs
4. **Monitor CSV logs**: Analyze token usage patterns to optimize prompts
5. **Upgrade selectively**: Use higher quality presets only when needed

## Token Estimation

- API-provided counts used when available
- Fallback: ~4 characters per token
- Formula: `tokens = len(text) / 4`

## Cost Calculation

```python
cost = (input_tokens / 1_000_000) * input_price + \
       (output_tokens / 1_000_000) * output_price
```

## Example: Cost Comparison

```python
# Base: 1000 input + 200 output tokens
# Cost = (1000/1M * $0.50) + (200/1M * $1.70) = $0.00084

# High: Same tokens
# Cost = (1000/1M * $3.00) + (200/1M * $10.00) = $0.00500
# = ~6x more expensive
```

## See Also

- Full documentation: `docs/TLM_TOKEN_TRACKING.md`
- Example script: `example/tlm_token_tracking_example.py`
- Pricing updates: https://tlm.cleanlab.ai/account
