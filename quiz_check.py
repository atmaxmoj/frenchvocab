#!/usr/bin/env python3
"""结构化题库 checker：核对每词的槽位是否都被覆盖（每槽≥2题）、答案是否对得上结构。
用法: python3 quiz_check.py [round]   # 默认查 quizslot_out/g{round}_*.json，round 缺省=全部
直接从结构查：每个 slot 应有 ≥2 题；tense 槽答案必须==该 (时态,人称) 的精确变位形。"""
import sys, json, glob, re, unicodedata, sqlite3
from collections import defaultdict

BASE = "/Users/wangsijie/Develop/projects/french/vocabulary"
rnd = sys.argv[1] if len(sys.argv) > 1 else "*"

def norm(s):
    s = unicodedata.normalize("NFD", str(s or "")).lower()
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return " ".join(s.split())

# 剥掉主语代词，只比变位动词部分（il/elle/on 同形、主语可换/可省，不算错）。
# 省音主语 j' 撇号后直接接；非省音主语必须后跟空白（避免把 "ont" 里的 "on" 误剥）。
_PRON = re.compile(
    r"^(que\s+|qu')?"
    r"(j'|"
    r"(?:je|tu|ils|elles|il|elle|on|nous|vous)(?:\s+(?:m'|t'|s'|me|te|se|nous|vous))?\s+)",
    re.I)
def verb_core(s):
    s = str(s or "")
    prev = None
    while prev != s:           # 反复剥（处理 que/qu' + 主语）
        prev = s
        s = _PRON.sub("", s, count=1)
    return norm(s)
# 比变位时再忽略尾部性数配合（être 动词 allé/allée/allés/allées 都对）
def tense_eq(a, target):
    strip = lambda x: re.sub(r"[es]+$", "", verb_core(x))
    return strip(a) == strip(target)

# 期望槽位（含 tense 槽的精确 target）
spec = {}
for fn in glob.glob(f"{BASE}/quizslot_w/*.json"):
    d = json.load(open(fn, encoding="utf-8"))
    spec[d["id"]] = {s["key"]: s for s in d["slots"]}

# 生成的题
got = defaultdict(lambda: defaultdict(list))   # wid -> slot -> [q...]
nfiles = 0
for fn in glob.glob(f"{BASE}/quizslot_out/g{rnd}_*.json"):
    nfiles += 1
    try:
        data = json.load(open(fn, encoding="utf-8"))
    except Exception as e:
        print(f"  ⚠ 读不动 {fn}: {e}"); continue
    for it in data:
        wid = it.get("id")
        for q in it.get("qs", []):
            got[wid][q.get("slot", "?")].append(q)

print(f"=== checker: {nfiles} 文件, {len(got)} 词 ===\n")
errs = defaultdict(int)
examples = defaultdict(list)
words_full = 0
for wid in sorted(got):
    exp = spec.get(wid, {})
    if not exp:
        errs["未知词id"] += 1; continue
    missing, badnum, badblank, badans, badslot, noen = [], [], [], [], [], []
    for key, sp in exp.items():
        qs = got[wid].get(key, [])
        if len(qs) < 2: missing.append(key)
    for slot, qs in got[wid].items():
        if slot not in exp: badslot.append(slot)
        for q in qs:
            s, a, en = q.get("s", ""), q.get("a", ""), q.get("en", "")
            if s.count("___") != 1: badblank.append(slot)
            if not a.strip(): pass
            if not en.strip(): noen.append(slot)
            # tense 槽：答案必须==精确变位形
            sp = exp.get(slot, {})
            if sp.get("facet") == "tense":
                if not tense_eq(a, sp.get("target", "")):
                    badans.append((slot, a, sp.get("target")))
                elif _PRON.match(a):       # 答案应是光动词形，不该带主语代词
                    badans.append((slot, a + " (带主语)", sp.get("target")))
    if missing: errs["槽位缺<2题"] += 1; examples["槽位缺<2题"].append((wid, missing[:3]))
    if badblank: errs["空格数≠1"] += 1
    if badans: errs["变位答案对不上"] += 1; examples["变位答案对不上"].append((wid, badans[:2]))
    if badslot: errs["多出未知槽"] += 1
    if noen: errs["缺英文翻译"] += 1
    if not (missing or badblank or badans or badslot or noen):
        words_full += 1

print(f"✅ 完全合格的词: {words_full}/{len(got)}")
print("问题统计:", dict(errs) if errs else "无")
for k, exs in examples.items():
    print(f"\n  [{k}] 例:")
    for wid, detail in exs[:4]:
        fr = sqlite3.connect(f"{BASE}/vocab.db").execute("SELECT fr FROM words WHERE id=?", (wid,)).fetchone()
        print(f"    {fr[0] if fr else wid}: {detail}")
