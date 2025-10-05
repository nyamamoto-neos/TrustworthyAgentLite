# Alternative LLM Providers Guide

AgentLite now supports multiple LLM providers beyond OpenAI, including **OpenRouter**, **DeepSeek**, and any **OpenAI-compatible endpoint**.

**Note:** This fork has **removed LangChain dependencies** and migrated to direct OpenAI SDK usage for a lighter, faster implementation with better control over API calls.

## Table of Contents
- [Quick Start](#quick-start)
- [Supported Providers](#supported-providers)
- [Configuration Examples](#configuration-examples)
- [Environment Variables](#environment-variables)
- [Model Selection](#model-selection)
- [Advanced Usage](#advanced-usage)
- [Troubleshooting](#troubleshooting)

---

## Quick Start

### 1. Install Dependencies

All dependencies are already included in `requirements.txt`:
```bash
pip install -r requirements.txt
```

### 2. Set API Key

Choose your provider and set the appropriate environment variable:

```bash
# For OpenRouter
export OPENROUTER_API_KEY="sk-or-v1-..."

# For DeepSeek
export DEEPSEEK_API_KEY="sk-..."

# For OpenAI (default)
export OPENAI_API_KEY="sk-..."
```

### 3. Configure Your Agent

```python
from agentlite.llm.LLMConfig import LLMConfig
from agentlite.llm.agent_llms import get_llm_backend

# OpenRouter example
config = LLMConfig({
    "provider": "openrouter",
    "llm_name": "anthropic/claude-3.5-sonnet",
    "temperature": 0.7,
    "max_tokens": 2048
})

llm = get_llm_backend(config)
response = llm("What is the capital of France?")
print(response)
```

---

## Supported Providers

### 1. **OpenRouter** 🚀
Unified API for 100+ models from multiple providers.

**Advantages:**
- Single API for OpenAI, Anthropic, Meta, Google, and more
- No need to manage multiple API keys
- Transparent pricing and model selection
- Fallback options for reliability

**Website:** https://openrouter.ai

### 2. **DeepSeek** 🧠
High-performance models optimized for chat and coding.

**Advantages:**
- Specialized models for different tasks
- Competitive pricing
- Fast inference
- Strong reasoning capabilities

**Website:** https://platform.deepseek.com

### 3. **OpenAI-Compatible** 🔧
Any service implementing the OpenAI Chat Completions API.

**Use cases:**
- Self-hosted models (vLLM, Ollama with OpenAI compatibility)
- Custom inference servers
- Enterprise proxy endpoints
- Local development

---

## Configuration Examples

### OpenRouter Configuration

#### Basic Usage
```python
from agentlite.llm.LLMConfig import LLMConfig
from agentlite.llm.agent_llms import get_llm_backend

config = LLMConfig({
    "provider": "openrouter",
    "llm_name": "anthropic/claude-3.5-sonnet",  # Model from OpenRouter catalog
})

llm = get_llm_backend(config)
```

#### Available Models (Examples)
```python
# Anthropic models
"anthropic/claude-3.5-sonnet"
"anthropic/claude-3-opus"
"anthropic/claude-3-haiku"

# Meta models
"meta-llama/llama-3.1-70b-instruct"
"meta-llama/llama-3.1-8b-instruct"

# Google models
"google/gemini-pro"
"google/gemini-pro-1.5"

# OpenAI models (via OpenRouter)
"openai/gpt-4-turbo"
"openai/gpt-3.5-turbo"

# And many more: https://openrouter.ai/models
```

#### With Custom Settings
```python
import os

config = LLMConfig({
    "provider": "openrouter",
    "llm_name": "anthropic/claude-3.5-sonnet",
    "api_key": os.getenv("OPENROUTER_API_KEY"),  # Explicit key
    "base_url": "https://openrouter.ai/api/v1",   # Custom endpoint (optional)
    "temperature": 0.7,
    "max_tokens": 4096,
    "stop": ["\n\n", "Human:", "Assistant:"]
})
```

### DeepSeek Configuration

#### Basic Usage
```python
config = LLMConfig({
    "provider": "deepseek",
    "llm_name": "deepseek-chat",  # General-purpose model
})

llm = get_llm_backend(config)
```

#### Available Models
```python
# General chat model (recommended)
"deepseek-chat"

# Optimized for code generation
"deepseek-coder"

# Enhanced reasoning capabilities
"deepseek-reasoner"
```

#### With Custom Settings
```python
config = LLMConfig({
    "provider": "deepseek",
    "llm_name": "deepseek-coder",
    "temperature": 0.3,  # Lower for code generation
    "max_tokens": 8192,
})
```

### OpenAI-Compatible Configuration

#### Local vLLM Server
```python
config = LLMConfig({
    "provider": "openai_compatible",
    "llm_name": "meta-llama/Llama-3.1-8B-Instruct",
    "base_url": "http://localhost:8000/v1",
    "api_key": "not-required",  # Local server might not need auth
})
```

#### Ollama with OpenAI Compatibility
```bash
# Start Ollama with OpenAI-compatible endpoint
ollama serve
```

```python
config = LLMConfig({
    "provider": "openai_compatible",
    "llm_name": "llama3.1:8b",
    "base_url": "http://localhost:11434/v1",
    "api_key": "ollama",
})
```

---

## Environment Variables

### Priority Order
1. Explicit `api_key` in `LLMConfig`
2. Provider-specific environment variable
3. Fallback to `OPENAI_API_KEY`

### All Supported Variables

```bash
# OpenAI (default provider)
export OPENAI_API_KEY="sk-..."
export OPENAI_API_BASE="https://api.openai.com/v1"  # Optional

# OpenRouter
export OPENROUTER_API_KEY="sk-or-v1-..."
export OPENROUTER_API_BASE="https://openrouter.ai/api/v1"  # Optional

# DeepSeek
export DEEPSEEK_API_KEY="sk-..."
export DEEPSEEK_API_BASE="https://api.deepseek.com"  # Optional
```

### .env File Example

Create a `.env` file in your project root:

```bash
# Choose one or more providers

# OpenRouter (recommended for variety)
OPENROUTER_API_KEY=sk-or-v1-your-key-here

# DeepSeek (recommended for performance)
DEEPSEEK_API_KEY=sk-your-key-here

# OpenAI (default)
OPENAI_API_KEY=sk-your-key-here
```

Load it in your code:
```python
from dotenv import load_dotenv
load_dotenv()  # Loads .env file
```

---

## Model Selection

### Auto-Detection

The system automatically detects the provider based on model name patterns:

```python
# These automatically use OpenRouter (model name contains "/")
config = LLMConfig({"llm_name": "anthropic/claude-3.5-sonnet"})
config = LLMConfig({"llm_name": "meta-llama/llama-3.1-70b"})

# These automatically use DeepSeek
config = LLMConfig({"llm_name": "deepseek-chat"})
config = LLMConfig({"llm_name": "deepseek-coder"})

# These use OpenAI (default)
config = LLMConfig({"llm_name": "gpt-4-turbo"})
config = LLMConfig({"llm_name": "gpt-3.5-turbo"})
```

### Explicit Provider Override

```python
# Force OpenRouter even for OpenAI model names
config = LLMConfig({
    "provider": "openrouter",
    "llm_name": "openai/gpt-4-turbo"  # Via OpenRouter
})

# Force OpenAI-compatible for custom endpoints
config = LLMConfig({
    "provider": "openai_compatible",
    "llm_name": "custom-model",
    "base_url": "http://your-server/v1"
})
```

---

## Advanced Usage

### Multi-Agent System with Different Providers

```python
from agentlite.agents.BaseAgent import BaseAgent
from agentlite.llm.LLMConfig import LLMConfig
from agentlite.llm.agent_llms import get_llm_backend

# Agent 1: Uses Claude for reasoning
reasoning_config = LLMConfig({
    "provider": "openrouter",
    "llm_name": "anthropic/claude-3.5-sonnet",
    "temperature": 0.7
})
reasoning_llm = get_llm_backend(reasoning_config)

# Agent 2: Uses DeepSeek Coder for code generation
coding_config = LLMConfig({
    "provider": "deepseek",
    "llm_name": "deepseek-coder",
    "temperature": 0.3,
    "max_tokens": 4096
})
coding_llm = get_llm_backend(coding_config)

# Agent 3: Uses GPT-4 for final review
review_config = LLMConfig({
    "llm_name": "gpt-4-turbo",
    "temperature": 0.5
})
review_llm = get_llm_backend(review_config)

# Create agents with different LLMs
# reasoning_agent = BaseAgent(..., llm=reasoning_llm)
# coding_agent = BaseAgent(..., llm=coding_llm)
# review_agent = BaseAgent(..., llm=review_llm)
```

### Cost Optimization

```python
# Use cheaper models for simple tasks
simple_config = LLMConfig({
    "provider": "openrouter",
    "llm_name": "meta-llama/llama-3.1-8b-instruct",  # Cheaper
    "temperature": 0.7
})

# Use powerful models for complex reasoning
complex_config = LLMConfig({
    "provider": "openrouter",
    "llm_name": "anthropic/claude-3-opus",  # More expensive but better
    "temperature": 0.8
})
```

### Fallback Strategy

```python
def create_llm_with_fallback():
    """Try primary provider, fall back to alternatives."""
    providers = [
        {
            "provider": "deepseek",
            "llm_name": "deepseek-chat",
        },
        {
            "provider": "openrouter",
            "llm_name": "anthropic/claude-3-haiku",
        },
        {
            "llm_name": "gpt-3.5-turbo",  # OpenAI fallback
        }
    ]

    for config_dict in providers:
        try:
            config = LLMConfig(config_dict)
            llm = get_llm_backend(config)
            # Test the connection
            llm("test")
            return llm
        except Exception as e:
            print(f"Failed to initialize {config_dict}: {e}")
            continue

    raise RuntimeError("All LLM providers failed")
```

---

## Troubleshooting

### Common Issues

#### 1. API Key Not Found
```
ValueError: OpenRouter API key not found. Set OPENROUTER_API_KEY...
```

**Solution:**
```bash
export OPENROUTER_API_KEY="your-key-here"
# Or set it explicitly in LLMConfig
```

#### 2. Import Errors
```
ImportError: cannot import name 'OpenRouterLLM'
```

**Solution:**
Ensure you're running the latest version with the new providers:
```bash
pip install -e .  # Reinstall in development mode
```

#### 3. Model Not Found
```
openai.NotFoundError: 404 model 'anthropic/claude-3.5-sonnet' not found
```

**Solution:**
- Check model name on provider's website
- Ensure you're using the correct provider setting
- Verify your API key has access to the model

#### 4. Rate Limiting
```
openai.RateLimitError: Rate limit exceeded
```

**Solution:**
- Implement retry logic with exponential backoff
- Use `temperature` and `max_tokens` to reduce costs
- Consider switching providers temporarily

### Debugging Tips

#### Enable Verbose Logging
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

#### Test Connection
```python
config = LLMConfig({
    "provider": "openrouter",
    "llm_name": "anthropic/claude-3-haiku",  # Fast, cheap model for testing
})

llm = get_llm_backend(config)
try:
    response = llm("Say hello")
    print(f"Success: {response}")
except Exception as e:
    print(f"Error: {e}")
```

#### Check Base URL
```python
config = LLMConfig({
    "provider": "openrouter",
    "llm_name": "anthropic/claude-3.5-sonnet"
})
print(f"Base URL: {config.base_url or 'default'}")
print(f"API Key present: {bool(config.api_key and config.api_key != 'EMPTY')}")
```

---

## Performance Comparison

| Provider | Speed | Cost | Quality | Best For |
|----------|-------|------|---------|----------|
| **OpenAI GPT-4** | Medium | High | Excellent | Complex reasoning, production |
| **OpenRouter/Claude** | Medium | High | Excellent | Long context, analysis |
| **DeepSeek Chat** | Fast | Low | Good | General chat, high volume |
| **DeepSeek Coder** | Fast | Low | Excellent | Code generation |
| **OpenRouter/Llama** | Fast | Low | Good | Simple tasks, experimentation |

---

## Getting API Keys

### OpenRouter
1. Visit https://openrouter.ai
2. Sign up for an account
3. Go to Keys page: https://openrouter.ai/keys
4. Create a new key
5. Add credits: https://openrouter.ai/credits

### DeepSeek
1. Visit https://platform.deepseek.com
2. Sign up for an account
3. Navigate to API Keys section
4. Create a new key
5. Add credits to your account

---

## Migration Guide

### From OpenAI to OpenRouter

**Before:**
```python
config = LLMConfig({
    "llm_name": "gpt-4",
    "api_key": os.getenv("OPENAI_API_KEY")
})
```

**After:**
```python
config = LLMConfig({
    "provider": "openrouter",
    "llm_name": "openai/gpt-4",  # Same model via OpenRouter
    "api_key": os.getenv("OPENROUTER_API_KEY")
})

# Or use a different model with similar capabilities
config = LLMConfig({
    "provider": "openrouter",
    "llm_name": "anthropic/claude-3.5-sonnet",
})
```

### From OpenAI to DeepSeek

**Before:**
```python
config = LLMConfig({
    "llm_name": "gpt-3.5-turbo",
})
```

**After:**
```python
config = LLMConfig({
    "provider": "deepseek",
    "llm_name": "deepseek-chat",  # Similar performance, lower cost
})
```

---

## Support

For issues specific to:
- **AgentLite integration**: Open an issue on GitHub
- **OpenRouter API**: https://openrouter.ai/docs
- **DeepSeek API**: https://platform.deepseek.com/docs

---

## License

This extension maintains the same license as the main AgentLite project.
