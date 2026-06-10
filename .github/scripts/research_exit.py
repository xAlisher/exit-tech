#!/usr/bin/env python3
"""Assemble a research pack for drafting an exit page.

Usage: python3 .github/scripts/research_exit.py <term>
       python3 .github/scripts/research_exit.py --issue <number>   (needs gh)

Checks every wired source for the term and prints a markdown research pack:
ToS;DR rating, JustDeleteMe deletion entry, JustGetMyData entry,
fuzzy matches in awesome-privacy / awesome-selfhosted / web3privacy,
and similar existing exits. The drafting agent (or human) turns this
into data/exits/<id>.yaml.
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
    except Exception as e:
        return {"_error": str(e)}


def fetch_text(url: str) -> str | None:
    try:
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.read().decode("utf-8", "replace")
    except Exception:
        return None


def section(title: str):
    print(f"\n## {title}")


def main():
    args = sys.argv[1:]
    if not args:
        sys.exit(__doc__)
    if args[0] == "--issue":
        out = subprocess.run(["gh", "issue", "view", args[1], "--json", "title,body"],
                             capture_output=True, text=True, check=True).stdout
        issue = json.loads(out)
        term = re.sub(r"^exit:\s*", "", issue["title"], flags=re.I)
        term = re.sub(r"\s*\(×\d+\)$", "", term).strip()
        print(f"# Research pack: {term}\n\nFrom issue: {issue['title']}\n> {issue['body'][:500]}")
    else:
        term = " ".join(args).strip()
        print(f"# Research pack: {term}")

    t = term.lower()
    slug = re.sub(r"[^a-z0-9]+", "-", t).strip("-")
    print(f"\nProposed id: `{slug}`  → data/exits/{slug}.yaml")

    section("ToS;DR (terms-of-service rating) — enrich.tosdr")
    d = fetch_json(f"https://api.tosdr.org/search/v5/?query={urllib.request.quote(t)}")
    for s in (d.get("services") or [])[:3]:
        print(f"- {s['name']}: rating {s.get('rating')} (slug for enrich: '{t}' matched; "
              f"service id {s['id']}, urls {s.get('urls', [])[:2]})")
    if not d.get("services"):
        print("- no match")

    section("JustDeleteMe (deletion link) — enrich.justdeleteme")
    sites = fetch_json("https://raw.githubusercontent.com/justdeleteme/justdelete.me/master/sites.json")
    hits = [s for s in (sites if isinstance(sites, list) else [])
            if t in s["name"].lower()]
    for s in hits[:5]:
        print(f"- name: '{s['name']}'  difficulty: {s.get('difficulty')}  url: {s.get('url')}")
        if s.get("notes"):
            print(f"  notes: {s['notes']}")
    if not hits:
        print("- no match")

    section("Awesome Privacy (alternatives) — alternative enrich.awesome_privacy")
    ap = fetch_text("https://raw.githubusercontent.com/Lissy93/awesome-privacy/main/awesome-privacy.yml")
    if ap:
        # find categories/sections mentioning the term, list their services
        import yaml
        data = yaml.safe_load(ap)
        found = []
        for cat in data.get("categories", []):
            for sec in cat.get("sections", []):
                blob = json.dumps(sec).lower()
                if t in blob:
                    names = [s.get("name") for s in sec.get("services") or []]
                    found.append(f"- section '{sec.get('name')}' (category {cat.get('name')}): {names[:12]}")
        print("\n".join(found[:6]) or "- term not mentioned; consider searching by category")

    section("awesome-selfhosted (self-host path) — alternative enrich.awesome_selfhosted")
    listing = fetch_json("https://api.github.com/repos/awesome-selfhosted/awesome-selfhosted-data/contents/software")
    if isinstance(listing, list):
        slugs = [f["name"][:-4] for f in listing if f["name"].endswith(".yml")]
        near = [s for s in slugs if t.replace(" ", "") in s.replace("-", "")]
        print(f"- slug matches: {near[:10] or 'none'}")
        print("- (for category alternatives, browse https://awesome-selfhosted.net)")

    section("web3privacy (privacy/crypto alternatives) — alternative enrich.web3privacy")
    w3p = fetch_json("https://explorer-data.web3privacy.info/index.json")
    if "projects" in w3p:
        near = [p["id"] for p in w3p["projects"] if t in p.get("name", "").lower()]
        print(f"- project matches: {near[:10] or 'none'}")

    section("Existing exits (style reference + duplicates)")
    existing = sorted(p.stem for p in (ROOT / "data" / "exits").glob("*.yaml")
                      if not p.name.startswith("_"))
    dup = [e for e in existing if slug in e or e in slug]
    print(f"- current exits: {existing}")
    print(f"- possible duplicate: {dup or 'none'}")

    section("Drafting checklist")
    print("""- copy data/exits/_template.yaml -> data/exits/{slug}.yaml
- only set enrich keys confirmed above; only claim recommended_by a source actually makes
- stub: true if no curated routes yet — the agent prompt still must be useful
- sensitive topic? defer to professional help in the prompt (see CLAUDE.md rules)
- validate: python3 build.py --offline""".replace("{slug}", slug))


if __name__ == "__main__":
    main()
