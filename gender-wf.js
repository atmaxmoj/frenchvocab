export const meta = {
  name: 'gender-fix',
  description: '补名词缺失的阴阳性（le/la）：Sonnet 判定 → 校验轮',
  phases: [
    { title: 'Gen', detail: '一批一 agent 判性' },
    { title: 'Verify', detail: '同批校验、写文件' },
  ],
}

const DIR = '/Users/wangsijie/Develop/projects/french/vocabulary'
let A = args
if (typeof A === 'string') { try { A = JSON.parse(A) } catch (e) { A = {} } }
A = A || {}
const N = A.batches || 3

const ITEMS = { type: 'object', additionalProperties: false, required: ['items'],
  properties: { items: { type: 'array', items: {
    type: 'object', additionalProperties: false, required: ['id', 'g'],
    properties: { id: { type: 'integer' }, g: { type: 'string', enum: ['m', 'f'] } } } } } }
const WRITTEN = { type: 'object', additionalProperties: false, required: ['written'],
  properties: { written: { type: 'integer' } } }

const RULES = `给每个法语名词判定语法性别 g：'m'(阳，le/un) 或 'f'(阴，la/une)。
- 多义/双性词（如 page: la page 书页 / le page 侍童；tour: le tour 圈·轮 / la tour 塔；mode: la mode 时尚 / le mode 方式；mémoire: la mémoire 记忆 / le mémoire 论文；poste: la poste 邮局 / le poste 岗位；faux: la faux 镰刀 / le faux 赝品；somme: la somme 总额 / le somme 小睡；fin: la fin 结束 / le fin 精细）→ 取【最常用义/对照 zh 首义】对应的性别。
- 双性指人名词（juge, enfant, élève, ministre, collègue, partenaire, secrétaire, auteur, professeur…）→ 按传统引用性别取 'm'（le juge、un enfant）。
- 必须基于真实法语，每个 id 都要给 m 或 f。`

phase('Gen')
const idxs = (A.only && A.only.length) ? A.only : Array.from({ length: N }, (_, i) => i)
const res = await pipeline(idxs,
  (gi) => agent(
    `读取 ${DIR}/gender_batch/b${gi}.json —— 数组 {id,fr,en,zh}。\n${RULES}\n返回 {items:[{id, g}]}（每词都要）。`,
    { label: `gen:b${gi}`, phase: 'Gen', schema: ITEMS, agentType: 'Explore', model: 'sonnet' })
    .then(r => ({ gi, items: (r && r.items) || [] })),
  (prev) => agent(
    `校验名词性别。先读 ${DIR}/gender_batch/b${prev.gi}.json（该批全部 {id,fr,en,zh}）。下面是候选性别，逐词核对（尤其多义/双性词按主义取性别），改对、补齐每一个 id。\n${RULES}\n` +
    `把【最终】结果写成 JSON 数组 [{id, g}] 到 ${DIR}/gender_out/b${prev.gi}.json（Write 工具）。返回 {written:<条数>}。\n\n候选:\n${JSON.stringify(prev.items)}`,
    { label: `verify:b${prev.gi}`, phase: 'Verify', schema: WRITTEN, agentType: 'Explore', model: 'sonnet' })
    .then(r => (r && r.written) || 0)
)
const total = res.filter(Boolean).reduce((a, b) => a + b, 0)
log(`gender-fix: ${idxs.length} 批 → ${total} 词`)
return { batches: idxs.length, words: total }
