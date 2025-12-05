import os
import shutil
import threading
from tkinter import filedialog

import ffmpeg
from src.frames.scale.scale_ui import SCALE_UI
from src.frames.scale.util.scale_util import format_resolution, inc_scale_frame_row_index
from src.types.enums.color import LabelColor
from src.types.models.downloaded_video_info import DownloadedVideoInfo
from src.util import REFRESH_RATES, SCALES, add_widget_to_grid, create_button, create_combobox, create_label, edit_label_text, remove_widget_from_grid, set_combobox_value, update_combobox_values


scale_frame_ref = None
video_file_path = None
video_to_scale_info = None
selected_resolution_for_scale = None
selected_frame_rate_for_scale = None

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
    global video_file_path, video_to_scale_info, selected_frame_rate_for_scale, selected_resolution_for_scale

    video_file_path = filedialog.askopenfilename(
        title="Select video",
        filetypes=[("MP4 Videos", "*.mp4")]
    )

    if video_file_path:
        info = DownloadedVideoInfo.get_video_information_from_video_file(video_file_path)
        video_to_scale_info = info
        video_resolution = format_resolution(info.resolution)
        resolution_string = info.get_pretty_resolution(combine=True)
        selected_video_refresh_rate = video_to_scale_info.get_pretty_resolution()[1]

        if not SCALE_UI["selected_video_title"] and not SCALE_UI["selected_video_resolution"] and not SCALE_UI["scale_to_label"] and not SCALE_UI["scale_to_combobox"]:
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
            SCALE_UI["scale_to_combobox"] = create_combobox(scale_frame_ref, command=on_resolution_selected)
            update_combobox_values(SCALE_UI["scale_to_combobox"], new_values=[s for s in SCALES if s != video_resolution])
            add_widget_to_grid(
                SCALE_UI["scale_to_combobox"],
                row=SCALE_UI["scale_frame_row_index"]
            )

            inc_scale_frame_row_index()

        edit_label_text(
            SCALE_UI["selected_video_title"],
            new_text=f"Selected video: {os.path.basename(video_file_path)}"
        )
        edit_label_text(
            SCALE_UI["selected_video_resolution"],
            new_text=f"Resolution: {resolution_string}"
        )
        if SCALE_UI["scale_to_combobox"] and SCALE_UI["refresh_rate_combobox"]:
            set_combobox_value(SCALE_UI["scale_to_combobox"], "")
            set_combobox_value(SCALE_UI["refresh_rate_combobox"], "")
            update_combobox_values(SCALE_UI["scale_to_combobox"], new_values=[s for s in SCALES if s != video_resolution])
            update_combobox_values(SCALE_UI["refresh_rate_combobox"], new_values=[r for r in REFRESH_RATES if r != selected_video_refresh_rate])
            selected_resolution_for_scale = None
            selected_frame_rate_for_scale = None

def on_resolution_selected(e):
    global selected_resolution_for_scale

    selected_resolution_for_scale = SCALE_UI["scale_to_combobox"].get()

    if not SCALE_UI["refresh_rate_label"] and not SCALE_UI["refresh_rate_combobox"]:
        # Refresh rate label
        SCALE_UI["refresh_rate_label"] = create_label(scale_frame_ref, text="with Refresh rate")
        add_widget_to_grid(
            SCALE_UI["refresh_rate_label"],
            row=SCALE_UI["scale_frame_row_index"]
        )

        inc_scale_frame_row_index()

        # Refresh rate combobox
        SCALE_UI["refresh_rate_combobox"] = create_combobox(scale_frame_ref, command=on_refresh_rate_selected)
        update_combobox_values(SCALE_UI["refresh_rate_combobox"], new_values=[r for r in REFRESH_RATES if r != video_to_scale_info.get_pretty_resolution()[1]])
        add_widget_to_grid(
            SCALE_UI["refresh_rate_combobox"],
            row=SCALE_UI["scale_frame_row_index"]
        )

        inc_scale_frame_row_index()
        
def on_refresh_rate_selected(e):
    global selected_frame_rate_for_scale

    selected_frame_rate_for_scale = SCALE_UI["refresh_rate_combobox"].get()
    if not SCALE_UI["scale_button"]:
        # Scale button
        SCALE_UI["scale_button"] = create_button(scale_frame_ref, text="Scale video", command=on_scale_button_click)
        add_widget_to_grid(
            SCALE_UI["scale_button"],
            row=SCALE_UI["scale_frame_row_index"]
        )

        inc_scale_frame_row_index()

def on_scale_button_click():
    if selected_frame_rate_for_scale and selected_resolution_for_scale:
        SCALE_UI["scaling_status"] = create_label(scale_frame_ref, text="Scaling...", foreground=LabelColor.ORANGE)
        add_widget_to_grid(
            SCALE_UI["scaling_status"],
            row=SCALE_UI["scale_frame_row_index"]
        )

        inc_scale_frame_row_index()
        
        try:
            thread = threading.Thread(target=_video_scaling_thread)
            thread.start()
        except Exception as e:
            edit_label_text(
                SCALE_UI["scaling_status"],
                new_text=f"Error occurred during scaling: {e}",
                foreground=LabelColor.RED
            )

def _video_scaling_thread():
    video_file_name = os.path.basename(video_file_path)

    ffmpeg.input(
        video_file_path
    ).output(
        video_file_name,
        vf = f"scale={selected_resolution_for_scale}:flags=lanczos",
        r=selected_frame_rate_for_scale
    ).run()
    move_video_to_folder(video_file_name)

    edit_label_text(
        SCALE_UI["scaling_status"],
        new_text="Scaling completed successfully!",
        foreground=LabelColor.GREEN
    )

def move_video_to_folder(video):
    scaled_video_file = next((f for f in os.listdir(os.path.join(".")) if f == video))

    if not scaled_video_file:
        edit_label_text(
            SCALE_UI["scaling_status"],
            new_text="File not found",
            foreground=LabelColor.RED
        )

    resolution_string = video_to_scale_info.get_pretty_resolution()
    target_folder = os.path.join("scaled", resolution_string[0], str(resolution_string[1]))
    os.makedirs(target_folder, exist_ok=True)
    shutil.move(scaled_video_file, os.path.join(target_folder, os.path.basename(scaled_video_file)))