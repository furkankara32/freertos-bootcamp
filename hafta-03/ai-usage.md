# AI kullanımı ve doğrulama

12 Ekim 2026 tarihinde Codex desteğiyle ders paketi okundu, konu anlatımı PDF'si ve spec hazırlandı. Kullanıcının kart düzeltmesi üzerine STM32F407G-DISC1 için firmware portu, build aracı, seri kayıt/matris/analiz araçları, testler ve çalışma belgeleri oluşturuldu.

Hafta 3'ün deney algoritması ve SystemView entegrasyonu verilen referanstan türetildi. STM32F4 HAL, CMSIS, startup ve linker temeli önceki Hafta 1 projesinden alındı. Kart saat/pin düzeni önceki proje kaynakları ve ST kart kılavuzuyla karşılaştırıldı. FreeRTOS 11.1.0 bu haftanın referansından korundu; önceki 10.3.1 kernel'iyle karıştırılmadı.

Doğrulama: ARM Release/Debug derlemeleri; protokolün yanlış hedef/build, eksik satır, sayaç, checksum, trace kaybı, parçalı seri okuma ve istatistik yollarının masaüstü testleri. Son durum `docs/DOGRULAMA.md` içindedir.

**İlk hazırlık aşamasında kullanıcı donanımı henüz bağlamayacağını belirtti. Kart bağlantısı, flash, gerçek ölçüm, SystemView olaylarının hedefte doğrulanması veya video kaydı yapılmadı.** Sentetik test örnekleri gerçek sonuç olarak kullanılmadı. Bu eksikler sonraki fiziksel doğrulama oturumunda kapatılacak ve bu kayıt güncellenecektir.

## İlk donanım pilotu

Kullanıcının bağlantılar hazır onayı üzerine 12 Ekim 2026 tarihinde eski flash yedeklendi, Release firmware programlandı/doğrulandı ve yalnız A/NORMAL koşusu alındı. Sayaç ve aktarım doğrulamaları geçti. SystemView GUI kontrolü odak/iletişim kutusu otomasyon sorunu nedeniyle tamamlanmadı. Gerçek kanıt ve sınırlar `docs/PILOT_TESTI.md` içinde.

## 13 Ekim 2026 — gerçek CSV analizi

Kullanıcının aldığı yedi donanım kaydı Codex desteğiyle karşılaştırıldı. 308 CSV satırının her alanı ham protokolle eşleştirildi; hash, firmware kimliği, sayaçlar, trace bütünlüğü ve istatistikler doğrulandı. Ayrı koşular session.json ile indekslendi, analysis/comparison.csv ve comparison.md üretildi, analysis/yorum.md gerçek sonuçlarla tamamlandı. Politika seçimi raporda açık bir uygulama varsayımına bağlandı. Ölçümler değiştirilmedi veya yeniden alınmadı. Üç SystemView görseli ve video üretilmedi; CSV verilerinden kesin scheduler olay sırası iddia edilmedi.
