import customtkinter as ctk

from src.frames.convert.convert import set_convert_frame_components
from src.frames.download.download import set_download_frame_components
from src.frames.scale.scale import set_scale_frame_components

download_frame = None
convert_frame = None
scale_frame = None

def main():
    global download_frame, convert_frame, scale_frame

    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    
    root = ctk.CTk()
    root.title("ServerVideoCreator")
    root.geometry("1000x700")

    tabview = ctk.CTkTabview(root, width=950, height=650)
    tabview.pack(padx=20, pady=20, fill="both", expand=True)

    download_tab = tabview.add("Download")
    convert_tab = tabview.add("Convert")
    scale_tab = tabview.add("Scale")

    set_download_frame_components(download_tab)
    set_convert_frame_components(convert_tab)
    set_scale_frame_components(scale_tab)

    root.mainloop()

if __name__ == "__main__":
    main()