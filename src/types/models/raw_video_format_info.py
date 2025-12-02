import re


class RawVideoFormatInfo():
    def __init__(self, id, resolution, fps, protocol, extension):
        # Format ID of the video
        self.id = id
        # Resolution of the video 
        self.resolution = resolution
        # Frames per second of the video
        self.fps = fps
        # Protocol for which the video respects
        self.protocol = protocol
        # Extension of the video
        self.extension = extension

    def __str__(self):
        return f"({self.id}) {self.resolution} {self.fps} {self.extension} via {self.protocol}"
    
    def get_format_from_string(format_string):
        video_pattern = re.compile(
            r"\((?P<id>[^\)]+)\)\s+"
            r"(?P<resolution>\d+x\d+)\s+"
            r"(?P<fps>\d+|n/a)\s+"
            r"(?P<extension>\w+)\s+via\s+(?P<protocol>\S+)"
        )

        match = video_pattern.match(format_string)
        if match:
            return RawVideoFormatInfo(
                id=match.group("id"),
                resolution=match.group("resolution"),
                fps=match.group("fps"),
                protocol=match.group("protocol"),
                extension=match.group("extension")
            )