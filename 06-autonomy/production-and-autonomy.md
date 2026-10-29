# Production & Autonomy: Cortex PM Chief-of-Staff Agent

> Module 6 · ★ Deliverable 5, how you'd ship it, govern it, and widen trust over time
>
> ✅ **What this validates:** you can ship it, govern it, and widen trust deliberately, by the end you'll have proven an autonomy dial, a Trust Ladder rung with its eval gate, and a governance plan.

## Autonomy Dial by segment

Autonomy is a product decision per user, not one global setting.

| Segment | Desired autonomy | Why |
|---|---|---|
| New eng lead | Supervised | First time reviewing Cortex, wants to confirm every action |
| Seasoned ops user | Bounded-autonomous | Has watched Cortex draft updates correctly for months, trusts routine ones |

The dial changes how many approvals a user sees. It never moves the agent line. Posting a company-wide update stays human-approved for everyone.

## Trust Ladder

- **Current rung:** Supervised, by design. Every output is held for human approval. No shadow or assisted window has run on real inputs yet, and evals have only run on fixtures.
- **Eval gate to reach Bounded-autonomous:** all 5 M5 evals pass at 90% or better, with 0 unsafe actions, over 4 weeks of real runs, and a clean incident log.
- **Incident record so far:** 0 real incidents, because Cortex has not run in production. Test findings (the critic catching a stale "Green" status, a stale `.env` setting) were caught before anything went out.

## Deployment plan

- **Runtime:** Serverless function, because Cortex runs on a weekly schedule, not all day. It is pay-per-run.
- **Operator / on-call owner:** The product lead is the owner and I am the backup. It is a weekly job, so failures are handled during business hours, not paged at 2am.
- **Rollback:** Flip the kill switch (instant), then revert to the last good prompt version.
- **Monitoring:** A weekly dashboard with 4 numbers: eval pass %, escalation rate, cost per run, and number of STUCK runs. I check it once a week.

## ROI metrics (beyond adoption & tokens)

| Metric | Target |
|---|---|
| Task completion rate | 80% of routine updates completed end to end, needing only approval. A realistic target for a new agent. |
| Time saved / cost-to-serve | About 2 hours saved per week. Model cost under $0.05 per run, with review time counted in. |
| Trust incidents | 0 serious incidents per quarter. Any one drops Cortex back a rung. |

## Widen-autonomy decision rule

Turn the dial up one rung only when all 5 evals pass at 90% or better, with 0 unsafe actions, over 4 weeks of real runs, with a clean incident log. One serious incident drops Cortex back a rung until the cause is fixed and the gate is cleared again.

## Governance & forward strategy

- **Compliance:** Confidential items (like unreleased roadmap names) must never appear in a prompt or output. The critic blocks named confidential items. Only fake or approved data is used.
- **Safety:** Posting, merging and closing stay above the agent line for everyone. There is no post tool, and the kill switch halts Cortex.
- **Reliability:** 8-iteration cap, $0.05 per-run cap, and escalate when stuck. If the model is down, the run stops and a human is told. Nothing is posted.
- **Strategy:** The next segment to widen into is the seasoned ops user. The gate is the same 4-week eval bar.
