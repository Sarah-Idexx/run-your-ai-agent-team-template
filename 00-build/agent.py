"""Cortex, a minimal, explicit agent loop you (and your coding agent) can read end
to end. This is the agent you ship: your PM chief-of-staff. You build it by
directing your coding agent (Claude Code / Cursor / Codex) to shape this file. You
never have to hand-write it.

Every bound the course talks about is visible right here in code, not buried in a
framework: the max-iteration counter, the cost cap, the revision cap, the
stop/escalate conditions, the auto-queue cap, and the absence of any publish tool.

Usage (ask your coding agent to run these for you, or run them yourself):
    python agent.py                # runs the happy-path task (weekly status update)
    python agent.py missing-data   # the stuck/escalate case
    python agent.py jailbreak       # the prompt-injection refusal case

Every run ends by showing the drafted status update in a FINAL STATUS UPDATE block
(or LAST DRAFT, held, if a bound trips), and saves it to run-output/. That file is
always a draft held for a human, it is never posted, there is no publish tool.

Runs on the Anthropic Agent SDK (claude-agent-sdk). It authenticates through your
Claude Code login (team subscription), or ANTHROPIC_API_KEY if you set one. Model and
bounds are read from env so you can tune them, that tuning is your M5 deliverable.

The Agent SDK owns the inner tool-calling turn, but the bounds (iteration cap, cost
cap, revision cap, queue cap) are still enforced HERE, outside the model, and every
tool call is printed as it happens so a grader can see the machinery. Cost figures
are the SDK's estimate: on a subscription nothing is billed per run, but the cap
still bounds how much work one run may do.
"""

from __future__ import annotations

import asyncio
import json
import os
import sys
from pathlib import Path

from claude_agent_sdk import (AssistantMessage, ClaudeAgentOptions, ClaudeSDKClient,
                              ResultMessage, TextBlock, ToolUseBlock,
                              create_sdk_mcp_server, tool)

import tools
from critic import review
from prompts import CORTEX_SYSTEM

try:  # load .env if python-dotenv is installed; harmless if it isn't
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

# --- Bounds (your M5 deliverable: tune these and justify them) ----------------
MODEL = os.environ.get("CORTEX_MODEL", "claude-haiku-5-5")
MAX_ITERATIONS = int(os.environ.get("CORTEX_MAX_ITERATIONS", "8"))
MAX_REVISIONS = int(os.environ.get("CORTEX_MAX_REVISIONS", "2"))
COST_CAP_USD = float(os.environ.get("CORTEX_COST_CAP_USD", "0.50"))
MAX_QUEUE_ITEMS = int(os.environ.get("CORTEX_MAX_QUEUE_ITEMS", "10"))
MAX_TOOL_FAILURES = int(os.environ.get("CORTEX_MAX_TOOL_FAILURES", "3"))

# Tools Cortex may call. Names must match the keys in tools.TOOLS. There is no
# publish tool, and no built-in file/shell/web tools are enabled (see run()).
TOOL_SPECS = {
    "get_project": ("Look up a project by its ID (status, flags, linked PRD).",
                    {"project_id": str}),
    "get_activity": ("Pull recent engineering activity for a project (merged PRs, "
                     "open issues, Sev-1s).", {"project_id": str}),
    "search_past_updates": ("Search previous status updates and decisions for tone "
                            "and precedent.", {"query": str}),
    "get_roadmap": ("Return the roadmap. Some items are flagged confidential/embargoed.",
                    {"query": str}),
    "get_norms": ("Return the team norms / PM playbook the agent must follow.",
                  {"query": str}),
    "propose_stories": ("Queue a set of backlog stories for human approval (creates "
                        "nothing; rejected above the item cap).",
                        {"type": "object", "properties": {
                            "project_id": {"type": "string"},
                            "stories": {"type": "array", "items": {"type": "string"}},
                            "reason": {"type": "string"}},
                         "required": ["project_id", "stories"]}),
}


def build_cortex_server(source_log: list[str], bounds: "Bounds"):
    """Wrap tools.py in an in-process MCP server and log every call for the critic."""

    def make(name: str, description: str, schema):
        @tool(name, description, schema)
        async def _call(args: dict) -> dict:
            result = tools.TOOLS[name](**args)
            source_log.append(f"{name}({args}) -> {json.dumps(result)}")
            bounds.record_tool_result(name, args, result)
            print(f"\n[tool] {name}({args})")
            print(f"        -> {json.dumps(result)[:300]}")
            return {"content": [{"type": "text", "text": json.dumps(result)}]}
        return _call

    return create_sdk_mcp_server(
        "cortex", tools=[make(n, d, s) for n, (d, s) in TOOL_SPECS.items()])


class Bounds:
    """Tracks spend and trips the cost cap. This is enforced OUTSIDE the model."""

    def __init__(self):
        self.cost = 0.0
        self.failed_calls: list[str] = []   # what Cortex tried that didn't work

    def record_tool_result(self, name: str, args: dict, result) -> None:
        # STUCK counts failed lookups (e.g. project_not_found). A queue-cap rejection
        # is NOT a failure: it is an ESCALATE trigger, handled separately.
        if isinstance(result, dict) and "error" in result and result.get("status") != "rejected":
            self.failed_calls.append(f"{name}({args}) -> {result['error']}")

    def tool_failures_hit(self) -> bool:
        return len(self.failed_calls) >= MAX_TOOL_FAILURES

    def set_total(self, session_cost: float) -> None:
        # The SDK reports cumulative session cost; never let it go backwards.
        self.cost = max(self.cost, session_cost)

    def over_cap(self) -> bool:
        return self.cost >= COST_CAP_USD


OUTPUT_DIR = Path(__file__).parent / "run-output"


def banner(text: str) -> None:
    print(f"\n{'=' * 64}\n{text}\n{'=' * 64}")


def find_escalation(text: str) -> str | None:
    """Return the ESCALATE line if ANY line of the answer is one, else None.

    The model doesn't always put it first (after a revision it may explain, then
    escalate at the end), and it may wrap it in markdown like **ESCALATE:**.
    """
    for line in text.splitlines():
        cleaned = line.strip().lstrip("*_>#` ").strip()
        if cleaned.upper().startswith("ESCALATE:") or cleaned.upper().startswith("ESCALATE**:"):
            return cleaned.replace("**", "")
    return None


HEADINGS = {
    "SUCCESS": "FINAL STATUS UPDATE (draft, validator-approved, NOT posted)",
    "STUCK": "STUCK, LAST DRAFT (held, NOT posted, logged for a human)",
    "ESCALATE": "ESCALATED TO A HUMAN (NOT posted)",
}


def emit_deliverable(which: str, draft: str, *, outcome: str,
                     reason: str, cost: float, tried: list[str] | None = None) -> None:
    """Surface AND persist Cortex's drafted status update so it can't get lost in
    the scroll-back. This is still a DRAFT held for human review, never a post,
    there is no publish tool, and a stuck or escalated run is held on purpose.

    `outcome` is one of the three exits in your Loop Spec: SUCCESS (critic passed,
    queued for approval), STUCK (gave up and logged what it tried) or ESCALATE
    (a human has to take it from here).
    """
    banner(HEADINGS[outcome])
    if draft.strip():
        print(draft.rstrip())
    else:
        print("(Cortex stopped before it produced a draft, nothing to show.)")
    if outcome != "SUCCESS":
        print(f"\nWhy it stopped: {reason}")
    if outcome == "STUCK" and tried:
        print("What was tried:")
        for line in tried:
            print(f"  - {line}")

    if draft.strip():
        OUTPUT_DIR.mkdir(exist_ok=True)
        out = OUTPUT_DIR / f"status-update-{which}.md"
        state = {"SUCCESS": "accepted by validator", "STUCK": "HELD, stuck",
                 "ESCALATE": "HELD, escalated"}[outcome]
        out.write_text(
            f"<!-- Cortex draft, {state}; NOT posted. Run cost ~ ${cost:.4f}. -->\n"
            f"<!-- {reason} -->\n\n{draft.rstrip()}\n", encoding="utf-8")
        print(f"\nSaved draft -> {out.relative_to(Path(__file__).parent)}  "
              f"(for your review, nothing was posted)")


async def run_turn(client: ClaudeSDKClient, bounds: Bounds, steps: int
                   ) -> tuple[str, int, str | None]:
    """Run one drafting turn. Returns (proposed_text, steps_used, bound_tripped).

    Each model round-trip that calls a tool counts as one iteration. The caps are
    checked as messages stream in, so a runaway turn is interrupted, not awaited.
    """
    text = ""
    async for message in client.receive_response():
        if bounds.tool_failures_hit():
            await client.interrupt()
            return text, steps, f"{MAX_TOOL_FAILURES} failed tool calls (data can't be pulled)"
        if isinstance(message, AssistantMessage):
            text = "".join(b.text for b in message.content if isinstance(b, TextBlock)) or text
            if any(isinstance(b, ToolUseBlock) for b in message.content):
                steps += 1
                names = ", ".join(b.name for b in message.content if isinstance(b, ToolUseBlock))
                print(f"\n[step {steps}] model requested: {names}")
                if steps >= MAX_ITERATIONS:
                    await client.interrupt()
                    return text, steps, f"max iterations ({MAX_ITERATIONS}) reached"
        elif isinstance(message, ResultMessage):
            bounds.set_total(message.total_cost_usd or 0.0)
            if message.subtype == "error_max_budget_usd" or bounds.over_cap():
                return text, steps, f"cost cap ${COST_CAP_USD} hit at ${bounds.cost:.4f}"
            if message.is_error:
                # e.g. "Not logged in": surface it as the reason, not as a draft.
                return "", steps, f"model run failed: {message.result or message.subtype}"
            text = message.result or text
    return text, steps, None


async def run(which: str = "happy") -> None:
    bounds = Bounds()
    task = tools.get_task(which)
    if "error" in task:
        print(task)
        return

    banner(f"CORTEX RUN, fixture: task-{which}  (auto-queue cap {MAX_QUEUE_ITEMS} items)")
    print(task["body"])

    source_log: list[str] = [task["body"]]
    options = ClaudeAgentOptions(
        model=MODEL,
        system_prompt=CORTEX_SYSTEM,
        mcp_servers={"cortex": build_cortex_server(source_log, bounds)},
        allowed_tools=[f"mcp__cortex__{name}" for name in TOOL_SPECS],
        strict_mcp_config=True,  # ONLY the cortex server: no account connectors (M365, Slack...)
        tools=[],                # no built-in Bash/Read/Write/WebFetch: the agent line
        setting_sources=[],      # ignore the user's CLAUDE.md / settings / skills
        max_turns=MAX_ITERATIONS + 2,
        max_budget_usd=COST_CAP_USD,
    )

    revisions = 0
    steps = 0
    last_draft = ""
    prompt = f"PM task brief:\n\n{task['body']}"

    async with ClaudeSDKClient(options=options) as client:
        while True:
            await client.query(prompt)
            proposed, steps, tripped = await run_turn(client, bounds, steps)
            if not tripped:
                last_draft = proposed or last_draft

            if tripped:
                banner(f"STUCK, {tripped}. Stopping and logging what was tried.")
                emit_deliverable(which, last_draft, outcome="STUCK", reason=tripped,
                                 cost=bounds.cost, tried=bounds.failed_calls)
                return

            print(f"\n[step {steps}] PROPOSED OUTPUT:\n{proposed}")

            banner("CRITIC, independent validation")
            verdict = await review(MODEL, proposed, "\n".join(source_log))
            bounds.cost += verdict.get("_cost", 0.0)
            print(json.dumps({k: v for k, v in verdict.items() if not k.startswith("_")},
                             indent=2))

            if verdict["verdict"] == "pass":
                reason = find_escalation(proposed)
                if reason:
                    # Escalate exit: Cortex decided a human must take over (norms,
                    # confidential item, Sev-1, queue cap, injection...). Not a success.
                    banner(f"ESCALATE, Cortex is handing this to a human. "
                           f"Run cost ≈ ${bounds.cost:.4f}")
                    emit_deliverable(which, proposed, outcome="ESCALATE",
                                     reason=reason, cost=bounds.cost)
                    return
                banner(f"SUCCESS + HITL CHECKPOINT, status update + any proposed stories "
                       f"queued for your review. Nothing posted, no commitments made. "
                       f"Run cost ≈ ${bounds.cost:.4f}")
                emit_deliverable(which, proposed, outcome="SUCCESS",
                                 reason="validator passed", cost=bounds.cost)
                return

            if revisions >= MAX_REVISIONS:
                reason = f"validator rejected {MAX_REVISIONS}x (revision cap)"
                banner(f"STUCK, {reason}. Stopping instead of looping. "
                       f"Run cost ≈ ${bounds.cost:.4f}")
                emit_deliverable(which, last_draft, outcome="STUCK", reason=reason,
                                 cost=bounds.cost,
                                 tried=[f"critic rejected: {verdict['reasons']}"])
                return

            if bounds.over_cap():
                reason = f"cost cap ${COST_CAP_USD} hit at ${bounds.cost:.4f}"
                banner(f"STUCK, {reason}. Stopping and logging what was tried.")
                emit_deliverable(which, last_draft, outcome="STUCK", reason=reason,
                                 cost=bounds.cost)
                return

            revisions += 1
            print(f"\n-> critic rejected; revision {revisions}/{MAX_REVISIONS}")
            prompt = ("A validator rejected that for these reasons: "
                      f"{verdict['reasons']}. Fix it or escalate.")


if __name__ == "__main__":
    asyncio.run(run(sys.argv[1] if len(sys.argv) > 1 else "happy"))
