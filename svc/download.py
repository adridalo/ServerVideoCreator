import os
import shutil
import time
from tkinter import *
from tkinter import ttk
import yt_dlp
import re

from svc.models.audio import Audio
from svc.models.video import Video
from svc.util import yt_fetch_video_info, get_proxy
from svc.models.video_info import DownloadedVideoInfo

# Globals specific to download tab
video_url = ""
video_formats = ["---"]
audio_formats = ["---"]
is_video_selected = False
is_audio_selected = False
dl_row_index = 0

# These will be set later during UI setup
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
    global download_tab_ref, dl_row_index
    global fetched_video_info_text

    download_tab_ref = tab

    Label(tab, text="Enter YouTube URL:").grid(row=0, column=0, sticky=W, padx=10, pady=5)
    url_entry = Entry(tab, width=100)
    url_entry.grid(row=0, column=1, padx=10, pady=5)

    fetch_button = Button(tab, text="Get Info", command=generate_resolutions)
    fetch_button.grid(row=1, column=0, sticky=W, padx=10, pady=5)

    fetched_video_info_text = Label(tab, text="")
    fetched_video_info_text.grid_forget()

    resolutions_combobox = ttk.Combobox(tab, values=video_formats, width=35)
    resolutions_combobox.grid(row=3, column=1, sticky=W, padx=10, pady=5)
    resolutions_combobox.grid_remove()
    resolutions_combobox.bind("<<ComboboxSelected>>", on_resolution_selected)

    resolution_label = Label(tab, text="", anchor=W, width=50)
    resolution_label.grid(row=4, column=0, columnspan=2, sticky=W, padx=10, pady=5)

    audio_combobox = ttk.Combobox(tab, values=audio_formats, width=35)
    audio_combobox.grid(row=5, column=1, sticky=W, padx=10, pady=5)
    audio_combobox.grid_remove()
    audio_combobox.bind("<<ComboboxSelected>>", on_audio_selected)

    audio_label = Label(tab, text="", anchor=W, width=50)
    audio_label.grid(row=6, column=0, columnspan=2, sticky=W, padx=10, pady=5)

    dl_row_index = 7

    download_button = Button(tab, text="Download", command=download_video)
    download_button.grid(row=dl_row_index, column=0, columnspan=2, sticky=W, padx=10, pady=5)
    download_button.grid_remove()

    finished_downloading_text = Label(tab, text="", anchor=W, width=50)
    finished_downloading_text.grid(row=dl_row_index + 1, column=0, columnspan=2, sticky=W, padx=10, pady=5)
    finished_downloading_text.grid_remove()

    open_folder_button = Button(tab, text="Open Containing Folder", command=open_folder)
    open_folder_button.grid(row=dl_row_index + 2, column=0, columnspan=2, sticky=W, padx=10, pady=5)
    open_folder_button.grid_remove()


def generate_resolutions():
    global video_url, video_formats, audio_formats
    global is_video_selected, is_audio_selected

    video_formats = ["---"]
    audio_formats = ["---"]
    is_video_selected = False
    is_audio_selected = False

    download_button.grid_remove()
    finished_downloading_text.grid_remove()
    open_folder_button.grid_remove()

    if url_entry.get() == "":
        return

    video_url = url_entry.get()
    video_info = yt_fetch_video_info(video_url)

    for fmt in video_info.get("formats", []):
        if fmt.get("vcodec") == "none":
            continue

        height = fmt.get("height")
        width = fmt.get("width")
        fps = fmt.get("fps")
        protocol = fmt.get("protocol")
        ext = fmt.get("ext")
        format_id = fmt.get("format_id")

        if height and width:
            resolution_str = f"{width}x{height}"
        else:
            resolution_str = "unknown"

        fps_str = f"{int(fps)}" if fps else "n/a"

        current_video_obj = Video(format_id, resolution_str, fps_str, protocol, ext)
        video_formats.append(current_video_obj)

    pretty_video_formats = ["---"]
    for i in range(1, len(video_formats)):
        fmt = video_formats[i]
        pretty_video_formats.append(
            f"({fmt.id}){fmt.resolution} {fmt.fps} {fmt.extension} via {fmt.protocol}"
        )

    resolutions_combobox["values"] = pretty_video_formats
    resolutions_combobox.current(0)
    resolutions_combobox.set("---")
    resolutions_combobox.grid()
    resolution_label.config(text="No resolution selected!")

    generate_audio()


def generate_audio():
    global fetched_video_info_text

    video_info = yt_fetch_video_info(video_url)

    for fmt in video_info.get("formats", []):
        current_format = fmt.get("resolution")
        if current_format == "audio only":
            try:
                current_audio_obj = Audio(fmt["format_id"], fmt["ext"], fmt["protocol"], fmt["asr"], fmt["filesize"])
            except KeyError:
                current_audio_obj = Audio(fmt["format_id"], fmt["ext"], fmt["protocol"])
            audio_formats.append(current_audio_obj)

    pretty_audio_formats = ["---"]
    for i in range(1, len(audio_formats)):
        pretty_audio_formats.append(
            f"{audio_formats[i].extension} via {audio_formats[i].protocol} at {audio_formats[i].asr if audio_formats[i].asr else 'n/a'}Hz ~{audio_formats[i].filesize if audio_formats[i].filesize else 'n/a'}B"
        )

    audio_combobox["values"] = pretty_audio_formats
    audio_combobox.current(0)
    audio_combobox.set("---")
    audio_combobox.grid()
    audio_label.config(text="No audio selected!")

    title = video_info.get("title", "Unknown title")
    duration = video_info.get("duration_string", "Unknown duration") or video_info.get("duration", "Unknown duration")

    formatted_info = (
        f"Title: {title}\n"
        f"Duration: {duration}\n"
    )

    fetched_video_info_text.config(text=formatted_info, justify="left", anchor="w", foreground="black")
    fetched_video_info_text.grid(row=2, column=0, columnspan=2, sticky=W, padx=10, pady=5)


def on_resolution_selected(event):
    global is_video_selected

    selected = resolutions_combobox.get()
    if selected == "---":
        resolution_label.config(text="No resolution selected")
        is_video_selected = False
    else:
        resolution_label.config(text=f"Selected resolution: {selected}")
        is_video_selected = True
    check_video_audio_selection()

def on_audio_selected(event):
    global is_audio_selected

    selected = audio_combobox.get()
    if selected == "---":
        audio_label.config(text="No audio selected")
        is_audio_selected = False
    else:
        audio_label.config(text=f"Selected audio: {selected}")
        is_audio_selected = True
    check_video_audio_selection()

def check_video_audio_selection():
    if is_video_selected and is_audio_selected:
        download_button.grid()
    else:
        download_button.grid_remove()

def download_video():
    global dl_row_index
    video_format, audio_format = get_format_from_format_string()

    yt_video_info = yt_fetch_video_info(video_url)
    raw_title = yt_video_info["title"]
    sanitized_title = re.sub(r'[^A-Za-z0-9]', '', raw_title)

    ydl_options = {
        "proxy": get_proxy(),
        "format": f"{video_format.id}+{audio_format.id}",
        "outtmpl": f"{sanitized_title}.%(ext)s",
        "restrictfilenames": True
    }

    try:
        with yt_dlp.YoutubeDL(params=ydl_options) as ydl:
            ydl.download(video_url)
            move_video_to_folder(sanitized_title)
    except Exception as e:
        finished_downloading_text.config(text=f"Something went wrong with the download: {e}", foreground="red")

    finished_downloading_text.grid()
    open_folder_button.grid()

def move_video_to_folder(title):
    downloaded_file = None
    for ext in ['mp4', 'mkv', 'webm', 'flv', 'avi']:
        candidate = f"{title}.{ext}"
        if os.path.exists(candidate):
            downloaded_file = candidate
            break

    if downloaded_file is None:
        finished_downloading_text.config(text="Downloaded file not found", foreground="red")
        finished_downloading_text.grid()
        return
    
    info = DownloadedVideoInfo.get_video_info(downloaded_file)
    if info is None:
        finished_downloading_text.config(text="Could not get info", foreground="red")
        finished_downloading_text.grid()
        return
    
    height = info.resolution[0]
    fps = info.fps

    pretty_res = DownloadedVideoInfo._get_pretty_resolution(height, fps, include_fps=False)

    target_folder = os.path.join("raw", pretty_res, str(fps))
    os.makedirs(target_folder, exist_ok=True)

    target_path = os.path.join(target_folder, os.path.basename(downloaded_file))
    shutil.move(downloaded_file, target_path)

    finished_downloading_text.config(text=f"Downloaded successfully", foreground="green")

def get_format_from_format_string():
    selected_video_text = resolutions_combobox.get()
    selected_audio_text = audio_combobox.get()

    video_obj = None
    audio_obj = None

    for vf in video_formats:
        if vf == "---":
            continue
        pretty_format = f"({vf.id}){vf.resolution} {vf.fps} {vf.extension} via {vf.protocol}"
        if pretty_format == selected_video_text:
            video_obj = vf
            break

    for af in audio_formats:
        if af == "---":
            continue
        pretty_format = f"{af.extension} via {af.protocol} at {af.asr if af.asr else 'n/a'}Hz ~{af.filesize if af.filesize else 'n/a'}B"
        if pretty_format == selected_audio_text:
            audio_obj = af
            break

    return video_obj, audio_obj

def open_folder():
    os.startfile("raw")
