# Anlık Sistem Sesi Transkript Uygulaması

Bu uygulama, bilgisayarınızın hoparlöründen (sistem sesi) gelen sesi anlık olarak dinleyip transkripte dönüştürmek için geliştirilmiş bir Python uygulamasıdır. Arka planda çalan videoların veya herhangi bir ses kaynağının konuşmalarını gerçek zamanlı olarak metne çevirebilirsiniz.

## Özellikler

- **Sistem sesi (hoparlör) üzerinden doğrudan kayıt** (Windows'ta)
- **Gerçek zamanlı konuşma tanıma** ve anlık transkript
- **Çoklu dil desteği** (Türkçe, İngilizce, Almanca, Fransızca, İspanyolca)
- **Özelleştirilebilir ayarlar**:
  - Kayıt süresi ayarı (1-30 saniye)
  - Ses algılama eşiği ayarı (100-1000)
- **Transkriptleri zaman damgalarıyla kaydetme**
- **Kullanıcı dostu arayüz**

## Ekran Görüntüsü

![Uygulama Ekran Görüntüsü](screenshot.png)

## Gereksinimler

Uygulamayı çalıştırmak için aşağıdaki kütüphanelere ihtiyacınız vardır:

```
PyQt5==5.15.9
SpeechRecognition==3.10.0
pyaudio==0.2.13
numpy==1.24.3
```

## Kurulum

1. Gerekli kütüphaneleri yükleyin:

```bash
pip install -r requirements.txt
```

2. Uygulamayı çalıştırın:

```bash
python gui_transcriber.py
```

## Kullanım

1. Uygulamayı başlatın
2. Ses kaynağını seçin:
   - Sisteminizdeki mikrofonlar
   - Stereo Mix, What U Hear veya benzer bir cihaz (sistem sesini kaydetmek için)
3. Dil seçin (varsayılan: Türkçe)
4. Kayıt süresini ayarlayın:
   - Daha kısa süre (1-2 saniye): Daha anlık transkript, ancak daha fazla CPU kullanımı
   - Daha uzun süre (3-5 saniye): Daha az anlık transkript, ancak daha az CPU kullanımı
5. Ses algılama eşiğini ayarlayın:
   - Düşük değer (100-300): Daha hassas ses algılama, ancak daha fazla gürültü
   - Yüksek değer (400-1000): Daha az hassas ses algılama, ancak daha az gürültü
6. "Transkript Başlat" butonuna tıklayın
7. Uygulama seçilen kaynaktan gelen sesi dinlemeye başlayacak ve konuşmaları metne çevirecektir
8. Transkript işlemini durdurmak için "Durdur" butonuna tıklayın
9. Transkripti kaydetmek için "Transkripti Kaydet" butonuna tıklayın

## Nasıl Çalışır?

1. Uygulama, seçilen ses kaynağını kullanarak sesi yakalar
2. Yakalanan ses, Google Speech Recognition API kullanılarak metne dönüştürülür
3. Dönüştürülen metin, zaman damgasıyla birlikte arayüzde gösterilir
4. Cümle tamamlama özelliği sayesinde, yarım kalan cümleler bir sonraki kayıtla birleştirilir
5. Transkript işlemi, siz durdurana kadar devam eder

## Sistem Sesi Kaydı (Windows)

Windows'ta sistem sesini (hoparlör) kaydetmek için:

1. Ses kaynağı olarak "Stereo Mix", "What U Hear" veya benzer bir cihaz seçin
2. Bu tür bir cihaz yoksa:
   - Ses ayarlarından "Stereo Mix" cihazını etkinleştirin
   - Veya harici bir mikrofonu bilgisayarınızın hoparlörüne yakın tutun

## İpuçları

- Sistem sesi kaydı kullanırken, bilgisayarınızın ses seviyesinin yeterince yüksek olduğundan emin olun
- Kayıt süresini kısaltarak daha anlık transkript elde edebilirsiniz
- Ses algılama eşiğini ortama göre ayarlayın (sessiz ortamda düşük, gürültülü ortamda yüksek)
- Uzun konuşmaları transkript ederken, düzenli olarak kaydetme yapmanız önerilir
- Transkript kalitesi, ses kalitesine ve konuşmanın netliğine bağlıdır

## Notlar

- Konuşma tanıma için Google Speech Recognition API kullanılmaktadır
- Türkçe dil desteği mevcuttur
- İnternet bağlantısı gereklidir
- Konuşma tanıma doğruluğu, ses kalitesi ve ortam gürültüsüne bağlı olarak değişebilir
- Sistem sesi kaydı özelliği sadece Windows'ta desteklenmektedir

## Sorun Giderme

- **Ses kaydı yapılamıyor**: Seçilen cihazın doğru olduğundan emin olun
- **Transkript eksik veya hatalı**: Kayıt süresini ve ses algılama eşiğini ayarlayın
- **Sistem sesi kaydedilemiyor**: Windows ses ayarlarından "Stereo Mix" cihazını etkinleştirin
- **CPU kullanımı yüksek**: Kayıt süresini artırın

## Lisans

Bu proje açık kaynaklıdır ve eğitim amaçlı olarak kullanılabilir. 