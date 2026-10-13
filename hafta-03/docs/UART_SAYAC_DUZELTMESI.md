# UART sayaç kapsamı düzeltmesi - 13 Ekim 2026

Kullanıcının `A_NORMAL_trace1_1791897400930513200.failed.txt` kaydında 44 girişim, 44 kabul, 0 başarısız, 44 tamamlanan ve trace drops=0 vardı. Doğrulama `#RX,1,0` nedeniyle durdu. Eski firmware RX sayaçlarını açılıştan beri biriktiriyordu; hatanın koşu öncesi mi sırasında mı gerçekleştiği bu kayıttan belirlenemez. Eski kayıt geçerli ölçüm olarak yeniden etiketlenmedi.

Yeni firmware koşu başlangıcındaki RX sayaçlarını atomik olarak alır. Rapor:

- `#RX`: koşu başlangıcından sonuç raporundaki sayaç okumasına kadar hata/drop farkı; sıfır değilse kayıt yine reddedilir.
- `#RX_BASE`: koşu öncesindeki birikmiş sayaçlar.
- `#RX_TOTAL`: rapor anındaki birikmiş sayaçlar.

Başlangıç ve toplam sayaçlar JSON'da korunur. Parser delta tutarlılığını da kontrol eder. Hata denetimi kapatılmadı; bağlantı geçmişiyle koşu hatası ayrıldı. SVDat aktarımı ayrıca FNV-1a, byte sayısı ve trace drop sayacıyla doğrulanır.

## Doğrulama

- 39 yazılım testi geçti; eski hata/koşu hatası ayrımı ve tutarsız sayaçlar sınandı.
- Release/Debug derlemeleri başarılı; Release vektör ve manifest kontrolü geçti.
- Yeni Release karta yüklendi ve read-back doğrulandı: `provenance/pilot/flash-rx-fix-20261013.log`.
- Yalnız bir A/NORMAL gerçek kontrol koşusu: **44/44 kabul ve tamamlanma, failed=0, RX delta=0/0, RX base=0/0, RX total=0/0, SEGGER drops=0**.
- Kayıt: `measurements/pilot-rx-fix/A_NORMAL_trace1_1791897520525153000.*`.
- Build: `81f84d3135e5bc8a88101ae85466e23d0009cc9ff12c5d22767f9200c2d6b1c6`.

Diğer senaryolar çalıştırılmadı. Yeni ölçüm matrisinin tamamı bu firmware ile alınmalı; eski build kayıtlarıyla aynı matris içinde karıştırılmamalı. Önceki doğrulama raporundaki build kimlikleri tarihsel kayıtlardır. Karta yeniden yükleme yapılmıştır; kullanıcı doğrudan capture komutunu çalıştırabilir.

`startup_lines` içinde tek BAD_COMMAND görülmesi yeni bağlantı eşlemesinde bilerek gönderilen geçersiz satırın yanıtı olabilir; bu donanım UART hata sayacı değildir. Koşu içindeki protokol hataları bastırılmaz.
