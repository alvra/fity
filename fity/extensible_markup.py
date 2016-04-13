import re
from .base import Filetype
from .categories import ImageType


search_span = 1024
xml_regex = re.compile(br'\s*' + re.escape(b'<?xml') + br'\s+version="', re.I)
svg_regex = re.compile(br'xmlns(:svg)?="http://www.w3.org/2000/svg"', re.I)
html_regex = re.compile(br'\s*' + re.escape(b'<!doctype') + br'\s+' + re.escape(b'html'), re.I)


class XML(Filetype):
    mimetype = 'application/xml'
    extension = 'xml'
    description = 'Extensible Markup Language document'

    @classmethod
    def detect(cls, file):
        start = file.read(search_span)
        if xml_regex.match(start) is not None:
            return 13
        else:
            return 0


class WebpageType(Filetype):
    pass


class HTML(WebpageType):
    mimetype = 'text/html'
    extension = 'html'
    description = 'Hypertext document'

    @classmethod
    def detect(cls, file):
        start = file.read(search_span)
        if html_regex.match(start) is not None:
            return 14
        else:
            return 0


class XHTML(WebpageType):
    mimetype = 'text/html'
    extension = 'html'
    description = 'Hypertext document'

    @classmethod
    def detect(cls, file):
        start = file.read(search_span)
        if xml_regex.match(start) is not None and html_regex.search(start) is not None:
            return 13 + 14
        else:
            return 0


class SVG(ImageType):
    mimetype = 'image/svg+xml'
    extension = 'svg'
    description = 'Scalable Vector Graphics'

    @classmethod
    def detect(cls, file):
        start = file.read(search_span)
        if xml_regex.match(start) is not None and svg_regex.search(start) is not None:
            return 13 + 34
        else:
            return 0
