#!/usr/bin/env python3
"""预生成 TTS 音频。用法: python prebuild_tts.py <voice>
  voice = denise (女法, -> vocab-app/audio/, 含变位)
        | henri  (男法, -> vocab-app/audio/henri/, 词头+例句)
        | aria   (女英, -> vocab-app/audio/en/, 英文释义 enGloss，供 Sens 跟读)
文本: 法语音色=词头+例句(+变位合读)；英语音色=enGloss 释义。
文件名 = FNV-1a(文本)。断点续、跳过已存在。前端 speak()/speakEn() 用同样哈希取文件。
"""
import asyncio, json, os, re, sqlite3, sys
import edge_tts

BASE = os.path.dirname(os.path.abspath(__file__))
VOICES = {  # key: (voice, dir, include_conj, is_en, words_only)
    "denise": ("fr-FR-DeniseNeural", os.path.join(BASE, "vocab-app", "audio"), True, False, False),
    "henri":  ("fr-FR-HenriNeural",  os.path.join(BASE, "vocab-app", "audio", "henri"), False, False, True),
    "remy":   ("fr-FR-RemyMultilingualNeural", os.path.join(BASE, "vocab-app", "audio", "remy"), False, False, True),
    "aria":   ("en-US-AriaNeural",   os.path.join(BASE, "vocab-app", "audio", "en"), False, True, False),
}
key = sys.argv[1] if len(sys.argv) > 1 else "denise"
VOICE, AUDIO, INCLUDE_CONJ, IS_EN, WORDS_ONLY = VOICES[key]
os.makedirs(AUDIO, exist_ok=True)
CONC = 10

def fnv1a(s: str) -> str:
    h = 0xcbf29ce484222325
    for b in s.encode("utf-8"):
        h ^= b; h = (h * 0x100000001b3) & 0xFFFFFFFFFFFFFFFF
    return format(h, "016x")

# 英文释义规整：必须与前端 components.jsx 的 enGloss 完全一致（哈希才对得上）
_NOUN_SKIP = {"a", "an", "the", "some", "any", "this", "that", "these", "those", "his", "her",
             "its", "their", "my", "your", "our", "one", "two", "no", "not", "if", "whether",
             "there", "here", "before", "after", "well", "less", "more"}
_VERB_SKIP = {"being", "footstep", "footing", "can", "may", "must", "shall", "will", "might"}
def en_gloss(pos, en):
    if not en:
        return ""
    strip = lambda s: re.sub(r"\s*\([^)]*\)", "", s).strip()   # 去掉括号收紧说明，与前端 speakEn 一致
    is_noun, is_verb = pos == "noun", pos == "verb"
    if not is_noun and not is_verb:
        return strip(en)
    out = []
    for seg in re.split(r"([,;]\s*)", en):
        if not seg or re.match(r"^[,;]", seg):
            out.append(seg); continue
        t = seg.lstrip()
        if not t:
            out.append(seg); continue
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

con = sqlite3.connect(os.path.join(BASE, "vocab.db"))
texts = set()
if IS_EN:
    for pos, en in con.execute("SELECT pos, en FROM words WHERE en<>''"):
        g = en_gloss(pos, (en or "").strip())
        if g.strip():
            texts.add(g)
else:
    for (fr,) in con.execute("SELECT fr FROM words WHERE fr<>''"):
        texts.add(fr.strip())
    if not WORDS_ONLY:                       # 只生成词级音频时跳过例句
        for (fr,) in con.execute("SELECT fr FROM examples WHERE fr<>''"):
            texts.add(fr.strip())
    # 名词带冠词朗读："le/la/l' + 词"，必须与前端 frSpoken 完全一致（元音/h → l'）
    _VOWEL = re.compile(r"^[aeiouàâäéèêëîïoôöùûüœ]", re.I)
    for fr, gender in con.execute("SELECT fr, gender FROM words WHERE gender IN ('m','f')"):
        fr = (fr or "").strip()
        if not fr:
            continue
        if _VOWEL.match(fr) or fr[:1].lower() == "h":
            texts.add("l'" + fr)
        else:
            texts.add(("le " if gender == "m" else "la ") + fr)
    if INCLUDE_CONJ:
        # 每个 (word, tense) 的 6 个形式按 person 排序后用 ", " 合读 —— 与前端 conj[t].join(', ') 一致
        rows = con.execute("SELECT word_id,tense,person,form FROM conj ORDER BY word_id,tense,person").fetchall()
        groups = {}
        for wid, tense, person, form in rows:
            groups.setdefault((wid, tense), []).append((person, form))
            texts.add(form)                       # 单个变位形式（如 "tu parviens"）
        for k, lst in groups.items():
            lst.sort()
            texts.add(", ".join(f for _, f in lst))  # 整组合读
    # 阴性形音频：bare 阴性形 + 名词带阴性冠词（与前端 femSpoken 一致），供阴阳两读
    import glob as _g
    posg = {str(r[0]): (r[1], r[2]) for r in con.execute("SELECT id,pos,gender FROM words")}
    for fn in _g.glob(os.path.join(BASE, "formF_out", "*.json")):
        try:
            data_ff = json.load(open(fn, encoding="utf-8"))
        except Exception:
            continue
        for e in data_ff:
            f = (e.get("f") or "").strip()
            if not f:
                continue
            texts.add(f)
            pos, gender = posg.get(str(e.get("id")), (None, None))
            if pos == "noun" and gender in ("m", "f"):
                texts.add(("l'" + f) if (_VOWEL.match(f) or f[:1].lower() == "h") else ("la " + f))
con.close()
texts = sorted(texts)

todo = [(t, os.path.join(AUDIO, fnv1a(t) + ".mp3")) for t in texts]
todo = [(t, p) for t, p in todo if not (os.path.exists(p) and os.path.getsize(p) > 0)]
print(f"[{key}/{VOICE}] 文本 {len(texts)}；待生成 {len(todo)} -> {AUDIO}", flush=True)

# 发音覆盖：单个字母被 TTS 读成字母名（y→"i grec"、代词 y 其实是 /i/）。文件仍按原词哈希存，只换合成文本。
PRONOUNCE_AS = {"y": "i"}
done = [0]; fails = []
sem = asyncio.Semaphore(CONC)
async def synth(text, path):
    speak = PRONOUNCE_AS.get(text, text)
    async with sem:
        for attempt in range(3):
            try:
                await edge_tts.Communicate(speak, VOICE).save(path)
                if os.path.getsize(path) > 0:
                    done[0] += 1
                    if done[0] % 1000 == 0: print(f"  …{done[0]}/{len(todo)}", flush=True)
                    return
            except Exception as e:
                if attempt == 2: fails.append((text[:30], str(e)[:50]))
                await asyncio.sleep(1.5 * (attempt + 1))
async def main():
    await asyncio.gather(*(synth(t, p) for t, p in todo))
if todo: asyncio.run(main())
n = len([x for x in os.listdir(AUDIO) if x.endswith(".mp3")])
print(f"[{key}] 完成：本次生成 {done[0]}，失败 {len(fails)}，目录现有 {n}", flush=True)
for f in fails[:10]: print("  失败:", f, flush=True)
