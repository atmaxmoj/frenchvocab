/* global React, window */
/* Review view — 3-button self-rated SR quiz */

const { useState: useStateR, useEffect: useEffectR, useMemo: useMemoR, useRef: useRefR } = React;

function ReviewView({ words, srState, settings, onRate, onSettings }) {
  const queue = useMemoR(
    () => window.SR.buildReviewQueue(srState, words, settings),
    [srState, words, settings.dailyNewTarget, settings.reviewQueueSize]
  );

  const [idx, setIdx] = useStateR(0);
  const [revealed, setRevealed] = useStateR(false);
  const [showConj, setShowConj] = useStateR(false);
  const [doneCount, setDoneCount] = useStateR(0);
  const [sessionStart] = useStateR(() => Date.now());

  const current = queue[idx];
  const previews = current
    ? window.SR.previewIntervals(srState, current.id)
    : { again:'10m', hard:'10m', good:'1d' };

  // keyboard shortcuts
  useEffectR(() => {
    function onKey(e) {
      if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
      if (!current) return;
      if (!revealed) {
        if (e.key === ' ' || e.key === 'Enter') { e.preventDefault(); setRevealed(true); }
        return;
      }
      if (e.key === '1' || e.key === 'j') { e.preventDefault(); doRate('again'); }
      else if (e.key === '2' || e.key === 'k') { e.preventDefault(); doRate('hard'); }
      else if (e.key === '3' || e.key === 'l') { e.preventDefault(); doRate('good'); }
      else if (e.key === 'p') { e.preventDefault(); window.speak(current.fr); }
      else if (e.key === 'c') { e.preventDefault(); setShowConj(s => !s); }
    }
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [current, revealed]);

  function doRate(rating) {
    if (!current) return;
    onRate(current.id, rating);
    setRevealed(false);
    setShowConj(false);
    setDoneCount(d => d + 1);
    if (idx + 1 < queue.length) setIdx(idx + 1);
    else setIdx(queue.length); // beyond
  }

  // count today
  const today = window.SR.todayKey();
  const todayHist = srState.history[today] || { new:0, rev:0 };
  const dueCounts = useMemoR(() => {
    const r = window.SR.dueCards(srState, words);
    return {
      learning: r.learning.length,
      review: r.review.length,
      new: Math.max(0, settings.dailyNewTarget - srState.introducedToday.count),
    };
  }, [srState, words, settings.dailyNewTarget]);

  if (!current) {
    return (
      <div className="review-wrap">
        <div className="review-done">
          <h2>— Tout est en ordre. —</h2>
          <p>Aucune carte à réviser pour l'instant.</p>
          <div className="meta" style={{marginTop:24, lineHeight:1.8}}>
            Aujourd'hui : <strong style={{color:'var(--ink-1)'}}>{todayHist.new}</strong> nouveaux,
            <strong style={{color:'var(--ink-1)'}}> {todayHist.rev}</strong> révisions
          </div>
          <div className="meta" style={{marginTop:8}}>
            Objectif quotidien : {settings.dailyNewTarget} nouveaux mots
          </div>
        </div>
      </div>
    );
  }

  const w = current;
  const progress = ((doneCount) / Math.max(1, queue.length)) * 100;

  return (
    <div className="review-wrap">
      <div className="review-progress">
        <div className="review-bar"><div className="review-bar-fill" style={{ width: progress + '%' }}/></div>
        <div className="review-counts">
          <span className="new">N {dueCounts.new}</span>
          <span className="lrn">A {dueCounts.learning}</span>
          <span className="rev">R {dueCounts.review}</span>
        </div>
      </div>

      <div className="review-card fade-in" key={w.id}>
        <span className="stage-tag">
          {labelForState(srState.cards[w.id]) }
        </span>
        <div className="pos-corner">
          <PosPill pos={w.pos}/>
        </div>

        <div className="fr-big">
          {w.gender && <span className={'gender-tag ' + (w.gender==='m'?'le':'la')}
                              style={{ fontSize:'0.45em', verticalAlign:'0.55em', marginRight:8 }}>
            {w.gender === 'm' ? 'le' : 'la'}
          </span>}
          {w.fr}
        </div>
        {w.ipa && <div className="ipa-big">{w.ipa}</div>}

        <div style={{ textAlign:'center', marginTop: 16 }}>
          <button className="icon-btn" onClick={() => window.speak(w.fr)} title="Prononcer (P)">
            {window.I.volume}
          </button>
        </div>

        {!revealed ? (
          <button className="show-btn" onClick={() => setRevealed(true)}>
            Révéler · <span className="kbd" style={{
              background:'rgba(255,255,255,0.08)', borderColor:'rgba(255,255,255,0.18)',
              color:'var(--bg)', marginLeft:6
            }}>Espace</span>
          </button>
        ) : (
          <>
            <div className="reveal">
              <div className="en">{w.en}</div>
              {w.zh && <div className="zh">{w.zh}</div>}
            </div>

            {w.examples && w.examples[0] && (
              <div className="reveal-ex">
                <span>{window.highlightTarget(w.examples[0].fr, w.examples[0].target)}</span>
                {w.examples[0].en && <div className="en-trans">{w.examples[0].en}</div>}
              </div>
            )}

            {w.etym && (
              <div className="etym" style={{ marginTop:18 }}>
                <span className="from">{w.etym.from}</span>{w.etym.text}
              </div>
            )}

            {w.conj && (
              <div style={{ marginTop:18, textAlign:'center' }}>
                <button className="seg-btn"
                        style={{ border:'1px solid var(--ink-hair-strong)' }}
                        onClick={() => setShowConj(s => !s)}>
                  {showConj ? 'Cacher la conjugaison' : 'Voir la conjugaison'} · <span className="kbd">C</span>
                </button>
                {showConj && <div style={{marginTop:12}}><ConjTable conj={w.conj}/></div>}
              </div>
            )}

            <div className="review-actions">
              <button className="rate-btn rate-again" onClick={() => doRate('again')}>
                <span>Je ne sais pas</span>
                <span className="next">↻ {previews.again}</span>
                <span className="key">1 / J</span>
              </button>
              <button className="rate-btn rate-hard" onClick={() => doRate('hard')}>
                <span>Flou</span>
                <span className="next">→ {previews.hard}</span>
                <span className="key">2 / K</span>
              </button>
              <button className="rate-btn rate-good" onClick={() => doRate('good')}>
                <span>Je connais</span>
                <span className="next">→ {previews.good}</span>
                <span className="key">3 / L</span>
              </button>
            </div>
          </>
        )}
      </div>

      <div className="meta" style={{
        textAlign:'center', marginTop:18, display:'flex',
        justifyContent:'center', gap:18,
      }}>
        <span>Session : {doneCount} cartes</span>
        <span>·</span>
        <span>File : {idx + 1} / {queue.length}</span>
        <span>·</span>
        <span>Objectif : {srState.introducedToday.count} / {settings.dailyNewTarget}</span>
      </div>
    </div>
  );
}

function labelForState(c) {
  if (!c || c.reps === 0) return '— Nouveau —';
  const cl = window.SR.classify(c);
  return ({
    learning: '— Apprentissage —',
    young: '— Jeune —',
    mature: '— Mûr —',
    mastered: '— Acquis —',
    lapsed: '— Rappel raté —',
    new: '— Nouveau —',
  })[cl] || '—';
}

window.ReviewView = ReviewView;
