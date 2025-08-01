import os
import pathlib
import shutil
import subprocess
from pathlib import Path
from tkinter import W, Button, IntVar, Label, Scale, Text, filedialog, ttk

from svc.models.video_info import DownloadedVideoInfo
from svc.util import supported_formats

# UI and state references
convert_tab_ref = None
cv_row_index = 0
filepaths = []

# Conversion options
b_frames_value = None
selected_compression = None
selected_color_space = None
selected_audio_codec = None

# UI Elements
def_ui = lambda: {
    "select_file_button": None,
    "select_directory_button": None,
    "file_list_label": None,
    "file_list_text": None,
    "clear_paths_button": None,
    "convert_button": None,
    "compression_dropbox": None,
    "compression_dropbox_label": None,
    "color_space_dropbox": None,
    "color_space_dropbox_label": None,
    "bit_rate_scale": None,
    "bit_rate_scale_label": None,
    "audio_codec_label": None,
    "audio_codec_dropbox": None,
    "b_frames_checkbox": None,
    "b_frames_checkbox_label": None
}
ui = def_ui()


def setup_convert_tab(tab):
    global convert_tab_ref, cv_row_index, b_frames_value, ui
    convert_tab_ref = tab
    cv_row_index = 0
    b_frames_value = IntVar()
    ui.update(def_ui())

    ui["select_file_button"] = Button(tab, text="Select video to convert", command=select_files)
    ui["select_file_button"].grid(row=cv_row_index, column=0, sticky=W, padx=10, pady=5)

    ui["select_directory_button"] = Button(tab, text="Select directory to convert", command=select_directory)
    ui["select_directory_button"].grid(row=cv_row_index, column=1, sticky=W, padx=10, pady=5)
    cv_row_index += 1

    ui["file_list_label"] = Label(tab, text="Selected video files:", anchor='w', justify='left')
    ui["file_list_text"] = Text(tab, height=6, width=70, wrap="word", state="disabled")
    ui["clear_paths_button"] = Button(tab, text="Clear all video paths", command=on_clear_path)

    ui["compression_dropbox_label"] = Label(tab, text="Select compression: ")
    ui["compression_dropbox"] = ttk.Combobox(tab, values=["---", "H264", "H265"])
    ui["compression_dropbox"].bind("<<ComboboxSelected>>", on_compression_selected)
    ui["compression_dropbox"].set("---")

    ui["color_space_dropbox_label"] = Label(tab, text="Select color space")
    ui["color_space_dropbox"] = ttk.Combobox(tab, values=["---", "4:2:0", "4:2:2", "4:4:4"])
    ui["color_space_dropbox"].bind("<<ComboboxSelected>>", on_color_space_selected)
    ui["color_space_dropbox"].set("---")

    ui["bit_rate_scale_label"] = Label(tab, text="Select bit rate: ")
    ui["bit_rate_scale"] = Scale(tab, from_=1, to=100, orient="horizontal")

    ui["audio_codec_label"] = Label(tab, text="Select audio codec: ")
    ui["audio_codec_dropbox"] = ttk.Combobox(tab, values=["---", "aac", "flac", "mp3", "alac", "opus", "sbc", "aptx"])
    ui["audio_codec_dropbox"].bind("<<ComboboxSelected>>", on_audio_codec_selected)
    ui["audio_codec_dropbox"].set("---")

    ui["b_frames_checkbox_label"] = Label(tab, text="Enable B-Frames")
    ui["b_frames_checkbox"] = ttk.Checkbutton(tab, variable=b_frames_value)

    ui["convert_button"] = Button(tab, text="Convert video(s)", command=convert_videos)


def on_compression_selected(event):
    global selected_compression
    selected_compression = {"H264": "264", "H265": "265"}.get(ui["compression_dropbox"].get())
    will_convert_button_appear()


def on_color_space_selected(event):
    global selected_color_space
    selected_color_space = {"4:2:0": "420", "4:2:2": "422", "4:4:4": "444"}.get(ui["color_space_dropbox"].get())
    will_convert_button_appear()


def on_audio_codec_selected(event):
    global selected_audio_codec
    val = ui["audio_codec_dropbox"].get()
    selected_audio_codec = val if val != "---" else None
    will_convert_button_appear()


def on_clear_path():
    global filepaths
    filepaths.clear()
    ui["file_list_text"].config(state='normal')
    ui["file_list_text"].delete("1.0", "end")
    ui["file_list_text"].config(state='disabled')
    ui["convert_button"].grid_remove()
    ui["clear_paths_button"].grid_remove()


def will_convert_button_appear():
    if selected_compression and selected_color_space and selected_audio_codec:
        ui["convert_button"].grid(row=cv_row_index, column=0, columnspan=2, sticky=W, padx=10, pady=5)
    else:
        ui["convert_button"].grid_remove()


def select_files():
    global filepaths
    video_file_path = list(filedialog.askopenfilenames(
        title="Select videos",
        initialdir=".",
        filetypes=[("All files", "*.*"), ("MP4 Videos", "*.mp4"), ("MKV Videos", "*.mkv"), ("WebM Videos", "*.webm")]
    ))
    if video_file_path:
        if os.path.splitext(video_file_path[0])[1][1:] in supported_formats:
            filepaths.extend(video_file_path)
            display_selected_files()

def select_directory():
    global filepaths
    video_files_path = list(filedialog.askdirectory(
        title="Select videos",
        initialdir="."
    ))
    video_files_path = "".join(video_files_path)
    if video_files_path:
        files = []
        for root, _, filenames in os.walk(video_files_path):
            for filename in filenames:
                generated_path = os.path.join(root, filename)
                if os.path.splitext(filename)[1][1:] in supported_formats:
                    files.append(generated_path)
        filepaths.extend(files)
        display_selected_files()

def display_selected_files():
    global cv_row_index

    ui["file_list_label"].grid(row=cv_row_index, column=0, columnspan=2, sticky='w', padx=10, pady=(10, 0))
    cv_row_index += 1

    ui["file_list_text"].config(state='normal')
    ui["file_list_text"].delete('1.0', 'end')
    for path in filepaths:
        info = DownloadedVideoInfo.get_video_info(path)
        res = DownloadedVideoInfo._get_pretty_resolution(info.resolution[0], info.fps)
        ui["file_list_text"].insert("end", f"• {os.path.basename(path)} ({res})\n")
    ui["file_list_text"].config(state='disabled')
    ui["file_list_text"].grid(row=cv_row_index, column=0, columnspan=2, sticky='w', padx=10, pady=(0, 10))
    cv_row_index += 1

    for key in ["clear_paths_button", "compression_dropbox_label", "compression_dropbox", "color_space_dropbox_label",
                "color_space_dropbox", "bit_rate_scale_label", "bit_rate_scale", "audio_codec_label",
                "audio_codec_dropbox", "b_frames_checkbox_label", "b_frames_checkbox"]:
        ui[key].grid(row=cv_row_index, column=0 if 'label' in key else 1, sticky=W, padx=10, pady=5)
        if 'label' not in key:
            cv_row_index += 1

    will_convert_button_appear()


def determine_overlay_text_size(res_height):
    for h, size in [(2160, 200), (1080, 100), (720, 75), (480, 50), (360, 30), (240, 15)]:
        if res_height == h:
            return size
    return 10


def calculate_goc(fps):
    return int(fps * 1.5)


def convert_videos():
    if not filepaths:
        print("No files selected")
        return

    b_frames = b_frames_value.get()
    bit_rate = ui["bit_rate_scale"].get()

    for path in filepaths:
        info = DownloadedVideoInfo.get_video_info(path)
        res_str = DownloadedVideoInfo._get_pretty_resolution(info.resolution[0], info.fps)
        overlay_size = determine_overlay_text_size(info.resolution[0])

        input_path = Path(path)
        out_name = f"{'BF_' if b_frames else ''}{input_path.stem}_{res_str}_H{selected_compression}_{bit_rate}bits{input_path.suffix}"
        output_path = input_path.with_name(out_name)

        vf = (f"format=yuv{selected_color_space}p,drawtext=fontfile=InfiniteBeyond.ttf:"
              f"text='{res_str}     H{selected_compression}     {selected_color_space}     {bit_rate} bits':"
              f"fontcolor=white:fontsize={overlay_size}:x=(w-text_w)/2:y=25")

        if b_frames:
            vf += (f",drawtext=fontfile=InfiniteBeyond.ttf:text='B-Frames':fontcolor=red:"
                   f"fontsize={overlay_size}:x=(w-text_w)/2:y=h-text_h-25")

        cmd = ["ffmpeg", "-i", str(input_path),
               "-acodec", selected_audio_codec,
               "-c:v", f"libx{selected_compression}",
               "-g", str(calculate_goc(info.fps)),
               "-b:v", f"{bit_rate}M",
               "-bf", "0", "-ac", "2",
               "-vf", vf, str(output_path)]

        if b_frames:
            cmd.pop(11)  # remove "-bf"
            cmd.pop(11)  # remove "0"

        subprocess.run(cmd, check=True)

        target_dir = os.path.join("converted", res_str, str(info.fps))
        os.makedirs(target_dir, exist_ok=True)
        shutil.move(output_path, os.path.join(target_dir, os.path.basename(output_path)))
