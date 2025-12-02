import math
import os
import ffmpeg


class DownloadedVideoInfo():
    def __init__(self, name, path, resolution, fps):
        self.name = name
        self.path = path
        self.resolution = resolution
        self.fps = fps

    def get_video_information_from_video_file(video_file):
        try:
            probe = ffmpeg.probe(video_file)

            video_stream = next(
                (stream for stream in probe["streams"] if stream["codec_type"] == "video"),
                None
            )

            if video_stream is None:
                raise ValueError("No video stream found")
            
            height = video_stream["height"]
            width = video_stream["width"]

            rate = video_stream.get("avg_frame_rate", "0/0")
            num, denom = map(int, rate.split("/"))
            frame_rate = round(num / denom) if denom != 0 else 0

            return DownloadedVideoInfo(
                os.path.basename(video_file),
                video_file,
                (height, width),
                frame_rate
            )
    
        except ffmpeg.Error as e:
            print("FFMPEG Error: ", e.stderr.decode())
        except Exception as e:
            print("Error: ", str(e))

    def get_pretty_resolution(self):
        rounded_fps = math.ceil(self.fps)

        if self.resolution[1] == 1080:
            return f"HD{rounded_fps}"
        elif self.resolution[1] == 2160:
            return f"4K{rounded_fps}"
        else:
            return f"{self.resolution[1]}p{rounded_fps}"