# Başlangıç komut eşleme düzeltmesi - 13 Ekim 2026

Kullanıcının A/NORMAL girişimi HELLO aşamasında `#ERROR,BAD_COMMAND` ile durdu. RUN gönderilmedi; bu girişim geçerli bir senaryo ölçümü değildir. Özgün hata `measurements/hardware/A_NORMAL_trace1_1791897158395429900.failed.*` içinde korunuyor.

İncelemede COM5 üzerinden HELLO ve BUILD doğru döndü; karttaki Release build kimliği değişmemişti. İlk hatanın kesin nedeni kayıttan belirlenemiyor. Kartta kalan yarım komut satırı olası sebeplerden biridir; PC'nin `reset_input_buffer()` işlemi kartın komut tamponunu temizlemez.

`capture.py` artık HELLO öncesi önceki satırı geçersiz kılan bir kontrol karakteri ve satır sonu gönderir. Böylece yarım satır yeni HELLO ile birleşmez; tamponda bekleyen bir RUN satırı da tamamlanıp yanlışlıkla çalıştırılmaz. Yalnız başlangıçta BAD_COMMAND/LINE_TOO_LONG yanıtları sınırlı sayıda kabul edilir ve JSON içindeki `startup_lines` alanında korunur. Kimlik, BUILD ve sonraki deney hataları eskisi gibi işlemi durdurur; hatalar ölçümden gizlenmez.

Eklenen `--check-only`, HELLO/BUILD kontrolünden sonra portu kapatır; RUN göndermez. COM5 üzerinde bu mod başarılı oldu. 35 masaüstü testi geçti; başlangıç bozuk/uzun satırı, bilinmeyen hata reddi ve sonraki hataların yutulmaması sınandı. Yeni donanım senaryosu çalıştırılmadı. Firmware değişmedi; yeniden flash gerekmiyor.
