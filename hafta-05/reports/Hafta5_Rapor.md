# Hafta 5 - FreeRTOS deney raporu

26 Ekim 2026 | STM32F407G-DISC1 | UART, StreamBuffer, Event Group ve notification

## 1. Amaç ve sistem yapısı

Amaç, yalnız çalışan bir veri yolu kurmak değil; kontrollü hataların task zamanlamasına etkisini SystemView ile gözlemlemek ve düzeltmenin sonucunu ölçmektir. Dört senaryo incelenmiştir: doğru referans, polling TX, uzun parser işi ve Event Group/Queue ilişkisi.

Tek USB-TTL kullanılır: TTL TX -> PB11 (USART3 RX), TTL RX <- PA2 (USART2 TX), ortak GND. Hatlar 115200 baud, 8N1 çalışır. Programlama ve trace çıkarımı ST-LINK üzerinden yapılır; J-Link kullanılmaz.

Veri yolu: USART3 RX kesmesi -> RX StreamBuffer -> Parser -> CommandQueue + Event Group -> Execute -> ResultQueue + notification -> Report -> TX StreamBuffer -> USART2.

| Task | Öncelik | Görev ve bekleme |
|---|---|---|
| Parser | 4 | Paket/CRC kontrolü; komut aktarımı; veri yoksa StreamBuffer'da bekler. |
| Execute | 3 | LED durum makinesi; event veya sıradaki LED zamanını bekler. |
| Report | 2; S2'de 5 olabilir | Rapor üretir; normal TX'te tamamlanma notification'ını bekler. |

RX tamponu 4096 bayt, uyandırma eşiği 64 bayttır. TX tamponu 512 bayt; komut kuyruğu 8, sonuç kuyruğu 64 elemandır. Notification indeks 1 rapor işini, indeks 2 TX tamamlanmasını bildirir. FreeRTOS IDLE task'ını kendisi oluşturur. Büyük öncelik sayısı daha yüksek önceliktir.

## 2. S1 - Doğru çalışan referans

LED dizisi sürerken 100 adet 100 baytlık LOAD paketi gönderilir. Parser çerçeveyi kontrol edip LOAD sayısını artırır; her LOAD için Execute'a LED komutu göndermez. 10 KB'nin hatta aktarımı en az yaklaşık 0,87 saniye sürer. Parser mevcut baytları hızla işleyip tampon boşken bloklanır; IDLE çalışırken UART kesmeleri veri almaya devam eder.

Son kullanıcı kaydı: 100 LOAD paketi işlenmiş; RX/UART/parser hata sayaçları sıfır, tampon yüksek su seviyesi 64 bayt. 12 LED geçişinde en büyük gecikme **0,856 ms**. IDLE aralıkları, tek başına veri alımının durduğunu göstermez.

## 3. S2 - Polling ve task önceliği

Hatalı varyantta Report önceliği 5'tir. İlk LED geçişine yakın 20 x 100 bayt rapor, UART hazır bayrakları döngüde beklenerek gönderilir. Report Blocked olmaz; Execute hazır olsa bile CPU alamaz. SysTick kesmesinden sonra yüksek öncelikli Report'a dönülür.

Son kullanıcı kaydında maksimum LED geçiş gecikmesi **133,958 ms**; ekran görüntüsünde yaklaşık 133,8 ms Ready beklemesi görülmüştür. Bunlar farklı ölçümlerdir: Ready beklemesi ile hedef zamana göre LED gecikmesi birebir aynı değildir.

Düzeltmeler: Report önceliğini 2'ye indirmek veya önceliği 5 bırakıp kesmeli TX kullanmak. Kesmeli TX'te baytları ISR gönderir; Report notification beklerken bloklanır. Otomatik testlerde iki düzeltme de LED gecikmesini 1 ms altına indirmiştir.

<!-- pagebreak -->

## 4. S3 - Kesintisiz ve parçalı parser işi

Hatalı varyantta Parser'a yaklaşık 200 ms CPU işi eklenir. Parser önceliği 4, Execute 3'tür. Parser iş sırasında bloklanmadığından LED zamanı gelen Execute Ready durumunda bekler. Parser, Execute'ı doğrudan Blocked yapmaz; CPU'yu kullanmasını geciktirir.

İncelenen hatalı kullanıcı koşusunda iş süresi 200,852 ms, ilk LED gecikmesi 166,806 ms idi. Bu eski kayıt tek-kayıt politikasıyla değiştirilmiştir; sayı önceki koşunun konuşma sırasında okunan loguna dayanır. Mevcut kayıt olarak sunulmaz.

Düzeltmede iş yaklaşık 5 ms'lik parçalara ayrılır ve aralara vTaskDelay(1) konur. Parser bir tick için bekleme durumuna geçerek Execute ve Report'a fırsat verir. Bir tick bu sistemde 1 ms'dir; çağrının tick'e göre anına bağlı olarak gerçek bekleme daha kısa olabilir. Yalnız taskYIELD, daha düşük öncelikli task'a CPU verme garantisi sağlamaz.

Son düzeltilmiş kullanıcı kaydında maksimum LED gecikmesi **2,905 ms**. SystemView görüntüsündeki yaklaşık 3 ms Ready beklemesi, düzeltmenin etkisiyle uyumludur. Öncelikler değişmemiştir; değişen, Parser'ın kesintisiz CPU tuttuğu süredir.

## 5. S4 - Event biti iş sayısını tutmaz

100 ms/LED ve 1 tur ayarında, ilk dizi çalışırken dört ek LED komutu gönderilir. Queue dört komutu ayrı saklar; aynı Event Group bitinin tekrar set edilmesi dört ayrı bildirim biriktirmez.

Hatalı kod event başına tek komut alır ve kalan kuyruğu kontrol etmeden yeni event bekler. Kullanıcı deneyinde ilk dizi + bir ek dizi yaklaşık 0,8 saniyede tamamlanmış, **üç komut kuyrukta kalmıştır**. Komutlar kaybolmamış; işlenmeden beklemiştir.

Düzeltmede her dizi sonunda Queue kontrol edilir; iş varsa sıradaki komut alınır. Son kullanıcı kaydında **20 LED geçişi** vardır: ilk dizi + dört ek dizi, yaklaşık 2 saniye. Kuyruk STOP'tan önce sıfıra iner. LED zamanını beklerken Execute'ın Blocked olması normaldir. STOP kuyruğu temizlediği için yalnız STOP sonrası Queue=0 görmek başarı kanıtı değildir.

## 6. Son saklanan kullanıcı kayıtları

| Kayıt | Varyant | LED geçişi | Maks. gecikme | 10 ms üzeri |
|---|---|---|---|---|
| S1 / 16:47 | Referans | 12 | 0,856 ms | 0 |
| S2 / 17:02 | Hatalı polling | 12 | 133,958 ms | 1 |
| S3 / 17:36 | Parçalı iş | 12 | 2,905 ms | 0 |
| S4 / 17:48 | Queue tüketimi | 20 | 0,983 ms | 0 |

Tümü 26.10.2026 tarihli, COMPLETE ve trace_drop=0 kayıtlarıdır. İlk üçünde 1000 ms/LED, 3 tur; S4'te 100 ms/LED, 1 tur kullanılmıştır. COMPLETE, trace penceresinin eksiksizliğini belirtir; deadline başarısı değildir. S2 bilerek hata üreten bir kayıttır.

<!-- pagebreak -->

## 7. Ayrı otomatik doğrulama serisi

25.10.2026 tarihli otomatik testler aşağıdadır. Bu seri, önceki sayfadaki son kullanıcı kayıtlarıyla karıştırılmamalıdır. Sonuç kaynağı: docs/regression-results.json.

| Senaryo / varyant | LED geçişi | Maks. gecikme | Bekleyen komut |
|---|---|---|---|
| S1 referans | 32 | 0,865 ms | 0 |
| S2 yüksek öncelik + polling | 32 | 122,935 ms | 0 |
| S2 düşük öncelik + polling | 32 | 0,866 ms | 0 |
| S2 yüksek öncelik + kesme | 32 | 0,781 ms | 0 |
| S3 kesintisiz iş | 32 | 153,803 ms | 0 |
| S3 parçalı iş | 32 | 4,910 ms | 0 |
| S4 event başına tek komut | 36 | 0,971 ms | 3 |
| S4 Queue tüketimi | 48 | 0,971 ms | 0 |

Sekiz varyant, beklenen hata/düzeltme davranışı kontrollerini geçti. 17 yazılım testi; protokol ayrıştırma, kayıt değiştirme/geri alma, firmware eşleşmesi ve arayüz korumalarını kapsar. Kartta bozuk/parçalı çerçeve toparlanması, geçersiz komut reddi, STOP ile iş iptali ve 100 KB RX yükünde sıfır yeni kayıp/hata doğrulandı. Paketlenmiş EXE, görünür pencere açmadan iki tam kayıt/değiştirme döngüsünü geçti. Bu son test görsel arayüz testi değildir.

## 8. Ölçüm sınırları ve yorum

SystemView, ST-LINK üzerinden alınan **1,5 saniyelik RAM penceresidir**; UART logu tüm koşuyu kapsar. S4'ün yaklaşık 2 saniyelik tamamlanması UART olaylarından doğrulanır. Trace penceresini yeniden başlatmak RAM'deki önceki pencerenin yerini alır.

UART bayt başına ISR ve ayrıntılı FreeRTOS API giriş/çıkış olayları filtrelidir. Bu nedenle SystemView'da USART ISR sayısının sıfır görünmesi, kesmelerin çalışmadığı anlamına gelmez. Task çizelgesi, LED zamanları ve UART durum sayaçları birlikte değerlendirilmelidir.

Durum sayaçları açılıştan beri birikir. Son S2-S4 loglarında parser rejected-byte sayacı 5 olarak sabittir; yalnız bu değerle hatanın ilgili koşuda başladığı söylenemez. Host decoder rejected-byte sayacı ayrı bir ölçüttür ve son kayıtların tamamında sıfırdır. RX son bayt -> komut kabulü için ayrı 50 ms kabul ölçümü ve optik/logic analyzer LED ölçümü yapılmamıştır.

## 9. Teslim ve yeniden üretim

Git kökü D:/freertos-bootcamp; Hafta 5 bu repodaki hafta-05 klasörüdür. Kaynaklar, testler, lisanslar, raporlar ve yalnız güncel records/S1-S4 kayıtları sürümlenir. EXE paketi, build klasörleri, yerel ayarlar, kısayollar ve eski/geçici kayıtlar Git dışında kalır. Yeni bilgisayarda kurulum/derleme adımları README.md içindedir.

Kanıt dosyaları: records/S1-S4 içindeki manifest.json, summary.json, events.jsonl, led_timing.csv ve systemview/trace.SVDat; docs/regression-results.json, protocol-stress.json, interface-smoke.json. Rapor anındaki dosya hash'leri reports/evidence-manifest.json içindedir. Yeni başarılı kayıt aynı senaryonun önceki kaydını değiştirir; bu rapor 26 Ekim değerlendirmesidir, canlı gösterge değildir.

Temel sonuç: Öncelik tek başına doğruluk sağlamaz. CPU bekleyen task ile veri/zaman bekleyen task ayrılmalı; yüksek öncelikli işler gerektiğinde gerçekten bloklanmalı ve event bildirimi kuyruktaki iş sayısının yerine kullanılmamalıdır.
