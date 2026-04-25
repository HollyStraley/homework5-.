Also tell the user:
- Who is still in the current rotation (hasn't gone yet this cycle)
- If the rotation wrapped (a new cycle started mid-assignment), say so clearly

---

## How to invoke the script

Run the script at `/mnt/skills/public/meeting-slot-randomizer/scripts/assign_slots.py`
(or wherever this skill is installed) using `bash_tool`:

```bash
python /path/to/scripts/assign_slots.py \
  --team "Alice" "Bob" "Carmen" "Dan" \
  --slots 3 \
  --history ./rotation_history.json
  # optionally: --seed 42
```

Parse stdout for the assignment list. The history file is updated in place.

---

## Script reference

See `scripts/assign_slots.py`. It accepts:

- `--team NAME [NAME ...]` — space-separated list of names
- `--slots N` — integer, number of slots to fill
- `--history PATH` — path to JSON history file (created if absent)
- `--seed N` — optional integer seed

Exits 0 on success, 1 on error (error message on stderr).

---

## Edge cases Claude should handle gracefully

- **New team member added**: If a name appears in `--team` that isn't in the
  history, insert them into the remaining pool for the current rotation
  (the script handles this automatically).
- **Team member removed**: Names in history but not in `--team` are silently
  dropped. Mention this to the user if it happens.
- **Slots > team size**: The rotation will wrap — some people get a second
  slot before others get their first. Tell the user this happened and who
  repeated.
- **History file missing**: Script creates a fresh one. Tell the user a new
  rotation is starting.
