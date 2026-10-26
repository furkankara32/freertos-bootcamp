# Hafta 05 — UART, StreamBuffer, Event Group ve zamanlama deneyleri

Sürüm: 0.3 | Tarih: 25 Ekim 2026 | Durum: Uygulama başladı; çalışan pilot mevcut, tam kabul serisi bekliyor

Kullanıcı uygulama başlangıcını onayladı. Firmware, EXE arayüzü ve ST-LINK RAM kayıt yolu geliştiriliyor. Güncel uygulama/ölçüm durumu README.md ve docs/VALIDATION.md içindedir; SPEC hedefleri ile pilot sonucu aynı şey değildir. USART-A RX = USART3 PB11; USART-B TX = USART2 PA2 olarak doğrulandı.

## 1. Amaç

STM32F407G-DISC1 üzerinde doğru çalışan bir veri yolu kurmak; ardından kontrollü hatalar oluşturarak task zamanlamasını, LED geçişlerini, veri kaybını ve gecikmeyi SEGGER SystemView ile açıklamak.

Başarı yalnız çalışan uygulama değildir. Öğrenci tahmin yapmalı, senaryoyu kaydetmeli, darboğazı trace üzerinden göstermeli, tek değişiklik yapmalı ve önce/sonra sonuçlarını karşılaştırmalıdır.

Toplam **dört senaryo** vardır. Doğru çalışan referans sistem S1'dir. S2–S4 içindeki hata/düzeltme koşuları ayrı senaryo sayılmaz. Baud karşılaştırması ve aynı UART hattında büyük/küçük gönderim rekabeti kapsam dışıdır.

ZIP'teki L476RG, 230400 baud, STOP/SETPOINT ve T1–T8 ödevi bu çalışmanın bağlayıcı tanımı değildir. Bu SPEC, konuşmada kararlaştırılan F4, PC kaynaklı USART-A RX girişi, USART-B TX log çıkışı, LED, dört senaryo, Windows EXE ve SystemView gereksinimlerini esas alır.

## 2. Donanım ve bağlantı

- Kart: STM32F4 Discovery **STM32F407G-DISC1**, STM32F407VG.
- Bir adet **3,3 V lojik seviyeli USB–TTL** adaptörü; ortak GND.
- Kart programlama/debug bağlantısı: yerleşik ST-LINK/SWD. **Kullanıcıda J-Link yoktur.** SystemView için ST-LINK üzerinden RAM kayıt çıkarımı kullanılacak; J-Link veya ek debug donanımı gerekmeyecek.
- İki bağımsız USART, ikisi de **115200 baud, 8N1**, akış kontrolü kapalı.
- USART-A RX: arayüzden gelen bulk veri, LED komutları ve deney kontrolü; TTL TX → USART-A RX.
- USART-B TX: arayüze log, ACK ve durum çıktısı; USART-B TX → TTL RX.
- Aynı TTL adaptörünün TX ve RX yönleri farklı MCU USART birimlerine bağlıdır. PC tek COM portunu çift yönlü kullanır; iki ayrı COM portu gerekmez.
- USART-A TX ve USART-B RX bu uygulamada kullanılmaz. TX–RX loopback jumper bağlantısı yoktur. GND → GND bağlanır.
- TTL VCC hattıyla ek besleme yapılmaz; iki TX çıkışı birbirine bağlanmaz.
- Doğrulanmış bağlantı: USART-A RX = USART3 PB11; USART-B TX = USART2 PA2. Tek TTL adaptörünün TX çıkışı PB11'e, RX girişi PA2'ye bağlanır.

| Kullanıcı LED'i | Renk | GPIO |
|---|---|---|
| LD4 | Yeşil | PD12 |
| LD3 | Turuncu | PD13 |
| LD5 | Kırmızı | PD14 |
| LD6 | Mavi | PD15 |

Önerilen sıra: yeşil → turuncu → kırmızı → mavi. Her LED'in nominal açık kalma süresi 1000 ms. Geçişlerde önceki LED söndürülür, sonraki LED yakılır; normal dizide aynı anda yalnız bir LED açık tutulur.

## 3. Sistem mimarisi

```text
Windows EXE: bulk üretici + LED/deney komutları
                         │ Tek COM portunun TX yönü
                         ▼
                      TTL TX
                         │
                  USART-A RX ISR
                         │ A_RX_Stream
                         ▼
                     ParserTask
                         │ CommandQueue + Event Group
                         ▼
                     ExecuteTask → LED GPIO'ları
                         │ ResultQueue + Notification
                         ▼
                      ReportTask
                         │ B_TX_Stream
                         ▼
                    USART-B TX
                         │
                      TTL RX
                         │ Aynı COM portunun RX yönü
                         ▼
               Windows EXE: log, grafik, kayıt
```

Bulk verinin üreticisi PC arayüzüdür; kart üzerinde BulkTxTask yoktur. Bir test patlamasının toplam boyutu başlıklar dahil **10.000 bayt** olacak. Dolgu/yük çerçeveleri ile LED ve deney kontrol komutları aynı A RX hattında tür alanıyla ayrılacak. Parser tüm patlamayı beklemeden tamamlanmış komutu işlemeye iletecek.

10.000 baytın ideal 115200/8N1 hat süresi yaklaşık 0,868 saniyedir. LED geçişlerini yük altında görmek için arayüz yük patlamalarını geçişleri kapsayacak şekilde tekrarlar. PC yazma zamanları ile kartın gerçek alım zamanları ayrı kaydedilir; seri write başarısı fiziksel teslim kanıtı değildir.

UI'deki tek seri gönderim yöneticisi bulk ve kontrol çerçevelerini sıralar; farklı host thread'leri aynı portta çerçevelerin baytlarını karıştırmaz. Başlat/durdur/yapılandır komutları da A RX ve ParserTask yolundan geçer. LED ve deney durumunun sahibi ExecuteTask'tır. Kontrol komutları çerçeve sınırlarında gönderilebilir; işletim sistemi/USB tamponuna önceden yazılmış bulk verisini geçemez. Bu nedenle yoğun giriş altında STOP'a bağımsız, anlık erişim garantisi verilmez. ACK ve hatalar B TX üzerinden döner; LED komutları parser'ı atlayamaz.


StreamBuffer bayt taşır; peripheral'ı kendisi sürmez. TX tarafında kesme tabanlı sürücü, başlangıç/yeniden başlatma mekanizması ve gerçek aktarım sonu bildirimi gerekir. DMA zorunlu değildir.

## 4. Task'lar ve sahiplik

Referans öncelikleri öneridir; manifestte gerçek değerler tutulur. Native FreeRTOS'ta büyük sayı daha yüksek önceliktir.

| Task | Önerilen öncelik | Sorumluluk / bekleme |
|---|---:|---|
| ParserTask | 4 | A_RX_Stream okur, parçalı parser çalıştırır, doğrulanmış komutu kuyruğa koyar; veri yokken bloklanır |
| ExecuteTask | 3 | Komutları ve LED zamanlamasını yönetir; event veya sonraki LED deadline'ına kadar bloklanır |
| ReportTask | 2 | Sonuçları biçimlendirir, B_TX_Stream'e aktarır; iş yokken notification bekler |
Bulk üretimi ve seri gönderim planlaması Windows EXE içinde yapılır. Kart üzerinde ayrı BulkTxTask veya B RX ControlTask bulunmaz.

S2'de ReportTask için örneğin 5 kullanılır; configMAX_PRIORITIES bu değeri desteklemelidir. Task öncelikleri ile NVIC öncelikleri aynı sayı sistemi değildir. RTOS çağıran ISR'ların syscall sınırına uygunluğu ayrıca doğrulanacak.

- A_RX_Stream: tek yazıcı A RX ISR, tek okuyucu ParserTask.
- B_TX_Stream: tek yazıcı ReportTask, tek okuyucu B TX sürücüsü/ISR.
- TX başlatma sırasında ISR ile task arasında ikinci okuyucu yarışı oluşturulmaz.
- LED GPIO'larının tek sahibi ExecuteTask'tır.
- USART-B uygulama çıktısının tek sahibi ReportTask'tır. Deney kontrol yanıtları da ResultQueue ve notification üzerinden raporlama yoluna girer.
- Queue elemanları başlangıçta değer kopyasıdır. Pointer kullanılacaksa ömür, sahiplik ve iade koşulları ayrıca belgelenir.
- Task'lar iş yokken polling döngüsünde çalışmaz. Başlangıç sonrası uygulama kaynaklı dinamik ayırma yapılmaması hedeflenir.

## 5. Parser, Queue, Event Group ve Notify sözleşmeleri

### 5.1 Parser ve protokol

- A hattı tür, uzunluk, komut/çerçeve kimliği ve bütünlük kontrolü taşıyan sınırlı boyutlu çerçeveler kullanacak; kesin byte formatı uygulama başlangıcında dokümante edilecek.
- LED_SEQUENCE komutu sıra, led_duration_ms ve tur sayısı taşır. İlk referans: 1000 ms ve 3 tur.
- LOAD/PADDING türü veri yükü üretir, LED işi oluşturmaz. Her bayt veya her dolgu çerçevesi için log üretilmez.
- Parser durumu Receive çağrıları arasında korunur. Tek Receive tek çerçeve kabul edilmez.
- Geçersiz uzunluk, yarım çerçeve, bozuk veri ve yeniden senkronizasyon yönetilir. Protokol boyut sınırları ve timeout değerleri test edilir.
- A RX protokolünde LOAD, LED_SEQUENCE ve deney kontrol türleri açıkça ayrılır. B TX protokolü log/ACK/durum taşır; komut ve oturum kimliğiyle eşleştirilir.

### 5.2 Event Group

- Gerçek Event Group API'si kullanılır; notification eSetBits bunun yerine sayılmaz.
- Parser önce CommandQueue'ya başarıyla yazar, sonra EVT_COMMAND_READY bitini set eder.
- Event biti sayaç değildir; verinin ve bekleyen iş sayısının kaynağı Queue'dur.
- Referans ExecuteTask, event uyanışında ve bir komutun tamamlanmasında bekleyen Queue durumunu kontrol eder. Queue boş değilken yalnız yeni event bekleyerek işi unutmaz.
- Yeni komutlar aktif LED dizisini gizlice iptal etmez. Referans politika FIFO: aktif komut tamamlanır, sonra sıradaki çalışır. Kuyruğun dolması açık ret üretir.
- Event bitini iş bitişinde körlemesine temizlemek yerine tanımlı wait/clear sözleşmesi uygulanır.
- LED dizisi çalışırken ExecuteTask bütün dizi süresi boyunca tek bloklayan fonksiyona gömülmez; durum makinesi kullanır. Event bekleme timeout'u sonraki LED geçişinin kalan süresine göre belirlenir.

### 5.3 Notification ve sonuçlar

- ResultQueue'ya başarıyla eklenen her kayıt için ReportTask'a bir Give gönderilir.
- ReportTask Take(pdFALSE) ile bir sayım tüketip bir kayıt alır; biriktirilmiş sayımın dönüş değerini yanlışlıkla iş adedi olarak tekrar işlemez.
- ResultQueue'ya kabul edilmeyen kayıt için notification üretilmez.
- Uygulama notification indeksi 1; indeks 0 StreamBuffer iç kullanımı için ayrılır.
- ExecuteTask rapor kuyruğu dolduğu için LED geçişini bekletmez: sıfır/sınırlı bekleme politikası açık tanımlanır, kayıp sayacı artırılır. Kayıplı koşu tam ölçüm olarak sunulmaz.

## 6. LED zamanlama ve ölçüm

İlk LED'in gerçek yanma zamanı referans alınarak mutlak hedefler üretilir: t0+1000, t0+2000, ... ms. Sadece her işten sonra 1000 ms delay ekleyerek biriken kayma gizlenmez.

Her geçişte en az şu bilgiler kaydedilir:

```text
run_id, scenario_id, variant_id, command_id, event_seq,
previous_led, current_led, planned_us, actual_us,
previous_on_us, actual_on_duration_us, transition_lateness_us
```

- Geçiş gecikmesi = actual_us - planned_us.
- Önceki LED açık kalma süresi = gerçek sönme - gerçek yanma.
- Süre sapması = açık kalma süresi - 1.000.000 us.
- Ölçüm GPIO değişimine yakın kart zamanından alınır; bu yazılım zaman damgasıdır, fiziksel optik ölçüm değildir.
- LED'in geç yanması ile uzun açık kalması farklı sonuçlardır; ikisi ayrı gösterilir.
- Birden çok deadline kaçırılırsa hızlı yakala-söndür döngüsü yapılmaz. Öneri: missed_transition sayısını artır, tek geçiş yap, sonraki hedefi gelecekteki ilk uygun zaman dilimine taşı; atlanan hedefleri kaydet. Bu politika uygulamadan önce kesinleştirilecek.
- Ölçüm saati monotonic olmalı; çözünürlük, timer frekansı ve wrap yönetimi açıklanmalı. FreeRTOS tick ile mikrosaniye sayacı karıştırılmamalı.

Önerilen hedefler, geri bildirime açıktır:

| Ölçüt | Taslak hedef |
|---|---|
| Nominal LED süresi | 1000 ms |
| Referans geçiş gecikmesi | En fazla 10 ms |
| Komut son baytı RX → parser doğrulama/Queue kabulü | En fazla 50 ms; tam LED dizisinin bitişi değildir |
| Kayıp | S1'de uygulama/trace kaybı yok |
| Tek koşu | En az 3 tam renk turu; ağır trace için kısa tekrar pencereleri mümkün |
| Karşılaştırma | En az 30 geçiş; renk başına örnek sayıları da gösterilir |

100 baytlık rapor şartını korumak için LED olayları sabit **100 baytlık uygulama çerçevesi** olarak tasarlanacak; başlık, payload, padding ve bütünlük alanları bu toplamın içinde olacak. Kesin yerleşim sonraki aşamada belgelenecek. Diğer kontrol mesajlarının aynı boyutta olması zorunlu değil. UI bunları okunabilir loga dönüştürür.

UART TX StreamBuffer'a kabul, TX başlaması ve donanımın son baytı göndermesi ayrı olaylardır. Arayüzde görünme zamanı LED olay zamanı olarak kullanılmaz. 100 baytın ideal 115200/8N1 hat süresi yaklaşık 8,68 ms'dir; bu bir uçtan uca garanti değildir.

## 7. Tam olarak dört senaryo

### S1 — Doğru çalışan referans sistem

- Kesme tabanlı TX, doğru bloklanma, referans öncelikler, doğru Queue/Event/Notify tüketimi.
- LED dizisi sürerken EXE, TTL TX → A RX üzerinden 10.000 baytlık yük patlamalarını gönderir; kart alım zamanlarıyla LED geçişleriyle örtüşme doğrulanır.
- B hattından canlı LED logları alınır; UART ve UI gecikmeleri kart ölçümünden ayrılır.
- Beklenen kanıt: çalışan veri yolu, uygun Running/Ready/Blocked geçişleri, süre hedefleri ve sıfır kayıp. Başarı gerçek ölçümle doğrulanır.

### S2 — CPU rekabeti ve yanlış öncelik/bekleme yöntemi

- Yeni bağlantıda kart bulk göndermediği için CPU'yu meşgul eden gönderim deneyi ReportTask ve B TX sürücüsüne uygulanır.
- Hatalı koşul: ReportTask LED zincirinden yüksek öncelikli; B TX sürücüsünde polling beklemesi CPU'yu bırakmaz. Interrupt/scheduler kapatılmaz.
- B_TX_Stream yolu korunur. Polling ve kesmeli tüketiciler aynı anda aktif değildir; seçilen sürücü tamponun tek tüketicisidir.
- Tek 100 baytın yaklaşık 8,68 ms olması nedeniyle, görünür ve tekrarlanabilir CPU baskısı için LED geçişi çevresinde sınırlı bir tanı raporu dizisi kullanılır. Öneri: 20 adet 100 baytlık kayıt; adet ve tetik zamanı bütün karşılaştırmalarda sabit tutulur. Bunlar gerçek LED olaylarından ayrı etiketlenir.
- Düzeltme A: polling ve rapor yükü sabit, yalnız ReportTask önceliği düşürülür.
- Düzeltme B: yüksek öncelik geri alınır, yalnız TX kesmeli/bloklanan yönteme döner.
- PC'den A RX'e gelen bulk profili de tüm varyantlarda aynıdır. RX taşması oluşursa ayrıca raporlanır.
- İnceleme: ExecuteTask Ready bekleme süresi, uzun yanan LED ve CPU kullanımı. Bu bir baud veya aynı hatta bulk/kısa cevap rekabeti deneyi değildir; B hattındaki yük sabitken CPU bekleme yöntemi karşılaştırılır.


### S3 — Uzun parser işi ve parçalı işleme

- Hatalı koşul: yüksek öncelikli ParserTask'ta kalibre edilmiş, örneğin 100–200 ms CPU işi; iş yükü kartta ölçülür, vTaskDelay CPU işi sayılmaz.
- CPU işi LED geçişine yakın tetiklenir; tetikleme anı trace'e kaydedilir.
- Düzeltme: aynı toplam işi sınırlı parçalara böl; parçalar arasında düşük öncelikli task'lara gerçek çalışma fırsatı veren bloklanma uygula. Sadece taskYIELD yeterli kabul edilmez.
- Karşılaştır: LED gecikmesi, parser tamamlanma süresi, RX doluluk/kayıp. LED iyileşirken parser veya veri kaybı kötüleşebilir; bu bedel raporlanır.
- Başlangıç iş süresi/parça boyutu ve bekleme değerleri manifestte tutulur; bunlar ölçüm öncesi sabitlenir.

### S4 — Burst, event birleşmesi ve Queue tüketimi

- Kontrollü bekleyen ExecuteTask sırasında birden fazla tam LED komutu Queue'ya kabul edilir; aynı event biti tekrar set edilir.
- Hatalı koşul: event uyanışında yalnız bir komutu işle, tamamlanınca Queue'yu kontrol etmeden yeniden event bekle.
- Düzeltme: LED komutlarını FIFO sırayla tamamla; sıradaki komut için yeni event gerektirme. Aktif diziyi bozmadan bekleyen işleri tüket.
- Önce Queue'ya sığan burst ile event hatası izole edilir. Ardından kapasiteyi aşan burst ile açık ret sayacı doğrulanır; iki kayıp nedeni karıştırılmaz.
- İnceleme: Queue doluyken task'ın neden uyuduğu; event bitinin neden sayaç olmadığı; komut kuyruk yaşının artışı.
- FIFO'da uzun LED dizilerinin arkasında beklemek tek başına scheduler hatası değildir. Komut kabulü, çalışmaya başlama ve LED geçiş deadline'ları ayrı değerlendirilir.

## 8. Windows masaüstü arayüzü (.exe)

Teslim, Windows üzerinde kullanıcı tarafından **.exe ile açılabilen** masaüstü uygulamasıdır. Kullanıcıdan Python veya terminal komutu çalıştırması beklenmez. Kaynak ve tekrar paketleme adımları da teslim edilir. UI teknolojisi geri bildirim sonrası seçilir; Python/PySide + PyInstaller bir adaydır, kesin karar değildir.

Zorunlu işlevler:

- COM port seçimi, bağlan/ayrıl; firmware kimliği ve kart oturumu doğrulama.
- S1/S2/S3/S4 ve senaryo içi varyant seçimi; geçerli ayarların görünmesi.
- Deney başlat/durdur; kayıt hazırlama, kayıt durumu, sonuç klasörünü açma.
- Aynı COM portundan bulk ve komut gönderirken logları eşzamanlı alma; UI donmadan seri I/O yürütme.
- Tek host TX yöneticisiyle 10.000 baytlık yük üretimi, çerçeve/parça planlama ve tekrarlanabilir patlama profili. Gönderilen veri, gerçek host hızı ve kartta alınan baytlar ayrı kaydedilir.
- LED'lerin karttan doğrulanmış son durumu; bağlantı kopunca eski durumun güncel gibi gösterilmemesi.
- Her renk için gerçek açık kalma süresi, sapma, geçiş gecikmesi ve örnek sayısı.
- Zaman grafiği, min/ortalama/maksimum ve deadline ihlal sayısı.
- UART/StreamBuffer/Queue/rapor/trace kayıp sayaçları.
- Türkçe okunabilir log: örneğin “Kırmızı LED söndü; açık kalma 1037 ms; sapma +37 ms”.
- Ham veriyi JSONL/binary olarak koruma, CSV özet ve karşılaştırma dışa aktarma.
- Kullanıcının güncel kararı: her senaryo için yalnız bir tamamlanmış kayıt tutulur. Aynı senaryoda yeni varyant kaydı da öncekinin yerini alır; arayüzde çoklu koşu geçmişi tutulmaz. Test karşılaştırma sayıları ayrı doğrulama raporunda bulunabilir.
- “SystemView kaydını aç” eylemi: seçilen koşunun gerçek .SVDat dosyasını SystemView ile açar.
- SystemView bulunamaması, eksik trace, kayıt taşması ve uyuşmayan run_id açık hata/uyarı olarak gösterilir.

UI ile SystemView aynı TTL COM portunu eşzamanlı açmaz. TTL COM portunun iki yönü UI'ye aittir: TX → USART-A RX, RX ← USART-B TX. Trace için ayrı debug/RAM kayıt yolu kullanılacak; plansızca ham SystemView baytları ile uygulama logları aynı seri hatta karıştırılmayacak.

## 9. SEGGER SystemView altyapısı ve kayıt akışı

SystemView entegrasyonu isteğe bağlı ekran görüntüsü değildir; projenin temel teslimidir. Firmware'de FreeRTOS trace hook'ları, SystemView/RTT yapılandırması, task adları, ISR işaretleri ve uygulama olayları bulunacak. Kullanılan FreeRTOS/SystemView sürümleri sabitlenip kaydedilecek.

### 9.1 Debug donanımına uygun kayıt yöntemi

**Kesin donanım koşulu: J-Link yoktur; kartın yerleşik ST-LINK bağlantısı kullanılacaktır.** Bu projenin SystemView yöntemi RAM üzerinde single-shot/post-mortem kayıt ve ölçüm bittikten sonra ST-LINK/SWD ile dışa aktarmadır. Canlı SystemView RTT akışı bu sürümün kapsamında değildir. Arayüzün canlı UART logları ile sonradan açılabilen SystemView trace kaydı ayrı işlevlerdir.

- **Mevcut donanımla temel yol:** SystemView uyumlu single-shot veya post-mortem RAM kaydı. Koşu penceresi bittikten sonra SWD üzerinden doğru buffer içeriği çıkarılır ve geçerli .SVDat oluşturulur. Decoder'ın beklediği metadata ve ring sırası korunur; rastgele RAM dump'ına uzantı vermek yeterli değildir.
- ST-LINK firmware dönüşümü yapılmaz; J-Link satın alma veya kullanma gereksinimi yoktur.
- RAM kapasitesi, event hızı ve kayıt süresi bütçelenir. Uzun koşu sığmıyorsa aynı senaryo içinde kısa, kimlikli trace pencereleri alınır; eksik pencere tüm koşunun kaydı gibi sunulmaz.
- Çalışan ölçümü breakpoint ile durdurmak yasaktır. Single-shot dışa aktarmada halt gerekiyorsa ölçüm penceresi bittikten sonra yapılır; resume sonrası aynı kesintisiz koşu devam etmiş sayılmaz.

Uygulamanın ilk teknik doğrulaması: yerleşik ST-LINK ve seçilen debugger/CLI ile kısa bir RAM kaydını geçerli .SVDat dosyasına çıkarmak, SystemView'da task geçişlerini ve kullanıcı işaretini görmek. Bu doğrulama olmadan tam arayüz kayıt otomasyonu tamamlandı sayılmaz.

### 9.2 Arayüzden senaryo bazlı kayıt

1. UI benzersiz run_id oluşturur; senaryo/varyant/parametre manifestini yazar.
2. Firmware'e hazırlık komutu gönderilir; kuyruklar ve önceki koşu durumu güvenli şekilde kapatılmış olmalıdır.
3. Kartın RAM trace tamponu ve kayıt penceresi hazırlanır; hazır bilgisi doğrulanır. Hazır olmayan kayıtta UI “tam kayıt” göstermez.
4. Kart RUN_START(run_id, scenario_id, variant_id) işaretini uygulama kaydına ve SystemView'a yazar.
5. Deney çalışırken UI UART-B loglarını ham olarak kaydeder; SystemView trace kart RAM'inde tutulur.
6. RUN_END veya hata sonu işareti üretilir; tamamlanmamış işler ve son sayaçlar alınır.
7. Ölçüm penceresi bittikten sonra trace durdurulur; gerekiyorsa hedef halt edilerek ST-LINK/SWD üzerinden RAM kaydı çıkarılır ve .SVDat olarak koşu klasörüne eklenir. Bu duraklama LED zamanlama ölçümüne dahil edilmez. Dosyaların varlığı ve kimlik eşleşmesi denetlenir.
8. UI özet ve trace kapsamını gösterir. Kullanıcı aynı koşunun .SVDat dosyasını SystemView'da açar.

Hedef: başlat/durdur/kaydet akışını EXE'den yönetmek. SystemView'ın desteklenen CLI/TCP kontrolü sürümle doğrulanır. ST-LINK RAM çıkarımı için kullanılacak debugger/CLI ayrıca denenir. Otomasyon mümkün olmayan adım açık ve yönlendirilmiş olmalı; manuel eklenen trace “otomatik kaydedildi” diye gösterilmemeli. Manuel fallback tek başına tam otomasyon kabulü sayılmaz.

### 9.3 Trace olayları ve güvenilirlik

Asgari işaretler: RUN_START/END, LOAD_START/END, FRAME_VALID, COMMAND_ACCEPT/REJECT, EVENT_SET, EXECUTE_START, LED_TRANSITION, PARSER_WORK_BEGIN/END, RESULT_ACCEPT/DROP, NOTIFY_SENT, REPORT_TX_BEGIN/END.

- Task Running/Ready/Blocked ve ISR süreleri izlenir; uygulama event'leri run_id, command_id ve event_seq ile eşleşir.
- MCU ölçüm saati ile SystemView zaman tabanı arasındaki eşleme/senkronizasyon noktaları belgelenir; host saatiyle MCU saati doğrudan çıkarılmaz.
- Her UART baytına özel kullanıcı logu eklenmez. ISR trace yükü ve taşma ayrıca gözlenir.
- Trace buffer dolduğunda LED task'ını sonsuz bekletmek yasaktır; kayıp/overflow görünür olur.
- Trace açık/kapalı kısa bir kalibrasyon aynı senaryonun ölçüm kontrolüdür; beşinci senaryo değildir.
- Firmware ELF, map, build kimliği ve trace konfigürasyonu korunur; trace başka firmware ile açıklanmaz.

## 10. Koşu kayıt paketi

```text
records/S1/  (diğer senaryolar için S2, S3, S4)
  manifest.json
  raw_rx_uart.bin
  host_tx.bin
  host_tx_events.jsonl
  events.jsonl
  led_timing.csv
  summary.json
  systemview/
    trace.SVDat
    capture_metadata.json
  notes.md
```

Yeni koşu önce records/.pending altında hazırlanır. UART kaydı ve eşleşen, tam SystemView penceresi doğrulandıktan sonra records/Sx değiştirilir ve önceki tamamlanmış kayıt silinir. Eksik/başarısız koşu önceki geçerli kaydı değiştirmez. Geçici başarısız kayıtlar tamamlanmış senaryo kaydı sayılmaz.

Manifest: kart/firmware/build hash, senaryo/varyant, task öncelikleri, tick/CPU/ölçüm frekansı, baud, buffer/Queue kapasiteleri, LED süreleri, host bulk profili, S2 tanı raporu adedi, parser iş yükü, probe/kayıt modu ve trace penceresi. Ham olaylar ve durum mesajları ayrı dosyalardadır.

İşlem durumu ayrı alanlarda tutulur: deney sonucu PASS/FAIL, kayıt durumu COMPLETE/PARTIAL/MISSING, sistem bağlantı durumu. Deadline ihlali olan ama doğru kaydedilmiş koşu değerli bir FAIL kanıtıdır; kayıt eksiği saklanmaz.

Her varyant için tahmin, gözlem, darboğaz, tek değişiklik ve bedeli notes.md içine yazılır. Ekran görüntüsü ham trace'in yerine geçmez.

## 11. Kabul koşulları

1. Tek TTL ile PC TX → USART-A RX ve USART-B TX → PC RX veri yolu çalışır. Bulk ve komutlar EXE tarafından üretilir; LED komutları parser yolundan geçer. Loopback yoktur.
2. EXE, Python kurulumu gerektirmeden açılır; COM üzerinden kontrol ve kayıt yapar.
3. S1 gerçek ölçümle doğrulanır; süre hedefleri geri bildirim sonrası kesinleşir.
4. S2 CPU rekabetini, S3 parser kaynaklı gecikmeyi, S4 event/Queue hatasını tekrarlanabilir biçimde gösterir.
5. Her senaryoda SystemView ile ilgili neden incelenebilir; hata/düzeltme kayıtları karışmaz.
6. En az bir LED'in uzayan süresi ilgili Ready/Running zamanlarıyla açıklanır; sonuç uydurulmaz.
7. ResultQueue/trace kaybı, RX hatası, kısmi stream gönderimi ve komut reddi ayrı sayılır.
8. UI seçilen koşunun .SVDat dosyasını açabilir; kaydın run_id ve pencere bilgisi doğrulanır.
9. Önceki haftalar değiştirilmez; yeni çalışma hafta-05 içinde tutulur.
10. Kaynaklar, build/paketleme yönergesi, kablolama, dört senaryo tablosu ve gerçek kanıt dosyaları teslim edilir.

## 12. Uygulama öncesi açık kararlar

- Kullanıcının bu SPEC için geri bildirimi.
- Kart revizyonu, USART-A RX pini ve farklı USART-B TX pini; B için USART2 PA2 önerisinin doğrulanması.
- J-Link olmadığı kesindir. Açık seçimler: yerleşik ST-LINK ile kullanılacak RAM kayıt çıkarma debugger/CLI aracı, kurulu SystemView sürümü ve EXE entegrasyonunun doğrulanması.
- Kesin LED gecikme toleransı, parser iş/parça süreleri ve trace pencere süresi.
- StreamBuffer/Queue boyutları, 100 bayt rapor formatı, A/B protokolü.
- Masaüstü UI teknolojisi, dağıtım biçimi ve SystemView otomasyon yöntemi.

Uygulama ve gerçek kart testleri yürütülmektedir; güncel sonuçlar docs/VALIDATION.md ve docs/regression-results.json içindedir.

## 13. Kaynaklar

- Kullanıcının bu konuşmadaki mimari, dört senaryo, kart, tek TTL, EXE ve SystemView talepleri birincil kapsam kaynağıdır.
- Önceki yerel bağlam: `../hafta-03/spec.md` (F407, USART2/TTL ve mevcut çalışma düzeni; yeni ölçüm kanıtı değildir).
- ST UM1472: https://www.st.com/resource/en/user_manual/um1472-stm32f4-discovery-stmicroelectronics.pdf — kart ve LED pinleri.
- SEGGER SystemView kılavuzu: https://doc.segger.com/UM08027_SystemView.html — kayıt biçimi, taşıma seçenekleri ve otomasyon başvurusu; kurulu sürümde doğrulama gerekir.
- SEGGER single-shot: https://www.segger.com/products/development-tools/systemview/technology/single-shot-recording/ — debugger ile kayıt çıkarma yaklaşımı.
- FreeRTOS Event Group: https://freertos.org/Documentation/02-Kernel/04-API-references/12-Event-groups-or-flags/04-xEventGroupWaitBits
- FreeRTOS StreamBuffer: https://freertos.org/Documentation/02-Kernel/04-API-references/08-Stream-buffers/05-xStreamBufferReceive
