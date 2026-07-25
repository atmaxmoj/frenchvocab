export const meta = {
  name: 'etym-hook',
  description: '词源记忆钩子：一词一 agent 生成（词根拆解+为什么是这个义+英语桥+同根词），再分组审计写文件',
  phases: [
    { title: 'Generate', detail: '每个词一个 agent 写钩子' },
    { title: 'Audit', detail: '分组审词源准确性 + 写文件' },
  ],
}

const DIR = '/Users/wangsijie/Develop/projects/french/vocabulary'
let A = args
if (typeof A === 'string') { try { A = JSON.parse(A) } catch (e) { A = {} } }
A = A || {}
const round = A.round || 0
// chunk 文件名列表（每个 ≤4096 个 id，避开 VM 边界数组上限）；或单个 chunk；或直接 ids
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
log('etym round ' + round + ' · ' + ids.length + ' 词')

const HOOK = {
  type: 'object', additionalProperties: false,
  required: ['id', 'roots', 'why'],
  properties: {
    id: { type: 'integer' },
    roots: { type: 'string' },
    why: { type: 'string' },
    en: { type: 'string' },
    family: { type: 'array', items: { type: 'string' } },
  },
}
const GENOUT = { type: 'object', additionalProperties: false, required: ['id', 'roots', 'why'],
  properties: HOOK.properties }
const WRITTEN = { type: 'object', additionalProperties: false, required: ['written'],
  properties: { written: { type: 'integer' } } }

const GEN = `为这个法语词写一个【词源记忆钩子】，帮助一个【能读英文的中文母语者】把词义串起来、记住。读 etym_w/{ID}.json（含 fr/pos/en/zh/etym_from/etym_text）。

风格范例（travers）：
- roots: "travers ← 拉丁 transversus = trans-（横/穿过）+ versus（转 · vers-）= 横转过去"
- why: "核心义 = 横/斜/穿过。「缺点·过失」是引申：斜→歪→偏离正道→性格缺点(un travers)、行为出错(de travers)。"
- en: "英语 across/transverse = 「横」这层；「缺点」义英语没有(flaw/fault)，是法语从「斜」独有引申。"
- family: ["vers-（转）","inversion","bouleversement","envers","divers"]

要求：
- roots：词根/词缀拆解 + 来源（拉丁/希腊/法兰克等）+ 每个词素中文括注；尽量点出一个英语里也存在的词根。
- why：为什么是这些意思——尤其【多义词】反直觉的义项如何从核心义引申。1–3 句，简洁。
- en：【英语桥】——相近/同源的英文词（帮助记忆）或平行直觉；英语若无对应义，点明。这条对能读英文的人最关键。
- family：同根、学习者可能认识的词（法语为主，3–6 个，可含词根本身如 "vers-（转）"）。
- 别生硬堆术语；目标是"让我联系得上、记得住"。【绝不编造词源】——拿不准就基于 etym_text 老实写、宁可简单（family 可省、en 可省）。
返回 {id, roots, why, en, family}。`

phase('Generate')
// 单次 parallel() 上限 4096，分批跑
const GENBATCH = 1500
const items = []
for (let off = 0; off < ids.length; off += GENBATCH) {
  const sub = ids.slice(off, off + GENBATCH)
  const gen = await parallel(sub.map(id => () =>
    agent(GEN.replace('{ID}', id),
      { label: `gen:${id}`, phase: 'Generate', schema: GENOUT, agentType: 'Explore', model: 'sonnet' })
      .then(h => h ? { ...h, id } : null)
  ))
  items.push(...gen.filter(Boolean))
  log(`gen ${items.length}/${ids.length}`)
}

phase('Audit')
const GRPW = 25
const groups = []
for (let i = 0; i < items.length; i += GRPW) groups.push(items.slice(i, i + GRPW))
const res = await parallel(groups.map((grp, gi) => () =>
  agent(
    `审计这组词源钩子：① 词源【不能编造】，与已知词源/etym_text 一致，拿不准就简化；② roots 词素拆解正确；③ en 英语桥的同源/相近词真的相关（错就删 en 或改成平行直觉）；④ family 同根可信（错的删）；⑤ why 简洁、引申逻辑成立；⑥ id 不变。\n` +
    `改好后写成 JSON 数组 [{id, roots, why, en?, family?}] 到 ${DIR}/etym_hook_out/g${round}_${gi}.json（用 Write 工具）。\n` +
    `【JSON 必须合法·铁律】文本里要引用某个词时一律用中文引号「」或（），【绝对禁止】在字符串内用 ASCII 双引号 " 或反斜杠 \\\\（它们会破坏 JSON）。写完心里过一遍：能被 JSON.parse 解析。返回 {written:<条数>}。\n\nItems:\n${JSON.stringify(grp)}`,
    { label: `audit:r${round}:${gi}`, phase: 'Audit', schema: WRITTEN, model: 'sonnet' })
    .then(r => ({ n: (r && r.written) || 0 }))
))
const total = res.filter(Boolean).reduce((s, r) => s + r.n, 0)
log(`etym round ${round}: ${items.length} 词 → ${total} 条`)
return { round, words: items.length, total }
