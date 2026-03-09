import os
import sys
from tkinter import Frame, Tk, ttk

from src.frames.convert.convert import set_convert_frame_components
from src.frames.download.download import set_download_frame_components
from src.frames.scale.scale import set_scale_frame_components

download_frame = None
convert_frame = None
scale_frame = None

def main():
    global download_frame, convert_frame, scale_frame
    
    root = Tk()
    root.title("ServerVideoCreator")
    root.geometry("1000x700")

    notebook = ttk.Notebook(root)
    notebook.pack(fill="both", expand=True)

    download_frame = Frame(notebook)
    notebook.add(download_frame, text="Download")
    set_download_frame_components(download_frame)

    convert_frame = Frame(notebook)
    notebook.add(convert_frame, text="Convert")
    set_convert_frame_components(convert_frame)

    scale_frame = Frame(notebook)
    notebook.add(scale_frame, text="Scale")
    set_scale_frame_components(scale_frame)

    root.mainloop()

if __name__ == "__main__":
    main()