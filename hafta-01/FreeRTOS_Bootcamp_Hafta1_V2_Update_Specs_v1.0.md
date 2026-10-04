# FreeRTOS Bootcamp — Hafta 1 / V2 Update Specs v1.0

**Tarih:** 26 Eylül 2026  
**Durum:** Uygulanacak tasarım ve kabul şartnamesi; V2 henüz uygulanmış veya kart üzerinde doğrulanmış değildir.  
**Temel belge:** [Specs v0.3](FreeRTOS_Bootcamp_Hafta1_Specs_v0.3.md)  
**Mevcut uygulama sonuçları:** [V1 ölçüm raporu](analysis/report.md)  
**Hedef proje:** STM32F407G-DISC1, `firmware/Homework_001`, Python/PySide6 arayüzü.

## 1. Amaç ve bu belgenin önceliği

Hocanın geri bildirimi: fiziksel kartta buton yanıtlarını 20 ms altına, mümkünse maksimum 10 ms'ye indirmek; yaklaşık 160 ms'ye çıkan gecikmeyi, özellikle d3 beklemesini azaltmak. **Task öncelikleri değiştirilmeyecek.**

V2'nin kabul hedefi, tanımlanan deney koşullarında kabul edilen bütün fiziksel buton olaylarının **R ≤ 10000 µs** ile tamamlanması ve hiçbirinin kaybolmamasıdır. Düşen olayların çıkarılmasıyla düşük maksimum elde edilmesi kabul edilmez.

Bu belge v0.3'ün tamamını tekrarlamaz. Yalnız aşağıda açıkça değiştirilen kuyruk, CPU yük yürütme biçimi, baud, protokol sürümü ve deadline raporlama hükümleri V2 için v0.3'ün yerine geçer. Diğer donanım, güvenli kayıt, ölçüm bütünlüğü ve hata görünürlüğü hükümleri korunur. v0.3'teki geçmiş inceleme ve uygulama durumu ifadeleri tarihsel bağlamdır.

460800 baud ve işin parçalı yürütülmesi kullanıcı tarafından seçilen V2 tasarım değişiklikleridir; bunlar hocanın ayrıca doğrulanmış kurs şartları olarak sunulmayacaktır. V1'in 115200 baud sonuçları arşivlenir; V2 aynı koşullarla yapılmış bir V1 tekrarı diye etiketlenmez.

## 2. Mevcut durum ve gecikme kaynakları

Mevcut `app.c` içinde ISR → Button task yolu için `button_q` zaten vardır. Button task'ın hazırladığı BTN ve Telemetry task'ın hazırladığı TEL mesajları daha sonra aynı 16 elemanlı `tx_q` içine girer. UART task'ı FIFO sırayla bunları gönderir. S5'te Telemetry task'ı ayrıca tek parça yaklaşık 5 ms CPU işi yapar.

Bu nedenle iki farklı bekleme vardır:

1. BTN mesajının ortak kuyrukta eski TEL mesajlarının arkasında kalması.
2. Telemetry task'ı çalışırken daha düşük öncelikli Button/UART task'larının CPU alamaması.

V1 resmi seçili S5 koşusunda maksimum R 164,794 ms, ortalama d3 yaklaşık 113,644 ms, TX kuyruk tepe doluluğu 16 ve 18 BTN TX düşmesi ölçülmüştür. Kullanıcının daha sonraki ekran görüntüsü başka bir koşudur; o görüntüdeki sayılar resmi seçili koşunun ham verisiyle birleştirilmeyecektir. Geri bildirimdeki “d3'ün 96 ms'si” sabit bir sistem parametresi değildir.

## 3. Korunacak gereksinimler

| Özellik | V2 sözleşmesi |
|---|---|
| Uygulama task'ları | Telemetry, Button, UART; yeni uygulama task'ı eklenmez |
| Native FreeRTOS öncelikleri | Telemetry=3, Button=2, UART=1; çalışma sırasında da sabit |
| CPU / zaman tabanı | SYSCLK 168 MHz, TIM5 1 MHz, RTOS tick 1 kHz |
| UART sahibi | USART2 DMA TX çağrısını yalnız UART task'ı yapar |
| Çerçeve | TEL ve BTN, LF dahil 64 bayt; 8N1 |
| Fiziksel bağlantı | PA2 → TTL RX, PA3 ← TTL TX, ortak GND, 3,3 V lojik |
| Ölçüm | MCU t0…t4; R=t4−t0; PC varış zamanı ölçüm değildir |
| Isınma / basış | 5 s ısınma; kabul edilen basış aralığı ≥0,5 s |
| Debounce | 30 ms; ilk geçerli kenarın zaman damgası korunur |
| Hata görünürlüğü | Drop, timeout, UART hatası ve eksik kayıt gizlenmez |
| Eski veriler | V1 firmware kimliği, ham kayıtlar ve seçili sonuçlar korunur |

Öncelik yükseltme, priority inheritance üzerinden dolaylı öncelik değişikliği, hesaplamayı uzun ISR içine taşıma, uzun interrupt maskesi veya UART için busy-wait bu tasarımın çözümü değildir. Mevcut RTOS uyumlu IRQ öncelik kuralları korunur.

## 4. Değişiklik A — BTN öncelikli ayrı TX kuyrukları

```text
Buton ISR → button_q[8] → Button task → btn_tx_q[8] ┐
                                                   ├→ UART task → USART2 DMA
Telemetry task ─────────────────────→ tel_tx_q[16] ┘
```

### 4.1. Kuyruk ve seçim sözleşmesi

- `button_q` ISR olaylarını taşımaya devam eder. Yeni `btn_tx_q` hazırlanmış BTN mesajlarını, `tel_tx_q` TEL mesajlarını taşır. Her sınıf kendi içinde FIFO'dur.
- Kuyruk kapasiteleri başlangıç tasarımı olarak 8/8/16'dır. Ayrı TX kuyruklarının ek RAM maliyeti build ve minimum boş heap ölçümüyle doğrulanır; sessizce kuyruk küçültülmez.
- Her yeni DMA aktarımı seçilirken önce BTN, sonra TEL seçilir. Kuyrukların seçim kontrolü kısa, sınırlı bir kritik bölümle tutarlı yapılır; formatlama ve HAL aktarımı bu kritik bölümde yapılmaz.
- BTN kontrolünden sonra seçilen bir TEL, BTN gelmeden hemen önce taahhüt edilmiş olabilir. Bu tek devam eden/taahhüt edilmiş çerçevenin engellemesi gecikme bütçesinde açıkça yer alır. Kesinlikle sıfır TEL beklemesi iddia edilmez.
- UART task'ı yalnız bir sınıfın kuyruğunda sonsuz beklemez. Her başarılı enqueue, ortak “iş var” task notification bitini set eder. Task uyandığında kuyrukları yeniden kontrol eder; notification sayısı mesaj sayısı yerine kullanılmaz.
- Kuyruk boş kontrolü ile uykuya geçiş arasında kaybolan uyandırma olmamalıdır. Bildirim beklenmeden önce körlemesine temizlenmez. “İş var”, “TX tamamlandı”, “TX hata” ve kontrol bildirimleri ayrı bitlerdir; DMA bekleyişi iş bildirimini yutsa bile kuyruklar sonraki seçimde yeniden taranır.
- Kuyruk dolduğunda üretici bloklanarak CPU yükünü değiştirmez. Sıfır beklemeli enqueue başarısızlığı ilgili sayaç ve olay durumuna yazılır. BTN kaybı kabul testini başarısız yapar; TEL kaybı da raporlanır.
- Devam eden DMA aktarımı yeni BTN geldi diye kesilmez. DMA tamponu TC/abort tamamlanıncaya kadar sahibi tarafından korunur.

### 4.2. STOP, kontrol ve DUMP

Tek ortak TX kuyruğuna ait eski barrier mantığı aynen kopyalanamaz. STOP sırasında yeni olay kabulü ve TEL üretimi kapatılır; `button_q` içindeki daha önce kabul edilmiş bütün olayların Button task tarafından işlendiği barrier ile doğrulanır. Ardından **iki TX kuyruğu ve aktif DMA** birlikte boşalmadan drain tamamlandı sayılmaz.

Kontrol/DUMP işleri ayrı bir kontrol yolu üzerinden aynı UART sahibine iletilir; RUN sırasında uzun dump gönderilmez. RAM kaydı ancak bütün kabul edilen olaylar terminal duruma ulaştığında dondurulur. Drain zaman aşımı INCOMPLETE/FAULT olarak görünür; başarı gibi sunulmaz. Yeni START, önceki kaydın kurtarılmasına ilişkin mevcut arayüz korumasını korur.

## 5. Değişiklik B — Aynı CPU işini parçalı yürütmek

Amaç S5 yükünü azaltmak değil, yüksek öncelikli task'ın CPU'yu kesintisiz tuttuğu süreyi sınırlamaktır.

| Senaryo | Periyot | Aktivasyon başına CPU işi | Başlangıç dilim tasarımı |
|---|---:|---:|---|
| S0 | Telemetri yok | 0 | Yok |
| S1 | 100 ms | 0 | Yok |
| S2 | 20 ms | 0 | Yok |
| S3 | 10 ms | 0 | Yok |
| S4 | 10 ms | Yaklaşık 2 ms | 2 × yaklaşık 1 ms |
| S5 | 10 ms | Yaklaşık 5 ms | 5 × yaklaşık 1 ms |

- Başlangıç uygulaması dilimler arasında `vTaskDelay(1)` kullanır; son dilimden sonra ek dilim arası bekleme eklenmez. Bir tick bekleme tick fazına bağlıdır, tam 1000 µs duvar zamanı garantisi değildir. `taskYIELD()` ve `vTaskDelay(0)` alt öncelikli task'lara CPU bırakma çözümü olarak kullanılmaz.
- 5 × 1 ms hesaplama ve dört adet en fazla yaklaşık bir tick bekleme, 10 ms periyot içinde yürütülmek üzere tasarlanır. Gerçek formatlama, scheduler ve IRQ ek yükleriyle bu koşul ölçülür; sığdığı varsayılmaz.
- Task periyodu mutlak referanslı `vTaskDelayUntil` yaklaşımıyla korunur. Her parça sonrasında “yeniden 10 ms bekle” yaklaşımı kullanılmaz. TEL üretim periyodu aynı aktivasyon noktaları arasında ölçülür; mesaj enqueue anı ayrıca farklı olabilir.
- Hesaplama kalibrasyonu bloklama sürelerini içermez. Parça süreleri ayrı ölçülür ve toplanır. Aktivasyonun uçtan uca duvar süresi ayrı metrik olarak saklanır. İşin bir kısmını atlamak veya delay süresini CPU işi diye saymak yasaktır.
- Başlangıç kalibrasyon hedefi S4 için 2000 µs, S5 için 5000 µs; toplam kalibrasyon ortalaması hedefin ±%5'i içinde, tek dilim kalibrasyon maksimumu ≤1100 µs olmalıdır. Gerçek koşudaki interrupt etkileri ayrıca raporlanır.
- İş dilimlerine ayrılırken hesaplama durumu devam ettirilir; parça sınırlarının kalibrasyona ve yapılan işe etkisi belgelenir. Kalibrasyon ölçümden önce tamamlanır.
- `period_overrun` sıfır olmalıdır. Aşım varsa yük azaltılarak saklanmaz; dilim/bekleme düzeni yeniden tasarlanır ve yeniden doğrulanır. Bu şartname tick hızını değiştirmeyi veya yeni timer kullanmayı kendiliğinden zorunlu kılmaz.

## 6. Değişiklik C — 460800 baud

V2 varsayılanı USART2 **460800 baud, 8N1**, çerçeve uzunluğu yine 64 bayttır. Firmware ve arayüz aynı baud ile açılmalıdır. V1 115200 seçeneği uyumluluk ve karşılaştırma için korunur.

| Hat hızı | 64 bayt için nominal hat süresi | Bir TEL kalan süresi + bir BTN üst sınırı, yalnız hat |
|---|---:|---:|
| 115200 | 5,556 ms | Yaklaşık 11,111 ms |
| 460800 | 1,389 ms | Yaklaşık 2,778 ms |

Formül: `64 × 10 / baud`. Gerçek baud, USART çevre birimi saati ve BRR bölücüsünden hesaplanır; nominal/gerçek baud ve hata yüzdesi metadata'ya yazılır. Bu süreler CPU beklemesi ve HAL/IRQ ek yükünü içermez.

115200 baud'da yeni BTN, bir TEL iletiminin başına rastlarsa yalnız seri hat beklemesi ve kendi aktarımı bile 10 ms'yi aşabilir. Dolayısıyla 115200/64 bayt profilinde bütün fazlar için 10 ms garanti edilmez.

Baud profili ilk uygulamada build sırasında seçilir ve GUI bağlantıdan önce kullanıcıya baud seçtirir. RUN sırasında baud değiştirme veya sessiz otomatik baud geçişi yapılmaz. Yanlış baud/HELLO zaman aşımı açık hata mesajıyla gösterilir. TTL adaptörünün 460800 desteği gerçek bağlantıda doğrulanır; başarısız olursa 10 ms hedefi sağlandı denmez.

## 7. Zaman damgaları ve performans bütçesi

V1 ile aynı anlamlar korunur: t0 kabul edilen ISR giriş zamanı; t1 Button task dequeue sonrası; t2 BTN TX kuyruğuna gönderim sınırı; t3 DMA başlatma sınırı; t4 UART TC callback zamanı. `d1=t1−t0`, `d2=t2−t1`, `d3=t3−t2`, `d4=t4−t3`. 32 bit wrap hesabı korunur. t4 DMA bellek transfer tamamlanmasıyla karıştırılmaz; UART son bit tamamlanmasına dayanan mevcut TC yolu korunur.

| Metrik | V2 mühendislik bütçesi |
|---|---:|
| d1 | ≤1,5 ms |
| d2 | ≤0,2 ms |
| d3 | ≤5,0 ms |
| d4 | ≤1,6 ms |
| Toplam bütçe | 8,3 ms; 10 ms sınırına 1,7 ms pay |

Bu tablo kanıtlanmış üst sınır veya ölçülmüş sonuç değildir. Ana kabul kriteri olay başına R≤10 ms'dir; aşama bütçesi aşılırsa neden araştırılır. 1 s olay gözetim/timeout süresi 10 ms'ye indirilmez: geç tamamlanan olayların gerçek gecikmesi kaybolmamalıdır.

Başarıyla iletilmiş fakat geç bir olay `ok` taşıyabilir; bunun anlamı zamanında tamamlanma değildir. 10 ms ve tarihsel 20 ms ihlalleri ayrı hesaplanır. Tam 10000 µs kabul edilir, `R > 10000` geçtir. Başarısız olaylara R=0 atanmaz.

## 8. Protokol, metadata ve arayüz

V1 **PROTO2** kayıtları değişmez. V2, farklı metadata/deadline anlamlarını karıştırmamak için **PROTO3** olarak tanıtılır. 64 bayt çerçeveleme, M1/M2 zaman damgası aktarımı, CRC, kayıt sayısı doğrulaması ve atomik kayıt ilkeleri korunur. Yeni GUI hem PROTO2 hem PROTO3 okur; bilinmeyen sürümü açıkça reddeder. Eski GUI'nin V2'yi desteklediği varsayılmaz.

PROTO3 için eski ortak alanlara ek olarak aşağıdaki metadata zorunludur:

- `design_version=2`, `variant`, `deadline_us=10000`, nominal baud, `baud_actual`, `uart_brr`, `uart_pclk_hz`.
- `queue_policy=btn_first`, `btn_txq_len`, `tel_txq_len`; eski `txq_len` birleşik fiziksel kuyruk varmış gibi kullanılmaz. Ayrık kuyruklu PROTO3'te bunun yerine yeni alanlar esas alınır.
- `work_mode`, `slice_target_us`, `slice_count`, `slice_gap_ticks`, `cpu_work_mean_us`, `cpu_work_max_us`, `slice_max_us`, `activation_wall_max_us`; kalibrasyon ve koşu gözlemleri açıkça ayırt edilir.
- `btn_txq_hwm`, `tel_txq_hwm`, mevcut BTN/TEL düşme sayaçları, `late_10ms`, `late_20ms`, `period_overrun`.
- Firmware ELF SHA256, kaynak commit/dirty bilgisi ve build profili host metadata'sında korunur. Firmware'in kendi kısa kimliği tam ELF hash'i yerine sunulmaz.

Yeni sayaçların MET/SUM sınıflaması uygulamada tek bir protokol tablosunda sabitlenir ve firmware/parser testleriyle eşleştirilir. Her satır 63 ASCII payload baytını aşmamalıdır. Eski `late_completed` PROTO2'de 20 ms anlamını korur; PROTO3'te açık `late_10ms` ve `late_20ms` kullanılır. Eksik zorunlu alanlı dump geçerli sayılmaz.

GUI bağlantı öncesinde COM ve baud seçtirir; bağlantı sonrasında protokol, varyant ve deadline gösterir. V2 grafiğinde 10 ms ana sınır, 20 ms karşılaştırma sınırı yer alır. Canlı BTN sayacı ile deney sonu doğrulanmış R grafiğinin farkı açıklanır. Önceki kaydı alma/START koruması ve CONFIGURED→WARMUP→ARMED yönlendirmesi korunur.

CSV olay sütunları V1 ile aynı kalabilir; sürüm ve varyant metadata'dan okunur. Analiz script'lerinin sabit 115200, tek TX kuyruğu veya yalnız 20 ms varsayımları kaldırılır. PROTO2 ve PROTO3 sonuçları açık etiket olmadan birleştirilmez.

## 9. Uygulama ve karşılaştırma sırası

| Varyant | TX düzeni | CPU işi | Baud | Amaç |
|---|---|---|---:|---|
| B0 / V1 | Ortak FIFO | Tek parça | 115200 | Arşivlenmiş referans |
| Q | BTN öncelikli ayrık | Tek parça | 115200 | Yalnız kuyruk değişiminin etkisi |
| QW | BTN öncelikli ayrık | Parçalı | 115200 | CPU düzeninin ek etkisi |
| QB | BTN öncelikli ayrık | Tek parça | 460800 | Baud etkisini ayrıştırmak |
| QWB / V2 | BTN öncelikli ayrık | Parçalı | 460800 | Nihai tasarım |

Q/QW profillerinin 10 ms'yi geçmesi test hatası diye gizlenmez; bunlar tanı/karşılaştırma profilleridir. Nihai kabul QWB içindir. Varyantlar aynı derleyici/optimizasyonla oluşturulur; doğal olarak farklı ELF hash'leri ayrı kaydedilir. V1 firmware ve ölçümleri üzerine yazılmaz.

Uygulama sırası: V1 arşivi → protokol/metadata ve GUI uyumluluğu → ayrık kuyruklar ve yeni drain → parçalı iş ve kalibrasyon → 460800 profil → masaüstü testleri → kart denemeleri → analiz ve Windows paket testi.

## 10. Doğrulama ve kabul

### 10.1. Yazılım ve firmware davranış testleri

- BTN ve TEL birlikte beklerken BTN seçimi; her sınıfta FIFO; boş kuyruk/uyandırma yarışları; aktif TEL sırasında gelen BTN'nin sonraki seçimde alınması.
- İki kuyruğun dolması, ayrı HWM/drop sayaçları; zorlanmış BTN kaybının raporda başarısızlığa dönüşmesi.
- STOP sırasında button_q, iki TX kuyruğu ve aktif DMA birlikte doluyken bütün olayların terminal duruma ulaşması; yanlış erken DUMP/START olmaması.
- CPU iş kalibrasyonunda bekleme sürelerinin hariç tutulması; toplam işin ve üretim periyodunun korunması; overrun'ın görünmesi.
- PROTO2 ve PROTO3 fixture'ları; CRC bozulması, eksik MET/SUM, yanlış sürüm/baud; 32 bit taşma; tam 10000/10001 ve 20000/20001 µs sınırları.
- GUI: önceki kayıt kilidi, baud seçimi, 10/20 ms sınırları, başarısız olay gösterimi, kaynak ve paketlenmiş EXE açılışı. Sentetik test sonuçları donanım kanıtı değildir.

### 10.2. Fiziksel kart deneyleri

1. Q, QW ve QB için S5'te en az 30 kabul edilen fiziksel olay; 5 s ısınma ve ≥0,5 s aralık. B0 arşivi referans olarak kullanılır; yeni B0 çekilirse ayrı kaydedilir.
2. Nihai QWB ile S0–S5'in her birinde en az 30 kabul edilen olay. Aynı nihai ELF, saatler ve ayarlar kullanılır.
3. QWB S5 için en az 100 kabul edilen olaylık ek dayanıklılık koşusu. 128 kayıt sınırı aşılmadan durdurulur; gerekirse bağımsız koşular yapılır, eksik dump'lar birleştirilerek tamamlanmış gösterilmez.
4. Basış fazları değişken tutulur. `t0` ile telemetri aktivasyon referansı arasındaki 10 ms faz dağılımı raporlanır; her 1 ms dilimde örnek hedeflenir. Fazı kapsanmayan bölgeler açıkça belirtilir. Tek faza kilitli basışla maksimum iddiası yapılmaz.
5. 460800 bağlantısında fiziksel TTL ile HELLO, koşu, STOP ve tam DUMP doğrulanır; çerçeve/CRC/UART hataları sayılır. Ölçüm sırasında breakpoint kullanılmaz.

### 10.3. Nihai QWB geçiş koşulları

- Kabul edilen her buton olayı iletilmiş olmalı; BTN queue/TX drop, timeout, kayıt taşması veya kayıtsız olay **0**.
- Başarılı olayların tamamında **R≤10000 µs**; `late_10ms=0`. Ortalama veya p99 tek başına yeterli değildir.
- Normal tanımlı yükte TEL drop, UART/format/CRC hatası, drain timeout ve periyot aşımı **0** olmalı. Başarısız koşular arşivden silinmez.
- S4/S5 CPU kalibrasyon hedefleri sağlanmalı; gerçek üretim hızı hedefin ±%1'i içinde olmalı. Yük/frekans azaltılarak hedef sağlanmış sayılmaz.
- Dump kayıt sayısı accepted sayısıyla uyumlu olmalı; kaynak hardware, protokol, varyant ve ELF kimliği eksiksiz olmalı.

Testlerden geçmek tanımlanan örneklemde hedefin sağlandığını gösterir; matematiksel WCRT garantisi değildir. Her faz için sert üst sınır iddiası ayrıca interrupt/critical section ve scheduler analizi gerektirir. Logic analyzer ile kenar/son bit doğrulaması yapılırsa kullanılan pinler ve ölçüm etkisi belgelenir; yapılmadıysa raporda belirtilir.

## 11. Dosyalar ve teslim çıktıları

| Alan | Planlanan değişiklik |
|---|---|
| `firmware/Homework_001/Src/app.c`, `Inc/app.h` | Ayrık TX kuyrukları, uyandırma, drain, parçalı iş, sayaçlar |
| UART init / `.ioc` / build yapılandırması | 115200 ve 460800 profilleri; V2 baud tutarlılığı |
| `interface/src/protocol.py` | PROTO2/PROTO3 sözleşmeleri ve zorunlu alan doğrulaması |
| `interface/src/serial_worker.py`, `main.py` | Baud seçimi, sürüm/variant, deadline ve kullanıcı yönlendirmesi |
| `interface/src/simulator.py`, `tests/` | V2 simülasyon fixture'ları ve regresyon testleri |
| `analysis/` | Varyant bazlı karşılaştırma, d1…d4, 10/20 ms ihlalleri |
| `docs/` ve `README.md` | V2 kurulum, protokol ve deney adımları |

Yeni gerçek kayıtlar `measurements/v2/<variant>/runs/` altında; seçili final kayıtlar `measurements/v2/QWB/selected/` altında tutulur. V2 rapor ve grafikler `analysis/v2/` altında oluşturulur. Mevcut V1 seçim script'i V2 klasörlerini otomatik taramaz; V2 seçimi varyant ve firmware kimliğini denetler.

V2 teslimi: build/ELF kimliği, test günlükleri, her senaryonun ham CSV+metadata+seri akışı, varyant karşılaştırma tablosu, d3/R grafikleri, doğrulama sınırları ve çalışan Windows paketi. Şu anki teslim yalnız bu güncelleme şartnamesidir; firmware veya arayüz bu belge oluşturulurken değiştirilmemiştir.
