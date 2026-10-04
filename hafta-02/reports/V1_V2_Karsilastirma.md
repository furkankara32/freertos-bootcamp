# V1–V2 genel karşılaştırma ve sonuç raporu

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

| Sürüm / senaryo | Kabul | Tamamlanan | Min | Ortalama | Medyan | p95 | Maks | >10 ms | >20 ms |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| V1 / S0 | 73 | 73 | 5.627 | 5.636 | 5.633 | 5.655 | 5.659 | 0 | 0 |
| V2 / S0 | 62 | 62 | 1.471 | 1.477 | 1.473 | 1.494 | 1.498 | 0 | 0 |

Süreler ms; istatistikler yalnız tamamlanan olaylar içindir. Eşik aşımı sayıları da tamamlanan olaylara aittir; düşen mesajlar ayrıca gösterilir.

| Ortalama aşama | V1 (µs) | V2 (µs) |
|---|---:|---:|
| t1−t0: kesme → olayı alma | 18.274 | 17.887 |
| t2−t1: mesaj hazırlama | 26.534 | 26.548 |
| t3−t2: hazır → TX başlangıcı | 34.575 | 38.887 |
| t4−t3: TX başlangıcı → UART TC | 5556.151 | 1393.661 |

İki sürümde de kabul edilen butonların tamamı gönderildi; kuyruk kaybı yok. S0'da telemetri olmadığı için ortak FIFO'nun telemetriyle dolma problemi tetiklenmez. İlk üç aşamanın ortalamaları birbirine yakındır; fark esas olarak t4−t3'tedir.

**Şu yüzden böyle oldu:** USART2 çerçevesi 64 bayt ve 8N1'dir; bayt başına 10 bit ile nominal süre 640/115200 ≈ 5,556 ms, 640/460800 ≈ 1,389 ms olur. Ölçülen süreler bu büyüklüklerle uyumludur. Callback/başlatma ve gerçek baud farkları nedeniyle birebir eşitlik beklenmez. V2 düşük yükte aynı mesajı yaklaşık dörtte bir hat süresinde taşır. Bu senaryo tek başına kuyruk politikasının veya iş dilimlemenin kazancını kanıtlamaz.

Örnek olaylar: V1 run=1/id=13 toplam 5,655 ms; V2 run=2/id=3 toplam 1,493 ms. Bunlar ayrı fiziksel basışlardır; tablo tek olay yerine tüm tamamlanmış olay dağılımlarını verir.

## 3. V1 S5 ↔ V2 S5

| Sürüm / senaryo | Kabul | Tamamlanan | Min | Ortalama | Medyan | p95 | Maks | >10 ms | >20 ms |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| V1 / S5 | 108 | 64 | 17.888 | 144.949 | 161.944 | 165.217 | 165.562 | 64 | 63 |
| V2 / S5 | 78 | 78 | 1.471 | 1.864 | 1.619 | 2.761 | 3.256 | 0 | 0 |

Süreler ms; istatistikler yalnız tamamlanan olaylar içindir. Eşik aşımı sayıları da tamamlanan olaylara aittir; düşen mesajlar ayrıca gösterilir.

| Kayıp / doluluk | V1 S5 | V2 S5 |
|---|---:|---:|
| BTN TX kaybı / kabul | 44 / 108 (%40,74) | 0 / 78 (%0) |
| TEL kaybı / üretilen | 49 / 4158 (%1,18) | 0 / 3986 (%0) |
| TEL tamamlanan | 4109 | 3986 |
| TX en yüksek doluluk | ortak FIFO 16/16 | BTN 1/8; TEL 1/16 |
| UART donanım hatası / timeout | 0 / 0 | 0 / 0 |

| Ortalama aşama | V1 (µs) | V2 (µs) |
|---|---:|---:|
| t1−t0: kesme → olayı alma | 430.188 | 257.756 |
| t2−t1: mesaj hazırlama | 26.391 | 39.423 |
| t3−t2: hazır → TX başlangıcı | 138935.328 | 160.679 |
| t4−t3: TX başlangıcı → UART TC | 5556.609 | 1406.462 |

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

- **S0:** tamamlanan olayların ortalama yanıtı bu örneklemde %73.79, gözlenen maksimumu %73.53 daha düşük.
- **S5:** tamamlanan olayların ortalama yanıtı bu örneklemde %98.71, gözlenen maksimumu %98.03 daha düşük.

Bu yüzdeler ölçülen iki dağılımın betimsel farkıdır; eşlenmiş giriş deneyi veya değişiklik başına nedensel etki değildir. S5'te V1'in 44 düşen mesajı gecikme istatistiğinde yoktur; bu nedenle yüzdeyi kayıp oranından bağımsız başarı ölçütü olarak okumamak gerekir.

| Koşu | Aktif süre (s) | Kabul edilmiş giriş/s |
|---|---:|---:|
| V1 S0 | 35.236 | 2.072 |
| V1 S5 | 41.580 | 2.597 |
| V2 S0 | 33.570 | 1.847 |
| V2 S5 | 39.860 | 1.957 |

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

- Manuel girişler aynı fiziksel basış dizisi değildir. Koşu süreleri ve basış hızları farklıdır; V1 S5'te daha fazla buton girişi vardır. Bu yüzden değişikliklere ait bağımsız nedensel katkı yüzdeleri veya eşit giriş altında kesin hızlanma iddiası kurulmaz.
- Her koşu aralıklı trace pencereleri içerir. İstatistikler trace açık/kapalı aralıkların birlikte bulunduğu tüm UART koşusundandır. Ayrı eşlenmiş trace ek yükü deneyi yoktur; SWD okuma ve izleme maliyeti sıfır varsayılmaz.
- S0 için iki sürümde de 6×1000 ms, S5 için 8×500 ms trace alındı; tüm 28 pencere taşmasızdır. İlk başarısız/butonsuz hazırlık pilotları sonuç hesabına alınmadı ve silinmedi.
- p95, sıralı dizinin ceil(0.95×n) elemanıdır (nearest rank). TIM5 farkları unsigned 32 bit hesaplandı. t0 fiziksel parmak hareketi değil kabul edilen kesme zamanıdır; t1 görev switch-in değil olayın kuyruktan alınmasıdır.
- t3 DMA başlatma çağrısının öncesidir; t4 UART TC callback'idir. t4−t3 duvar süresidir, CPU çalışma süresi değildir. Preemption ve callback gecikmesi içerebilir.
- V1'in 20 ms ve V2'nin 10 ms hedefleri farklıdır; adil okunabilmesi için her iki eşik her sürümde hesaplanmıştır. Düşen mesajlar başarılı veya sıfır gecikmeli sayılmamıştır.
- Bu sonuçlar gözlenen koşulara aittir; WCRT/deadline garantisi değildir. Hafta 1'in eski rapor sonuçları yeni ölçüm olarak kullanılmamıştır. S1–S4 ve Trexcope kapsam dışıdır.

Raporlar Markdown olarak kaydedildi. Yeniden hesaplama: Hafta 02 kökünde `projects/v2/interface/.venv/Scripts/python.exe tools/final_reports.py`. Bu betik tüm dört koşunun dump/trace bütünlüğünü doğrular, V1 ve ana raporu, birleşik olay dizinini ve hesap manifestini üretir. V2 raporunun özgün üreticisi `tools/report_v2.py` ayrıca mevcuttur.

- **V1 S0:** [dump](../traces/v1/S0/20261004-151001-observation/dump.json), [oturum](../traces/v1/S0/20261004-151001-observation/session.json), [SystemView kaydı](../traces/v1/S0/20261004-151001-observation/window-02/recording.SVDat), [çözümlenmiş olaylar](../docs/v1-s0-observation-events.csv).
- **V1 S5:** [dump](../traces/v1/S5/20261004-151332-observation/dump.json), [oturum](../traces/v1/S5/20261004-151332-observation/session.json), [SystemView kaydı](../traces/v1/S5/20261004-151332-observation/window-02/recording.SVDat), [çözümlenmiş olaylar](../docs/v1-s5-observation-events.csv).
- **V2 S0:** [dump](../traces/v2/S0/20261003-160814-observation/dump.json), [oturum](../traces/v2/S0/20261003-160814-observation/session.json), [SystemView kaydı](../traces/v2/S0/20261003-160814-observation/window-01/recording.SVDat), [çözümlenmiş olaylar](../docs/s0-observation-events.csv).
- **V2 S5:** [dump](../traces/v2/S5/20261003-161935-observation/dump.json), [oturum](../traces/v2/S5/20261003-161935-observation/session.json), [SystemView kaydı](../traces/v2/S5/20261003-161935-observation/window-01/recording.SVDat), [çözümlenmiş olaylar](../docs/s5-observation-events.csv).
- [V1 ayrıntılı rapor](V1_S0_S5.md), [V2 ayrıntılı rapor](V2_S0_S5.md).
- [V1 kaynak arşivi kimliği](../provenance/v1-source.json), [V2 kaynak kimliği](../provenance/v2-source.json).
- [V1 uygulaması](../projects/v1/firmware/Homework_001/Src/app.c): ortak `tx_q`, tek parça `workload`, FIFO alımı.
- [V2 uygulaması](../projects/v2/firmware/Homework_001/Src/app.c): `btn_tx_q` önce seçimi ve dilimler arası `vTaskDelay(1)`.
- [V2 profil ayarları](../projects/v2/firmware/Homework_001/Inc/app_config.h): QWB, baud ve iş modu.
- [Hesap/kanıt manifesti](report-manifest.json), [birleşik olay dizini](experiment.csv).

Kod incelemesi, entegrasyon ve rapor hesaplamalarında Codex desteği kullanıldı. Sentetik olaylar veya eski Hafta 1 sonuçları bu tablolara eklenmedi.
