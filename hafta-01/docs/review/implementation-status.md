# Uygulama ve doğrulama durumu — 24 Eylül 2026

Specs v0.3 temel alınarak firmware, seri protokol, PC arayüzü ve analiz hattı uygulanmış; gerçek kartla S0–S5 deneyleri tamamlanmıştır. Proje yerel olarak test edilebilir durumdadır. [Ölçüm raporu](../../analysis/report.md).

## Tamamlanan doğrulamalar

- Release/-Os firmware derlendi, ST-LINK/SWD ile karta yüklendi ve yükleme doğrulandı. Uygulama kaynaklarında uyarı yok; vendor HAL içinde üç kullanılmayan parametre uyarısı vardır. [Build kaydı](firmware-implementation-build.log), [metadata](firmware-build.json), [yükleme kaydı](flash-log.txt).
- Protokol, CRC/bütünlük, zaman damgası taşması, senaryolar ve GUI akışlarını kapsayan 21 otomatik test geçti. [Test kaydı](software-tests.log).
- Altı gerçek senaryoda 195 kabul edilen olay toplandı; 177 iletim tamamlandı. S5'te 18 TX kuyruk düşmesi ve 26 geç tamamlanma ham verilerde korunur. [Özet](../../measurements/summary.csv), [seçim manifesti](../../measurements/selection.json).
- COM5 üzerinden gerçek GUI HELLO ve DUMP akışı 30 kayıtla doğrulandı; CRC kontrolü, CSV kaydı ve ekran çizimi başarılı. [Test kaydı](gui-hardware-test.log), [ekran](ui-hardware.png).
- Windows EXE'nin QtCore DLL yükleme hatası giderildi. Paketleme PATH'i ilgisiz araçların ICU DLL'lerini toplamaması için sınırlandı; temiz paket yeniden üretildi. Paketlenmiş GUI başlangıç/ekran testi çıkış kodu 0 ile tamamlandı. [Kayıt](exe-test.log), [ekran](exe-final/packaged-gui.png).

Çalıştırılabilir dosya `interface/dist/BootcampMonitor/BootcampMonitor.exe`; taşıma için `_internal` dahil tüm BootcampMonitor klasörü gerekir. Kaynaktan başlatma `./interface/run.ps1`, kart gerektirmeyen demo `./interface/run.ps1 -Demo`.

## Ölçülen firmware kimliği

ELF SHA256: `1d808b630065538a1d4824aaf96ed170b7ad6a43cc7d453f0e1b6555c36486f1`.

Altı resmi koşunun host build metadata'sı bu hash ile aynıdır. Temel kaynak commit'i `7c6c83fbb21885d30aa82b25f9bd0821291346b4`, ancak uygulama henüz commit edilmediğinden `git_dirty=true` kaydedilmiştir. Kaynak dosya hash'leri [manifestte](firmware-source-manifest.json) bulunur. Flash text 27748 + data 104 bayt; statik RAM data 104 + bss 43248 bayttır. Ölçümlerde minimum boş heap 21344 bayt kaldı.

## Kapsam sınırları

- `.ioc` güncellendi; CubeMX ile yeniden üretim eşdeğerliği test edilmedi. Ölçülen build depodaki kaynaklardan standalone build script'iyle üretildi.
- Bağımsız logic analyzer doğrulaması yapılmadı; ölçümler MCU zaman damgalarına dayanır.
- Gerçek donanımda stack overflow, DMA abort/timeout ve tüm hata yollarına zorlanmış hata enjeksiyonu yapılmadı. Normal koşu ve S5 kuyruk dolması doğrulandı.
- Bağımsız donanım watchdog'u ve FAULT sonrası otomatik toparlanma uygulanmadı; bu durumlar teşhis/reset gerektirir.
- GitHub'a commit/push, video veya harici teslim yapılmadı. Paket ve ölçüm çıktıları yerel çalışma alanındadır.

