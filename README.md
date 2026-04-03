# 3B-Balistik-Simülasyon
RK4 (Runge-Kutta 4) sistemi kullanılarak geliştirilmiş, 3 boyutlu balistik simülasyon terminali. Hava yoğunluğu (ISA), Coriolis, Eötvös, Magnus, Aerodinamik Jump ve Spin Drift etkilerini dinamik olarak hesaplar. .50 BMG ve .338 Lapua gibi mühimmatlar için yüksek hassasiyetli yörünge analizi sunar (eğtim amaçlıdır).

* PROJE: Balistik Atış Simülasyonu
* PROJE SAHİBİNİN ADI SOYADI: Kıvanç Altıntopu
* PROJE SAHİBİNİN BÖLÜMÜ: Makine Mühendisliği Hazırlık Öğrencisi
* OKULUN ADI: Manisa Celal Bayar Üniversitesi Mühendislik ve Doğa Bilimlei Kampüsü
* PROJENİN BİTİŞ TARİHİ: 24.02.2026
    
#----------GÜNCELLEMELER----------#

Tarih:28.02.2026:
* Mermi kütüphanesi eklendi artık merminin gerekli değerlerini (yanal alanı.vb)
direk merminin türüne göre kütüphaneden seçiyor kütüphanede olamayan mermileri ise verileri ile birlikte kaydediyor
    
Tarih:02.03.2026:
* Mermilerdeki G1 ve G7 katsayıları eklendi 
* Atmosferdeki etkenler gerçek hayata daha yakın olacak şekil daha dinamikleştirildi

Tarih:06.03.2026:
* Kullanıcıdan alınması gereken değerler input yerine sözlük yapısı olarak alınacak şekilde ayarlandı 
böylece artık değerleri girmek daha kolay hale gelecek    
* Balistik atış simülasyonu RK4 sistemine göre en baştan ayarlandı böylece artık daha keskin sonuçlar alınabiliyor.

Tarih:08.03.2026
* Dürbün sıfırlama sıfırlama seçeneği eklendi. Kullanıcının belirlediği mesafe ve dürbün ayarlarına göre, merminin namludan çıkış vektörünü otomatik olarak hesaplayan bir algoritma eklendi. Bu sayede, ilk atıştaki sapma verileri kullanılarak yapılan ikinci atışta "tam isabet" (sıfır sapma) veya sıfıra en yakın sonuç elde edilmektedir.

Tarih: 03.04.2026
* Dürbün ayarına "daming factor" eklendi bunun sebebi ise çok yüksek sapmalarda dürbün sıfırlama sistemi saçma sonuçlar verebiliyordu
damping factor ile bu sistemin en azından saçma sonuçlar vermesi bir yere kadar engellenildi ama gene de bu eklenti düşük sapmalarda 
sıfırlama hassasiyetini azalltı 
