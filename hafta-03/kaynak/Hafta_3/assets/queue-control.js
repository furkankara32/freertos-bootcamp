'use strict';
window.initQueueControl=function(root){
 const $=k=>root.querySelector(`[data-qc="${k}"]`),mode=root.dataset.mode,animations=[];
 let step=0,items=[],serial=10;
 const frame=(q,wait,ready,title,description,api)=>({q,wait,ready,title,description,api});
 const send=mode==='send',who=send?'Gönderici':'Alıcı';
 const frames=[
  frame(send?[10,20,30]:[],[],[],send?'Queue dolu: boş slot yok.':'Queue boş: okunacak mesaj yok.','Önce düşük, sonra yüksek öncelikli task çağrı yapacak. Çağrı sırasını bu senaryoda elle ilerletiyoruz.','uxLength = 3'),
  frame(send?[10,20,30]:[],['P1'],[],`${who} P1 → Blocked`,send?'P1, 40 göndermek için yer bekliyor. 40 henüz queue içinde değil.':'P1, veri olmadığı için mesaj bekliyor. Henüz hiçbir payload okunmadı.',send?'xQueueSendToBack(q, &v40, 30)':'xQueueReceive(q, &outP1, 30)'),
  frame(send?[10,20,30]:[],['P3','P1'],[],`${who} P3 de bekliyor.`, 'P3 daha sonra gelse de yüksek önceliği nedeniyle listenin başındadır. İki bekleyen task, iki mesaj demek değildir.',send?'xQueueSendToBack(q, &v50, 100)':'xQueueReceive(q, &outP3, 100)'),
  frame(send?[20,30]:[42],['P1'],['P3:Ready'],send?'Receive bir slot açtı → P3 Ready.':'Send bir mesaj ekledi → P3 Ready.',send?'10 okundu; sayaç 3 → 2. P3 bekleme listesinden çıkarıldı. Bekleyen 50 henüz yazılmadı.':'42 kopyalandı; sayaç 0 → 1. P3 bekleme listesinden çıkarıldı. Mesaj henüz alınmadı.',send?'xQueueReceive(q, &out, 0) → pdPASS':'xQueueSendToBack(q, &v42, 0) → pdPASS'),
  frame(send?[20,30,50]:[],['P1'],['P3:Running'],send?'P3 çalıştı → gönderim tamamlandı.':'P3 çalıştı → Receive tamamlandı.',send?'Scheduler P3’ü çalıştırdığında çağrı yeniden kontrol eder, 50 kopyalanır; sayaç 2 → 3.':'Scheduler P3’ü çalıştırdığında çağrı yeniden kontrol eder, 42 alınır; sayaç 1 → 0.',send?'P3: bekleyen xQueueSendToBack() → pdPASS':'P3: bekleyen xQueueReceive() → pdPASS'),
  frame(send?[20,30,50]:[],[],['P1:Ready'], 'P1 için bekleme süresi doldu.', 'Arada başka queue işlemi olmadı. Timeout, P1’i event listesinden çıkarıp Ready yapar. Sayaç değişmez; task henüz dönüş kodunu işlemedi.','Timeout → Blocked → Ready'),
  frame(send?[20,30,50]:[],[],['P1:Running'], 'P1 çalıştı → işlem başarısız.',send?'Queue hâlâ dolu olduğundan P1’in 40 gönderimi başarısız döner. Sayaç değişmez.':'Queue hâlâ boş olduğundan P1’in Receive çağrısı başarısız döner. Sayaç değişmez.',send?'P1: xQueueSendToBack() → errQUEUE_FULL':'P1: xQueueReceive() → errQUEUE_EMPTY')
 ];
 function animate(el){if(!matchMedia('(prefers-reduced-motion: reduce)').matches)animations.push(el.animate([{opacity:.35,transform:'translateY(10px)'},{opacity:1,transform:'translateY(0)'}],{duration:330,easing:'ease-out'}));}
 function render(f){
  $('slots').innerHTML=Array.from({length:3},(_,i)=>`<div class="qc-slot ${i<f.q.length?'filled':''}">${f.q[i]??'·'}</div>`).join('');
  $('count').textContent=f.q.length;$('meter').style.width=f.q.length/3*100+'%';
  for(const k of ['send','receive'])$(''+k).innerHTML=(mode===k?f.wait:[]).map(p=>`<span class="qc-chip waiting">${p} · Blocked</span>`).join('<span aria-hidden="true">→</span>')||'<span class="qc-empty">∅ Liste boş</span>';
  $('ready').innerHTML=f.ready.map(p=>{const [id,state]=p.split(':');return `<span class="qc-chip ${state.toLowerCase()}">${id} · ${state}</span>`;}).join('')||'<span class="qc-empty">Bu adımda gösterilen task yok</span>';
  for(const k of ['title','description','api'])$(k).textContent=f[k];
  $('step').textContent=mode==='count'?'CANLI SAYAÇ':`ADIM ${step+1} / ${frames.length}`;
  if(mode!=='count'){$('previous').disabled=step===0;$('advance').disabled=step===frames.length-1;}
  animate($('count'));animate($('slots'));animate($(mode==='count'?'ready':mode));animate($('ready'));
 }
 function reset(){step=0;items=[];serial=10;if(mode==='count')render(frame(items,[],[],'Sayaç = queue içindeki mesaj adedi.','İşlemleri deneyin. Tüm çağrılar 0 tick; dolu/boş durumda task bekleme listesine girmez.','uxQueueMessagesWaiting(q) → 0'));else render(frames[step]);}
 if(mode==='count'){
  $('controls').innerHTML='<button data-op="back">Send to Back +</button><button data-op="front">Send to Front +</button><button data-op="receive">Receive −</button><button data-op="peek">Peek =</button>';
  root.querySelectorAll('[data-op]').forEach(b=>b.onclick=()=>{const op=b.dataset.op;let title,desc,api;
   if(op==='back'||op==='front'){api=`xQueueSendTo${op==='back'?'Back':'Front'}(q, &value, 0)`;if(items.length===3){title='Queue dolu → sayaç değişmez.';desc='errQUEUE_FULL: 0 tick çağrısı beklemez; gönderici event listesine girmez.';}else{const value=serial;serial+=10;items[op==='back'?'push':'unshift'](value);title=`${value} kopyalandı → sayaç +1`;desc='pdPASS: ekleme yönü sıralamayı değiştirir; her iki yönde de mesaj adedi bir artar.';}}
   else{api=`xQueue${op==='peek'?'Peek':'Receive'}(q, &out, 0)`;if(!items.length){title='Queue boş → sayaç değişmez.';desc='errQUEUE_EMPTY: 0 tick çağrısı beklemez; alıcı event listesine girmez.';}else{const value=items[0];if(op==='receive')items.shift();title=op==='peek'?`${value} kopyalandı; queue içinde kaldı.`:`${value} okundu ve çıkarıldı → sayaç −1`;desc=op==='peek'?'pdPASS: Peek sayacı azaltmaz.':'pdPASS: Receive ön elemanı çıkarır.';}}
   render(frame(items,[],[],title,desc,api+` · uxMessagesWaiting = ${items.length}`));});
 }else{
  $('controls').innerHTML='<button data-qc="previous">← Önceki olay</button><button class="primary" data-qc="advance">Sonraki olayı çalıştır →</button><span class="mini">Ready ≠ işlem tamamlandı · Boş slot / mesaj rezerve edilmez.</span>';
  $('previous').onclick=()=>{step=Math.max(0,step-1);render(frames[step]);};$('advance').onclick=()=>{step=Math.min(frames.length-1,step+1);render(frames[step]);};
 }
 $('reset').onclick=reset;reset();return()=>animations.forEach(a=>a.cancel());
};
