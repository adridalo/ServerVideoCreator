import os
import re
import shutil
import threading
from tkinter import Toplevel

import yt_dlp

from src.frames.download.download_ui import DOWNLOAD_UI
from src.frames.download.util.download_util import get_audio_formats_from_video_info, get_title_and_duration_from_video, get_video_formats_from_video_info, inc_download_frame_row_index, yt_dlp_fetch_video_info
from src.util import BASE_APP_DIR
from src.types.enums.color import LabelColor
from src.types.models.downloaded_video_info import DownloadedVideoInfo
from src.types.models.raw_audio_format_info import RawAudioFormatInfo
from src.types.models.raw_video_format_info import RawVideoFormatInfo
from src.util import add_widget_to_grid, create_button, create_combobox, create_entry, create_label, edit_label_text, get_proxy, open_folder, remove_widget_from_grid, resource_path, update_combobox_values

download_frame_ref = None
selected_resolution = None
selected_audio = None
video_info = None
downloaded_video_path = None

def set_download_frame_components(frame):
    global download_frame_ref

    download_frame_ref = frame

    # Enter YouTube URL Label
    DOWNLOAD_UI["enter_yt_url_text"] = create_label(frame, "Enter YouTube URL: ")
    add_widget_to_grid(DOWNLOAD_UI["enter_yt_url_text"])

    # YouTube URL Entry (input box)
    DOWNLOAD_UI["url_entry"] = create_entry(frame)
    add_widget_to_grid(DOWNLOAD_UI["url_entry"], column=1)

    inc_download_frame_row_index()

    # Get Info button
    DOWNLOAD_UI["get_info_button"] = create_button(
        frame,
        text="Get Info", 
        command=generate_video_resolutions_components
    )
    add_widget_to_grid(
        DOWNLOAD_UI["get_info_button"], 
        row=DOWNLOAD_UI["download_frame_row_index"]
    )

    inc_download_frame_row_index()

def generate_video_resolutions_components():
    global video_info

    reset_ui()

    if not DOWNLOAD_UI["url_entry"].get():
        return
    
    video_url = DOWNLOAD_UI["url_entry"].get()
    video_info = yt_dlp_fetch_video_info(video_url)
    video_formats = get_video_formats_from_video_info(video_info)

    (video_title, video_duration) = get_title_and_duration_from_video(video_info)

    # Fetched video information text
    DOWNLOAD_UI["fetched_video_info_text"] = create_label(download_frame_ref, text=f"Title: {video_title}\nDuration: {video_duration}")
    DOWNLOAD_UI["fetched_video_info_text"].config(justify="left")
    add_widget_to_grid(
        DOWNLOAD_UI["fetched_video_info_text"],
        row=DOWNLOAD_UI["download_frame_row_index"],
        column=0,
        columnspan=2
    )

    inc_download_frame_row_index()

    # Resolutions combobox
    DOWNLOAD_UI["resolutions_combobox"] = create_combobox(download_frame_ref, command=on_video_resolution_selected)
    update_combobox_values(
        DOWNLOAD_UI["resolutions_combobox"], 
        [str(vf) for vf in video_formats]
    )
    DOWNLOAD_UI["resolutions_combobox"].set("---")
    add_widget_to_grid(
        DOWNLOAD_UI["resolutions_combobox"], 
        row=DOWNLOAD_UI["download_frame_row_index"], 
        column=1
    )

    inc_download_frame_row_index()

    # Selected resolution information
    DOWNLOAD_UI["resolution_label"] = create_label(download_frame_ref, text="No resolution selected")
    add_widget_to_grid(
        DOWNLOAD_UI["resolution_label"],
        row=DOWNLOAD_UI["download_frame_row_index"],
        column=0,
        columnspan=2
    )

    inc_download_frame_row_index()

def on_video_resolution_selected(e):
    global selected_resolution

    current_selected_resolution = DOWNLOAD_UI["resolutions_combobox"].get()
    if current_selected_resolution == "---":
        return
    
    edit_label_text(DOWNLOAD_UI["resolution_label"], f"Selected resolution: {current_selected_resolution}")

    selected_resolution = current_selected_resolution

    generate_audio_components()

def generate_audio_components():
    audio_formats = get_audio_formats_from_video_info(video_info)

    if DOWNLOAD_UI["audio_combobox"] is None:
        # Audio combobox
        DOWNLOAD_UI["audio_combobox"] = create_combobox(download_frame_ref, command=on_audio_resolution_selected)
        update_combobox_values(
            DOWNLOAD_UI["audio_combobox"], 
            [str(af) for af in audio_formats]
        )
        DOWNLOAD_UI["audio_combobox"].set("---")
        add_widget_to_grid(
            DOWNLOAD_UI["audio_combobox"], 
            row=DOWNLOAD_UI["download_frame_row_index"], 
            column=1
        )

        inc_download_frame_row_index()

        # Selected audio information
        DOWNLOAD_UI["audio_label"] = create_label(download_frame_ref, text="No audio selected")
        add_widget_to_grid(
            DOWNLOAD_UI["audio_label"],
            row=DOWNLOAD_UI["download_frame_row_index"],
            column=0,
            columnspan=2
        )

        inc_download_frame_row_index()

def on_audio_resolution_selected(e):
    global selected_audio

    current_selected_audio = DOWNLOAD_UI["audio_combobox"].get()
    if current_selected_audio == "---":
        return
    
    edit_label_text(DOWNLOAD_UI["audio_label"], f"Selected audio: {current_selected_audio}")

    selected_audio = current_selected_audio

    if DOWNLOAD_UI["download_button"] is None:
        # Download video button
        DOWNLOAD_UI["download_button"] = create_button(download_frame_ref, text="Download", command=on_download_button_click)
        add_widget_to_grid(DOWNLOAD_UI["download_button"], DOWNLOAD_UI["download_frame_row_index"])

        inc_download_frame_row_index()

def on_download_button_click():
    thread = threading.Thread(target=_download_video_thread)
    thread.start()

def _download_video_thread():
    global downloaded_video_path

    resolution_format = RawVideoFormatInfo.get_format_from_string(selected_resolution)
    audio_format = RawAudioFormatInfo.get_format_from_string(selected_audio)
    video_url = DOWNLOAD_UI["url_entry"].get()

    try:
        # Download status
        if DOWNLOAD_UI["download_status_text"] is None:
            DOWNLOAD_UI["download_status_text"] = create_label(download_frame_ref, text="Downloading...", foreground=LabelColor.ORANGE)
            add_widget_to_grid(
                DOWNLOAD_UI["download_status_text"],
                row=DOWNLOAD_UI["download_frame_row_index"],
            )

            inc_download_frame_row_index()
        
        elif DOWNLOAD_UI["download_status_text"] is not None:
            edit_label_text(
                DOWNLOAD_UI["download_status_text"],
                new_text="Downloading...",
                foreground=LabelColor.ORANGE
            )
            remove_widget_from_grid(DOWNLOAD_UI["open_folder_button"])

        def output_path_hook(d):
            global downloaded_video_path
            if d["status"] == "finished":
                info = d.get("info_dict", {})
                downloaded_video_path = os.path.abspath(
                    info.get("filepath") or info.get("_filename")
                )


        cleaned_title = re.sub(r'[^A-Za-z0-9]', '', video_info.get("title", "video"))
        save_path = os.path.join(BASE_APP_DIR, f"{cleaned_title}.%(ext)s")
        yt_dlp_options = {
            # Uses the IDs selected from your UI dropdowns
            "format": f"{resolution_format.id}+{audio_format.id}",
            "outtmpl": save_path,
            "restrictfilenames": True,
            "progress_hooks": [output_path_hook],

            "javascript_executable": resource_path("qjs.exe"),
            "ffmpeg_location": resource_path("."), 
            "ffprobe_location": resource_path("."),
            "cookiefile": resource_path("cookies.txt"),
            
            # Add this to match your fetch logic
            "remote_components": ["ejs:github"],
    
            "extractor_args": {
                "youtube": {
                    # CHANGE: Match the fetching clients to avoid PO Token errors
                    "player_client": ["ios", "android_vr"],
                    "player_js_version": ["actual"]
                    # REMOVED: "skip": ["dash", "hls"] 
                }
            },
        }

        proxy = get_proxy()
        if proxy:
            yt_dlp_options["proxy"] = proxy

        with yt_dlp.YoutubeDL(yt_dlp_options) as ydl:
            ydl.download([video_url])

        downloaded_video_title = open_title_window(cleaned_title)
        move_video_to_folder(cleaned_title, renamed_title=downloaded_video_title)

        edit_label_text(DOWNLOAD_UI["download_status_text"], "Download successful!", foreground=LabelColor.GREEN)

        # Open folder button
        DOWNLOAD_UI["open_folder_button"] = create_button(download_frame_ref, text="Open video in containing folder", command=on_open_file_in_folder_button_press)
        add_widget_to_grid(
            DOWNLOAD_UI["open_folder_button"],
            row=DOWNLOAD_UI["download_frame_row_index"]
        )

        inc_download_frame_row_index()
    except Exception as e:
        print(e)
        edit_label_text(DOWNLOAD_UI["download_status_text"], f"Download unsuccessful: {e}", foreground=LabelColor.RED)

def open_title_window(original_title):
    title_to_save = original_title

    new_window = Toplevel(download_frame_ref)
    new_window.title("Set new video title")
    new_window.geometry("500x200")

    add_widget_to_grid(create_label(new_window, text="Enter title for downloaded video"))
    new_title_entry = create_entry(new_window, width=60)
    new_title_entry.insert(0, original_title)
    add_widget_to_grid(new_title_entry, column=1)

    def confirm_title():
        nonlocal title_to_save
        new_title = new_title_entry.get().strip()
        if new_title:
            sanitized = re.sub(r'[^A-Za-z0-9]', '', new_title)
            if sanitized:
                title_to_save = sanitized
            else:
                title_to_save = original_title
    
        new_window.destroy()

    add_widget_to_grid(create_button(new_window, text="Confirm", command=confirm_title), row=1)
    new_window.grab_set()
    download_frame_ref.wait_window(new_window)
    return title_to_save

def move_video_to_folder(title, **kwargs):
    global downloaded_video_path 
    
    if not os.path.exists(downloaded_video_path):
        return
    
    downloaded_video_info = DownloadedVideoInfo.get_video_information_from_video_file(downloaded_video_path)
    if not downloaded_video_info:
        edit_label_text(
            DOWNLOAD_UI["download_status_text"],
            new_text="Could not extract video info",
            foreground=LabelColor.RED,
            wraplength=100
        )
        return  
    
    downloaded_video_pretty_resolution = downloaded_video_info.get_pretty_resolution()[0]


    target_folder = os.path.join("raw", downloaded_video_pretty_resolution, str(downloaded_video_info.fps))
    os.makedirs(target_folder, exist_ok=True)

    renamed_video_title = kwargs.get("renamed_title")
    if renamed_video_title and renamed_video_title != title:
        folder = os.path.dirname(downloaded_video_path)
        _, ext = os.path.splitext(downloaded_video_path)

        new_filename = renamed_video_title + ext
        new_full_path = os.path.join(folder, new_filename)

        os.rename(downloaded_video_path, new_full_path)
        downloaded_video_path = new_full_path
        
    destination_file_path = os.path.join(target_folder, os.path.basename(downloaded_video_path))
    shutil.move(downloaded_video_path, destination_file_path)
    downloaded_video_path = os.path.abspath(destination_file_path)

def on_open_file_in_folder_button_press():
    open_folder(os.path.dirname(downloaded_video_path))

def reset_ui():
    global selected_resolution, selected_audio, video_info

    selected_resolution = None
    selected_audio = None
    video_info = None

    components_to_reset = [
        "fetched_video_info_text",
        "resolutions_combobox",
        "resolution_label",
        "audio_combobox",
        "audio_label",
        "download_button",
        "download_status_text",
        "open_folder_button",
    ]

    for key in components_to_reset:
        widget = DOWNLOAD_UI.get(key)
        if widget is not None:
            remove_widget_from_grid(widget)
            DOWNLOAD_UI[key] = None