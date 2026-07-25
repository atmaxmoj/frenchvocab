export const meta = {
  name: 'gloss-audit',
  description: '释义意义复查：补漏的常用义、剔除生僻义（只改有明显问题的词，Haiku）',
  phases: [
    { title: 'Plan', detail: '导出全词 gloss_audit_batch/' },
    { title: 'Audit', detail: '一批一 agent 审释义集' },
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
    `用 python3 从 ${DIR}/vocab.db 取【所有】词 id,fr,pos,en,zh，每 80 个写一个 JSON 数组到 ${DIR}/gloss_audit_batch/b{序号}.json（序号 0 起，先建目录）。返回 {batches:<批数>}。`,
    { label: 'plan', phase: 'Plan', schema: COUNT })
  N = (plan && plan.batches) || 0
}
log(`gloss-audit: ${N} 批`)
if (!N) return { batches: 0 }

const PROMPT = `读 ${DIR}/gloss_audit_batch/b{GI}.json —— 数组 {id,fr,pos,en,zh}。en=英文释义，zh=中文释义（各义项用逗号/分号/、隔开）。
复查每词的释义集，只输出【有明显问题】需要改的词：
① 漏了【常用义】：现代法语该词高频常用的意思没列出 → 补上。
② 含【生僻/罕用/古旧义】：明显冷门、学习者用不到的义项 → 删掉，别让它混进来误导（尤其别让冷门义排在前面）。
目标：每词释义 = 现代法语【高频常用义】，不多不少；最常用义在前；en 与 zh 一一对应平行。
【铁律·保守】只动【确有问题】的词；释义已经合理的【不要输出】。改时保持原有分隔风格（en 用逗号/分号；zh 用「；」「、」）。给【完整重写后】的 en 和 zh。
写 JSON 数组 [{id, en:<新英文>, zh:<新中文>}] 到 ${DIR}/gloss_audit_out/b{GI}.json（Write 工具）。返回 {written:<条数>}。`

phase('Audit')
const idxs = (A.only && A.only.length) ? A.only : Array.from({ length: N }, (_, i) => i)
const res = await parallel(idxs.map(gi => () =>
  agent(PROMPT.replace(/\{GI\}/g, gi),
    { label: `audit:b${gi}`, phase: 'Audit', schema: WRITTEN, agentType: 'Explore', model: 'haiku' })
    .then(r => (r && r.written) || 0)
))
const total = res.filter(Boolean).reduce((a, b) => a + b, 0)
log(`gloss-audit: ${idxs.length} 批 → ${total} 词改动`)
return { batches: idxs.length, changes: total }
