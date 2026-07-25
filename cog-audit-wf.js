export const meta = {
  name: 'cog-audit',
  description: '同源词复审：删假朋友/无用同形，给无 cog 的词补明显有用的同源桥（Haiku，避开 Sonnet 限额）',
  phases: [
    { title: 'Plan', detail: '导出全词 cog_audit_batch/' },
    { title: 'Audit', detail: '一批一 agent 判 keep/drop/set' },
  ],
}

const DIR = '/Users/wangsijie/Develop/projects/french/vocabulary'
let A = args
if (typeof A === 'string') { try { A = JSON.parse(A) } catch (e) { A = {} } }
A = A || {}

const COUNT = { type: 'object', additionalProperties: false, required: ['batches'],
  properties: { batches: { type: 'integer' } } }
const WRITTEN = { type: 'object', additionalProperties: false, required: ['written'],
  properties: { written: { type: 'integer' } } }

phase('Plan')
let N = A.batches
if (!N) {
  const plan = await agent(
    `用 python3 从 ${DIR}/vocab.db 取【所有】词 id,fr,pos,en,zh,cog（cog 可能为空），每 80 个写一个 JSON 数组到 ${DIR}/cog_audit_batch/b{序号}.json（序号 0 起，先建目录）。返回 {batches:<批数>}。`,
    { label: 'plan', phase: 'Plan', schema: COUNT })
  N = (plan && plan.batches) || 0
}
log(`cog-audit: ${N} 批`)
if (!N) return { batches: 0 }

const PROMPT = `读 ${DIR}/cog_audit_batch/b{GI}.json —— 数组 {id,fr,pos,en,zh,cog}。cog = 当前给该法语词配的【英文同源词】(记忆桥)，可能为空。
逐词判断，只输出【需要改】的词：
【有 cog 但该删 → action "drop"】① 假朋友：英文 cog 的意思和该法语词不同（对照 en/zh），如 concurrentiel 的 cog=concurrent（英文 concurrent=同时的，≠竞争的）；② 和法语词【完全同形】且毫无新信息（如 contingent↔contingent）；③ 牵强/无关。
【无 cog 但可补 → action "set"】仅当有一个【明显有用】的英文同源词：真实英文词、意思和该法语词相符、拼写看得出同源、且和法语词【不同形】到值得提示。给 cog（英文词）+ cogFr（法语词差异标注，如 c[oura]nt）+ cogEn（英文词差异标注，如 c[urre]nt）。拿不准就别动。
【好的 cog、或无明显同源的词】→ 不要输出。
铁律：宁缺毋滥，只动有把握的。写 JSON 数组 [{id, action:"drop"|"set", cog?, cogFr?, cogEn?}] 到 ${DIR}/cog_audit_out/b{GI}.json（Write 工具）。返回 {written:<条数>}。`

phase('Audit')
const idxs = (A.only && A.only.length) ? A.only : Array.from({ length: N }, (_, i) => i)
const res = await parallel(idxs.map(gi => () =>
  agent(PROMPT.replace(/\{GI\}/g, gi),
    { label: `audit:b${gi}`, phase: 'Audit', schema: WRITTEN, agentType: 'Explore', model: 'haiku' })
    .then(r => (r && r.written) || 0)
))
const total = res.filter(Boolean).reduce((a, b) => a + b, 0)
log(`cog-audit: ${idxs.length} 批 → ${total} 处改动`)
return { batches: idxs.length, changes: total }
