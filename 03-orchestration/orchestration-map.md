# Orchestration Map: Cortex PM Chief-of-Staff Agent

> Module 3 · Orchestration & Subagents, ★ Deliverable 3
>
> ✅ **What this validates:** nothing advances unchecked, by the end you'll have proven a justified topology, a roster, and a validator with a defined fail action.
>
> Builds on your M2 Loop Spec. Only split one agent into a team when there's a real reason, coordination has a cost.

## 1. Why split? (or why not)

Cortex stays a single agent for the work, with **one** added subagent: an independent validator (the critic).

**Why the validator:** Cortex can't reliably catch its own leaks and unsupported claims. In my runs it twice put a confidential item and a "Green" call it couldn't support into a draft, and only a separate critic with its own context caught them.

**Why nothing else:**
- **Separation of concerns:** not needed, because Cortex only has one job.
- **Parallelism:** not needed, because the reads are small and run one after the other.
- **Context-window pressure:** not an issue, because there's one agent per run.

## 2. Topology

**Pattern:** single agent plus one subagent.

```
[Inbound PM task] → [Cortex: pulls data, drafts update + stories]
                  → [Critic]
                       pass → [PM review checkpoint] → queued (never auto-sent)
                       fail → [Escalate to a human, with the critic's reasons]
```

## 3. Roster

| Agent / subagent | Responsibility | Runs which Loop Spec |
|---|---|---|
| Cortex (chief-of-staff) | Pulls data, drafts the update, queues proposed stories | The M2 loop |
| Critic / validator | Checks the draft against five rules, once per draft | The validation step of the M2 loop |

## 4. Communication & hand-offs

A plain in-process hand-off. No MCP or A2A protocol is used. Cortex hands the critic the draft plus the log of everything it pulled. The critic hands back a pass or fail verdict with reasons.

## 5. The validator

- **What the critic checks:**
  1. The update references the correct project and real PR and issue IDs.
  2. Every figure is traceable to pulled data.
  3. No commitments Cortex may not make (ship or GA dates, launch gates), so nothing is committed without a human in the loop.
  4. No confidential or embargoed item is named, which needs a human in the loop.
  5. A red, yellow or green call must rest on recent evidence. This is really important.
- **Fail action:** escalate. A rejected draft goes straight to a human with the critic's reasons, to make sure nothing inaccurate or incorrect gets included.
- **Revision cap:** 0. The first rejection escalates, so a draft can't bounce back and forth.
- **Pass action:** a passing draft advances to the PM review checkpoint. It is never sent automatically.
- **Built into the tools, not the critic:** Cortex has no tool that posts or sends, and the tool rejects an over-cap story batch, so those are enforced in code.

## 6. State: shared vs isolated

- **Shared:** the draft and the source data Cortex pulled, so the critic can check every figure.
- **Isolated:** Cortex's reasoning and conversation stay out of the critic's view, so the critic can't inherit Cortex's blind spots.
- **For the human reviewer:** the full trace, including Cortex's reasoning, is available at the checkpoint.
- State stays per project, with nothing shared across projects, as in the Loop Spec.

## 7. Cost & latency budget

- **Extra model calls:** the critic adds **1** call per draft. With a revision cap of 0, the worst case is also 1 per run.
- **Measured cost:** about $0.0004 per critic call, out of about $0.003 for a whole run (the SDK's estimate, not a bill on a subscription).
- **Added latency:** about 8 seconds before a draft reaches the PM, in a run of about 19 seconds.
- **Budget ceiling:** a run may cost up to **$0.50**, which matches the build's current cost cap.
- **Bound for M5:** at most 1 critic call per draft, and a per-run cost cap of $0.50.
