import os
import sys
from tkinter import W, Button, Entry, Label, Scale, Text, ttk
import customtkinter as ctk

from src.types.enums.color import LabelColor

BASE_APP_DIR = None

if getattr(sys, "frozen", False):
    BASE_APP_DIR = os.path.dirname(sys.executable)
else:
    BASE_APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

BASE_APP_DIR = os.path.normpath(BASE_APP_DIR)

def resource_path(relative_path):
    import sys
    import os

    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def get_proxy():
    import os, json

    config_path = resource_path("proxy.config.json")

    if os.path.exists(config_path):
        try:
            with open(config_path, "r") as f:
                data = json.load(f)
                return data.get("proxy", "")
        except:
            return ""
    return ""
    
def to_mb(bytes):
    return f"{bytes / 1_000_000:.2f}Mb" if bytes else "n/a"

def create_label(parent, text, **kwargs):
    if "text_color" in kwargs and hasattr(kwargs["text_color"], 'value'):
        kwargs["text_color"] = kwargs["text_color"].value

    return ctk.CTkLabel(parent, text=text, **kwargs)

def create_entry(parent, **kwargs):
    return ctk.CTkEntry(parent, **kwargs)

def create_button(parent, text, command, **kwargs):
    return ctk.CTkButton(parent, text=text, command=command, **kwargs)

def create_text(frame, height=6, width=70, wrap="word", state="normal"):
    return Text(frame, height=height, width=width, wrap=wrap, state=state)

def create_combobox(parent, command=None, **kwargs):
    return ctk.CTkComboBox(parent, command=command, **kwargs)

def create_scale(frame, from_=1, to=100, orient="horizontal"):
    return Scale(frame, from_=from_, to=to, orient=orient)

def create_checkbutton(frame, variable):
    return ttk.Checkbutton(frame, variable=variable)

def edit_label_text(label, new_text, text_color=LabelColor.WHITE, wraplength=500):
    label.configure(
        text=new_text,
        text_color=text_color.value if hasattr(text_color, 'value') else text_color,
        wraplength=wraplength
    )

def change_text_widget_state(widget, state):
    widget.configure(state=state)

def update_combobox_values(combobox, new_values):
    combobox.configure(values=new_values)

def add_to_text_widget(text_widget, text):
    text_widget.insert("end", text)

def add_widget_to_grid(widget, row=0, column=0, padx=10, pady=5, columnspan=1, sticky="w"):
    widget.grid(row=row, column=column, padx=padx, pady=pady, columnspan=columnspan, sticky=sticky)

def set_combobox_value(combobox, value):
    combobox.set(value)

def remove_widget_from_grid(widget):
    if widget != None:
        widget.grid_remove()
        widget = None

def open_folder(path):
    os.startfile(path)

# Compression constants
SUPPORTED_COMPRESSION = [ "H264", "H265" ]
SUPPORTED_COLOR_SPACE = [ "4:4:4", "4:2:2", "4:2:0" ]
SUPPORTED_AUDIO_CODEC = [ "aac", "flac", "mp3", "alac", "opus", "sbc", "aptx" ]
SUPPORTED_VIDEO_FORMAT = [ "mp4" ]

# Scaling constants
SCALES = [ "1280x720", "1920x1080", "3840x2160", "7680x4230" ]
REFRESH_RATES = [ 25, 30, 50, 60 ]