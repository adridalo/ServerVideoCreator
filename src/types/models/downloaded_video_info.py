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

            rotation = None
            side_data = video_stream.get("side_data_list")
            if side_data and isinstance(side_data, list):
                rotation = side_data[0].get("rotation")

            if rotation in (90, 270):
                width, height = height, width

            if width < height:
                width, height = height, width

            rate = video_stream.get("avg_frame_rate", "0/0")
            num, denom = map(int, rate.split("/"))
            frame_rate = round(num / denom) if denom != 0 else 0

            return DownloadedVideoInfo(
                os.path.basename(video_file),
                video_file,
                (width, height),
                frame_rate
            )
    
        except ffmpeg.Error as e:
            print("FFMPEG Error: ", e.stderr.decode())
        except Exception as e:
            print("Error: ", str(e))

    # contain=False: seperates resolution and fps into tuple
    # contain=True: combines resolution and fps into one str
    def get_pretty_resolution(self, combine=False):
        rounded_fps = math.ceil(self.fps)
        height = self.resolution[1]

        if height == 1080:
            return ("HD", rounded_fps) if not combine else f"HD{rounded_fps}"
        elif height == 2160:
            return ("4K", rounded_fps) if not combine else f"4K{rounded_fps}"
        elif height == 4230:
            return ("8K", rounded_fps) if not combine else f"8K{rounded_fps}"
        else:
            return (f"{height}p", rounded_fps) if not combine else f"{height}p{rounded_fps}"