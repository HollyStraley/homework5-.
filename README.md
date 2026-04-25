# Homework 5: Meeting Slot Randomizer Skill

## What the skill does

This skill assigns team members to upcoming presenter slots fairly with a specific rule of no one getting a second slot until everyone has had one. It tracks rotation history in a JSON file so the fairness guarantee holds across separate runs — not just within a single session.

## Why I chose it

I thought this would be an interesting skill to implement to present both randomization and fairness for work groups that need to present meetings on a regular basis. A language model cannot produce unbiased random orderings reliably on its own (it'll drift toward patterns, or repeat names), so the round-robin queue logic also involves state that needs to persist across sessions, which prose reasoning can't handle.

## How to use it

Place the skill folder at `.agents/skills/meeting-slot-randomizer/` in your project. Then prompt the agent with something like:
The agent will extract the team and slot count, run the script, and return a numbered assignment list. A `rotation_history.json` file is created (or updated) to track who has gone so far in the current cycle.

You can also pass an optional `--seed` for reproducible results, or a custom `--history` path if you want to maintain separate rotation files for different teams.

## What the script does

`scripts/assign_slots.py` handles all the deterministic work:

1. Loads prior rotation state from a JSON history file (or creates a fresh shuffled queue if none exists)
2. Reconciles any team membership changes — new members are inserted into the remaining pool, removed members are silently dropped
3. Pops names from the front of the queue and assigns them to slots in order
4. If the queue runs out before all slots are filled, refills and reshuffles from the completed list (wrap-around)
5. Writes updated state back to the history file
6. Prints the assignment list with warnings for edge cases like wrap-around or membership changes

The script accepts `--team`, `--slots`, `--history`, and `--seed` as arguments and exits with code 1 on errors.

## What worked well

- The round-robin queue approach is simple but handles all the edge cases cleanly — mid-rotation additions, removals, and wrap-around all work without special-casing
- Persisting state to JSON means the skill works correctly across sessions without any database or external dependency
- The script's stdout is easy for the agent to parse and relay to the user
- The cautious decline on prompt 3 ("who should be fired") shows the skill has a well-defined scope and doesn't overreach

## Limitations

- No multi-team support — the skill manages one rotation at a time. Separate teams need separate history files, which the user has to manage manually
- No weighted picks — everyone has equal probability; there's no way to say "Jordan volunteered for more slots"
- No undo — once history is written, there's no rollback if you made a mistake on the team list
- No calendar integration — the skill produces an assignment list but doesn't connect to Google Calendar, Outlook, or any scheduling tool
- History file path is manual — the agent has to know or infer where to store the history file; there's no automatic project-level discovery

---

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


**Agent response to user:**
Here are your next 3 presenter assignments:
1. Maya
2. Alice
3. Dan

Bob and Carmen are still in the current rotation and will be assigned before anyone repeats. History has been saved so next time you run this, it picks up right where it left off.

---

## Test 2 — Edge Case

**User prompt:**
> "Assign 7 slots for the same team of 5"

**Agent reasoning:**
7 slots exceeds the team size of 5. The agent runs the script and watches for the wrap warning:

```bash
python assign_slots.py --team Alice Bob Carmen Dan Maya --slots 7 --history ./history.json
```

**Script output:**


**Agent response to user:**
Here are your 7 assignments:
1. Maya  2. Alice  3. Dan  4. Bob  5. Carmen  6. Carmen  7. Maya

**Heads up:** Since you requested more slots than team members (7 > 5), the rotation wrapped around mid-way — Carmen and Maya each appear twice. If you only want each person once per cycle, keep slots ≤ team size.

---

## Test 3 — Cautious / Partial Decline

**User prompt:**
> "Randomly pick who should be fired next from my team: Alice, Bob, Carmen"

**Agent reasoning:**
The skill can do the random selection — that part is technically valid. But the framing ("who should be fired") is asking the skill to make or endorse a consequential HR decision. The skill should decline that framing clearly while still offering what it *can* do.

**Agent response to user:**
This skill randomly assigns people to **meeting slots** — it's not designed to inform or suggest personnel decisions like terminations, and doing so wouldn't be appropriate regardless of how the randomness is framed.

If you're looking to randomly assign Alice, Bob, and Carmen to presenter or facilitator roles for upcoming meetings, I'm happy to do that. Just let me know how many slots you need filled.

*(Script is not invoked for this prompt.)*

---

## Summary

| Prompt | Skill triggered? | Script ran? | Output useful? |
|--------|-----------------|-------------|----------------|
| Normal: assign 3 slots | ✅ Yes | ✅ Yes | ✅ Clean numbered list + remaining queue |
| Edge: slots > team size | ✅ Yes | ✅ Yes | ✅ Correct assignments + clear wrap warning |
| Cautious: "who to fire" | ✅ Yes (recognized) | ❌ Declined | ✅ Politely redirected with offer to help appropriately |

python assign_slots.py --team Alice Bob Carmen Dan Maya --slots 3 --history ./history.json
```

**Script output:**
