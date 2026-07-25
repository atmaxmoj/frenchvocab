/* global React, window */
/* Cram (填鸭) view — read-through flashcards organized by Ebbinghaus
   batch intervals. Big card, full info, no rating. Just flip through. */

const { useState: useStateK, useEffect: useEffectK, useMemo: useMemoK } = React;

function CramView({ words, srState, settings, onTick }) {
  // Ensure today's batch exists
  useEffectK(() => {
    const today = window.SR.todayKey();
    if (!srState.batches[today]) {
      const s = { ...srState, batches: { ...srState.batches }, cramSeen: { ...srState.cramSeen } };
      window.SR.ensureTodaysBatch(s, words, settings.cramTarget);
      onTick(s);
    }
  // eslint-disable-next-line
  }, []);

  const session = useMemoK(
    () => window.SR.buildCramSession(srState, words),
    [srState, words]
  );

  // Flatten into one queue with section refs
  const queue = useMemoK(() => {
    const q = [];
    for (const sec of session.sections) {
      for (const w of sec.words) q.push({ word: w, section: sec });
    }
    return q;
  }, [session]);

  const [idx, setIdx] = useStateK(0);
  const [showConj, setShowConj] = useStateK(false);
  const [autoPlay, setAutoPlay] = useStateK(false);
  const [autoSpeed, setAutoSpeed] = useStateK(4); // seconds

  const cur = queue[idx];

  function go(delta) {
    if (!queue.length) return;
    const next = Math.max(0, Math.min(queue.length - 1, idx + delta));
    setIdx(next);
    setShowConj(false);
    if (cur && delta > 0) {
      const s = { ...srState, cramSeen: { ...srState.cramSeen }, history: { ...srState.history } };
      window.SR.markCramSeen(s, cur.section.batchDate, cur.word.id);
      onTick(s);
    }
  }

  // Keyboard
  useEffectK(() => {
    function onKey(e) {
      if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
      if (e.key === ' ' || e.key === 'ArrowRight' || e.key === 'j' || e.key === 'Enter') {
        e.preventDefault(); go(+1);
      } else if (e.key === 'ArrowLeft' || e.key === 'k') {
        e.preventDefault(); go(-1);
      } else if (e.key === 'p') {
        e.preventDefault(); cur && window.speak(cur.word.fr);
      } else if (e.key === 'c') {
        e.preventDefault(); setShowConj(s => !s);
      } else if (e.key === 'a') {
        e.preventDefault(); setAutoPlay(a => !a);
      }
    }
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [idx, queue.length, cur]);

  // Auto-play with TTS
  useEffectK(() => {
    if (!autoPlay || !cur) return;
    if (settings.ttsEnabled) window.speak(cur.word.fr);
    const t = setTimeout(() => {
      if (idx + 1 < queue.length) go(+1);
      else setAutoPlay(false);
    }, autoSpeed * 1000);
    return () => clearTimeout(t);
  }, [autoPlay, idx, autoSpeed]);

  if (!session.total) {
    return (
      <div className="cram-wrap">
        <div className="review-done">
          <h2>— Pas de lot prévu. —</h2>
          <p>Le prochain rappel selon Ebbinghaus n'arrive pas aujourd'hui.</p>
        </div>
      </div>
    );
  }

  if (!cur) return null;

  const w = cur.word;
  const sec = cur.section;
  const progress = ((idx + 1) / queue.length) * 100;

  // Section progress
  let sectionStart = 0;
  for (const s of session.sections) {
    if (s === sec) break;
    sectionStart += s.words.length;
  }
  const inSectionIdx = idx - sectionStart;

  return (
    <div className="cram-wrap">
      <CramHeader session={session} idx={idx}
                  autoPlay={autoPlay} setAutoPlay={setAutoPlay}
                  autoSpeed={autoSpeed} setAutoSpeed={setAutoSpeed}/>

      <div className="cram-progress">
        <div className="cram-progress-bar">
          <div className="cram-progress-fill" style={{ width: progress + '%' }}/>
        </div>
        <div className="cram-progress-text">
          {idx + 1} / {queue.length}
        </div>
      </div>

      <div className="cram-section-tag">
        <span className={'cram-age-pill age-' + sec.ageDays}>
          {sec.ageDays === 0 ? 'NEUF' : 'J+' + sec.ageDays}
        </span>
        <span className="meta">{sec.label} · {inSectionIdx + 1} / {sec.words.length}</span>
      </div>

      <CramCard word={w} showConj={showConj} setShowConj={setShowConj}/>

      <div className="cram-controls">
        <button className="cram-arrow" onClick={() => go(-1)} disabled={idx === 0} title="Précédent (←)">
          {window.I.left}
          <span>Précédent</span>
        </button>
        <div className="cram-keys">
          <span><span className="kbd">Espace</span> suivant</span>
          <span><span className="kbd">←</span> retour</span>
          <span><span className="kbd">P</span> prononcer</span>
          <span><span className="kbd">C</span> conjug.</span>
          <span><span className="kbd">A</span> auto</span>
        </div>
        <button className="cram-arrow primary" onClick={() => go(+1)} disabled={idx === queue.length - 1} title="Suivant (Espace / →)">
          <span>Suivant</span>
          {window.I.right}
        </button>
      </div>
    </div>
  );
}

function CramHeader({ session, idx, autoPlay, setAutoPlay, autoSpeed, setAutoSpeed }) {
  return (
    <div className="cram-header">
      <div>
        <div className="cram-title">Bourrage du jour</div>
        <div className="cram-sub">
          {session.sections.length} {session.sections.length === 1 ? 'lot' : 'lots'} · {session.total} cartes à parcourir
        </div>
      </div>
      <div className="cram-sections">
        {session.sections.map((sec, i) => {
          let s = 0;
          for (let j = 0; j < i; j++) s += session.sections[j].words.length;
          const isCurrent = idx >= s && idx < s + sec.words.length;
          return (
            <div key={sec.batchDate}
                 className={'cram-section-chip' + (isCurrent ? ' current' : '')}>
              <span className={'age-dot age-' + sec.ageDays}/>
              <span>{sec.ageDays === 0 ? 'J0' : 'J+' + sec.ageDays}</span>
              <span className="meta" style={{marginLeft:4}}>{sec.words.length}</span>
            </div>
          );
        })}
      </div>
      <div className="cram-auto">
        <button className={'icon-btn' + (autoPlay ? ' active' : '')}
                onClick={() => setAutoPlay(a => !a)}
                title="Lecture auto (A)">
          {autoPlay
            ? <svg viewBox="0 0 24 24" width="14" height="14" fill="currentColor"><rect x="6" y="5" width="4" height="14"/><rect x="14" y="5" width="4" height="14"/></svg>
            : <svg viewBox="0 0 24 24" width="14" height="14" fill="currentColor"><polygon points="6,4 20,12 6,20"/></svg>}
        </button>
        {autoPlay && (
          <div style={{display:'flex', alignItems:'center', gap:6}}>
            <input type="range" min="2" max="10" step="0.5" value={autoSpeed}
                   onChange={e => setAutoSpeed(parseFloat(e.target.value))}
                   style={{width:80}}/>
            <span className="meta">{autoSpeed}s</span>
          </div>
        )}
      </div>
    </div>
  );
}

function CramCard({ word, showConj, setShowConj }) {
  const w = word;
  return (
    <div className="cram-card fade-in" key={w.id}>
      <div className="cram-pos-corner">
        <PosPill pos={w.pos}/>
      </div>

      <div className="cram-fr-row">
        {w.gender && (
          <span className={'gender-tag ' + (w.gender === 'm' ? 'le' : 'la')}
                style={{ fontSize:'0.42em', verticalAlign:'0.65em', marginRight:8 }}>
            {w.gender === 'm' ? 'le' : 'la'}
          </span>
        )}
        <span className="cram-fr">{w.fr}</span>
        <button className="tts-btn" onClick={() => window.speak(w.fr)} title="Prononcer (P)"
                style={{ fontSize:22, marginLeft:14, verticalAlign:'middle' }}>
          <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
            <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/>
            <path d="M15.54 8.46a5 5 0 0 1 0 7.07"/>
            <path d="M19.07 4.93a10 10 0 0 1 0 14.14"/>
          </svg>
        </button>
      </div>
      {w.ipa && <div className="cram-ipa">{w.ipa}</div>}

      <div className="cram-glosses">
        <div className="cram-en">{w.en}</div>
        {w.zh && <div className="cram-zh">{w.zh}</div>}
      </div>

      {w.examples && w.examples[0] && (
        <div className="cram-example">
          <div className="cram-example-fr">
            {window.highlightTarget(w.examples[0].fr, w.examples[0].target)}
          </div>
          {w.examples[0].en && <div className="cram-example-en">{w.examples[0].en}</div>}
        </div>
      )}

      {w.etym && (
        <div className="etym" style={{ marginTop:18 }}>
          <span className="from">{w.etym.from}</span>{w.etym.text}
        </div>
      )}

      {w.forms && (w.forms.f || w.forms.plural) && (
        <div className="meta" style={{ marginTop:14, display:'flex', gap:18 }}>
          {w.forms.f && <span>féminin : <em style={{color:'var(--ink-1)', fontStyle:'normal', fontWeight:500}}>{w.forms.f}</em></span>}
          {w.forms.plural && <span>pluriel : <em style={{color:'var(--ink-1)', fontStyle:'normal', fontWeight:500}}>{w.forms.plural}</em></span>}
        </div>
      )}

      {w.conj && (
        <>
          <div style={{ marginTop:20, textAlign:'center' }}>
            <button className="seg-btn"
                    style={{ border:'1px solid var(--ink-hair-strong)', padding:'6px 14px' }}
                    onClick={() => setShowConj(s => !s)}>
              {showConj ? 'Cacher la conjugaison' : 'Voir la conjugaison'} · <span className="kbd">C</span>
            </button>
          </div>
          {showConj && <div style={{ marginTop:14 }}><ConjTable conj={w.conj}/></div>}
        </>
      )}
    </div>
  );
}

window.CramView = CramView;
