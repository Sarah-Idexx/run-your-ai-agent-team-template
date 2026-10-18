"""Independent validator (M3). A separate model call that never saw the drafting
context, so it can't inherit the draft's blind spots. Returns a pass/fail verdict.
The revision cap that stops a critic<->drafter loop lives in `agent.py`.
"""

from __future__ import annotations

import json
import re

from claude_agent_sdk import ClaudeAgentOptions, ResultMessage, query

from prompts import CRITIC_SYSTEM


async def review(model: str, proposed_output: str, source_data: str) -> dict:
    """Return {"verdict": "pass"|"fail", "reasons": [...]} for a proposed output."""
    options = ClaudeAgentOptions(
        model=model,
        system_prompt=CRITIC_SYSTEM,
        tools=[],              # the critic reads what it is given, it can do nothing
        setting_sources=[],
        max_turns=3,
    )
    prompt = (f"SOURCE DATA Cortex used:\n{source_data}\n\n"
              f"CORTEX PROPOSED OUTPUT:\n{proposed_output}\n\n"
              'Reply with ONLY a JSON object: {"verdict": "pass"|"fail", "reasons": [...]}')

    text, cost = "", 0.0
    async for message in query(prompt=prompt, options=options):
        if isinstance(message, ResultMessage):
            text = message.result or ""
            cost = message.total_cost_usd or 0.0

    try:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        verdict = json.loads(match.group(0))
        if verdict.get("verdict") not in ("pass", "fail"):
            raise ValueError("bad verdict")
    except (AttributeError, json.JSONDecodeError, ValueError):
        verdict = {"verdict": "fail", "reasons": ["critic returned unparseable output"]}
    verdict["_cost"] = cost
    return verdict
