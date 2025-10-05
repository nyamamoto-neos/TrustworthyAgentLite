import os


class LLMConfig:
    """
    Configuration class for LLM backends in the multi-agent system.

    Supports multiple providers:
    - OpenAI (default): Standard OpenAI models
    - OpenRouter: Unified API for multiple providers (Anthropic, Meta, Google, etc.)
    - DeepSeek: DeepSeek's native models (chat, coder, reasoner)
    - OpenAI-compatible: Any custom endpoint with OpenAI-compatible API

    Configuration options:
        llm_name (str): Model identifier
            - For OpenAI: "gpt-4", "gpt-3.5-turbo", etc.
            - For OpenRouter: "anthropic/claude-3.5-sonnet", "meta-llama/llama-3.1-70b", etc.
            - For DeepSeek: "deepseek-chat", "deepseek-coder", "deepseek-reasoner"
            - For custom: any model name your endpoint supports

        provider (str, optional): Explicit provider selection
            - "openrouter": Use OpenRouter API
            - "deepseek": Use DeepSeek API
            - "openai_compatible": Use custom OpenAI-compatible endpoint
            - None: Auto-detect from model name or default to OpenAI

        api_key (str): API key for the provider
            - Can be set via environment variables:
              - OPENAI_API_KEY (OpenAI/default)
              - OPENROUTER_API_KEY (OpenRouter)
              - DEEPSEEK_API_KEY (DeepSeek)

        base_url (str, optional): Custom API endpoint
            - OpenRouter: https://openrouter.ai/api/v1 (default)
            - DeepSeek: https://api.deepseek.com (default)
            - Custom: your endpoint URL

        temperature (float): Sampling temperature (0.0-1.0, default: 0.9)
        max_tokens (int): Maximum tokens in response (default: 256)
        stop (list): Stop sequences (default: ["\\n"])
        context_len (int, optional): Context window size
        end_of_prompt (str): Prompt terminator string

    Examples:
        # OpenAI (default)
        config = LLMConfig({
            "llm_name": "gpt-4-turbo",
            "api_key": "sk-..."
        })

        # OpenRouter with Claude
        config = LLMConfig({
            "provider": "openrouter",
            "llm_name": "anthropic/claude-3.5-sonnet",
            "api_key": "sk-or-v1-..."
        })

        # DeepSeek
        config = LLMConfig({
            "provider": "deepseek",
            "llm_name": "deepseek-chat"
            # Uses DEEPSEEK_API_KEY from environment
        })

        # Custom endpoint
        config = LLMConfig({
            "provider": "openai_compatible",
            "llm_name": "your-model",
            "base_url": "http://localhost:8000/v1",
            "api_key": "not-required"
        })
    """

    def __init__(self, config_dict: dict) -> None:
        self.config_dict = config_dict
        self.context_len = None
        self.llm_name = "gpt-3.5-turbo"
        self.temperature = 0.9
        self.stop = ["\n"]
        self.max_tokens = 256
        self.end_of_prompt = ""
        self.api_key: str = os.environ.get("OPENAI_API_KEY", "EMPTY")
        self.base_url = None
        self.provider = None
        self.__dict__.update(config_dict)
