"""Visual explanation of the three Queue_t bookkeeping fields."""
def extend_control(lesson, slide, code, cols, panel, call):
    block = [slide('03 / Queue control block', 'Mesajlar ayrı.<br><span class="accent">Bekleyen task’lar ayrı.</span>',
        'Queue_t, veriyi ve bu veriyi bekleyen task’ları üç farklı alanla takip eder.',
        '<div class="qc-overview">' +
        panel('01 / uxMessagesWaiting', '<div class="qc-symbol">3 / 4</div><p>Queue içindeki <b>mevcut mesaj sayısı</b>. Task sayısı veya bayt sayısı değildir.</p><small>volatile UBaseType_t</small>') +
        panel('02 / xTasksWaitingToSend', '<div class="qc-symbol amber">P3 → P1</div><p>Queue doluyken <b>yer açılmasını bekleyen göndericiler</b>. Öncelik sıralı event listesi.</p><small>List_t</small>') +
        panel('03 / xTasksWaitingToReceive', '<div class="qc-symbol blue">P4 → P2</div><p>Queue boşken <b>mesaj gelmesini bekleyen alıcılar</b>. Öncelik sıralı event listesi.</p><small>List_t</small>') + '</div>' +
        call('Mesaj depolama alanı payload kopyalarını tutar. Bekleme listeleri ise task’ın <code>xEventListItem</code> düğümünü bağlar; mesajı veya TCB’nin tamamını kopyalamaz.') +
        '<p class="mini">Kernel iç isimleri: <code>uxMessagesWaiting</code>, <code>xTasksWaitingToSend</code>, <code>xTasksWaitingToReceive</code>. Uygulama bu özel alanları doğrudan değiştirmez.</p>',
        'Bu üç alan tüm Queue_t değildir. pcHead, pcWriteTo, uxLength, uxItemSize ve kilit alanları da vardır. Sonraki görseller normal queue için öğretici olay adımlarıdır; tüm kernel veya scheduler simülasyonu değildir.')]
    for mode,title,lead,note in [
        ('count','İçeride kaç mesaj var?', 'uxMessagesWaiting: başarılı gönderimde +1, başarılı okumada −1.', 'Peek yalnız sayacı değiştirmez. Genel kernel davranışında Peek başka bir bekleyen alıcıyı uyandırabilir; burada bekleyen task yoktur. uxQueueMessagesWaiting(q) anlık değer verir; bu değer daha sonraki Send/Receive sonucunu garanti etmez.'),
        ('send','Yer açılmasını kim bekliyor?', 'xTasksWaitingToSend: dolu queue → Blocked göndericiler → bir slot açılır → bir task Ready.', 'En yüksek öncelikli bekleyen gönderici uyandırılır. Ready olmak gönderimin tamamlandığı anlamına gelmez. Slot task’a rezerve edilmez. Bekleme parametresi API çağrısının duvar saatindeki kesin üst sınırı değildir: timeout sonrası CPU alması scheduler’a bağlıdır. Gerçek preemptive sistemde yüksek öncelikli task hemen çalışabilir; burada öğretim amacıyla Ready ve Running adımları ayrılmıştır.'),
        ('receive','Mesaj gelmesini kim bekliyor?', 'xTasksWaitingToReceive: boş queue → Blocked alıcılar → mesaj gelir → bir task Ready.', 'Listeler task önceliğine göre tutulur. Mesaj sırası ile task önceliği farklı kavramlardır. Timeout süresi olan task ayrıca kernel’in gecikme takibindedir; timeout event listesinden de çıkarır. Ready checkpoint’i öğretim amaçlıdır; gerçek sistemde bağlam değişimi hemen olabilir.')]:
        body=f'''<section class="qc-lab" id="queueControl" data-mode="{mode}">
          <div class="qc-toolbar"><span class="tag">QUEUE_t / İÇ DURUM</span><span data-qc="step"></span><button data-qc="reset">Sıfırla</button></div>
          <div class="qc-grid"><div class="qc-storage"><div class="qc-label">MESAJ DEPOLAMA ALANI · FRONT → BACK</div><div class="qc-slots" data-qc="slots"></div><div class="qc-meter"><i data-qc="meter"></i></div><p class="mini">Kapasite: <b>3 mesaj</b> · Her kutu bir payload kopyası</p><div class="qc-ready"><div class="qc-label">TASK DURUMU / CPU TARAFI</div><div data-qc="ready"></div></div></div>
          <div class="qc-block"><div class="qc-field"><code>uxMessagesWaiting</code><b data-qc="count">0</b></div><div class="qc-field-list"><code>xTasksWaitingToSend</code><div data-qc="send"></div></div><div class="qc-field-list"><code>xTasksWaitingToReceive</code><div data-qc="receive"></div></div></div></div>
          <div class="qc-event" aria-live="polite"><b data-qc="title"></b><p data-qc="description"></p><code data-qc="api"></code></div>
          <div class="qc-controls" data-qc="controls"></div>
        </section>'''
        body += '<p class="mini">Öğretici model · Normal queue, task bağlamı · Büyük P değeri yüksek öncelik. Kaynak: <a href="https://www.freertos.org/Documentation/02-Kernel/02-Kernel-features/02-Queues-mutexes-and-semaphores/01-Queues" target="_blank" rel="noopener">FreeRTOS Queues</a> · Yerel queue.c / tasks.c</p>'
        block.append(slide('03 / Queue control block',title,lead,body,note))
    at=next(i for i,s in enumerate(lesson) if s['title'].startswith('Öne eklemek'))+1
    lesson[at:at]=block
