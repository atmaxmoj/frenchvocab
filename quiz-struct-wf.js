export const meta = {
  name: 'quiz-struct',
  description: '结构化题库：按每词的槽位清单（变位/义项/冠词/配合）逐槽出 2 题，槽位写进 prompt 保证覆盖',
  phases: [
    { title: 'Generate', detail: '一词一 agent，按槽位清单出题' },
    { title: 'Audit', detail: '分组校验 + 写文件' },
  ],
}

const DIR = '/Users/wangsijie/Develop/projects/french/vocabulary'
let A = args
if (typeof A === 'string') { try { A = JSON.parse(A) } catch (e) { A = {} } }
A = A || {}
const round = A.round || 0
const chunkNames = A.chunks && A.chunks.length ? A.chunks : (A.chunk != null ? [A.chunk] : [])
let ids = (A.ids && A.ids.length) ? A.ids.slice() : []
for (const cn of chunkNames) {
  const r = await agent(
    `读取文件 ${DIR}/quiz_chunks/${cn}.json，原样返回其中的整数数组。返回 {ids:[<整数...>]}`,
    { label: 'plan:' + cn, phase: 'Generate', agentType: 'Explore', model: 'haiku',
      schema: { type: 'object', additionalProperties: false, required: ['ids'],
        properties: { ids: { type: 'array', items: { type: 'integer' } } } } })
  ids.push(...((r && r.ids) || []))
}
log('quiz-struct round ' + round + ' · ' + ids.length + ' 词')

const QITEM = {
  type: 'object', additionalProperties: false, required: ['id', 'qs'],
  properties: {
    id: { type: 'integer' },
    qs: { type: 'array', items: {
      type: 'object', additionalProperties: false, required: ['slot', 'f', 's', 'en', 'a'],
      properties: {
        slot: { type: 'string' }, f: { type: 'string' },
        s: { type: 'string' }, en: { type: 'string' }, a: { type: 'string' },
        alts: { type: 'array', items: { type: 'string' } }, form: { type: 'string' },
      },
    } },
  },
}
const WRITTEN = { type: 'object', additionalProperties: false, required: ['written'],
  properties: { written: { type: 'integer' } } }

// === 生成 prompt（记录见仓库 QUIZ_GEN_PROMPT.md，二者保持一致）===
const GEN = `为这个法语词出填空题。先读 ${DIR}/quizslot_w/{ID}.json —— 含 fr/pos/en/zh 和一个 slots 数组。

【铁律·覆盖】为 slots 里【每一个槽】出【正好 2 道】题，绝不漏槽，也【绝不多出 slots 之外的考点】（spec 里没有的槽一律不出）。题数 = 2 × 槽数。每题对象：slot(照抄 key)、f(照抄 facet)、s(完整自然法语句、恰好一个 ___)、a(___ 确切答案)、en(准确英译)、alts(真正可互换的其它正确答案，否则 [])、form(动词题填时态名)。

【各 facet 出题规则】
A. facet="tense"（变位）：a = 该槽 "target"（【光动词形】，如 "cherche" / "ai cherché" / "est allé"），【绝不带主语代词】。句子里【必须写出主语】（主语属该槽 "persons" 里的某个人称，可用代词或同人称的名词），___ 只填动词形。例：槽 target="a cherché" persons=["il/elle/on"] → s="Hier, mon frère ___ ses clés partout." a="a cherché"。两题用不同主语/语境（都属该人称）。être 复合时态按句子主语做性数配合（"Elle ___"→"est allée"），配合后的形式就是 a。
B. facet="subj"（虚拟式，每动词仅此 1 槽、出 2 题）：句子含虚拟式触发 + 【从句里写明主语】，如 "Il faut que tu ___ ." / "Je veux qu'elle ___ ."；a = 该主语的虚拟式动词形（光形，不带主语）。两题用【不同人称 + 不同触发词】。【禁用 "tenir à que"】（语法错，要用 "tenir à ce que"）；别用锁不住人称的无人称结构（"Il est important ___" 不行，必须 "...que tu ___"）。
C. facet="sense"：句子精确锁定该槽 "sense_zh" 对应的那一个义项（对照 zh），不串到该词其它义；a = 该法语词。【只考词条 zh 里列出的义项，别自创义项（如 aussi 不要考"因此"义）】。若该义项有更地道的近义词会让答案不唯一（dire 讲故事→其实 raconter 更地道、faire 工厂制造→fabriquer/produire、voir 电视→regarder），就【换一个目标词才最地道的语境】（dire la vérité、faire ses devoirs…），或把真可互换的近义词放进 alts。
D. facet="gender"（名词冠词）：挖空冠词，a 填 le/la/l'/les/un/une/du/de la/des 之一，体现该词性别。facet="agree"（形容词配合）：作该槽 gender(mp/f/fp) 配合，a 填配合后形式。

【质量硬规则——高频翻车点】
1. 句子【合逻辑合常识】：无时间矛盾、无语义荒谬。
2. 【答案唯一，或 alts 收全】：给定 en 语境下 ___ 唯一最佳填法应是 a。真能互换的全进 alts（都算对）：cela↔ça、donc↔ainsi、également↔aussi、savoir↔connaître、par↔avec、voir↔regarder 等。能靠改写句子排除其它词的，优先改写让 a 唯一。
3. 【搭配地道 + 用对词】：用该词在该语境最自然的搭配（看电视=regarder、讲故事=raconter）；抽象"善"用名词 le bien 不用 le bon。目标词在某搭配不地道，就换它地道的语境。
4. 【绝不串词】：a 必须是【目标词】或其变化形，绝不写成别的词（vouloir≠espérer、voir≠regarder 当槽是 voir 时）。
5. 不要倒装/反身冲突。
6. 【省音】：主语 je/que 只在【元音开头】的动词形前用 j'/qu'；辅音开头用 "Je"/"Il"（"Je commencerai" 不是 "J'commencerai"）。
7. 【条件式 Conditionnel】：假设句【只用 "Si + 主语 + imparfait"】（Si tu avais…）；【禁 si+présent、禁 si+plus-que-parfait】（后者要配条件式过去时，与本槽不符）。别用 "À ta place, tu…"（该习语主语必须是 je）。
10. 【passé composé 用"一次性/完成"语境】，别配持续时段（"pendant tout le discours" 这种状态持续→该用 imparfait）；状态动词（sembler/être/paraître）尤其注意。
8. 【频率副词】：toujours/souvent/jamais/déjà 等放在【简单时态动词之后】（"boit toujours" 不是 "toujours boit"）。
9. 【副词不能放反身代词和动词之间】（"se lève toujours" 不是 "toujours se lève"）。

返回 {id, qs:[...]}。再确认：每槽正好 2 题、slot 照抄 key、不串词、答案唯一或 alts 收全。`

phase('Generate')
const GENBATCH = 800
const items = []
for (let off = 0; off < ids.length; off += GENBATCH) {
  const sub = ids.slice(off, off + GENBATCH)
  const gen = await parallel(sub.map(id => () =>
    agent(GEN.replace('{ID}', id),
      { label: `gen:${id}`, phase: 'Generate', schema: QITEM, agentType: 'Explore', model: 'sonnet' })
      .then(r => r && r.qs && r.qs.length ? { id, qs: r.qs } : null)
  ))
  // 每小批立即审计+写盘（防中途崩了全丢）
  const fresh = gen.filter(Boolean)
  phase('Audit')
  const GRPW = 3   // 写文件组要小：动词 78 题/词，组太大会撑爆 32k 输出上限
  const groups = []
  for (let i = 0; i < fresh.length; i += GRPW) groups.push(fresh.slice(i, i + GRPW))
  const gi0 = Math.floor(off / GENBATCH) * 1000
  await parallel(groups.map((grp, gi) => () =>
    agent(
      `审计这组结构化填空题并写文件。逐题检查：① s 是完整法语句、恰好一个 ___；② en 翻译准确；③ tense 题的 a 必须与该词该槽 target 的精确变位形一致（错就改对）；④ sense 题语境锁定对应义项；⑤ gender/agree 形态正确；⑥ slot 字段保持原样、每槽 2 题（缺了就补、与覆盖对齐）。\n` +
      `改好后写 JSON 数组 [{id, qs:[{slot,f,s,en,a,alts?,form?}]}] 到 ${DIR}/quizslot_out/g${round}_${gi0 + gi}.json（Write 工具）。返回 {written:<题数>}。\n\nItems:\n${JSON.stringify(grp)}`,
      { label: `audit:r${round}:${gi0 + gi}`, phase: 'Audit', schema: WRITTEN, model: 'sonnet' })
      .then(r => ({ n: (r && r.written) || 0 }))
  ))
  items.push(...fresh)
  log(`已处理 ${items.length}/${ids.length} 词`)
}
return { round, words: items.length }
