# OpenRouter & DeepSeek Setup Guide

Complete guide to using OpenRouter (for Claude 3.5 Sonnet and 100+ other models) and DeepSeek with TrustworthyAgentLite.

## Table of Contents
- [Quick Start](#quick-start)
- [OpenRouter Setup](#openrouter-setup)
- [DeepSeek Setup](#deepseek-setup)
- [Configuration](#configuration)
- [Usage Examples](#usage-examples)
- [Troubleshooting](#troubleshooting)

---

## Quick Start

### 1. Get API Key
Visit [OpenRouter](https://openrouter.ai/) and create an account to get your API key.

### 2. Set Environment Variable
```bash
export OPENROUTER_API_KEY=sk-or-v1-your-key-here
```

### 3. Use in Code
```python
from agentlite.llm.LLMConfig import LLMConfig
from agentlite.llm.agent_llms import get_llm_backend

config = LLMConfig({
    "llm_name": "openrouter/anthropic/claude-3.5-sonnet"
})
llm = get_llm_backend(config)
response = llm("Hello, Claude!")
print(response)
```

That's it! You're now using Claude 3.5 Sonnet (Preview).

---

## OpenRouter Setup

### Step 1: Create Account
1. Visit https://openrouter.ai/
2. Sign up for an account
3. Add credits to your account (required for usage)

### Step 2: Get API Key
1. Go to https://openrouter.ai/keys
2. Create a new API key
3. Copy the key (starts with `sk-or-v1-...`)

### Step 3: Configure Environment
```bash
# Option A: Export in terminal (temporary)
export OPENROUTER_API_KEY=sk-or-v1-your-key-here

# Option B: Add to ~/.zshrc or ~/.bashrc (permanent)
echo 'export OPENROUTER_API_KEY=sk-or-v1-your-key-here' >> ~/.zshrc
source ~/.zshrc

# Option C: Use .env file (recommended for projects)
echo 'OPENROUTER_API_KEY=sk-or-v1-your-key-here' >> .env
```

### Step 4: Install Dependencies (if not done)
```bash
conda activate TLM
pip install -r requirements.txt
```

### Step 5: Test Installation
```bash
python test_alternative_providers.py
```

### Available Models via OpenRouter

#### Claude Models (Anthropic)
```python
"openrouter/anthropic/claude-3.5-sonnet"  # Latest (Preview)
"openrouter/anthropic/claude-3-opus"      # Most capable
"openrouter/anthropic/claude-3-sonnet"    # Balanced
"openrouter/anthropic/claude-3-haiku"     # Fastest & cheapest
```

#### OpenAI Models
```python
"openrouter/openai/gpt-4-turbo"
"openrouter/openai/gpt-4"
"openrouter/openai/gpt-3.5-turbo"
```

#### Google Models
```python
"openrouter/google/gemini-pro"
"openrouter/google/gemini-pro-vision"
```

#### Meta (Llama) Models
```python
"openrouter/meta-llama/llama-3.1-405b-instruct"
"openrouter/meta-llama/llama-3.1-70b-instruct"
"openrouter/meta-llama/llama-3.1-8b-instruct"
```

#### Other Popular Models
```python
"openrouter/mistralai/mixtral-8x7b-instruct"
"openrouter/cohere/command-r-plus"
"openrouter/anthropic/claude-2.1"
```

**Full list**: https://openrouter.ai/models

---

## DeepSeek Setup

### Step 1: Create Account
1. Visit https://platform.deepseek.com/
2. Sign up for an account
3. Verify your email

### Step 2: Get API Key
1. Go to API Keys section
2. Create a new API key
3. Copy the key (starts with `sk-...`)

### Step 3: Configure Environment
```bash
# Export in terminal
export DEEPSEEK_API_KEY=sk-your-key-here

# Or add to ~/.zshrc
echo 'export DEEPSEEK_API_KEY=sk-your-key-here' >> ~/.zshrc
source ~/.zshrc

# Or use .env file
echo 'DEEPSEEK_API_KEY=sk-your-key-here' >> .env
```

### Step 4: Test
```bash
python test_alternative_providers.py
```

### Available DeepSeek Models
```python
"deepseek/deepseek-chat"     # General purpose
"deepseek/deepseek-coder"    # Code-specialized
```

---

## Configuration

### Basic Configuration
```python
from agentlite.llm.LLMConfig import LLMConfig

config = LLMConfig({
    "llm_name": "openrouter/anthropic/claude-3.5-sonnet"
})
```

### Full Configuration Options
```python
config = LLMConfig({
    "llm_name": "openrouter/anthropic/claude-3.5-sonnet",
    "temperature": 0.7,           # 0.0 (deterministic) to 1.0 (creative)
    "max_tokens": 2000,           # Maximum response length
    "context_len": 16000,         # Context window size
    "stop_words": ["END", "STOP"], # Optional stop sequences
})
```

### Environment Variables

#### OpenRouter
```bash
OPENROUTER_API_KEY=sk-or-v1-...          # Required
OPENROUTER_API_BASE=https://openrouter.ai/api/v1  # Optional (default shown)
```

#### DeepSeek
```bash
DEEPSEEK_API_KEY=sk-...                  # Required
DEEPSEEK_API_BASE=https://api.deepseek.com  # Optional (default shown)
```

#### OpenAI (for backward compatibility)
```bash
OPENAI_API_KEY=sk-...                    # Required for OpenAI models
OPENAI_API_BASE=https://api.openai.com/v1  # Optional
```

### Using .env File (Recommended)

Create `.env` file:
```bash
# Copy from template
cp .env.example .env

# Edit with your keys
nano .env
```

Load in Python:
```python
from dotenv import load_dotenv
load_dotenv()

# Now environment variables are available
```

---

## Usage Examples

### Example 1: Simple Text Generation
```python
from agentlite.llm.LLMConfig import LLMConfig
from agentlite.llm.agent_llms import get_llm_backend

# Configure Claude 3.5 Sonnet
config = LLMConfig({
    "llm_name": "openrouter/anthropic/claude-3.5-sonnet",
    "temperature": 0.7
})

llm = get_llm_backend(config)

# Generate response
prompt = "Explain quantum computing in simple terms."
response = llm(prompt)
print(response)
```

### Example 2: Using with Agent
```python
from agentlite.agents import BaseAgent
from agentlite.actions import FinishAct
from agentlite.commons import TaskPackage
from agentlite.logging.terminal_logger import AgentLogger

# Configure LLM
config = LLMConfig({
    "llm_name": "openrouter/anthropic/claude-3.5-sonnet"
})
llm = get_llm_backend(config)

# Create agent
agent = BaseAgent(
    name="Claude Assistant",
    role="helpful AI assistant",
    llm=llm,
    actions=[FinishAct()],
    logger=AgentLogger()
)

# Execute task
task = TaskPackage(
    instruction="Analyze the pros and cons of renewable energy."
)
response = agent(task)
print(response)
```

### Example 3: Switching Providers
```python
# Try Claude first
config_claude = LLMConfig({
    "llm_name": "openrouter/anthropic/claude-3.5-sonnet"
})

# Fallback to GPT-4 if needed
config_gpt4 = LLMConfig({
    "llm_name": "openrouter/openai/gpt-4"
})

# Or use DeepSeek for cost-effectiveness
config_deepseek = LLMConfig({
    "llm_name": "deepseek/deepseek-chat"
})

# Easy to switch!
llm = get_llm_backend(config_claude)
```

### Example 4: Custom Actions with Claude
```python
from agentlite.actions import BaseAction

class ResearchAction(BaseAction):
    def __init__(self):
        super().__init__(
            action_name="Research",
            action_desc="Search for information on a topic",
            params_doc={"topic": "the topic to research"}
        )

    def __call__(self, topic: str):
        # Your research logic here
        return f"Research results for: {topic}"

# Use with Claude
config = LLMConfig({
    "llm_name": "openrouter/anthropic/claude-3.5-sonnet"
})
llm = get_llm_backend(config)

agent = BaseAgent(
    name="Research Assistant",
    role="research expert",
    llm=llm,
    actions=[ResearchAction(), FinishAct()]
)
```

### Example 5: Streaming (if supported)
```python
config = LLMConfig({
    "llm_name": "openrouter/anthropic/claude-3.5-sonnet",
    "stream": True  # Enable streaming
})
llm = get_llm_backend(config)

# Streaming will work if the backend supports it
for chunk in llm.stream("Tell me a story"):
    print(chunk, end="", flush=True)
```

---

## Troubleshooting

### Error: "API key not found"

**Problem**: Environment variable not set

**Solutions**:
```bash
# Check if variable is set
echo $OPENROUTER_API_KEY

# If empty, set it
export OPENROUTER_API_KEY=sk-or-v1-your-key-here

# Verify it's set
echo $OPENROUTER_API_KEY

# Make sure to set it in the same terminal where you run Python
```

### Error: "Invalid API key"

**Problem**: API key is incorrect or doesn't have credits

**Solutions**:
1. Verify key format (should start with `sk-or-v1-` for OpenRouter)
2. Check you have credits at https://openrouter.ai/
3. Generate a new API key if needed
4. Ensure no extra spaces in the key

### Error: "Module not found: langchain"

**Problem**: Dependencies not installed

**Solution**:
```bash
conda activate TLM
pip install -r requirements.txt
```

### Error: "Model not found"

**Problem**: Incorrect model name format

**Solutions**:
1. Verify model name includes provider prefix: `openrouter/` or `deepseek/`
2. Check model is available: https://openrouter.ai/models
3. Example correct formats:
   - ✅ `openrouter/anthropic/claude-3.5-sonnet`
   - ❌ `claude-3.5-sonnet` (missing prefix)
   - ❌ `anthropic/claude-3.5-sonnet` (wrong prefix)

### Error: "Rate limit exceeded"

**Problem**: Too many requests

**Solutions**:
1. Wait a few seconds before retrying
2. Check your rate limits on the provider dashboard
3. Upgrade your plan if needed
4. Implement exponential backoff in your code

### Error: "Insufficient credits"

**Problem**: No credits on OpenRouter account

**Solutions**:
1. Visit https://openrouter.ai/
2. Go to Credits section
3. Add credits to your account
4. Retry your request

### Connection Issues

**Problem**: Cannot connect to API

**Solutions**:
```bash
# Test network connectivity
curl https://openrouter.ai/api/v1/models

# Check if API base URL is correct
echo $OPENROUTER_API_BASE

# Try with explicit base URL
export OPENROUTER_API_BASE=https://openrouter.ai/api/v1
```

### Import Errors

**Problem**: Cannot import modules

**Solution**:
```bash
# Ensure you're in the right directory
cd /path/to/TrustworthyAgentLite-main

# Install in development mode
pip install -e .

# Or add to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:/path/to/TrustworthyAgentLite-main"
```

---

## Testing Your Setup

### Run Test Suite
```bash
# Set API keys first
export OPENROUTER_API_KEY=sk-or-v1-your-key
export DEEPSEEK_API_KEY=sk-your-key

# Run tests
python test_alternative_providers.py
```

### Expected Output
```
============================================================
Testing Alternative LLM Provider Support
============================================================

=== Testing Configuration Options ===
✓ Minimal config works
✓ Full config works

=== Testing OpenAI Compatibility ===
✓ OpenAI backend created
✓ Existing OpenAI integration preserved

=== Testing OpenRouter ===
✓ OpenRouter backend created: OpenAICompatibleLLM
✓ Response: Hello from OpenRouter...

=== Testing DeepSeek ===
✓ DeepSeek backend created: OpenAICompatibleLLM
✓ Response: Hello from DeepSeek...

============================================================
Testing Complete
============================================================
```

### Run Claude Example
```bash
export OPENROUTER_API_KEY=sk-or-v1-your-key
python examples/example_claude_sonnet.py
```

---

## Best Practices

### 1. Never Hardcode API Keys
```python
# ❌ Bad
config = LLMConfig({"api_key": "sk-or-v1-hardcoded"})

# ✅ Good
import os
api_key = os.getenv("OPENROUTER_API_KEY")
```

### 2. Use .env for Projects
```bash
# Create .env file (don't commit to git!)
echo '.env' >> .gitignore
echo 'OPENROUTER_API_KEY=sk-or-v1-...' >> .env

# Load in Python
from dotenv import load_dotenv
load_dotenv()
```

### 3. Handle Errors Gracefully
```python
try:
    llm = get_llm_backend(config)
    response = llm(prompt)
except Exception as e:
    print(f"Error: {e}")
    # Fallback to another provider
    config_fallback = LLMConfig({"llm_name": "gpt-3.5-turbo"})
    llm = get_llm_backend(config_fallback)
```

### 4. Monitor Costs
- Check usage on provider dashboards
- Set spending limits
- Use cheaper models for testing
- Cache responses when possible

### 5. Test Locally First
```python
# Use cheap model for testing
config_test = LLMConfig({
    "llm_name": "openrouter/anthropic/claude-3-haiku"  # Cheapest
})

# Switch to powerful model for production
config_prod = LLMConfig({
    "llm_name": "openrouter/anthropic/claude-3.5-sonnet"
})
```

---

## Additional Resources

### Documentation
- **OpenRouter Docs**: https://openrouter.ai/docs
- **OpenRouter Models**: https://openrouter.ai/models
- **DeepSeek Docs**: https://platform.deepseek.com/docs
- **Quick Reference**: See `QUICK_REFERENCE.md`

### Support
- **OpenRouter Discord**: https://discord.gg/openrouter
- **DeepSeek Support**: https://platform.deepseek.com/support

### Pricing
- **OpenRouter Pricing**: https://openrouter.ai/models (varies by model)
- **DeepSeek Pricing**: https://platform.deepseek.com/pricing

---

## Summary

You now have:
- ✅ OpenRouter integrated (100+ models)
- ✅ DeepSeek integrated
- ✅ Claude 3.5 Sonnet (Preview) enabled
- ✅ Easy provider switching
- ✅ Backward compatibility maintained

**Next**: Check out `QUICK_REFERENCE.md` for quick usage patterns!
