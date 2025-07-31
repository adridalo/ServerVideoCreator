import os
import re
import shutil
from tkinter import *
from tkinter import ttk
import yt_dlp

from svc.models.audio import Audio
from svc.models.video import Video
from svc.models.video_info import DownloadedVideoInfo
from svc.util import yt_fetch_video_info, get_proxy

# Globals
video_url = ""
video_formats = []
audio_formats = []
is_video_selected = False
is_audio_selected = False

# Tkinter widgets
url_entry = None
resolutions_combobox = None
resolution_label = None
audio_combobox = None
audio_label = None
download_button = None
finished_downloading_text = None
open_folder_button = None
download_tab_ref = None
fetched_video_info_text = None

def setup_download_tab(tab):
    global url_entry, resolutions_combobox, resolution_label
    global audio_combobox, audio_label, download_button
    global finished_downloading_text, open_folder_button
    global download_tab_ref, fetched_video_info_text

    download_tab_ref = tab

    Label(tab, text="Enter YouTube URL:").grid(row=0, column=0, sticky=W, padx=10, pady=5)
    url_entry = Entry(tab, width=100)
    url_entry.grid(row=0, column=1, padx=10, pady=5)

    Button(tab, text="Get Info", command=generate_resolutions).grid(row=1, column=0, sticky=W, padx=10, pady=5)

    fetched_video_info_text = Label(tab, text="")
    fetched_video_info_text.grid_forget()

    resolutions_combobox = ttk.Combobox(tab, values=["---"], width=50)
    resolutions_combobox.grid(row=3, column=1, sticky=W, padx=10, pady=5)
    resolutions_combobox.grid_remove()
    resolutions_combobox.bind("<<ComboboxSelected>>", on_resolution_selected)

    resolution_label = Label(tab, text="", anchor=W, width=50)
    resolution_label.grid(row=4, column=0, columnspan=2, sticky=W, padx=10, pady=5)

    audio_combobox = ttk.Combobox(tab, values=["---"], width=50)
    audio_combobox.grid(row=5, column=1, sticky=W, padx=10, pady=5)
    audio_combobox.grid_remove()
    audio_combobox.bind("<<ComboboxSelected>>", on_audio_selected)

    audio_label = Label(tab, text="", anchor=W, width=50)
    audio_label.grid(row=6, column=0, columnspan=2, sticky=W, padx=10, pady=5)

    download_button = Button(tab, text="Download", command=download_video)
    download_button.grid(row=7, column=0, columnspan=2, sticky=W, padx=10, pady=5)
    download_button.grid_remove()

    finished_downloading_text = Label(tab, text="", anchor=W, width=50)
    finished_downloading_text.grid(row=8, column=0, columnspan=2, sticky=W, padx=10, pady=5)
    finished_downloading_text.grid_remove()

    open_folder_button = Button(tab, text="Open Containing Folder", command=open_folder)
    open_folder_button.grid(row=9, column=0, columnspan=2, sticky=W, padx=10, pady=5)
    open_folder_button.grid_remove()

def generate_resolutions():
    global video_url, video_formats, is_video_selected

    reset_download_ui()

    if not url_entry.get():
        return

    video_url = url_entry.get()
    video_info = yt_fetch_video_info(video_url)

    video_formats.clear()
    video_formats.append("---")

    for fmt in video_info.get("formats", []):
        if fmt.get("vcodec") == "none":
            continue

        resolution = f"{fmt.get('width', '?')}x{fmt.get('height', '?')}"
        fps = f"{int(fmt.get('fps', 0))}" if fmt.get("fps") else "n/a"

        video_formats.append(Video(
            fmt.get("format_id"),
            resolution,
            fps,
            fmt.get("protocol"),
            fmt.get("ext")
        ))

    pretty_video_formats = ["---"] + [
        f"({vf.id}) {vf.resolution} {vf.fps} {vf.extension} via {vf.protocol}"
        for vf in video_formats[1:]
    ]

    resolutions_combobox.config(values=pretty_video_formats)
    resolutions_combobox.current(0)
    resolutions_combobox.set("---")
    resolutions_combobox.grid()
    resolution_label.config(text="No resolution selected!")

    generate_audio(video_info)

def generate_audio(video_info):
    global audio_formats

    audio_formats.clear()
    audio_formats.append("---")

    for fmt in video_info.get("formats", []):
        if fmt.get("resolution") == "audio only":
            try:
                audio = Audio(
                    fmt["format_id"],
                    fmt["ext"],
                    fmt["protocol"],
                    fmt.get("asr"),
                    fmt.get("filesize")
                )
                audio_formats.append(audio)
            except KeyError:
                continue

    pretty_audio_formats = ["---"] + [
        f"({af.id}) {af.extension} via {af.protocol} at {af.asr or 'n/a'}Hz ~{to_mb(af.filesize)}"
        for af in audio_formats[1:]
    ]

    audio_combobox.config(values=pretty_audio_formats)
    audio_combobox.current(0)
    audio_combobox.set("---")
    audio_combobox.grid()
    audio_label.config(text="No audio selected!")

    title = video_info.get("title", "Unknown title")
    duration = video_info.get("duration_string") or video_info.get("duration") or "Unknown duration"
    fetched_video_info_text.config(text=f"Title: {title}\nDuration: {duration}", justify="left", anchor="w", foreground="black")
    fetched_video_info_text.grid(row=2, column=0, columnspan=2, sticky=W, padx=10, pady=5)

def on_resolution_selected(event):
    global is_video_selected
    selected = resolutions_combobox.get()
    is_video_selected = selected != "---"
    resolution_label.config(text=f"Selected resolution: {selected}" if is_video_selected else "No resolution selected")
    check_video_audio_selection()

def on_audio_selected(event):
    global is_audio_selected
    selected = audio_combobox.get()
    is_audio_selected = selected != "---"
    audio_label.config(text=f"Selected audio: {selected}" if is_audio_selected else "No audio selected")
    check_video_audio_selection()

def check_video_audio_selection():
    if is_video_selected and is_audio_selected:
        download_button.grid()
    else:
        download_button.grid_remove()

def download_video():
    video_format, audio_format = get_format_from_format_string()

    try:
        yt_info = yt_fetch_video_info(video_url)
        title = re.sub(r'[^A-Za-z0-9]', '', yt_info.get("title", "video"))
        ydl_opts = {
            "format": f"{video_format.id}+{audio_format.id}",
            "outtmpl": f"{title}.%(ext)s",
            "restrictfilenames": True
        }

        if get_proxy() != "":
            ydl_opts["proxy"] = get_proxy()

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])

        move_video_to_folder(title)
        finished_downloading_text.config(text="Downloaded successfully", foreground="green")
    except Exception as e:
        finished_downloading_text.config(text=f"Download error: {e}", foreground="red", wraplength=200)

    finished_downloading_text.grid()
    open_folder_button.grid()

def move_video_to_folder(title):
    downloaded_file = next((f"{title}.{ext}" for ext in ["mp4", "mkv", "webm", "flv", "avi"] if os.path.exists(f"{title}.{ext}")), None)

    if not downloaded_file:
        finished_downloading_text.config(text="Downloaded file not found", foreground="red")
        return

    info = DownloadedVideoInfo.get_video_info(downloaded_file)
    if not info:
        finished_downloading_text.config(text="Could not extract video info", foreground="red", wraplength=100)
        return

    res = DownloadedVideoInfo._get_pretty_resolution(info.resolution[0], info.fps, include_fps=False)
    target_folder = os.path.join("raw", res, str(info.fps))
    os.makedirs(target_folder, exist_ok=True)
    shutil.move(downloaded_file, os.path.join(target_folder, os.path.basename(downloaded_file)))

def get_format_from_format_string():
    selected_video = resolutions_combobox.get()
    selected_audio = audio_combobox.get()

    video = next((vf for vf in video_formats if vf != "---" and f"({vf.id}) {vf.resolution} {vf.fps} {vf.extension} via {vf.protocol}" == selected_video), None)
    audio = next((af for af in audio_formats if af != "---" and f"({af.id}) {af.extension} via {af.protocol} at {af.asr or 'n/a'}Hz ~{to_mb(af.filesize)}" == selected_audio), None)

    return video, audio

def to_mb(bytes_val):
    return f"{bytes_val / 1_000_000:.2f} MB" if bytes_val else "n/a"

def open_folder():
    os.startfile("raw")

def reset_download_ui():
    global is_video_selected, is_audio_selected
    video_formats.clear()
    audio_formats.clear()
    is_video_selected = False
    is_audio_selected = False
    download_button.grid_remove()
    finished_downloading_text.grid_remove()
    open_folder_button.grid_remove()
