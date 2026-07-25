#!/usr/bin/env python3
"""为「一起记词组」里的动词成员生成变位（side-by-side 对比用）。
用 .venv 的 python 跑（verbecc 在那里）：  .venv/bin/python build_cluster_conj.py
读 cluster_out/*.json，收集所有 pos=verb 的成员 fr，verbecc 变位，
输出 cluster_conj.json: { infinitif: {Présent:[6], ...} }（与 conj.json 同 schema）。
"""
import json, os, glob, re
from verbecc import Conjugator

BASE = os.path.dirname(os.path.abspath(__file__))
c = Conjugator(lang="fr")
MAP = [
    ("Présent",       "indicatif",    "présent"),
    ("Passé composé", "indicatif",    "passé-composé"),
    ("Imparfait",     "indicatif",    "imparfait"),
    ("Futur",         "indicatif",    "futur-simple"),
    ("Conditionnel",  "conditionnel", "présent"),
    ("Subjonctif",    "subjonctif",   "présent"),
]

def infinitive(fr):
    s = fr.strip()
    m = re.match(r"^s['’]\s*(.+)$", s) or re.match(r"^se\s+(.+)$", s)
    return (m.group(1).strip() if m else s)

verbs = set()
for fn in glob.glob(f"{BASE}/cluster_out/batch_*.json"):
    try:
        data = json.load(open(fn, encoding="utf-8"))
    except Exception:
        continue
    for item in data:
        for m in (item.get("members") or []):
            if m.get("pos") == "verb" and m.get("fr"):
                verbs.add(m["fr"].strip())

out, fails = {}, []
for v in sorted(verbs):
    inf = infinitive(v)
    if " " in inf:
        fails.append((v, "multiword")); continue
    try:
        moods = c.conjugate(inf)["moods"]
        out[v] = {label: list(moods[mood][tense]) for label, mood, tense in MAP}
    except Exception as e:
        fails.append((v, str(e)[:40]))

json.dump(out, open(f"{BASE}/cluster_conj.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print(f"成员动词变位: {len(out)} / {len(verbs)}  失败 {len(fails)}")
for f in fails[:15]:
    print("  ", f)
