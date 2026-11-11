const test = require('node:test');
const assert = require('node:assert/strict');
const C = require('../src/core.js');
test('fractions, decimals and ranges scale without lost precision', () => {
  for (const [q,f,result] of [['¼ tsp',.5,'⅛ tsp'],['75 ml',.5,'37.5 ml'],['120 g',2,'240 g'],['1½ tbsp',2,'3 tbsp'],['1/2 tsp',2,'1 tsp'],['1 1/2 cups',2,'3 cups'],['2–3 cloves',2,'4–6 cloves'],['½ cup + 1 tbsp',2,'1 cup + 2 tbsp'],['½ / ¼ tsp',2,'1 / ½ tsp']]) assert.equal(C.scaleQuantity(q,f),result);
  assert.throws(()=>C.scaleQuantity('1 g',-1));
});
test('small exact amounts never become a little',()=>assert.equal(C.scaleQuantity('⅛ tsp',.5),'0.0625 tsp'));
test('pantry stock is independent of shopping intentions',()=>{assert.equal(C.pantryAvailable(2),false); assert.equal(C.pantryAvailable(0),true); assert.equal(C.pantryAvailable(1),true);});
test('storage failure is observable; successful write preserves JSON',()=>{
  assert.equal(C.writeStorage({setItem(){throw new Error('quota')}},'state',{}).ok,false);
  let stored; assert.equal(C.writeStorage({setItem(k,v){stored=v}},'state',{a:1}).ok,true); assert.deepEqual(JSON.parse(stored),{a:1});
});
test('time filters include preparation and exclude unknown totals',()=>{
  const r={time:'20 min + soaking',timing:{cookMinutes:[20,25],prerequisiteMinutes:[180,240],prerequisites:['Soak dal']}};
  assert.equal(C.withinTime(r,30),false); assert.equal(C.timing(r,false).min,200); assert.equal(C.timing(r,true).max,25);
  assert.equal(C.withinTime({time:'20 minutes',minutes:20},30),false);
});
test('import validates version, pantry and plan references',()=>{
  const x={v:2}; for(const k of ['done','week','pantry','days','set','plan','basket','pick','me','wlog','labs']) x[k]={};
  assert.equal(C.validImport(x,['rice'],['atta']),null);
  assert.match(C.validImport({...x,v:3},[],[]),/version/);
  assert.match(C.validImport({...x,pantry:{atta:5}},[],['atta']),/pantry/);
  assert.match(C.validImport({...x,plan:{'2026-11-06':{s:2,n:1,m:{d:[['unknown',1]]}}}},['rice'],[]),/Unknown/);
});
