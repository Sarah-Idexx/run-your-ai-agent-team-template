# Cortex, a PM Chief-of-Staff Agent

> A chief-of-staff agent that drafts a PM’s weekly status update and proposes a story batch, so the team approves instead of assembling from scratch.

_Sarah Thomson · Advanced AI Agents · IDEXX · October 2026_

Repo: https://github.com/Sarah-Idexx/run-your-ai-agent-team-template

This repo is my final project for the Agentic Loops for PMs Certification, **Cortex**. Each module’s artifact lives in its own folder; this README is the dashboard and the pitch.

---

## Module artifacts

### M1 · The Agent Line
- **Agent-line map**: [`01-agent-line/agent-line-map.md`](01-agent-line/agent-line-map.md)

### M2 · Loop Engineering
- **Loop spec**: [`02-loop-design/loop-spec.md`](02-loop-design/loop-spec.md)

### M3 · Orchestration & Subagents
- **Orchestration map**: [`03-orchestration/orchestration-map.md`](03-orchestration/orchestration-map.md)

### M4 · Context Engineering & Memory
- **Memory & context plan**: [`04-memory-context/memory-and-context.md`](04-memory-context/memory-and-context.md)

### M5 · Bounds & Evals
- **Bounds & evals**: [`05-bounds-evals/bounds-and-evals.md`](05-bounds-evals/bounds-and-evals.md)

### M6 · Autonomy & Production
- **Production & autonomy plan**: [`06-autonomy/production-and-autonomy.md`](06-autonomy/production-and-autonomy.md)
- **Prototype write-up**: [`06-autonomy/prototype.md`](06-autonomy/prototype.md)
- **Build insights**: [`06-autonomy/build-insights.md`](06-autonomy/build-insights.md)

Open [`pitch.html`](pitch.html) in a browser for the visual pitch.

---

## Ship plan

### Autonomy dial (per segment)
- **New eng lead:** Supervised. First time reviewing Cortex, wants to confirm every action.
- **Seasoned ops user:** Bounded-autonomous. Has watched Cortex draft updates correctly for months, trusts routine ones.

The dial changes how many approvals a user sees. It never moves the agent line. Posting a company-wide update stays human-approved for everyone.

### Trust Ladder rung + eval gate
- **Current rung:** Supervised, by design. Every output is held for human approval. No shadow or assisted window has run on real inputs yet, and evals have only run on fixtures.
- **Gate to Bounded-autonomous:** all 5 M5 evals pass at 90% or better, with 0 unsafe actions, over 4 weeks of real runs, and a clean incident log.
- **Incident record:** 0 real incidents, because Cortex has not run in production. Test findings (critic caught a stale "Green" status, a stale .env setting) were caught before anything went out.

### Deployment plan
- **Runtime:** Serverless function, because Cortex runs on a weekly schedule, not all day. Pay-per-run.
- **Owner:** The product lead is the owner and I am the backup. Weekly job, so failures are handled during business hours, not paged at 2am.
- **Rollback:** Flip the kill switch (instant), then revert to the last good prompt version.
- **Monitoring:** Weekly dashboard with 4 numbers: eval pass %, escalation rate, cost per run, number of STUCK runs.

### ROI metrics + widen-autonomy rule
- **Task completion rate:** 80% of routine updates completed end to end, needing only approval.
- **Time saved / cost-to-serve:** About 2 hours saved per week. Model cost under $0.05 per run, with review time counted in.
- **Trust incidents:** 0 serious incidents per quarter. Any one drops Cortex back a rung.
- **Widen rule:** Turn the dial up one rung only when all 5 evals pass at 90% or better, with 0 unsafe actions, over 4 weeks of real runs, with a clean incident log. One serious incident drops Cortex back a rung until the cause is fixed and the gate is cleared again.

### Governance & strategy
- **Compliance:** Confidential items (like unreleased roadmap names) must never appear in a prompt or output. The critic blocks named confidential items. Only fake or approved data is used.
- **Safety:** Posting, merging and closing stay above the agent line for everyone. There is no post tool, and the kill switch halts Cortex.
- **Reliability:** 8-iteration cap, $0.05 per-run cap, and escalate when stuck. If the model is down, the run stops and a human is told. Nothing is posted.
- **Strategy:** Next segment to widen into is the seasoned ops user. Same 4-week eval gate.
- **Known gaps:** the kill-switch flag, 90s timeout and $5/day cap are policy and not yet built in code. The 2 hours/week saving is a target to verify against a shadow-mode baseline.

---

## Build insights

- **Friction point.** Learning the new terms (bounds, evals, trust ladder) without being in class has been challenging.
- **Key learning.** An agent needs hard limits (bounds) outside the model, not just instructions in a prompt. I used to focus on writing good prompts. Now I understand it's much more than that. Trust is also earned in steps. Next time I’d add a freshness check so stale data is caught before drafting.
- **Aha moment.** Not having a post tool is a great safety net. Human checkpoints aren't weaknesses, they're necessary.

---

_Certification submission, Agentic Loops for PMs Certification._
