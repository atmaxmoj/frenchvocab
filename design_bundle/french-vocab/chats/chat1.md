# 法语词汇速记系统

_Started 2026-06-03 03:40 UTC_

---

## User

我要最大努力speedrun法语b2，我现在要弄一个自己顺手的背单词的，我的背单词的方法不一样，我喜欢大量看而不使劲背，这样我每天能背下300+个词，词源不需要你定，但是我需要例句，阴阳性 etymology，conjugations这些东西，还有内置个日历，掩盖模式（只有法语或者英语）还有抽词考试，就是按照我的计划kao wo，按照艾宾浩斯遗忘曲线考我

## Assistant

_[tool: questions_v2]_

好的，我先理解一下：你想要一个B2法语刷词工具，自己粘词，让工具自动配上例句、阴阳性、词源、变位，再加日历追踪 + 遮罩浏览 + 艾宾浩斯抽考。

在动手前问几个关键问题，让我做出来的东西真的顺手：

## User

Questions answered:
- daily_target: 600
- word_input: 我会让Claude code写死在数据库里
- ai_enrich: 也有数据库
- card_layout: 可切换密度
- mask_modes: 全部要
- test_format: 认识 / 模糊 / 不认识 三键自评（类似Anki）
- calendar_view: 下面三个都要：热力图 + 月历 + streak
- conjug_tenses: 全部要
- device: 随便，自用的这个是
- theme_pref: Sepia（日光泛黄，护眼）
- extra_features: 发音播放（TTS）, 什么是会不会依靠考试来记我

## Assistant

_[tool: snip]_

_[tool: update_todos]_

_[tool: list_files]_

_[tool: read_file]_

_[tool: list_files]_

_[tool: grep]_

_[tool: read_file]_

_[tool: read_file]_

_[tool: write_file]_

Got it. Now I have the design system in hand. Let me build this out.

System I'll commit to:
- **Sepia theme**: warm yellow paper canvas (#f4ecd8), sepia ink (#5b4636), gold accent for masculine, dusty rose for feminine.
- **Type**: EB Garamond for French (display + body) — proper book feel for a vocab-as-reading tool.
- **Layout**: top nav (LUCERNA · vocabulaire wordmark + tabs), three views: Browse / Review / Calendar.
- **POS color underlines** from design system (`--pos-noun`, `--pos-verb`...).
- **Gender system**: re-purpose German gender tokens (`--gender-der` for `le`, `--gender-die` for `la`).
- **SR scheduler**: Ebbinghaus-ish steps `[10min, 1d, 2d, 4d, 7d, 14d, 30d, 90d, 180d]`. 不认识 resets to 0; 模糊 stays; 认识 advances.

Let me start writing.

_[tool: write_file]_

Now the vocab database. I'll seed ~80 quality B2-level entries spanning all POS, with full conjugations on the top verbs and concise etymology throughout.

_[tool: write_file]_

Now the React components — shared primitives, Browse view, Review view, Calendar view, and the app shell.

_[tool: write_file]_

_[tool: write_file]_

_[tool: write_file]_

_[tool: write_file]_

Now the app shell with seeded demo history (so the empty calendar isn't barren on first open) and the index.html.

_[tool: write_file]_

_[tool: write_file]_

_[tool: show_html]_

_[tool: done]_

_[tool: str_replace_edit]_

_[tool: done]_

_[tool: fork_verifier_agent]_

做好了。整个工具是一个 React 单文件应用，标题 **Lucerne · vocabulaire — B2**，用 Lucerna 设计系统的 sepia 暖纸色基调。

**三个主视图：**
- **Parcourir** — 词卡瀑布流。密度可切换（Aérée / Normale / Dense），mask 模式六选（无 / FR遮罩 / EN遮罩 / 例句完型 / 词尾遮罩 / 全部 hover 揭示）。点击卡片展开词源 + 完整变位表。Filter 按 SR 状态（Neufs / Apprentissage / Révision / Acquis）。
- **Réviser** — 一次一张大卡，Anki 风格 **Je ne sais pas / Flou / Je connais** 三键，键盘 `Espace`/`1·2·3`/`J·K·L`/`P`(TTS)/`C`(展开变位)。按艾宾浩斯 step `[10min, 1d, 2d, 4d, 7d, 14d, 30d, 90d, 180d, 365d]` 推进。
- **Calendrier** — 53周热力图 + 月历（每天显示新增+复习）+ streak 大数字 + 未来30天到期柱状预览 + 词库全局 stats。

**已经种下90天演示数据**，所以一打开热力图、streak、月历都是实在的。右上角设置菜单可以一键 **「Tout effacer」** 清空，或 **「Recharger la démonstration」** 重置。

**词库** — 80个 B2 词，覆盖 12 个全变位动词（présent/passé composé/imparfait/futur/conditionnel/subjonctif）+ 25个名词带阴阳性 + 形容词/副词/连词/惯用语，每个都有词源、IPA、例句、中英翻译。

**Claude Code 接力点**：所有 100+ 词条都在 `data.js` 里一个数组，schema 在文件顶部注释清楚了，让 Claude Code 按同样格式扩到几千条就行。Storage 用 `localStorage`，键 `fr_b2_sr_v1` 和 `fr_b2_settings_v1`。

下一步如果你想：
- 加导入/导出（CSV / Anki .apkg）
- 主题切换器（washi / dark / kanagawa 都在设计系统里现成）
- 按主题打 tag 然后子集学习（你的 extras 里勾的「按主题分组」我没做，等你确认要再加）
- 听写模式 / 选择题模式（现在只有自评）

## User

Verifier agent check completed

## Assistant

_[tool: str_replace_edit]_

_[tool: str_replace_edit]_

Both fixes:

_[tool: done]_

修好了：
- **Réviser 空白** — `.fade-in` 现在 baseline `opacity: 1`，动画从 `0` 起步（不强制 `both`），即使浏览器没启动动画也能正常显示。
- **月历空格的 "0"** — 把 `||` 链条改成显式 `> 0` 比较，0 不再泄漏成文本节点。

