# Ölçümler

Güncel kayıtlar `hardware/` altında tutulur. Her varyant/yük/trace seçimi için tek dosya takımı vardır: örneğin `A_NORMAL_trace1.csv`, `.txt`, `.json`, `.SVDat`. Aynı senaryonun başarılı tekrarı bu dosyaları değiştirir. Trace kapalı senaryoda SVDat yoktur.

CSV: UTF-8 BOM, noktalı virgül ayıracı; Türkçe Excel içinde sütunlara ayrılır. Özet rapordaki ondalık ayıracı virgüldür. Yeniden kayıt öncesinde açık CSV/SVDat dosyasını kapat.

Başarısız deneme önceki geçerli kaydı değiştirmez. Son hatanın `.failed.txt` / `.failed.json` dosyaları üzerine yazılır, başarılı tekrarda kaldırılır. Eski başarılı kaydın zamanı JSON içindeki `captured_utc` alanından kontrol edilir.

`tools/run_matrix.py` aynı klasörde yedi senaryoyu yeniler; `session.json` tamamlanma ve koşu indeksini tutar. Tamamlanınca `python tools/analyze.py measurements/hardware` çalıştır. Raporu yeni ölçümlerden sonra yeniden üret.

13 Ekim 2026: mevcut A/NORMAL kaydı sabit ada ve yeni CSV biçimine dönüştürüldü; 44 satır/6 sütun doğrulandı. Ham seri ve SystemView baytları korundu; CSV hash'i güncellendi. Tarihli eski hardware kayıtları temizlendi. Ayrı `pilot` dizinleri geçmiş doğrulama kanıtlarıdır.

Test verileri yalnız geçici dizinlerde üretilir. `kaynak/Hafta_3/measurements` L476 eğitmen kayıtlarıdır; öğrenci ölçümü değildir.
