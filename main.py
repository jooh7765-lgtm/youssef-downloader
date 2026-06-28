import os
import threading
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.progressbar import ProgressBar
from kivy.uix.togglebutton import ToggleButton
from kivy.core.window import Window
from kivy.utils import get_color_from_hex
import yt_dlp

# إعداد حجم نافذة وهمي يشبه الموبايل أثناء الاختبار على الكمبيوتر
Window.size = (360, 640)

class YoussefDownloaderApp(App):
    def build(self):
        self.title = "Video Downloader Pro"
        
        # الحاوية الرئيسية للتطبيق
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        # تغيير خلفية التطبيق للون الفاتح
        with layout.canvas.before:
            from kivy.graphics import Color, Rectangle
            Color(0.95, 0.95, 0.97, 1)
            self.rect = Rectangle(size=layout.size, pos=layout.pos)
            layout.bind(size=self._update_rect, pos=self._update_rect)

        # عنوان التطبيق
        title_text = Label(
            text="مُحمل اليوتيوب الاحترافي", 
            font_size='24sp', 
            bold=True, 
            color=get_color_from_hex("#0D47A1"),
            halign='center'
        )
        layout.add_widget(title_text)

        # حقل إدخال الرابط
        self.url_input = TextInput(
            hint_text="أدخل رابط الفيديو أو قائمة التشغيل أدناه",
            size_hint_y=None,
            height=50,
            multiline=False,
            background_color=get_color_from_hex("#FFFFFF"),
            foreground_color=get_color_from_hex("#000000")
        )
        layout.add_widget(self.url_input)

        # أزرار اختيار الصيغة (فيديو أو صوت)
        format_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, spacing=10)
        self.btn_mp4 = ToggleButton(text="فيديو (MP4)", state='down', group='format', color=(1,1,1,1))
        self.btn_mp3 = ToggleButton(text="صوت فقط (MP3)", group='format', color=(1,1,1,1))
        format_layout.add_widget(self.btn_mp4)
        format_layout.add_widget(self.btn_mp3)
        layout.add_widget(format_layout)

        # زر بدء التحميل
        self.download_btn = Button(
            text="ابدأ التحميل الآن",
            size_hint_y=None,
            height=55,
            background_color=get_color_from_hex("#1B5E20"),
            color=(1, 1, 1, 1),
            bold=True
        )
        self.download_btn.bind(on_press=self.start_download_thread)
        layout.add_widget(self.download_btn)

        # كارت عرض التقدم
        self.info_label = Label(text="التطبيق مستعد وجاهز للعمل...", font_size='13sp', color=get_color_from_hex("#546E7A"))
        self.progress_bar = ProgressBar(max=100, value=0, size_hint_y=None, height=20)
        self.progress_label = Label(text="0%", font_size='14sp', bold=True, color=get_color_from_hex("#000000"))

        layout.add_widget(self.info_label)
        layout.add_widget(self.progress_bar)
        layout.add_widget(self.progress_label)

        # توقيع المطور بالأسفل
        dev_label = Label(text="Developer: Youssef Ahmed Hassan", font_size='12sp', color=get_color_from_hex("#78909C"))
        layout.add_widget(dev_label)

        return layout

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def start_download_thread(self, instance):
        # تشغيل التحميل في خلفية مستقلة لعدم تجميد الشاشة
        threading.Thread(target=self.run_download, daemon=True).start()

    def run_download(self):
        url = self.url_input.text.strip()
        if not url:
            self.info_label.text = "برجاء إدخال رابط صحيح!"
            return

        self.download_btn.disabled = True
        self.progress_bar.value = 0
        self.progress_label.text = "0%"
        self.info_label.text = "جاري الاتصال بالسيرفر وجلب البيانات..."

        save_path = "/sdcard/Download" if os.path.exists("/sdcard") else "Downloads"
        os.makedirs(save_path, exist_ok=True)
        out_template = os.path.join(save_path, '%(title)s.%(ext)s')

        def progress_hook(d):
            if d['status'] == 'downloading':
                total = d.get('total_bytes') or d.get('total_bytes_estimate') or 0
                downloaded = d.get('downloaded_bytes', 0)
                if total > 0:
                    percent = (downloaded / total) * 100
                    self.progress_bar.value = percent
                    self.progress_label.text = f"{percent:.1f}%"
                    self.info_label.text = "جاري التحميل الآن..."

        ydl_opts = {
            'outtmpl': out_template,
            'progress_hooks': [progress_hook],
        }

        if self.btn_mp3.state == 'down':
            ydl_opts['format'] = 'bestaudio/best'

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            self.info_label.text = "اكتمل التحميل بنجاح! ستجده في مجلد Downloads."
            self.progress_bar.value = 100
            self.progress_label.text = "100%"
        except Exception as e:
            self.info_label.text = f"حدث خطأ: {str(e)}"
        finally:
            self.download_btn.disabled = False

if _name_ == '_main_':
    YoussefDownloaderApp().run()
