"""
OpenAI-compatible LLM backends for OpenRouter, DeepSeek, and other compatible APIs.

This module provides adapters for any OpenAI-compatible API endpoint, including:
- OpenRouter (https://openrouter.ai) - unified access to multiple LLM providers
- DeepSeek (https://platform.deepseek.com) - DeepSeek's native API
- Any other service that implements the OpenAI Chat Completions API

Usage:
    Set environment variables:
    - OPENROUTER_API_KEY for OpenRouter
    - DEEPSEEK_API_KEY for DeepSeek
    - Or use OPENAI_API_KEY with custom base_url

    Configure via LLMConfig:
        config = LLMConfig({
            "provider": "openrouter",  # or "deepseek" or "openai_compatible"
            "llm_name": "anthropic/claude-3.5-sonnet",  # model identifier
            "base_url": "https://openrouter.ai/api/v1",  # optional, has defaults
            "api_key": "sk-or-v1-...",  # optional if env var is set
        })
"""

import os
from openai import OpenAI

from agentlite.llm.LLMConfig import LLMConfig
from agentlite.llm.agent_llms import BaseLLM


class OpenRouterLLM(BaseLLM):
    """
    OpenRouter backend - unified API for multiple LLM providers.

    Supports models from:
    - OpenAI (gpt-4, gpt-3.5-turbo, etc.)
    - Anthropic (claude-3-opus, claude-3-sonnet, etc.)
    - Meta (llama-3.1, etc.)
    - Google (gemini-pro, etc.)
    - And many more: https://openrouter.ai/models

    Model naming format: "provider/model-name"
    Examples:
        - "anthropic/claude-3.5-sonnet"
        - "openai/gpt-4-turbo"
        - "meta-llama/llama-3.1-70b-instruct"
        - "google/gemini-pro"

    Environment variables:
        OPENROUTER_API_KEY: Your OpenRouter API key (required)
        OPENROUTER_API_BASE: Custom base URL (optional, defaults to https://openrouter.ai/api/v1)
    """

    DEFAULT_BASE_URL = "https://openrouter.ai/api/v1"

    def __init__(self, llm_config: LLMConfig):
        super().__init__(llm_config=llm_config)

        # Get API key from config or environment
        api_key = llm_config.api_key
        if api_key == "EMPTY" or not api_key:
            api_key = os.environ.get("OPENROUTER_API_KEY")

        if not api_key:
            raise ValueError(
                "OpenRouter API key not found. Set OPENROUTER_API_KEY environment variable "
                "or pass api_key in LLMConfig."
            )

        # Get base URL from config or use default
        base_url = llm_config.base_url or os.environ.get("OPENROUTER_API_BASE", self.DEFAULT_BASE_URL)

        # OpenRouter requires HTTP-Referer and X-Title headers; allow override via env vars
        referer = os.environ.get(
            "OPENROUTER_APP_URL",
            "https://github.com/making-iot/AgentLiteTLM"
        )
        title = os.environ.get("OPENROUTER_APP_TITLE", "AgentLite")

        # Provide both Referer header variants to satisfy stricter gateways
        default_headers = {
            "HTTP-Referer": referer,
            "Referer": referer,
            "X-Title": title,
            "User-Agent": os.environ.get("OPENROUTER_USER_AGENT", "AgentLiteTLM/1.0"),
            "Accept": "application/json",
        }

        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url,
            default_headers=default_headers
        )

    def run(self, prompt: str):
        """Execute the prompt and return the response."""
        # Build request parameters - only include optional params if non-default
        request_params = {
            "model": self.llm_name,
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt},
            ],
        }

        # Only add temperature if not default (0.0)
        if self.temperature > 0:
            request_params["temperature"] = self.temperature

        # Only add max_tokens if not default (2048)
        if self.max_tokens != 2048:
            request_params["max_tokens"] = self.max_tokens

        response = self.client.chat.completions.create(**request_params)
        return response.choices[0].message.content


class DeepSeekLLM(BaseLLM):
    """
    DeepSeek backend - DeepSeek's native API.

    Supports DeepSeek models:
    - deepseek-chat (general purpose, recommended)
    - deepseek-coder (optimized for code)
    - deepseek-reasoner (for complex reasoning tasks)

    Environment variables:
        DEEPSEEK_API_KEY: Your DeepSeek API key (required)
        DEEPSEEK_API_BASE: Custom base URL (optional, defaults to https://api.deepseek.com)

    More info: https://platform.deepseek.com/api-docs/
    """

    DEFAULT_BASE_URL = "https://api.deepseek.com"

    def __init__(self, llm_config: LLMConfig):
        super().__init__(llm_config=llm_config)

        # Get API key from config or environment
        api_key = llm_config.api_key
        if api_key == "EMPTY" or not api_key:
            api_key = os.environ.get("DEEPSEEK_API_KEY")

        if not api_key:
            raise ValueError(
                "DeepSeek API key not found. Set DEEPSEEK_API_KEY environment variable "
                "or pass api_key in LLMConfig."
            )

        # Get base URL from config or use default
        base_url = llm_config.base_url or os.environ.get("DEEPSEEK_API_BASE", self.DEFAULT_BASE_URL)

        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url
        )

    def run(self, prompt: str):
        """Execute the prompt and return the response."""
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


class OpenAICompatibleLLM(BaseLLM):
    """
    Generic OpenAI-compatible backend for any API that implements the OpenAI Chat Completions format.

    Use this for:
    - Self-hosted models (vLLM, Ollama with OpenAI compatibility, etc.)
    - Custom endpoints
    - Any service with OpenAI-compatible API

    Required configuration:
        base_url: The base URL of your API endpoint
        api_key: Your API key (or "EMPTY" if not required)

    Example:
        config = LLMConfig({
            "provider": "openai_compatible",
            "llm_name": "your-model-name",
            "base_url": "http://localhost:8000/v1",
            "api_key": "not-required",  # or your actual key
        })
    """

    def __init__(self, llm_config: LLMConfig):
        super().__init__(llm_config=llm_config)

        if not llm_config.base_url:
            raise ValueError(
                "base_url is required for OpenAI-compatible backend. "
                "Set it in LLMConfig or via environment variable."
            )

        # API key might not be required for local endpoints
        api_key = llm_config.api_key or "not-required"

        self.client = OpenAI(
            api_key=api_key,
            base_url=llm_config.base_url
        )

    def run(self, prompt: str):
        """Execute the prompt and return the response."""
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
