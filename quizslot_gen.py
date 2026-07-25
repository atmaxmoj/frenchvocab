#!/usr/bin/env python3
"""生成每词的槽位规格 quizslot_w/{id}.json（结构化题库 v2）。
- 变位：每个【非虚拟式】时态按【不同的光动词形】去重，每形一槽，target=光动词形(无主语)。
- 虚拟式：每动词 1 槽（不枚举人称）。
- sense（义项）/ gender（名词冠词）/ agree（形容词性数）。
- 非人称/事物主语动词：只出第三人称变位（concerner 不能说 je concerne X）。
"""
import sqlite3, json, re, os

BASE = os.path.dirname(os.path.abspath(__file__))
c = sqlite3.connect(os.path.join(BASE, "vocab.db"))
conj = json.load(open(os.path.join(BASE, "conj.json"), encoding="utf-8"))
PERS = ["je/j'", "tu", "il/elle/on", "nous", "vous", "ils/elles"]

# 只用第三人称单数（il）的纯无人称动词
IL_ONLY = {"falloir", "pleuvoir", "neiger", "geler", "bruiner", "tonner"}
# 事物/抽象作主语、人作宾语的动词：只第三人称(单/复)
THING_SUBJ = {"concerner", "importer", "suffire", "s'agir", "valoir", "plaire", "découler", "résulter", "incomber"}

_SUBJ = re.compile(r"^(qu(?:e\s+|'))?(j'|(?:je|tu|ils|elles|il|elle|on|nous|vous)"
                   r"(?:\s+(?:m'|t'|s'|me|te|se|nous|vous))?\s+)", re.I)
def bare(f):
    return _SUBJ.sub("", f, count=1).strip()
def senses(zh):
    return [s.strip() for s in re.split(r"[；;、]", zh or "") if s.strip()]

n = 0; slots_tot = 0
for wid, fr, pos, gender, en, zh in c.execute("SELECT id,fr,pos,gender,en,zh FROM words"):
    slots = []
    if pos == "verb":
        # 限定可用人称（非人称/事物主语动词只第三人称）
        if fr in IL_ONLY:
            allowed = {2}
        elif fr in THING_SUBJ:
            allowed = {2, 5}
        else:
            allowed = set(range(6))
        for tense, forms in conj.get(str(wid), {}).items():
            if tense == "Subjonctif":
                slots.append({"key": "t|Subjonctif", "facet": "subj", "tense": "Subjonctif"})
                continue
            seen = {}
            for p, f in enumerate(forms):
                if p not in allowed:
                    continue
                seen.setdefault(bare(f), []).append(PERS[p])
            for i, (b, ppl) in enumerate(seen.items()):
                slots.append({"key": f"t|{tense}|{i}", "facet": "tense", "tense": tense, "target": b, "persons": ppl})
    for i, s in enumerate(senses(zh)):
        slots.append({"key": f"s|{i}", "facet": "sense", "sense_zh": s})
    if pos == "noun" and gender in ("m", "f"):
        slots.append({"key": "gender", "facet": "gender", "gender": gender})
    if pos == "adj":
        for g, lab in [("mp", "阳性复数"), ("f", "阴性单数"), ("fp", "阴性复数")]:
            slots.append({"key": f"g|{g}", "facet": "agree", "gender": g, "label": lab})
    json.dump({"id": wid, "fr": fr, "pos": pos, "gender": gender, "en": en, "zh": zh, "slots": slots},
              open(os.path.join(BASE, "quizslot_w", f"{wid}.json"), "w"), ensure_ascii=False)
    n += 1; slots_tot += len(slots)
print(f"槽位规格重写 {n} 词, 共 {slots_tot} 槽")
# 确认非人称动词
for fr in ("concerner", "importer", "falloir"):
    r = c.execute("SELECT id FROM words WHERE fr=?", (fr,)).fetchone()
    if r:
        d = json.load(open(os.path.join(BASE, "quizslot_w", f"{r[0]}.json"), encoding="utf-8"))
        tn = [s["key"] for s in d["slots"] if s["facet"] == "tense"]
        print(f"  {fr}: {len(tn)} 个变位槽 (示例 {tn[:3]})")
