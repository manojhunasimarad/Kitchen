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
  const ingredientQuantity = (item, factor) => item.scaleMode === 'pan' ? item.q : scaleQuantity(item.q, factor);
  function stepText(recipe,index,servings,smart) {
    if (!recipe.stepTemplates) return smart ? scaleStepText(recipe.steps[index], servings/(recipe.yield||1)) : recipe.steps[index];
    const items=Object.fromEntries(recipe.ingredients.flatMap(g=>g.items).map(item=>[item.id,item]));
    return recipe.stepTemplates[index].replace(/\{\{([a-z0-9-]+)\}\}/g,(_,id)=>smart ? "\uE000" + smartQuantity(items[id],servings/(recipe.yield||1)) + "\uE001" : ingredientQuantity(items[id],servings/(recipe.yield||1)));
  }
  /* Cook-friendly scaling for display: whole spices grow slowly, counted vegetables round to halves
     and show their weight for the kitchen scale, spoon and gram amounts round to what you can measure. */
  const WHOLE_SPICE = /\b(bay lea(f|ves)|cinnamon|cloves?|cardamom|star anise|dried red chill|peppercorns|marathi moggu|kalpasi|stone flower|mace|tea bag)\b/i;
  const COUNTED = [
    [/spring onion/i, null], [/onion/i, {large:150, medium:110, small:70, def:110}], [/tomato/i, {large:140, medium:100, small:70, def:100}],
    [/potato/i, {large:200, medium:150, small:90, def:150}], [/green chill/i, {def:4, whole:true, noGrams:true}], [/carrot/i, {def:70}],
    [/capsicum/i, {def:120}], [/garlic/i, {def:4, whole:true}], [/^eggs?\b|\beggs?\b(?!.*(noodle|rice|plant))/i, {def:50, whole:true, noGrams:true}]];
  const plainCount = new RegExp("^(" + number + ")(?:\\s*[–-]\\s*(" + number + "))?\\s*(large|medium|small|cloves?|pods?|inch(?:es)?|sticks?)?$");
  const roundTo = (n, step) => Math.round(n / step) * step;
  function tidy(s) {
    const re = new RegExp("(" + number + ")(?:\\s*[–-]\\s*(" + number + "))?\\s*(pinch(?:es)?|tsp|tbsp|g|ml|cups?)\\b", "g");
    return s.replace(re, (all, a, b, unit) => {
      let x = value(a), y = b ? value(b) : null;
      if (/^pinch/.test(unit)) { if (x <= 3) return all; x = Math.max(.25, roundTo(x / 8, .25)); y = y && Math.max(.25, roundTo(y / 8, .25)); unit = "tsp"; return format(x) + (y && y !== x ? "–" + format(y) : "") + " tsp"; }
      if (unit === "tsp" && x >= 3) { unit = "tbsp"; x /= 3; if (y) y /= 3; }
      const r = n => unit === "g" ? (n >= 20 ? roundTo(n, 5) : n >= 2 ? Math.round(n) : roundTo(n, .5)) :
        unit === "ml" ? (n >= 50 ? roundTo(n, 10) : Math.max(5, roundTo(n, 5))) : n >= 1 ? roundTo(n, .25) : Math.max(.125, Math.floor(n * 4 + .4) / 4);
      x = r(x); if (y) y = r(y);
      const out = format(x, unit === "g" || unit === "ml") + (y && y !== x ? "–" + format(y, unit === "g" || unit === "ml") : "");
      return out + " " + (/^cup/.test(unit) ? (x <= 1 && !y ? "cup" : "cups") : unit);
    });
  }
  function smartQuantity(item, factor) {
    if (!item || !item.q) return item ? item.q : "";
    if (item.scaleMode === "pan") return item.q;
    const name = item.name || "", note = item.note || "";
    let base = item.q, f = factor;
    // the books give 1- and 2-serving amounts; scale bigger batches from the 2-serving column
    if (factor >= 1.5 && item.q2 && item.q2 !== item.q && !/[\/+]/.test(item.q2) && plainOrUnit(item.q2)) { base = item.q2; f = factor / 2; }
    if (/ \/ /.test(name) || /[\/+]/.test(base)) return factor === 1 ? base : tidy(scaleQuantity(base, f));
    const m = base.trim().match(plainCount);
    if (m && WHOLE_SPICE.test(name) && !/garlic|powder|ground/i.test(name)) {
      const v = value(m[1]), n = f > 1 ? Math.round(v * Math.sqrt(f)) : Math.max(1, Math.round(v * f));
      return format(n) + (m[3] ? " " + m[3].replace(/s$/, "") + (n > 1 && !/inch/.test(m[3]) ? "s" : n > 1 ? "es" : "") : "");
    }
    const counted = COUNTED.find(([re]) => re.test(name));
    if (m && counted && counted[1] && (!m[3] || /large|medium|small|cloves?/.test(m[3]))) {
      const spec = counted[1], size = (m[3] || "") + " " + note + " " + name, v = value(m[1]) * f, hi = m[2] ? value(m[2]) * f : null;
      const g = /large/.test(size) ? spec.large : /small/.test(size) ? spec.small : /medium/.test(size) ? spec.medium : null;
      const each = g || spec.def, rq = n => spec.whole ? Math.max(1, Math.round(n)) : Math.max(.5, roundTo(n, .5));
      const cnt = format(rq(v)) + (hi ? "–" + format(rq(hi)) : "") + (m[3] && !/cloves?/.test(m[3]) ? " " + m[3] : /cloves?/.test(m[3] || "") ? (rq(v) > 1 ? " cloves" : " clove") : "");
      if (spec.noGrams) return cnt;
      const grams = n => n * each >= 20 ? roundTo(n * each, 5) : Math.round(n * each);
      return cnt + " (≈ " + grams(v) + (hi ? "–" + grams(hi) : "") + " g)";
    }
    return factor === 1 ? base : tidy(scaleQuantity(base, f));
  }
  function plainOrUnit(q) { try { scaleQuantity(q, 2); return true; } catch (e) { return false; } }
  /* Scale the amounts written inside an older method step (cups, spoons, grams, ml), leaving times,
     temperatures, whistles and counts alone. Scaled amounts are wrapped in \uE000…\uE001 so the page can bold them. */
  function scaleStepText(text, factor) {
    if (!text || factor === 1) return text;
    const re = new RegExp("(" + number + ")(?:\\s*[–-]\\s*(" + number + "))?\\s*(kg|g|ml|litres?|l|cups?|tbsp|tsp)\\b(?![\\w°])", "g");
    return text.replace(re, (all, a, b, unit) => {
      const u = /^litre/.test(unit) ? "l" : unit, q = a + (b ? "–" + b : "") + " " + u;
      let out; try { out = tidy(scaleQuantity(q, factor)); } catch (e) { return all; }
      if (/^l$/.test(u)) out = out.replace(/ l$/, /^litres/.test(unit) ? " litres" : " l");
      return "\uE000" + out + "\uE001";
    });
  }
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
    const ymdRe=/^\d{4}-\d{2}-\d{2}$/, hmRe=/^\d{2}:\d{2}$/;
    if (x.set.since != null && (!object(x.set.since) || Object.entries(x.set.since).some(([k,d]) => !pantryKeys.includes(k) || !ymdRe.test(d)))) return "Invalid purchase dates.";
    if (x.set.checks != null && (!object(x.set.checks) || Object.entries(x.set.checks).some(([d,l]) => !ymdRe.test(d) || !Array.isArray(l) || l.some(h => !hmRe.test(h))))) return "Invalid pantry checks.";
    if (x.set.reminders != null && (!object(x.set.reminders) || typeof x.set.reminders.on !== "boolean" || !Array.isArray(x.set.reminders.times) || x.set.reminders.times.length > 4 || x.set.reminders.times.some(h => !hmRe.test(h)))) return "Invalid reminders.";
    if (x.set.pricey != null && (!Array.isArray(x.set.pricey) || x.set.pricey.some(k => !pantryKeys.includes(k)))) return "Invalid pricey list.";
    if (x.set.budget != null && typeof x.set.budget !== "boolean") return "Invalid budget setting.";
    if(x.set.nutritionPerson&&!['v1','v2','e1','n1','n2'].includes(x.set.nutritionPerson))return 'Invalid nutrition person.';
    if (x.set.household) {
      const H=typeof module!=='undefined'&&module.exports ? require('./household.js') : root.KitchenHousehold;
      const error=H.validateProfile(x.set.household);if(error)return error;
    }
    for (const [date,p] of Object.entries(x.plan)) {
      if (!/^\d{4}-\d{2}-\d{2}$/.test(date) || !object(p) || !object(p.m) || ![1,2,3].includes(p.s) || !Number.isInteger(p.n) || p.n < 1 || p.n > 12) return "Invalid meal plan.";
      for (const [slot, dishes] of Object.entries(p.m)) {
        if (!["b","l","d"].includes(slot) || !Array.isArray(dishes)) return "Invalid meal slot.";
        if (!dishes.every(row => Array.isArray(row) && row.length === 2 && recipeIds.includes(row[0]) && Number.isFinite(row[1]) && row[1] > 0 && row[1] <= 40)) return "Unknown dish or invalid serving quantity.";
      }
      if(p.attendance) {
        if(!object(p.attendance))return 'Invalid attendance.';
        for(const [slot,entries] of Object.entries(p.attendance)) {
          if(!['b','l','d'].includes(slot)||!object(entries))return 'Invalid attendance.';
          for(const [id,m] of Object.entries(entries))if(!['v1','v2','e1','n1','n2'].includes(id)||!object(m)||typeof m.eating!=='boolean'||![0.5,1,1.5,2].includes(m.portions)||!/^([01]\d|2[0-3]):[0-5]\d$/.test(m.time))return 'Invalid member meal entry.';
        }
      }
      if(p.assignments) {
        if(!object(p.assignments))return 'Invalid dish assignments.';
        for(const [slot,dishes] of Object.entries(p.assignments)) {
          if(!['b','l','d'].includes(slot)||!object(dishes))return 'Invalid dish assignments.';
          for(const [id,people] of Object.entries(dishes))if(!recipeIds.includes(id)||!Array.isArray(people)||new Set(people).size!==people.length||people.some(p=>!['v1','v2','e1','n1','n2'].includes(p)))return 'Invalid dish recipients.';
        }
      }
    }
    for (const v of Object.values(x.done)) if (!Number.isFinite(v)) return "Invalid progress entry.";
    for (const v of Object.values(x.week)) if (!object(v)) return "Invalid weekly progress.";
    for (const v of Object.values(x.labs)) if (!object(v) && typeof v !== "string") return "Invalid profile record.";
    return null;
  }
  const api = {scaleQuantity, ingredientQuantity, smartQuantity, scaleStepText, stepText, format, pantryAvailable, writeStorage, timing, withinTime, validImport};
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  else root.KitchenCore = api;
})(typeof globalThis !== "undefined" ? globalThis : this);
