/* global React, window */
/* Browse view — the "大量看不使劲背" stream
   Density toggle + all mask modes + filters */

const { useState: useStateB, useMemo: useMemoB, useEffect: useEffectB } = React;

function BrowseView({ words, srState, settings, onSettings, onMarkSeen }) {
  const [expanded, setExpanded] = useStateB({});
  const [search, setSearch] = useStateB('');
  const [globalReveal, setGlobalReveal] = useStateB(0);

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
          {filtered.map(w => (
            <WordCard key={w.id + '-' + globalReveal} word={w}
                      density={settings.density}
                      maskMode={settings.maskMode}
                      sr={srState.cards[w.id]}
                      expanded={!!expanded[w.id]}
                      onToggle={() => setExpanded(e => ({...e, [w.id]: !e[w.id]}))} />
          ))}
        </div>
      )}
    </div>
  );
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
            placeholder="chercher…"
            style={{
              background:'transparent', border:'none', outline:'none',
              fontFamily:'var(--font-display)', fontSize:13, width:120, color:'var(--ink-1)',
            }}/>
        </div>
        <span className="meta" style={{ minWidth: 80, textAlign:'right' }}>{count} / {total}</span>
      </div>
    </div>
  );
}

function WordCard({ word, density, maskMode, sr, expanded, onToggle }) {
  const isHover = maskMode === 'hover';
  const isFr = maskMode === 'fr';
  const isEn = maskMode === 'en';
  const isCloze = maskMode === 'cloze';
  const isEndings = maskMode === 'endings';

  const w = word;
  const masteryColor = sr ? srColor(window.SR.classify(sr)) : 'var(--sr-new)';

  return (
    <div className={'wcard ' + density}
         onClick={() => density !== 'sparse' && onToggle()}
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
