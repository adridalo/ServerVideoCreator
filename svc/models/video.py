# Represents the video format
class Video():
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