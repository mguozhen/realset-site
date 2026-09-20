#!/usr/bin/env python3
"""Convert gateway captures of the OpenAI Responses API (Codex-style agent runs) into Realset turn JSONL.
Usage: python3 tools/gpt_convert.py <raw_dir> <out_dir> [N=10]
- groups captures into conversations (prompt_cache_key, else hash of first user message), keeps the fullest capture per conversation
- maps input items: message(user/assistant) -> text turns; reasoning -> thinking block; function_call / custom_tool_call -> tool_use;
  function_call_output / custom_tool_call_output -> tool_result; developer/system instructions are DROPPED (harness prompts)
- rebuilds the model's final output from response.stream_events (response.output_item.done)
- drops identifiers (request_id, user_id, token_id, channel_id, client_metadata, item ids), runs the Realset scrubber on all text
- ranks conversations by tool calls and writes the top N as session_XX.jsonl + a stats table to stdout"""
import json, glob, os, sys, hashlib, collections, importlib.util, shutil
HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("deid", os.path.join(HERE, "deidentify.py")); deid = importlib.util.module_from_spec(spec); spec.loader.exec_module(deid)

def text_of(content):
    if isinstance(content, str): return content
    if isinstance(content, list):
        return "\n".join(c.get("text", "") for c in content if isinstance(c, dict) and c.get("type") in ("input_text", "output_text", "text"))
    return ""

def item_to_turn(it, model):
    t = it.get("type"); r = it.get("role")
    if t == "message" and r == "user":
        s = text_of(it.get("content"));  return {"type": "user", "message": {"role": "user", "content": [{"type": "text", "text": s}]}} if s.strip() else None
    if t == "message" and r == "assistant":
        s = text_of(it.get("content"));  return {"type": "assistant", "message": {"role": "assistant", "model": model, "content": [{"type": "text", "text": s}]}} if s.strip() else None
    if t == "reasoning":
        s = "\n".join(x.get("text", "") for x in (it.get("summary") or []) if isinstance(x, dict))
        return {"type": "assistant", "message": {"role": "assistant", "model": model, "content": [{"type": "thinking", "thinking": s or "(reasoning summary not included)"}]}}
    if t == "function_call":
        try: args = json.loads(it.get("arguments") or "{}")
        except Exception: args = {"arguments": it.get("arguments")}
        return {"type": "assistant", "message": {"role": "assistant", "model": model, "content": [{"type": "tool_use", "id": it.get("call_id"), "name": it.get("name"), "input": args}]}}
    if t == "custom_tool_call":
        return {"type": "assistant", "message": {"role": "assistant", "model": model, "content": [{"type": "tool_use", "id": it.get("call_id"), "name": it.get("name") or "custom_tool", "input": {"input": it.get("input")}}]}}
    if t in ("function_call_output", "custom_tool_call_output"):
        out = it.get("output"); out = out if isinstance(out, str) else json.dumps(out, ensure_ascii=False)
        return {"type": "user", "message": {"role": "user", "content": [{"type": "tool_result", "tool_use_id": it.get("call_id"), "content": out}]}}
    return None  # developer/system messages, compaction, additional_tools etc. are dropped

def output_items_from_stream(events):
    items = []
    for e in events or []:
        if isinstance(e, dict) and e.get("type") == "response.output_item.done" and isinstance(e.get("item"), dict): items.append(e["item"])
    return items

def convert(path):
    o = json.load(open(path)); raw = o["request"]["raw"]
    if isinstance(raw, str): raw = json.loads(raw)
    model = o.get("upstream_model") or o.get("model") or raw.get("model")
    turns = [t for t in (item_to_turn(it, model) for it in raw.get("input") or [] if isinstance(it, dict)) if t]
    resp = o.get("response") or {}
    out_items = output_items_from_stream(resp.get("stream_events")) if isinstance(resp.get("stream_events"), list) else []
    if not out_items and isinstance(resp.get("raw"), dict): out_items = resp["raw"].get("output") or []
    turns += [t for t in (item_to_turn(it, model) for it in out_items if isinstance(it, dict)) if t]
    if turns and o.get("usage"): turns[-1]["message"]["usage"] = {"input_tokens": o["usage"].get("prompt_tokens"), "output_tokens": o["usage"].get("completion_tokens")}
    key = raw.get("prompt_cache_key")
    if not key:
        first = next((text_of(it.get("content")) for it in raw.get("input") or [] if isinstance(it, dict) and it.get("role") == "user"), "")
        key = hashlib.md5(first[:4000].encode()).hexdigest()
    if os.environ.get("KEEP_SYSTEM") == "1" and (raw.get("instructions") or raw.get("tools")):
        turns.insert(0, {"type": "system", "message": {"role": "system", "content": [{"type": "text", "text": raw.get("instructions") or "(no instructions)"}]}, "tools": raw.get("tools") or []})
    return key, turns, o.get("created_at"), len(raw.get("input") or []), o.get("usage")

def main(src, dst, N=10):
    os.makedirs(dst, exist_ok=True)
    best = {}; siblings = collections.defaultdict(list)
    for f in sorted(glob.glob(os.path.join(src, "**", "*.json"), recursive=True)):
        try: key, turns, ts, n_in, usage = convert(f)
        except Exception as e: print("skip", os.path.basename(f)[:20], str(e)[:60], file=sys.stderr); continue
        siblings[key].append((n_in, ts, usage))
        if key not in best or len(turns) > len(best[key][0]): best[key] = (turns, ts, f)
    print("captures:", len(glob.glob(os.path.join(src, "**", "*.json"), recursive=True)), "conversations:", len(best), file=sys.stderr)
    rows = []
    for key, (turns, ts, f) in best.items():
        sc = deid.Scrubber(); recs = [{"type": "meta", "session": {"source": os.environ.get("SOURCE_LABEL", "gateway-openai-responses"), "api": "openai.responses", "harness": os.environ.get("HARNESS", "codex-style agent"),
            "model": next((t["message"].get("model") for t in turns if t["type"] == "assistant" and t["message"].get("model")), None), "conversation_key": str(key)[:12], "captures_in_conversation": len(siblings[key]),
            "license_status": os.environ.get("LICENSE_STATUS", "pending review"), "environment_snapshot": "not captured", "verification": "not captured",
            "tool_naming": "original tool names retained; name_normalized added on every tool_use", "usage_timestamps": "per response where a capture of that response exists; reasoning is summary-only"}}]
        for t in turns:
            rec = {"type": t["type"], "timestamp": ts if t is turns[-1] else None, "message": sc.walk(t["message"])}
            if t["type"] == "system": rec["tools"] = sc.walk(t.get("tools") or [])
            recs.append(rec)
        # each sibling capture with k input items produced the response items starting at history index k
        off = 1 + (1 if any(r["type"] == "system" for r in recs) else 0)
        for k_, ts_, us_ in sorted(siblings[key], key=lambda x: (x[0], x[1] or "")):
            i = off + k_
            if i < len(recs) and recs[i]["type"] == "assistant":
                if ts_ and not recs[i].get("timestamp"): recs[i]["timestamp"] = ts_
                if us_ and not recs[i]["message"].get("usage"): recs[i]["message"]["usage"] = {"input_tokens": us_.get("prompt_tokens"), "output_tokens": us_.get("completion_tokens")}
        recs[0]["session"]["assistant_turns_with_usage"] = sum(1 for r in recs if r["type"] == "assistant" and r["message"].get("usage"))
        def blocks(r): c = r.get("message", {}).get("content"); return [b for b in c if isinstance(b, dict)] if isinstance(c, list) else []
        tu = sum(1 for r in recs for b in blocks(r) if b.get("type") == "tool_use"); tr = sum(1 for r in recs for b in blocks(r) if b.get("type") == "tool_result")
        asst = sum(1 for r in recs if r["type"] == "assistant"); names = collections.Counter(b.get("name") for r in recs for b in blocks(r) if b.get("type") == "tool_use")
        rows.append((tu, tr, asst, len(recs), dict(sc.stats), key[:10], recs, dict(names.most_common(4))))
    rows.sort(key=lambda r: (-r[0], -r[3]))
    print("tool_use tool_result asst turns scrubs key top_tools", file=sys.stderr)
    for r in rows[:30]: print(r[0], r[1], r[2], r[3], r[4], r[5], r[7], file=sys.stderr)
    kept = [r for r in rows if r[0] >= 3 and r[3] >= 8][:N]
    for i, r in enumerate(kept, 1):
        with open(os.path.join(dst, f"session_{i:02d}.jsonl"), "w") as w:
            for rec in r[6]: w.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print("written", len(kept), "->", dst, file=sys.stderr)

if __name__ == "__main__": main(sys.argv[1], sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 10)
