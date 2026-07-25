#!/usr/bin/env python3
"""words.csv -> vocab_skeleton.json
确定字段（来自书，可靠）：id, rank, fr, pos, gender, en
待 agent 生成的字段此处留空：ipa, zh, etym, examples, conj, forms
注意：不携带书的例句到产物里（版权）；英文释义足以让 agent 写原创例句。
"""
import csv, json, os, re

BASE = os.path.dirname(os.path.abspath(__file__))
rows = list(csv.DictReader(open(os.path.join(BASE, "words.csv"), encoding="utf-8")))

def parse_pos(raw, fr):
    toks = [t.strip() for t in re.split(r"[;,]", raw) if t.strip()]
    base = set()
    for t in toks:
        base.add(re.sub(r"\(.*?\)", "", t))  # 去掉 (f)/(pl) 等后缀
    gender = None
    if "nm" in base and "nf" in base:
        gender = None            # 双性，留空让 agent 判定主用法
    elif "nm" in base or "nmi" in base:
        gender = "m"
    elif "nf" in base:
        gender = "f"

    if " " in fr.strip():
        pos = "expr"
    elif "v" in base:
        pos = "verb"
    elif base & {"nm", "nf", "nmi", "n"}:
        pos = "noun"
    elif "nadj" in base:
        pos = "adj"              # 名形兼用，默认形容词，agent 可纠正
    elif base & {"adj", "adji"}:
        pos = "adj"
    elif "adv" in base:
        pos = "adv"
    elif "prep" in base:
        pos = "prep"
    elif "conj" in base:
        pos = "conj"
    elif "pro" in base:
        pos = "pron"
    else:
        pos = "other"           # det / intj / 其它
    return pos, gender

out = []
for r in rows:
    rank = int(r["rank"])
    fr = r["headword"].strip()
    pos, gender = parse_pos(r["pos"], fr)
    rec = {
        "id": str(rank),
        "rank": rank,
        "fr": fr,
        "pos": pos,
        "en": r["en"].strip(),
        "raw_pos": r["pos"].strip(),   # 给 agent 参考，不进最终 data.js
    }
    if gender:
        rec["gender"] = gender
    out.append(rec)

out.sort(key=lambda x: x["rank"])
with open(os.path.join(BASE, "vocab_skeleton.json"), "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)

# 统计
from collections import Counter
pc = Counter(x["pos"] for x in out)
gc = Counter(x.get("gender", "—") for x in out)
print(f"骨架 {len(out)} 条 -> vocab_skeleton.json")
print("pos:", dict(pc))
print("gender:", dict(gc))
