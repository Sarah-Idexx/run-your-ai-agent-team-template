# Loop Spec: Cortex PM Chief-of-Staff Agent

> Module 2 · Loop Engineering, ★ Deliverable 2
>
> ✅ **What this validates:** the agent knows when to run and when to stop, by the end you'll have proven a one-page Loop Spec with a trigger, a definition of "done," and explicit stop conditions.
>
> Your one-page blueprint for how the work you handed to the agent (M1) actually *runs*.
> An agent is just a prompt that fires itself, this spec says when it fires, what "done" means, and what it needs to do the job. Living document; refine as the course progresses.

## 1. Trigger & loop type

**Chosen type:** cron, as the primary trigger. Cortex runs once per day at a fixed, regular time (for example 9am on weekdays; the exact time is a setting that can change), then stops.

**Why this type:** the status update happens on a regular schedule, so a daily check is enough and it doesn't need to start the moment a task arrives. Running once and then stopping is also the easiest kind of loop to bound.

**Ruled out:**
- **Hook:** Cortex doesn't need to react to each task instantly, and a hook fires more often and adds more to bound.
- **Heartbeat:** polling every few minutes would waste runs and cost when nothing has changed.
- **Goal:** the job isn't open-ended. It's one bounded draft per run, so there's no need to keep working until a goal is met.

**Duplicate check:** if the same task shows up in two runs, Cortex must not draft two updates. Each task has an ID, and Cortex logs the IDs it has already handled and skips any it has seen.

## 2. Goal / definition of done

A run is done when the status update is drafted, the proposed stories are queued under the cap, and a human approves both before anything goes out. A human is kept in the loop, and Cortex never posts or sends anything.

## 3. Stop conditions

| Condition | What it looks like | What happens |
|---|---|---|
| **Success** | The critic returns a "pass" verdict, and the draft and stories are queued for approval. | The loop stops at the human-approval checkpoint, and the draft is saved for review. |
| **Stuck / give up** | A tool fails or finds nothing after 3 attempts, OR the iteration cap is hit. These catch different problems. | The loop stops and logs what it tried. It doesn't invent an answer. |
| **Escalate to human** | Any of these: the brief asks for something outside the rules (such as a ship or GA date); the story batch is over the cap; a confidential or embargoed item is involved; an open Sev-1 or launch hold is found; the brief contains instructions trying to change Cortex's rules; the critic rejects the draft (revision cap 0, so the first rejection escalates). | Cortex stops and hands off to a human, at the human-approval checkpoint from the agent line map. This keeps confidential data from leaking and incorrect information out of the update. |

## 4. State

The task-ID log and last week's update for each project persist between runs. The log supports the duplicate check, and last week's update keeps the format consistent. Nothing is shared across projects, so confidential items can't leak between them.

## 5. The five things a loop can lean on

_`state` is always-on. `connectors` only if you already have one wired (e.g. a Jira key or Google MCP), otherwise just note it as a plan. `skills`, `subagents`, `work tree` scale with autonomy; "not needed yet, because…" is a valid answer._

| Component | For Cortex |
|---|---|
| **Work tree** (isolated workspace per run, a git worktree) | Not needed yet, because each run only reads data and writes a draft file, with no code changes that need an isolated workspace. |
| **Skills** (reusable capabilities) | Not needed yet, because Cortex has one workflow, the weekly status update. |
| **Plugins / connectors** (tools & access, optional if you don't have one yet) | None wired today, because Cortex reads sample files. Plan: connect Jira and GitHub for live project activity later. |
| **Subagents** (independent check when the loop can't grade itself) | The independent critic already checks each draft. Defined further in M3 `orchestration-map.md`. |
| **State tracking** | The task-ID log plus last week's update per project, as in §4. |

> Context plan (M4) and the hand-off to bounds & evals (M5) come in later modules, you'll add them to their own deliverables then, not here.

## Link to live loop

_[path to your agent in `00-build/`]_
