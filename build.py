#!/usr/bin/env python3
"""exit.tech static site builder.

Reads data/exits.yaml (our dependency -> exit-paths mapping) and
data/sources.yaml (credited external sources), enriches exits with live
data from those sources (cached in data/cache/), renders public/.

Usage: python3 build.py [--offline]   (--offline: cache only, no network)
"""

import json
import re
import sys
import urllib.request
from pathlib import Path

import yaml

ROOT = Path(__file__).parent
CACHE = ROOT / "data" / "cache"
PUBLIC = ROOT / "public"
OFFLINE = "--offline" in sys.argv

UA = {"User-Agent": "exit.tech-builder/0.1 (https://github.com/xAlisher/exit-tech)"}


def fetch(key: str, url: str) -> str | None:
    """Fetch url, caching body under data/cache/<key>. Returns None on failure."""
    CACHE.mkdir(parents=True, exist_ok=True)
    path = CACHE / key
    if path.exists():
        return path.read_text()
    if OFFLINE:
        return None
    try:
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=20) as r:
            body = r.read().decode("utf-8", "replace")
        path.write_text(body)
        return body
    except Exception as e:
        print(f"  warn: fetch failed for {key}: {e}", file=sys.stderr)
        return None


# --- source fetchers ----------------------------------------------------------

def tosdr_rating(slug: str) -> dict | None:
    body = fetch(f"tosdr-{slug}.json", f"https://api.tosdr.org/search/v5/?query={slug}")
    if not body:
        return None
    services = json.loads(body).get("services") or []
    if not services:
        return None
    s = services[0]
    return {"name": s["name"], "rating": s.get("rating"),
            "url": f"https://tosdr.org/en/service/{s['id']}"}


def justdeleteme(name: str) -> dict | None:
    body = fetch("justdeleteme-sites.json",
                 "https://raw.githubusercontent.com/justdeleteme/justdelete.me/master/sites.json")
    if not body:
        return None
    for site in json.loads(body):
        if site["name"].lower() == name.lower():
            return {"url": site.get("url"), "difficulty": site.get("difficulty"),
                    "notes": site.get("notes")}
    return None


def awesome_privacy(name: str) -> dict | None:
    body = fetch("awesome-privacy.yml",
                 "https://raw.githubusercontent.com/Lissy93/awesome-privacy/main/awesome-privacy.yml")
    if not body:
        return None
    data = yaml.safe_load(body)
    for cat in data.get("categories", []):
        for sec in cat.get("sections", []):
            for svc in sec.get("services", []) or []:
                if svc.get("name", "").lower() == name.lower():
                    return {"description": svc.get("description"),
                            "openSource": svc.get("openSource"),
                            "securityAudited": svc.get("securityAudited")}
    return None


def awesome_selfhosted(slug: str) -> dict | None:
    body = fetch(f"awesome-selfhosted-{slug}.yml",
                 f"https://raw.githubusercontent.com/awesome-selfhosted/awesome-selfhosted-data/master/software/{slug}.yml")
    if not body:
        return None
    d = yaml.safe_load(body)
    return {"description": d.get("description"), "license": d.get("licenses"),
            "language": d.get("platforms"), "source": d.get("source_code_url")}


def web3privacy(slug: str) -> dict | None:
    body = fetch(f"web3privacy-{slug}.yml",
                 f"https://raw.githubusercontent.com/web3privacy/explorer-data/main/src/projects/{slug}/index.yaml")
    if not body:
        return None
    d = yaml.safe_load(body)
    return {"description": d.get("description"),
            "openSource": (d.get("blockchain_features") or {}).get("opensource")}


# --- enrichment ---------------------------------------------------------------

def enrich_exit(ex: dict) -> dict:
    keys = ex.get("enrich") or {}
    live = {}
    if "tosdr" in keys:
        live["tosdr"] = tosdr_rating(keys["tosdr"])
    if "justdeleteme" in keys:
        live["justdeleteme"] = justdeleteme(keys["justdeleteme"])
    if "justgetmydata" in keys:
        live["justgetmydata"] = {"url": f"https://justgetmydata.com/#{keys['justgetmydata']}"}
    ex["live"] = {k: v for k, v in live.items() if v}

    for path in ex.get("paths", []):
        for alt in path.get("alternatives", []):
            akeys = alt.get("enrich") or {}
            if "awesome_privacy" in akeys:
                alt["live"] = awesome_privacy(akeys["awesome_privacy"])
            elif "awesome_selfhosted" in akeys:
                alt["live"] = awesome_selfhosted(akeys["awesome_selfhosted"])
            elif "web3privacy" in akeys:
                alt["live"] = web3privacy(akeys["web3privacy"])
    return ex


def build_prompt(ex: dict) -> str:
    """Assemble the copy-paste agent prompt for an exit from its data."""
    lines = [f"I want to exit {ex['name']}. Act as my exit guide.", ""]
    if ex.get("extract"):
        lines.append("First, help me get my data out:")
        lines += [f"- {s['step']}" for s in ex["extract"]]
        lines.append("")
    for path in ex.get("paths", []):
        alts = ", ".join(a["name"] for a in path["alternatives"])
        lines.append(f"{path['label']}: help me choose between {alts} based on my situation — ask me what matters before recommending.")
    jdm = (ex.get("live") or {}).get("justdeleteme")
    if jdm and jdm.get("url"):
        lines.append(f"When I'm ready, walk me through deleting my account "
                     f"(difficulty: {jdm.get('difficulty', 'unknown')}): {jdm['url']}")
    lines.append("")
    lines += ex.get("prompt", [])
    lines += ["", "Go step by step. One thing at a time. I want to actually finish this."]
    return "\n".join(lines)


# --- rendering ----------------------------------------------------------------

def esc(s) -> str:
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            .replace('"', "&quot;"))


def page(title: str, body: str, depth: int = 0, header: bool = True) -> str:
    pre = "../" * depth
    header_html = (f'\n<header><a class="tag" href="{pre}index.html">Exit is culture'
                   '<span class="cursor"></span></a></header>') if header else ""
    body_class = "" if header else ' class="home"'
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(title)}</title>
<link rel="stylesheet" href="{pre}style.css">
</head>
<body{body_class}>{header_html}
<main>
{body}
</main>
<footer>
  <a href="{pre}sources.html">sources &amp; credits</a> ·
  <a href="{pre}exits.json">open data</a> ·
  <a href="https://github.com/xAlisher/exit-tech">github</a>
</footer>
</body>
</html>"""


def badge_row(refs: list, sources_by_id: dict) -> str:
    out = []
    for r in refs:
        s = sources_by_id.get(r)
        label = s["name"] if s else r
        out.append(f'<a class="badge" href="../sources.html#{esc(r)}" title="{esc(label)}">{esc(r)}</a>')
    return f'<div class="badges">via {" ".join(out)}</div>'


def render_exit(ex: dict, sources_by_id: dict) -> str:
    b = [f'<p class="crumb">~/exit/{esc(ex["id"])}</p>',
         f'<h1>Exit {esc(ex["name"])}</h1>',
         f'<p class="tagline">{esc(ex["tagline"])}</p>']

    b.append("<h2>// why</h2><ul>")
    b += [f"<li>{esc(w)}</li>" for w in ex.get("why", [])]
    tosdr = (ex.get("live") or {}).get("tosdr")
    if tosdr and tosdr.get("rating"):
        b.append(f'<li>Terms of service rated <strong>“{esc(tosdr["rating"])}”</strong> '
                 f'— <a href="{esc(tosdr["url"])}">see the documented points at ToS;DR</a></li>')
    b.append("</ul>")

    extract = list(ex.get("extract") or [])
    jgmd = (ex.get("live") or {}).get("justgetmydata")
    if extract or jgmd:
        b.append("<h2>// first, get your stuff out</h2><ol>")
        b += [f"<li>{esc(s['step'])}</li>" for s in extract]
        if jgmd:
            b.append(f'<li><a href="{esc(jgmd["url"])}">Data export links at JustGetMyData</a></li>')
        b.append("</ol>")

    if ex.get("stub"):
        b.append("<h2>// exit routes</h2>")
        b.append('<p>This exit is still being mapped — no curated routes yet. The prompt '
                 'below already works. Want this page to exist properly? '
                 '<a href="https://github.com/xAlisher/exit-tech">Help chart it.</a></p>')
    else:
        b.append("<h2>// exit paths</h2>")
    for path in ex.get("paths", []):
        b.append(f'<h3><span class="ptype">[{esc(path["type"])}]</span> {esc(path["label"])}</h3>')
        for alt in path["alternatives"]:
            live = alt.get("live") or {}
            desc = alt.get("note") or live.get("description") or ""
            flags = []
            if live.get("openSource"):
                flags.append("open source")
            if live.get("securityAudited"):
                flags.append("audited")
            flag_html = f' <span class="flags">{esc(" · ".join(flags))}</span>' if flags else ""
            b.append('<div class="alt">'
                     f'<a class="alt-name" href="{esc(alt["url"])}">{esc(alt["name"])}</a>{flag_html}'
                     f'<p>{esc(desc)}</p>'
                     f'{badge_row(alt.get("recommended_by", []), sources_by_id)}'
                     "</div>")

    jdm = (ex.get("live") or {}).get("justdeleteme")
    if jdm and jdm.get("url"):
        b.append("<h2>// burn the bridge</h2>")
        diff = jdm.get("difficulty", "unknown")
        b.append(f'<p>Delete your account (difficulty: <strong>{esc(diff)}</strong>) — '
                 f'<a href="{esc(jdm["url"])}">direct link via JustDeleteMe</a></p>')

    b.append("<h2>// take an agent with you</h2>")
    b.append("<p>Paste this into Claude, ChatGPT or your agent of choice and it will walk you through the exit, personalized:</p>")
    b.append(f'<pre id="prompt">{esc(ex["agent_prompt"])}</pre>')
    b.append('<button onclick="navigator.clipboard.writeText(document.getElementById(\'prompt\').innerText).then(()=>{this.innerText=\'copied ✓\'})">copy prompt</button>')
    return page(f"Exit {ex['name']} — exit.tech", "\n".join(b), depth=1)


def render_index(exits: list) -> str:
    targets = json.dumps([{"id": ex["id"], "name": ex["name"]} for ex in exits])
    body = f'''<div class="hero">
<label for="q" class="promptline">Exit&nbsp;</label><span class="wrap">
<span class="ghost" aria-hidden="true"><span id="gcur"></span><i id="gpad"></i><span id="grest"></span></span>
<input id="q" class="empty" autocomplete="off" spellcheck="false" aria-label="what do you want to exit">
</span>
</div>
<p id="nohit" hidden>No exit here yet. That's the point of the prototype — <a href="https://github.com/xAlisher/exit-tech">ask for it</a>.</p>
<script>
const EXITS = {targets};
const q = document.getElementById('q'),
      gpad = document.getElementById('gpad'),
      grest = document.getElementById('grest'),
      gcur = document.getElementById('gcur');
let match = null;

function update() {{
  const empty = !q.value;
  gcur.hidden = !empty;
  q.classList.toggle('empty', empty);
  const v = q.value.trim().toLowerCase();
  match = v ? (EXITS.find(e => e.name.toLowerCase().startsWith(v))
            || EXITS.find(e => e.name.toLowerCase().includes(v))) : null;
  document.getElementById('nohit').hidden = !(v && !match);
  gpad.textContent = ''; grest.textContent = '';
  if (match) {{
    if (match.name.toLowerCase().startsWith(v)) {{
      gpad.textContent = q.value;
      grest.textContent = match.name.slice(q.value.length) + '  ⏎';
    }} else {{
      gpad.textContent = q.value;
      grest.textContent = '  → ' + match.name + '  ⏎';
    }}
  }}
}}

// --- idle glitch: random service names scramble in and dissolve ---
const GLYPHS = "!<>-_\\\\/[]{{}}=+*^?#░▒▓";
let glitchTimer = null, glitchAnim = null;

function glyph() {{ return GLYPHS[Math.random() * GLYPHS.length | 0]; }}

function stopGlitch() {{
  clearTimeout(glitchTimer); clearInterval(glitchAnim);
  glitchTimer = glitchAnim = null;
  if (!q.value) {{ gpad.textContent = ''; grest.textContent = ''; }}
}}


function scheduleGlitch(delay) {{
  clearTimeout(glitchTimer);
  glitchTimer = setTimeout(fireGlitch, delay);
}}

function fireGlitch() {{
  if (q.value) return;
  const name = EXITS[Math.random() * EXITS.length | 0].name;
  const locks = [...name].map(() => 6 + (Math.random() * 14 | 0));
  const hold = 34, fadeStart = Math.max(...locks) + hold;
  let f = 0;
  clearInterval(glitchAnim);
  glitchAnim = setInterval(() => {{
    if (q.value) {{ stopGlitch(); return; }}
    let out = '';
    [...name].forEach((ch, i) => {{
      if (f >= fadeStart) out += (f - fadeStart > 1) ? '' : glyph();
      else if (f >= locks[i]) out += ch;
      else out += glyph();
    }});
    grest.textContent = out;
    f++;
    if (f > fadeStart + 3) {{
      clearInterval(glitchAnim); glitchAnim = null;
      grest.textContent = '';
      scheduleGlitch(900 + Math.random() * 2000);
    }}
  }}, 40);
}}

scheduleGlitch(600);

q.addEventListener('input', () => {{
  if (q.value) stopGlitch();
  else scheduleGlitch(800 + Math.random() * 1500);
  update();
}});
q.addEventListener('keydown', e => {{
  const caretAtEnd = q.selectionStart === q.value.length && q.selectionEnd === q.value.length;
  if ((e.key === 'Tab' || (e.key === 'ArrowRight' && caretAtEnd)) && match && q.value) {{
    e.preventDefault();
    q.value = match.name;
    update();
  }} else if (e.key === 'Enter' && match) {{
    location.href = 'exit/' + match.id + '.html';
  }} else if (e.key === 'Escape') {{
    q.value = '';
    update();
  }}
}});
</script>'''
    return page("exit.tech", body, header=False)


def render_sources(sources: list) -> str:
    b = ["<h1>Sources &amp; credits</h1>",
         "<p>exit.tech is an index over the existing exit ecosystem. Every recommendation "
         "is aggregated from these open projects — visit them, contribute to them, fund them. "
         "Our merged dataset is published openly at <a href='exits.json'>exits.json</a>.</p>"]
    for s in sources:
        status = "" if s["status"] == "wired" else ' <span class="flags">(integration planned)</span>'
        b.append(f'''<div class="alt" id="{esc(s["id"])}">
<a class="alt-name" href="{esc(s["url"])}">{esc(s["name"])}</a>{status}
<p>{esc(s["role"])}</p>
<div class="badges">license: {esc(s["license"])} · <a href="{esc(s["data"])}">data</a></div>
</div>''')
    return page("Sources & credits — exit.tech", "\n".join(b))


CSS = """
* { margin: 0; padding: 0; box-sizing: border-box; }
:root { --fg: #fff; --dim: #888; --line: #2a2a2a; --acc: #6f6; }
html, body { background: #000; color: var(--fg);
  font-family: ui-monospace, "JetBrains Mono", Menlo, monospace; font-size: 14px; line-height: 1.6; }
main { max-width: 720px; margin: 0 auto; padding: 96px 20px 64px; }
header { position: fixed; top: 32px; left: 40px; }
.tag { font-size: 13px; color: var(--fg); letter-spacing: 0.04em; text-decoration: none;
  display: flex; align-items: center; gap: 2px; }
.cursor { display: inline-block; width: 7px; height: 13px; background: var(--fg);
  animation: blink 1s step-end infinite; }
@keyframes blink { 0%, 100% { opacity: 1; } 50% { opacity: 0; } }
a { color: var(--acc); text-decoration: none; }
a:hover { text-decoration: underline; }
h1 { font-size: 22px; margin: 8px 0 4px; font-weight: 600; }
h2 { font-size: 13px; color: var(--dim); margin: 40px 0 12px; font-weight: 400;
  letter-spacing: 0.06em; }
h3 { font-size: 14px; margin: 24px 0 8px; font-weight: 600; }
.ptype { color: var(--acc); font-weight: 400; }
.crumb { color: var(--dim); font-size: 12px; }
.tagline { color: var(--dim); margin-bottom: 8px; }
ul, ol { padding-left: 20px; }
li { margin: 6px 0; }
body.home { display: flex; flex-direction: column; min-height: 100vh; }
body.home main { flex: 1; display: flex; flex-direction: column; justify-content: center;
  width: 100%; padding: 20px; }
body.home footer { padding-bottom: 32px; }
.hero { font-size: 20px; display: flex; align-items: center; justify-content: center; }
.hero .wrap { flex: 0 0 20ch; }
#nohit { margin-top: 16px; color: var(--dim); text-align: center; }
.promptline { white-space: pre; }
.wrap { position: relative; flex: 1; }
#q { background: none; border: none; outline: none; color: var(--acc);
  font: inherit; caret-color: var(--acc); width: 100%; position: relative;
  padding: 0; line-height: 28px; height: 28px; display: block; }
.ghost { position: absolute; left: 0; top: 0; color: var(--dim); pointer-events: none;
  white-space: pre; line-height: 28px; }
.ghost i { visibility: hidden; font-style: normal; }
#gcur { display: inline-block; width: 3px; height: 19px; background: var(--acc);
  animation: blink 1s step-end infinite; vertical-align: -2px; margin-right: 3px; }
#gcur[hidden] { display: none; }
#q.empty { caret-color: transparent; }
.alt { border: 1px solid var(--line); padding: 14px 18px; margin: 10px 0; }
.alt-name { font-weight: 600; color: var(--fg); }
.alt p { color: var(--dim); margin: 4px 0; }
.flags { color: var(--acc); font-size: 12px; }
.badges { font-size: 11px; color: var(--dim); margin-top: 6px; }
.badge { color: var(--dim); border: 1px solid var(--line); padding: 1px 6px; margin-right: 4px; }
.badge:hover { color: var(--acc); border-color: var(--acc); text-decoration: none; }
pre { border: 1px solid var(--line); padding: 16px; white-space: pre-wrap;
  color: var(--dim); font-size: 12.5px; margin: 12px 0; }
button { background: none; border: 1px solid var(--acc); color: var(--acc); font: inherit;
  padding: 6px 16px; cursor: pointer; }
button:hover { background: var(--acc); color: #000; }
footer { max-width: 720px; margin: 0 auto; padding: 0 20px 48px; color: #444;
  font-size: 12px; }
footer a { color: #444; }
footer a:hover { color: var(--dim); }
"""


def main():
    exits = yaml.safe_load((ROOT / "data" / "exits.yaml").read_text())
    sources = yaml.safe_load((ROOT / "data" / "sources.yaml").read_text())
    sources_by_id = {s["id"]: s for s in sources}

    print(f"building {len(exits)} exits...")
    for ex in exits:
        enrich_exit(ex)
        ex["agent_prompt"] = build_prompt(ex)
        print(f"  {ex['id']}: live={list((ex.get('live') or {}).keys())}")

    (PUBLIC / "exit").mkdir(parents=True, exist_ok=True)
    (PUBLIC / "style.css").write_text(CSS.strip() + "\n")
    (PUBLIC / "index.html").write_text(render_index(exits))
    (PUBLIC / "sources.html").write_text(render_sources(sources))
    for ex in exits:
        (PUBLIC / "exit" / f"{ex['id']}.html").write_text(render_exit(ex, sources_by_id))

    # published merged dataset (the share-alike obligation, honored)
    (PUBLIC / "exits.json").write_text(json.dumps(
        {"about": "exit.tech merged exit dataset. Aggregated from credited open sources — see /sources.html.",
         "exits": exits, "sources": sources}, indent=2, ensure_ascii=False))
    print(f"done → {PUBLIC}/")


if __name__ == "__main__":
    main()
