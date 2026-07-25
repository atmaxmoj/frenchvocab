export const meta = {
  name: 'quiz-review',
  description: '题目质量复查：Sonnet 逐题读，挑出答案不唯一/句子不自然/翻译不准/义项错位的问题题',
  phases: [{ title: 'Review', detail: '每组10词一个 agent 通读挑刺' }],
}

const DIR = '/Users/wangsijie/Develop/projects/french/vocabulary'
let A = args
if (typeof A === 'string') { try { A = JSON.parse(A) } catch (e) { A = {} } }
A = A || {}
const files = A.files || []     // 形如 ['d1_0','d1_1',...]
log('质检 ' + files.length + ' 组')

const FLAGS = {
  type: 'object', additionalProperties: false, required: ['reviewed', 'flags'],
  properties: {
    reviewed: { type: 'integer' },
    flags: { type: 'array', items: {
      type: 'object', additionalProperties: false,
      required: ['fr', 'slot', 'a', 'issue', 'severity'],
      properties: {
        fr: { type: 'string' }, slot: { type: 'string' }, a: { type: 'string' },
        issue: { type: 'string' },
        severity: { type: 'string', enum: ['bad', 'minor'] },
      },
    } },
  },
}

const PROMPT = `你是法语命题质检员。读 {FILE}（一个数组，每个词含 fr/pos/en/zh 和 qs 题目数组，每题有 slot/f/s/a/en/form）。

【逐题】判断质量，只挑【真有问题】的题（别吹毛求疵）。检查：
1. 句子 s：完整、自然、地道法语，恰好一个 ___。
2. 答案唯一性【最重要】：在给定英文翻译 en 的语境下，___ 处的唯一最佳填法必须就是 a。若有别的常见法语词/形式也同样说得通（句子语境不足以排除），= 问题题。
3. 翻译 en：准确传达法语句意。
4. tense 题：a 是否真的是该 form(时态) 该人称的正确变位；句子语境是否匹配该时态/人称。
5. sense 题：句子语境是否锁定该词在本题应考的那个义项（对照 zh 的对应义），没串到别的义。
6. gender 题：冠词/性别对。 agree 题：形容词性数配合形态对。

对每个有问题的题，输出 {fr, slot, a, issue(中文一句说清毛病), severity}：
- severity="bad"：答案不唯一、变位错、翻译错、句子病句 —— 必须修。
- severity="minor"：能用但略生硬/语境偏弱。
全对就 flags:[]。返回 {reviewed:<本组题总数>, flags:[...]}。`

phase('Review')
const res = await parallel(files.map(f => () =>
  agent(PROMPT.replace('{FILE}', `${DIR}/quiz_review_in/${f}.json`),
    { label: 'review:' + f, phase: 'Review', schema: FLAGS, model: 'sonnet', agentType: 'Explore' })
))
const flags = []
let reviewed = 0
for (const r of res.filter(Boolean)) { reviewed += r.reviewed || 0; flags.push(...(r.flags || [])) }
const bad = flags.filter(f => f.severity === 'bad')
log(`复查 ${reviewed} 题，问题 ${flags.length}（bad ${bad.length} / minor ${flags.length - bad.length}）`)
return { reviewed, total_flags: flags.length, bad: bad.length, flags }
