#!/usr/bin/env python3
"""词条完整性闸门 —— 结构上保证"加词不丢 compartment"。

一个完整词条需要的 compartment（== build_datajs.py 合并的各源）：
  无条件:  fr · pos · en · zh · ipa · etym.text · etym.hook · examples(≥2) · quiz(slot 覆盖)
  按词性:  gender(noun) · conj(verb) · formF(adj/人称名词阴性)
  已查即可: cog(有同源桥 或 显式无) —— 允许为空，但须"查过"(此处仅告警，不阻断)
  可选:    cluster(一起记词组) —— 不要求
  音频:    三音色 mp3 都要在 —— denise(词头/冠词形) · henri(裸词, Réviser用) · aria(en释义)

用法:
  python3 coverage/word_complete.py            # 查全部 5000
  python3 coverage/word_complete.py 5001 5002  # 只查指定 id（loop 里查新加的那批）
退出码: 有任一必需 compartment 缺失 -> 1（可用于卡住 24h/300 生成 loop）
"""
import json, os, re, sqlite3, sys

BASE = os.path.dirname(os.path.abspath(__file__))
APP = os.path.join(BASE, "..", "vocab-app")

def load_vocab():
    txt = open(os.path.join(APP, "data.js"), encoding="utf-8").read()
    i = txt.index("window.VOCAB"); j = txt.index("window.POS_LABELS")
    seg = txt[i:j].strip(); seg = seg[seg.index("=") + 1:].rstrip().rstrip(";")
    return json.loads(seg)

def nonempty(v):
    return bool(v) and (len(v) > 0 if isinstance(v, (list, dict, str)) else True)

# ---- 音频完整性（三音色都要有；与 prebuild_tts / 前端 fnv1a 完全一致）----
def fnv1a(s):
    h = 0xcbf29ce484222325
    for b in s.encode("utf-8"):
        h ^= b; h = (h * 0x100000001b3) & 0xFFFFFFFFFFFFFFFF
    return format(h, "016x")

_VOWEL = re.compile(r"^[aeiouàâäéèêëîïoôöùûüœ]", re.I)
def frspoken(w):   # denise/Cram·Quiz 读：名词带冠词，其余裸词（= 前端 frSpoken）
    fr = (w.get("fr") or "").strip()
    if w.get("pos") == "noun" and w.get("gender") in ("m", "f"):
        if _VOWEL.match(fr) or fr[:1].lower() == "h":
            return "l'" + fr
        return ("le " if w["gender"] == "m" else "la ") + fr
    return fr

_NOUN_SKIP = {"a","an","the","some","any","this","that","these","those","his","her","its","their",
              "my","your","our","one","two","no","not","if","whether","there","here","before","after","well","less","more"}
_VERB_SKIP = {"being","footstep","footing","can","may","must","shall","will","might"}
def en_gloss(pos, en):   # aria 读的英文释义（= prebuild_tts.en_gloss / 前端 speakEn）
    if not en: return ""
    strip = lambda s: re.sub(r"\s*\([^)]*\)", "", s).strip()
    is_noun, is_verb = pos == "noun", pos == "verb"
    if not is_noun and not is_verb: return strip(en)
    out = []
    for seg in re.split(r"([,;]\s*)", en):
        if not seg or re.match(r"^[,;]", seg): out.append(seg); continue
        t = seg.lstrip()
        if not t: out.append(seg); continue
        lead = seg[:len(seg) - len(t)]
        if is_verb:
            pm = re.match(r"^(?:\([^)]*\)\s*)+", t)          # 前导括注不算动词部分（与前端 enGloss 一致）
            plead = pm.group(0) if pm else ""
            prest = t[len(plead):]
            if not prest or re.match(r"^to\s", prest, re.I) or prest.lower() in _VERB_SKIP:
                out.append(seg)
            else:
                out.append(lead + plead + "to " + prest)
            continue
        w0 = re.split(r"[\s’']", t.lower())[0]
        out.append(seg if w0 in _NOUN_SKIP else lead + "the " + t)
    return strip("".join(out))

def load_audio_sets():
    def mp3set(*parts):
        p = os.path.join(APP, "audio", *parts)
        return set(f[:-4] for f in os.listdir(p) if f.endswith(".mp3")) if os.path.isdir(p) else set()
    return {"denise": mp3set(), "henri": mp3set("henri"), "aria": mp3set("en")}

def missing_compartments(w, quiz_ids, audio=None):
    """返回该词缺失的必需 compartment 列表（空 = 完整）。"""
    miss = []
    et = w.get("etym") or {}
    pos = w.get("pos")
    fr = (w.get("fr") or "").strip().lower()
    fr_raw = (w.get("fr") or "").strip()
    checks = {
        "en":         nonempty(w.get("en")),
        "zh":         nonempty(w.get("zh")),
        "ipa":        nonempty(w.get("ipa")),
        "etym.text":  nonempty(et.get("text")),
        "etym.hook":  nonempty(et.get("hook")),
        "quiz(slot)": str(w["id"]) in quiz_ids,
    }
    # examples≥2 只对内容词(名/动/形)强制；功能词(冠/介/连/代/数/叹)按设计少例句
    if pos in ("noun", "verb", "adj"):
        checks["examples>=2"] = len(w.get("examples") or []) >= 2
    if pos == "noun": checks["gender"] = nonempty(w.get("gender"))
    if pos == "verb": checks["conj"]   = nonempty(w.get("conj"))
    # formF 只对"阴性会变形"的形容词要求：以 -e 结尾者阴阳同形；下列为已知不变形形容词
    INVARIABLE_ADJ = {"soi-disant", "chic", "sympa", "super", "extra", "marron", "orange",
                      "snob", "kaki", "sexy", "cool", "bien", "châtain", "standard", "récap", "high-tech", "pop", "in", "multimédia"}
    if pos == "adj" and not fr.endswith("e") and fr not in INVARIABLE_ADJ:
        checks["formF"] = nonempty(w.get("formF"))
    # 音频三音色：Réviser=henri(裸词) · Cram/Quiz=denise(冠词形) · 英文跟读=aria(释义)
    if audio is not None:
        checks["audio.denise"] = fnv1a(frspoken(w)) in audio["denise"]
        checks["audio.henri"]  = fnv1a(fr_raw) in audio["henri"]
        g = en_gloss(pos, (w.get("en") or "").strip())
        if g:
            checks["audio.aria"] = fnv1a(g) in audio["aria"]
    return [k for k, ok in checks.items() if not ok]

def main():
    ids = set(sys.argv[1:])
    arr = load_vocab()
    if ids:
        arr = [w for w in arr if str(w["id"]) in ids]
    db = sqlite3.connect(os.path.join(BASE, "..", "vocab.db"))
    quiz_ids = {str(r[0]) for r in db.execute(
        "SELECT DISTINCT word_id FROM quiz WHERE slot IS NOT NULL")}
    audio = load_audio_sets()

    incomplete = []
    from collections import Counter
    by_comp = Counter()
    for w in arr:
        m = missing_compartments(w, quiz_ids, audio)
        if m:
            incomplete.append((w["id"], w.get("fr"), w.get("pos"), m))
            for c in m: by_comp[c] += 1

    print(f"检查 {len(arr)} 词 · 不完整 {len(incomplete)}")
    if by_comp:
        print("按缺失 compartment：")
        for c, n in by_comp.most_common():
            print(f"  {c:14s} 缺 {n}")
    if incomplete:
        print("\n不完整词（前 40）：")
        for wid, fr, pos, m in incomplete[:40]:
            print(f"  #{wid} {fr} ({pos}) → 缺 {', '.join(m)}")
    # 告警：cog 未解决（非阻断）
    unresolved_cog = [w for w in arr if not nonempty(w.get("cog"))]
    print(f"\n(告警) 无 cog 的词: {len(unresolved_cog)}  —— 需确认是'已查无同源'而非'漏查'")
    return 1 if incomplete else 0

if __name__ == "__main__":
    sys.exit(main())
