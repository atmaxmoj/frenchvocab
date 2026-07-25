# B2 补词 Wave — Handoff（给便宜 agent 独立执行）

你要把 ~300 个 B2 漏词灌进法语词汇 deck。一条流水线，7 步，每步验证。所有命令在
`/Users/wangsijie/Develop/projects/french/vocabulary/`（下称 ROOT）下运行。coverage/ 是子目录。

**本波状态**：Step 1 已完成。300 词已选好，ids 6795–7094，在 `coverage/seed_wave.json` + `coverage/seed_mini.json`。
从 Step 2 开始。（要跑新一波：先做 Step 1。）

规则用词固定，不换同义词。gloss = 释义。bundle = 一个词的完整数据对象。

---

## Step 1 — 选词（本波已做，跳过）

命令：`cd ROOT/coverage && python3 select_wave.py`
产出：`seed_wave.json`（全字段）+ `seed_mini.json`（agent 读这个）。
校验动词能变位：`ROOT/../.venv/bin/python -c "import json;from verbecc import Conjugator;cg=Conjugator(lang='fr');[cg.conjugate(w['fr']) for w in json.load(open('ROOT/coverage/seed_wave.json')) if w['pos']=='verb']"`
坏 lemma（缺陷动词/异体/专名）加进 `select_wave.py` 顶部的 `BLOCKLIST`，再重跑 select。

---

## Step 2 — enrich（便宜 agent 做这步）

1. 清空 `ROOT/coverage/enrich_stage/`。
2. 把 `seed_mini.json`（300 词）切成批。每批 ~50 词。写成 `enrich_stage/slice_0.json` … `slice_5.json`。
3. 每批喂一个 agent。每个 agent 读它那片，产出 50 个 bundle，写成 `enrich_stage/enr_batch_<i>.json`（JSON 数组）。

**bundle 结构（每词一个）**：
```json
{"id":"6795","fr":"natte","pos":"noun","en":"<英文释义>","ipa":"/nat/","zh":"<中文释义>",
 "etym":{"from":"lat.","text":"Du latin <em>X</em>, « 义 ».","hook":{"roots":"<中文·富>","why":"<中文·记忆钩>"}},
 "examples":[{"fr":"<法语句>","en":"<英译>","target":"natte"},{"fr":"<法语句>","en":"<英译>","target":"natte"}],
 "formF":"<阴性形 或 \"\">","cog":"<英语近似词 或 \"\">","cogWarn":["<可选·中文差异>"]}
```

### gloss 铁律（en 和 zh 都遵守 — 这些是这个 deck 最重要的规则）
1. **en 和 zh 里禁出现任何法语词**。尤其禁词本身的反身式/变化形。法语固定搭配只能进 zh 的说明，**绝不进 en**。（错例：`to soar (s'élancer)` — 把答案印在题面上。）
2. **禁 `=` 号**。禁「French phrase = English」格式。
3. **多个同义译词用逗号或分号平列**。不塞括号。不用斜杠 `/` 分隔同义词（斜杠只在括号内表"或"，如 `(milk/juice)`）。
4. **括号只做消歧**。当一个英文译词单拎出来、学习者第一反应≠法语义时，加短 context 收紧。例：run→`print run`、wings→`stage wings`、iron→`to iron (clothes)`。不用括号堆同义词、不塞法语、不写解释性长句。
5. **北美英语优先**。NA 和英式并存时，NA 打头。例：lay out 先于 mark out；sweater 先于 jumper；flashlight 先于 torch。
6. **粗口/俚语保留**。但英语硬种族蔑称打码：写 `the n-word` 或 `[racial slur]`，不拼出 negro/nigger。法语词本身留。
7. **禁裸同形歧义 gloss**（别只写 minutes/show/grip）。en 和 zh 的义项集合要对齐（同样几个义）。

### 各字段要求
- **ipa**：标准法语，斜杠包。
- **etym.from**：来源语言缩写。lat. / lat. vulg. / gr. / frq.（法兰克）/ germ. / ar. / it. / esp. / angl. / néerl. / onom. / dériv. / npr.。
- **etym.text**：一句法语，`Du latin <em>X</em>, « 义 ».` 句式，词根包 `<em>`。**只有 etym.text 用 `<em>`。**
- **etym.hook.roots 和 why**：中文。**纯文本，禁任何 HTML，禁 `<em>`**。roots 要"富"：①词源链（真实拉丁/希腊/法兰克词形）②词根拆解逐素给义 ③2–4 个真同源英语词（锚定）④核心义/意象。why：讲语义如何演变到今义 / 记忆钩。参见 `ROOT/ETYM_HOOK_SPEC.md`。
  - 富样例：travailler — roots:`travailler ← 通俗拉丁 tripaliare（用 tripalium 折磨）← tri-（三）+ palus（桩）= 三桩刑具。palus 在英语=impale、pale。` why:`「工作」来自「受刑」——农奴劳动是苦役，苦受→苦干→劳作。`
- **examples**：正好 2 条。每条 `{fr,en,target}`。target 是词本身，逐字（或自然变化形）出现在 fr 里。两句不同场景。地道 B2。
- **formF**（阴性形）：性数会变的形容词给阴性（optimal→optimale, paternel→paternelle）；人称/职业/动物名词给阴性（joaillier→joaillière, débiteur→débitrice, lion→lionne）；物件/抽象/épicène（dentiste/-logue/-iste）/不变形词/动词/副词 → `""`。
- **cog**（必产此字段）：有拼写相近+义相同的英语词就填（associatif→associative）；纯语义不相近或只有生僻同根词 → `""`。假朋友填 cog + cogWarn（中文说差异）。"有的词就没有"是正常。

**enrich 自检**（写完每批过一遍）：字段全、id 对、examples target 在句、hook.roots 够富、人称名词有 formF、**en/zh 无法语无 `=`、roots 无 `<em>`、同义词无斜杠**。

---

## Step 3 — 合入

1. 改 `ROOT/coverage/validate_merge.py` 顶部 `TAG = "b2_w5"`（本波标识，下波递增）。
2. 运行：`cd ROOT/coverage && python3 validate_merge.py`。
3. 它自动校验 + 合入：skeleton(en/gender/formF)、`enrich_out/batch_new_<TAG>.json`、`etym_hook_out/new_<TAG>.json`、`formF_out/new_<TAG>.json`、`cognate_out/batch_new_<TAG>.json`（cog 有才写）。
4. 报 `ERRORS: 0` 才算过。WARNINGS 里 "target not in ex" 多是变化形误报，看一眼确认是真变化形即可。

---

## Step 4 — 变位

`cd ROOT && ../.venv/bin/python build_conj.py`
**必须用 french/.venv 的 python**（系统 verbecc 被 numpy2 弄坏）。报 "失败/跳过 0 个" 才算过。

---

## Step 5 — build + 闸门 + 出题

1. `cd ROOT && python3 build_datajs.py`（产 data.js + vocab.db）。
2. 闸门：`python3 coverage/word_complete.py`。**必须最终 0 不完整**。此时会报新词缺 quiz + audio（正常，后面补）。同时看有没有 gender/formF 边角要补：
   - 名词缺 gender → 手动在 skeleton 补（épicène/兼性人称名词默认 m；同形异义如 poêle/moule 看 gloss 挑主义的性）。
   - 形容词误报 formF（其实不变形，如 in/multimédia）→ 加进 `coverage/word_complete.py` 的 `INVARIABLE_ADJ`。
   - 动词形误标 noun（如 sors/pleure）→ 在 skeleton 把 pos 改 interj。
   - 补完重跑 build + gate。
3. 槽位：`python3 quizslot_gen.py`（给每词生成 `quizslot_w/<id>.json` 出题规格）。
4. **出题（这步最贵，用便宜 agent + 大批）**：
   - 每个 agent 读一批 `quizslot_w/<id>.json`（**建议一 agent 管 20–30 词**，别一词一 agent），按规格给每个槽出正好 2 题，写成 `quizslot_out/g<round>_<n>.json`。round 从 **6012** 起（每波递增）。
   - 出题规则见 `ROOT/QUIZ_GEN_PROMPT.md`（照抄槽 key、句里恰好一个 `___`、答案唯一或 alts 收全、变位题填光动词形不带主语、别串词）。
   - 出完再 `python3 build_datajs.py` 把题合进库。
5. 出题若有 agent 失败：查哪些 id 没写进 `quizslot_out/g<round>_*.json`，单独补跑那几个 id。

---

## Step 6 — 音频（三音色缺一不可）

`cd ROOT`，逐个跑（工具默认超时 2 分钟，用长 timeout）：
- `python3 prebuild_tts.py denise`（词头+冠词形+例句+变位+阴性形）
- `python3 prebuild_tts.py henri`（裸词，Réviser 男声 — 别漏）
- `python3 prebuild_tts.py aria`（英文释义）

每个跑到"待生成 0"。三个都是 `失败 0`。（自动带 formF 阴性形 + 阴性冠词形音频。）

---

## Step 7 — 收尾验证

1. `python3 coverage/word_complete.py` → **0 不完整**。
2. `python3 quiz_check.py <round>` → 完全合格 ≥ ~98%。残差 ~1.7% 可接受。
3. **忽略这类 checker 误报**：defective/être/reflexive 动词（bruire、renaître、repentir、pavaner 之类）——verbecc 给的参考才是错的，生成的 "suis xx" 反而对。
4. 汇报本波词数 + 抽查（gloss 无污染 / etym 富度 / formF / cog 命中 ~60–70% 属正常）。

---

## 老词 gloss 修正（不走这条流水线）

要改已有词的 en/zh，写进 `ROOT/gloss_audit_out/user_fix.json`（数组，每项 `{"id":int,"en":"...","zh":"..."}`），再 `build_datajs.py`。build 时 user_fix 覆盖生成值。改完若 en 变了要重跑 `prebuild_tts.py aria`（英文音频哈希变了）。

## 已知 BLOCKLIST（select_wave.py 顶部，别灌回来）
bruir（=bruire 异体）、accroire（缺陷动词）、gaspard（人名噪声）、mac（品牌噪声）。逮到新噪声往里加。

## 参照
- `ROOT/ETYM_HOOK_SPEC.md` — 词源钩子规范（富样例）。
- `ROOT/QUIZ_GEN_PROMPT.md` — 出题规范。
- gap 源：`ROOT/coverage/gap_B2.tsv`。剩 ~1750 词（本波后 ~1450）。
