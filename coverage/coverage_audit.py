#!/usr/bin/env python3
"""覆盖排查：拿我们的 deck(vocab_skeleton.json) 对 FLELex(CEFR 分级教学词表)做差集。
FLELex = UCLouvain CEFRLex，来自 FFL 教材+分级读物语料，每词标 A1–C2 + 各级词频。
→ 漏出来的 = "B2 前学到、我们却没有"的考试相关实词（天然不含字幕俚语）。

用法: python3 coverage_audit.py
产出: coverage/gap_{A1,A2,B1,B2}.tsv (word\tpos\tfreq)  +  coverage/gaps_all.tsv (含 level 列)
参照: coverage/FleLex_TT_Beacco.tsv (14,236 lemma; CC-BY-NC-SA, cental.uclouvain.be/cefrlex)
"""
import json, csv, re, os

BASE = os.path.dirname(os.path.abspath(__file__))
DECK = os.path.join(BASE, "..", "vocab_skeleton.json")
FLELEX = os.path.join(BASE, "FleLex_TT_Beacco.tsv")

def oe(s):  # œ/æ 归一到 oe，覆盖 deck 里 œ 误存成 æ 的历史 bug
    return (s or "").replace("œ", "oe").replace("æ", "oe")

def norm(s):
    s = oe((s or "").strip().lower())
    s = re.sub(r"^(se |s'|s’)", "", s)      # 去反身
    s = re.sub(r"\s*\(.*?\)\s*", "", s)     # 去括号补充
    return s.strip()

def load_deck():
    d = json.load(open(DECK, encoding="utf-8"))
    W = d["words"] if isinstance(d, dict) and "words" in d else d
    ours = set(norm(w["fr"]) for w in W) | set(oe((w["fr"] or "").strip().lower()) for w in W)
    forms = set()
    for w in W:
        if w.get("formF"):
            forms.add(oe(w["formF"].strip().lower()))
        def walk(x):
            if isinstance(x, str): forms.add(oe(x.strip().lower()))
            elif isinstance(x, dict): [walk(v) for v in x.values()]
            elif isinstance(x, list): [walk(v) for v in x]
        walk(w.get("conj") or {})
    return ours, forms

def covered(wd, ours, forms):
    n, o = norm(wd), oe(wd.lower())
    if n in ours or o in ours or o in forms:
        return True
    # 形容词阴性/变体 → 阳性在库即算覆盖
    for masc in {o[:-1], re.sub(r"ne$", "n", o), re.sub(r"se$", "x", o),
                 re.sub(r"lle$", "l", o), re.sub(r"ère$", "er", o),
                 re.sub(r"ue$", "", o), re.sub(r"gue$", "g", o)}:
        if masc in ours:
            return True
    return False

def main():
    ours, forms = load_deck()
    CONTENT = ("NOM", "VER", "ADJ", "ADV")
    best = {}
    with open(FLELEX, encoding="utf-8") as f:
        for x in csv.DictReader(f, delimiter="\t"):
            tag, lvl, wd = x["tag"], x["level"], x["word"].strip().lower()
            if not tag.startswith(CONTENT) or lvl not in ("A1", "A2", "B1", "B2"):
                continue
            if len(wd) < 2 or wd.startswith("-"):
                continue
            try: ft = float(x["freq_total"])
            except: ft = 0.0
            if wd not in best or ft > best[wd][2]:
                best[wd] = (tag.split(":")[0], lvl, ft)
    miss = [(wd, tg, lvl, ft) for wd, (tg, lvl, ft) in best.items()
            if not covered(wd, ours, forms)]
    order = {"A1": 0, "A2": 1, "B1": 2, "B2": 3}
    miss.sort(key=lambda m: (order[m[2]], -m[3]))
    with open(os.path.join(BASE, "gaps_all.tsv"), "w", encoding="utf-8") as f:
        f.write("word\tpos\tlevel\tfreq\n")
        for wd, tg, lvl, ft in miss:
            f.write(f"{wd}\t{tg}\t{lvl}\t{ft:.1f}\n")
    from collections import Counter
    dist = Counter(m[2] for m in miss)
    for L in ("A1", "A2", "B1", "B2"):
        lst = [m for m in miss if m[2] == L]
        with open(os.path.join(BASE, f"gap_{L}.tsv"), "w", encoding="utf-8") as f:
            f.write("\n".join(f"{w}\t{t}\t{ft:.1f}" for w, t, _, ft in lst))
    print("净漏(FLELex level≤B2 实词):", len(miss), "| 分布:", dict(dist))
    print("产出: coverage/gaps_all.tsv + gap_A1/A2/B1/B2.tsv")

if __name__ == "__main__":
    main()
