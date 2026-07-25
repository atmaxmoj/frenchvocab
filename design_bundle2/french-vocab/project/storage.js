/* =============================================================
   SR engine + localStorage persistence
   ============================================================= */
/* global window */

(function() {
  const KEY = 'fr_b2_sr_v1';
  const SETTINGS_KEY = 'fr_b2_settings_v1';

  // Ebbinghaus-ish step intervals (in days).
  // Index advances on 'good', stays on 'hard', resets on 'again'.
  const STEPS = [
    1/144,    // 10 min  (=0.0069 d)  — learning step
    1,        // 1 d
    2,        // 2 d
    4,        // 4 d
    7,        // 7 d
    14,       // 14 d
    30,       // 30 d
    90,       // 90 d
    180,      // 6 mo
    365,      // 1 y
  ];

  const dayMs = 86400000;

  function todayKey(t) {
    const d = new Date(t || Date.now());
    return d.getFullYear() + '-' +
      String(d.getMonth()+1).padStart(2,'0') + '-' +
      String(d.getDate()).padStart(2,'0');
  }

  function loadState() {
    try {
      const raw = localStorage.getItem(KEY);
      if (!raw) return defaultState();
      const s = JSON.parse(raw);
      if (!s.cards) s.cards = {};
      if (!s.history) s.history = {}; // { 'YYYY-MM-DD': { new: 0, rev: 0, again: 0 } }
      if (!s.batches) s.batches = {};
      if (!s.cramSeen) s.cramSeen = {};
      if (!s.introducedToday) s.introducedToday = { date: todayKey(), count: 0 };
      // roll daily counter
      if (s.introducedToday.date !== todayKey()) {
        s.introducedToday = { date: todayKey(), count: 0 };
      }
      return s;
    } catch (e) {
      return defaultState();
    }
  }

  function defaultState() {
    return {
      cards: {},
      history: {},
      batches: {},                // { 'YYYY-MM-DD': [wordId, ...] } — daily cram batches
      cramSeen: {},               // { 'YYYY-MM-DD': { wordId: timesSeen } } — today's swipes per batch-day
      introducedToday: { date: todayKey(), count: 0 },
      firstSeen: Date.now(),
    };
  }

  function saveState(s) {
    try { localStorage.setItem(KEY, JSON.stringify(s)); }
    catch(e) { console.error('save failed', e); }
  }

  function loadSettings() {
    try {
      const raw = localStorage.getItem(SETTINGS_KEY);
      if (!raw) return defaultSettings();
      return Object.assign(defaultSettings(), JSON.parse(raw));
    } catch(e) { return defaultSettings(); }
  }

  function defaultSettings() {
    return {
      dailyNewTarget: 600,
      cramTarget: 2000,          // # words in a fresh daily cram batch
      density: 'normal',         // sparse | normal | dense
      maskMode: 'none',          // none | fr | en | cloze | endings | hover
      browseFilter: 'all',       // all | new | learning | review | mastered
      browseOrder: 'sequential', // sequential | shuffle
      ttsEnabled: true,
      reviewQueueSize: 60,       // max cards per review session
    };
  }

  function saveSettings(s) {
    try { localStorage.setItem(SETTINGS_KEY, JSON.stringify(s)); }
    catch(e){}
  }

  /* ------------- per-card state shape -------------
     {
       id, step, due (ms), lapses, reps, intro (ms),
       state: 'new' | 'learning' | 'young' | 'mature' | 'lapsed'
     }
  ---------------------------------------------- */
  function newCard(id) {
    return {
      id, step: 0, due: 0, lapses: 0, reps: 0, intro: null, state: 'new',
    };
  }

  function classify(c) {
    if (!c || c.reps === 0) return 'new';
    if (c.state === 'lapsed') return 'lapsed';
    if (c.step <= 1) return 'learning';
    if (c.step <= 4) return 'young';
    if (c.step <= 6) return 'mature';
    return 'mastered';
  }

  function rateCard(state, id, rating) {
    // rating: 'again' | 'hard' | 'good'
    const now = Date.now();
    let c = state.cards[id] || newCard(id);
    const isNew = c.reps === 0;
    if (isNew && !c.intro) {
      c.intro = now;
      state.introducedToday.count++;
    }
    c.reps++;

    if (rating === 'again') {
      c.lapses++;
      c.step = 0;
      c.due = now + STEPS[0] * dayMs;
      c.state = isNew ? 'learning' : 'lapsed';
    } else if (rating === 'hard') {
      // stay at current step but push due slightly
      c.step = Math.max(0, c.step);
      const interval = STEPS[c.step] * 0.85;
      c.due = now + Math.max(interval, STEPS[0]) * dayMs;
      c.state = classify(c);
    } else if (rating === 'good') {
      c.step = Math.min(STEPS.length - 1, c.step + 1);
      c.due = now + STEPS[c.step] * dayMs;
      c.state = classify(c);
    }

    state.cards[id] = c;

    // History
    const k = todayKey();
    if (!state.history[k]) state.history[k] = { new: 0, rev: 0, again: 0, hard: 0, good: 0 };
    if (isNew) state.history[k].new++;
    else state.history[k].rev++;
    state.history[k][rating] = (state.history[k][rating] || 0) + 1;

    saveState(state);
    return c;
  }

  function dueCards(state, allWords, opts) {
    // Returns { learning: [...], review: [...], newPool: [...] }
    const now = Date.now();
    const learning = [];
    const review = [];
    const newPool = [];
    for (const w of allWords) {
      const c = state.cards[w.id];
      if (!c || c.reps === 0) { newPool.push(w); continue; }
      if (c.due <= now) {
        if (c.state === 'learning' || c.state === 'lapsed') learning.push(w);
        else review.push(w);
      }
    }
    return { learning, review, newPool };
  }

  function buildReviewQueue(state, allWords, settings) {
    const { learning, review, newPool } = dueCards(state, allWords);
    const dailyRemaining = Math.max(0, (settings.dailyNewTarget|0) - (state.introducedToday.count|0));
    const newCount = Math.min(dailyRemaining, newPool.length, settings.reviewQueueSize);

    // Interleave: learning first, then alternate review/new
    const queue = [];
    queue.push(...learning);
    const r = review.slice();
    const n = newPool.slice(0, newCount);
    // shuffle the new pool a bit so it's not always alphabetical
    shuffle(n);
    let i = 0, j = 0;
    while (i < r.length || j < n.length) {
      if (i < r.length) queue.push(r[i++]);
      if (j < n.length) queue.push(n[j++]);
    }
    return queue.slice(0, settings.reviewQueueSize);
  }

  function shuffle(a) {
    for (let i = a.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i+1));
      [a[i], a[j]] = [a[j], a[i]];
    }
    return a;
  }

  function formatDue(intervalDays) {
    if (intervalDays < 1/24) return Math.round(intervalDays*1440) + 'm';
    if (intervalDays < 1) return Math.round(intervalDays*24) + 'h';
    if (intervalDays < 30) return Math.round(intervalDays) + 'd';
    if (intervalDays < 365) return Math.round(intervalDays/30) + 'mo';
    return (intervalDays/365).toFixed(1) + 'y';
  }

  // Compute the upcoming intervals for the rate buttons
  function previewIntervals(state, id) {
    const c = state.cards[id] || newCard(id);
    const isNew = c.reps === 0;
    const again = STEPS[0];
    const hard = isNew ? STEPS[0] : STEPS[c.step] * 0.85;
    const good = isNew ? STEPS[1] : STEPS[Math.min(STEPS.length - 1, c.step + 1)];
    return {
      again: formatDue(again),
      hard: formatDue(hard),
      good: formatDue(good),
    };
  }

  function computeStreak(history) {
    let n = 0;
    const today = new Date();
    today.setHours(0,0,0,0);
    // If user did anything today, count today.
    // Otherwise, the streak can still continue if yesterday counts.
    let cursor = new Date(today);
    let includeToday = !!history[todayKey(today.getTime())];
    if (!includeToday) {
      cursor.setDate(cursor.getDate() - 1);
    }
    while (true) {
      const k = todayKey(cursor.getTime());
      if (history[k] && (history[k].new + history[k].rev) > 0) {
        n++;
        cursor.setDate(cursor.getDate() - 1);
      } else break;
    }
    return n;
  }

  function statsForCards(cards) {
    const out = { total: 0, learning: 0, young: 0, mature: 0, mastered: 0, lapsed: 0, new: 0 };
    for (const id in cards) {
      out.total++;
      const c = cards[id];
      const cl = classify(c);
      out[cl] = (out[cl] || 0) + 1;
    }
    return out;
  }

  // due-in-the-future preview for heatmap
  function projectFutureDue(state, days) {
    const now = Date.now();
    const out = {};
    for (const id in state.cards) {
      const c = state.cards[id];
      if (c.due > now) {
        const diff = Math.floor((c.due - now) / dayMs);
        if (diff < days) out[diff] = (out[diff] || 0) + 1;
      }
    }
    return out;
  }

  /* ============================================================
     CRAM (填鸭) — batch-based Ebbinghaus replay
     Each day, a fresh batch of `cramTarget` words is stamped.
     A batch from day J resurfaces on J+1, J+2, J+4, J+7, J+15, J+30.
     Today's session = today's new batch + every past batch
     whose age (today − stampDate) hits one of those intervals.
     ============================================================ */
  const CRAM_INTERVALS = [0, 1, 2, 4, 7, 15, 30]; // 0 = today's fresh

  function dateKeyMinusDays(n, fromTs) {
    const d = new Date(fromTs || Date.now());
    d.setHours(0,0,0,0);
    d.setDate(d.getDate() - n);
    return todayKey(d.getTime());
  }

  function daysBetween(aKey, bKey) {
    // returns bKey - aKey in days
    const a = new Date(aKey + 'T00:00:00');
    const b = new Date(bKey + 'T00:00:00');
    return Math.round((b - a) / dayMs);
  }

  // Stamp today's batch if not already.
  // Picks first N words not yet stamped in any batch.
  function ensureTodaysBatch(state, allWords, cramTarget) {
    const today = todayKey();
    if (state.batches[today]) return state.batches[today];
    const stamped = new Set();
    for (const k in state.batches) {
      for (const id of state.batches[k]) stamped.add(id);
    }
    const pool = allWords.filter(w => !stamped.has(w.id));
    const take = pool.slice(0, cramTarget).map(w => w.id);
    state.batches[today] = take;
    state.cramSeen[today] = state.cramSeen[today] || {};
    saveState(state);
    return take;
  }

  // Build today's cram session: today's fresh + every past due batch.
  // Returns { sections: [{ batchDate, ageDays, label, wordIds: [...] }] , total }
  function buildCramSession(state, allWords) {
    const today = todayKey();
    const wordIndex = new Map(allWords.map(w => [w.id, w]));
    const sections = [];

    // Iterate batch dates from oldest to newest so order is stable.
    const batchKeys = Object.keys(state.batches).sort();
    for (const k of batchKeys) {
      const age = daysBetween(k, today);
      if (age < 0) continue;
      if (!CRAM_INTERVALS.includes(age)) continue;
      const ids = state.batches[k] || [];
      const words = ids.map(id => wordIndex.get(id)).filter(Boolean);
      if (!words.length) continue;
      sections.push({
        batchDate: k,
        ageDays: age,
        label: age === 0 ? 'Aujourd\'hui — nouveau' : `J+${age} · lot du ${prettyDate(k)}`,
        words,
      });
    }

    const total = sections.reduce((s, sec) => s + sec.words.length, 0);
    return { sections, total };
  }

  function prettyDate(k) {
    const d = new Date(k + 'T00:00:00');
    return d.getDate() + '/' + (d.getMonth()+1);
  }

  function markCramSeen(state, batchDate, wordId) {
    state.cramSeen[batchDate] = state.cramSeen[batchDate] || {};
    state.cramSeen[batchDate][wordId] = (state.cramSeen[batchDate][wordId] || 0) + 1;
    // Track activity in history too
    const k = todayKey();
    if (!state.history[k]) state.history[k] = { new: 0, rev: 0, again: 0, hard: 0, good: 0, cram: 0 };
    state.history[k].cram = (state.history[k].cram || 0) + 1;
    saveState(state);
  }

  window.SR = {
    loadState, saveState, defaultState,
    loadSettings, saveSettings, defaultSettings,
    newCard, classify,
    rateCard, dueCards, buildReviewQueue,
    previewIntervals, formatDue,
    computeStreak, statsForCards, projectFutureDue,
    todayKey, STEPS,
    // cram
    CRAM_INTERVALS,
    ensureTodaysBatch, buildCramSession, markCramSeen,
    daysBetween, dateKeyMinusDays,
  };
})();
