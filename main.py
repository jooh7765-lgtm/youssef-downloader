import flet as ft
import yt_dlp
import os
import threading

def main(page: ft.Page):
    # إعدادات الصفحة لتناسب شاشة الموبايل والتنسيق العربي والإنكليزي الموحد
    page.title = "Video Downloader Pro"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.scroll = ft.ScrollMode.AUTO
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 20

    # عناصر الواجهة العصرية للموبايل
    title_text = ft.Text("مُحمل اليوتيوب الاحترافي", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_900)
    
    url_input = ft.TextField(
        label="أدخل رابط الفيديو أو قائمة التشغيل أدناه",
        hint_text="https://...",
        rtl=True,
        width=350,
        border_color=ft.Colors.BLUE_400
    )

    type_radio = ft.RadioGroup(
        content=ft.Row([
            ft.Radio(value="MP4", label="فيديو (MP4)"),
            ft.Radio(value="MP3", label="صوت فقط (MP3)"),
        ], alignment=ft.MainAxisAlignment.CENTER),
        value="MP4"
    )

    quality_radio = ft.RadioGroup(
        content=ft.ResponsiveRow([
            ft.Radio(value="360p", label="360p", col={"xs": 4, "sm": 3}),
            ft.Radio(value="480p", label="480p", col={"xs": 4, "sm": 3}),
            ft.Radio(value="720p", label="720p", col={"xs": 4, "sm": 3}),
            ft.Radio(value="1080p", label="1080p", col={"xs": 4, "sm": 3}),
            ft.Radio(value="2K", label="2K", col={"xs": 4, "sm": 3}),
            ft.Radio(value="4K", label="4K", col={"xs": 4, "sm": 3}),
            ft.Radio(value="MAX", label="أقصى جودة", col={"xs": 6, "sm": 3}),
        ], alignment=ft.MainAxisAlignment.CENTER),
        value="720p"
    )

    # كارت تفاعلي لعرض شريط التقدم على شاشة الهاتف
    info_label = ft.Text("التطبيق مستعد وجاهز للعمل...", size=13, color=ft.Colors.BLUE_GREY_600)
    progress_bar = ft.ProgressBar(value=0, width=330, color=ft.Colors.GREEN_500, bgcolor=ft.Colors.BLUE_GREY_100)
    progress_label = ft.Text("0%", size=14, weight=ft.FontWeight.BOLD)
    
    progress_card = ft.Container(
        content=ft.Column([
            info_label,
            progress_bar,
            progress_label
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        padding=15,
        border=ft.Border.all(1, ft.Colors.BLUE_GREY_200),
        border_radius=10,
        width=350,
        bgcolor=ft.Colors.BLUE_GREY_50
    )

    def start_download(e):
        url = url_input.value.strip()
        if not url:
            page.open(ft.SnackBar(ft.Text("برجاء إدخال رابط صحيح!", rtl=True)))
            return

        file_type = type_radio.value
        quality_choice = quality_radio.value

        # مسار مجلد التحميلات (Downloads) الافتراضي والحتمي داخل هواتف الأندرويد
        save_path = "/sdcard/Download"
        
        if 'list=' in url:
            out_template = os.path.join(save_path, '%(playlist_title)s/%(playlist_index)s - %(title)s.%(ext)s')
        else:
            out_template = os.path.join(save_path, '%(title)s.%(ext)s')

        # دالة تحديث شريط التقدم والنسبة على شاشة الموبايل
        def progress_hook(d):
            if d['status'] == 'downloading':
                total = d.get('total_bytes') or d.get('total_bytes_estimate') or 0
                downloaded = d.get('downloaded_bytes', 0)
                filename = d.get('filename', '').split('/')[-1]
                if len(filename) > 30: filename = filename[:30] + "..."
                
                if total > 0:
                    percent = downloaded / total
                    progress_bar.value = percent
                    progress_label.value = f"{percent*100:.1f}%"
                    info_label.value = f"جاري تحميل: {filename}"
                    page.update()
            elif d['status'] == 'finished':
                info_label.value = "جاري المعالجة النهائية للملف..."
                page.update()

        ydl_opts = {
            'ignoreerrors': True,
            'outtmpl': out_template,
            'progress_hooks': [progress_hook],
            # الأندرويد سيتولى الدمج تلقائياً عبر نظام التشغيل
        }

        if file_type == 'MP4':
            if quality_choice == 'MAX': format_setting = 'bestvideo+bestaudio/best'
            elif quality_choice == '4K': format_setting = 'bestvideo[height<=2160]+bestaudio/best[height<=2160]/best'
            elif quality_choice == '2K': format_setting = 'bestvideo[height<=1440]+bestaudio/best[height<=1440]/best'
            elif quality_choice == '1080p': format_setting = 'bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080][ext=mp4]/best'
            elif quality_choice == '720p': format_setting = 'bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720][ext=mp4]/best'
            elif quality_choice == '480p': format_setting = 'bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a]/best[height<=480][ext=mp4]/best'
            else: format_setting = 'bestvideo[height<=360][ext=mp4]+bestaudio[ext=m4a]/best[height<=360][ext=mp4]/best'
            
            ydl_opts['format'] = format_setting
            ydl_opts['merge_output_format'] = 'mp4'
        else:
            ydl_opts['format'] = 'bestaudio/best'
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]

        def run_dl():
            download_btn.disabled = True
            progress_bar.value = None # حركة دائرية انتظارية أثناء الاتصال
            info_label.value = "جاري الاتصال بالسيرفر وجلب البيانات..."
            page.update()

            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
                progress_bar.value = 1
                progress_label.value = "100%"
                info_label.value = "اكتمل التحميل بنجاح!"
                page.open(ft.SnackBar(ft.Text("تم التحميل! ستجد الملف في مجلد Downloads بهاتفك.", rtl=True)))
            except Exception as ex:
                info_label.value = "فشل التحميل."
                page.open(ft.SnackBar(ft.Text(f"حدث خطأ: {str(ex)}", rtl=True)))
            finally:
                download_btn.disabled = False
                page.update()

        threading.Thread(target=run_dl, daemon=True).start()

    download_btn = ft.ElevatedButton(
        text="ابدأ التحميل الآن",
        color=ft.Colors.WHITE,
        bgcolor=ft.Colors.GREEN_600,
        width=220,
        height=48,
        on_click=start_download
    )

    page.add(
        ft.Container(height=10),
        title_text,
        ft.Container(height=15),
        url_input,
        ft.Container(height=10),
        ft.Text("اختر الصيغة المطلوبة:", weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_900),
        type_radio,
        ft.Container(height=10),
        ft.Text("اختر الجودة (للفيديو فقط):", weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_900),
        quality_radio,
        ft.Container(height=15),
        download_btn,
        ft.Container(height=15),
        progress_card,
        ft.Container(expand=True),
        ft.Text("Developer: Youssef Ahmed Hassan", font_family="Courier", size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_GREY_400)
    )

ft.app(target=main)
