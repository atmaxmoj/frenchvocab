#!/usr/bin/env python3
"""校验 6 个 enr_batch + 合入 skeleton / enrich_out / etym_hook_out / formF_out。"""
import json, glob, unicodedata, re, sys

TAG = "b2_w8"

def strip_acc(s):
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")

def norm(s):
    return strip_acc((s or "").lower()).replace("œ","oe").replace("æ","ae")

# load bundles
bundles = []
for fn in sorted(glob.glob("enrich_stage/enr_batch_*.json")):
    bundles += json.load(open(fn, encoding="utf-8"))
print(f"loaded {len(bundles)} bundles from {len(glob.glob('enrich_stage/enr_batch_*.json'))} files")

seed = {w["id"]: w for w in json.load(open("seed_wave.json"))}
assert len(bundles) == len(seed) == 300, f"count mismatch: {len(bundles)} vs {len(seed)}"

errs, warns = [], []
seen_ids = set()
for b in bundles:
    wid = b.get("id")
    fr = seed.get(wid, {}).get("fr", b.get("fr",""))
    if wid not in seed: errs.append(f"{wid}: id not in seed"); continue
    if wid in seen_ids: errs.append(f"{wid}: dup id")
    seen_ids.add(wid)
    for f in ("en","ipa","zh"):
        if not (b.get(f) or "").strip(): errs.append(f"{wid} {fr}: empty {f}")
    et = b.get("etym") or {}
    if not (et.get("from") or "").strip(): errs.append(f"{wid} {fr}: empty etym.from")
    if not (et.get("text") or "").strip(): errs.append(f"{wid} {fr}: empty etym.text")
    hk = et.get("hook") or {}
    roots = (hk.get("roots") or "").strip()
    if len(roots) < 55: warns.append(f"{wid} {fr}: thin hook.roots ({len(roots)}c)")
    if not (hk.get("why") or "").strip(): errs.append(f"{wid} {fr}: empty hook.why")
    exs = b.get("examples") or []
    if len(exs) != 2: errs.append(f"{wid} {fr}: {len(exs)} examples (need 2)")
    ntgt = norm(fr); stem = ntgt[:max(4,len(ntgt)-2)]
    for i,ex in enumerate(exs):
        if not (ex.get("fr") or "").strip(): errs.append(f"{wid} {fr}: ex{i} empty fr")
        if not (ex.get("en") or "").strip(): errs.append(f"{wid} {fr}: ex{i} empty en")
        nfr = norm(ex.get("fr",""))
        if ntgt not in nfr and stem not in nfr:
            warns.append(f"{wid} {fr}: target not in ex{i} fr «{ex.get('fr','')[:60]}»")

print(f"\n=== ERRORS: {len(errs)} ===")
for e in errs[:40]: print("  ✗", e)
print(f"=== WARNINGS: {len(warns)} ===")
for w in warns[:40]: print("  ⚠", w)

if errs:
    print("\n有硬错误，未合入。先修。"); sys.exit(1)

# ---- merge ----
# 1) skeleton append
sk = json.load(open("../vocab_skeleton.json"))
have = set(w["id"] for w in sk)
bybid = {b["id"]: b for b in bundles}
added = 0
for wid, s in seed.items():
    if wid in have: continue
    b = bybid[wid]
    rec = {"id": wid, "rank": s["rank"], "fr": s["fr"], "pos": s["pos"],
           "en": b["en"].strip()}
    if s["pos"] == "noun" and s.get("gender"): rec["gender"] = s["gender"]
    if (b.get("formF") or "").strip(): rec["formF"] = b["formF"].strip()
    sk.append(rec); added += 1
json.dump(sk, open("../vocab_skeleton.json","w"), ensure_ascii=False, indent=1)
print(f"\nskeleton: +{added} (now {len(sk)})")

# 2) enrich_out
enr = [{"id": b["id"], "ipa": b["ipa"].strip(), "zh": b["zh"].strip(),
        "etym": {"from": b["etym"]["from"].strip(), "text": b["etym"]["text"].strip()},
        "examples": b["examples"]} for b in bundles]
json.dump(enr, open(f"../enrich_out/batch_new_{TAG}.json","w"), ensure_ascii=False, indent=1)
print(f"enrich_out/batch_new_{TAG}.json: {len(enr)}")

# 3) etym_hook_out
hooks = [{"id": b["id"], "roots": b["etym"]["hook"]["roots"].strip(),
          "why": b["etym"]["hook"]["why"].strip()} for b in bundles]
json.dump(hooks, open(f"../etym_hook_out/new_{TAG}.json","w"), ensure_ascii=False, indent=1)
print(f"etym_hook_out/new_{TAG}.json: {len(hooks)}")

# 4) formF_out
formf = [{"id": b["id"], "f": b["formF"].strip()} for b in bundles if (b.get("formF") or "").strip()]
json.dump(formf, open(f"../formF_out/new_{TAG}.json","w"), ensure_ascii=False, indent=1)
print(f"formF_out/new_{TAG}.json: {len(formf)}")

# 5) cognate_out —— 只收有拼写相近+义同英语近似词的（没有就不写，属正常）
cog = []
for b in bundles:
    c = (b.get("cog") or "").strip().lower()
    if not c:
        continue
    rec = {"id": b["id"], "cog": c}
    warn = [s.strip() for s in (b.get("cogWarn") or b.get("warn") or []) if isinstance(s, str) and s.strip()]
    if warn:
        rec["warn"] = warn
    cog.append(rec)
json.dump(cog, open(f"../cognate_out/batch_new_{TAG}.json","w"), ensure_ascii=False, indent=1)
print(f"cognate_out/batch_new_{TAG}.json: {len(cog)}  (无 cog 的词属正常，不写)")
