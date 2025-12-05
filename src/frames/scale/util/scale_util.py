from src.frames.scale.scale_ui import SCALE_UI


def inc_scale_frame_row_index():
    SCALE_UI["scale_frame_row_index"] += 1

def format_resolution(resolution):
    return f"{resolution[0]}x{resolution[1]}"