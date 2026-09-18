#!/usr/bin/env python3
"""De-identify Claude Code / Messages-API style JSONL transcripts before they leave the company.
Usage: python3 tools/deidentify.py in.jsonl out.jsonl [--report]
Rules (documented on the sample page): emails -> <EMAIL>, secrets/tokens -> <SECRET>, IPv4 -> <IP>,
absolute home paths -> /workspace/<...>, usernames -> user_N, repo/org names in git URLs -> org_N/repo_N,
drops Claude-Code-internal envelope fields (uuid/parentUuid/requestId/cwd/gitBranch/atis/...) and keeps
only message-bearing lines (type user|assistant) so the output is a clean turn list."""
import json, re, sys, hashlib, collections
SECRET = re.compile(r'\b(sk-[A-Za-z0-9_\-]{8,}|ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|xox[abp]-[A-Za-z0-9\-]{10,}|AKIA[0-9A-Z]{16}|cfut_[A-Za-z0-9_\-]{30,}|eyJ[A-Za-z0-9_\-]{20,}\.[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}|(?:api[_-]?key|token|secret|password|passwd)\s*[=:]\s*["\']?[^\s"\']{6,})', re.I)
EMAIL = re.compile(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}')
IPV4 = re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b')
HOME = re.compile(r'/(?:Users|home)/([A-Za-z0-9._-]+)')
GITURL = re.compile(r'(github\.com[:/])([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+)')
KEEP_TYPES = {"user", "assistant"}
# Company / product / person names that must never leave the company (case-insensitive). Longer first.
BRANDS = [("hunter guo","<PERSON>"),("zhen guo","<PERSON>"),("guo zhen","<PERSON>"),("郭振","<PERSON>"),("mguozhen","<PERSON>"),("hunter","<PERSON>"),("guozhen","<PERSON>"),("flatkey","<ORG_A>"),("vocai","<ORG_B>"),("voc ai","<ORG_B>"),("voc-ai","<ORG_B>"),("www.voc.ai","<ORG_B>.example"),("voc.ai","<ORG_B>.example"),("voc-tools-hub","<ORG_B>-tools-hub"),("voc-integration","<ORG_B>-integration"),("voc_","<ORG_B>_"),("solvea","<ORG_C>"),("shulex","<ORG_D>"),("11agents","<ORG_F>"),("nuvelle","<ORG_G>"),("btcmind","<ORG_H>"),("realset","<ORG_I>"),("unifyai","<ORG_J>"),("daboss","<ORG_K>"),("natura","<ORG_L>")]
BRAND_RE = re.compile("|".join(re.escape(b) for b,_ in BRANDS), re.I)
BRAND_MAP = {b:r for b,r in BRANDS}
DROP_KEYS = {"uuid","parentUuid","requestId","cwd","gitBranch","atis","leafUuid","promptId","promptSource","permissionMode","userType","entrypoint","sourceToolAssistantUUID","isSidechain","apiBlockIndex","rendered","attachment","lastPrompt","operation"}

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
        if isinstance(o,dict): return {k:self.walk(v) for k,v in o.items() if k not in DROP_KEYS}
        return o

def main(src, dst, report=False):
    sc=Scrubber(); out=[]; kept=0; total=0
    for line in open(src, encoding='utf8', errors='ignore'):
        line=line.strip()
        if not line: continue
        total+=1
        try: o=json.loads(line)
        except json.JSONDecodeError: continue
        # Accept both Claude Code envelope lines ({type, message:{role,content}}) and bare Messages lines ({role, content})
        if 'message' not in o and o.get('role') in ('user','assistant') and o.get('content'):
            o={"type":o['role'],"timestamp":o.get('timestamp'),"message":{k:v for k,v in o.items() if k!='timestamp'}}
        if o.get('type') not in KEEP_TYPES: continue
        m=o.get('message')
        if not isinstance(m,dict) or not m.get('content'): continue
        rec={"type":o["type"],"timestamp":o.get("timestamp"),"message":sc.walk(m)}
        if "toolUseResult" in o: rec["toolUseResult"]=sc.walk(o["toolUseResult"])
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
