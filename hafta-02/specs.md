# FreeRTOS Bootcamp — Hafta 2: V2 ve V1 SystemView incelemesi

**Durum:** v0.5 — S0/S5 kapsamı; V2 gözlemleri tamamlandı  
**Tarih:** 3 Ekim 2026  
**Kart:** Aynı STM32F407G-DISC1 / STM32F407VGT6  
**Sıra:** Yerel V2 kopyası → SystemView → birlikte gözlem → V2 raporu → GitHub V1 → SystemView → birlikte gözlem → V1 raporu → karşılaştırma raporu.

## 1. Amaç ve kesinleşen kapsam

Kullanıcı, Hafta 1'de V1 sorunlarını çözmek için V2'yi zaten geliştirdi. Bu çalışmanın amacı mevcut iki tasarımı SystemView ile gözlemek, ayrı ayrı raporlamak ve V1'den V2'ye yapılan değişikliklerin sonuçlarını karşılaştırmaktır.

Yeni A/B/C tasarımları, S6 senaryosu veya ek tek değişkenli iyileştirme profili oluşturulmayacak. Önceki taslaktaki beş koşulluk A/B/C matrisi ve baud 230400 deneyi, kullanıcının son kapsam açıklamasıyla kaldırılmıştır. V2 içindeki Q/QW/QB ara profillerini ayrıca ölçmek de mevcut kapsamın parçası değildir; karşılaştırma V1 ile nihai V2-QWB arasında yapılacaktır. Trexcope şimdilik kapsam dışıdır.

Hafta 1'deki çalışan proje korunacak. Önce yerel V2 kaynakları ayrı Hafta 2 çalışma alanına kopyalanacak; SystemView için gereken değişiklikler bu kopyaya uygulanacak. V2 gözlemi ve raporu sonrasında GitHub'daki sabit V1 commit'i ayrı dizine indirilecek ve aynı izleme yaklaşımı ona eklenecek.

**Uygulama durumu (4 Ekim 2026):** Yalnız S0/S5 kapsamındaki V2 ve V1 kayıtları alındı. V2, V1 ve karşılıklı senaryo karşılaştırma raporları `reports/V2_S0_S5.md`, `reports/V1_S0_S5.md`, `reports/V1_V2_Karsilastirma.md` içinde tamamlandı. Ana rapor V1 S0 ile V2 S0 ve V1 S5 ile V2 S5 karşılaştırır; kod/iz kanıtıyla nedenleri açıklar. Manuel giriş farkı ve ölçülmemiş trace ek yükü açıkça belirtilmiştir. Kartta izlemeli V1 yüklüdür.

## 2. Kaynaklar ve sürüm kimliği

| Sürüm | Kaynak | Sabit kimlik |
|---|---|---|
| V2 | `D:/freertos-bootcamp/hafta-01` yerel proje | `32f7e1dfeb69075d02084f08b4596d8febdccfb4` — HomeworkV2 |
| V1 | GitHub `furkankara32/hafta-01` geçmişi | `b74863a3a27ebeb14ca932737005b68d9eee1945` — 24/09/2026 Version 1 Completed |

[V1 commit'i GitHub üzerinde doğrulandı](https://github.com/furkankara32/hafta-01/commit/b74863a3a27ebeb14ca932737005b68d9eee1945). V1 indirilirken güncel main kullanılmayacak; bu commit sabitlenecek. V1 geçmişi yerelde de bulunuyor, fakat V1 çalışma kopyası kullanıcının istediği gibi GitHub kaynağından alınacak.

V2 kopyalanmadan önce çalışma ağacı yeniden kontrol edilecek. Commit edilmemiş kaynak değişiklikleri varsa yerel V2'nin parçası olarak korunup dosya hash manifestine yazılacak; yalnız HEAD arşivlenerek kaybedilmeyecek. Şu an şartname dışındaki çalışma ağacı temizdir. Eski notlardaki “V2 commit edilmedi” ifadesi tarihsel kalmıştır. Eski V2 doğrulama notları fiziksel kabul ölçümü bulunmadığını söylüyor; kartta yüklü binary ayrıca doğrulanacak.

Ödev kaynak paketi `C:/Users/furkan/Downloads/Hafta_2.zip`; yalnız `odev-systemview.html`, `odev-02.html`, `ders-02.html`, `FreeRTOS_Architecture.html` içeriyor. Hazır referans firmware veya SystemView kaydı yok. Bu belgeler izleme yöntemi, ölçüm disiplini ve rapor kanıtları için kaynak olarak kullanılacak. İçlerindeki A/B/C ve tek değişken beklentilerinden farklı olarak bu çalışma kullanıcının belirlediği V1/V2 kapsamını uygular; raporda kapsam farkı açıkça belirtilir. Tam ödev rubriğinin tüm maddelerinin karşılandığı iddia edilmez.

## 3. Çalışma alanı ve kopyalama

Uygulama hedefi mevcut projenin kardeş dizini olan `D:/freertos-bootcamp/hafta-02`:

```text
hafta-02/
  specs.md
  README.md
  provenance/
    v2-source.json
    v1-source.json
    v1-to-v2.diff
  projects/
    v2/                     # önce yerel V2 kaynak kopyası
      firmware/
      interface/
      tests/
      ...
    v1/                     # V2 raporundan sonra GitHub V1 kaynakları
      firmware/
      interface/
      tests/
      ...
  traces/v2/<scenario>/<run>/
  traces/v1/<scenario>/<run>/
  measurements/v2/<scenario>/<run>/
  measurements/v1/<scenario>/<run>/
  reports/
    01-v2-systemview.md
    02-v1-systemview.md
    03-v1-v2-comparison.md
    figures/
  docs/
    setup-systemview.md
    observation-v2.md
    observation-v1.md
    instrumentation-changes.md
  experiment.csv
  ai-usage.md
```

Hafta 1 kaynaklarında izleme değişikliği yapılmayacak. Hafta 2 hedefi zaten varsa içeriği incelenmeden üzerine yazılmayacak. Bu düzen bir proje kopyasıdır; Hafta 1 checkout'unu eski commit'e döndürmez.

Kopya; firmware, CubeIDE proje dosyaları, build script'leri, arayüz, testler ve ilgili dokümantasyonu içerecek. `.git`, taşınamaz Python sanal ortamı, IDE cache'leri ve eski build/dist çıktıları yeni build gibi kullanılmayacak. Gerekli ortam yeniden kurulacak. Eski ölçüm/raporlar tarihsel kaynak olarak ayrı işaretlenecek; yeni Hafta 2 ölçümlerine karıştırılmayacak. Derleme script'lerinin Git kimliği varsayımları yeni düzene uyarlanacak: özgün kaynak commit'i, izleme değişiklikleri, dosya manifesti ve yeni ELF hash'i ayrı saklanacak.

Bu şartname Hafta 2 kökünde kaydedildi; güncel çalışma belgesi `D:/freertos-bootcamp/hafta-02/specs.md` dosyasıdır. Commit/push veya GitHub'a teslim bu hazırlık adımının otomatik parçası değildir.

## 4. Karşılaştırılacak mevcut tasarımlar

Yerel commit farkı ve kaynak kod üzerinden doğrulanan başlangıç:

| Özellik | V1 | V2-QWB |
|---|---|---|
| Task öncelikleri TEL / BTN / UART | 3 / 2 / 1 | 3 / 2 / 1 — korunmuş |
| Veri mesajı seçimi | Ortak FIFO | Ayrı kuyruklardan BTN önce |
| TX kapasitesi | Ortak TX kuyruğu 16 | BTN 8, TEL 16; ayrıca kontrol/barrier 4 |
| S4/S5 CPU işi | Tek parça | Hedef 1 ms dilimler; aralarda bir tick bloklama |
| UART | 115200, 8N1, 64 bayt | 460800, 8N1, 64 bayt |
| TX sürücüsü | DMA / UART TC callback | DMA / UART TC callback |
| Ölçüm saati | TIM5, 1 MHz | TIM5, 1 MHz |
| Protokol | PROTO2 | PROTO3 ve ek metadata/sayaçlar |
| Tasarım hedefi | 20 ms | 10 ms |
| Senaryolar | S0–S5 | S0–S5 |

Her ikisi de aynı kart, 168 MHz sistem saati, FreeRTOS 10.3.1 ve 1 kHz tick üzerinden incelenecek. V2'nin kuyruk kapasitesi, baud'u veya iş dilimleri V1'e eşitlenmeyecek; bunlar ölçmek istediğimiz tasarım değişiklikleridir. Önceliklerin yükseltilmesi V1→V2 değişikliği gibi anlatılmayacak.

V2'de bildirimle UART görevini uyandırma, drain/barrier akışı, yeni sayaçlar, build kimliği ve analiz altyapısı da değişmiştir. Üçüncü rapor yalnız üç ana optimizasyonu değil, davranışı etkileyen diğer ilgili farkları ve bellek maliyetlerini de kod farkıyla inceleyecek.

Tarihsel V1 raporu S5'te kuyruk doluluğu, düşen mesajlar ve uzun TX beklemesi bildiriyor. Bu, yeni izlerde araştırılacak başlangıç bulgusudur; yeni SystemView ölçümü yerine kullanılmayacak. V2'nin bu sorunları ne ölçüde çözdüğü ölçümden önce sonuç kabul edilmeyecek.

## 5. Donanım ve kayıt yolu

Kullanıcıda harici J-Link yok; normal kod yükleme USB kablosu ve USB–TTL adaptörü var. Kartın yerleşik programlayıcısı ST-LINK'tir. USB kablosu bu programlayıcıya erişir; USB–TTL ise mevcut USART2 ölçüm iletişimini taşır.

**Seçilen ve pilotla doğrulanan yol:** Yerleşik ST-LINK V2J48M35 ile işlemci çalışırken donmuş RAM trace tamponunu OpenOCD üzerinden okuma ve SystemView 4.10a'da `.SVDat` açma. J-Link OB dönüşümü yapılmadı. Varsayılan pencere 500 ms, tampon 65536 bayt; kayıt otomatik durur. Kayıt sırasında hedef halt/reset edilmez. Bu çevrimdışı gözlemdir; canlı J-Link bağlantısı değildir.

USB–TTL COM5 mevcut USART2 uygulama protokolünü V2’de 460800, V1’de 115200 baud ile taşır; trace için paylaşılmaz. SystemView taşınabilir uygulaması `tools/SystemView-4.10a` altında hazırdır. Kaynak sürümleri ve araç/build bilgileri `provenance`, `build.json` ve hazırlık loglarında saklanır. FreeRTOS 10.3.1 yükseltilmeden uygun trace adaptörü ve çekirdek hook'ları eklendi.

## 6. SystemView için izin verilen kaynak değişiklikleri

İki sürüme de yalnız izlenebilirlik, kayıt kimliği ve bunun için gerekli build/araç uyarlamaları eklenecek. Mevcut tasarımı iyileştirmek için görev sırası, kuyruk politikası, baud, iş yükü veya sürücü değiştirilmeyecek. Zorunlu işlevsel bir düzeltme ortaya çıkarsa özgün sürümden farkı ayrıca belirtilecek; sessizce kaynak sürüme mal edilmeyecek.

Entegrasyon işleri:

- Sürümü sabitlenmiş SystemView, RTT ve FreeRTOS adaptörü kaynaklarını eklemek.
- FreeRTOS 10.3.1'e uygun kernel hook uyarlamalarını inceleyip belgelemek. 11.x entegrasyonu veya 10.4.3 yaması doğrudan uygulanmayacak.
- CubeIDE ve bağımsız build script'lerine aynı kaynak/include seçeneklerini eklemek.
- İzleme açık ve kapalı derlemeleri desteklemek; SystemView yapılandırmasını doğru başlangıç noktasında çağırmak.
- Timestamp kaynağı/frekansını doğrulamak; mevcut TIM5 t0–t4 ölçümlerini korumak. DWT seçilirse SystemCoreClock ile yapılandırıp ortak uygulama işaretleriyle zaman alanlarını eşlemek.
- Task isimleri, Idle ve timer service task'ını görünür kılmak; kuyrukları adlandırmak.
- EXTI0, USART2 ve ilgili DMA ISR giriş/çıkışlarını doğru eşlemek; yield makroları nedeniyle çift ISR çıkış kaydı oluşturmamak.
- Trace buffer'ını linker map, heap ve stack marjlarıyla boyutlandırmak; dolulukta uygulamayı bekleten aktarım kullanmamak; overflow'u görünür kılmak.
- İki sürümde eşdeğer olay noktaları kullanmak; entegrasyon farklarını `instrumentation-changes.md` içine kaydetmek.

Yerel V2'de `configUSE_TRACE_FACILITY=1` olması tek başına SystemView entegrasyonu değildir. SEGGER rehberi V10 ve öncesi için kernel uyarlaması gerektirdiğini belirtir; sürüm ayrıntıları resmî rehberle doğrulanacaktır.

### Olay işaretleri ve kimlik

| İşaret | Anlam |
|---|---|
| RUN_CONFIG / START / STOP | Kaynak sürüm, profil, senaryo, koşu kimliği |
| BTN_ACCEPT | Kabul edilen EXTI, event_id, mevcut t0 |
| BTN_TASK | Kuyruktan alım ve t1 |
| BTN_READY | Enqueue öncesi t2 |
| BTN_ENQUEUE / DROP | Kuyruk sonucu, derinlik, kayıp nedeni |
| BTN_TX_START | DMA çağrısı öncesi t3; çağrı başarısızlığı ayrıca ayırt edilir |
| BTN_TX_TC | UART TC callback'inde t4 |
| TEL_ENQUEUE / TX_START / TX_TC | Telemetri sırası, bekleme ve tamamlanma |
| WORK_SLICE_BEGIN / END | V2 dilimleri; V1'de eşdeğer tek iş bloğu |

Bunlar uygulama etiketleridir, hazır SEGGER API isimleri değildir. Sabitlenmiş sürümün uygun olay API'sine eşlenecek. Kimlik `(source_version, build_id, run_id, event_id)` ile tutulacak. Timestamp önce alınacak; trace çağrısı mevcut zaman sınırını başka yere taşımayacak. Telemetri ölçümleri mümkün olduğunca trace üzerinden çıkarılacak; kuyruk elemanına alan eklemek gerekirse RAM ve ek yük farkı yazılacak.

## 7. Aşamalar ve duraklar

| Sıra | İş | Tamamlanma ölçütü |
|---|---|---|
| 1 | Yerel V2'yi Hafta 2'ye kopyala, kaynak manifestini oluştur | Hafta 1 korunmuş; V2 kopyası kaynakla eşleşiyor |
| 2 | İzleme öncesi build ve kayıt yolunu doğrula | Araç/probe/firmware kimlikleri belli |
| 3 | V2'ye SystemView ekle, derle ve karta yükleyip doğrula | V2-QWB davranışı ve 460800 iletişimi çalışıyor |
| 4 | V2/S0 kısa pilot; SystemView arayüzünü gerçek kayıtla aç | Görevler ve bir BTN zinciri görünür; birlikte gözlem için dur |
| 5 | Kullanıcıyla V2 gözlemleri ve ölçümleri | Olay kimlikli notlar ve geçerli kayıt seti |
| 6 | Birinci raporu yaz | `01-v2-systemview.md` |
| 7 | GitHub'dan sabit V1'i ayrı dizine indir; eşdeğer izleme ekle | V1 davranışı, 115200 iletişimi ve build doğrulanmış |
| 8 | V1 pilotu, kullanıcıyla gözlem ve ölçüm | Aynı yöntemle geçerli V1 kayıtları |
| 9 | İkinci raporu yaz | `02-v1-systemview.md` |
| 10 | Kaynak farklarını ve iki raporu karşılaştır | `03-v1-v2-comparison.md` |

İlk kullanıcı rehberi; programı açma, recorder/target seçimi, kayıt başlatma-durdurma, kaydetme-açma, görev filtreleme, yakınlaştırma ve olay aramayı içerir. Menü adları kurulan sürümde doğrulanır.

Hazır ekran kabulü: SystemView penceresi açık, gerçek kayıt yüklenmiş, üç uygulama görevi isimleriyle görünür, zaman ölçeği TIM5 ile tutarlı, en az bir gerçek BTN olayının tam t0→t4 zinciri eşlenmiş olmalı. Pilot penceresi overflow içermemeli; kayıt kaydedilip yeniden açılabilmeli. Bu teknik kontrol asistan tarafından hazırlanır; ayrıntılı yorum kullanıcıyla yapılır.

## 8. V1/V2 ölçüm planı

Her sürümde yalnız S0 ve S5 ölçülecek. S0 düşük yük referansı; S5 yoğun yükte ana sorun/iyileşme incelemesidir. V2 raporu ardından V1 gözlemi/raporu, en son sürümler arası karşılaştırma yapılır.

| Koşul | Her sürüm için hedef | Amaç |
|---|---:|---|
| S0 kısa pilot | 5 kabul edilmiş fiziksel olay | Bağlantı ve olay zinciri |
| S0 gözlem koşusu | En az 30 kabul edilmiş olay | Düşük yük referansı |
| S5 gözlem koşusu | En az 30 kabul edilmiş olay | Yoğun CPU yükü, kuyruk, kayıp ve yanıt |

5 saniye ısınma, en az 0,5 saniye aralıklı gerçek buton basışları ve çeşitli basış fazları kullanılacak. Her resmi senaryodan en az üç tamamlanmış olayın tam zincirini kapsayan temiz iz pencereleri hedeflenecek. Düşen olaylar ayrıca izlenecek; tamamlanmamış zincir başarısızlık nedeniyle atılmayacak. Kabul/tamamlanma/drop sayıları ayrı raporlanacak.

İki sürümde aynı kart, güç/bağlantı düzeni, toolchain, optimizasyon, senaryo yük tanımı ve ölçüm prosedürü kullanılacak. **Başlangıç tercihi her ikisinde Release / -Os**: önceki V1 fiziksel ölçümleri ve V2 ana build akışıyla uyumludur. Debug gerekirse sorun çözmek için ayrı çalıştırılır; Release sonucu ile aynı karşılaştırma setine karıştırılmaz. Bu tercih HTML'deki Debug sabitinden farklıdır ve raporda belirtilir.

Baud, kuyruk düzeni, CPU işinin parçalanması ve sürüme özgü hedefler tasarım farkı olarak korunur. Kalibrasyonun gerçek hesaplama süreleri ve V2'nin bloklamalar dahil aktivasyon süresi de kaydedilir; aynı hedef iş yükünün iki sürümde aynı duvar süresi tuttuğu varsayılmaz.

V2'nin önceki şartnamesindeki tam 10 ms kabulünü ayrıca iddia etmek gerekirse S5'te en az 100 olay/faz kapsamı gibi oradaki ek koşullar da gerekir. Bu çalışmadaki 30 olaylık karşılaştırma tek başına o kabulü veya worst-case garantisini sağlamaz.

### İzlemenin etkisi

Mevcut S0/S5 koşuları aralıklı trace pencereleri içerir. Ayrı eşlenmiş izleme açık/kapalı koşu yapılmadığı için trace ek yükü nicel ayrıştırılamaz. Bu sınırlama tüm raporlarda belirtilir; gözlem sonuçları biçimsel deadline kabulü veya izleme etkisinden arındırılmış performans iddiasına dönüştürülmez. Ek yükün ayrıca ölçülmesi gerektiğinde aynı S5 üzerinde ayrı kontrol koşusu planlanabilir.

İzler kısa pencereler halinde tutulabilir; her dosya koşu ve olay kimlikleriyle eşlenir. Debugger ölçüm sırasında hedefi durdurmayacak; RAM aktarımı gerekiyorsa kayıt penceresi tamamlandıktan sonra yapılacak. Reset sonrası run_id tekrarları build/oturum kimliğiyle ayrılacak.

## 9. Üç raporun içeriği

### Rapor 1 — V2 SystemView incelemesi

V2 kaynağı ve QWB ayarları; izleme entegrasyonu; kayıt yolu; S0 ve S5 sonuçları; görevlerin Running/Ready/Blocked aralıkları; BTN önce seçimi; iş dilimleri; DMA/TC akışı; kuyruk ve kayıp sayaçları; telemetri bekleme/üretim düzeni; heap/stack ve trace ek yükü. Gerçek iz ekranlarında olay kimlikleri işaretlenir. V2'nin 10 ms hedefi karşısındaki gözlem, kanıt kapsamıyla birlikte yazılır.

### Rapor 2 — V1 SystemView incelemesi

Sabit GitHub commit'i ve orijinal ayarlar; aynı izleme yöntemi; S0 ve S5 sonuçları; tek parça CPU işi; ortak FIFO ve UART görevinin çalışabilmesi; kuyruk doluluğu ve drop'lar; telemetri etkisi; 20 ms hedefi ve trace ek yükü. Tarihsel Hafta 1 bulguları ile yeni kayıtların farkları açıklanır; eski sonuçlar yeni ölçüm gibi sunulmaz.

### Rapor 3 — V1'den V2'ye değişiklikler ve sonuçları

Kaynak diff'i üzerinden değişiklik envanteri çıkarılır. Her madde şu sırayla anlatılır: V1'de gözlenen sorun → V2'deki kod/tasarım değişikliği → iki rapordaki ilgili iz ve ölçüm → elde edilen çözüm ve kalan bedel/sınır.

| Değişiklik | İncelenecek kanıt |
|---|---|
| Ortak FIFO → BTN önce / ayrı kuyruklar | t3−t2, mesaj seçimi, BTN/TEL beklemesi ve drop |
| Tek parça iş → dilimler ve bloklama | Button/UART'ın CPU bulduğu aralıklar, t1−t0, aktivasyon duvar süresi |
| 115200 → 460800 | t4−t3, hat doluluğu, gerçek baud, UART hataları |
| Kuyruk kapasitesi ve kontrol akışı | Doluluk, RAM, drain/barrier, kayıp ve timeout |
| Protokol/analiz iyileştirmeleri | Ek sayaçların açıklayıcılığı ve koşu/build eşleşmesi |

Aynı senaryo için toplam R, dört aşama, kabul/tamamlanma, kayıp, deadline aşımı ve telemetri ölçümleri yan yana verilir. R ortalama, medyan, p95 ve gözlenen maksimum gösterilir. Her iki veri setinde hem 10 ms hem 20 ms ihlalleri hesaplanır; sürümlerin kendi hedefleri ayrıca belirtilir.

Bu, iki mevcut tasarımın toplam etkisinin karşılaştırmasıdır. Birden fazla değişiklik birlikte yapıldığı için toplam kazancın kesin yüzde kaçının her bir değişiklikten geldiği iddia edilmez. İzlerde mekanizma açıklanabilir; bağımsız katkı yüzdesi için ek ara tasarımlar gerekir ve bunlar mevcut kapsamda değildir. Fayda görülmeyen veya kötüleşen koşullar da raporda yer alır.

## 10. Ölçüm sınırları ve kanıt bütünlüğü

R=t4−t0; aşamalar t1−t0, t2−t1, t3−t2, t4−t3. TIM5 unsigned farkları tek taşma turundan kısa aralıklar için kullanılır. Eksik zamanlar sıfırla tamamlanmaz. Düşen olaylara sıfır yanıt süresi atanmaz; istatistiklerin hangi tamamlanmış olayları kapsadığı ve kayıp oranı birlikte yazılır.

- t0 fiziksel parmak hareketi değil kabul edilen EXTI zamanıdır.
- t1 task switch-in değil, kuyruktan alım sınırıdır.
- t3 DMA başlatma çağrısı öncesi, t4 UART TC callback'idir; DMA complete son UART bitinin çıkmasıyla aynı sayılmaz.
- Boş task çizgisi tek başına Ready kanıtı değildir; block/wakeup/scheduler olayları birlikte okunur.
- UART hat doluluğu CPU kullanımından ayrıdır; duvar süreleri ISR/preemption içerebilir.
- Manuel basışlar iki sürümde birebir aynı fiziksel olay değildir; aynı yükteki koşular karşılaştırılır, benzer örnek olaylar ayrıca işaretlenir.
- Gözlenen maksimum kanıtlanmış WCRT değildir. Trace overflow içeren pencere temiz nedensel iz sayılmaz; ham veri ve hata bilgisi saklanır.

Her koşu için ham UART, CSV, metadata, özgün SystemView kaydı, ELF hash'i, kaynak kimliği ve izleme yaması eşlenir. `experiment.csv`: sürüm, profil, senaryo, trace durumu, build/oturum/run/event kimliği, dosya yolları ve geçerlilik notu içerir. Sentetik veriler gerçek rapora girmez. Başarısız koşular sonuç seçimiyle gizlenmez.

## 11. Doğrulama ve tamamlanma

Kaynak kopyasının manifesti doğrulanacak; izleme açık/kapalı ARM build'leri ve mevcut işlevsel/protokol testleri çalıştırılacak. Test uyarlamaları izleme hook'ları ve kayıt bütünlüğü için gerektiği ölçüde yapılacak. Sürümlerin özgün görev/baud/kuyruk/iş profilleri değişmediği diff ile kontrol edilecek.

Donanımda doğru build yüklemesi, UART haberleşmesi, görev isimleri, zaman ölçeği, kayıp/overflow ve heap/stack marjları doğrulanacak. Yazılım testleri fiziksel zamanlama kanıtı sayılmayacak. Sonuçlar ancak gerçek kayıtlar ve birlikte gözlem sonrasında yazılacak.

Çalışma; üç ayrı rapor, kaynak/build/iz eşlemesi, işaretli görseller ve tekrar uygulanabilir SystemView kurulum rehberi tamamlandığında bitmiş sayılır. Anlatım videosu için 3–5 dakikalık taslak hazırlanabilir; video kaydı kullanıcıyla yürütülür. Kesin teslim tarihi eğitmen duyurusuna bağlıdır.

## 12. Teknik başvuru kaynakları

- [SEGGER FreeRTOS entegrasyonu](https://kb.segger.com/FreeRTOS_with_SystemView)
- [J-Link OB uyumluluğu ve ST-LINK'e geri dönüş](https://www.segger.com/products/debug-probes/j-link/models/other-j-links/st-link-on-board/)
- [SystemView kullanıcı kılavuzu](https://doc.segger.com/UM08027_SystemView.html)
- [SystemView UART Recorder](https://kb.segger.com/Use_SystemView_UART_Recorder)
- [SystemView indirme](https://www.segger.com/downloads/systemview)
- [Kartın ST ürün sayfası](https://www.st.com/en/evaluation-tools/stm32f4discovery.html)

Bu kaynaklar araç entegrasyonuna yardımcıdır. Çalışma kapsamını kullanıcının V2 → V1 → karşılaştırma talebi belirler.
