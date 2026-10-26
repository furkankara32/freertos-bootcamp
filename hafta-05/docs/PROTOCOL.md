# Seri protokol v1

Her çerçeve tam 100 bayt. Little-endian: `magic[2]='W5', version:u8=1, type:u8, seq:u32, values[22]:u32, reserved[2]=0, crc:u16`.

CRC-16/CCITT-FALSE, init FFFF, poly 1021, refin/refout false, xorout 0. İlk 98 bayt üzerinden hesaplanır. Kontrol vektörü `123456789 → 29B1`.

| Host type | Komut | values |
|---:|---|---|
| 1 | HELLO | boş |
| 2 | START | run_id, scenario 1–4, variant 0–2, led_ms, cycles, trace_ms (en fazla 2000) |
| 3 | STOP | Bekleyen komutları iptal eder, LED'leri söndürür |
| 4 | LOAD | Payload işlenmeden sayılır; 100 çerçeve = 10 KB |
| 5 | WORK | CPU iş birimi (başlangıçta ms için kalibre edilir), en fazla 200 |
| 6 | SEQUENCE | ilk üç alan ayrılmış; led_ms, cycles |
| 7 | TRACE | trace_ms; mevcut RAM kaydını yeniler |
| 8 | STATUS | boş |
| 9 | DIAG | 20 adet 100 bayt tanı raporu üretir |

Kart type 128–135: HELLO, ACK, RUN_START, LED, DONE, STATUS, ERROR, DIAG.

LED values: run_id, command_id, old_color, new_color, planned_us, actual_us, previous_on_us, actual_duration_us, lateness_us, period_us. Renk 0 yeşil, 1 turuncu, 2 kırmızı, 3 mavi, 4 kapalı. İlk yanışta old_color=4; bu kayıt açık kalma süresi hesabına katılmaz.

STATUS values: run_id, request_id, active, rx_bytes, rx_drop, rx_error, parser_rejected_bytes, command_drop, report_drop, load_frames, rx_high_water, command_queue_depth, trace_bytes, trace_dropped, trace_complete, trace_reason, tx_frames, scenario, variant, parser_stack_high_water, free_heap, timer_us.

Trace reason 1: süre sonu; 2: RAM koruma eşiği. Sayımlar boot'tan beri birikir; koşu karşılaştırmasında başlangıç/son farkı alınmalıdır. Parser rejected bytes, bağımsız bozuk çerçeve sayısı değildir.

STOP hattaki önceden yazılmış baytları geçemez. UI yalnız kendi bekleyen gönderimlerini iptal edebilir. SystemView verisi bu seri protokole karıştırılmaz; SWD ile alınır.
