import math
import ffmpeg

# Represents the video information of a video that has been downloaded
class DownloadedVideoInfo:
    def __init__(self, path, resolution, fps):
        # Location of the downloaded video
        self.path = path
        # Resolution of the video
        self.resolution = resolution
        # Frames per second of the video
        self.fps = fps

    # Returns a nicer format of the resolution
    # Args:
    # - resolution_height: Resolution height of the video
    # - frame_rate: Frame rate of the video
    # - include_fps: if True:
    #                   Includes the FPS in the resolution (ex: 4K60)
    #                else:
    #                   Just gives the resolution height (ex: 4K)
    def get_pretty_resolution(resolution_height, frame_rate, include_fps=True):
        # Rounds the FPS up
        rounded_fps = math.ceil(frame_rate)

        # if resolution is HD
        if resolution_height == 1080:
            return f"HD{rounded_fps if include_fps else ""}"
        # if resolution is 4K
        elif resolution_height == 2160:
            return f"4K{rounded_fps if include_fps else ""}"
        # other resolutions
        else:
            return f"{resolution_height}{f"p{rounded_fps}" if include_fps else ""}"

    # Retrieves video information on the supplied video
    # Args:
    # - video: video (path) to get information on
    def get_video_info(video):
        try:
            # probe video for information
            probe = ffmpeg.probe(video)

            # get first video stream found based on valid parameters
            video_stream = next(
                (stream for stream in probe["streams"] if stream["codec_type"] == "video"),
                None
            )

            # if no stream is found
            if video_stream is None:
                raise ValueError("No video stream found")
            
            # height + width of video
            height = video_stream['height']
            width = video_stream['width']

            # Gets average frame rate of video in a fraction format
            rate = video_stream.get("avg_frame_rate", "0/0")
            # gets numerator and denominator in separate variables
            num, denom = map(int, rate.split("/"))
            # calculates the frame rate and rounds it
            frame_rate = round(num / denom) if denom != 0 else 0

            # returns video information for that video
            return DownloadedVideoInfo(
                video,
                (height, width),
                frame_rate
            )

        except ffmpeg.Error as e:
            print("FFmpeg error:", e.stderr.decode())
        except Exception as e:
            print("Error:", str(e))