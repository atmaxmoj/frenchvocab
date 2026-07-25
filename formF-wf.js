export const meta = {
  name: 'formF',
  description: '补阴性形：形容词 + 人称名词的阴性书写形（Sonnet 生成 → 逐词校验轮）',
  phases: [
    { title: 'Gen', detail: '一批一 agent 生成阴性形' },
    { title: 'Verify', detail: '同批校验、纠错、补漏，写文件' },
  ],
}

const DIR = '/Users/wangsijie/Develop/projects/french/vocabulary'
let A = args
if (typeof A === 'string') { try { A = JSON.parse(A) } catch (e) { A = {} } }
A = A || {}
const N = A.batches || 63

const ITEMS = { type: 'object', additionalProperties: false, required: ['items'],
  properties: { items: { type: 'array', items: {
    type: 'object', additionalProperties: false, required: ['id', 'f'],
    properties: { id: { type: 'integer' }, f: { type: 'string' } } } } } }
const WRITTEN = { type: 'object', additionalProperties: false, required: ['written'],
  properties: { written: { type: 'integer' } } }

const RULES = `规则：
【形容词 adj】给阴性书写形：grand→grande、beau→belle、heureux→heureuse、premier→première、gentil→gentille、fou→folle、blanc→blanche、long→longue、frais→fraîche、doux→douce、faux→fausse、ancien→ancienne、cruel→cruelle、complet→complète、actif→active、menteur→menteuse、protecteur→protectrice。阴阳【同形】(rouge/jeune/facile 等 -e 结尾，以及 même/leur/chaque 等不可变) → 不收录。
【人称名词 noun】给阴阳成对的阴性形：acteur→actrice、ami→amie、chien→chienne、époux→épouse、directeur→directrice、infirmier→infirmière、roi→reine、héros→héroïne。épicène(enfant/élève/touriste/artiste 同形) 或【不指人】(moteur 引擎、bonheur、saison) → 不收录。
只收录【确有且不同形】的阴性形，阴性形必须是真实法语词形，拿不准就不收录。`

const GEN = `读取 ${DIR}/formF_batch/b{GI}.json —— 数组 {id,fr,pos,en}。给出每个词的阴性书写形。\n${RULES}\n返回 {items:[{id, f:<阴性形>}]}（只含有不同阴性形的词）。`

phase('Gen')
const idxs = (A.only && A.only.length) ? A.only : Array.from({ length: N }, (_, i) => i)
const res = await pipeline(idxs,
  (gi) => agent(GEN.replace(/\{GI\}/g, gi),
    { label: `gen:b${gi}`, phase: 'Gen', schema: ITEMS, agentType: 'Explore', model: 'sonnet' })
    .then(r => ({ gi, items: (r && r.items) || [] })),
  (prev) => agent(
    `校验阴性形。先读 ${DIR}/formF_batch/b${prev.gi}.json（该批全部词 {id,fr,pos,en}）。下面是上一轮生成的候选阴性形。\n` +
    `逐词核对：① 候选阴性形拼写【正确】吗？错就改对；② 有没有【该收录却漏了】的词（按规则补上）；③ 有没有【不该收录】的（同形/不指人，删掉）。\n${RULES}\n` +
    `把【最终】结果写成 JSON 数组 [{id, f}] 到 ${DIR}/formF_out/b${prev.gi}.json（用 Write 工具）。返回 {written:<条数>}。\n\n候选:\n${JSON.stringify(prev.items)}`,
    { label: `verify:b${prev.gi}`, phase: 'Verify', schema: WRITTEN, agentType: 'Explore', model: 'sonnet' })
    .then(r => (r && r.written) || 0)
)
const total = res.filter(Boolean).reduce((a, b) => a + b, 0)
log(`formF: ${idxs.length} 批 → ${total} 词有阴性形`)
return { batches: idxs.length, words: total }
