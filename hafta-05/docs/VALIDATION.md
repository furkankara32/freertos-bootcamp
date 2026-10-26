# Test ve dogrulama raporu

25 Ekim 2026, STM32F407G-DISC1, COM5, TTL TX -> PB11 / RX <- PA2; ST-LINK.

Firmware: `d19451555c74be55ef54dd0031091f765e67ad6bdbd34e666efc484e22ce79de`.

## Gercek kart senaryo testleri

| Senaryo | Varyant | LED gecisi | Maksimum gecikme (ms) | Bekleyen komut | Trace |
|---|---|---:|---:|---:|---|
| S1 | 0 | 32 | 0.865 | 0 | COMPLETE |
| S2 | 0 | 32 | 122.935 | 0 | COMPLETE |
| S2 | 1 | 32 | 0.866 | 0 | COMPLETE |
| S2 | 2 | 32 | 0.781 | 0 | COMPLETE |
| S3 | 0 | 32 | 153.803 | 0 | COMPLETE |
| S3 | 1 | 32 | 4.910 | 0 | COMPLETE |
| S4 | 0 | 36 | 0.971 | 3 | COMPLETE |
| S4 | 1 | 48 | 0.971 | 0 | COMPLETE |

Tum sekiz varyant beklenen davranis kontrollerini gecti. Hatali varyantin testten gecmesi, beklenen gecikme veya kuyruk problemini olusturdugu anlamina gelir; deadline hedefini sagladigi anlamina gelmez.

17 otomatik yazilim testi: protokol CRC/parcalama, kayit degistirme, kismi/yanlis trace, dosya tasima hatasinda geri alma, senaryolarin bagimsizligi, UI kapatma korumasi, firmware uyusmazligi, eski kosunun LED verisini dislama.

Gercek kart sinir testleri: bozuk cerceve sonrasi toparlanma, parcalanmis komut, alti gecersiz parametre, aktif kosu sirasinda START reddi, STOP ile aktif is ve kuyruk temizleme, 100.000 bayt RX yukunde sifir yeni kayip/hata. Sonuclar: `protocol-stress.json`.

## Kayit politikasi

Son paketlenmis EXE, `--smoke-test COM5` ile Qt olay dongusu uzerinden iki tam donanim kosusu yapti. Baglanti, RUN_START, LED olcumleri, STOP cevabi, ST-LINK trace ve ikinci kaydin ilkini degistirmesi dogrulandi. Sonuc: docs/interface-smoke.json (passed=true). Bu otomatik test offscreen calisir; gorsel yerlesim testi degildir.

Yeni tamamlanmis kayitlar records/S1, S2, S3, S4 altinda tutulur. Son test varyantlari: S1 V0, S2 V2, S3 V1, S4 V1. Yeni ayni-senaryo kaydi eski varyanti da degistirir. Tam ve eslesen trace alinmadan onceki kayit silinmez. Gecici basarisiz girisimler .pending altindadir. Eski pilot klasorlerinin silinmesi otomatik guvenlik denetimi tarafindan reddedildi; mevcut eski klasorler halen duruyor.

## Olcum sinirlari

- S1/S2/S3: LED basina 1000 ms ve her varyantta 32 gecis. S4: 100 ms ile kuyruk davranisi testi (36/48 gecis).
- SystemView tek penceresi 1,5 saniyedir; tum LED kosusunu kapsamaz. UART kaydi kosu boyunca surer. Tum test trace pencereleri COMPLETE, drop=0.
- UART bayt basina ISR ve FreeRTOS API giris/cikis ayrintilari RAM butcesi nedeniyle filtrelidir. Task cizelgesi ve uygulama olaylari tutulur.
- RX son bayttan komut kabule 50 ms kosulu icin ayri ISR zaman damgasi olcumu yoktur; bu hedef dogrulandi sayilmaz.
- GPIO yazilimsal zaman damgasi kullanilir; optik veya logic analyzer olcumu yapilmadi.
- Testler belirtilen yukleri kapsar; tum olasi kullanimlarda hatasizlik garantisi degildir.
