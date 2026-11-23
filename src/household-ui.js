/* Household Today planner. Attendance and recipients drive servings, shopping and nutrition;
   menus are varied per day (seeded so a day's default stays put) and Shuffle/Swap are random. */
const H = KitchenHousehold;
const household = () => S.set.household || H.clone(H.defaults);
const allDishes = () => Object.assign({}, X, R);
const DIETNAME = { veg: 'vegetarian', egg: 'eggetarian', nonveg: 'non-vegetarian' };
const memberLabel = m => m.name + ' (' + DIETNAME[m.diet] + ')';
const shortName = n => String(n).replace(/^Non-vegetarian/i, 'Non-veg').replace(/^Vegetarian/i, 'Veg').replace(/^Eggetarian/i, 'Egg');
const mealServings = (p, sl, r, k = 1) => H.servings(p, sl, r, k, household());
const dishDiet = r => r.diet || (r.keys ? (r.keys.includes('eggs') ? 'egg' : 'veg') : 'veg');
const mePerson = () => { const h = household(); return h.members.find(m => m.id === S.set.nutritionPerson) || h.members[0]; };
let viewPerson = null;

/* ---------- choosing dishes for a mixed household ---------- */
function seeded(str) {
  let h = 1779033703 ^ str.length;
  for (let i = 0; i < str.length; i++) { h = Math.imul(h ^ str.charCodeAt(i), 3432918353); h = h << 13 | h >>> 19; }
  return () => { h = Math.imul(h ^ h >>> 16, 2246822507); h = Math.imul(h ^ h >>> 13, 3266489909); return ((h ^= h >>> 16) >>> 0) / 4294967296; };
}
const isMain = (r, sl) => !!r && (sl === 'b' ? r.course === 'breakfast' : r.course === 'main' || r.course === 'soup');
const CARBS = ['phulka-soft-chapati', 'rice-cooked-right'];
function pickWeighted(list, rng) {
  if (!list.length) return null;
  const w = list.map(r => Math.pow(Math.max(4, r.nutr.p), 1.5)), tot = w.reduce((a, b) => a + b, 0);
  let v = rng() * tot;
  for (let i = 0; i < list.length; i++) { v -= w[i]; if (v <= 0) return list[i]; }
  return list[list.length - 1];
}
/* How often you cook shapes the menu:
   once  — one session: a breakfast ready in 20 minutes without soaking, and lunch and dinner from one batch;
   twice — breakfast and the lunch box together in the morning: breakfast within 30 minutes, a lunch that packs well;
   three times — everything is cooked fresh, so any dish fits. */
const soaks = r => /soak|overnight/i.test(r.time || '');
function breakfastFits(r, s) { if (!isMain(r, 'b')) return true; if (s === 1) return !!r.minutes && r.minutes <= 20 && !soaks(r); if (s === 2) return !!r.minutes && r.minutes <= 30; return true; }
const lunchFits = (r, s) => !isMain(r, 'l') || s === 3 || !!r.holds;
const sameRows = (a, b) => JSON.stringify(a || []) === JSON.stringify(b || []);
const linkedDinner = q => q.s === 1 && (q.m.l || []).length > 0 && sameRows(q.m.l, q.m.d);
function chooseDish(sl, diet, sessions, rng, avoid, preferReady, prefer) {
  const h = household(), holds = (sl === 'l' && sessions <= 2) || (sl === 'd' && sessions === 1);
  const base = D.recipes.filter(r => isMain(r, sl) && dishDiet(r) === diet && !(avoid || []).includes(r.id) && !H.equipmentIssues(r, h).length);
  const fits = r => (!holds || r.holds) && (sl !== 'b' || breakfastFits(r, sessions));
  const liked = prefer || (() => true);
  const tiers = [r => fits(r) && liked(r) && budgetOk(r) && (!preferReady || !status(r).missing.length), r => fits(r) && liked(r) && budgetOk(r), r => fits(r) && liked(r), fits, r => !holds || r.holds, () => true];
  for (const f of tiers) { const l = base.filter(f); if (l.length) return pickWeighted(l, rng); }
  return null;
}
/* A meal everyone present can eat: a shared veg base, plus egg and meat additions when Settings asks for them. */
function buildMeal(p, sl, rng, avoid, preferReady) {
  const h = household(), people = H.attendees(p, sl, h), rows = [], assign = {};
  if (!people.length) return { rows, assign };
  const used = [...(avoid || [])], add = (r, who) => { rows.push([r.id, 1]); used.push(r.id); if (who) assign[r.id] = who.map(m => m.id); };
  const base = chooseDish(sl, 'veg', p.s, rng, used, preferReady);
  if (base) add(base);
  if (h.approach === 'mixed') {
    const eggs = people.filter(m => m.diet === 'egg'), meat = people.filter(m => m.diet === 'nonveg');
    const m = meat.length && chooseDish(sl, 'nonveg', p.s, rng, used, preferReady);
    if (m) add(m, meat);
    const eggFor = eggs.concat(m ? [] : meat);
    const e = eggFor.length && chooseDish(sl, 'egg', p.s, rng, used, preferReady);
    if (e) add(e, eggFor);
  }
  if (rows.some(([id]) => needsCarb(R[id]))) rows.push([CARBS[rng() < 0.5 ? 0 : 1], 1]);
  addPairs(rows);
  return { rows, assign };
}
/* Dishes that are eaten with a particular partner: mudde with saaru, bhatura with chole, holige with its saaru. */
const PAIRS = { 'ragi-mudde': 'hurali-saaru', 'atta-bhatura': 'chole', 'bele-holige': 'kattina-saaru', 'poori': 'chole' };
function addPairs(rows) {
  rows.slice().forEach(([id]) => { const mate = PAIRS[id]; if (mate && R[mate] && !rows.some(r => r[0] === mate)) rows.push([mate, 1]); });
  return rows;
}
/* Default day: the book's weekly menu, completed so vegetarians and the eggetarian always get a main. */
const defaultCache = {};
function defaultMenu(ds, sessions) {
  const h = household(), key = ds + '|' + sessions + '|' + JSON.stringify(h);
  if (defaultCache[key]) return JSON.parse(defaultCache[key]);
  const w = D.week[dayIdx(parseYmd(ds))], rng = seeded(ds), m = {}, probe = { s: sessions, m: {} };
  const weekIds = SLOTS.flatMap(sl => (w.dishes[sl] || []).map(x => x[0]));
  SLOTS.forEach(sl => {
    const rows = JSON.parse(JSON.stringify(w.dishes[sl] || [])).filter(([id]) => dish(id));
    const mains = rows.map(([id]) => dish(id)).filter(r => isMain(r, sl));
    const uncovered = H.attendees(probe, sl, h).filter(mem => !mains.some(r => H.compatible(mem, r)));
    if (uncovered.length) {
      // a meal that already has rice or rotis gets a curry or dal, not another rice dish
      const hasCarb = rows.some(([id]) => CARBS.includes(id) || (R[id] && R[id].course === 'side' && /rice|phulka|roti|chapati|paratha/i.test(R[id].title)));
      const r = chooseDish(sl, 'veg', sessions, rng, weekIds, false, hasCarb ? (x => needsCarb(x)) : null);
      if (r) {
        rows.unshift([r.id, 1]); weekIds.push(r.id);
        if (needsCarb(r) && !rows.some(([id]) => CARBS.includes(id))) rows.push([CARBS[rng() < 0.5 ? 0 : 1], 1]);
      }
    }
    m[sl] = rows;
  });
  const q = { s: sessions, m, assignments: {} };
  fitToSessions(q, ds, null);
  defaultCache[key] = JSON.stringify(q.m);
  return q.m;
}
/* Swap any dish that doesn't suit how often you cook; when cooking once, dinner is lunch's batch. */
function fitToSessions(q, ds, fallback) {
  const s = q.s, rng = seeded(ds + '|sessions' + s), h = household(), clone = H.clone;
  const used = () => SLOTS.flatMap(sl => (q.m[sl] || []).map(x => x[0]));
  const swapUnfit = (sl, ok) => {
    q.m[sl] = (q.m[sl] || []).map(row => {
      const r = R[row[0]]; if (!r || ok(r, s) || (q.pin?.[sl] || []).includes(row[0])) return row;
      const here = used(), alt = pickWeighted(D.recipes.filter(x => x.course === r.course && dishDiet(x) === dishDiet(r) && ok(x, s) && !here.includes(x.id) && !H.equipmentIssues(x, h).length), rng);
      if (!alt) return row;
      const a = q.assignments?.[sl]; if (a && a[r.id]) { a[alt.id] = a[r.id]; delete a[r.id]; }
      return [alt.id, row[1]];
    });
    if ((q.m[sl] || []).some(([id]) => R[id] && needsCarb(R[id])) && !(q.m[sl] || []).some(([id]) => CARBS.includes(id))) q.m[sl].push([CARBS[rng() < 0.5 ? 0 : 1], 1]);
  };
  swapUnfit('b', breakfastFits);
  swapUnfit('l', lunchFits);
  if (s === 1) { q.m.d = clone(q.m.l || []); (q.assignments ||= {}).d = clone(q.assignments?.l || {}); }
  else if (fallback && (q.m.l || []).length && sameRows(q.m.l, q.m.d)) { q.m.d = clone(fallback.d || []); if (q.assignments) delete q.assignments.d; }
}
/* Switching back and forth is reversible: q.base keeps the dishes you chose (or the default) before
   they were fitted to a cooking mode, so going Once → 3 times brings your own breakfast and dinner back.
   A meal you edit after a switch becomes the new base for that meal. */
function setSessions(v) {
  const ds = selDate, edited = !!S.plan[ds], before = H.clone(planOf(ds));
  editPlan(ds, q => {
    q.sChosen = true;
    if (!edited || q.auto) { q.s = v; q.m = defaultMenu(ds, v); q.assignments = {}; q.auto = true; delete q.base; delete q.fitted; }
    else {
      const base = q.base ? H.clone(q.base) : { m: {}, a: {} }, linked = linkedDinner(q);
      SLOTS.forEach(sl => {
        const touched = !q.fitted || !sameRows(q.fitted[sl], q.m[sl]) || !base.m[sl];
        // when cooking once, dinner is a copy of lunch, not a dinner you chose
        if (sl === 'd' && linked && base.m.d) return;
        if (touched) { base.m[sl] = H.clone(q.m[sl] || []); base.a[sl] = H.clone(q.assignments?.[sl] || {}); }
      });
      if (linked && !q.base) { base.m.d = H.clone(defaultMenu(ds, v).d || []); base.a.d = {}; }
      q.s = v; q.m = H.clone(base.m); q.assignments = H.clone(base.a);
      fitToSessions(q, ds, defaultMenu(ds, v));
      q.base = base; q.fitted = H.clone(q.m);
    }
    planNote = sessionNote(before, q);
  });
}
function sessionNote(before, after) {
  const title = id => (dish(id) || {}).title, out = [];
  SLOTS.forEach(sl => {
    if (sl === 'd' && linkedDinner(after)) { out.push('dinner is lunch’s pot, so lunch is cooked in double'); return; }
    const a = (before.m[sl] || []).map(x => x[0]), b = (after.m[sl] || []).map(x => x[0]);
    const gone = a.filter(x => !b.includes(x)).map(title).filter(Boolean), added = b.filter(x => !a.includes(x)).map(title).filter(Boolean);
    if (gone.length || added.length) out.push(SLOT[sl].toLowerCase() + ' ' + (gone.join(', ') || 'nothing') + ' → ' + (added.join(', ') || 'nothing'));
  });
  const why = ['', 'quick breakfast, one pot for lunch and dinner', 'quick breakfast and a lunch that packs, dinner fresh', 'everything cooked fresh'][after.s];
  return ['', 'Cooking once', 'Cooking twice', 'Cooking 3 times'][after.s] + ' (' + why + '): ' +
    (out.length ? out.join('; ') : 'these dishes already suit it, so only the cooking sessions changed') + '.';
}
/* Days you haven't touched follow the usual number of cooking times from Settings. */
function followDefault(q, ds) {
  const s = setv('sessions');
  // sDefault marks a plan that was only stored because of an attendance tick, not a chosen mode
  if (q && q.auto && !q.sChosen && q.sDefault === q.s && q.s !== s) { q.s = q.sDefault = s; q.m = defaultMenu(ds, s); q.assignments = {}; }
  return q;
}
function makeUsualSessions() {
  const v = planOf(selDate).s;
  apply(s => { s.set.sessions = v; });
  planNote = 'Days you haven’t changed now cook ' + ['', 'once', 'twice', '3 times'][v] + ' a day.';
  renderToday();
}

/* ---------- cooking now, today or tomorrow ---------- */
let cookWhen = 'today', planNote = '';
const toMin = t => { const [h, m] = String(t || '0:0').split(':').map(Number); return h * 60 + (m || 0); };
const nowMin = () => { const d = new Date(); return d.getHours() * 60 + d.getMinutes(); };
const hhmm = m => String(Math.floor(m / 60) % 24).padStart(2, '0') + ':' + String(m % 60).padStart(2, '0');
function slotTime(p, sl) {
  const ts = H.attendees(p, sl, household()).map(m => toMin(m.time || H.times[sl]));
  return ts.length ? Math.min(...ts) : toMin(H.times[sl]);
}
/* A meal counts as over 30 minutes after its eating time. */
function pastSlots(p, ds, at = nowMin()) { return ds === todayStr() ? SLOTS.filter(sl => at > slotTime(p, sl) + 30) : []; }
const hiddenSlots = (p, ds) => cookWhen === 'now' ? pastSlots(p, ds) : [];
/* Best available time estimate: reviewed timings first, then the book's minutes; soaking dishes can't be made now. */
function estMinutes(r) {
  const t = KitchenCore.timing(r, false); if (t.max !== null) return t.max;
  return soaks(r) || !r.minutes ? Infinity : r.minutes;
}
function cookingDeadline(p, sl, left) {
  // dishes cooked in the same session must be ready for the earliest meal in it
  const se = SESS[p.s].find(x => x.slots.includes(sl));
  return Math.min(...se.slots.filter(x => left.includes(x)).map(x => slotTime(p, x)));
}
function setCookWhen(w) {
  const t = new Date(); planNote = '';
  if (w === 'tomorrow') { cookWhen = w; t.setDate(t.getDate() + 1); selDate = ymd(t); renderToday(); return; }
  cookWhen = w; selDate = todayStr();
  if (w !== 'now') { renderToday(); return; }
  const p = planOf(selDate), gone = pastSlots(p, selDate), left = SLOTS.filter(sl => !gone.includes(sl) && H.attendees(p, sl, household()).length);
  if (!left.length) {
    cookWhen = 'tomorrow'; t.setDate(t.getDate() + 1); selDate = ymd(t);
    planNote = 'Today’s meals are over, so this shows tomorrow. ' + (nightBefore(todayStr()) || '');
    renderToday(); return;
  }
  fitToNow(left);
}
/* Cooking right now: keep what fits the time until the meal and what's in the pantry; swap the rest. */
function fitToNow(left) {
  const ds = selDate, p = planOf(ds), h = household(), at = nowMin(), checkPantry = pantryTouched();
  const here = SLOTS.flatMap(s => (p.m[s] || []).map(x => x[0])), linked = linkedDinner(p), changes = [], stuck = [], notes = [];
  left.forEach(sl => {
    if (sl === 'd' && linked && left.includes('l')) return; // follows lunch
    if (sl === 'd' && linked && eaten(ds, 'l')) { notes.push('Dinner is from lunch’s pot: reheat it until steaming hot all the way through.'); return; }
    const minutes = cookingDeadline(p, sl, left) - at, budget = Math.max(20, minutes), free = minutes >= 150;
    (p.m[sl] || []).forEach(([id], i) => {
      const r = R[id]; if (!r || CARBS.includes(id)) return;
      const slow = !free && estMinutes(r) > budget, short = checkPantry ? status(r).missing : [];
      if (!slow && !short.length) return;
      const list = D.recipes.filter(x => x.id !== id && x.course === r.course && dishDiet(x) === dishDiet(r) && !here.includes(x.id) &&
        !H.equipmentIssues(x, h).length && (sl !== 'b' || breakfastFits(x, p.s)) && (sl !== 'l' || lunchFits(x, p.s)) &&
        (free || estMinutes(x) <= budget) && (!checkPantry || !status(x).missing.length) && budgetOk(x));
      // closest swap first: same cuisine and the same need for rice or rotis on the side
      const near = list.filter(x => x.cuisine === r.cuisine && needsCarb(x) === needsCarb(r));
      const pick = pickWeighted(near.length ? near : list, Math.random);
      if (!pick) { stuck.push(r.title + (slow ? ' needs about ' + estMinutes(r) + ' min' : ' needs ' + short.map(tokLabel).join(', ').toLowerCase())); return; }
      here.push(pick.id);
      changes.push({ sl, i, from: id, to: pick.id, why: slow ? 'ready in ~' + estMinutes(pick) + ' min' : 'uses what you have' });
    });
  });
  const head = 'Cooking now (' + hhmm(at) + '): ';
  const done = left.length < 3 ? ' ' + SLOTS.filter(sl => !left.includes(sl)).map(sl => SLOT[sl]).join(' and ') + (3 - left.length === 1 ? ' is' : ' are') + ' over, so ' + (3 - left.length === 1 ? 'it is' : 'they are') + ' left out.' : '';
  planNote = head + (changes.length ? changes.map(c => SLOT[c.sl].toLowerCase() + ' ' + R[c.from].title + ' → ' + R[c.to].title + ' (' + c.why + ')').join('; ') + '.' :
    'what’s left today fits the time you have' + (checkPantry ? ' and your pantry.' : '. Tick your pantry for picks that use what you have.')) +
    done + (stuck.length ? ' No quicker swap for: ' + stuck.join('; ') + '.' : '') + (notes.length ? ' ' + notes.join(' ') : '');
  if (!changes.length) { renderToday(); return; }
  editPlan(ds, q => {
    const link = linkedDinner(q);
    changes.forEach(c => {
      const row = (q.m[c.sl] || [])[c.i]; if (!row || row[0] !== c.from) return; row[0] = c.to;
      const a = q.assignments?.[c.sl]; if (a && a[c.from]) { a[c.to] = a[c.from]; delete a[c.from]; }
      if (link && c.sl === 'l') { q.m.d = H.clone(q.m.l); (q.assignments ||= {}).d = H.clone(q.assignments?.l || {}); }
    });
    delete q.auto;
  });
}
/* Edit one meal; when cooking once and dinner is lunch's batch, keep the two in step. */
function editMeal(sl, fn) {
  editPlan(selDate, q => {
    const linked = linkedDinner(q);
    fn(q); delete q.auto;
    if (linked && (sl === 'l' || sl === 'd')) { const to = sl === 'l' ? 'd' : 'l'; q.m[to] = H.clone(q.m[sl] || []); (q.assignments ||= {})[to] = H.clone(q.assignments?.[sl] || {}); }
  });
}
function shuffleMeal(sl) {
  const p = planOf(selDate), together = linkedDinner(p) && (sl === 'l' || sl === 'd'), from = together ? 'l' : sl;
  const avoid = SLOTS.flatMap(s => (p.m[s] || []).map(x => x[0]));
  const meal = buildMeal(p, from, Math.random, avoid, true);
  editPlan(selDate, q => {
    delete q.auto; q.m[from] = meal.rows; (q.assignments ||= {})[from] = meal.assign;
    if (together) { q.m.d = H.clone(meal.rows); q.assignments.d = H.clone(meal.assign); }
  });
}
function surpriseDay() {
  const p = planOf(selDate), used = [], menu = {}, assign = {};
  SLOTS.forEach(sl => {
    if (sl === 'd' && p.s === 1) { menu.d = H.clone(menu.l); assign.d = H.clone(assign.l); return; }
    const meal = buildMeal(p, sl, Math.random, used, true); menu[sl] = meal.rows; assign[sl] = meal.assign; used.push(...meal.rows.map(x => x[0]));
  });
  editPlan(selDate, q => { q.m = menu; q.assignments = assign; delete q.auto; });
}
function swapDish(sl, i) {
  const p = planOf(selDate), row = (p.m[sl] || [])[i]; if (!row) return;
  const old = dish(row[0]), here = SLOTS.flatMap(s => (p.m[s] || []).map(x => x[0])), h = household();
  let list;
  if (X[row[0]]) list = D.extras.filter(x => x.id !== row[0] && dishDiet(x) === dishDiet(old) && !here.includes(x.id));
  else if (CARBS.includes(row[0])) list = CARBS.filter(id => id !== row[0]).map(id => R[id]);
  else list = D.recipes.filter(r => r.id !== row[0] && r.course === old.course && dishDiet(r) === dishDiet(old) && !here.includes(r.id) && !H.equipmentIssues(r, h).length && (sl !== 'b' || breakfastFits(r, p.s)) && (sl !== 'l' || lunchFits(r, p.s)));
  const ready = list.filter(r => !R[r.id] || (!status(r).missing.length && budgetOk(r)));
  const pick = pickWeighted(ready.length ? ready : list, Math.random); if (!pick) return;
  editMeal(sl, q => {
    const it = q.m[sl][i]; if (!it) return; const from = it[0]; it[0] = pick.id;
    const a = q.assignments?.[sl]; if (a && a[from]) { a[pick.id] = a[from]; delete a[from]; }
  });
}
function removeDish(sl, i) {
  editMeal(sl, q => { const it = q.m[sl][+i]; if (!it) return; q.m[sl].splice(+i, 1); if (q.assignments?.[sl]) delete q.assignments[sl][it[0]]; });
}
/* What to do the night before: soaking for tomorrow's dishes, and setting curd when tomorrow uses it. */
function nightBefore(ds) {
  const d = parseYmd(ds); d.setDate(d.getDate() + 1);
  const p = planOf(ymd(d)), ids = [...new Set(SLOTS.flatMap(sl => (p.m[sl] || []).filter(([id, k]) => dish(id) && mealServings(p, sl, dish(id), k) > 0).map(x => x[0])))];
  const soak = ids.filter(id => R[id] && /soak|overnight/i.test(R[id].time || '')).map(id => R[id].title);
  const curd = ids.some(id => id === 'x-curd' || (R[id] && R[id].needs.some(t => t.split('|').includes('curd'))));
  const out = [];
  if (curd) out.push('set curd');
  if (soak.length) out.push('soak for ' + soak.map(s => s.toLowerCase()).join(', '));
  return out.length ? 'For ' + DAYS[dayIdx(d)] + ': ' + out.join('; ') + '.' : '';
}

/* ---------- pieces of the day ticket ---------- */
function whoHTML(p, sl) {
  const h = household();
  const chips = h.members.map(m => {
    const a = p.attendance?.[sl]?.[m.id] || { eating: true };
    return '<button type="button" class="who-chip" data-attend-toggle="' + sl + '|' + m.id + '" aria-pressed="' + !!a.eating + '" aria-label="' + esc(m.name) + ' eating ' + SLOT[sl].toLowerCase() + '"><i class="dd d-' + m.diet + '" aria-hidden="true"></i>' + esc(shortName(m.name)) + '</button>';
  }).join('');
  const rows = h.members.map(m => {
    const a = p.attendance?.[sl]?.[m.id] || { eating: true, portions: 1, time: H.times[sl] };
    return '<div class="member-row"><span class="mr-n">' + esc(shortName(m.name)) + '</span><label>Portions <select aria-label="' + esc(SLOT[sl] + ' portions for ' + m.name) + '" data-portion="' + sl + '|' + m.id + '">' + [0.5, 1, 1.5, 2].map(n => '<option value="' + n + '"' + (a.portions === n ? ' selected' : '') + '>' + n + '</option>').join('') + '</select></label><label>Eats at <input type="time" aria-label="' + esc(SLOT[sl] + ' time for ' + m.name) + '" data-mealtime="' + sl + '|' + m.id + '" value="' + esc(a.time || H.times[sl]) + '"></label></div>';
  }).join('');
  return '<div class="who" role="group" aria-label="Who is eating ' + SLOT[sl].toLowerCase() + '">' + chips + '</div><details class="pt" id="pt-' + sl + '"><summary>Portions and eating times</summary>' + rows + '</details>';
}
function recipientsHTML(p, sl, r, label) {
  const h = household(), eligible = H.attendees(p, sl, h).filter(m => H.compatible(m, r)), ids = H.recipients(p, sl, r, h).map(m => m.id);
  return '<details class="hd-who" id="who-' + sl + '-' + r.id + '"><summary>' + label + '</summary><div class="who">' + (eligible.length ? eligible.map(m => '<label class="who-chip"><input type="checkbox" data-recipient="' + sl + '|' + r.id + '|' + m.id + '"' + (ids.includes(m.id) ? ' checked' : '') + '> ' + esc(shortName(m.name)) + '</label>').join('') : '<span class="small">Nobody eating this meal can have this dish.</span>') + '</div></details>';
}
function dishHTML(p, sl, id, k, i) {
  const r = dish(id); if (!r) return '';
  const h = household(), attending = H.attendees(p, sl, h), people = H.recipients(p, sl, r, h), n = mealServings(p, sl, r, k);
  const forTxt = !people.length ? 'nobody' : people.length === attending.length && attending.length > 1 ? 'everyone' : people.map(m => shortName(m.name)).join(', ');
  const title = R[id] ? '<button type="button" class="linkish" data-hh-open="' + sl + '|' + id + '">' + esc(r.title) + '</button>' : '<span>' + esc(r.title) + '</span>';
  return '<li class="hd"><i class="dd d-' + dishDiet(r) + '" aria-hidden="true" title="' + DIETNAME[dishDiet(r)] + '"></i><div class="hd-t">' + title + '</div>' +
    recipientsHTML(p, sl, r, nice(n) + (n === 1 ? ' serving' : ' servings') + ' · ' + esc(forTxt)) +
    '<div class="hd-c"><span class="cnt"><button type="button" data-dish="' + sl + '|' + i + '|-1" aria-label="Smaller portions of ' + esc(r.title) + '">−</button>×' + nice(k) + '<button type="button" data-dish="' + sl + '|' + i + '|1" aria-label="Bigger portions of ' + esc(r.title) + '">+</button></span>' +
    '<button type="button" class="x" data-swap="' + sl + '|' + i + '" aria-label="Swap ' + esc(r.title) + ' for another dish" title="Swap">⟳</button><button type="button" class="x" data-rm="' + sl + '|' + i + '" aria-label="Remove ' + esc(r.title) + '" title="Remove">×</button></div></li>';
}
function mealHTML(p, sl, me) {
  const h = household(), attending = H.attendees(p, sl, h), rows = p.m[sl] || [], on = eaten(selDate, sl);
  const g = Math.round(H.personNutrition(p, sl, me.id, allDishes(), h).p || 0);
  const covered = m => rows.some(([id, k]) => dish(id) && isMain(dish(id), sl) && H.recipients(p, sl, dish(id), h).some(x => x.id === m.id));
  const uncovered = rows.length ? attending.filter(m => !covered(m)) : [];
  const fromLunch = sl === 'd' && linkedDinner(p);
  return '<div class="meal"><div class="meal-h"><input type="checkbox" id="eat-' + sl + '" data-eat="' + sl + '"' + (on ? ' checked' : '') + ' aria-label="' + SLOT[sl] + ' eaten"><span class="slot">' + SLOT[sl] + '</span><span class="g">' + (attending.some(m => m.id === me.id) ? '~' + g + ' g protein · ' + esc(shortName(me.name)) : attending.length + ' eating') + '</span></div>' +
    whoHTML(p, sl) +
    (fromLunch ? '<p class="link-line">Same pot as lunch: cooked once in the morning, so its servings are in the morning cooking amounts. Changes to lunch apply here too.</p>' : '') +
    (!attending.length ? '<p class="small">Nobody is eating this meal, so nothing is cooked for it.</p>' :
      (rows.length ? '<ul class="dishes">' + rows.map(([id, k], i) => dishHTML(p, sl, id, k, i)).join('') + '</ul>' : '<p class="small">Nothing planned.</p>') +
      (uncovered.length ? '<p class="warn-line">No main dish for ' + uncovered.map(m => esc(shortName(m.name))).join(', ') + '. Shuffle or add one.</p>' : '') +
      '<div class="meal-acts"><button type="button" class="btn sm" data-add="' + sl + '">+ Add</button><button type="button" class="btn sm" data-shuffle="' + sl + '">Shuffle</button></div>') + '</div>';
}
function workloadHTML(p, slots) {
  const h = household(), w = H.workload(p, slots, allDishes(), h), id = 'workload-' + slots.join('');
  if (!slots.some(sl => H.attendees(p, sl, h).length)) return '';
  const head = w.minutes === null ? 'timing needs review' : '~' + w.minutes + ' min' + (w.startBy ? ' · start by ' + w.startBy : '');
  return '<details class="wl" id="' + id + '"><summary>' + h.cooks + (h.cooks === 1 ? ' cook' : ' cooks') + ' · ' + esc(head) + '</summary><p class="small">' + esc(w.basis) + '</p>' +
    w.tasks.map(t => '<p>Cook ' + t.cook + ': ' + esc(dish(t.id).title) + ' · ' + nice(t.servings) + ' servings · ' + t.batches + (t.batches === 1 ? ' batch' : ' batches') + ' · minute ' + t.start + '–' + t.end + ' · ' + esc(t.resources.join(', ')) + '</p>').join('') +
    w.unknown.map(x => '<p class="small">• ' + esc(x) + '</p>').join('') +
    (w.minutes !== null && w.minutes > h.maxMinutes ? '<p class="warn-line">Over your ' + h.maxMinutes + '-minute target. Drop a dish or prepare ahead.</p>' : '') +
    '<p class="small">Keep vegetarian utensils separate. Wash hands and equipment between raw meat and other food.</p></details>';
}
function householdQuantities(p, slots, prefix = 'today') {
  slots = Array.isArray(slots) ? slots : [slots];
  const amounts = H.totals(p, allDishes(), household(), slots), list = Object.entries(amounts);
  if (!list.length) return '';
  return '<details class="recipe-details qty" id="quantities-' + prefix + '-' + slots.join('') + '"><summary>Quantities to cook</summary>' + list.map(([id, n]) => {
    const r = dish(id), f = n / (r.yield || 1);
    return '<h4>' + esc(r.title) + ' · ' + nice(n) + ' servings</h4>' + (r.ingredients || []).map(g => typeof g === 'string' ? '<p>' + esc(g) + ' · legacy quantity needs manual scaling</p>' : '<ul>' + g.items.map(i => '<li>' + esc(KitchenCore.ingredientQuantity(i, f)) + ' ' + esc(i.name) + (i.scaleMode === 'pan' ? ' (pan quantity; extra batches)' : '') + '</li>').join('') + '</ul>').join('');
  }).join('') + '</details>';
}
function dayPanelHTML(p, ds) {
  const h = household(), me = mePerson(), view = h.members.find(m => m.id === viewPerson) || me;
  const per = m => { const n = {}; SLOTS.forEach(sl => Object.entries(H.personNutrition(p, sl, m.id, allDishes(), h)).forEach(([k, x]) => n[k] = (n[k] || 0) + x)); return n; };
  const ppl = h.members.map(m => { const n = per(m); return '<button type="button" class="pp" data-view-person="' + m.id + '" aria-pressed="' + (m.id === view.id) + '"><i class="dd d-' + m.diet + '" aria-hidden="true"></i><b>' + esc(shortName(m.name)) + '</b><span>' + Math.round(n.kcal || 0) + ' kcal · ' + Math.round(n.p || 0) + ' g</span></button>'; }).join('');
  const t = nsum([[per(view), 1]]);
  return '<div class="ppl" role="group" aria-label="Whose nutrition to show">' + ppl + '</div>' +
    nutriHTML(t, 'Planned for ' + (ds === todayStr() ? 'today' : fmtDay(parseYmd(ds))) + ' · ' + view.name, true) +
    (view.id !== me.id ? '<p class="small">Percentages use the targets in Me, which are set for ' + esc(me.name) + '. ' + esc(view.name) + '’s needs may differ.</p>' : '');
}

/* ---------- Today ---------- */
function renderToday() {
  const t0 = new Date(), h = household(); let dates = '';
  for (let i = 0; i < 7; i++) { const d = new Date(t0); d.setDate(t0.getDate() + i); const ds = ymd(d); dates += '<button type="button" class="date" data-date="' + ds + '" aria-pressed="' + (ds === selDate) + '"><span>' + (i === 0 ? 'Today' : DAYS[dayIdx(d)]) + '</span><b>' + d.getDate() + '</b></button>'; }
  $('#dates').innerHTML = dates;
  const p = planOf(selDate), date = parseYmd(selDate), me = mePerson();
  document.querySelectorAll('#seg-sess button').forEach(b => b.setAttribute('aria-pressed', String(+b.dataset.sess === p.s)));
  document.querySelectorAll('#seg-when button').forEach(b => b.setAttribute('aria-pressed', String(b.dataset.when === cookWhen)));
  const usual = $('#sess-usual'); usual.hidden = p.s === setv('sessions'); usual.textContent = 'Cook ' + ['', 'once', 'twice', '3 times'][p.s] + ' every day';
  const pn = $('#plan-note'); pn.hidden = !planNote; pn.textContent = planNote;
  const hide = hiddenSlots(p, selDate);
  const sessions = SESS[p.s].map(se0 => {
    const se = Object.assign({}, se0, { slots: se0.slots.filter(sl => !hide.includes(sl)) });
    if (!se.slots.length) return '<div class="sess"><div class="sess-h"><h3>' + esc(se.name) + '</h3><span>done</span></div><p class="past-line">' + se0.slots.map(sl => SLOT[sl]).join(' and ') + (se0.slots.length > 1 ? ' times have passed, so they aren’t' : ' time has passed, so it isn’t') + ' in the cooking list.</p></div>';
    if (hide.includes('l') && se.slots.join() === 'd' && linkedDinner(p) && eaten(selDate, 'l'))
      return '<div class="sess"><div class="sess-h"><h3>Dinner</h3><span>from the morning pot</span></div><p class="link-line">Nothing to cook: dinner is the second half of lunch’s pot. Reheat it until steaming hot all the way through.</p>' + mealHTML(p, 'd', me) + '</div>';
    const ids = [...new Set(se.slots.flatMap(sl => (p.m[sl] || []).filter(([id, k]) => R[id] && mealServings(p, sl, R[id], k) > 0).map(x => x[0])))];
    const miss = []; ids.forEach(id => status(R[id]).missing.forEach(t => { const k = firstMissing(t); if (!miss.includes(k)) miss.push(k); }));
    const cook = Object.entries(H.totals(p, allDishes(), h, se.slots)).filter(([id]) => R[id]).map(([id, n]) => esc(R[id].title) + ' <b>' + nice(n) + '</b>');
    const note = p.s === 1 ? (h.fridge ? 'Breakfast is quick, and lunch and dinner come from one pot. Eat lunch fresh; cool dinner’s share and refrigerate it within 2 hours, then reheat until steaming hot all the way through.' : se.note) : se.note;
    return '<div class="sess"><div class="sess-h"><h3>' + esc(se.name) + '</h3><span>' + esc(se.when) + '</span></div>' + workloadHTML(p, se.slots) +
      (cook.length ? '<p class="cook-line"><span class="lbl-s">Cook</span> ' + cook.join(' · ') + ' <span class="small">servings</span></p>' : '') +
      (se.slots.length < se0.slots.length ? '<p class="past-line">' + se0.slots.filter(sl => hide.includes(sl)).map(sl => SLOT[sl]).join(' and ') + (se0.slots.filter(sl => hide.includes(sl)).length > 1 ? ' times have passed, so they aren’t' : ' time has passed, so it isn’t') + ' counted here.</p>' : '') +
      se.slots.map(sl => mealHTML(p, sl, me)).join('') +
      (note ? '<p class="sess-note">' + esc(note) + '</p>' : '') +
      (miss.length ? '<div class="miss"><span class="small">Missing:</span>' + missChips(miss) + '</div>' : '') +
      householdQuantities(p, se.slots) + '</div>';
  }).join('');
  const eat = nsum(SLOTS.filter(sl => eaten(selDate, sl)).map(sl => [H.personNutrition(p, sl, me.id, allDishes(), h), 1]));
  const plan = nsum(SLOTS.map(sl => [H.personNutrition(p, sl, me.id, allDishes(), h), 1]));
  const tmr = new Date(); tmr.setDate(tmr.getDate() + 1);
  const tonight = selDate === ymd(tmr) ? nightBefore(todayStr()) : '';
  const night = nightBefore(selDate), counts = h.members.reduce((o, m) => (o[m.diet] = (o[m.diet] || 0) + 1, o), {});
  $('#kot').innerHTML = '<div class="kot-head"><span>Kitchen order · ' + esc(fmtDay(date)) + '</span>' + (selDate === todayStr() ? '<span class="stamp">Today</span>' : '') + '</div>' +
    '<p class="kot-title">' + esc(date.toLocaleDateString('en-IN', { weekday: 'long' })) + '</p>' +
    '<p class="kot-sub">' + ['', 'Cooking once: quick breakfast, one pot for lunch and dinner', 'Cooking twice: quick breakfast and a packable lunch in the morning, dinner fresh', 'Cooking three times: everything fresh'][p.s] + ' · ' + h.members.length + ' people (' + ['veg', 'egg', 'nonveg'].filter(d => counts[d]).map(d => counts[d] + ' ' + { veg: 'veg', egg: 'egg', nonveg: 'non-veg' }[d]).join(', ') + ') · ' + (S.plan[selDate] && !S.plan[selDate].auto ? 'your plan' : 'default menu') + '. Tap names to mark who is eating.</p>' +
    sessions +
    '<div class="kot-foot"><span class="mono"><b>Protein</b>~' + Math.round(eat.p) + ' eaten of ~' + Math.round(plan.p) + ' g planned for ' + esc(shortName(me.name)) + ' (target ' + target('p') + ' g)</span>' +
    (tonight ? '<span><b>Tonight</b>' + esc(tonight) + '</span>' : '') +
    (night ? '<span><b>Night before</b>' + esc(night) + '</span>' : '') + '</div>';
  $('#day-reset').hidden = !S.plan[selDate] || !!S.plan[selDate].auto;
  $('#day-nutri').innerHTML = dayPanelHTML(p, selDate);
  $('#check-card').innerHTML = checkCardHTML();
}

/* ---------- Settings: household ---------- */
function householdSetupHTML() {
  const h = household();
  const fields = [['cooks', 'People cooking', 1, 2, 3, 4], ['burners', 'Stove burners', 1, 2, 3, 4, 5, 6, 8], ['induction', 'Induction hobs', 0, 1, 2], ['airfryer', 'Air fryers', 0, 1, 2], ['sandwich', 'Sandwich makers', 0, 1, 2], ['cooker3', '3 L pressure cookers', 0, 1, 2], ['cooker5', '5 L pressure cookers', 0, 1, 2]];
  return '<section class="sec"><h2>Your household</h2><p class="small">Names and diets drive who gets which dish on Today. Untick a name on Today when someone isn’t eating.</p>' + h.members.map(m => '<div class="member-row"><label>Name <input type="text" maxlength="60" data-member-name="' + m.id + '" value="' + esc(m.name) + '"></label><label>Diet <select data-member-diet="' + m.id + '">' + [['veg', 'Vegetarian'], ['egg', 'Eggetarian'], ['nonveg', 'Non-vegetarian']].map(([v, l]) => '<option value="' + v + '"' + (m.diet === v ? ' selected' : '') + '>' + l + '</option>').join('') + '</select></label></div>').join('') +
    '<label class="f">Meal suggestions<select data-kitchen="approach"><option value="shared"' + (h.approach === 'shared' ? ' selected' : '') + '>One shared vegetarian meal · least work</option><option value="mixed"' + (h.approach === 'mixed' ? ' selected' : '') + '>Shared veg base + egg and meat additions</option></select><span class="hint">Used by Shuffle and Surprise me. Default days follow the weekly menu, with a vegetarian main added where needed.</span></label>' +
    '<details class="recipe-details"><summary>Kitchen equipment and cooking window</summary><div class="fgrid">' + fields.map(([key, label, ...values]) => '<label>' + label + '<select data-kitchen="' + key + '">' + values.map(n => '<option value="' + n + '"' + (h[key] === n ? ' selected' : '') + '>' + n + '</option>').join('') + '</select></label>').join('') +
    '<label>Cooking window (min)<input type="number" min="10" max="240" step="5" data-kitchen="maxMinutes" value="' + h.maxMinutes + '"></label></div>' +
    '<label class="toggle"><input type="checkbox" data-kitchen="fridge"' + (h.fridge ? ' checked' : '') + '> Fridge available</label><label class="toggle"><input type="checkbox" data-kitchen="mixer"' + (h.mixer ? ' checked' : '') + '> Mixer/grinder available</label><p class="small">Times are estimates. The two pressure cookers use separate burner slots; a 5 L cooker is not assumed to double a recipe.</p></details></section>';
}
function changeHousehold(t) {
  if (t.dataset.portion || t.dataset.mealtime) {
    const [sl, id] = (t.dataset.portion || t.dataset.mealtime).split('|');
    editPlan(selDate, p => { const a = ((p.attendance ||= {})[sl] ||= {}); const m = a[id] || { eating: true, portions: 1, time: H.times[sl] };
      if (t.dataset.portion) m.portions = +t.value; if (t.dataset.mealtime && t.value) m.time = t.value; a[id] = m; });
    return true;
  }
  if (t.dataset.recipient) { const [sl, id, person] = t.dataset.recipient.split('|'), p = planOf(selDate), r = dish(id); let ids = H.recipients(p, sl, r, household()).map(m => m.id); ids = t.checked ? [...new Set([...ids, person])] : ids.filter(x => x !== person); editMeal(sl, p => { ((p.assignments ||= {})[sl] ||= {})[id] = ids; }); return true; }
  if (t.dataset.memberName || t.dataset.memberDiet || t.dataset.kitchen) {
    const h = H.clone(household());
    if (t.dataset.kitchen) { const k = t.dataset.kitchen; h[k] = ['fridge', 'mixer'].includes(k) ? t.checked : k === 'approach' ? t.value : +t.value; }
    else { const m = h.members.find(m => m.id === (t.dataset.memberName || t.dataset.memberDiet)); if (t.dataset.memberName) m.name = t.value.trim() || m.name; else m.diet = t.value; }
    const error = H.validateProfile(h); if (!error) apply(s => { s.set.household = h; s.set.people = h.members.length; });
    return true;
  }
  return false;
}
function toggleAttendance(sl, id) {
  editPlan(selDate, p => { const a = ((p.attendance ||= {})[sl] ||= {}); const m = a[id] || { eating: true, portions: 1, time: H.times[sl] }; m.eating = !m.eating; a[id] = m; });
}

/* ---------- "I want to cook this on that day" ---------- */
/* The dish takes the place of that meal's main for the same people, rice or rotis are added or dropped
   to suit it, and the day's cooking amounts, shopping and night-before prep follow. The dish is pinned,
   so changing how often you cook won't swap it away. */
function planDish(ds, sl, id, k, how) {
  const r = R[id], before = H.clone(planOf(ds)), h = household(); let replaced = [];
  editPlan(ds, q => {
    const rows = (q.m[sl] = q.m[sl] || []), d = dishDiet(r);
    if (how === 'replace' && isMain(r, sl)) {
      const same = rows.map((row, i) => [row, i]).filter(([row]) => R[row[0]] && isMain(R[row[0]], sl) && dishDiet(R[row[0]]) === d);
      if (same.length) {
        const [row] = same[0]; replaced = same.map(([x]) => x[0]);
        const a = q.assignments?.[sl]; if (a) { if (a[row[0]]) a[id] = a[row[0]]; replaced.forEach(x => delete a[x]); }
        q.m[sl] = rows.filter((x, i) => !same.slice(1).some(([, j]) => j === i)); q.m[sl][same[0][1]] = [id, k];
      } else q.m[sl].push([id, k]);
      const left = q.m[sl].map(x => R[x[0]]).filter(Boolean);
      if (!left.some(needsCarb)) q.m[sl] = q.m[sl].filter(x => !CARBS.includes(x[0]));
      else if (!q.m[sl].some(x => CARBS.includes(x[0]))) q.m[sl].push([CARBS[0], 1]);
    } else { q.m[sl].push([id, k]); if (needsCarb(r) && !q.m[sl].some(x => CARBS.includes(x[0]))) q.m[sl].push([CARBS[0], 1]); }
    addPairs(q.m[sl]);
    ((q.pin ||= {})[sl] ||= []).includes(id) || q.pin[sl].push(id);
    if (q.s === 1 && sl === 'l' && sameRows(before.m.l, before.m.d)) { q.m.d = H.clone(q.m.l); (q.assignments ||= {}).d = H.clone(q.assignments?.l || {}); }
    delete q.auto;
  });
  const p = planOf(ds), when = ds === todayStr() ? 'today' : fmtDay(parseYmd(ds)), miss = status(r).missing.map(tokLabel);
  const fits = (sl !== 'b' || breakfastFits(r, p.s)) && (sl !== 'l' || lunchFits(r, p.s));
  const parts = [r.title + ' is ' + when + '’s ' + SLOT[sl].toLowerCase() +
    (replaced.length ? ' in place of ' + replaced.map(x => R[x].title).join(' and ') : '') + '.'];
  if (p.s === 1 && sl === 'l' && linkedDinner(p)) parts.push('Cooking once, so it is dinner too; cook ' + nice(mealServings(p, 'l', r, k) + mealServings(p, 'd', r, k)) + ' servings.');
  else parts.push('Cook ' + nice(mealServings(p, sl, r, k)) + ' servings.');
  if (!fits) parts.push(sl === 'b' ? 'It takes longer than your ' + ['', '20', '30'][p.s] + '-minute breakfast window when cooking ' + ['', 'once', 'twice'][p.s] + '; start earlier or switch this day to 3 times.' : 'It doesn’t pack as well as most lunch-box dishes; eat it fresh if you can, or switch this day to 3 times.');
  if (soaks(r)) parts.push('It needs soaking: start the night before.');
  if (miss.length) parts.push('Missing: ' + miss.join(', ').toLowerCase() + ' (on your shopping list).');
  if (!H.attendees(p, sl, h).some(m => H.compatible(m, r))) parts.push('Nobody eating this meal can have it; tick who is eating on Today.');
  planNote = parts.join(' ');
  return planNote;
}
