import os
import re
import shutil
import threading
from tkinter import W, Button, Label, Entry, Toplevel, ttk
import yt_dlp

from svc.models.audio import Audio
from svc.models.video import Video
from svc.models.video_info import DownloadedVideoInfo
from svc.util import open_folder, to_mb, yt_fetch_video_info, get_proxy, supported_formats

# UI and state references
download_tab_ref = None
video_url = ""
video_formats = []
audio_formats = []
is_video_selected = False
is_audio_selected = False
downloaded_video_path = None

# Defines blank UI components
def_ui = lambda: {
    "url_entry": None,
    "get_info_button": None,
    "fetched_video_info_text": None,
    "resolutions_combobox": None,
    "resolution_label": None,
    "audio_combobox": None,
    "audio_label": None,
    "download_button": None,
    "download_status_text": None,
    "open_folder_button": None
}

ui = def_ui()

# Setup for UI elements. Hides most elements and will reveal them as application is used
# Args:
# - tab: Tkinter tab (used for frames for notebooks)
def setup_download_tab(tab):
    global download_tab_ref, ui
    download_tab_ref = tab
    # Update UI to be blank
    ui.update(def_ui())

    # YouTube URL entry UI component
    Label(tab, text="Enter YouTube URL:").grid(row=0, column=0, sticky=W, padx=10, pady=5)
    ui["url_entry"] = Entry(tab, width=100)
    ui["url_entry"].grid(row=0, column=1, padx=10, pady=5)

    # Get info UI component
    ui["get_info_button"] = Button(tab, text="Get Info", command=generate_resolutions)
    ui["get_info_button"].grid(row=1, column=0, sticky=W, padx=10, pady=5)

    # YouTube video fetched information text UI component
    ui["fetched_video_info_text"] = Label(tab, text="", anchor="w", justify="left")
    ui["fetched_video_info_text"].grid_remove()

    # Resolution formats label + combobox UI components
    ui["resolutions_combobox"] = ttk.Combobox(tab, values=["---"], width=50)
    ui["resolutions_combobox"].bind("<<ComboboxSelected>>", on_resolution_selected)
    ui["resolutions_combobox"].grid(row=3, column=1, sticky=W, padx=10, pady=5)
    ui["resolutions_combobox"].grid_remove()
    ui["resolution_label"] = Label(tab, text="", anchor="w", width=50)
    ui["resolution_label"].grid(row=4, column=0, columnspan=2, sticky=W, padx=10, pady=5)

    # Audio formats label + combobox UI components
    ui["audio_combobox"] = ttk.Combobox(tab, values=["---"], width=50)
    ui["audio_combobox"].bind("<<ComboboxSelected>>", on_audio_selected)
    ui["audio_combobox"].grid(row=5, column=1, sticky=W, padx=10, pady=5)
    ui["audio_combobox"].grid_remove()
    ui["audio_label"] = Label(tab, text="", anchor="w", width=50)
    ui["audio_label"].grid(row=6, column=0, columnspan=2, sticky=W, padx=10, pady=5)

    # Download button UI component
    ui["download_button"] = Button(tab, text="Download", command=download_video)
    ui["download_button"].grid(row=7, column=0, columnspan=2, sticky=W, padx=10, pady=5)
    ui["download_button"].grid_remove()

    # Download status UI component
    ui["download_status_text"] = Label(tab, text="", anchor="w", width=50)
    ui["download_status_text"].grid(row=8, column=0, columnspan=2, sticky=W, padx=10, pady=5)
    ui["download_status_text"].grid_remove()

    # Open containing folder button UI component
    ui["open_folder_button"] = Button(tab, text="Open Containing Folder", command=lambda: open_folder(downloaded_video_path))
    ui["open_folder_button"].grid(row=9, column=0, columnspan=2, sticky=W, padx=10, pady=5)
    ui["open_folder_button"].grid_remove()

# Event to handle resolution generation
def generate_resolutions():
    global video_url, video_formats, is_video_selected

    # Resets UI
    reset_download_ui()

    # If there is not URL supplied in the URL entry
    if not ui["url_entry"].get():
        # Escape
        return

    # Retrieve YouTube URL from entry
    video_url = ui["url_entry"].get()
    # Get video information from URL
    video_info = yt_fetch_video_info(video_url)

    # Clear any existing video formats
    video_formats.clear()
    # Append empty value
    video_formats.append("---")

    # For each format in video information formats
    for fmt in video_info.get("formats", []):
        # If there is no exising video codec for the current format
        if fmt.get("vcodec") == "none":
            continue

        # Resolution of current format
        resolution = f"{fmt.get('width', '?')}x{fmt.get('height', '?')}"
        # Frames per second of current format
        fps = f"{int(fmt.get('fps', 0))}" if fmt.get("fps") else "n/a"

        # Add Video object to list of video formats
        video_formats.append(Video(fmt.get("format_id"), resolution, fps, fmt.get("protocol"), fmt.get("ext")))

    # Add format to combobox options
    ui["resolutions_combobox"].config(values=["---"] + [
        f"({vf.id}) {vf.resolution} {vf.fps} {vf.extension} via {vf.protocol}" for vf in video_formats[1:]
    ])
    ui["resolutions_combobox"].set("---")
    ui["resolutions_combobox"].grid()
    ui["resolution_label"].config(text="No resolution selected!")

    # Generate audio
    generate_audio(video_info)

    # Get title from video
    title = video_info.get("title", "Unknown title")
    # Get duration of video
    duration = video_info.get("duration_string") or video_info.get("duration") or "Unknown duration"

    # Set video information text to use above values
    ui["fetched_video_info_text"].config(text=f"Title: {title}\nDuration: {duration}", foreground="black")
    ui["fetched_video_info_text"].grid(row=2, column=0, columnspan=2, sticky=W, padx=10, pady=5)

# Event to handle audio generation
def generate_audio(video_info):
    global audio_formats

    # Clear any existing formats
    audio_formats.clear()
    # Append empty value
    audio_formats.append("---")

    # For each format in audio information formats
    for fmt in video_info.get("formats", []):
        # If format is audio
        if fmt.get("resolution") == "audio only":
            try:    
                # Add a new Audio object with current format information
                audio_formats.append(Audio(fmt["format_id"], fmt["ext"], fmt["protocol"], fmt.get("asr"), fmt.get("filesize")))
            # If any of the keys used to create the Audio object aren't existent in the current format
            except KeyError:
                # Skip it
                continue
    
    # Add format to combobox options
    ui["audio_combobox"].config(values=["---"] + [
        f"({af.id}) {af.extension} via {af.protocol} at {af.asr or 'n/a'}Hz ~{to_mb(af.filesize)}"
        for af in audio_formats[1:]
    ])
    ui["audio_combobox"].set("---")
    ui["audio_combobox"].grid()
    ui["audio_label"].config(text="No audio selected!")

# Event used to handle when a resolution is selected
def on_resolution_selected(event):
    global is_video_selected

    # Get current selected resolution
    selected = ui["resolutions_combobox"].get()
    is_video_selected = selected != "---"
    # Updates the resolution label with the current resolution (if a vaild one was selected)
    ui["resolution_label"].config(text=f"Selected resolution: {selected}" if is_video_selected else "No resolution selected")
    # Checks if the download button can be displayed
    check_video_audio_selection()

# Event used to handle when an audio is selected
def on_audio_selected(event):
    global is_audio_selected

    # Get current selected audio
    selected = ui["audio_combobox"].get()
    is_audio_selected = selected != "---"
    # Updates the audio label with the current audio (if a valid one was selected)
    ui["audio_label"].config(text=f"Selected audio: {selected}" if is_audio_selected else "No audio selected")
    # Checks if the download button can be displayed
    check_video_audio_selection()

# Checks if the download button can be displayed and used
# Can only be displayed if:
# - A valid video format is selected and;
# - A valid audio format is selected and;
# - A URL is supplied in the entry field
def check_video_audio_selection():
    if is_video_selected and is_audio_selected and (len(video_url) != 0 or video_url is not None):
        ui["download_button"].grid()
    else:
        ui["download_button"].grid_remove()

# Event used to handle download thread
def download_video():
    thread = threading.Thread(target=_download_video_thread)
    thread.start()

# Function to download video (started via thread ^)
def _download_video_thread():
    # Get video and audio format
    video_format, audio_format = get_format_from_format_string()
    try:
        # Display download status text, remove open folder button 
        ui["download_status_text"].grid()
        ui["download_status_text"].config(text="Downloading...", foreground="orange")
        ui["open_folder_button"].grid_remove()

        # Get YouTube video information video supplied URL
        yt_info = yt_fetch_video_info(video_url)
        # Ensure title from video has only valid characters
        title = re.sub(r'[^A-Za-z0-9]', '', yt_info.get("title", "video"))
        # YDL options
        ydl_opts = {
            "format": f"{video_format.id}+{audio_format.id}",
            "outtmpl": f"{title}.%(ext)s",
            "restrictfilenames": True
        }

        # Get proxy information
        proxy = get_proxy()
        # If a proxy value is retrieved
        if proxy:
            # Add it to YDL options
            ydl_opts["proxy"] = proxy

        # Open YDL operation
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Download video via URL to current working location
            ydl.download([video_url])

        # Gets renamed video title
        renamed_title = open_title_window(title)
        # Move video to respective location
        move_video_to_folder(title, renamed_title=renamed_title)

        # Update download status and display open folder button
        ui["download_status_text"].config(text="Downloaded successfully", foreground="green")
        ui["open_folder_button"].grid()
    except Exception as e:
        ui["download_status_text"].config(text=f"Download error: {e}", foreground="red", wraplength=200)

# Function used to open a window for the user to rename the downloaded video
# Args:
# - original_title: The original title of the video
def open_title_window(original_title):
    # dictionary which holds the value of the final title for the video to be named
    final_title = {"result": original_title}

    # Renaming video window object creation
    new_window = Toplevel(download_tab_ref)
    # Renaming video window title
    new_window.title("Set Video Title")
    # Renaming video window size
    new_window.geometry("700x200")

    # Label and entry UI components for video title naming
    Label(new_window, text="Enter title for downloaded video (no extension):").grid(row=0, column=0)
    new_title_entry = Entry(new_window, width=60)
    new_title_entry.insert(0, original_title)
    new_title_entry.grid(row=0, column=1)

    # Local event used to confirm the title entry
    def confirm_title():
        # Gets entered value for video title
        new_title = new_title_entry.get().strip()
        # If theres a title
        if new_title:
            # Sanitize the title to have only valid characters
            sanitized = re.sub(r'[^A-Za-z0-9]', '', new_title)
            # If sanitized value is present
            if sanitized:
                # Update the final result of the title to be this new sanitized title
                final_title["result"] = sanitized
            # otherwise
            else:
                # Keep the original title
                final_title["result"] = original_title
        # Destroy the window
        new_window.destroy()

    # Add a button to confirm the selection
    Button(new_window, text="Confirm", command=confirm_title).grid(row=1, sticky=W)

    # Ensure that the main window can not be interacted with while this one is up
    new_window.grab_set()
    # Wait for the new window to be closed before continuing interaction with it
    download_tab_ref.wait_window(new_window)

    # Return final title
    return final_title['result']

# Function used to move a video (via the title) to its respective location
# Args:
# - title: Video title used to move to respective location
# - **kwargs: Possible arguments:
#             - renamed_title: The title to use for the originating file and rename it to this
def move_video_to_folder(title, **kwargs):
    global downloaded_video_path

    # Retrieves the first downloaded video from current working location using the title, query using the supported video formats
    downloaded_file = next((f"{title}.{ext}" for ext in supported_formats if os.path.exists(f"{title}.{ext}")), None)
    # If there is no downloaded video found with the same title and extension
    if not downloaded_file:
        # Update UI mentioning no video found, escape
        ui["download_status_text"].config(text="Downloaded file not found", foreground="red")
        return

    # Get information on downloaded video
    info = DownloadedVideoInfo.get_video_info(downloaded_file)
    # If there is not information found on this video
    if not info:
        # Update UI mentioning there was no way to extract the information, escape
        ui["download_status_text"].config(text="Could not extract video info", foreground="red", wraplength=100)
        return

    # Get downloaded video resolution
    res = DownloadedVideoInfo.get_pretty_resolution(info.resolution[0], info.fps, include_fps=False)
    
    # Generate target folder location for video using the:
    # - video resolution
    # - and frames per second
    target_folder = os.path.join("raw", res, str(info.fps))
    # Create the directories, ignores if its already created
    os.makedirs(target_folder, exist_ok=True)

    # Renamed title supplied by additional arguments
    renamed_title = kwargs.get("renamed_title")
    # If a value for a new title is present and is not the same as the original
    if renamed_title and renamed_title != title:
        # Get the extension of the downloaded file
        _, ext = os.path.splitext(downloaded_file)
        # Appends the extention to the renamed title
        renamed_title += ext
        # Renames the original file with this new renamed title
        os.rename(downloaded_file, renamed_title)
        # Set the downloaded file to the new renamed title
        downloaded_file = renamed_title

    # Move the downloaded file to the target directory followed by its filename
    shutil.move(downloaded_file, os.path.join(target_folder, os.path.basename(downloaded_file)))
    # Update the downloaded video path, set it to its target folder
    downloaded_video_path = target_folder

# Function used to get the video and audio format from the current selected options from each respective combobox
def get_format_from_format_string():
    # Current video format
    selected_video = ui["resolutions_combobox"].get()
    # Current audio format
    selected_audio = ui["audio_combobox"].get()

    # Gets the first video format based off the value of the combobox option
    video = next((vf for vf in video_formats if vf != "---" and
                  f"({vf.id}) {vf.resolution} {vf.fps} {vf.extension} via {vf.protocol}" == selected_video), None)
    # Gets the first audio format based off the value of the combobox option
    audio = next((af for af in audio_formats if af != "---" and
                  f"({af.id}) {af.extension} via {af.protocol} at {af.asr or 'n/a'}Hz ~{to_mb(af.filesize)}" == selected_audio), None)

    # Return video and audio formats
    return video, audio

# Function used to reset the download UI components
def reset_download_ui():
    global is_video_selected, is_audio_selected
    
    # Clear video and audio format listts
    video_formats.clear()
    audio_formats.clear()
    
    # Update selected video and audio formats to False
    is_video_selected = False
    is_audio_selected = False

    # Remove download status text, download and open folder button UI components
    ui["download_button"].grid_remove()
    ui["download_status_text"].grid_remove()
    ui["open_folder_button"].grid_remove()
