# Hafta 3 — ST-LINK ile SystemView ve canlı anlatım

Bu paket `Hafta_2/firmware` board/HAL/FreeRTOS altyapısından türetilen ayrı bir **RTOS_Hafta_3_L476RG** projesidir. Hafta 2 dosyaları değiştirilmedi. Hafta 3 uygulaması kontrollü queue deneyidir; eski buton/telemetri A/B/C protokolü bu firmware'de kullanılmaz. Önceki app.c, `Hafta2_app_reference.c.txt` dosyasında başvuru için saklandı.

## 1. Ne indireceksiniz?

[SEGGER SystemView masaüstü uygulamasını resmî sayfadan indirin](https://www.segger.com/downloads/systemview/). Kurulum ve kullanım koşulları SEGGER'e aittir. Hedef tarafı SystemView ve RTT kaynakları pakette lisanslarıyla bulunur; firmware derlemek için SystemView masaüstü uygulamasının kurulması gerekmez.

Bu paketin bağlantısı **RAM single-shot → ST-LINK Virtual COM Port → .SVDat → SystemView** şeklindedir. SystemView'in J-Link canlı recorder bağlantısını veya UART Recorder modunu seçmeyin. USB üzerinden taşınan, deney bittikten sonra alınan bir dosyadır. ST-LINK firmware'ini J-Link'e dönüştürmeyin.

## 2. Kart ve bağlantı

| Ayar | Değer |
|---|---|
| Kart | NUCLEO-L476RG / STM32L476RGT6 |
| Programlama | ST-LINK, SWD |
| Komut / sonuç portu | ST-LINK VCP, USART2 PA2/PA3 |
| Seri ayarlar | **230400 baud, 8N1**, flow control yok |
| CPU / ölçüm | 80 MHz / TIM2 1 MHz |
| FreeRTOS | 11.1.0, tick 1 kHz |
| Yük | Yazılımla oluşturulur; B1'e basmak gerekmez |
| LED | LD2 deney boyunca yanar |

5 Ekim 2026 doğrulamasında kart COM4 üzerinde görüldü. Başka bilgisayarda port değişebilir. Tek portu aynı anda yalnız bir program açabilir; CubeIDE seri terminali ve diğer terminalleri kapatın. CubeIDE SWD debug bağlantısı ile VCP ayrı arayüzlerdir; normal çalışmada breakpoint'e takılı kalmayın.

## 3. CubeIDE ile derleme ve yükleme

1. File → Import → General → Existing Projects into Workspace.
2. Kök klasör olarak bu paketteki `firmware` klasörünü seçin.
3. Proje adı **RTOS_Hafta_3_L476RG** olmalıdır.
4. Debug konfigürasyonunu seçip Build Project çalıştırın.
5. Debug As → STM32 C/C++ Application; ST-LINK/SWD ve STM32L476RG hedefini seçin.
6. Main'de durursa Resume yapın. Firmware işlemeye devam etmelidir.

Bu proje elle sürdürülen native CubeIDE projesidir; CubeMX .ioc projesi değildir. `vendor`, `include`, `src`, `.project` ve `.cproject` birlikte taşınmalıdır. Linked klasöründeki dosyalar vendor altındaki proje içi bağlantılardır.

Alternatif derleme:

```powershell
./firmware/build_week3.ps1
# Veya kurulu CubeIDE ile:
./firmware/build_cubeide.ps1
```

CMake yolu Arm GCC, CMake ve Ninja kullanır. `-ArmBin` parametresiyle Arm GCC bin dizini belirtilebilir. Hazır CMake çıktıları `firmware/prebuilt` altındadır; ölçülen sürümün hash'i doğrulama raporundadır.

## 4. Derste kayıt alma

1. `Baslat.ps1` çalıştırın; `http://localhost:8766/` açılır. Alternatif: `python tools/serve.py`.
2. Chrome/Edge'de **Kayıt masası** bağlantısını açın.
3. **Seri porta bağlan** → ST-LINK Virtual COM Port seçin.
4. “Hafta 3 firmware doğrulandı” yazısını bekleyin.
5. A + Normal seçip **Deneyi çalıştır** düğmesine basın. Yaklaşık 4–5 saniye sürer.
6. Bitişte sayaçları kontrol edin; CSV, ham oturum ve metadata'yı indirin.
7. **Son izi karttan al** düğmesine basın. Byte sayısı ve FNV-1a checksum kontrol edilir.
8. Sonuç kartındaki **.SVDat indir** düğmesini kullanın.
9. SystemView'de **File → Open** ile bu dosyayı açın.
10. A/Yoğun, B/Yoğun, C/Yoğun koşullarını ayrı ayrı çalıştırın. **Yeni koşudan önce önceki izi indirin.** Kart yalnız son izi tutar; tarayıcı sonuçları sekme açıkken korur.

Sunumlar doğrudan dosyadan, internet olmadan da açılır. Seri arayüz sorunlarında localhost yöntemi tercih edilir. Sunum kısayolları: oklar, N (notlar), G (içindekiler), F (tam ekran). Kontroller odaktayken alt gezinme düğmeleri kullanılabilir.

## 5. SystemView'de anlatım sırası

1. Task adları: **Producer**, **Consumer**, **Console** ve Idle görünümünü bulun.
2. Events ve Timeline pencerelerini birlikte açın. Zaman ölçeğini birkaç milisaniyelik aralığa yakınlaştırın.
3. **W3 / RUN** olayını bulun. `run` değeri CSV oturumuyla eşleşmelidir.
4. Bir mesajın `id` değerini seçin: SEND_BEGIN → SEND_OK veya SEND_FAIL → varsa RECEIVE → DONE.
5. A/Yoğun'da hızlı başarısız gönderimleri, C/Yoğun'da üreticinin queue üzerinde beklemesini gösterin.
6. B/Yoğun'da kabul edilen mesaj sayısını ve CSV'deki gecikmeleri A ile karşılaştırın. 200 ms pencere bütün B kuyruğunun boşalmasını kapsamayabilir.

Kullanıcı olay açıklamaları firmware tarafından kayda eklenir. FreeRTOS API olay adlarının doğru çözülmesi için kullandığınız SystemView sürümünün FreeRTOS 11 desteğini kontrol edin. İşletim sistemi/API açıklaması bulunamazsa SystemView kurulumunun Description kaynaklarına bakın; kullanıcı olay kimliklerini isim görmeden yorumlamayın.

## 6. Kayıt penceresi ve anlamı

- RAM tamponu **32768 bayt**, nominal pencere **200 ms**.
- Normal yükte ilk mesajdan, yoğun yükte **11. mesajdan önce** kayıt başlar.
- Task listesi, sistem tanımı ve W3 modülü her kaydın başında tekrar gönderilir.
- DWT CYCCNT, CPU frekansı olan 80 MHz ile trace timestamp üretir. TIM2 ölçümleri 1 MHz'dir. İki saatin mutlak değerlerini birbirinden çıkarmayın.
- SysTick giriş/çıkış olaylarını FreeRTOS ARM_CM4F portu zaten üretir; ikinci kez eklenmedi.
- USART2 ISR girişi ve tek çıkışı board.c içinde kaydedilir. Priority 6, RTT BASEPRI kilidi 0x50 ile korunur.
- Pencere bitince kayıt durur; buffer az kaldığında erken durma kontrolü de vardır. Metadata stop_reason: **1 = süre**, **2 = buffer sınırına yaklaşma**, **0 = diğer durdurma**.
- `drops > 0` eksik izdir. Arayüz bunu görünür biçimde etiketler. Buffer kontrolü kayıp ihtimalini matematiksel olarak ortadan kaldırmaz.
- CSV bütün **44** mesajı kapsar. Trace kısa penceredir; pencerede olmayan olay yok sayılmaz.
- `TRACE OFF`, kaydı kapatır; trace hook kodunu binary'den çıkarmaz. İz açık/kapalı deneyi kayıt etkinliğinin ek yükünü karşılaştırır.

## 7. Deneyin gerçek davranışı

Mesaj `sequence`, `generated_us`, `value` olmak üzere 12 bayttır. A: 4 eleman/0 tick; B: 16 eleman/0 tick; C: 4 eleman/20 ms. Her iki kuyruk başlangıçta oluşturulur; koşu başında boş olan seçilir. Üretici P2, tüketici P1, konsol P3'tür.

Normal yük: 44 mesaj, her girişim sonrasında 100 ms bekleme. Yoğun yük: 10 normal + 24 art arda gönderme girişimi + 10 normal. Bloklayan gönderim C'nin burst süresini uzatabilir. `vTaskDelay(20 ms)` tüketicinin dış servis beklemesini **modeller**; 20 ms CPU tüketimi değildir. UART'tan mesaj başına trafik üretilmez; sonuçlar deney bittikten sonra çıkarılır. Bu nedenle bu laboratuvar Hafta 2 UART hattının performans testi değildir.

`send_call_us` duvar saati süresidir; trace işaretleri ve CPU beklemesi dahil olabilir. `generation_to_receive_us` üretimden consumer'ın mesajı aldığı ana kadardır; C'de queue'ya girmeden önceki bekleme de dahildir. Saf kuyrukta kalış veya tamamlanma süresi olarak adlandırmayın.

## 8. Komut satırı alternatifi

```powershell
python -m pip install pyserial
python tools/capture.py --port COM4 --variant A --load BURST
python tools/capture.py --port COM4 --variant A --load BURST --no-trace
```

Portu tarayıcıdan ayırın. Araç gerçek veri için sayaç, sıra ve checksum kontrolleri yapar; ham oturum, CSV, metadata ve .SVDat üretir. Başarısız olayın latency alanı boş bırakılır.

## 9. Sorun giderme ve B planı

| Belirti | Kontrol |
|---|---|
| Bağlantı yok | Doğru USB soketi, COM portu, 230400 baud ve başka terminal |
| Firmware eşleşmiyor | Hafta 3 ELF yüklü mü? Eski Hafta 2 protokolü kabul edilmez |
| Yanıt zaman aşımı | CPU breakpoint'te mi? Reset/Resume ardından tekrar bağlanın |
| İz yok | İz açık mı? Koşu tamamlandı mı? Yeni koşu önceki buffer'ı sıfırladı mı? |
| Checksum hatası | Aktarımı yeniden alın; reset olduysa yeni koşu gerekir |
| Olaylar eksik | drops ve stop_reason alanlarını, pencerenin sınırlarını kontrol edin |
| Görev adları yok | Dosyanın başlangıcı eksik mi? SystemView sürümü/Description uyumu |

Canlı bağlantı düzelmiyorsa `measurements/hardware` içindeki gerçek .SVDat dosyalarını açın. Hazır kaydı canlı deney olarak sunmayın. C/Yoğun kaydı bloklanmayı anlatmak için, A ve B ise kapasite karşılaştırması için uygundur.

## 10. Kaynaklar

- [SEGGER FreeRTOS entegrasyonu](https://kb.segger.com/FreeRTOS_with_SystemView)
- [SystemView User Guide](https://doc.segger.com/UM08027_SystemView.html) — Single-shot recording, dış debugger ile buffer dosyası alma
- [SEGGER SystemView hedef kaynakları](https://github.com/SEGGERMicro/SystemView)
- [SEGGER RTT](https://github.com/SEGGERMicro/RTT)
- [FreeRTOS Queue açıklaması](https://www.freertos.org/Documentation/02-Kernel/02-Kernel-features/02-Queues-mutexes-and-semaphores/01-Queues)

Kaynak kontrolü: 5 Ekim 2026. Sabit commit ve arşiv SHA256 değerleri `firmware/segger.lock.json` dosyasında; orijinal lisanslar vendor klasörlerinde korunur.
