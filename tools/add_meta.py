#!/usr/bin/env python3
"""Prepend a session meta record to turn-JSONL files that lack one. Usage: add_meta.py <file>... --source X --api Y --harness Z --license L"""
import json,sys,argparse
ap=argparse.ArgumentParser(); ap.add_argument('files',nargs='+'); ap.add_argument('--source',required=True); ap.add_argument('--api',default='anthropic.messages'); ap.add_argument('--harness',default='Claude Code'); ap.add_argument('--license',default='pending review'); ap.add_argument('--force',action='store_true')
a=ap.parse_args()
for f in a.files:
    recs=[json.loads(l) for l in open(f) if l.strip()]
    if recs and recs[0].get('type')=='meta':
        if not a.force: continue
        recs=recs[1:]
    model=next((r['message'].get('model') for r in recs if r.get('type')=='assistant' and r.get('message',{}).get('model')),None)
    meta={"type":"meta","session":{"source":a.source,"api":a.api,"harness":a.harness,"model":model,"license_status":a.license,"environment_snapshot":"not captured","verification":"not captured","tool_naming":"original tool names retained; name_normalized added on every tool_use","usage_timestamps":"per assistant turn where available","assistant_turns_with_usage":sum(1 for r in recs if r.get('type')=='assistant' and (r.get('message',{}).get('usage') or {}))}}
    with open(f,'w') as w:
        w.write(json.dumps(meta,ensure_ascii=False)+"\n")
        for r in recs: w.write(json.dumps(r,ensure_ascii=False)+"\n")
    print('meta added:',f)
