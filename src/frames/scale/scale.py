import os
import shutil
import threading
from tkinter import filedialog

import ffmpeg
from src.frames.scale.scale_ui import SCALE_UI
from src.frames.scale.util.scale_util import format_resolution, inc_scale_frame_row_index
from src.types.enums.color import LabelColor
from src.types.models.downloaded_video_info import DownloadedVideoInfo
from src.util import BASE_APP_DIR, REFRESH_RATES, SCALES, add_widget_to_grid, create_button, create_combobox, create_label, edit_label_text, remove_widget_from_grid, resource_path, set_combobox_value, update_combobox_values


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

    selected = filedialog.askopenfilename(
        title="Select video",
        initialdir=os.path.join("."),
        filetypes=[("MP4 Videos", "*.mp4")]
    )

    if not selected:
        return

    video_file_path = selected
    info = DownloadedVideoInfo.get_video_information_from_video_file(video_file_path)
    video_to_scale_info = info
    
    # format_resolution converts internal resolution (like 1080) to your SCALES constants (like "HD")
    resolution_string = info.get_pretty_resolution(combine=True)

    if not SCALE_UI.get("selected_video_title"):
        # Selected video title
        SCALE_UI["selected_video_title"] = create_label(scale_frame_ref, text="")
        add_widget_to_grid(SCALE_UI["selected_video_title"], row=SCALE_UI["scale_frame_row_index"])
        inc_scale_frame_row_index()

        # Selected video resolution
        SCALE_UI["selected_video_resolution"] = create_label(scale_frame_ref, text="")
        add_widget_to_grid(SCALE_UI["selected_video_resolution"], row=SCALE_UI["scale_frame_row_index"])
        inc_scale_frame_row_index()

        # Scale to label
        SCALE_UI["scale_to_label"] = create_label(scale_frame_ref, text="Scale to ")
        add_widget_to_grid(SCALE_UI["scale_to_label"], row=SCALE_UI["scale_frame_row_index"])
        inc_scale_frame_row_index()

        # Scale combobox
        SCALE_UI["scale_to_combobox"] = create_combobox(scale_frame_ref, command=on_resolution_selected)
        add_widget_to_grid(SCALE_UI["scale_to_combobox"], row=SCALE_UI["scale_frame_row_index"])
        inc_scale_frame_row_index()
    
    # Update label text with new video info
    edit_label_text(
        SCALE_UI["selected_video_title"], 
        new_text=f"Selected video: {os.path.basename(video_file_path)}"
    )
    edit_label_text(
        SCALE_UI["selected_video_resolution"], 
        new_text=f"Resolution: {resolution_string}"
    )

    # Reset selections and update resolution list
    # We allow the user to select any resolution from SCALES
    update_combobox_values(SCALE_UI["scale_to_combobox"], new_values=[s for s in SCALES])
    set_combobox_value(SCALE_UI["scale_to_combobox"], "")

    # Clear the refresh rate combobox if it exists from a previous video
    if SCALE_UI.get("refresh_rate_combobox"):
        set_combobox_value(SCALE_UI["refresh_rate_combobox"], "")
        
    # Clear the status label if it exists (so it doesn't say "Success" from the last video)
    if SCALE_UI.get("scaling_status"):
        edit_label_text(SCALE_UI["scaling_status"], "")

    # Reset global selection state
    selected_resolution_for_scale = None
    selected_frame_rate_for_scale = None

def on_resolution_selected(e):
    global selected_resolution_for_scale

    selected_resolution_for_scale = SCALE_UI["scale_to_combobox"].get()

    input_res = format_resolution(video_to_scale_info.resolution)
    input_fps = str(video_to_scale_info.fps)

    if selected_resolution_for_scale == input_res:
        new_refresh_rates_values = [r for r in REFRESH_RATES if str(r) != input_fps]
    else:
        new_refresh_rates_values = [r for r in REFRESH_RATES]

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
        update_combobox_values(SCALE_UI["refresh_rate_combobox"], new_values=new_refresh_rates_values)
        add_widget_to_grid(
            SCALE_UI["refresh_rate_combobox"],
            row=SCALE_UI["scale_frame_row_index"]
        )

        inc_scale_frame_row_index()
    else:
        update_combobox_values(SCALE_UI["refresh_rate_combobox"], new_values=new_refresh_rates_values)

        if SCALE_UI["refresh_rate_combobox"].get() == input_fps and selected_resolution_for_scale == input_res:
            set_combobox_value(SCALE_UI["refresh_rate_combobox"], "")
        
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
        if not SCALE_UI.get("scaling_status"):
            SCALE_UI["scaling_status"] = create_label(scale_frame_ref, text="Scaling...", foreground=LabelColor.ORANGE)
            add_widget_to_grid(
                SCALE_UI["scaling_status"],
                row=SCALE_UI["scale_frame_row_index"]
            )

            inc_scale_frame_row_index()
        else:
            edit_label_text(SCALE_UI["scaling_status"], "Scaling...", LabelColor.ORANGE)
        
        try:
            thread = threading.Thread(target=_video_scaling_thread)
            thread.start()
        except Exception as e:
            edit_label_text(
                SCALE_UI["scaling_status"],
                new_text=f"Error occurred during scaling: {e}",
                text_color=LabelColor.RED
            )

def _video_scaling_thread():
    # Append resolution and fps to filename to avoid overwriting source
    base_name = os.path.splitext(os.path.basename(video_file_path))[0]
    scaled_name = f"{base_name}_{selected_resolution_for_scale}_{selected_frame_rate_for_scale}.mp4"
    
    ffmpeg_executable = resource_path("ffmpeg.exe")

    ffmpeg.input(video_file_path).output(
        scaled_name,
        vf=f"scale={selected_resolution_for_scale}:flags=lanczos",
        r=selected_frame_rate_for_scale
    ).run(cmd=ffmpeg_executable, overwrite_output=True) # Added overwrite flag
    
    move_video_to_folder(scaled_name)
    edit_label_text(
        SCALE_UI["scaling_status"],
        new_text="Video scaling successful",
        text_color=LabelColor.GREEN
    )

def move_video_to_folder(video):
    # scaled_video_file = next((f for f in os.listdir(os.path.join(".")) if f == video))
    scaled_video_file = os.path.join(BASE_APP_DIR, video)

    if not scaled_video_file:
        edit_label_text(
            SCALE_UI["scaling_status"],
            new_text="File not found",
            text_color=LabelColor.RED
        )

    resolution_string = DownloadedVideoInfo.get_video_information_from_video_file(scaled_video_file).get_pretty_resolution()
    target_folder = os.path.join("scaled", resolution_string[0], str(resolution_string[1]))
    os.makedirs(target_folder, exist_ok=True)
    shutil.move(scaled_video_file, os.path.join(target_folder, os.path.basename(scaled_video_file)))