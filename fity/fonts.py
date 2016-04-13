from collections import OrderedDict
import six
from fontTools.ttLib import TTFont
from .base import hexbytes, ExtractionError
from .categories import FontType


class FontToolsMixin(object):
    @classmethod
    def extract(cls, file):
        font = TTFont(file)
        names = {n.nameID: n for n in font['name'].names}
        name = names[1].string.decode('utf-8')
        style = names[2].string.decode('utf-8')
        return cls(file, OrderedDict([('name', name), ('style', style)]))


class TrueTypeFont(FontToolsMixin, FontType):
    mimetype = 'application/x-font-ttf'
    extension = 'ttf'
    description = 'TrueType font'
    signature = hexbytes('00 01 00 00 00')


class OpenTypeFont(FontToolsMixin, FontType):
    mimetype = 'application/x-font-opentype'
    extension = 'otf'
    description = 'TrueType font'
    signature = hexbytes('4F 54 54 4F 00 ? 00 80 00 03 00')


class WoffFont(FontToolsMixin, FontType):
    mimetype = 'application/font-woff'
    extension = 'woff'
    description = 'Woff font'
    signature = hexbytes('77 4F 46 46')


class Woff2Font(FontToolsMixin, FontType):
    mimetype = 'application/font-woff2'
    extension = 'woff2'
    description = 'Woff2 font'
    signature = hexbytes('77 4F 46 32')


def get_utf16le_string(data):
    string = None
    assert isinstance(data, six.binary_type)
    for n in six.moves.range(0, len(data), 2):
        if data[n:n + 2] == b'\x00\x00':
            string = data[0:n]
            break
    if string is None:
        raise ExtractionError("Data does not end in zero byte %r" % data)
    return string.decode('utf-16-le')


class EotFont(FontType):
    mimetype = 'application/vnd.ms-fontobject'
    extension = 'eot'
    description = 'Eot font'
    signature = hexbytes('? ? ? 00 ? ? ? 00 ? 00 02 00 ? 00 00 00 ? ? ? ? 00 00 00 ? 00 00 01 00 ? ? 00 00 ? 00 4C 50')

    @classmethod
    def extract(cls, file):
        file.seek(84)
        data = file.read(200)
        name = get_utf16le_string(data)
        style = get_utf16le_string(data[2 * len(name) + 4:])
        return cls(file, OrderedDict([('name', name), ('style', style)]))
