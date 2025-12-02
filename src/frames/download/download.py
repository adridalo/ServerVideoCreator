import re
import threading
from tkinter import Button, Label

import yt_dlp

from src.frames.download.download_ui import DOWNLOAD_FRAME_UI
from src.frames.download.util.download_util import get_audio_formats_from_video_info, get_title_and_duration_from_video, get_video_formats_from_video_info, inc_download_frame_row_index, yt_dlp_fetch_video_info
from src.types.enums.color import LabelColor
from src.types.models.raw_audio_format_info import RawAudioFormatInfo
from src.types.models.raw_video_format_info import RawVideoFormatInfo
from src.util import add_widget_to_grid, create_button, create_combobox, create_entry, create_label, edit_label_text, get_proxy, remove_widget_from_grid, update_combobox_values

download_frame_ref = None
selected_resolution = None
selected_audio = None
video_info = None

def set_download_frame_components(frame):
    global download_frame_ref

    download_frame_ref = frame

    # Enter YouTube URL Label
    DOWNLOAD_FRAME_UI["enter_yt_url_text"] = create_label(frame, "Enter YouTube URL: ")
    add_widget_to_grid(DOWNLOAD_FRAME_UI["enter_yt_url_text"])

    # YouTube URL Entry (input box)
    DOWNLOAD_FRAME_UI["url_entry"] = create_entry(frame)
    add_widget_to_grid(DOWNLOAD_FRAME_UI["url_entry"], column=1)

    inc_download_frame_row_index()

    # Get Info button
    DOWNLOAD_FRAME_UI["get_info_button"] = create_button(
        frame,
        text="Get Info", 
        command=generate_video_resolutions_components
    )
    add_widget_to_grid(
        DOWNLOAD_FRAME_UI["get_info_button"], 
        row=DOWNLOAD_FRAME_UI["download_frame_row_index"]
    )

    inc_download_frame_row_index()

def generate_video_resolutions_components():
    global video_info

    reset_ui()

    if not DOWNLOAD_FRAME_UI["url_entry"].get():
        return
    
    video_url = DOWNLOAD_FRAME_UI["url_entry"].get()
    video_info = yt_dlp_fetch_video_info(video_url)
    video_formats = get_video_formats_from_video_info(video_info)

    (video_title, video_duration) = get_title_and_duration_from_video(video_info)

    # Fetched video information text
    DOWNLOAD_FRAME_UI["fetched_video_info_text"] = create_label(download_frame_ref, text=f"Title: {video_title}\nDuration: {video_duration}")
    DOWNLOAD_FRAME_UI["fetched_video_info_text"].config(justify="left")
    add_widget_to_grid(
        DOWNLOAD_FRAME_UI["fetched_video_info_text"],
        row=DOWNLOAD_FRAME_UI["download_frame_row_index"],
        column=0,
        columnspan=2
    )

    inc_download_frame_row_index()

    # Resolutions combobox
    DOWNLOAD_FRAME_UI["resolutions_combobox"] = create_combobox(download_frame_ref, command=on_video_resolution_selected)
    DOWNLOAD_FRAME_UI["resolutions_combobox"].config(
        
    )
    update_combobox_values(
        DOWNLOAD_FRAME_UI["resolutions_combobox"], 
        [str(vf) for vf in video_formats]
    )
    DOWNLOAD_FRAME_UI["resolutions_combobox"].set("---")
    add_widget_to_grid(
        DOWNLOAD_FRAME_UI["resolutions_combobox"], 
        row=DOWNLOAD_FRAME_UI["download_frame_row_index"], 
        column=1
    )

    inc_download_frame_row_index()

    # Selected resolution information
    DOWNLOAD_FRAME_UI["resolution_label"] = create_label(download_frame_ref, text="No resolution selected")
    add_widget_to_grid(
        DOWNLOAD_FRAME_UI["resolution_label"],
        row=DOWNLOAD_FRAME_UI["download_frame_row_index"],
        column=0,
        columnspan=2
    )

    inc_download_frame_row_index()

def on_video_resolution_selected(e):
    global selected_resolution

    current_selected_resolution = DOWNLOAD_FRAME_UI["resolutions_combobox"].get()
    if current_selected_resolution == "---":
        return
    
    edit_label_text(DOWNLOAD_FRAME_UI["resolution_label"], f"Selected resolution: {current_selected_resolution}")

    selected_resolution = current_selected_resolution

    generate_audio_components()

def generate_audio_components():
    audio_formats = get_audio_formats_from_video_info(video_info)

    if DOWNLOAD_FRAME_UI["audio_combobox"] is None:
        DOWNLOAD_FRAME_UI["audio_combobox"] = create_combobox(download_frame_ref, command=on_audio_resolution_selected)
        update_combobox_values(
            DOWNLOAD_FRAME_UI["audio_combobox"], 
            [str(af) for af in audio_formats]
        )
        DOWNLOAD_FRAME_UI["audio_combobox"].set("---")
        add_widget_to_grid(
            DOWNLOAD_FRAME_UI["audio_combobox"], 
            row=DOWNLOAD_FRAME_UI["download_frame_row_index"], 
            column=1
        )

        inc_download_frame_row_index()

        # Selected resolution information
        DOWNLOAD_FRAME_UI["audio_label"] = create_label(download_frame_ref, text="No audio selected")
        add_widget_to_grid(
            DOWNLOAD_FRAME_UI["audio_label"],
            row=DOWNLOAD_FRAME_UI["download_frame_row_index"],
            column=0,
            columnspan=2
        )

        inc_download_frame_row_index()

def on_audio_resolution_selected(e):
    global selected_audio

    current_selected_audio = DOWNLOAD_FRAME_UI["audio_combobox"].get()
    if current_selected_audio == "---":
        return
    
    edit_label_text(DOWNLOAD_FRAME_UI["audio_label"], f"Selected audio: {current_selected_audio}")

    selected_audio = current_selected_audio

    if DOWNLOAD_FRAME_UI["download_button"] is None:
        DOWNLOAD_FRAME_UI["download_button"] = create_button(download_frame_ref, text="Download", command=on_download_button_click)
        add_widget_to_grid(DOWNLOAD_FRAME_UI["download_button"], DOWNLOAD_FRAME_UI["download_frame_row_index"])

        inc_download_frame_row_index()

def on_download_button_click():
    thread = threading.Thread(target=_download_video_thread)
    thread.start()

def _download_video_thread():
    resolution_format = RawVideoFormatInfo.get_format_from_string(selected_resolution)
    audio_format = RawAudioFormatInfo.get_format_from_string(selected_audio)
    video_url = DOWNLOAD_FRAME_UI["url_entry"].get()

    DOWNLOAD_FRAME_UI["download_status_text"] = create_label(download_frame_ref, text="Downloading...", foreground=LabelColor.ORANGE)
    add_widget_to_grid(
        DOWNLOAD_FRAME_UI["download_status_text"],
        row=DOWNLOAD_FRAME_UI["download_frame_row_index"],
    )

    inc_download_frame_row_index()

    cleaned_title = re.sub(r'[^A-Za-z0-9]', '', video_info.get("title", "video"))
    yt_dlp_options = {
        "format": f"{resolution_format.id}+{audio_format.id}",
        "outtmpl": f"{cleaned_title}.%(ext)s",
        "restrictfilenames": True
    }

    # Get proxy information
    proxy = get_proxy()
    # If a proxy value is retrieved
    if proxy:
        # Add it to YDL options
        yt_dlp_options["proxy"] = proxy

    with yt_dlp.YoutubeDL(yt_dlp_options) as ydl:
        ydl.download(video_url)

    edit_label_text(DOWNLOAD_FRAME_UI["download_status_text"], "Download successful!", foreground=LabelColor.GREEN)

def reset_ui():
    global selected_resolution, selected_audio, video_info

    selected_resolution = None
    selected_audio = None
    video_info = None

    for i in ["fetched_video_info_text", "resolutions_combobox", "resolution_label", "audio_combobox", "audio_label"]:
        remove_widget_from_grid(DOWNLOAD_FRAME_UI[i])