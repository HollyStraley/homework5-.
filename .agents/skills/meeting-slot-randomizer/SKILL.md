---
name: meeting-slot-randomizer
description: >
  Randomly assigns team members to upcoming meeting presenter slots in a fair,
  round-robin-shuffled order — no one repeats until everyone has presented once.
  Tracks history across runs in a JSON file so the fairness guarantee holds
  over time. Use this skill whenever a user wants to schedule who presents,
  leads, or facilitates upcoming meetings, standups, demos, or retrospectives,
  especially when they want rotation to be fair and random. Trigger even for
  casual requests like "who should present next week?" or "shuffle the demo
  order for my team."
---

# Meeting Slot Randomizer

## What this skill does

Assigns team members to a specified number of upcoming meeting slots using
a **shuffled round-robin**: everyone in the pool is randomly ordered, then
assigned to slots in that order. No one gets a second slot until everyone
has had one. History is persisted to a JSON file so the rotation continues
correctly across separate runs.

## Why the script is required

- Shuffling must use a real RNG — Claude cannot produce unbiased random
  orderings reliably from prose alone.
- History state must be read and written deterministically across sessions.
- The "no repeats until full rotation" rule is algorithmic: it requires
  maintaining a queue, detecting exhaustion, and refilling it, which prose
  reasoning gets wrong under edge cases (wrap-around, mid-rotation additions,
  etc.).

## What this skill does NOT do

- Does not schedule actual calendar events.
- Does not handle weighted probabilities or opt-outs (keep it simple).
- Does not manage multiple separate teams or meeting types in one call.
- Does not send notifications or emails.

---

## Inputs

Claude should extract the following from the user's message:

| Input | Description | Required |
|-------|-------------|----------|
| `team` | List of team member names | Yes |
| `slots` | Number of upcoming slots to fill | Yes |
| `history_file` | Path to the JSON history file | No (defaults to `./rotation_history.json`) |
| `seed` | Integer random seed for reproducibility | No (omit for true randomness) |

If `team` or `slots` is missing, ask the user before running the script.

---

## Output

The script prints a numbered assignment list and writes updated history.
Claude should relay the list to the user in a readable format, e.g.:


# Skill Demo: `meeting-slot-randomizer`

This document shows the skill being used in an agent workflow across three test prompts.

---

## How the skill is discovered

The agent scans `available_skills` at the start of each conversation. The skill's description reads:

> "Randomly assigns team members to upcoming meeting presenter slots in a fair, round-robin-shuffled order… Trigger even for casual requests like 'who should present next week?' or 'shuffle the demo order for my team.'"

When a user asks anything about assigning, rotating, or scheduling who presents or leads a meeting, the agent recognizes the match and loads `SKILL.md` before responding.

---

## Test 1 — Normal Case

**User prompt:**
> "Assign the next 3 presenter slots for my team: Alice, Bob, Carmen, Dan, Maya"

**Agent reasoning:**
This is a direct match for the skill. The agent extracts `team = [Alice, Bob, Carmen, Dan, Maya]` and `slots = 3`, then runs the script:

```bash
python assign_slots.py --team Alice Bob Carmen Dan Maya --slots 3 --history ./history.json
```

**Script output:**
