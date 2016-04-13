import six
import rarfile
from .base import AllNodesExtractionArchive


class RarArchive(AllNodesExtractionArchive):
    def _open_archive(self, file):
        try:
            return rarfile.RarFile(file, mode='r')
        except rarfile.NotRarFile as e:
            six.raise_from(ValueError(str(e)), e)
        except rarfile.BadRarFile as e:
            six.raise_from(ValueError(str(e)), e)

    def _open_file(self, archive, path):
        try:
            return archive.open(path)
        except rarfile.RarCannotExec as e:
            if 'Unrar not installed?' not in str(e):
                raise
            # the unrar command is not installed
            if six.PY2:
                # rarfile's error is clear enough
                raise
            else:
                # give some extra information
                raise six.raise_from(RuntimeError(
                    "It seems the 'unrar' command is not installed, or for some other reason "
                    "could not be found. Please make sure it is available or "
                    "name the it explicitly by setting 'import rarfile; rarfile.UNRAR_TOOL' "
                    "to the correct command name. "
                    ""

                    "This can probably be solved by installing unrar using your system's package manager "
                    "`apt-get install unrar-free` (debian) "
                    "`apt-get install unrar` (ubuntu) "
                    "`yum install unrar` (fedora) "
                    "`pacman -S unrar` (arch) "
                    "`zipper install unrar` (suse). "
                    ""
                    "Alternatively, you can find the command binary at "
                    "http://www.rarlab.com/rar/rarlinux-5.3.0.tar.gz (32 bit) "
                    "or "
                    "http://www.rarlab.com/rar/rarlinux-x64-5.3.0.tar.gz (64 bit) "
                    "and extract the 'unrar' binary with "
                    "'tar -zxvf rarlinux-*.tar.gz'."
                ), e)

    def _get_contents(self, archive):
        return ((i.filename, i) for i in archive.infolist())

    def _content_object_is_dir(self, fileobj):
        return fileobj.filename.endswith('/')
