# Aura - Premium Dijital Saat 🕒

Aura, modern estetiği fütüristik özelliklerle birleştiren, Python ve CustomTkinter ile geliştirilmiş premium bir masaüstü dijital saat uygulamasıdır.

## ✨ Özellikler

- **Modern Tasarım:** Şık, minimalist ve özelleştirilebilir glassmorphic arayüz.
- **Dinamik Temalar:** 6 farklı premium renk paleti (Midnight Sky, Forest Edge, Sunset Glow, vb.).
- **Akıllı Araçlar:**
  - **Alarm:** Sesli uyarı sistemi.
  - **Pomodoro Zamanlayıcı:** Odaklanma seansları için optimize edilmiş sayaç.
  - **Dünya Saatleri:** Farklı şehirlerin anlık zaman takibi.
- **Hava Durumu:** Konum bazlı anlık hava durumu bilgisi (wttr.in entegrasyonu).
- **Otomatik Konum:** IP tabanlı şehir algılama.
- **Sistem Tepsisi (Tray):** Arka planda çalışma ve hızlı erişim.
- **Özelleştirme:** Şeffaflık ayarı, "Her Zaman Üstte" modu ve Koyu/Aydınlık tema desteği.

## 🚀 Kurulum

Projeyi yerel makinenizde çalıştırmak için:

1. Depoyu klonlayın:
   ```bash
   git clone https://github.com/Memati8383/dijital-saat.git
   ```
2. Gerekli kütüphaneleri yükleyin:
   ```bash
   pip install customtkinter pillow requests pystray
   ```
3. Uygulamayı başlatın:
   ```bash
   python 1.py
   ```

## 📦 EXE Oluşturma (Build)

Uygulamayı tek bir `.exe` dosyası haline getirmek için PyInstaller kullanabilirsiniz:

1. PyInstaller'ı yükleyin:
   ```bash
   pip install pyinstaller
   ```
2. Aşağıdaki komutu terminalde çalıştırın:

   ```bash
   pyinstaller --noconsole --onefile --name "AuraClock" --collect-all customtkinter --add-data "clock_settings.json;." 1.py
   ```

   _Not: `--noconsole` terminalin açılmasını engeller, `--onefile` her şeyi tek bir dosyada toplar._

3. Oluşturulan dosya `dist` klasörü içinde yer alacaktır.

## 🛠️ Kullanılan Teknolojiler

- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) - Modern UI bileşenleri.
- [Pillow](https://python-pillow.org/) - Gelişmiş resim işleme ve tray ikon üretimi.
- [wttr.in](https://wttr.in/) - Ücretsiz hava durumu servisi.
- [ip-api.com](https://ip-api.com/) - Coğrafi konum servisi.

## 📄 Lisans

Bu proje MIT lisansı altında lisanslanmıştır.
