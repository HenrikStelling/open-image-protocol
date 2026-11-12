#!/usr/bin/env python3
"""Story map: paint recent repository activity onto the structure of docs/STORY.md.

Reads the story file and the git log, writes one self-contained HTML page showing, for each pipeline stage and each
application tier, how many commits touched its files in the window, the newest of them, and whether the working tree has
uncommitted changes there; then the story deltas as a timeline, the scars as a count per lesson, and the status section.

    python scripts/story_map.py                    # last 14 days -> docs/story-map.html
    python scripts/story_map.py --days 30 --out /tmp/map.html
    python scripts/story_map.py --open             # also open it in the default browser

Pure standard library. Run from the repository root (or pass --repo).
"""
from __future__ import annotations
import argparse, datetime as dt, html, re, subprocess, sys, webbrowser
from pathlib import Path

# ---- the structure of the story: which files belong to which box ----------------------------------------------------
STAGES = [
    ("1 De-identify", ["src/oip/deid.py"]),
    ("2 Geometry", ["src/oip/geometry.py"]),
    ("3 Renders", ["src/oip/render.py", "src/oip/fonts/"]),
    ("4 Manifest", ["src/oip/convert.py", "src/oip/convert_image.py", "src/oip/adapters.py", "src/oip/identity.py"]),
    ("5 Reference file", ["src/oip/context.py"]),
    ("6 Validate", ["src/oip/validate.py", "spec/schemas/"]),
    ("7a Anatomy + measure", ["src/oip/anatomy.py", "src/oip/anatomy_cxas.py", "src/oip/measure.py", "scripts/cxas_worker.py"]),
    ("7b Pixel check", ["src/oip/check.py"]),
    ("Verbs: CLI, tools, MCP", ["src/oip/cli.py", "src/oip/tools.py", "src/oip/mcp_server.py"]),
]
TIERS = [
    ("Protocol", ["spec/", "docs/01-reference-protocols/", "docs/03-brainstorm/"]),
    ("Reference implementation", ["src/", "scripts/", "tests/", "pyproject.toml", "Makefile"]),
    ("Evidence", ["bench/", "docs/reports/"]),
    ("Paper and governance", ["docs/paper/", "PLAN.md", "CHANGELOG.md", "CITATION.cff", "README.md", "REPRODUCE.md", "CONTRIBUTING.md"]),
    ("The story itself", ["docs/STORY.md", "docs/story-map.html", "scripts/story_map.py", "CLAUDE.md"]),
]


def _matches(path: str, patterns: list[str]) -> bool:
    return any(path == p or (p.endswith("/") and path.startswith(p)) for p in patterns)


# ---- git ----------------------------------------------------------------------------------------------------------------
def git(repo: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, check=True).stdout


def commits_since(repo: Path, days: int) -> list[dict]:
    since = (dt.date.today() - dt.timedelta(days=days)).isoformat()
    raw = git(repo, "log", f"--since={since}", "--date=short", "--format=%x1e%h%x1f%ad%x1f%s", "--name-only")
    out = []
    for block in raw.split("\x1e"):
        block = block.strip()
        if not block:
            continue
        head, _, files = block.partition("\n")
        h, d, s = head.split("\x1f")
        out.append({"hash": h, "date": d, "subject": s, "files": [f for f in files.splitlines() if f.strip()]})
    return out


def dirty_files(repo: Path) -> list[str]:
    return [line[3:].strip() for line in git(repo, "status", "--porcelain", "--untracked-files=all").splitlines() if line.strip()]


def activity(boxes, commits, dirty):
    rows = []
    for name, pats in boxes:
        hits = [c for c in commits if any(_matches(f, pats) for f in c["files"])]
        rows.append({"name": name, "count": len(hits), "latest": hits[0] if hits else None,
                     "dirty": sum(1 for f in dirty if _matches(f, pats)), "paths": pats})
    return rows


# ---- the story file -----------------------------------------------------------------------------------------------------
def parse_story(text: str) -> dict:
    sections = re.split(r"^## ", text, flags=re.M)
    by_title = {}
    for s in sections[1:]:
        title, _, body = s.partition("\n")
        by_title[title.strip()] = body
    lessons = []
    scars_sec = next((b for t, b in by_title.items() if t.startswith("5.")), "")
    for part in re.split(r"^### ", scars_sec, flags=re.M)[1:]:
        title, _, body = part.partition("\n")
        bullets = re.findall(r"^- \*\*(.+?)\*\*", body, flags=re.M)
        lessons.append({"title": title.strip(), "n": len(bullets), "items": bullets})
    deltas_sec = next((b for t, b in by_title.items() if t.startswith("7.")), "")
    deltas = []
    for m in re.finditer(r"^- (\d{4}-\d{2}-\d{2}) — (.+?)(?=^- \d{4}-|\Z)", deltas_sec, flags=re.M | re.S):
        deltas.append({"date": m.group(1), "text": " ".join(m.group(2).split())})
    status_sec = next((b for t, b in by_title.items() if t.startswith("6.")), "")
    status = [" ".join(x.split()) for x in re.findall(r"^- (.+?)(?=^- |\Z|^Detail:)", status_sec, flags=re.M | re.S)]
    m = re.search(r"Last full rewrite: (\S+)", text)
    return {"lessons": lessons, "deltas": deltas, "status": status, "rewrite": m.group(1) if m else "?"}


# ---- html -----------------------------------------------------------------------------------------------------------------
CSS = """
:root{--bg:#f7f6f2;--fg:#1d1d1b;--mute:#6b6a64;--line:#dcdad2;--card:#fffffd;--h0:#ecece6;--h1:#dbe8d6;--h2:#b9d6ad;--h3:#8fbf7d;--h4:#5e9e4a;--warn:#c9742a;--acc:#2a5db0}
@media (prefers-color-scheme: dark){:root:not([data-theme=light]){--bg:#161714;--fg:#ebe9e2;--mute:#9b9a92;--line:#2f3029;--card:#1f201c;--h0:#24251f;--h1:#27362a;--h2:#2f4d31;--h3:#3f6f3c;--h4:#5a9a4f;--warn:#e09a55;--acc:#7fa6e6}}
:root[data-theme=dark]{--bg:#161714;--fg:#ebe9e2;--mute:#9b9a92;--line:#2f3029;--card:#1f201c;--h0:#24251f;--h1:#27362a;--h2:#2f4d31;--h3:#3f6f3c;--h4:#5a9a4f;--warn:#e09a55;--acc:#7fa6e6}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:15px/1.5 -apple-system,"Segoe UI",Helvetica,Arial,sans-serif}
main{max-width:1080px;margin:0 auto;padding:28px 16px 64px}h1{font-size:26px;margin:0 0 4px}h2{font-size:17px;margin:36px 0 10px;letter-spacing:.02em;text-transform:uppercase;color:var(--mute)}
.sub{color:var(--mute);margin:0 0 8px}.grid{display:grid;gap:10px;grid-template-columns:repeat(auto-fill,minmax(210px,1fr))}
.box{border:1px solid var(--line);border-radius:10px;padding:12px 14px;background:var(--card);position:relative;min-height:108px}
.box.h0{background:var(--h0)}.box.h1{background:var(--h1)}.box.h2{background:var(--h2)}.box.h3{background:var(--h3)}.box.h4{background:var(--h4);color:#fff}.box.h4 .m{color:#eee}
.box b{display:block;font-size:14px;padding-right:84px}.scars .box b{padding-right:0}.box .n{font-size:28px;font-weight:600;line-height:1.1;margin:2px 0}.box .m{font-size:12px;color:var(--mute);overflow:hidden;display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical}
.dirty{position:absolute;top:10px;right:12px;font-size:11px;color:var(--warn);font-weight:600}.box.h4 .dirty{color:#ffe3bf}
.flow{display:flex;flex-wrap:wrap;gap:8px;align-items:stretch}.flow .box{flex:1 1 150px}
ol.tl{list-style:none;padding:0;margin:0;border-left:2px solid var(--line)}ol.tl li{padding:4px 0 10px 16px;position:relative}ol.tl li::before{content:"";position:absolute;left:-7px;top:11px;width:10px;height:10px;border-radius:50%;background:var(--acc)}
ol.tl time{font-weight:600;margin-right:8px}.scars{display:grid;gap:10px;grid-template-columns:repeat(auto-fill,minmax(300px,1fr))}
.scars .box{min-height:0}.scars ul{margin:6px 0 0;padding-left:18px;font-size:13px;color:var(--mute)}
.legend{display:flex;gap:6px;align-items:center;font-size:12px;color:var(--mute);margin-top:8px}.legend i{display:inline-block;width:22px;height:12px;border-radius:3px;border:1px solid var(--line)}
footer{margin-top:40px;font-size:12px;color:var(--mute)}
"""


def heat(n: int) -> str:
    return "h0" if n == 0 else "h1" if n == 1 else "h2" if n <= 3 else "h3" if n <= 6 else "h4"


def box(r: dict, days: int) -> str:
    e = html.escape
    latest = f"{r['latest']['date']} · {e(r['latest']['subject'])}" if r["latest"] else f"untouched in {days} days"
    dirty = f"<span class=dirty>{r['dirty']} uncommitted</span>" if r["dirty"] else ""
    return (f"<div class='box {heat(r['count'])}' title='{e(', '.join(r['paths']))}'>{dirty}<b>{e(r['name'])}</b>"
            f"<div class=n>{r['count']}</div><div class=m>{latest}</div></div>")


def render(repo: Path, days: int, story: dict, stages, tiers, commits, dirty) -> str:
    e = html.escape
    head = git(repo, "log", "-1", "--format=%h %ad", "--date=short").strip()
    branch = git(repo, "rev-parse", "--abbrev-ref", "HEAD").strip()
    parts = [f"<!doctype html><html lang=en><head><meta charset=utf-8><meta name=viewport content='width=device-width,initial-scale=1'>"
             f"<title>OIP story map</title><style>{CSS}</style></head><body><main>",
             f"<h1>OIP story map</h1><p class=sub>Activity of the last {days} days painted onto the structure of <code>docs/STORY.md</code>. "
             f"Branch <code>{e(branch)}</code> at {e(head)} · {len(commits)} commits in the window · {len(dirty)} uncommitted files · story last rewritten {e(story['rewrite'].rstrip('.'))}.</p>",
             "<div class=legend>commits touching the box: <i style='background:var(--h0)'></i>0 <i style='background:var(--h1)'></i>1 <i style='background:var(--h2)'></i>2–3 <i style='background:var(--h3)'></i>4–6 <i style='background:var(--h4)'></i>7+</div>",
             "<h2>The pipeline (story section 2)</h2><div class=flow>", *[box(r, days) for r in stages], "</div>",
             "<h2>The tiers (story section 3.2)</h2><div class=grid>", *[box(r, days) for r in tiers], "</div>"]
    parts.append("<h2>Story deltas (section 7)</h2>")
    if story["deltas"]:
        parts.append("<ol class=tl>" + "".join(f"<li><time>{e(d['date'])}</time>{e(d['text'])}</li>" for d in reversed(story["deltas"])) + "</ol>")
    else:
        parts.append("<p class=sub>No deltas yet.</p>")
    if story["deltas"]:
        last = story["deltas"][-1]["date"]
        watched = [p for _, pats in STAGES + TIERS[:1] for p in pats]
        newer = [c for c in commits if c["date"] > last and any(_matches(f, watched) for f in c["files"])]
        if newer:
            parts.append(f"<p class=sub style='color:var(--warn)'>{len(newer)} commit(s) touched the pipeline or the protocol after the last delta ({e(last)}): "
                         + "; ".join(f"{e(c['hash'])} {e(c['subject'])}" for c in newer[:6]) + ("…" if len(newer) > 6 else "") + ". The story may be behind.</p>")
    parts.append("<h2>Scars by lesson (section 5)</h2><div class=scars>")
    for L in story["lessons"]:
        parts.append(f"<div class=box><b>{e(L['title'])}</b><div class=n>{L['n']}</div><ul>" + "".join(f"<li>{e(i)}</li>" for i in L["items"]) + "</ul></div>")
    parts.append("</div><h2>Where the work stands (section 6)</h2><ul>" + "".join(f"<li>{e(s)}</li>" for s in story["status"]) + "</ul>")
    parts.append(f"<footer>Generated {dt.datetime.now():%Y-%m-%d %H:%M} by scripts/story_map.py. Regenerate: <code>python scripts/story_map.py</code></footer></main></body></html>")
    return "\n".join(parts)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Story map: recent repository activity painted onto docs/STORY.md")
    ap.add_argument("--repo", default=".", help="repository root")
    ap.add_argument("--days", type=int, default=14)
    ap.add_argument("--out", default="docs/story-map.html")
    ap.add_argument("--open", action="store_true")
    a = ap.parse_args(argv)
    repo = Path(a.repo).resolve()
    story_path = repo / "docs" / "STORY.md"
    if not story_path.exists():
        sys.exit(f"no story file at {story_path}")
    story = parse_story(story_path.read_text())
    commits = commits_since(repo, a.days)
    dirty = dirty_files(repo)
    page = render(repo, a.days, story, activity(STAGES, commits, dirty), activity(TIERS, commits, dirty), commits, dirty)
    out = Path(a.out) if Path(a.out).is_absolute() else repo / a.out
    out.write_text(page)
    print(out)
    if a.open:
        webbrowser.open(out.as_uri())


if __name__ == "__main__":
    main()
