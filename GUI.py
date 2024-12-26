import yt_dlp  # type: ignore
import subprocess
import sys
import tkinter as tk
from tkinter import messagebox

def check_ffmpeg_installed():
    """Kiểm tra xem FFmpeg đã được cài đặt chưa."""
    try:
        # Kiểm tra phiên bản FFmpeg bằng cách gọi lệnh "ffmpeg -version"
        result = subprocess.run(['D:\\Works\\Code\\Test\\ffmpeg\\bin\\ffmpeg.exe', '-version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Kiểm tra nếu FFmpeg trả về thông tin phiên bản
        if result.returncode == 0:
            return True
        else:
            return False
    except FileNotFoundError:
        return False

def download_video(url, download_path="downloads"):
    # Kiểm tra xem FFmpeg có được cài đặt không
    if not check_ffmpeg_installed():
        messagebox.showerror("Lỗi", "FFmpeg không được cài đặt trên máy tính này. Vui lòng cài đặt FFmpeg.")
        return

    # Đường dẫn tới FFmpeg (thay đổi theo vị trí bạn cài đặt FFmpeg)
    ffmpeg_path = r"D:\Works\Code\Test\ffmpeg\bin\ffmpeg.exe"  # Đường dẫn đúng tới FFmpeg

    # Tạo một tùy chọn để tải video
    ydl_opts = {
        'outtmpl': f'{download_path}/%(title)s.%(ext)s',  # Đặt tên tệp tải về
        'format': 'bestvideo+bestaudio/best',  # Tải video và audio tốt nhất
        'postprocessors': [{  # Sử dụng FFmpeg để hợp nhất video và audio
            'key': 'FFmpegVideoConvertor',
            'preferedformat': 'mp4',  # Định dạng xuất ra
        }],
        'ffmpeg_location': ffmpeg_path,  # Chỉ định đường dẫn tới FFmpeg
    }

    # Sử dụng yt-dlp để tải video
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
        messagebox.showinfo("Hoàn thành", f"Video đã được tải về từ: {url}")

# Hàm để xử lý khi nhấn nút tải video
def on_download_button_click():
    video_url = url_entry.get()
    if not video_url:
        messagebox.showwarning("Cảnh báo", "Vui lòng nhập URL của video.")
        return
    download_video(video_url)

# Tạo giao diện người dùng (GUI)
root = tk.Tk()
root.title("Download Video")

# Thiết lập giao diện
tk.Label(root, text="Nhập URL của video:").pack(pady=5)

url_entry = tk.Entry(root, width=50)
url_entry.pack(pady=5)

download_button = tk.Button(root, text="Tải Video", command=on_download_button_click)
download_button.pack(pady=20)

# Chạy GUI
root.mainloop()
