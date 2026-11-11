const test=require('node:test'),assert=require('node:assert/strict');
const H=require('../src/household.js'),C=require('../src/core.js');
const data=require('../data/data.json'),recipes=Object.fromEntries(data.recipes.map(r=>[r.id,r]));
const sample=()=>({s:3,n:5,m:{b:[],l:[],d:[['rice-cooked-right',1],['egg-bhurji-and-masala-omelette',1],['pepper-chicken-fry',1]]}});
test('five-person household allocates 5 shared, 1 egg and 2 meat portions',()=>{
 const p=sample(),h=H.clone(H.defaults);p.assignments={d:{'egg-bhurji-and-masala-omelette':['e1']}};
 const t=H.totals(p,recipes,h,['d']);assert.equal(t['rice-cooked-right'],5);assert.equal(t['egg-bhurji-and-masala-omelette'],1);assert.equal(t['pepper-chicken-fry'],2);
 for(const id of ['v1','v2'])assert.ok(!H.recipients(p,'d',recipes['pepper-chicken-fry'],h).some(m=>m.id===id));
 assert.ok(!H.recipients(p,'d',recipes['pepper-chicken-fry'],h).some(m=>m.id==='e1'));
});
test('absence, half-portions, zero recipients and meal isolation affect every total',()=>{
 const p=sample(),h=H.clone(H.defaults);p.attendance={d:{n1:{eating:false,portions:1,time:'20:00'},v1:{eating:true,portions:.5,time:'20:00'}}};
 assert.equal(H.totals(p,recipes,h,['d'])['rice-cooked-right'],3.5);
 assert.equal(H.totals(p,recipes,h,['d'])['pepper-chicken-fry'],1);
 assert.equal(H.attendees(p,'l',h).length,5);
 p.assignments={d:{'pepper-chicken-fry':[]}};assert.equal(H.totals(p,recipes,h,['d'])['pepper-chicken-fry'],undefined);
 p.assignments.d['pepper-chicken-fry']=['v1'];assert.equal(H.totals(p,recipes,h,['d'])['pepper-chicken-fry'],undefined);
});
test('individual nutrition agrees with allocated quantities instead of a shared average',()=>{
 const p=sample(),h=H.clone(H.defaults);p.assignments={d:{'egg-bhurji-and-masala-omelette':['e1']}};
 const summed=h.members.reduce((n,m)=>n+(H.personNutrition(p,'d',m.id,recipes,h).p||0),0);
 const byDish=Object.entries(H.totals(p,recipes,h,['d'])).reduce((n,[id,q])=>n+recipes[id].nutr.p*q,0);
 assert.ok(Math.abs(summed-byDish)<1e-8);
 assert.equal(H.personNutrition(p,'d','v1',recipes,h).p,recipes['rice-cooked-right'].nutr.p);
});
test('two cooks never overlap their own tasks or a single appliance',()=>{
 const h=H.clone(H.defaults);h.mixer=true;
 const p={m:{d:[['badanekayi-yennegai',1],['kesari-bath',1],['ven-pongal',1]]}};
 const w=H.workload(p,'d',recipes,h);assert.ok(w.tasks.length===3);assert.ok(w.minutes>0);
 for(const c of [1,2]){const tasks=w.tasks.filter(t=>t.cook===c);for(let i=1;i<tasks.length;i++)assert.ok(tasks[i].start>=tasks[i-1].end);}
 assert.ok(w.tasks.find(t=>t.id==='ven-pongal').resources.includes('cooker3'));
 const single=H.clone(h);single.cooks=1;assert.ok(H.workload(p,'d',recipes,single).minutes>=w.minutes);
});
test('unknown preparation, unavailable mixer and different eating times stay explicit',()=>{
 const p=sample(),h=H.clone(H.defaults);assert.equal(H.workload(p,'d',recipes,h).minutes,null);
 assert.ok(H.equipmentIssues(recipes['badanekayi-yennegai'],h).includes('confirm mixer availability'));
 p.m.d=[['kesari-bath',1]];p.attendance={d:{n2:{eating:true,portions:1,time:'22:00'}}};
 assert.equal(H.workload(p,'d',recipes,h).minutes,null);
});
test('a combined session uses both cookers and does not double-book cooks across meals',()=>{
 const h=H.clone(H.defaults),a={...recipes['ven-pongal'],id:'first',yield:5},b={...a,id:'second'};
 const p={m:{b:[['first',1]],l:[['second',1]]}},w=H.workload(p,['b','l'],{first:a,second:b},h);
 assert.equal(w.tasks.length,2);assert.notEqual(w.tasks[0].cook,w.tasks[1].cook);
 assert.ok(w.tasks[0].resources.includes('cooker3'));assert.ok(w.tasks[1].resources.includes('cooker5'));
 assert.equal(w.minutes,null); // Breakfast and lunch times differ; safe storage needs review.
 const dinner={m:{d:[['first',1]]}};assert.equal(H.workload(dinner,'d',{first:a},h).startBy,'19:00');
});
test('new regional method quantities follow servings, frying pan oil stays fixed',()=>{
 const r=recipes['badanekayi-yennegai'];assert.match(C.stepText(r,0,5),/750 g/);assert.match(C.stepText(r,6,5),/15 tsp/);
 const p=recipes['cabbage-pakoda'];assert.match(C.stepText(p,3,5),/500 ml/);
 assert.ok(!C.stepText(r,0,5).includes('{{'));
});
test('household backup validates attendance, recipients and equipment',()=>{
 const x={v:2};for(const k of ['done','week','pantry','days','set','plan','basket','pick','me','wlog','labs'])x[k]={};
 x.set.household=H.clone(H.defaults);x.plan['2026-11-11']=sample();
 const ids=Object.keys(recipes);assert.equal(C.validImport(x,ids,[]),null);
 x.plan['2026-11-11'].attendance={d:{e1:{eating:true,portions:1,time:'25:00'}}};assert.match(C.validImport(x,ids,[]),/member meal/);
 delete x.plan['2026-11-11'].attendance;x.set.household.cooks=0;assert.match(C.validImport(x,ids,[]),/capacity/);
});
