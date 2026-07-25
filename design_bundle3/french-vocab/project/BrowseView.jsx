/* global React, window */
/* Browse view — the "大量看不使劲背" stream
   Density toggle + all mask modes + filters */

const { useState: useStateB, useMemo: useMemoB, useEffect: useEffectB } = React;

function BrowseView({ words, srState, settings, onSettings, onMarkSeen }) {
  const [expanded, setExpanded] = useStateB({});
  const [search, setSearch] = useStateB('');
  const [globalReveal, setGlobalReveal] = useStateB(0);
  const [focusIdx, setFocusIdx] = useStateB(0);
  const cardRefs = React.useRef({});

  const filtered = useMemoB(() => {
    let list = words;
    if (settings.browseFilter !== 'all') {
      list = list.filter(w => {
        const c = srState.cards[w.id];
        const cl = window.SR.classify(c);
        if (settings.browseFilter === 'new')      return !c || c.reps === 0;
        if (settings.browseFilter === 'learning') return cl === 'learning' || cl === 'lapsed';
        if (settings.browseFilter === 'review')   return cl === 'young' || cl === 'mature';
        if (settings.browseFilter === 'mastered') return cl === 'mastered';
        return true;
      });
    }
    if (search.trim()) {
      const q = search.trim().toLowerCase();
      list = list.filter(w =>
        w.fr.toLowerCase().includes(q) ||
        (w.en && w.en.toLowerCase().includes(q)) ||
        (w.zh && w.zh.includes(q))
      );
    }
    if (settings.browseOrder === 'shuffle') {
      // deterministic shuffle by re-reveal counter so it doesn't churn
      list = [...list].sort((a,b) => {
        const ha = hashStr(a.id + globalReveal), hb = hashStr(b.id + globalReveal);
        return ha - hb;
      });
    }
    return list;
  }, [words, srState, settings.browseFilter, settings.browseOrder, search, globalReveal]);

  // Reset focus when filtered set shrinks below the index
  useEffectB(() => {
    if (focusIdx >= filtered.length) setFocusIdx(Math.max(0, filtered.length - 1));
  }, [filtered.length]);

  // Keyboard nav
  useEffectB(() => {
    function onKey(e) {
      if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') {
        if (e.key === 'Escape') e.target.blur();
        return;
      }
      const cols = colsForDensity(settings.density);
      const max = filtered.length;
      if (!max) return;

      let next = focusIdx;
      let handled = true;
      switch (e.key) {
        case 'ArrowRight': case 'l': next = Math.min(max - 1, focusIdx + 1); break;
        case 'ArrowLeft':  case 'h': next = Math.max(0, focusIdx - 1); break;
        case 'ArrowDown':  case 'j': next = Math.min(max - 1, focusIdx + cols); break;
        case 'ArrowUp':    case 'k': next = Math.max(0, focusIdx - cols); break;
        case 'Home':       next = 0; break;
        case 'End':        next = max - 1; break;
        case 'PageDown':   next = Math.min(max - 1, focusIdx + cols * 5); break;
        case 'PageUp':     next = Math.max(0, focusIdx - cols * 5); break;
        case ' ': case 'Enter': {
          const w = filtered[focusIdx];
          if (w) setExpanded(ex => ({ ...ex, [w.id]: !ex[w.id] }));
          break;
        }
        case 'p': case 'P': {
          const w = filtered[focusIdx];
          if (w) window.speak(w.fr);
          break;
        }
        case 'r': case 'R': setGlobalReveal(g => g + 1); break;
        case 's': case 'S': {
          onSettings({ ...settings,
            browseOrder: settings.browseOrder === 'shuffle' ? 'sequential' : 'shuffle'
          });
          break;
        }
        case '1': onSettings({ ...settings, density: 'sparse' }); break;
        case '2': onSettings({ ...settings, density: 'normal' }); break;
        case '3': onSettings({ ...settings, density: 'dense' }); break;
        case '/': {
          const inp = document.querySelector('[data-browse-search]');
          if (inp) { inp.focus(); inp.select && inp.select(); }
          break;
        }
        default: handled = false;
      }
      if (handled) e.preventDefault();
      if (next !== focusIdx) {
        setFocusIdx(next);
        const w = filtered[next];
        if (w) {
          const node = cardRefs.current[w.id];
          if (node) {
            // gentle scroll — keep card in view but don't snap top of page
            const r = node.getBoundingClientRect();
            const margin = 80;
            if (r.top < margin || r.bottom > window.innerHeight - margin) {
              window.scrollTo({
                top: window.scrollY + r.top - 140,
                behavior: 'smooth',
              });
            }
          }
        }
      }
    }
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [focusIdx, filtered, settings]);

  function set(key, val) { onSettings({ ...settings, [key]: val }); }

  return (
    <div>
      <Toolbar settings={settings} set={set} search={search} setSearch={setSearch}
               revealAll={() => setGlobalReveal(g => g+1)}
               count={filtered.length}
               total={words.length} />
      {filtered.length === 0 ? (
        <div className="empty">— Aucun mot ne correspond. —</div>
      ) : (
        <div className={'word-grid ' + settings.density}>
          {filtered.map((w, i) => (
            <WordCard key={w.id + '-' + globalReveal} word={w}
                      density={settings.density}
                      maskMode={settings.maskMode}
                      sr={srState.cards[w.id]}
                      expanded={!!expanded[w.id]}
                      focused={i === focusIdx}
                      cardRef={el => { cardRefs.current[w.id] = el; }}
                      onFocus={() => setFocusIdx(i)}
                      onToggle={() => setExpanded(e => ({...e, [w.id]: !e[w.id]}))} />
          ))}
        </div>
      )}
    </div>
  );
}

function colsForDensity(density) {
  const w = window.innerWidth;
  if (density === 'sparse') return 1;
  if (density === 'dense')  return Math.max(1, Math.floor((Math.min(w, 1200) - 56) / 230));
  // normal
  return Math.max(1, Math.floor((Math.min(w, 1200) - 56) / 336));
}

function hashStr(s) {
  let h = 0;
  for (let i = 0; i < s.length; i++) h = (h * 31 + s.charCodeAt(i)) | 0;
  return h;
}

function Toolbar({ settings, set, search, setSearch, revealAll, count, total }) {
  return (
    <div className="toolbar">
      <div className="toolbar-group">
        <span className="toolbar-label">Densité</span>
        <div className="seg">
          {['sparse','normal','dense'].map(d =>
            <button key={d} className={'seg-btn' + (settings.density === d ? ' active' : '')}
                    onClick={() => set('density', d)}>
              {d === 'sparse' ? 'Aérée' : d === 'normal' ? 'Normale' : 'Dense'}
            </button>
          )}
        </div>
      </div>

      <div className="toolbar-group">
        <span className="toolbar-label">Masque</span>
        <div className="seg">
          {[
            { v:'none', l:'—' },
            { v:'fr', l:'FR' },
            { v:'en', l:'EN' },
            { v:'cloze', l:'Trou' },
            { v:'endings', l:'Désin.' },
            { v:'hover', l:'Survol' },
          ].map(o =>
            <button key={o.v} className={'seg-btn' + (settings.maskMode === o.v ? ' active' : '')}
                    onClick={() => set('maskMode', o.v)} title={o.v}>{o.l}</button>
          )}
        </div>
      </div>

      <div className="toolbar-group">
        <span className="toolbar-label">Filtre</span>
        <div className="seg">
          {[
            { v:'all', l:'Tous' },
            { v:'new', l:'Neufs' },
            { v:'learning', l:'Appr.' },
            { v:'review', l:'Révision' },
            { v:'mastered', l:'Acquis' },
          ].map(o =>
            <button key={o.v} className={'seg-btn' + (settings.browseFilter === o.v ? ' active' : '')}
                    onClick={() => set('browseFilter', o.v)}>{o.l}</button>
          )}
        </div>
      </div>

      <div className="toolbar-group">
        <button className={'icon-btn' + (settings.browseOrder === 'shuffle' ? ' active' : '')}
                title={settings.browseOrder === 'shuffle' ? 'Mélangé' : 'Séquence'}
                onClick={() => set('browseOrder', settings.browseOrder === 'shuffle' ? 'sequential' : 'shuffle')}>
          {window.I.shuffle}
        </button>
        <button className="icon-btn" title="Tout révéler à nouveau" onClick={revealAll}>
          {window.I.eye}
        </button>
      </div>

      <div className="toolbar-group" style={{ marginLeft: 'auto' }}>
        <div style={{
          display:'flex', alignItems:'center', gap:6,
          padding:'4px 10px',
          background:'var(--bg-washi)', border:'1px solid var(--ink-hair)', borderRadius:3
        }}>
          <span style={{ color:'var(--ink-5)', display:'flex' }}>{window.I.search}</span>
          <input value={search} onChange={e=>setSearch(e.target.value)}
            placeholder="chercher…  (/)"
            data-browse-search
            style={{
              background:'transparent', border:'none', outline:'none',
              fontFamily:'var(--font-display)', fontSize:13, width:140, color:'var(--ink-1)',
            }}/>
        </div>
        <span className="meta" style={{ minWidth: 80, textAlign:'right' }}>{count} / {total}</span>
      </div>
    </div>
  );
}

function WordCard({ word, density, maskMode, sr, expanded, focused, cardRef, onFocus, onToggle }) {
  const isHover = maskMode === 'hover';
  const isFr = maskMode === 'fr';
  const isEn = maskMode === 'en';
  const isCloze = maskMode === 'cloze';
  const isEndings = maskMode === 'endings';

  const w = word;
  const masteryColor = sr ? srColor(window.SR.classify(sr)) : 'var(--sr-new)';

  return (
    <div ref={cardRef}
         className={'wcard ' + density + (focused ? ' focused' : '')}
         onClick={() => { onFocus && onFocus(); density !== 'sparse' && onToggle(); }}
         style={{ cursor: density === 'sparse' ? 'default' : 'pointer' }}>
      {/* mastery dot */}
      <div style={{
        position:'absolute', top:14, right:14,
        width:6, height:6, borderRadius:'50%', background:masteryColor
      }} title={sr ? window.SR.classify(sr) : 'new'}/>

      <div className="wcard-head">
        <h3 className="fr" style={{ margin:0 }}>
          {w.gender && <GenderTag g={w.gender}
                                  masked={isHover}
                                  onReveal={() => {}} />}
          {isFr || isHover
            ? <HiddenFr text={w.fr} alwaysVisible={isHover ? false : false} />
            : <span>{w.fr}</span>}
        </h3>
        <PosPill pos={w.pos} />
        {w.ipa && density !== 'dense' && <span className="ipa">{w.ipa}</span>}
        <TtsBtn text={w.fr} />
      </div>

      {density !== 'dense' && (
        <div className="gloss">
          <div className="en">
            {isEn || isHover
              ? <HiddenEn text={w.en} />
              : w.en}
          </div>
          {w.zh && density !== 'dense' && (
            <div className="zh">{isEn || isHover ? <HiddenEn text={w.zh}/> : w.zh}</div>
          )}
        </div>
      )}

      {density === 'sparse' && w.examples && w.examples[0] && (
        <ExampleBlock ex={w.examples[0]} maskMode={maskMode}/>
      )}
      {density === 'normal' && expanded && w.examples && w.examples[0] && (
        <ExampleBlock ex={w.examples[0]} maskMode={maskMode}/>
      )}

      {/* etymology — sparse always shows, normal on expand */}
      {(density === 'sparse' || (density === 'normal' && expanded)) && w.etym && (
        <div className="etym">
          <span className="from">{w.etym.from}</span>{w.etym.text}
        </div>
      )}

      {/* conjugation — sparse always shows; normal on expand; dense never */}
      {(density === 'sparse' || (density === 'normal' && expanded)) && w.conj && (
        <ConjTable conj={w.conj} dense={density === 'dense'}/>
      )}

      {/* extra example sentences in sparse */}
      {density === 'sparse' && w.examples && w.examples.length > 1 && (
        w.examples.slice(1).map((ex, i) => <ExampleBlock key={i} ex={ex} maskMode={maskMode}/>)
      )}

      {/* forms (plural / feminine) */}
      {density !== 'dense' && (density === 'sparse' || expanded) && w.forms && (
        <div style={{ marginTop:10 }} className="meta">
          {w.forms.f && <span>féminin: <em style={{color:'var(--ink-1)'}}>{w.forms.f}</em></span>}
          {w.forms.plural && <span style={{marginLeft:14}}>pluriel: <em style={{color:'var(--ink-1)'}}>{w.forms.plural}</em></span>}
        </div>
      )}
    </div>
  );
}

function HiddenFr({ text }) {
  const [shown, setShown] = useStateB(false);
  if (shown) return <span>{text}</span>;
  return <span className="mask" onClick={(e) => { e.stopPropagation(); setShown(true); }}
               style={{ padding:'0 .4em' }}>
    {'\u00A0'.repeat(Math.max(4, text.length))}
  </span>;
}
function HiddenEn({ text }) {
  const [shown, setShown] = useStateB(false);
  if (shown) return <span>{text}</span>;
  return <span className="mask" onClick={(e) => { e.stopPropagation(); setShown(true); }}
               style={{ padding:'0 .4em' }}>
    {'\u00A0'.repeat(Math.max(6, Math.min(40, text.length)))}
  </span>;
}

function ExampleBlock({ ex, maskMode }) {
  const useCloze = maskMode === 'cloze';
  const useEndings = maskMode === 'endings';

  let body;
  if (useCloze) body = window.clozeTarget(ex.fr, ex.target);
  else if (useEndings) body = window.endingsTarget(ex.fr, ex.target);
  else body = window.highlightTarget(ex.fr, ex.target);

  return (
    <div className="example">
      <div className="example-fr">{body}</div>
      {ex.en && <div className="example-en">{ex.en}</div>}
    </div>
  );
}

function srColor(state) {
  return {
    new:'var(--sr-new)',
    learning:'var(--sr-learning)',
    young:'var(--sr-young)',
    mature:'var(--sr-mature)',
    mastered:'var(--sr-mastered)',
    lapsed:'var(--sr-lapsed)',
  }[state] || 'var(--sr-new)';
}

window.BrowseView = BrowseView;
