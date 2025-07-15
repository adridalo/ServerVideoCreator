import os
from pathlib import Path
import shutil
import subprocess
from tkinter import W, Button, IntVar, Label, Scale, Text, filedialog, ttk

from svc.models.video_info import DownloadedVideoInfo

convert_tab_ref = None
cv_row_index = 0
filepaths = []
b_frames_value = None
selected_compression = None
selected_color_space = None
selected_audio_codec = None

select_files_button = None
file_list_label = None
file_list_text = None
convert_button = None
compression_dropbox = None
compression_dropbox_label = None
color_space_dropbox = None
color_space_dropbox_label = None
bit_rate_scale = None
bit_rate_scale_label = None
audio_codec_label = None
audio_codec_dropbox = None
b_frames_checkbox = None
b_frames_checkbox_label = None


def setup_convert_tab(tab):
    global convert_tab_ref, cv_row_index, select_files_button, convert_button, compression_dropbox, compression_dropbox_label
    global color_space_dropbox, color_space_dropbox_label, bit_rate_scale, bit_rate_scale_label, audio_codec_label
    global audio_codec_dropbox, b_frames_checkbox, b_frames_checkbox_label, b_frames_value
    global file_list_label, file_list_text

    convert_tab_ref = tab
    cv_row_index = 0

    select_files_button = Button(tab, text="Select files to convert", command=select_files)
    select_files_button.grid(row=cv_row_index, column=0, columnspan=2, sticky=W, padx=10, pady=5)
    cv_row_index += 1

    
    file_list_label = Label(tab, text="Selected video files:", anchor='w', justify='left')
    file_list_text = Text(tab, height=6, width=70, wrap="word", state="disabled")

    compression_dropbox_label = Label(tab, text="Select compression: ")
    compression_dropbox = ttk.Combobox(tab, values=["---", "H264", "H265"])
    compression_dropbox.bind("<<ComboboxSelected>>", on_compression_selected)
    compression_dropbox.set("---")

    color_space_dropbox_label = Label(tab, text="Select color space")
    color_space_dropbox = ttk.Combobox(tab, values=["---", "4:2:0", "4:2:2", "4:4:4"])
    color_space_dropbox.bind("<<ComboboxSelected>>", on_color_space_selected)
    color_space_dropbox.set("---")

    bit_rate_scale_label = Label(tab, text="Select bit rate: ")
    bit_rate_scale = Scale(tab, from_=1, to=100, orient="horizontal")

    audio_codec_label = Label(tab, text="Select audio codec: ")
    audio_codec_dropbox = ttk.Combobox(tab, values=["---", "aac", "flac", "mp3", "alac", "opus", "sbc", "aptx"])
    audio_codec_dropbox.bind("<<ComboboxSelected>>", on_audio_codec_selected)
    audio_codec_dropbox.set("---")

    b_frames_checkbox_label = Label(tab, text="Enable B-Frames")
    b_frames_value = IntVar()
    b_frames_checkbox = ttk.Checkbutton(tab, variable=b_frames_value)

    convert_button = Button(tab, text="Convert video(s)", command=convert_videos)


def on_compression_selected(event):
    global selected_compression

    value = compression_dropbox.get()
    selected_compression = None
    if value == "H264":
        selected_compression = "264"
    elif value == "H265":
        selected_compression = "265"

    will_convert_button_appear()


def on_color_space_selected(event):
    global selected_color_space

    value = color_space_dropbox.get()
    selected_color_space = None
    if value == "4:2:0":
        selected_color_space = "420"
    elif value == "4:2:2":
        selected_color_space = "422"
    elif value == "4:4:4":
        selected_color_space = "444"

    will_convert_button_appear()


def on_audio_codec_selected(event):
    global selected_audio_codec

    value = audio_codec_dropbox.get()
    selected_audio_codec = None if value == "---" else value

    will_convert_button_appear()


def will_convert_button_appear():
    if selected_compression and selected_color_space and selected_audio_codec:
        convert_button.grid(row=cv_row_index, column=0, columnspan=2, sticky=W, padx=10, pady=5)
    else:
        convert_button.grid_remove()


def select_files():
    global filepaths, cv_row_index

    filepaths = filedialog.askopenfilenames(
        title="Select videos",
        initialdir=".",
        filetypes=[
            ("All files", "*.*"),
            ("MP4 Videos", "*.mp4"),
            ("MKV Videos", "*.mkv"),
            ("WebM Videos", "*.webm"),
        ]
    )

    if filepaths:
        file_list_label.grid(row=cv_row_index, column=0, columnspan=2, sticky='w', padx=10, pady=(10, 0))
        cv_row_index += 1

        file_list_text.config(state='normal')
        file_list_text.delete('1.0', 'end')
        for path in filepaths:
            file_info = DownloadedVideoInfo.get_video_info(path)
            file_res = DownloadedVideoInfo._get_pretty_resolution(file_info.resolution[0], file_info.fps)
            file_list_text.insert("end", f"• {os.path.basename(path)} ({file_res})\n")
        file_list_text.config(state='disabled')
        file_list_text.grid(row=cv_row_index, column=0, columnspan=2, sticky='w', padx=10, pady=(0, 10))
        cv_row_index += 1

        compression_dropbox_label.grid(row=cv_row_index, column=0, sticky=W, padx=10, pady=5)
        compression_dropbox.grid(row=cv_row_index, column=1, sticky=W, padx=10, pady=5)
        cv_row_index += 1

        color_space_dropbox_label.grid(row=cv_row_index, column=0, sticky=W, padx=10, pady=5)
        color_space_dropbox.grid(row=cv_row_index, column=1, sticky=W, padx=10, pady=5)
        cv_row_index += 1

        bit_rate_scale_label.grid(row=cv_row_index, column=0, sticky=W, padx=10, pady=5)
        bit_rate_scale.grid(row=cv_row_index, column=1, sticky=W, padx=10, pady=5)
        cv_row_index += 1

        audio_codec_label.grid(row=cv_row_index, column=0, sticky=W, padx=10, pady=5)
        audio_codec_dropbox.grid(row=cv_row_index, column=1, sticky=W, padx=10, pady=5)
        cv_row_index += 1

        b_frames_checkbox_label.grid(row=cv_row_index, column=0, sticky=W, padx=10, pady=5)
        b_frames_checkbox.grid(row=cv_row_index, column=1, sticky=W, padx=10, pady=5)
        cv_row_index += 1

        will_convert_button_appear()


def determine_overlay_text_size(res_height):
    if res_height == 2160:
        return 200
    elif res_height == 1080:
        return 100
    elif res_height == 720:
        return 75
    elif res_height == 480:
        return 50
    elif res_height == 360:
        return 30
    elif res_height == 240:
        return 15
    else:
        return 10


def calculate_goc(fps):
    return int(fps * 1.5)


def convert_videos():
    if not filepaths:
        print("No files selected")
        return

    convert_b_frames = b_frames_value.get()
    convert_compression = selected_compression
    convert_bit_rate = bit_rate_scale.get()
    convert_color_space = selected_color_space

    for path in filepaths:
        path_video_info = DownloadedVideoInfo.get_video_info(path)
        path_pretty_resolution = DownloadedVideoInfo._get_pretty_resolution(path_video_info.resolution[0], path_video_info.fps)
        overlay_text_size = determine_overlay_text_size(path_video_info.resolution[0])

        input_path = Path(path)
        output_path = input_path.with_name(f"{'BF_' if convert_b_frames else ''}{input_path.stem}_{path_pretty_resolution}_H{convert_compression}_{convert_bit_rate}bits{input_path.suffix}")

        vf_filter = f"format=yuv{convert_color_space}p,drawtext=fontfile=InfiniteBeyond.ttf:text='{path_pretty_resolution}     H{selected_compression}     {convert_color_space}     {convert_bit_rate} bits':fontcolor=white:fontsize={overlay_text_size}:x=(w-text_w)/2:y=25"

        if convert_b_frames:
            vf_filter += f",drawtext=fontfile=InfiniteBeyond.ttf:text='B-Frames':fontcolor=red:fontsize={overlay_text_size}:x=(w-text_w)/2:y=h-text_h-25"

        command = [
            "ffmpeg",
            "-i", str(path),
            "-acodec", selected_audio_codec,
            "-c:v", f"libx{convert_compression}",
            "-g", f"{calculate_goc(path_video_info.fps)}",
            "-b:v", f"{convert_bit_rate}M",
            "-ac", "2",
            "-vf", vf_filter,
            str(output_path)
        ]

        if not convert_b_frames:
            command += ["-bf", "0"]

        subprocess.run(command, check=True)

        height = path_video_info.resolution[0]
        fps = path_video_info.fps
        pretty_res = DownloadedVideoInfo._get_pretty_resolution(height, fps, include_fps=False)

        target_folder = os.path.join("converted", pretty_res, str(fps))
        os.makedirs(target_folder, exist_ok=True)

        target_path = os.path.join(target_folder, os.path.basename(output_path))
        shutil.move(output_path, target_path)
