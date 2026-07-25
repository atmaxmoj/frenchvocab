export const meta = {
  name: 'gloss-order',
  description: '把多义词的英文释义按【最常用义在前】重排（保留所有义项，只调顺序）',
  phases: [{ title: 'Reorder', detail: '一批一 agent，读 gloss_batch/b{i}.json 重排写 gloss_order_out/' }],
}

const DIR = '/Users/wangsijie/Develop/projects/french/vocabulary'
let A = args
if (typeof A === 'string') { try { A = JSON.parse(A) } catch (e) { A = {} } }
A = A || {}
const N = A.batches || 29

const WRITTEN = { type: 'object', additionalProperties: false, required: ['written'],
  properties: { written: { type: 'integer' } } }

const PROMPT = `读取 ${DIR}/gloss_batch/b{GI}.json —— 一个数组，每项 {id, fr, pos, en, zh}。
任务：把每个词的英文释义 en 按【最常用 / 最核心义在前】重新排序。
【铁律】① 只调整义项顺序，【不增不删、不改写】任何义项的措辞；② 分隔符原样保留（原来用逗号就用逗号、分号就用分号，保持同样的分隔风格）；③ zh 仅供你判断该词主义是什么，别动它、也别输出它；④ 若原顺序已是主义在前，就原样返回。
判断"最常用义"：结合该法语词在现代法语中的高频用法 + zh 中文释义的首义。例 fête「节日；庆典；派对」→ 主义是 holiday/celebration，已在前则不动。
逐条返回，并写成 JSON 数组 [{id, en:<重排后的英文释义串>}] 到 ${DIR}/gloss_order_out/b{GI}.json（用 Write 工具）。返回 {written:<条数>}。`

phase('Reorder')
// A.only=[i...] 只重跑指定批次（补漏）；否则全跑 0..N-1
const idxs = (A.only && A.only.length) ? A.only : Array.from({ length: N }, (_, i) => i)
const res = await parallel(idxs.map(gi => () =>
  agent(PROMPT.replace(/\{GI\}/g, gi),
    { label: `reorder:b${gi}`, phase: 'Reorder', schema: WRITTEN, agentType: 'Explore', model: A.model || 'haiku' })
    .then(r => (r && r.written) || 0)
))
const total = res.filter(Boolean).reduce((a, b) => a + b, 0)
log(`gloss-order: ${N} 批 → ${total} 词重排`)
return { batches: N, words: total }
