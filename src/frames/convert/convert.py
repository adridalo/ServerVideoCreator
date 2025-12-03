import os
from tkinter import IntVar, filedialog

from src.frames.convert.convert_ui import CONVERT_FRAME_UI
from src.frames.convert.util.convert_util import inc_convert_frame_row_index
from src.types.models.downloaded_video_info import DownloadedVideoInfo
from src.util import SUPPORTED_AUDIO_CODEC, SUPPORTED_COLOR_SPACE, SUPPORTED_COMPRESSION, add_to_text_widget, add_widget_to_grid, create_button, create_checkbutton, create_combobox, create_label, create_scale, create_text, remove_widget_from_grid, update_combobox_values

convert_frame_ref = None
videos_paths = []
b_frames_variable = None
include_text_overlay_variable = None

def set_convert_frame_components(frame):
    global convert_frame_ref, b_frames_variable, include_text_overlay_variable

    convert_frame_ref = frame
    b_frames_variable = IntVar(frame)
    include_text_overlay_variable = IntVar(value=1)

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
        display_conversion_options()

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

def display_conversion_options():
    # Select compression label
    CONVERT_FRAME_UI["compression_dropbox_label"] = create_label(convert_frame_ref, text="Select compression: ")
    add_widget_to_grid(CONVERT_FRAME_UI["compression_dropbox_label"], row=CONVERT_FRAME_UI["convert_frame_row_index"], pady=2)

    inc_convert_frame_row_index()

    # Select compression combobox
    CONVERT_FRAME_UI["compression_dropbox"] = create_combobox(convert_frame_ref, command=print("x"))
    add_widget_to_grid(CONVERT_FRAME_UI["compression_dropbox"], row=CONVERT_FRAME_UI["convert_frame_row_index"], columnspan=2, pady=2)
    update_combobox_values(CONVERT_FRAME_UI["compression_dropbox"], SUPPORTED_COMPRESSION)

    inc_convert_frame_row_index()

    # Select color space label
    CONVERT_FRAME_UI["color_space_dropbox_label"] = create_label(convert_frame_ref, text="Select color space: ")
    add_widget_to_grid(CONVERT_FRAME_UI["color_space_dropbox_label"], row=CONVERT_FRAME_UI["convert_frame_row_index"], pady=2)

    inc_convert_frame_row_index()

    # Select color space combobox
    CONVERT_FRAME_UI["color_space_dropbox"] = create_combobox(convert_frame_ref, command=print("\n"))
    add_widget_to_grid(CONVERT_FRAME_UI["color_space_dropbox"], row=CONVERT_FRAME_UI["convert_frame_row_index"], columnspan=2, pady=2)
    update_combobox_values(CONVERT_FRAME_UI["color_space_dropbox"], SUPPORTED_COLOR_SPACE)

    inc_convert_frame_row_index()

    # Select bit rate label
    CONVERT_FRAME_UI["bit_rate_scale_label"] = create_label(convert_frame_ref, text="Select bit rate: ")
    add_widget_to_grid(CONVERT_FRAME_UI["bit_rate_scale_label"], row=CONVERT_FRAME_UI["convert_frame_row_index"], pady=2)

    inc_convert_frame_row_index()

    # Select bit rate scale
    CONVERT_FRAME_UI["bit_rate_scale"] = create_scale(convert_frame_ref)
    add_widget_to_grid(CONVERT_FRAME_UI["bit_rate_scale"], row=CONVERT_FRAME_UI["convert_frame_row_index"], pady=2)

    inc_convert_frame_row_index()

    # Select audio codec label
    CONVERT_FRAME_UI["audio_codec_label"] = create_label(convert_frame_ref, text="Select audio codec: ")
    add_widget_to_grid(CONVERT_FRAME_UI["audio_codec_label"], row=CONVERT_FRAME_UI["convert_frame_row_index"], pady=2)

    inc_convert_frame_row_index()

    # Select audio codec combobox
    CONVERT_FRAME_UI["audio_codec_combobox"] = create_combobox(convert_frame_ref, command=print("\n"))
    add_widget_to_grid(CONVERT_FRAME_UI["audio_codec_combobox"], row=CONVERT_FRAME_UI["convert_frame_row_index"], columnspan=2, pady=2)
    update_combobox_values(CONVERT_FRAME_UI["audio_codec_combobox"], SUPPORTED_AUDIO_CODEC)

    inc_convert_frame_row_index()

    # Enable B-Frames label
    CONVERT_FRAME_UI["b_frames_checkbox_label"] = create_label(convert_frame_ref, text="Enable B-Frames? ")
    add_widget_to_grid(CONVERT_FRAME_UI["b_frames_checkbox_label"], row=CONVERT_FRAME_UI["convert_frame_row_index"], pady=2)

    inc_convert_frame_row_index()

    # Enable B-Frames checkbutton
    CONVERT_FRAME_UI["b_frames_checkbox"] = create_checkbutton(convert_frame_ref, variable=b_frames_variable)
    add_widget_to_grid(CONVERT_FRAME_UI["b_frames_checkbox"], row=CONVERT_FRAME_UI["convert_frame_row_index"], pady=2)

    inc_convert_frame_row_index()

    # Include text overlay label
    CONVERT_FRAME_UI["include_text_overlay_label"] = create_label(convert_frame_ref, text="Include text overlay? ")
    add_widget_to_grid(CONVERT_FRAME_UI["include_text_overlay_label"], row=CONVERT_FRAME_UI["convert_frame_row_index"], pady=2)

    inc_convert_frame_row_index()

    # Include text overlay checkbutton
    CONVERT_FRAME_UI["include_text_overlay_checkbox"] = create_checkbutton(convert_frame_ref, variable=include_text_overlay_variable)
    add_widget_to_grid(CONVERT_FRAME_UI["include_text_overlay_checkbox"], row=CONVERT_FRAME_UI["convert_frame_row_index"], pady=2)

    inc_convert_frame_row_index()

def on_clear_path_button_click():
    print("deleting")