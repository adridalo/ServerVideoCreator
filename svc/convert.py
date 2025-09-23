import os
import shutil
import subprocess
from pathlib import Path
import threading
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

# Defines blank UI components
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
    "b_frames_checkbox_label": None,
    "convert_status_text": None,
}

ui = def_ui()

# Setup for UI elements. Hides most elements and will reveal them as application is used
# Args:
# - tab: Tkinter tab (used for frames for notebooks)
def setup_convert_tab(tab):
    global convert_tab_ref, cv_row_index, b_frames_value, include_text_overlay_value, ui

    convert_tab_ref = tab
    cv_row_index = 0
    b_frames_value = IntVar()
    include_text_overlay_value = IntVar(value=1)
    # Update UI to be blank
    ui.update(def_ui())

    # Select file(s) button UI component
    ui["select_file_button"] = Button(tab, text="Select video to convert", command=select_files)
    ui["select_file_button"].grid(row=cv_row_index, column=0, sticky=W, padx=10, pady=5)

    # Select directory button UI component
    ui["select_directory_button"] = Button(tab, text="Select directory to convert", command=select_directory)
    ui["select_directory_button"].grid(row=cv_row_index, column=1, sticky=W, padx=10, pady=5)
    cv_row_index += 1

    # Label + List of selected video(s) UI components
    ui["file_list_label"] = Label(tab, text="Selected video files:", anchor='w', justify='left')
    ui["file_list_text"] = Text(tab, height=6, width=70, wrap="word", state="disabled")

    # Clear selected video paths button UI component
    ui["clear_paths_button"] = Button(tab, text="Clear all video paths", command=on_clear_path)

    # Compression dropbox + label UI components (initialize with empty value "---")
    ui["compression_dropbox_label"] = Label(tab, text="Select compression: ")
    ui["compression_dropbox"] = ttk.Combobox(tab, values=["---", "H264", "H265"])
    ui["compression_dropbox"].bind("<<ComboboxSelected>>", on_compression_selected)
    ui["compression_dropbox"].set("---")

    # Color space dropbox + label UI components (initialize with empty value "---")
    ui["color_space_dropbox_label"] = Label(tab, text="Select color space")
    ui["color_space_dropbox"] = ttk.Combobox(tab, values=["---", "4:2:0", "4:2:2", "4:4:4"])
    ui["color_space_dropbox"].bind("<<ComboboxSelected>>", on_color_space_selected)
    ui["color_space_dropbox"].set("---")

    # Bit rate scale + label UI componenets
    ui["bit_rate_scale_label"] = Label(tab, text="Select bit rate: ")
    ui["bit_rate_scale"] = Scale(tab, from_=1, to=100, orient="horizontal")

    # Audio codec dropbox + label UI components (initialize with empty value "---")
    ui["audio_codec_label"] = Label(tab, text="Select audio codec: ")
    ui["audio_codec_dropbox"] = ttk.Combobox(tab, values=["---", "aac", "flac", "mp3", "alac", "opus", "sbc", "aptx"])
    ui["audio_codec_dropbox"].bind("<<ComboboxSelected>>", on_audio_codec_selected)
    ui["audio_codec_dropbox"].set("---")

    # B Frames checkbox + label UI components
    ui["b_frames_checkbox_label"] = Label(tab, text="Enable B-Frames")
    ui["b_frames_checkbox"] = ttk.Checkbutton(tab, variable=b_frames_value)

    # Include text overlay checkbox + label UI components
    ui["include_text_overlay_label"] = Label(tab, text="Include text overlay")
    ui["include_text_overlay_checkbox"] = ttk.Checkbutton(tab, variable=include_text_overlay_value)

    # Status of conversion text UI component
    ui["convert_status_text"] = Label(tab, text="", anchor="w", width=50)
    ui["convert_status_text"].grid_remove()

    # Convert button UI component
    ui["convert_button"] = Button(tab, text="Convert video(s)", command=convert_videos)

# Event to handle when video compression is selected
def on_compression_selected(event):
    global selected_compression
    selected_compression = {"H264": "264", "H265": "265"}.get(ui["compression_dropbox"].get())
    # checks if convert button can appear
    will_convert_button_appear()

# Event to handle when color space is selected
def on_color_space_selected(event):
    global selected_color_space
    selected_color_space = {"4:2:0": "420", "4:2:2": "422", "4:4:4": "444"}.get(ui["color_space_dropbox"].get())
    # checks if convert button can appear
    will_convert_button_appear()

# Event to handle when audio codec is selected
def on_audio_codec_selected(event):
    global selected_audio_codec
    val = ui["audio_codec_dropbox"].get()
    selected_audio_codec = val if val != "---" else None
    # checks if convert button can appear
    will_convert_button_appear()

# Event to handle when user clears video paths list
def on_clear_path():
    global filepaths
    filepaths.clear()
    # Resets UI, clears list
    ui["file_list_text"].config(state='normal')
    ui["file_list_text"].delete("1.0", "end")
    ui["file_list_text"].config(state='disabled')
    ui["convert_button"].grid_remove()
    ui["clear_paths_button"].grid_remove()

# Checks if the convert button can display
# Can appear if:
# - Compression is selected and;
# - Color space is selected and;
# - Audio codec is selected
# - Filepaths contains at least one video
# Otherwise it can not display
def will_convert_button_appear():
    if selected_compression and selected_color_space and selected_audio_codec and len(filepaths) != 0:
        ui["convert_button"].grid(row=cv_row_index, column=0, columnspan=2, sticky=W, padx=10, pady=5)
    else:
        ui["convert_button"].grid_remove()

# Event to handle when user selects file(s)
def select_files():
    global filepaths
    # Opens file explorer for user to select video(s)
    video_file_path = list(filedialog.askopenfilenames(
        # Title of explorer window
        title="Select videos",
        # Opens in app location
        initialdir=".",
        # Supported filetypes for conversion
        filetypes=[("All files", "*.*"), ("MP4 Videos", "*.mp4"), ("MKV Videos", "*.mkv"), ("WebM Videos", "*.webm")]
    ))
    # If there are any videos
    if video_file_path:
        # If the video selected is in a supported format
        if os.path.splitext(video_file_path[0])[1][1:] in supported_formats:
            # Include selected video(s) to filepaths
            filepaths.extend(video_file_path)
            # Display selected files in the list
            display_selected_files()

# Event to handle when user selects a directory
def select_directory():
    global filepaths
    # Opens file explorer for user to select directory
    video_files_path = list(filedialog.askdirectory(
        # Title of explorer window
        title="Select videos",
        # Opens in app location
        initialdir="."
    ))
    # Joins the list of characters generated by above function call into a single string (reconstructing the original path)
    video_files_path = "".join(video_files_path)
    # If theres a path
    if video_files_path:
        # list of files
        files = []
        # for each path and file within that path:
        for root, _, filenames in os.walk(video_files_path):
            # for each file
            for filename in filenames:
                # generate a path for file
                generated_path = os.path.join(root, filename)
                # if file is in a supported format
                if os.path.splitext(filename)[1][1:] in supported_formats:
                    # add to list of files
                    files.append(generated_path)
        # Extend files into global filepaths
        filepaths.extend(files)
        # display selected files in the list
        display_selected_files()

# Event to handle displaying selected file(s)
def display_selected_files():
    global cv_row_index

    # Display list of paths
    ui["file_list_label"].grid(row=cv_row_index, column=0, columnspan=2, sticky='w', padx=10, pady=(10, 0))
    cv_row_index += 1

    # Display list of paths component, delete residing contents
    ui["file_list_text"].config(state='normal')
    ui["file_list_text"].delete('1.0', 'end')

    # For each path in global filepaths
    for path in filepaths:
        # Get downloaded video information
        info = DownloadedVideoInfo.get_video_info(path)
        # Get resolution + FPS of this video
        res = DownloadedVideoInfo.get_pretty_resolution(info.resolution[0], info.fps)
        # Add this video into UI list of files
        ui["file_list_text"].insert("end", f"• {os.path.basename(path)} ({res})\n")

    # Disable list of files, display it in the UI
    ui["file_list_text"].config(state='disabled')
    ui["file_list_text"].grid(row=cv_row_index, column=0, columnspan=2, sticky='w', padx=10, pady=(0, 10))
    cv_row_index += 1

    # For each UI component to be shown now that there is a list of files to convert
    for key in ["clear_paths_button", "compression_dropbox_label", "compression_dropbox", "color_space_dropbox_label",
                "color_space_dropbox", "bit_rate_scale_label", "bit_rate_scale", "audio_codec_label",
                "audio_codec_dropbox", "b_frames_checkbox_label", "b_frames_checkbox", "include_text_overlay_label", "include_text_overlay_checkbox"]:
        # Ff UI component is a label put it in the first column
        ui[key].grid(row=cv_row_index, column=0 if 'label' in key else 1, sticky=W, padx=10, pady=5)
        # If theres no label for that component, go to next row
        if 'label' not in key:
            cv_row_index += 1

    # Checks if convert button can appear
    will_convert_button_appear()

# Generates text overlay size for converted videos based on resolution height of video
# Args:
# - res_height: Resolution height of a video
def determine_overlay_text_size(res_height):
    for h, size in [(2160, 200), (1080, 100), (720, 75), (480, 50), (360, 30), (240, 15)]:
        if res_height == h:
            return size
    return 10

# Calculates Group of Pictures of a video based of FPS
# Args:
# - fps: Frames per second used to calculate GOC
def calculate_goc(fps):
    return int(fps * 1.5)

# Event used to handle conversion thread
def convert_videos():
    # Create + start the thread to convert
    thread = threading.Thread(target=_convert_videos_thread)
    thread.start()

# Function to convert video(s) (started via thread ^)
def _convert_videos_thread():
    # If theres no videos current at access to convert
    if not filepaths:
        print("No files selected")
        return

    # B Frames + include text overlay checkbox value
    b_frames = b_frames_value.get()
    include_text_overlay = include_text_overlay_value.get()
    # Bit rate value
    bit_rate = ui["bit_rate_scale"].get()

    # For each file in filepaths
    for path in filepaths:
        # Get downloaded video information on it
        info = DownloadedVideoInfo.get_video_info(path)
        # Get pretty resolution w/ FPS
        res_str = DownloadedVideoInfo.get_pretty_resolution(info.resolution[0], info.fps)
        # Get pretty resolution w/o FPS
        res_str_no_fps = DownloadedVideoInfo.get_pretty_resolution(info.resolution[0], info.fps, False)
        # Get overlay size based off resolution
        overlay_size = determine_overlay_text_size(info.resolution[0])

        # Convert input file path (string) to a Path object
        input_path = Path(path)
        # Generate output filename based on parameters
        out_name = f"{'BF_' if b_frames else ''}{input_path.stem}_{res_str}_H{selected_compression}_{bit_rate}bits{input_path.suffix}"
        # Create a new Path object for the output file in the same directory as the input file, using the generated filename
        output_path = input_path.with_name(out_name)

        # Video format options
        vf = (
            f"format=yuv{selected_color_space}p"
            + (
                f",drawtext=fontfile=InfiniteBeyond.ttf:text='{res_str}     H{selected_compression}     {selected_color_space}     {bit_rate} bits':fontcolor=white:fontsize={overlay_size}:x=(w-text_w)/2:y=25"
                if include_text_overlay else ""
            )
        )

        # If B Frames were enabled
        if b_frames:
            # Add additional video format option which includes text overlay for B Frames to video
            vf += (f",drawtext=fontfile=InfiniteBeyond.ttf:text='B-Frames':fontcolor=red:"
                   f"fontsize={overlay_size}:x=(w-text_w)/2:y=h-text_h-25")
            
        # Command list used to run ffmpeg operations to convert video(s)
        cmd = ["ffmpeg",
               "-i", str(input_path), # -i: Input (current file (path))
               "-acodec", selected_audio_codec, # -acodec: Audio codec
               "-c:v", f"libx{selected_compression}", # -c:v: Compression algo
               "-g", str(calculate_goc(info.fps)), # -g: GOC
               "-b:v", f"{bit_rate}M", # -b:v: Bit rate
               "-bf", "0", # -bf: B Frames
               "-ac", "2", # -ac: Audio channels
               "-vf", vf, # -vf: filtergraph
               str(output_path)] # output path

        # If B Frames were enabled
        if b_frames:
            # Remove commands from command list to disabled B Frames (which default to not including B Frames)
            cmd.pop(11)  # remove "-bf"
            cmd.pop(11)  # remove "0"

        # Display conversion status text UI component
        ui["convert_status_text"].grid()
        ui["convert_status_text"].config(text="Converting...", foreground="orange")
        # Run the command
        subprocess.run(cmd, check=True)

        # Generate target directory location for final converted video using:
        # - "converted"
        # - selected conversion algo (ex: H265)
        # - non-FPS resolution (ex: 4K)
        # - FPS (ex: 60)
        target_dir = os.path.join("converted", f"H{selected_compression}", res_str_no_fps, str(info.fps)) if not b_frames else os.path.join("converted", f"H{selected_compression}", res_str_no_fps, str(info.fps), "BFrames")
        # Creates the target directory (if it exists already, ignore re-creation)
        os.makedirs(target_dir, exist_ok=True)
        # Move the converted video to the target directory followed by its filename
        shutil.move(output_path, os.path.join(target_dir, os.path.basename(output_path)))

    # Update conversion status text to notify user that conversion was successful
    ui["convert_status_text"].config(text=f"Successfully converted {len(filepaths)} video(s)!", foreground="green")
