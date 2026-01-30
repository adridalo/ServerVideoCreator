import yt_dlp
from src.frames.download.download_ui import DOWNLOAD_UI
from src.types.models.raw_audio_format_info import RawAudioFormatInfo
from src.types.models.raw_video_format_info import RawVideoFormatInfo
from src.util import get_proxy


def inc_download_frame_row_index():
    DOWNLOAD_UI["download_frame_row_index"] += 1

def yt_dlp_fetch_video_info(url):
    if url is None or len(url) == 0:
        return
    
    yt_dlp_options = {
        "listformats": True,
        "quiet": True,
        "forcejson": True,
        "dump_single_json": True,
        "cookiefile": 'cookies.txt'
    }

    if get_proxy() != "":
        yt_dlp_options["proxy"] = get_proxy()

    with yt_dlp.YoutubeDL(params=yt_dlp_options) as ydl:
        video_info = ydl.extract_info(url, download=False)
        return video_info
    
def get_video_formats_from_video_info(video_info):
    video_formats = []
    
    for fmt in video_info.get("formats", []):
        if fmt.get("vcodec") == "none":
            continue

        resolution = f"{fmt.get("width", "?")}x{fmt.get("height", "?")}"
        fps = f"{int(fmt.get("fps", 0))}" if fmt.get("fps") else "n/a"

        video_formats.append(RawVideoFormatInfo(
            fmt.get("format_id"), 
            resolution, 
            fps, 
            fmt.get("protocol"), 
            fmt.get("ext")
        ))

    return video_formats

def get_audio_formats_from_video_info(video_info):
    audio_formats = []

    for fmt in video_info.get("formats", []):
        if fmt.get("resolution") == "audio only":
            try:
                audio_formats.append(RawAudioFormatInfo(
                    fmt["format_id"],
                    fmt["ext"],
                    fmt["protocol"],
                    fmt.get("asr"),
                    fmt.get("filesize")
                ))
            except KeyError:
                continue

    return audio_formats

def get_title_and_duration_from_video(video_info):
    return (
        video_info.get("title", "Unknown title"),
        video_info.get("duration_string") or video_info.get("duration") or "Unknown duration"
    )