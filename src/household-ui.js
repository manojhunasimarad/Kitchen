/* Household UI shares attendance/serving calculations with shopping and cooking. */
const H = KitchenHousehold;
const household = () => S.set.household || H.clone(H.defaults);
const allDishes = () => Object.assign({},X,R);
const memberLabel = m => m.name+' ('+({veg:'vegetarian',egg:'eggetarian',nonveg:'non-vegetarian'}[m.diet])+')';
const mealServings = (p,sl,r,k=1) => H.servings(p,sl,r,k,household());
function attendanceHTML(p,sl) {
  const h=household(),present=H.attendees(p,sl,h);
  return '<details class="recipe-details" id="attendance-'+sl+'"><summary>Who is eating? '+present.length+' of '+h.members.length+'</summary><p class="small">Set attendance, portions and eating time for each person. Each dish below has its own recipients.</p>'+h.members.map(m=>{
    const a=p.attendance?.[sl]?.[m.id]||{eating:true,portions:1,time:H.times[sl]};
    return '<div class="member-row"><label><input type="checkbox" data-attend="'+sl+'|'+m.id+'"'+(a.eating?' checked':'')+'> '+esc(memberLabel(m))+'</label><label>Portions <select aria-label="'+esc(SLOT[sl]+' portions for '+m.name)+'" data-portion="'+sl+'|'+m.id+'">'+[0.5,1,1.5,2].map(n=>'<option value="'+n+'"'+(a.portions===n?' selected':'')+'>'+n+'</option>').join('')+'</select></label><label>Eating time <input type="time" aria-label="'+esc(SLOT[sl]+' time for '+m.name)+'" data-mealtime="'+sl+'|'+m.id+'" value="'+esc(a.time)+'"></label></div>';
  }).join('')+'</details>';
}
function recipientsHTML(p,sl,r) {
  const h=household(),eligible=H.attendees(p,sl,h).filter(m=>H.compatible(m,r)),ids=H.recipients(p,sl,r,h).map(m=>m.id);
  return '<details id="recipients-'+sl+'-'+r.id+'"><summary>Dish recipients</summary>'+(eligible.length?eligible.map(m=>'<label class="toggle"><input type="checkbox" data-recipient="'+sl+'|'+r.id+'|'+m.id+'"'+(ids.includes(m.id)?' checked':'')+'> '+esc(m.name)+'</label>').join(''):'<p>No attending member can eat this dish.</p>')+'</details>';
}
function householdSetupHTML(){
  const h=household();
  const fields=[['cooks','People cooking',1,2,3,4],['burners','Stove burners',1,2,3,4,5,6,8],['induction','Induction hobs',0,1,2],['airfryer','Air fryers',0,1,2],['sandwich','Sandwich makers',0,1,2],['cooker3','3 L pressure cookers',0,1,2],['cooker5','5 L pressure cookers',0,1,2]];
  return '<section class="sec"><h2>Your five-person household</h2><p>Shared vegetarian base; egg and meat additions use separate utensils. Keep raw meat separate from ready-to-eat and vegetarian food.</p>'+h.members.map(m=>'<div class="member-row"><label>Name <input type="text" maxlength="60" data-member-name="'+m.id+'" value="'+esc(m.name)+'"></label><label>Diet <select data-member-diet="'+m.id+'">'+[['veg','Vegetarian'],['egg','Eggetarian'],['nonveg','Non-vegetarian']].map(([v,l])=>'<option value="'+v+'"'+(m.diet===v?' selected':'')+'>'+l+'</option>').join('')+'</select></label></div>').join('')+
    fields.map(([key,label,...values])=>'<label class="f">'+label+'<select data-kitchen="'+key+'">'+values.map(n=>'<option value="'+n+'"'+(h[key]===n?' selected':'')+'>'+n+'</option>').join('')+'</select></label>').join('')+
    '<label class="toggle"><input type="checkbox" data-kitchen="fridge"'+(h.fridge?' checked':'')+'> Fridge available</label><label class="toggle"><input type="checkbox" data-kitchen="mixer"'+(h.mixer?' checked':'')+'> Mixer/grinder available (confirm before choosing ground pastes)</label>'+
    '<label class="f">Meal suggestions <select data-kitchen="approach"><option value="shared"'+(h.approach==='shared'?' selected':'')+'>Shared vegetarian meal · least separate work</option><option value="mixed"'+(h.approach==='mixed'?' selected':'')+'>Shared base + separate egg and meat additions</option></select></label><label class="f">Desired cooking window (minutes)<input type="number" min="10" max="240" step="5" data-kitchen="maxMinutes" value="'+h.maxMinutes+'"></label><p class="small">Cooking times remain estimates. The two pressure cookers occupy separate burner/induction slots when used. Check actual fill limits; the planner does not assume a 5 L cooker doubles recipe capacity.</p></section>';
}
function workloadHTML(p,sl){
  const h=household(),w=H.workload(p,sl,allDishes(),h);
  if(!(Array.isArray(sl)?sl:[sl]).some(slot=>H.attendees(p,slot,h).length))return '<p class="small">Nobody attending: no quantities or cooking allocated.</p>';
  return '<details class="recipe-details" id="workload-'+sl+'"><summary>'+h.cooks+' cooks · '+h.burners+' burners + '+h.induction+' induction · '+(w.minutes===null?'timing needs review':w.minutes+' min conservative workload')+'</summary><p class="small">'+esc(w.basis)+'</p>'+(w.startBy?'<p><b>Estimated start by '+esc(w.startBy)+'</b> for the selected eating time. Allow extra margin.</p>':'')+w.tasks.map(t=>'<p>Cook '+t.cook+': '+esc(dish(t.id).title)+' · '+nice(t.servings)+' servings · '+t.batches+' base batch(es) · estimated minute '+t.start+'–'+t.end+' · '+esc(t.resources.join(', '))+'</p>').join('')+w.unknown.map(x=>'<p class="banner">'+esc(x)+'</p>').join('')+(w.minutes!==null&&w.minutes>h.maxMinutes?'<p class="banner">Exceeds your '+h.maxMinutes+'-minute target. Reduce dishes or plan preparation ahead.</p>':'')+'<p>Keep vegetarian utensils separate. The additions cook must wash hands and clean equipment between raw meat and other food. Serving at different times requires a fresh-cooking or safe chill/reheat plan.</p></details>';
}
function householdQuantities(p,sl,prefix="today"){
  const amounts=H.totals(p,allDishes(),household(),[sl]);
  return '<details class="recipe-details" id="quantities-'+prefix+'-'+sl+'"><summary>Ingredient quantities for these eaters</summary>'+Object.entries(amounts).map(([id,n])=>{
    const r=dish(id),f=n/(r.yield||1);
    return '<h4>'+esc(r.title)+' · '+nice(n)+' servings</h4>'+(r.ingredients||[]).map(g=>typeof g==='string'?'<p>'+esc(g)+' · legacy quantity needs manual scaling</p>':'<ul>'+g.items.map(i=>'<li>'+esc(KitchenCore.ingredientQuantity(i,f))+' '+esc(i.name)+(i.scaleMode==='pan'?' (pan quantity; extra batches)':'')+'</li>').join('')+'</ul>').join('');
  }).join('')+'</details>';
}
function renderToday() {
  const t0=new Date(),h=household();let dates='';
  for(let i=0;i<7;i++){const d=new Date(t0);d.setDate(t0.getDate()+i);const ds=ymd(d);dates+='<button type="button" class="date" data-date="'+ds+'" aria-pressed="'+(ds===selDate)+'"><span>'+(i===0?'Today':DAYS[dayIdx(d)])+'</span><b>'+d.getDate()+'</b></button>';}
  $('#dates').innerHTML=dates;const p=planOf(selDate);
  document.querySelectorAll('#seg-sess button').forEach(b=>b.setAttribute('aria-pressed',String(+b.dataset.sess===p.s)));
  $('#ppl-n').textContent=h.members.length;document.querySelectorAll('[data-people]').forEach(b=>{b.disabled=true;b.title='Select each meal’s eaters below';});
  const sessions=SESS[p.s].map(se=>'<section class="sess"><h3>'+esc(se.name)+'</h3><p class="small">Combined session resource allocation (all meals below):</p>'+workloadHTML(p,se.slots)+se.slots.map(sl=>{
    const attending=H.attendees(p,sl,h),rows=p.m[sl]||[];
    const menu=rows.map(([id,k],i)=>{const r=dish(id);if(!r)return '';const n=mealServings(p,sl,r,k),people=H.recipients(p,sl,r,h);
      return '<li class="household-dish"><div>'+(R[id]?recBtn(id):esc(r.title))+' <b>'+nice(n)+' total servings</b><p class="small">'+(people.length?people.map(m=>esc(m.name)).join(', '):'No eligible recipients; not included in quantities')+'</p>'+recipientsHTML(p,sl,r)+'</div><div class="recipe-tools"><button class="btn sm" data-hh-open="'+sl+'|'+id+'">Cook these portions</button><button class="btn sm" data-dish="'+sl+'|'+i+'|-1">− portion multiplier</button><span>×'+nice(k)+' each</span><button class="btn sm" data-dish="'+sl+'|'+i+'|1">+ portion multiplier</button><button class="btn sm" data-rm="'+sl+'|'+i+'">Remove</button></div></li>';
    }).join('');
    const nutrition=attending.map(m=>{const n=H.personNutrition(p,sl,m.id,allDishes(),h);return '<li>'+esc(m.name)+' · '+esc(m.time)+' · ~'+Math.round(n.kcal||0)+' kcal, '+Math.round(n.p||0)+' g protein'+(!Object.keys(n).length?' · no food assigned':'')+'</li>';}).join('');
    const uncovered=attending.filter(m=>!rows.some(([id,k])=>dish(id)&&mealServings(p,sl,dish(id),k)>0&&H.recipients(p,sl,dish(id),h).some(x=>x.id===m.id)));
    return '<section class="meal"><h3>'+SLOT[sl]+'</h3>'+attendanceHTML(p,sl)+(uncovered.length?'<p class="banner">No dish assigned to '+uncovered.map(m=>esc(m.name)).join(', ')+'.</p>':'')+'<ul class="plain">'+menu+'</ul><div class="recipe-tools"><button class="btn" data-hh-suggest="'+sl+'">Suggest for these eaters</button><button class="btn" data-add="'+sl+'">+ Add dish</button></div>'+workloadHTML(p,sl)+householdQuantities(p,sl)+'<details id="nutrition-'+sl+'"><summary>Per-person meal nutrition · estimates</summary><ul>'+nutrition+'</ul><p class="small">Totals follow assigned dishes and portion multipliers. These are not individual nutrition targets.</p></details><label class="toggle"><input type="checkbox" data-eat="'+sl+'"'+(eaten(selDate,sl)?' checked':'')+'> Meal finished</label></section>';
  }).join('')+'</section>').join('');
  $('#kot').innerHTML='<div class="kot-head">Kitchen order · '+esc(fmtDay(parseYmd(selDate)))+'</div><p class="kot-title">Five people, different diets</p><p>Choose eaters and portions for each meal. Shared vegetarian dishes can feed everyone; egg/meat assignments respect diet automatically. Change names and kitchen equipment in Settings.</p>'+sessions;
  $('#day-reset').hidden=!S.plan[selDate];
  $('#day-nutri').innerHTML='<h3>Daily estimates by person</h3>'+h.members.map(m=>{const n={};SLOTS.forEach(sl=>{const v=H.personNutrition(p,sl,m.id,allDishes(),h);Object.entries(v).forEach(([k,x])=>n[k]=(n[k]||0)+x);});return '<p>'+esc(m.name)+': ~'+Math.round(n.kcal||0)+' kcal · '+Math.round(n.p||0)+' g protein planned</p>';}).join('')+'<p class="small">Profile targets and the top protein meter remain for one person; select that person in Settings. Meal completion ticks apply to the meal, not proof each person ate their portion.</p>';
}
function suggestHousehold(slot){
  const h=household(),p=planOf(selDate),people=H.attendees(p,slot,h);
  if(!people.length){editPlan(selDate,p=>{p.m[slot]=[];});return;}
  const candidates=D.recipes.filter(r=>r.diet==='veg'&&(slot==='b'?r.course==='breakfast':r.course==='main'||r.course==='soup')&&!H.equipmentIssues(r,h).length);
  const score=r=>status(r).missing.length*100+(KitchenCore.timing(r,false).max||r.minutes+90)+r.needs.length;
  candidates.sort((a,b)=>score(a)-score(b));
  // Prefer candidates whose conservative scaled workload fits. Unknowns remain explicit.
  const fits=r=>{const q=H.clone(p);q.m[slot]=[[r.id,1]];if(needsCarb(r))q.m[slot].push(['rice-cooked-right',1]);q.assignments={...q.assignments,[slot]:{}};const w=H.workload(q,slot,allDishes(),h);return w.minutes!==null&&w.minutes<=h.maxMinutes;};
  const r=candidates.find(fits)||candidates[0];if(!r)return;
  const menu=[[r.id,1]],assign={};
  if(needsCarb(r))menu.push(['rice-cooked-right',1]);
  if(h.approach==='mixed'){
    const eggPeople=people.filter(m=>m.diet==='egg'),meatPeople=people.filter(m=>m.diet==='nonveg');
    if(eggPeople.length){menu.push(['egg-bhurji-and-masala-omelette',1]);assign['egg-bhurji-and-masala-omelette']=eggPeople.map(m=>m.id);}
    if(meatPeople.length){menu.push(['pepper-chicken-fry',1]);assign['pepper-chicken-fry']=meatPeople.map(m=>m.id);}
  }
  editPlan(selDate,p=>{p.m[slot]=menu;(p.assignments||={})[slot]=assign;});
}
function changeHousehold(t){
  if(t.dataset.attend||t.dataset.portion||t.dataset.mealtime){
    const [sl,id]=(t.dataset.attend||t.dataset.portion||t.dataset.mealtime).split('|');
    editPlan(selDate,p=>{const a=((p.attendance||={})[sl]||={});const m=a[id]||{eating:true,portions:1,time:H.times[sl]};
      if(t.dataset.attend)m.eating=t.checked;if(t.dataset.portion)m.portions=+t.value;if(t.dataset.mealtime&&t.value)m.time=t.value;a[id]=m;});return true;
  }
  if(t.dataset.recipient){const [sl,id,person]=t.dataset.recipient.split('|'),p=planOf(selDate),r=dish(id);let ids=H.recipients(p,sl,r,household()).map(m=>m.id);ids=t.checked?[...new Set([...ids,person])]:ids.filter(x=>x!==person);editPlan(selDate,p=>{((p.assignments||={})[sl]||={})[id]=ids;});return true;}
  if(t.dataset.memberName||t.dataset.memberDiet||t.dataset.kitchen){
    const h=H.clone(household());if(t.dataset.kitchen){const k=t.dataset.kitchen;h[k]=['fridge','mixer'].includes(k)?t.checked:k==='approach'?t.value:+t.value;}
    else{const m=h.members.find(m=>m.id===(t.dataset.memberName||t.dataset.memberDiet));if(t.dataset.memberName)m.name=t.value.trim()||m.name;else m.diet=t.value;}
    const error=H.validateProfile(h);if(!error)apply(s=>{s.set.household=h;s.set.people=5;});return true;
  }return false;
}
