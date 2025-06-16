import re
import numpy as np
from textwrap import dedent

CONFIDENCE_PROMPT = """Interaction:
{full_prompt_and_actions}

Finish action:
{finish_action}

Instruction:
Evaluate whether the Finish action's "response" correctly and completely answers the task described in the Interaction.

Output (strictly):
Explanation: [one- or two-sentence rationale]
Correct: [Yes or No]"""

def construct_confidence_prompt(full_prompt_and_actions, finish_action):
    """Construct a confidence evaluation prompt for self-evaluation scoring.
    
    Args:
        full_prompt_and_actions: The full interaction including prompt and actions
        finish_action: The finish action to evaluate
        
    Returns:
        str: Formatted confidence evaluation prompt
    """
    template = f"""Interaction:
        {full_prompt_and_actions}

        Finish action:
        {finish_action}

        Instruction:
        Evaluate whether the Finish action's "response" correctly and completely answers the task described in the Interaction.

        Output (strictly):
        Explanation: [one- or two-sentence rationale]
        Correct: [Yes or No]"""
    return dedent(template)

def parse_self_eval_score(text: str):
    """Parse the self-evaluation score from the LLM response.
    
    Args:
        text: The LLM response containing the confidence evaluation
        
    Returns:
        float: Confidence score (1.0 for "Yes", 0.0 for "No") or np.nan if parsing fails
    """
    try:
        # Look for "Correct: Yes" or "Correct: No" pattern
        if "Correct: Yes" in text or "correct: yes" in text.lower():
            return 1.0
        elif "Correct: No" in text or "correct: no" in text.lower():
            return 0.0
        else:
            return np.nan
    except:
        return np.nan

def get_self_eval_score(llm, full_prompt_and_actions, finish_action):
    """Get self-evaluation confidence score using the provided LLM.
    
    Args:
        llm: The language model to use for self-evaluation
        full_prompt_and_actions: The full interaction including prompt and actions
        finish_action: The finish action to evaluate
        
    Returns:
        float: Confidence score (1.0 for correct, 0.0 for incorrect) or np.nan if evaluation fails
    """
    try:
        confidence_prompt = construct_confidence_prompt(full_prompt_and_actions, finish_action)
        eval_response = llm(confidence_prompt)
        return parse_self_eval_score(eval_response)
    except Exception as e:
        print(f"Error in self-evaluation: {e}")
        return np.nan 