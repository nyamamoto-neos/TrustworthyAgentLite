# Quick Reference: Using Alternative LLM Providers

## 🚀 Quick Start

### Claude 3.5 Sonnet (Preview) - OpenRouter
```bash
# 1. Set API key
export OPENROUTER_API_KEY=sk-or-v1-your-key-here

# 2. In Python
from agentlite.llm.LLMConfig import LLMConfig
from agentlite.llm.agent_llms import get_llm_backend

config = LLMConfig({"llm_name": "openrouter/anthropic/claude-3.5-sonnet"})
llm = get_llm_backend(config)
response = llm("Hello!")
```

### DeepSeek
```bash
# 1. Set API key
export DEEPSEEK_API_KEY=sk-your-key-here

# 2. In Python
config = LLMConfig({"llm_name": "deepseek/deepseek-chat"})
llm = get_llm_backend(config)
```

## 📋 Available Models

### OpenRouter (100+ models)
```python
"openrouter/anthropic/claude-3.5-sonnet"     # Latest Claude (Preview)
"openrouter/anthropic/claude-3-opus"         # Most capable
"openrouter/anthropic/claude-3-sonnet"       # Balanced
"openrouter/anthropic/claude-3-haiku"        # Fastest
"openrouter/openai/gpt-4-turbo"              # Latest GPT-4
"openrouter/openai/gpt-3.5-turbo"            # Fast & cheap
"openrouter/google/gemini-pro"               # Google's model
"openrouter/meta-llama/llama-3.1-405b"       # Large Llama
```

Full list: https://openrouter.ai/models

### DeepSeek
```python
"deepseek/deepseek-chat"                     # Main model
"deepseek/deepseek-coder"                    # Code-specialized
```

### OpenAI (Original - no change needed)
```python
"gpt-4"                                      # Keep existing code
"gpt-3.5-turbo"                              # Works as before
```

## 🔑 Get API Keys

- **OpenRouter**: https://openrouter.ai/ (requires credits)
- **DeepSeek**: https://platform.deepseek.com/ (may have free tier)
- **OpenAI**: https://platform.openai.com/

## ⚙️ Full Configuration Options

```python
config = LLMConfig({
    "llm_name": "openrouter/anthropic/claude-3.5-sonnet",
    "temperature": 0.7,           # 0.0 to 1.0
    "max_tokens": 2000,           # Response length
    "context_len": 16000,         # Context window
    "stop_words": ["END"],        # Optional stop sequences
})
```

## 🧪 Test Your Setup

```bash
# Run test suite
python test_alternative_providers.py

# Run Claude example
python examples/example_claude_sonnet.py
```

## 🛠️ With Agents

```python
from agentlite.agents import BaseAgent
from agentlite.actions import FinishAct

# Configure LLM
config = LLMConfig({"llm_name": "openrouter/anthropic/claude-3.5-sonnet"})
llm = get_llm_backend(config)

# Create agent
agent = BaseAgent(
    name="Assistant",
    role="helpful assistant",
    llm=llm,
    actions=[FinishAct()],
)

# Use agent
from agentlite.commons import TaskPackage
task = TaskPackage(instruction="Your task here")
response = agent(task)
```

## 📊 Cost Comparison (approximate, check current rates)

| Model                          | Cost/1M tokens | Use Case           |
|--------------------------------|----------------|--------------------|
| GPT-4                          | ~$30           | Complex reasoning  |
| Claude 3.5 Sonnet              | ~$15           | Balanced           |
| GPT-3.5 Turbo                  | ~$1            | Simple tasks       |
| Claude 3 Haiku                 | ~$0.80         | Fast responses     |
| DeepSeek Chat                  | ~$0.14         | Cost-effective     |

*Prices via OpenRouter may include markup. Check https://openrouter.ai/models for current rates.*

## ❗ Troubleshooting

| Issue | Solution |
|-------|----------|
| "API key not found" | Run `export OPENROUTER_API_KEY=...` in terminal |
| "Invalid API key" | Check key format, verify credits on provider site |
| "Module not found" | Run `pip install -r requirements.txt` |
| "Model not found" | Check model name format (must include provider prefix) |
| Rate limit error | Wait or upgrade plan on provider site |

## 💡 Tips

1. **Start with free tier**: DeepSeek may offer free usage
2. **Test with cheap models first**: Use `gpt-3.5-turbo` or `claude-3-haiku`
3. **Use environment variables**: Never hardcode API keys
4. **Monitor costs**: Track usage on provider dashboards
5. **Fallback strategy**: Configure multiple providers for redundancy

## 📁 Files You Need

```
.env                              # Your API keys (don't commit!)
test_alternative_providers.py     # Test suite
examples/example_claude_sonnet.py # Usage example
OPENROUTER_DEEPSEEK_SETUP.md     # Full setup guide
```

## 🔗 Useful Links

- OpenRouter Dashboard: https://openrouter.ai/
- OpenRouter Models: https://openrouter.ai/models
- DeepSeek Platform: https://platform.deepseek.com/
- DeepSeek Docs: https://platform.deepseek.com/docs

## 📝 Environment Template

Create `.env` file:
```bash
# OpenRouter (for Claude, GPT, etc.)
OPENROUTER_API_KEY=sk-or-v1-...

# DeepSeek (optional)
DEEPSEEK_API_KEY=sk-...

# OpenAI (optional, if using direct)
OPENAI_API_KEY=sk-...
```

Load with:
```python
from dotenv import load_dotenv
load_dotenv()
```

---

**Need help?** Check `OPENROUTER_DEEPSEEK_SETUP.md` for detailed instructions.
