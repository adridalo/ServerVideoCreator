import os
from tkinter import filedialog

from src.frames.convert.convert_ui import CONVERT_FRAME_UI
from src.frames.convert.util.convert_util import inc_convert_frame_row_index
from src.types.models.downloaded_video_info import DownloadedVideoInfo
from src.util import add_to_text_widget, add_widget_to_grid, create_button, create_label, create_text, remove_widget_from_grid

convert_frame_ref = None
videos_paths = []

def set_convert_frame_components(frame):
    global convert_frame_ref

    convert_frame_ref = frame

    # Select files to convert button
    CONVERT_FRAME_UI["select_file_button"] = create_button(frame, text="Select files to convert", command=on_file_select_button_click)
    add_widget_to_grid(
        CONVERT_FRAME_UI["select_file_button"],
        row=CONVERT_FRAME_UI["convert_frame_row_index"]
    )

    inc_convert_frame_row_index()

def on_file_select_button_click():
    global videos_paths

    selected_video_path = list(filedialog.askopenfilenames(
        title="Select videos",
        initialdir=os.path.join("."),
        filetypes=[("MP4 Videos", "*.mp4"), ("MKV Videos", "*.mkv")]
    ))

    if selected_video_path:
        videos_paths.extend(selected_video_path)

        display_selected_files()

def display_selected_files():
    if CONVERT_FRAME_UI["file_list_label"] is not None and CONVERT_FRAME_UI["file_list_text"] is not None:
        remove_widget_from_grid(CONVERT_FRAME_UI["file_list_label"])
        remove_widget_from_grid(CONVERT_FRAME_UI["file_list_text"])
        remove_widget_from_grid(CONVERT_FRAME_UI["clear_paths_button"])
    # File list label
    CONVERT_FRAME_UI["file_list_label"] = create_label(convert_frame_ref, text="Selected videos for conversion:")
    add_widget_to_grid(
        CONVERT_FRAME_UI["file_list_label"],
        row=CONVERT_FRAME_UI["convert_frame_row_index"]
    )

    inc_convert_frame_row_index()

    # File list
    CONVERT_FRAME_UI["file_list_text"] = create_text(convert_frame_ref)
    add_widget_to_grid(
        CONVERT_FRAME_UI["file_list_text"],
        row=CONVERT_FRAME_UI["convert_frame_row_index"]
    )

    for path in videos_paths:
        info = DownloadedVideoInfo.get_video_information_from_video_file(path)
        res = info.get_pretty_resolution(True)
        add_to_text_widget(CONVERT_FRAME_UI["file_list_text"], f"• {os.path.basename(path)} ({res})\n")

    # Clear all video paths button
    CONVERT_FRAME_UI["clear_paths_button"] = create_button(convert_frame_ref, text="Clear all video paths", command=on_clear_path_button_click)
    add_widget_to_grid(
        CONVERT_FRAME_UI["clear_paths_button"],
        row=CONVERT_FRAME_UI["convert_frame_row_index"],
        column=1,
    )

    inc_convert_frame_row_index()

def on_clear_path_button_click():
    print("deleting")