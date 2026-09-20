#!/usr/bin/env python3
"""Render de-identified JSONL sessions into HTML blocks + a pool-stats JSON for the private sample page.
Usage: python3 tools/render_sessions.py <sessions_dir> <out_dir>   (each *.jsonl in sessions_dir = one session)
Produces out_dir/sessions.html (viewer blocks) and out_dir/stats.json (computed from the given files only;
merge with full-pool numbers from the store separately)."""
import json, sys, os, html, glob, collections, hashlib, datetime
def esc(s): return html.escape(str(s))
def blocks(m):
    c=m.get('content')
    if isinstance(c,str): return [{"type":"text","text":c}]
    return [b for b in c if isinstance(b,dict)] if isinstance(c,list) else []
def render_session(path, idx):
    turns=[json.loads(l) for l in open(path) if l.strip()]
    model=next((t['message'].get('model') for t in turns if t['type']=='assistant' and t['message'].get('model')), '')
    nsys=sum(1 for t in turns if t['type']=='system'); turns_n=len(turns)-nsys
    tools=collections.Counter(); tin=tout=0; first_user=''
    for t in turns:
        m=t['message']
        if t['type']=='assistant':
            u=m.get('usage') or {}; tin+=u.get('input_tokens',0)+u.get('cache_read_input_tokens',0)+u.get('cache_creation_input_tokens',0); tout+=u.get('output_tokens',0)
            for b in blocks(m):
                if b.get('type')=='tool_use': tools[b.get('name','?')]+=1
        elif t['type']=='user' and not first_user:
            for b in blocks(m):
                if b.get('type')=='text' and b.get('text','').strip(): first_user=b['text'].strip(); break
    ts=[t.get('timestamp') for t in turns if t.get('timestamp')]
    dur=''
    try:
        # active time: sum of gaps between consecutive turns, ignoring idle gaps > 30 min
        pts=[datetime.datetime.fromisoformat(x.replace('Z','+00:00')) for x in ts]
        act=sum(min((b-a).total_seconds(),1800) for a,b in zip(pts,pts[1:]) if (b-a).total_seconds()<=1800)
        if act>0: dur=f"{int(act//60)} min active"
    except Exception: pass
    sha=hashlib.sha256(open(path,'rb').read()).hexdigest()
    title=esc(first_user[:110]+('…' if len(first_user)>110 else '')) or f"Session {idx:02d}"
    head=f'''<div class="sess"><div class="sess-h"><span class="k">session {idx:02d}</span><h3>{title}</h3>
<div class="sess-meta"><span>{esc(model)}</span><span>{turns_n} turns</span>{'<span>system prompt + tool schemas included</span>' if nsys else ''}<span>{sum(tools.values())} tool calls</span><span>{(tin+tout)//1000}K tokens</span>{f"<span>{dur}</span>" if dur else ""}<span class="mono">sha256 {sha[:12]}…</span></div></div><div class="turns">'''
    body=[]; MAX=int(os.environ.get("RS_MAX_TURNS","0") or 0); shown=turns[:MAX] if MAX and len(turns)>MAX else turns
    for t in shown:
        m=t['message']; role=t['type']
        if role=='system':
            st=next((b.get('text','') for b in blocks(m) if b.get('type')=='text'),''); tschemas=t.get('tools') or []
            names=", ".join(esc((x.get('function') or x).get('name','?')) for x in tschemas if isinstance(x,dict))
            body.append(f'<details class="turn think"><summary>system prompt · {len(st)} chars</summary><div class="txt">{esc(st)}</div></details>')
            if tschemas: body.append(f'<details class="turn tool"><summary>tool schemas · {len(tschemas)} tools: {names}</summary><pre>{esc(json.dumps(tschemas,ensure_ascii=False,indent=1)[:60000])}</pre></details>')
            continue
        for b in blocks(m):
            ty=b.get('type')
            if ty=='text' and b.get('text','').strip():
                body.append(f'<div class="turn {role}"><div class="role">{role}</div><div class="txt">{esc(b["text"])}</div></div>')
            elif ty=='thinking':
                body.append(f'<details class="turn think"><summary>thinking · {len(b.get("thinking",""))} chars</summary><div class="txt">{esc(b.get("thinking",""))}</div></details>')
            elif ty=='tool_use':
                body.append(f'<details class="turn tool"><summary>tool_use · <b>{esc(b.get("name"))}</b></summary><pre>{esc(json.dumps(b.get("input"),ensure_ascii=False,indent=1)[:4000])}</pre></details>')
            elif ty=='tool_result':
                cc=b.get('content'); s=cc if isinstance(cc,str) else json.dumps(cc,ensure_ascii=False)
                body.append(f'<details class="turn result"><summary>tool_result · {len(s)} chars{" · error" if b.get("is_error") else ""}</summary><pre>{esc(s[:4000])}{"…" if len(s)>4000 else ""}</pre></details>')
    if MAX and len(turns)>MAX: body.append(f'<div class="turn"><div class="txt" style="color:var(--mut)">… {len(turns)-MAX} more turns in this session. The full session is in the JSONL download.</div></div>')
    return head+"".join(body)+'</div></div>', dict(model=model,turns=len(turns),tools=dict(tools),tokens=tin+tout,sha256=sha,file=os.path.basename(path))
def main(src,out):
    os.makedirs(out,exist_ok=True); files=sorted(glob.glob(os.path.join(src,'*.jsonl'))); htmls=[]; metas=[]
    for i,f in enumerate(files,1):
        h,m=render_session(f,i); htmls.append(h); metas.append(m)
    open(os.path.join(out,'sessions.html'),'w').write("\n".join(htmls))
    agg=collections.Counter(); 
    for m in metas: agg.update(m['tools'])
    json.dump({"sessions":metas,"tool_calls_total":dict(agg.most_common()),"n":len(metas)},open(os.path.join(out,'stats.json'),'w'),indent=1)
    print(f"rendered {len(metas)} sessions -> {out}")
if __name__=="__main__": main(sys.argv[1],sys.argv[2])
