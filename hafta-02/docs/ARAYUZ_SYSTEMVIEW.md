# Arayüzden SystemView kaydı

**Çift tıklayarak aç:** `Arayuz/Guncel/BootcampMonitor/BootcampMonitor.exe` veya hafta-02 altındaki `Hafta-02 Arayuz.lnk` kısayolu. EXE ile `_internal` klasörü birlikte kalmalı; bu paket yerel hafta-02 araçlarını ve Python ortamını kullanır. Tek EXE'yi başka bir klasöre taşıma.

PowerShell alternatifi:

```powershell
cd D:\freertos-bootcamp\hafta-02
.\tools\open-interface.ps1
```

Bu başlatıcı V1 için 115200 baud seçer. V2-QWB için arayüzde 460800 seçin veya `-Baud 460800` verin. Hafta-01'in eski arayüzü / EXE'si bu yeni paneli içermez. Hafta-02'deki V2 arayüzü hem V1 hem V2-QWB kart yazılımını destekler.

1. ST-LINK USB ve USB-TTL bağlantıları takılı olsun. Başka seri terminali ve aktif debug bağlantısını kapatın.
2. Gerçek COM portunu, karta uygun baud'u seçip **Bağlan** düğmesine basın. Önceki deney varsa **Önceki kaydı al** ile koruyun.
3. S0 veya S5 seçin, **Senaryoyu uygula**, ardından **Başlat** seçin. Isınma bitip **ARMED** görünmesini bekleyin.
4. SystemView panelinde ELF yolunun karta yüklenen derlemeye ait olduğunu kontrol edin. Farklı bir derleme yüklediyseniz **Yüklü ELF seç** ile onu seçin; CubeIDE ELF dosyasında `build.json` zorunlu değildir; gerekli SystemView sembolleri kontrol edilir. build.json varsa ELF hash ve profil kontrolü ayrıca yapılır. Arayüz karta firmware yüklemez; ELF hash'ini build.json ile doğrular fakat MCU'daki yazılım hash'ini okuyamaz.
5. Başlangıç için S0'da 1000 ms, S5'te 500 ms seçin. **SystemView için kaydet** düğmesine basın. Üç saniyelik hazırlık sayacı sonunda **KAYIT AÇIK** yazınca mavi USER butonuna basın.
6. Süre bitince arayüz ST-LINK üzerinden RAM'deki kaydı dosyaya çıkarır. UART aynı bağlantıda okunmaya devam eder. Kayıt/aktarım bitene kadar deney kontrol düğmeleri kilitlidir.
7. **Kayıt hazır** yazınca **SystemView’da aç** veya **Klasörü aç** seçin. Birden fazla pencere aldıysanız açılır listeden istediğinizi seçin. Bu liste mevcut arayüz oturumundaki başarılı kayıtları gösterir; eski kayıtlar diskten açılabilir.
8. Deney devam eder. Yeni pencere almak için tekrar kaydet düğmesine basabilirsiniz. Sonunda **Durdur ve aktar** ile normal CSV/ölçüm kaydını tamamlayın. Aynı bağlantı ve run'a ait izleme manifestlerine ölçüm klasörü eklenir.

Varsayılan dosya konumu:

```
hafta-02/measurements/systemview/<V1 veya QWB>/<senaryo>/<tarih-saat>/
  recording.SVDat  # SystemView'da açılacak dosya
  trace.json      # tamamlanma, taşma, boyut ve SHA256
  session.json    # sürüm, run, aktif senaryo, build, kayıt durumu
  openocd.log
  export.log
  ram.bin         # ham SRAM, SystemView'da doğrudan açılmaz
```

**Kayıt konumu** seçimi bu yolu da değiştirir. Dışa aktarma veya doğrulama hatasında kısmi dosyalar hata manifestiyle korunur ve kayıt başarılı listeye eklenmez. `clean: true` uygulamada buton kaybı olmadığı anlamına gelmez; yalnız trace olay kaybının olmadığı anlamına gelir.

Demo modunda donanımsal kayıt düğmesi kapalıdır. 2000 ms üst sınırı tamponun her senaryoda yeterli olacağı garantisi değildir; taşmada süreyi kısaltın. Fiziksel basış pencereye denk gelmediyse başka kısa kayıt alın. RTT kaydı kısa bir pencereyi, Durdur ve aktar dökümü tüm deneyin uygulama ölçümlerini kapsar.

TRACE komutu firmware'de ACK üretmez; kayıt zamanı SerialWorker'ın komutu gerçekten porta yazdığını bildirmesiyle başlar. Host sayaçları donanım zaman damgası değildir. Kayıt süresi bittiğinde CPU durdurulmaz; yalnız izleme tamponu sabitlenir. Mevcut firmware ve deney tasarımları değiştirilmemiştir.

## CubeIDE'den yükleyerek kullanma

ELF, CubeIDE'nin derleme sonucu ürettiği dosyadır. Arayüz ELF içindeki sembol adresleriyle RAM'deki izleme tamponunu bulur; dosyayı karta yüklemez.

1. Hafta-02 içindeki ilgili projeyi CubeIDE'de aç: `projects/v1/firmware/Homework_001` veya `projects/v2/firmware/Homework_001`. Eski hafta-01 projesi yerine izleme eklenmiş bu kopyayı kullan.
2. Debug/Release derlemelerinin C compiler symbols ayarına `APP_TRACE=1` eklendi. Karşılaştırma için aynı Release ayarını kullan. V2 varsayılan profil QWB'dir.
3. Build Project ile derle. CubeIDE Run/Debug Configuration içindeki **C/C++ Application** alanının bu derlemenin ELF dosyasını gösterdiğini kontrol edip karta yükle.
4. Kartı çalışır bırak; breakpoint üzerinde durmasın. Aktif debug oturumunu kapatıp ST-LINK'i serbest bırak. Gerekirse kartı resetleyerek normal çalışmasını başlat.
5. Arayüzde karta bağlan. **Yüklü ELF seç** ile gerçekten karta yüklediğin dosyayı seç:
   - V1 Release: `projects/v1/firmware/Homework_001/Release/Homework_001.elf`
   - V2 Release: `projects/v2/firmware/Homework_001/Release/Homework_001.elf`
   - Debug kullandıysan aynı projedeki `Debug/Homework_001.elf` dosyasını seç.
6. Senaryoyu uygula, başlat, ARMED'i bekle ve SystemView kaydını al.

Kod/derleme ayarı değiştiğinde yeniden derleyip karta yükle; arayüzde o ELF'i kullan. Varsayılan otomatik ELF yolu Python build.py çıktısına gider. CubeIDE'den yüklediğinde **Yüklü ELF seç** ile CubeIDE çıktısını seçmen gerekir. Arayüz seçilen ELF'in MCU'dakiyle aynı olduğunu otomatik kanıtlayamaz; sembol ve dosya kontrollerini yapar.

6 Ekim 2026 doğrulaması: paketlenmiş EXE açılış/ekran testi; GUI testleri; CubeIDE Release derlemeleri. Gerçek kart bu aşamada bağlı olmadığından yeni uçtan uca donanım kaydı alınmadı.

## Kayıt süresi ve son kontrol

Isınma en az 5 saniyedir; ardından kuyruklar boşaltılıp ARMED durumuna geçilir. Bu süre SystemView kaydına dahil değildir. Kayıt düğmesinin 3 saniyelik hazırlık sayacı da kayıt süresine dahil değildir. S0 için 1000 ms, S5 için 500 ms ile başlayın. Arayüz gerçek senaryo değişince bu başlangıç değerlerini seçer; isterseniz elle değiştirebilirsiniz.

İzin verilen aralık 50–2000 ms'dir. 64 KiB tampon yüzünden 2000 ms kayıpsızlık garantisi değildir. Kayıt kaybı oluşursa süreyi azaltıp yeni pencere alın. Butona KAYIT AÇIK yazısının başlangıcında basın; pencere sonunda basılan olayın tamamlanması kaydın dışında kalabilir. Kaydın bitişi ile RAM aktarımı arasında ayrıca kısa bir bekleme vardır; bu aşamada yeni basışlar bu pencereye dahil olmaz.

Kayıt klasöründe firmware.elf kopyası da saklanır; dışa aktarım bu sabit kopyanın sembollerini kullanır. Böylece IDE'nin aynı dosyayı yeniden üretmesi sürmekte olan dışa aktarımın adreslerini değiştirmez. Karta yeniden yazılım yüklenirse mevcut koşuyu bitirip doğru ELF ile yeni koşu başlatın.

Güncel EXE: Arayuz/Guncel/BootcampMonitor/BootcampMonitor.exe. Hafta-02 Arayuz kısayolu bu sürüme yönlendirilmiştir. Daha önce açılmış eski arayüzü kapatıp bu kısayolla tekrar açın.
