# STM32F407G-DISC1 - Donanım doğrulama oturumu

Bu aşama kart bağlandığında uygulanacak. 12 Ekim 2026 hazırlığında uygulanmadı.

## Bağlantı ve sürüm

1. Kart üstündeki MCU'nun STM32F407VG olduğunu doğrula. ST-LINK USB programlama/debug içindir.
2. Önceki USB-TTL düzeni: adaptör RX -> PA2, TX -> PA3, GND -> GND; 3,3 V lojik. Adaptör VCC/5 V hattını bağlama. USART2 230400 baud, 8N1.
3. PA0 USER butonu bu yük protokolünde kullanılmaz. Yeşil LD4/PD12 koşu sırasında yanar. Kırmızı LD5/PD14 fatal durumda yanar; debugger'da fault_file/fault_line incelenir.
4. `python firmware/build.py --config Release` çalıştır. ELF/HEX'in SHA256'sı build.json içindedir. Tüm yedi koşuda aynı Release binary kullan.
5. STM32CubeProgrammer'da ST-LINK/SWD ile bağlan, hedef kimliğini doğrula, mevcut firmware gerekiyorsa yedekle. `firmware/build/Release/week3_f407.hex` yükle, doğrulamayı etkinleştir, ardından Run/Reset. CubeIDE alternatifi: aynı ELF ile debug ve Resume. Ölçümde breakpoint bırakma.
6. USB-TTL portunu `python -m serial.tools.list_ports` ile bul. Eski terminalleri kapat; bir portu yalnız kayıt aracı açsın.

Discovery kartındaki ST-LINK VCP uçlarının hedef USART'a kendiliğinden bağlı olmadığına ilişkin resmî kaynak: [ST UM1472](https://www.st.com/resource/en/user_manual/dm00039084.pdf). Bu proje lehim/jumper değişikliği gerektiren VCP yolunu kullanmaz.

## İlk açılış kabulü

- [ ] Firmware MCU/saat/baud yanıtı: `#HELLO,WEEK3,1,STM32F407VG,230400,168000000`.
- [ ] `BUILD` yanıtı yerel Release build.json kimliğiyle eşleşiyor (capture aracı kontrol eder).
- [ ] A/NORMAL pilotunda 44 girişim, sayaç tutarlılığı, UART hata/drop=0, pozitif stack headroom.
- [ ] Yeşil LED koşu sonunda sönüyor; kırmızı LED yanmıyor.
- [ ] SystemView dosyası açılıyor, Producer/Consumer/Console isimleri ve W3 olayları görünüyor.
- [ ] TIM2 1 MHz ve DWT 168 MHz ölçekleri mantıklı. Yaklaşık 100 ms normal aralar ve yaklaşık 20 ms servis beklemesi görülüyor. Bu gözlem hassas saat kalibrasyonu yerine geçmez.

Pilot başarılıysa `python tools/run_matrix.py --port <PORT>` çalıştır. Yedi koşuyu kesintisiz aynı binary ile tamamla. Araç hata verirse matris eksik işaretlenir; sorunu çözdükten sonra matrisi yeniden çalıştır. Aynı senaryo dosyaları yenilenir. Kartı matris ortasında resetleme.

## Dosyalar ve trace incelemesi

Her koşu için `.txt` ham seri, `.csv` 44 girişim, `.json` kimlik/sayaç/hash; altı trace açık koşu için `.SVDat`. Trace kapalı yedinci koşuda SVDat beklenmez. Matris `session.json` içinde indekslenir. Matris tamamlanınca `python tools/analyze.py measurements/hardware` çalıştır. Dosyalar tarih eki olmadan, örneğin `A_NORMAL_trace1.csv` adıyla tutulur ve başarılı tekrarda üzerine yazılır. CSV ayıracı noktalı virgüldür; Türkçe Excel sütunları doğrudan açar. Yeni kayıt öncesinde ilgili CSV/SVDat dosyasını kapat.

SystemView mevcut kurulumu kullanılabilir: önceki haftadaki `tools/SystemView-4.10a` veya kurulu sürüm. Bu projenin kernel'i FreeRTOS 11.1.0'dır. Hafta 2'nin özel 10.3.1 olay açıklamalarını körlemesine kopyalama; FreeRTOS 11 API açıklamaları ve W3 modül açıklamalarının doğru çözüldüğünü kontrol et. Kaynak adaptörü `firmware/vendor/systemview/Sample/FreeRTOSV11` altındadır.

Nominal pencere 200 ms, buffer 32768 bayt. NORMAL ilk mesaj, BURST id=11 öncesinden başlar. drops=0, checksum/byte sayısı doğru olmalıdır. stop_reason=1 süre, 2 buffer sınırına yaklaşma, 0 diğer durdurma. Erken duran pencereyi tam 200 ms gibi etiketleme. Trace kaybında koşu otomatik geçerli sayılmaz; pencereyi değiştirmen gerekirse tüm karşılaştırma koşullarını tutarlı ayarla, yeniden build al ve matrisi tekrarla.

## Üç kanıt görseli

`analysis/figures/` altında daha sonra kaydet; her görsele run_id, mesaj id, zaman aralığı ve kaynağın SVDat adını yaz.

1. `A_BURST.png`: SEND_BEGIN -> SEND_FAIL; kuyruk doluluğu bağlamını API olaylarıyla açıkla.
2. `B_BURST.png`: A'ya göre kabul/bekleme farkı. B'nin sonraki receive olayları pencere dışında kalabilir; bütün koşunun sayıları için CSV kullan.
3. `C_BURST.png`: send sırasında Producer Blocked, Consumer receive, Producer'ın tekrar ilerlemesi. SEND_OK yalnız enqueue başarısıdır; RECEIVE ve DONE ayrı olaylardır.

## Son teslim kapısı

- [ ] Yedi koşu `analyze.py` doğrulamasından geçti.
- [ ] Aynı firmware/build ID kullanıldı; binary ve kaynak manifesti arşivlendi.
- [ ] Üç gerçek SystemView görseli ve bir sayfalık politika yorumu tamamlandı.
- [ ] 3-5 dakikalık video kaydedildi; bir mesaj olay zinciriyle anlatıldı.
- [ ] AI desteği, referans kullanımı ve ölçüm sınırları yazıldı.
- [ ] GitHub kod bağlantısı, video ve kurs teslimi kullanıcı tarafından son kez kontrol edildi.
