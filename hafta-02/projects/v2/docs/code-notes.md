# Kod notları

## Zaman damgası ve ISR

`stm32f4xx_it.c::EXTI0_IRQHandler` ilk kullanıcı işlemi olarak `App_Now()` çağırır. `App_ButtonIRQ` kabul kapısını ve 30 ms filtresini kontrol eder. İlk kenar ayrı bayrakla kabul edilir. Kayıt slotu **queue send öncesi** ayrılır; queue dolsa bile id/t0 korunur.

```c
uint32_t now = App_Now();
/* pending clear */
App_ButtonIRQ(now);
```

`app.c` içinde ana havuz 128, ek alan 8 kayıttır. 129. kabulde `record_overflow` kaydı oluşturulur, kapı kapanır, AUTO_STOP bildirimi gider. Run sırasında slot tekrar kullanılmaz.

## Görevler ve sahiplik

```text
EXTI0 → buttonQ[8] → ButtonTask P2 → txQ[16] → UartTxTask P1 → UART TC
                         TelemetryTask P3 ────────┘
```

ButtonTask t1’i queue receive dönüşünde, t2’yi sıfır beklemeli enqueue öncesinde alır. UartTxTask t3’ü DMA başlangıcından önce alır. 64 B DMA tamponu task’ın kalıcı SRAM alanıdır; callback/abort tamamlanmadan yeniden kullanılmaz.

Normal DMA transfer-complete yalnız UART TC interrupt’ını açar. `HAL_UART_TxCpltCallback` gerçek TC yolu üzerinden gelir; t4 burada aynı kayıt kimliğine yazılır. Callback notification bitini task beklemeye başlamadan verse de kaybolmaz.

```c
uint32_t dt_us = (uint32_t)(end_us - start_us);
```

Farklar unsigned wrap ile hesaplanır. t0 fiziksel kenarın donanımsal capture anı değildir; t4 TC callback gözlem zamanıdır. d2 duvar saati, d3 enqueue+FIFO+scheduling aralığıdır; saf CPU zamanı veya tek başına kuyruk beklemesi sayılmaz.

## STOP ve timeout

Kabul kapısı kapanır; Telemetry yeni üretimi bırakır; buttonQ sonuna bariyer konur. ButtonTask önceki olayları işler, sonra txQ sonuna bariyer ekler. UART sahibi bariyeri tüketmeden snapshot/dump başlamaz. Kontrol task’ı bu sırada bloklanır.

20 ms deadline aktarımı iptal etmez. 1 s olay/drain gözetimi ayrı kullanılır. Timeout’ta TX sahibi HAL abort yapar; eski DMA/TC durumu sakinleştirilmeden yeni tampon aktarımı başlatılmaz. Bekleyen mesajlar timeout terminal durumuna alınır. Callback/timeout sonucu tek seferliktir; kritik bölgeler formatlama/uzun bekleme içermez.

Kurtarma veya bariyer hatasında FAULT yeni kabulü durdurur; RAM korunur. Bu sürüm FAULT durumundan otomatik yeniden başlatma yapmaz; hata kökü incelenmelidir. Donanım watchdog eklenmemiştir.

## PC ve kayıt

`serial_worker.py` portu QThread içinde açar/okur/yazar/kapatır. GUI komutları thread-safe kuyruğa atar. `protocol.py` parçalı byte akışından 64 B frame çıkarır; M1/M2 eşleşmesini, CRC’yi, sayaçları ve timestamp zincirini doğrular. Tam dump atomik `events.csv` adıyla kaydedilir; ham log kalır.

`tests/test_protocol.py` taşma, deadline sınırı, eksik M2, CRC, metadata ve parçalı alımı sınar. `tests/test_gui.py` gerçek Qt uygulamasında demo bağlantı→CFG→START→basış→STOP→CSV akışını çalıştırır. Demo bir scheduler simülasyonu değildir ve sonuçları `synthetic` olarak işaretlidir.
