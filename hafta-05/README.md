# Hafta 5 — STM32F4 UART / LED laboratuvarı

Bu proje gerçek STM32F407G-DISC1 üzerinde çalışır. Uygulama ekranındaki veriler simülasyon değildir. Tek USB–TTL ile iki ayrı USART kullanılır; J-Link gerekmez.

**Rapor:** [Markdown](reports/Hafta5_Rapor.md) · [PDF](reports/Hafta5_Rapor.pdf). Güncel dört deney kaydı `records/S1`–`S4` altındadır. Ayrıntılı test sonuçları `docs/` içinde tutulur.

## Yeni bilgisayarda kurulum

Windows, Python 3.12, STM32CubeIDE (ARM GCC ve OpenOCD) ve SEGGER SystemView gerekir. STM32CubeIDE araçları mevcut betiklerde `C:/ST` altında aranır. SystemView yolu arayüzden seçilir. TTL portunu cihazına göre seç; son kullanıcı deneylerinde COM7 kullanıldı.

Repo kökünden:

```powershell
cd hafta-05
py -3.12 -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe firmware/build.py
.venv\Scripts\python.exe -m unittest discover -s tests -v
.venv\Scripts\python.exe tools/hardware.py flash
.\interface\build_exe.ps1 -Python .\.venv\Scripts\python.exe
```

Sonra **`dist/Hafta5Lab/Hafta5Lab.exe`** açılır. `interface/build` altındaki ara EXE çalıştırılmaz. `dist` paketi Git'e dahil değildir; EXE ve yanındaki `_internal` klasörü birlikte üretilir. Aynı ELF ile programlama ve trace çıkarımı yapılmalıdır; başka build'e ait ELF ile eski RAM kaydı çıkarılmaz. Önceden kaydedilmiş `.SVDat` dosyaları SystemView'da doğrudan açılabilir.

## Açılış

1. Kartı ST-LINK USB ile bilgisayara bağlayın.
2. 3,3 V USB–TTL: **TX → PB11**, **RX → PA2**, **GND → GND**. VCC bağlamayın. Loopback yok.
3. `dist/Hafta5Lab/Hafta5Lab.exe` dosyasını açın. Yanındaki `_internal` klasörünü koruyun.
4. TTL portunu seçin (ilk doğrulamada **COM5**). ST-LINK'in sanal COM12 portu bu veri yolu değildir.
5. **Bağlan**: firmware kimliğinin doğrulanmasını bekleyin.
6. Senaryo/varyant seçip **Kaydı başlat** düğmesine basın. İlk hata/yük tetiklemesi otomatik yapılır; elle tekrarlamak için ilgili düğmeyi kullanabilirsiniz.
7. **Durdur ve kaydet**: STOP cevabından sonra UART verisi kaydedilir ve ST-LINK ile RAM trace çıkarılır. İşlem sırasında kart kısa süre duraklatılabilir; bu aşama ölçüm sonrasıdır.
8. **SystemView ile aç**: aynı koşunun `trace.SVDat` dosyasını açar. Eski koşuyu seçerek geçmiş kayıtları da açabilirsiniz.

Firmware kartta yüklüdür; yeniden yüklemek gerekirse arayüzdeki **Firmware yükle (ST-LINK)** düğmesi kullanılabilir. Bu işlem kart uygulamasını değiştirir ve yeniden başlatır. CubeIDE debug oturumunun probe'u kilitlemediğinden emin olun.

## Senaryolar

| Senaryo | Varyantlar | Gözlem |
|---|---|---|
| S1 | Referans | LED geçişleri ve 10 KB RX yükü |
| S2 | Yüksek öncelik/polling; düşük öncelik/polling; yüksek öncelik/kesme | Report task CPU'yu bırakmadığında LED gecikmesi |
| S3 | Kesintisiz parser CPU işi; parçalı iş | Parser'ın Execute task'ını geciktirmesi |
| S4 | Event başına tek komut; doğru Queue tüketimi | Event birleşmesi nedeniyle Queue'da unutulan işler |

S2 ve S3 tetiklemesi ilk LED geçişinin yakınında planlanır. PC/USB zamanlaması kesin değildir; gerçek tetik anı kart trace'inden kontrol edilir. S4'te her komut bir LED dizisidir; 1000 ms ve çok tur seçilirse kuyruk doğal olarak uzun bekler. Hızlı inceleme için 100 ms / 1 tur kullanılabilir.

## Trace sınırı

SystemView kaydı tüm LED deneyinin otomatik olarak tamamını kapsamaz. Başlangıçta **1,5 saniyelik RAM penceresi** alınır; UART kaydı tüm koşu boyunca sürer. Sonraki geçiş için “Trace penceresi” düğmesi mevcut RAM kaydını yeniler. Önceki pencere gerekiyorsa önce kaydedin. Tampon erken dolarsa PARTIAL yazılır, başarı gibi sunulmaz.

Task Ready/Running/Blocked ve uygulama olayları tutulur. Yoğun FreeRTOS API giriş/çıkış ayrıntıları RAM bütçesi için filtrelidir. UART byte başına ISR görünümü bu sürümde açık değildir; mikro-saniyelik ISR profilinin eksiksiz ölçüldüğü iddia edilmez. SysTick ve task çizelgesi korunur.

SystemView yolu `interface/settings.json` içinde tutulur; bu bilgisayarda önceki haftanın mevcut SystemView 4.10a kurulumu kullanılır. Başka bilgisayarda uygulama yolu seçilebilir. ST-LINK/OpenOCD ve ARM sembol aracı için STM32CubeIDE araçları gereklidir; uygulama bunları `C:/ST` altında bulur.

## Kayıtlar

Her senaryo için **yalnız bir kayıt** tutulur: `records/S1`, `S2`, `S3`, `S4`. Yeni koşu, UART ve eşleşen SystemView kaydı doğrulandıktan sonra aynı senaryonun eski kaydını değiştirir; varyant değişmesi ayrı bir arşiv oluşturmaz. Aktarım başarısızsa önceki geçerli kayıt korunur. Tamamlanmamış girişimler `.pending` altında kalır ve arayüzden yeniden trace çıkarımı denenebilir.

Her kayıt manifest, ham TX/RX, JSONL olayları, LED CSV, özet ve SystemView dosyası içerir. “COMPLETE” yalnız kayıt penceresinin tamamlanmasıdır; tüm senaryonun deadline testini geçtiği anlamına gelmez. Ölçüm saati kartın TIM2 sayacıdır; host saatiyle birbirinden çıkarılmaz.

`docs/VALIDATION.md` ve `docs/regression-results.json` test sonuçlarını içerir. Bağlantı kaybında STOP cevabı alınamıyorsa **Kaydı iptal et** önceki geçerli kaydı koruyarak arayüzü serbest bırakır; kartın durduğunu doğrulamaz. Yeni denemeden önce kart resetlenmelidir.

## Kaynak ve derleme

- `firmware/`: F407 HAL/CMSIS, FreeRTOS 11.1.0, SystemView/RTT ve uygulama.
- `host/`: 100 baytlık protokol, tek yazıcılı seri oturum ve kayıt.
- `interface/main.py`: PySide6 masaüstü arayüzü.
- `tools/hardware.py`: ST-LINK yükleme ve ölçüm sonrası RAM trace çıkarımı.
- `tools/hardware_check.py`: kart üzerinde dört senaryo pilot matrisi.
- `tests/`: protokol testleri.

Python 3.12 ve `requirements.txt` ile:

```powershell
python -m pip install -r requirements.txt
python firmware/build.py
python -m unittest discover -s tests -v
python tools/hardware.py flash
python interface/main.py
```

EXE paketlemek için `interface/build_exe.ps1` kullanılır. EXE'nin çalışması Python kurulumu gerektirmez. Firmware build, flash ve trace araçları harici STM32CubeIDE kurulumunu kullanır.

Tekrarlanabilir testler: `python tools/regression_check.py` dört senaryonun sekiz varyantını gerçek kartta çalıştırır. `python tools/protocol_stress.py` komut sınırlarını ve 100 KB yükü sınar. `dist/Hafta5Lab/Hafta5Lab.exe --smoke-test COM5` paketlenmiş arayüzün iki kayıt/değiştirme döngüsünü görünür pencere açmadan çalıştırır; S1 kaydını değiştirir. Bu testlerde COM5 başka uygulamada açık olmamalıdır.

`SPEC.md` tasarım belgesidir; `interface/Hafta5Lab.spec` PyInstaller paketleme tarifidir, ikinci bir ödev spesifikasyonu değildir.

PDF raporunu yeniden üretmek için `python -m pip install -r requirements-report.txt` ve `python tools/build_report.py` kullanılır (Windows Arial yazı tipleri gerekir). Kaynak rapor `reports/Hafta5_Rapor.md` dosyasıdır; ölçüm değişince metin ayrıca gözden geçirilmelidir. Üçüncü taraf lisans listesi `docs/THIRD_PARTY.md`, GitHub Desktop gönderim adımları `docs/GITHUB_DESKTOP.md` içindedir.
