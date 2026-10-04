# FreeRTOS Bootcamp — Hafta 01 / V2

STM32F407G-DISC1 üzerinde buton yanıt süresi laboratuvarı. V2; BTN öncelikli ayrı TX kuyrukları, parçalı CPU işi ve 460800 baud ekler. Task öncelikleri Telemetry=3, Button=2, UART=1 olarak korunur.

**Durum:** Yerel V2 uygulaması ve yazılım testleri hazır. Fiziksel kartta ≤10 ms kabul testi henüz yapılmadı; sentetik/masaüstü testleri bu hedefin donanım kanıtı değildir.

- [V2 güncelleme şartnamesi](FreeRTOS_Bootcamp_Hafta1_V2_Update_Specs_v1.0.md)
- [V2 kurulum, protokol ve deney adımları](docs/v2.md)
- [V2 doğrulama durumu](docs/review/v2/status.md)
- [V1 şartnamesi](FreeRTOS_Bootcamp_Hafta1_Specs_v0.3.md) ve [gerçek V1 ölçüm raporu](analysis/report.md)

## Hızlı başlangıç

PowerShell, repo kökünde:

```powershell
./interface/setup.ps1
./interface/run.ps1 -Demo
```

Demo **sentetiktir**. Sıra: Senaryoyu uygula → Başlat → 5 s bekle → Demo: butona bas → Durdur ve aktar. Canlı BTN sayacı ile deney sonu doğrulanan tablo/grafik ayrı gösterilir.

Windows paketi üretmek için:

```powershell
./interface/build_exe.ps1
```

Çıktı: `interface/dist/BootcampMonitorV2/BootcampMonitorV2.exe`. `_internal` dahil bütün klasörü birlikte taşıyın. Önceki `BootcampMonitor` V1 paketi üzerine yazılmaz. Git klonunda build/dist çıktıları bulunmaz; script'lerle yeniden üretilir.

## Firmware

```powershell
./interface/.venv/Scripts/python.exe firmware/build.py --variant QWB --config Release
```

Çıktı: `firmware/build/v2/QWB/Release/Homework_001.elf`, `.bin`, map, build.log ve build.json. ARM GCC, PATH veya `C:/ST` altında aranır; gerekirse `--toolchain '<bin>'` verin. CubeIDE varsayılanı da QWB'dir. V1 build dizini korunur.

QWB ELF dosyasını STM32CubeProgrammer ile ST-LINK/SWD üzerinden yükleyip doğrulayın. Bu yerel güncelleme karta otomatik yükleme yapmaz. Ardından:

```powershell
./interface/run.ps1 -Port COM5 -Baud 460800 -Build firmware/build/v2/QWB/Release/build.json
```

Port adı bilgisayara göre değişebilir. PA2 → TTL RX, PA3 ← TTL TX, ortak GND, 3,3 V lojik. Portu aynı anda tek uygulama açmalıdır. Kartta hâlâ V1 varsa **115200** seçin; arayüz PROTO2'yi okumaya devam eder. 460800 ile V1 kart yanıt vermez.

EXE açılışında COM/baud seçebilir, **Yüklenen firmware build.json seç** düğmesiyle gerçekten karta yüklediğiniz build kimliğini kayda ekleyebilirsiniz. Otomatik olarak yakındaki herhangi bir ELF'in karta yüklü olduğu varsayılmaz.

Başlat pasifse **Önceki kaydı al → Senaryoyu uygula → Başlat** sırasını izleyin. CONFIGURED ölçüm değildir; ARMED beklenmelidir. USER butonuna basınca BTN sayacı artar; **Durdur ve aktar** tam kaydı doğrular, CSV ve grafiği oluşturur.

## Karşılaştırma profilleri

| Profil | TX seçimi | CPU işi | Baud |
|---|---|---|---:|
| V1 (arşiv) | Ortak FIFO | Tek parça | 115200 |
| Q | BTN öncelikli | Tek parça | 115200 |
| QW | BTN öncelikli | Parçalı | 115200 |
| QB | BTN öncelikli | Tek parça | 460800 |
| QWB | BTN öncelikli | Parçalı | 460800 |

`--variant Q`, `QW`, `QB` veya `QWB` ile derlenir. Nihai 10 ms kabul hedefi QWB içindir. Senaryolar S0 kapalı, S1 10 Hz, S2 50 Hz, S3 100 Hz, S4 100 Hz + 2 ms CPU, S5 100 Hz + 5 ms CPU olarak korunur.

## Test ve ölçüm

```powershell
./interface/.venv/Scripts/python.exe -m pytest -q
./interface/.venv/Scripts/python.exe tests/hardware_smoke.py --port COM5 --baud 460800 --scenario S5 --seconds 90 --formal --build firmware/build/v2/QWB/Release/build.json
./interface/.venv/Scripts/python.exe -m analysis.v2_report measurements/v2/QWB/runs --output analysis/v2/QWB
```

Fiziksel test script'i gerçek buton basışlarını bekler; olay üretmez. En az 30 kabul edilen olay, ≥0,5 s aralık ve 5 s ısınma gerekir. Son QWB doğrulamasında ayrıca S5 için en az 100 olaylık koşu ve faz kapsamı aranır. Donanım koşusu yapılmadan rapor başarı üretmez.

Native C testleri üretim `app.c` kodunu sahte HAL/RTOS ile çalıştırır; host GCC yoksa bu testler skip edilir. ARM derlemesi ve gerçek zamanlama ölçümü bunun yerine geçmez. Native GCC bu çalışma alanında mevcuttur.

V2 gerçek kayıtları `measurements/v2/<variant>/runs`, sentetik kayıtları aynı varyantın `demo` klasöründedir. Kaynak GUI varsayılan ölçüm kökü repo içindeki `measurements`; EXE varsayılanı kendi yanındaki `measurements` klasörüdür. `--output` ile değiştirilebilir. Analiz yolunu kullandığınız kayıt konumuna göre seçin.

V1 `measurements/selected`, S0–S5 CSV'leri ve `analysis/report.md` korunur. V2 raporları bütün koşuları, kayıpları ve 10/20 ms ihlallerini ayrı gösterir; farklı firmware hash'leri tek kabul setinde birleştirilmez. Maksimum gözlem, kanıtlanmış WCRT değildir.

Kaynak depo: https://github.com/furkankara32/hafta-01. Commit ve push kullanıcı tarafından yapılacaktır.
