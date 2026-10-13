# Donanımsız doğrulama - 12 Ekim 2026

**Sonuç: Yazılım hazırlık kapısı geçti. Donanım kabulü henüz yapılmadı.**

## Yapılan doğrulamalar

| Kontrol | Sonuç |
|---|---|
| ARM GCC Release derlemesi | Başarılı, 0 hata, 0 uyarı |
| ARM GCC Debug derlemesi | Başarılı, 0 hata, 0 uyarı |
| Python unittest | 31 test başarılı |
| ELF/BIN kimlik ve kaynak manifesti | İki yapılandırmada doğrulandı |
| F407 vector table / stack başlangıcı | İki yapılandırmada doğrulandı |
| Gerçek kart, flash, UART, SystemView | Uygulanmadı |

Compiler: CubeIDE ile gelen ARM GCC 14.3.rel1. Uygulama `-Wall -Wextra -Werror` ile derlendi. STM32 HAL'in tek banklı F407 hedefinde kullanılmayan bank argümanları için yalnız HAL kaynaklarında `-Wno-unused-parameter` var; uygulama uyarıları bastırılmadı.

Release FLASH 27480 bayt (%2,62); Debug FLASH 29756 bayt (%2,84). Linker raporunda iki yapılandırma için RAM 62400 / 131072 bayt (%47,61); CCM RAM kullanılmıyor. RTOS heap ve 32 KB trace tamponu bu statik tahsis içinde. Bu, çalışma zamanı stack güvenliğinin donanım kanıtı değildir; gerçek high-water mark değerleri her koşuda ayrıca alınacak.

Release build ID: `e3e19bc3a4a179e411f6acb7d828a5866b1f70b3d5692b42ba430a6e39b231d6`

Debug build ID: `765af499c119d8b9f3102f7f1e46043b12a6ccce03ad84464c395667a829fcbf`

Yeniden derleme veya kaynak değişikliği kimlikleri değiştirebilir; sonraki ölçümde `build.json` esas alınır. `provenance/offline-validation.json` bu kontrolün kaydını tutar. Ayrıntılı compiler komutları ve kaynak hash'leri `firmware/build/<config>/` altındadır.

## Test kapsamı

- Yedi konfigürasyonun protokol doğrulaması; hedef/clock/build/ACK kimliği.
- Eksik, tekrarlı veya sırası bozuk mesaj kimliği; bozuk bayrak ve negatif zaman değeri.
- attempted/accepted/failed/consumed tutarlılığı, tamamlanmamış drain.
- UART hata/drop sayacı ve sıfır stack headroom reddi.
- FNV-1a için bilinen vektör; hatalı trace checksum, offset, sonlandırma ve run kimliği.
- Trace kaybının geçersiz olarak işaretlenmesi.
- Parçalı seri okuma -> dosya oluşturma; başarısız latency alanının boş kalması.
- Başarısızların gecikme ortalamasından çıkarılması; boş grubun N/A olması.
- Tam yedi koşuluk oturum -> analiz raporu; sonradan değişmiş CSV, trace veya metadata'nın reddi.
- Gerçek bağlanmış binary'de Reset, HardFault, SVC, PendSV, SysTick ve USART2 vektörleri; Thumb bitleri, başlangıç stack adresi ve Default_Handler'a yanlış bağlantı kontrolü.

Protokol testleri sentetik veriyi yalnız geçici test klasörlerinde kullanır. Sahte trace byte'larının SystemView kaydı olduğu iddia edilmez; bunlar taşıma/checksum testidir. Scheduler'ın gerçek bloklanması ve queue olaylarının SystemView'de çözülmesi henüz doğrulanmadı.

## Kaynak incelemesi ve port kararları

- HSE 8 MHz, PLL 8/336/2/7, SYSCLK 168 MHz; APB1 42 MHz, APB2 84 MHz.
- TIM2 clock APB1 prescaler nedeniyle 84 MHz; PSC=83 ile nominal 1 MHz. L476'nin CPU clock üzerinden kurulan prescaler hesabı doğrudan taşınmadı.
- F407 startup/linker ve HAL/CMSIS önceki projeden; kernel ve SystemView adaptörü aynı Hafta 3 FreeRTOS 11.1.0 paketinden.
- USART2 IRQ önceliği 6, syscall eşiği 5; RX callback FromISR queue kullanıyor.
- Bu portta `portYIELD_FROM_ISR` trace çıkışı da ürettiğinden callback yalnız `portYIELD` ile PendSV ister; board handler tek ISR çıkışını kaydeder. Hata IRQ yolu da aynı handler'dan çıkar.
- SysTick trace'i FreeRTOS portunda mevcut; ikinci enter/exit eklenmedi. Trace stop muhasebesi ISR maskesiyle korunuyor.
- Queue beklemeleri kritik bölge dışında; ölçüm anında mesaj başına UART çıktısı yok. Sonuç servis tamamlandıktan sonra aktarılıyor.

## Kartta tamamlanacaklar

`DONANIM_TESTI.md` adımları: flash/read-back, HELLO/BUILD, 44 girişimlik pilot, tam yedi koşu, gerçek SystemView API/W3 çözümleme, üç işaretli görsel, sonuç yorumu ve video. HSE'nin başlaması, fiziksel UART hattı, gerçek timer ölçeği ve task zamanlaması yalnız derlemeyle doğrulanamaz.
