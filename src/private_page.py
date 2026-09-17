"""Private sample page generator (no session data lives in the repo; pass dirs at run time).
Usage (from site/):
  python3 -m src.private_page --slug meta-coding-sessions-7k2q --sessions <dir_with_jsonl> --pool pool.json --password <pw> [--out <dir>]
Default --out is s/<slug>/ inside the site (deployed). Use --out elsewhere for previews."""
import argparse, hashlib, json, pathlib, sys, html
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src')); sys.path.insert(0, str(ROOT/'tools'))
import render_sessions
from pages import section, spec, cards

GATE_JS = r'''
(function(){var g=document.getElementById('gate'),c=document.getElementById('content'),f=document.getElementById('gf'),e=document.getElementById('ge');
async function sha(s){const b=await crypto.subtle.digest('SHA-256',new TextEncoder().encode(s));return [...new Uint8Array(b)].map(x=>x.toString(16).padStart(2,'0')).join('')}
async function unlock(pw){if(await sha(pw)===g.dataset.h){c.hidden=false;g.hidden=true;try{sessionStorage.setItem('rs_'+g.dataset.k,'1')}catch(_){}}else{e.hidden=false}}
try{if(sessionStorage.getItem('rs_'+g.dataset.k)==='1'){c.hidden=false;g.hidden=true}}catch(_){}
f.addEventListener('submit',function(ev){ev.preventDefault();unlock(f.pw.value.trim())});
document.querySelectorAll('[data-reveal]').forEach(function(b){b.addEventListener('click',function(){var t=document.getElementById(b.dataset.reveal);if(t){t.hidden=false;b.hidden=true}})});
})();'''

def build(slug, sessions_dir, pool, password, prepared_for, date, out=None):
    out = pathlib.Path(out) if out else ROOT/'s'/slug
    out.mkdir(parents=True, exist_ok=True)
    tmp = out/'_r'; render_sessions.main(sessions_dir, str(tmp))
    sess_html = (tmp/'sessions.html').read_text(); st = json.load(open(tmp/'stats.json'))
    bundle = out/'sessions.jsonl'
    with open(bundle,'w') as w:
        for f in sorted(pathlib.Path(sessions_dir).glob('*.jsonl')): w.write(open(f).read().rstrip('\n')+'\n')
    bsha = hashlib.sha256(bundle.read_bytes()).hexdigest(); bsize = bundle.stat().st_size
    for f in tmp.iterdir(): f.unlink()
    tmp.rmdir()
    pw_hash = hashlib.sha256(password.encode()).hexdigest()
    n = st['n']; tools = st['tool_calls_total']
    pool_rows = [(k, html.escape(str(v))) for k, v in pool.items()]
    tool_rows = "".join(f"<tr><td>{html.escape(k)}</td><td>{v}</td></tr>" for k, v in list(tools.items())[:12])
    css_hash = hashlib.sha1((ROOT/'assets/site.css').read_bytes()).hexdigest()[:8]
    href = f"/s/{slug}/sessions.jsonl" if out == ROOT/'s'/slug else "sessions.jsonl"
    page = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>Realset — Coding sessions sample pack</title><meta name="robots" content="noindex,nofollow,noarchive"><link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/site.css?v={css_hash}"><link rel="stylesheet" href="/assets/private.css?v={css_hash}"></head><body>
<header class="nav solid"><div class="wrap"><nav class="links" aria-label="Primary"><a href="/body/">Body</a><a href="/field/">Field</a><a href="/judge/">Judge</a><a href="/samples/">Samples</a></nav><a class="logo" href="/" aria-label="Realset home">realset<span>.</span></a><div class="navr"><span class="signin">Confidential sample</span></div></div></header>
<section class="phero" id="gate" data-h="{pw_hash}" data-k="{slug}"><div class="wrap"><span class="k">Prepared for {html.escape(prepared_for)} · {html.escape(date)}</span><h1>Coding sessions sample pack</h1><p>This page is private. Enter the access code you received to view the samples.</p>
<form id="gf" class="gatef"><input name="pw" type="password" placeholder="Access code" autocomplete="off" required><button class="btn" type="submit">Open →</button></form><p id="ge" class="mut" hidden style="color:var(--bad)">That code did not match.</p></div></section>
<div id="content" hidden>
<section class="phero"><div class="wrap"><span class="k">Prepared for {html.escape(prepared_for)} · {html.escape(date)} · Confidential</span><h1>Claude Code coding sessions</h1><p>De-identified agent trajectories from Realset's production LLM gateway. {n} sessions readable below, the same {n} as a JSONL download, and statistics for the full pool they were drawn from.</p><div class="cta"><a class="btn" href="#sessions">Read the sessions →</a><a class="btn sec" href="#download">Download JSONL</a></div></div></section>
{section("Data card", "What this dataset is, in the fields a buyer needs before asking anything.", spec([
 ("Source","Realset production LLM gateway (Claude Code sessions), captured under the gateway terms of use"),
 ("Unit","session (one complete multi-turn agent run); also priced per turn on request"),
 ("Content","user ↔ assistant turns with tool_use / tool_result blocks, model id, token usage, timestamps"),
 ("Field readability","tool_use inputs and tool_result outputs: full · thinking blocks: present where the model emitted them · signatures: stripped"),
 ("Distribution","see pool statistics below; task mix is software engineering (bug fix, feature work, refactor, ops)"),
 ("Supply","in stock, continuous; custom slices by language / task type / model version / date range"),
 ("De-identification","emails, secrets, IPs, home paths, usernames, git org/repo names replaced (rule table below); SHA-256 per file"),
 ("Use of this sample","internal evaluation only; no training, no redistribution; commercial license under MSA"),
]))}
{section("Pool statistics", "Computed over the full pool the samples were drawn from, not over the samples.", spec(pool_rows) + f'<h3 style="margin-top:var(--sp-md)">Tool calls in the {n} sample sessions</h3><div class="spec"><table>{tool_rows}</table></div>')}
<section class="section" id="sessions"><div class="wrap"><div class="section-head"><h2>Sessions</h2><p>Every turn as it was produced. Tool calls and results are collapsed; click to expand. Text is shown verbatim after de-identification.</p></div>{sess_html}</div></section>
<section class="section" id="download"><div class="wrap"><div class="section-head"><h2>Download &amp; schema</h2><p>One JSONL file, one JSON object per turn, in Messages-API block structure.</p></div>
<div class="cta" style="justify-content:flex-start"><button class="btn" type="button" data-reveal="dl">I agree to the sample terms · show download</button></div>
<div id="dl" hidden style="margin-top:var(--sp-sm)"><p class="mut" style="font-size:14px">Internal evaluation only. No training, no redistribution, no attempt to re-identify. Commercial terms under a master services agreement.</p><p><a class="btn sec" href="{href}" download>sessions.jsonl · {bsize//1024} KB · {n} sessions</a></p><p class="mono mut" style="font-size:13px">sha256 {bsha}</p></div>
{spec([("type","&quot;user&quot; | &quot;assistant&quot;"),("timestamp","ISO-8601"),("message.role","&quot;user&quot; | &quot;assistant&quot;"),("message.model","model id on assistant turns"),("message.content[]","blocks: text · thinking · tool_use{{id,name,input}} · tool_result{{tool_use_id,content,is_error}}"),("message.usage","input_tokens, output_tokens, cache_* on assistant turns"),("toolUseResult","structured result the harness attached to a tool_result turn, when present")])}
<pre class="code">import json
turns = [json.loads(l) for l in open("sessions.jsonl")]
tool_calls = [b for t in turns if t["type"] == "assistant"
              for b in t["message"]["content"] if b["type"] == "tool_use"]
print(len(turns), "turns,", len(tool_calls), "tool calls")</pre></div></section>
{section("De-identification rules", "Applied before the data left our storage. Mappings are consistent within a session.", spec([("Email addresses","&lt;EMAIL&gt;"),("API keys, tokens, JWTs, password= values","&lt;SECRET&gt;"),("IPv4 addresses","&lt;IP&gt;"),("Home directories (/Users/x, /home/x)","/workspace/user_N"),("Git org / repo in URLs","org_N / repo_N"),("Harness envelope (uuid, cwd, branch, request ids)","dropped"),("Integrity","SHA-256 per file and for the bundle")]))}
{section("About Realset", "Real-world data lab. Legal entity VOC AI INC, San Jose, California.", cards([("Company","VOC AI INC · San Jose","160 E Tasman Dr, Suite 215, San Jose, CA 95134. Security program audited to SOC 2 Type II and ISO 27001, continuously monitored through Vanta."),("What we produce","Body · Field · Judge","Embodied demonstrations, RL environments from real workflows, and expert evaluation. Eight embodied sample packs are open at realset.ai/samples."),("This dataset","Own gateway, own pipeline","Sessions come from infrastructure we operate, so slices, volumes and refresh cadence are under our control, not a broker's.")]) + '<div class="trust" style="margin-top:var(--sp-sm)"><span class="tlabel">Trusted &amp; verified by</span><a class="badge" href="https://www.cert-assure.com/serchresult.php?type=Management+System+Certification&amp;certificate=USA-SOC2-220513" target="_blank" rel="noopener noreferrer nofollow">SOC 2 Type II</a><a class="badge" href="https://www.cert-assure.com/serchresult.php?type=Management+System+Certification&amp;certificate=USA-I-270513" target="_blank" rel="noopener noreferrer nofollow">ISO 27001</a><span class="badge">GDPR compliant</span><a class="badge" href="https://www.vanta.com/integrations?built-by=Partner" target="_blank" rel="noopener noreferrer nofollow">Vanta monitored</a><span class="badge">US-hosted delivery</span></div>')}
{section("Next step", "Tell us the slice you want: volume, languages, task types, model versions, date range. We reply with a scoped batch, a price per session, and delivery terms.", '<div class="cta" style="justify-content:flex-start"><a class="btn" href="mailto:hello@realset.ai?subject=Coding%20sessions%20%E2%80%94%20scoped%20batch">Email Hunter Guo, Chairman →</a><a class="btn sec" href="/samples/">See other sample packs</a></div>')}
</div>
<footer><div class="wrap"><div class="fbottom"><div>© 2026 realset.ai · VOC AI INC, San Jose, CA. Confidential sample prepared for {html.escape(prepared_for)}. <a href="/terms/">Terms</a> · <a href="/privacy/">Privacy</a></div><div class="fmark">realset<span>.</span></div></div></div></footer>
<script>{GATE_JS}</script></body></html>'''
    (out/'index.html').write_text(page)
    print(f"wrote {out/'index.html'} ({len(page)//1024} KB), bundle {bsize//1024} KB sha256 {bsha[:16]}…")

if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--slug', required=True); ap.add_argument('--sessions', required=True); ap.add_argument('--pool', required=True); ap.add_argument('--password', required=True)
    ap.add_argument('--for', dest='prepared_for', default='Meta'); ap.add_argument('--date', default='September 17, 2026'); ap.add_argument('--out')
    a = ap.parse_args(); build(a.slug, a.sessions, json.load(open(a.pool)), a.password, a.prepared_for, a.date, a.out)
