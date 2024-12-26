import yt_dlp
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import threading
import os
import subprocess
import validators

# Global variable to manage active downloads
active_downloads = {}

# Function to check if the URL is valid
def is_valid_url(url):
    return bool(url) and validators.url(url)

# Function to get available formats for a video
def get_available_formats(url):
    try:
        with yt_dlp.YoutubeDL() as ydl:
            info = ydl.extract_info(url, download=False)
            formats = info.get('formats', [])
            available_formats = []

            desired_qualities = [144, 360, 480, 720, 1080, 2160]  # 2160 for 4K
            for f in formats:
                height = f.get('height')
                if height and height in desired_qualities:
                    format_str = f"{height}p - {f.get('ext', '')}"
                    available_formats.append((f['format_id'], format_str))

            available_formats.sort(key=lambda x: int(x[1].split('p')[0]), reverse=True)
            return available_formats
    except Exception as e:
        messagebox.showerror("Error", f"Failed to fetch formats: {e}")
        return []

# Download video task
def download_video(url, quality):
    if not url:
        messagebox.showerror("Error", "Please enter a valid URL!")
        return

    if url in active_downloads:
        messagebox.showinfo("Info", "This video is already downloading!")
        return

    active_downloads[url] = {"status": "downloading", "thread": threading.Thread(target=download_task, args=(url, quality), daemon=True)}
    active_downloads[url]["thread"].start()

# Download task in separate thread
def download_task(url, quality):
    try:
        ydl_opts = {'format': quality, 'progress_hooks': [progress_hook]}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            video_title = info.get('title', 'video')

            # Open save dialog
            default_path = filedialog.asksaveasfilename(
                defaultextension=".mp4",
                initialfile=video_title,
                filetypes=[("MP4 files", "*.mp4")]
            )
            if default_path:
                ydl_opts['outtmpl'] = default_path
                progress_var.set(0)
                progress_bar.place(relx=0.5, rely=0.7, anchor="center")

                with yt_dlp.YoutubeDL(ydl_opts) as ydl_inner:
                    ydl_inner.download([url])

                progress_var.set(100)
                progress_label.config(text="100%")
                add_download_to_history(default_path, "Completed")
                show_success_dialog(default_path)
            else:
                active_downloads.pop(url)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to download video: {e}")
    finally:
        progress_bar.place_forget()  # Hide the progress bar
        progress_label.place_forget()  # Hide the progress label
        active_downloads.pop(url)

# Function to handle progress updates
def progress_hook(d):
    if d['status'] == 'downloading' and d.get('total_bytes') is not None:
        percent = d['downloaded_bytes'] / d['total_bytes'] * 100
        progress_var.set(percent)
        progress_label.config(text=f"{int(percent)}%")
        root.update_idletasks()
    elif d['status'] == 'finished':
        progress_var.set(100)
        progress_label.config(text="100%")
        messagebox.showinfo("Success", "Download complete!")

# Show success dialog after download completion
def show_success_dialog(file_path):
    def open_file():
        os.startfile(file_path)  # Open the downloaded file

    def open_with():
        # Cross-platform support for opening with VLC
        if os.name == 'nt':  # Windows
            os.startfile(file_path)  # Open with the default app
        elif os.name == 'posix':  # macOS/Linux
            subprocess.run(["open", "-a", "VLC", file_path])  # Open with VLC (change as needed)

    def close_dialog():
        success_dialog.destroy()

    success_dialog = tk.Toplevel(root)
    success_dialog.title("Download Complete")
    success_dialog.geometry("300x180")

    tk.Label(success_dialog, text="Download complete!", font=("Arial", 12, "bold")).pack(pady=10)

    # Buttons
    btn_open = tk.Button(success_dialog, text="Open", command=open_file)
    btn_open.pack(pady=5)

    btn_open_with = tk.Button(success_dialog, text="Open With", command=open_with)
    btn_open_with.pack(pady=5)

    btn_close = tk.Button(success_dialog, text="Close", command=close_dialog)
    btn_close.pack(pady=5)

# Function to add download details to the history list
def add_download_to_history(file_path, status):
    download_tree.insert("", "end", values=(file_path, status, "100%"))

# Dialog to input video URL and quality
def open_add_url_dialog():
    def start_download():
        url = url_entry.get()
        if not is_valid_url(url):
            messagebox.showerror("Error", "Please enter a valid video URL!")
            return

        available_formats = get_available_formats(url)
        if not available_formats:
            messagebox.showerror("Error", "No available formats for the selected video!")
            return

        quality_var.set(available_formats[0][0])  # Default to the first available format
        quality_options = [format[1] for format in available_formats]
        quality_menu['values'] = quality_options  # Update available formats in the combobox
        quality_menu.pack(pady=5)

        threading.Thread(target=download_video, args=(url, quality_var.get()), daemon=True).start()
        url_dialog.destroy()

    url_dialog = tk.Toplevel(root)
    url_dialog.title("Add URL")
    url_dialog.geometry("400x250")

    tk.Label(url_dialog, text="Enter Video URL:", font=("Arial", 12)).pack(pady=10)
    url_entry = tk.Entry(url_dialog, font=("Arial", 12), width=40)
    url_entry.pack(pady=5)

    tk.Label(url_dialog, text="Select Video Quality:", font=("Arial", 12)).pack(pady=10)
    quality_var = tk.StringVar(value="1080p")
    quality_menu = ttk.Combobox(url_dialog, textvariable=quality_var, state="readonly")
    quality_options = ["1080p", "720p", "480p", "360p", "144p"]
    quality_menu['values'] = quality_options
    quality_menu.current(quality_options.index("1080p"))
    quality_menu.pack(pady=5)

    tk.Button(url_dialog, text="Download", command=start_download).pack(pady=10)

# Function to show registration dialog
def open_registration_dialog():
    def handle_registration():
        first_name = first_name_entry.get()
        last_name = last_name_entry.get()
        email = email_entry.get()
        serial_number = serial_number_entry.get()

        if not first_name or not last_name or not email or not serial_number:
            messagebox.showerror("Error", "Please fill all fields.")
            return

        messagebox.showinfo("Registration", "Registration Successful!")
        registration_dialog.destroy()

    registration_dialog = tk.Toplevel(root)
    registration_dialog.title("Registration")
    registration_dialog.geometry("400x300")

    tk.Label(registration_dialog, text="First Name").pack(pady=5)
    first_name_entry = tk.Entry(registration_dialog)
    first_name_entry.pack(pady=5)

    tk.Label(registration_dialog, text="Last Name").pack(pady=5)
    last_name_entry = tk.Entry(registration_dialog)
    last_name_entry.pack(pady=5)

    tk.Label(registration_dialog, text="Email").pack(pady=5)
    email_entry = tk.Entry(registration_dialog)
    email_entry.pack(pady=5)

    tk.Label(registration_dialog, text="Serial Number").pack(pady=5)
    serial_number_entry = tk.Entry(registration_dialog)
    serial_number_entry.pack(pady=5)

    tk.Button(registration_dialog, text="Register", command=handle_registration).pack(pady=10)

# Function to delete all download history
def delete_all():
    for item in download_tree.get_children():
        download_tree.delete(item)  # Clear the history list
    messagebox.showinfo("Delete All", "All history cleared.")

def stop_download():
    messagebox.showinfo("Stop", "Stop functionality is not implemented yet!")

# Function to create buttons with icons
def create_icon_button(frame, image_path, text, command):
    # Load and resize the icon
    icon_image = Image.open(image_path).resize((32, 32))  # Resize icon to 32x32
    icon = ImageTk.PhotoImage(icon_image)
    # Create button with icon and text
    btn = tk.Button(frame, image=icon, text=text, compound="top", command=command)
    btn.image = icon  # Store reference to prevent garbage collection
    btn.pack(side="left", padx=5, pady=5)
    return btn


# Create the main GUI window
root = tk.Tk()
root.title("VideoDownloader Pro")
root.state("zoomed")

# Menu bar
menu_bar = tk.Menu(root)
root.config(menu=menu_bar)

# Add File menu
file_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="File", menu=file_menu)
file_menu.add_command(label="Exit", command=root.quit)

# Add Help menu
help_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="Help", menu=help_menu)
help_menu.add_command(label="About", command=lambda: messagebox.showinfo(
    "About", "VideoDownloader Pro\nVersion: 1.0\nAuthor: Nguyễn Văn Mão\nEmail: nguyenmao.2912@gmail.com\nCopyright 2024"))

# Taskbar below the menu
taskbar_frame = tk.Frame(root, bg="#f0f0f0")
taskbar_frame.pack(fill="x", padx=10, pady=5)

# Frame for buttons with icons below the taskbar
icon_frame = tk.Frame(root)
icon_frame.pack(fill="x", padx=10, pady=10)

# Create buttons with icons
create_icon_button(taskbar_frame, "Images/AddURL.png", "Add URL", open_add_url_dialog)
create_icon_button(taskbar_frame, "Images/Stop.png", "Stop", stop_download)
create_icon_button(taskbar_frame, "Images/Delete.png", "Delete All", delete_all)

# Create registration option button
create_icon_button(taskbar_frame, "Images/Register.png", "Register", open_registration_dialog)

# Download history list
download_frame = tk.Frame(root)
download_frame.pack(fill="both", expand=True, padx=10, pady=5)

# Treeview for download history
download_tree = ttk.Treeview(download_frame, columns=("File", "Status", "Progress"), show="headings")
download_tree.heading("File", text="File Name")
download_tree.heading("Status", text="Status")
download_tree.heading("Progress", text="Progress")
download_tree.column("File", width=400)
download_tree.column("Status", width=100, anchor="center")
download_tree.column("Progress", width=100, anchor="center")
download_tree.pack(fill="both", expand=True)

# Progress bar and label
progress_var = tk.IntVar()
progress_bar = ttk.Progressbar(root, orient="horizontal", length=400, mode="determinate", variable=progress_var)
progress_label = tk.Label(root, text="", font=("Arial", 12, "bold"), fg="#0078D4")

# Place the progress bar at the center of the window
progress_bar.place(relx=0.5, rely=0.7, anchor="center")
progress_label.place(relx=0.5, rely=0.75, anchor="center")

root.mainloop()
