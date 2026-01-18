# Aura - Premium Dijital Saat v1.0.0

Aura, Python ve CustomTkinter kullanılarak geliştirilmiş, modern, lüks ve kullanıcı dostu bir dijital saat uygulamasıdır. Şık bir "Glassmorphic" tasarım anlayışıyla geliştirilen uygulama, hem estetik hem de fonksiyonelliği bir arada sunar.

![Aura Clock Preview](aura_icon.png)

## 🌟 Özellikler

- **Modern Tasarım:** Tamamen özelleştirilebilir, premium kart tabanlı arayüz.
- **Dinamik Temalar:** 6 farklı lüks renk paleti (Midnight Sky, Forest Edge, Sunset Glow, Royal Purple, Crimson Red, Silver Slate).
- **Otomatik Konum & Hava Durumu:** IP tabanlı konum algılama ve wttr.in üzerinden anlık Türkçe hava durumu bilgisi.
- **Pomodoro Zamanlayıcı:** Odaklanma sürelerinizi yönetmek için şık bir zamanlayıcı.
- **Gelişmiş Alarm:** Basit ve etkili alarm sistemi.
- **Dünya Saatleri:** Seçkin dünya şehirlerinin saatlerini anlık takip edin.
- **Sistem Tepsisi (Tray) Desteği:** Uygulamayı kapatmadan arka planda çalıştırın.
- **Yüksek Özelleştirme:** Şeffaflık ayarı, "Her Zaman Üstte" modu ve Koyu/Aydınlık tema desteği.

## 🚀 Kurulum ve Çalıştırma

### Gereksinimler

- Python 3.11+
- Pip paket yöneticisi

### Adımlar

1. Depoyu klonlayın:
   ```bash
   git clone https://github.com/Memati8383/dijital-saat.git
   cd dijital-saat
   ```
2. Gerekli kütüphaneleri yükleyin:
   ```bash
   pip install customtkinter requests pillow pystray
   ```
3. Uygulamayı başlatın:
   ```bash
   python main.py
   ```

## �️ EXE Oluşturma

Uygulamayı tek bir `.exe` dosyası haline getirmek için PyInstaller kullanabilirsiniz:

1. PyInstaller yükleyin:
   ```bash
   pip install pyinstaller
   ```
2. Aşağıdaki komutu terminalde çalıştırın:
   ```bash
   pyinstaller --noconfirm --onefile --windowed --name "AuraClock" --add-data "C:/Users/USER/AppData/Local/Programs/Python/Python314/Lib/site-packages/customtkinter;customtkinter/" main.py
   ```
   _Not: CustomTkinter'ın yolunu sisteminize göre kontrol ediniz._

## 📄 Lisans

Bu proje MIT lisansı ile lisanslanmıştır.

---

Geliştiren: **Memati8383**
