#!/usr/bin/env python3
"""Wave 选词：从 gap_B2.tsv 取接下来 ~300 个未在 deck 的 B2 词。"""
import json, csv, sys, unicodedata, re

N = 300
POS_MAP = {"NOM": "noun", "VER": "verb", "ADJ": "adj", "ADV": "adv"}

def norm(s):
    s = (s or "").strip().lower()
    s = s.replace("œ", "oe").replace("æ", "ae")
    return unicodedata.normalize("NFC", s)

# deck fr set
sk = json.load(open("../vocab_skeleton.json"))
deck = set(norm(w.get("fr")) for w in sk)
maxid = max(int(w["id"]) for w in sk)

# Lexique gender map: lemme -> genre (m/f), only NOM rows
gender = {}
with open("Lexique383.tsv", encoding="utf-8") as f:
    r = csv.reader(f, delimiter="\t")
    header = next(r)
    li = {h: i for i, h in enumerate(header)}
    ilem, icg, igen = li["lemme"], li["cgram"], li["genre"]
    for row in r:
        if len(row) <= igen: continue
        if row[icg] != "NOM": continue
        g = row[igen].strip()
        if g in ("m", "f"):
            gender.setdefault(norm(row[ilem]), g)

# 坏 lemma 黑名单：gap 表里拼错/异体，且正确形已在 deck（normalization 桥不过去）
BLOCKLIST = {"bruir", "accroire", "gaspard", "mac"}   # accroire=缺陷动词(仅不定式,verbecc变不了→过不了闸门)
# 注：enrich gloss 铁律(修正在 gloss_audit_out/user_fix.json)：
#  ① en 禁「French phrase = English」格式(=号会污染 MC 选项)
#  ② en/zh 禁出现【任何法语词，尤其词本身的反身/变形】——那等于把答案写在题面上，Réviser 考不到人
#     (2026-07-18 用户 "在翻译里面写 to soar (s'élancer)会考不到人")；固定搭配只能进 zh 的说明、绝不进 en
#  ③ 括号只做【短消歧】：裸译词第一联想≠法语义时加 context（run→print run、iron→to iron (clothes)），不堆同义词、不塞法语、不写长句
#  已全库清 127 条法语泄漏 + 18 个 = 号 + 32 个裸同形消歧；MC 选项显示完整 gloss（不去括注——用户从没要求去括注）

def is_noise(fr, pos):
    if fr.strip().lower() in BLOCKLIST: return True # 已知坏 lemma
    if "'" in fr or "’" in fr: return True          # 缩合
    if " " in fr or "-" in fr.strip("-"): pass       # keep hyphen compounds like week-end? drop spaces
    if " " in fr: return True
    if fr[:1].isupper(): return True                 # 专名
    if not re.match(r"^[a-zàâäéèêëîïôöùûüÿçœæ\-]+$", fr): return True
    if pos not in POS_MAP: return True
    return False

picked = []
nid = maxid + 1
with open("gap_B2.tsv", encoding="utf-8") as f:
    for line in f:
        parts = line.rstrip("\n").split("\t")
        if len(parts) < 3: continue
        fr_raw, pos_raw, freq = parts[0], parts[1], parts[2]
        fr = fr_raw.strip()
        if is_noise(fr, pos_raw): continue
        if norm(fr) in deck: continue
        deck.add(norm(fr))   # 去重（防 gap 内重复）
        pos = POS_MAP[pos_raw]
        g = gender.get(norm(fr), "") if pos == "noun" else ""
        picked.append({
            "id": str(nid), "rank": nid, "fr": fr, "pos": pos,
            "en": "", "_level": "B2", "_freq": float(freq), "gender": g,
        })
        nid += 1
        if len(picked) >= N: break

json.dump(picked, open("seed_wave.json", "w"), ensure_ascii=False, indent=1)
mini = [{"id": w["id"], "fr": w["fr"], "pos": w["pos"], "gender": w["gender"], "lvl": "B2"} for w in picked]
json.dump(mini, open("seed_mini.json", "w"), ensure_ascii=False, indent=1)

print(f"selected {len(picked)} words, ids {picked[0]['id']}..{picked[-1]['id']}")
from collections import Counter
print("pos:", dict(Counter(w["pos"] for w in picked)))
print("nouns w/ gender:", sum(1 for w in picked if w["pos"]=="noun" and w["gender"]),
      "/ nouns:", sum(1 for w in picked if w["pos"]=="noun"))
print("sample:", ", ".join(w["fr"] for w in picked[:15]))
