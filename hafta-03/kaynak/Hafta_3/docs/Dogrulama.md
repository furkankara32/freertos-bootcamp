# Hafta 3 — Doğrulama ve gerçek kart sonuçları

**Tarih:** 5 Ekim 2026. **Kart:** NUCLEO-L476RG, ST-LINK V2J48M35, SWD, COM4. **Firmware:** Hafta 3 queue deneyi.

## Yapılan kontroller

- CMake/Ninja ve GNU Arm 14.3.1 ile derleme ve link başarılı.
- STM32CubeIDE 2.2.0 native managed-build Debug derlemesi başarılı: **0 hata, 0 uyarı**. Günlük: `../validation/cubeide-build.log`.
- Ana flash'ın 1 MB yedeği alındı; ardından CMake ELF yüklendi, programmer verify başarılı oldu. Option bytes değiştirilmedi.
- Gerçek kartta A/B/C × NORMAL/BURST altı koşul ve A/BURST trace kapalı bir koşul tamamlandı.
- Her koşuda 44 girişim; accepted + failed = attempted, consumed = accepted. 44 CSV satırı ve benzersiz olay kimlikleri doğrulandı.
- Altı .SVDat aktarımında boyut ve FNV-1a checksum doğrulandı; trace kayıp sayacı **0**. Kayıtlar süre sınırında durdu (stop_reason=1).
- Tüm koşul sonuçlarında UART RX hata ve RX queue kayıp sayaçları **0**.
- Kaydedilen stack high-water değerleri Producer için en az 708, Consumer için 710, Console için 772 eleman. Cortex-M4F üzerinde eleman 4 bayttır; bunlar yalnız gözlenen koşulara aittir.
- Gerçek yedi ham oturum web arayüzünün ortak parser'ıyla tekrar okundu. Eksik sıra, bozuk hex, checksum, boyut, tekrarlanan satır ve eksik sonuç kontrolleri yapıldı.

## Gerçek sonuçlar

| Varyant | Yük | Trace | Kabul | Başarısız | Tamamlanan | Maks. üretim→alma (ms) | Maks. send (ms) | Trace bayt |
|---|---|---|---:|---:|---:|---:|---:|---:|
| A | BURST | Kapalı | 24 | 20 | 24 | 59.936 | 0.030 | — |
| A | BURST | Açık | 24 | 20 | 24 | 60.870 | 0.048 | 12908 |
| A | NORMAL | Açık | 44 | 0 | 44 | 0.136 | 0.048 | 12069 |
| B | BURST | Açık | 36 | 8 | 36 | 300.425 | 0.055 | 12544 |
| B | NORMAL | Açık | 44 | 0 | 44 | 0.136 | 0.048 | 12070 |
| C | BURST | Açık | 34 | 10 | 34 | 80.367 | 19.775 | 15963 |
| C | NORMAL | Açık | 44 | 0 | 44 | 0.136 | 0.048 | 12070 |

Bu tablo gerçek donanımdan alınan tekil koşuları gösterir; performans garantisi veya istatistiksel üst sınır değildir. Ham veriler, CSV ve özgün .SVDat dosyaları `../measurements/hardware/` altında eşleşen dosya adlarıyla saklanır. JSON metadata iz durumunu ve ölçüm binary'sinin hash'ini içerir.

## Derste neyi gösterebilirsiniz?

- A/Yoğun: 4 eleman dolduğunda 0 tick gönderimlerin başarısızlığı.
- B/Yoğun: kabul sayısı artarken gecikmenin yaklaşık 300 ms'ye çıkması.
- C/Yoğun: 20 ms sınırlı bekleme ile kabul sayısının artması; yine de bazı girişimlerin timeout ile başarısız olması. 20 ms consumer beklemesi ile aynı büyüklükteki send timeout'un faz/scheduler etkilerine duyarlılığını tartışın.
- A/Yoğun iz açık/kapalı: ölçümde görülen küçük farkı bütün sistemler için sabit bir overhead sayısı gibi sunmayın.

## Kapsam ve kalan kontroller

**SystemView masaüstü uygulaması bu bilgisayarda kurulu değildi.** Dosyalar gerçek SEGGER recorder çıktısıdır ve taşıma bütünlüğü kontrol edilmiştir; SystemView GUI'de dosya açma, timeline ve FreeRTOS API isimlerinin görünmesi bu çalışmada gözlemlenmemiştir. Kullanıcı uygulamayı kurduktan sonra kurulum rehberindeki adımlarla ilk .SVDat dosyasını açıp bunu doğrulamalıdır. Bu sınır, kartta kaydın alındığı ve dosyanın doğru aktarıldığı testlerden ayrıdır.

Tarayıcı kontrolleri `../validation/browser-qa.json` içinde raporlanır. Testler 1440 px ve 390 px genişliklerde sunumları, queue timeout/uyanma davranışını, kopyalama örneğini, gezinmeyi, gerçek ham kayıtların içe aktarımını ve .SVDat indirmeyi kapsar. Tarayıcının işletim sistemi seri port seçicisi test otomasyonuyla açılmadı; fiziksel seri aktarım Python/pyserial yoluyla doğrulandı.

## Binary ve bellek

CMake ELF SHA256:

`5863ee03913750f2c91c05b3d64e55bf2597a743c228feb9873eea0f45366f54`

CMake boyutları: Flash 31.992 bayt; RAM 65.536 bayt / 98.304 bayt (%66,67). RAM bütçesi 32 KB trace buffer, 24 KB FreeRTOS heap, uygulama verileri ve linker rezervlerini içerir. Heap'in tamamının ayrılmış olması task'ların tamamını kullandığı anlamına gelmez. CubeIDE ELF boyutu derleme seçeneklerindeki farklar nedeniyle küçük miktarda değişir; gerçek deneyler CMake ELF ile yapılmıştır.

## Yedek ve kartın son durumu

Yerel yedek: `../validation/flash_before_20261005.bin`, 1.048.576 bayt. Dağıtım ZIP'ine dahil edilmez. Yalnız ana flash yedeğidir. Geri dönüş için STM32CubeProgrammer ile doğrulanmış bu BIN, 0x08000000 adresine yüklenebilir; mevcut Hafta 3 firmware'i üzerine yazılır.

Testler sonunda kartta Hafta 3 firmware'i çalışır. Seri port ve programmer bağlantıları kapatılır; kullanıcı COM4'e bağlanabilir. Son test trace kapalı karşılaştırma olabilir; kayıt masasındaki İz kaydı açık kutusu bir sonraki koşu için TRACE ON gönderir.
