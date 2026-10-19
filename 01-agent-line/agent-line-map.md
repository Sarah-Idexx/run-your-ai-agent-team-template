# Agent Line Map: Cortex PM Chief-of-Staff Agent

> Module 1 · The Agent Line
>
> ✅ **What this validates:** every risky action has a clear owner, by the end you'll have proven an above/below-the-line map with HITL checkpoints, scored on reversibility, blast radius, and measurability.

## The workflow, decision by decision

List every discrete decision or action in your agent's workflow, then score each one and place it **above** the line (a human owns it) or **below** (the agent owns it). Borderline calls get an HITL checkpoint.

| Decision / action | Reversibility (H/M/L) | Blast radius (H/M/L) | Measurability (H/M/L) | Above / Below | HITL? |
|---|---|---|---|---|---|
| Pull project state and activity | H | M | H | Below | No |
| Decide relevant context | H | H | H | Below | Yes, human approves |
| Draft the update | H | L | H | Below | Yes, human approves |
| Decide tone and commitment level | H | L | H | Below | No |
| Flag at-risk items and escalation | H | H | M | Below | Yes, human approves |
| Choose what to escalate | H | H | M | Above | n/a |
| Propose a story batch (capped) | H | M | M | Below | Yes, human approves |
| Post or approve a company-wide update | H | H | H | Below | Yes, human approves |

## Agent anatomy (sketch)

- **Model:** the default is `claude-haiku-5-5`, a fast and cheap model. Cortex escalates to a frontier model when the critic rejects a draft twice, so extra cost is spent only where the fast model is struggling.
- **Tools:** read-only lookups for project, activity, past updates, roadmap and team norms, plus a capped story-proposal tool that only queues requests for human approval. There is deliberately no tool that posts, creates, merges or closes anything, so the agent line is enforced in code.
- **Memory:** what persists across runs is the roadmap, team norms, past updates and the decision log. A run's drafts and tool outputs are purged, and nothing carries over between runs.
- **Loop:** placeholder, defined in M2 `loop-spec.md`
- **Bounds:** placeholder, defined in M5 `bounds-and-evals.md`
- **Evals:** placeholder, defined in M5 `bounds-and-evals.md`

## The golden rule, applied

1. **Pull project state and activity** sits below the line because it's easy to reverse, has a medium blast radius, and is easy to verify. Deciding factor: measurability, because it provides the links to the correct material.
2. **Decide relevant context** sits below the line, with human approval, because it's easy to reverse, has a high blast radius, and is easy to verify. Deciding factor: reversibility, because I can change this as work progresses.
3. **Draft the update** sits below the line, with human approval, because it's easy to reverse, has a low blast radius, and is easy to verify. Deciding factor: reversibility, because I can change this as work progresses.
4. **Decide tone and commitment level** sits below the line because it's easy to reverse, has a low blast radius, and is easy to verify. Deciding factor: reversibility, because I can change this as work progresses.
5. **Flag at-risk items and escalation** sits below the line, with human approval, because it's easy to reverse, has a high blast radius, and is moderately measurable. Deciding factor: blast radius, because there's high impact if risks or escalations are incorrect or missed.
6. **Choose what to escalate** sits above the line because it's easy to reverse, has a high blast radius, and is moderately measurable. Deciding factor: blast radius, because there's high impact if risks or escalations are incorrect or missed.
7. **Propose a story batch (capped)** sits below the line, with human approval, because it's easy to reverse, has a medium blast radius, and is moderately measurable. Deciding factor: measurability, because of the direction of the output.
8. **Post or approve a company-wide update** sits below the line, with human approval, because it's easy to reverse, has a high blast radius, and is easy to verify. Deciding factor: blast radius, because there's high impact if something is incorrect or missed.

## Hardest call

**Decide tone and commitment level.** I first put this above the line, because tone should be determined by a human. I moved it below because it's easy to amend if it turns out to be wrong, and a human approves the draft before anything goes out. The deciding axis was **reversibility**: I can change it if it's incorrect.
