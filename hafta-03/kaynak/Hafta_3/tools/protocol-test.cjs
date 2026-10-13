const assert=require('node:assert/strict'),fs=require('fs'),path=require('path');
const {Parser,fnv,csv}=require('../interface/protocol.js');
const folder=path.join(__dirname,'../measurements/hardware');let count=0;
for(const name of fs.readdirSync(folder).filter(n=>n.endsWith('.txt'))){
 const events=[];const p=new Parser((type,data)=>events.push({type,data}));
 fs.readFileSync(path.join(folder,name),'utf8').split(/\r?\n/).forEach(l=>p.line(l));
 assert.equal(events.filter(e=>e.type==='error').length,0,name);
 const result=events.find(e=>e.type==='result')?.data;assert.ok(result,name);assert.equal(result.attempted,44);
 assert.equal(result.rows.filter(r=>r[2]).length,result.consumed);
 for(const row of csv(result).trim().split('\n').slice(1))if(row.split(',')[2]==='0')assert.ok(row.endsWith(','),'failed latency must be empty');
 if(result.traceEnabled){const tr=events.find(e=>e.type==='trace')?.data;assert.ok(tr);assert.equal(tr.drops,0);assert.equal(tr.id,result.id);assert.deepEqual(Buffer.from(tr.bytes),fs.readFileSync(path.join(folder,name.replace('.txt','.SVDat'))));}
 count++;
}
function invalid(lines){const events=[];const p=new Parser((t,d)=>events.push([t,d]));lines.forEach(l=>p.line(l));assert.ok(events.some(e=>e[0]==='error'));assert.ok(!events.some(e=>e[0]==='trace'));}
invalid(['#TRACE,1,12,00000000,0,1','#HEX,1,0011']);
invalid(['#TRACE,1,12,00000000,0,1','#HEX,0,00112233445566778899AABB','#TRACE_END,1']);
invalid(['#TRACE,1,12,00000000,0,1','#HEX,0,GG']);
invalid(['#TRACE,1,40000,00000000,0,1']);
invalid(['#RESULT,1,A,BURST,44,24,20,24,1,12886,0','#ROW,1,1,1,123,10,20','#ROW,1,1,1,123,10,20']);
invalid(['#RESULT,1,A,BURST,44,24,20,24,1,12886,0','#END,1']);
assert.equal(fnv(Buffer.from('hello')),0x4f9f2cab);
console.log(JSON.stringify({real_sessions:count,malformed_cases:6,fnv_vector:'passed',result:'passed'},null,2));
