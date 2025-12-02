import re
from src.util import to_mb


class RawAudioFormatInfo():
    def __init__(self, id, extension, protocol, asr=None, filesize=None):
        # Format ID of the audio
        self.id = id
        # Extension of the audio
        self.extension = extension
        # Protocol for which the audio respects
        self.protocol = protocol
        # Audio sample rate
        self.asr = asr
        # Filesize of audio
        self.filesize = filesize

    def __str__(self):
        return f"({self.id}) {self.extension} via {self.protocol} at {self.asr or "n/a"}Hz (~{to_mb(self.filesize)})"
    
    def get_format_from_string(format_string):
        audio_pattern = re.compile(
            r"\((?P<id>[^\)]+)\)\s+"
            r"(?P<extension>\w+)\s+via\s+(?P<protocol>\S+)"
            r"(?:\s+at\s+(?P<asr>\d+)Hz)?"
            r"(?:\s+\(~(?P<filesize>[0-9\.]+)Mb\))?"
        )

        match = audio_pattern.match(format_string)
        if match:
            return RawAudioFormatInfo(
                id=match.group("id"),
                extension=match.group("extension"),
                protocol=match.group("protocol"),
                asr=match.group("asr"),
                filesize=float(match.group("filesize"))
            )