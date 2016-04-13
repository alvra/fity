import itertools
from .base import Filetype, ExtractionError
from .categories import (
    TextType, ApplicationType, ScriptType, DocumentType, ImageType,
    AudioType, VideoType, CompressedType, ArchiveType, FontType
)
from . import (
    archives, audio, extensible_markup, fonts, images, matroska, office,
    portable_documents, scripts, unicode, video
)


class DetectionError(Exception):
    pass

class NoMatch(DetectionError):
    pass

class AmbigousFile(DetectionError):
    def __init__(self, results):
        self.results = results

class NoValidMatch(NoMatch):
    pass


def inspect(file, debug=False):
    "Returns an iterable of 2-tuples as (Filetype-class, likeliness) sorted by matching likeliness."
    matches = []
    file.seek(0)
    for filetype in Filetype.subclasses:
        likeliness = filetype.detect(file)
        file.seek(0)
        if likeliness > 0:
            if debug:
                print('    {}: {}'.format(filetype.__name__, likeliness))
            matches.append((filetype, likeliness))
    return sorted(matches, key=lambda m: m[1], reverse=True)


def group_matches(matches):
    """Given a list of matches (as returned by 'inspect'), returns an iterable
    of 2-tuples (likeliness, list of Filetype-classes).
    """
    return ((l, [x[0] for x in m]) for l, m in itertools.groupby(matches, key=lambda x: x[1]))


def detect(file, debug=False):
    "Returns the filetype instance for this file, or raises DetectionError if it could not be determined."
    matches = inspect(file, debug=debug)
    if not matches:
        raise NoMatch

    for _, filetypes in group_matches(matches):
        results = []
        for filetype in filetypes:
            try:
                results.append(filetype.extract(file))
            except ExtractionError:
                pass
            file.seek(0)
        if len(results) == 1:
            return results[0]
        elif len(results) > 1:
            raise AmbigousFile(results)
    raise NoValidMatch
