/* Pantry check (twice a day), "use it first" for fresh food, budget mode and reminders.
   Purchase dates live in S.set.since, check times in S.set.checks, reminder times in S.set.reminders. */
const SHELF = (D.shelf && D.shelf.items) || {}, SHELF_SRC = (D.shelf && D.shelf.sources) || {};
const REMIND_DEFAULT = { on: true, times: ["08:00", "19:30"] };
const reminders = () => Object.assign({}, REMIND_DEFAULT, S.set.reminders || {});
const priceyList = () => S.set.pricey || D.shelf.pricey || [];
const isPricey = k => priceyList().includes(k);
const daysAgo = n => { const d = new Date(); d.setDate(d.getDate() - n); return ymd(d); };

/* purchase dates: set when something goes from Out to Have/Low, cleared when it runs out */
function trackSince(s, k, was, v) {
  if (!SHELF[k]) return;
  s.set.since = s.set.since || {};
  if (v === 2) delete s.set.since[k];
  else if (was === 2) s.set.since[k] = todayStr();
}
function ageOf(k) { const d = (S.set.since || {})[k]; return d ? Math.max(0, Math.round((parseYmd(todayStr()) - parseYmd(d)) / 864e5)) : null; }
function freshness(k) {
  const sh = SHELF[k]; if (!sh || pstate(k) === 2) return null;
  const age = ageOf(k);
  if (age === null) return { k, age, level: "unknown", sh };
  return { k, age, sh, level: age > sh.days ? "old" : age >= sh.days - 1 ? "soon" : "ok" };
}
const useFirst = () => Object.keys(SHELF).map(freshness).filter(f => f && (f.level === "old" || f.level === "soon")).sort((a, b) => (b.age - b.sh.days) - (a.age - a.sh.days));
function freshText(f) {
  if (!f) return "";
  if (f.level === "unknown") return "When did you buy it?";
  const ago = f.age === 0 ? "bought today" : f.age === 1 ? "bought yesterday" : "bought " + f.age + " days ago";
  if (f.level === "old") return ago + " · usually keeps " + f.sh.range + ". Check it before using.";
  if (f.level === "soon") return ago + " · use it today or tomorrow";
  return ago;
}
/* recipes that use an item and that you can cook now */
const usesKey = (r, k) => r.strict.some(t => t.split("|").includes(k)) || (r.needs || []).some(t => t.split("|").includes(k));
const cookWith = k => { const l = D.recipes.filter(r => usesKey(r, k)); return l.filter(r => !status(r).missing.length).concat(l.filter(r => status(r).missing.length === 1)).slice(0, 4); };
/* fresh food (and anything low or out) is worth checking; long-life staples you have are not */
const FRESH_GROUPS = /^(Fresh protein|Dairy|Vegetables)/;
const worthChecking = k => !!SHELF[k] || pstate(k) > 0 || (FRESH_GROUPS.test(PDEF[k].group) && !["onion", "potato", "garlic", "ginger", "ghee", "coconut"].includes(k));

/* budget mode: dishes needing pricey items you don't have are picked last */
const needsPriceyBuy = r => r.strict.some(t => t.split("|").every(k => isPricey(k) && !avail(k)));
const budgetOk = r => !S.set.budget || !needsPriceyBuy(r);

/* what the next meals need, whether you have it or not */
function upcomingKeys() {
  const keys = new Set(), t0 = new Date();
  for (let i = 0; i < 2; i++) {
    const d = new Date(t0); d.setDate(t0.getDate() + i); const ds = ymd(d), p = planOf(ds);
    SLOTS.forEach(sl => { if (i === 0 && eaten(ds, sl)) return; (p.m[sl] || []).forEach(([id, k]) => { const r = R[id]; if (!r || !mealServings(p, sl, r, k)) return; r.strict.forEach(t => { const ks = t.split("|"); keys.add(ks.find(avail) || ks[0]); }); }); });
  }
  return [...keys];
}

/* check times: due when a reminder time has passed today without a check after it */
const checksToday = () => ((S.set.checks || {})[todayStr()] || []);
function checkDue() {
  const now = new Date(), hm = String(now.getHours()).padStart(2, "0") + ":" + String(now.getMinutes()).padStart(2, "0");
  const passed = reminders().times.filter(t => t && t <= hm).sort();
  if (!passed.length) return false;
  const last = passed[passed.length - 1];
  return !checksToday().some(t => t >= last);
}

function checkRow(k, note) {
  const s = pstate(k), f = freshness(k);
  const ask = f && f.level === "unknown" && s < 2;
  return '<li class="ck"><div class="ck-l"><b>' + esc(PDEF[k].label) + "</b>" + (isPricey(k) ? ' <span class="chip">₹</span>' : "") +
    '<span class="small' + (f && f.level === "old" ? " warn" : "") + '">' + esc(note || (f && !ask ? freshText(f) : "")) + "</span>" +
    (ask ? '<label class="small">Bought <select data-bought="' + k + '"><option value="">?</option><option value="0">today</option><option value="1">yesterday</option><option value="2">2 days ago</option><option value="3">3 days ago</option><option value="5">5+ days ago</option></select></label>' : "") +
    '</div><div class="seg ck-s" role="group" aria-label="' + esc(PDEF[k].label) + '">' + PLABEL.map((l, v) => '<button type="button" data-pset="' + k + "|" + v + '" aria-pressed="' + (s === v) + '">' + l + "</button>").join("") + "</div></li>";
}
function checkHTML() {
  const first = useFirst(), firstKeys = first.map(f => f.k), need = upcomingKeys().filter(k => !firstKeys.includes(k) && worthChecking(k));
  const fresh = Object.keys(SHELF).filter(k => pstate(k) < 2 && !firstKeys.includes(k) && !need.includes(k));
  const done = checksToday();
  const ideas = [...new Set(firstKeys.flatMap(k => cookWith(k).map(r => r.id)))].slice(0, 5);
  return '<p class="small">' + (done.length ? "Checked today at " + done.join(" and ") + "." : "Not checked yet today.") + " Tap Have, Low or Out. It takes a minute and keeps the app honest about your kitchen.</p>" +
    (first.length ? '<h3>Use these first</h3><ul class="ck-list">' + first.map(f => checkRow(f.k)).join("") + "</ul>" +
      (ideas.length ? '<p class="small">Cook now with them:</p><div class="needs">' + ideas.map(id => '<button type="button" class="chip p" data-open="' + id + '">' + esc(R[id].title) + (status(R[id]).missing.length ? " (needs 1 more)" : "") + "</button>").join("") + "</div>" : "") : "") +
    '<h3>Needed today and tomorrow</h3>' + (need.length ? '<ul class="ck-list">' + need.map(k => checkRow(k)).join("") + "</ul>" : '<p class="empty">Nothing planned.</p>') +
    (fresh.length ? '<h3>Other fresh food you have</h3><ul class="ck-list">' + fresh.map(k => checkRow(k)).join("") + "</ul>" : "") +
    '<div class="actbar"><button type="button" class="btn primary" data-check-done>Done</button><button type="button" class="btn" data-go="pantry" data-close-check>Full pantry</button></div>' +
    '<details class="recipe-details"><summary>Where the keeping times come from</summary><p class="small">Times are for a fridge at 4 °C or colder unless noted, and are guidance, not a guarantee. If something smells, looks or feels off, throw it out.</p>' +
    Object.values(SHELF_SRC).map(s => '<p><a href="' + esc(s.url) + '" target="_blank" rel="noopener">' + esc(s.title) + "</a></p>").join("") + "</details>";
}
function openCheck() { $("#check-in").innerHTML = '<div class="dlg-top"><h2 id="check-title">Pantry check</h2><button class="close" type="button" data-close="checkdlg" aria-label="Close">×</button></div><div id="check-body">' + checkHTML() + "</div>"; openSheet("checkdlg"); }
function refreshCheck() { const b = $("#check-body"); if (b && $("#checkdlg").open) b.innerHTML = checkHTML(); }
window.openCheck = openCheck;

/* the card at the top of Today */
function checkCardHTML() {
  const first = useFirst(), due = checkDue(), done = checksToday(), r = reminders();
  const next = r.on ? r.times.filter(Boolean).sort().find(t => t > new Date().toTimeString().slice(0, 5)) : null;
  return '<div class="ck-card' + (due ? " due" : "") + '"><div><b>' + (due ? "Pantry check due" : done.length ? "Pantry checked at " + done[done.length - 1] : "Pantry check") + "</b>" +
    '<span class="small">' + (first.length ? "Use first: " + first.slice(0, 4).map(f => esc(PDEF[f.k].label)).join(", ") + (first.length > 4 ? " +" + (first.length - 4) : "") : "Nothing fresh is getting old.") + (next ? " · next check " + next : "") + "</span></div>" +
    '<button type="button" class="btn' + (due ? " primary" : "") + '" data-open-check>' + (due ? "Check now" : "Check") + "</button></div>";
}

/* reminder text for the Android notification, kept in step with the pantry */
let lastReminderSync = "";
function syncReminders() {
  if (!APP || !APP.setReminders) return;
  const r = reminders(), first = useFirst(), need = upcomingKeys().filter(k => !avail(k));
  const text = [first.length ? "Use first: " + first.slice(0, 3).map(f => PDEF[f.k].label).join(", ") : "", need.length ? "Missing for your plan: " + need.slice(0, 3).map(k => PDEF[k].label).join(", ") : ""].filter(Boolean).join(" · ") || "Two-minute check of what you have.";
  const payload = JSON.stringify({ on: !!r.on, times: r.times.filter(Boolean), text });
  if (payload === lastReminderSync) return;
  lastReminderSync = payload;
  try { APP.setReminders(payload); } catch (e) {}
}
function calendarLink(t) {
  const d = new Date(); const [h, m] = t.split(":").map(Number); d.setHours(h, m, 0, 0); if (d < new Date()) d.setDate(d.getDate() + 1);
  const f = x => x.getFullYear() + String(x.getMonth() + 1).padStart(2, "0") + String(x.getDate()).padStart(2, "0") + "T" + String(x.getHours()).padStart(2, "0") + String(x.getMinutes()).padStart(2, "0") + "00";
  const e = new Date(d.getTime() + 10 * 60000);
  return "https://calendar.google.com/calendar/render?action=TEMPLATE&text=" + encodeURIComponent("Pantry check (Kitchen From Zero)") + "&details=" + encodeURIComponent(location.origin + location.pathname + "#check") + "&dates=" + f(d) + "/" + f(e) + "&ctz=" + encodeURIComponent(Intl.DateTimeFormat().resolvedOptions().timeZone || "Asia/Kolkata") + "&recur=" + encodeURIComponent("RRULE:FREQ=DAILY");
}
function remindersHTML() {
  const r = reminders();
  return '<section class="sec"><h2>Pantry check reminders</h2><p class="small">Twice a day the app asks you to tick what you have, so it never suggests food you’ve run out of and warns you before fresh food goes bad.</p>' +
    '<label class="toggle"><input type="checkbox" data-remind-on' + (r.on ? " checked" : "") + "> Remind me</label>" +
    '<div class="fgrid">' + r.times.map((t, i) => '<label>' + (i ? "Evening" : "Morning") + ' check<input type="time" data-remind-time="' + i + '" value="' + esc(t) + '"></label>').join("") + "</div>" +
    (APP && APP.setReminders ? '<p class="small">The app shows a notification at these times. Tap it to open the check.</p>' + (APP.addClockAlarm ? '<div class="actbar">' + r.times.map((t, i) => '<button type="button" class="btn sm" data-clock="' + i + '">Also set a Clock alarm at ' + esc(t) + "</button>").join("") + "</div>" : "")
      : '<p class="small">Notifications need the Android app. On this device you can add daily calendar reminders instead:</p><div class="actbar">' + r.times.map(t => '<a class="btn sm" target="_blank" rel="noopener" href="' + esc(calendarLink(t)) + '">Add ' + esc(t) + " to Google Calendar</a>").join("") + "</div>") +
    "</section>";
}
function budgetHTML() {
  const pricey = priceyList();
  const options = [...new Set(pricey.concat(["mutton", "prawns", "fish", "chicken", "chickenbl", "paneer", "cheese", "cream", "butter", "mushrooms", "cashews", "saffron", "ghee", "coconut"]))].filter(k => PDEF[k]);
  return '<section class="sec"><h2>Budget</h2><label class="toggle"><input type="checkbox" data-budget' + (S.set.budget ? " checked" : "") + '> Budget mode: Shuffle and Surprise avoid dishes that need a pricey item you don’t have</label>' +
    '<p class="small">Pricey items (tap to change your list; they’re marked ₹ in Shopping and the pantry check):</p><div class="needs">' +
    options.map(k => '<button type="button" class="chip' + (pricey.includes(k) ? " on" : "") + '" data-pricey="' + k + '" aria-pressed="' + pricey.includes(k) + '">' + esc(PDEF[k].label) + "</button>").join("") + "</div></section>";
}

/* events */
document.addEventListener("click", e => {
  const c = s => e.target.closest && e.target.closest(s); let el;
  if (c("[data-open-check]")) { openCheck(); return; }
  if ((el = c("[data-pset]"))) { const [k, v] = el.dataset.pset.split("|"); apply(s => setPantry(s, k, +v)); refreshCheck(); return; }
  if (c("[data-check-done]")) { const hm = new Date().toTimeString().slice(0, 5), ds = todayStr(); apply(s => { const ch = (s.set.checks = s.set.checks || {}); (ch[ds] = ch[ds] || []).push(hm); const cut = daysAgo(14); Object.keys(ch).forEach(d => { if (d < cut) delete ch[d]; }); }); closeD("checkdlg"); return; }
  if (c("[data-close-check]")) { closeD("checkdlg"); return; }
  if ((el = c("[data-pricey]"))) { const k = el.dataset.pricey; apply(s => { const l = (s.set.pricey || priceyList()).slice(); s.set.pricey = l.includes(k) ? l.filter(x => x !== k) : l.concat(k); }); return; }
  if ((el = c("[data-clock]"))) { const t = reminders().times[+el.dataset.clock]; if (t && APP && APP.addClockAlarm) { const [h, m] = t.split(":").map(Number); try { APP.addClockAlarm(h, m, "Pantry check"); } catch (err) {} } return; }
});
document.addEventListener("change", e => {
  const t = e.target;
  if (t.dataset.bought != null && t.value !== "") { const k = t.dataset.bought, n = +t.value; apply(s => { (s.set.since = s.set.since || {})[k] = daysAgo(n); }); refreshCheck(); return; }
  if (t.dataset.remindOn != null) { apply(s => { s.set.reminders = Object.assign(reminders(), { on: t.checked }); }); return; }
  if (t.dataset.remindTime != null && t.value) { const i = +t.dataset.remindTime; apply(s => { const r = reminders(); r.times = r.times.slice(); r.times[i] = t.value; s.set.reminders = r; }); return; }
  if (t.dataset.budget != null) { apply(s => { s.set.budget = t.checked; }); return; }
});
