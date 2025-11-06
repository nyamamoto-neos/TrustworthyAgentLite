# TLM Token Tracking Implementation Summary

## ✅ Implementation Complete

Token usage tracking and cost calculation has been successfully added to `TrustworthyAgent`.

---

## 📁 Files Created/Modified

### 1. Configuration File
- **`agentlite/config/tlm_pricing.json`** ⭐ NEW
  - Pricing for 4 quality presets (base, medium, high, best)
  - Easily updatable without code changes

### 2. Core Implementation
- **`agentlite/agents/TrustworthyAgent.py`** ✏️ MODIFIED
  - Added token tracking to `__init__` and `__next_act__`
  - New method: `get_token_usage_summary()`
  - Enhanced CSV logging with 3 new columns
  - Added `tlm_quality` parameter

### 3. Documentation
- **`docs/TLM_TOKEN_TRACKING.md`** ⭐ NEW
  - Comprehensive usage guide
  - Configuration details
  - Examples and best practices

- **`docs/TLM_TOKEN_TRACKING_QUICKREF.md`** ⭐ NEW
  - Quick reference guide
  - Code snippets
  - Pricing table

- **`docs/TLM_TOKEN_TRACKING_CHANGELOG.md`** ⭐ NEW
  - Detailed change log
  - Implementation details
  - Testing checklist

### 4. Examples
- **`example/tlm_token_tracking_example.py`** ⭐ NEW
  - Runnable examples
  - Multiple quality preset demos
  - Cost comparison examples

---

## 🎯 Features Implemented

### ✅ Token Tracking
- Tracks input and output tokens per TLM call
- Cumulative totals across all interactions
- Estimation fallback when API doesn't provide counts

### ✅ Cost Calculation
- Per-interaction cost calculation
- Running total cost tracking
- Quality preset-based pricing

### ✅ Quality Presets
- 4 presets: base, medium, high, best
- Configurable via JSON file
- Default fallback if config missing

### ✅ Logging
- Console logs with token usage per call
- Enhanced CSV with token/cost columns
- Usage summary API

### ✅ Backward Compatibility
- Fully compatible with existing code
- Optional parameters
- Graceful fallbacks

---

## 📊 Pricing Configuration

| Quality | Input $/1M | Output $/1M | Use Case |
|---------|-----------|-------------|----------|
| base    | $0.50     | $1.70       | Simple tasks, fastest |
| medium  | $1.50     | $5.00       | Balanced quality/cost |
| high    | $3.00     | $10.00      | Complex tasks |
| best    | $5.00     | $17.00      | Maximum accuracy |

---

## 🚀 Quick Start

```python
from agentlite.agents import TrustworthyAgent

# Create agent with token tracking
agent = TrustworthyAgent(
    name="MyAgent",
    role="Assistant",
    llm=my_llm,
    tlm_quality="base",  # Choose: base, medium, high, best
)

# Run tasks (automatic tracking)
result = agent(task)

# Get usage summary
summary = agent.get_token_usage_summary()
print(f"Tokens used: {summary['total_tokens']:,}")
print(f"Total cost: ${summary['total_cost_usd']:.6f}")
```

---

## 📈 Data Logged

### Console Output
```
[INFO] Using TLM quality preset: base (Input: $0.5/1M, Output: $1.7/1M)
[INFO] TLM Token Usage - Input: 856, Output: 124, Cost: $0.000639 (Total: $0.000639)
```

### CSV Columns Added
- `input_tokens` - Input tokens used
- `output_tokens` - Output tokens generated
- `cost_usd` - Cost for this interaction

### API Response
```python
{
    "total_input_tokens": 3004,
    "total_output_tokens": 569,
    "total_tokens": 3573,
    "total_cost_usd": 0.002470,
    "quality_preset": "base",
    "pricing": {...}
}
```

---

## 🔧 Configuration

### Location
`agentlite/config/tlm_pricing.json`

### Structure
```json
{
  "pricing": {
    "base": {
      "input_per_1m_tokens": 0.50,
      "output_per_1m_tokens": 1.70,
      "description": "..."
    }
  },
  "default_quality": "base"
}
```

### Updating Prices
1. Edit `tlm_pricing.json`
2. No code changes needed
3. Restart agents to pick up new prices

---

## 📚 Documentation

1. **Quick Start**: `docs/TLM_TOKEN_TRACKING_QUICKREF.md`
2. **Full Guide**: `docs/TLM_TOKEN_TRACKING.md`
3. **Change Log**: `docs/TLM_TOKEN_TRACKING_CHANGELOG.md`
4. **Examples**: `example/tlm_token_tracking_example.py`

---

## 🧪 Testing

Run the example script:
```bash
cd AgentLiteTLM
python example/tlm_token_tracking_example.py
```

Expected output:
- Agent initialization with quality preset
- Token usage per interaction
- Cumulative cost tracking
- Summary statistics
- Quality comparison

---

## 💡 Key Benefits

1. **Cost Transparency**: Know exactly what each TLM call costs
2. **Budget Control**: Track spending in real-time
3. **Quality Selection**: Choose appropriate preset for each task
4. **Data Analysis**: CSV logs for post-hoc analysis
5. **Easy Configuration**: Update pricing without code changes

---

## ⚠️ Important Notes

### Token Estimation
- Uses API-provided counts when available
- Falls back to `characters / 4` estimation
- Actual counts may vary slightly

### Cost Accuracy
- Based on configured pricing
- Verify current pricing at https://tlm.cleanlab.ai/account
- Update `tlm_pricing.json` as needed

### Backward Compatibility
- Existing code works without changes
- New features are optional
- Default behavior unchanged

---

## 🎓 Best Practices

1. **Start with base**: Use lowest cost for development
2. **Monitor logs**: Check console output for per-call costs
3. **Use summaries**: Call `get_token_usage_summary()` periodically
4. **Skip local actions**: Exclude operations that don't need TLM
5. **Upgrade selectively**: Use higher quality only when needed
6. **Update pricing**: Keep config current with Cleanlab's pricing

---

## 📞 Next Steps

1. Review documentation in `docs/`
2. Run example script to see it in action
3. Update `tlm_pricing.json` with current pricing
4. Integrate into your existing agents
5. Monitor token usage and costs
6. Optimize based on actual usage patterns

---

## ✨ Example Usage Summary

```python
# Initialize with quality preset
agent = TrustworthyAgent(..., tlm_quality="medium")

# Run multiple tasks
for task in tasks:
    result = agent(task)
    # Token usage logged automatically

# Get final summary
summary = agent.get_token_usage_summary()
print(f"""
Total Tokens: {summary['total_tokens']:,}
Total Cost: ${summary['total_cost_usd']:.6f}
Quality: {summary['quality_preset']}
""")
```

---

## 🔗 Resources

- **Cleanlab TLM**: https://tlm.cleanlab.ai/
- **Pricing Info**: https://tlm.cleanlab.ai/account
- **Configuration**: `agentlite/config/tlm_pricing.json`
- **Examples**: `example/tlm_token_tracking_example.py`

---

**Implementation Date**: January 15, 2025
**Status**: ✅ Complete and tested
**Version**: 1.0.0
