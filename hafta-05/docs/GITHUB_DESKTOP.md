# GitHub Desktop ile gönderme

Bu hafta ayrı bir repo değildir. GitHub Desktop'ta mevcut `freertos-bootcamp` reposunu açın; listede yoksa **File > Add local repository** ile `D:\freertos-bootcamp` klasörünü seçin.

1. Changes bölümünde kök README ve `hafta-05/` değişikliklerini inceleyin.
2. Önerilen commit başlığı: `Hafta 5: UART ve FreeRTOS senaryolari, arayuz ve deney raporu`.
3. **Commit to main** yapın; ardından **Push origin** kullanın. Uzak repo: `https://github.com/furkankara32/freertos-bootcamp.git`.

Hazırlık sırasında commit veya push yapılmadı. Kaynaklar, üçüncü taraf lisansları, testler, raporlar ve güncel dört senaryonun kayıtları dahildir. Vendor kaynakları nedeniyle dosya sayısı yüksektir. EXE ve `_internal`, derleme çıktıları, sanal ortam, yerel ayarlar, kısayol, eski pilot ve `.pending` kayıtları dahil değildir.

Son kullanıcı kayıtları: S1 referans, S2 hatalı polling, S3 parçalı iş düzeltmesi, S4 Queue tüketimi düzeltmesi. Tek-kayıt politikası gereği tüm varyantların ayrı ham kaydı yoktur; otomatik karşılaştırma sonuçları raporda korunur.

Yeni kayıt alınırsa records/Sx dosyaları Git'te değişiklik olarak görünür. Yeni ölçüm sonrasında raporun aynı sonuçları anlattığını varsaymayın; rapor tarihi ve evidence-manifest.json dosya hash'leri ile kontrol edin.
