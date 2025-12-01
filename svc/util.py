import os
import yt_dlp

# Application supported video formats
SUPPORTED_FORMATS = ["mp4", "mkv", "webm", "flv", "avi"]

# Funtion to get proxy settings based off included 'proxy.config.json'
def get_proxy():
    import os, json

    # Base path set used to look for config file
    base_path = os.path.abspath(".")

    # Config file path
    config_path = os.path.join(base_path, "proxy.config.json")
    # If the file exists
    if os.path.exists(config_path):
        # Open it and read the file contents
        with open(config_path, 'r') as f:
            # Extract the data
            data = json.load(f)
            # Return proxy value
            return data.get("proxy", "")
    # If file is not found (non-existent)
    else:
        return ""

# Function used to fetch video information via yt-dlp
# Args:
# - url: YouTube URL
def yt_fetch_video_info(url):
    # If no URL is supplied/is empty
    if url is None or len(url) == 0:
        # Escape
        return
    
    # Define options for downloading
    ydl_options = {
        "listformats": True,
        "quiet": True,
        "forcejson": True,
        "dump_single_json": True
    }

    # If proxy is found
    if get_proxy() != "":
        # Add it to options
        ydl_options["proxy"] = get_proxy()

    # Open YDL operation
    with yt_dlp.YoutubeDL(params=ydl_options) as ydl:
        # Extract information
        video_info = ydl.extract_info(url, download=False)
        # Return it
        return video_info
    
# Function used to bytes to MB
def to_mb(bytes_val):
    return f"{bytes_val / 1_000_000:.2f} MB" if bytes_val else "n/a"

# Event used to handle opening the downloaded video in an explorer window
# Args:
# - path: Path to open in an explorer window
def open_folder(path):
    os.startfile(path)