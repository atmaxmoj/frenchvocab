/* global React, window */
/* Calendar view — heatmap (year) + monthly grid + streak panel */

const { useState: useStateC, useMemo: useMemoC } = React;

function CalendarView({ words, srState }) {
  const today = new Date();
  today.setHours(0,0,0,0);

  const [monthCursor, setMonthCursor] = useStateC(() => new Date(today.getFullYear(), today.getMonth(), 1));

  // 365 days back
  const yearCells = useMemoC(() => buildYearCells(today, srState.history), [srState.history]);
  const monthCells = useMemoC(() => buildMonthCells(monthCursor, today, srState.history), [monthCursor, srState.history]);
  const streak = useMemoC(() => window.SR.computeStreak(srState.history), [srState.history]);
  const stats = useMemoC(() => window.SR.statsForCards(srState.cards), [srState.cards]);
  const future = useMemoC(() => window.SR.projectFutureDue(srState, 30), [srState]);

  // total words learned / sums
  const totalWords = words.length;
  const introduced = stats.total;
  const totalActions = Object.values(srState.history).reduce((s,d) => s + (d.new||0) + (d.rev||0), 0);
  const totalDays = Object.keys(srState.history).length;

  return (
    <div>
      {/* Top row — heatmap + streak */}
      <div className="cal-grid">
        <div className="cal-card">
          <h3 className="cal-card-title">365 derniers jours</h3>
          <YearHeatmap cells={yearCells} />
          <div className="heatmap-legend">
            <span>moins</span>
            <span className="swatches">
              <span className="hcell"/>
              <span className="hcell l1"/>
              <span className="hcell l2"/>
              <span className="hcell l3"/>
              <span className="hcell l4"/>
              <span className="hcell l5"/>
            </span>
            <span>plus</span>
            <span style={{ marginLeft:'auto' }}>
              {totalActions} actions sur {totalDays || 0} jours
            </span>
          </div>
        </div>

        <div className="cal-card">
          <h3 className="cal-card-title">Série en cours</h3>
          <div style={{display:'flex', alignItems:'baseline'}}>
            <span className="streak-num">{streak}</span>
            <span className="streak-unit">{streak === 1 ? 'jour' : 'jours'} consécutifs</span>
          </div>
          <p className="streak-sub">
            {streak === 0
              ? 'Commencez aujourd\'hui pour bâtir une série.'
              : streak < 7
              ? 'Belle constance. Encore quelques jours pour ancrer l\'habitude.'
              : streak < 30
              ? 'Vous lisez plus que la plupart. Continuez.'
              : 'Lectorat assidu — un mois plein de pratique.'}
          </p>

          <div style={{ marginTop: 22 }}>
            <div className="stat-row"><span className="key">Mots dans la base</span><span className="val">{totalWords}</span></div>
            <div className="stat-row"><span className="key">Introduits</span><span className="val">{introduced}</span></div>
            <div className="stat-row"><span className="key">En apprentissage</span><span className="val">{stats.learning|0}</span></div>
            <div className="stat-row"><span className="key">Jeunes</span><span className="val">{stats.young|0}</span></div>
            <div className="stat-row"><span className="key">Mûrs</span><span className="val">{stats.mature|0}</span></div>
            <div className="stat-row"><span className="key">Acquis</span><span className="val">{stats.mastered|0}</span></div>
            {stats.lapsed > 0 && <div className="stat-row"><span className="key">Rappels ratés</span><span className="val">{stats.lapsed}</span></div>}
          </div>
        </div>
      </div>

      {/* Month grid */}
      <div className="cal-card" style={{ marginTop: 24 }}>
        <div className="month-head">
          <div className="month-title">
            {monthName(monthCursor)} {monthCursor.getFullYear()}
          </div>
          <div className="month-nav">
            <button className="icon-btn" onClick={() => stepMonth(-1)} title="Mois précédent">{window.I.left}</button>
            <button className="icon-btn" onClick={() => setMonthCursor(new Date(today.getFullYear(), today.getMonth(), 1))}>
              <span style={{fontFamily:'var(--font-display)', fontSize:10, letterSpacing:'0.08em'}}>AUJ</span>
            </button>
            <button className="icon-btn" onClick={() => stepMonth(1)} title="Mois suivant">{window.I.right}</button>
          </div>
        </div>
        <div className="month-grid">
          {['L','M','M','J','V','S','D'].map((d,i) => <div key={i} className="dow">{d}</div>)}
          {monthCells.map((cell, i) => (
            <div key={i} className={'dcell ' + cell.cls}
                 title={cell.title}>
              {cell.day != null && <span className="dnum">{cell.day}</span>}
              {cell.day != null && (cell.newCount > 0 || cell.revCount > 0 || cell.dueCount > 0) && (
                <div className="dstats">
                  {cell.newCount ? <span className="dnew">+{cell.newCount}</span> : null}
                  {cell.revCount ? <span className="drev">↻{cell.revCount}</span> : null}
                  {!cell.newCount && !cell.revCount && cell.dueCount ? <span className="drev" style={{color:'var(--ink-5)'}}>·{cell.dueCount}</span> : null}
                </div>
              )}
            </div>
          ))}
        </div>
        <div className="meta" style={{ marginTop: 14, display:'flex', gap:18 }}>
          <span><strong style={{color:'var(--sr-learning)'}}>+N</strong> nouveaux mots</span>
          <span><strong style={{color:'var(--ink-1)'}}>↻N</strong> révisions effectuées</span>
          <span><strong style={{color:'var(--ink-5)'}}>·N</strong> cartes à venir</span>
        </div>
      </div>

      {/* Upcoming due — preview */}
      <div className="cal-card" style={{ marginTop: 24 }}>
        <h3 className="cal-card-title">À venir — 30 prochains jours</h3>
        <UpcomingBars future={future} />
      </div>
    </div>
  );

  function stepMonth(delta) {
    setMonthCursor(new Date(monthCursor.getFullYear(), monthCursor.getMonth() + delta, 1));
  }
}

function YearHeatmap({ cells }) {
  // 7 rows (Mon..Sun), variable columns (weeks). cells is an array of weeks, each week is [{date, count, future, cls}].
  // Build month-label row.
  const monthLabels = [];
  let lastMonth = -1;
  cells.forEach((week, i) => {
    const firstDay = week.find(d => d.date)?.date;
    if (firstDay && firstDay.getMonth() !== lastMonth && firstDay.getDate() <= 7) {
      monthLabels.push({ col: i, label: monthAbbr(firstDay) });
      lastMonth = firstDay.getMonth();
    }
  });

  return (
    <>
      <div className="heatmap-month-row" style={{
        gridTemplateColumns: `repeat(${cells.length}, 12px)`,
        columnGap: 2,
      }}>
        {cells.map((_, i) => {
          const lab = monthLabels.find(m => m.col === i);
          return <span key={i} style={{ gridColumn: i+1, textAlign:'left' }}>{lab ? lab.label : ''}</span>;
        })}
      </div>
      <div className="heatmap">
        <div className="heatmap-day-labels">
          <span>L</span><span></span><span>M</span><span></span><span>V</span><span></span><span>D</span>
        </div>
        <div className="heatmap-cells" style={{ gridTemplateColumns: `repeat(${cells.length}, 12px)` }}>
          {cells.map((week, wi) =>
            week.map((cell, di) => (
              <div key={wi + '-' + di} className={'hcell ' + cell.cls}
                   style={{ gridColumn: wi+1, gridRow: di+1 }}
                   title={cell.title || ''} />
            ))
          )}
        </div>
      </div>
    </>
  );
}

function UpcomingBars({ future }) {
  const max = Math.max(1, ...Object.values(future));
  const days = [];
  for (let i = 0; i < 30; i++) days.push(future[i] || 0);
  return (
    <div style={{ display:'flex', alignItems:'flex-end', gap:3, height:90 }}>
      {days.map((n, i) => {
        const h = max > 0 ? (n / max) * 100 : 0;
        const isWeek = i < 7;
        return (
          <div key={i} title={`J+${i}: ${n}`} style={{
            flex:1,
            display:'flex', flexDirection:'column', alignItems:'center', gap:3,
          }}>
            <div style={{
              width:'100%', height: Math.max(2, h) + '%',
              background: isWeek ? 'var(--accent)' : 'var(--ink-6)',
              opacity: n === 0 ? 0.2 : 1,
              transition: 'height 240ms var(--ease)',
              borderRadius:'2px 2px 0 0',
            }}/>
            {i % 5 === 0 && <span className="meta" style={{ fontSize:9 }}>J+{i}</span>}
          </div>
        );
      })}
    </div>
  );
}

function buildYearCells(today, history) {
  // Walk back ~52 weeks. Align so the last column ends on today's day-of-week.
  const cells = [];
  const start = new Date(today);
  // 53 weeks back, aligned to Monday weeks
  start.setDate(start.getDate() - 52*7);
  // shift to Monday
  const dow = (start.getDay() + 6) % 7;
  start.setDate(start.getDate() - dow);

  let cursor = new Date(start);
  const todayKey = window.SR.todayKey(today.getTime());

  let week = [];
  for (let i = 0; i < 53 * 7; i++) {
    const k = window.SR.todayKey(cursor.getTime());
    const h = history[k];
    const count = h ? (h.new || 0) + (h.rev || 0) : 0;
    const isFuture = cursor > today;
    const cls = isFuture ? 'future' : level(count);
    week.push({
      date: new Date(cursor),
      count, future: isFuture, cls,
      title: isFuture ? '' : `${k}: ${count} actions`,
    });
    if (week.length === 7) { cells.push(week); week = []; }
    cursor.setDate(cursor.getDate() + 1);
  }
  if (week.length) cells.push(week);
  return cells;
}

function level(n) {
  if (n === 0) return '';
  if (n < 30) return 'l1';
  if (n < 100) return 'l2';
  if (n < 300) return 'l3';
  if (n < 600) return 'l4';
  return 'l5';
}

function buildMonthCells(monthCursor, today, history) {
  const y = monthCursor.getFullYear();
  const m = monthCursor.getMonth();
  const first = new Date(y, m, 1);
  // monday=0
  const offset = (first.getDay() + 6) % 7;
  const daysInMonth = new Date(y, m+1, 0).getDate();
  const cells = [];
  for (let i = 0; i < offset; i++) cells.push({ cls:'empty' });
  for (let d = 1; d <= daysInMonth; d++) {
    const date = new Date(y, m, d);
    const k = window.SR.todayKey(date.getTime());
    const h = history[k] || {};
    const isToday = sameDay(date, today);
    const isFuture = date > today;
    cells.push({
      day: d,
      newCount: h.new || 0,
      revCount: h.rev || 0,
      dueCount: 0,
      cls: (isToday ? 'today ' : '') + (isFuture ? 'future' : ''),
      title: isFuture ? '' : `${k}: ${(h.new||0)} nouveaux, ${(h.rev||0)} révisions`,
    });
  }
  return cells;
}

function sameDay(a,b) {
  return a.getFullYear()===b.getFullYear() && a.getMonth()===b.getMonth() && a.getDate()===b.getDate();
}
function monthName(d) {
  return ['Janvier','Février','Mars','Avril','Mai','Juin','Juillet','Août','Septembre','Octobre','Novembre','Décembre'][d.getMonth()];
}
function monthAbbr(d) {
  return ['Jan','Fév','Mar','Avr','Mai','Jun','Jul','Aoû','Sep','Oct','Nov','Déc'][d.getMonth()];
}

window.CalendarView = CalendarView;
