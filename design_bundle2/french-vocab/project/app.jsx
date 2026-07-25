/* global React, ReactDOM, window */
const { useState: useStateA, useEffect: useEffectA, useMemo: useMemoA } = React;

function App() {
  const [tab, setTab] = useStateA('browse');
  const [srState, setSrState] = useStateA(() => {
    const s = window.SR.loadState();
    const seeded = seedDemoIfEmpty(s);
    // Ensure today's batch exists eagerly so Cram view doesn't flicker.
    const settings = window.SR.loadSettings();
    window.SR.ensureTodaysBatch(seeded, window.VOCAB, settings.cramTarget);
    return seeded;
  });
  const [settings, setSettings] = useStateA(() => window.SR.loadSettings());

  const words = window.VOCAB;

  function updateSettings(next) {
    setSettings(next);
    window.SR.saveSettings(next);
  }

  function onRate(id, rating) {
    const s = { ...srState, cards: { ...srState.cards }, history: { ...srState.history } };
    window.SR.rateCard(s, id, rating);
    setSrState({ ...s });
  }

  function resetAll() {
    if (!confirm('Effacer toute la progression ?')) return;
    localStorage.removeItem('fr_b2_sr_v1');
    setSrState(window.SR.defaultState());
  }
  function resetToDemo() {
    if (!confirm('Recharger les données de démonstration ?')) return;
    localStorage.removeItem('fr_b2_sr_v1');
    const s = window.SR.defaultState();
    setSrState(seedDemoIfEmpty(s, true));
  }

  // Daily queue counts
  const queueCounts = useMemoA(() => {
    const d = window.SR.dueCards(srState, words);
    return {
      due: d.learning.length + d.review.length,
      newAvail: Math.max(0, settings.dailyNewTarget - srState.introducedToday.count),
    };
  }, [srState, words, settings.dailyNewTarget]);

  return (
    <div className="app">
      <div className="vert-rail">LUCERNE · VOCABULAIRE</div>

      <header className="topbar">
        <div className="topbar-inner">
          <div className="brand">
            <span className="brand-mark">Lucerne</span>
            <span className="brand-sub">vocabulaire · B2</span>
            <span className="brand-beta">DEV</span>
          </div>
          <nav className="nav">
            <button className={'nav-item' + (tab==='browse'?' active':'')} onClick={()=>setTab('browse')}>Parcourir</button>
            <button className={'nav-item' + (tab==='cram'?' active':'')} onClick={()=>setTab('cram')}>Bourrage</button>
            <button className={'nav-item' + (tab==='review'?' active':'')} onClick={()=>setTab('review')}>Réviser</button>
            <button className={'nav-item' + (tab==='calendar'?' active':'')} onClick={()=>setTab('calendar')}>Calendrier</button>
          </nav>
          <div style={{ display:'flex', gap:10, alignItems:'center' }}>
            <button className="queue-pill" onClick={() => setTab('review')} title="File de révision">
              <span className="dot"/>
              <span>{queueCounts.due} à réviser</span>
              <span style={{color:'var(--ink-5)'}}>·</span>
              <span>{queueCounts.newAvail} neufs</span>
            </button>
            <SettingsMenu settings={settings} onChange={updateSettings}
                          onReset={resetAll} onDemo={resetToDemo} />
          </div>
        </div>
      </header>

      <main className="main">
        {tab === 'browse'   && <window.BrowseView   words={words} srState={srState} settings={settings} onSettings={updateSettings}/>}
        {tab === 'cram'     && <window.CramView     words={words} srState={srState} settings={settings} onTick={setSrState}/>}
        {tab === 'review'   && <window.ReviewView   words={words} srState={srState} settings={settings} onSettings={updateSettings} onRate={onRate}/>}
        {tab === 'calendar' && <window.CalendarView words={words} srState={srState}/>}
      </main>

      <footer style={{
        maxWidth:1200, margin:'40px auto 30px', padding:'0 28px',
        display:'flex', justifyContent:'space-between',
      }} className="meta">
        <span>Lucerne · vocabulaire — read more, cram less.</span>
        <span>© 2026 · 灯下，众语皆明</span>
      </footer>
    </div>
  );
}

function SettingsMenu({ settings, onChange, onReset, onDemo }) {
  const [open, setOpen] = useStateA(false);
  return (
    <div style={{ position:'relative' }}>
      <button className="icon-btn" onClick={() => setOpen(o => !o)} title="Paramètres">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" style={{width:14, height:14}}>
          <circle cx="12" cy="12" r="3"/>
          <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/>
        </svg>
      </button>
      {open && (
        <>
          <div onClick={() => setOpen(false)} style={{position:'fixed', inset:0, zIndex:60}}/>
          <div style={{
            position:'absolute', top:'calc(100% + 8px)', right:0,
            zIndex:70,
            minWidth:280,
            background:'var(--bg-card)',
            border:'1px solid var(--ink-hair-strong)',
            boxShadow:'var(--shadow-pop)',
            borderRadius:4,
            padding:'14px 16px',
            fontFamily:'var(--font-display)',
          }}>
            <div className="label" style={{marginBottom:8}}>Objectif quotidien</div>
            <input type="number" min="50" max="2000" step="50"
                   value={settings.dailyNewTarget}
                   onChange={e => onChange({...settings, dailyNewTarget: parseInt(e.target.value)||0})}
                   style={{
                     width:'100%',
                     fontFamily:'var(--font-display)', fontSize:18, padding:'6px 10px',
                     background:'var(--bg-washi)', border:'1px solid var(--ink-hair)',
                     color:'var(--ink-1)', outline:'none', borderRadius:3,
                   }}/>
            <div className="meta" style={{marginTop:4}}>nouveaux mots à introduire par jour (Réviser)</div>

            <div className="label" style={{marginTop:18, marginBottom:8}}>Bourrage — lot quotidien</div>
            <input type="number" min="100" max="5000" step="100"
                   value={settings.cramTarget}
                   onChange={e => onChange({...settings, cramTarget: parseInt(e.target.value)||0})}
                   style={{
                     width:'100%',
                     fontFamily:'var(--font-display)', fontSize:18, padding:'6px 10px',
                     background:'var(--bg-washi)', border:'1px solid var(--ink-hair)',
                     color:'var(--ink-1)', outline:'none', borderRadius:3,
                   }}/>
            <div className="meta" style={{marginTop:4}}>
              taille du lot du jour · revu à J+1, J+2, J+4, J+7, J+15, J+30
            </div>

            <div className="label" style={{marginTop:18, marginBottom:8}}>File de révision</div>
            <input type="number" min="10" max="500" step="10"
                   value={settings.reviewQueueSize}
                   onChange={e => onChange({...settings, reviewQueueSize: parseInt(e.target.value)||10})}
                   style={{
                     width:'100%',
                     fontFamily:'var(--font-display)', fontSize:16, padding:'6px 10px',
                     background:'var(--bg-washi)', border:'1px solid var(--ink-hair)',
                     color:'var(--ink-1)', outline:'none', borderRadius:3,
                   }}/>
            <div className="meta" style={{marginTop:4}}>nombre max de cartes par session</div>

            <div className="label" style={{marginTop:18, marginBottom:8}}>Données</div>
            <div style={{display:'flex', flexDirection:'column', gap:6}}>
              <button className="seg-btn" style={{border:'1px solid var(--ink-hair-strong)', textAlign:'left', padding:'8px 12px'}}
                      onClick={() => { onDemo(); setOpen(false); }}>
                Recharger la démonstration
              </button>
              <button className="seg-btn" style={{border:'1px solid rgba(184,93,74,0.4)', color:'var(--sr-lapsed)', textAlign:'left', padding:'8px 12px'}}
                      onClick={() => { onReset(); setOpen(false); }}>
                Tout effacer
              </button>
            </div>

            <div className="meta" style={{marginTop:18, lineHeight:1.6}}>
              Raccourcis pendant la révision :<br/>
              <span className="kbd">Espace</span> révéler · <span className="kbd">1/2/3</span> noter · <span className="kbd">P</span> prononcer · <span className="kbd">C</span> conjugaison
            </div>
          </div>
        </>
      )}
    </div>
  );
}

/* ─── Demo seeding ─────────────────────────────────────────────────────
   On first load, plant ~30 days of history so the calendar/heatmap/streak
   feel populated. Realistic distribution: heavier on workdays, lighter on
   weekends. Also pre-rate a few words so card states show.            */
function seedDemoIfEmpty(state, force) {
  if (state.cards && Object.keys(state.cards).length > 0 && !force) return state;
  // build 90 days of history
  const hist = {};
  const today = new Date();
  today.setHours(0,0,0,0);
  for (let i = 89; i >= 0; i--) {
    const d = new Date(today); d.setDate(d.getDate() - i);
    const dow = d.getDay();
    const weekend = (dow === 0 || dow === 6);
    // Skip ~30% of days to create gaps
    if (Math.random() < (weekend ? 0.45 : 0.15)) continue;
    const newCt  = weekend ? Math.floor(Math.random()*150 + 30) : Math.floor(Math.random()*420 + 180);
    const revCt  = weekend ? Math.floor(Math.random()*200 + 40) : Math.floor(Math.random()*600 + 200);
    const k = window.SR.todayKey(d.getTime());
    hist[k] = { new: newCt, rev: revCt, again: Math.floor(revCt*0.1), hard: Math.floor(revCt*0.25), good: Math.floor(revCt*0.65) };
  }
  state.history = hist;

  const words = window.VOCAB;
  const now = Date.now();
  const dayMs = 86400000;
  state.cards = {};
  for (let i = 0; i < words.length; i++) {
    if (i % 13 === 0) continue;
    const w = words[i];
    const r = Math.random();
    let step, due;
    if (r < 0.25) { step = 0; due = now + Math.random()*1*dayMs; }
    else if (r < 0.55) { step = 2; due = now + (1+Math.random()*4)*dayMs; }
    else if (r < 0.78) { step = 4; due = now + (3+Math.random()*10)*dayMs; }
    else if (r < 0.92) { step = 6; due = now + (14+Math.random()*30)*dayMs; }
    else { step = 8; due = now + (60+Math.random()*120)*dayMs; }
    if (Math.random() < 0.22) due = now - Math.random()*dayMs*2;
    const c = { id: w.id, step, due, lapses: Math.floor(Math.random()*2), reps: 3 + Math.floor(Math.random()*8), intro: now - Math.random()*30*dayMs };
    c.state = window.SR.classify(c);
    state.cards[w.id] = c;
  }

  // also seed today's count partially
  state.introducedToday = { date: window.SR.todayKey(), count: 120 };

  // Seed past cram batches so the Bourrage view shows the Ebbinghaus stack.
  // We stamp batches at J-1, J-2, J-4, J-7, J-15 so today's session has them all due.
  // With a small word base we reuse words across batches — fine for demo.
  state.batches = {};
  state.cramSeen = {};
  const sample = (n, seed) => {
    const arr = words.map(w => w.id);
    // deterministic shuffle by seed
    let h = seed;
    for (let i = arr.length - 1; i > 0; i--) {
      h = (h * 1103515245 + 12345) & 0x7fffffff;
      const j = h % (i + 1);
      [arr[i], arr[j]] = [arr[j], arr[i]];
    }
    return arr.slice(0, Math.min(n, arr.length));
  };
  [1, 2, 4, 7, 15].forEach((daysAgo, i) => {
    const k = window.SR.dateKeyMinusDays(daysAgo);
    state.batches[k] = sample(Math.min(words.length, 40 + i*5), 1234 + daysAgo);
  });

  window.SR.saveState(state);
  return state;
}

ReactDOM.createRoot(document.getElementById('root')).render(<App/>);
