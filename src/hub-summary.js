/* ---------- summary for Dinachari ----------
   Dinachari, the day app at the root of this site (manojhunasimarad.github.io/), shows today's meals,
   what to soak or marinate and what to buy without opening this page. It reads one small key,
   kfz.summary, written here shortly after each change and when the page is hidden. Nothing else in
   this app reads it. Dinachari may tick a prep task: it writes S.done[key] in kfz.state, the same
   field the tick box here writes, and the storage listener below shows that change in any open tab. */
const HUB_KEY = "kfz.summary";
let hubTimer = null;
function hubDay(now, offset) {
  const d = new Date(now); d.setDate(d.getDate() + offset);
  const ds = ymd(d), p = planOf(ds), h = household();
  return { date: ds, sessions: p.s, linked: !!linkedDinner(p), meals: SLOTS.map(sl => ({
    slot: sl, name: SLOT[sl], time: hhmm(slotTime(p, sl)), people: H.attendees(p, sl, h).length, eaten: eaten(ds, sl),
    dishes: (p.m[sl] || []).filter(([id, k]) => dish(id) && mealServings(p, sl, dish(id), k) > 0)
      .map(([id]) => ({ id, title: dish(id).title, mins: (R[id] && R[id].minutes) || null })) })) };
}
function hubSummary(now = new Date()) {
  const ds = todayStr(), p = planOf(ds), me = mePerson(), h = household();
  const nut = only => nsum(SLOTS.filter(sl => !only || eaten(ds, sl)).map(sl => [H.personNutrition(p, sl, me.id, allDishes(), h), 1]));
  let prep = [];
  try {
    prep = prepTasks(now).map(t => ({ key: t.key, what: t.what, kind: t.t.kind, dish: t.r ? t.r.title : "", ds: t.ds, slot: t.sl,
      start: t.s && t.s.at ? +t.s.at : (t.s && t.s.state === "now" ? +now : null), by: +t.by, from: +t.from,
      state: t.s ? t.s.state : "", done: advDone(t), quick: t.t.quick || t.t.noQuick || "" })).slice(0, 20);
  } catch (e) {}
  const label = k => (PDEF[k] ? PDEF[k].label : k);
  const need = planNeeds(2);
  const eat = nut(true), plan = nut(false);
  return {
    v: 1, at: +now, date: ds, days: [hubDay(now, 0), hubDay(now, 1)], prep,
    shop: {
      need: Object.keys(need).filter(k => PDEF[k]).map(k => ({ key: k, label: label(k), for: need[k].slice(0, 3) })),
      bring: Object.keys(S.basket).filter(k => S.basket[k].via === "bring" && PDEF[k]).map(label),
      ordered: Object.keys(S.basket).filter(k => (S.basket[k].via === "order" || S.basket[k].via === "search") && PDEF[k]).map(label),
      low: D.pantry.filter(x => pstate(x.key) === 1 && !S.basket[x.key]).map(x => x.label),
      app: appOf().label
    },
    nutrition: { person: me.name, p: Math.round(eat.p), pPlan: Math.round(plan.p), pTarget: Math.round(+target("p") || 0),
      kcal: Math.round(eat.kcal), kcalPlan: Math.round(plan.kcal), kcalTarget: Math.round(+target("kcal") || 0) },
    people: h.members.length, fridge: fridgeOn(ds), tonight: nightBefore(ds) || "", cooked: Object.keys(S.done).filter(k => !k.startsWith("adv:")).length
  };
}
function writeHubSummary() {
  clearTimeout(hubTimer); hubTimer = null;
  try { localStorage.setItem(HUB_KEY, JSON.stringify(hubSummary())); } catch (e) {}
}
function scheduleHubSummary() { if (!hubTimer) hubTimer = setTimeout(writeHubSummary, 600); }
document.addEventListener("visibilitychange", () => { if (document.visibilityState === "hidden") writeHubSummary(); });

/* Another tab or Dinachari changed the saved data: show it here instead of overwriting it later. */
window.addEventListener("storage", e => {
  if (e.key !== "kfz.state" || !e.newValue || mode === "db" || dirty || writing) return;
  try {
    const next = norm(JSON.parse(e.newValue));
    if (JSON.stringify(next) !== JSON.stringify(S)) { S = next; render(); }
  } catch (err) {}
});
