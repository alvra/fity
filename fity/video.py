from collections import OrderedDict
from .base import hexbytes, hexadecimals
from .categories import VideoType


class AVIVideo(VideoType):
    mimetype = 'video/avi'
    extension = 'avi'
    description = 'AVI video file'
    signatures = [
        hexbytes('52 49 46 46 ? ? ? ? 41 56 49 20 4C 49 53 54'),
    ]

#    @classmethod
#    def extract(cls, file):
#        raise NotImplementedError  # TODO resolution duration subtitles etc


class MP4Video(VideoType):
    mimetype = 'video/mp4'
    extension = 'mp4'
    description = 'MP4 video file'
    signatures = [
        hexbytes('? ? ? ? 66 74 79 70 33 67 70 35'),
        hexbytes('? ? ? ? 66 74 79 70 4D 34 56 20'),
        hexbytes('? ? ? ? 66 74 79 70 4D 53 4E 56'),
        hexbytes('? ? ? ? 66 74 79 70 69 73 6F 6D'),
        hexbytes('? ? ? ? 66 74 79 70 6D 70 34 32'),
    ]

#    @classmethod
#    def extract(cls, file):
#        raise NotImplementedError  # TODO


class MOVVideo(VideoType):
    mimetype = 'video/quicktime'
    extension = 'mov'
    description = 'QuickTime movie'
    signatures = [
        hexbytes('00 00 00 ?? 66 74 79 70 71 74 20 20 20 05 03 00 71 74'),  # ftyp qt
        hexbytes('00 00 ?? ?? 6D 6F 6F 76 00 00 00 6C 6D 76 68 64 00 00 00 00'),  # moov lmvhd
        hexbytes('00 00 ?? ?? 6D 6F 6F 76 00 00 43 B7 63 6D 6F 76 00 00 00 0C 64 63 6F 6D 7A 6C 69 62 00 00'),  # moov cmov dcomzlib
    ]

#    @classmethod
#    def extract(cls, file):
#        raise NotImplementedError  # TODO


class FlashVideo(VideoType):
    mimetype = 'video/x-flv'
    extension = 'flv'
    description = 'Flash video'
    signature = hexbytes('46 4C 56 01 05 00 00 00 09 00 00 00 00 12 00')

#    @classmethod
#    def extract(cls, file):
#        raise NotImplementedError  # TODO


class MPEGVideo(VideoType):
    mimetype = 'video/mpeg'
    extension = 'mpg'
    description = 'MPEG video'
    signatures = [
        # TODO distinguish from .vob
        hexbytes('00 00 01 B%s' % s) for s in hexadecimals
    ]

#    @classmethod
#    def extract(cls, file):
#        raise NotImplementedError  # TODO


class BluRayVideoVideo(VideoType):
    mimetype = 'video/mp2t'
    extension = 'm2ts'
    description = 'Blu-ray Disc video'
    # signature = hexbytes('')  # TODO

#    @classmethod
#    def extract(cls, file):
#        raise NotImplementedError  # TODO


class WindowsMediaVideo(VideoType):
    mimetype = 'video/x-ms-wmv'
    extension = 'wmv'
    description = 'Windows media video'
    # TODO distinguish from .wma and .asf
    signature = hexbytes('30 26 B2 75 8E 66 CF 11 A6 D9 00 AA 00 62 CE 6C')

#    @classmethod
#    def extract(cls, file):
#        raise NotImplementedError  # TODO


class AdvancedSystemsFormatVideo(VideoType):
    mimetype = 'video/x-ms-asf'
    extension = 'asf'
    description = 'Advanced Systems Format video'
    # TODO distinguish from .wmv and .wma
    signature = hexbytes('30 26 B2 75 8E 66 CF 11 A6 D9 00 AA 00 62 CE 6C')

#    @classmethod
#    def extract(cls, file):
#        raise NotImplementedError  # TODO


class VideoObject(VideoType):
    mimetype = 'video/dvd'
    extension = 'vob'
    description = 'DVD Video Object file'
    # TODO distinguish from .mpg
    signature = hexbytes('00 00 01 BA')

#    @classmethod
#    def extract(cls, file):
#        raise NotImplementedError  # TODO
