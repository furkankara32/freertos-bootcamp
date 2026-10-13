# Hafta 03 - Queue deney ödevi spesifikasyonu

Sürüm: 1.1 | Güncelleme: 12 Ekim 2026 | Hedef: STM32F407G-DISC1 | Durum: A/NORMAL pilotu geçti; tam matris ve SystemView görsel incelemesi bekliyor

## 1. Amaç ve kaynakların statüsü

Bir üretici-tüketici veri yolunda kuyruk kapasitesi ve gönderme bekleme süresinin kabul, başarısızlık, gecikme ve üretici zamanlamasına etkisini kontrollü deneyle açıklamak.

Bu dosya `kaynak/Hafta_3/assets/odev-03.js` içindeki 13 ödev slaytından türetilmiştir. Teknik ayrıntılar `assets/ders-03.js`, `firmware/src/app.c`, `docs/SystemView_Kurulum.md` ve paket README'siyle karşılaştırılmıştır. Paket belgeleri başvuru malzemesidir; içlerindeki çalıştırma, kurulum ve teslim ifadeleri bu hazırlık sırasında otomatik olarak uygulanmamıştır.

**STM32F407VG firmware uyarlaması, kayıt/analiz araçları ve donanımsız testler hazırdır. Karta yükleme ve yeni donanım ölçümü yapılmadı.** `kaynak/` altındaki kayıtlar eğitmenin paketinden gelen örneklerdir. Kendi sonuçların gibi teslim edilmemelidir.

## 2. Başlangıç seçimi

- Zorunlu: Önceki projeden bir üretici-tüketici yolu seç veya izin verilen Hafta 3 referans firmware'ini kullan. Önceki sürümü commit/tag ile koru.
- Seçilen başlangıç: Hafta 3 referans deney uygulaması STM32F407VG'ye uyarlandı. Önceki haftanın STM32F4 HAL/CMSIS/startup kaynakları yeniden kullanıldı; önceki projeler değiştirilmedi. Başlangıç commit'i ve ders paketi SHA256'sı `provenance/baseline.json` içinde kayıtlıdır.
- Referans kullanılırsa kaynağı ve kendi değişikliklerini README'de ayır. Çalışma kopyasını `firmware/` altında tut; `kaynak/Hafta_3/` dizinini başvuru olarak koru.
- Kesin hedef: **STM32F4 Discovery / STM32F407G-DISC1, STM32F407VG**. Bu seçim önceki hafta projeleriyle aynıdır. L476 referansının 80 MHz mutlak sonuçları F407'nin 168 MHz sonuçlarıyla birebir eşdeğer sayılmaz.
- Teslim tarihi ve teslim kanalı pakette kesinleştirilmemiştir; eğitmen duyurusundan alınacaktır.

## 3. Kapsam

Zorunlu kapsam: queue üzerinden aktarım, dönüş değeri kontrolü, A/B/C x normal/yoğun altı koşu, A/yoğun trace kapalı ek koşusu, sayısal analiz, üç işaretli iz görseli, bir sayfa yorum, tekrar üretilebilir kaynak ve 3-5 dakikalık video.

Yeni PC arayüzü, yeni kart, ikinci analiz aracı, mutex/event groups, pointer kuyruğu veya ek optimizasyon zorunlu değildir. SystemView ya da önceden kullanılan bir analiz aracı yeterlidir. Yoğun koşuların üçer tekrarı isteğe bağlıdır.

## 4. Ön çalışma çıktısı

Ölçümden önce aşağıdakileri README veya analiz notuna yaz:

- Üretici kim, tüketici kim, hangi veri aktarılıyor?
- Kuyruğun eleman sayısı ve `sizeof(item)` kaç?
- Struct kopyası mı, pointer mı taşınıyor; veri ömründen kim sorumlu?
- Boş kuyrukta tüketici ve dolu kuyrukta üretici ne yapıyor?
- Başarısız gönderme hangi sayaçta tutuluyor?
- Basit şema: `Producer -> MessageQueue -> Consumer`.
- A/B ve A/C için ölçüm öncesi kabul, gecikme ve bekleme tahmini.

## 5. Deney konfigürasyonu

| Varyant | Kapasite | Gönderme beklemesi | Kontrollü karşılaştırma |
|---|---:|---|---|
| A | 4 mesaj | 0 tick | Başlangıç |
| B | 16 mesaj | 0 tick | A/B: yalnız kapasite |
| C | 4 mesaj | `pdMS_TO_TICKS(20)` | A/C: yalnız bekleme |

Öncelikler, mesaj boyutu, tüketici davranışı ve yük tarifi sabit tutulmalıdır. B/C birlikte kapasite ve timeout değiştirdiğinden tek değişkenli nedensellik kanıtı değildir. Bu adlar Hafta 2 öncelik varyantlarıyla karıştırılmamalıdır.

Uygulanmış F407 ayarları:

| Alan | Değer |
|---|---|
| Hedef | STM32F4 Discovery / STM32F407G-DISC1 / STM32F407VG |
| RTOS | Native FreeRTOS 11.1.0 |
| CPU / tick / ölçüm | HSE 8 MHz -> CPU 168 MHz / 1 kHz / TIM2 1 MHz |
| APB1 / timer | 42 MHz / TIM2 clock 84 MHz, PSC=83 |
| LED | Yeşil LD4 PD12: koşu aktif; kırmızı LD5 PD14: fatal |
| Task öncelikleri | Producer 2, Consumer 1, Console 3 |
| Mesaj | `uint32_t sequence, generated_us, value`; hedefte 12 bayt |
| Gönderim yönü | Back (`xQueueSend`) |
| Consumer receive timeout | `pdMS_TO_TICKS(25)` |
| Servis modeli | `vTaskDelay(pdMS_TO_TICKS(20))` |
| Seri bağlantı | Haricî 3,3 V USB-TTL, USART2 PA2 TX / PA3 RX, ortak GND; 230400 baud, 8N1 |
| Programlama | Yerleşik ST-LINK üzerinden SWD; veri USB-TTL üzerinden |

ST-LINK USB bağlantısının USART2'ye otomatik bağlı olduğu varsayılmaz. Önceki haftalardaki USB-TTL kablolaması kullanılır. PA2 -> adaptör RX, PA3 -> adaptör TX, GND -> GND. Adaptörün 5 V/VCC hattını bağlama. USER butonu kullanılmaz. [ST UM1472 kart kılavuzu](https://www.st.com/resource/en/user_manual/dm00039084.pdf).

20 ms servis modeli CPU'yu 20 ms meşgul etmek değildir. UART yalnız komut ve deney sonrası aktarım içindir. Kendi projende farklı servis süresi gerekiyorsa gerekçesini yaz ve altı temel koşul boyunca sabit tut; sonucu referansla birebir eşdeğer sunma.

### Yük tarifi

- NORMAL: 44 gönderme girişimi, her girişimden sonra 100 ms bekleme.
- BURST: 10 normal + 24 art arda girişim + 10 normal; toplam 44.
- Referans kodda burst mesaj kimlikleri 11-34'tür; 11-33 sonrasında 100 ms ara yoktur, 34 sonrasında normal araya dönülür.
- C'de bloklayan send fiziksel girişim zamanlarını ve burst süresini uzatabilir; bu, politikanın ölçülecek sonucudur.

## 6. Yazılım gereksinimleri

- [x] Queue oluşturma ve task oluşturma başarısızlıkları kontrol ediliyor.
- [x] Her send sonucu `pdPASS` ile kontrol edilip accepted veya failed artırılıyor.
- [x] Consumer yalnız başarılı receive sonrasında mesajı kullanıyor.
- [x] Mesaj kimliği her koşuda 1-44; zaman damgası send öncesinde alınıyor.
- [x] Bloklayan send kritik bölge içinde çağrılmıyor.
- [x] ISR gerekiyorsa task API'leri yerine uygun FromISR API'si kullanılıyor; kesme önceliği port kuralları korunuyor.
- [x] Ölçüm sırasında mesaj başına UART/printf eklenmiyor; sonuçlar bitişte aktarılıyor.
- [x] Yeni koşu önceki üretim ve tüketim bittikten sonra başlıyor; sayaçlar ve kuyruk başlangıç durumu sıfırlanıyor.
- [x] accepted ile consumed, kuyruk boşaldıktan ve son servis tamamlandıktan sonra karşılaştırılıyor.

Kaynak incelemesinde bu yazılım gereksinimleri karşılandı; donanım davranışı henüz ölçülmedi. `firmware/build.py` kaynak manifesti ve build ID üretir. `tools/capture.py` kartın HELLO hedefini ve BUILD kimliğini doğrular; yanlış firmware ile koşuya başlamaz.

## 7. Asgari koşu matrisi

### Senaryo özellikleri — deney sırasında başvuru tablosu

Kapasite, kuyrukta bekleyebilen mesaj sayısıdır; toplam gönderilecek mesaj sayısı değildir. Her senaryoda **44 gönderme girişimi** yapılır. Gönderme beklemesi, kuyruk doluyken `xQueueSend()` çağrısına verilen **en fazla boş yer bekleme süresidir**; her mesajda zorunlu bir gecikme değildir.

| Senaryo | Varyant / yük | Kuyruk kapasitesi | Gönderme beklemesi | Üretim düzeni | Tüketici servis beklemesi | Trace | Dosya kökü |
|---|---|---|---|---|---|---|---|
| 01 | A / NORMAL | 4 mesaj | 0 ms | 44 normal girişim; her girişim sonrası 100 ms | Her alınan mesaj sonrası 20 ms | Açık | `A_NORMAL_trace1` |
| 02 | B / NORMAL | 16 mesaj | 0 ms | 44 normal girişim; her girişim sonrası 100 ms | Her alınan mesaj sonrası 20 ms | Açık | `B_NORMAL_trace1` |
| 03 | C / NORMAL | 4 mesaj | 20 ms | 44 normal girişim; her girişim sonrası 100 ms | Her alınan mesaj sonrası 20 ms | Açık | `C_NORMAL_trace1` |
| 04 | A / BURST | 4 mesaj | 0 ms | 10 normal + 24 art arda + 10 normal | Her alınan mesaj sonrası 20 ms | Açık | `A_BURST_trace1` |
| 05 | B / BURST | 16 mesaj | 0 ms | 10 normal + 24 art arda + 10 normal | Her alınan mesaj sonrası 20 ms | Açık | `B_BURST_trace1` |
| 06 | C / BURST | 4 mesaj | 20 ms | 10 normal + 24 art arda + 10 normal | Her alınan mesaj sonrası 20 ms | Açık | `C_BURST_trace1` |
| 07 | A / BURST | 4 mesaj | 0 ms | 10 normal + 24 art arda + 10 normal | Her alınan mesaj sonrası 20 ms | Kapalı | `A_BURST_trace0` |

Ortak ayarlar ve tabloyu okuma:

- **NORMAL:** Her gönderme girişiminden sonra `vTaskDelay(100 ms)` uygulanır. Bu nedenle zaman damgaları arasındaki fark yaklaşık 100 ms'dir; gönderme çağrısı ve zamanlama ek süre oluşturabilir.
- **BURST:** Mesaj 1–10 normal, 11–34 art arda, 35–44 normaldir. Mesaj 11–33 sonrasında 100 ms bekleme uygulanmaz; 34 sonrasında yeniden uygulanır. Art arda gönderim sıfır işlem süresi anlamına gelmez. C'de kuyruk dolunca gönderici bekleyebildiği için burst daha uzun sürebilir.
- **0 ms gönderme beklemesi:** Kuyruk doluysa boş yer beklenmeden başarısız dönülür. CSV'de `accepted=0` görülür. Çağrının kendisi yine mikrosaniye düzeyinde süre alır.
- **20 ms gönderme beklemesi:** Yer varsa hemen eklenir; doluysa en fazla 20 tick (1 kHz tick ile nominal 20 ms) boş yer beklenir. Yer açılmazsa başarısız döner. CSV'deki `send_call_us`, çağrı/izleme ve yeniden çalıştırılma sürelerini de içerdiğinden tam 20.000 µs sınırı olarak yorumlanmaz.
- **Tüketici:** Bütün senaryolarda kuyruktan mesaj bekleme timeout'u 25 ms'dir. Başarılı alımdan sonra 20 ms servis beklemesi uygulanır. Bunlar göndericinin beklemesinden farklıdır; kuyrukta mesaj varsa alım için 25 ms beklenmez. Servis beklemesi `generation_to_receive_us` ölçümüne dahil değildir.
- **Sabit tutulanlar:** Producer önceliği 2, Consumer önceliği 1, Console önceliği 3; mesaj boyutu 12 bayt. Trace açıkken nominal 200 ms pencere NORMAL'de ilk mesajda, BURST'te 11. mesajda başlar. CSV her durumda 44 girişimin tamamını kapsar.

### Sonuçları karşılaştırırken

| Karşılaştırma | Değişen özellik | CSV / SystemView üzerinde kontrol |
|---|---|---|
| 01 / 02 ve 04 / 05 (A / B) | Kapasite: 4 → 16; gönderme beklemesi 0 ms | Kabul/ret sayıları ve tüketiciye ulaşma gecikmesi. Daha büyük kuyruk daha fazla mesaj tutabilir; gecikmeyi mutlaka azaltmaz. |
| 01 / 03 ve 04 / 06 (A / C) | Gönderme beklemesi: 0 → 20 ms; kapasite 4 | Kabul/ret sayıları, `send_call_us`, üretim zamanlarının açılması ve izde göndericinin bloklanması. |
| 01 / 04, 02 / 05, 03 / 06 | NORMAL → BURST; varyant sabit | Özellikle mesaj 11–34 arasında ret, kuyruk birikmesi ve gecikme değişimi. |
| 04 / 07 | Trace açık → kapalı; A/BURST sabit | Gönderme ve ulaşma süreleri ile kabul/ret sayıları üzerinden kayıt etkisi. Trace kapalı koşuda SVDat oluşmaz. |

Bunlar inceleme yönleridir; kesin kabul/ret sayıları veya gecikme sonuçları önceden varsayılmaz, gerçek kayıttan okunur. B ile C karşılaştırmasında hem kapasite hem gönderme beklemesi değiştiği için fark tek bir özelliğe bağlanmaz.

Senaryo seçimi için `python tools/capture.py --port COM5 --variant A --load NORMAL` komutundaki varyantı ve yükü tablodan seç. Yalnız senaryo 07 için `--no-trace` ekle. Portu bağlı adaptöre göre belirle.

Dosyalar `measurements/hardware` altında tabloda belirtilen sabit kökle `.csv`, `.txt`, `.json` ve trace açıkken `.SVDat` olarak saklanır. Aynı senaryonun başarılı tekrarı önceki dosyaların üzerine yazar. Gerçek cihaz `run_id` değeri dosya içeriğinde ayrıca korunur; tablodaki senaryo numarasıyla aynı olmak zorunda değildir.

## 8. Ölçüm sözlüğü ve hesaplamalar

| Ölçüm | Anlam / kural |
|---|---|
| attempted | Toplam send girişimi; referansta 44 |
| accepted | Queue'nun kabul ettiği girişim sayısı |
| failed | Başarısız girişim sayısı; bu referansta yeniden deneme yok |
| consumed | Servisi tamamlanan mesaj sayısı; yalnız receive sayısı değildir |
| send_call_us | Send çevresindeki duvar saati; bloklanma, preemption ve yakındaki trace maliyeti içerebilir |
| generation_to_receive_us | Üretimden başarılı receive'e; C'de enqueue öncesi bekleme dahil |
| received | CSV satırında receive gerçekleşti mi? |

Her koşu için sayaçları, başarılı mesajların send ve generation-to-receive ortalama/maksimumlarını raporla. Önerilen ek alanlar: bütün girişimlerin send ortalama/maksimumu ve başarısızların ayrı send istatistiği. Böylece timeout bedeli başarılılar grubunda gizlenmez. Kullanılan alt kümeyi ve örnek sayısını tablo başlığında belirt.

- Başarılı send kümesi: `accepted == 1` olan satırlar.
- Gecikme kümesi: `received == 1` ve gecikme alanı dolu satırlar.
- Ortalama = seçilen sürelerin toplamı / seçilen örnek sayısı.
- Başarısızlık oranı = `failed / attempted * 100`.
- Boş gecikme alanını sıfıra dönüştürme. Örnek yoksa ortalama/maksimum `N/A` yaz.
- Kontrol: `attempted == accepted + failed`; drain ve servis sonunda `accepted == consumed`.
- CSV'deki received toplamı da tamamlanmış koşuda accepted ile uyumlu olmalıdır.
- Ham protokolde başarısız mesajın latency alanı 0 olabilir; CSV üretirken received bayrağıyla boş bırakılır. Bu sıfırı gerçek gecikme sanma.

Önerilen sonuç tablosu:

`run_id | varyant | yük | trace | attempted | accepted | failed | consumed | n_success | mean/max_send_success_us | n_received | mean/max_latency_us | trace_drops | açıklama`

Sonuçlar henüz ölçülmedi. Bu dosyada hedef kabul sayısı veya uydurulmuş süre verilmez.

## 9. Trace toplama ve geçerlilik

13 Ekim UART kuralı: `#RX` koşu başlangıcından rapora kadar artışı gösterir ve sıfır olmalıdır. `#RX_BASE` önceki hataları, `#RX_TOTAL` birikmiş toplamı korur; parser farkı doğrular. Eski firmware kayıtlarının sayaç kapsamı farklıdır; yeni build ile aynı matriste karıştırılmaz.

Referans: 32768 bayt RAM, nominal 200 ms pencere. NORMAL ilk mesaj çevresinde, BURST 11. mesajdan önce başlar. CSV tüm 44 girişimi kapsar; trace tüm koşuyu kapsamaz.

1. Koşu tamamlanana kadar bekle.
2. CSV, ham seri ve metadata'yı kaydet.
3. Trace açıksa son izi karttan al, `.SVDat` olarak kaydet ve SystemView'de File > Open ile aç.
4. Bir sonraki koşudan önce izi mutlaka indir; yeni koşu karttaki eski izi değiştirir.
5. run_id, byte sayısı, FNV-1a checksum, drops ve stop_reason alanlarını kontrol et.
6. `drops > 0` ise izi eksik olarak işaretle; daha kısa pencereyle tekrar alırsan değişikliği raporla. Checksum bozuk dosyayı geçerli kanıt olarak kullanma.

stop_reason: 1 süre doldu, 2 buffer sınırına yaklaşma, 0 diğer durdurma. Buffer nedeniyle erken biten kaydın kapsadığı aralığı açıkça belirt. DWT ve TIM2 mutlak zamanlarını birbirinden çıkarma. Trace OFF yalnız kayıt etkinliğini kapatır; trace hook kodunu binary'den kaldırmaz ve TIM2/CSV ölçümleri devam eder.

## 10. Zorunlu üç iz görseli

Her görselde koşu kimliği, mesaj kimliği ve okunur zaman aralığı bulunmalıdır.

1. A/BURST: Dolu kuyrukta en az bir başarısız send olayı; SEND_BEGIN ve SEND_FAIL bağlantısı.
2. B/BURST: A'ya göre kabul ve bekleme farkının iz ve CSV ile açıklanması.
3. C/BURST: Producer'ın queue üzerinde Blocked olması ve Consumer'ın ilerlemesi.

SEND_BEGIN -> SEND_OK/SEND_FAIL -> varsa RECEIVE -> DONE olaylarını aynı run/id ile eşleştir. FreeRTOS API olaylarını ve W3 işaretlerini birlikte oku. Olay görünmüyorsa pencereyi, yükü ve varsayımı kontrol et; beklenen sonucu olmuş gibi yazma.

## 11. Analiz ve anlatım

Bir sayfalık yorum şu beş soruyu yanıtlamalıdır:

1. B daha çok mesaj kabul etti mi, gecikme bedeli ne oldu?
2. C'de üretici ne kadar bekledi, diğer üretici işleri nasıl etkilenebilir?
3. A/BURST trace açık-kapalı farkı nedir?
4. Kendi uygulaman için hangi politikayı hangi gerekçeyle seçersin?
5. Ölçüm hangi durumları kapsamıyor?

Gözlenen maksimum hard real-time üst sınırı değildir. Tek koşudan istatistiksel kesinlik çıkarma. Hazır paket kayıtlarını yalnız açıkça etiketlenmiş başvuru karşılaştırması olarak kullan. Ölçümün beklentiye uymaması tek başına başarısızlık değildir; neden-sonuç açıklaması önemlidir.

## 12. Teslim yapısı ve kabul kontrolü

```text
hafta-03/
  Hafta_03_Konu_Anlatimi.pdf   # öğrenme rehberi, bu hazırlığın çıktısı
  spec.md                    # bu dosya
  kaynak/Hafta_3/             # açılmış orijinal ders paketi
  firmware/                  # STM32F407VG çalışma projesi + build.py
  measurements/              # kendi 7 koşunun CSV + ham seri + metadata'sı
  traces/                    # kendi özgün iz dosyaların
  analysis/                  # karşılaştırma tablosu, 3 görsel, 1 sayfa yorum
  README.md                  # kart, sürümler, komutlar, commit, kaynak ayrımı
  ai-usage.md                # alınan destek ve nasıl doğrulandığı
```

Firmware, yedi gerçek ölçüm kaydı ve CSV karşılaştırma raporu hazırdır. Sonuç yorumu `analysis/yorum.md`, sayısal tablolar `analysis/comparison.csv` ve `analysis/comparison.md` içindedir. Trace ekran görüntüleri ve video ayrıca tamamlanmalıdır. PDF üretim kaynakları `docs/` ve `tools/` altında saklanır.

- [x] Kaynak ve proje dosyalarıyla build yeniden üretilebilir; yalnız binary teslim edilmiyor.
- [x] Yedi koşunun konfigürasyonu ve firmware build kimliği belli; Git commit kimliği yükleme sonrasında kaydedilecek.
- [x] Sayaç eşitlikleri ve eksik gecikme alanları doğrulandı.
- [x] Altı trace açık koşunun özgün izleri ve geçerlilik bilgileri var.
- [ ] Üç görsel ve bir sayfalık yorum tamamlandı; A/B ve A/C ayrı tartışıldı.
- [ ] 3-5 dakikalık videoda en az bir mesaj iz üzerinden açıklandı.
- [ ] `ai-usage.md` içinde bu öğrenme rehberi/spec hazırlığı ve sonraki AI desteği açıklandı.
- [ ] Kod GitHub'da; video ve bağlantı mevcut kurs teslim kanalına verildi.
- [ ] Son tarih eğitmen duyurusundan doğrulandı.

Puanlama: Queue ve dönüş değerleri 30; kontrollü deney ve ölçüm 30; izde neden-sonuç 25; tekrar üretilebilir teslim 15. Toplam 100.

## 13. Önerilen çalışma sırası

1. PDF bölüm 1-8: Kavramlar, API ve zamanlama. Kâğıt üzerinde örnekleri çöz.
2. PDF bölüm 9-12: Kod, ölçüm ve trace. Hazır kayıtları yalnız öğrenmek için incele.
3. PDF bölüm 13: Kontrol sorularını cevap anahtarına bakmadan yanıtla.
4. Proje yolunu seç, önceki sürümü koru, kart/sürüm bilgilerini yaz.
5. Bir NORMAL denemesiyle kayıt zincirini doğrula; ardından yedi koşuyu uygula.
6. Tablo, görseller, yorum ve videoyu hazırla; kabul kontrolünü tamamla.

## 14. Donanımsız tamamlanan çalışma ve sonraki kapı

- ARM GCC ile Release ve Debug derlemeleri, ELF/HEX/BIN, map, build kimliği ve kaynak manifesti üretildi.
- Protokol, parçalı seri okuma, sayaç, CRC yerine kullanılan FNV-1a, kimlik ve hata yolları masaüstünde test edildi. Test verileri sentetiktir ve donanım ölçümü değildir.
- `tools/run_matrix.py` yedi koşuyu sırayla kaydeder; `tools/analyze.py` tam oturumu doğrulayıp sayısal raporu üretir.
- `docs/DONANIM_TESTI.md`, `analysis/yorum.md` ve `analysis/video-plani.md` sonraki uygulama adımlarını tanımlar.
- PDF, özgün L476 ders referansını anlatır. Kendi proje bağlantın ve build komutları için bu spec ve README esastır.
- Kart bağlandığında flash doğrulaması, yedi gerçek koşu, üç SystemView görseli ve videoyla donanım/teslim kapısı kapanır. Şimdilik bunlar tamamlandı olarak işaretlenmez.

## 15. İlk kart pilotu

12 Ekim 2026: Release programlama/read-back başarılı. COM5 üzerinden tek A/NORMAL koşusu: 44 kabul, 0 başarısız, 44 tamamlanan; UART hata/drop=0, SEGGER drop=0. Tam matris çalıştırılmadı. GUI olay incelemesi henüz doğrulanmadı. Ayrıntılar `docs/PILOT_TESTI.md`. Önceki hazırlık bölümlerinin donanım yapılmadı ifadeleri hazırlık aşamasına aittir.

## Kayıt dosyası davranışı (13 Ekim 2026)

- CSV UTF-8 BOM ve noktalı virgül ayıracıyla Türkçe Excel içinde ayrı sütunlarda açılmalıdır.
- Her varyant/yük/trace seçimi sabit dosya adı kullanır: `A_NORMAL_trace1.*` gibi. Başarılı tekrar önceki kayıt takımını değiştirir; tarihli kopya biriktirilmez.
- Başarısız tekrar önceki başarılı ölçümü korur, yalnız son hata dosyaları tutulur. Yeni başarılı koşu hata dosyalarını kaldırır.
- Yedi koşuluk matris aynı `measurements/hardware` klasörünü ve `session.json` indeksini yeniler.
