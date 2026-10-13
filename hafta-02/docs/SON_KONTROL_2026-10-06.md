# Son kontrol - 6 Ekim 2026

- V2 tam test takımı: 82 geçti (GUI, SystemView, protokol ve yerel firmware testleri).
- V1 test takımı: 21 geçti.
- Güncel paketli EXE açılış testi: çıkış kodu 0; ekran görüntüsü görsel olarak kontrol edildi.
- CubeIDE V1/V2 Release derlemeleri önceki adımda sıfır hata ve sıfır uyarıyla tamamlandı; bu kontrolde firmware kaynakları değiştirilmedi.
- Isınmada kayıt kilidi, senaryo varsayılanları, gerçek UART yazımından sonra zamanlama, aktarım hataları, metadata hataları, ELF kopyasının yeniden derlemeden etkilenmemesi test edildi.
- Güncel EXE: Arayuz/Guncel/BootcampMonitor/BootcampMonitor.exe. Hafta-02 Arayuz.lnk güncellendi.
- Donanım sınırı: COM aygıtı bulunamadı. Bu kontrolde fiziksel butonla yeni uçtan uca kayıt alınmadı. Firmware ile ELF'in eşleşmesi operatörün sorumluluğunda; testler gerçek donanım zamanlaması kanıtı değildir.

S0: 1000 ms. S5: 500 ms. Isınma ve üç saniyelik geri sayım bu sürelere eklenmez. Aralık 50–2000 ms; tampon kaybı durumunda süre azaltılır.
