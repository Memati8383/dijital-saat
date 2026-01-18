import customtkinter as ctk
import json
import os
import threading
from datetime import datetime, timedelta, timezone
import winsound
import requests
from PIL import Image, ImageDraw
import pystray
from pystray import MenuItem as item
import sys

# --- Üretim Konfigürasyonu ---
SETTINGS_FILE = "clock_settings.json"
VERSION = "1.0.0"

# Uygulama ölçeklendirme ayarları (Yüksek DPI desteği)
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

DEFAULT_SETTINGS = {
    "theme": "Midnight Sky",
    "appearance": "Dark",
    "always_on_top": False,
    "transparency": 1.0,
    "weather_city": "İstanbul"
}

class SettingsManager:
    @staticmethod
    def load():
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    # Mevcut ayarları varsayılanlarla harmanla (yeni özellikler için)
                    return {**DEFAULT_SETTINGS, **data}
            except Exception:
                return DEFAULT_SETTINGS.copy()
        return DEFAULT_SETTINGS.copy()

    @staticmethod
    def save(settings):
        try:
            with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
                json.dump(settings, f, indent=4, ensure_ascii=False)
        except Exception:
            pass

class ModernClockApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.settings = SettingsManager.load()
        
        # --- Pencere Yapılandırması ---
        self.title(f"Aura - Premium Saat v{VERSION}")
        self.geometry("850x570")
        self.resizable(False, False)
        
        # Windows spesifik kapama protokolü
        self.protocol('WM_DELETE_WINDOW', self.on_close_event)
        
        # --- Dinamik Renk Paletleri ---
        self.themes = {
            "Midnight Sky": {"main": "#3B8ED0", "hover": "#1F538D"},
            "Forest Edge":  {"main": "#2DBA4E", "hover": "#1E7E34"},
            "Sunset Glow":  {"main": "#FF8C00", "hover": "#CC7000"},
            "Royal Purple": {"main": "#8A2BE2", "hover": "#6A1FB8"},
            "Crimson Red":  {"main": "#FA5252", "hover": "#E03131"},
            "Silver Slate": {"main": "#868E96", "hover": "#495057"}
        }
        
        # Tema Doğrulama
        self.current_theme = self.settings.get("theme", "Midnight Sky")
        if self.current_theme not in self.themes: self.current_theme = "Midnight Sky"

        # Uygulama Durumu (State)
        self.alarm_time = None
        self.is_alarm_on = False
        self.last_alarm_minute = None
        self.pomodoro_seconds = 25 * 60
        self.pomodoro_running = False
        self.weather_text = "Hava durumu yükleniyor..."
        self.tray_icon = None
        
        # UI Kurulumu
        self.setup_ui()
        self.apply_initial_state()
        
        # Döngüleri Başlat
        self.update_clock_loop()
        self.update_weather_loop()

    def setup_ui(self):
        # Görsel stabilite renkleri
        self.bg_color_main = "#121212"    
        self.bg_color_tabs = "#181818"    
        self.card_bg_color = "#242424"    

        self.configure(fg_color=self.bg_color_main)
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Sekme Görünümü (Tabview)
        self.tabview = ctk.CTkTabview(
            self, 
            corner_radius=25, 
            border_width=1,
            fg_color=self.bg_color_tabs,
            segmented_button_fg_color="#121212",
            segmented_button_unselected_hover_color="#333333",
            bg_color=self.bg_color_main
        )
        self.tabview.grid(row=0, column=0, padx=30, pady=30, sticky="nsew")

        self.tab_clock = self.tabview.add("GÖRÜNÜM")
        self.tab_tools = self.tabview.add("ARAÇLAR")
        self.tab_world = self.tabview.add("DÜNYA")
        self.tab_settings = self.tabview.add("AYARLAR")

        self.setup_clock_tab()
        self.setup_tools_tab()
        self.setup_world_tab()
        self.setup_settings_tab()

    def setup_clock_tab(self):
        self.tab_clock.grid_columnconfigure(0, weight=1)
        self.tab_clock.grid_rowconfigure((0, 1, 2, 3), weight=1)

        self.time_label = ctk.CTkLabel(
            self.tab_clock, 
            text="00:00:00", 
            font=ctk.CTkFont(family="Segoe UI Variable Display", size=140, weight="bold")
        )
        self.time_label.grid(row=1, column=0, sticky="s")

        self.date_label = ctk.CTkLabel(
            self.tab_clock, 
            text="", 
            font=ctk.CTkFont(family="Segoe UI", size=24, weight="normal"),
            text_color="#888888"
        )
        self.date_label.grid(row=2, column=0, sticky="n", pady=(0, 10))

        self.weather_label = ctk.CTkLabel(
            self.tab_clock, 
            text=self.weather_text, 
            font=ctk.CTkFont(size=14, slant="italic"),
            text_color="#666666"
        )
        self.weather_label.grid(row=3, column=0, sticky="n")

    def setup_tools_tab(self):
        self.tab_tools.grid_columnconfigure((0, 1), weight=1)
        self.tab_tools.grid_rowconfigure(0, weight=1)

        # Alarm Kartı
        self.alarm_card = ctk.CTkFrame(self.tab_tools, corner_radius=20, border_width=1, 
                                       fg_color=self.card_bg_color, bg_color=self.bg_color_tabs)
        self.alarm_card.grid(row=0, column=0, padx=15, pady=20, sticky="nsew")
        
        ctk.CTkLabel(self.alarm_card, text="ALARM", font=ctk.CTkFont(weight="bold", size=16)).pack(pady=(20, 10))
        self.alarm_entry = ctk.CTkEntry(self.alarm_card, placeholder_text="08:30", width=120, height=35)
        self.alarm_entry.pack(pady=5)
        
        self.alarm_btn = ctk.CTkButton(self.alarm_card, text="Kur", command=self.toggle_alarm, height=35)
        self.alarm_btn.pack(pady=15)
        
        self.alarm_info = ctk.CTkLabel(self.alarm_card, text="Pasif", text_color="#666666")
        self.alarm_info.pack()

        # Pomodoro Kartı
        self.pomo_card = ctk.CTkFrame(self.tab_tools, corner_radius=20, border_width=1, 
                                      fg_color=self.card_bg_color, bg_color=self.bg_color_tabs)
        self.pomo_card.grid(row=0, column=1, padx=15, pady=20, sticky="nsew")
        
        ctk.CTkLabel(self.pomo_card, text="POMODORO", font=ctk.CTkFont(weight="bold", size=16)).pack(pady=(20, 10))
        self.pomo_display = ctk.CTkLabel(self.pomo_card, text="25:00", font=ctk.CTkFont(size=48, weight="bold"))
        self.pomo_display.pack(pady=10)
        
        p_btns = ctk.CTkFrame(self.pomo_card, fg_color="transparent")
        p_btns.pack(pady=10)
        
        self.pomo_start_btn = ctk.CTkButton(p_btns, text="Başlat", width=75, command=self.start_pomo)
        self.pomo_start_btn.pack(side="left", padx=5)
        self.pomo_reset_btn = ctk.CTkButton(p_btns, text="Sıfırla", width=75, fg_color="#444444", hover_color="#555555", command=self.reset_pomo)
        self.pomo_reset_btn.pack(side="left", padx=5)

    def setup_world_tab(self):
        self.tab_world.grid_columnconfigure(0, weight=1)
        self.tab_world.grid_rowconfigure(0, weight=1)
        
        self.world_scroll = ctk.CTkScrollableFrame(self.tab_world, fg_color=self.bg_color_tabs)
        self.world_scroll.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        
        self.world_widgets = []
        cities = [("Londra", 0), ("İstanbul", 3), ("Tokyo", 9), ("New York", -5), ("Berlin", 1), ("Dubai", 4)]
        for name, offset in cities:
            f = ctk.CTkFrame(self.world_scroll, corner_radius=15, border_width=1, border_color="#222222", 
                             fg_color=self.card_bg_color, bg_color=self.bg_color_tabs)
            f.pack(fill="x", pady=5, padx=10)
            ctk.CTkLabel(f, text=name, font=ctk.CTkFont(size=16, weight="bold")).pack(side="left", padx=25, pady=12)
            l = ctk.CTkLabel(f, text="00:00", font=ctk.CTkFont(family="Consolas", size=20))
            l.pack(side="right", padx=25)
            # Store frame for theme updates
            self.world_widgets.append({"frame": f, "label": l, "offset": offset})

    def setup_settings_tab(self):
        self.tab_settings.grid_columnconfigure((0, 1), weight=1)
        
        # Sol Sütun (Görünüm)
        col1 = ctk.CTkFrame(self.tab_settings, fg_color="transparent")
        col1.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        
        ctk.CTkLabel(col1, text="GÖRÜNÜM", font=ctk.CTkFont(weight="bold")).pack(pady=10)
        self.theme_menu = ctk.CTkOptionMenu(col1, values=list(self.themes.keys()), command=self.change_theme_event)
        self.theme_menu.set(self.current_theme)
        self.theme_menu.pack(fill="x", pady=10)
        
        ctk.CTkLabel(col1, text="Şeffaflık", font=ctk.CTkFont(size=12)).pack(anchor="w")
        self.trans_slider = ctk.CTkSlider(col1, from_=0.4, to=1.0, command=self.change_trans_event)
        self.trans_slider.pack(fill="x", pady=10)

        # Sağ Sütun (Sistem)
        col2 = ctk.CTkFrame(self.tab_settings, fg_color="transparent")
        col2.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        
        ctk.CTkLabel(col2, text="SİSTEM", font=ctk.CTkFont(weight="bold")).pack(pady=10)
        self.ontop_sw = ctk.CTkSwitch(col2, text="Her Zaman Üstte", command=self.change_ontop_event)
        self.ontop_sw.pack(pady=10)
        
        self.mode_sw = ctk.CTkSwitch(col2, text="Koyu Tema", command=self.change_mode_event)
        self.mode_sw.select()
        self.mode_sw.pack(pady=10)

        ctk.CTkLabel(col2, text="Hava Durumu Şehri", font=ctk.CTkFont(size=12)).pack(anchor="w", pady=(10, 0))
        self.city_entry = ctk.CTkEntry(col2, placeholder_text="Şehir giriniz...", height=30)
        self.city_entry.insert(0, self.settings.get("weather_city", "İstanbul"))
        self.city_entry.pack(fill="x", pady=5)
        
        self.city_btn = ctk.CTkButton(col2, text="Şehri Güncelle", command=self.change_city_event, height=30)
        self.city_btn.pack(fill="x", pady=5)
        
        self.auto_loc_btn = ctk.CTkButton(col2, text="Konumu Bul (Auto)", fg_color="#333333", hover_color="#444444", 
                                          command=self.auto_locate_event, height=30)
        self.auto_loc_btn.pack(fill="x", pady=5)

        ctk.CTkLabel(col2, text=f"Aura v{VERSION}\n© 2026", text_color="#444444", font=("Arial", 10)).pack(side="bottom", pady=10)

    # --- Döngüler ve İş Mantığı ---
    def update_clock_loop(self):
        now = datetime.now()
        self.time_label.configure(text=now.strftime("%H:%M:%S"))
        
        # Gün ve Ay İsimleri
        days = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]
        months = ["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran", "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"]
        d_str = f"{now.day} {months[now.month-1]} {now.year}, {days[now.weekday()]}"
        self.date_label.configure(text=d_str)

        # Alarm Kontrolü
        current_minute = now.strftime("%H:%M")
        if self.is_alarm_on and self.alarm_time == current_minute:
            if self.last_alarm_minute != current_minute:
                self.last_alarm_minute = current_minute
                threading.Thread(target=self.fire_alarm, daemon=True).start()

        # Pomodoro Kontrolü
        if self.pomodoro_running and self.pomodoro_seconds > 0:
            self.pomodoro_seconds -= 1
            m, s = divmod(self.pomodoro_seconds, 60)
            self.pomo_display.configure(text=f"{m:02d}:{s:02d}")
            if self.pomodoro_seconds == 0:
                self.pomodoro_running = False
                self.pomo_start_btn.configure(text="Başlat")
                threading.Thread(target=lambda: winsound.Beep(800, 1500), daemon=True).start()

        # Dünya Saati Kontrolü
        for item in self.world_widgets:
            t = (datetime.now(timezone.utc) + timedelta(hours=item["offset"])).strftime("%H:%M")
            item["label"].configure(text=t)

        self.after(1000, self.update_clock_loop)

    def update_weather_loop(self):
        def fetch():
            try:
                # Otomatik konum algılama
                current_city = self.settings.get("weather_city", "").strip()
                if not current_city or current_city.lower() == "istanbul":
                    try:
                        geo_resp = requests.get("http://ip-api.com/json/", timeout=5)
                        if geo_resp.status_code == 200:
                            geo_data = geo_resp.json()
                            if geo_data.get("status") == "success":
                                current_city = geo_data.get("city", "İstanbul")
                                self.settings["weather_city"] = current_city
                                SettingsManager.save(self.settings)
                                self.after(0, lambda: self.city_entry.delete(0, "end"))
                                self.after(0, lambda: self.city_entry.insert(0, current_city))
                    except: pass

                if not current_city: current_city = "İstanbul"

                # Hava durumu verisi çekme
                url = f"https://wttr.in/{current_city}?format=%C+%t&lang=tr"
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    weather_data = response.text.replace("+", "").strip()
                    self.weather_text = f"{current_city}: {weather_data}"
                else:
                    self.weather_text = "Hava durumu alınamadı"
                
                self.after(0, lambda: self.weather_label.configure(text=self.weather_text))
            except Exception:
                self.after(0, lambda: self.weather_label.configure(text="Bağlantı Hatası"))
        
        threading.Thread(target=fetch, daemon=True).start()
        self.after(1200000, self.update_weather_loop)

    # --- Olaylar ve Temalandırma ---
    def apply_initial_state(self):
        self.change_theme_event(self.current_theme)
        t_val = self.settings.get("transparency", 1.0)
        self.trans_slider.set(t_val)
        self.attributes("-alpha", t_val)
        if self.settings.get("always_on_top", False): self.ontop_sw.select()
        self.attributes("-topmost", self.settings.get("always_on_top", False))
        ctk.set_appearance_mode(self.settings.get("appearance", "Dark"))

    def change_theme_event(self, choice):
        self.current_theme = choice
        self.settings["theme"] = choice
        theme = self.themes[choice]
        c, h = theme["main"], theme["hover"]
        
        # UI Senkronizasyonu
        self.time_label.configure(text_color=c)
        self.tabview.configure(segmented_button_selected_color=c)
        
        # Butonlar
        self.alarm_btn.configure(fg_color=c, hover_color=h)
        self.pomo_start_btn.configure(fg_color=c, hover_color=h)
        self.city_btn.configure(fg_color=c, hover_color=h)
        
        # Diğer Elementler
        self.theme_menu.configure(fg_color=c, button_color=c, button_hover_color=h)
        self.trans_slider.configure(button_color=c, progress_color=c)
        self.ontop_sw.configure(progress_color=c)
        self.mode_sw.configure(progress_color=c)
        
        # Kart Çerçeveleri
        self.alarm_card.configure(border_color=c)
        self.pomo_card.configure(border_color=c)
        
        for item in self.world_widgets:
            item["frame"].configure(border_color=c)
            
        SettingsManager.save(self.settings)

    def change_trans_event(self, val):
        self.settings["transparency"] = val
        self.attributes("-alpha", val)
        SettingsManager.save(self.settings)

    def change_ontop_event(self):
        s = self.ontop_sw.get()
        self.settings["always_on_top"] = s
        self.attributes("-topmost", s)
        SettingsManager.save(self.settings)

    def change_mode_event(self):
        m = "Dark" if self.mode_sw.get() else "Light"
        self.settings["appearance"] = m
        ctk.set_appearance_mode(m)
        SettingsManager.save(self.settings)

    def change_city_event(self):
        new_city = self.city_entry.get().strip()
        if new_city:
            self.settings["weather_city"] = new_city
            SettingsManager.save(self.settings)
            self.update_weather_loop()

    def auto_locate_event(self):
        self.settings["weather_city"] = ""
        SettingsManager.save(self.settings)
        self.update_weather_loop()

    # --- Araç Eylemleri ---
    def toggle_alarm(self):
        if not self.is_alarm_on:
            try:
                t = self.alarm_entry.get().strip()
                datetime.strptime(t, "%H:%M")
                self.alarm_time = t
                self.is_alarm_on = True
                self.alarm_info.configure(text=f"Aktif: {t}", text_color=self.themes[self.current_theme]["main"])
                self.alarm_btn.configure(text="İptal")
            except Exception:
                self.alarm_info.configure(text="HH:MM formatı!", text_color="#FF5252")
        else:
            self.is_alarm_on = False
            self.alarm_info.configure(text="Pasif", text_color="#666666")
            self.alarm_btn.configure(text="Kur")

    def fire_alarm(self):
        for _ in range(3):
            winsound.Beep(1000, 500)
        self.after(0, lambda: self.alarm_info.configure(text="Uyanma Vakti!", text_color="#FF5252"))

    def start_pomo(self):
        if not self.pomodoro_running:
            self.pomodoro_running = True
            self.pomo_start_btn.configure(text="Duraklat")
        else:
            self.pomodoro_running = False
            self.pomo_start_btn.configure(text="Devam")

    def reset_pomo(self):
        self.pomodoro_running = False
        self.pomodoro_seconds = 25 * 60
        self.pomo_display.configure(text="25:00")
        self.pomo_start_btn.configure(text="Başlat")

    # --- Sistem Tepsisi (Tray) İşlemleri ---
    def withdraw_to_tray(self):
        self.withdraw()
        if self.tray_icon:
            self.tray_icon.visible = True
            return

        size = 64
        image = Image.new('RGBA', (size, size), (0,0,0,0))
        draw = ImageDraw.Draw(image)
        # Daha profesyonel bir tray simgesi (Daire içinde nokta)
        main_color = self.themes[self.current_theme]["main"]
        draw.ellipse((8, 8, size-8, size-8), outline=main_color, width=4)
        draw.ellipse((24, 24, size-24, size-24), fill=main_color)
        
        menu = (item('Geri Yükle', self.restore_app), item('Çıkış', self.quit_app_final))
        self.tray_icon = pystray.Icon("Aura", image, "Aura Premium Saat", menu)
        threading.Thread(target=self.tray_icon.run, daemon=True).start()

    def restore_app(self, icon, item):
        self.tray_icon.stop()
        self.tray_icon = None
        self.deiconify()

    def on_close_event(self):
        # Pencere kapandığında direkt tepsiye küçült
        self.withdraw_to_tray()

    def quit_app_final(self, icon, item):
        if self.tray_icon:
            self.tray_icon.stop()
        self.destroy()
        sys.exit()

if __name__ == "__main__":
    try:
        app = ModernClockApp()
        app.mainloop()
    except Exception as e:
        print(f"Kritik Başlatma Hatası: {e}")
