/* Prep ahead and batch prep.
   Soaking, sprouting, marinating and dough resting that must start hours or days before a planned meal,
   timed from each meal's eating time; batch-prep suggestions for the next few days; and a fridge switch
   (working / off until a date) that changes what is safe to do ahead. */
const PREP_AHEAD = (D.advance && D.advance.recipes) || {};
const BATCH = D.batch || { components: [], noFridge: [] };
const SLEEP_FROM = 23 * 60, WAKE = 6 * 60 + 30;

/* ---------- fridge ---------- */
function fridgeOn(ds) {
  if (!household().fridge) return false;
  const off = S.set.fridgeOff;
  if (!off) return true;
  if (off === "off") return false;
  return ds >= off;
}
function fridgeBackLabel() {
  const off = S.set.fridgeOff;
  if (!off || off === "off") return "";
  return off === ymd(new Date(Date.now() + 864e5)) ? "tomorrow" : DAYS[dayIdx(parseYmd(off))] + " " + parseYmd(off).getDate();
}

/* ---------- quantities ---------- */
const findItem = (r, word) => (r.ingredients || []).flatMap(g => typeof g === "string" ? [] : g.items).find(i => i.name.toLowerCase().includes(word.toLowerCase()));
function dryGrams(r, word, servings) {
  const it = findItem(r, word); if (!it || !it.q) return null;
  let q; try { q = KitchenCore.scaleQuantity(it.q, servings / (r.yield || 1)); } catch (e) { return null; }
  const m = q.match(/(\d+(?:\.\d+)?)\s*g dry/) || q.match(/from about (\d+(?:\.\d+)?)\s*g/) || q.match(/(\d+(?:\.\d+)?)\s*g\b/);
  return m ? Math.round(+m[1] / 5) * 5 || +m[1] : null;
}
function itemQty(r, word, servings) { const it = findItem(r, word); return it ? KitchenCore.smartQuantity(it, servings / (r.yield || 1)) : ""; }
const mlText = ml => ml >= 1000 ? (Math.round(ml / 100) / 10) + " L" : (Math.round(ml / 50) * 50) + " ml";
const hrs = h => h < 1 ? Math.round(h * 60) + " min" : (h % 1 ? KitchenCore.format(Math.round(h * 4) / 4) : h) + (h === 1 ? " hour" : " hours");
const range = a => a[0] === a[1] ? hrs(a[0]) : (a[0] < 1 || a[1] < 1 ? hrs(a[0]) + "–" + hrs(a[1]) : KitchenCore.format(a[0]) + "–" + KitchenCore.format(a[1]) + " hours");

/* One sentence saying exactly what to do, with scaled amounts. */
function advWhat(r, t, servings, fridge) {
  const g = t.item ? dryGrams(r, t.item, servings) : null, q = g ? g + " g " : (t.item ? itemQty(r, t.item, servings) + " " : "");
  if (t.kind === "soak") return "Soak " + q + t.what + (t.water && g ? " in about " + mlText(g * t.water) + " water" : t.water === 0 ? "" : " in plenty of water") + " for " + range(t.hours) + (t.max > t.hours[1] ? " (up to " + hrs(t.max) + " is fine)" : "") + ".";
  if (t.kind === "sprout") return "Soak " + q + t.what + (g ? " in about " + mlText(g * (t.water || 3)) + " water" : "") + " for " + range(t.hours) + ", then drain and sprout " + range(t.sprout) + ".";
  if (t.kind === "marinate") { const max = fridge ? t.fridgeMax : t.roomMax; return "Marinate " + (q.trim() ? q : "") + t.what + " for " + range(t.hours) + (fridge ? (max > t.hours[1] ? "; covered in the fridge it can go up to " + hrs(max) : ", no longer") : "; fridge off, so no more than " + hrs(max) + ", covered, in the coolest spot") + "."; }
  if (t.kind === "rest") return "Make the " + t.what + " and rest it " + range(t.hours) + ".";
  return t.what;
}

/* ---------- timing ---------- */
const atMin = (ds, m) => { const d = parseYmd(ds); d.setHours(0, 0, 0, 0); return new Date(d.getTime() + m * 60000); };
function sessionDeadline(p, sl) {
  const se = (SESS[p.s] || []).find(x => x.slots.includes(sl)) || { slots: [sl] };
  return Math.min(...se.slots.filter(x => (p.m[x] || []).length).map(x => slotTime(p, x)).concat(slotTime(p, sl)));
}
const inSleep = d => { const m = d.getHours() * 60 + d.getMinutes(); return m >= SLEEP_FROM || m < WAKE; };
function whenLabel(d, now) {
  const day = Math.round((new Date(d).setHours(0, 0, 0, 0) - new Date(now).setHours(0, 0, 0, 0)) / 864e5);
  const hm = hhmm(d.getHours() * 60 + d.getMinutes()), h = d.getHours();
  const part = h >= 21 || h < 4 ? "night" : h >= 17 ? "evening" : h < 12 ? "morning" : "";
  if (day === 0) return (h >= 21 ? "tonight " : part ? "this " + part + " " : "today ") + hm;
  if (day === 1) return "tomorrow " + (part ? part + " " : "") + hm;
  return DAYS[dayIdx(d)] + " " + (part ? part + " " : "") + hm;
}
/* Latest convenient start inside [from, by]: avoid 23:00–06:30 by moving to 22:30 the evening before,
   or to 06:30 if the evening is too early. */
function suggestStart(ideal, by, now, from = ideal, preferEvening) {
  if (now > by) return { state: "late" };
  if (now >= ideal && preferEvening !== true) return { state: "now" };
  const eveBefore = d => { const e = new Date(d); if (e.getHours() < 12) e.setDate(e.getDate() - 1); e.setHours(22, 30, 0, 0); return e; };
  if (preferEvening === true) { const e = eveBefore(new Date(by.getTime() - 6 * 36e5)); if (e >= from && e <= by && e > now) return { state: "plan", at: e };
    if (now >= from && !inSleep(now)) return { state: "now" };
    const m = new Date(now); if (m.getHours() >= 12) m.setDate(m.getDate() + 1); m.setHours(6, 30, 0, 0);
    if (m >= from && m <= by) return { state: "plan", at: m }; }
  if (preferEvening === "anchor") {
    // soaking fits around the day: before bed (22:30) or first thing (06:45), whichever is latest in the window
    const c = []; for (let d = new Date(by); d >= new Date(from.getTime() - 864e5); d = new Date(d.getTime() - 864e5)) { const e = new Date(d); e.setHours(22, 30, 0, 0); const m = new Date(d); m.setHours(6, 45, 0, 0); c.push(e, m); }
    const ok = c.filter(x => x >= new Date(from.getTime() - 36e5) && x <= by && x > now).sort((a, b) => b - a)[0];
    if (ok) return { state: "plan", at: ok };
  }
  let t = new Date(by);
  if (inSleep(t)) {
    const eve = eveBefore(t), morn = new Date(t); if (morn.getHours() >= 12) morn.setDate(morn.getDate() + 1); morn.setHours(6, 30, 0, 0);
    if (eve >= from && eve <= by && eve > now) t = eve;
    else if (morn >= from && morn <= by) t = morn;
    else if (now >= from || eve <= now && now <= by) return { state: "now" };
    else if (eve >= new Date(from.getTime() - 3 * 36e5) && eve <= by && eve > now) return { state: "plan", at: eve, long: eve < new Date(from.getTime() - 36e5) };
    else t = new Date(ideal);
  }
  return { state: t <= now ? "now" : "plan", at: t };
}

/* Every prep task for the next 4 days that hasn't been eaten yet. */
function prepTasks(now = new Date()) {
  const out = [], curd = {};
  for (let i = 0; i < 4; i++) {
    const d = new Date(now); d.setDate(d.getDate() + i); const ds = ymd(d), p = planOf(ds), linked = linkedDinner(p);
    SLOTS.forEach(sl => {
      if (sl === "d" && linked) return; // cooked with lunch
      const eat = atMin(ds, slotTime(p, sl));
      if (eaten(ds, sl) || now > new Date(eat.getTime() + 30 * 60000)) return;
      (p.m[sl] || []).forEach(([id, k], idx) => {
        const r = R[id]; if (!r) return;
        let n = mealServings(p, sl, r, k); if (linked && sl === "l") n += mealServings(p, "d", r, k);
        if (!(n > 0)) return;
        const cookStart = atMin(ds, sessionDeadline(p, sl) - (r.minutes || 45));
        (PREP_AHEAD[id] || []).forEach((t, ti) => {
          const fridge = fridgeOn(ds);
          let lo = t.hours[0], hi = t.max || t.hours[1];
          if (t.kind === "sprout") { lo = t.hours[0] + t.sprout[0]; hi = t.hours[1] + t.sprout[1]; }
          if (t.kind === "marinate") hi = Math.max(t.hours[0], fridge ? t.fridgeMax : t.roomMax);
          const ideal = t.kind === "sprout" ? t.hours[1] + t.sprout[1] : t.hours[1];
          const by = new Date(cookStart.getTime() - lo * 36e5), from = new Date(cookStart.getTime() - hi * 36e5), idealFrom = new Date(cookStart.getTime() - Math.min(hi, ideal) * 36e5);
          out.push({ key: "adv:" + ds + ":" + sl + ":" + id + ":" + ti, ds, sl, idx, id, r, t, n, fridge, by, from, cookStart, eat, s: suggestStart(idealFrom, by, now, from, t.kind === "soak" || t.kind === "sprout" ? "anchor" : false), what: advWhat(r, t, n, fridge) });
        });
        if (r.needs.some(x => x.split("|").includes("curd"))) {
          const it = (r.ingredients || []).flatMap(g => typeof g === "string" ? [] : g.items).filter(x => /\bcurd\b/i.test(x.name) && !/hung/i.test(x.name));
          let g = 0; it.forEach(x => { try { const q = KitchenCore.scaleQuantity(x.q, n / (r.yield || 1)); const m = q.match(/(\d+(?:\.\d+)?)\s*g\b/), t = q.match(/(\d+(?:\.\d+)?)\s*tbsp/); g += m ? +m[1] : t ? +t[1] * 15 : 0; } catch (e) {} });
          const c = curd[ds] || (curd[ds] = { g: 0, dishes: [], first: cookStart, sl });
          c.g += g; if (!c.dishes.includes(r.title)) c.dishes.push(r.title); if (cookStart < c.first) { c.first = cookStart; c.sl = sl; }
        }
      });
    });
  }
  Object.entries(curd).forEach(([ds, c]) => {
    const t = D.advance.curd || { hours: [6, 10] };
    const by = new Date(c.first.getTime() - t.hours[0] * 36e5), from = new Date(c.first.getTime() - (fridgeOn(ds) ? 40 : 16) * 36e5);
    const g = Math.max(100, Math.ceil(c.g * 1.2 / 50) * 50);
    out.push({ key: "adv:" + ds + ":curd", ds, sl: c.sl, id: "x-curd", t: { kind: "curd", note: t.note, quick: "Too late to set it: buy a packet of fresh curd on the way." }, by, from, cookStart: c.first, s: suggestStart(new Date(c.first.getTime() - t.hours[1] * 36e5), by, new Date(), from, true),
      what: "Set about " + g + " g curd (" + g + " ml milk + 1 tsp curd per 250 ml) for " + c.dishes.slice(0, 3).join(", ") + (c.dishes.length > 3 ? " and more" : "") + ". Takes " + range(t.hours) + "." });
  });
  return out.sort((a, b) => (a.s.at || a.by) - (b.s.at || b.by));
}
const advDone = t => !!S.done[t.key];

/* ---------- batch prep ---------- */
function gramsOf(item, f, unit) {
  let q; try { q = KitchenCore.smartQuantity(item, f); } catch (e) { return null; }
  let m = q.match(/≈ (\d+(?:\.\d+)?)(?:–\d+)? g/) || q.match(/(\d+(?:\.\d+)?)\s*kg\b/) && [0, q.match(/(\d+(?:\.\d+)?)\s*kg\b/)[1] * 1000] || q.match(/(\d+(?:\.\d+)?)\s*g\b/);
  if (m) return +m[1];
  m = q.match(/^([\d.]+\s*[½¼¾⅓⅔⅛⅜⅝⅞]?|[½¼¾⅓⅔⅛⅜⅝⅞])\s*(tbsp|tsp|cups?|cloves?)\b/);
  if (m) { const u = m[2].replace(/s$/, ""), v = (parseFloat(m[1]) || 0) + ({ "½": .5, "¼": .25, "¾": .75, "⅓": 1 / 3, "⅔": 2 / 3, "⅛": .125 }[m[1].trim().slice(-1)] || 0); return unit[u] ? v * unit[u] : null; }
  return null;
}
function batchPlan(now = new Date()) {
  const days = [];
  for (let i = 0; i < 4; i++) { const d = new Date(now); d.setDate(d.getDate() + i); days.push(ymd(d)); }
  const uses = {};
  days.forEach((ds, i) => {
    const p = planOf(ds);
    SLOTS.forEach(sl => {
      if (eaten(ds, sl) || (i === 0 && now > new Date(atMin(ds, slotTime(p, sl)).getTime() + 30 * 60000))) return;
      (p.m[sl] || []).forEach(([id, k]) => {
        const r = R[id]; if (!r) return; const n = mealServings(p, sl, r, k); if (!(n > 0)) return;
        BATCH.components.forEach(c => {
          if (c.recipes && !c.recipes.includes(id)) return;
          const re = new RegExp(c.match, "i"), skip = c.skip ? new RegExp(c.skip, "i") : null;
          const items = (r.ingredients || []).flatMap(g => typeof g === "string" ? [] : g.items).filter(it => re.test(it.name) && !(skip && skip.test(it.name)));
          if (!items.length) return;
          const g = items.reduce((a, it) => a + (gramsOf(it, n / (r.yield || 1), c.unit) || 0), 0);
          (uses[c.id] = uses[c.id] || []).push({ ds, i, sl, title: r.title, g });
        });
      });
    });
  });
  return { days, uses };
}
function batchHTML(now = new Date()) {
  const today = todayStr(), { uses } = batchPlan(now), onToday = fridgeOn(today);
  const backIdx = [1, 2, 3].find(i => fridgeOn(ymd(new Date(now.getTime() + i * 864e5))));
  const groups = [];
  const block = (startIdx, fridge) => BATCH.components.map(c => {
    const keep = fridge ? c.fridgeDays : c.roomHours / 24, list = (uses[c.id] || []).filter(u => u.i >= startIdx && u.i - startIdx <= Math.max(0, Math.floor(keep)) && (fridge || c.roomHours > 0 || u.i === startIdx));
    if (list.length < 2) return "";
    const g = list.reduce((a, u) => a + u.g, 0), all = list.map(u => (u.i === 0 ? "today" : DAYS[dayIdx(parseYmd(u.ds))]) + " " + SLOT[u.sl].toLowerCase() + " (" + u.title + ")");
    const meals = all.length > 4 ? all.slice(0, 4).concat("and " + (all.length - 4) + " more") : all;
    const keeps = fridge ? (c.fridgeDays >= 14 ? "Keeps for weeks" : "Keeps " + c.fridgeDays + " days in the fridge") : c.roomHours >= 72 ? "Keeps " + (c.roomHours >= 336 ? "weeks" : Math.round(c.roomHours / 24) + " days") + " in an airtight jar, no fridge needed" : c.roomHours ? "Keeps about " + c.roomHours + " hours" : "";
    if (!fridge && !c.roomHours) return '<li><b>' + esc(c.title) + '</b> <span class="small">· ' + esc(c.noFridge) + "</span></li>";
    return '<li><b>' + esc(c.title) + (g ? " · about " + (g >= 1000 ? (Math.round(g / 100) / 10) + " kg" : Math.round(g / 5) * 5 + " g") : "") + '</b> for ' + list.length + " meals: " + esc(meals.join(", ")) + '. <span class="small">' + esc(keeps) + ". " + esc(c.how) + "</span></li>";
  }).filter(Boolean).join("");
  if (onToday) { const b = block(0, true); if (b) groups.push("<h4>Batch once for the next 3 days</h4><ul class='plain batch'>" + b + "</ul>"); }
  else {
    const b = block(0, false);
    groups.push("<h4>While the fridge is off</h4><ul class='plain batch'>" + BATCH.noFridge.map(x => "<li>" + esc(x) + "</li>").join("") + "</ul>" + (b ? "<h4>Prep for today only</h4><ul class='plain batch'>" + b + "</ul>" : ""));
    if (backIdx) { const b2 = block(backIdx, true); groups.push("<h4>Once the fridge is back (" + esc(backIdx === 1 ? "tomorrow" : DAYS[dayIdx(new Date(now.getTime() + backIdx * 864e5))]) + ")</h4><p class='small'>" + esc(BATCH.newFridge) + "</p>" + (b2 ? "<ul class='plain batch'>" + b2 + "</ul>" : "<p class='small'>Nothing in the next three days shares enough prep to batch.</p>")); }
  }
  return groups.join("") || '<p class="small">Nothing in the next three days shares enough prep to batch. Plan more days, or cook the same base twice.</p>';
}

/* ---------- Today card ---------- */
function fridgeSwitchHTML() {
  const off = S.set.fridgeOff, on = fridgeOn(todayStr());
  if (!household().fridge) return '<p class="small">No fridge in Settings → Your household, so everything here is planned without one.</p>';
  const tmr = ymd(new Date(Date.now() + 864e5)), day2 = ymd(new Date(Date.now() + 2 * 864e5));
  return '<div class="fridge-row"><span class="lbl-s">Fridge</span><div class="seg" role="group" aria-label="Is the fridge working?">' +
    '<button type="button" data-fridge="" aria-pressed="' + !off + '">Working</button>' +
    '<button type="button" data-fridge="' + tmr + '" aria-pressed="' + (off === tmr) + '">Off till tomorrow</button>' +
    '<button type="button" data-fridge="' + day2 + '" aria-pressed="' + (off === day2) + '">Off 2 days</button>' +
    '<button type="button" data-fridge="off" aria-pressed="' + (off === "off") + '">Off</button></div>' +
    (on ? "" : '<p class="small warn">Fridge off' + (fridgeBackLabel() ? ", back " + esc(fridgeBackLabel()) : "") + ': marinate for at most 2 hours, cook close to eating, and no leftovers.</p>') + "</div>";
}
function taskHTML(t, now) {
  const done = advDone(t), meal = (t.ds === todayStr() ? "today’s " : DAYS[dayIdx(parseYmd(t.ds))] + " ") + SLOT[t.sl].toLowerCase();
  let when;
  if (t.s.state === "late") when = '<span class="tag bad">Late</span> needed by ' + esc(whenLabel(t.by, now));
  else if (t.s.state === "now") when = '<span class="tag warn">Now</span> start before ' + esc(whenLabel(t.by, now));
  else when = '<span class="tag">' + esc(whenLabel(t.s.at, now)) + '</span> <span class="small">window ' + esc(whenLabel(t.from > now ? t.from : now, now)) + " – " + esc(whenLabel(t.by, now)) + "</span>";
  const alarm = t.s.state === "plan" && !done ? (APP && APP.addClockAlarm ? '<button type="button" class="btn sm" data-adv-alarm="' + t.s.at.getHours() + ':' + t.s.at.getMinutes() + '" data-adv-label="' + esc(t.what.slice(0, 60)) + '">⏰ Alarm</button>' :
    '<a class="btn sm" target="_blank" rel="noopener" href="' + esc(calLink(t.s.at, t.what, t.r ? t.r.title : "Kitchen")) + '">⏰ Calendar</a>') : "";
  const late = t.s.state === "late" && !done ? '<p class="small">' + esc(t.t.quick || t.t.noQuick || "Too late for this step now: swap the dish or move it to a later meal.") + '</p><div class="actbar"><button type="button" class="btn sm" data-adv-swap="' + t.ds + "|" + t.sl + "|" + (t.idx ?? -1) + '">Swap ' + esc(t.r ? t.r.title : "dish") + "</button></div>" : "";
  return '<li class="adv-task' + (done ? " done" : "") + (t.s.state === "late" && !done ? " late" : "") + '"><label class="step-check"><input type="checkbox" data-adv-done="' + esc(t.key) + '"' + (done ? " checked" : "") + '><span><b>' + esc(t.what) + "</b> " +
    '<span class="small">For ' + esc(meal) + (t.r ? " · " + '<button type="button" class="linkish" data-open="' + t.id + '">' + esc(t.r.title) + "</button>" : "") + "</span><br>" + when + (t.s.long && !done ? '<br><span class="small">That makes a slightly longer soak than the recipe’s limit: change the water once when you wake up.</span>' : "") + (t.t.note && !done && (t.t.kind !== "marinate" || !t.fridge) ? '<br><span class="small">' + esc(t.t.note) + "</span>" : "") + "</span></label>" + alarm + late + "</li>";
}
function calLink(at, text, title) {
  const f = x => x.getFullYear() + String(x.getMonth() + 1).padStart(2, "0") + String(x.getDate()).padStart(2, "0") + "T" + String(x.getHours()).padStart(2, "0") + String(x.getMinutes()).padStart(2, "0") + "00";
  return "https://calendar.google.com/calendar/render?action=TEMPLATE&text=" + encodeURIComponent("Prep: " + title) + "&details=" + encodeURIComponent(text + "\n" + location.origin + location.pathname + "#today") + "&dates=" + f(at) + "/" + f(new Date(at.getTime() + 600000));
}
function prepCardHTML() {
  const now = new Date(), tasks = prepTasks(now), horizon = new Date(now.getTime() + 36 * 36e5);
  const soon = tasks.filter(t => !advDone(t) ? (t.s.state !== "plan" || t.s.at <= horizon) : t.by > now);
  const later = tasks.filter(t => !soon.includes(t) && !advDone(t));
  const lateN = soon.filter(t => t.s.state === "late" && !advDone(t)).length;
  return '<section class="prep-card' + (lateN ? " has-late" : "") + '" aria-label="Prep ahead"><div class="prep-h"><h3>Prep ahead</h3><span class="small">' +
    (soon.length ? soon.filter(t => !advDone(t)).length + " to do in the next 36 hours" : "Nothing to soak or marinate in the next 36 hours") + "</span></div>" +
    (soon.length ? '<ul class="plain adv-list">' + soon.map(t => taskHTML(t, now)).join("") + "</ul>" : "") +
    (later.length ? '<details class="recipe-details"><summary>Later this week (' + later.length + ")</summary><ul class=\"plain adv-list\">" + later.map(t => taskHTML(t, now)).join("") + "</ul></details>" : "") +
    fridgeSwitchHTML() +
    '<details class="recipe-details" id="batch-prep"><summary>Batch and prep ideas</summary>' + batchHTML(now) + "</details></section>";
}
function prepReminderText() {
  try {
    const now = new Date(), t = prepTasks(now).filter(x => !advDone(x) && x.s.state !== "late" && (x.s.state === "now" || x.s.at - now < 18 * 36e5));
    return t.length ? "Prep: " + t.slice(0, 2).map(x => x.what.replace(/ for \d.*$/, "").replace(/\.$/, "")).join("; ") : "";
  } catch (e) { return ""; }
}
/* Used by the recipe sheet: what this recipe needs ahead, at the servings shown. */
function recipeAheadHTML(r, servings) {
  const fridge = fridgeOn(todayStr()), list = PREP_AHEAD[r.id] || [];
  const rows = list.map(t => "<li><b>" + esc(t.kind === "sprout" ? "2 days ahead" : t.kind === "marinate" ? (fridge && t.fridgeMax >= 8 ? "Night before or " + hrs(t.hours[0]) + " ahead" : hrs(t.hours[0]) + " ahead") : t.hours[0] >= 6 ? "Night before" : hrs(t.hours[0]) + " ahead") + ":</b> " + esc(advWhat(r, t, servings, fridge)) + (t.note && (t.kind !== "marinate" || !fridge) ? ' <span class="small">' + esc(t.note) + "</span>" : "") + (t.quick ? '<br><span class="small"><b>Forgot?</b> ' + esc(t.quick.replace(/^Forgot\?\s*/, "")) + "</span>" : t.noQuick ? '<br><span class="small">' + esc(t.noQuick) + "</span>" : "") + "</li>");
  if (r.needs.some(x => x.split("|").includes("curd"))) rows.push("<li><b>Night before:</b> make sure there is set curd (it takes " + range((D.advance.curd || { hours: [6, 10] }).hours) + ").</li>");
  return rows.length ? '<div class="ahead"><h4>Do ahead</h4><ul class="plain">' + rows.join("") + "</ul></div>" : "";
}

/* ---------- cooking timers (from the ⏱ buttons on recipe steps) ---------- */
const TIMERS = []; let timerTick = null, timerSeq = 0;
function timerBar() {
  let bar = document.getElementById("timer-bar");
  if (!bar) { bar = document.createElement("div"); bar.id = "timer-bar"; bar.setAttribute("aria-live", "polite"); }
  const host = document.querySelector("dialog[open]") || document.body;
  if (bar.parentNode !== host) host.appendChild(bar);
  return bar;
}
function beep() {
  try { const A = window.AudioContext || window.webkitAudioContext, a = new A(); [0, .45, .9].forEach(t => { const o = a.createOscillator(), g = a.createGain(); o.frequency.value = 880; o.connect(g); g.connect(a.destination); g.gain.setValueAtTime(.25, a.currentTime + t); o.start(a.currentTime + t); o.stop(a.currentTime + t + .3); }); } catch (e) {}
  try { navigator.vibrate && navigator.vibrate([400, 200, 400, 200, 400]); } catch (e) {}
}
function renderTimers() {
  const bar = timerBar(), now = Date.now();
  bar.innerHTML = TIMERS.map(t => { const left = Math.max(0, Math.round((t.end - now) / 1000)); return '<div class="tmr' + (left ? "" : " ring") + '"><span>' + esc(t.label) + " · " + (left ? Math.floor(left / 60) + ":" + String(left % 60).padStart(2, "0") : "done") + '</span><button type="button" data-timer-stop="' + t.id + '">' + (left ? "Stop" : "OK") + "</button></div>"; }).join("");
  TIMERS.forEach(t => { if (!t.rang && now >= t.end) { t.rang = true; beep(); } });
  if (!TIMERS.length && timerTick) { clearInterval(timerTick); timerTick = null; }
}
function startTimer(sec, label) {
  TIMERS.push({ id: ++timerSeq, end: Date.now() + sec * 1000, label });
  if (!timerTick) timerTick = setInterval(renderTimers, 1000);
  renderTimers();
}

/* ---------- events ---------- */
document.addEventListener("click", e => {
  const c = s => e.target.closest && e.target.closest(s); let el;
  if ((el = c("[data-timer]"))) { startTimer(+el.dataset.timer, el.dataset.timerLabel || "Timer"); return; }
  if ((el = c("[data-timer-stop]"))) { const i = TIMERS.findIndex(t => t.id === +el.dataset.timerStop); if (i >= 0) TIMERS.splice(i, 1); renderTimers(); return; }
  if ((el = c("[data-fridge]"))) { const v = el.dataset.fridge; apply(s => { if (v) s.set.fridgeOff = v; else delete s.set.fridgeOff; }); return; }
  if ((el = c("[data-adv-swap]"))) { const [ds, sl, i] = el.dataset.advSwap.split("|"); if (+i < 0) return; selDate = ds; cookWhen = ds === todayStr() ? "today" : cookWhen; swapDish(sl, +i); return; }
  if ((el = c("[data-adv-alarm]"))) { const [h, m] = el.dataset.advAlarm.split(":").map(Number); try { APP.addClockAlarm(h, m, "Prep: " + el.dataset.advLabel); el.textContent = "Alarm set"; } catch (err) {} return; }
});
document.addEventListener("change", e => {
  const t = e.target;
  if (t.dataset && t.dataset.advDone) {
    const k = t.dataset.advDone, cut = ymd(new Date(Date.now() - 7 * 864e5));
    apply(s => { if (t.checked) s.done[k] = Date.now(); else delete s.done[k]; Object.keys(s.done).forEach(x => { if (x.startsWith("adv:") && x.slice(4, 14) < cut) delete s.done[x]; }); });
  }
});
