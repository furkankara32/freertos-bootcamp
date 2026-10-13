# Hafta 03 - Donanım ölçüm karşılaştırması

Build kimliği: `81f84d3135e5bc8a88101ae85466e23d0009cc9ff12c5d22767f9200c2d6b1c6`

Süreler us cinsindedir. Send sütunu başarılı girişimleri, gecikme sütunu alınan mesajları kullanır. Başarısızlar gecikme ortalamasına sıfır olarak katılmaz.

| Koşu | Varyant/yük | Trace | Kabul / başarısız / tamamlanan | Send ort./maks. | Gecikme ort./maks. |
|---|---|---|---|---|---|
| 3 | A/NORMAL | 1 | 44 / 0 / 44 | 12.16 / 19.00 | 33.82 / 52.00 |
| 5 | B/NORMAL | 1 | 44 / 0 / 44 | 12.16 / 19.00 | 33.82 / 52.00 |
| 7 | C/NORMAL | 1 | 44 / 0 / 44 | 12.16 / 19.00 | 33.82 / 52.00 |
| 4 | A/BURST | 1 | 24 / 20 / 24 | 12.42 / 19.00 | 5036.38 / 59929.00 |
| 6 | B/BURST | 1 | 36 / 8 / 36 | 11.92 / 19.00 | 78299.53 / 299765.00 |
| 8 | C/BURST | 1 | 34 / 10 / 34 | 31.79 / 80.00 | 27112.56 / 80140.00 |
| 9 | A/BURST | 0 | 24 / 20 / 24 | 11.33 / 12.00 | 5034.75 / 59973.00 |

## Kontrollü farklar

Farklar ikinci koşul eksi ilk koşuldur; tek örnek nedensellik için zaman çizgisiyle birlikte değerlendirilmelidir.

- NORMAL A/B kapasite: kabul farkı +0; başarılı send ortalaması farkı 0.00 us; alınanların maksimum gecikme farkı 0.00 us.
- NORMAL A/C bekleme: kabul farkı +0; başarılı send ortalaması farkı 0.00 us; alınanların maksimum gecikme farkı 0.00 us.
- BURST A/B kapasite: kabul farkı +12; başarılı send ortalaması farkı -0.50 us; alınanların maksimum gecikme farkı 239836.00 us.
- BURST A/C bekleme: kabul farkı +10; başarılı send ortalaması farkı 19.38 us; alınanların maksimum gecikme farkı 20211.00 us.
- BURST A trace OFF/ON: kabul farkı +0; başarılı send ortalaması farkı 1.08 us; alınanların maksimum gecikme farkı -44.00 us.

## Kayıt kapsamı

CSV 44 girişimin tamamını, SystemView nominal 200 ms pencereyi kapsar. C’de enqueue öncesi bekleme gecikmeye dahildir. vTaskDelay dış servis beklemesi modelidir. Gözlenen maksimum kesin üst sınır değildir.

- run 3: `A_NORMAL_trace1.json`; trace 11704 bayt, drops=0, stop_reason=1.
- run 5: `B_NORMAL_trace1.json`; trace 11704 bayt, drops=0, stop_reason=1.
- run 7: `C_NORMAL_trace1.json`; trace 11704 bayt, drops=0, stop_reason=1.
- run 4: `A_BURST_trace1.json`; trace 12514 bayt, drops=0, stop_reason=1.
- run 6: `B_BURST_trace1.json`; trace 12202 bayt, drops=0, stop_reason=1.
- run 8: `C_BURST_trace1.json`; trace 15326 bayt, drops=0, stop_reason=1.
- run 9: `A_BURST_trace0.json`; trace kapalı.

## İnsan incelemesi gereken kanıt

CSV sonuç yorumu ve politika değerlendirmesi `analysis/yorum.md` içindedir; kayıtlar yenilenirse yorum da güncellenmelidir. Üç SystemView görseli ayrıca hazırlanmalıdır. Bu otomatik rapor scheduler olaylarını decode etmez; bloklanmayı kendiliğinden kanıtlamaz.
