import six
from gzip import GzipFile
from ..base import Filetype, hexbytes
from ..categories import CompressedType, ArchiveType
from .base import DecompressedFile, DecompressedArchive
from .bzip2open import Bzip2File
from .gzipopen import GzipFile
from .zipopen import ZipArchive
from .taropen import TarArchive
from .raropen import RarArchive


# compressed

class Bzip2CompressedType(CompressedType):
    mimetype = 'application/x-bzip2'
    extension = 'bz2'
    description = 'Bzip2 archive'
    signature = hexbytes('42 5A 68')
    decompress_opener = DecompressedFile.implement(Bzip2File)


class GzipCompressedType(CompressedType):
    mimetype = 'application/gzip'
    extension = 'gz'
    description = 'Gzip archive'
    signatures = [
        hexbytes('1F 8B 08 08'),
        hexbytes('1F 8B 08 00'),
    ]
    decompress_opener = DecompressedFile.implement(GzipFile)


# archives

class ZipArchiveType(ArchiveType):
    mimetype = 'application/zip'
    extension = 'zip'
    description = 'Zip archive'
    signatures = [
        hexbytes('50 4B 03 04 14 00'),
        hexbytes('50 4B 03 04 0A'),
    ]
    archive_opener = ZipArchive


class TarArchiveType(ArchiveType):
    mimetype = 'application/x-tar'
    extension = 'tar'
    description = 'Tar archive'
    signature = hexbytes(
        ' '.join('?' for _ in six.moves.xrange(257)) +
        ' 75 73 74 61 72'
    )
    archive_opener = TarArchive


class RarArchiveType(ArchiveType):
    mimetype = 'application/x-rar-compressed'
    extension = 'rar'
    description = 'Rar archive'
    signatures = [
        hexbytes('52 61 72 21 1A 07 00'),
        hexbytes('52 61 72 21 1A 07 01 00'),
    ]
    archive_opener = RarArchive


# compressed archives

class CompressedArchiveType(CompressedType, ArchiveType):
    archive_filetype = NotImplemented

    @classmethod
    def detect(cls, file):
        ln1 = super(CompressedArchiveType, cls).detect(file)
        if ln1 == 0:
            return 0
        file.seek(0)
        try:
            decompressed = cls.decompress_opener(file)
        except ValueError:
            return 0
        with decompressed:
            ln2 = cls.archive_filetype.detect(decompressed)
        if ln2 == 0:
            return 0
        return ln1 + ln2


class TarBzip2ArchiveType(CompressedArchiveType, Bzip2CompressedType):
    mimetype = 'application/x-bzip2'
    extension = 'tar.bz2'
    description = 'Bzipped tar archive'
    archive_filetype = TarArchiveType
    archive_opener = DecompressedArchive.implement(Bzip2File, TarArchive)


class TarGzipArchiveType(CompressedArchiveType, GzipCompressedType):
    mimetype = 'application/gzip'
    extension = 'tar.gz'
    description = 'Gzipped tar archive'
    archive_filetype = TarArchiveType
    archive_opener = DecompressedArchive.implement(GzipFile, TarArchive)
