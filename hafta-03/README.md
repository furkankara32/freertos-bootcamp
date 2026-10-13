# Hafta 03 - STM32F4 Discovery Queue laboratuvarı

13 Ekim güncellemesi: UART geçmiş sayaçları ile koşu sayaçları ayrıldı; yeni firmware karta yüklendi ve A/NORMAL kontrolü geçti. Yeni senaryoları bu firmware ile al. [Düzeltme ve ölçüm kanıtı](docs/UART_SAYAC_DUZELTMESI.md).

**Güncel durum: Firmware karta yüklendi ve bir A/NORMAL pilotu başarılı. 44/44 mesaj, 0 hata ve kayıpsız SEGGER aktarımı. SystemView GUI incelemesi ve diğer senaryolar bekliyor. [Pilot raporu](docs/PILOT_TESTI.md).**

Hedef STM32F407G-DISC1 / STM32F407VG. Native FreeRTOS 11.1.0, HSE 8 MHz -> CPU 168 MHz, tick 1 kHz, TIM2 1 MHz. A/B/C bu haftanın queue kapasitesi/bekleme varyantlarıdır. Önceki haftanın uygulama protokolü kullanılmaz.

## Veri yolu ve deney

`Producer P2 -> MessageQueue -> Consumer P1`; Console P3 komutları ve koşu sonrası dışa aktarımı yönetir. Mesaj, sequence/generated_us/value alanlarından oluşan 12 bayt struct kopyasıdır. Queue doluyken A/B beklemeden başarısız döner; C en çok 20 ms tick bekleme bütçesiyle yer bekler. Boş queue'da consumer 25 ms receive beklemesi kullanır. Başarılı receive sonrası 20 ms `vTaskDelay` dış servis süresini modeller. Başarısız send failed sayacına gider ve tekrar denenmez.

| Varyant | Kapasite | Send beklemesi |
|---|---:|---|
| A | 4 | 0 tick |
| B | 16 | 0 tick |
| C | 4 | 20 ms -> tick |

NORMAL 44 girişim, her girişimden sonra 100 ms bekleme. BURST 10 normal + 24 ardışık girişim + 10 normal. Her koşu 44 girişimdir. C'nin bloklanması burst süresini uzatabilir. A/B yalnız kapasiteyi, A/C yalnız bekleme politikasını değiştirir. Trace kapalı ek koşu A/BURST'tür. Her iki queue başlangıçta ayrıldığından bu binary içinde varyant değiştirmek RAM tahsisini değiştirmez.

Ön tahminler: Normal yükte consumer'ın yetişmesi; A/yoğun'da daha fazla başarısızlık; B/yoğun'da kabul artışıyla gecikme bedeli; C/yoğun'da üreticinin beklemesi. Bunlar ölçüm sonucu değildir.

## Donanımsız kullanım

Komutları `D:\freertos-bootcamp\hafta-03` klasöründe çalıştır:

```powershell
python firmware/build.py --config Release
python firmware/build.py --config Debug
python -m unittest discover -s tests -v
```

Build aracı PATH'teki ARM GCC'yi veya `C:\ST` altındaki CubeIDE toolchain'ini bulur. Alternatif: `--toolchain "C:\...\tools\bin"`. Derleme sırasında indirme, karta bağlanma veya flash yapılmaz. Yerel vendor kaynakları kullanılır. `firmware/build/Release` içinde `week3_f407.elf`, `.hex`, `.bin`, `.map`, `build.json`, `source-manifest.json` ve `build.log` oluşur. Debug ayrı klasördedir. Bu proje CubeMX `.ioc` üretimi değildir; tekrar üretilebilir derleme girişi `build.py`'dir. CubeIDE debugger'da bu ELF kullanılabilir.

Testler sentetik protokol verilerini geçici dizinlerde kullanır. RTOS zamanlamasını veya gerçek kartı simüle ettikleri iddia edilmez. Ayrıntı: [doğrulama raporu](docs/DOGRULAMA.md).

## Kart bağlandığında

Önce [donanım testi rehberi](docs/DONANIM_TESTI.md) ile hedefi ve kabloları kontrol et; derlenen HEX'i STM32CubeProgrammer veya ELF'i CubeIDE/ST-LINK ile yükle ve doğrula. A/NORMAL pilotu uygulanmıştır; ayrıntılar `docs/UART_SAYAC_DUZELTMESI.md` içindedir.

Seri veri haricî **3,3 V USB-TTL** üzerinden: PA2 -> RX, PA3 -> TX, GND -> GND. ST-LINK programlama içindir; USART2'nin ST-LINK USB'ye doğrudan bağlı olduğu varsayılmaz. Adaptör VCC/5 V hattını bağlama. 230400 baud, 8N1, flow control yok. Önceki COM5 yalnız tarihsel örnektir; portu o gün belirle.

```powershell
python -m pip install -r requirements.txt
python -m serial.tools.list_ports
# Yalnız bağlantı kontrolü; deney başlatmaz:
python tools/capture.py --port COM5 --check-only
# COM5'i kendi portunla değiştir:
python tools/capture.py --port COM5 --variant A --load NORMAL
python tools/run_matrix.py --port COM5
python tools/analyze.py measurements/hardware
```

Kayıtlar `measurements/hardware` altında sabit senaryo adlarıyla tutulur; örneğin `A_NORMAL_trace1.csv`. Aynı varyant/yük/trace seçimi yeniden çalıştırıldığında önceki başarılı kayıt değiştirilir; tarihli kopya veya oturum klasörü oluşturulmaz. Araç her koşunun özgün izini almadan sonrakine geçmez. Hedef MCU, saat, baud, firmware build ID, 44 satır, sayaçlar, stack, RX hataları ve FNV-1a doğrulanır. Kaynaklar build'den sonra değiştiyse yeniden derleme istenir. Hata durumunda ham/eksik kayıt korunur ve matris durur; otomatik yeniden koşular sonuçlara karışmaz.

Koşu çıktıları aynı klasörde CSV, TXT, JSON ve trace açıkken SVDat olarak saklanır. CSV dosyaları Türkçe Excel için UTF-8 BOM ve noktalı virgül ayıracı kullanır; özet raporda ondalık ayıracı virgüldür. Yeniden kayıt almadan önce ilgili dosyayı Excel/SystemView içinde kapat. Başarısız deneme önceki başarılı kaydı korur; son hatanın `.failed.txt` ve `.failed.json` dosyaları yenilenir, sonraki başarılı kayıtta kaldırılır. Matris yeniden başlatıldığında `session.json` tamamlanmamış olarak sıfırlanır. Özgün SVDat'ları oturumla birlikte koru; `traces/README.md` bu dizinlere indeks verir. `analyze.py` tam yedi koşuyu tekrar doğrular, `analysis/comparison.csv`, `comparison.md` ve `validated-runs.json` üretir. Başarısız mesajın gecikmesi boş bırakılır; ortalamaya sıfır eklenmez.

SystemView'de File > Open ile SVDat açılır. Bu bir RAM snapshot'ıdır; J-Link canlı bağlantı veya UART Recorder kullanılmaz. 200 ms pencere tüm koşuyu kapsamaz. Trace OFF hook kodunu binary'den çıkarmaz; yalnız kaydı durdurur.

## Teslim ve kaynak ayrımı

- [spec.md](spec.md): gereksinimler ve kabul listesi.
- [analysis/yorum.md](analysis/yorum.md): yedi gerçek koşunun sonuç raporu; kapasite, bekleme, trace etkisi ve politika seçimi.
- [analysis/video-plani.md](analysis/video-plani.md): 3-5 dakikalık anlatım planı.
- [ai-usage.md](ai-usage.md): alınan destek ve doğrulama sınırı.
- `kaynak/Hafta_3`: özgün L476 ders paketi ve eğitmen kayıtları; bizim donanım ölçümlerimiz değildir.
- `firmware/src/app.c`, `app_trace.c`: ders referansından uyarlama; F407 hedefi, LED ve BUILD kimliği eklendi; tek ISR çıkış kaydı korundu.
- `firmware/vendor/Drivers`, startup/system dosyaları: Hafta 1 F407 kaynaklarından; FreeRTOS 11.1.0 ve SEGGER kaynakları Hafta 3 paketinden. Lisanslar vendor içinde korunur.
- `provenance/baseline.json`: başlangıç Git commit'i ve ders arşivi SHA256. Mevcut diğer hafta değişiklikleri korunmuştur.

Konu anlatımı PDF'si L476 ders referansını açıklar. Bu projenin F407 bağlantı ve saat ayarları için README/spec geçerlidir. Yedi gerçek koşu ve CSV sonuç raporu tamamlandı. Üç SystemView görseli ve video ayrıca tamamlanmalıdır. GitHub'a yükleme ve kursa gönderme henüz yapılmadı; son tarih eğitmen duyurusundan alınır.
