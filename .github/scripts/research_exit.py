#!/usr/bin/env python3
"""Assemble a research pack for drafting an exit page.

Usage: python3 .github/scripts/research_exit.py <term>
       python3 .github/scripts/research_exit.py --issue <number>   (needs gh)
       python3 .github/scripts/research_exit.py --json <term>

Checks every wired source for the term: ToS;DR rating, JustDeleteMe deletion
entry, fuzzy matches in awesome-privacy / awesome-selfhosted / web3privacy,
and similar existing exits. Markdown for humans/agents, --json for the
local drafting pipeline and its deterministic truth-check.
"""

import json
import re
import subprocess
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
UA = {"User-Agent": "exit.tech-research/0.1 (https://github.com/xAlisher/exit-tech)"}


def fetch_json(url: str):
    try:
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=20) as r:
            return json.loads(r.read().decode("utf-8", "replace"))
    except Exception:
        return None


def fetch_text(url: str) -> str | None:
    try:
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.read().decode("utf-8", "replace")
    except Exception:
        return None


def research(term: str) -> dict:
    t = term.lower().strip()
    slug = re.sub(r"[^a-z0-9]+", "-", t).strip("-")
    pack: dict = {"term": term, "slug": slug}

    d = fetch_json(f"https://api.tosdr.org/search/v5/?query={urllib.request.quote(t)}")
    pack["tosdr"] = [
        {"name": s["name"], "rating": s.get("rating"), "id": s["id"]}
        for s in (d.get("services") or [])[:3]
    ] if d else []

    sites = fetch_json("https://raw.githubusercontent.com/justdeleteme/justdelete.me/master/sites.json")
    pack["justdeleteme"] = [
        {"name": s["name"], "difficulty": s.get("difficulty"),
         "url": s.get("url"), "notes": s.get("notes")}
        for s in (sites if isinstance(sites, list) else [])
        if t in s["name"].lower()
    ][:5]

    pack["awesome_privacy_sections"] = []
    ap = fetch_text("https://raw.githubusercontent.com/Lissy93/awesome-privacy/main/awesome-privacy.yml")
    if ap:
        import yaml
        data = yaml.safe_load(ap)
        for cat in data.get("categories", []):
            for sec in cat.get("sections", []):
                blob = json.dumps(sec).lower()
                if t in blob:
                    pack["awesome_privacy_sections"].append({
                        "section": sec.get("name"), "category": cat.get("name"),
                        "services": [s.get("name") for s in sec.get("services") or []],
                    })
        pack["awesome_privacy_sections"] = pack["awesome_privacy_sections"][:6]

    listing = fetch_json("https://api.github.com/repos/awesome-selfhosted/awesome-selfhosted-data/contents/software")
    pack["awesome_selfhosted_slugs"] = [
        f["name"][:-4] for f in listing
        if f["name"].endswith(".yml") and t.replace(" ", "") in f["name"].replace("-", "")
    ][:10] if isinstance(listing, list) else []

    w3p = fetch_json("https://explorer-data.web3privacy.info/index.json")
    pack["web3privacy_ids"] = [
        p["id"] for p in w3p.get("projects", []) if t in p.get("name", "").lower()
    ][:10] if w3p else []

    existing = sorted(p.stem for p in (ROOT / "data" / "exits").glob("*.yaml")
                      if not p.name.startswith("_"))
    pack["existing_exits"] = existing
    pack["possible_duplicates"] = [e for e in existing if slug in e or e in slug]
    return pack


def render_markdown(pack: dict, issue_header: str = "") -> str:
    out = [f"# Research pack: {pack['term']}"]
    if issue_header:
        out.append(issue_header)
    out.append(f"\nProposed id: `{pack['slug']}`  → data/exits/{pack['slug']}.yaml")

    out.append("\n## ToS;DR (terms-of-service rating) — enrich.tosdr")
    out += [f"- {s['name']}: rating {s['rating']} (service id {s['id']})"
            for s in pack["tosdr"]] or ["- no match"]

    out.append("\n## JustDeleteMe (deletion link) — enrich.justdeleteme")
    for s in pack["justdeleteme"]:
        out.append(f"- name: '{s['name']}'  difficulty: {s['difficulty']}  url: {s['url']}")
        if s.get("notes"):
            out.append(f"  notes: {s['notes']}")
    if not pack["justdeleteme"]:
        out.append("- no match")

    out.append("\n## Awesome Privacy sections mentioning the term")
    out += [f"- '{s['section']}' ({s['category']}): {s['services'][:12]}"
            for s in pack["awesome_privacy_sections"]] or ["- none"]

    out.append("\n## awesome-selfhosted slug matches")
    out.append(f"- {pack['awesome_selfhosted_slugs'] or 'none'}")

    out.append("\n## web3privacy project matches")
    out.append(f"- {pack['web3privacy_ids'] or 'none'}")

    out.append("\n## Existing exits (style reference + duplicates)")
    out.append(f"- current exits: {pack['existing_exits']}")
    out.append(f"- possible duplicate: {pack['possible_duplicates'] or 'none'}")

    out.append("\n## Drafting checklist")
    out.append("""- copy data/exits/_template.yaml -> data/exits/{slug}.yaml
- only set enrich keys confirmed above; only claim recommended_by a source actually makes
- stub: true if no curated routes yet — the agent prompt still must be useful
- sensitive topic? defer to professional help in the prompt (see CLAUDE.md rules)
- validate: python3 build.py --offline""".replace("{slug}", pack["slug"]))
    return "\n".join(out)


def main():
    args = sys.argv[1:]
    as_json = "--json" in args
    args = [a for a in args if a != "--json"]
    if not args:
        sys.exit(__doc__)

    issue_header = ""
    if args[0] == "--issue":
        out = subprocess.run(["gh", "issue", "view", args[1], "--json", "title,body"],
                             capture_output=True, text=True, check=True).stdout
        issue = json.loads(out)
        term = re.sub(r"^exit:\s*", "", issue["title"], flags=re.I)
        term = re.sub(r"\s*\(×\d+\)$", "", term).strip()
        issue_header = f"\nFrom issue: {issue['title']}\n> {issue['body'][:500]}"
    else:
        term = " ".join(args).strip()

    pack = research(term)
    if as_json:
        print(json.dumps(pack, indent=2, ensure_ascii=False))
    else:
        print(render_markdown(pack, issue_header))


if __name__ == "__main__":
    main()
