from pathlib import Path
import subprocess
from tkinter import W, Button, filedialog


convert_tab_ref = None
cv_row_index = 0
select_files_button = None

def setup_convert_tab(tab):
    global convert_tab_ref, cv_row_index, select_files_button

    convert_tab_ref = tab
    cv_row_index = 0

    select_files_button = Button(tab, text="Select files to convert", command=select_files)
    select_files_button.grid(row=cv_row_index, column=0, columnspan=2, sticky=W, padx=10, pady=5)
    cv_row_index += 1

def select_files():
    filepaths = filedialog.askopenfilenames(
        title="Select videos",
        initialdir=Path.home(),
        filetypes=[
            ("All files", "*.*")
        ]
    )
    if filepaths:
        for path in filepaths:
            input_path = Path(path)
            output_path = input_path.with_name(f"{input_path.stem}_{"4K60"}_{"H264"}_{20}bits{input_path.suffix}")

            vf_filter = f"format=yuv{420}p,drawtext=fontfile=InfiniteBeyond.ttf:text='{"4K60"}     {"H264"}     {420}     {20} bits':fontcolor=white:fontsize=200:x=(w-text_w)/2:y=25"

            command = [
                "ffmpeg",
                "-i", str(path),
                "-acodec", "aac",
                "-c:v", f"libx26{4}",
                "-g", "90",
                "-b:v", f"{20}M",
                "-bf", f"{0}",
                "-ac", "2",
                "-vf", vf_filter,
                str(output_path)
            ]

            subprocess.run(command, check=True)
    else:
        print("No files selected")