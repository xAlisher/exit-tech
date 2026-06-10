#!/usr/bin/env python3
"""Dedupe exit-request issues and keep a weight counter in the title.

For each group of open exit-request issues with the same normalized term,
the oldest issue is canonical. Duplicates get a pointer comment and are
closed; each merged duplicate adds a '+1 (duplicate request)' comment on
the canonical issue. Weight = 1 + those comments, shown as 'exit: <term> (xN)'.

Needs: gh CLI authenticated (GH_TOKEN), repo context via GH_REPO or cwd.
"""

import collections
import json
import re
import subprocess
import sys

MARKER = "+1 (duplicate request)"


def gh(*args: str) -> str:
    res = subprocess.run(["gh", *args], capture_output=True, text=True)
    if res.returncode != 0:
        print(f"gh {' '.join(args)} failed: {res.stderr}", file=sys.stderr)
        sys.exit(1)
    return res.stdout


def norm(title: str) -> str:
    t = title.lower().strip()
    t = re.sub(r"^exit:\s*", "", t)
    t = re.sub(r"\s*\(×\d+\)$", "", t)
    return t.strip()


def main() -> None:
    issues = json.loads(gh("issue", "list", "--label", "exit-request",
                           "--state", "open", "--json", "number,title",
                           "--limit", "500"))
    groups = collections.defaultdict(list)
    for i in issues:
        groups[norm(i["title"])].append(i)

    for term, group in groups.items():
        if not term:
            continue
        group.sort(key=lambda i: i["number"])
        keep, dupes = group[0], group[1:]

        for d in dupes:
            gh("issue", "comment", str(d["number"]),
               "-b", f"Duplicate of #{keep['number']} — weight moved there.")
            gh("issue", "close", str(d["number"]), "-r", "not planned")
            gh("issue", "comment", str(keep["number"]), "-b", MARKER)
            print(f"merged #{d['number']} into #{keep['number']} ({term})")

        comments = json.loads(gh("issue", "view", str(keep["number"]),
                                 "--json", "comments"))["comments"]
        weight = 1 + sum(1 for c in comments if c["body"].strip() == MARKER)
        want = f"exit: {term}" + (f" (×{weight})" if weight > 1 else "")
        if keep["title"] != want:
            gh("issue", "edit", str(keep["number"]), "--title", want)
            print(f"#{keep['number']} -> '{want}'")


if __name__ == "__main__":
    main()
