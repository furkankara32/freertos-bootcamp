/* Same parser for browser UI and Node protocol tests. No synthetic data path. */
(function(root){
'use strict';
function fnv(bytes){let h=2166136261;for(const b of bytes)h=Math.imul(h^b,16777619)>>>0;return h;}
function number(s){if(!/^\d+$/.test(s||''))throw Error('Geçersiz sayısal alan');const n=Number(s);if(!Number.isSafeInteger(n))throw Error('Sayı aralık dışında');return n;}
class Parser{
 constructor(callback){this.callback=callback;this.run=null;this.trace=null;this.raw=[];}
 emit(type,data){this.callback(type,data);}
 line(line){line=line.trim();if(!line)return;this.raw.push(line);const a=line.split(',');
  try{
   if(a[0]==='#HELLO'){if(a[1]!=='WEEK3'||a[2]!=='1')throw Error('Hafta 3 firmware/protokol sürümü eşleşmiyor');this.emit('hello',a.slice(1));}
   else if(a[0]==='#ACK')this.emit('ack',a[1]);
   else if(a[0]==='#ERROR'){this.trace=null;this.emit('error',a.slice(1).join(','));}
   else if(a[0]==='#RUN'){this.run=null;this.trace=null;this.raw=[line];this.emit('started',{id:number(a[1]),variant:a[2],load:a[3]});}
   else if(a[0]==='#RESULT'){
    if(a.length!==11||!['A','B','C'].includes(a[2])||!['NORMAL','BURST'].includes(a[3]))throw Error('Sonuç başlığı geçersiz');
    this.run={id:number(a[1]),variant:a[2],load:a[3],attempted:number(a[4]),accepted:number(a[5]),failed:number(a[6]),consumed:number(a[7]),traceEnabled:number(a[8]),traceBytes:number(a[9]),drops:number(a[10]),rows:[],capturedAt:new Date().toISOString(),source:'hardware_serial'};
   }else if(a[0]==='#ROW'){
    if(!this.run||a.length!==7)throw Error('Sonuç başlığı olmadan/veri eksik satır');
    const nums=a.slice(1).map(number);if(nums[0]<1||nums[0]>44||nums[1]>1||nums[2]>1||this.run.rows.some(r=>r[0]===nums[0]))throw Error('Tekrarlanan/geçersiz olay');
    this.run.rows.push(nums);
   }else if(a[0]==='#STACK'){if(this.run)this.run.stack=a.slice(1).map(number);}
   else if(a[0]==='#RX'){if(this.run)this.run.rx=a.slice(1).map(number);}
   else if(a[0]==='#END'){
    const r=this.run;
    if(!r||number(a[1])!==r.id||r.rows.length!==r.attempted||r.attempted!==44||r.accepted+r.failed!==r.attempted||r.accepted!==r.consumed||r.rows.filter(x=>x[1]).length!==r.accepted||r.rows.filter(x=>x[2]).length!==r.consumed||r.rows.some(x=>x[1]!==x[2]))throw Error('Sayaç/satır tutarsızlığı veya eksik kayıt');
    r.rows.sort((x,y)=>x[0]-y[0]);r.raw=this.raw.join('\n')+'\n';this.emit('result',r);this.run=null;
   }else if(a[0]==='#TRACE'){
    if(a.length!==6||!/^[0-9A-Fa-f]{8}$/.test(a[3]))throw Error('Trace başlığı geçersiz');
    const size=number(a[2]);if(size<10||size>32768)throw Error('Trace boyutu geçersiz');
    this.trace={id:number(a[1]),size,hash:parseInt(a[3],16)>>>0,drops:number(a[4]),reason:number(a[5]),bytes:new Uint8Array(size),offset:0};
   }else if(a[0]==='#HEX'){
    const t=this.trace;if(!t||number(a[1])!==t.offset||!/^([0-9A-Fa-f]{2})+$/.test(a[2]||'')||t.offset+a[2].length/2>t.size)throw Error('Eksik/sırası bozuk trace parçası');
    for(let i=0;i<a[2].length;i+=2)t.bytes[t.offset++]=parseInt(a[2].slice(i,i+2),16);
    this.emit('progress',Math.round(t.offset/t.size*100));
   }else if(a[0]==='#TRACE_END'){
    const t=this.trace;
    if(!t||number(a[1])!==t.id||t.offset!==t.size||fnv(t.bytes)!==t.hash)throw Error('Trace uzunluğu/checksum doğrulanamadı; dosya kaydedilmedi');
    this.trace=null;this.emit('trace',t);
   }
  }catch(e){this.trace=null;this.run=null;this.emit('error',e.message);}
 }
}
function csv(r){return 'id,accepted,received,generated_us,send_call_us,generation_to_receive_us\n'+r.rows.map(x=>x.slice(0,5).join(',')+','+(x[2]?x[5]:'')).join('\n')+'\n';}
root.Week3Protocol={Parser,fnv,csv};if(typeof module!=='undefined')module.exports=root.Week3Protocol;
})(typeof globalThis!=='undefined'?globalThis:this);
