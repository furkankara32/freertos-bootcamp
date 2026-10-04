# FreeRTOS Bootcamp — Hafta 01

STM32F407G-DISC1 üzerinde yük altında buton yanıt süresi ölçümü. Üç uygulama görevi, USART2 DMA TX, 1 MHz TIM5 ve PySide6 PC arayüzü içerir.

Güncel tasarım: [Specs v0.3](FreeRTOS_Bootcamp_Hafta1_Specs_v0.3.md). Uygulama ve doğrulama durumu: [test raporu](docs/review/implementation-status.md).

S0–S5 gerçek kart deneyleri tamamlandı: 195 kabul edilen olay, 21 başarılı otomatik test. Sonuçlar ve S5 yük altında kuyruk kayıpları [ölçüm raporunda](analysis/report.md) açıklanır. Seçim ve grafikleri yeniden üretmek için `./interface/.venv/Scripts/python.exe -m analysis.select_runs` çalıştırın.

## Hızlı başlangıç — Windows

Repo kökünde PowerShell:

```powershell
./interface/setup.ps1
./interface/run.ps1 -Demo
```

Demo gerçek kart ölçümü değildir. Arayüzde **Senaryoyu uygula → Başlat → 5 s ısınma → Demo: butona bas → Durdur ve aktar** sırasını kullanın. Demo basışları en az 0,5 s aralıklı kabul edilir. Sentetik kayıtlar yalnız `measurements/demo/` altına gider.

Gerçek kart için `./interface/run.ps1`, TTL adaptörünün COM portu ve **Bağlan** seçilir. HELLO yanıtından sonra senaryo uygulanır. Firmware çalışırken portu aynı anda başka terminal/test script’i açmamalıdır.

**Başlat pasifse:** kartta önceki deneyden kalan kayıt olabilir. Önce **Önceki kaydı al**, ardından **Senaryoyu uygula → Başlat** seçin. `CONFIGURED` ölçümün başladığı anlamına gelmez; 5 saniyelik ısınmadan sonra `ARMED` görünmelidir. Fiziksel basışlar **Alınan BTN** sayacında canlı görünür. Ayrıntılı tablo ve grafik **Durdur ve aktar** sonrası doğrulanan kayıttan oluşturulur.

## Firmware derleme ve yükleme

Kurulu ARM GCC ile:

```powershell
python firmware/build.py --config Release
```

Araç zinciri PATH veya `C:/ST` altında değilse `--toolchain '<ARM GCC bin klasörü>'` verin. Çıktılar `firmware/build/Release/`: ELF, BIN, map, build.log ve gerçek hash/derleyici bilgili build.json. Script yalnız yerel kaynakları derler, kütüphane indirmez.

STM32CubeIDE için `firmware/Homework_001` projesini import edip build edin. Ölçümde aynı build/optimizasyon kullanın; Debug ve Release verilerini karıştırmayın. Standalone build script’i yeni `Src/*.c` dosyalarını otomatik toplar; eski Debug makefile’ı yeni kaynaklar için elle yamalanmaz.

STM32CubeProgrammer ile ST-LINK/SWD üzerinden ELF’i yükleyip doğrulayın ve resetleyin. [Bağlantı ve yapılandırma](docs/setup.md) dosyasına bakın.

## Deney

| Senaryo | Telemetri | Aktivasyon başına ek iş |
|---|---:|---:|
| S0 | Kapalı | Yok |
| S1 | 10 Hz | Yok |
| S2 | 50 Hz | Yok |
| S3 | 100 Hz | Yok |
| S4 | 100 Hz | Yaklaşık 2 ms |
| S5 | 100 Hz | Yaklaşık 5 ms |

Her senaryo: 5 s ısınma, ARMED bildirimi, ≥30 fiziksel basış (aralık ≥0,5 s, değişken faz), **Durdur ve aktar**. Normal mesajlar LF dahil 64 B, baud 115200 8N1; deadline 20 ms. R, MCU `t4−t0` farkıdır; PC varış zamanı değildir.

Tam dump otomatik olarak benzersiz bir `measurements/runs/<oturum>_Sx_runN/` klasörüne kaydedilir. `events.csv`, `metadata.json`, `serial_raw.bin`, `derived.csv` birlikte korunur. Eksik/bozuk dump resmi CSV yapılmaz; bağlantı ham log’u `connection_.../serial_raw.partial.bin` altında kalır. **Kaydı tekrar al** RAM’deki sonucu yeniden alır. Kaydetme hatası sonrası yeni START eski RAM kaydını silebilir; önce kurtarın.

Grafikleri yeniden üretmek için senaryo başına bir koşu içeren dizin verin:

```powershell
./interface/.venv/Scripts/python.exe analysis/analyze.py measurements/selected --output analysis/results
```

Seçilen gerçek koşular `measurements/selected/S0/` … `S5/` altında hazırdır. Script aynı senaryo için birden fazla koşuyu sessiz birleştirmez. Ödev teslimi için olay CSV’leri `measurements/S0.csv` … `S5.csv`, metadata’ları `Sx_meta.json`, özet `measurements/summary.csv` olarak hazırlanmıştır.

## Testler ve paketleme

```powershell
./interface/.venv/Scripts/python.exe -m pytest -q
./interface/.venv/Scripts/python.exe tests/generate_demo.py
./interface/.venv/Scripts/python.exe tests/hardware_smoke.py --port COM5 --scenario S0 --seconds 45
./interface/build_exe.ps1
```

Windows uygulaması `interface/dist/BootcampMonitor/BootcampMonitor.exe`; bütün klasörü birlikte taşıyın. Kaynakla çalıştırma alternatifi korunur. Demo grafikler `analysis/demo_results/`; gerçek sonuçlarla karıştırılmaz.

- [Kurulum](docs/setup.md)
- [Kritik kod ve sahiplik](docs/code-notes.md)
- [Yapay zekâ kullanımı](docs/ai-usage.md)
- [Analiz raporu / gerçek ölçüm durumu](analysis/report.md)

Kaynak depo: https://github.com/furkankara32/hafta-01. Bu çalışma otomatik commit/push veya Telegram teslimi yapmaz.
