# A/NORMAL kısa donanım testi - 12 Ekim 2026

Yalnız bir A/NORMAL, trace açık koşusu çalıştırıldı. Diğer senaryolar kullanıcıya bırakıldı.

## Sonuç: temel kart ve kayıt zinciri başarılı

- ST-LINK: STM32F4DISCOVERY, device ID 0x413, 1 MB flash.
- Önceki 1 MB flash `provenance/pilot/before-week3.bin` dosyasına yedeklendi; option bytes yedeği değildir.
- Release HEX programlandı ve STM32CubeProgrammer read-back doğrulaması başarılı. Log: `provenance/pilot/flash.log`.
- UART: USB-TTL COM5, 230400 baud. Kart HELLO/BUILD kimliği yerel firmware ile eşleşti.
- run_id: 1; attempted=44, accepted=44, failed=0, consumed=44.
- RX hata/drop: 0/0. Stack boşluk alt değerleri (word): [700, 702, 736].
- Send ortalama/maksimum: 12.16 / 18 us.
- Üretimden receive'e gecikme ortalama/maksimum: 32.86 / 52 us.
- Normal mesaj üretim aralıkları: min 99109, max 100000, ortalama 99979.12 us; nominal 100 ms ile uyumlu.
- SEGGER snapshot: 11702 bayt, FNV-1a doğru, drops=0, stop_reason=1 (süre).

## Kapsam ve açık kalan doğrulama

Özgün SVDat dosyası kaydedildi ve aktarım bütünlüğü doğrulandı. SystemView masaüstü başlatıldı; dosya açma iletişim kutusu otomasyonu hedef/odak sorunu verdi. Bu nedenle yeni F407 kaydının GUI içinde decode edilmesi, yaklaşık 20 ms servis aralığı ve task olaylarının görsel incelemesi bu testte doğrulanmış sayılmaz. Eski otomatik açılan Hafta 1 kaydı yeni testin kanıtı değildir.

Bu tek normal koşu BURST ve B/C davranışını veya bütün ödev matrisini doğrulamaz. LED fiziksel olarak gözlenmedi. STM32CubeProgrammer bağlantıda hedef gerilimini 2,89 V bildirdi; testte bağlantı/flash/seri hata gözlenmedi.

Dosyalar: `measurements/pilot/A_NORMAL_trace1_1791816005471778700.csv`, `.txt`, `.json`, `.SVDat`.

Build: `e3e19bc3a4a179e411f6acb7d828a5866b1f70b3d5692b42ba430a6e39b231d6`. Kartta bu Release firmware bırakıldı. Kayıt aracı COM5'i kapattı; senaryo denemelerine hazır.
