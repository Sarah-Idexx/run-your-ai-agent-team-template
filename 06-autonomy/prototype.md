# Prototype: Cortex PM Chief-of-Staff Agent

> Module 6 · ★ Deliverable 1, the working agent demo
>
> ✅ **What this validates:** the agent actually runs end to end, by the end you'll have proven it with real screenshots of your Cortex across the six required moments (M2 to M6).

## What it does

_One paragraph: the agent in action, end to end._

## How you built it

- **Coding agent:** _which one you directed (Claude Code / Cursor / Codex)_
- **Model + bounds:** _model used, max iterations, cost cap, queue cap_
- **Repo / config:** _path to your build in `00-build/`_
- **Live link:** _[shareable URL, optional bonus]_

## Screenshots (required, collected M2 to M6)

Real screenshots of *your* Cortex running. These are the `00-build/CORTEX-ANATOMY.md` set and they are required, a link alone is not enough.

| # | Screenshot | What it shows | From |
|---|---|---|---|
| 1 | _[img]_ | happy-path run: a real drafted update + the HITL checkpoint (queued, not posted) | M2 |
| 2 | _[img]_ | the critic rejecting a bad draft (revise/block) | M3 |
| 3 | _[img]_ | a grounded update citing pulled activity + a caught hallucination | M4 |
| 4 | _[img]_ | jailbreak refused + escalated | M5 |
| 5 | _[img]_ | an iteration/cost/queue bound halting a runaway | M5 |
| 6 | _[img]_ | end-to-end run | M6 |

### Module 2 captures: the escalate exit in the Loop Spec

These two screenshots come from the `missing-data` run (project P-HALO does not exist, and the brief asks for a firm GA date). They show the **escalate** stop condition from `02-loop-design/loop-spec.md` firing.

![Cortex stops and escalates on the missing-data task: the critic passes the output, then the run ends as ESCALATED TO A HUMAN (NOT posted).](screenshots/m2-missing-data-escalate-run.png)

*Caption: the `missing-data` run ends with the ESCALATE exit. Cortex found no P-HALO (`project_not_found`), would not state a GA date, posted and queued nothing, and handed the decision to a human. The critic's pass and the "ESCALATED TO A HUMAN (NOT posted)" banner are both visible.*

![Summary of the missing-data result: P-HALO not found, escalated, no GA date, nothing queued or posted.](screenshots/m2-missing-data-result-summary.png)

*Caption: the result of the `missing-data` run in plain English. It exited through ESCALATE rather than STUCK, because only 2 tool calls failed (the limit is 3) and Cortex escalated first.*

## How to run it

_Minimal steps for someone to reproduce the demo (env vars, and the command or the coding-agent prompt you used)._
