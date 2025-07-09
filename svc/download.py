import os
from tkinter import *
from tkinter import ttk
import yt_dlp

from svc.audio import Audio
from svc.video import Video
from svc.util import fetch_video_info, get_proxy

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

def setup_download_tab(tab):
    global url_entry, resolutions_combobox, resolution_label
    global audio_combobox, audio_label, download_button
    global finished_downloading_text, open_folder_button
    global download_tab_ref, dl_row_index

    download_tab_ref = tab

    # Row 0
    Label(tab, text="Enter YouTube URL:").grid(row=0, column=0, sticky=W, padx=10, pady=5)
    url_entry = Entry(tab, width=100)
    url_entry.grid(row=0, column=1, padx=10, pady=5)

    # Row 1
    fetch_button = Button(tab, text="Get Info", command=generate_resolutions)
    fetch_button.grid(row=1, column=0, sticky=W, padx=10, pady=5)

    # Row 2
    resolutions_combobox = ttk.Combobox(tab, values=video_formats, width=35)
    resolutions_combobox.grid(row=2, column=1, sticky=W, padx=10, pady=5)
    resolutions_combobox.grid_remove()
    resolutions_combobox.bind("<<ComboboxSelected>>", on_resolution_selected)

    # Row 3
    resolution_label = Label(tab, text="", anchor=W, width=50)
    resolution_label.grid(row=3, column=0, columnspan=2, sticky=W, padx=10, pady=5)

    # Row 4
    audio_combobox = ttk.Combobox(tab, values=audio_formats, width=35)
    audio_combobox.grid(row=4, column=1, sticky=W, padx=10, pady=5)
    audio_combobox.grid_remove()
    audio_combobox.bind("<<ComboboxSelected>>", on_audio_selected)

    # Row 5
    audio_label = Label(tab, text="", anchor=W, width=50)
    audio_label.grid(row=5, column=0, columnspan=2, sticky=W, padx=10, pady=5)

    # Now set dl_row_index dynamically to the next empty row after row 5
    dl_row_index = 6

    # Setup download button (hidden initially)
    download_button = Button(tab, text="Download", command=download_video)
    download_button.grid(row=dl_row_index, column=0, columnspan=2, sticky=W, padx=10, pady=5)
    download_button.grid_remove()

    # Setup finished label
    finished_downloading_text = Label(tab, text="", anchor=W, width=50)
    finished_downloading_text.grid(row=dl_row_index + 1, column=0, columnspan=2, sticky=W, padx=10, pady=5)
    finished_downloading_text.grid_remove()

    # Setup open folder button
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
    video_info = fetch_video_info(video_url)

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
    for i in range(1, len(video_formats) - 1):
        fmt = video_formats[i]
        pretty_video_formats.append(
            f"({fmt.id}){fmt.resolution} {fmt.fps} {fmt.extension} via {fmt.protocol}"
        )

    resolutions_combobox["values"] = pretty_video_formats
    resolutions_combobox.current(0)
    resolutions_combobox.grid()
    resolution_label.config(text="No resolution selected!")

    generate_audio()


def generate_audio():
    video_info = fetch_video_info(video_url)

    for fmt in video_info.get("formats", []):
        current_format = fmt.get("resolution")
        if current_format == "audio only":
            try:
                current_audio_obj = Audio(fmt["format_id"], fmt["ext"], fmt["protocol"], fmt["asr"], fmt["filesize"])
            except KeyError:
                current_audio_obj = Audio(fmt["format_id"], fmt["ext"], fmt["protocol"])
            audio_formats.append(current_audio_obj)

    pretty_audio_formats = ["---"]
    for i in range(1, len(audio_formats) - 1):
        pretty_audio_formats.append(
            f"{audio_formats[i].extension} via {audio_formats[i].protocol} at {audio_formats[i].asr if audio_formats[i].asr else 'n/a'}Hz ~{audio_formats[i].filesize if audio_formats[i].filesize else 'n/a'}B"
        )

    audio_combobox["values"] = pretty_audio_formats
    audio_combobox.current(0)
    audio_combobox.grid()
    audio_label.config(text="No audio selected!")


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

    video_info = fetch_video_info(video_url)
    raw_title = video_info["title"]
    sanitized_title = raw_title.replace(" ", "")

    ydl_options = {
        "proxy": get_proxy(),
        "format": f"{video_format.id}+{audio_format.id}",
        "outtmpl": f"{sanitized_title}.%(ext)s",
        "restrictfilenames": True
    }

    with yt_dlp.YoutubeDL(params=ydl_options) as ydl:
        try:
            ydl.download(video_url)
            finished_downloading_text.config(text="Download completed!", foreground="green")
        except Exception:
            finished_downloading_text.config(text="Something went wrong with the download", foreground="red")

    finished_downloading_text.grid()
    open_folder_button.grid()

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
    import os
    os.startfile(".")
