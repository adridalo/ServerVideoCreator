class Audio():
    def __init__(self, id, extension, protocol, asr=None, filesize=None):
        self.id = id
        self.extension = extension
        self.protocol = protocol
        self.asr = asr
        self.filesize = filesize