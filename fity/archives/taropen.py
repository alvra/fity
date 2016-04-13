import six
import tarfile
from .base import AllNodesExtractionArchive


class TarArchive(AllNodesExtractionArchive):
    def _open_archive(self, file):
        try:
            return tarfile.TarFile(fileobj=file, mode='r', errorlevel=2)
        except tarfile.ReadError as e:
            six.raise_from(ValueError(str(e)), e)

    def _open_file(self, archive, path):
        return archive.extractfile(path)

    def _get_contents(self, archive):
        return ((i.name, i) for i in archive.getmembers())

    def _content_object_is_dir(self, fileobj):
        return fileobj.isdir()

    def _content_object_is_file(self, fileobj):
        return fileobj.isfile()
