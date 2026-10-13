# FreeRTOS Bootcamp — Hafta 3

**Konu:** Task'lar arası veri aktarımı, Queue, timeout ve kontrollü yük. 100 dakika ders + 20 dakika mola. Ders/teslim tarihi eğitmen tarafından duyurulur.

Başlangıç: **index.html**. Sunumlar çevrimdışı açılır; `assets` klasörünü yanlarında tutun.

| Dosya | İçerik |
|---|---|
| ders-03.html | 30 slayt, animasyonlu Front/Back/Receive/Peek, timeout ve kopyalama görselleri, eğitmen notları |
| odev-03.html | 13 slayt, 7 deneylik ödev ve puanlama |
| interface/index.html | Gerçek kart deneyini yönetme, CSV ve .SVDat alma |
| docs/SystemView_Kurulum.html | ST-LINK, CubeIDE, kayıt alma ve anlatım rehberi |
| docs/Dogrulama.html | Gerçek testler ve sınırlar |
| firmware/ | FreeRTOS 11.1.0, STM32L476RG, SEGGER SystemView entegre proje |
| firmware/prebuilt/ | Ölçülen CMake derlemesinin ELF/HEX/BIN dosyaları |
| measurements/hardware/ | Gerçek kartta alınmış CSV, ham UART, metadata ve .SVDat |
| tools/capture.py | Python/pyserial ile doğrulanmış kayıt alma |
| tools/serve.py | Yalnız localhost üzerinde çalışan arayüz sunucusu |

## Hızlı kullanım

1. SystemView masaüstü uygulamasını SEGGER'in resmî sitesinden indirin.
2. CubeIDE'ye `firmware` klasörünü import edin; **RTOS_Hafta_3_L476RG** projesini derleyin ve ST-LINK ile yükleyin.
3. CPU'yu Resume yapın. `Baslat.ps1` → Chrome/Edge → Kayıt masası.
4. VCP portuna bağlanın; varyant ve yükü seçip deneyi çalıştırın.
5. Son izi karttan alın ve `.SVDat` indirin. SystemView → File → Open.

**Bağlantı 230400 baud'dur.** Hafta 2'nin eski dokümanlarındaki baud bilgisini bu paket için kullanmayın. SystemView'e ST-LINK üzerinden doğrudan J-Link recorder bağlantısı yapılmaz; 200 ms RAM snapshot'ı deney sonunda VCP üzerinden aktarılır. Sürekli canlı trace akışı değildir.

## Derleme

`firmware/build_week3.ps1` CMake/Ninja/Arm GCC ile derler. `firmware/build_cubeide.ps1` kurulu CubeIDE'nin native managed-build yolunu kullanır. Hedef kaynakları ve lisanslar yereldir; SEGGER sabit sürümleri `segger.lock.json` içindedir.

## Deney anlamı

Bu haftanın A/B/C varyantları **queue kapasitesi ve timeout** içindir. Hafta 2'nin aynı adlı görev önceliği düzenleriyle aynı değildir. Üretici P2, tüketici P1, konsol P3; normal ve yoğun yükte 44 gönderme girişimi. Tüketici 20 ms dış servis beklemesini vTaskDelay ile modeller. UART mesaj taşıma performansı ölçülmez; UART yalnız deney sonrası sonuç ve trace dosyası taşır.

Hafta 2 kaynağına dokunulmadı. Hafta 3 board/HAL/FreeRTOS temeli oradan kopyalandı; yeni app.c ve SystemView entegrasyonu bu klasöre eklendi. Önceki uygulama `docs/Hafta2_app_reference.c.txt` olarak korunur.

## Yeniden üretim ve doğrulama

- `python tools/build_presentations.py`: sunumları oluşturur.
- `python tools/render_docs.py`: Markdown rehberlerin HTML sürümlerini oluşturur.
- `node tools/protocol-test.cjs`: gerçek kayıtların ve bozuk aktarım durumlarının parser kontrolü.
- `tools/browser-qa.cjs`: Playwright ile sunum ve arayüz doğrulaması; PLAYWRIGHT_PATH ortam değişkeni veya yerel playwright kurulumu gerekir.
- Donanım: `python tools/capture.py --port COM4 --variant C --load BURST`.

Flash yedeği yalnız bu bilgisayarda `validation/flash_before_20261005.bin` dosyasındadır; dağıtım paketine alınmaz. Ana flash 1 MB yedeklendi; option bytes yedeği değildir. Seri port ve ST-LINK oturumları testlerden sonra serbest bırakılır.

## Queue görselleri — 6 Ekim güncellemesi

Dersin 10–13. slaytları Front/Back/Receive/Peek API farklarını genişletir. **11. slaytta** animasyonlu queue laboratuvarı bulunur: mesaj değeri seçme, öne/arkaya kopyalama, önden okuma, Peek, dolu/boş kontrolü ve altı adımlı rehberli örnek. Model mantıksal sırayı gösterir; fiziksel RAM kaydırması veya donanım ölçümü değildir. A/B/C firmware deneyi arkaya gönderim kullanır.

`node tools/queue-operations-qa.cjs` animasyonlu modelin sıralama, hata, iptal ve reduced-motion kontrollerini çalıştırır.

### Queue control block görselleri
13–16. slaytlar: üç alanın görevleri, canlı uxMessagesWaiting sayacı, öncelik sıralı xTasksWaitingToSend ve xTasksWaitingToReceive senaryoları. Sonraki/önceki olay ve sıfırlama kontrolleri; Ready, Running ve timeout ayrımı.
