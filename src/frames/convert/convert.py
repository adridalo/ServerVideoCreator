import os
from pathlib import Path
import threading
from tkinter import IntVar, filedialog

import ffmpeg

from src.frames.convert.convert_ui import CONVERT_FRAME_UI
from src.frames.convert.util.convert_util import inc_convert_frame_row_index
from src.types.enums.color import LabelColor
from src.types.models.downloaded_video_info import DownloadedVideoInfo
from src.util import SUPPORTED_AUDIO_CODEC, SUPPORTED_COLOR_SPACE, SUPPORTED_COMPRESSION, add_to_text_widget, add_widget_to_grid, change_text_widget_state, create_button, create_checkbutton, create_combobox, create_label, create_scale, create_text, edit_label_text, remove_widget_from_grid, update_combobox_values

convert_frame_ref = None
videos_paths = []
b_frames_variable = None
include_text_overlay_variable = None

def set_convert_frame_components(frame):
    global convert_frame_ref, b_frames_variable, include_text_overlay_variable

    convert_frame_ref = frame
    CONVERT_FRAME_UI["convert_frame_row_index"] = 0

    b_frames_variable = IntVar(frame, 0)
    include_text_overlay_variable = IntVar(frame, 1)

    # Select file button
    CONVERT_FRAME_UI["select_file_button"] = create_button(
        frame,
        text="Select files to convert",
        command=on_file_select_button_click
    )
    add_widget_to_grid(CONVERT_FRAME_UI["select_file_button"],
                       row=CONVERT_FRAME_UI["convert_frame_row_index"])
    
    inc_convert_frame_row_index()


def on_file_select_button_click():
    global videos_paths

    selected = filedialog.askopenfilenames(
        title="Select videos",
        filetypes=[("Videos", "*.mp4 *.mkv")]
    )

    if not selected:
        return

    videos_paths = list(selected)

    display_selected_files()
    display_conversion_options()


def display_selected_files():
    # First creation
    if CONVERT_FRAME_UI["file_list_label"] is None:
        CONVERT_FRAME_UI["file_list_label"] = create_label(convert_frame_ref,
                                                           text="Selected videos:")
        add_widget_to_grid(CONVERT_FRAME_UI["file_list_label"],
                           row=CONVERT_FRAME_UI["convert_frame_row_index"])
        inc_convert_frame_row_index()

    if CONVERT_FRAME_UI["file_list_text"] is None:
        CONVERT_FRAME_UI["file_list_text"] = create_text(convert_frame_ref, height=6)
        add_widget_to_grid(CONVERT_FRAME_UI["file_list_text"],
                           row=CONVERT_FRAME_UI["convert_frame_row_index"])
        inc_convert_frame_row_index()

    # Always refresh text
    change_text_widget_state(CONVERT_FRAME_UI["file_list_text"], "normal")
    CONVERT_FRAME_UI["file_list_text"].delete("1.0", "end")

    for p in videos_paths:
        info = DownloadedVideoInfo.get_video_information_from_video_file(p)
        res = info.get_pretty_resolution(True)
        CONVERT_FRAME_UI["file_list_text"].insert("end", f"• {os.path.basename(p)} ({res})\n")

    change_text_widget_state(CONVERT_FRAME_UI["file_list_text"], "disabled")

    # Clear button (created once)
    if CONVERT_FRAME_UI["clear_paths_button"] is None:
        CONVERT_FRAME_UI["clear_paths_button"] = create_button(
            convert_frame_ref,
            text="Clear paths",
            command=on_clear_path_button_click
        )
        add_widget_to_grid(CONVERT_FRAME_UI["clear_paths_button"],
                           row=CONVERT_FRAME_UI["convert_frame_row_index"],
                           column=1)
        
        inc_convert_frame_row_index()

def display_conversion_options():
    if CONVERT_FRAME_UI["compression_combobox"] is not None:
        return  # options already created

    # COMPRESSION
    CONVERT_FRAME_UI["compression_combobox_label"] = create_label(convert_frame_ref,
        text="Select compression:")
    add_widget_to_grid(CONVERT_FRAME_UI["compression_combobox_label"],
                       row=CONVERT_FRAME_UI["convert_frame_row_index"])
    inc_convert_frame_row_index()

    CONVERT_FRAME_UI["compression_combobox"] = create_combobox(
        convert_frame_ref,
        command=update_conversion_options_values
    )
    update_combobox_values(CONVERT_FRAME_UI["compression_combobox"], SUPPORTED_COMPRESSION)
    add_widget_to_grid(CONVERT_FRAME_UI["compression_combobox"],
                       row=CONVERT_FRAME_UI["convert_frame_row_index"])
    inc_convert_frame_row_index()

    # COLOR SPACE
    CONVERT_FRAME_UI["color_space_combobox_label"] = create_label(convert_frame_ref,
        text="Select color space:")
    add_widget_to_grid(CONVERT_FRAME_UI["color_space_combobox_label"],
                       row=CONVERT_FRAME_UI["convert_frame_row_index"])
    inc_convert_frame_row_index()

    CONVERT_FRAME_UI["color_space_combobox"] = create_combobox(
        convert_frame_ref,
        command=update_conversion_options_values
    )
    update_combobox_values(CONVERT_FRAME_UI["color_space_combobox"], SUPPORTED_COLOR_SPACE)
    add_widget_to_grid(CONVERT_FRAME_UI["color_space_combobox"],
                       row=CONVERT_FRAME_UI["convert_frame_row_index"])
    inc_convert_frame_row_index()

    # BIT RATE
    CONVERT_FRAME_UI["bit_rate_scale_label"] = create_label(convert_frame_ref,
        text="Select bit rate (Mbps):")
    add_widget_to_grid(CONVERT_FRAME_UI["bit_rate_scale_label"],
                       row=CONVERT_FRAME_UI["convert_frame_row_index"])
    inc_convert_frame_row_index()

    CONVERT_FRAME_UI["bit_rate_scale"] = create_scale(convert_frame_ref)
    add_widget_to_grid(CONVERT_FRAME_UI["bit_rate_scale"],
                       row=CONVERT_FRAME_UI["convert_frame_row_index"])
    inc_convert_frame_row_index()

    # AUDIO
    CONVERT_FRAME_UI["audio_codec_label"] = create_label(convert_frame_ref,
        text="Select audio codec:")
    add_widget_to_grid(CONVERT_FRAME_UI["audio_codec_label"],
                       row=CONVERT_FRAME_UI["convert_frame_row_index"])
    inc_convert_frame_row_index()

    CONVERT_FRAME_UI["audio_codec_combobox"] = create_combobox(
        convert_frame_ref,
        command=update_conversion_options_values
    )
    update_combobox_values(CONVERT_FRAME_UI["audio_codec_combobox"], SUPPORTED_AUDIO_CODEC)
    add_widget_to_grid(CONVERT_FRAME_UI["audio_codec_combobox"],
                       row=CONVERT_FRAME_UI["convert_frame_row_index"])
    inc_convert_frame_row_index()

    # B-FRAMES
    CONVERT_FRAME_UI["b_frames_combobox_label"] = create_label(convert_frame_ref,
        text="Enable B-Frames:")
    add_widget_to_grid(CONVERT_FRAME_UI["b_frames_combobox_label"],
                       row=CONVERT_FRAME_UI["convert_frame_row_index"])
    inc_convert_frame_row_index()

    CONVERT_FRAME_UI["b_frames_combobox"] = create_checkbutton(
        convert_frame_ref,
        variable=b_frames_variable
    )
    add_widget_to_grid(CONVERT_FRAME_UI["b_frames_combobox"],
                       row=CONVERT_FRAME_UI["convert_frame_row_index"])
    inc_convert_frame_row_index()

    # TEXT OVERLAY
    CONVERT_FRAME_UI["include_text_overlay_label"] = create_label(convert_frame_ref,
        text="Include overlay text:")
    add_widget_to_grid(CONVERT_FRAME_UI["include_text_overlay_label"],
                       row=CONVERT_FRAME_UI["convert_frame_row_index"])
    inc_convert_frame_row_index()

    CONVERT_FRAME_UI["include_text_overlay_combobox"] = create_checkbutton(
        convert_frame_ref,
        variable=include_text_overlay_variable
    )
    add_widget_to_grid(CONVERT_FRAME_UI["include_text_overlay_combobox"],
                       row=CONVERT_FRAME_UI["convert_frame_row_index"])
    inc_convert_frame_row_index()

def update_conversion_options_values(event=None):
    if (not CONVERT_FRAME_UI["compression_combobox"].get()
        or not CONVERT_FRAME_UI["color_space_combobox"].get()
        or not CONVERT_FRAME_UI["audio_codec_combobox"].get()):
        return

    if CONVERT_FRAME_UI["convert_button"] is None:
        CONVERT_FRAME_UI["convert_button"] = create_button(
            convert_frame_ref,
            text="Convert videos",
            command=on_convert_button_click
        )
        add_widget_to_grid(CONVERT_FRAME_UI["convert_button"],
                           row=CONVERT_FRAME_UI["convert_frame_row_index"])
        inc_convert_frame_row_index()


def on_convert_button_click():
    CONVERT_FRAME_UI["convert_status_text"] = create_label(
        convert_frame_ref,
        "Converting video(s)...",
        foreground=LabelColor.ORANGE
    )
    add_widget_to_grid(
        CONVERT_FRAME_UI["convert_status_text"],
        row=CONVERT_FRAME_UI["convert_frame_row_index"]               
    )

    thread = threading.Thread(target=_convert_videos_thread)
    thread.start()

def _convert_videos_thread():
    if not videos_paths:
        edit_label_text(
            CONVERT_FRAME_UI["convert_status_text"],
            "No videos found for conversion",
            LabelColor.RED
        )

    selected_compression = CONVERT_FRAME_UI["compression_combobox"].get()
    selected_color_space = CONVERT_FRAME_UI["color_space_combobox"].get()
    selected_audio_codec = CONVERT_FRAME_UI["audio_codec_combobox"].get()
    b_frames_value = b_frames_variable.get()
    include_text_overlay_value = include_text_overlay_variable.get()
    bit_rate_value = CONVERT_FRAME_UI["bit_rate_scale"].get()

    for path in videos_paths:
        info = DownloadedVideoInfo.get_video_information_from_video_file(path)
        res = info.get_pretty_resolution()
        res_combined = info.get_pretty_resolution(combine=True)
        if include_text_overlay_value == 1:
            overlay_text_size = determine_overlay_text_size(res[0])

        split_file_name = os.path.splitext(path)
        output_path = f"{"BF_" if b_frames_value else ""}{os.path.basename(path)}_{res_combined}_{selected_compression}_{format_color_space_for_conversion(selected_color_space) + "_" if selected_color_space != "4:2:0" else ""}{bit_rate_value}bits{split_file_name[1]}"
        
        # Video format options
        vf = (
            f"format=yuv{format_color_space_for_conversion(selected_color_space)}p"
            + (
                f",drawtext=fontfile=InfiniteBeyond.ttf:text='{res_combined}     {selected_compression}     {format_color_space_for_conversion(selected_color_space)}     {bit_rate_value} bits':fontcolor=white:fontsize={overlay_text_size}:x=(w-text_w)/2:y=25"
                if include_text_overlay_value else ""
            )
        )

        # If B Frames were enabled
        if b_frames_value:
            # Add additional video format option which includes text overlay for B Frames to video
            vf += (f",drawtext=fontfile=InfiniteBeyond.ttf:text='B-Frames':fontcolor=red:"
                   f"fontsize={overlay_text_size}:x=(w-text_w)/2:y=h-text_h-25")
            
        stream_input = ffmpeg.input(path)

        output_options = {
            'b:v': f'{bit_rate_value}M',
            'acodec': selected_audio_codec,
            'vcodec': f'libx{format_compression_for_conversion(selected_compression)}',
            'g': str(calculate_gop(res[1])),
            'ac': '2',
            'vf': vf,
            'bf': 0
        }

        if b_frames_value:
            del output_options['bf']

        stream = ffmpeg.output(
            stream_input,
            output_path,
            **output_options
        )

        ffmpeg.run(stream)
        convert_frame_ref.after(0, lambda: edit_label_text(
            CONVERT_FRAME_UI["convert_status_text"],
            new_text="Conversion completed successfully!",
            foreground=LabelColor.GREEN
        ))

def determine_overlay_text_size(resolution):
    resolution_without_p = int(resolution.replace("p", ""))
    for h, size in [("4K", 200), (1440, 150), ("HD", 100), (720, 75), (480, 50), (360, 30), (240, 15)]:
        if resolution_without_p == h:
            return size
    return 10

def calculate_gop(fps):
    return int(fps * 1.5)

def format_color_space_for_conversion(color_space):
    return color_space.replace(":", "")

def format_compression_for_conversion(compression):
    return compression.replace("H", "")

def on_clear_path_button_click():
    print("deleting")