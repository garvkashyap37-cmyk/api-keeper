#!/usr/bin/env python3
"""api-keeper fixer: replaces deprecated names with their replacements.

Usage:
    python fixer.py /path/to/repo           # preview only, changes nothing
    python fixer.py /path/to/repo --apply   # actually edit the files

Only rules marked "drop_in": true are replaced. The rest need a human.
"""
import os
import sys

from scanner import EXTENSIONS, SKIP_DIRS, SKIP_FILES, load_rules


def fix_file(path, rules, apply):
    """Return a list of (rule, count) for replacements made in one file."""
    # newline="" keeps Windows/Unix line endings exactly as they were.
    with open(path, encoding="utf-8", newline="") as f:
        text = f.read()
    changes = []
    for rule in rules:
        if not rule["drop_in"]:
            continue
        text, count = rule["pattern"].subn(rule["new"], text)
        if count:
            changes.append((rule, count))
    if changes and apply:
        with open(path, "w", encoding="utf-8", newline="") as f:
            f.write(text)
    return changes


def main():
    args = [a for a in sys.argv[1:] if a != "--apply"]
    apply = "--apply" in sys.argv
    root = args[0] if args else "."
    rules_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "rules.json")
    rules = load_rules(rules_path)

    total = 0
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            if name in SKIP_FILES or name in ("scanner.py", "fixer.py"):
                continue
            if os.path.splitext(name)[1].lower() not in EXTENSIONS:
                continue
            path = os.path.join(dirpath, name)
            try:
                changes = fix_file(path, rules, apply)
            except (UnicodeDecodeError, OSError):
                continue
            for rule, count in changes:
                total += count
                print(f"{path}: {rule['old']} -> {rule['new']}  ({count}x)")

    verb = "Replaced" if apply else "Would replace"
    print(f"\n{verb} {total} usage(s).")
    if not apply and total:
        print("Run again with --apply to make the changes.")
    print("Entries that are not simple renames are skipped. Run scanner.py to see them.")


if __name__ == "__main__":
    main()