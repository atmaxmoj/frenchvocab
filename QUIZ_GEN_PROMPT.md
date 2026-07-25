# 结构化题库 — 生成 Prompt（记录）

`quiz-struct-wf.js` 的 `GEN` 常量权威记录。**改 prompt 两处保持一致。** 规则来自每批质检（`quiz-review-wf.js`）反馈逐条沉淀。

## 设计要点（v2，2026-06-18 重构）
槽位生成 `quizslot_w/{id}.json`：
- **变位 tense**：每个时态按【不同的光动词形】去重，每个形一槽，`target`=光动词形（**不含主语**，如 `cherche`/`ai cherché`/`est allé`）。`persons`=共享该形的人称。
- **虚拟式 subj**：每动词**仅 1 槽**（不枚举人称），出 2 题。无精确 target。
- sense（每义项）、gender（名词冠词）、agree（形容词性数）。
- 全库 ~52k 槽 → ~104k 题（2/槽）。

## 铁律·覆盖
为每个槽出正好 2 题，不漏不多。每题：`slot`(照抄 key)、`f`、`s`(完整句、一个 `___`)、`a`、`en`、`alts`、`form`(动词题填时态名)。

## 各 facet 规则
- **tense**：`a`=`target`（光动词形，**绝不带主语**）；句子**必须写出主语**（属该槽 persons），`___` 只填动词形。être 复合时态按句子主语做性数配合（Elle→est allée），配合后即 a。
- **subj**（1 槽/动词，2 题）：句子含虚拟式触发 + **从句写明主语**（`Il faut que tu ___`、`Je veux qu'elle ___`）；a=该主语的虚拟式形（光形）。两题不同人称+不同触发词。**禁 `tenir à que`**（须 `tenir à ce que`）；禁锁不住人称的无人称结构。
- **sense**：句子锁定该槽 `sense_zh` 单一义项，不串义；a=该词。
- **gender**：挖冠词。**agree**：形容词配合后形式。

## 质量硬规则（高频翻车点，逐条来自质检）
1. 句子合逻辑合常识（无时间矛盾/语义荒谬）。
2. **答案唯一 或 `alts` 收全**：真可互换全进 alts——cela↔ça、donc↔ainsi、également↔aussi、savoir↔connaître、par↔avec、voir↔regarder…
3. 搭配地道 + 用对词：regarder la télé、raconter une histoire、抽象善=le bien(非 le bon)。
4. **绝不串词**：a 必是目标词或其变化形（vouloir≠espérer）。
5. 不要倒装/反身冲突。

## 历史教训
- v1（带主语代词的 target）质检暴露：①答案带 il/ils 但句子主语阴性(la pluie→elle) ②虚拟式按 6 人称无法锁定 ③answer 不唯一。→ v2 改为光动词形 + 主语留句中 + 虚拟式 1 槽。
- 写文件 `GRPW=3`（动词题多，组大撑爆 32k 输出）。质检按 ~150 题/组（防 agent 跑飞）。
- checker `tense_eq`：剥主语 + 忽略尾部性数(allé/allée)；tense 答案若带主语代词→flag(应光形)。
