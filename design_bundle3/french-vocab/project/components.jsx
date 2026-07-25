/* global React */
const { useState, useEffect, useMemo, useRef } = React;

// ─── Icons (inline lucide-style strokes) ───────────────────────────────
const I = {
  volume: <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/><path d="M15.54 8.46a5 5 0 0 1 0 7.07"/><path d="M19.07 4.93a10 10 0 0 1 0 14.14"/></svg>,
  shuffle: <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"><path d="M16 3h5v5"/><path d="M4 20L21 3"/><path d="M21 16v5h-5"/><path d="M15 15l6 6"/><path d="M4 4l5 5"/></svg>,
  arrow: <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"><path d="M5 12h14"/><path d="M12 5l7 7-7 7"/></svg>,
  eye:   <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"><path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7z"/><circle cx="12" cy="12" r="3"/></svg>,
  eyeoff:<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-10-7-10-7a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 10 7 10 7a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/><line x1="1" y1="1" x2="23" y2="23"/></svg>,
  left:  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"><path d="M15 18l-6-6 6-6"/></svg>,
  right: <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"><path d="M9 18l6-6-6-6"/></svg>,
  search:<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>,
};

// ─── POS pill ───────────────────────────────────────────────────────────
function PosPill({ pos }) {
  const labels = window.POS_LABELS;
  return <span className={'pos-pill ' + pos}>{labels[pos] || labels.other}</span>;
}

// ─── Gender tag (le / la) ──────────────────────────────────────────────
function GenderTag({ g, masked, onReveal }) {
  if (!g) return null;
  const label = g === 'm' ? 'le' : 'la';
  if (masked) {
    return <span className="mask" onClick={onReveal} title="Hidden">●●</span>;
  }
  return <span className={'gender-tag ' + (g === 'm' ? 'le' : 'la')}>{label}</span>;
}

// ─── TTS ────────────────────────────────────────────────────────────────
let frVoice = null;
function pickFrVoice() {
  if (frVoice) return frVoice;
  const voices = window.speechSynthesis ? window.speechSynthesis.getVoices() : [];
  frVoice = voices.find(v => v.lang === 'fr-FR') ||
            voices.find(v => v.lang && v.lang.startsWith('fr')) ||
            null;
  return frVoice;
}
function speak(text) {
  if (!window.speechSynthesis) return;
  window.speechSynthesis.cancel();
  const u = new SpeechSynthesisUtterance(text);
  u.lang = 'fr-FR';
  u.rate = 0.9;
  const v = pickFrVoice();
  if (v) u.voice = v;
  window.speechSynthesis.speak(u);
}
if (window.speechSynthesis) {
  window.speechSynthesis.onvoiceschanged = () => { frVoice = null; pickFrVoice(); };
  pickFrVoice();
}

function TtsBtn({ text, size }) {
  return (
    <button className="tts-btn" onClick={e => { e.stopPropagation(); speak(text); }}
            title="Prononcer">
      {I.volume}
    </button>
  );
}

// ─── Highlight target word in an example ─────────────────────────────
function highlightTarget(text, target) {
  if (!target) return text;
  // Use word boundary on Latin; fallback to plain match for multi-word targets.
  const tgt = target.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  const re = new RegExp('(' + tgt + ')', 'i');
  const parts = text.split(re);
  return parts.map((p, i) =>
    i % 2 === 1 ? <span key={i} className="target">{p}</span> : <React.Fragment key={i}>{p}</React.Fragment>
  );
}

// Cloze version — replaces the target with a clickable blank
function clozeTarget(text, target) {
  if (!target) return text;
  const tgt = target.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  const re = new RegExp('(' + tgt + ')', 'i');
  const parts = text.split(re);
  return parts.map((p, i) => {
    if (i % 2 === 0) return <React.Fragment key={i}>{p}</React.Fragment>;
    return <ClozeBlank key={i} answer={p} />;
  });
}

function ClozeBlank({ answer }) {
  const [shown, setShown] = useState(false);
  return (
    <span className={'cloze' + (shown ? ' shown' : '')}
          onClick={() => setShown(s => !s)}
          style={{ minWidth: (answer.length * 0.55) + 'em' }}>
      {shown ? answer : '\u00A0'}
    </span>
  );
}

// Hide endings (last 2 chars of target) — useful for adjectives & verbs
function endingsTarget(text, target) {
  if (!target) return text;
  const tgt = target.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  const re = new RegExp('(' + tgt + ')', 'i');
  const parts = text.split(re);
  return parts.map((p, i) => {
    if (i % 2 === 0) return <React.Fragment key={i}>{p}</React.Fragment>;
    const cut = Math.min(3, Math.max(1, Math.floor(p.length / 3)));
    const stem = p.slice(0, p.length - cut);
    const ending = p.slice(p.length - cut);
    return (
      <span key={i} className="target">{stem}<HiddenSpan text={ending}/></span>
    );
  });
}

function HiddenSpan({ text }) {
  const [shown, setShown] = useState(false);
  return (
    <span className={'mask' + (shown ? ' shown' : '')}
          onClick={() => setShown(s => !s)}>{text}</span>
  );
}

// Maskable word — main French word
function MaskedWord({ text, mode, onReveal }) {
  const [shown, setShown] = useState(false);
  const hidden = mode === 'fr' && !shown;
  if (hidden) {
    return <span className="mask" style={{ padding: '0 .3em' }}
                 onClick={() => { setShown(true); onReveal && onReveal(); }}>
      {'\u00A0'.repeat(Math.max(4, text.length))}
    </span>;
  }
  return <>{text}</>;
}

function MaskedGloss({ text, mode }) {
  const [shown, setShown] = useState(false);
  if (mode === 'en' && !shown) {
    return <span className="mask" style={{ padding: '0 .3em' }}
                 onClick={() => setShown(true)}>
      {'\u00A0'.repeat(Math.max(6, Math.min(40, text.length)))}
    </span>;
  }
  return <>{text}</>;
}

// ─── Conjugation table ──────────────────────────────────────────────────
function ConjTable({ conj, dense }) {
  if (!conj) return null;
  const tenses = Object.keys(conj);
  return (
    <div className="conj">
      {tenses.map(t => (
        <div key={t} className="conj-table">
          <div className="conj-tense">{t}</div>
          {conj[t].map((form, i) => {
            // Try to split off pronoun
            const m = form.match(/^(que\s+|qu')?(j['e]?|tu|il|elle|on|nous|vous|ils|elles|je\s+me|tu\s+t['e]?|il\s+s['e]?|nous\s+nous|vous\s+vous|ils\s+se)\s+(.+)$/i);
            let pron, rest;
            if (m) { pron = (m[1]||'') + m[2]; rest = m[3]; }
            else { pron = ''; rest = form; }
            return (
              <div key={i} className="conj-row">
                <span className="pron">{pron}</span>
                <span className="form">{rest}</span>
              </div>
            );
          })}
        </div>
      ))}
    </div>
  );
}

// Expose
Object.assign(window, {
  I, PosPill, GenderTag, TtsBtn,
  highlightTarget, clozeTarget, endingsTarget,
  MaskedWord, MaskedGloss, ConjTable, speak,
});
