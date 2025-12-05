import os
from tkinter import filedialog
from src.frames.scale.scale_ui import SCALE_UI
from src.frames.scale.util.scale_util import format_resolution, inc_scale_frame_row_index
from src.types.models.downloaded_video_info import DownloadedVideoInfo
from src.util import SCALES, add_widget_to_grid, create_button, create_combobox, create_label, update_combobox_values


scale_frame_ref = None
video_file_path = None

def set_scale_frame_components(frame):
    global scale_frame_ref

    scale_frame_ref = frame

    # Select video button
    SCALE_UI["select_video_button"] = create_button(
        frame,
        text="Select video to scale",
        command=on_video_select_click
    )
    add_widget_to_grid(
        SCALE_UI["select_video_button"],
        row=SCALE_UI["scale_frame_row_index"]
    )

    inc_scale_frame_row_index()

def on_video_select_click():
    global video_file_path

    video_file_path = filedialog.askopenfilename(
        title="Select video",
        filetypes=[("MP4 Videos", "*.mp4")]
    )

    if video_file_path:
        info = DownloadedVideoInfo.get_video_information_from_video_file(video_file_path)
        video_resolution = format_resolution(info.resolution)
        resolution_string = info.get_pretty_resolution(combine=True)

        # Selected video title
        SCALE_UI["selected_video_title"] = create_label(scale_frame_ref, text=f"Selected video: {os.path.basename(video_file_path)}")
        add_widget_to_grid(
            SCALE_UI["selected_video_title"],
            row=SCALE_UI["scale_frame_row_index"]
        )

        inc_scale_frame_row_index()

        # Selected video resolution
        SCALE_UI["selected_video_resolution"] = create_label(scale_frame_ref, text=f"Resolution: {resolution_string}")
        add_widget_to_grid(
            SCALE_UI["selected_video_resolution"],
            row=SCALE_UI["scale_frame_row_index"]
        )

        inc_scale_frame_row_index()

        # Scale to label
        SCALE_UI["scale_to_label"] = create_label(scale_frame_ref, text="Scale to ")
        add_widget_to_grid(
            SCALE_UI["scale_to_label"],
            row=SCALE_UI["scale_frame_row_index"]
        )

        inc_scale_frame_row_index()

        # Scale combobox
        SCALE_UI["scale_to_combobox"] = create_combobox(scale_frame_ref, command=on_scale_selected)
        update_combobox_values(SCALE_UI["scale_to_combobox"], new_values=[f for f in SCALES if f != video_resolution])
        add_widget_to_grid(
            SCALE_UI["scale_to_combobox"],
            row=SCALE_UI["scale_frame_row_index"]
        )

        inc_scale_frame_row_index()

def on_scale_selected(e):
    pass