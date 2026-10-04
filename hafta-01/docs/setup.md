# Kurulum ve deney ayarları

Hedef STM32F407G-DISC1 / STM32F407VGT6. USB üzerinden ST-LINK güç/programlama; ayrı USB–TTL adaptörü USART2 için kullanılır. Gerçek testte adaptör COM5 (Prolific), ST-LINK VCP COM12 olarak görüldü; numaralar başka bilgisayarda değişebilir.

| Kart | TTL adaptörü |
|---|---|
| PA2 — USART2 TX | RX |
| PA3 — USART2 RX | TX |
| GND | GND |

3,3 V lojik kullanın. UART için adaptörün VCC çıkışını karta bağlamak gerekmez; ortak GND gerekir. USB–TTL TX/RX isimleri adaptör bakış açısındadır, çapraz bağlanır. Fiziksel deney butonu PA0 / mavi USER’dır. Reset butonu farklıdır ve RAM kayıtlarını siler.

## Saatler ve FreeRTOS

- HSE 8 MHz; PLL M=8, N=336, P=2, Q=7; SYSCLK 168 MHz.
- APB1 42 MHz; TIM5 saati 84 MHz, PSC=83, ARR=0xFFFFFFFF; serbest 32 bit 1 MHz sayaç.
- TIM3 HAL tick, SysTick RTOS tick=1000 Hz; TIM5 bunların yerine geçmez.
- Üç CMSIS task oluşturulur, scheduler başlamadan native öncelikler Telemetry=3, Button=2, UART=1 yapılır. Idle ve kernel timer service uygulama görevi değildir.
- Başlangıç stack’leri görev başına 768 word (3072 B), heap_4=32768 B. Bu, specs’in önerilen ilk bütçelerinden bilinçli sapmadır: UART dump/printf ve newlib için alan bırakır. Son karar high-water/min-free-heap ölçümüyle verilir.
- EXTI0/USART2/DMA1 Stream5/6 öncelik 5; FreeRTOS syscall eşiği 5. TIM3/SysTick/PendSV 15.
- USART2 115200 8N1; TX DMA1 Stream6 Channel4 NORMAL. RX için bir bayt interrupt alımı; yapılandırılmış RX DMA başlatılmaz.
- `vTaskDelayUntil` kullanılır; projedeki V10.3.1 kernel’inde `xTaskDelayUntil` yoktur.

## Generate sonrası

`.ioc` TIM5 ve EXTI0 yapılandırmasını içerir. Uygulama `Src/app.c`, `Inc/app.h` altında; giriş çağrıları ve priority dönüşümleri USER CODE alanlarında. EXTI0’ın USER CODE kısmı t0 alır, pending flag’i temizler ve uygulamaya verir; sonraki HAL işleyicisi temizlenmiş bayrağı ikinci kez olaya dönüştürmez. Olay kabul kapısı scheduler/queue hazırlığından önce kapalıdır.

CubeMX yeniden üretimi bu oturumda çalıştırılmadı. Generate sonrası `.ioc`, TIM5 init, task stack/heap, USER CODE ve EXTI0 handler’ını diff ile kontrol edip yeniden derleyin. HAL/CMSIS/FreeRTOS kaynaklarını yeniden indirmeniz gerekmez.

## Araçlar

Doğrulanan standalone toolchain: GNU Tools for STM32 14.3.rel1, GCC 14.3.1; programlama: STM32CubeProgrammer 2.23.0. Python 3.12 ortamı ve tam bağımlılık sürümleri `interface/requirements.txt` içinde. Debug `-O0`, Release `-Os`; gerçek build metadata’sı ELF yanında `build.json` içinde.

İş yükü her START’ta S4/S5 için aynı binary üzerinde kalibre edilir: sabit iterasyon sayısı seçilir, ardından 100 ölçümün min/mean/max değerleri MET olarak saklanır. Kesmeler açıktır. Süreler duvar saatidir, kesin saf CPU süresi iddiası yoktur. Nihai ölçümlerde kalibrasyon sapmasını ve MCU/timer doğruluğunu inceleyin.

Boot mesajı yoktur; bağlantıda PC `HELLO,0` yollar. Yanıt yoksa doğru COM, çapraz TX/RX, ortak GND, reset sonrası çalışma ve başka programın portu kullanıp kullanmadığı kontrol edilir. Sadece portun açılması firmware ile haberleşildiği anlamına gelmez.
