import os
from tkinter import W, Button, Entry, Label, Text, ttk

from src.types.enums.color import LabelColor


def get_proxy():
    import os, json

    base_path = os.path.abspath(".")

    config_path = os.path.join(base_path, "proxy.config.json")
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            data = json.load(f)
            return data.get("proxy", "")
        
    else:
        return ""
    
def to_mb(bytes):
    return f"{bytes / 1_000_000:.2f}Mb" if bytes else "n/a"

def create_label(frame, text="", foreground=LabelColor.BLACK):
    return Label(frame, text=text, foreground=foreground)

def create_entry(frame, width=75):
    return Entry(frame, width=width)

def create_button(frame, text, command):
    return Button(frame, text=text, command=command)

def create_text(frame, height=6, width=70, wrap="word", state="normal"):
    return Text(frame, height=height, width=width, wrap=wrap, state=state)

def create_combobox(frame, width=40, command=lambda: None):
    combobox = ttk.Combobox(frame, width=width)
    combobox.bind("<<ComboboxSelected>>", command)
    return combobox

def edit_label_text(label, new_text, foreground=LabelColor.BLACK, wraplength=500):
    label.config(text=new_text, foreground=foreground, wraplength=wraplength)

def update_combobox_values(combobox, new_values):
    combobox.config(values=new_values)

def add_to_text_widget(text_widget, text):
    text_widget.insert("end", text)

def add_widget_to_grid(widget, row=0, column=0, padx=10, pady=5, columnspan=1):
    widget.grid(row=row, column=column, padx=padx, pady=pady, sticky=W, columnspan=columnspan)

def remove_widget_from_grid(widget):
    if widget != None:
        widget.grid_remove()

def open_folder(path):
    os.startfile(path)