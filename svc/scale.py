import os
from tkinter import W, Button, Label, filedialog

from svc.models.video_info import DownloadedVideoInfo

video_file_path = None
scale_tab_ref = None
sc_row_index = 0

def_ui = lambda: {
    "select_video_button": None,
    "selected_video_title": None,
    "selected_video_resolution": None
}

ui = def_ui()

def setup_scale_tab(tab):
    global scale_tab_ref, sc_row_index, ui

    scale_tab_ref = tab
    ui.update(def_ui())

    ui["select_video_button"] = Button(tab, text="Select video to scale", command=on_video_select_click)
    ui["select_video_button"].grid(row=sc_row_index, column=0, sticky=W, padx=10, pady=5)
    sc_row_index += 1

def on_video_select_click():
    global video_file_path, sc_row_index, scale_tab_ref

    video_file_path = filedialog.askopenfilename(
        title="Select video",
        filetypes=[("All files", "*.*"), ("MP4 Videos", "*.mp4"), ("MKV Videos", "*.mkv"), ("WebM Videos", "*.webm")]
    )

    if video_file_path:
        info = DownloadedVideoInfo.get_video_info(video_file_path)
        res = DownloadedVideoInfo.get_pretty_resolution(info.resolution[0], info.fps)
        
        ui["selected_video_title"] = Label(scale_tab_ref, text=f"Selected video: {os.path.basename(video_file_path)}")
        ui["selected_video_title"].grid(row=sc_row_index, column=0, sticky=W, padx=10)
        sc_row_index += 1

        ui["selected_video_resolution"] = Label(scale_tab_ref, text=f"Resolution: {res}")
        ui["selected_video_resolution"].grid(row=sc_row_index, column=0, sticky=W, padx=10)