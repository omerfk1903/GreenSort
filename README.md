# GreenSort

NOT : GreenSort projesi geliştirme aşamasında olması sebebiyle bazı fonksiyonlar çalışmıyor durumdadır ama temel yapması gereken işlemleri yapıyor.

GreenSort cihazı atık ayırma projesidir.Projenin temel amacı, geri dönüştürülebilir atıkların ayrımının yapılabilmesidir. Geri dönüştürülebilir ise atıkların ana maddesine göre bölgelere ayrılıyor.

<img src="GreenSort/img/GreenSort.jpg" alt="Proje Görseli" width="500" height="200"/>

Projede yapay zeka uygulamaları için YOLOv8 kütüphanesi kullanılmıştır. Yapay zeka modeli, Google Colab altyapısı üzerinde, Roboflow platformundaki hazır görüntüler ve kendimizizn çektiği fotoğraflar ile eğitilmiştir.

<img src="GreenSort/img/colob.jpg" alt="Proje Görseli" width="500" height="200"/> <img src="GreenSort/img/roboflow.jpg" alt="Proje Görseli" width="500" height="200"/>

<img src="GreenSort/img/Camo.jpg" alt="Proje Görseli" width="50" height="50"/> - Telefonun kamera görüntüsü CAMO uyuglaması kullanılarak aktarılıyor.

- Projenin yazılım kısmında python ve C/C++ programlama dilleri kullanılmıştır.
- python programla dili Görüntü işleme ,yapay zeka ,Socketler arası iletişim ve menü oluşturmada kullanılmıştır.
- C/C++ programlama dili ise mikrodenetleyicinin servo , motor ve motorların çalışma süresi gibi işlemleri yapmak için kullanılmıştır.

# Çalışma diyagramı :  

  - Kontrol sistemi ile yapay zeka arasındaki soket bağlantısı üzerinden komutlar iletilmektedir. Kontrol sistemi bir komut gönderdiğinde, yapay zeka aldığı görüntüde geri dönüştürülebilir bir atık tespit ederse, atığın türüne uygun kutunun servo motorları açılır. Geri dönüşüm atığı, servo motor yardımıyla ilgili kutuya yönlendirilirken bu süreç boyunca motorlar çalışır. İşlem tamamlandığında motorlar durur, servo kapanır ve geri dönüşüm atığı kutuya bırakılır. Bir sonraki işlem, kontrol sisteminden yeni bir komut alınıncaya kadar başlatılmaz.

<img src="GreenSort/img/Diyagram.jpg" alt="Proje Görseli" width="1000" height="350"/>

# Kullanılan malzemeler  : 
    
    1-) Arduino 
    
    2-) Ana bilgisayar(Kişisel bilgisayarım) veya raspberry gibi mini bilgisayarlarda kullanılabilir.
    
    3-) 2 tane servo 
    
    4-) 12v motor 
    
    5-) bant 
    
    6-) kamera(kişisel telefonumu kullandım) 

    7-) AC-DC Dönüştürücü 220v-12v

    8-) Röle 






