#!/usr/bin/env python3
import argparse
import json
import random
import sys
from pathlib import Path


def load_history(path: Path) -> dict:
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return {"remaining": [], "completed": []}


def save_history(path: Path, state: dict) -> None:
    with open(path, "w") as f:
        json.dump(state, f, indent=2)


def assign(team, slots, history_path, seed=None):
    rng = random.Random(seed)
    state = load_history(history_path)

    team_set = set(team)
    remaining = [n for n in state["remaining"] if n in team_set]
    completed = [n for n in state["completed"] if n in team_set]

    known = set(state["remaining"]) | set(state["completed"])
    added = [n for n in team if n not in known]
    removed = [n for n in known if n not in team_set]

    remaining = remaining + added

    assignments = []
    wrapped = False

    for slot_num in range(1, slots + 1):
        if not remaining:
            new_pool = list(completed)
            rng.shuffle(new_pool)
            remaining = new_pool
            completed = []
            wrapped = True

        if not remaining:
            sys.exit("Error: team is empty.")

        name = remaining.pop(0)
        completed.append(name)
        assignments.append((slot_num, name))

    save_history(history_path, {"remaining": remaining, "completed": completed})

    return {"assignments": assignments, "remaining": remaining, "wrapped": wrapped,
            "added": added, "removed": removed}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--team", nargs="+", required=True)
    parser.add_argument("--slots", type=int, required=True)
    parser.add_argument("--history", type=Path, default=Path("./rotation_history.json"))
    parser.add_argument("--seed", type=int, default=None)
    args = parser.parse_args()

    if not args.history.exists():
        rng = random.Random(args.seed)
        shuffled = list(dict.fromkeys(args.team))
        rng.shuffle(shuffled)
        args.history.parent.mkdir(parents=True, exist_ok=True)
        with open(args.history, "w") as f:
            json.dump({"remaining": shuffled, "completed": []}, f, indent=2)

    team = list(dict.fromkeys(args.team))
    result = assign(team, args.slots, args.history, seed=args.seed)

    print("Upcoming presenter assignments:")
    for slot_num, name in result["assignments"]:
        print(f"  Slot {slot_num} — {name}")
    print(f"\nHistory saved to {args.history}")
    if result["remaining"]:
        print(f"Remaining in current rotation (not yet assigned): {', '.join(result['remaining'])}")
    else:
        print("Current rotation complete — next run starts a fresh cycle.")
    if result["wrapped"]:
        print("Warning: rotation wrapped mid-assignment (slots > team size).")
    if result["added"]:
        print(f"New members added to rotation: {', '.join(result['added'])}")
    if result["removed"]:
        print(f"Members removed (no longer on team): {', '.join(result['removed'])}")


if __name__ == "__main__":
    main()
