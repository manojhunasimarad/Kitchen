/* Kitchen AI: optional Gemini assistant. The API key stays in this browser's localStorage only:
   it is never written to S (so it is not synced, exported or committed). */
const AI = {
  KEY: "kfz.gemini", MODEL: "kfz.gemini.model", DEFAULT_MODEL: "gemini-flash-latest",
  BASE: "https://generativelanguage.googleapis.com/v1beta/",
  chat: [], recipeId: null, busy: false, photo: null
};
const aiGet = k => { try { return localStorage.getItem(k) || ""; } catch (e) { return ""; } };
const aiSet = (k, v) => { try { v ? localStorage.setItem(k, v) : localStorage.removeItem(k); } catch (e) {} };
const aiKey = () => aiGet(AI.KEY);

const AI_RULES = [
  "You are the cooking assistant inside Kitchen From Zero, a meal planner for a shared household in Bengaluru, India.",
  "Answer cooking, pantry, meal-planning, shopping and kitchen-cleaning questions only. Politely decline anything else.",
  "Prefer the app's own recipes (listed in the context) and what is in the pantry. When you suggest an app recipe, put its exact id in `recipes`.",
  "Never suggest beef or pork. Respect each person's diet: veg means no meat, fish or egg; egg means vegetarian plus eggs; nonveg eats chicken, mutton, fish and prawns.",
  "Answer like an experienced Indian home cook standing next to them: concrete and specific. Give amounts in grams (they have a kitchen scale) or spoons, flame level (low/medium/high), minutes, whistles, and what it should look, smell or feel like when each stage is done.",
  "Use the CURRENT RECIPE amounts (already scaled to the servings they are cooking) and its steps first. When you add a number the recipe doesn't give, mark it with ≈.",
  "Always mention anything that must be done ahead (soaking, sprouting, marinating, setting curd, resting dough) and how long, using the PREP AHEAD list when it is given. Respect the FRIDGE status: without a fridge, no marinating over 2 hours, no keeping cooked food over 2 hours, no batch cooking for later days.",
  "Food-safety questions (raw meat, leftovers kept out, reheating, spoiled or sour-smelling food, allergies, pregnancy): be cautious, say when to throw food away, and put the warning in `caution`. Never say food is definitely safe.",
  "No medical or diagnosis advice. Be practical: numbered steps for methods, '- ' lists for options, and enough detail to cook without guessing. Use Indian ingredient names where natural.",
  "If you are unsure, say so instead of guessing."
].join("\n");

function aiCatalogue() {
  return D.recipes.map(r => {
    const m = status(r).missing;
    return r.id + " | " + r.title + " | " + (r.diet || "") + " | " + (r.course || "") + " | " + (r.minutes || r.time || "") + " min | missing:" + (m.length ? m.slice(0, 4).map(k => k.split("|")[0]).join(",") + (m.length > 4 ? "+" + (m.length - 4) : "") : "none");
  }).join("\n");
}
function aiPantry() {
  const have = [], low = [];
  D.pantry.forEach(p => { const s = pstate(p.key); if (s === 0) have.push(p.label); else if (s === 1) low.push(p.label); });
  let first = []; try { first = useFirst().map(f => PDEF[f.k].label); } catch (e) {}
  return "Have: " + (have.join(", ") || "nothing marked") + "\nRunning low: " + (low.join(", ") || "none") + "\nUse first (getting old): " + (first.join(", ") || "none");
}
function aiHousehold() {
  try { const h = household(); return h.members.map(m => m.name + " (" + m.diet + ")").join(", "); } catch (e) { return ""; }
}
function aiRecipeText(id, servings) {
  const r = D.recipes.find(x => x.id === id); if (!r) return "";
  const n = servings || (typeof dlgId !== "undefined" && dlgId === id ? dlgServ : setv("people")), f = n / (r.yield || 1);
  const ing = (r.ingredients || []).map(g => typeof g === "string" ? g : (g.group ? g.group + ": " : "") + (g.items || []).map(i => i.name + (i.note ? " (" + i.note + ")" : "") + " " + KitchenCore.smartQuantity(i, f)).join("; ")).join("\n");
  const steps = (r.steps || []).map((s, i) => (i + 1) + ". " + KitchenCore.stepText(r, i, n, true).replace(/[\uE000\uE001]/g, "")).join("\n");
  const ahead = ((D.advance && D.advance.recipes[r.id]) || []).map(t => "- " + advWhat(r, t, n, fridgeOn(todayStr())) + (t.quick ? " " + t.quick : "")).join("\n");
  return "CURRENT RECIPE (" + r.id + "): " + r.title + "\nCooking for: " + n + " servings (" + (r.servingLabel || "1 serving") + " each) · " + (r.time || "") + (r.uses ? " · uses " + r.uses : "") +
    (ahead ? "\nDo ahead:\n" + ahead : "") + "\nIngredients (scaled):\n" + ing + "\nMethod (scaled):\n" + steps +
    ((r.cues || []).length ? "\nChecks: " + r.cues.join(" | ") : "") + ((r.tips || []).length ? "\nTips: " + r.tips.map(t => t.title + ": " + t.text).join(" | ") : "") +
    ((r.var || []).length ? "\nVariations: " + r.var.join(" | ") : "") + (r.keeps ? "\nKeeps: " + r.keeps : "");
}
function aiPlanText() {
  try {
    const lines = [];
    for (let i = 0; i < 2; i++) { const d = new Date(); d.setDate(d.getDate() + i); const ds = ymd(d), p = planOf(ds);
      lines.push((i ? "Tomorrow" : "Today") + " (" + DAYS[dayIdx(d)] + "): " + SLOTS.map(sl => SLOT[sl] + " " + ((p.m[sl] || []).filter(([id]) => R[id]).map(([id, k]) => R[id].title + " ×" + nice(mealServings(p, sl, R[id], k))).join(", ") || "—")).join(" · ")); }
    const t = prepTasks(new Date()).filter(x => !advDone(x)).slice(0, 6).map(x => "- " + x.what + " (for " + (x.ds === todayStr() ? "today" : DAYS[dayIdx(parseYmd(x.ds))]) + " " + SLOT[x.sl].toLowerCase() + "; " + (x.s.state === "late" ? "LATE" : x.s.state === "now" ? "start now" : "start " + whenLabel(x.s.at, new Date())) + ")");
    return "PLAN\n" + lines.join("\n") + (t.length ? "\nPREP AHEAD\n" + t.join("\n") : "") + "\nFRIDGE: " + (fridgeOn(todayStr()) ? "working" : "NOT working" + (fridgeBackLabel() ? " (back " + fridgeBackLabel() + ")" : "")) + "\nNow: " + new Date().toLocaleString("en-IN", { weekday: "short", hour: "2-digit", minute: "2-digit" });
  } catch (e) { return ""; }
}
function aiContext() {
  return "Today: " + todayStr() + "\nHousehold: " + aiHousehold() + "\nKitchen: kitchen scale, 4 gas burners, induction, 3 L and 5 L pressure cookers, air fryer, sandwich maker, pull-cord chopper.\n\n" + aiPlanText() + "\n\nPANTRY\n" + aiPantry() + "\n\n" + (AI.recipeId ? aiRecipeText(AI.recipeId) + "\n\n" : "") + "APP RECIPES (id | title | diet | course | time | ingredients missing from the pantry)\n" + aiCatalogue();
}

const AI_SCHEMA = { type: "OBJECT", properties: {
  answer: { type: "STRING", description: "The reply to show the cook. Plain text; use '- ' lines for lists." },
  recipes: { type: "ARRAY", items: { type: "STRING" }, description: "Ids of app recipes you recommend, if any (max 5)." },
  caution: { type: "STRING", description: "A food-safety warning, or empty." } }, required: ["answer"] };
const PHOTO_SCHEMA = { type: "OBJECT", properties: {
  found: { type: "ARRAY", items: { type: "OBJECT", properties: { key: { type: "STRING" }, sure: { type: "BOOLEAN" } }, required: ["key"] } },
  note: { type: "STRING" } }, required: ["found"] };

async function aiPost(model, body, key) {
  const res = await fetch(AI.BASE + "models/" + encodeURIComponent(model) + ":generateContent", {
    method: "POST", headers: { "Content-Type": "application/json", "x-goog-api-key": key }, body: JSON.stringify(body) });
  let data = null; try { data = await res.json(); } catch (e) {}
  if (!res.ok) { const err = new Error((data && data.error && data.error.message) || ("HTTP " + res.status)); err.status = res.status; throw err; }
  return data;
}
async function aiPickModel(key) {
  const res = await fetch(AI.BASE + "models?pageSize=200", { headers: { "x-goog-api-key": key } });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) { const err = new Error((data.error && data.error.message) || "HTTP " + res.status); err.status = res.status; throw err; }
  const ver = n => (n.match(/(\d+(?:\.\d+)?)/) || [0, 0])[1] * 1;
  const ok = (data.models || []).filter(m => (m.supportedGenerationMethods || []).includes("generateContent") && /flash/.test(m.name) && !/image|tts|audio|live|embed|thinking-exp/.test(m.name));
  ok.sort((a, b) => (/preview|exp/.test(a.name) - /preview|exp/.test(b.name)) || (/lite/.test(a.name) - /lite/.test(b.name)) || ver(b.name) - ver(a.name));
  if (!ok.length) throw new Error("No Gemini Flash model is available for this key.");
  return ok[0].name.replace(/^models\//, "");
}
async function aiGenerate(body) {
  const key = aiKey(); if (!key) throw new Error("no-key");
  let model = aiGet(AI.MODEL) || AI.DEFAULT_MODEL;
  try { return await aiPost(model, body, key); }
  catch (e) {
    if (e.status !== 404 && !(e.status === 400 && /model/i.test(e.message))) throw e;
    model = await aiPickModel(key); aiSet(AI.MODEL, model);
    return aiPost(model, body, key);
  }
}
function aiJSON(data) {
  const parts = (((data || {}).candidates || [])[0] || {}).content?.parts || [];
  const txt = parts.filter(p => !p.thought && p.text).map(p => p.text).join("");
  if (!txt) { const why = data?.promptFeedback?.blockReason || data?.candidates?.[0]?.finishReason || "empty reply"; throw new Error("Gemini gave no answer (" + why + ")."); }
  try { return JSON.parse(txt); } catch (e) { return { answer: txt }; }
}
function aiErrText(e) {
  if (e.message === "no-key") return "Add your free Gemini key first.";
  if (e.status === 400 && /key/i.test(e.message) || e.status === 403) return "Gemini didn't accept the key. Check it in AI Studio, or remove it and paste it again.";
  if (e.status === 429) return "The free Gemini limit is used up for now. Try again in a minute, or tomorrow if the daily limit is reached.";
  if (e.status >= 500) return "Gemini is busy right now. Try again in a moment.";
  if (e instanceof TypeError) return "Couldn't reach Gemini. Check your internet connection.";
  return "Something went wrong: " + e.message;
}

/* ---------- UI ---------- */
const AI_QUICK = [
  ["What can I cook now?", "What can I cook right now with what's in my pantry? Give the best 3 options for the household."],
  ["Use what's getting old", "Which items should I use up first, and what should I cook with them today?"],
  ["Plan tomorrow", "Suggest breakfast, lunch and dinner for tomorrow from the app's recipes, using the pantry and keeping it simple."],
  ["Something's gone wrong", "My dish has gone wrong. Ask me what happened, then help me fix it."]
];
function aiFmt(t) {
  return esc(t).replace(/\*\*(.+?)\*\*/g, "<b>$1</b>").split(/\n/).map(l => /^\s*[-•*]\s+/.test(l) ? "<li>" + l.replace(/^\s*[-•*]\s+/, "") + "</li>" : l ? "<p>" + l + "</p>" : "").join("").replace(/(<li>.*?<\/li>)+/g, m => "<ul>" + m + "</ul>");
}
function aiMsgHTML(m) {
  if (m.role === "user") return '<div class="ai-msg me">' + (m.img ? '<img src="' + m.img + '" alt="Your photo">' : "") + "<p>" + esc(m.text) + "</p></div>";
  if (m.role === "error") return '<div class="ai-msg err" role="alert"><p>' + esc(m.text) + "</p></div>";
  const ids = (m.recipes || []).filter(id => D.recipes.some(r => r.id === id)).slice(0, 5);
  return '<div class="ai-msg bot">' + aiFmt(m.text) + (m.caution ? '<p class="ai-caution">⚠ ' + esc(m.caution) + "</p>" : "") +
    (ids.length ? '<div class="needs">' + ids.map(id => '<button type="button" class="chip" data-ai-recipe="' + id + '">' + esc(D.recipes.find(r => r.id === id).title) + "</button>").join("") + "</div>" : "") +
    (m.found ? aiFoundHTML(m) : "") + "</div>";
}
function aiFoundHTML(m) {
  if (!m.found.length) return "<p class='small'>Nothing from the pantry list was recognised.</p>";
  return '<form class="ai-found" data-ai-found="' + m.id + '"><p class="small">Tick what you really have, then save. Nothing changes until you do.</p>' +
    m.found.map(f => '<label class="toggle"><input type="checkbox" value="' + f.key + '"' + (m.applied ? " disabled" : "") + (f.sure !== false ? " checked" : "") + "> " + esc(PDEF[f.key].label) + (pstate(f.key) === 0 ? ' <span class="small">(already Have)</span>' : "") + (f.sure === false ? ' <span class="small">(not sure)</span>' : "") + "</label>").join("") +
    (m.applied ? '<p class="small">Saved to the pantry.</p>' : '<button class="btn primary" type="submit">Mark ticked items as Have</button>') + "</form>";
}
function aiSetupHTML() {
  return '<section class="ai-setup"><p>The assistant uses Google Gemini’s free tier. You need your own free key — it takes about 2 minutes:</p><ol>' +
    '<li>Open <a href="https://aistudio.google.com/apikey" target="_blank" rel="noopener">aistudio.google.com/apikey</a> and sign in with a Google account.</li>' +
    '<li>Tap <b>Create API key</b> and copy it.</li><li>Paste it below. Don’t add billing to that project: then it can never charge you, it just pauses when the free limit is reached.</li></ol>' +
    '<label for="ai-key">Gemini API key</label><input id="ai-key" type="password" autocomplete="off" spellcheck="false" placeholder="Paste your key">' +
    '<button class="btn primary" type="button" data-ai-savekey>Save key</button>' +
    '<p class="small">No key? <button type="button" class="linkish" data-ask-claude>Ask Claude instead</button> — opens Claude with your question and this kitchen’s details filled in.</p>' +
    '<p class="small">The key is stored only on this phone or browser. It is never synced, exported in backups or sent anywhere except Google. On the free tier Google may use what you send to improve its products, so don’t include private details.</p></section>';
}
function aiBodyHTML() {
  if (!aiKey()) return aiSetupHTML();
  const r = AI.recipeId && D.recipes.find(x => x.id === AI.recipeId);
  return (r ? '<p class="ai-ctx">Asking about <b>' + esc(r.title) + '</b> <button type="button" class="linkish" data-ai-clear-recipe>Ask in general</button></p>' : "") +
    '<div class="ai-log" id="ai-log" aria-live="polite">' + (AI.chat.length ? AI.chat.map(aiMsgHTML).join("") : '<p class="small">Ask anything about cooking, your pantry or this week’s meals. Answers use your pantry and the app’s recipes. AI can be wrong — check quantities against the recipe.</p>') +
    (AI.busy ? '<p class="ai-msg bot ai-wait">Thinking…</p>' : "") + "</div>" +
    (AI.chat.length ? "" : '<div class="needs">' + AI_QUICK.map((q, i) => '<button type="button" class="chip" data-ai-quick="' + i + '">' + esc(q[0]) + "</button>").join("") + "</div>") +
    '<form class="ai-form" data-ai-form><textarea id="ai-q" rows="2" maxlength="1500" placeholder="' + (r ? "e.g. The gravy is too watery, what now?" : "e.g. I have 2 cut lemons and paneer, ideas?") + '"></textarea>' +
    '<div class="ai-row"><label class="btn ai-photo">📷 Pantry photo<input type="file" accept="image/*" data-ai-photo hidden></label><button class="btn" type="button" data-ask-claude>Ask Claude</button><button class="btn primary" type="submit"' + (AI.busy ? " disabled" : "") + ">Ask</button></div></form>" +
    '<details class="recipe-details"><summary>AI settings</summary><p class="small">Model: ' + esc(aiGet(AI.MODEL) || AI.DEFAULT_MODEL) + '</p><button class="btn" type="button" data-ai-newchat>New chat</button> <button class="btn" type="button" data-ai-removekey>Remove key from this device</button></details>';
}
function aiRender() {
  const b = $("#ai-body"); if (!b) return;
  b.innerHTML = aiBodyHTML();
  const log = $("#ai-log"); if (log) log.scrollTop = log.scrollHeight;
}
function openAI(recipeId) {
  if (recipeId && recipeId !== AI.recipeId) AI.chat = [];
  AI.recipeId = recipeId || null;
  $("#ai-in").innerHTML = '<div class="dlg-top"><h2 id="ai-title">Ask Kitchen AI</h2><button class="close" type="button" data-close="aidlg" aria-label="Close">×</button></div><div id="ai-body"></div>';
  aiRender(); openSheet("aidlg");
  const q = $("#ai-q"); if (q && !AI.chat.length) setTimeout(() => q.focus(), 50);
}
window.openAI = openAI;

/* Hand a question to Claude: opens a new Claude chat with the question and this kitchen's context filled in
   (and copies the same text, in case the app opens without it). Nothing is sent until you press send there. */
function claudePrompt(question, recipeId) {
  const ctx = (recipeId ? aiRecipeText(recipeId) + "\n\n" : "") + aiPlanText() + "\n\nPANTRY\n" + aiPantry() + "\nHousehold: " + aiHousehold();
  const q = (question || (recipeId ? "Walk me through cooking this step by step for the servings above: what to do the day before, what to chop and measure first, then each step with flame, time and how it should look." : "Help me with today's cooking.")).trim();
  return ("I'm cooking from my Kitchen From Zero app (Bengaluru; I have a kitchen scale, so grams please). " + q + "\n\n--- context from the app ---\n" + ctx).slice(0, 7000);
}
function askClaude(question, recipeId) {
  const text = claudePrompt(question, recipeId);
  try { copyText(text); } catch (e) {}
  const url = "https://claude.ai/new?q=" + encodeURIComponent(text);
  if (APP && APP.openExternal) { try { APP.openExternal(url); return; } catch (e) {} }
  window.open(url, "_blank", "noopener");
}
window.askClaude = askClaude;

async function aiAsk(text) {
  text = (text || "").trim(); if (!text || AI.busy) return;
  AI.chat.push({ role: "user", text }); AI.busy = true; aiRender();
  const hist = AI.chat.filter(m => m.role === "user" || m.role === "bot").slice(-10);
  const contents = hist.map((m, i) => ({ role: m.role === "user" ? "user" : "model",
    parts: [{ text: (i === 0 ? aiContext() + "\n\nQUESTION: " : "") + (m.role === "bot" ? JSON.stringify({ answer: m.text, recipes: m.recipes || [] }) : m.text) }] }));
  try {
    const out = aiJSON(await aiGenerate({ systemInstruction: { parts: [{ text: AI_RULES }] }, contents,
      generationConfig: { temperature: 0.4, maxOutputTokens: 8192, responseMimeType: "application/json", responseSchema: AI_SCHEMA } }));
    AI.chat.push({ role: "bot", text: String(out.answer || "").slice(0, 12000), recipes: Array.isArray(out.recipes) ? out.recipes : [], caution: out.caution || "" });
  } catch (e) { AI.chat.push({ role: "error", text: aiErrText(e) }); }
  AI.busy = false; aiRender();
}

function aiShrink(file) {
  return new Promise((ok, bad) => {
    const img = new Image(), url = URL.createObjectURL(file);
    img.onload = () => { const s = Math.min(1, 1024 / Math.max(img.width, img.height)), c = document.createElement("canvas");
      c.width = Math.round(img.width * s); c.height = Math.round(img.height * s); c.getContext("2d").drawImage(img, 0, 0, c.width, c.height);
      URL.revokeObjectURL(url); ok(c.toDataURL("image/jpeg", 0.8)); };
    img.onerror = () => { URL.revokeObjectURL(url); bad(new Error("Couldn't read that photo.")); };
    img.src = url;
  });
}
async function aiPhoto(file) {
  if (!file || AI.busy) return;
  let dataUrl; try { dataUrl = await aiShrink(file); } catch (e) { AI.chat.push({ role: "error", text: e.message }); return aiRender(); }
  AI.chat.push({ role: "user", text: "What's in this photo? Update my pantry.", img: dataUrl }); AI.busy = true; aiRender();
  const list = D.pantry.map(p => p.key + " = " + p.label).join("\n");
  try {
    const out = aiJSON(await aiGenerate({ contents: [{ role: "user", parts: [
      { inline_data: { mime_type: "image/jpeg", data: dataUrl.split(",")[1] } },
      { text: "This is a photo of a kitchen shelf, fridge or groceries. Identify which of these pantry items are clearly visible. Use only keys from this list; set sure=false when you are guessing. Ignore items not on the list.\n" + list } ] }],
      generationConfig: { temperature: 0.1, responseMimeType: "application/json", responseSchema: PHOTO_SCHEMA } }));
    const seen = new Set(), found = (out.found || []).filter(f => PDEF[f.key] && !seen.has(f.key) && seen.add(f.key));
    AI.chat.push({ role: "bot", id: "f" + Date.now(), text: found.length ? "I can see these items. Untick anything I got wrong:" : "I couldn't match anything in the photo to your pantry list.", found, caution: "" });
    if (out.note) AI.chat[AI.chat.length - 1].text += "\n" + out.note;
  } catch (e) { AI.chat.push({ role: "error", text: aiErrText(e) }); }
  AI.busy = false; aiRender();
}

document.addEventListener("click", e => {
  const c = s => e.target.closest && e.target.closest(s); let el;
  if ((el = c("[data-ask-claude]"))) { const q = ($("#ai-q") && $("#ai-q").value.trim()) || ((AI.chat.filter(m => m.role === "user").pop() || {}).text || ""); askClaude(q, el.dataset.askClaude || (el.closest("#aidlg") ? AI.recipeId : null)); return; }
  if ((el = c("[data-open-ai]"))) { if (typeof closeDrawer === "function") closeDrawer(); openAI(el.dataset.openAi || dlgId || null); return; }
  if (c("[data-ai-savekey]")) { const v = ($("#ai-key").value || "").trim(); if (v.length < 20) { $("#ai-key").setCustomValidity("That doesn't look like a full key."); $("#ai-key").reportValidity(); return; } aiSet(AI.KEY, v); aiSet(AI.MODEL, ""); aiRender(); return; }
  if (c("[data-ai-removekey]")) { aiSet(AI.KEY, ""); aiSet(AI.MODEL, ""); AI.chat = []; aiRender(); return; }
  if (c("[data-ai-newchat]")) { AI.chat = []; aiRender(); return; }
  if (c("[data-ai-clear-recipe]")) { AI.recipeId = null; AI.chat = []; aiRender(); return; }
  if ((el = c("[data-ai-quick]"))) { aiAsk(AI_QUICK[+el.dataset.aiQuick][1]); return; }
  if ((el = c("[data-ai-recipe]"))) { closeD("aidlg"); openRecipe(el.dataset.aiRecipe); return; }
});
document.addEventListener("submit", e => {
  if (e.target.matches("[data-ai-form]")) { e.preventDefault(); const q = $("#ai-q"); const v = q.value; q.value = ""; aiAsk(v); return; }
  const f = e.target.closest("[data-ai-found]");
  if (f) { e.preventDefault(); const m = AI.chat.find(x => x.id === f.dataset.aiFound); const keys = [...f.querySelectorAll("input:checked")].map(i => i.value).filter(k => PDEF[k]);
    if (keys.length) apply(s => keys.forEach(k => setPantry(s, k, 0))); if (m) m.applied = true; aiRender(); }
});
document.addEventListener("keydown", e => { if (e.key === "Enter" && !e.shiftKey && e.target.id === "ai-q") { e.preventDefault(); e.target.form.requestSubmit(); } });
document.addEventListener("change", e => { if (e.target.matches("[data-ai-photo]")) { const f = e.target.files && e.target.files[0]; e.target.value = ""; aiPhoto(f); } });
