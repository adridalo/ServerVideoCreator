import math
import ffmpeg


class DownloadedVideoInfo:
    def __init__(self, path, resolution, fps):
        self.path = path
        self.resolution = resolution
        self.fps = fps

    def _get_pretty_resolution(resolution_height, frame_rate, include_fps=True):
        rounded_fps = math.ceil(frame_rate)

        if resolution_height == 1080:
            return f"HD{rounded_fps if include_fps else ""}"
        elif resolution_height == 2160:
            return f"4K{rounded_fps if include_fps else ""}"
        else:
            return f"{resolution_height}p{rounded_fps if include_fps else ""}"

    def get_video_info(video):
        try:
            probe = ffmpeg.probe(video)

            video_stream = next(
                (stream for stream in probe["streams"] if stream["codec_type"] == "video"),
                None
            )

            if video_stream is None:
                raise ValueError("No video stream found")
            
            height = video_stream['height']
            width = video_stream['width']

            rate = video_stream.get("avg_frame_rate", "0/0")
            num, denom = map(int, rate.split("/"))
            frame_rate = round(num / denom) if denom != 0 else 0

            return DownloadedVideoInfo(
                video,
                (height, width),
                frame_rate
            )

        except ffmpeg.Error as e:
            print("FFmpeg error:", e.stderr.decode())
        except Exception as e:
            print("Error:", str(e))