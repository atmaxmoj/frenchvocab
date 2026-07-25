#!/usr/bin/env python3
"""装配最终词库：
  vocab_skeleton.json (fr/pos/gender/en/rank)
  + enrich_out/*.json  (ipa/zh/etym/examples)
  + conj.json          (动词变位)
  -> vocab-app/data.js  (window.VOCAB，app 直接加载)
  -> vocab.db           (SQLite 规范化库：words / examples / conj)
"""
import json, glob, os, sqlite3, re

BASE = os.path.dirname(os.path.abspath(__file__))
sk = {w["id"]: w for w in json.load(open(f"{BASE}/vocab_skeleton.json", encoding="utf-8"))}
conj = json.load(open(f"{BASE}/conj.json", encoding="utf-8"))

enr = {}
# 先铺 enrich 基线，再用 audit 修正覆盖
for fn in sorted(glob.glob(f"{BASE}/enrich_out/batch_*.json")):
    for e in json.load(open(fn, encoding="utf-8")):
        enr[str(e["id"])] = e
for fn in sorted(glob.glob(f"{BASE}/audit_out/batch_*.json")):
    for e in json.load(open(fn, encoding="utf-8")):
        enr[str(e["id"])] = e
# QA 复查：字段级修正（最高优先，只覆盖被标记的字段）
_qa_n = 0
for fn in sorted(glob.glob(f"{BASE}/qa_out/batch_*.json")):
    try:
        data = json.load(open(fn, encoding="utf-8"))
    except Exception:
        continue
    for item in data:
        if not (isinstance(item, dict) and item.get("id") and item.get("fix")):
            continue
        wid = str(item["id"])
        if wid not in enr:
            continue
        for k, v in item["fix"].items():
            if k in ("ipa", "zh", "etym", "examples"):
                enr[wid][k] = v
        _qa_n += 1
print(f"QA 字段级修正应用: {_qa_n} 条")

# 例句补充（补齐"只有 1 例句"的词）：examples_supp/*.json = [{id, examples:[{fr,en,target}]}]
# 追加到已有 examples 之后（按 fr 去重）
_supp_n = 0
for fn in sorted(glob.glob(f"{BASE}/examples_supp/*.json")):
    try:
        data = json.load(open(fn, encoding="utf-8"))
    except Exception:
        continue
    for item in data:
        wid = str(item.get("id", ""))
        if wid not in enr:
            continue
        cur = enr[wid].setdefault("examples", [])
        have = {(x.get("fr") or "").strip() for x in cur}
        for ex in item.get("examples", []):
            if ex.get("fr") and ex["fr"].strip() not in have:
                cur.append(ex); have.add(ex["fr"].strip()); _supp_n += 1
print(f"例句补充追加: {_supp_n} 条")

# 词源记忆钩子（etymology hook）：词根拆解 + 为什么是这个义 + 英语桥 + 同根词。
# 手写 etym_hooks.json + 生成 etym_hook_out/*.json，id -> {roots, why, en?, family?[]}
etym_hooks = {}
def _load_hooks(src):
    try:
        d = json.load(open(src, encoding="utf-8"))
    except Exception:
        return
    items = d.items() if isinstance(d, dict) else ((str(x.get("id")), x) for x in d if isinstance(x, dict) and x.get("id"))
    for wid, h in items:
        if isinstance(h, dict) and (h.get("roots") or h.get("why")):
            etym_hooks[str(wid)] = {k: h[k] for k in ("roots", "why", "en", "family") if h.get(k)}
for _hf in sorted(glob.glob(f"{BASE}/etym_hook_out/*.json")):
    _load_hooks(_hf)
_load_hooks(f"{BASE}/etym_hooks.json")   # 手写优先（最后加载覆盖生成的）
print(f"词源钩子: {len(etym_hooks)} 条")

# 同源词（cognate）：agents 标注的「拼写相近 + 意义相同」英文词，写到 cog 字段
# 文件：cognate_out/batch_*.json，每条 {"id":.., "cog":"ignore"}（无同源词则省略/为空）
cog_map = {}    # id -> 英文同源词
warn_map = {}   # id -> [法语有但同源词没有的中文义项]，前端标红
cogfr_map = {}  # id -> 法语词的 agent 认知差异标注 "change[ment]"
cogen_map = {}  # id -> 英文同源词的差异标注 "change"
import unicodedata
_unbracket = re.compile(r"[\[\]]")
_brk = re.compile(r"\[[^\]]*\]")
def _strip_acc(s):
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")
def _valid_mark(mark, plain):
    # 去掉方括号后应与原词一致（忽略大小写/空白），否则视为无效
    return isinstance(mark, str) and _unbracket.sub("", mark).strip().lower() == (plain or "").strip().lower()
def _shared(mark):
    # 方括号"外"的共享词干（去重音、小写），用于校验法/英两边共享部分确实一致
    return _strip_acc(_brk.sub("", mark or "")).lower()
def _affix_overlap(a, b):
    # 前缀+后缀共享长度 / 短词长度，判断 fr 与英文同源词是否真有可视词干
    a = _strip_acc(a or "").lower(); b = _strip_acc(b or "").lower()
    n, m = len(a), len(b); p = 0
    while p < n and p < m and a[p] == b[p]: p += 1
    s = 0
    while s < n - p and s < m - p and a[n - 1 - s] == b[m - 1 - s]: s += 1
    return (p + s) / min(n, m) if n and m else 0, p + s
for fn in sorted(glob.glob(f"{BASE}/cognate_out/batch_*.json")):
    try:
        data = json.load(open(fn, encoding="utf-8"))
    except Exception:
        continue
    for item in data:
        if isinstance(item, dict) and item.get("id"):
            wid = str(item["id"])
            v = (item.get("cog") or "").strip().lower()
            if v:
                cog_map[wid] = v
                warn = [s.strip() for s in (item.get("warn") or []) if isinstance(s, str) and s.strip()]
                if warn:
                    warn_map[wid] = warn
                # agent 写的认知差异标注（拼写差异不是算法能定的）
                cf, ce = item.get("cogFr"), item.get("cogEn")
                if _valid_mark(ce, v):
                    cogen_map[wid] = ce.strip()
                if cf:  # 法语原词在装配阶段才有，这里先存，下面校验
                    cogfr_map[wid] = cf.strip()
# 同源词复审（cog_audit_out/*.json）：drop=删假朋友/同形；set=给无 cog 词补桥（人工覆盖仍优先于它）
_audit_drop = _audit_set = 0
for fn in glob.glob(f"{BASE}/cog_audit_out/*.json"):
    try:
        data = json.load(open(fn, encoding="utf-8"))
    except Exception:
        continue
    for e in data:
        wid = str(e.get("id"))
        if e.get("action") == "drop":
            cog_map.pop(wid, None); cogfr_map.pop(wid, None); cogen_map.pop(wid, None); warn_map.pop(wid, None)
            _audit_drop += 1
        elif e.get("action") == "set" and (e.get("cog") or "").strip():
            cog_map[wid] = e["cog"].strip().lower()
            if e.get("cogFr"): cogfr_map[wid] = e["cogFr"].strip()
            if e.get("cogEn"): cogen_map[wid] = e["cogEn"].strip()
            warn_map[wid] = []
            _audit_set += 1
if _audit_drop or _audit_set:
    print(f"同源词复审: 删 {_audit_drop}，补 {_audit_set}")

# 人工覆盖（用户逐个纠正的词，最高优先）：cognate_overrides.json
#   {"501": {"cog":"past","cogFr":"pas[sé]","cogEn":"pas[t]","warn":[]}}  或  {"id": null} 删除
try:
    _ov = json.load(open(f"{BASE}/cognate_overrides.json", encoding="utf-8"))
except Exception:
    _ov = {}
for wid, o in _ov.items():
    if not o or not o.get("cog"):
        cog_map.pop(wid, None); cogfr_map.pop(wid, None); cogen_map.pop(wid, None); warn_map.pop(wid, None)
    else:
        cog_map[wid] = o["cog"].strip().lower()
        if o.get("cogFr"): cogfr_map[wid] = o["cogFr"]
        if o.get("cogEn"): cogen_map[wid] = o["cogEn"]
        warn_map[wid] = [s for s in (o.get("warn") or []) if isinstance(s, str) and s.strip()]
if _ov:
    print(f"人工覆盖: {len(_ov)} 条")
print(f"同源词标注: {len(cog_map)} 条，含义项告警: {len(warn_map)} 条，差异标注: {len(cogfr_map)} 条")
_cog_dropped = 0  # 所有义项都被告警(即同源词不覆盖任何义)的假朋友，丢弃
_cog_badmark = 0  # 差异标注矛盾且无词干重叠，丢弃
_cog_algomark = 0  # 标注矛盾但词干重叠，保留同源词、差异走前端算法

# 一起记的词组：cluster_out/*.json + cluster_conj.json（动词成员变位）
cluster_map = {}
_cluster_badid = 0
try:
    cluster_conj = json.load(open(f"{BASE}/cluster_conj.json", encoding="utf-8"))
except Exception:
    cluster_conj = {}
for fn in sorted(glob.glob(f"{BASE}/cluster_out/batch_*.json")):
    try:
        data = json.load(open(fn, encoding="utf-8"))
    except Exception:
        continue
    for item in data:
        if not (isinstance(item, dict) and item.get("id") and item.get("members")):
            continue
        wid = str(item["id"])
        if wid not in sk:                 # id 必须是真实词 id（挡掉幻觉/范围 id）
            _cluster_badid += 1
            continue
        head_fr = sk[wid]["fr"].strip().lower()
        members, seen = [], set()
        for m in item["members"]:
            if not (isinstance(m, dict) and m.get("fr")):
                continue
            fr = m["fr"].strip()
            key = fr.lower()
            if key == head_fr or key in seen:   # 别把本词或重复词列进来
                continue
            seen.add(key)
            mem = {"fr": fr, "pos": m.get("pos", "other"), "gloss": (m.get("gloss") or "").strip()}
            if mem["pos"] == "verb" and fr in cluster_conj:
                mem["conj"] = cluster_conj[fr]
            members.append(mem)
        if members:
            cluster_map[wid] = {"note": (item.get("note") or "").strip(), "members": members}
print(f"一起记词组: {len(cluster_map)} 条（丢弃非法 id {_cluster_badid}）")

# 小测验题库：quiz_out/*.json，每条 {id, qs:[{f,s,en,a,alts,form?}]}
def _norm_form(s):
    return " ".join(_strip_acc(str(s or "")).lower().split())

# être 助动词复合时态：分词性数不定（je suis allé/allée），自动把阴/阳两形都收进 alts
_ETRE_AUX = {"suis", "es", "est", "sommes", "êtes", "sont"}
def _etre_gender_alts(a):
    toks = str(a or "").split()
    if len(toks) < 2 or not any(t.lower() in _ETRE_AUX for t in toks):
        return []
    plural = any(t.lower() in {"sommes", "êtes", "sont"} for t in toks)
    last = toks[-1]; low = last.lower()
    for ms, fs, mp, fp in [("é", "ée", "és", "ées"), ("i", "ie", "is", "ies"), ("u", "ue", "us", "ues")]:
        for suf in (fp, mp, fs, ms):          # 最长优先
            if low.endswith(suf):
                base = last[: len(last) - len(suf)]
                pre = " ".join(toks[:-1])
                return [f"{pre} {base}{x}" for x in ((mp, fp) if plural else (ms, fs))]
    return []
quiz_map = {}
_quiz_q = 0
_quiz_badtense = 0
_quiz_malformed = 0
_struct_words_set = set()
for fn in sorted(glob.glob(f"{BASE}/quiz_out/*.json")):
    try:
        data = json.load(open(fn, encoding="utf-8"))
    except Exception:
        continue
    for item in data:
        if not (isinstance(item, dict) and item.get("id") and item.get("qs")):
            continue
        wid = str(item["id"])
        if wid not in sk:
            continue
        # 该动词所有精确变位形式拼一起，用于校验 tense 题答案
        forms_flat = " || ".join(_norm_form(f) for arr in conj.get(wid, {}).values() for f in arr)
        qs = []
        for q in item["qs"]:
            if not (isinstance(q, dict) and q.get("s") and q.get("a") and "___" in q.get("s", "")):
                continue
            f = q.get("f", "usage")
            a = q["a"].strip()
            # 畸形：多个 ___ 但空格数与答案词数不符（如两空都想填 "médecine"，或 "à ... à"）
            nb = q["s"].count("___")
            if nb > 1 and nb != len(a.split()):
                _quiz_malformed += 1
                continue
            # 变位题：答案形态必须在精确变位表里找到，否则丢弃（防 agent 编错变位）
            if f == "tense" and forms_flat and _norm_form(a) not in forms_flat:
                _quiz_badtense += 1
                continue
            qq = {"f": f, "s": q["s"].strip(), "en": (q.get("en") or "").strip(),
                  "a": a, "slot": None,
                  "alts": [x.strip() for x in (q.get("alts") or []) if isinstance(x, str) and x.strip()]}
            if q.get("form"):
                qq["form"] = q["form"].strip()
            qs.append(qq)
        if qs:
            quiz_map[wid] = qs
            _quiz_q += len(qs)

# 结构化题库（quizslot_out）：带 slot 标签，按词【覆盖】旧的 freeform 题
def _slotkeys(wid):
    try:
        d = json.load(open(f"{BASE}/quizslot_w/{wid}.json", encoding="utf-8"))
        return {s["key"] for s in d.get("slots", [])}
    except Exception:
        return set()
_struct_words = 0
_quiz_unknownslot = 0
for fn in sorted(glob.glob(f"{BASE}/quizslot_out/*.json")):
    try:
        data = json.load(open(fn, encoding="utf-8"))
    except Exception:
        continue
    for item in data:
        if not (isinstance(item, dict) and item.get("id") and item.get("qs")):
            continue
        wid = str(item["id"])
        if wid not in sk:
            continue
        known = _slotkeys(wid)
        qs = []
        for q in item["qs"]:
            if not (isinstance(q, dict) and q.get("s") and q.get("a") and "___" in q.get("s", "")):
                continue
            slot = (q.get("slot") or "").strip() or None
            if slot not in known:          # 丢掉规格外的多余槽（如 epicene 名词的 gender 题）
                _quiz_unknownslot += 1
                continue
            f = q.get("f", "usage")
            a = q["a"].strip()
            nb = q["s"].count("___")
            if nb > 1 and nb != len(a.split()):
                _quiz_malformed += 1
                continue
            qq = {"f": f, "s": q["s"].strip(), "en": (q.get("en") or "").strip(),
                  "a": a, "slot": slot,
                  "alts": [x.strip() for x in (q.get("alts") or []) if isinstance(x, str) and x.strip()]}
            if f == "tense":               # être 复合时态：阴/阳两形都算对
                for v in _etre_gender_alts(a):
                    if v != a and v not in qq["alts"]:
                        qq["alts"].append(v)
            if q.get("form"):
                qq["form"] = q["form"].strip()
            qs.append(qq)
        if qs:
            if wid not in _struct_words_set:
                _struct_words += 1
            quiz_map[wid] = qs          # 覆盖该词的旧题
            _struct_words_set.add(wid)
print(f"小测验题库: {len(quiz_map)} 词（结构化 {_struct_words} 词）/ "
      f"{sum(len(v) for v in quiz_map.values())} 题（变位丢弃 {_quiz_badtense}、畸形 {_quiz_malformed}、规格外槽丢弃 {_quiz_unknownslot}）")

# 清洗：剥掉混进文本的 HTML 标签（部分 agent 用 <em> 标斜体，前端按纯文本渲染会原样显示）
_TAG = re.compile(r"<[^>]+>")
def clean(s):
    return _TAG.sub("", s).strip() if isinstance(s, str) else s

# 多义词释义重排（最常用义在前）：gloss_order_out/*.json -> {id: en}
import glob as _glob, re as _re
gloss_order = {}
for fn in _glob.glob(f"{BASE}/gloss_order_out/*.json"):
    try:
        for e in json.load(open(fn, encoding="utf-8")):
            if e.get("id") is not None and (e.get("en") or "").strip():
                gloss_order[str(e["id"])] = e["en"].strip()
    except Exception as ex:
        print(f"  ⚠ gloss_order 读不动 {fn}: {ex}")
def _sense_set(s):
    return frozenset(x.strip().lower() for x in _re.split(r"[,;/]", s or "") if x.strip())

# 释义意义复查 gloss_audit_out/*.json -> {id:en},{id:zh}（重写释义集，作为 en/zh 的基底）
meaning_en = {}; meaning_zh = {}
for fn in _glob.glob(f"{BASE}/gloss_audit_out/*.json"):
    try:
        for e in json.load(open(fn, encoding="utf-8")):
            wid = str(e.get("id"))
            if (e.get("en") or "").strip(): meaning_en[wid] = e["en"].strip()
            if (e.get("zh") or "").strip(): meaning_zh[wid] = e["zh"].strip()
    except Exception as ex:
        print(f"  ⚠ gloss_audit 读不动 {fn}: {ex}")
if meaning_en or meaning_zh:
    print(f"释义意义复查: en {len(meaning_en)} 词，zh {len(meaning_zh)} 词")

# 中文释义按英文顺序对齐：zh_order_out/*.json -> {id: zh}
zh_order = {}
for fn in _glob.glob(f"{BASE}/zh_order_out/*.json"):
    try:
        for e in json.load(open(fn, encoding="utf-8")):
            if e.get("id") is not None and (e.get("zh") or "").strip():
                zh_order[str(e["id"])] = e["zh"].strip()
    except Exception as ex:
        print(f"  ⚠ zh_order 读不动 {fn}: {ex}")
def _zh_sense_set(s):
    return frozenset(x.strip() for x in _re.split(r"[；;、]", s or "") if x.strip())
_zo_ok = 0; _zo_skip = 0
def _apply_zh_order(wid, zh):
    global _zo_ok, _zo_skip
    z = zh_order.get(str(wid))
    if not z:
        return zh
    if _zh_sense_set(z) == _zh_sense_set(zh):   # 只调顺序、义项集合一致才采纳
        _zo_ok += 1; return z
    _zo_skip += 1; return zh

# 补缺失名词性别 gender_out/*.json -> {id: 'm'|'f'}
gender_fix = {}
for fn in _glob.glob(f"{BASE}/gender_out/*.json"):
    try:
        for e in json.load(open(fn, encoding="utf-8")):
            if e.get("id") is not None and e.get("g") in ("m", "f"):
                gender_fix[str(e["id"])] = e["g"]
    except Exception as ex:
        print(f"  ⚠ gender_fix 读不动 {fn}: {ex}")
if gender_fix:
    print(f"名词性别补缺: {len(gender_fix)} 词")

# 阴性形 formF_out/*.json -> {id: 阴性书写形}
form_f = {}
for fn in _glob.glob(f"{BASE}/formF_out/*.json"):
    try:
        for e in json.load(open(fn, encoding="utf-8")):
            if e.get("id") is not None and (e.get("f") or "").strip():
                form_f[str(e["id"])] = e["f"].strip()
    except Exception as ex:
        print(f"  ⚠ formF 读不动 {fn}: {ex}")
if form_f:
    print(f"阴性形 formF: {len(form_f)} 词")
_go_ok = 0; _go_skip = 0
def _apply_gloss_order(wid, en):
    global _go_ok, _go_skip
    g = gloss_order.get(str(wid))
    if not g:
        return en
    if _sense_set(g) == _sense_set(en):   # 只调顺序、义项集合一致才采纳（防 LLM 改写/丢义）
        _go_ok += 1; return g
    _go_skip += 1; return en

# 命令式（impératif）：从présent规则推导 tu/nous/vous 三形（含反身 -toi/-nous/-vous）
_IMP_IRREG = {"être": ["sois", "soyons", "soyez"], "avoir": ["aie", "ayons", "ayez"],
              "savoir": ["sache", "sachons", "sachez"], "vouloir": ["veuille", "veuillons", "veuillez"]}
_IMP_SKIP = {"falloir", "pleuvoir", "neiger", "geler", "bruiner", "tonner", "pouvoir"}
_IMP_SUBJ = _re.compile(r"^(je|tu|ils|elles|il|elle|on|nous|vous)\s+", _re.I)
_IMP_REFL = _re.compile(r"^(me|te|se|nous|vous|m'|t'|s')\s*", _re.I)
def _make_imperatif(fr, present):
    if fr in _IMP_SKIP:
        return None
    if fr in _IMP_IRREG:
        return _IMP_IRREG[fr]
    if not present or len(present) < 5:
        return None
    refl = fr.startswith("se ") or fr.startswith("s'")
    def bare(f, drop_s):
        f = _IMP_SUBJ.sub("", f, count=1)
        if refl:
            f = _IMP_REFL.sub("", f, count=1)
        f = f.strip()
        if drop_s and _re.search(r"(es|as)$", f):    # -er 型：tu 形去末尾 s（parle, va）
            f = f[:-1]
        return f
    tu, nous, vous = bare(present[1], True), bare(present[3], False), bare(present[4], False)
    if not (tu and nous and vous):
        return None
    if refl:
        tu, nous, vous = tu + "-toi", nous + "-nous", vous + "-vous"
    return [tu, nous, vous]

vocab = []
for wid, w in sorted(sk.items(), key=lambda kv: kv[1]["rank"]):
    e = enr.get(wid, {})
    etym = e.get("etym", {"from": "", "text": ""})
    rec = {
        "id": wid,
        "rank": w["rank"],
        "fr": w["fr"],
        "ipa": e.get("ipa", ""),
        "pos": w["pos"],
        "en": _apply_gloss_order(wid, meaning_en.get(wid, w["en"])),
        "zh": _apply_zh_order(wid, clean(meaning_zh.get(wid, e.get("zh", "")))),
        "etym": {"from": clean(etym.get("from", "")), "text": clean(etym.get("text", ""))},
        "examples": [
            {"fr": clean(x.get("fr", "")), "en": clean(x.get("en", "")), "target": clean(x.get("target", ""))}
            for x in e.get("examples", []) if x.get("fr")
        ],
    }
    if w.get("gender"):
        rec["gender"] = w["gender"]
    elif w["pos"] == "noun" and wid in gender_fix:   # 补缺失名词性别
        rec["gender"] = gender_fix[wid]
    if wid in form_f:
        rec["formF"] = form_f[wid]            # 阴性书写形（adj/人称名词）
    if wid in etym_hooks:
        rec["etym"]["hook"] = etym_hooks[wid]
    if wid in cog_map:
        zh_senses = [s.strip() for s in re.split(r"[；;、]", rec["zh"]) if s.strip()]
        warn_set = set(warn_map.get(wid, []))
        kept = [s for s in zh_senses if s in warn_set]      # 同源词不覆盖的义项（精确匹配 zh）
        covered = [s for s in zh_senses if s not in warn_set]
        cf, ce = cogfr_map.get(wid), cogen_map.get(wid)
        # 差异标注必须：法/英括号都能还原原词，且括号"外"共享词干一致
        marks_ok = bool(cf and ce and _valid_mark(cf, rec["fr"]) and _valid_mark(ce, cog_map[wid])
                        and _shared(cf) and _shared(cf) == _shared(ce))
        if wid in _ov:
            # 人工覆盖：完全信任，不走任何丢弃守卫（如 étage→stage 这种假朋友拼写钩子）
            rec["cog"] = cog_map[wid]
            if cf and ce and _valid_mark(cf, rec["fr"]) and _valid_mark(ce, cog_map[wid]):
                rec["cogFr"] = cf
                rec["cogEn"] = ce
            if kept:
                rec["cogWarn"] = kept
        elif zh_senses and not covered:
            _cog_dropped += 1            # 同源词不覆盖任何义项 → 假朋友
        elif marks_ok:
            rec["cog"] = cog_map[wid]
            rec["cogFr"] = cf
            rec["cogEn"] = ce
            if kept:
                rec["cogWarn"] = kept
        else:
            # 标注自相矛盾：若 fr 与同源词仍有明显词干重叠，保留同源词、差异交前端兜底算法；
            # 否则（如 écrire/scribe 这种只剩词源关系的）整条丢弃
            ratio, sh = _affix_overlap(rec["fr"], cog_map[wid])
            if sh >= 3 and ratio >= 0.5:
                rec["cog"] = cog_map[wid]
                if kept:
                    rec["cogWarn"] = kept
                _cog_algomark += 1
            else:
                _cog_badmark += 1
    if wid in conj:
        cj = dict(conj[wid])
        _imp = _make_imperatif(w["fr"], cj.get("Présent"))
        if _imp:
            cj["Impératif"] = _imp
        rec["conj"] = cj
    if wid in cluster_map:
        rec["cluster"] = cluster_map[wid]
    # 注意：quiz 不进 data.js（太大），只进 vocab.db，前端按需查
    vocab.append(rec)

_cog_final = sum(1 for r in vocab if r.get("cog"))
print(f"同源词最终保留: {_cog_final} 条（假朋友丢弃 {_cog_dropped}，标注矛盾无重叠丢弃 {_cog_badmark}，算法兜底 {_cog_algomark}）")

if gloss_order:
    print(f"释义重排（主义在前）: 采纳 {_go_ok}，跳过(义项集合不符) {_go_skip}")
if zh_order:
    print(f"中文释义对齐英文: 采纳 {_zo_ok}，跳过(义项集合不符) {_zo_skip}")
# ---- 写 data.js ----
POS_LABELS = {"noun":"N","verb":"V","adj":"ADJ","adv":"ADV","prep":"PRÉP",
              "conj":"CONJ","pron":"PRON","det":"DÉT","interj":"INTERJ",
              "expr":"EXPR","other":"—"}
PRONOUNS = ["je","tu","il","nous","vous","ils"]
out = f"{BASE}/vocab-app/data.js"
with open(out, "w", encoding="utf-8") as f:
    f.write("/* B2 French vocab — 5000 mots (généré). schema: id,fr,ipa,pos,gender?,en,zh,etym,examples[],conj? */\n")
    f.write("window.VOCAB = ")
    json.dump(vocab, f, ensure_ascii=False, separators=(",", ":"))
    f.write(";\n")
    f.write("window.POS_LABELS = " + json.dumps(POS_LABELS, ensure_ascii=False) + ";\n")
    f.write("window.PRONOUNS = " + json.dumps(PRONOUNS, ensure_ascii=False) + ";\n")
sz = os.path.getsize(out)

# ---- 写 SQLite 规范库 ----
db = f"{BASE}/vocab.db"
if os.path.exists(db): os.remove(db)
c = sqlite3.connect(db)
c.executescript("""
CREATE TABLE words(id INTEGER PRIMARY KEY, rank INTEGER, fr TEXT, ipa TEXT, pos TEXT,
                   gender TEXT, en TEXT, zh TEXT, etym_from TEXT, etym_text TEXT, cog TEXT);
CREATE TABLE examples(word_id INTEGER, idx INTEGER, fr TEXT, en TEXT, target TEXT);
CREATE TABLE conj(word_id INTEGER, tense TEXT, person INTEGER, form TEXT);
CREATE TABLE quiz(word_id INTEGER, idx INTEGER, f TEXT, s TEXT, en TEXT, a TEXT, alts TEXT, form TEXT, slot TEXT);
""")
for r in vocab:
    c.execute("INSERT INTO words VALUES(?,?,?,?,?,?,?,?,?,?,?)",
              (int(r["id"]), r["rank"], r["fr"], r["ipa"], r["pos"], r.get("gender"),
               r["en"], r["zh"], r["etym"].get("from",""), r["etym"].get("text",""), r.get("cog")))
    for i, ex in enumerate(r["examples"]):
        c.execute("INSERT INTO examples VALUES(?,?,?,?,?)",
                  (int(r["id"]), i, ex["fr"], ex["en"], ex["target"]))
    for tense, forms in r.get("conj", {}).items():
        for p, form in enumerate(forms):
            c.execute("INSERT INTO conj VALUES(?,?,?,?)", (int(r["id"]), tense, p, form))
# 小测验题库进 DB（不进 data.js）
for wid, qs in quiz_map.items():
    for i, q in enumerate(qs):
        c.execute("INSERT INTO quiz VALUES(?,?,?,?,?,?,?,?,?)",
                  (int(wid), i, q["f"], q["s"], q["en"], q["a"],
                   json.dumps(q.get("alts", []), ensure_ascii=False), q.get("form"), q.get("slot")))
c.execute("CREATE INDEX idx_quiz_word ON quiz(word_id)")
c.commit()
nw = c.execute("SELECT COUNT(*) FROM words").fetchone()[0]
nex = c.execute("SELECT COUNT(*) FROM examples").fetchone()[0]
ncj = c.execute("SELECT COUNT(*) FROM conj").fetchone()[0]
nqz = c.execute("SELECT COUNT(*) FROM quiz").fetchone()[0]
c.close()

print(f"data.js: {len(vocab)} 词, {sz//1024} KB -> vocab-app/data.js")
print(f"vocab.db: words={nw}, examples={nex}, conj={ncj}, quiz={nqz}")
