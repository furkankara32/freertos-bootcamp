'use strict';
window.initQueueOperations=function(root){
 const el=id=>root.querySelector('#'+id),NS='http://www.w3.org/2000/svg';
 let queue=[],nextId=1,busy=false,disposed=false,animations=[],generation=0,demo=-1;
 const actions=['qFront','qBack','qReceive','qPeek'];
 const steps=[['back',10],['back',20],['front',99],['peek'],['receive'],['receive']];
 const position=i=>({x:235+95*i,y:73}),source={x:78,y:222},output={x:940,y:222};
 function svg(tag,attrs,parent){const n=document.createElementNS(NS,tag);for(const [k,v]of Object.entries(attrs))n.setAttribute(k,v);parent.append(n);return n;}
 function token(item,pos,parent,kind=''){const g=svg('g',{'class':'q-token '+kind,'data-message':item.id,transform:`translate(${pos.x} ${pos.y})`},parent);svg('rect',{width:82,height:65,rx:10},g);const id=svg('text',{x:41,y:19,'text-anchor':'middle',class:'q-id'},g);id.textContent='MSG '+String(item.id).padStart(2,'0');const value=svg('text',{x:41,y:48,'text-anchor':'middle',class:'q-value'},g);value.textContent=item.value;return g;}
 function order(items){return items.length?'[ '+items.map(x=>x.value).join(' → ')+' ]':'[ boş ]';}
 function lock(value){busy=value;actions.forEach(id=>el(id).disabled=value);el('qDemo').disabled=value;el('qValue').disabled=value;root.setAttribute('aria-busy',String(value));}
 function draw(){el('qMessages').replaceChildren();queue.forEach((m,i)=>token(m,position(i),el('qMessages'),m.kind));el('qOrder').textContent=order(queue);el('qCount').textContent=`${queue.length} / 6 dolu`;el('qDiagramDesc').textContent='Okunma sırası front → back: '+order(queue)+'. Receive ön elemanı çıkarır; Peek çıkarmaz.';}
 function motion(node,points){if(matchMedia('(prefers-reduced-motion: reduce)').matches)return Promise.resolve();const a=node.animate(points.map(p=>({transform:`translate(${p.x}px, ${p.y}px)`})),{duration:780,easing:'cubic-bezier(.2,.7,.2,1)'});animations.push(a);return a.finished.catch(()=>{});}
 function reset(){generation++;animations.forEach(a=>a.cancel());animations=[];queue=[];nextId=1;demo=-1;el('qTransient').replaceChildren();el('qOut').textContent='—';el('qValue').value=10;el('qProducerValue').textContent='10';el('qCode').textContent='Bir işlem seçin.';el('qStatus').textContent='Boş kuyruk. 10 ve 20’yi arkaya, 99’u öne gönderip Receive deneyin.';el('qBefore').textContent='Her işlem sıralamayı ve doluluk sayısını günceller.';el('qDemo').textContent='Rehberli örnek: başlat';root.querySelectorAll('.q-route').forEach(n=>n.classList.remove('chosen'));lock(false);draw();}
 async function operate(kind,value,fromDemo=false){
  if(busy||disposed)return;
  if(!fromDemo){demo=-1;el('qDemo').textContent='Rehberli örnek: başlat';}
  const send=kind==='front'||kind==='back';
  if(send){value=Number(value);if(!Number.isInteger(value)||value<0||value>999){el('qStatus').textContent='Mesaj değeri 0–999 arasında bir tam sayı olmalı.';return;}}
  const before=queue.slice(),version=generation;const api={front:'xQueueSendToFront(q, &msg, 0)',back:'xQueueSendToBack(q, &msg, 0)',receive:'xQueueReceive(q, &out, 0)',peek:'xQueuePeek(q, &out, 0)'}[kind];
  el('qBefore').textContent='Önce: '+order(before);root.querySelectorAll('.q-route').forEach(n=>n.classList.remove('chosen'));el(kind==='front'?'qFrontPath':kind==='back'?'qBackPath':'qReceivePath').classList.add('chosen');
  if(send&&queue.length===6){el('qCode').textContent=api+' → errQUEUE_FULL';el('qStatus').textContent='Queue dolu. 0 tick: beklemeden başarısız. Front da mevcut mesajın üzerine yazmaz; sıra değişmedi.';return;}
  if(!send&&!queue.length){el('qCode').textContent=api+' → errQUEUE_EMPTY';el('qStatus').textContent='Queue boş. 0 tick: beklemeden başarısız; out değişmedi.';return;}
  lock(true);animations=[];el('qTransient').replaceChildren();el('qCode').textContent=api+';';
  let item,explanation;
  if(send){item={id:nextId++,value,kind:kind==='front'?'front-token':'back-token'};if(kind==='front')queue.unshift(item);else queue.push(item);explanation=kind==='front'?`${value} ön sıraya eklendi. Bir sonraki Receive artık bu mesajı alır.`:`${value} arka sıraya eklendi. Önündeki mesajların okunma sırası korunur.`;}
  else {item=queue[0];if(kind==='receive')queue.shift();explanation=kind==='receive'?`Öndeki ${item.value} out değişkenine kopyalandı ve kuyruktan çıkarıldı. Bir yer boşaldı.`:`Öndeki ${item.value} out değişkenine kopyalandı; kuyrukta kaldı. Doluluk değişmedi.`;}
  draw();const pending=[];
  queue.forEach((m,i)=>{const node=el('qMessages').querySelector(`[data-message="${m.id}"]`);const old=before.findIndex(x=>x.id===m.id),dest=position(i);if(old>=0&&old!==i)pending.push(motion(node,[position(old),dest]));if(send&&m.id===item.id)pending.push(motion(node,[source,{x:source.x,y:155},{x:kind==='back'?840:dest.x,y:155},dest]));});
  if(!send){const ghost=token(item,output,el('qTransient'));pending.push(motion(ghost,[position(0),{x:position(0).x,y:155},{x:output.x,y:155},output]));}
  el('qStatus').textContent=send?'Mesaj içeriği seçilen uca kopyalanıyor…':kind==='peek'?'Ön elemanın kopyası okunuyor; queue içeriği korunuyor…':'Ön eleman tüketiciye taşınıyor…';
  await Promise.all(pending);if(disposed||version!==generation)return;
  el('qTransient').replaceChildren();if(!send)el('qOut').textContent=item.value;else{el('qValue').value=value>=990?0:value+10;el('qProducerValue').textContent=el('qValue').value;}
  el('qCode').textContent=api+' → pdPASS';el('qStatus').textContent=explanation;lock(false);
 }
 for(let i=0;i<6;i++){const p=position(i);svg('rect',{x:p.x,y:p.y,width:82,height:65,rx:10,class:'q-slot'},el('qSlots'));const t=svg('text',{x:p.x+41,y:161,'text-anchor':'middle',class:'q-label'},el('qSlots'));t.textContent='Sıra '+(i+1);}
 el('qValue').oninput=()=>el('qProducerValue').textContent=el('qValue').value||'—';
 el('qFront').onclick=()=>operate('front',el('qValue').value);el('qBack').onclick=()=>operate('back',el('qValue').value);el('qReceive').onclick=()=>operate('receive');el('qPeek').onclick=()=>operate('peek');el('qReset').onclick=reset;
 el('qDemo').onclick=async()=>{if(demo<0||demo>=steps.length){reset();demo=0;}const step=steps[demo++];if(step[1]!==undefined){el('qValue').value=step[1];el('qProducerValue').textContent=step[1];}const version=generation;await operate(step[0],step[1],true);if(disposed||generation!==version)return;el('qDemo').textContent=demo===steps.length?'Örnek tamamlandı · yeniden başlat':`Örnek adımı ${demo}/${steps.length} · sonrakini göster`;};
 reset();return ()=>{disposed=true;generation++;animations.forEach(a=>a.cancel());};
};
