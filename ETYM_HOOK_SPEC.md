# 词源钩子 — 生成规范（Etymology Hook Spec）

每个词条的 `etym` 字段权威规范。**enrich 生成 prompt 必须按此写**（agent 产出的 `etym` 直接决定 app 里"词源"框的质量）。灌新词时把本文件的"富样例"贴进 agent prompt，别再产出"ad + dere"那种一行裸拆。

## 数据结构

```json
"etym": {
  "from": "lat.",                 // 来源语言缩写
  "text": "Du latin additio, de addere « ajouter ».",   // 一句法语词源（前端次要显示）
  "hook": {
    "roots": "……",                // ← 【核心】app 词源框主要显示这个，必须"富"
    "why":   "……"                 // 记忆钩 / 语义演变说明
  }
}
```

- **`from`**：来源语言缩写。常用：`lat.`(拉丁) `lat. vulg.`(通俗拉丁) `gr.`(希腊) `germ.`/`frq.`(法兰克·日耳曼) `ar.`(阿拉伯) `it.`(意大利) `esp.`(西班牙) `angl.`(英语) `néerl.`(荷兰) `celt.`(凯尔特) `npr.`(专名) `onom.`(拟声) `dériv.`(法语内部派生)。
- **`text`**：一句**法语**词源，`Du latin X, de Y « 义 ».` 句式；词根用 `<em>…</em>` 包裹（如 `<em>additio</em>`）。简短即可，这是次要显示。
- **`hook.roots`** 和 **`hook.why`**：**中文**，是学习者真正读的东西，要求见下。

## `hook.roots` —— 必须"富"（四要素）

用中文，一段话（2–5 句），把下面四样串起来：

1. **词源链**：`词 ← [来源语言] 源词 ← [更古的根]`，**点出真实的拉丁/希腊/法兰克词形**（不是只写英文词缀）。
2. **词根拆解**：把源词拆成词素，逐个给义（如 `tri-（三）+ palus（桩）`、`af-（=ad-，朝向）+ fect-（做）`）。
3. **英语同源桥**：给 2–4 个**同根英语词**，点明共享的词根（如 palus → impale/pale；pot- → potent/potential/omnipotent）。学习者靠英语锚定。
4. **核心义/意象**：一句话点出贯穿各义项的核心动作或画面。

## `hook.why` —— 记忆钩 / 语义说明

用中文一段，做下面之一或组合：
- 解释**语义如何从词根演变到今义**（尤其反直觉的，如 travailler「受刑→劳作」）；
- 若多义，说明**几个义项如何从同一核心裂开**（如 pouvoir 动词"能"↔名词"权力"，对照英语 power 同走一路）；
- 给一个**生动的记忆画面**。
不要只重复 roots，要补充"为什么"和"怎么记"。

## ✅ 富样例（照这个水平写）

- **travailler** — roots：`travailler ← 通俗拉丁 tripaliare（用 tripalium 折磨/拷打）← tri-（三）+ palus（桩·柱）= 三根桩组成的刑具。核心词根 palus 在英语里是 impale（穿刺）、pale（栅栏桩）。` why：`「工作」竟来自「受刑折磨」——中世纪农奴的劳动是苦役，tripalium 是套在囚犯身上的三桩架，苦受→苦干→劳作，意义随历史温和化。`
- **pouvoir** — roots：`pouvoir ← 拉丁通俗语 *potere ← 古典拉丁 posse = potis（有能力的）+ esse（是）=「能够成立」→ 能做某事。词根 pot- 在英语里留下 potent、potential、omnipotent。` why：`动词 pouvoir = can；名词 le pouvoir 是同一步引申「能做事的能力→权力」，跟英语 power 一词双义走同一条路。`
- **fenêtre** — roots：`fenêtre ← 拉丁 fenestra =「窗、开口」（来源有争议，主流认为借自伊特鲁里亚语），核心意象「让光透进来的洞口」。英语同根：fenestration（开窗术）、defenestrate（de-出 + fenestra = 扔出窗外）。` why：`窗户就是窗户，无复杂引申；现代 fenêtre 也指电脑「视窗」，平行英语 window 的双义。`

## ❌ 反面（太薄，别这样）

- **addition**（曾经）— roots：`ad（向）+ dere（放/给）` why：`把数字加上去就是加法，也是结账单`
  - 病：没词源链(没点出拉丁 additio/addere)、没英语同源桥(add/addendum/edition)、roots 只一行裸拆。**这就是"像开玩笑"的原因。**
  - 应改成：roots：`addition ← 拉丁 additio ← addere =「加上、添上」= ad-（向、往）+ dare/-dere（给、放）。词根 dare「给」在英语里是 add（加）、addendum（附加项）、edition（版本←e-出+给=印出来发行）。` why：`核心是「把 X 放/给到某处上面」→ 数字往上加 = 加法；账单是把各项「加总」出来给你 = 结账单。同一个「累加」动作，数学义和餐厅义一脉相承。`

## 生成注意

- 词源链要**真实准确**，别编造词形；不确定的来源用"主流认为/来源有争议"。
- 英语同源桥要是**真同根**（别硬凑假朋友）。
- 全中文讲解 + 法语/拉丁词形；符合本 deck 的 house style（字面拆解 + 中英对照 + 记忆钩）。
- `text`(法语) 简短、`roots`(中文) 要富——app 主显 `roots`。

相关：[[QUIZ_GEN_PROMPT.md]] 是题库生成规范；本文件是词源钩子规范。灌词流程见 memory `vocab-coverage-audit`。
