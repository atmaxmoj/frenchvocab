export const meta = {
  name: 'gloss-zh',
  description: '把中文释义按已排序的英文顺序对齐（自带取数→重排→校验→写文件）',
  phases: [
    { title: 'Plan', detail: '取多义词、切批写 zh_batch/' },
    { title: 'Gen', detail: '一批一 agent 对齐中文顺序' },
    { title: 'Verify', detail: '同批校验、写 zh_order_out/' },
  ],
}

const DIR = '/Users/wangsijie/Develop/projects/french/vocabulary'
let A = args
if (typeof A === 'string') { try { A = JSON.parse(A) } catch (e) { A = {} } }
A = A || {}

const COUNT = { type: 'object', additionalProperties: false, required: ['batches'],
  properties: { batches: { type: 'integer' } } }
const ITEMS = { type: 'object', additionalProperties: false, required: ['items'],
  properties: { items: { type: 'array', items: {
    type: 'object', additionalProperties: false, required: ['id', 'zh'],
    properties: { id: { type: 'integer' }, zh: { type: 'string' } } } } } }
const WRITTEN = { type: 'object', additionalProperties: false, required: ['written'],
  properties: { written: { type: 'integer' } } }

// === Plan：取数+切批（不依赖外部脚本，agent 自己跑）===
phase('Plan')
let N = A.batches
if (!N) {
  const plan = await agent(
    `准备数据。运行 python3 从 ${DIR}/vocab.db 取所有【中文释义有 ≥2 个义项】的词（zh 按 「；」「;」「、」 切分后非空段 ≥2），字段 id,fr,en,zh，每 30 个写一个 JSON 数组到 ${DIR}/zh_batch/b{序号}.json（序号从 0 开始，先确保该目录存在）。en 直接用库里的（已是最常用义在前）。完成后返回 {batches:<生成的批数>}。`,
    { label: 'plan', phase: 'Plan', schema: COUNT })
  N = (plan && plan.batches) || 0
}
log(`gloss-zh: ${N} 批待处理`)
if (!N) return { batches: 0, words: 0 }

const RULES = `任务：把每个词的中文释义 zh 的【义项顺序】重排成与英文 en 的义项顺序【一一平行】（en 第1义对应的中文排第1，第2义排第2…）。
【铁律】① 只调整 zh 义项的【先后顺序】，绝不增删、不改写任何中文义项的字眼；② 分隔符原样保留（「；」还是「；」，「、」还是「、」）；③ zh 义项数与 en 不一致时，让主义(en 第1义)对应的中文排最前，其余按 en 顺序跟上；④ 已对齐就原样返回。`

const GEN = `读取 ${DIR}/zh_batch/b{GI}.json —— 数组 {id, fr, en, zh}（en 已"最常用义在前"）。\n${RULES}\n返回 {items:[{id, zh:<重排后的中文释义串>}]}。`

phase('Gen')
const idxs = (A.only && A.only.length) ? A.only : Array.from({ length: N }, (_, i) => i)
const res = await pipeline(idxs,
  (gi) => agent(GEN.replace(/\{GI\}/g, gi),
    { label: `gen:b${gi}`, phase: 'Gen', schema: ITEMS, agentType: 'Explore', model: 'sonnet' })
    .then(r => ({ gi, items: (r && r.items) || [] })),
  (prev) => agent(
    `校验中文释义对齐。先读 ${DIR}/zh_batch/b${prev.gi}.json（该批全部 {id,fr,en,zh}）。下面是候选重排,逐词核对：中文义项顺序是否真和英文 en 平行?有没有改字眼/增删义项(必须只调顺序)?改对。\n${RULES}\n` +
    `把【最终】结果写成 JSON 数组 [{id, zh}] 到 ${DIR}/zh_order_out/b${prev.gi}.json（Write 工具）。返回 {written:<条数>}。\n\n候选:\n${JSON.stringify(prev.items)}`,
    { label: `verify:b${prev.gi}`, phase: 'Verify', schema: WRITTEN, agentType: 'Explore', model: 'sonnet' })
    .then(r => (r && r.written) || 0)
)
const total = res.filter(Boolean).reduce((a, b) => a + b, 0)
log(`gloss-zh: ${idxs.length} 批 → ${total} 词`)
return { batches: idxs.length, words: total }
