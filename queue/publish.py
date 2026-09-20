# Publishes the next queued article. Run by .github/workflows/daily-publish.yml
import json, os, re, pathlib
Q = pathlib.Path("queue")
man = json.loads((Q / "manifest.json").read_text(encoding="utf-8"))
slugs = [a["slug"] for a in man]
live = {s for s in slugs if pathlib.Path(s).exists()}
nxt = next((a for a in man if a["slug"] not in live), None)
out = os.environ.get("GITHUB_OUTPUT")
def setout(k, v):
    if out:
        with open(out, "a") as f:
            f.write(f"{k}={v}\n")
    print(f"{k}={v}")
if nxt:
    live.add(nxt["slug"])
    card = f'<div class="card"><a href="{nxt["slug"]}">{nxt["title"]}</a>\n<p>{nxt["desc"]}</p></div>'
    for f in ("guides.html", "index.html"):
        p = pathlib.Path(f)
        t = p.read_text(encoding="utf-8")
        if f'href="{nxt["slug"]}"' not in t and "<!--AUTO-CARDS-->" in t:
            t = t.replace("<!--AUTO-CARDS-->", "<!--AUTO-CARDS-->\n" + card, 1)
            p.write_text(t, encoding="utf-8")
    setout("slug", nxt["slug"])
else:
    setout("slug", "none")
pending = [s for s in slugs if s not in live]
# Re-render every live queued article from its source, turning links to
# not-yet-published articles into plain text so nothing 404s.
for s in sorted(live):
    t = (Q / s).read_text(encoding="utf-8")
    for pnd in pending:
        t = re.sub(r'<a href="' + re.escape(pnd) + r'"[^>]*>(.*?)</a>', r"\1", t, flags=re.S)
    pathlib.Path(s).write_text(t, encoding="utf-8")
setout("remaining", len(pending))
