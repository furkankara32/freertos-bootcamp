# Hafta 02 — V2 SystemView hazırlığı

**Yeni: [Arayüzden SystemView kaydı](docs/ARAYUZ_SYSTEMVIEW.md)** — `tools/open-interface.ps1` ile açın; V1/V2-QWB için senaryoyu başlatıp kayıt alın ve `.SVDat` dosyasını SystemView’da açın.

**Güncel durum (4 Ekim 2026):** S0/S5 ölçümleri ve üç rapor tamamlandı:

- [V1 raporu](reports/V1_S0_S5.md)
- [V2 raporu](reports/V2_S0_S5.md)
- [Karşılıklı S0/S5 ana karşılaştırması](reports/V1_V2_Karsilastirma.md)

Kartta izlemeli **V1** yüklüdür. V1 kayıt aracı `tools/capture-v1.ps1`, baud 115200. Aşağıdaki V2 komutları V2 tekrar yüklenmeden kullanılmaz. Sonuç raporları biçimsel deadline garantisi değildir; sınırlamalar raporlarda açıklanır.

Çalışma şartnamesi: [specs.md](specs.md). V2 çalışma kopyası `projects/v2`; özgün Hafta 1 kaynakları korunur. Rapor bağlantıları yukarıdadır; aşağıdaki bölüm V2 hazırlığının tarihsel kullanım rehberidir.

## Şu anki durum

- STM32F407VG üzerinde izleme eklenmiş V2-QWB yüklendi ve flash doğrulandı.
- FreeRTOS **10.3.1 korundu**. SystemView adaptörü bu çekirdeğe uyarlandı. Görev öncelikleri, kuyruk politikası, 460800 baud ve iş dilimleri korunur.
- SystemView **4.10a** taşınabilir sürümü `tools/SystemView-4.10a` içindedir.
- Yerleşik ST-LINK kullanılır; probe firmware'i dönüştürülmedi. USB–TTL COM5, mevcut USART2 PA2/PA3/GND bağlantısını taşır.
- Kayıt yöntemi **çevrimdışı kısa pencere**: hedef 500 ms boyunca RAM'e kaydeder, kayıt donar, OpenOCD işlemci çalışırken RAM'i okur; `.SVDat` SystemView'da açılır. F5 ile canlı J-Link bağlantısı bu düzenin parçası değildir.
- Bağımsız izleme açık/kapalı derlemeleri başarılı; CubeIDE Release: 0 hata, 0 uyarı. Mevcut yazılım testleri: 67 başarılı.
- S5 hazırlık pilotunda kayıp olay ve UART decoder hatası yok. Bu pilotlarda kabul edilmiş fiziksel buton olayı **0**; BTN t0→t4 doğrulaması ve performans sonuçları henüz tamamlanmadı.

## Birlikte gözlem

Kartın iki bağlantısını açık tut. Aynı anda seri terminal, eski Python arayüzü veya CubeIDE debug oturumu çalışmasın. Kart şu an hazırlanmış firmware'i çalıştırır; yeniden derleme/yükleme gerekmiyor.

Hafta 02 kökünde PowerShell:

```powershell
.\tools\capture-v2.ps1 -Scenario S5 -Windows 8
.\tools\open-systemview.ps1
```

Capture önce senaryoyu başlatır ve kalibrasyon/ARMED aşamasını bekler. `CAPTURE` satırları sırasında mavi USER düğmesine basılır. Pencereler yalnız 500 ms olduğundan bazı basışlar pencere dışında kalabilir; UART koşusunda görünseler bile trace içinde görünmeyebilirler. İzleri birlikte incelerken tam zincir içeren pencere seçilecek. Siyah RESET düğmesi ölçüm sırasında kullanılmaz.

SystemView lisans ekranında eğitim kullanımı için `Continue under SFL`, System Information ekranında `OK` seçilir. Kayıt zaten yüklenmiştir. Events List, Timeline ve Context Statistics üzerinden TelemetryTask, ButtonTask, UartTxTask ve IRQ'lar incelenir. Açılışta ilk yaklaşık 0.6 ms tanımlama maliyetidir; kararlı yük analizi bundan sonraki aralığa bakar.

BTN_ACCEPT=t0, BTN_TASK=t1, BTN_READY=t2, BTN_TX_START=t3, BTN_TX_TC=t4. `run` ve `id` aynı olay zincirini eşler; `tim5_us` orijinal uygulama zamanıdır. DMA complete ile son UART bitinin çıkışını gösteren UART TC aynı olay değildir.

Yeni kayıtlar `traces/v2/<senaryo>/<oturum>/window-*/recording.SVDat`; her pencerede `trace.json`, RAM ve OpenOCD logu bulunur. Oturumda ham UART, CRC denetimli dump ve build kimliği saklanır. Pilot ölçümleri `measurements/pilots` altındadır; otomatik olarak sonuç raporu sayılmaz.

`trace.json` içindeki `clean=true` ve `dropped_events=0` kontrol edilir. Taşan pencere yorumlanmaz; süre azaltılır. İlk 32 KB/700 ms denemeleri taşmıştır ve geçmiş kayıt olarak korunur. Son ayar 64 KB/500 ms'dir. İşlemciyi durduran ilk denemeler de resmi ölçüm değildir.

## Yeniden üretim

```powershell
.\projects\v2\interface\.venv\Scripts\python.exe .\projects\v2\firmware\build.py --config Release --variant QWB --trace systemview
```

ELF: `projects/v2/firmware/build/v2/QWB/Release/systemview/Homework_001.elf`. `build.json` ve `source-manifest.json` eşlik eder. `--trace none` ayrı klasöre izleme kapalı build üretir. CubeIDE ile `projects/v2/firmware/Homework_001` içe aktarılabilir; gözlem için yüklenmiş bağımsız build'in ELF'i esas alınır. Başka bir ELF yüklenirse capture aracının ELF yolu da eşleşmelidir.

Özgün flash yedeği `provenance/before-v2-flash.bin`; kaynak kimlikleri `provenance` altındadır. `tools/integrate_v2.py` ve `instrument_app.py` ilk hazırlık yardımcılarıdır; tekrar çalıştırılmaz. Güncel kaynak dosyaları ve manifestler esas alınır.

SEGGER olay açıklamaları taşınabilir uygulamanın `Description` klasörüne eklendi. OS açıklamasındaki 512–528 kimlikleri yalnız bu V2 modülüne aittir; V1 hazırlanırken açıklamalar ayrıca eşlenecek. Dosya biçimi için [SEGGER kılavuzu](https://doc.segger.com/UM08027_SystemView.html).

İzleme ek yükü ve SWD okumasının etkisi sıfır varsayılmaz. Kaydetme penceresi bittikten sonra SWD okunur; resmi karşılaştırmada izleme açık/kapalı koşular şartnameye göre ayrıca ölçülür. Hazırlık, entegrasyon ve dokümantasyonda Codex desteği kullanıldı; pilot veriler gerçek karttan alınmıştır.
