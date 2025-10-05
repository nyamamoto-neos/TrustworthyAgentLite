"""
Example: Using Claude 3.5 Sonnet via OpenRouter

This example demonstrates how to use Claude 3.5 Sonnet (Preview) through OpenRouter.

Setup:
1. Get an API key from https://openrouter.ai/
2. Set environment variable: export OPENROUTER_API_KEY=your_key_here
3. Run this script

Note: Claude 3.5 Sonnet is currently in preview on OpenRouter
"""
import os
from agentlite.agents import ABCAgent, BaseAgent
from agentlite.actions import BaseAction, FinishAct
from agentlite.actions.InnerActions import INNER_ACT_KEY
from agentlite.llm.agent_llms import get_llm_backend
from agentlite.llm.LLMConfig import LLMConfig
from agentlite.logging.terminal_logger import AgentLogger

# Simple calculator action as example
class CalculatorAction(BaseAction):
    """A simple calculator action."""

    def __init__(self):
        action_name = "Calculator"
        action_desc = "Calculate mathematical expressions. Input should be a valid Python math expression."
        params_doc = {"expression": "a string containing a mathematical expression"}
        super().__init__(
            action_name=action_name,
            action_desc=action_desc,
            params_doc=params_doc,
        )

    def __call__(self, expression: str):
        try:
            # Safe eval with limited scope
            result = eval(expression, {"__builtins__": {}}, {})
            return f"Result: {result}"
        except Exception as e:
            return f"Error: {str(e)}"

def main():
    # Check for API key
    if not os.getenv("OPENROUTER_API_KEY"):
        print("❌ Error: OPENROUTER_API_KEY environment variable not set!")
        print("\nTo use this example:")
        print("1. Get an API key from https://openrouter.ai/")
        print("2. Run: export OPENROUTER_API_KEY=your_key_here")
        print("3. Run this script again")
        return

    print("=" * 70)
    print("Claude 3.5 Sonnet (Preview) via OpenRouter - Example")
    print("=" * 70)

    # Configure Claude 3.5 Sonnet via OpenRouter
    llm_config = LLMConfig({
        "llm_name": "openrouter/anthropic/claude-3.5-sonnet",
        "temperature": 0.7,
        "max_tokens": 2000,
        "context_len": 16000,
    })

    print(f"\n✓ Using: {llm_config.config_dict['llm_name']}")
    print(f"✓ Temperature: {llm_config.temperature}")
    print(f"✓ Max tokens: {llm_config.max_tokens}")

    # Get LLM backend
    llm = get_llm_backend(llm_config)

    # Create logger
    logger = AgentLogger()

    # Create simple agent with calculator action
    agent = BaseAgent(
        name="Claude Assistant",
        role="helpful assistant with calculator capabilities",
        llm=llm,
        actions=[CalculatorAction(), FinishAct()],
        logger=logger,
    )

    # Test with a simple task
    print("\n" + "-" * 70)
    print("Test Task: Calculate (25 * 4) + (100 / 2)")
    print("-" * 70)

    from agentlite.commons import TaskPackage

    task = TaskPackage(instruction="Calculate (25 * 4) + (100 / 2) and explain the result.")

    try:
        response = agent(task)
        print(f"\n✓ Agent Response:\n{response}")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        print("\nPossible issues:")
        print("- Check your OPENROUTER_API_KEY is valid")
        print("- Ensure you have credits on OpenRouter")
        print("- Verify network connectivity")

    print("\n" + "=" * 70)
    print("Example Complete")
    print("=" * 70)

    print("\nOther Claude models available on OpenRouter:")
    print("- openrouter/anthropic/claude-3.5-sonnet (Preview)")
    print("- openrouter/anthropic/claude-3-opus")
    print("- openrouter/anthropic/claude-3-sonnet")
    print("- openrouter/anthropic/claude-3-haiku")

    print("\nOther providers you can use:")
    print("- DeepSeek: deepseek/deepseek-chat")
    print("- OpenAI: gpt-4, gpt-3.5-turbo (via OPENAI_API_KEY)")

if __name__ == "__main__":
    main()
