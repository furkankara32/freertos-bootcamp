window.SLIDES = [
  {
    "section": "Hafta 03 / Açılış",
    "title": "Task’lar konuşsun.<br><span class=\"accent\">Veri akışını yönet.</span>",
    "lead": "Queue, bekleme ve yük altında tasarım kararı.",
    "body": "<div class=\"grid\"><div><p>İlk projeyi çalıştırdık. İz kaydında task’ları gördük. Şimdi bir verinin üreticiden tüketiciye yolculuğunu kontrol ediyoruz.</p><div class=\"callout\">Ana soru: Üretici veri gönderirken tüketici yetişemezse ne olur?</div><p class=\"mini\">Erhan Konak · 100 dakika ders + 20 dakika mola<br>Tek çekirdek · Native FreeRTOS · STM32L476RG</p></div><div class=\"panel\"><div class=\"hero-number\">03</div><h2>Tahmin → deney → iz → açıklama</h2><p>Her sonucu bir kod kararıyla ilişkilendir.</p></div></div>",
    "note": "Bu hafta tek bir yeni mekanizmaya odaklanın: Queue. Mutex, event groups ve bütün senkronizasyon API’lerini aynı derse sığdırmayın."
  },
  {
    "section": "Ders haritası",
    "title": "İki saatlik yolculuk.",
    "lead": "Önce ödevden öğren, sonra bir değişkeni kontrollü değiştir.",
    "body": "<div class=\"table-wrap\"><table><thead><tr><th>Dakika</th><th>İçerik</th><th>Öğrencinin yaptığı</th></tr></thead><tbody><tr><td>00–15</td><td>SystemView / Traxcope ödev değerlendirmesi</td><td>İki kaydı birlikte okur</td></tr><tr><td>15–25</td><td>Ready / Running / Blocked tekrarı</td><td>“Neden çalışmıyor?” sorusunu yanıtlar</td></tr><tr><td>25–40</td><td>Queue ve veri kopyalama</td><td>Bir mesajın yolunu çizer</td></tr><tr><td>40–60</td><td>Queue işlemleri / Control block / Timeout</td><td>Mesaj ve task bekleme listelerini adımlar</td></tr><tr><td>60–80</td><td>Mola</td><td></td></tr><tr><td>80–100</td><td>Canlı A/B/C deneyi</td><td>Tek değişkenle karşılaştırır</td></tr><tr><td>100–112</td><td>Sonuç ve bedel</td><td>Kayıp, gecikme ve üretici beklemesini yorumlar</td></tr><tr><td>112–120</td><td>Ödev ve çıkış soruları</td><td>Deney planını yazar</td></tr></tbody></table></div>",
    "note": "SystemView bağlantı sorunu 3 dakikada çözülmezse paketteki gerçek donanım kaydını açın. Canlı ölçüm ve hazır kaydı açıkça ayırın."
  },
  {
    "section": "01 / Önceki ödev",
    "title": "Bir ekran görüntüsü değil,<br>bir neden anlat.",
    "lead": "Öğrenci kaydından tek bir olayı birlikte takip edelim.",
    "body": "<div class=\"grid\"><div class=\"panel\"><h2>Üç soru</h2><p>① Task ne zaman Ready oldu?</p><p>② CPU üzerinde ne zaman Running oldu?</p><p>③ Bekleme sırasında hangi task veya ISR çalışıyordu?</p></div><div class=\"panel\"><h2>İyi bir açıklama</h2><p>“Gecikme var” yerine:</p><p>“Üretici veriyi hazırladıktan sonra tüketici henüz seçilemedi. Bu aralıkta yüksek öncelikli task çalışıyordu.”</p><p class=\"mini\">Yalnız görüntüde kanıtlanan kısmı söyleyin; eksik trace penceresini tahminle doldurmayın.</p></div></div>",
    "note": "Gönüllü iki öğrencinin kaydını seçin. Araç menülerini karşılaştırmaktan çok olayların sırasını tartışın. Dosya/sürüm ve kayıt kaynağını görünür tutun."
  },
  {
    "section": "01 / Temel tekrar",
    "title": "Çalışmıyor olmak tek bir durum değil.",
    "lead": "Scheduler yalnız çalışabilecek task’lar arasından seçim yapar.",
    "body": "<div class=\"grid three\"><div class=\"panel\"><h2>Ready</h2><div class=\"big\">Sıra</div><p>İş var; CPU bekleniyor.</p></div><div class=\"panel\"><h2>Running</h2><div class=\"big\">CPU</div><p>Komutlar şu anda yürütülüyor.</p></div><div class=\"panel\"><h2>Blocked</h2><div class=\"big\">Olay</div><p>Veri, yer veya süre bekleniyor.</p></div></div><div class=\"callout\">Queue üzerinde bloklanan yüksek öncelikli üretici, düşük öncelikli tüketicinin çalışmasına fırsat verebilir.</div>",
    "note": "Sorun: “Producer P2, Consumer P1. Producer queue doluyken bloklanırsa Consumer çalışabilir mi?” Cevap: Evet, daha yüksek başka Ready task yoksa."
  },
  {
    "section": "02 / Mimari",
    "title": "İki task, bir veri yolu.",
    "lead": "Queue üretici ve tüketicinin doğrudan aynı değişken üzerinden haberleşmesini gerektirmez.",
    "body": "<div class=\"flow\"><div class=\"node\">Producer<small>Message üretir</small></div><span class=\"arrow\">→</span><div class=\"node\">MessageQueue<small>Sınırlı sayıda kopya saklar</small></div><span class=\"arrow\">→</span><div class=\"node\">Consumer<small>Alır ve işler</small></div></div><div class=\"grid\"><div class=\"panel\"><h2>Üretici</h2><p>Veriyi hazırlar. Göndermeyi dener. Başarılı mı kontrol eder.</p></div><div class=\"panel\"><h2>Tüketici</h2><p>Veriyi almayı bekler. Aldığı kendi kopyasını işler.</p></div></div>",
    "note": "Her fonksiyon ayrı task değildir. Burada iki ayrı görev rolü seçiyoruz. Console yalnız komut ve deney sonrası aktarım için üçüncü task’tır."
  },
  {
    "section": "02 / Queue",
    "title": "Queue bir bekleme odasıdır.",
    "lead": "Bir elemanın boyutu ve toplam eleman sayısı oluşturma anında belirlenir.",
    "body": "<pre><code>typedef struct {\n    uint32_t sequence;\n    uint32_t generated_us;\n    uint32_t value;\n} Message;\n\nQueueHandle_t q = xQueueCreate(4, sizeof(Message));\nconfigASSERT(q != NULL);</code></pre><div class=\"callout\">Bu hedefte Message = 12 bayt; 4 eleman için veri alanı 48 bayt. Kernel yönetim bilgisi ve allocator ek yükü ayrıca RAM kullanır.</div>",
    "note": "Native FreeRTOS queue boyutu byte olarak item size + item count ile belirlenir. Task stack derinliğinin eleman cinsinden olmasıyla karıştırmayın. Dinamik oluşturma başarısız olabilir."
  },
  {
    "section": "02 / Veri sahipliği",
    "title": "Gönderilen kopya bağımsızdır.",
    "lead": "Yerel değişkeni sonradan değiştirmek kuyruğa alınan struct’ı değiştirmez.",
    "body": "<div class=\"grid\"><div class=\"panel\"><h2>Üreticinin nesnesi</h2><div class=\"big\" id=\"copyValue\">42</div><div class=\"controls\"><button id=\"copySend\" class=\"primary\">Queue’ya kopyala</button><button id=\"copyChange\">Yerel değeri değiştir</button></div></div><div class=\"panel\"><h2>Kuyruktaki kopya</h2><div class=\"big\" id=\"queueValue\">—</div><p id=\"copyStatus\" role=\"status\">Önce bir değer gönderin.</p></div></div><div class=\"callout\">Pointer kuyruğu farklıdır: pointer değeri kopyalanır; işaret edilen buffer kopyalanmaz. Bu hafta struct’ı değer olarak taşıyoruz.</div>",
    "note": "Önce 42’yi gönderin, sonra yerel nesneyi 99 yapın. Queue değerinin 42 kaldığını gösterin. Pointer ömrünü ayrıntılı zorunlu ödeve çevirmeyin."
  },
  {
    "section": "03 / Üretici",
    "title": "xQueueSend(): sonuç önemlidir.",
    "lead": "Kuyruğa veri yazmayı denemek, verinin mutlaka kabul edildiği anlamına gelmez.",
    "body": "<pre><code>Message msg = { .sequence = 1, .value = 42 };\n\nBaseType_t result = xQueueSend(q, &amp;msg, 0);\nif (result == pdPASS) {\n    accepted++;\n} else {\n    failed++;\n}</code></pre><div class=\"grid\"><div class=\"panel\"><h2>Yer varsa</h2><p>Mesaj kopyalanır. Başarılı dönüş alınır.</p></div><div class=\"panel\"><h2>Doluysa ve bekleme 0 ise</h2><p>Task yer açılmasını beklemez. Çağrı başarısız döner; uygulama karar vermelidir.</p></div></div>",
    "note": "failed sayacı burada gönderme girişimi başarısızlığıdır. Kayıt almadan sessizce yok saymak verinin akıbetini belirsiz yapar. Dönüş değerini mutlaka kontrol edin."
  },
  {
    "section": "03 / Tüketici",
    "title": "xQueueReceive(): boşken ne olacak?",
    "lead": "Bekleme süresi seçimi, tüketicinin boş kuyruktaki davranışını belirler.",
    "body": "<pre><code>Message msg;\nif (xQueueReceive(q, &amp;msg, pdMS_TO_TICKS(25)) == pdPASS) {\n    ProcessMessage(&amp;msg);\n} else {\n    // 25 tick hedefi boyunca veri gelmedi.\n    // Normal akış veya uygulamaya uygun timeout yolu.\n}</code></pre><div class=\"callout\">Bu firmware’de tick 1 kHz. Bekleme süreleri tick cinsindedir; timeout sonrasında task’ın CPU alması ayrıca scheduler’a bağlıdır.</div>",
    "note": "ProcessMessage öğretim örneği fonksiyondur. Gerçek laboratuvar consumer kodunda 20 ms vTaskDelay kullanılır. Genel projelerde ms ve tick’i eşit varsaymayın."
  },
  {
    "section": "03 / Queue uçları",
    "title": "İki giriş yönü.<br>Tek okuma yönü.",
    "lead": "Front, bir sonraki okumanın yapılacağı uçtur. Yalnız Back kullanıldığında FIFO sırası korunur.",
    "body": "<div class=\"table-wrap\"><table><thead><tr><th>API</th><th>Mesaj nerede?</th><th>Başarıdan sonra doluluk</th></tr></thead><tbody><tr><td><code>xQueueSendToBack()</code></td><td>Yeni mesaj arka uca eklenir</td><td>+1</td></tr><tr><td><code>xQueueSendToFront()</code></td><td>Yeni mesaj ön uca eklenir</td><td>+1</td></tr><tr><td><code>xQueueReceive()</code></td><td>Ön eleman kopyalanır ve çıkarılır</td><td>−1</td></tr><tr><td><code>xQueuePeek()</code></td><td>Ön eleman kopyalanır; queue içinde kalır</td><td>Değişmez</td></tr></tbody></table></div><div class=\"callout\"><code>xQueueSend()</code>, <code>xQueueSendToBack()</code> ile eşdeğerdir. Başarı için <code>pdPASS</code> kontrol edilir.</div>",
    "note": "Front/Back fiziksel RAM adresi değildir. Kuyruğun mantıksal sırasını anlatır. Receive her zaman front elemanını alır; front kullanıldıktan sonra bu eleman en eski gönderilen mesaj olmak zorunda değildir. Send/Receive veri kopyalama API’leridir."
  },
  {
    "section": "03 / Etkileşimli queue laboratuvarı",
    "title": "Gönder. Oku. <span class=\"accent\">Sırayı izle.</span>",
    "lead": "Send to Front, Send to Back, Receive ve Peek işlemlerini aynı kuyrukta deneyin.",
    "body": "<section id=\"queueOperations\" class=\"q-lab\" aria-label=\"Etkileşimli FreeRTOS queue işlemleri\">\n  <div class=\"q-toolbar\"><label>Yeni mesajın değeri <input id=\"qValue\" type=\"number\" min=\"0\" max=\"999\" step=\"1\" value=\"10\"></label><span class=\"tag\">Kapasite: 6 mesaj</span><span class=\"tag\">Bekleme: 0 tick</span><span id=\"qCount\" class=\"q-count\">0 / 6 dolu</span></div>\n  <div class=\"q-canvas\"><svg id=\"qDiagram\" viewBox=\"0 0 1100 300\" role=\"img\" aria-labelledby=\"qDiagramTitle qDiagramDesc\">\n    <title id=\"qDiagramTitle\">Queue'nun önüne veya arkasına gönder; önünden al</title><desc id=\"qDiagramDesc\">Mesajlar soldan sağa okunma sırasıyla gösterilir. Receive soldaki front elemanını çıkarır. Peek aynı elemanın kopyasını verir, queue'da bırakır.</desc>\n    <defs><marker id=\"qArrow\" viewBox=\"0 0 10 10\" refX=\"8\" refY=\"5\" markerWidth=\"7\" markerHeight=\"7\" orient=\"auto-start-reverse\"><path d=\"M 0 0 L 10 5 L 0 10 z\" fill=\"currentColor\"/></marker></defs>\n    <text x=\"235\" y=\"27\" class=\"q-end front\">FRONT / ÖN</text><text x=\"800\" y=\"27\" text-anchor=\"end\" class=\"q-end back\">BACK / ARKA</text>\n    <text x=\"235\" y=\"49\" class=\"q-label\">Bir sonraki Receive buradan alır</text>\n    <path id=\"qFrontPath\" class=\"q-route front\" d=\"M 119 216 L 119 103 L 216 103\" marker-end=\"url(#qArrow)\"/>\n    <path id=\"qBackPath\" class=\"q-route back\" d=\"M 165 247 L 840 247 L 840 103 L 812 103\" marker-end=\"url(#qArrow)\"/>\n    <path id=\"qReceivePath\" class=\"q-route receive\" d=\"M 277 145 L 277 187 L 970 187 L 970 216\" marker-end=\"url(#qArrow)\"/>\n    <g id=\"qSlots\"></g><g id=\"qMessages\"></g>\n    <rect x=\"52\" y=\"216\" width=\"135\" height=\"68\" rx=\"10\" class=\"q-pod\"/><text x=\"119\" y=\"239\" text-anchor=\"middle\" class=\"q-label\">ÜRETİCİ / msg</text><text id=\"qProducerValue\" x=\"119\" y=\"270\" text-anchor=\"middle\" class=\"q-payload\">10</text>\n    <rect x=\"915\" y=\"216\" width=\"135\" height=\"68\" rx=\"10\" class=\"q-pod\"/><text x=\"982\" y=\"239\" text-anchor=\"middle\" class=\"q-label\">TÜKETİCİ / out</text><text id=\"qOut\" x=\"982\" y=\"270\" text-anchor=\"middle\" class=\"q-payload\">—</text>\n    <text x=\"545\" y=\"284\" text-anchor=\"middle\" class=\"q-label\">Ekran mantıksal sırayı gösterir; fiziksel RAM yerleşimini değil.</text><g id=\"qTransient\"></g>\n  </svg></div>\n  <div class=\"q-actions\"><button id=\"qFront\" class=\"q-front\">↗ Send to Front</button><button id=\"qBack\" class=\"q-back\">↖ Send to Back</button><button id=\"qReceive\" class=\"primary\">Receive →</button><button id=\"qPeek\">Peek / çıkarma</button><button id=\"qReset\">Sıfırla</button></div>\n  <div class=\"q-feedback\"><div><span class=\"eyebrow\">Son API çağrısı</span><pre id=\"qCode\">Bir işlem seçin.</pre><p id=\"qStatus\" role=\"status\">Boş kuyruk. Önce 10 ve 20’yi arkaya, sonra 99’u öne gönderin.</p></div><div><span class=\"eyebrow\">Okunma sırası · front → back</span><p id=\"qOrder\" class=\"q-order\">[ boş ]</p><p id=\"qBefore\" class=\"mini\">Her işlemin önceki ve sonraki sırası burada karşılaştırılır.</p><button id=\"qDemo\">Rehberli örnek: başlat</button></div></div>\n  <p class=\"mini q-caption\">Öğretim modeli · Task bağlamındaki API’ler · İşlemler elle tetiklenir · Animasyon süresi gerçek RTOS süresi değildir.</p>\n</section>\n",
    "note": "Rehberli örnek düğmesine her basış bir işlem yapar: Back 10, Back 20, Front 99, Peek, Receive, Receive. Önce öğrencilerden sıradaki çıkışı tahmin etmelerini isteyin. Altı kapasiteyi doldurup Front deneyin: baştaki mesajı ezmez; errQUEUE_FULL döner. Kuyruk boşken Receive ve Peek başarısızdır, out değişmez. Diyagramdaki kayma mantıksal sıra değişimidir; kernel bütün elemanları RAM’de kaydırıyor anlamına gelmez. Model yalnız sıralama içindir; sonraki model bloklanma ve timeout’u gösterir."
  },
  {
    "section": "03 / Tasarım kararı",
    "title": "Öne eklemek bir seçimdir.<br>Ücretsiz öncelik değildir.",
    "lead": "Send to Front mesaj sırasını değiştirir; task önceliğini veya kapasiteyi değiştirmez.",
    "body": "<div class=\"grid three\"><div class=\"panel\"><h2>Yeni öne gönderim</h2><p>[10, 20] kuyruğuna önce 99, sonra 88 öne gönderilirse sıra <b>[88, 99, 10, 20]</b> olur.</p><p>Yeni öne eklenen, önceki öne ekleneni de geçer.</p></div><div class=\"panel\"><h2>Dolu kuyruk</h2><p>Front ve Back için aynı kapasite sınırı geçerlidir.</p><p>0 tick ile doluysa başarısız döner; dolu kuyruğun en eski elemanını otomatik silmez.</p></div><div class=\"panel\"><h2>Adalet / starvation</h2><p>Sürekli öne veri eklenmesi arkadaki mesajları uzun süre bekletebilir.</p><p>Send to Front, mesajlara sayısal öncelik atayan genel bir priority queue değildir.</p></div></div><div class=\"callout\">Ders deneyi A/B/C, arkaya gönderim kullanmaya devam eder. Bu etkileşimli bölüm, farklı API’lerin sıralama davranışını karşılaştırır.</div><p class=\"mini\">Başvuru: <a href=\"https://github.com/FreeRTOS/FreeRTOS-Kernel-Book/blob/main/ch05.md\" target=\"_blank\" rel=\"noopener\">FreeRTOS / Queue Management</a> · Yerel API: firmware/vendor/freertos/include/queue.h</p>",
    "note": "Hangi task CPU alacak sorusunu scheduler, hangi mesaj okunacak sorusunu queue sırası belirler. Task önceliğini artırmak kuyruktaki mesajları yeniden sıralamaz. Task önceliği yükseltilmediği halde Receive çıktısının değişebildiğini vurgulayın. Bu haftanın ölçümlü ödevinde Front eklemeyin; A/B kapasite ve A/C timeout karşılaştırmalarındaki tek değişken korunmalı. Ek alıştırma olarak sürekli Front gönderimi altında eski mesajın kaç adım beklediğini tartışabilirsiniz."
  },
  {
    "section": "03 / Queue control block",
    "title": "Mesajlar ayrı.<br><span class=\"accent\">Bekleyen task’lar ayrı.</span>",
    "lead": "Queue_t, veriyi ve bu veriyi bekleyen task’ları üç farklı alanla takip eder.",
    "body": "<div class=\"qc-overview\"><div class=\"panel\"><h2>01 / uxMessagesWaiting</h2><div class=\"qc-symbol\">3 / 4</div><p>Queue içindeki <b>mevcut mesaj sayısı</b>. Task sayısı veya bayt sayısı değildir.</p><small>volatile UBaseType_t</small></div><div class=\"panel\"><h2>02 / xTasksWaitingToSend</h2><div class=\"qc-symbol amber\">P3 → P1</div><p>Queue doluyken <b>yer açılmasını bekleyen göndericiler</b>. Öncelik sıralı event listesi.</p><small>List_t</small></div><div class=\"panel\"><h2>03 / xTasksWaitingToReceive</h2><div class=\"qc-symbol blue\">P4 → P2</div><p>Queue boşken <b>mesaj gelmesini bekleyen alıcılar</b>. Öncelik sıralı event listesi.</p><small>List_t</small></div></div><div class=\"callout\">Mesaj depolama alanı payload kopyalarını tutar. Bekleme listeleri ise task’ın <code>xEventListItem</code> düğümünü bağlar; mesajı veya TCB’nin tamamını kopyalamaz.</div><p class=\"mini\">Kernel iç isimleri: <code>uxMessagesWaiting</code>, <code>xTasksWaitingToSend</code>, <code>xTasksWaitingToReceive</code>. Uygulama bu özel alanları doğrudan değiştirmez.</p>",
    "note": "Bu üç alan tüm Queue_t değildir. pcHead, pcWriteTo, uxLength, uxItemSize ve kilit alanları da vardır. Sonraki görseller normal queue için öğretici olay adımlarıdır; tüm kernel veya scheduler simülasyonu değildir."
  },
  {
    "section": "03 / Queue control block",
    "title": "İçeride kaç mesaj var?",
    "lead": "uxMessagesWaiting: başarılı gönderimde +1, başarılı okumada −1.",
    "body": "<section class=\"qc-lab\" id=\"queueControl\" data-mode=\"count\">\n          <div class=\"qc-toolbar\"><span class=\"tag\">QUEUE_t / İÇ DURUM</span><span data-qc=\"step\"></span><button data-qc=\"reset\">Sıfırla</button></div>\n          <div class=\"qc-grid\"><div class=\"qc-storage\"><div class=\"qc-label\">MESAJ DEPOLAMA ALANI · FRONT → BACK</div><div class=\"qc-slots\" data-qc=\"slots\"></div><div class=\"qc-meter\"><i data-qc=\"meter\"></i></div><p class=\"mini\">Kapasite: <b>3 mesaj</b> · Her kutu bir payload kopyası</p><div class=\"qc-ready\"><div class=\"qc-label\">TASK DURUMU / CPU TARAFI</div><div data-qc=\"ready\"></div></div></div>\n          <div class=\"qc-block\"><div class=\"qc-field\"><code>uxMessagesWaiting</code><b data-qc=\"count\">0</b></div><div class=\"qc-field-list\"><code>xTasksWaitingToSend</code><div data-qc=\"send\"></div></div><div class=\"qc-field-list\"><code>xTasksWaitingToReceive</code><div data-qc=\"receive\"></div></div></div></div>\n          <div class=\"qc-event\" aria-live=\"polite\"><b data-qc=\"title\"></b><p data-qc=\"description\"></p><code data-qc=\"api\"></code></div>\n          <div class=\"qc-controls\" data-qc=\"controls\"></div>\n        </section><p class=\"mini\">Öğretici model · Normal queue, task bağlamı · Büyük P değeri yüksek öncelik. Kaynak: <a href=\"https://www.freertos.org/Documentation/02-Kernel/02-Kernel-features/02-Queues-mutexes-and-semaphores/01-Queues\" target=\"_blank\" rel=\"noopener\">FreeRTOS Queues</a> · Yerel queue.c / tasks.c</p>",
    "note": "Peek yalnız sayacı değiştirmez. Genel kernel davranışında Peek başka bir bekleyen alıcıyı uyandırabilir; burada bekleyen task yoktur. uxQueueMessagesWaiting(q) anlık değer verir; bu değer daha sonraki Send/Receive sonucunu garanti etmez."
  },
  {
    "section": "03 / Queue control block",
    "title": "Yer açılmasını kim bekliyor?",
    "lead": "xTasksWaitingToSend: dolu queue → Blocked göndericiler → bir slot açılır → bir task Ready.",
    "body": "<section class=\"qc-lab\" id=\"queueControl\" data-mode=\"send\">\n          <div class=\"qc-toolbar\"><span class=\"tag\">QUEUE_t / İÇ DURUM</span><span data-qc=\"step\"></span><button data-qc=\"reset\">Sıfırla</button></div>\n          <div class=\"qc-grid\"><div class=\"qc-storage\"><div class=\"qc-label\">MESAJ DEPOLAMA ALANI · FRONT → BACK</div><div class=\"qc-slots\" data-qc=\"slots\"></div><div class=\"qc-meter\"><i data-qc=\"meter\"></i></div><p class=\"mini\">Kapasite: <b>3 mesaj</b> · Her kutu bir payload kopyası</p><div class=\"qc-ready\"><div class=\"qc-label\">TASK DURUMU / CPU TARAFI</div><div data-qc=\"ready\"></div></div></div>\n          <div class=\"qc-block\"><div class=\"qc-field\"><code>uxMessagesWaiting</code><b data-qc=\"count\">0</b></div><div class=\"qc-field-list\"><code>xTasksWaitingToSend</code><div data-qc=\"send\"></div></div><div class=\"qc-field-list\"><code>xTasksWaitingToReceive</code><div data-qc=\"receive\"></div></div></div></div>\n          <div class=\"qc-event\" aria-live=\"polite\"><b data-qc=\"title\"></b><p data-qc=\"description\"></p><code data-qc=\"api\"></code></div>\n          <div class=\"qc-controls\" data-qc=\"controls\"></div>\n        </section><p class=\"mini\">Öğretici model · Normal queue, task bağlamı · Büyük P değeri yüksek öncelik. Kaynak: <a href=\"https://www.freertos.org/Documentation/02-Kernel/02-Kernel-features/02-Queues-mutexes-and-semaphores/01-Queues\" target=\"_blank\" rel=\"noopener\">FreeRTOS Queues</a> · Yerel queue.c / tasks.c</p>",
    "note": "En yüksek öncelikli bekleyen gönderici uyandırılır. Ready olmak gönderimin tamamlandığı anlamına gelmez. Slot task’a rezerve edilmez. Bekleme parametresi API çağrısının duvar saatindeki kesin üst sınırı değildir: timeout sonrası CPU alması scheduler’a bağlıdır. Gerçek preemptive sistemde yüksek öncelikli task hemen çalışabilir; burada öğretim amacıyla Ready ve Running adımları ayrılmıştır."
  },
  {
    "section": "03 / Queue control block",
    "title": "Mesaj gelmesini kim bekliyor?",
    "lead": "xTasksWaitingToReceive: boş queue → Blocked alıcılar → mesaj gelir → bir task Ready.",
    "body": "<section class=\"qc-lab\" id=\"queueControl\" data-mode=\"receive\">\n          <div class=\"qc-toolbar\"><span class=\"tag\">QUEUE_t / İÇ DURUM</span><span data-qc=\"step\"></span><button data-qc=\"reset\">Sıfırla</button></div>\n          <div class=\"qc-grid\"><div class=\"qc-storage\"><div class=\"qc-label\">MESAJ DEPOLAMA ALANI · FRONT → BACK</div><div class=\"qc-slots\" data-qc=\"slots\"></div><div class=\"qc-meter\"><i data-qc=\"meter\"></i></div><p class=\"mini\">Kapasite: <b>3 mesaj</b> · Her kutu bir payload kopyası</p><div class=\"qc-ready\"><div class=\"qc-label\">TASK DURUMU / CPU TARAFI</div><div data-qc=\"ready\"></div></div></div>\n          <div class=\"qc-block\"><div class=\"qc-field\"><code>uxMessagesWaiting</code><b data-qc=\"count\">0</b></div><div class=\"qc-field-list\"><code>xTasksWaitingToSend</code><div data-qc=\"send\"></div></div><div class=\"qc-field-list\"><code>xTasksWaitingToReceive</code><div data-qc=\"receive\"></div></div></div></div>\n          <div class=\"qc-event\" aria-live=\"polite\"><b data-qc=\"title\"></b><p data-qc=\"description\"></p><code data-qc=\"api\"></code></div>\n          <div class=\"qc-controls\" data-qc=\"controls\"></div>\n        </section><p class=\"mini\">Öğretici model · Normal queue, task bağlamı · Büyük P değeri yüksek öncelik. Kaynak: <a href=\"https://www.freertos.org/Documentation/02-Kernel/02-Kernel-features/02-Queues-mutexes-and-semaphores/01-Queues\" target=\"_blank\" rel=\"noopener\">FreeRTOS Queues</a> · Yerel queue.c / tasks.c</p>",
    "note": "Listeler task önceliğine göre tutulur. Mesaj sırası ile task önceliği farklı kavramlardır. Timeout süresi olan task ayrıca kernel’in gecikme takibindedir; timeout event listesinden de çıkarır. Ready checkpoint’i öğretim amaçlıdır; gerçek sistemde bağlam değişimi hemen olabilir."
  },
  {
    "section": "04 / Yük",
    "title": "Ortalama hız yetmez; burst de önemlidir.",
    "lead": "Tüketici aynı anda yalnız bir mesajı işler.",
    "body": "<div class=\"grid\"><div class=\"panel\"><h2>Normal yük</h2><div class=\"big\">100 ms</div><p>İki gönderme girişimi arası bekleme. Tüketicinin modellenen servis beklemesi 20 ms.</p></div><div class=\"panel\"><h2>Yoğun bölüm</h2><div class=\"big\">24</div><p>Art arda gönderme girişimi. Üretici 0 tick politikasında hazır kalır; küçük kuyruk hızlı dolar.</p></div></div><div class=\"callout\">Kalıcı üretim hızı tüketim hızını aşarsa hiçbir sonlu kuyruk sınırsız süre boyunca kayıpsız depolayamaz.</div>",
    "note": "Bu deneyde burst, 24 gönderme girişimidir. C’de gönderme çağrısı bloklandığı için fiziksel girişim zamanları uzar; bunu adil olmayan deney diye saklamayın, politikanın sonucu olarak raporlayın."
  },
  {
    "section": "04 / Mola",
    "title": "20 dakika mola.",
    "lead": "Dönüşte tahminlerimizi aynı kart üzerinde sınayacağız.",
    "body": "<div class=\"grid\"><div class=\"hero-number\">20′</div><div class=\"panel\"><h2>Dönüş sorusu</h2><p>Kuyruğu 4’ten 16’ya çıkarmak hangi durumu iyileştirebilir?</p><p>Hangi durumda mesajlar daha uzun bekleyebilir?</p><p>Ön tahmininizi iki cümleyle yazın.</p></div></div>",
    "note": "Mola sırasında hazır SystemView dosyasını ve kayıt masasını açın. Bağlı portu yalnız bir uygulamanın kullandığını kontrol edin."
  },
  {
    "section": "05 / Gerçek firmware",
    "title": "Aynı donanım, üç politika.",
    "lead": "Bu haftanın A/B/C isimleri queue deneyini tanımlar; Hafta 2’deki öncelik varyantları değildir.",
    "body": "<div class=\"table-wrap\"><table><thead><tr><th>Varyant</th><th>Kapasite</th><th>Gönderme beklemesi</th><th>Değişen tek etken</th></tr></thead><tbody><tr><td>A</td><td>4 mesaj</td><td>0 tick</td><td>Başlangıç</td></tr><tr><td>B</td><td>16 mesaj</td><td>0 tick</td><td>A → B: kapasite</td></tr><tr><td>C</td><td>4 mesaj</td><td>20 ms → tick</td><td>A → C: bekleme politikası</td></tr></tbody></table></div><div class=\"callout\">Sabitler: Producer P2, Consumer P1, Console P3 · Message 12 bayt · servis beklemesi 20 ms · UART 230400 baud.</div>",
    "note": "Önemli: A/B/C aynı adlar ama yeni deney tanımları. Mevcut board ve FreeRTOS altyapısından türetildi; Hafta 2 projesi değiştirilmedi. B’nin daha büyük kapasitesi tek başına CPU hızını değiştirmez."
  },
  {
    "section": "05 / Canlı deney",
    "title": "Önce tahmin; sonra çalıştır.",
    "lead": "Altı koşul: A/B/C × normal/yoğun yük.",
    "body": "<div class=\"flow\"><div class=\"node\">Kayıt masasını aç</div><span class=\"arrow\">→</span><div class=\"node\">Varyant ve yük seç</div><span class=\"arrow\">→</span><div class=\"node\">Deneyi çalıştır</div><span class=\"arrow\">→</span><div class=\"node\">CSV + .SVDat al</div></div><div class=\"grid\"><div class=\"panel\"><h2>Normal</h2><p>44 mesaj. Her gönderimden sonra 100 ms bekleme.</p></div><div class=\"panel\"><h2>Yoğun</h2><p>10 normal + 24 art arda girişim + 10 normal mesaj. Toplam yine 44.</p></div></div><div class=\"callout\"><a href=\"interface/index.html\" target=\"_blank\">Kayıt masasını aç ↗</a> · Seri port: ST-LINK VCP · Bu bilgisayarda doğrulanan port COM4.</div>",
    "note": "Arayüz gerçek ölçüm verir; model göstermez. LD2 deney boyunca yanar. B1 butonunu kullanmayın: yük yazılımla tekrarlanabilir üretilir. Deney bittikten sonra kayıtları indirin."
  },
  {
    "section": "05 / Entegrasyon",
    "title": "ST-LINK ile SystemView akışı.",
    "lead": "Kod çalışırken RAM’e kaydet; sonrasında aynı USB üzerinden dışarı al.",
    "body": "<div class=\"flow\"><div class=\"node\">Task / IRQ / Queue<small>FreeRTOS trace hook’ları</small></div><span class=\"arrow\">→</span><div class=\"node\">RAM / 32 KB<small>200 ms pencere</small></div><span class=\"arrow\">→</span><div class=\"node\">ST-LINK VCP<small>Deney sonrası aktarım</small></div><span class=\"arrow\">→</span><div class=\"node\">SystemView<small>.SVDat dosyasını aç</small></div></div><div class=\"callout\">SystemView içinde “J-Link ile canlı bağlan” kullanılmaz. Bu pakette ST-LINK firmware’i dönüştürülmez; snapshot dosyası açılır.</div>",
    "note": "Normal yükte ilk mesaj çevresinden; burst yükte 11. mesajdan önce kayıt başlar. 200 ms bütün deneyi kapsamaz. CSV bütün 44 mesajı kapsar. UART Recorder protokolü değil, sonradan HEX aktarımı kullanılıyor."
  },
  {
    "section": "05 / Trace okuma",
    "title": "Bir mesajı dört olayla izle.",
    "lead": "Aynı run ve id değerlerini eşleştir.",
    "body": "<div class=\"table-wrap\"><table><thead><tr><th>Olay</th><th>Anlam</th><th>Bakılacak yer</th></tr></thead><tbody><tr><td>SEND_BEGIN</td><td>xQueueSend öncesi</td><td>Producer / çalışıyor mu?</td></tr><tr><td>SEND_OK / SEND_FAIL</td><td>API dönüşü ve send_us</td><td>Başarı veya timeout</td></tr><tr><td>RECEIVE</td><td>Consumer mesajı aldı</td><td>latency_us: üretimden almaya</td></tr><tr><td>DONE</td><td>Modellenen servis tamamlandı</td><td>20 ms bekleme sonrası</td></tr></tbody></table></div><div class=\"callout\">SystemView’de Events ve Timeline pencerelerini yan yana açın. Kullanıcı olayları W3 modülü altında açıklamalarıyla kaydedilir.</div>",
    "note": "Kayıt başlamadan önce task’lar vardır; başlangıçta task listesi ve queue adı tekrar gönderilir. İlk önce Task adları Producer, Consumer, Console görünür mü kontrol edin. SysTick native port tarafından zaten izlenir; ikinci giriş/çıkış eklenmez."
  },
  {
    "section": "06 / Zaman sınırları",
    "title": "İki gecikmeyi karıştırmayalım.",
    "lead": "Biri gönderme çağrısının süresi, diğeri mesajın tüketiciye ulaşma süresi.",
    "body": "<div class=\"grid\"><div class=\"panel\"><h2>send_call_us</h2><p>Gönderme çağrısı çevresindeki duvar saati.</p><p>Bloklanma, preemption ve yakındaki trace maliyetini içerebilir; saf CPU süresi değildir.</p></div><div class=\"panel\"><h2>generation_to_receive_us</h2><p>Mesaj üretim zamanından consumer’ın mesajı aldığı ana kadar.</p><p>C’de kuyrukta yer bekleme süresi de buna dahildir. Saf queue residence time değildir.</p></div></div><div class=\"callout\">Başarısız gönderime 0 ms gecikme atamayın. CSV’de alınmayan mesajın generation_to_receive_us alanı boştur.</div>",
    "note": "timestamp DWT trace saati ile TIM2 ölçüm saati aynı sıfıra sahip değildir. Ham mutlak değerleri birbirinden çıkarmayın; aynı olay kimliğiyle eşleyip süreleri yorumlayın."
  },
  {
    "section": "06 / Kanıt",
    "title": "Bir tablo, üç ayrı soru.",
    "lead": "Başarı sayısını gecikmeden ayrı okuyun.",
    "body": "<div class=\"table-wrap\"><table><thead><tr><th>Karşılaştırma</th><th>Soru</th><th>Bedel</th></tr></thead><tbody><tr><td>A → B</td><td>Büyük buffer daha fazla mesaj kabul etti mi?</td><td>Bekleyen mesajların gecikmesi artabilir</td></tr><tr><td>A → C</td><td>Üretici bekleyince daha fazla mesaj kabul edildi mi?</td><td>Üreticinin döngüsü uzar</td></tr><tr><td>Trace açık → kapalı</td><td>İzleme ölçülen davranışı etkiliyor mu?</td><td>İz ek yükü sıfır kabul edilmez</td></tr></tbody></table></div><div class=\"callout\">Kaybı azaltan bir tasarım her task’ın zamanlama ihtiyacını iyileştirmiş olmayabilir.</div>",
    "note": "Rakamları measurements/hardware dosyalarından okuyun. Gözlenen maksimum bir worst-case ispatı değildir. Kısa tek örnekten kesin üst sınır çıkarmayın."
  },
  {
    "section": "06 / Kapasite ve gecikme",
    "title": "Daha çok yer, daha çok bekleme olabilir.",
    "lead": "Bekleyen mesaj sayısı × servis süresi, bir başlangıç sezgisi verir.",
    "body": "<div class=\"grid\"><div class=\"panel\"><h2>4 eleman</h2><div class=\"big\">≈ 80 ms</div><p>Önünde dört servis işi varsa 4 × 20 ms. Scheduler ve tick etkileri dahil değil.</p></div><div class=\"panel\"><h2>16 eleman</h2><div class=\"big\">≈ 320 ms</div><p>Önünde on altı servis işi varsa 16 × 20 ms. Bu bir ölçüm veya garanti değil.</p></div></div><div class=\"callout\">Kapasite kabul olasılığını etkiler. Kullanıcıya geç ulaşan veri hâlâ geç veridir.</div>",
    "note": "Bu sayılar belirli bir kuyruk konumu varsayımıdır; kartta gözlenen maksimumla eşitlemeyin. Gecikmenin kuyruktaki konuma göre değiştiğini çizerek anlatın."
  },
  {
    "section": "06 / Dikkat",
    "title": "Critical section içinde bekleme yok.",
    "lead": "Scheduler’ın ilerlemesi gereken bir işlemi kapalı bölgede beklemeyin.",
    "body": "<div class=\"grid\"><pre><code>// YANLIŞ TASARIM\ntaskENTER_CRITICAL();\nxQueueSend(q, &amp;msg, pdMS_TO_TICKS(20));\ntaskEXIT_CRITICAL();</code></pre><pre><code>// BU DENEYDE\nBaseType_t result = xQueueSend(\n    q, &amp;msg, pdMS_TO_TICKS(20));\n// Queue kendi iç senkronizasyonunu yapar.</code></pre></div><div class=\"callout warn\">Hafta 2’de 0 tick ile yapılan kritik bölge içi gönderimi, yalnız timeout’u değiştirerek bloklayan hale getirmeyin.</div>",
    "note": "Bu tuzak önemlidir: önceki referans enqueue içinde kritik bölüm kullanıyordu. Hafta 3 ayrı app.c’de queue’nun kendi eşzamanlılık mekanizmasına dayanır. ISR’den normal API çağrılmaz; FromISR sürümleri ve kesme önceliği kuralları ayrı konudur."
  },
  {
    "section": "07 / Bilgini sına",
    "title": "Büyük kuyruk her şeyi çözer mi?",
    "lead": "Üretici sürekli 100 mesaj/s, tüketici 50 mesaj/s işleyebiliyor.",
    "body": "<div class=\"panel quiz\"><button data-answer=\"wrong\">Kapasiteyi 16 yaparsak sistem sonsuza kadar kayıpsız çalışır.</button><button data-answer=\"correct\">Daha büyük kuyruk taşmayı geciktirebilir; hız farkı sürerse yine dolar.</button><button data-answer=\"wrong\">Task önceliğini artırınca tüketicinin bütün servis beklemesi ortadan kalkar.</button><p id=\"answer\" role=\"status\">Bir yanıt seçin.</p></div>",
    "note": "Sayılar öğretim senaryosudur. Öğrenciden sonuç yerine gerekçe isteyin: saniyede 50 mesaj birikiyor, sonlu alan sonunda doluyor."
  },
  {
    "section": "07 / Yeni ödev",
    "title": "Kuyruk dolunca sistemim ne yapıyor?",
    "lead": "İlk hafta projesinin bir üretici–tüketici yolunu deneyle açıklayın.",
    "body": "<div class=\"grid\"><div class=\"panel\"><h2>Zorunlu</h2><p>A/B/C × normal/yoğun: altı deney.</p><p>A/yoğun için bir trace kapalı karşılaştırma.</p><p>Kod, ölçüm tablosu, iz kanıtı ve kısa anlatım.</p></div><div class=\"panel\"><h2>Kolay başlangıç</h2><p>Kendi projesinde uygun yol olmayanlar Hafta 3 referansını kullanabilir.</p><p>Yeni kart veya PC arayüzü yazılması gerekmiyor.</p></div></div><div class=\"callout\"><a href=\"odev-03.html\" target=\"_blank\">Ödev sunumunu aç ↗</a></div>",
    "note": "Her iki analiz aracını yeniden kurmayı zorunlu tutmayın. Bir çalışan araçla doğru açıklama yeterli. İkinci araçla karşılaştırma isteğe bağlı."
  },
  {
    "section": "07 / Kapanış",
    "title": "Bugünün üç cümlesi.",
    "lead": "Veri akışını koddan ve izden açıklayabiliyorsanız hedefe ulaştık.",
    "body": "<div class=\"grid three\"><div class=\"panel\"><h2>Kopya</h2><p>Queue, belirlenen boyuttaki veriyi kopyalar.</p></div><div class=\"panel\"><h2>Bekleme</h2><p>Boşta tüketici; doluyken üretici bloklanabilir.</p></div><div class=\"panel\"><h2>Bedel</h2><p>Kapasite ve timeout; kayıp, gecikme ve üretici zamanlamasını birlikte etkiler.</p></div></div><div class=\"callout\">Bir sonraki soru: İki task aynı kaynağı doğrudan kullanmak isterse ne olacak? → Mutex ve ortak kaynak yönetimi.</div>",
    "note": "Çıkış: 1) Queue doluysa 0 tick ne yapar? 2) 20 ms kesin başarı mı? 3) Kapasite artışı neden daha büyük gecikmeyle birlikte görülebilir?"
  },
  {
    "section": "Başvuru",
    "title": "Kaynaklar ve çalışma dosyaları.",
    "lead": "Teknik anlatım resmî belgelerle, uygulama ise yerel kaynak kodla eşleştirildi.",
    "body": "<div class=\"panel\"><p><a href=\"https://www.freertos.org/Documentation/02-Kernel/02-Kernel-features/02-Queues-mutexes-and-semaphores/01-Queues\" target=\"_blank\" rel=\"noopener\">FreeRTOS / Queues</a></p><p><a href=\"https://kb.segger.com/FreeRTOS_with_SystemView\" target=\"_blank\" rel=\"noopener\">SEGGER / FreeRTOS with SystemView</a></p><p><a href=\"https://doc.segger.com/UM08027_SystemView.html\" target=\"_blank\" rel=\"noopener\">SystemView User Guide / single-shot recording</a></p><p><a href=\"docs/SystemView_Kurulum.html\">Yerel kurulum ve canlı anlatım rehberi</a></p><p><a href=\"docs/Dogrulama.html\">Derleme, donanım ve arayüz doğrulaması</a></p><p class=\"mini\">Kaynak kontrolü: 5 Ekim 2026 · firmware/src/app.c · firmware/src/app_trace.c<br>Sunum modelleri gerçek ölçüm olarak kullanılmaz. Gerçek kayıtlar measurements/hardware altında.</p></div>",
    "note": "İz dosyasını yorumlamadan önce overflow, timestamp ölçeği ve task adlarını kontrol edin. Hazır kayıtlar tek kart/sürüm/koşula aittir."
  }
];
