from .base import Filetype


class TextType(Filetype):
    "Any kind of human-readable text"


class ApplicationType(Filetype):
    "Any kind of application"

class ScriptType(ApplicationType):
    "Any kind of scripted application"


class DocumentType(Filetype):
    "Any kind of document like an article, spreadsheet or presentation"


class ImageType(Filetype):
    "Any kind of image"


class AudioType(Filetype):
    "Any kind of audio"


class VideoType(Filetype):
    "Any kind of video"


class FontType(Filetype):
    "Any kind of font"


class CompressedType(Filetype):
    "Any kind of compressed file"

    decompress_opener = NotImplemented

    def open_compressed(self):
        return self.decompress_opener(self.file)


class ArchiveType(Filetype):
    "Any kind of archive that can contain multiple files of any type"

    archive_opener = NotImplemented

    def open_archive(self):
        return self.archive_opener(self.file)
