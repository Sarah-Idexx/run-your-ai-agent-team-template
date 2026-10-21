"""Force a bad draft through the critic (M3, Step 4).

Cortex behaves well, so it won't write a bad draft on request. This script PLANTS one
(the draft below is written by hand, NOT by Cortex) and sends it through the real
critic and the real fail-action, so you can see the critic reject it and the
escalation fire. The source data is real: it is pulled with Cortex's own tools.

Usage:
    python force_failure.py

The planted draft breaks all five rules in the Orchestration Map's validator:
  1. Correct IDs          cites PR #899, which does not exist
  2. Traceable figures    invents a 63% activation rate
  3. No commitments       promises "GA on 15 November"
  4. No confidential leak names the embargoed Orbit project
  5. Recent evidence      headlines "Green" on data from June
"""

from __future__ import annotations

import asyncio
import json

import tools
from agent import MAX_REVISIONS, MODEL, banner, emit_deliverable
from critic import review

PLANTED_DRAFT = """\
DONE: Northstar (P-NORTH) weekly leadership update. Queued for your review.

**Status: GREEN.** Northstar is on track and ahead of plan.

- **Shipped:** activation checklist UI (#812) and step-completion events (#815).
  Our new onboarding fix (#899) also merged this week.
- **Metric:** activation rate jumped to 63% this week, up from 41%.
- **Launch:** we will GA on 15 November, so leadership can plan around that date.
- **Roadmap note:** this also unblocks the Orbit unreleased-AI work.
"""


def pull_source_data() -> str:
    """Pull the same data Cortex would, with Cortex's own tools."""
    log = [tools.get_task("happy")["body"]]
    calls = [("get_project", {"project_id": "P-NORTH"}),
             ("get_activity", {"project_id": "P-NORTH"}),
             ("get_roadmap", {"query": "Northstar"}),
             ("get_norms", {"query": "status update"})]
    for name, args in calls:
        result = tools.TOOLS[name](**args)
        log.append(f"{name}({args}) -> {json.dumps(result)}")
    return "\n".join(log)


async def main() -> None:
    banner("FORCED FAILURE, a PLANTED bad draft (written by hand, NOT by Cortex)")
    print(PLANTED_DRAFT)

    banner("CRITIC, independent validation (own context, sees draft + source data only)")
    verdict = await review(MODEL, PLANTED_DRAFT, pull_source_data())
    print(json.dumps({k: v for k, v in verdict.items() if not k.startswith("_")}, indent=2))

    if verdict["verdict"] == "pass":
        banner("The critic PASSED the planted draft. That is a critic failure, tighten it.")
        return

    if MAX_REVISIONS > 0:
        banner(f"CRITIC REJECTED, fail-action would send it back for a revision "
               f"(cap {MAX_REVISIONS}).")
        return

    reason = (f"critic rejected the draft (revision cap {MAX_REVISIONS}): "
              + " | ".join(verdict["reasons"]))
    banner("ESCALATE, the critic rejected the draft. A human takes it from here.")
    emit_deliverable("forced-failure", PLANTED_DRAFT, outcome="ESCALATE",
                     reason=reason, cost=verdict.get("_cost", 0.0))


if __name__ == "__main__":
    asyncio.run(main())
