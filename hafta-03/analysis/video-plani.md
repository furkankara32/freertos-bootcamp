# 3-5 dakikalık video anlatım planı

Kayıt kart testinden sonra yapılacak; bu dosya video değildir.

| Süre | Gösterilecek içerik |
|---|---|
| 0:00-0:35 | STM32F4 Discovery, kendi kaynak uyarlaması, Producer -> Queue -> Consumer şeması |
| 0:35-1:10 | A/B/C ayarları, aynı 44 girişim ve sabit öncelikler; yalnız hangi etkenin değiştiği |
| 1:10-2:10 | C/BURST'te bir run/id: SEND_BEGIN, Producer Blocked, Consumer ilerlemesi, SEND_OK, RECEIVE/DONE görünüyorsa eşleştirme |
| 2:10-3:00 | A/BURST başarısız send ve B/BURST kapasite farkı; üç işaretli gerçek görsel |
| 3:00-3:45 | Sayısal tablo: accepted/failed, gecikme, send süresi; trace açık/kapalı farkı |
| 3:45-4:30 | Kendi politika seçimi ve bedeli; 200 ms pencere, tek koşu ve maksimum sınırları |

Hazır cümle yapısı: "Bu koşunun run değeri ..., mesaj kimliği ... . Producer burada ... API'sinde bekliyor. Consumer şu anda ... . CSV'deki ... süresi ... ölçüyor; servis tamamlanma süresiyle aynı değil."

Eksik olay trace penceresi dışında kalmışsa bunu açıkça söyle. Görülmeyen bir DONE olayını gösterilmiş gibi anlatma. Kaynak kullanımını ve AI desteğini kapanışta veya açıklama metninde belirt.
