import zipfile
from collections import namedtuple
import six
from .base import hexbytes, ExtractionError
from .categories import DocumentType


XDocumentType = namedtuple('XDocumentType', 'name extension mimetype partname')

doctypes = [
    XDocumentType('Word', 'docx', 'application/msword', 'PartName="/word/'),
    XDocumentType('Excel', 'xlsx', 'application/excel', 'PartName="/xl/'),
    XDocumentType('Powerpoint', 'pptx', 'application/mspowerpoint', 'PartName="/ppt/'),
]


class OfficeXDocument(DocumentType):
    signatures = [
        hexbytes('50 4B 03 04 14 00'),
        hexbytes('50 4B 03 04 0A'),
    ]

    def __init__(self, file, properties, doctype):
        self.file = file
        self.properties = properties
        self.doctype = doctype

    @property
    def mimetype(self):
        return self.doctype.mimetype

    @property
    def extension(self):
        return self.doctype.extension

    @property
    def description(self):
        return '%s document' % self.doctype.name

    @classmethod
    def _detect_doctype(cls, file):
        try:
            z = zipfile.ZipFile(file, mode='r')
        except zipfile.BadZipfile as e:
            six.raise_from(ExtractionError('Cannot unzip'), e)
        try:
            ctf = z.open('[Content_Types].xml', mode='r')
        except KeyError as e:
            six.raise_from(ExtractionError('No content types found'), e)
        ct = ctf.read(1024)
        for doctype in doctypes:
            if doctype.partname in ct:
                return doctype
        raise ExtractionError("Could not determine doctype")

    @classmethod
    def extract(cls, file):
        doctype = cls._detect_doctype(file)
        return cls(file, dict(), doctype)

    @classmethod
    def detect(cls, file):
        likeliness = super(OfficeXDocument, cls).detect(file)
        if likeliness == 0:
            return 0
        try:
            doctype = cls._detect_doctype(file)
        except ExtractionError:
            return 0
        return 10 if doctype is None else 128


class WordDocument(DocumentType):
    mimetype = 'application/msword'
    extension = 'doc'
    description = 'Word document'
    signatures = [
        hexbytes(
            'D0 CF 11 E0 A1 B1 1A E1 ' +
            ' '.join('?' for _ in six.moves.range(512 - 8)) +
            ' EC A5 C1 00'
        ),
        hexbytes(
            'D0 CF 11 E0 A1 B1 1A E1 ' +
            ' '.join('?' for _ in six.moves.range(512 - 8)) +
            ' FD FF FF FF FF'
        ),
    ]


class ExcelDocument(DocumentType):
    mimetype = 'application/excel'
    extension = 'xls'
    description = 'Excel document'
    signatures = [
        hexbytes(
            'D0 CF 11 E0 A1 B1 1A E1 ' +
            ' '.join('?' for _ in six.moves.range(512 - 8)) +
            ' 09 08 10 00 00 06 05 00'
        ),
#        hexbytes(
#            'D0 CF 11 E0 A1 B1 1A E1 ' +
#            ' '.join('?' for _ in six.moves.range(512 - 8)) +
#            ' FD FF FF FF nn 00'
#        ),
#        hexbytes(
#            'D0 CF 11 E0 A1 B1 1A E1 ' +
#            ' '.join('?' for _ in six.moves.range(512 - 8)) +
#            ' FD FF FF FF nn 02'
#        ),
#        hexbytes(
#            'D0 CF 11 E0 A1 B1 1A E1 ' +
#            ' '.join('?' for _ in six.moves.range(512 - 8)) +
#            ' FD FF FF FF 20 00 00 00'
#        ),
        hexbytes(
            'D0 CF 11 E0 A1 B1 1A E1 ' +
            ' '.join('?' for _ in six.moves.range(512 - 8)) +
            ' FD FF FF FF'  # TODO distinguish from ppt
        ),
    ]


class PowerpointDocument(DocumentType):
    mimetype = 'application/mspowerpoint'
    extension = 'ppt'
    description = 'Powerpoint document'
    signatures = [
        hexbytes(
            'D0 CF 11 E0 A1 B1 1A E1 ' +
            ' '.join('?' for _ in six.moves.range(512 - 8)) +
            ' 00 6E 1E F0'
        ),
        hexbytes(
            'D0 CF 11 E0 A1 B1 1A E1 ' +
            ' '.join('?' for _ in six.moves.range(512 - 8)) +
            ' 0F 00 E8 03'
        ),
        hexbytes(
            'D0 CF 11 E0 A1 B1 1A E1 ' +
            ' '.join('?' for _ in six.moves.range(512 - 8)) +
            ' A0 46 1D F0'
        ),
#        hexbytes(
#            'D0 CF 11 E0 A1 B1 1A E1 ' +
#            ' '.join('?' for _ in six.moves.range(512 - 8)) +
#            ' FD FF FF FF nn nn 00 00'
#        ),
        hexbytes(
            'D0 CF 11 E0 A1 B1 1A E1 ' +
            ' '.join('?' for _ in six.moves.range(512 - 8)) +
            ' FD FF FF FF'  # TODO distinguish from xls
        ),
    ]
