# V2 yerel uygulama ve doğrulama — 26 Eylül 2026

V2 şartnamesinin yerel firmware, protokol, arayüz, kayıt ve analiz değişiklikleri tamamlandı. **Bu sürüm karta yüklenmedi; gerçek kartta ≤10 ms kabul hedefi henüz doğrulanmadı.** Bu klasördeki GUI ekranı ve demo audit sentetiktir.

## Uygulananlar

- BTN ve TEL için ayrı TX kuyrukları; tek UART sahibi; BTN önce seçimi; notification ile iki kaynaktan uyanma; yeni çift kuyruk drain/barrier akışı.
- QW/QWB profillerinde hesaplama durumunu ve toplam işi koruyan 1 ms hedefli dilimler; aralarda bloklama; kalibrasyon, dilim ve gerçek aktivasyon sürelerinin ayrı raporlanması.
- Q/QW 115200, QB/QWB 460800 baud; öncelikler 3/2/1 sabit. V2 varsayılanı QWB.
- PROTO3 ve V1 PROTO2 uyumluluğu, ayrı kuyruk sayaçları, 10/20 ms ihlalleri, baud ve firmware profili doğrulaması.
- GUI baud/build seçimi, açık sürüm bilgisi, 10 ms grafik sınırı, önceki kayıt koruması; V2 kayıtları için ayrı klasörler.
- V2 ham dump/CSV eşleşme denetimi, bütün koşulları ve kayıpları koruyan kabul raporu, firmware kimliği ve nominal faz kapsamı kontrolü.

## Kanıtlar

| Kontrol | Sonuç / kanıt |
|---|---|
| Python + native C testleri | **67 passed** — [günlük](software-tests.log) |
| Q Release | Başarılı — [build metadata](Q-build.json), [özet](Q-build-summary.log) |
| QW Release | Başarılı — [build metadata](QW-build.json), [özet](QW-build-summary.log) |
| QB Release | Başarılı — [build metadata](QB-build.json), [özet](QB-build-summary.log) |
| QWB Release | Başarılı — [build metadata](QWB-build.json), [özet](QWB-build-summary.log) |
| GUI sentetik uçtan uca | PROTO3 QWB S5, 5 olay, CRC ve CSV — [günlük](gui-demo-test.log), [ekran](gui-demo.png) |
| Paketli V2 EXE | Çıkış kodu 0 — [günlük](exe-test.log), [ekran](exe-smoke/packaged-gui.png) |
| Sentetik audit | Donanım kabulü **false**, beklendiği gibi — [audit](synthetic-audit/audit.json) |
| V1 arşiv uyumluluğu | Altı fiziksel seçili koşunun ham dump ve metadata eşleşmesi yeni parser ile tekrar doğrulandı |

Native C düzeneği gerçek `app.c` kodunu sahte HAL/RTOS ile çalıştırır. BTN önceliğini, sınıf içi FIFO sırasını, DMA sırasında gelen BTN'yi, kuyruk dolmasında gerçek Button task drop kaydını, iki veri kuyruğundan sonra barrier onayını, boşta uyandırmayı ve parçalara bölündüğünde hesabın korunmasını sınar. Her dört profilin firmware dump'ı Python parser'ından geçer. Bu testler scheduler gecikmesi veya fiziksel UART ölçümü değildir.

Dört ARM build'de uygulama kaynaklarında uyarı yoktur; vendor HAL flash sürücüsünde üç mevcut kullanılmayan parametre uyarısı vardır. QWB text=29288, data=104, bss=43296 bayttır. Dinamik kuyruklar FreeRTOS heap içindedir; yeni minimum boş heap ve stack marjları kartta ölçülecektir.

QWB ELF SHA256: `71139f5208540c56517ef368ef36e3a1fdc6763428a97fba6fef9e53bc443d4d`. Temel commit `b74863a3a27ebeb14ca932737005b68d9eee1945` V1 commit'idir; V2 değişiklikleri henüz commit edilmediğinden metadata `git_dirty=true` içerir. [Firmware kaynak hash manifesti](firmware-source-manifest.json) bu yerel build'in kaynaklarını kaydeder. Kullanıcı commit sonrası yeniden derlerse ELF kimliği değişebilir; deneyde gerçekten yüklenen build.json kullanılmalıdır.

## Yerel çıktılar

- `firmware/build/v2/QWB/Release/Homework_001.elf` ve diğer varyant klasörleri.
- `interface/dist/BootcampMonitorV2/BootcampMonitorV2.exe`; `_internal` ile birlikte kullanılmalıdır.
- Önceki V1 build, Windows paketi ve ölçüm kayıtları korunmuştur. Git commit/push yapılmamıştır.

Derleme çıktıları `.gitignore` kapsamındadır; GitHub'a kaynaklar, testler ve dokümantasyon gider. Başka bilgisayarda build/setup script'leriyle üretilir.

## Kalan donanım doğrulaması

Doğru QWB ELF'i karta yükleyip 460800 TTL iletişimini, kalibrasyonu, periyot aşımı olmadığını ve S0–S5 yanıtlarını doğrulamak gerekir. Şartnamedeki S5 ≥100 olay/faz kapsamı ve sıfır kayıp koşulları ölçülmeden ≤10 ms sağlandı denmez. Bağımsız logic analyzer, gerçek hata enjeksiyonu, yeni runtime heap/stack marjları ve CubeMX yeniden üretimi bu yerel doğrulamada çalıştırılmamıştır.

Kullanım komutları [README](../../../README.md) ve [V2 uygulama notlarındadır](../../v2.md).
