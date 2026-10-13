# Hafta 3 — STM32F4 kuyruk deneyleri sonuç raporu

## Deney ve doğrulama

13 Ekim 2026'da STM32F407G-DISC1 üzerinde alınan yedi gerçek kayıt karşılaştırılmıştır. CPU 168 MHz, FreeRTOS 11.1.0, tick 1 kHz, ölçüm sayacı 1 MHz; Producer/Consumer öncelikleri 2/1, mesaj 12 bayt, tüketici servis beklemesi 20 ms'dir. A: kapasite 4 / send beklemesi 0 ms; B: 16 / 0 ms; C: 4 / 20 ms. NORMAL her girişim sonrası 100 ms bekler; BURST, 10 normal + 24 art arda + 10 normal girişim içerir.

Kaynak: [measurements/hardware](../measurements/hardware/). Ayrı ayrı alınan kayıtlar yeniden deney yapılmadan [session.json](../measurements/hardware/session.json) ile indekslenmiştir. Kayıt zamanları Türkiye saatiyle 16:28:38–16:49:04; ortak firmware build kimliği: `81f84d3135e5bc8a88101ae85466e23d0009cc9ff12c5d22767f9200c2d6b1c6`.

308 CSV satırının tüm alanları ham seri verileriyle karşılaştırılmış, dosya hash'leri ve istatistikleri doğrulanmıştır. Her koşuda `attempted = accepted + failed = 44` ve `accepted = consumed` sağlanır. Koşu içindeki UART hata/kayıp sayaçları sıfırdır. Altı SystemView dosyasının baytları seri aktarımla eşleşir; trace drop sayıları sıfırdır. Bu kontroller zaman çizelgesinin görsel incelemesi değildir.

## Ölçüm özeti

Süreler **µs** cinsindedir (1.000 µs = 1 ms). Send ortalaması yalnız başarılı girişimleri, ulaşma ortalaması yalnız alınan mesajları kullanır. Reddedilen mesajın boş gecikmesi sıfır sayılmamıştır. Ulaşma süresi mesajın kendi servis beklemesini içermez.

| Koşu | Senaryo | Kabul / ret | Ret oranı | Başarılı send ort. / maks. | Ulaşma ort. / maks. |
|---|---|---|---|---|---|
| 3 | A/NORMAL, trace açık | 44 / 0 | %0 | 12,16 / 19 | 33,82 / 52 |
| 5 | B/NORMAL, trace açık | 44 / 0 | %0 | 12,16 / 19 | 33,82 / 52 |
| 7 | C/NORMAL, trace açık | 44 / 0 | %0 | 12,16 / 19 | 33,82 / 52 |
| 4 | A/BURST, trace açık | 24 / 20 | %45,45 | 12,42 / 19 | 5.036,38 / 59.929 |
| 6 | B/BURST, trace açık | 36 / 8 | %18,18 | 11,92 / 19 | 78.299,53 / 299.765 |
| 8 | C/BURST, trace açık | 34 / 10 | %22,73 | 31,79 / 80 | 27.112,56 / 80.140 |
| 9 | A/BURST, trace kapalı | 24 / 20 | %45,45 | 11,33 / 12 | 5.034,75 / 59.973 |

## 1. Kapasite etkisi: A ve B

NORMAL'de üç varyant da 44 mesajı kayıpsız almıştır. Yaklaşık 100 ms üretim aralığı, 20 ms servis beklemesine zaman bıraktığından bu yükte kapasite/bekleme artışının ölçülen kazancı yoktur.

BURST'te A yoğun bölümde mesaj 11–14'ü kabul etmiş, 15–34'ü reddetmiştir. Mesaj 12/13/14'ün ulaşma süreleri 19.959/39.944/59.929 µs'dir; yaklaşık 20 ms basamaklar tüketici servis beklemesiyle uyumludur. B yoğun bölümde 11–26'yı kabul etmiş, 27–34'ü reddetmiştir. Kapasite artışı toplam kabulü **24'ten 36'ya (+12)** yükseltmiş, maksimum gecikmeyi **59,929 ms'den 299,765 ms'ye** çıkarmıştır. Büyük kuyruk daha az ret, fakat daha uzun bekleme sağlamıştır. Ortalamalar farklı kabul kümelerine aittir; aynı mesaj kümesinin saf hız karşılaştırması değildir.

## 2. Gönderme beklemesi etkisi: A ve C

C, A'dan 10 fazla mesaj kabul etmiş; ancak **34 kabul / 10 ret** ile kayıpsızlık sağlamamıştır. Başarılı send ortalaması 31,79 µs ve maksimumu 80 µs iken başarısız 10 send'in ortalaması **19.905,90 µs**, maksimumu **19.914 µs**'dir. Yalnız başarılı çağrı ortalaması üreticinin bekleme maliyetini gizler. Tüm 44 çağrının ortalaması C'de **4.548,64 µs**, A'da **11,91 µs**; toplam çağrı süresi C'de **200,140 ms**, A'da **0,524 ms**'dir. Bunlar CPU kullanım süresi değil, çağrı içinde geçen duvar saati süreleridir.

Mesaj 11 ile 34'ün üretim zaman damgaları arasındaki fark A'da **339 µs**, C'de **180.071 µs** olmuştur; bu fark 34. mesajın kendi send süresini içermez. Bekleme, art arda üretim bölümünü uzatmıştır; aynı Producer task'ındaki sonraki işler de çağrı tamamlanana kadar ilerleyemez. C'nin 20 ms send timeout'u ile tüketicinin 20 ms servis beklemesi aynı mertebededir; tick ve görev zamanlaması önemlidir. CSV hangi scheduler olayının hangi timeout'a neden olduğunu tek başına kanıtlamaz; kesin olay sırası SystemView'de incelenmelidir. B/C karşılaştırmasında iki ayar birlikte değiştiği için sonuç tek etkene bağlanmaz.

## 3. SystemView kayıt etkisi: A/BURST açık ve kapalı

İki koşuda da 24 kabul / 20 ret vardır. Trace açıkken tüm send çağrılarının ortalaması **11,91 µs**, kapalıyken **9,41 µs**; fark **+2,50 µs**'dir. Başarılı send ortalaması farkı **+1,08 µs**, başarısız send ortalaması farkı **+4,20 µs**'dir. Ortalama ulaşma farkı **+1,625 µs**, maksimum farkı **−44 µs**'dir. Bu kayıt çiftinde send maliyeti daha yüksek görünmüş, kabul sayısı değişmemiştir; her gecikme ölçütünün artmaması tek tekrarın değişkenliğini de gösterir.

Bu değerler kesin bir ek yük yüzdesi veya CPU yükü ölçümü değildir. Trace kapalıyken hook kodu firmware'de kalır. Açık trace nominal 200 ms, CSV tüm koşuyu kapsar; bütün koşu ortalaması etkin kayıt penceresinin saf maliyeti değildir. UART aktarımı deneyden sonra yapılır; bilgisayardaki SEGGER arayüzünün yükü ölçülmez.

## 4. Politika seçimi

Bu rapor için uygulama varsayımım: üretici beklememeli, kısa yoğun yükte A'ya göre daha çok örnek saklanmalı ve yaklaşık 300 ms gözlenen gecikme kabul edilebilmelidir. **Bu varsayımla B'yi seçerim:** üreticide bekleme tanımlamadan 36/44 kabul sağlamıştır. Bedeli 16 mesajlık kapasite ve uzun kuyruk gecikmesidir. B de sekiz mesajı reddettiğinden kayıpsız uygulamaya yeterli değildir. Az bekleyen veri ve hızlı başarısızlık öncelikliyse A, üreticinin beklemesine izin veriliyorsa C değerlendirilebilir. Kesin gecikme sınırı veya kayıpsızlık için tüketim kapasitesi, yük ve hata politikası yeniden tasarlanmalıdır.

## 5. Sınırlar ve teslim kanıtı

Tek kart, tek firmware ve senaryo başına tek kayıt incelenmiştir. Gözlenen maksimum hard real-time üst sınırı değildir. Sürekli aşırı yük, gerçek çevrebirim servis süresi ve bütün kesme yükleri sınanmamıştır. **CSV analizi tamamlanmıştır; üç SystemView ekran görüntüsü ve 3–5 dakikalık video bu rapordan ayrı teslim kanıtlarıdır.** Zaman çizelgesi görsel olarak doğrulanmadığı için Producer'ın Blocked durumu görülmüş bir olay olarak sunulmamıştır.

Ayrıntılı sonuçlar: [comparison.csv](comparison.csv), [comparison.md](comparison.md), [validated-runs.json](validated-runs.json).

Sayısal raporu yeniden üretmek için: `python tools/analyze.py measurements/hardware --output analysis`. Senaryolar yeniden kaydedilirse bu yorumdaki sayılar da yeni sonuçlara göre güncellenmelidir.
