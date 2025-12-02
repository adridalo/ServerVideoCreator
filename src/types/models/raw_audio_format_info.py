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