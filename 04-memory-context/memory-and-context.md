# Context Engineering & Memory: Cortex PM Chief-of-Staff Agent

> Module 4 · Context Engineering & Memory
>
> ✅ **What this validates:** the agent reasons on the right, safe inputs, by the end you'll have proven a context budget, per-source retrieve-vs-long-context decisions, and a memory map with risk mitigations.
>
> 🗂️ **How the lab maps to this file:** In **Part A** (before the lecture) you don't edit this file, you rough-draft on scratch, focused on the per-source calls in **section 2** plus a quick remember/forget + "how it rots" sketch. In **Part B** (after the lecture) you complete **all five sections**; the Lab Guide's guided builder writes this file for you to copy in and commit.

## 1. Context budget

_What does each loop iteration actually receive, and why? (You can't fit everything, what's the priority order?)_

**Always on: confidential items must always be protected.** The roadmap filter runs outside the model on every run, before anything reaches the prompt, and no priority ranking can override it.

Priority order for what fits in a run (first = protected longest, last = first to drop):

1. **Task brief** (`get_task`): the ask itself, never cut.
2. **Team norms, full playbook** (`get_norms`): the rules Cortex must cite; a missed rule is costly.
3. **Retrieved activity** (`get_activity`): the evidence behind every number.
4. **Roadmap slice, filtered** (`get_roadmap`): needed for launch claims.
5. **Past updates** (`search_past_updates`): format and tone only, so first to drop.

## 2. Retrieve vs. long-context: per source

For each data source, decide: **retrieve** (narrow a large/changing corpus to the relevant slice) or **long-context** (just include a bounded set you can reason over).

| Source | Size / volatility | Decision | Deciding factor | Why (in my words) |
|---|---|---|---|---|
| `get_activity` (GitHub/Jira activity) | grows fast, changes daily | Retrieve | Volatility | "Things can get quite large in size quickly… look at the amount of volatility." |
| `search_past_updates` (past updates + decision log) | unbounded, append-only | Retrieve | Size / growth | "To gather the latest updates." |
| `get_roadmap` | medium, slow-changing, has confidential flags | Retrieve | Risk / citation-audit | "I don't want to share confidential information." |
| `get_norms` (team norms / playbook) | small, bounded, must stay current | Long-context | Citation / audit | "So it has all the necessary exact rules." |
| `get_task` (this week's task brief) | one short doc | Long-context | Size | "It relates to the Northstar update." |

_Condition on `get_roadmap`:_ retrieval only protects confidential items if the filtering happens before the model sees the roadmap, outside the model.

## 3. Retrieval quality plan

_Which of these apply, and how? (This is what separates modern agentic retrieval from naive "embed → top-k → stuff".)_

Every retrieved source has at least one agentic move, matched to how that source fails (no naive-RAG rows).

| Source (retrieved) | Routing | Document grading | Reranking | Self-verification | Caching |
|---|---|---|---|---|---|
| `get_activity` | — | ✅ not stale, right project | — | ✅ every claim traces to pulled data | — |
| `search_past_updates` | — | ✅ relevant (drop other projects' updates) | ✅ latest update first, so numbers are accurate | — | — |
| `get_roadmap` | — | ✅ confidential items filtered before the model sees anything | — | ✅ re-check the draft for any confidential leak | — |

**Why these moves (in my words):**

- **`get_activity`:** grading + self-verification. "Check data is not stale and that updates are present."
- **`search_past_updates`:** grading + reranking. "Information accuracy and relevant."
- **`get_roadmap`:** grading + self-verification. "Definitely grading so no further info is shared incorrectly. Re-verification needs to happen to ensure there are no other leaks of confidential info."

**Deliberately not used:**

- **Routing:** each source is already the only place that answers its question, so there is nothing to route between.
- **Caching:** skipped everywhere for now. `get_activity` changes daily (a stale copy is the failure we're guarding against), `get_roadmap` holds confidential flags (a cached copy could outlive a filter change), and at this size caching saves almost nothing. Revisit for `search_past_updates` at scale, since it is append-only.

## 4. Memory map (your PM brain)

| Memory type | What Cortex stores | Scope / TTL | Who writes |
|---|---|---|---|
| **Working** (in-loop) | Task brief, pulled records (activity, norms, filtered roadmap slice, recent past updates), the draft, the critic verdict | This run only, purged at the end | Cortex |
| **Episodic** (past runs) | Approved status updates and decisions | 90 days | Cortex proposes, a human approves |
| **Semantic** (durable facts/prefs) | Team norms, non-confidential roadmap facts. Confidential items are never stored | Until next ingest | Human only; Cortex reads |
| **Shared** (across agents) | The critic verdict handed to the drafter | This run only, nothing saved after | The critic writes, the drafter reads; no one else writes, and the verdict never copies confidential details |

_Consistent with the M1 agent line:_ Cortex has read-only tools and no tool that posts or creates anything, so only a human-approved update becomes episodic memory and only a human edits semantic memory.

## 5. Memory risks & mitigations

| Risk | Where it bites Cortex | Mitigation |
|---|---|---|
| **Drift** | Cortex copies format and tone from the 90-day past updates. Small changes pile up, and its behavior slowly moves away from the playbook. | Norms (semantic) outrank past updates. The critic checks each draft against the norms every run. A human approves every entry that becomes episodic. Trend evals come in M5. |
| **Poisoning** | A wrong or injected item gets trusted, for example in an ingested fixture, the decision log, or a past update (the `task-jailbreak` fixture exercises this). | Only human-approved entries enter episodic memory. Ingests are reviewed in `git diff` before commit. Tool output is treated as data, never as instructions. The critic checks claims against the source. |
| **Staleness** | The Step 0 run: July data on October 22. Old norms or roadmap facts also expire. | Document grading checks dates. Escalate if the newest activity is older than a set age (for example 14 days). Fresh pulls every run, 90-day episodic expiry, semantic refreshed at each ingest. |
| **Confidential / PII / retention** | Confidential roadmap items (`Pulsar`, `Orbit`), plus names in updates, stored longer than needed. | Confidential items are never stored. Roadmap is filtered before the model. Working memory is purged each run, episodic expires at 90 days, and Shared memory never copies confidential details. |

_Ties to other modules:_ read/write scope comes from the M1 agent line (Cortex is read-only, humans approve writes); the TTLs (this run, 90 days, until next ingest) feed forward into M5 bounds.
