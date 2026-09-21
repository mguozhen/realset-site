#!/usr/bin/env python3
"""Convert gateway captures of the Anthropic Messages API into Realset turn JSONL, grouped by conversation.
Usage: python3 tools/capture_convert.py <raw_dir> <out_dir> [N=10] [prefix=session]
Handles two record shapes:
  A) {request:{messages,system,tools,...}, response:{stream_events|raw|final_text}, model|upstream_model, session_id?, created_at}
  B) {request:{encoding,value}, response:{raw:{data,encoding}, stream_events:[{event,data}], final_text}, identity, route, ...}
     where value/data are encoded (json | base64 | gzip | zlib | zstd, possibly chained like "gzip+base64").
Conversation key = session_id if present else md5 of the first user message. Keeps the fullest capture per conversation,
expands history + response via deidentify.expand (which reconstructs SSE streams and strips signatures), scrubs, ranks by tool_use."""
import json, glob, os, sys, hashlib, collections, importlib.util, base64, gzip, zlib
HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("deid", os.path.join(HERE, "deidentify.py")); deid = importlib.util.module_from_spec(spec); spec.loader.exec_module(deid)

def decode(encoding, value):
    e = (encoding or "").lower(); v = value
    if isinstance(v, (dict, list)): return v
    if not isinstance(v, str): return None
    try:
        if "base64" in e or "b64" in e: v = base64.b64decode(v)
        if "gzip" in e: v = gzip.decompress(v)
        if "zlib" in e or "deflate" in e: v = zlib.decompress(v)
        if "zstd" in e:
            import zstandard; v = zstandard.ZstdDecompressor().stream_reader(v).read()
        if isinstance(v, bytes): v = v.decode("utf8", "ignore")
        return json.loads(v)
    except Exception:
        try: return json.loads(v) if isinstance(v, str) else None
        except Exception: return None

def normalize(o):
    """Return a shape-A record or None."""
    if not isinstance(o, dict) or "request" not in o: return None
    r = o.get("request"); resp = o.get("response") or {}
    if isinstance(r, dict) and "value" in r and "encoding" in r:  # shape B
        r = decode(r.get("encoding"), r.get("value"))
        if isinstance(resp, dict):
            raw = resp.get("raw")
            if isinstance(raw, dict) and "data" in raw: raw = decode(raw.get("encoding"), raw.get("data"))
            resp = {"raw": raw, "stream_events": resp.get("stream_events"), "final_text": resp.get("final_text")}
    if isinstance(r, dict) and isinstance(r.get("raw"), dict) and "value" in r["raw"] and "encoding" in r["raw"]:  # shape C: request.raw = {encoding, value}
        r = decode(r["raw"].get("encoding"), r["raw"].get("value"))
        if isinstance(resp, dict) and isinstance(resp.get("raw"), dict) and "data" in resp["raw"]:
            raw = decode(resp["raw"].get("encoding"), resp["raw"].get("data")); resp = {"raw": raw if isinstance(raw, dict) else None, "stream_events": resp.get("stream_events"), "final_text": resp.get("final_text")}
    if isinstance(r, dict) and isinstance(r.get("raw"), (dict, str)) and "messages" not in r: r = decode("json", r["raw"]) if isinstance(r["raw"], str) else r["raw"]
    if not isinstance(r, dict) or not isinstance(r.get("messages"), list): return None
    rt = o.get("route") if isinstance(o.get("route"), dict) else {}
    model = o.get("upstream_model") or o.get("model") or rt.get("upstream_model") or r.get("model") or rt.get("model")
    return {"request": {"messages": r["messages"], "system": r.get("system"), "tools": r.get("tools")}, "response": resp, "model": model, "session_id": o.get("session_id"), "created_at": o.get("created_at")}

def text_first_user(msgs):
    for m in msgs:
        if isinstance(m, dict) and m.get("role") == "user":
            c = m.get("content")
            if isinstance(c, str): return c
            if isinstance(c, list): return " ".join(b.get("text", "") for b in c if isinstance(b, dict) and b.get("type") == "text")
    return ""

def main(src, dst, N=10, prefix="session"):
    os.makedirs(dst, exist_ok=True); files = [f for f in glob.glob(os.path.join(src, "**", "*"), recursive=True) if os.path.isfile(f)]
    best = {}; bad = 0; siblings = collections.defaultdict(list)  # key -> [(n_messages, created_at, usage, model)]
    for f in files:
        try: o = json.load(open(f))
        except Exception: bad += 1; continue
        n = normalize(o)
        if not n: bad += 1; continue
        msgs = n["request"]["messages"]; key = n.get("session_id") or hashlib.md5(text_first_user(msgs)[:4000].encode()).hexdigest()
        resp = n.get("response") or {}; usage = None
        for cand in (resp, resp.get("raw") if isinstance(resp, dict) else None, o.get("usage")):
            if isinstance(cand, dict) and (cand.get("usage") or cand.get("input_tokens") or cand.get("prompt_tokens")): usage = cand.get("usage") or cand; break
        siblings[key].append((len(msgs), n.get("created_at"), usage, n.get("model")))
        if key not in best or len(msgs) > len(best[key][0]["request"]["messages"]): best[key] = (n, f)
    print(f"files: {len(files)} unusable: {bad} conversations: {len(best)}", file=sys.stderr)
    rows = []
    for key, (n, f) in best.items():
        sc = deid.Scrubber(); recs = []
        src_label = os.environ.get("SOURCE_LABEL", "gateway-anthropic-messages"); lic = os.environ.get("LICENSE_STATUS", "pending review")
        recs.append({"type": "meta", "session": {"source": src_label, "api": "anthropic.messages", "harness": os.environ.get("HARNESS", "unknown"), "model": n.get("model"),
            "conversation_key": str(key)[:12], "captures_in_conversation": len(siblings[key]), "license_status": lic, "environment_snapshot": "not captured", "verification": "not captured",
            "tool_naming": "original tool names retained; name_normalized added on every tool_use", "usage_timestamps": "per assistant turn where a capture of that turn exists"}})
        for t in deid.expand(n):
            if t.get("type") not in ("user", "assistant", "system"): continue
            m = t.get("message")
            if not isinstance(m, dict) or not m.get("content"): continue
            rec = {"type": t["type"], "timestamp": t.get("timestamp"), "message": sc.walk(m)}
            if t.get("type") == "system": rec["tools"] = sc.walk(t.get("tools") or [])
            recs.append(rec)
        # per-turn usage/timestamp: a capture with k history messages produced the assistant turn at history index k
        off = 1 + (1 if any(r["type"] == "system" for r in recs) else 0)  # meta (+ system) records precede history
        by_len = {k_: (ts, us, mdl) for k_, ts, us, mdl in sorted(siblings[key], key=lambda x: (x[0], x[1] or ""))}
        for k_, (ts, us, mdl) in by_len.items():
            i = off + k_
            if i < len(recs) and recs[i]["type"] == "assistant":
                if ts and not recs[i].get("timestamp"): recs[i]["timestamp"] = ts
                if us and not recs[i]["message"].get("usage"): recs[i]["message"]["usage"] = us
        recs[0]["session"]["assistant_turns_with_usage"] = sum(1 for r in recs if r["type"] == "assistant" and r["message"].get("usage"))
        def blocks(r): c = r.get("message", {}).get("content"); return [b for b in c if isinstance(b, dict)] if isinstance(c, list) else []
        tu = sum(1 for r in recs for b in blocks(r) if b.get("type") == "tool_use"); tr = sum(1 for r in recs for b in blocks(r) if b.get("type") == "tool_result")
        asst = sum(1 for r in recs if r["type"] == "assistant"); names = collections.Counter(b.get("name") for r in recs for b in blocks(r) if b.get("type") == "tool_use")
        uniq = len({json.dumps(r.get("message", r), ensure_ascii=False)[:300] for r in recs})
        rows.append((tu, tr, asst, len(recs), uniq, dict(sc.stats), str(key)[:10], n.get("model"), recs, dict(names.most_common(4))))
    rows.sort(key=lambda r: (-r[0], -r[3]))
    print("tool_use tool_result asst turns uniq scrubs key model top_tools", file=sys.stderr)
    for r in rows[:25]: print(r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7], r[9], file=sys.stderr)
    kept = [r for r in rows if r[0] >= 3 and r[3] >= 8 and r[4] >= 8][:N]
    for i, r in enumerate(kept, 1):
        with open(os.path.join(dst, f"{prefix}_{i:02d}.jsonl"), "w") as w:
            for rec in r[8]: w.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print("written", len(kept), "->", dst, file=sys.stderr)

if __name__ == "__main__": main(sys.argv[1], sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 10, sys.argv[4] if len(sys.argv) > 4 else "session")
