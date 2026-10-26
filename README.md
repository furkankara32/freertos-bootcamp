# FreeRTOS Bootcamp

STM32F407 ile FreeRTOS ödevleri, kaynak kodları ve gerçek kart ölçümleri.

| Hafta | İçerik |
|---|---|
| [Hafta 01](hafta-01/) | V1/V2 uygulamaları, arayüz, testler ve ilk ölçümler |
| [Hafta 02](hafta-02/) | SEGGER SystemView entegrasyonu; V1/V2 S0 ve S5 gözlemleri |
| [Hafta 05](hafta-05/) | StreamBuffer, Event Group, task notification; dört UART/LED deneyi |

## Hafta 05 raporu

- [Deney raporu](hafta-05/reports/Hafta5_Rapor.md)
- [PDF raporu](hafta-05/reports/Hafta5_Rapor.pdf)
- [Kurulum, kullanım ve kayıtlar](hafta-05/README.md)

## Hafta 02 raporları

- [V1 — S0 ve S5](hafta-02/reports/V1_S0_S5.md)
- [V2 — S0 ve S5](hafta-02/reports/V2_S0_S5.md)
- [V1 ↔ V2 karşılıklı senaryo karşılaştırması](hafta-02/reports/V1_V2_Karsilastirma.md)
- [Şartname](hafta-02/specs.md)

Sonraki haftalar `hafta-03/`, `hafta-04/` şeklinde aynı repoya eklenir. Git kökü bu dizindir; haftalar ayrı Git repoları değildir.

## Geçmiş ve araçlar

Repo daha önce `hafta-01` adındaydı. Eski commit geçmişi korunmuştur; klasör düzeni yeni commit ile değiştirilmiştir. Eski commit'lerde Hafta 01 dosyaları kök dizinde bulunur.

V1 kaynak commit: `b74863a3a27ebeb14ca932737005b68d9eee1945`.
V2 kaynak commit: `32f7e1dfeb69075d02084f08b4596d8febdccfb4`.

Sanal ortamlar, indirilen araç paketleri, IDE çalışma alanları, derleme çıktıları ve tam RAM/flash yedekleri repoya dahil değildir. Ölçüm dump'ları, SystemView kayıtları ve rapor kanıtları saklanır. Bilgisayara özgü yollar tarihsel log ve metadata içinde bulunabilir; yeni bir bilgisayarda araç yolları uyarlanmalıdır.
