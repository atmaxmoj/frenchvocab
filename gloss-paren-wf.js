export const meta = {
  name: 'gloss-paren',
  description: '释义歧义收紧：英文释义词在英语里多义、但法语只对应其中一义 → 用括号收紧（Sonnet，保守）',
  phases: [
    { title: 'Plan', detail: '按 rank 区间导出 batch' },
    { title: 'Audit', detail: '一批一 agent 找歧义释义、加括号' },
  ],
}

const DIR = '/Users/wangsijie/Develop/projects/french/vocabulary'
let A = args
if (typeof A === 'string') { try { A = JSON.parse(A) } catch (e) { A = {} } }
A = A || {}
const LO = A.lo || 1, HI = A.hi || 160, BS = A.batch || 80

const COUNT = { type: 'object', additionalProperties: false, required: ['batches'], properties: { batches: { type: 'integer' } } }
const WRITTEN = { type: 'object', additionalProperties: false, required: ['written'], properties: { written: { type: 'integer' } } }

phase('Plan')
const plan = await agent(
  `用 python3 从 ${DIR}/vocab.db 取 rank BETWEEN ${LO} AND ${HI} 的词 id,fr,pos,en,zh，按 rank 排序，每 ${BS} 个写一个 JSON 数组到 ${DIR}/gloss_paren_batch/b{序号}.json（序号 0 起，先建目录 gloss_paren_batch 和 gloss_paren_out）。返回 {batches:<批数>}。`,
  { label: 'plan', phase: 'Plan', schema: COUNT })
const N = (plan && plan.batches) || 0
log(`gloss-paren: rank ${LO}-${HI} → ${N} 批`)
if (!N) return { batches: 0 }

const PROMPT = `读 ${DIR}/gloss_paren_batch/b{GI}.json —— 数组 {id,fr,pos,en,zh}。en=英文释义集，zh=中文释义集。
任务：找出【英文释义有歧义】的词，用括号把语义收紧。
判据：某个英文释义词/短语在英语里【本身有多个常见意思】（polysemous），而这个法语词只对应其中【一个】意思 → 学习者单看英文会误解。给那个义项加一个括号，写出限定搭配/语境，锁定到正确的意思。
范例：dicter en="to dictate, lay down" —— "lay down" 英语可指"放下/躺下/订立规则"，但 dicter 只表"订立(规则/条件)" → 改为 "to dictate, lay down (the law/terms/conditions)"。
括号里放英语典型搭配或限定词（用 / 分隔多个），让人立刻看出是哪个意思。对照 zh 判断法语到底指哪一面。
【铁律·保守】① 只改【确有歧义、会误导】的义项；本身清楚无歧义的【整词都不要输出】。② 不改变释义的真实意思，只用括号收紧；不要删/加义项。③ 不动 zh。④ 已有的对的义项原样保留，只在需要的义项后加括号。
给【完整重写后的 en】（含未改义项）。写 JSON 数组 [{id, en:<新英文>, note:<一句中文说明改了哪个词、为什么有歧义>}] 到 ${DIR}/gloss_paren_out/b{GI}.json（Write 工具）。无需改动的词不要写。返回 {written:<条数>}。`

phase('Audit')
const idxs = Array.from({ length: N }, (_, i) => i)
const res = await parallel(idxs.map(gi => () =>
  agent(PROMPT.replace(/\{GI\}/g, gi),
    { label: `paren:b${gi}`, phase: 'Audit', schema: WRITTEN, model: 'sonnet' })
    .then(r => (r && r.written) || 0)
))
const total = res.filter(Boolean).reduce((a, b) => a + b, 0)
log(`gloss-paren: ${idxs.length} 批 → ${total} 词加括号`)
return { batches: idxs.length, changes: total }
