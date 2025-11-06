"""
Example script demonstrating TLM token tracking and cost calculation in TrustworthyAgent.

This script shows how to:
1. Initialize a TrustworthyAgent with a specific TLM quality preset
2. Run tasks while automatically tracking token usage
3. Retrieve and display token usage summaries
4. Analyze costs across different quality presets
"""

from agentlite.agents import TrustworthyAgent
from agentlite.llm import LLM
from agentlite.commons import TaskPackage
from agentlite.actions import ThinkAct, FinishAct

def main():
    # Initialize the base LLM
    llm = LLM()  # Replace with your actual LLM configuration

    # Example 1: Create agent with default "base" quality preset
    print("=" * 80)
    print("Example 1: Using BASE quality preset")
    print("=" * 80)

    agent_base = TrustworthyAgent(
        name="BaseAgent",
        role="Research Assistant",
        llm=llm,
        actions=[ThinkAct, FinishAct],
        tlm_quality="base",  # Lowest cost, fastest
        agent_arch="ReAct"
    )

    # Create a sample task
    task = TaskPackage(
        task_id="task_001",
        instruction="What is the capital of France?",
        ground_truth="Paris"
    )

    # Execute the task (this will automatically track tokens)
    print("\nExecuting task with BASE quality...")
    result = agent_base(task)

    # Get token usage summary
    summary_base = agent_base.get_token_usage_summary()
    print("\n" + "-" * 80)
    print("Token Usage Summary (BASE quality):")
    print("-" * 80)
    print(f"Total Input Tokens:  {summary_base['total_input_tokens']:>8,}")
    print(f"Total Output Tokens: {summary_base['total_output_tokens']:>8,}")
    print(f"Total Tokens:        {summary_base['total_tokens']:>8,}")
    print(f"Total Cost:          ${summary_base['total_cost_usd']:.6f}")
    print(f"Quality Preset:      {summary_base['quality_preset']}")
    print(f"Input Price:         ${summary_base['pricing']['input_per_1m_tokens']}/1M tokens")
    print(f"Output Price:        ${summary_base['pricing']['output_per_1m_tokens']}/1M tokens")

    # Example 2: Create agent with "high" quality preset for comparison
    print("\n" + "=" * 80)
    print("Example 2: Using HIGH quality preset")
    print("=" * 80)

    agent_high = TrustworthyAgent(
        name="HighQualityAgent",
        role="Research Assistant",
        llm=llm,
        actions=[ThinkAct, FinishAct],
        tlm_quality="high",  # Higher cost, better quality
        agent_arch="ReAct"
    )

    print("\nExecuting same task with HIGH quality...")
    result = agent_high(task)

    summary_high = agent_high.get_token_usage_summary()
    print("\n" + "-" * 80)
    print("Token Usage Summary (HIGH quality):")
    print("-" * 80)
    print(f"Total Input Tokens:  {summary_high['total_input_tokens']:>8,}")
    print(f"Total Output Tokens: {summary_high['total_output_tokens']:>8,}")
    print(f"Total Tokens:        {summary_high['total_tokens']:>8,}")
    print(f"Total Cost:          ${summary_high['total_cost_usd']:.6f}")
    print(f"Quality Preset:      {summary_high['quality_preset']}")
    print(f"Input Price:         ${summary_high['pricing']['input_per_1m_tokens']}/1M tokens")
    print(f"Output Price:        ${summary_high['pricing']['output_per_1m_tokens']}/1M tokens")

    # Example 3: Cost comparison
    print("\n" + "=" * 80)
    print("Cost Comparison")
    print("=" * 80)

    cost_increase = (summary_high['total_cost_usd'] / summary_base['total_cost_usd'] - 1) * 100
    print(f"Base Quality Cost:  ${summary_base['total_cost_usd']:.6f}")
    print(f"High Quality Cost:  ${summary_high['total_cost_usd']:.6f}")
    print(f"Cost Increase:      {cost_increase:.1f}%")

    # Example 4: Running multiple tasks and tracking cumulative costs
    print("\n" + "=" * 80)
    print("Example 3: Multiple tasks with cumulative tracking")
    print("=" * 80)

    agent_multi = TrustworthyAgent(
        name="MultiTaskAgent",
        role="General Assistant",
        llm=llm,
        actions=[ThinkAct, FinishAct],
        tlm_quality="medium",
        agent_arch="ReAct"
    )

    tasks = [
        TaskPackage(task_id="t1", instruction="What is 2+2?", ground_truth="4"),
        TaskPackage(task_id="t2", instruction="Name a programming language.", ground_truth="Python"),
        TaskPackage(task_id="t3", instruction="What color is the sky?", ground_truth="Blue"),
    ]

    print(f"\nExecuting {len(tasks)} tasks with MEDIUM quality...")
    for i, task in enumerate(tasks, 1):
        print(f"\nTask {i}/{len(tasks)}: {task.instruction}")
        result = agent_multi(task)

        # Show running totals after each task
        summary = agent_multi.get_token_usage_summary()
        print(f"  Running total - Tokens: {summary['total_tokens']:,}, Cost: ${summary['total_cost_usd']:.6f}")

    # Final summary
    final_summary = agent_multi.get_token_usage_summary()
    print("\n" + "-" * 80)
    print("Final Summary (MEDIUM quality, 3 tasks):")
    print("-" * 80)
    print(f"Total Input Tokens:  {final_summary['total_input_tokens']:>8,}")
    print(f"Total Output Tokens: {final_summary['total_output_tokens']:>8,}")
    print(f"Total Tokens:        {final_summary['total_tokens']:>8,}")
    print(f"Total Cost:          ${final_summary['total_cost_usd']:.6f}")
    print(f"Average per Task:    ${final_summary['total_cost_usd'] / len(tasks):.6f}")

    # Example 5: Quality preset comparison chart
    print("\n" + "=" * 80)
    print("Quality Preset Pricing Reference")
    print("=" * 80)
    print(f"{'Preset':<10} {'Input ($/1M)':<15} {'Output ($/1M)':<15} {'Use Case':<30}")
    print("-" * 80)

    presets = {
        "base": ("$0.50", "$1.70", "Simple tasks, fastest"),
        "medium": ("$1.50", "$5.00", "Balanced performance"),
        "high": ("$3.00", "$10.00", "Complex tasks"),
        "best": ("$5.00", "$17.00", "Maximum quality")
    }

    for preset, (inp, out, desc) in presets.items():
        print(f"{preset:<10} {inp:<15} {out:<15} {desc:<30}")

    print("\n" + "=" * 80)
    print("CSV logs with detailed token usage saved to data/ directory")
    print("=" * 80)


if __name__ == "__main__":
    main()
