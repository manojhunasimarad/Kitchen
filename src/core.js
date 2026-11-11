/* Pure cooking calculations. Embedded into both builds; also tested with Node. */
(function (root) {
  "use strict";
  const fractions = {"½": .5, "¼": .25, "¾": .75, "⅓": 1/3, "⅔": 2/3, "⅛": .125, "⅜": .375, "⅝": .625, "⅞": .875};
  const number = "(?:\\d+\\s+\\d+/\\d+|\\d+/\\d+|\\d+(?:\\.\\d+)?\\s*[½¼¾⅓⅔⅛⅜⅝⅞]?|[½¼¾⅓⅔⅛⅜⅝⅞])";
  function value(s) {
    s = s.trim();
    const m = s.match(/^(?:(\d+)\s+)?(\d+)\/(\d+)$/);
    if (m) return +m[3] ? +(m[1] || 0) + +m[2] / +m[3] : NaN;
    return (parseFloat(s) || 0) + (fractions[s.slice(-1)] || 0);
  }
  function format(n, decimal) {
    if (!Number.isFinite(n)) return "unknown";
    if (!decimal) {
      const w = Math.floor(n), f = n - w;
      if (Math.abs(f) < 1e-8) return String(w);
      for (const [s, v] of Object.entries(fractions)) if (Math.abs(f - v) < 1e-8) return (w || "") + s;
    }
    return String(Math.round(n * 10000) / 10000);
  }
  function scaleQuantity(q, factor) {
    if (!q || factor === 1) return q;
    if (!(factor > 0) || !Number.isFinite(factor)) throw new Error("Invalid serving multiplier");
    return q.split(/(\s\/\s|\s\+\s)/).map(part => {
      if (/^\s[+/]\s$/.test(part)) return part;
      if (/^a pinch\b/i.test(part)) return format(factor) + (factor <= 1 ? " pinch" : " pinches") + part.slice(7);
      const m = part.match(new RegExp("^(" + number + ")(?:\\s*[–-]\\s*(" + number + "))?\\s*(.*)$"));
      if (!m) return part;
      const a = value(m[1]), b = m[2] ? value(m[2]) : null;
      if (!Number.isFinite(a) || (b !== null && !Number.isFinite(b))) return part;
      let unit = m[3], decimal = /^(g|kg|ml|l)\b/i.test(unit);
      unit = unit.replace(/^(cups?|cloves?|slices?|inches|inch)\b/, u => {
        const singular = u === "inches" ? "inch" : u.replace(/s$/, "");
        return a * factor <= 1 ? singular : singular + (singular === "inch" ? "es" : "s");
      });
      return format(a * factor, decimal) + (b !== null ? "–" + format(b * factor, decimal) : "") + (unit ? " " + unit : "");
    }).join("");
  }
  function pantryAvailable(state) { return state === 0 || state === 1; }
  function writeStorage(storage, key, data) {
    try { storage.setItem(key, JSON.stringify(data)); return {ok:true}; }
    catch (error) { return {ok:false, error:String(error.name || "StorageError")}; }
  }
  function timing(recipe, prepared) {
    const t = recipe.timing;
    if (!t) return {text:recipe.time || "Time not verified", max:null, conditional:true};
    const base = t.cookMinutes;
    const wait = prepared ? [0,0] : t.prerequisiteMinutes;
    if (!wait || !base) return {text:recipe.time + " · allow extra preparation time", max:null, conditional:true};
    const low = base[0] + wait[0], high = base[1] + wait[1];
    const label = low === high ? low + " min" : low + "–" + high + " min";
    return {text:label + (prepared && t.prerequisites.length ? " after preparation" : " estimated"), min:low, max:high, conditional:false};
  }
  function withinTime(recipe, limit) {
    const t = timing(recipe, false);
    return t.max !== null && t.max <= limit;
  }
  function validImport(x, recipeIds, pantryKeys) {
    const object = v => v && typeof v === "object" && !Array.isArray(v);
    if (!object(x) || x.v !== 2) return "Use a version 2 Kitchen backup.";
    const keys = ["done","week","pantry","days","set","plan","basket","pick","me","wlog","labs"];
    if (!keys.every(k => object(x[k]))) return "Backup is missing required sections.";
    if (JSON.stringify(x).length > 2000000) return "Backup exceeds the 2 MB limit.";
    if (/"(?:__proto__|constructor|prototype)"\s*:/.test(JSON.stringify(x))) return "Backup contains unsupported keys.";
    for (const [k,v] of Object.entries(x.pantry)) if (!pantryKeys.includes(k) || ![0,1,2].includes(v)) return "Invalid pantry entry.";
    for (const [k,v] of Object.entries(x.basket)) if (!pantryKeys.includes(k) || !object(v) || !["bring","order","search"].includes(v.via)) return "Invalid shopping entry.";
    for (const [k,v] of Object.entries(x.set)) {
      if (["people","sessions","kcal","p"].includes(k) && (typeof v !== "number" || !Number.isFinite(v))) return "Invalid numeric setting.";
    }
    if (x.set.people != null && !(Number.isInteger(x.set.people) && x.set.people >= 1 && x.set.people <= 12)) return "People must be between 1 and 12.";
    if (x.set.sessions != null && ![1,2,3].includes(x.set.sessions)) return "Invalid cooking sessions.";
    for (const [date,p] of Object.entries(x.plan)) {
      if (!/^\d{4}-\d{2}-\d{2}$/.test(date) || !object(p) || !object(p.m) || ![1,2,3].includes(p.s) || !Number.isInteger(p.n) || p.n < 1 || p.n > 12) return "Invalid meal plan.";
      for (const [slot, dishes] of Object.entries(p.m)) {
        if (!["b","l","d"].includes(slot) || !Array.isArray(dishes)) return "Invalid meal slot.";
        if (!dishes.every(row => Array.isArray(row) && row.length === 2 && recipeIds.includes(row[0]) && Number.isFinite(row[1]) && row[1] > 0 && row[1] <= 40)) return "Unknown dish or invalid serving quantity.";
      }
    }
    for (const v of Object.values(x.done)) if (!Number.isFinite(v)) return "Invalid progress entry.";
    for (const v of Object.values(x.week)) if (!object(v)) return "Invalid weekly progress.";
    for (const v of Object.values(x.labs)) if (!object(v) && typeof v !== "string") return "Invalid profile record.";
    return null;
  }
  const api = {scaleQuantity, format, pantryAvailable, writeStorage, timing, withinTime, validImport};
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  else root.KitchenCore = api;
})(typeof globalThis !== "undefined" ? globalThis : this);
