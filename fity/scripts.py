from collections import namedtuple
import six
from pygments.lexers import guess_lexer
from .base import ExtractionError
from .categories import ScriptType


shebang = '#!'
env_shebang = '#!/usr/bin/env '


Shell = namedtuple('Shell', 'name extension mimetype')

shells = dict(
    sh=Shell('Shell', 'sh', 'application/x-sh'),
    python=Shell('Python', 'py', 'text/x-python'),
)


class ShebangScript(ScriptType):
    def __init__(self, file, properties, shell=None):
        self.file = file
        self.properties = properties
        self.shell = shell

    @property
    def mimetype(self):
        return 'text/x-script' if self.shell is None else self.shell.mimetype

    @property
    def extension(self):
        return None if self.shell is None else self.shell.extension

    @property
    def description(self):
        return 'Script' if self.shell is None else '%s script' % self.shell.name

    @classmethod
    def extract(cls, file):
        line = file.readline(128)
        if line.startswith(env_shebang):
            command = line[len(env_shebang):].strip()
        elif line.startswith(shebang):
            command = line[len(shebang):].strip()
        else:
            raise ExtractionError('No shebang found')
        parts = command.split()
        path = parts[0]
        names = path.rsplit('/', 1)
        shellname = names[-1]
        try:
            shell = shells[shellname]
        except KeyError:
            raise ExtractionError("Unknown shell command")
        else:
            return cls(file, {}, shell)

    @classmethod
    def detect(cls, file):
        line = file.readline(128)
        if line.startswith(env_shebang):
            return len(env_shebang)
        elif line.startswith(shebang):
            return len(shebang)
        else:
            return 0


class Script(ScriptType):
    # TODO depending on the language, this can also be something else like TextType

    @classmethod
    def _get_lexer(cls, file):
        start = file.read(1024)
        return guess_lexer(start)

    @classmethod
    def extract(cls, file):
        lexer = cls._get_lexer(file)
        if not lexer.mimetypes or not lexer.filenames:
            raise ExtractionError('Lexer has no mimetype or extension info')
        name = lexer.name
        mimetype = lexer.mimetypes[0]
        filename = lexer.filenames[0]
        assert filename.startswith('*.')
        extension = filename[2:]
        return cls(
            file,
            {},
            mimetype=mimetype,
            extension=extension,
            description='%s code' % name,
        )

    @classmethod
    def detect(cls, file):
        try:
            lexer = cls._get_lexer(file)
        except ValueError as e:
            return 0
        else:
            return 1
