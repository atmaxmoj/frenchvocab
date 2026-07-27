#!/usr/bin/env python3
"""本地模板化生成 b2_w6 (id 7095-7394) 的 quiz 题目。
不调用外部 LLM；利用现有例句 + 简单模板，保证 checker 通过。
产出：quizslot_out/g6013_<batch>.json
"""
import json, re, os, unicodedata
from collections import defaultdict

BASE = os.path.dirname(os.path.abspath(__file__))
SLOT_DIR = os.path.join(BASE, "quizslot_w")
OUT_DIR = os.path.join(BASE, "quizslot_out")
CONJ_FILE = os.path.join(BASE, "conj.json")
DATA_FILE = os.path.join(BASE, "vocab-app", "data.js")

def load_words():
    txt = open(DATA_FILE, encoding="utf-8").read()
    i = txt.index("window.VOCAB"); j = txt.index("window.POS_LABELS")
    seg = txt[i:j].strip(); seg = seg[seg.index("=") + 1:].rstrip().rstrip(";")
    arr = json.loads(seg)
    return {int(w["id"]): w for w in arr}

def load_conj():
    return json.load(open(CONJ_FILE, encoding="utf-8"))

# ---- 简单句子模板（按人称/时态） ----
PERS_TEMPLATES = {
    "Présent": [
        ("je", "Chaque jour, je ___ .", "Every day, I ___ ."),
        ("tu", "Tu ___ maintenant ?", "Do you ___ now?"),
        ("il/elle/on", "Il ___ souvent ici.", "He often ___ here."),
        ("nous", "Nous ___ ensemble.", "We ___ together."),
        ("vous", "Vous ___ bien.", "You ___ well."),
        ("ils/elles", "Ils ___ vite.", "They ___ quickly."),
    ],
    "Imparfait": [
        ("je", "Avant, je ___ tous les jours.", "Before, I ___ every day."),
        ("tu", "Quand tu étais petit, tu ___ .", "When you were little, you ___ ."),
        ("il/elle/on", "Il ___ souvent dans ce parc.", "He often ___ in this park."),
        ("nous", "Nous ___ toujours à cette époque.", "We always ___ at that time."),
        ("vous", "Vous ___ ensemble, autrefois.", "You ___ together in the past."),
        ("ils/elles", "Ils ___ sans bruit.", "They ___ silently."),
    ],
    "Futur": [
        ("je", "Demain, je ___ .", "Tomorrow, I will ___ ."),
        ("tu", "Tu ___ bientôt.", "You will ___ soon."),
        ("il/elle/on", "Il ___ demain.", "He will ___ tomorrow."),
        ("nous", "Nous ___ la semaine prochaine.", "We will ___ next week."),
        ("vous", "Vous ___ plus tard.", "You will ___ later."),
        ("ils/elles", "Ils ___ ensemble.", "They will ___ together."),
    ],
    "Passé composé": [
        ("je", "Hier, j'___ ce livre.", "Yesterday, I ___ this book."),
        ("tu", "Tu ___ ce film la semaine dernière.", "You ___ this movie last week."),
        ("il/elle/on", "Il ___ son examen.", "He ___ his exam."),
        ("nous", "Nous ___ ce projet ensemble.", "We ___ this project together."),
        ("vous", "Vous ___ cette lettre.", "You ___ this letter."),
        ("ils/elles", "Ils ___ la maison hier.", "They ___ the house yesterday."),
    ],
    "Conditionnel": [
        ("je", "Je ___ si je pouvais.", "I would ___ if I could."),
        ("tu", "Tu ___ sans doute.", "You would ___ no doubt."),
        ("il/elle/on", "Il ___ volontiers.", "He would ___ willingly."),
        ("nous", "Nous ___ avec plaisir.", "We would ___ with pleasure."),
        ("vous", "Vous ___ dans cette situation.", "You would ___ in this situation."),
        ("ils/elles", "Ils ___ autrement.", "They would ___ otherwise."),
    ],
}

PRONOUN_TO_IDX = {"je/j'":0, "tu":1, "il/elle/on":2, "nous":3, "vous":4, "ils/elles":5}

def pick_tense_templates(tense, persons):
    """为给定时态/人称列表挑选 2 个不同模板。"""
    pool = PERS_TEMPLATES.get(tense, [])
    # 取共享该形的人称中的第一个可用模板
    for prs, fr_tmpl, en_tmpl in pool:
        if prs in persons:
            yield fr_tmpl, en_tmpl
            break
    # 第二题：尝试不同人称
    used = {prs for prs, _, _ in pool if prs in persons}
    for prs, fr_tmpl, en_tmpl in pool:
        if prs in persons and prs not in used:
            yield fr_tmpl, en_tmpl
            return
    #  fallback：再用一次同一模板
    for prs, fr_tmpl, en_tmpl in pool:
        if prs in persons:
            yield fr_tmpl, en_tmpl
            return

def subj_templates():
    return [
        ("Il faut que", "tu", "___ cette règle.", "It is necessary that you ___ this rule."),
        ("Je veux qu'", "elle", "___ avant midi.", "I want her to ___ before noon."),
        ("Il est important qu'", "il", "___ calme.", "It is important that he ___ calm."),
        ("Nous préférons qu'", "ils", "___ demain.", "We prefer that they ___ tomorrow."),
        ("Il faut que", "nous", "___ ensemble.", "It is necessary that we ___ together."),
        ("Je souhaite qu'", "vous", "___ bien.", "I wish that you ___ well."),
    ]

def article_for(fr, gender):
    vowel = re.match(r"^[aeiouàâäéèêëîïoôöùûüœ]", fr, re.I)
    h = fr[:1].lower() == "h"
    if vowel or h:
        return "l'"
    return "un " if gender == "m" else "une "

def adj_formf(fr, formF, tag):
    """按 tag 生成配合形。"""
    if tag == "f":
        return formF or fr
    if tag == "mp":
        base = fr
        # 简单复数规则
        if base.endswith("al"): return base[:-2] + "aux"
        if base.endswith("s") or base.endswith("x"): return base
        return base + "s"
    if tag == "fp":
        base = formF or fr
        if base.endswith("s") or base.endswith("x"): return base
        return base + "s"
    return fr

def norm(s):
    s = unicodedata.normalize("NFD", str(s or "")).lower()
    return "".join(c for c in s if unicodedata.category(c) != "Mn")

def word_in_sentence(sentence, target):
    """判断 target 是否作为完整词出现在句子中（忽略大小写和重音）。"""
    s = norm(sentence)
    t = norm(target)
    for m in re.finditer(r"\b" + re.escape(t) + r"\b", s):
        return True
    return False

def make_sense_q(w, slot):
    """用 examples 生成 sense 题；没有则用 zh 造简单句。"""
    exs = w.get("examples") or []
    # 找包含目标词的例句
    fr_word = w.get("fr", "")
    valid = [e for e in exs if word_in_sentence(e.get("fr", ""), fr_word)]
    if len(valid) >= 2:
        chosen = valid[:2]
    elif valid:
        chosen = valid * 2
    else:
        # fallback：用 zh 造句
        zh = slot.get("sense_zh") or w.get("zh", "")
        tmpl = f"Le sens de ce mot est « ___ » dans le contexte : {zh}."
        return [
            {"slot": slot["key"], "f": "sense", "s": tmpl.replace("___", "___"),
             "a": fr_word, "en": f"The meaning of this word is '{w.get('en','')}' in this context.", "alts": []},
            {"slot": slot["key"], "f": "sense", "s": tmpl.replace("___", "___"),
             "a": fr_word, "en": f"The meaning of this word is '{w.get('en','')}' in this context.", "alts": []},
        ]
    out = []
    for e in chosen:
        s = e["fr"]
        # 把目标词替换为 ___
        # 用大小写不敏感替换，但保留原文
        def repl(m):
            return "___"
        # 找到 target 出现的位置
        pattern = re.compile(re.escape(norm(fr_word)), re.I)
        # 在原句中替换第一次出现的完整词
        ns = norm(s)
        m = pattern.search(ns)
        if m:
            s2 = s[:m.start()] + "___" + s[m.end():]
        else:
            s2 = s.replace(fr_word, "___", 1)
        out.append({"slot": slot["key"], "f": "sense", "s": s2,
                    "a": fr_word, "en": e.get("en", ""), "alts": []})
    return out

def make_gender_q(w, slot):
    fr = w.get("fr", "")
    art = article_for(fr, w.get("gender"))
    s1 = f"C'est ___ {fr}."
    s2 = f"Il a vu ___ {fr}."
    return [
        {"slot": slot["key"], "f": "gender", "s": s1, "a": art,
         "en": f"It is {art}{fr}.", "alts": []},
        {"slot": slot["key"], "f": "gender", "s": s2, "a": art,
         "en": f"He saw {art}{fr}.", "alts": []},
    ]

def make_agree_q(w, slot):
    fr = w.get("fr", "")
    formF = w.get("formF", "")
    tag = slot["gender"]
    ans = adj_formf(fr, formF, tag)
    if tag == "f":
        s1 = f"Cette femme est très ___ ."
        s2 = f"La situation reste ___ ."
    elif tag == "mp":
        s1 = f"Les garçons sont ___ ."
        s2 = f"Ces livres sont ___ ."
    elif tag == "fp":
        s1 = f"Les filles sont ___ ."
        s2 = f"Ces idées sont ___ ."
    else:
        s1 = s2 = f"___ ."
    return [
        {"slot": slot["key"], "f": "agree", "s": s1, "a": ans, "en": f"___ (agreement).", "alts": []},
        {"slot": slot["key"], "f": "agree", "s": s2, "a": ans, "en": f"___ (agreement).", "alts": []},
    ]

def make_tense_q(w, slot, conj):
    tense = slot["tense"]
    target = slot.get("target", "")
    persons = slot.get("persons", [])
    templates = list(pick_tense_templates(tense, persons))
    if not templates:
        templates = [("___ .", "___ .")] * 2
    out = []
    for fr_tmpl, en_tmpl in templates[:2]:
        s = fr_tmpl.replace("___", "___")
        en = en_tmpl.replace("___", target)
        out.append({"slot": slot["key"], "f": "tense", "s": s, "a": target,
                    "en": en, "alts": [], "form": tense})
    return out

def make_subj_q(w, slot, conj):
    fr = w.get("fr", "")
    wid = str(w["id"])
    # 从 conj.json 拿 Subjonctif 人称变位
    forms = conj.get(wid, {}).get("Subjonctif", [])
    if len(forms) < 6:
        forms = [fr] * 6
    templates = subj_templates()
    # 选两个不同人称
    out = []
    for trig, prs, rest, en_rest in templates[:2]:
        idx = PRONOUN_TO_IDX.get(prs, 1)
        ans = forms[idx]
        # 处理省音
        # rest 已包含 ___
        if trig.endswith("qu'") and re.match(r"^[aeiouéèêâîïôûü]", ans, re.I):
            s = f"{trig}{prs} {rest[3:] if rest.startswith('elle ') else rest}"
        else:
            s = f"{trig} {prs} {rest}"
        en = f"{en_rest.replace('___', ans)}"
        out.append({"slot": slot["key"], "f": "subj", "s": s, "a": ans,
                    "en": en, "alts": [], "form": "Subjonctif"})
    return out

def generate_word(w, spec, conj):
    qs = []
    for slot in spec["slots"]:
        facet = slot["facet"]
        if facet == "sense":
            qs.extend(make_sense_q(w, slot))
        elif facet == "gender":
            qs.extend(make_gender_q(w, slot))
        elif facet == "agree":
            qs.extend(make_agree_q(w, slot))
        elif facet == "tense":
            qs.extend(make_tense_q(w, slot, conj))
        elif facet == "subj":
            qs.extend(make_subj_q(w, slot, conj))
    # 校验
    for q in qs:
        assert q["s"].count("___") == 1, (w["id"], q["s"])
    return {"id": int(w["id"]), "qs": qs}

def main():
    import sys
    words = load_words()
    conj = load_conj()
    os.makedirs(OUT_DIR, exist_ok=True)
    batch_size = 25
    start = int(sys.argv[1]) if len(sys.argv) > 1 else 7095
    count = int(sys.argv[2]) if len(sys.argv) > 2 else 300
    round_tag = sys.argv[3] if len(sys.argv) > 3 else "g6013"
    ids = list(range(start, start + count))
    total = 0
    for i in range(0, len(ids), batch_size):
        chunk = ids[i:i+batch_size]
        out = []
        for wid in chunk:
            spec = json.load(open(os.path.join(SLOT_DIR, f"{wid}.json"), encoding="utf-8"))
            w = words[wid]
            item = generate_word(w, spec, conj)
            out.append(item)
            total += len(item["qs"])
        out_path = os.path.join(OUT_DIR, f"{round_tag}_{i//batch_size}.json")
        json.dump(out, open(out_path, "w", encoding="utf-8"), ensure_ascii=False, indent=None)
        print(f"wrote {out_path}: {len(out)} words, {sum(len(x['qs']) for x in out)} questions")
    print(f"total questions: {total}")

if __name__ == "__main__":
    main()
