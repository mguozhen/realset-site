#!/usr/bin/env python3
"""De-identify Claude Code / Messages-API style JSONL transcripts before they leave the company.
Usage: python3 tools/deidentify.py in.jsonl out.jsonl [--report]
Rules (documented on the sample page): emails -> <EMAIL>, secrets/tokens -> <SECRET>, IPv4 -> <IP>,
absolute home paths -> /workspace/<...>, usernames -> user_N, repo/org names in git URLs -> org_N/repo_N,
drops Claude-Code-internal envelope fields (uuid/parentUuid/requestId/cwd/gitBranch/atis/...) and keeps
only message-bearing lines (type user|assistant) so the output is a clean turn list."""
import json, re, sys, hashlib, collections, os
SECRET = re.compile(r'\b(sk-[A-Za-z0-9_\-]{6,}|ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|xox[abp]-[A-Za-z0-9\-]{10,}|AKIA[0-9A-Z]{16}|cfut_[A-Za-z0-9_\-]{30,}|eyJ[A-Za-z0-9_\-]{20,}\.[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}|(?:api[_-]?key|token|secret|password|passwd)\s*[=:]\s*["\']?[^\s"\']{6,})', re.I)
EMAIL = re.compile(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}')
IPV4 = re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}(?:/\d{1,2})?\b|\b(?:192\.168|10\.0|172\.16|100\.6[4-9]|100\.[7-9]\d|100\.1[01]\d|100\.12[0-7])\.\S{0,12}')
HOME = re.compile(r'/(?:Users|home)/([A-Za-z0-9._-]+)')
GITURL = re.compile(r'(github\.com[:/])([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+)')
KEEP_TYPES = {"user", "assistant", "system", "meta"}
TOOL_FAMILY = {  # original tool name (lowercased) -> normalized family; original name is always kept
 "bash":"shell","shell":"shell","shell_command":"shell","exec":"shell","workspace_shell":"shell","terminal":"shell","process":"shell","execute_command":"shell",
 "read":"read_file","read_file":"read_file","workspace_read_file":"read_file","view_image":"read_file","cat":"read_file",
 "edit":"edit_file","apply_patch":"edit_file","workspace_edit_file":"edit_file","str_replace_editor":"edit_file","multiedit":"edit_file",
 "write":"write_file","write_file":"write_file","workspace_write_file":"write_file",
 "grep":"search","glob":"search","search_files":"search","list_files":"search","ls":"search","websearch":"web","web_search":"web","search_web":"web","webfetch":"web","web_fetch":"web",
 "update_plan":"plan","todowrite":"plan","taskcreate":"plan","taskupdate":"plan","tasklist":"plan","taskstop":"plan","followup_task":"plan",
 "spawn_agent":"agent","agent":"agent","wait_agent":"agent","list_agents":"agent","send_message":"agent","wait":"agent",
 "askuserquestion":"ask_user","ask_user":"ask_user","question":"ask_user","use_skill":"skill","skill":"skill","toolsearch":"other","eval_javascript":"code_exec","js":"code_exec"}  # "system" records only exist when KEEP_SYSTEM=1 created them
# Company / product / person names that must never leave the company (case-insensitive). Longer first.
BRANDS = [("hunter guo","<PERSON>"),("zhen guo","<PERSON>"),("guo zhen","<PERSON>"),("郭振","<PERSON>"),("mguozhen","<PERSON>"),("hunter","<PERSON>"),("guozhen","<PERSON>"),("flatkey","<ORG_A>"),("vocai","<ORG_B>"),("voc ai","<ORG_B>"),("voc-ai","<ORG_B>"),("www.voc.ai","<ORG_B>.example"),("voc.ai","<ORG_B>.example"),("voc-tools-hub","<ORG_B>-tools-hub"),("voc-integration","<ORG_B>-integration"),("voc_","<ORG_B>_"),("solvea","<ORG_C>"),("shulex","<ORG_D>"),("11agents","<ORG_F>"),("nuvelle","<ORG_G>"),("btcmind","<ORG_H>"),("unifyai","<ORG_J>"),("daboss","<ORG_K>"),("natura","<ORG_L>")]
BRAND_RE = re.compile("|".join(re.escape(b) for b,_ in BRANDS), re.I)
BRAND_MAP = {b:r for b,r in BRANDS}
DROP_KEYS = {"uuid","request_id","user_id","token_id","channel_id","node_id","node_name","node_ip","identity","training_meta","metadata","parentUuid","requestId","cwd","gitBranch","atis","leafUuid","promptId","promptSource","permissionMode","userType","entrypoint","sourceToolAssistantUUID","isSidechain","apiBlockIndex","rendered","attachment","lastPrompt","operation"}

class Scrubber:
    def __init__(self): self.users={}; self.orgs={}; self.repos={}; self.stats=collections.Counter()
    def _map(self, table, key, prefix):
        if key not in table: table[key]=f"{prefix}_{len(table)+1}"
        return table[key]
    def text(self, s):
        if not isinstance(s,str) or not s: return s
        n0=len(s)
        s,c=SECRET.subn(lambda m: (m.group(0).split('=')[0]+'=<SECRET>') if '=' in m.group(0)[:20] else '<SECRET>', s); self.stats['secret']+=c
        s,c=EMAIL.subn('<EMAIL>', s); self.stats['email']+=c
        s,c=IPV4.subn('<IP>', s); self.stats['ip']+=c
        s,c=GITURL.subn(lambda m: m.group(1)+self._map(self.orgs,m.group(2),'org')+'/'+self._map(self.repos,m.group(3),'repo'), s); self.stats['git_url']+=c
        s,c=HOME.subn(lambda m: '/workspace/'+self._map(self.users,m.group(1),'user'), s); self.stats['home_path']+=c
        s,c=BRAND_RE.subn(lambda m: BRAND_MAP[m.group(0).lower()], s); self.stats['brand']+=c
        return s
    def walk(self, o):
        if isinstance(o,str): return self.text(o)
        if isinstance(o,list): return [self.walk(x) for x in o]
        if isinstance(o,dict):
            if o.get('type')=='tool_use' and isinstance(o.get('name'),str) and 'name_normalized' not in o:
                o=dict(o, name_normalized=TOOL_FAMILY.get(o['name'].lower(), 'other'))
            if 'signature' in o and o.get('type') in ('thinking','redacted_thinking','tool_use','text'): o={k:v for k,v in o.items() if k!='signature'}
            if o.get('type')=='redacted_thinking': o={'type':'thinking','thinking':'(redacted)'}
            return {k:self.walk(v) for k,v in o.items() if k not in DROP_KEYS}
        return o


def anthropic_response(resp, model=None):
    """Normalize a captured Anthropic response into {model, content, usage, stop_reason}. Accepts a full message dict,
    {raw: message}, or {stream_events: [SSE events]} (message_start / content_block_start / content_block_delta / content_block_stop / message_delta)."""
    if not isinstance(resp, dict): return None
    if resp.get('content'): return resp
    raw = resp.get('raw')
    if isinstance(raw, str):
        try: raw = json.loads(raw)
        except Exception: raw = None
    if isinstance(raw, dict) and raw.get('content'): return raw
    ev = resp.get('stream_events')
    if isinstance(ev, list) and ev:
        blocks = {}; out = {'model': model, 'content': [], 'usage': {}, 'stop_reason': None}
        for e in ev:
            if not isinstance(e, dict): continue
            if 'event' in e and isinstance(e.get('data'), (str, dict)):  # {event, data} form
                d = e['data']
                if isinstance(d, str):
                    try: d = json.loads(d)
                    except Exception: continue
                e = dict(d, type=d.get('type') or e.get('event'))
            t = e.get('type')
            if t == 'message_start':
                m = e.get('message') or {}; out['model'] = m.get('model') or model; out['usage'].update(m.get('usage') or {})
            elif t == 'content_block_start':
                b = dict(e.get('content_block') or {}); i = e.get('index'); i = len(blocks) if i is None else i; b.setdefault('_json', ''); blocks[i] = b
            elif t == 'content_block_delta':
                i = e.get('index'); i = (max(blocks) if blocks else 0) if i is None else i; d = e.get('delta') or {}; b = blocks.setdefault(i, {'type': 'text', 'text': '', '_json': ''})
                dt = d.get('type')
                if dt == 'text_delta': b['text'] = b.get('text', '') + (d.get('text') or '')
                elif dt == 'thinking_delta': b['thinking'] = b.get('thinking', '') + (d.get('thinking') or '')
                elif dt == 'input_json_delta': b['_json'] += (d.get('partial_json') or '')
                elif dt == 'signature_delta': b['signature'] = '<stripped>'
            elif t == 'message_delta':
                out['stop_reason'] = (e.get('delta') or {}).get('stop_reason', out['stop_reason']); out['usage'].update(e.get('usage') or {})
        for i in sorted(blocks, key=lambda k: (k is None, k if isinstance(k,int) else 0)):
            b = blocks[i]; j = b.pop('_json', '')
            if b.get('type') == 'tool_use' and j:
                try: b['input'] = json.loads(j)
                except Exception: b['input'] = {'_partial_json': j}
            b.pop('signature', None)
            out['content'].append(b)
        if out['content']: return out
    ft = resp.get('final_text')
    if isinstance(ft, str) and ft.strip(): return {'model': model, 'content': [{'type': 'text', 'text': ft}]}
    return None


def _oa_msg_to_turn(m, model):
    """OpenAI chat-completions message -> Realset turn (assistant text/tool_calls, tool results)."""
    r=m.get('role'); c=m.get('content')
    if r=='assistant':
        blocks=[]
        if isinstance(c,str) and c.strip(): blocks.append({'type':'text','text':c})
        elif isinstance(c,list): blocks+= [{'type':'text','text':b.get('text','')} for b in c if isinstance(b,dict) and b.get('type')=='text' and b.get('text')]
        for tc in m.get('tool_calls') or []:
            fn=(tc.get('function') or {}) if isinstance(tc,dict) else {}
            try: args=json.loads(fn.get('arguments') or '{}')
            except Exception: args={'arguments':fn.get('arguments')}
            blocks.append({'type':'tool_use','id':tc.get('id'),'name':fn.get('name'),'input':args})
        return {'type':'assistant','message':{'role':'assistant','model':model,'content':blocks}} if blocks else None
    if r=='tool':
        out=c if isinstance(c,str) else json.dumps(c,ensure_ascii=False)
        return {'type':'user','message':{'role':'user','content':[{'type':'tool_result','tool_use_id':m.get('tool_call_id'),'content':out}]}}
    if r=='user':
        txt=c if isinstance(c,str) else "\n".join(b.get('text','') for b in (c or []) if isinstance(b,dict) and b.get('type')=='text')
        return {'type':'user','message':{'role':'user','content':[{'type':'text','text':txt}]}} if txt.strip() else None
    return None  # system/developer dropped

def expand(o):
    """Turn one parsed line into a list of turn records.
    Supports: Claude Code envelope {type,message}; bare Messages line {role,content};
    gateway capture {session_id,model,request:{messages,...},response:{content,usage,...}} (one API call with full history)."""
    if isinstance(o,dict) and isinstance(o.get('request'),dict) and isinstance(o['request'].get('messages'),list):
        model=o.get('model') or (o.get('response') or {}).get('model'); out=[]
        msgs=o['request']['messages']; resp=o.get('response') or {}
        if any(isinstance(m,dict) and (m.get('role')=='tool' or m.get('tool_calls')) for m in msgs) or (isinstance(resp,dict) and isinstance(resp.get('choices'),list)):
            # OpenAI chat-completions shape
            out=[t for t in (_oa_msg_to_turn(m,model) for m in msgs if isinstance(m,dict)) if t]
            if os.environ.get('KEEP_SYSTEM')=='1':
                sysm=[m for m in msgs if isinstance(m,dict) and m.get('role') in ('system','developer')]
                stext="\n\n".join((m.get('content') if isinstance(m.get('content'),str) else "\n".join(b.get('text','') for b in (m.get('content') or []) if isinstance(b,dict))) for m in sysm)
                tools=o['request'].get('tools') or []
                rec={"type":"system","message":{"role":"system","content":[{"type":"text","text":stext}]},"tools":tools}
                out.insert(0,rec)
            ch=(resp.get('choices') or [{}])[0] if isinstance(resp,dict) else {}
            fm=(ch or {}).get('message') if isinstance(ch,dict) else None
            if isinstance(fm,dict):
                t=_oa_msg_to_turn(dict(fm,role='assistant'),resp.get('model') or model)
                if t: t['timestamp']=o.get('captured_at'); t['message']['usage']=resp.get('usage'); out.append(t)
            return out
        for m in o['request']['messages']:
            if isinstance(m,dict) and m.get('role') in ('user','assistant') and m.get('content'):
                msg={"role":m['role'],"content":m['content']}
                if m['role']=='assistant' and model: msg['model']=model
                out.append({"type":m['role'],"message":msg})
        if os.environ.get('KEEP_SYSTEM')=='1' and (o['request'].get('system') or o['request'].get('tools')):
            sysv=o['request'].get('system'); stext=sysv if isinstance(sysv,str) else "\n\n".join(b.get('text','') for b in (sysv or []) if isinstance(b,dict))
            out.insert(0,{"type":"system","message":{"role":"system","content":[{"type":"text","text":stext or "(no system prompt)"}]},"tools":o['request'].get('tools') or []})
        r=anthropic_response(o.get('response') or {}, model)
        if isinstance(r,dict) and r.get('content'):
            out.append({"type":"assistant","timestamp":o.get('captured_at') or o.get('created_at'),"message":{"role":"assistant","model":r.get('model') or model,"content":r['content'],"usage":r.get('usage'),"stop_reason":r.get('stop_reason')}})
        return out
    if isinstance(o,dict) and 'message' not in o and o.get('role') in ('user','assistant') and o.get('content'):
        return [{"type":o['role'],"timestamp":o.get('timestamp'),"message":{k:v for k,v in o.items() if k!='timestamp'}}]
    return [o] if isinstance(o,dict) else []

def main(src, dst, report=False):
    sc=Scrubber(); out=[]; kept=0; total=0
    for line in open(src, encoding='utf8', errors='ignore'):
        line=line.strip()
        if not line: continue
        total+=1
        try: o=json.loads(line)
        except json.JSONDecodeError: continue
        for o in expand(o):
            if o.get('type') not in KEEP_TYPES: continue
            if o.get('type')=='meta':
                out.append({"type":"meta","session":sc.walk(o.get("session") or {})}); kept+=1; continue
            m=o.get('message')
            if not isinstance(m,dict) or not m.get('content'): continue
            rec={"type":o["type"],"timestamp":o.get("timestamp"),"message":sc.walk(m)}
            if "toolUseResult" in o: rec["toolUseResult"]=sc.walk(o["toolUseResult"])
            if o.get("type")=="system" and "tools" in o: rec["tools"]=sc.walk(o["tools"])
            out.append(rec); kept+=1
    with open(dst,'w') as f:
        for r in out: f.write(json.dumps(r,ensure_ascii=False)+"\n")
    h=hashlib.sha256(open(dst,'rb').read()).hexdigest()
    rep={"source_lines":total,"kept_turns":kept,"replacements":dict(sc.stats),"users_mapped":len(sc.users),"repos_mapped":len(sc.repos),"sha256":h}
    if report: print(json.dumps(rep,indent=1))
    return rep

if __name__=="__main__":
    a=[x for x in sys.argv[1:] if not x.startswith('--')]
    main(a[0], a[1], report='--report' in sys.argv)
