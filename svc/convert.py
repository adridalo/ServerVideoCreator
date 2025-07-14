from pathlib import Path
import subprocess
from tkinter import W, Button, IntVar, Label, Scale, filedialog, ttk

from svc.models.video_info import DownloadedVideoInfo

convert_tab_ref = None
cv_row_index = 0
filepaths = []
b_frames_value = None
selected_compression = None
selected_color_space = None

select_files_button = None
convert_button = None
compression_dropbox = None
compression_dropbox_label = None
color_space_dropbox = None
color_space_dropbox_label = None
bit_rate_scale = None
bit_rate_scale_label = None
b_frames_checkbox = None
b_frames_checkbox_label = None

def setup_convert_tab(tab):
    global convert_tab_ref, cv_row_index, select_files_button, convert_button, compression_dropbox, compression_dropbox_label, color_space_dropbox, color_space_dropbox_label, bit_rate_scale, bit_rate_scale_label, b_frames_checkbox, b_frames_checkbox_label, b_frames_value

    convert_tab_ref = tab
    cv_row_index = 0

    select_files_button = Button(tab, text="Select files to convert", command=select_files)
    select_files_button.grid(row=cv_row_index, column=0, columnspan=2, sticky=W, padx=10, pady=5)

    cv_row_index += 1

    compression_dropbox_label = Label(tab, text="Select compression: ")
    compression_dropbox_label.grid_forget()
    compression_dropbox = ttk.Combobox(tab, values=["---", "H264", "H265"])
    compression_dropbox.bind("<<ComboboxSelected>>", on_compression_selected)
    compression_dropbox.set("---")
    compression_dropbox.grid_forget()

    color_space_dropbox_label = Label(tab, text="Select color space")
    color_space_dropbox_label.grid_forget()
    color_space_dropbox = ttk.Combobox(tab, values=["---", "4:2:0", "4:2:2", "4:4:4"])
    color_space_dropbox.bind("<<ComboboxSelected>>", on_color_space_selected)
    color_space_dropbox.set("---")
    color_space_dropbox.grid_forget()

    bit_rate_scale_label = Label(tab, text="Select bit rate: ")
    bit_rate_scale_label.grid_forget()
    bit_rate_scale = Scale(tab, from_=1, to=100, orient="horizontal")
    bit_rate_scale.grid_forget()

    b_frames_checkbox_label = Label(tab, text="Enable B-Frames")
    b_frames_checkbox_label.grid_forget()
    b_frames_value = IntVar()
    b_frames_checkbox = ttk.Checkbutton(tab, variable=b_frames_value)
    b_frames_checkbox.grid_forget()

    convert_button = Button(tab, text="Convert video(s)", command=convert_videos)
    convert_button.grid_forget()

def on_compression_selected(event):
    global selected_compression, compression_dropbox

    current_compression_selection = compression_dropbox.get()
    if current_compression_selection == "---":
        selected_compression = None

    if current_compression_selection == "H264":
        selected_compression = "264"
    elif current_compression_selection == "H265":
        selected_compression = "265"

    will_convert_button_appear()

def on_color_space_selected(event):
    global selected_color_space, color_space_dropbox

    current_color_space = color_space_dropbox.get()
    if current_color_space == "---":
        selected_color_space = None

    if current_color_space == "4:2:0":
        selected_color_space = "420"
    elif current_color_space == "4:2:2":
        selected_color_space = "422"
    elif current_color_space == "4:4:4":
        selected_color_space = "444"

    will_convert_button_appear()

def will_convert_button_appear():
    global selected_compression, b_frames_value, filepaths, bit_rate_scale, convert_button, selected_color_space, cv_row_index

    if selected_compression is not None and selected_color_space is not None:
        convert_button.grid(row=cv_row_index)
    else:
        convert_button.grid_forget()

def select_files():
    global filepaths, options_label, convert_button, cv_row_index, compression_dropbox, compression_dropbox_label, color_space_dropbox, color_space_dropbox_label, bit_rate_scale, bit_rate_scale_label, b_frames_checkbox, b_frames_checkbox_label

    filepaths = filedialog.askopenfilenames(
        title="Select videos",
        initialdir=".",
        filetypes=[
            ("MP4 Videos", "*.mp4"),
            ("MKV Videos", "*.mvk"),
            ("WebM Videos", "*.webm"),
        ]
    )

    if filepaths:
        compression_dropbox_label.grid(row=cv_row_index, column=0)
        compression_dropbox.grid(row=cv_row_index, column=1)
        cv_row_index += 1

        color_space_dropbox_label.grid(row=cv_row_index, column=0)
        color_space_dropbox.grid(row=cv_row_index, column=1)
        cv_row_index += 1

        bit_rate_scale_label.grid(row=cv_row_index, column=0)
        bit_rate_scale.grid(row=cv_row_index, column=1)
        cv_row_index += 1

        b_frames_checkbox_label.grid(row=cv_row_index, column=0)
        b_frames_checkbox.grid(row=cv_row_index, column=1)
        cv_row_index += 1

def determine_overlay_text_size(resolution):
    if resolution == 2160:
        return 200
    elif resolution == 1080:
        return 100
    elif resolution == 720:
        return 75
    elif resolution == 480:
        return 50

def convert_videos():
    global filepaths, selected_compression, bit_rate_scale, b_frames_value, selected_color_space

    convert_b_frames = b_frames_value.get()
    convert_compression = selected_compression
    convert_bit_rate = bit_rate_scale.get()
    convert_color_space = selected_color_space

    if filepaths:
        for path in filepaths:
            path_video_info = DownloadedVideoInfo.get_video_info(path)
            path_pretty_resolution = DownloadedVideoInfo._get_pretty_resolution(path_video_info.resolution[0], path_video_info.fps)
            overlay_text_size = determine_overlay_text_size(path_video_info.resolution[0])

            input_path = Path(path)
            output_path = input_path.with_name(f"{"BF_" if convert_b_frames == 1 else ""}{input_path.stem}_{path_pretty_resolution}_H{convert_compression}_{convert_bit_rate}bits{input_path.suffix}")

            vf_filter = f"format=yuv{convert_color_space}p,drawtext=fontfile=InfiniteBeyond.ttf:text='{path_pretty_resolution}     H{selected_compression}     {convert_color_space}     {convert_bit_rate} bits':fontcolor=white:fontsize={overlay_text_size}:x=(w-text_w)/2:y=25"

            if convert_b_frames == 1:
                vf_filter += f",drawtext=fontfile=InfiniteBeyond.ttf:text='B-Frames':fontcolor=red:fontsize={overlay_text_size}:x=(w-text_w)/2:y=h-text_h-25"

            command = [
                "ffmpeg",
                "-i", str(path),
                "-acodec", "aac",
                "-c:v", f"libx{convert_compression}",
                "-g", "90",
                "-b:v", f"{convert_bit_rate}M",
                "-ac", "2",
                "-vf", vf_filter,
                str(output_path)
            ]

            if convert_b_frames == 0:
                command += ["-bf", "0"]

            subprocess.run(command, check=True)
    else:
        print("No files selected")