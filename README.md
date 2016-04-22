# Fity

This is a Python module to detect file types (including mimetype and extension)
and metadata based solely on file contents.


## Installation

Installing with pip will also take care of all Python dependencies.

```
$ pip install fity
```

To enable extraction of compressed files from rar archives, install the `unrar` package
using your system package manager.

```
$ apt-get install unrar-free  # debian
$ apt-get install unrar       # ubuntu
$ yum install unrar           # fedora
$ pacman -S unrar             # arch
$ zipper install unrar        # suse
```


### Requirements

This pure Python module supports both version 2 and 3, including alternative implementations like Pypy,
although it's dependencies might be more restrictive.

To support both Python 2 and 3 in one codebase, it depends on the Python module `six`.
For the extraction of metadata, some additional modules are required.

The following is a complete list of all requirements.

* `six`
* `pillow`
* `mutagen`
* `pygments`
* `PyPDF2`
* `python-dateutil`
* `fontTools`
* `brotlipy`
* `bz2file`
* `rarfile`

The `rarfile` module depends on the `unrar` utility to extract compressed files from rar archives.
Refer to the documentation of that module for more details.


## Documentation

### Detecting file types

Finding the filetype of a given file-like takes only a single function call.
Be aware that the file-like must be seekable, and that the file position is not restored
but instead left at the start (`seek(0)`).

```python
import fity

with open('/path/to/file/') as f:
    filetype = fity.detect(f)
    print(filetype.description)
    print(filetype.extension)
    print(filetype.mimetype)
    for key, value in filetype.properties.items():
        print('{}: {}'.format(key, value))
```

However, sometimes it is not that simple.
There are a few things that can go wrong.

* There will always be files that cannot be detected. The `NoMatch` exception is raised when
  fity has no clue what file it was given.
* For some files, fity cannot decide. The `AmbigousFile` exception indicates there were
  multiple possible file types. Its `results` attribute will contain all filetype instances
  it thinks it could be, so you can choose for yourself (or pass it on to your users, like we do).
* Of course, fity could also be wrong. This should never happen, please let us know if it does.


### Filetype API

When you've obtained a filetype instance for your mysterious file, you'll want to know all about it.

Each filetype instance has a few attributes.
* The original file it describes can be retrieved at `file`. Beware that it might since have been closed.
* The file's `mimetype`
* The `extension` without the leading dot
* A short textual `description` of the file type to show your users
* A mapping of normalized metadata can be found at `properties`.
  The exact content depends on the filetype.
  For instance, an image contains a number of pixels for `height`, `width` and `pixels`.


### Categories

To organize all filetype classes, each concrete filetype is an instance of a subclass
of one the following categories.

* `TextType` Human-readable text
* `ApplicationType` Any kind of application
* `ScriptType` (subclass of `ApplicationType`) Any application whose content is plain-text
* `DocumentType` Any kind of document like an article, spreadsheet or presentation
* `ImageType` Any kind of image
* `VideoType` Any kind of video
* `FontType` Any kind of font
* `CompressedType` Any kind of compressed file, which can be decompressed
  by calling the `open_compressed()` method.
* `ArchiveType` Any kind of archive that can contain multiple files of any type,
  which can be accessed by calling the `open_archive()` method.

These supertypes can be used to categorize files.

```python
filetype = fity.detect(file)
if isinstance(filetype, fity.TextType):
    pass  # handle text
```

Both compressed files and archive typoes have the a universal interface to access their content.
See the sections on their respective subjects below for their interfaces.


### Compressed files

By calling `open_compressed()` on a compressed filetype instance, you obtain a file-like object
of the decompressed file. Besides the standard Python file api, this object exposes an `inspect()` method
to obtain its filetype that otherwise behaves indentically to the main `fity.inspect` method.

Note that to decompress the file object used to detect the filetype instance,
it must not have been closed since.


### Archives

Calling `open_archive()` on any archive filetype instance returns an archive instance.
This object can be opened by using it as a context manager, or by calling it's `open()` and `close()`
methods, and otherwise behaves like an archive directory.

All directory and file instances have the following attributes.

* `path` gives the path in the archive of this node without a leading slash.
  The root dir (the archive itself) is at `''`.
* `name` is the final component in the path, the name of this node.
* `is_file` is `True` for files.
* `is_dir` is `True` for directories.
* `parent` points to the parent directory, or `None` for the root directory (the archive itself).
* `archive` holds a reference to the archive instance.

#### Directories

An archive directory (and the archive itself, when it's opened) can be iterated or indexed
to obtain its content. Additionally, it exposes the following methods.

* `list(path=None)` Like iterating the directory itself, this returns an iterator of its content.
* `get(path)` Like indexing, this methods returns the directory or file at the given path,
  or raises `ValueError` if there is no content at the given path.
* `file(path)` Identical to the `get` method, but only returns files
  and raises `ValueError` if the path leads to a directory.
* `dir(path)` Like the `file` method but for directories.
* `describe(indent=0, spacer='  ', file_format='{indent}{file.name}', dir_format='{indent}{dir.name}/')`
  This method can be used to generate a textual description of this dir by listing its content.

#### Files

Besides the standard Python file api, an archive file exposes an `inspect()` method
to obtain its filetype that otherwise behaves indentically to the main `fity.inspect` method.


### Detection script

Fity includes a command-line script to detect file types and metadata.
Its installed by default when using pip.

```
$ fity.py file_1 file_2 file_3
```


## Contributing

If you've found a file whose file type is supported but fity could not detect (correctly),
please file a issue report with the file, the file header or at least the error in the fity
detection headers.

For any missing common file type or metadata item you need to support,
please file submit a pull request or file a ticket.


## License

See LICENSE file.
