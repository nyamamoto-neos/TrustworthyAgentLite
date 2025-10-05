from openai import OpenAI

from agentlite.llm.LLMConfig import LLMConfig

OPENAI_CHAT_MODELS = [
    "gpt-3.5-turbo",
    "gpt-3.5-turbo-16k-0613",
    "gpt-3.5-turbo-16k",
    "gpt-4",
    "gpt-4-0613",
    "gpt-4-turbo",
    "gpt-4-32k",
    "gpt-4-32k-0613",
    "gpt-4-1106-preview",
    "gpt-4.1-mini",
    "gpt-4o",
    "gpt-4o-mini",
]

# DeepSeek models
DEEPSEEK_MODELS = [
    "deepseek-chat",
    "deepseek-coder",
    "deepseek-reasoner"
]


class BaseLLM:
    def __init__(self, llm_config: LLMConfig) -> None:
        self.llm_name = llm_config.llm_name
        self.context_len: int = llm_config.context_len
        self.stop: list = llm_config.stop
        self.max_tokens: int = llm_config.max_tokens
        self.temperature: float = llm_config.temperature
        self.end_of_prompt: str = llm_config.end_of_prompt

    def __call__(self, prompt: str) -> str:
        return self.run(prompt)

    def run(self, prompt: str):
        # return str
        raise NotImplementedError


class OpenAIChatLLM(BaseLLM):
    """
    Direct OpenAI Chat API implementation (no LangChain dependency).
    Supports all OpenAI chat models including GPT-3.5, GPT-4, etc.
    """
    def __init__(self, llm_config: LLMConfig):
        super().__init__(llm_config=llm_config)
        self.client = OpenAI(
            api_key=llm_config.api_key,
            base_url=llm_config.base_url
        )

    def run(self, prompt: str):
        response = self.client.chat.completions.create(
            model=self.llm_name,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt},
            ],
            temperature=self.temperature,
            max_tokens=self.max_tokens,
        )
        return response.choices[0].message.content


def get_llm_backend(llm_config: LLMConfig):
    """
    Factory function to get the appropriate LLM backend based on provider and model name.

    Supports:
    - OpenAI models (direct OpenAI SDK, no LangChain)
    - OpenRouter (any model via OpenRouter's unified API)
    - DeepSeek (DeepSeek's native models)
    - OpenAI-compatible endpoints (custom/self-hosted)

    Provider selection (in order of precedence):
    1. Explicit provider in config: llm_config.provider
    2. Model name pattern matching (e.g., deepseek-chat -> deepseek)
    3. Default to OpenAI chat backend

    Args:
        llm_config: LLMConfig object with model name, provider, and credentials

    Returns:
        BaseLLM: Configured LLM backend instance
    """
    from agentlite.llm.openai_compatible_llm import (
        OpenRouterLLM,
        DeepSeekLLM,
        OpenAICompatibleLLM
    )

    llm_name = llm_config.llm_name
    llm_provider = llm_config.provider

    # Explicit provider selection
    if llm_provider == "openrouter":
        return OpenRouterLLM(llm_config)
    elif llm_provider == "deepseek":
        return DeepSeekLLM(llm_config)
    elif llm_provider == "openai_compatible":
        return OpenAICompatibleLLM(llm_config)

    # Model name pattern matching
    if llm_name in DEEPSEEK_MODELS:
        return DeepSeekLLM(llm_config)
    elif "/" in llm_name and llm_name not in OPENAI_CHAT_MODELS:
        # OpenRouter model naming convention: "provider/model"
        # E.g., "anthropic/claude-3.5-sonnet", "meta-llama/llama-3.1-70b"
        return OpenRouterLLM(llm_config)

    # Default: use OpenAI chat backend for all other models
    # This handles all OpenAI models and any unrecognized model names
    return OpenAIChatLLM(llm_config)