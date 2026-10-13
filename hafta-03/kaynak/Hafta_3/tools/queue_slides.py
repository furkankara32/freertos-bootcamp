"""Expanded queue-operation lesson block, inserted after the Receive API slide."""
def extend_lesson(lesson,root,slide,table,panel,cols,code,call):
    block=[]
    block.append(slide('03 / Queue uçları','İki giriş yönü.<br>Tek okuma yönü.','Front, bir sonraki okumanın yapılacağı uçtur. Yalnız Back kullanıldığında FIFO sırası korunur.',
        table(['API','Mesaj nerede?','Başarıdan sonra doluluk'],[
            ['<code>xQueueSendToBack()</code>','Yeni mesaj arka uca eklenir','+1'],
            ['<code>xQueueSendToFront()</code>','Yeni mesaj ön uca eklenir','+1'],
            ['<code>xQueueReceive()</code>','Ön eleman kopyalanır ve çıkarılır','−1'],
            ['<code>xQueuePeek()</code>','Ön eleman kopyalanır; queue içinde kalır','Değişmez']])+call('<code>xQueueSend()</code>, <code>xQueueSendToBack()</code> ile eşdeğerdir. Başarı için <code>pdPASS</code> kontrol edilir.'),
        'Front/Back fiziksel RAM adresi değildir. Kuyruğun mantıksal sırasını anlatır. Receive her zaman front elemanını alır; front kullanıldıktan sonra bu eleman en eski gönderilen mesaj olmak zorunda değildir. Send/Receive veri kopyalama API’leridir.'))
    block.append(slide('03 / Etkileşimli queue laboratuvarı','Gönder. Oku. <span class="accent">Sırayı izle.</span>','Send to Front, Send to Back, Receive ve Peek işlemlerini aynı kuyrukta deneyin.',
        (root/'assets/queue-lab.html').read_text(encoding='utf-8'),
        'Rehberli örnek düğmesine her basış bir işlem yapar: Back 10, Back 20, Front 99, Peek, Receive, Receive. Önce öğrencilerden sıradaki çıkışı tahmin etmelerini isteyin. Altı kapasiteyi doldurup Front deneyin: baştaki mesajı ezmez; errQUEUE_FULL döner. Kuyruk boşken Receive ve Peek başarısızdır, out değişmez. Diyagramdaki kayma mantıksal sıra değişimidir; kernel bütün elemanları RAM’de kaydırıyor anlamına gelmez. Model yalnız sıralama içindir; sonraki model bloklanma ve timeout’u gösterir.'))
    block.append(slide('03 / Tasarım kararı','Öne eklemek bir seçimdir.<br>Ücretsiz öncelik değildir.','Send to Front mesaj sırasını değiştirir; task önceliğini veya kapasiteyi değiştirmez.',
        cols(panel('Yeni öne gönderim','<p>[10, 20] kuyruğuna önce 99, sonra 88 öne gönderilirse sıra <b>[88, 99, 10, 20]</b> olur.</p><p>Yeni öne eklenen, önceki öne ekleneni de geçer.</p>'),
             panel('Dolu kuyruk','<p>Front ve Back için aynı kapasite sınırı geçerlidir.</p><p>0 tick ile doluysa başarısız döner; dolu kuyruğun en eski elemanını otomatik silmez.</p>'),
             panel('Adalet / starvation','<p>Sürekli öne veri eklenmesi arkadaki mesajları uzun süre bekletebilir.</p><p>Send to Front, mesajlara sayısal öncelik atayan genel bir priority queue değildir.</p>'))+
        call('Ders deneyi A/B/C, arkaya gönderim kullanmaya devam eder. Bu etkileşimli bölüm, farklı API’lerin sıralama davranışını karşılaştırır.')+
        '<p class="mini">Başvuru: <a href="https://github.com/FreeRTOS/FreeRTOS-Kernel-Book/blob/main/ch05.md" target="_blank" rel="noopener">FreeRTOS / Queue Management</a> · Yerel API: firmware/vendor/freertos/include/queue.h</p>',
        'Hangi task CPU alacak sorusunu scheduler, hangi mesaj okunacak sorusunu queue sırası belirler. Task önceliğini artırmak kuyruktaki mesajları yeniden sıralamaz. Task önceliği yükseltilmediği halde Receive çıktısının değişebildiğini vurgulayın. Bu haftanın ölçümlü ödevinde Front eklemeyin; A/B kapasite ve A/C timeout karşılaştırmalarındaki tek değişken korunmalı. Ek alıştırma olarak sürekli Front gönderimi altında eski mesajın kaç adım beklediğini tartışabilirsiniz.'))
    at=next(i for i,s in enumerate(lesson) if s['title'].startswith('xQueueReceive'))+1
    lesson[at:at]=block
