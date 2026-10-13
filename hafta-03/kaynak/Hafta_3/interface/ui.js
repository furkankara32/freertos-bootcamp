'use strict';
const $=id=>document.getElementById(id);
let port,reader,writer,reading,parser,busy=false,ready=false,timeout,ackWait=null,lastRun=null;
const runs=[];
function status(s){$('status').textContent=s;}
function controls(){for(const id of ['run','fetchTrace','variant','load','traceOn'])$(id).disabled=busy||!ready;$('fetchTrace').disabled=busy||!ready||!lastRun?.traceBytes;$('connect').disabled=!!port;$('disconnect').disabled=!port;}
function setBusy(value){busy=value;clearTimeout(timeout);if(value)timeout=setTimeout(()=>{setBusy(false);ready=false;controls();status('Yanıt zaman aşımı. Bağlantıyı kesip tekrar bağlanın; kartın çalıştığını kontrol edin.');},20000);controls();}
function download(data,name,type='application/octet-stream'){const url=URL.createObjectURL(new Blob([data],{type}));const a=document.createElement('a');a.href=url;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);}
function saveName(r){return `W3_${r.variant}_${r.load}_run${r.id}_${r.capturedAt.replace(/[:.]/g,'-')}`;}
function updateRuns(){const host=$('runs');host.innerHTML='';for(const r of [...runs].reverse()){
 const el=document.createElement('article');el.className='result';const good=r.rows.filter(x=>x[2]);const avg=good.length?good.reduce((s,x)=>s+x[5],0)/good.length/1000:0;const max=good.length?Math.max(...good.map(x=>x[5]))/1000:0;
 const h=document.createElement('h3');h.textContent=`${r.variant} / ${r.load} · Koşu ${r.id}`;el.append(h);
 const p=document.createElement('p');p.textContent=`Deneme ${r.attempted} · Kabul ${r.accepted} · Başarısız ${r.failed} · Tamamlanan ${r.consumed} | Üretim → alma: ort. ${avg.toFixed(2)} ms / maks. ${max.toFixed(2)} ms`;el.append(p);
 const info=document.createElement('p');info.className='mini';info.textContent=`${r.source} · ${r.capturedAt} · İz ${r.traceEnabled?'açık':'kapalı'} · Trace kayıp sayacı: ${r.drops} · RX hata/kayıp: ${(r.rx||[]).join('/')||'bilinmiyor'}`;el.append(info);
 const buttons=document.createElement('div');buttons.className='controls';
 function button(label,fn){const b=document.createElement('button');b.textContent=label;b.onclick=fn;buttons.append(b);}
 button('CSV indir',()=>download(Week3Protocol.csv(r),saveName(r)+'.csv','text/csv;charset=utf-8'));
 button('Ham oturum indir',()=>download(r.raw,saveName(r)+'.txt','text/plain'));
 button('Metadata indir',()=>{const {rows,raw,trace,...metadata}=r;download(JSON.stringify({...metadata,trace:trace?{size:trace.size,checksum:trace.hash,drops:trace.drops,stopReason:trace.reason}:null},null,2),saveName(r)+'.json','application/json');});
 if(r.trace)button('.SVDat indir',()=>download(r.trace.bytes,saveName(r)+(r.trace.drops?'_INCOMPLETE':'')+'.SVDat'));
 el.append(buttons);host.append(el);
}}
function makeParser(imported=false){return new Week3Protocol.Parser((type,data)=>{
 if(type==='hello'&&!imported){ready=true;$('connection').textContent='Hafta 3 firmware doğrulandı';setBusy(false);status('Hazır. Varyantı ve yükü seçin.');}
 if(type==='ack'&&ackWait){const fn=ackWait;ackWait=null;fn(data);}
 if(type==='started'){lastRun=null;status(`Koşu ${data.id}: ${data.variant}/${data.load} çalışıyor. Yaklaşık 3–5 saniye; kayıt sırasında komut gönderilmez.`);}
 if(type==='result'){if(imported)data.source='imported_serial_log';runs.push(data);lastRun=data;setBusy(false);updateRuns();status('Deney tamamlandı. CSV’yi indirin; iz açıksa “Son izi karttan al” düğmesine basın.');}
 if(type==='progress')$('transfer').value=data;
 if(type==='trace'){
  const r=lastRun;if(!r||r.id!==data.id){setBusy(false);status('İz koşu kimliği sonuçla eşleşmiyor; kayıt reddedildi.');return;}
  r.trace=data;r.raw=parser.raw.join('\n')+'\n';setBusy(false);updateRuns();
  status(data.drops?'İz alındı fakat olay kaybı var. Eksik izden kesin zamanlama sonucu çıkarmayın.':`İz doğrulandı: ${data.size} bayt. .SVDat dosyasını SystemView’de açabilirsiniz.`);
 }
 if(type==='error'){setBusy(false);status('Hata: '+data);}
 });}
async function send(text){if(!writer)throw Error('Bağlantı yok');await writer.write(new TextEncoder().encode(text+'\n'));}
async function close(){ready=false;setBusy(false);if(ackWait){ackWait=null;}if(reader)await reader.cancel().catch(()=>{});if(reading)await reading.catch(()=>{});reader=null;if(writer){writer.releaseLock();writer=null;}if(port){await port.close().catch(()=>{});port=null;}$('connection').textContent='Bağlı değil';controls();}
$('connect').onclick=async()=>{try{
 if(!navigator.serial)throw Error('Web Serial yok. Chrome/Edge ve localhost adresini kullanın.');
 port=await navigator.serial.requestPort();await port.open({baudRate:230400});writer=port.writable.getWriter();reader=port.readable.getReader();parser=makeParser();controls();setBusy(true);
 reading=(async()=>{let buffer='';const decoder=new TextDecoder();try{for(;;){const {value,done}=await reader.read();if(done)break;buffer+=decoder.decode(value,{stream:true});let cut;while((cut=buffer.indexOf('\n'))>=0){const line=buffer.slice(0,cut).replace(/\r$/,'');buffer=buffer.slice(cut+1);$('log').textContent=($('log').textContent+line+'\n').slice(-14000);parser.line(line);}if(buffer.length>10000)throw Error('Geçersiz seri akış');}}catch(e){ready=false;setBusy(false);status('Bağlantı kesildi: '+e.message);}finally{reader?.releaseLock();reader=null;}})();
 await send('HELLO');
 }catch(e){status(e.message);await close();}};
$('disconnect').onclick=()=>close().catch(e=>status(e.message));
$('run').onclick=async()=>{try{setBusy(true);const enabled=$('traceOn').checked;
 await new Promise((resolve,reject)=>{const t=setTimeout(()=>{ackWait=null;reject(Error('TRACE ayarı onaylanmadı'));},3000);ackWait=value=>{clearTimeout(t);value===(enabled?'TRACE_ON':'TRACE_OFF')?resolve():reject(Error('Beklenmeyen onay'));};send('TRACE '+(enabled?'ON':'OFF')).catch(reject);});
 await send(`RUN ${$('variant').value} ${$('load').value}`);
 }catch(e){setBusy(false);status(e.message);}};
$('fetchTrace').onclick=async()=>{try{setBusy(true);$('transfer').value=0;status('İz aktarılıyor; byte sayısı ve FNV-1a checksum doğrulanacak.');await send('TRACE');}catch(e){setBusy(false);status(e.message);}};
$('import').onchange=async e=>{if(busy){status('Önce mevcut aktarımın bitmesini bekleyin.');return;}const file=e.target.files[0];if(!file)return;const input=await file.text();parser=makeParser(true);for(const line of input.split(/\r?\n/))parser.line(line);};
controls();
