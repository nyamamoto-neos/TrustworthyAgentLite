"""functions or objects shared by agents"""

import re
import json

from agentlite.actions.BaseAction import BaseAction


def name_checking(name: str):
    """ensure no white space in name"""
    white_space = [" ", "\n", "\t"]
    for w in white_space:
        if w in name:
            return False
    return True


def act_match(input_act_name: str, act: BaseAction):
    if input_act_name == act.action_name:  # exact match
        return True
    ## To-Do More fuzzy match
    return False


def parse_action(string: str) -> tuple[str, dict, bool]:
    """
    Parse an action string into an action type and an argument.
    Supports both standard format: ActionName[{...}]
    and OpenRouter format: Action: ActionName[{...}]
    """

    string = string.strip(" ").strip(".").strip(":").split("\n")[0]

    # First try OpenRouter format: "Action: ActionName[{...}]"
    openrouter_pattern = r"^Action:\s*(\w+)\[(.+)\]$"
    openrouter_match = re.match(openrouter_pattern, string)

    if openrouter_match:
        action_type = openrouter_match.group(1).strip()
        arguments = openrouter_match.group(2).strip()
        try:
            arguments = json.loads(arguments)
        except json.JSONDecodeError:
            # Try a tolerant fallback: LLMs sometimes emit bare identifiers (e.g. values: [population])
            # which are invalid JSON. Attempt to quote barewords (identifiers) and parse again.
            try:
                # Insert quotes around unquoted barewords that appear as values (not object keys).
                # This is a best-effort heuristic and intentionally conservative.
                tolerant = re.sub(r'(?P<prefix>[:\[,\s])(?P<word>[A-Za-z_][A-Za-z0-9_]*)' \
                                   r'(?P<suffix>\s*(?=[,\]\}]))',
                                   r"\g<prefix>\"\g<word>\"\g<suffix>",
                                   arguments)
                arguments = json.loads(tolerant)
            except Exception:
                return string, {}, False
        return action_type, arguments, True

    # Fallback to standard format: "ActionName[{...}]"
    pattern = r"^(\w+)\[(.+)\]$"
    match = re.match(pattern, string)
    PARSE_FLAG = True

    if match:
        action_type = match.group(1).strip()
        arguments = match.group(2).strip()
        try:
            arguments = json.loads(arguments)
        except json.JSONDecodeError:
            PARSE_FLAG = False
            return string, {}, PARSE_FLAG
        return action_type, arguments, PARSE_FLAG
    else:
        PARSE_FLAG = False
        return string, {}, PARSE_FLAG


AGENT_CALL_ARG_KEY = "Task"
NO_TEAM_MEMEBER_MESS = (
    """No team member for manager agent. Please check your manager agent team."""
)
ACION_NOT_FOUND_MESS = (
    """"This is the wrong action to call. Please check your available action list."""
)
