#!/usr/bin/env python3
"""Draft an exit page on the local model (llama-server on Sneg), then
truth-check and validate deterministically. Claude (or a human) reviews.

Usage:
  python3 .github/scripts/draft_local.py <term>
  python3 .github/scripts/draft_local.py --issue <number>
  LLAMA_URL=http://host:11435/v1 ...   (default: Sneg via Tailscale)

Pipeline:
  research (structured)  ->  qwen3 drafts YAML  ->  truth-check strips any
  enrichment/recommendation the research pack didn't confirm  ->
  build.py --offline validates  ->  on failure, errors fed back, retry (max 3)

Writes data/exits/<slug>.yaml and prints a report. Does NOT commit.
"""

import json
import re
import subprocess
import sys
import urllib.request
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).parent))
from research_exit import research  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
LLAMA_URL = __import__("os").environ.get("LLAMA_URL", "http://100.108.127.3:11435/v1")
MAX_ATTEMPTS = 3


def llm(messages: list, max_tokens: int = 3000) -> str:
    body = json.dumps({
        "model": "qwen3",
        "messages": messages,
        "max_tokens": max_tokens,
        "chat_template_kwargs": {"enable_thinking": False},
    }).encode()
    req = urllib.request.Request(
        f"{LLAMA_URL}/chat/completions", data=body,
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=600) as r:
        d = json.loads(r.read())
    return d["choices"][0]["message"]["content"] or ""


def build_prompt(pack: dict) -> list:
    template = (ROOT / "data/exits/_template.yaml").read_text()
    rules = (ROOT / "docs/skills/drafting-exits.md").read_text()
    examples = "\n---\n".join(
        f"# data/exits/{n}.yaml\n" + (ROOT / f"data/exits/{n}.yaml").read_text()
        for n in ("whatsapp", "spotify"))
    system = f"""You draft exit pages for exit.tech — guides for leaving dependencies.

Follow these house rules:
{rules}

The file schema (template with comments):
{template}

Two examples of the voice and structure:
{examples}"""
    user = f"""Draft data/exits/{pack['slug']}.yaml for the dependency: {pack['term']}

Research pack (the ONLY facts you may claim — JSON):
{json.dumps(pack, indent=2, ensure_ascii=False)}

Hard rules:
- id must be exactly: {pack['slug']}
- Only include an `enrich` key if the research pack confirms it (tosdr non-empty,
  justdeleteme non-empty — use the exact 'name' value from the pack).
- Do NOT include enrich.justgetmydata (unverified by research).
- Only include `recommended_by` for an alternative if the research pack explicitly
  lists that alternative under that source. When in doubt, omit recommended_by.
- If you can't name genuinely good exit routes from the research, set `stub: true`
  and put the value into the agent prompt instead.
- Output ONLY the YAML file content. No markdown fences, no commentary."""
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]


def extract_yaml(text: str) -> str:
    text = text.strip()
    m = re.search(r"```(?:yaml)?\n(.*?)```", text, re.S)
    if m:
        text = m.group(1)
    return text.strip() + "\n"


def truth_check(doc: dict, pack: dict) -> list[str]:
    """Strip every claim the research pack doesn't confirm. Returns notes."""
    notes = []
    enrich = doc.get("enrich") or {}

    if "tosdr" in enrich and not pack["tosdr"]:
        notes.append(f"stripped enrich.tosdr '{enrich.pop('tosdr')}' — no ToS;DR match in research")
    jdm_names = {s["name"] for s in pack["justdeleteme"]}
    if "justdeleteme" in enrich and enrich["justdeleteme"] not in jdm_names:
        notes.append(f"stripped enrich.justdeleteme '{enrich.pop('justdeleteme')}' — not in research ({jdm_names or 'no matches'})")
    if "justgetmydata" in enrich:
        notes.append(f"stripped enrich.justgetmydata '{enrich.pop('justgetmydata')}' — unverifiable")
    if not enrich:
        doc.pop("enrich", None)

    ap_services = {s.lower() for sec in pack["awesome_privacy_sections"]
                   for s in sec["services"]}
    ash_slugs = set(pack["awesome_selfhosted_slugs"])
    w3p_ids = set(pack["web3privacy_ids"])

    for path in doc.get("paths") or []:
        for alt in path.get("alternatives") or []:
            a_enrich = alt.get("enrich") or {}
            if "awesome_privacy" in a_enrich and a_enrich["awesome_privacy"].lower() not in ap_services:
                notes.append(f"stripped {alt.get('name')}.enrich.awesome_privacy — not confirmed")
                a_enrich.pop("awesome_privacy")
            if "awesome_selfhosted" in a_enrich and a_enrich["awesome_selfhosted"] not in ash_slugs:
                notes.append(f"stripped {alt.get('name')}.enrich.awesome_selfhosted — not confirmed")
                a_enrich.pop("awesome_selfhosted")
            if "web3privacy" in a_enrich and a_enrich["web3privacy"] not in w3p_ids:
                notes.append(f"stripped {alt.get('name')}.enrich.web3privacy — not confirmed")
                a_enrich.pop("web3privacy")
            if not a_enrich:
                alt.pop("enrich", None)

            confirmed_sources = set()
            if alt.get("name", "").lower() in ap_services:
                confirmed_sources.add("awesome-privacy")
            if (alt.get("enrich") or {}).get("awesome_selfhosted") in ash_slugs:
                confirmed_sources.add("awesome-selfhosted")
            if (alt.get("enrich") or {}).get("web3privacy") in w3p_ids:
                confirmed_sources.add("web3privacy")
            kept, dropped = [], []
            for ref in alt.get("recommended_by") or []:
                (kept if ref in confirmed_sources else dropped).append(ref)
            if dropped:
                notes.append(f"stripped {alt.get('name')}.recommended_by {dropped} — research can't confirm; reviewer may restore with evidence")
            if kept:
                alt["recommended_by"] = kept
            else:
                alt.pop("recommended_by", None)
    return notes


def validate() -> tuple[bool, str]:
    r = subprocess.run([sys.executable, "build.py", "--offline"],
                       capture_output=True, text=True, cwd=ROOT)
    return r.returncode == 0, (r.stderr or r.stdout)


def main():
    args = sys.argv[1:]
    if not args:
        sys.exit(__doc__)
    if args[0] == "--issue":
        out = subprocess.run(["gh", "issue", "view", args[1], "--json", "title"],
                             capture_output=True, text=True, check=True).stdout
        term = re.sub(r"^exit:\s*", "", json.loads(out)["title"], flags=re.I)
        term = re.sub(r"\s*\(×\d+\)$", "", term).strip()
    else:
        term = " ".join(args).strip()

    print(f"researching '{term}'...")
    pack = research(term)
    if pack["possible_duplicates"]:
        sys.exit(f"possible duplicate of existing exit: {pack['possible_duplicates']}")
    target = ROOT / "data" / "exits" / f"{pack['slug']}.yaml"
    if target.exists():
        sys.exit(f"{target} already exists")

    messages = build_prompt(pack)
    all_notes = []
    for attempt in range(1, MAX_ATTEMPTS + 1):
        print(f"drafting (attempt {attempt}, local model)...")
        raw = llm(messages)
        text = extract_yaml(raw)
        try:
            doc = yaml.safe_load(text)
            assert isinstance(doc, dict)
        except Exception as e:
            messages += [{"role": "assistant", "content": raw},
                         {"role": "user", "content": f"That was not valid YAML ({e}). Output only the corrected YAML file."}]
            continue

        doc["id"] = pack["slug"]
        notes = truth_check(doc, pack)
        all_notes += notes
        out_text = "# drafted by qwen3.6-27b (local, Sneg) — pending review\n" + yaml.dump(
            doc, sort_keys=False, allow_unicode=True, width=100)
        target.write_text(out_text)

        ok, log = validate()
        if ok:
            print(f"\n✓ draft written: {target.relative_to(ROOT)}")
            if all_notes:
                print("\ntruth-check strips (reviewer: investigate/restore with evidence):")
                for n in all_notes:
                    print(f"  - {n}")
            print("\nnext: review the draft (tagline, prompt, tone), then commit on a draft/ branch.")
            return
        print(f"  validation failed:\n{log}")
        messages += [{"role": "assistant", "content": raw},
                     {"role": "user", "content": f"The file failed validation:\n{log}\nOutput the corrected full YAML file only."}]

    target.unlink(missing_ok=True)
    sys.exit(f"failed after {MAX_ATTEMPTS} attempts")


if __name__ == "__main__":
    main()
