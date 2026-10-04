# Yapay zekâ kullanımı

Specs/kurs karşılaştırması, yerel firmware incelemesi, uygulama mimarisi, C firmware, Python/PySide6 arayüz, protokol parser’ı, testler, build/paketleme script’leri ve bu belgeler Codex desteğiyle hazırlandı.

Kontrol: yerel HAL UART DMA→TC ve CMSIS→native priority eşlemesi okundu; ARM GCC ile derleme, protokol/fault-input testleri, Qt demo uçtan uca testi, görsel kontrol ve ST-LINK flash doğrulaması yapıldı. Gerçek kart deneylerinin kapsamı ve eksikleri `docs/review/implementation-status.md` ve `analysis/report.md` içinde yazılır.

Değiştirilen öneriler: kernel yükseltmek yerine kurulu `vTaskDelayUntil` API’si; stack/heap bütçelerini artırma; TX sahipliğini tek görevde tutma; GUI offscreen font sorunu için paketlenebilir Unicode font; sentetik verileri ayrı dizin ve etiketle saklama.

Kullanıcı teslimden önce ISR/task/TC akışını, zaman sınırlarını, hata yollarını ve ölçüm yorumlarını kendi sözleriyle açıklamalıdır. Sentetik sonuçlar gerçek kart ölçümü olarak sunulmaz. AI desteği bağımsız zaman doğruluğu veya worst-case garantisi değildir.
