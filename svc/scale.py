import os
import shutil
from tkinter import W, Button, Label, filedialog, ttk

import ffmpeg

from svc.models.scales import REFRESH_RATES, SCALES
from svc.models.video_info import DownloadedVideoInfo
from svc.util import SUPPORTED_FORMATS

video_file_path = None
video_original_resolution = None
scale_tab_ref = None
sc_row_index = 0
selected_scale = None
selected_refresh_rate = None

def_ui = lambda: {
    "select_video_button": None,
    "selected_video_title": None,
    "selected_video_resolution": None,
    "scale_to_label": None,
    "scale_to_combobox": None,
    "refresh_rate_label": None,
    "refresh_rate_combobox": None,
    "scale_button": None,
    "scaling_status": None
}

ui = def_ui()

def setup_scale_tab(tab):
    global scale_tab_ref, sc_row_index, ui

    scale_tab_ref = tab
    ui.update(def_ui())  # Update UI

    ui["select_video_button"] = Button(tab, text="Select video to scale", command=on_video_select_click)
    ui["select_video_button"].grid(row=sc_row_index, column=0, sticky=W, padx=10, pady=5)
    sc_row_index += 1

def on_video_select_click():
    global video_file_path, video_original_resolution, sc_row_index, scale_tab_ref

    reset_scale_ui(video_info_components=True, scale_components=True, refresh_rate_components=True, scaling_status_components=True)

    video_file_path = filedialog.askopenfilename(
        title="Select video",
        filetypes=[("All files", "*.*"), ("MP4 Videos", "*.mp4"), ("MKV Videos", "*.mkv"), ("WebM Videos", "*.webm")]
    )

    if video_file_path:
        info = DownloadedVideoInfo.get_video_info(video_file_path)
        video_original_resolution = format_resolution(info.resolution)
        res = DownloadedVideoInfo.get_pretty_resolution(info.resolution[0], info.fps)
        
        ui["selected_video_title"] = Label(scale_tab_ref, text=f"Selected video: {os.path.basename(video_file_path)}")
        ui["selected_video_title"].config(underline=True)
        ui["selected_video_title"].grid(row=sc_row_index, column=0, sticky=W, padx=10)
        sc_row_index += 1

        ui["selected_video_resolution"] = Label(scale_tab_ref, text=f"Resolution: {res}")
        ui["selected_video_resolution"].grid(row=sc_row_index, column=0, sticky=W, padx=10)
        sc_row_index += 1

        ui["scale_to_label"] = Label(scale_tab_ref, text="Scale to ")
        ui["scale_to_label"].grid(row=sc_row_index, column=0, sticky=W, padx=10)
        sc_row_index += 1

        ui["scale_to_combobox"] = ttk.Combobox(scale_tab_ref, values=[f for f in SCALES if f != video_original_resolution])
        ui["scale_to_combobox"].bind("<<ComboboxSelected>>", on_scale_selected)
        ui["scale_to_combobox"].grid(row=sc_row_index, column=0, sticky=W, padx=10)
        sc_row_index += 1

def on_scale_selected(e):
    global selected_scale, scale_tab_ref, sc_row_index

    reset_scale_ui(scale_components=False, refresh_rate_components=True, scaling_status_components=True)

    selected_scale = ui["scale_to_combobox"].get()

    # Show the refresh rate controls
    ui["refresh_rate_label"] = Label(scale_tab_ref, text="with Refresh rate ")
    ui["refresh_rate_label"].grid(row=sc_row_index, column=0, sticky=W, padx=10)
    sc_row_index += 1

    ui["refresh_rate_combobox"] = ttk.Combobox(scale_tab_ref, values=[r for r in REFRESH_RATES])
    ui["refresh_rate_combobox"].bind("<<ComboboxSelected>>", on_refresh_rate_selected)
    ui["refresh_rate_combobox"].grid(row=sc_row_index, column=0, sticky=W, padx=10)
    sc_row_index += 1

def on_refresh_rate_selected(e):
    global selected_refresh_rate, scale_tab_ref, sc_row_index

    reset_scale_ui(scale_components=False, refresh_rate_components=False, scaling_status_components=True)

    selected_refresh_rate = ui["refresh_rate_combobox"].get()
    ui["scale_button"] = Button(scale_tab_ref, text="Scale", command=on_scale_button_click)
    ui["scale_button"].grid(row=sc_row_index, column=0, sticky=W, padx=10, pady=20)
    sc_row_index += 1

def on_scale_button_click():
    global scale_tab_ref

    ui["scaling_status"] = Label(scale_tab_ref, text="Scaling...")
    ui["scaling_status"].config(fg="#FFA500")
    ui["scaling_status"].grid(row=sc_row_index, column=0, sticky=W, padx=10, pady=5)

    video_file_name = os.path.basename(video_file_path)

    ffmpeg.input(video_file_path).output(os.path.join(".", video_file_name), vf=f"scale={selected_scale}:flags=lanczos", r=selected_refresh_rate).run()
    move_video_to_folder(video_file_name)

    ui["scaling_status"].config(fg="#00FF00", text="Scaling complete!")
    ui["scaling_status"].grid(row=sc_row_index, column=0, sticky=W, padx=10, pady=5)

def move_video_to_folder(title):
    global video_file_path

    scaled_video_file = next((f for f in os.listdir(os.path.join(".")) if f == title))

    if not scaled_video_file:
        ui["scaling_status"].config(text="File not found", fg="#FF0000")
        return
    
    info = DownloadedVideoInfo.get_video_info(scaled_video_file)
    if not info:
        ui["scaling_status"].config(text="Could not extract video info", fg="#FF0000", wraplength=100)
        return
    
    res = DownloadedVideoInfo.get_pretty_resolution(info.resolution[0], info.fps, include_fps=False)

    target_folder = os.path.join("scaled", res, str(info.fps))

    os.makedirs(target_folder, exist_ok=True)

    shutil.move(scaled_video_file, os.path.join(target_folder, os.path.basename(scaled_video_file)))
    scaled_video_file = os.path.join(target_folder, os.path.basename(scaled_video_file))

def reset_scale_ui(video_info_components=False, scale_components=False, refresh_rate_components=False, scaling_status_components=False):
    global video_file_path, video_original_resolution, sc_row_index, selected_scale, selected_refresh_rate

    # Reset video components
    if video_info_components and video_file_path is not None:
        video_file_path = None
        video_original_resolution = None
        sc_row_index = 0
        if ui["select_video_button"] is not None:
            ui["select_video_button"].grid_remove()
        if ui["selected_video_title"] is not None:
            ui["selected_video_title"].grid_remove()
        if ui["selected_video_resolution"] is not None:
            ui["selected_video_resolution"].grid_remove()

    # Reset scale components if needed, but keep the scale combobox visible
    if scale_components and (ui["scale_to_label"] is not None or ui["scale_to_combobox"] is not None):
        selected_scale = None
        if ui["scale_to_label"] is not None:
            ui["scale_to_label"].grid_remove()
        if ui["scale_to_combobox"] is not None:
            ui["scale_to_combobox"].grid_remove()

    # Reset refresh rate components if needed, but keep the scale combobox visible
    if refresh_rate_components and (ui["refresh_rate_label"] is not None or ui["refresh_rate_combobox"] is not None):
        selected_refresh_rate = None
        if ui["refresh_rate_label"] is not None:
            ui["refresh_rate_label"].grid_remove()
        if ui["refresh_rate_combobox"] is not None:
            ui["refresh_rate_combobox"].grid_remove()

    # Reset scaling status components
    if scaling_status_components and (ui["scale_button"] is not None or ui["scaling_status"] is not None):
        if ui["scale_button"] is not None:
            ui["scale_button"].grid_remove()
        if ui["scaling_status"] is not None:
            ui["scaling_status"].grid_remove()

def format_resolution(resolution):
    return f"{resolution[1]}x{resolution[0]}"
