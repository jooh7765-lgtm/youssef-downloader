import os
import threading
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.progressbar import ProgressBar
from kivy.uix.togglebutton import ToggleButton
from kivy.core.window import Window
from kivy.utils import get_color_from_hex
import yt_dlp

class YoussefDownloaderPro(App):
    def build(self):
        self.title = "Video Downloader Pro"
        
        # تصميم الواجهة بالوضع الداكن العصري
        layout = BoxLayout(orientation='vertical', padding=24, spacing=16)
        
        with layout.canvas.before:
            from kivy.graphics import Color, Rectangle
            Color(0.07, 0.09, 0.13, 1)
            self.rect = Rectangle(size=layout.size, pos=layout.pos)
            layout.bind(size=self._update_rect, pos=self._update_rect)

        # عنوان التطبيق
        title_text = Label(
            text="VIDEO DOWNLOADER PRO", 
            font_size='26sp', 
            bold=True, 
            color=get_color_from_hex("#64B5F6"),
            halign='center',
            size_hint_y=None,
            height=40
        )
        layout.add_widget(title_text)

        # مربع الرابط
        self.url_input = TextInput(
            hint_text="Paste your video or playlist link here...",
            size_hint_y=None,
            height=55,
            multiline=False,
            background_color=get_color_from_hex("#1E293B"),
            foreground_color=get_color_from_hex("#F8FAFC"),
            hint_text_color=get_color_from_hex("#64748B"),
            font_size='16sp',
            cursor_color=get_color_from_hex("#38BDF8")
        )
        self.url_input.bind(minimum_height=self.url_input.setter('height'))
        layout.add_widget(self.url_input)

        # اختيار الصيغة
        layout.add_widget(Label(text="Select Format", font_size='14sp', bold=True, color=get_color_from_hex("#94A3B8"), size_hint_y=None, height=15))
        format_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=48, spacing=12)
        self.btn_mp4 = ToggleButton(text="Video (MP4)", state='down', group='format', background_color=get_color_from_hex("#0284C7"))
        self.btn_mp3 = ToggleButton(text="Audio (MP3)", group='format', background_color=get_color_from_hex("#0284C7"))
        format_layout.add_widget(self.btn_mp4)
        format_layout.add_widget(self.btn_mp3)
        layout.add_widget(format_layout)

        # اختيار الجودة
        layout.add_widget(Label(text="Select Quality", font_size='14sp', bold=True, color=get_color_from_hex("#94A3B8"), size_hint_y=None, height=15))
        
        quality_layout = GridLayout(cols=4, spacing=8, size_hint_y=None, height=85)
        qualities = ["360p", "480p", "720p", "1080p", "2K", "4K", "MAX"]
        self.q_buttons = {}
        
        for q in qualities:
            state = 'down' if q == '720p' else 'normal'
            btn = ToggleButton(text=q, state=state, group='quality', background_color=get_color_from_hex("#334155"))
            self.q_buttons[q] = btn
            quality_layout.add_widget(btn)
            
        layout.add_widget(quality_layout)

        # زر التحميل
        self.download_btn = Button(
            text="START DOWNLOAD",
            size_hint_y=None,
            height=58,
            background_color=get_color_from_hex("#10B981"),
            color=get_color_from_hex("#FFFFFF"),
            bold=True,
            font_size='16sp'
        )
        self.download_btn.bind(on_press=self.start_download_thread)
        layout.add_widget(self.download_btn)

        # مراقب التقدم والسرعة
        self.info_label = Label(text="Ready (Auto-Update Bypass Enabled)...", font_size='14sp', color=get_color_from_hex("#38BDF8"))
        self.progress_bar = ProgressBar(max=100, value=0, size_hint_y=None, height=12)
        self.progress_label = Label(text="0%", font_size='15sp', bold=True, color=get_color_from_hex("#38BDF8"))

        layout.add_widget(self.info_label)
        layout.add_widget(self.progress_bar)
        layout.add_widget(self.progress_label)

        # اسمك منور بالذهبي تحت كمطور رسمي
        dev_label = Label(
            text="DEVELOPED BY: YOUSSEF AHMED HASSAN", 
            font_size='14sp', 
            bold=True, 
            color=get_color_from_hex("#F59E0B"), 
            size_hint_y=None,
            height=30
        )
        layout.add_widget(dev_label)

        return layout

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def start_download_thread(self, instance):
        threading.Thread(target=self.run_download, daemon=True).start()

    def run_download(self):
        url = self.url_input.text.strip()
        if not url:
            self.info_label.text = "Please paste a valid URL link!"
            return

        self.download_btn.disabled = True
        self.progress_bar.value = 0
        self.progress_label.text = "0%"
        self.info_label.text = "Bypassing protection & fetching details..."

        quality_choice = '720p'
        for q, btn in self.q_buttons.items():
            if btn.state == 'down':
                quality_choice = q

        save_path = "/sdcard/Download"
        if not os.path.exists(save_path):
            save_path = os.path.join(os.path.expanduser("~"), "Downloads")
            
        os.makedirs(save_path, exist_ok=True)

        if 'list=' in url or 'playlist' in url.lower():
            out_template = os.path.join(save_path, '%(playlist_title)s/%(playlist_index)s - %(title)s.%(ext)s')
        else:
            out_template = os.path.join(save_path, '%(title)s.%(ext)s')

        def progress_hook(d):
            if d['status'] == 'downloading':
                total = d.get('total_bytes') or d.get('total_bytes_estimate') or 0
                downloaded = d.get('downloaded_bytes', 0)
                filename = d.get('filename', '').split('/')[-1]
                if len(filename) > 25: filename = filename[:25] + "..."
                if total > 0:
                    percent = (downloaded / total) * 100
                    self.progress_bar.value = percent
                    self.progress_label.text = f"{percent:.1f}%"
                    self.info_label.text = f"Downloading: {filename}"

        # إعدادات السرعة الصاروخية وتخطي الحماية
        ydl_opts = {
            'outtmpl': out_template,
            'progress_hooks': [progress_hook],
            'ignoreerrors': True,
            'concurrent_fragment_downloads': 16, # تحميل فائق السرعة بـ 16 مسار
            'nocheckcertificate': True,            # تخطي فحص الأمان لتسريع وقت البدء
            'extractor_args': {'youtube': {'player_client': ['android', 'web']}}, # خداع سيرفر يوتيوب وتحديث فوري للحماية
        }

        if self.btn_mp4.state == 'down':
            if quality_choice == 'MAX': format_setting = 'bestvideo+bestaudio/best'
            elif quality_choice == '4K': format_setting = 'bestvideo[height<=2160]+bestaudio/best'
            elif quality_choice == '2K': format_setting = 'bestvideo[height<=1440]+bestaudio/best'
            elif quality_choice == '1080p': format_setting = 'bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best'
            elif quality_choice == '720p': format_setting = 'bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best'
            elif quality_choice == '480p': format_setting = 'bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a]/best'
            else: format_setting = 'bestvideo[height<=360][ext=mp4]+bestaudio[ext=m4a]/best'
            
            ydl_opts['format'] = format_setting
            ydl_opts['merge_output_format'] = 'mp4'
        else:
            ydl_opts['format'] = 'bestaudio/best'

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            self.info_label.text = "Success! Saved in Downloads."
            try:
                import sys
                sys.stdout.write('\a')
                sys.stdout.flush()
            except:
                pass
        except Exception as e:
            self.info_label.text = "Download failed! Check link."
        finally:
            self.download_btn.disabled = False

if _name_ == '_main_':
    YoussefDownloaderPro().run()
