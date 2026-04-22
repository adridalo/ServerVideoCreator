import os
from pathlib import Path
import shutil
import threading
from tkinter import IntVar, filedialog

import ffmpeg

from src.frames.convert.convert_ui import CONVERT_UI
from src.frames.convert.util.convert_util import calculate_gop, determine_overlay_text_size, format_color_space_for_conversion, format_compression_for_conversion, inc_convert_frame_row_index
from src.types.enums.color import LabelColor
from src.types.models.downloaded_video_info import DownloadedVideoInfo
from src.util import SUPPORTED_AUDIO_CODEC, SUPPORTED_COLOR_SPACE, SUPPORTED_COMPRESSION, SUPPORTED_VIDEO_FORMAT, add_to_text_widget, add_widget_to_grid, change_text_widget_state, create_button, create_checkbutton, create_combobox, create_label, create_scale, create_text, edit_label_text, remove_widget_from_grid, resource_path, update_combobox_values

convert_frame_ref = None
videos_paths = []
b_frames_variable = None
include_text_overlay_variable = None
last_opened_navigation_path = os.path.join(".")

def set_convert_frame_components(frame):
    global convert_frame_ref, b_frames_variable, include_text_overlay_variable

    convert_frame_ref = frame
    CONVERT_UI["convert_frame_row_index"] = 0

    b_frames_variable = IntVar(frame, 0)
    include_text_overlay_variable = IntVar(frame, 1)

    # Select file button
    CONVERT_UI["select_file_button"] = create_button(
        frame,
        text="Select files to convert",
        command=on_file_select_button_click
    )
    add_widget_to_grid(CONVERT_UI["select_file_button"],
                       row=CONVERT_UI["convert_frame_row_index"])
    
    CONVERT_UI["select_directory_button"] = create_button(
        frame,
        text="Select directory to convert",
        command=on_directory_select_button_click
    )
    add_widget_to_grid(CONVERT_UI["select_directory_button"],
                       row=CONVERT_UI["convert_frame_row_index"], column=1, padx=10, pady=5)
    
    inc_convert_frame_row_index()


def on_file_select_button_click():
    global videos_paths, last_opened_navigation_path

    selected = filedialog.askopenfilenames(
        title="Select videos",
        initialdir=last_opened_navigation_path,
        filetypes=[("Videos", "*.mp4 *.mkv")]
    )

    if not selected:
        return

    last_opened_navigation_path = os.path.dirname(selected[0])
    videos_paths.extend(selected)

    display_selected_files()
    display_conversion_options()
    update_conversion_options_values()

def on_directory_select_button_click():
    global videos_paths, last_opened_navigation_path

    selected = list(filedialog.askdirectory(
        title="Select directory",
        initialdir=last_opened_navigation_path
    ))

    selected = "".join(selected)
    last_opened_navigation_path = selected

    if selected:
        files = []
        for root, _, filenames in os.walk(selected):
            for filename in filenames:
                generated_path = os.path.join(root, filename)
                if os.path.splitext(filename)[1][1:] in SUPPORTED_VIDEO_FORMAT:
                    files.append(generated_path)

        videos_paths.extend(files)

        display_selected_files()
        display_conversion_options()
        update_conversion_options_values()

def display_selected_files():
    # First creation
    if CONVERT_UI["file_list_label"] is None:
        CONVERT_UI["file_list_label"] = create_label(convert_frame_ref,
                                                           text="Selected videos:")
        add_widget_to_grid(CONVERT_UI["file_list_label"],
                           row=CONVERT_UI["convert_frame_row_index"])
        inc_convert_frame_row_index()

    if CONVERT_UI["file_list_text"] is None:
        CONVERT_UI["file_list_text"] = create_text(convert_frame_ref, height=6)
        add_widget_to_grid(CONVERT_UI["file_list_text"],
                           row=CONVERT_UI["convert_frame_row_index"])
        inc_convert_frame_row_index()

    # Always refresh text
    change_text_widget_state(CONVERT_UI["file_list_text"], "normal")
    CONVERT_UI["file_list_text"].delete("1.0", "end")

    for p in videos_paths:
        info = DownloadedVideoInfo.get_video_information_from_video_file(p)
        res = info.get_pretty_resolution(True)
        CONVERT_UI["file_list_text"].insert("end", f"• {os.path.basename(p)} ({res})\n")

    change_text_widget_state(CONVERT_UI["file_list_text"], "disabled")

    # Clear button (created once)
    if CONVERT_UI["clear_paths_button"] is None:
        CONVERT_UI["clear_paths_button"] = create_button(
            convert_frame_ref,
            text="Clear paths",
            command=on_clear_path_button_click
        )
        add_widget_to_grid(CONVERT_UI["clear_paths_button"],
                           row=CONVERT_UI["convert_frame_row_index"],
                           column=1)
        
        inc_convert_frame_row_index()

def display_conversion_options():
    if CONVERT_UI["compression_combobox"] is not None:
        return  # options already created

    # COMPRESSION
    CONVERT_UI["compression_combobox_label"] = create_label(convert_frame_ref, text="Select compression:")
    add_widget_to_grid(CONVERT_UI["compression_combobox_label"], row=CONVERT_UI["convert_frame_row_index"])
    inc_convert_frame_row_index()

    CONVERT_UI["compression_combobox"] = create_combobox(
        convert_frame_ref, command=update_conversion_options_values
    )
    update_combobox_values(CONVERT_UI["compression_combobox"], SUPPORTED_COMPRESSION)
    add_widget_to_grid(CONVERT_UI["compression_combobox"], row=CONVERT_UI["convert_frame_row_index"])
    inc_convert_frame_row_index()

    # COLOR SPACE
    CONVERT_UI["color_space_combobox_label"] = create_label(convert_frame_ref, text="Select color space:")
    add_widget_to_grid(CONVERT_UI["color_space_combobox_label"], row=CONVERT_UI["convert_frame_row_index"])
    inc_convert_frame_row_index()

    CONVERT_UI["color_space_combobox"] = create_combobox(
        convert_frame_ref, command=update_conversion_options_values
    )
    update_combobox_values(CONVERT_UI["color_space_combobox"], SUPPORTED_COLOR_SPACE)
    add_widget_to_grid(CONVERT_UI["color_space_combobox"], row=CONVERT_UI["convert_frame_row_index"])
    inc_convert_frame_row_index()

    # BIT RATE
    CONVERT_UI["bit_rate_scale_label"] = create_label(convert_frame_ref, text="Select bit rate (Mbps):")
    add_widget_to_grid(CONVERT_UI["bit_rate_scale_label"], row=CONVERT_UI["convert_frame_row_index"])
    inc_convert_frame_row_index()

    CONVERT_UI["bit_rate_scale"] = create_scale(convert_frame_ref)
    add_widget_to_grid(CONVERT_UI["bit_rate_scale"], row=CONVERT_UI["convert_frame_row_index"])
    inc_convert_frame_row_index()

    # AUDIO CODEC
    CONVERT_UI["audio_codec_label"] = create_label(convert_frame_ref, text="Select audio codec:")
    add_widget_to_grid(CONVERT_UI["audio_codec_label"], row=CONVERT_UI["convert_frame_row_index"])
    inc_convert_frame_row_index()

    CONVERT_UI["audio_codec_combobox"] = create_combobox(
        convert_frame_ref, command=update_conversion_options_values
    )
    update_combobox_values(CONVERT_UI["audio_codec_combobox"], SUPPORTED_AUDIO_CODEC)
    add_widget_to_grid(CONVERT_UI["audio_codec_combobox"], row=CONVERT_UI["convert_frame_row_index"])
    inc_convert_frame_row_index()

    # B-FRAMES
    CONVERT_UI["b_frames_combobox_label"] = create_label(convert_frame_ref, text="Enable B-Frames:")
    add_widget_to_grid(CONVERT_UI["b_frames_combobox_label"], row=CONVERT_UI["convert_frame_row_index"])
    inc_convert_frame_row_index()

    CONVERT_UI["b_frames_combobox"] = create_checkbutton(convert_frame_ref, variable=b_frames_variable)
    add_widget_to_grid(CONVERT_UI["b_frames_combobox"], row=CONVERT_UI["convert_frame_row_index"])
    inc_convert_frame_row_index()

    # TEXT OVERLAY
    CONVERT_UI["include_text_overlay_label"] = create_label(convert_frame_ref, text="Include overlay text:")
    add_widget_to_grid(CONVERT_UI["include_text_overlay_label"], row=CONVERT_UI["convert_frame_row_index"])
    inc_convert_frame_row_index()

    CONVERT_UI["include_text_overlay_combobox"] = create_checkbutton(
        convert_frame_ref, variable=include_text_overlay_variable
    )
    add_widget_to_grid(CONVERT_UI["include_text_overlay_combobox"], row=CONVERT_UI["convert_frame_row_index"])
    inc_convert_frame_row_index()

    # Initially hide the convert button
    if CONVERT_UI.get("convert_button") is not None:
        remove_widget_from_grid(CONVERT_UI["convert_button"])

def should_show_convert_button() -> bool:
    """Return True only if all required fields are filled"""
    if not videos_paths:
        return False

    if not CONVERT_UI.get("compression_combobox") or not CONVERT_UI["compression_combobox"].get():
        return False
    if not CONVERT_UI.get("color_space_combobox") or not CONVERT_UI["color_space_combobox"].get():
        return False
    if not CONVERT_UI.get("audio_codec_combobox") or not CONVERT_UI["audio_codec_combobox"].get():
        return False

    return True

def update_conversion_options_values(event=None):
    """Called whenever any combobox changes"""
    if CONVERT_UI.get("convert_button") is None:
        # Create the button once
        CONVERT_UI["convert_button"] = create_button(
            convert_frame_ref,
            text="Convert videos",
            command=on_convert_button_click
        )

    if should_show_convert_button():
        add_widget_to_grid(CONVERT_UI["convert_button"],
                           row=CONVERT_UI["convert_frame_row_index"])
        inc_convert_frame_row_index()  # Only increment if we actually show it
    else:
        # Hide the button if conditions are not met
        remove_widget_from_grid(CONVERT_UI["convert_button"])


def on_convert_button_click():
    CONVERT_UI["convert_status_text"] = create_label(
        convert_frame_ref,
        "Converting video(s)...",
        foreground=LabelColor.ORANGE
    )
    add_widget_to_grid(
        CONVERT_UI["convert_status_text"],
        row=CONVERT_UI["convert_frame_row_index"]               
    )

    thread = threading.Thread(target=_convert_videos_thread)
    thread.start()

def on_clear_path_button_click():
    global videos_paths
    videos_paths.clear()
    
    if CONVERT_UI.get("file_list_text"):
        change_text_widget_state(CONVERT_UI["file_list_text"], "normal")
        CONVERT_UI["file_list_text"].delete('1.0', "end")
        change_text_widget_state(CONVERT_UI["file_list_text"], "disabled")

    # Refresh convert button visibility after clearing
    update_conversion_options_values()

def _convert_videos_thread():
    if not videos_paths:
        edit_label_text(
            CONVERT_UI["convert_status_text"],
            "No videos found for conversion",
            LabelColor.RED
        )

    selected_compression = CONVERT_UI["compression_combobox"].get()
    selected_color_space = CONVERT_UI["color_space_combobox"].get()
    selected_audio_codec = CONVERT_UI["audio_codec_combobox"].get()
    b_frames_value = b_frames_variable.get()
    include_text_overlay_value = include_text_overlay_variable.get()
    bit_rate_value = CONVERT_UI["bit_rate_scale"].get()

    for path in videos_paths:
        info = DownloadedVideoInfo.get_video_information_from_video_file(path)
        res = info.get_pretty_resolution()
        res_combined = info.get_pretty_resolution(combine=True)
        if include_text_overlay_value == 1:
            overlay_text_size = determine_overlay_text_size(res[0])

        file_name_no_ext, ext = os.path.splitext(os.path.basename(path))
        output_path = (
            f'{"BF_" if b_frames_value else ""}'
            f'{file_name_no_ext}_{res_combined}_{selected_compression}_'
            f'{format_color_space_for_conversion(selected_color_space) + "_" if selected_color_space != "4:2:0" else ""}'
            f'{bit_rate_value}bits{ext}'
        )

        font_path = resource_path("InfiniteBeyond.ttf")
        sanitized_font_path = font_path.replace("\\", "/").replace(":", "\\\\:")
        
        # Video format options
        vf = (
            f"format=yuv{format_color_space_for_conversion(selected_color_space)}p"
            + (
                f",drawtext=fontfile={sanitized_font_path}:text='{res_combined}     {selected_compression}     {format_color_space_for_conversion(selected_color_space)}     {bit_rate_value} bits':fontcolor=white:fontsize={overlay_text_size}:x=(w-text_w)/2:y=25"
                if include_text_overlay_value else ""
            )
        )

        # If B Frames were enabled
        if b_frames_value:
            # Add additional video format option which includes text overlay for B Frames to video
            vf += (f",drawtext=fontfile={sanitized_font_path}:text='B-Frames':fontcolor=red:"
                   f"fontsize={determine_overlay_text_size(res[0])}:x=(w-text_w)/2:y=h-text_h-25")
            
        try:
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
            
            ffmpeg_executable = resource_path("ffmpeg.exe")
            
            ffmpeg.run(stream, cmd=ffmpeg_executable)

            target_dir = os.path.join(
                "converted", 
                selected_compression, 
                res[0], 
                str(res[1]), 
                format_color_space_for_conversion(selected_color_space) if selected_color_space != "4:2:0" else "",
                "B-Frames" if b_frames_value else ""
            )
            os.makedirs(target_dir, exist_ok=True)
            shutil.move(output_path, os.path.join(target_dir, os.path.basename(output_path)))
        except Exception as e:
            edit_label_text(
                CONVERT_UI["convert_status_text"],
                new_text=f"Error occurred during conversion: {e}",
                foreground=LabelColor.RED
            )

    convert_frame_ref.after(0, lambda: edit_label_text(
        CONVERT_UI["convert_status_text"],
        new_text=f"Conversion of {len(videos_paths)} video(s) completed!",
        foreground=LabelColor.GREEN
    ))