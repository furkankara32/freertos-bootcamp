"""Rebuild final V1 and matched-scenario comparison reports from hardware evidence."""
from pathlib import Path
import csv, hashlib, json, math, statistics
W=Path(__file__).resolve().parents[1]; R=W/'reports'
S={('V1','S0'):'20261004-151001-observation',('V1','S5'):'20261004-151332-observation',('V2','S0'):'20261003-160814-observation',('V2','S5'):'20261003-161935-observation'}
D={};manifest=[];events=[]
for key,session in S.items():
 v,sc=key;p=W/'traces'/v.lower()/sc/session
 j=json.loads((p/'dump.json').read_text());m=json.loads((p/'session.json').read_text());good=[x for x in j['rows'] if x['status']=='ok']
 values=sorted((x['t4_us']-x['t0_us'])&0xffffffff for x in good)
 assert len(good)==j['counters']['ok'] and len(j['rows'])==j['counters']['accepted'] and not m['decoder_errors']
 windows=sorted(p.glob('window-*/trace.json'));assert len(windows)==(6 if sc=='S0' else 8)
 for t in windows:
  a=json.loads(t.read_text());assert a['clean'] and a['dropped_events']==0
  assert hashlib.sha256(t.with_name('recording.SVDat').read_bytes()).hexdigest()==a['trace_sha256']
 duration=((j['metadata']['run_stop_us']-j['metadata']['run_start_us'])&0xffffffff)/1e6
 stats={'n':len(values),'accepted':j['counters']['accepted'],'min':min(values),'mean':statistics.mean(values),'median':statistics.median(values),'p95':values[math.ceil(.95*len(values))-1],'max':max(values),'late10':sum(x>10000 for x in values),'late20':sum(x>20000 for x in values),'duration':duration}
 stages=[statistics.mean((x[f't{i+1}_us']-x[f't{i}_us'])&0xffffffff for x in good) for i in range(4)]
 D[key]={'dump':j,'stats':stats,'stages':stages,'path':p,'meta':m}
 manifest.append({'version':v,'scenario':sc,'session':session,'dump_sha256':hashlib.sha256((p/'dump.json').read_bytes()).hexdigest(),'elf_sha256':m['build']['elf_sha256'],'stats':stats,'stage_means_us':stages})
 for x in j['rows']:
  events.append({'version':v,'scenario':sc,'session':session,'event_id':x['event_id'],'status':x['status'],'r_us':((x['t4_us']-x['t0_us'])&0xffffffff) if x['status']=='ok' else '', 'trace_condition':'intermittent; per-event trace membership not classified','elf_sha256':m['build']['elf_sha256'],'dump_path':str(p/'dump.json')})
def table(keys):
 out=['| Sürüm / senaryo | Kabul | Tamamlanan | Min | Ortalama | Medyan | p95 | Maks | >10 ms | >20 ms |','|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
 for k in keys:
  s=D[k]['stats'];out.append(f'| {k[0]} / {k[1]} | {s["accepted"]} | {s["n"]} | '+' | '.join(f'{s[n]/1000:.3f}' for n in ['min','mean','median','p95','max'])+f' | {s["late10"]} | {s["late20"]} |')
 return '\n'.join(out)+'\n\nSüreler ms; istatistikler yalnız tamamlanan olaylar içindir. Eşik aşımı sayıları da tamamlanan olaylara aittir; düşen mesajlar ayrıca gösterilir.'
def stage_table(sc):
 out=['| Ortalama aşama | V1 (µs) | V2 (µs) |','|---|---:|---:|']
 for i,label in enumerate(['t1−t0: kesme → olayı alma','t2−t1: mesaj hazırlama','t3−t2: hazır → TX başlangıcı','t4−t3: TX başlangıcı → UART TC']):out.append(f'| {label} | {D[("V1",sc)]["stages"][i]:.3f} | {D[("V2",sc)]["stages"][i]:.3f} |')
 return '\n'.join(out)
def evidence(keys):
 out=[]
 for v,sc in keys:
  d=D[(v,sc)];rel=d['path'].relative_to(W).as_posix();name=('v1-' if v=='V1' else '')+sc.lower()+'-observation-events.csv';window='02' if v=='V1' else '01'
  out.append(f'- **{v} {sc}:** [dump](../{rel}/dump.json), [oturum](../{rel}/session.json), [SystemView kaydı](../{rel}/window-{window}/recording.SVDat), [çözümlenmiş olaylar](../docs/{name}).')
 return '\n'.join(out)
limitations='''- Manuel girişler aynı fiziksel basış dizisi değildir. Koşu süreleri ve basış hızları farklıdır; V1 S5'te daha fazla buton girişi vardır. Bu yüzden değişikliklere ait bağımsız nedensel katkı yüzdeleri veya eşit giriş altında kesin hızlanma iddiası kurulmaz.
- Her koşu aralıklı trace pencereleri içerir. İstatistikler trace açık/kapalı aralıkların birlikte bulunduğu tüm UART koşusundandır. Ayrı eşlenmiş trace ek yükü deneyi yoktur; SWD okuma ve izleme maliyeti sıfır varsayılmaz.
- S0 için iki sürümde de 6×1000 ms, S5 için 8×500 ms trace alındı; tüm 28 pencere taşmasızdır. İlk başarısız/butonsuz hazırlık pilotları sonuç hesabına alınmadı ve silinmedi.
- p95, sıralı dizinin ceil(0.95×n) elemanıdır (nearest rank). TIM5 farkları unsigned 32 bit hesaplandı. t0 fiziksel parmak hareketi değil kabul edilen kesme zamanıdır; t1 görev switch-in değil olayın kuyruktan alınmasıdır.
- t3 DMA başlatma çağrısının öncesidir; t4 UART TC callback'idir. t4−t3 duvar süresidir, CPU çalışma süresi değildir. Preemption ve callback gecikmesi içerebilir.
- V1'in 20 ms ve V2'nin 10 ms hedefleri farklıdır; adil okunabilmesi için her iki eşik her sürümde hesaplanmıştır. Düşen mesajlar başarılı veya sıfır gecikmeli sayılmamıştır.
- Bu sonuçlar gözlenen koşulara aittir; WCRT/deadline garantisi değildir. Hafta 1'in eski rapor sonuçları yeni ölçüm olarak kullanılmamıştır. S1–S4 ve Trexcope kapsam dışıdır.'''
v1='''# V1 — S0 ve S5 SystemView sonuç raporu

**Tarih:** 4 Ekim 2026. **Kaynak:** GitHub commit `b74863a3a27ebeb14ca932737005b68d9eee1945`. Kaynak ayrı `projects/v1` dizinine indirildi; bu rapor yeni gerçek kart kayıtlarına dayanır.

## Sonuç

V1 düşük yükte 73 buton olayının tamamını yaklaşık 5,63 ms içinde gönderdi. S5 yoğun yük koşusunda ortak TX kuyruğu 16/16 doldu; 108 kabul edilmiş buton olayından 44'ü gönderim kuyruğuna alınamadı. Tamamlanan 64 olayın ortalama yanıtı 144,949 ms, en uzunu 165,562 ms oldu. Sorun yalnız buton görevinin CPU beklemesi değildir: mesaj hazırlandıktan sonraki TX beklemesi baskındır.

## Sistem ve ölçüm düzeni

STM32F407VG, 168 MHz; FreeRTOS 10.3.1; Release/-Os; USART2 115200 baud, 64 bayt sabit çerçeve. TelemetryTask/ButtonTask/UartTxTask öncelikleri 3/2/1. Buton giriş kuyruğu 8, ortak TX FIFO 16 eleman. S0'da telemetri yoktur. S5'te 100 Hz telemetri ve her üretimde tek parça yaklaşık 5 ms CPU işi vardır. İzleme için bu tasarım kararları değiştirilmedi.

TIM5 1 MHz t0–t4 zamanlarını üretir. SystemView DWT 168 MHz ile görev/ISR olaylarını kaydeder. ST-LINK, otomatik dondurulan trace tamponunu işlemci çalışırken okur. UART dump CRC doğrulamasından geçti. İzleme açık/kapalı ARM derlemeleri ve V1'in 21 yazılım testi başarılıdır; bunlar fiziksel zamanlama kabulü yerine geçmez.

## S0 ve S5 ölçümleri

'''+table([('V1','S0'),('V1','S5')])+'''

| Sayaç | S0 | S5 |
|---|---:|---:|
| BTN TX kuyruk kaybı | 0 | 44 / 108 (%40,74) |
| TEL TX kuyruk kaybı | 0 | 49 / 4158 (%1,18) |
| Telemetri üretilen / tamamlanan | 0 / 0 | 4158 / 4109 |
| Ortak TX kuyruğu en yüksek doluluk | 1 / 16 | 16 / 16 |
| Buton giriş kuyruğu en yüksek doluluk | 1 / 8 | 1 / 8 |
| Debounce reddi | 5 | 8 |
| UART hatası / TX timeout | 0 / 0 | 0 / 0 |

Debounce reddi kabul edilmiş bir olayın kaybı değildir. Buton giriş kuyruğu kaybı, record overflow, decoder hatası ve trace overflow iki koşuda da 0'dır. Firmware'in `COMPLETE` durumu koşunun ve dump'ın tamamlandığını belirtir; tüm mesajların başarıyla gönderildiği anlamına gelmez.

## S0: düşük yükte gönderim

`window-02`, run=1, id=13: sıra 593 BTN_ACCEPT, 599 BTN_TASK, 600 BTN_READY, 610 BTN_TX_START, 640 BTN_TX_TC.

| Aşama | Süre (µs) |
|---|---:|
| t1−t0 | 24 |
| t2−t1 | 27 |
| t3−t2 | 47 |
| t4−t3 | 5557 |
| Toplam | 5655 |

Görev ve kuyruk beklemesi küçüktür; sürenin çoğu 115200 baud UART gönderimindedir. UART görevi DMA'yı başlattıktan sonra beklemeye geçer; yaklaşık 5,56 ms'nin tamamı CPU tüketimi değildir.

## S5: ortak FIFO'da bekleme ve düşme

**Tamamlanan örnek:** `window-02`, run=2, id=18. Sıra 1732 BTN_ACCEPT, 1738 BTN_TASK, 1739 BTN_READY, 1741 BTN_ENQUEUE (depth=16), 2765 BTN_TX_START, 2799 BTN_TX_TC.

| Aşama | Süre (µs) |
|---|---:|
| t1−t0 | 24 |
| t2−t1 | 27 |
| t3−t2 | 156449 |
| t4−t3 | 5562 |
| Toplam | 162062 |

ButtonTask hızlı çalışmasına rağmen mesaj ortak FIFO'nun sonuna girer. 156,449 ms'lik t3−t2, kuyruk ve gönderim görevinin CPU bulma beklemesini kapsar. FIFO düzeninde BTN, önündeki TEL mesajlarını atlayamaz.

**Düşen örnek:** run=2, id=17. Sıra 843 BTN_ACCEPT, 858 BTN_TASK, 859 BTN_READY ve 861 BTN_DROP (reason=3, TX_DROP). Dump durumu `tx_drop`; t3/t4 yoktur. Bu mesajın yanıt süresi hesaplanmaz.

**Kuyruk neden boşalamıyor?** Sıra 2700'de TEL gönderimi 0,405109250 s'de başlar. TelemetryTask 2728'de tek parça CPU işine girer. UART TC 2734'te 0,410668363 s'de gelir ve UART görevi Ready olur (2736). Fakat yüksek öncelikli TelemetryTask sürer; UART ancak 2761'de 0,415085940 s'de çalışır. Ready→Run beklemesi yaklaşık 4,410 ms'dir. Sonraki BTN gönderimi 2765'te 0,415107881 s'de başlar. Bu örnekte iki gönderim başlangıcı yaklaşık 10 ms aralıklıdır; fiziksel hat aktarımı yalnız yaklaşık 5,56 ms sürmüştür.

Bu nedenle DMA'nın bitmesi otomatik olarak sonraki kuyruk elemanının DMA'ya verildiği anlamına gelmez. Düşük öncelikli UART görevinin yeniden CPU alması gerekir. 100 Hz TEL üretimi bu servis düzenini doldururken ek BTN girişleri FIFO birikimini artırır; kapasite tükenince hem BTN hem TEL kaybı görülür. Bu, izde desteklenen mekanizma açıklamasıdır; yalnız baud hesabından çıkarılmış bir kapasite iddiası değildir.

## Sınırlar ve kanıtlar

'''+limitations+'\n\n'+evidence([('V1','S0'),('V1','S5')])+'''
- [V1 build kimliği](../provenance/builds/v1/build.json), [izleme kaynak farkı](../provenance/v1-instrumentation.patch), [kaynak arşiv kimliği](../provenance/v1-source.json).
- [Tekrar üretilebilir hesaplamalar](../tools/final_reports.py), [tüm olayların dizini](experiment.csv), [hesap/kanıt manifesti](report-manifest.json).

V1 ve V2'nin karşılıklı senaryo değerlendirmesi [ana karşılaştırma raporundadır](V1_V2_Karsilastirma.md). Rapor hesapları ve entegrasyon Codex yardımıyla hazırlanmış; ölçümler gerçek karttan alınmıştır.
'''
main='''# V1–V2 genel karşılaştırma ve sonuç raporu

**Tarih:** 4 Ekim 2026. **Kapsam:** V1 S0 ↔ V2 S0 ve V1 S5 ↔ V2 S5. S0 ile S5 birbirinin yerine karşılaştırılmamıştır. V1 kayıtları 4 Ekim, V2 kayıtları 3 Ekim 2026'da aynı kartta alınmıştır.

## Sonuç

**S0'da farkın baskın nedeni UART hızıdır:** iki sürümde görev/mesaj hazırlama aşamaları benzerken, 64 bayt gönderimin ortalama süresi V1'de yaklaşık 5,556 ms, V2'de 1,394 ms'dir. Baud'un 115200'den 460800'e çıkması ile tutarlıdır.

**S5'te ana fark birikmenin giderilmesidir:** V1'in ortak FIFO'su dolmuş, 44/108 buton mesajı düşmüş ve tamamlanan mesajlarda TX öncesi bekleme baskın hale gelmiştir. V2'nin bu koşusunda buton kaybı yoktur ve ortalama TX öncesi bekleme 0,161 ms'dir. Daha hızlı UART, yüksek öncelikli CPU işinin dilimlenmesi ve BTN önce seçimi birlikte katkı sağlar. Tek bir değişikliğe bağımsız kazanç yüzdesi atanmamıştır.

## 1. Karşılaştırılan tasarımlar

| Özellik | V1 | V2-QWB | Sonuca etkisi |
|---|---|---|---|
| Kaynak commit | b74863a3a27ebeb14ca932737005b68d9eee1945 | 32f7e1dfeb69075d02084f08b4596d8febdccfb4 | Ayrı, sabit tasarımlar |
| UART baud | 115200 | 460800 | Aynı çerçevenin hat süresi kısalır |
| TX kuyruğu | TEL/BTN/kontrol ortak FIFO, 16 | BTN 8, TEL 16, kontrol 4 | TEL birikimi BTN kapasitesini doğrudan tüketmez |
| Mesaj seçimi | FIFO sırası | BTN önce | Kuyruktaki BTN, bekleyen TEL mesajlarını atlayabilir |
| S5 CPU işi | Tek parça yaklaşık 5 ms | Beş yaklaşık 1 ms dilim, aralarda vTaskDelay(1) | Düşük öncelikli görevler için çalışma fırsatları oluşur |
| TEL / BTN / UART öncelikleri | 3 / 2 / 1 | 3 / 2 / 1 | Kazanç öncelik yükseltmesinden gelmez |
| S0 / S5 yükü | 0 Hz / 100 Hz TEL | 0 Hz / 100 Hz TEL | Karşılıklı senaryo tanımları aynı |
| Protokol / kendi hedefi | PROTO2 / 20 ms | PROTO3 / 10 ms | Her iki eşik ayrıca hesaplanır |

Kart STM32F407VG, CPU 168 MHz, FreeRTOS 10.3.1, TIM5 1 MHz, toolchain ARM GCC 14.3.1, optimizasyon Release/-Os ve 64 bayt çerçeve iki sürümde aynıdır. İzleme kaynak ekleri özgün tasarımlardan ayrı manifest ve patch olarak saklanmıştır.

## 2. V1 S0 ↔ V2 S0

'''+table([('V1','S0'),('V2','S0')])+'\n\n'+stage_table('S0')+'''

İki sürümde de kabul edilen butonların tamamı gönderildi; kuyruk kaybı yok. S0'da telemetri olmadığı için ortak FIFO'nun telemetriyle dolma problemi tetiklenmez. İlk üç aşamanın ortalamaları birbirine yakındır; fark esas olarak t4−t3'tedir.

**Şu yüzden böyle oldu:** USART2 çerçevesi 64 bayt ve 8N1'dir; bayt başına 10 bit ile nominal süre 640/115200 ≈ 5,556 ms, 640/460800 ≈ 1,389 ms olur. Ölçülen süreler bu büyüklüklerle uyumludur. Callback/başlatma ve gerçek baud farkları nedeniyle birebir eşitlik beklenmez. V2 düşük yükte aynı mesajı yaklaşık dörtte bir hat süresinde taşır. Bu senaryo tek başına kuyruk politikasının veya iş dilimlemenin kazancını kanıtlamaz.

Örnek olaylar: V1 run=1/id=13 toplam 5,655 ms; V2 run=2/id=3 toplam 1,493 ms. Bunlar ayrı fiziksel basışlardır; tablo tek olay yerine tüm tamamlanmış olay dağılımlarını verir.

## 3. V1 S5 ↔ V2 S5

'''+table([('V1','S5'),('V2','S5')])+'''

| Kayıp / doluluk | V1 S5 | V2 S5 |
|---|---:|---:|
| BTN TX kaybı / kabul | 44 / 108 (%40,74) | 0 / 78 (%0) |
| TEL kaybı / üretilen | 49 / 4158 (%1,18) | 0 / 3986 (%0) |
| TEL tamamlanan | 4109 | 3986 |
| TX en yüksek doluluk | ortak FIFO 16/16 | BTN 1/8; TEL 1/16 |
| UART donanım hatası / timeout | 0 / 0 | 0 / 0 |

'''+stage_table('S5')+'''

V1'in tamamlanan olaylarında ortalama t3−t2 ≈ 138,935 ms; V2'de ≈ 0,161 ms. Bu aşama kuyruk, mevcut aktarım ve UART görevinin CPU alması için beklemeyi içerir. **Bu farkın tamamını sadece FIFO politikasına bağlamak doğru değildir:** baud ve CPU iş düzeni de değişmiştir.

### 3.1 Tek parça CPU işi UART servisinde boşluk oluşturuyor

V1 izinde UART TC geldikten sonra UartTxTask hazır olur, fakat TelemetryTask yaklaşık 5 ms'lik işini bitirene kadar çalışamaz. Sıra 2736→2761 Ready→Run aralığı yaklaşık 4,410 ms'dir. DMA aktarımı bitmiş olsa da sonraki çerçeve başlatılamaz. Böylece nominal hat kapasitesinin tamamı uygulama tarafından kullanılamaz. 115200 baud ve 64 baytta teorik yaklaşık 180 çerçeve/s hesabı, bu planlama beklemesini içermez; 100 Hz'in teorik sınırın altında olması kuyruk birikmeyeceğini garanti etmez.

V2 CPU işini yaklaşık 1 ms dilimlere ayırıp aralarda bir tick bloklanır. Bu aralar ButtonTask ve UartTxTask'ın CPU bulmasına imkân verir. Öncelik sırası değişmez; ButtonTask halen çalışan yüksek öncelikli dilimi kesemez. Beş dilimin toplam CPU işi yaklaşık 5 ms iken bloklama araları nedeniyle aktivasyon duvar süresi daha uzundur.

### 3.2 FIFO sırası buton mesajına uzun bekleme getiriyor

V1 S5 id=18: BTN_ENQUEUE sıra 1741'de ortak kuyruk doluluğu 16'dır. BTN_TX_START ancak 2765'te gelir; t3−t2 **156,449 ms**. Aynı pencerede id=17, TX kuyruğu dolu olduğu için BTN_DROP ile biter. V1'de buton için ayrılmış TX kapasitesi veya BTN önce seçimi yoktur.

V2 S5 izinde TEL_ENQUEUE 1961, BTN_ENQUEUE 1971 sırasındadır; buna rağmen UART 1976'da `btn_tx_q` kuyruğundan alır. Bu, BTN önce politikasının doğrudan kanıtıdır. Başlamış bir TEL aktarımı kesilmez; avantaj bir sonraki mesaj seçimindedir.

### 3.3 Daha hızlı hat, gönderim süresini ve kuyrukta kalışı azaltıyor

V1'de her çerçeve yaklaşık 5,56 ms, V2'de yaklaşık 1,39 ms hat süresi ister. V2 aynı veri yükünü daha kısa sürede taşır; kalan bir TEL aktarımının bitmesini bekleme süresi de kısalır. Bu değişiklik, CPU'ya daha sık erişim ve BTN önce seçimiyle birlikte birikmeyi azaltır. Yeni V2 koşusunda kuyruk doluluğu 1 seviyesinde kalmış ve kayıp görülmemiştir; bunun her yükte geçerli olduğu iddia edilmez.

### 3.4 Her tekil basış daha hızlı uyanmak zorunda değil

İncelenen V1 S5 id=18'in t1−t0'ı 24 µs, V2 S5 id=2'nin 708 µs'dir. V1 basışı uygun bir CPU fazına denk gelmiş; V2 basışı son telemetri dilimi içinde gelmiştir. Buna rağmen toplamlar V1'de 162,062 ms, V2'de 2,175 ms'dir: V1 örneğini baskılayan etken TX beklemesidir. Tek bir elverişli basıştan görev uyandırma üstünlüğü çıkarılamaz. Tablodaki aşama ortalamaları yalnız tamamlanan mesajları kapsar; V1'de düşen mesajlar nedeniyle ayrıca seçim etkisi vardır.

## 4. Nicel farkların doğru yorumu

'''
for sc in ['S0','S5']:
 a=D[('V1',sc)]['stats'];b=D[('V2',sc)]['stats'];main+=f'- **{sc}:** tamamlanan olayların ortalama yanıtı bu örneklemde %{100*(a["mean"]-b["mean"])/a["mean"]:.2f}, gözlenen maksimumu %{100*(a["max"]-b["max"])/a["max"]:.2f} daha düşük.\n'
main+='''
Bu yüzdeler ölçülen iki dağılımın betimsel farkıdır; eşlenmiş giriş deneyi veya değişiklik başına nedensel etki değildir. S5'te V1'in 44 düşen mesajı gecikme istatistiğinde yoktur; bu nedenle yüzdeyi kayıp oranından bağımsız başarı ölçütü olarak okumamak gerekir.

| Koşu | Aktif süre (s) | Kabul edilmiş giriş/s |
|---|---:|---:|
'''
for k in S:
 s=D[k]['stats'];main+=f'| {k[0]} {k[1]} | {s["duration"]:.3f} | {s["accepted"]/s["duration"]:.3f} |\n'
main+='''
Giriş/s, kabul edilmiş buton olaylarının ortalama hızıdır; önerilen basış temposu veya eşit aralıklı uyarım anlamına gelmez. Özellikle V1 S5 giriş hızı V2 S5'ten yüksektir; bu fark kuyruk yükünü artırabilir. İzdeki scheduler/FIFO mekanizması doğrudan görülür, fakat toplam kazancı sadece tasarıma ait kesin bir oran diye sunmak için eşlenmiş giriş deneyi gerekir.

## 5. Sonuçların neden–sonuç özeti

| Gözlenen durum | Kanıtlanan / desteklenen neden | V2'de sonuç |
|---|---|---|
| S0'da V1 yaklaşık 5,63 ms, V2 yaklaşık 1,48 ms | Aynı çerçeve, dört kat nominal baud; t4−t3 baskın fark | Gönderim duvar süresi kısaldı |
| V1 S5'te UART TC sonrası Ready beklemesi | Tek parça, daha yüksek öncelikli TEL işi UART görevini geciktiriyor | Dilimler arasındaki bloklamalar CPU fırsatı sağlıyor |
| V1 S5'te BTN önünde TEL birikimi | Ortak FIFO, doluluk 16; BTN bekleyen mesajları atlayamıyor | Ayrı BTN kuyruğu ve BTN önce seçimi |
| V1 S5'te 44 BTN ve 49 TEL kaybı | TX kuyruğuna sıfır beklemeli gönderim dolu kuyrukta başarısız | Ölçülen V2 koşusunda kayıp 0; kapasite/servis düzeni birlikte değişti |

V2'nin bu ölçümlerde sağladığı çözüm yalnız buton görevini hızlandırmak değildir. **Gönderim yolunun hem hat süresi hem CPU'ya erişimi hem de mesaj seçimi değiştirilmiştir.** S0, hat süresindeki farkı belirginleştirir; S5, bu değişikliklerin birlikte kuyruk birikmesi ve kayıp üzerindeki sonucunu gösterir. UART hata sayısının 0 olması V1'deki kaybın UART donanım arızası olarak yorumlanmaması gerektiğini destekler.

## 6. Sınırlar, yeniden üretim ve kaynaklar

'''+limitations+'''

Raporlar Markdown olarak kaydedildi. Yeniden hesaplama: Hafta 02 kökünde `projects/v2/interface/.venv/Scripts/python.exe tools/final_reports.py`. Bu betik tüm dört koşunun dump/trace bütünlüğünü doğrular, V1 ve ana raporu, birleşik olay dizinini ve hesap manifestini üretir. V2 raporunun özgün üreticisi `tools/report_v2.py` ayrıca mevcuttur.

'''+evidence(list(S))+'''
- [V1 ayrıntılı rapor](V1_S0_S5.md), [V2 ayrıntılı rapor](V2_S0_S5.md).
- [V1 kaynak arşivi kimliği](../provenance/v1-source.json), [V2 kaynak kimliği](../provenance/v2-source.json).
- [V1 uygulaması](../projects/v1/firmware/Homework_001/Src/app.c): ortak `tx_q`, tek parça `workload`, FIFO alımı.
- [V2 uygulaması](../projects/v2/firmware/Homework_001/Src/app.c): `btn_tx_q` önce seçimi ve dilimler arası `vTaskDelay(1)`.
- [V2 profil ayarları](../projects/v2/firmware/Homework_001/Inc/app_config.h): QWB, baud ve iş modu.
- [Hesap/kanıt manifesti](report-manifest.json), [birleşik olay dizini](experiment.csv).

Kod incelemesi, entegrasyon ve rapor hesaplamalarında Codex desteği kullanıldı. Sentetik olaylar veya eski Hafta 1 sonuçları bu tablolara eklenmedi.
'''
(R/'V1_S0_S5.md').write_text(v1,encoding='utf-8');(R/'V1_V2_Karsilastirma.md').write_text(main,encoding='utf-8')
(R/'report-manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
with (R/'experiment.csv').open('w',newline='',encoding='utf-8') as f:
 writer=csv.DictWriter(f,fieldnames=events[0]);writer.writeheader();writer.writerows(events)
print('Verified 4 sessions, 28 clean trace windows;',len(events),'accepted events. Reports generated.')
