window.SLIDES = [
  {
    "section": "Hafta 03 / Ödev",
    "title": "Kuyruk dolunca<br><span class=\"accent\">sistemim ne yapıyor?</span>",
    "lead": "Ölçülen davranışı tek bir tasarım değişikliğiyle açıklayın.",
    "body": "<div class=\"grid\"><div><p>Yeni bir proje yazmak yerine önceki projenizdeki veri yolunu kullanın. Üretici ve tüketici arasındaki kuyruğu kontrollü yükle sınayın.</p><div class=\"callout\">Hedef en küçük süreyi elde etmek değil; kabul, kayıp, gecikme ve bekleme arasındaki ilişkiyi göstermek.</div></div><div class=\"panel\"><div class=\"hero-number\">03</div><h2>7 koşu · 1 karşılaştırma tablosu</h2><p>Kaynak + CSV + iz kaydı + kısa anlatım</p></div></div>",
    "note": "Teslim tarihi bu pakette atanmaz; eğitmen duyurusuyla kesinleşir. Bu ödev önceki analizin üzerine kuruludur."
  },
  {
    "section": "01 / Başlangıç",
    "title": "Aynı projeden devam edin.",
    "lead": "Kurulumla uğraşmaktan çok veri akışını anlamaya zaman ayırın.",
    "body": "<div class=\"grid\"><div class=\"panel\"><h2>Kendi projeniz</h2><p>Bir üretici–tüketici yolu seçin. Queue’nun kapasitesini ve bekleme politikasını deney için değiştirin.</p><p>Önceki sürümü bir commit/tag ile koruyun.</p></div><div class=\"panel\"><h2>Referans seçeneği</h2><p>Hafta 3 firmware’ini kullanabilirsiniz. Kart ve pinler STM32L476RG için hazırdır.</p><p>Kaynağı belirtin; kendi değişikliğinizi açıkça ayırın.</p></div></div><div class=\"callout\">SystemView veya önceden kullandığınız analiz aracından biri yeterli. İkinci araç karşılaştırması isteğe bağlı.</div>",
    "note": "Farklı kart kullananlar saat, pin ve ölçüm ayrıntılarını yazmalı. Mutlak süreleri kartlar arasında yarışa dönüştürmeyin."
  },
  {
    "section": "01 / Ön çalışma",
    "title": "Veri yolunu çizmeden ölçmeyin.",
    "lead": "Beş soruya kısa cevap verin.",
    "body": "<div class=\"flow\"><div class=\"node\">Kim üretiyor?</div><span class=\"arrow\">→</span><div class=\"node\">Ne gönderiyor?</div><span class=\"arrow\">→</span><div class=\"node\">Kaç eleman?</div><span class=\"arrow\">→</span><div class=\"node\">Kim tüketiyor?</div></div><div class=\"panel\"><h2>Ek sorular</h2><p>Queue boşken tüketici ne yapıyor?</p><p>Queue doluyken üretici ne yapıyor?</p><p>Gönderim başarısızlığı nerede sayılıyor?</p><p>Gönderilen şey struct kopyası mı, pointer mı?</p></div>",
    "note": "Çizim için özel araç gerekmiyor. Basit şema veya okunaklı fotoğraf kabul edilebilir. Veri sahipliğini doğru ifade etmesi önemli."
  },
  {
    "section": "02 / Deney tasarımı",
    "title": "Üç varyant; iki kontrollü karşılaştırma.",
    "lead": "A/B’de kapasite, A/C’de gönderme bekleme süresi değişir.",
    "body": "<div class=\"table-wrap\"><table><thead><tr><th>Varyant</th><th>Kapasite</th><th>Gönderme beklemesi</th><th>Değişen tek etken</th></tr></thead><tbody><tr><td>A</td><td>4 mesaj</td><td>0 tick</td><td>Başlangıç</td></tr><tr><td>B</td><td>16 mesaj</td><td>0 tick</td><td>A → B: kapasite</td></tr><tr><td>C</td><td>4 mesaj</td><td>20 ms → tick</td><td>A → C: bekleme politikası</td></tr></tbody></table></div><div class=\"callout\">Öncelikleri, item boyutunu, tüketici davranışını ve yük tarifini karşılaştırma boyunca aynı tutun.</div>",
    "note": "B/C iki değişkeni birden içerir; tek etkenin etkisini kanıtlamak için A/B ve A/C kullanılır. Hafta 2 varyantlarını bu tanımlarla karıştırmayın."
  },
  {
    "section": "02 / Yük protokolü",
    "title": "Normal ve yoğun yükü ayırın.",
    "lead": "Her koşuda toplam 44 gönderme girişimi.",
    "body": "<div class=\"grid\"><div class=\"panel\"><h2>Normal</h2><p>44 mesaj.</p><p>Her gönderme girişiminden sonra 100 ms bekleyin.</p><p>Tüketicinin servis beklemesi 20 ms.</p></div><div class=\"panel\"><h2>Yoğun</h2><p>10 normal mesaj.</p><p>24 art arda gönderme girişimi.</p><p>10 normal mesaj.</p><p>C’de bloklayan send burst süresini uzatabilir.</p></div></div><div class=\"callout\">Kendi projede farklı servis süresi gerekiyorsa sebebini yazın; altı koşul boyunca değiştirmeyin. Farklı yükü referansın birebir sonucu gibi sunmayın.</div>",
    "note": "Referans 20 ms’yi vTaskDelay ile temsil eder. CPU yükü değildir. Gerçek UART kullanan öğrenci bu ayrımı raporunda belirtmelidir."
  },
  {
    "section": "02 / Kayıt matrisi",
    "title": "Altı temel koşu + iz etkisi.",
    "lead": "İz açık/kapalı karşılaştırması aynı A/yoğun yükte yapılır.",
    "body": "<div class=\"table-wrap\"><table><thead><tr><th>Kayıt</th><th>Varyant</th><th>Yük</th><th>Trace</th></tr></thead><tbody><tr><td>01</td><td>A</td><td>Normal</td><td>Açık</td></tr><tr><td>02</td><td>B</td><td>Normal</td><td>Açık</td></tr><tr><td>03</td><td>C</td><td>Normal</td><td>Açık</td></tr><tr><td>04</td><td>A</td><td>Yoğun</td><td>Açık</td></tr><tr><td>05</td><td>B</td><td>Yoğun</td><td>Açık</td></tr><tr><td>06</td><td>C</td><td>Yoğun</td><td>Açık</td></tr><tr><td>07</td><td>A</td><td>Yoğun</td><td>Kapalı</td></tr></tbody></table></div><div class=\"callout\">Zamanınız varsa yoğun yük koşularını üçer kez tekrarlayın; tekrarlar arasındaki değişimi tartışın. Zorunlu asgari kapsam 7 koşudur.</div>",
    "note": "Trace kapalı olsa da TIM2 sayaçları ve CSV ölçümleri açık kalır. Bu karşılaştırma izleme açık/kapalı etkisidir; derleme konfigürasyonları arasında tüm binary maliyetini ölçmez."
  },
  {
    "section": "03 / Ölçüm",
    "title": "Kaybolan mesajı ortalamadan gizlemeyin.",
    "lead": "Sayaçları ve süreleri birlikte raporlayın.",
    "body": "<div class=\"table-wrap\"><table><thead><tr><th>Alan</th><th>Tanım</th></tr></thead><tbody><tr><td>attempted</td><td>Gönderme girişimi sayısı</td></tr><tr><td>accepted / failed</td><td>Kuyruğa alınan / başarısız girişim</td></tr><tr><td>consumed</td><td>Servisi tamamlanan mesaj</td></tr><tr><td>send_call_us</td><td>Gönderme çağrısının duvar saati süresi</td></tr><tr><td>generation_to_receive_us</td><td>Üretimden consumer’ın almasına kadar gecikme</td></tr></tbody></table></div><div class=\"callout\">Koşu bittiğinde: attempted = accepted + failed. Kuyruk boşaltılıp servis bitince accepted = consumed. Başarısız olayın gecikmesini 0 yapmayın.</div>",
    "note": "Kuyruğu drain etmeden consumed ile accepted eşitliğini aramayın. Fail durumlarını ayrıca sayın; başarılıların ortalama ve maksimumunu verin."
  },
  {
    "section": "03 / ST-LINK akışı",
    "title": "İz dosyanızı doğru pencereden alın.",
    "lead": "Bu referans, yoğun yükte 11. mesajdan önce 200 ms kayıt başlatır.",
    "body": "<div class=\"flow\"><div class=\"node\">Deneyi çalıştır</div><span class=\"arrow\">→</span><div class=\"node\">Bitişi bekle</div><span class=\"arrow\">→</span><div class=\"node\">Son izi karttan al</div><span class=\"arrow\">→</span><div class=\"node\">.SVDat indir</div><span class=\"arrow\">→</span><div class=\"node\">SystemView’de aç</div></div><div class=\"callout\">CSV 44 mesajın tamamını kapsar; trace yalnız kısa pencereyi kapsar. Pencerede görünmeyen sonraki bir mesaj için “çalışmadı” sonucu çıkarılamaz.</div><div class=\"panel\"><h2>Geçerlilik</h2><p>İz kayıp sayacı, byte sayısı, checksum ve durma nedeni metadata içinde tutulur.</p><p>Yeni koşu karttaki eski izi değiştirir; önce dosyanızı kaydedin.</p></div>",
    "note": "Arayüz checksum bozuk dosyayı kaydetmez. Kayıp sayacı sıfırdan büyükse dosya eksik olarak etiketlenir; daha kısa pencereyle tekrar alın."
  },
  {
    "section": "03 / Kanıt",
    "title": "Üç görsel; üç açıklama.",
    "lead": "Her görselde koşu kimliği, mesaj kimliği ve zaman aralığı görünsün.",
    "body": "<div class=\"grid three\"><div class=\"panel\"><h2>A / yoğun</h2><p>Dolu kuyrukta en az bir başarısız send gösterin.</p></div><div class=\"panel\"><h2>B / yoğun</h2><p>A’ya göre kabul ve bekleme farkını yorumlayın.</p></div><div class=\"panel\"><h2>C / yoğun</h2><p>Üreticinin queue üzerinde bloklanmasını ve consumer’ın ilerlemesini gösterin.</p></div></div><div class=\"callout\">Beklediğiniz olay görünmediyse sonucu uydurmayın. Pencereyi, yükü ve varsayımı kontrol edip nedenini yazın.</div>",
    "note": "SystemView API olaylarını ve W3 kullanıcı olaylarını birlikte kullanın. Tek ekranda bütün deneyi sıkıştırmak yerine okunur üç pencere seçin."
  },
  {
    "section": "04 / Sonuç",
    "title": "Ölçümden karar çıkarın.",
    "lead": "Bir sayfalık yorumda şu soruları cevaplayın.",
    "body": "<div class=\"panel\"><h2>Tartışma soruları</h2><p>① B daha fazla mesaj kabul etti mi? Bunun gecikme bedeli ne oldu?</p><p>② C’de üretici ne kadar bekledi? Bu, üreticinin diğer işlerini nasıl etkileyebilir?</p><p>③ Trace açık/kapalı koşulları arasında ne fark gördünüz?</p><p>④ Kendi uygulamanız için hangi politikayı neden seçersiniz?</p><p>⑤ Ölçümünüz hangi durumları kapsamıyor?</p></div><div class=\"callout\">“Daha hızlı oldu” yerine hangi süreyi, hangi koşulda, hangi veriyle karşılaştırdığınızı söyleyin.</div>",
    "note": "Gözlenen maksimumu hard real-time garantisi olarak yazmayın. İyileşme çıkmaması tek başına başarısız ödev değildir; doğru yöntem ve açıklama önemlidir."
  },
  {
    "section": "04 / Teslim",
    "title": "Az dosya; güçlü kanıt.",
    "lead": "Tekrar çalıştırılabilen bir teslim hazırlayın.",
    "body": "<pre><code>hafta-03/\n  firmware/          # kaynak ve proje dosyaları\n  measurements/      # 7 koşunun CSV + ham seri + metadata\n  traces/            # özgün iz dosyaları\n  analysis/          # tablo, 3 işaretli görsel, 1 sayfa yorum\n  README.md          # kart, sürümler, çalıştırma, commit\n  ai-usage.md        # alınan destek ve doğrulama</code></pre><div class=\"callout\">3–5 dakikalık videoda bir mesajı iz üzerinden açıklayın. Kod GitHub’a, video ve bağlantı mevcut kurs teslim kanalına. Tarih eğitmen duyurusuyla kesinleşir.</div>",
    "note": "Sadece screenshot veya binary yeterli değildir. Referans kullanımı serbest; neyin öğrenciye ait olduğu açıkça belirtilir."
  },
  {
    "section": "04 / Değerlendirme",
    "title": "Puan hız rekoruna verilmez.",
    "lead": "Çalışan kod, kontrollü deney ve doğru açıklama değerlendirilir.",
    "body": "<div class=\"table-wrap\"><table><thead><tr><th>Ölçüt</th><th>Puan</th></tr></thead><tbody><tr><td>Queue kullanımı ve dönüş değerleri</td><td>30</td></tr><tr><td>Kontrollü deney ve doğru ölçüm</td><td>30</td></tr><tr><td>İz üzerinden neden–sonuç açıklaması</td><td>25</td></tr><tr><td>Tekrar üretilebilir teslim</td><td>15</td></tr><tr><td>Toplam</td><td>100</td></tr></tbody></table></div><div class=\"callout\">İkinci araç, farklı kart veya ek arayüz tam puan için şart değildir.</div>",
    "note": "Teknik sınırlamayı dürüstçe raporlamak ödüllendirilmelidir. Başarısız sonuç saklamak veya sentetik veriyi donanım ölçümü diye sunmak doğru deney değildir."
  },
  {
    "section": "05 / Son kontrol",
    "title": "Göndermeden önce.",
    "lead": "Bir arkadaşınız yalnız README ile deneyi tekrar çalıştırabilir mi?",
    "body": "<div class=\"grid\"><div class=\"panel\"><h2>Veri</h2><p>7 koşu ve ayarları belli mi?</p><p>Sayaçlar tutarlı mı?</p><p>Trace penceresi ve kayıp durumu yazılı mı?</p><p>Ölçülen firmware sürümü belli mi?</p></div><div class=\"panel\"><h2>Anlatım</h2><p>A/B ve A/C ayrı mı?</p><p>Başarısız olaylar görünür mü?</p><p>3 görsel okunaklı mı?</p><p>Seçilen politikanın bedeli açık mı?</p></div></div><div class=\"callout\"><a href=\"ders-03.html\">Derse dön</a> · <a href=\"interface/index.html\">Kayıt masası</a> · <a href=\"docs/SystemView_Kurulum.html\">Kurulum rehberi</a></div>",
    "note": "Ödevi canlı ders sonunda bu kontrol listesiyle özetleyin. Öğrencilerin bütün ölçüm altyapısını baştan yazması gerekmiyor."
  }
];
