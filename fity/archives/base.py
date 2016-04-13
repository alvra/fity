import six
from collections import OrderedDict


def split(path):
    parts = path.rsplit('/', 1)
    if len(parts) == 1:
        return None, path
    else:
        return parts


def join(start, end):
    if not start:
        return end
    elif end is None:
        return start
    else:
        return '{}/{}'.format(start, end)


class FileWrapper(object):
    def __init__(self):
        self._file = None

    def _open(self):
        "Internal method to build and return the private file-like object"
        raise NotImplementedError

    def open(self):
        "Open the file"
        assert self._file is None
        self._file = self._open()
        return self

    def close(self):
        "Close the file"
        assert self._file is not None
        self._file.close()
        self._file = None

    def __enter__(self):
        return self.open()

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def read(self, length=None):
        return self._file.read(length)

    def seek(self, pos, whence=0):
        self._file.seek(pos, whence)

    def tell(self):
        return self._file.tell()

    def detect(self):
        from fity import detect
        return detect(self._file)

    def inspect(self):
        from fity import inspect
        return inspect(self._file)


class DecompressedFile(FileWrapper):
    opener_type = NotImplemented

    def __init__(self, file):
        self.file = file
        super(DecompressedFile, self).__init__()

    def _open(self):
        "Internal method to build and return the private file-like object"
        return self.opener_type(self.file)

    @classmethod
    def implement(cls, decompress_type):
        return type(
            'Decompressed{}'.format(decompress_type.__name__),
            (cls, ),
            dict(
                opener_type=decompress_type,
            )
        )


class ArchiveNode(object):
    is_file = False
    is_dir = False

    parent = NotImplemented
    path = NotImplemented

    @property
    def name(self):
        if self.path == '':
            return None
        return self.path.rsplit('/', 1)[-1]


class ArchiveFile(FileWrapper, ArchiveNode):
    is_file = True

    def __init__(self, archive, parent, path):
        self.archive = archive
        self.parent = parent
        self.path = path
        super(ArchiveFile, self).__init__()

    def _open(self):
        "Internal method to build and return the private file-like object"
        return self.archive._open_file(self.archive.archive, self.path)



class ArchiveDir(ArchiveNode):
    is_dir = True

    def __init__(self, archive, parent, path):
        self.archive = archive
        self.parent = parent
        self.path = path

    def list(self, path=None):
        "List all nodes at a given path"
        return self.archive.list(join(self.path, path))

    def get(self, path):
        "Obtain an ArchiveNode instance at a given path or raises ValueError"
        return self.archive.get('{}/{}'.format(self.path, path))

    def file(self, path):
        "Obtain an ArchiveFile instance at a given path or raises ValueError"
        node = self.get(path)
        if isinstance(node, ArchiveFile):
            return node
        elif isinstance(node, ArchiveDir):
            raise ValueError("Node is a dir")
        else:
            raise TypeError(node)

    def dir(self, path):
        "Obtain an ArchiveDir instance at a given path or raises ValueError"
        node = self.get(path)
        if isinstance(node, ArchiveDir):
            return node
        elif isinstance(node, ArchiveFile):
            raise ValueError("Node is a file")
        else:
            raise TypeError(node)

    def __iter__(self):
        return iter(self.list())

    def __getitem__(self, path):
        try:
            return self.get(path)
        except ValueError as e:
            raise six.raise_from(KeyError, e)

    def description_lines(self, indent=0, spacer='  ', file_format='{indent}{file.name}', dir_format='{indent}{dir.name}'):
        lines = []
        for node in self:
            tab = spacer * indent
            if isinstance(node, ArchiveFile):
                lines.append(file_format.format(indent=tab, file=node))
            elif isinstance(node, ArchiveDir):
                lines.append(dir_format.format(indent=tab, dir=node))
                lines.extend(node.description_lines(indent + 1, spacer, file_format, dir_format))
            else:
                raise TypeError(node)
        return lines

    def describe(self, indent=0, spacer='  ', file_format='{indent}{file.name}', dir_format='{indent}{dir.name}/'):
        return '\n'.join(self.description_lines(indent, spacer, file_format, dir_format))


class Archive(ArchiveDir):
    parent = None
    path = ''

    # interface

    def __init__(self, file):
        self.file = file
        self._archive = None

    def open(self):
        "Open the archive"
        assert self._archive is None
        self._archive = self._open_archive(self.file)
        return self

    def close(self):
        "Close the archive"
        assert self._archive is not None
        self._close_archive(self._archive)
        self._archive = None

    def __enter__(self):
        return self.open()

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def get(self, path):
        "Obtain an ArchiveNode instance at a given path or raises ValueError"
        raise NotImplementedError

    def list(self, path=None):
        "Iterate all nodes at a given path"
        raise NotImplementedError

    # internals

    def _create_dir(self, path):
        "Internal method to create an ArchiveDir instance for a path"
        parent = self
        for name in path.split('/'):
            parent = ArchiveDir(self, parent, join(parent.path, name))
        return parent

    def _create_file(self, path):
        "Internal method to create an ArchiveFile instance for a path"
        base, name = split(path)
        if base is None:
            parent = self
        else:
            parent = self._create_dir(base)
        return ArchiveFile(self, parent, path)

    # implementation

    def _open_archive(self, file):
        "Internal method to build and open the private archive object"
        raise NotImplementedError

    def _close_archive(self, archive):
        "Internal method to close the private archive object"
        archive.close()

    def _open_file(self, archive, path):
        "Internal method to build the private archive object"
        raise NotImplementedError


class AllNodesExtractionArchive(Archive):
    "Types of archives that return all nodes simultaneously"

    # interface

    def __init__(self, file):
        super(AllNodesExtractionArchive, self).__init__(file)
        self._contents = None

    def open(self):
        "Open the archive"
        super(AllNodesExtractionArchive, self).open()
        self._contents = None
        return self

    def close(self):
        "Close the archive"
        super(AllNodesExtractionArchive, self).close()
        self._contents = None

    def get(self, path):
        if path == '':
            return self
        base, name = split(path)
        if base is None:
            base = ''
        try:
            isdir = self._content[base][name]
        except KeyError:
            raise ValueError
        else:
            if isdir:
                return self._create_dir(path)
            else:
                return self._create_file(path)

    def list(self, path=None):
        "List all nodes at a given path"
        if self._contents is None:
            self._contents = self._get_structured_contents()
        if path is None:
            path = ''
        try:
            content = self._contents[path]
        except KeyError:
            raise ValueError("No path at '%s'" % path)
        for name, isdir in content.items():
            if isdir:
                yield self._create_dir(join(path, name))
            else:
                yield self._create_file(join(path, name))

    # internals

    def _get_structured_contents(self):
        "Internal method to return tree of all nodes"
        files = self._get_contents(self._archive)
        tree = OrderedDict([('', OrderedDict())])
        for path, pathobj in files:
            if self._content_object_is_dir(pathobj):
                if path == '':
                    # some zip files contain an entry for the root directory
                    continue
                base, name = split(path)
                if base is None:
                    parent = tree['']
                else:
                    parent = tree.setdefault(base, OrderedDict())
                parent[name] = True
                tree.setdefault(path, OrderedDict())
            elif self._content_object_is_file(pathobj):
                base, name = split(path)
                if base is None:
                    parent = tree['']
                else:
                    parent = tree.setdefault(base, OrderedDict())
                assert name not in parent
                parent[name] = False
        # some zip and tar achives omit some dir entries
        for dirpath in tree.keys():
            if dirpath == '':
                continue
            parts = dirpath.split('/')
            for n, part in enumerate(parts):
                tree.setdefault('/'.join(parts[:n]), OrderedDict())
                tree['/'.join(parts[:n])].setdefault(part, True)
        return tree

    # implementation

    def _get_contents(self, archive):
        "Internal method to return an interable of 2-tuples with paths and (non-dict!) objects"
        raise NotImplementedError

    def _content_object_is_dir(self, fileobj):
        "Should return True if the object as returned by _get_contents is a dir"
        raise NotImplementedError

    def _content_object_is_file(self, fileobj):
        "Should return True if the object as returned by _get_contents is a file"
        return not self._content_object_is_dir(fileobj)


class DecompressedArchive(Archive):
    decompress_opener = NotImplemented
    archive_type = NotImplemented

    def __init__(self, file):
        self._decompressed = None
        self._archive = None
        super(DecompressedArchive, self).__init__(file)

    def open(self):
        "Open the archive"
        assert self._decompressed is None
        assert self._archive is None
        self._decompressed = self.decompress_opener(self.file)
        self._archive = self._open_archive(self._decompressed)
        return self

    def close(self):
        "Close the archive"
        assert self._decompressed is not None
        assert self._archive is not None
        self._decompressed.close()
        self._archive.close()
        self._decompressed = None
        self._archive = None

    @classmethod
    def implement(cls, decompress_opener, archive_type):
        assert decompress_opener.__name__.endswith('File')
        return type(
            # eg. GzipTarArchive, Bzip2TarArchive
            '{}{}'.format(decompress_opener.__name__[:-4], archive_type.__name__),
            (cls, archive_type),
            dict(
                decompress_opener=decompress_opener,
                archive_type=archive_type,
            )
        )
