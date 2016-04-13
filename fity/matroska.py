from .base import hexbytes
from .categories import AudioType, VideoType


class MatroskaVideo(VideoType):
    mimetype = 'video/x-matroska'
    extension = 'mkv'
    description = 'Matroska video'
    signature = hexbytes('1A 45 DF A3')

#    @classmethod
#    def extract(cls, file):
#        raise NotImplementedError  # TODO resolution duration subtitles etc


class MatroskaAudio(AudioType):
    mimetype = 'audio/x-matroska'
    extension = 'mka'
    description = 'Matroska audio'
    # signature = hexbytes('')  # TODO

#    @classmethod
#    def extract(cls, file):
#        raise NotImplementedError  # TODO duration samplerate etc
