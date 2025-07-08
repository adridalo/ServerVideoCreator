import json

import yt_dlp


def get_proxy():
    import sys, os

    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")

    config_path = os.path.join(base_path, "proxy.config.json")
    proxy = ""
    with open(config_path, 'r') as f:
        data = json.load(f)
        proxy = data['proxy']
        return proxy
    
def fetch_video_info(url):
    ydl_options = {
        "proxy": get_proxy(),
        "listformats": True,
        "quiet": True,
        "forcejson": True,
        "dump_single_json": True
    }

    with yt_dlp.YoutubeDL(params=ydl_options) as ydl:
        video_info = ydl.extract_info(url, download=False)
        return video_info