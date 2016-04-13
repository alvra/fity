import six
import zipfile
from .base import AllNodesExtractionArchive


class ZipArchive(AllNodesExtractionArchive):
    def _open_archive(self, file):
        try:
            return zipfile.ZipFile(file, mode='r')
        except zipfile.BadZipfile as e:
            six.raise_from(ValueError(str(e)), e)

    def _open_file(self, archive, path):
        return archive.open(path)

    def _get_contents(self, archive):
        return ((i.filename.rstrip('/'), i) for i in archive.infolist())

    def _content_object_is_dir(self, fileobj):
        return fileobj.filename.endswith('/')
