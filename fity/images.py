from collections import OrderedDict
from PIL import Image
from .base import Filetype, hexbytes
from .categories import ImageType


# TODO
# maybe use the stdlib module imghdr
# https://docs.python.org/3.4/library/imghdr.html


class ImageMixin(object):
    @classmethod
    def extract(cls, file):
        image = Image.open(file)
        size = image.size
        props = OrderedDict([
            ('mode', image.mode),
            ('width', size[0]),
            ('height', size[1]),
            ('pixels', size[0] * size[1]),
        ])
        duration = image.info.get('duration')
        if duration:
            props['duration'] = duration
        return cls(file, props)


class PNGImage(ImageMixin, ImageType):
    mimetype = 'image/png'
    extension = 'png'
    description = 'PNG image'
    signature = hexbytes('89 50 4E 47 0D 0A 1A 0A')


class JPGImage(ImageMixin, ImageType):
    mimetype = 'image/jpeg'
    extension = 'jpg'
    description = 'JPG image'
    signatures = [
        hexbytes('FF D8 FF E0 ?? ?? 4A 46 49 46 00'),
        hexbytes('FF D8 FF E1 ?? ?? 45 78 69 66 00'),
        hexbytes('FF D8 FF E8 ?? ?? 53 50 49 46 46 00'),
        hexbytes('FF D8 FF DB 00 43 00'),
    ]


class GIFImage(ImageMixin, ImageType):
    mimetype = 'image/gif'
    extension = 'gif'
    description = 'GIF image'
    signatures = [
        hexbytes('47 49 46 38 37 61'),
        hexbytes('47 49 46 38 39 61'),
    ]
