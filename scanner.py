#!/usr/bin/env python3
"""api-keeper scanner: finds deprecated API/model names in a repo.
Usage: python scanner.py /path/to/repo
"""
import json
import os
import re
import sys
from datetime import date

SKIP_DIRS = {".git", "node_modules", "venv", ".venv", "__pycache__", "dist", "build"}
SKIP_FILES = {"rules.json"}
EXTENSIONS = {".py", ".js", ".ts", ".tsx", ".jsx", ".json", ".yaml", ".yml",
              ".toml", ".env", ".md", ".txt", ".go", ".rb", ".java", ".cs"}


def load_rules(path):
    with open(path, encoding="utf-8") as f:
        rules = json.load(f)
    for rule in rules:
        # Match the whole name only, so a short name never matches a longer one.
        rule["pattern"] = re.compile(r"(?<![\w.\-])" + re.escape(rule["old"]) + r"(?![\w.\-])")
    return rules


def status(rule):
    days = (date.fromisoformat(rule["shutdown"]) - date.today()).days
    if days < 0:
        return "ALREADY SHUT DOWN"
    return f"shuts down in {days} days ({rule['shutdown']})"


def scan(root, rules):
    findings = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            if name in SKIP_FILES:
                continue
            if os.path.splitext(name)[1].lower() not in EXTENSIONS:
                continue
            path = os.path.join(dirpath, name)
            try:
                with open(path, encoding="utf-8") as f:
                    for lineno, line in enumerate(f, 1):
                        for rule in rules:
                            if rule["pattern"].search(line):
                                findings.append((path, lineno, rule))
            except (UnicodeDecodeError, OSError):
                continue
    return findings


def main():
    root = sys.argv[1] if len(sys.argv) > 1 else "."
    rules_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "rules.json")
    findings = scan(root, load_rules(rules_path))
    if not findings:
        print("No deprecated usages found.")
        return
    for path, lineno, rule in findings:
        print(f"{path}:{lineno}  [{rule['vendor']}] {rule['old']} -> {rule['new']}")
        print(f"    {status(rule)}")
        if not rule["drop_in"]:
            print("    NOT a simple rename, needs manual migration")
        if rule["note"]:
            print(f"    note: {rule['note']}")
    print(f"\n{len(findings)} finding(s).")


if __name__ == "__main__":
    main()