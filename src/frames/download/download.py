from tkinter import Button, Label

from src.frames.download.download_ui import DOWNLOAD_FRAME_UI
from src.frames.download.util.download_util import inc_download_frame_row_index
from src.util import add_widget_to_grid, create_button, create_entry, create_label


def set_download_frame_components(frame):
    # Enter YouTube URL Label
    DOWNLOAD_FRAME_UI["enter_yt_url_text"] = create_label(frame, "Enter YouTube URL: ")
    add_widget_to_grid(DOWNLOAD_FRAME_UI["enter_yt_url_text"])

    # YouTube URL Entry (input box)
    DOWNLOAD_FRAME_UI["url_entry"] = create_entry(frame)
    add_widget_to_grid(DOWNLOAD_FRAME_UI["url_entry"], column=1)

    inc_download_frame_row_index()

    # Get Info button
    DOWNLOAD_FRAME_UI["get_info_button"] = create_button(frame, text="Get Info", command=generate_video_resolutions_components)
    add_widget_to_grid(DOWNLOAD_FRAME_UI["get_info_button"], row=DOWNLOAD_FRAME_UI["download_frame_row_index"])

    inc_download_frame_row_index()

def generate_video_resolutions_components():
    if not DOWNLOAD_FRAME_UI["url_entry"].get():
        print("HEE")