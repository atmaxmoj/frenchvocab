#!/usr/bin/env python3
"""用 verbecc 为所有动词生成 6 时态变位，映射到设计 schema。
输出 conj.json: { id: { 'Présent':[6], 'Passé composé':[6], 'Imparfait':[6],
                       'Futur':[6], 'Conditionnel':[6], 'Subjonctif':[6] } }
"""
import json, os, re, sys
from verbecc import Conjugator

BASE = os.path.dirname(os.path.abspath(__file__))
skeleton = json.load(open(os.path.join(BASE, "vocab_skeleton.json"), encoding="utf-8"))
c = Conjugator(lang="fr")

# verbecc mood/tense -> 设计 schema 键
MAP = [
    ("Présent",       "indicatif",     "présent"),
    ("Passé composé", "indicatif",     "passé-composé"),
    ("Imparfait",     "indicatif",     "imparfait"),
    ("Futur",         "indicatif",     "futur-simple"),
    ("Conditionnel",  "conditionnel",  "présent"),
    ("Subjonctif",    "subjonctif",    "présent"),
]

def infinitive(fr):
    """去掉反身代词，取裸不定式。返回 (inf, reflexive_bool)。"""
    s = fr.strip()
    m = re.match(r"^s['’]\s*(.+)$", s) or re.match(r"^se\s+(.+)$", s)
    if m:
        return m.group(1).strip(), True
    return s, False

out, fails = {}, []
for w in skeleton:
    if w["pos"] != "verb":
        continue
    inf, refl = infinitive(w["fr"])
    if " " in inf:           # 词组动词，跳过
        fails.append((w["id"], w["fr"], "multiword"))
        continue
    try:
        r = c.conjugate(inf)
        moods = r["moods"]
        conj = {}
        for label, mood, tense in MAP:
            conj[label] = list(moods[mood][tense])
        out[w["id"]] = conj
    except Exception as e:
        fails.append((w["id"], w["fr"], str(e)[:40]))

json.dump(out, open(os.path.join(BASE, "conj.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print(f"变位生成成功 {len(out)} / 动词总数 {sum(1 for w in skeleton if w['pos']=='verb')}")
print(f"失败/跳过 {len(fails)} 个")
for f in fails[:15]:
    print("  ", f)
