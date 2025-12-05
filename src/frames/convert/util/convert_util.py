from src.frames.convert.convert_ui import CONVERT_UI


def inc_convert_frame_row_index():
    CONVERT_UI["convert_frame_row_index"] += 1

def determine_overlay_text_size(resolution):
    try:
        parsed_resolution = int(resolution.replace("p", ""))
    except Exception:
        parsed_resolution = resolution

    for h, size in [("4K", 200), (1440, 150), ("HD", 100), (720, 75), (480, 50), (360, 30), (240, 15)]:
        if parsed_resolution == h:
            return size
    return 10

def calculate_gop(fps):
    return int(fps * 1.5)

def format_color_space_for_conversion(color_space):
    return color_space.replace(":", "")

def format_compression_for_conversion(compression):
    return compression.replace("H", "")

def on_clear_path_button_click():
    print("deleting")