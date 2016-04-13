import six
from .base import hexbytes
from .categories import TextType


class UnicodeMixin(object):
    mimetype = 'text/plain'
    extension = 'txt'
    description = 'Unicode text'
    encoding = NotImplemented
    encoding_name = NotImplemented

    @classmethod
    def extract(cls, file):
        start = file.read(1024)[self.signature.length:]
        assert isinstance(start, six.bytes_type)
        try:
            start.decode(self.encoding)
        except UnicodeDecodeError:
            raise ExtractionError("Could not decode as %s" % self.encoding_name)
        return cls(file, dict(encoding=cls.encoding_name))


def create_utf_filetype(encoding, name, signature):
    clsname = '%sText' % name.replace(' ', '')
    globals()[clsname] = type(
        clsname,
        (UnicodeMixin, TextType),
        dict(signature=hexbytes(signature), name=name, encoding=encoding),
    )


create_utf_filetype('utf-8',  'UTF8', 'EF BB BF')
create_utf_filetype('utf-16-be', 'UTF16 Big Endian', 'FE FF')
create_utf_filetype('utf-16-le', 'UTF16 Little Endian', 'FF FE')
create_utf_filetype('utf-32-be', 'UTF32 Big Endian', '00 00 FE FF')
create_utf_filetype('utf-32-le', 'UTF32 Little Endian', 'FF FE 00 00')
