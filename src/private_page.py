"""Private sample page generator (no session data lives in the repo; pass dirs at run time).
Usage (from site/):
  python3 -m src.private_page --slug meta-coding-sessions-7k2q --sessions <dir_with_jsonl> --pool pool.json --password <pw> [--out <dir>]
Default --out is s/<slug>/ inside the site (deployed). Use --out elsewhere for previews."""
import argparse, hashlib, json, pathlib, sys, html
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src')); sys.path.insert(0, str(ROOT/'tools'))
import render_sessions
from pages import section, spec, cards, steps

GATE_JS = r'''
(function(){var g=document.getElementById('gate'),c=document.getElementById('content'),f=document.getElementById('gf'),e=document.getElementById('ge');
async function sha(s){const b=await crypto.subtle.digest('SHA-256',new TextEncoder().encode(s));return [...new Uint8Array(b)].map(x=>x.toString(16).padStart(2,'0')).join('')}
async function unlock(pw){if(await sha(pw)===g.dataset.h){c.hidden=false;g.hidden=true;try{sessionStorage.setItem('rs_'+g.dataset.k,'1')}catch(_){}}else{e.hidden=false}}
try{if(sessionStorage.getItem('rs_'+g.dataset.k)==='1'){c.hidden=false;g.hidden=true}}catch(_){}
f.addEventListener('submit',function(ev){ev.preventDefault();unlock(f.pw.value.trim())});
var dl=document.getElementById('dl-link');if(dl){var u=new URL(location.href);u.searchParams.set('f','1');dl.href=u.toString();}var dp=document.getElementById('dl-pack');if(dp){var u2=new URL(location.href);u2.searchParams.set('f','2');dp.href=u2.toString();}
document.querySelectorAll('[data-reveal]').forEach(function(b){b.addEventListener('click',function(){var t=document.getElementById(b.dataset.reveal);if(t){t.hidden=false;b.hidden=true}})});
})();'''

def build(slug, sessions_dir, pool, password, prepared_for, date, out=None, title='Claude Code coding sessions', family='Claude Code', source_note="Realset production LLM gateway (Claude Code sessions), captured under the gateway terms of use"):
    # default: private-pages/<slug>.html (served only through /api/s signed links); bundle next to it
    out = pathlib.Path(out) if out else ROOT/'private-pages'/slug
    out.mkdir(parents=True, exist_ok=True)
    tmp = out/'_r'; render_sessions.main(sessions_dir, str(tmp))
    sess_html = (tmp/'sessions.html').read_text(); st = json.load(open(tmp/'stats.json'))
    bundle = out/'sessions.jsonl'
    with open(bundle,'w') as w:
        for f in sorted(pathlib.Path(sessions_dir).glob('*.jsonl')): w.write(open(f).read().rstrip('\n')+'\n')
    bsha = hashlib.sha256(bundle.read_bytes()).hexdigest(); bsize = bundle.stat().st_size
    for f in tmp.iterdir(): f.unlink()
    tmp.rmdir()
    # metadata pack: everything on the page as machine-readable files
    import zipfile, datetime as _dt
    meta = {"dataset": title, "prepared_for": prepared_for, "date": date, "source": source_note, "sessions": st["sessions"], "tool_calls_total": st["tool_calls_total"],
            "bundle": {"file": "sessions.jsonl", "bytes": bsize, "sha256": bsha}, "schema": {"type": "user|assistant", "timestamp": "ISO-8601 or null", "message.role": "user|assistant", "message.model": "model id on assistant turns",
            "message.content[]": "text | thinking | tool_use{id,name,input} | tool_result{tool_use_id,content,is_error}", "message.usage": "input_tokens, output_tokens on assistant turns"},
            "terms": "Internal evaluation only. No training, no redistribution, no re-identification. Commercial license under MSA.", "contact": "hello@realset.ai", "generated_at": _dt.datetime.utcnow().isoformat() + "Z"}
    (out/'metadata.json').write_text(json.dumps(meta, ensure_ascii=False, indent=1))
    readme = f"# Realset sample pack — {title}\n\nPrepared for {prepared_for}, {date}.\n\nFiles: sessions.jsonl (one JSON object per turn), metadata.json (data card, per-session stats, schema, SHA-256), README.md.\n\nLoad:\n\n    import json\n    turns = [json.loads(l) for l in open('sessions.jsonl')]\n\nTerms: {meta['terms']} Contact: {meta['contact']}\n"
    (out/'README.md').write_text(readme)
    with zipfile.ZipFile(out/'pack.zip', 'w', zipfile.ZIP_DEFLATED) as z:
        z.write(bundle, 'sessions.jsonl'); z.write(out/'metadata.json', 'metadata.json'); z.write(out/'README.md', 'README.md')
    psize = (out/'pack.zip').stat().st_size
    pw_hash = hashlib.sha256(password.encode()).hexdigest()
    n = st['n']; tools = st['tool_calls_total']
    pool_rows = [(k, html.escape(str(v))) for k, v in pool.items()]
    tool_rows = "".join(f"<tr><td>{html.escape(k)}</td><td>{v}</td></tr>" for k, v in list(tools.items())[:12])
    css_hash = hashlib.sha1((ROOT/'public'/'assets/site.css').read_bytes()).hexdigest()[:8]
    href = "#"  # replaced client-side with the current signed URL + &f=1 (bundle is served by /api/s)
    page = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>Realset — {html.escape(title)} sample pack</title><meta name="robots" content="noindex,nofollow,noarchive"><link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/site.css?v={css_hash}"><link rel="stylesheet" href="/assets/private.css?v={css_hash}"></head><body>
<header class="nav solid"><div class="wrap"><nav class="links" aria-label="Primary"><a href="/body/">Body</a><a href="/field/">Field</a><a href="/judge/">Judge</a><a href="/samples/">Samples</a></nav><a class="logo" href="/" aria-label="Realset home">realset<span>.</span></a><div class="navr"><span class="signin">Confidential sample</span></div></div></header>
<section class="phero" id="gate" data-h="{pw_hash}" data-k="{slug}"{' hidden' if not password else ''}><div class="wrap"><span class="k">Prepared for {html.escape(prepared_for)} · {html.escape(date)}</span><h1>Coding sessions sample pack</h1><p>This page is private. Enter the access code you received to view the samples.</p>
<form id="gf" class="gatef"><input name="pw" type="password" placeholder="Access code" autocomplete="off" required><button class="btn" type="submit">Open →</button></form><p id="ge" class="mut" hidden style="color:var(--bad)">That code did not match.</p></div></section>
<div id="content"{' hidden' if password else ''}>
<section class="phero"><div class="wrap"><span class="k">Prepared for {html.escape(prepared_for)} · {html.escape(date)} · Confidential</span><h1>{html.escape(title)}</h1><p>De-identified agent trajectories captured at Realset's own LLM gateway. {n} complete sessions readable below, and the same {n} as a JSONL download. Bucket credentials for the embodied sample packs are sent separately.</p><div class="cta"><a class="btn" href="#sessions">Read the sessions →</a><a class="btn sec" href="#download">Download JSONL</a></div></div></section>
{section("Data card", "What this dataset is, in the fields a buyer needs before asking anything.", spec([
 ("Source",source_note),
 ("Unit","session (one complete multi-turn agent run); also priced per turn on request"),
 ("Content","user ↔ assistant turns with tool_use / tool_result blocks (and reasoning summaries where the model emitted them), model id, token usage, timestamps"),
 ("Field readability","tool_use inputs and tool_result outputs: full · thinking blocks: present where the model emitted them · signatures: stripped"),
 ("Distribution","software engineering: bug fixes, feature work, refactors, infrastructure and deployment tasks; model versions listed per session below"),
 ("Supply","in stock, continuous; custom slices by language / task type / model version / date range"),
 ("De-identification","emails, secrets, IPs, home paths, usernames, git org/repo names replaced (rule table below); SHA-256 per file"),
 ("Use of this sample","internal evaluation only; no training, no redistribution; commercial license under MSA"),
]))}
{section("Capture pipeline", "Where these sessions come from and what happens before a buyer sees them.", steps([
 ("Capture","Sessions are recorded at Realset's own LLM gateway as the agent runs: every user turn, assistant turn, tool call and tool result, with model id and token usage."),
 ("Select","Runs are filtered to complete software-engineering sessions with real tool use (read, edit, run, test), not chat."),
 ("De-identify","Emails, secrets, IPs, home paths, usernames and git org/repo names are replaced with consistent placeholders; harness envelope fields are dropped. Rules are listed below."),
 ("Verify","Each session gets a SHA-256; the bundle gets one too. Slices by language, task type, model version and date range are produced on request."),
]) + f'<h3 style="margin-top:var(--sp-md)">Tool calls in the {n} sample sessions</h3><div class="spec"><table>{tool_rows}</table></div>')}
<section class="section" id="sessions"><div class="wrap"><div class="section-head"><h2>Sessions</h2><p>Every turn as it was produced. Tool calls and results are collapsed; click to expand. Text is shown verbatim after de-identification.</p></div>{sess_html}</div></section>
<section class="section" id="download"><div class="wrap"><div class="section-head"><h2>Download &amp; schema</h2><p>One JSONL file, one JSON object per turn, in Messages-API block structure.</p></div>
<div class="cta" style="justify-content:flex-start"><button class="btn" type="button" data-reveal="dl">I agree to the sample terms · show download</button></div>
<div id="dl" hidden style="margin-top:var(--sp-sm)"><p class="mut" style="font-size:14px">Internal evaluation only. No training, no redistribution, no attempt to re-identify. Commercial terms under a master services agreement.</p><p><a class="btn sec" id="dl-link" href="{href}">sessions.jsonl · {bsize//1024} KB · {n} sessions</a> <a class="btn sec" id="dl-pack" href="{href}">pack.zip · {psize//1024} KB · JSONL + metadata.json + README</a></p><p class="mono mut" style="font-size:13px">sha256 {bsha}</p></div>
{spec([("type","&quot;user&quot; | &quot;assistant&quot;"),("timestamp","ISO-8601"),("message.role","&quot;user&quot; | &quot;assistant&quot;"),("message.model","model id on assistant turns"),("message.content[]","blocks: text · thinking · tool_use{{id,name,input}} · tool_result{{tool_use_id,content,is_error}}"),("message.usage","input_tokens, output_tokens, cache_* on assistant turns"),("toolUseResult","structured result the harness attached to a tool_result turn, when present")])}
<pre class="code">import json
turns = [json.loads(l) for l in open("sessions.jsonl")]
tool_calls = [b for t in turns if t["type"] == "assistant"
              for b in t["message"]["content"] if b["type"] == "tool_use"]
print(len(turns), "turns,", len(tool_calls), "tool calls")</pre></div></section>
</div>
<footer><div class="wrap"><div class="fbottom"><div>© 2026 realset.ai · VOC AI INC, San Jose, CA. Confidential sample prepared for {html.escape(prepared_for)}. <a href="/terms/">Terms</a> · <a href="/privacy/">Privacy</a></div><div class="fmark">realset<span>.</span></div></div></div></footer>
<script>{GATE_JS}</script></body></html>'''
    (out.parent/f'{slug}.html').write_text(page) if out.parent.name=='private-pages' else (out/'index.html').write_text(page)  # bundle stays at private-pages/<slug>/sessions.jsonl
    print(f"wrote page for {slug} ({len(page)//1024} KB), bundle {out/'sessions.jsonl'} {bsize//1024} KB sha256 {bsha[:16]}…")

if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--slug', required=True); ap.add_argument('--sessions', required=True); ap.add_argument('--pool'); ap.add_argument('--password', default='')
    ap.add_argument('--for', dest='prepared_for', default='Meta'); ap.add_argument('--date', default='September 17, 2026'); ap.add_argument('--out'); ap.add_argument('--title', default='Claude Code coding sessions'); ap.add_argument('--family', default='Claude Code'); ap.add_argument('--source', default="Realset production LLM gateway (Claude Code sessions), captured under the gateway terms of use")
    a = ap.parse_args(); build(a.slug, a.sessions, json.load(open(a.pool)) if a.pool else {}, a.password, a.prepared_for, a.date, a.out, a.title, a.family, a.source)
