/* Household calculations are pure; the same module runs in browser and Node tests. */
(function(root){
  'use strict';
  const defaults={members:[{id:'v1',name:'Vegetarian 1',diet:'veg'},{id:'v2',name:'Vegetarian 2',diet:'veg'},
    {id:'e1',name:'Eggetarian',diet:'egg'},{id:'n1',name:'Non-vegetarian 1',diet:'nonveg'},
    {id:'n2',name:'Non-vegetarian 2',diet:'nonveg'}],cooks:2,burners:4,induction:1,airfryer:1,sandwich:1,
    cooker3:1,cooker5:1,fridge:true,mixer:false,approach:'shared',maxMinutes:60};
  const times={b:'08:00',l:'13:00',d:'20:00'};
  const clone=x=>JSON.parse(JSON.stringify(x));
  const dietOf=r=>r.diet||(r.keys?(r.keys.includes('eggs')?'egg':'veg'):'unknown');
  const compatible=(member,recipe)=>{const d=dietOf(recipe);return d==='veg'||d==='egg'&&member.diet!=='veg'||d==='nonveg'&&member.diet==='nonveg';};
  function attendees(plan,slot,profile){
    return profile.members.map(m=>({...m,...(plan.attendance?.[slot]?.[m.id]||{eating:true,portions:1,time:times[slot]})})).filter(m=>m.eating);
  }
  function recipients(plan,slot,recipe,profile){
    const assigned=plan.assignments?.[slot]?.[recipe.id];
    return attendees(plan,slot,profile).filter(m=>compatible(m,recipe)&&(!assigned||assigned.includes(m.id)));
  }
  const servings=(plan,slot,recipe,mult,profile)=>recipients(plan,slot,recipe,profile).reduce((n,m)=>n+m.portions*mult,0);
  function totals(plan,recipes,profile,slots=['b','l','d']){
    const out={};
    slots.forEach(sl=>(plan.m[sl]||[]).forEach(([id,k])=>{
      const recipe=recipes[id];if(!recipe)return;
      const n=servings(plan,sl,recipe,k,profile);if(n>0)out[id]=(out[id]||0)+n;
    }));return out;
  }
  function personNutrition(plan,slot,person,recipes,profile){
    const total={};(plan.m[slot]||[]).forEach(([id,k])=>{
      const r=recipes[id];if(!r)return;
      const m=recipients(plan,slot,r,profile).find(m=>m.id===person);if(!m)return;
      Object.entries(r.nutr).forEach(([key,n])=>total[key]=(total[key]||0)+n*m.portions*k);
    });return total;
  }
  function equipmentIssues(r,h){
    const uses=(r.uses||'').toLowerCase(),issues=[];
    if(/pressure cooker/.test(uses)&&!h.cooker3&&!h.cooker5)issues.push('pressure cooker unavailable');
    if(/mixer|blender/.test(uses)&&!h.mixer)issues.push('confirm mixer availability');
    if(/air fryer/.test(uses)&&!/optional| or /.test(uses)&&!h.airfryer)issues.push('air fryer unavailable');
    if(/sandwich maker/.test(uses)&&!/optional| or /.test(uses)&&!h.sandwich)issues.push('sandwich maker unavailable');
    if(!h.fridge&&/refrigerat|fridge/.test((r.steps||[]).join(' ').toLowerCase()))issues.push('recipe requires refrigeration');
    return issues;
  }
  function workload(plan,slot,recipes,h){
    const slots=Array.isArray(slot)?slot:[slot];
    const amounts=totals(plan,recipes,h,slots),cookFree=Array(h.cooks).fill(0);
    const resources={burner:Array(h.burners+h.induction).fill(0),airfryer:Array(h.airfryer).fill(0),sandwich:Array(h.sandwich).fill(0),
      cooker3:Array(h.cooker3).fill(0),cooker5:Array(h.cooker5).fill(0)};
    const tasks=[],unknown=[];
    Object.entries(amounts).forEach(([id,n])=>{
      const r=recipes[id],t=r.timing,issues=equipmentIssues(r,h);
      if(issues.length){unknown.push(r.title+': '+issues.join(', '));return;}
      if(!t?.cookMinutes||!t.prerequisiteMinutes){unknown.push(r.title+': preparation time not reviewed');return;}
      // Conservative batches, never assume a larger pot halves work or two cooks halve time.
      const batches=Math.ceil(n/(r.yield||1)),duration=(t.cookMinutes[1]+t.prerequisiteMinutes[1])*batches;
      const uses=(r.uses||'').toLowerCase();
      const required=/air fryer/.test(uses)&&!/optional| or /.test(uses)?['airfryer']:
        /sandwich maker/.test(uses)&&!/optional| or /.test(uses)?['sandwich']:['burner'];
      if(/pressure cooker/.test(uses)){
        const choices=['cooker3','cooker5'].filter(k=>resources[k].length);
        choices.sort((a,b)=>Math.min(...resources[a])-Math.min(...resources[b]));required.push(choices[0]);
      }
      if(required.some(k=>!resources[k].length)){unknown.push(r.title+': equipment unavailable');return;}
      const resourceIndices=required.map(k=>resources[k].indexOf(Math.min(...resources[k])));
      const choices=dietOf(r)==='veg'?cookFree.map((_,i)=>i):[h.cooks-1];
      let cook=choices.sort((a,b)=>cookFree[a]-cookFree[b])[0];
      const start=Math.max(cookFree[cook],...required.map((k,i)=>resources[k][resourceIndices[i]]));
      const end=start+duration;cookFree[cook]=end;
      required.forEach((k,i)=>resources[k][resourceIndices[i]]=end);
      tasks.push({id,cook:cook+1,start,end,batches,servings:n,resources:required});
    });
    const eaterTimes=slots.flatMap(sl=>attendees(plan,sl,h).map(m=>m.time));
    if(new Set(eaterTimes).size>1)unknown.push('Different eating times: plan fresh portions or safe refrigeration/reheating separately.');
    const minutes=unknown.length?null:Math.max(0,...cookFree);
    const target=eaterTimes[0];let startBy=null;
    if(minutes!==null&&target){const [hours,mins]=target.split(':').map(Number),start=hours*60+mins-minutes;
      startBy=(start<0?'previous day ':'')+String(Math.floor(((start%1440)+1440)%1440/60)).padStart(2,'0')+':'+String(((start%60)+60)%60).padStart(2,'0');}
    return {tasks,unknown,minutes,startBy,
      basis:'Conservative resource estimate: each cook is occupied for a full recipe; repeats the base batch when scaling. Larger-pot yields and actual kitchen timings are not tested.'};
  }
  function validateProfile(h){
    if(!h||!Array.isArray(h.members)||h.members.length!==5)return 'Household needs five members.';
    if(new Set(h.members.map(m=>m.id)).size!==5||h.members.some(m=>!['v1','v2','e1','n1','n2'].includes(m.id)||typeof m.name!=='string'||m.name.length>60||!['veg','egg','nonveg'].includes(m.diet)))return 'Invalid household member.';
    for(const k of ['cooks','burners','induction','airfryer','sandwich','cooker3','cooker5'])if(!Number.isInteger(h[k])||h[k]<(['cooks','burners'].includes(k)?1:0)||h[k]>8)return 'Invalid kitchen capacity.';
    if(typeof h.fridge!=='boolean'||typeof h.mixer!=='boolean'||!['shared','mixed'].includes(h.approach)||!Number.isFinite(h.maxMinutes)||h.maxMinutes<10||h.maxMinutes>240)return 'Invalid household preference.';
    return null;
  }
  const api={defaults,clone,times,compatible,attendees,recipients,servings,totals,personNutrition,equipmentIssues,workload,validateProfile};
  if(typeof module!=='undefined'&&module.exports)module.exports=api;else root.KitchenHousehold=api;
})(typeof globalThis!=='undefined'?globalThis:this);
