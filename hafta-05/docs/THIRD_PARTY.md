# Üçüncü taraf kaynaklar

Firmware vendor kaynakları önceki hafta projesinden alınmıştır; ilgili telif ve lisans dosyaları korunmuştur. Yeniden dağıtılan kaynakların koşulları kendi lisanslarında bulunur:

- FreeRTOS: `firmware/vendor/freertos/LICENSE.md`.
- STM32 HAL: `firmware/vendor/Drivers/STM32F4xx_HAL_Driver/LICENSE.txt`.
- CMSIS ve STM32 cihaz desteği: `firmware/vendor/Drivers/CMSIS/LICENSE.txt`, `firmware/vendor/Drivers/CMSIS/Device/ST/STM32F4xx/LICENSE.txt`.
- SEGGER SystemView hedef kaynakları: `firmware/vendor/systemview/LICENSE.md`.
- SEGGER RTT: `firmware/vendor/rtt/LICENSE.md`.

STM32CubeIDE, SystemView masaüstü uygulaması ve Python/Qt kurulumları bu repoda paketlenmez. Python bağımlılık sürümleri requirements.txt içindedir. Uygulama kaynaklarına tüm vendor bileşenlerini kapsayan yeni bir genel lisans atanmadı.
