import yt_dlp


supported_formats = ["mp4", "mkv", "webm", "flv", "avi"]

def get_proxy():
    import sys, os, json

    base_paths = [os.path.abspath(".")]

    if getattr(sys, 'frozen', False):
        base_paths.insert(0, sys._MEIPASS)

    for base_path in base_paths:
        config_path = os.path.join(base_path, "proxy.config.json")
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                data = json.load(f)
                return data.get("proxy", "")
        else:
            break
    
    return ""
    
def yt_fetch_video_info(url):
    ydl_options = {
        "listformats": True,
        "quiet": True,
        "forcejson": True,
        "dump_single_json": True
    }

    if get_proxy() != "":
        ydl_options["proxy"] = get_proxy()

    with yt_dlp.YoutubeDL(params=ydl_options) as ydl:
        video_info = ydl.extract_info(url, download=False)
        return video_info