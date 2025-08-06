import os
import re
import shutil
import threading
from tkinter import W, Button, Label, Entry, Text, filedialog, ttk
import yt_dlp

from svc.models.audio import Audio
from svc.models.video import Video
from svc.models.video_info import DownloadedVideoInfo
from svc.util import yt_fetch_video_info, get_proxy, supported_formats

# State
download_tab_ref = None
video_url = ""
video_formats = []
audio_formats = []
is_video_selected = False
is_audio_selected = False
downloaded_video_path = None

# UI Element Registry
def_ui = lambda: {
    "url_entry": None,
    "get_info_button": None,
    "fetched_video_info_text": None,
    "resolutions_combobox": None,
    "resolution_label": None,
    "audio_combobox": None,
    "audio_label": None,
    "download_button": None,
    "download_status_text": None,
    "open_folder_button": None
}
ui = def_ui()


def setup_download_tab(tab):
    global download_tab_ref, ui
    download_tab_ref = tab
    ui.update(def_ui())

    Label(tab, text="Enter YouTube URL:").grid(row=0, column=0, sticky=W, padx=10, pady=5)
    ui["url_entry"] = Entry(tab, width=100)
    ui["url_entry"].grid(row=0, column=1, padx=10, pady=5)

    ui["get_info_button"] = Button(tab, text="Get Info", command=generate_resolutions)
    ui["get_info_button"].grid(row=1, column=0, sticky=W, padx=10, pady=5)

    ui["fetched_video_info_text"] = Label(tab, text="", anchor="w", justify="left")
    ui["fetched_video_info_text"].grid_forget()

    ui["resolutions_combobox"] = ttk.Combobox(tab, values=["---"], width=50)
    ui["resolutions_combobox"].bind("<<ComboboxSelected>>", on_resolution_selected)
    ui["resolutions_combobox"].grid(row=3, column=1, sticky=W, padx=10, pady=5)
    ui["resolutions_combobox"].grid_remove()

    ui["resolution_label"] = Label(tab, text="", anchor="w", width=50)
    ui["resolution_label"].grid(row=4, column=0, columnspan=2, sticky=W, padx=10, pady=5)

    ui["audio_combobox"] = ttk.Combobox(tab, values=["---"], width=50)
    ui["audio_combobox"].bind("<<ComboboxSelected>>", on_audio_selected)
    ui["audio_combobox"].grid(row=5, column=1, sticky=W, padx=10, pady=5)
    ui["audio_combobox"].grid_remove()

    ui["audio_label"] = Label(tab, text="", anchor="w", width=50)
    ui["audio_label"].grid(row=6, column=0, columnspan=2, sticky=W, padx=10, pady=5)

    ui["download_button"] = Button(tab, text="Download", command=download_video)
    ui["download_button"].grid(row=7, column=0, columnspan=2, sticky=W, padx=10, pady=5)
    ui["download_button"].grid_remove()

    ui["download_status_text"] = Label(tab, text="", anchor="w", width=50)
    ui["download_status_text"].grid(row=8, column=0, columnspan=2, sticky=W, padx=10, pady=5)
    ui["download_status_text"].grid_remove()

    ui["open_folder_button"] = Button(tab, text="Open Containing Folder", command=open_folder)
    ui["open_folder_button"].grid(row=9, column=0, columnspan=2, sticky=W, padx=10, pady=5)
    ui["open_folder_button"].grid_remove()


def generate_resolutions():
    global video_url, video_formats, is_video_selected

    reset_download_ui()

    if not ui["url_entry"].get():
        return

    video_url = ui["url_entry"].get()
    video_info = yt_fetch_video_info(video_url)

    video_formats.clear()
    video_formats.append("---")

    for fmt in video_info.get("formats", []):
        if fmt.get("vcodec") == "none":
            continue

        resolution = f"{fmt.get('width', '?')}x{fmt.get('height', '?')}"
        fps = f"{int(fmt.get('fps', 0))}" if fmt.get("fps") else "n/a"

        video_formats.append(Video(fmt.get("format_id"), resolution, fps, fmt.get("protocol"), fmt.get("ext")))

    ui["resolutions_combobox"].config(values=["---"] + [
        f"({vf.id}) {vf.resolution} {vf.fps} {vf.extension} via {vf.protocol}" for vf in video_formats[1:]
    ])
    ui["resolutions_combobox"].set("---")
    ui["resolutions_combobox"].grid()
    ui["resolution_label"].config(text="No resolution selected!")

    generate_audio(video_info)

    title = video_info.get("title", "Unknown title")
    duration = video_info.get("duration_string") or video_info.get("duration") or "Unknown duration"
    ui["fetched_video_info_text"].config(text=f"Title: {title}\nDuration: {duration}", foreground="black")
    ui["fetched_video_info_text"].grid(row=2, column=0, columnspan=2, sticky=W, padx=10, pady=5)


def generate_audio(video_info):
    global audio_formats
    audio_formats.clear()
    audio_formats.append("---")

    for fmt in video_info.get("formats", []):
        if fmt.get("resolution") == "audio only":
            try:
                audio_formats.append(Audio(fmt["format_id"], fmt["ext"], fmt["protocol"], fmt.get("asr"), fmt.get("filesize")))
            except KeyError:
                continue

    ui["audio_combobox"].config(values=["---"] + [
        f"({af.id}) {af.extension} via {af.protocol} at {af.asr or 'n/a'}Hz ~{to_mb(af.filesize)}"
        for af in audio_formats[1:]
    ])
    ui["audio_combobox"].set("---")
    ui["audio_combobox"].grid()
    ui["audio_label"].config(text="No audio selected!")


def on_resolution_selected(event):
    global is_video_selected
    selected = ui["resolutions_combobox"].get()
    is_video_selected = selected != "---"
    ui["resolution_label"].config(text=f"Selected resolution: {selected}" if is_video_selected else "No resolution selected")
    check_video_audio_selection()


def on_audio_selected(event):
    global is_audio_selected
    selected = ui["audio_combobox"].get()
    is_audio_selected = selected != "---"
    ui["audio_label"].config(text=f"Selected audio: {selected}" if is_audio_selected else "No audio selected")
    check_video_audio_selection()


def check_video_audio_selection():
    if is_video_selected and is_audio_selected:
        ui["download_button"].grid()
    else:
        ui["download_button"].grid_remove()

def download_video():
    thread = threading.Thread(target=_download_video_thread)
    thread.start()

def _download_video_thread():
    video_format, audio_format = get_format_from_format_string()
    try:
        ui["download_status_text"].grid()
        ui["download_status_text"].config(text="Downloading...", foreground="orange")
        ui["open_folder_button"].grid_forget()
        yt_info = yt_fetch_video_info(video_url)
        title = re.sub(r'[^A-Za-z0-9]', '', yt_info.get("title", "video"))
        ydl_opts = {
            "format": f"{video_format.id}+{audio_format.id}",
            "outtmpl": f"{title}.%(ext)s",
            "restrictfilenames": True
        }

        proxy = get_proxy()
        if proxy:
            ydl_opts["proxy"] = proxy

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])

        move_video_to_folder(title)
        ui["download_status_text"].config(text="Downloaded successfully", foreground="green")
        ui["open_folder_button"].grid()
    except Exception as e:
        ui["download_status_text"].config(text=f"Download error: {e}", foreground="red", wraplength=200)

def move_video_to_folder(title):
    global downloaded_video_path

    downloaded_file = next((f"{title}.{ext}" for ext in supported_formats if os.path.exists(f"{title}.{ext}")), None)
    if not downloaded_file:
        ui["download_status_text"].config(text="Downloaded file not found", foreground="red")
        return

    info = DownloadedVideoInfo.get_video_info(downloaded_file)
    if not info:
        ui["download_status_text"].config(text="Could not extract video info", foreground="red", wraplength=100)
        return

    res = DownloadedVideoInfo.get_pretty_resolution(info.resolution[0], info.fps, include_fps=False)
    target_folder = os.path.join("raw", res, str(info.fps))
    os.makedirs(target_folder, exist_ok=True)
    shutil.move(downloaded_file, os.path.join(target_folder, os.path.basename(downloaded_file)))
    downloaded_video_path = target_folder


def get_format_from_format_string():
    selected_video = ui["resolutions_combobox"].get()
    selected_audio = ui["audio_combobox"].get()

    video = next((vf for vf in video_formats if vf != "---" and
                  f"({vf.id}) {vf.resolution} {vf.fps} {vf.extension} via {vf.protocol}" == selected_video), None)
    audio = next((af for af in audio_formats if af != "---" and
                  f"({af.id}) {af.extension} via {af.protocol} at {af.asr or 'n/a'}Hz ~{to_mb(af.filesize)}" == selected_audio), None)

    return video, audio


def to_mb(bytes_val):
    return f"{bytes_val / 1_000_000:.2f} MB" if bytes_val else "n/a"


def open_folder():
    os.startfile(downloaded_video_path)


def reset_download_ui():
    global is_video_selected, is_audio_selected
    video_formats.clear()
    audio_formats.clear()
    is_video_selected = False
    is_audio_selected = False
    ui["download_button"].grid_remove()
    ui["download_status_text"].grid_remove()
    ui["open_folder_button"].grid_remove()
